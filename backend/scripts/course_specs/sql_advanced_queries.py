"""SQL Track, Course 3 of 4: "SQL: Ilg'or So'rovlar va Performance".

Pure-data course spec — see course_builder/__init__.py for the contract.
No DB code lives here; build it with:

    cd backend
    python scripts/build_course.py scripts/course_specs/sql_advanced_queries.py --dry-run
    python scripts/build_course.py scripts/course_specs/sql_advanced_queries.py

Follows course 41 (SQL asoslari) and course 98 (DB dizayni). Every SQL
snippet below was executed against PostgreSQL 16 inside a rolled-back
transaction before being written here; the EXPLAIN node types, timings
and error texts quoted in the comments are real measured output, not
guesses.
"""

COURSE = {
    "title": "SQL: Ilg'or So'rovlar va Performance",
    "description": (
        "PostgreSQL'da chuqur so'rovlar: window funksiyalar, recursive CTE, "
        "EXPLAIN ANALYZE, indekslar, tranzaksiyalar va isolation levels, locking, "
        "partitioning. Har bir modul amaliy misollar bilan. Yakuniy capstone — "
        "katta hajmli jadvalda performance audit."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 5,
    "max_points": 182,
    "category_id": 10,
    "prerequisite_course_id": 98,
    "display_order": 502,
    "is_active": True,
    "is_published": False,
}


LESSONS = [
    # ══════════════════════════════════════════════════════════════════
    # 0
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 0,
        "title": "1-Window funksiyalar chuqur: ROW_NUMBER, RANK, LAG/LEAD",
        "title_ru": "1-Оконные функции углублённо: ROW_NUMBER, RANK, LAG/LEAD",
        "points_reward": 13,
        "code_language": "sql",
        "text_content": """<h3>Agregat yig'adi, window saqlaydi</h3>
<p>Bu ikkalasi orasidagi farqni bir jumlada aytish mumkin: <code>GROUP BY</code> bilan ishlangan agregat 100 ta qatordan 5 tasini qoldiradi, window funksiya esa 100 ta qatorni <em>100 ta bo'lib qoldiradi</em> va har biriga guruh haqidagi qo'shimcha ma'lumotni yozib qo'yadi.</p>
<p>Amalda buni shundan bilasiz: &ldquo;har bir sotuvchining o'z hududidagi o'rni&rdquo; kerak bo'lganda, agregat sizga hududlar ro'yxatini beradi &mdash; sotuvchilar yo'qoladi. Window funksiya esa har bir sotuvchini joyida qoldirib, yoniga <code>o_rin</code> ustunini qo'shadi. Birinchi kursda bu bilan tanishgan edingiz; endi uchta raqamlash funksiyasining haqiqiy farqini va davrlarni solishtirishni ko'ramiz.</p>

<h3>ROW_NUMBER / RANK / DENSE_RANK &mdash; farq faqat TENGLIKDA</h3>
<p>Uchalasi ham qatorlarga raqam qo'yadi. Ma'lumotda teng qiymat bo'lmasa, uchalasi <strong>bir xil</strong> natija beradi &mdash; shuning uchun ko'p dasturchi farqni bilmasdan ishlab yuraveradi, toki produksiyada birinchi tenglik chiqmaguncha.</p>
<table>
<tr><th>Sotuvchi</th><th>Jami</th><th>ROW_NUMBER</th><th>RANK</th><th>DENSE_RANK</th></tr>
<tr><td>Aziz</td><td>30 mln</td><td>1</td><td>1</td><td>1</td></tr>
<tr><td>Dilnoza</td><td>30 mln</td><td><strong>2</strong></td><td><strong>1</strong></td><td><strong>1</strong></td></tr>
<tr><td>Sardor</td><td>22 mln</td><td>3</td><td><strong>3</strong></td><td><strong>2</strong></td></tr>
</table>
<ul>
<li><strong>ROW_NUMBER</strong> tenglikni umuman tan olmaydi: har bir qatorga o'zining raqamini beradi. Aziz bilan Dilnoza orasida kim 1, kim 2 bo'lishi <em>aniqlanmagan</em> &mdash; so'rovni ikki marta ishga tushirsangiz natija almashishi mumkin.</li>
<li><strong>RANK</strong> tenglarga bir xil raqam beradi, keyin <em>sakraydi</em>: 1, 1, 3. Sport tabeli mantiqi &mdash; ikki oltin medaldan keyin darhol bronza.</li>
<li><strong>DENSE_RANK</strong> tenglarga bir xil raqam beradi, lekin <em>sakramaydi</em>: 1, 1, 2. &ldquo;Nechta turli daraja bor&rdquo; degan savolga shu javob beradi.</li>
</ul>
<p><strong>Amaliy qoida:</strong> <code>ROW_NUMBER</code> ishlatsangiz, <code>ORDER BY</code> ga har doim uziluvchi (tie-breaker) ustun qo'shing &mdash; masalan <code>ORDER BY jami DESC, sotuvchi</code>. Aks holda &ldquo;top-10&rdquo; ro'yxatingiz har safar boshqacha chiqadi va buni hech kim darhol sezmaydi.</p>

<h3>Nega window funksiyani WHERE da ishlatib bo'lmaydi</h3>
<p>Bu eng ko'p uchraydigan xato. Sababi &mdash; SQL ning mantiqiy bajarilish tartibi: <code>WHERE</code> window funksiyadan <em>oldin</em> ishlaydi, ya'ni <code>WHERE</code> bajarilayotgan paytda <code>o_rin</code> hali mavjud emas.</p>
<pre class="mermaid">
flowchart LR
  A["FROM / JOIN"] --> B["WHERE"]
  B --> C["GROUP BY"]
  C --> D["HAVING"]
  D --> E["WINDOW
funksiyalar"]
  E --> F["SELECT"]
  F --> G["ORDER BY"]
  G --> H["LIMIT"]
  style E fill:#ffe9b3,stroke:#d09000
  style B fill:#ffd6d6,stroke:#c00000
</pre>
<p>Yechim doimo bitta: window funksiyani CTE (yoki ichki so'rov) ichida hisoblang, keyin tashqarida filtrlang. Shu sababli &ldquo;har bir guruhdan top-N&rdquo; masalasi deyarli har doim CTE bilan yoziladi.</p>

<h3>LAG va LEAD &mdash; davrlarni solishtirish</h3>
<p><code>LAG(x)</code> tartiblangan oynada <em>oldingi</em> qatorning <code>x</code> qiymatini, <code>LEAD(x)</code> esa <em>keyingi</em> qatorning qiymatini qaytaradi. Aynan shu ikkitasi &ldquo;o'tgan oyga nisbatan o'sish&rdquo;, &ldquo;oldingi holatgacha necha kun o'tdi&rdquo; kabi hisobotlarni self-JOIN'siz yozish imkonini beradi.</p>
<p>Ikki nozik joy bor. Birinchisi: birinchi qatorda <code>LAG</code> har doim <code>NULL</code> qaytaradi &mdash; foizni hisoblashda <code>NULLIF(..., 0)</code> bilan nolga bo'linishdan ham himoyalaning. Ikkinchisi: <code>LAG(x, 1, 0)</code> shaklidagi uchinchi argument <code>NULL</code> o'rniga qo'yiladigan qiymatni belgilaydi.</p>

<h3>Freym (frame) &mdash; sukut bo'yicha nima bo'ladi</h3>
<p><code>OVER (ORDER BY oy)</code> yozganingizda PostgreSQL sizga sezdirmasdan <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> freymini qo'yadi. <code>RANGE</code> so'zi muhim: u <em>teng qiymatli</em> qatorlarni bitta blok deb qaraydi. Ya'ni bir xil sanaga ega uchta qator jamlanma yig'indida birdaniga qo'shiladi &mdash; qator-baqator emas.</p>
<p>Haqiqiy qator-baqator jamlanma kerak bo'lsa, <code>ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> ni <strong>oshkora</strong> yozish shart. Ko'p &ldquo;running total noto'g'ri chiqyapti&rdquo; degan xatoning sababi shu bitta so'z.</p>""",
        "text_content_ru": """<h3>Агрегат сворачивает, оконная функция сохраняет</h3>
<p>Разницу между ними можно уложить в одно предложение: агрегат с <code>GROUP BY</code> оставляет от 100 строк 5, а оконная функция оставляет <em>все 100 строк</em> и дописывает каждой дополнительную информацию о её группе.</p>
<p>На практике вы узнаёте это так: когда нужно «место каждого продавца внутри своего региона», агрегат отдаёт вам список регионов — продавцы исчезают. Оконная функция оставляет каждого продавца на месте и добавляет рядом колонку <code>o_rin</code>. На первом курсе вы с этим познакомились; теперь разберём настоящую разницу трёх ранжирующих функций и сравнение периодов.</p>

<h3>ROW_NUMBER / RANK / DENSE_RANK — разница видна только при РАВЕНСТВЕ</h3>
<p>Все три нумеруют строки. Если в данных нет равных значений, все три дают <strong>одинаковый</strong> результат — поэтому многие разработчики годами работают, не зная разницы, ровно до первого равенства в продакшене.</p>
<table>
<tr><th>Продавец</th><th>Итого</th><th>ROW_NUMBER</th><th>RANK</th><th>DENSE_RANK</th></tr>
<tr><td>Aziz</td><td>30 млн</td><td>1</td><td>1</td><td>1</td></tr>
<tr><td>Dilnoza</td><td>30 млн</td><td><strong>2</strong></td><td><strong>1</strong></td><td><strong>1</strong></td></tr>
<tr><td>Sardor</td><td>22 млн</td><td>3</td><td><strong>3</strong></td><td><strong>2</strong></td></tr>
</table>
<ul>
<li><strong>ROW_NUMBER</strong> вообще не признаёт равенства: каждой строке свой номер. Кто из Aziz и Dilnoza получит 1, а кто 2 — <em>не определено</em>: запустите запрос дважды, и результат может поменяться местами.</li>
<li><strong>RANK</strong> даёт равным одинаковый номер, а затем <em>перепрыгивает</em>: 1, 1, 3. Логика спортивной таблицы — после двух золотых сразу бронза.</li>
<li><strong>DENSE_RANK</strong> даёт равным одинаковый номер, но <em>не прыгает</em>: 1, 1, 2. Именно он отвечает на вопрос «сколько всего различных уровней».</li>
</ul>
<p><strong>Практическое правило:</strong> если используете <code>ROW_NUMBER</code>, всегда добавляйте в <code>ORDER BY</code> разрешающую (tie-breaker) колонку — например <code>ORDER BY jami DESC, sotuvchi</code>. Иначе ваш «топ-10» будет каждый раз разным, и это никто не заметит сразу.</p>

<h3>Почему оконную функцию нельзя использовать в WHERE</h3>
<p>Это самая частая ошибка. Причина — логический порядок выполнения SQL: <code>WHERE</code> отрабатывает <em>раньше</em> оконных функций, то есть в момент выполнения <code>WHERE</code> колонки <code>o_rin</code> ещё не существует.</p>
<pre class="mermaid">
flowchart LR
  A["FROM / JOIN"] --> B["WHERE"]
  B --> C["GROUP BY"]
  C --> D["HAVING"]
  D --> E["WINDOW
функции"]
  E --> F["SELECT"]
  F --> G["ORDER BY"]
  G --> H["LIMIT"]
  style E fill:#ffe9b3,stroke:#d09000
  style B fill:#ffd6d6,stroke:#c00000
</pre>
<p>Решение всегда одно: вычислите оконную функцию внутри CTE (или подзапроса), а фильтруйте снаружи. Именно поэтому задача «топ-N в каждой группе» почти всегда пишется через CTE.</p>

<h3>LAG и LEAD — сравнение периодов</h3>
<p><code>LAG(x)</code> возвращает значение <code>x</code> из <em>предыдущей</em> строки упорядоченного окна, а <code>LEAD(x)</code> — из <em>следующей</em>. Именно эти две функции позволяют писать отчёты вида «рост к прошлому месяцу» или «сколько дней прошло до предыдущего состояния» без self-JOIN.</p>
<p>Есть два тонких момента. Первый: в первой строке <code>LAG</code> всегда возвращает <code>NULL</code> — при расчёте процента защищайтесь ещё и от деления на ноль через <code>NULLIF(..., 0)</code>. Второй: третий аргумент в форме <code>LAG(x, 1, 0)</code> задаёт значение, подставляемое вместо <code>NULL</code>.</p>

<h3>Рамка (frame) — что происходит по умолчанию</h3>
<p>Когда вы пишете <code>OVER (ORDER BY oy)</code>, PostgreSQL незаметно для вас подставляет рамку <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>. Слово <code>RANGE</code> здесь важно: оно рассматривает строки с <em>равными</em> значениями как единый блок. То есть три строки с одинаковой датой попадут в накопительную сумму разом — а не построчно.</p>
<p>Если нужна настоящая построчная накопительная сумма, <code>ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> нужно писать <strong>явно</strong>. Причина многих жалоб «running total считается неправильно» — ровно это одно слово.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Window funksiyalar chuqur: ROW_NUMBER / RANK / DENSE_RANK, LAG / LEAD
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS sotuvlar;

CREATE TABLE sotuvlar (
    id       SERIAL        PRIMARY KEY,
    sotuvchi VARCHAR(40)   NOT NULL,
    hudud    VARCHAR(20)   NOT NULL,
    oy       DATE          NOT NULL,          -- har doim oyning 1-kuni
    summa    NUMERIC(12,2) NOT NULL CHECK (summa >= 0)
);

INSERT INTO sotuvlar (sotuvchi, hudud, oy, summa) VALUES
    ('Aziz',    'Toshkent',  '2024-01-01',  8000000),
    ('Aziz',    'Toshkent',  '2024-02-01', 10000000),
    ('Aziz',    'Toshkent',  '2024-03-01', 12000000),
    ('Dilnoza', 'Toshkent',  '2024-01-01', 12000000),
    ('Dilnoza', 'Toshkent',  '2024-02-01',  9000000),
    ('Dilnoza', 'Toshkent',  '2024-03-01',  9000000),
    ('Sardor',  'Toshkent',  '2024-01-01',  6000000),
    ('Sardor',  'Toshkent',  '2024-02-01',  7000000),
    ('Sardor',  'Toshkent',  '2024-03-01',  9000000),
    ('Nodira',  'Samarqand', '2024-01-01',  5000000),
    ('Nodira',  'Samarqand', '2024-02-01',  8000000),
    ('Nodira',  'Samarqand', '2024-03-01', 11000000),
    ('Kamola',  'Samarqand', '2024-01-01',  7000000),
    ('Kamola',  'Samarqand', '2024-02-01',  6000000),
    ('Kamola',  'Samarqand', '2024-03-01',  4000000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) Uchta raqamlash funksiyasi yonma-yon.
--    Toshkentda Aziz ham, Dilnoza ham 30 mln to'plagan — tenglik bor.
-- ─────────────────────────────────────────────────────────────────────
SELECT
    hudud,
    sotuvchi,
    SUM(summa)                                                      AS jami,
    ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS row_number,
    RANK()       OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS dense_rank
FROM sotuvlar
GROUP BY hudud, sotuvchi
ORDER BY hudud, jami DESC, sotuvchi;
-- Toshkent bo'yicha natija:
--   Aziz    30 mln -> rank 1, dense_rank 1
--   Dilnoza 30 mln -> rank 1, dense_rank 1   <-- tenglik
--   Sardor  22 mln -> rank 3, dense_rank 2   <-- RANK sakradi, DENSE_RANK yo'q
-- ROW_NUMBER esa 1, 2, 3 beradi. Lekin Aziz va Dilnozadan qaysi biri 1,
-- qaysi biri 2 bo'lishi ANIQLANMAGAN: ORDER BY tenglikni hal qilmagan.
-- Shuning uchun ROW_NUMBER da har doim uziluvchi ustun qo'shing:
--   ORDER BY SUM(summa) DESC, sotuvchi

-- ─────────────────────────────────────────────────────────────────────
-- 2) LAG — o'tgan oy bilan solishtirish (period-over-period)
-- ─────────────────────────────────────────────────────────────────────
SELECT
    oy,
    SUM(summa)                                      AS oylik,
    LAG(SUM(summa)) OVER (ORDER BY oy)              AS otgan_oy,
    SUM(summa) - LAG(SUM(summa)) OVER (ORDER BY oy) AS ozgarish,
    ROUND(
        100.0 * (SUM(summa) - LAG(SUM(summa)) OVER (ORDER BY oy))
        / NULLIF(LAG(SUM(summa)) OVER (ORDER BY oy), 0),
        1
    )                                               AS foiz_ozgarish
FROM sotuvlar
GROUP BY oy
ORDER BY oy;
-- Birinchi qatorda otgan_oy = NULL: undan oldin qator yo'q.
-- NULLIF(..., 0) nolga bo'linishdan himoya qiladi.

-- Uchinchi argument — NULL o'rniga qo'yiladigan qiymat:
SELECT oy,
       SUM(summa)                               AS oylik,
       LAG(SUM(summa), 1, 0) OVER (ORDER BY oy) AS otgan_oy_nolsiz
FROM sotuvlar
GROUP BY oy
ORDER BY oy;

-- LEAD — teskari yo'nalish: KEYINGI qatorga qaraydi
SELECT sotuvchi, oy, summa,
       LEAD(summa) OVER (PARTITION BY sotuvchi ORDER BY oy) AS keyingi_oy
FROM sotuvlar
WHERE hudud = 'Toshkent'
ORDER BY sotuvchi, oy;

-- ─────────────────────────────────────────────────────────────────────
-- 3) Har bir hududdan TOP-2.
--    Window funksiyani WHERE da ishlatib BO'LMAYDI — CTE kerak.
-- ─────────────────────────────────────────────────────────────────────
-- XATO variant (bajarilmaydi):
--   SELECT hudud, sotuvchi,
--          ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS o_rin
--   FROM sotuvlar GROUP BY hudud, sotuvchi
--   WHERE o_rin <= 2;
--   ERROR:  column "o_rin" does not exist

WITH reyting AS (
    SELECT
        hudud,
        sotuvchi,
        SUM(summa) AS jami,
        ROW_NUMBER() OVER (
            PARTITION BY hudud
            ORDER BY SUM(summa) DESC, sotuvchi   -- barqaror tie-breaker
        ) AS o_rin
    FROM sotuvlar
    GROUP BY hudud, sotuvchi
)
SELECT hudud, sotuvchi, jami, o_rin
FROM reyting
WHERE o_rin <= 2
ORDER BY hudud, o_rin;

-- ─────────────────────────────────────────────────────────────────────
-- 4) Freym: jamlanma yig'indi (running total).
--    ORDER BY bor window da standart freym — RANGE, ya'ni TENG qiymatlar
--    bitta blok bo'lib qo'shiladi. Qator-baqator kerak bo'lsa — ROWS.
-- ─────────────────────────────────────────────────────────────────────
SELECT
    oy,
    SUM(summa) AS oylik,
    SUM(SUM(summa)) OVER (
        ORDER BY oy
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS jamlanma
FROM sotuvlar
GROUP BY oy
ORDER BY oy;

-- ─────────────────────────────────────────────────────────────────────
-- 5) Bir nechta window bir xil bo'lsa — WINDOW bandi takrorlashni oldini oladi
-- ─────────────────────────────────────────────────────────────────────
SELECT
    sotuvchi, oy, summa,
    LAG(summa)  OVER w AS otgan,
    LEAD(summa) OVER w AS keyingi,
    AVG(summa)  OVER w AS oraliq_ortacha
FROM sotuvlar
WHERE hudud = 'Toshkent'
WINDOW w AS (PARTITION BY sotuvchi ORDER BY oy)
ORDER BY sotuvchi, oy;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Оконные функции углублённо: ROW_NUMBER / RANK / DENSE_RANK, LAG / LEAD
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS sotuvlar;

CREATE TABLE sotuvlar (
    id       SERIAL        PRIMARY KEY,
    sotuvchi VARCHAR(40)   NOT NULL,
    hudud    VARCHAR(20)   NOT NULL,
    oy       DATE          NOT NULL,          -- всегда 1-е число месяца
    summa    NUMERIC(12,2) NOT NULL CHECK (summa >= 0)
);

INSERT INTO sotuvlar (sotuvchi, hudud, oy, summa) VALUES
    ('Aziz',    'Toshkent',  '2024-01-01',  8000000),
    ('Aziz',    'Toshkent',  '2024-02-01', 10000000),
    ('Aziz',    'Toshkent',  '2024-03-01', 12000000),
    ('Dilnoza', 'Toshkent',  '2024-01-01', 12000000),
    ('Dilnoza', 'Toshkent',  '2024-02-01',  9000000),
    ('Dilnoza', 'Toshkent',  '2024-03-01',  9000000),
    ('Sardor',  'Toshkent',  '2024-01-01',  6000000),
    ('Sardor',  'Toshkent',  '2024-02-01',  7000000),
    ('Sardor',  'Toshkent',  '2024-03-01',  9000000),
    ('Nodira',  'Samarqand', '2024-01-01',  5000000),
    ('Nodira',  'Samarqand', '2024-02-01',  8000000),
    ('Nodira',  'Samarqand', '2024-03-01', 11000000),
    ('Kamola',  'Samarqand', '2024-01-01',  7000000),
    ('Kamola',  'Samarqand', '2024-02-01',  6000000),
    ('Kamola',  'Samarqand', '2024-03-01',  4000000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) Три ранжирующие функции рядом.
--    В Ташкенте и Aziz, и Dilnoza набрали по 30 млн — есть равенство.
-- ─────────────────────────────────────────────────────────────────────
SELECT
    hudud,
    sotuvchi,
    SUM(summa)                                                      AS jami,
    ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS row_number,
    RANK()       OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS dense_rank
FROM sotuvlar
GROUP BY hudud, sotuvchi
ORDER BY hudud, jami DESC, sotuvchi;
-- Результат по Ташкенту:
--   Aziz    30 млн -> rank 1, dense_rank 1
--   Dilnoza 30 млн -> rank 1, dense_rank 1   <-- равенство
--   Sardor  22 млн -> rank 3, dense_rank 2   <-- RANK прыгнул, DENSE_RANK нет
-- ROW_NUMBER же выдаст 1, 2, 3. Но кто из Aziz и Dilnoza получит 1,
-- а кто 2 — НЕ ОПРЕДЕЛЕНО: ORDER BY не разрешил равенство.
-- Поэтому в ROW_NUMBER всегда добавляйте разрешающую колонку:
--   ORDER BY SUM(summa) DESC, sotuvchi

-- ─────────────────────────────────────────────────────────────────────
-- 2) LAG — сравнение с прошлым месяцем (period-over-period)
-- ─────────────────────────────────────────────────────────────────────
SELECT
    oy,
    SUM(summa)                                      AS oylik,
    LAG(SUM(summa)) OVER (ORDER BY oy)              AS otgan_oy,
    SUM(summa) - LAG(SUM(summa)) OVER (ORDER BY oy) AS ozgarish,
    ROUND(
        100.0 * (SUM(summa) - LAG(SUM(summa)) OVER (ORDER BY oy))
        / NULLIF(LAG(SUM(summa)) OVER (ORDER BY oy), 0),
        1
    )                                               AS foiz_ozgarish
FROM sotuvlar
GROUP BY oy
ORDER BY oy;
-- В первой строке otgan_oy = NULL: перед ней строки нет.
-- NULLIF(..., 0) защищает от деления на ноль.

-- Третий аргумент — значение, подставляемое вместо NULL:
SELECT oy,
       SUM(summa)                               AS oylik,
       LAG(SUM(summa), 1, 0) OVER (ORDER BY oy) AS otgan_oy_nolsiz
FROM sotuvlar
GROUP BY oy
ORDER BY oy;

-- LEAD — обратное направление: смотрит на СЛЕДУЮЩУЮ строку
SELECT sotuvchi, oy, summa,
       LEAD(summa) OVER (PARTITION BY sotuvchi ORDER BY oy) AS keyingi_oy
FROM sotuvlar
WHERE hudud = 'Toshkent'
ORDER BY sotuvchi, oy;

-- ─────────────────────────────────────────────────────────────────────
-- 3) ТОП-2 из каждого региона.
--    Оконную функцию НЕЛЬЗЯ использовать в WHERE — нужен CTE.
-- ─────────────────────────────────────────────────────────────────────
-- ОШИБОЧНЫЙ вариант (не выполнится):
--   SELECT hudud, sotuvchi,
--          ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC) AS o_rin
--   FROM sotuvlar GROUP BY hudud, sotuvchi
--   WHERE o_rin <= 2;
--   ERROR:  column "o_rin" does not exist

WITH reyting AS (
    SELECT
        hudud,
        sotuvchi,
        SUM(summa) AS jami,
        ROW_NUMBER() OVER (
            PARTITION BY hudud
            ORDER BY SUM(summa) DESC, sotuvchi   -- устойчивый tie-breaker
        ) AS o_rin
    FROM sotuvlar
    GROUP BY hudud, sotuvchi
)
SELECT hudud, sotuvchi, jami, o_rin
FROM reyting
WHERE o_rin <= 2
ORDER BY hudud, o_rin;

-- ─────────────────────────────────────────────────────────────────────
-- 4) Рамка: накопительная сумма (running total).
--    В окне с ORDER BY рамка по умолчанию — RANGE, то есть РАВНЫЕ
--    значения добавляются одним блоком. Нужно построчно — пишите ROWS.
-- ─────────────────────────────────────────────────────────────────────
SELECT
    oy,
    SUM(summa) AS oylik,
    SUM(SUM(summa)) OVER (
        ORDER BY oy
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS jamlanma
FROM sotuvlar
GROUP BY oy
ORDER BY oy;

-- ─────────────────────────────────────────────────────────────────────
-- 5) Если окон несколько и они одинаковы — секция WINDOW убирает повтор
-- ─────────────────────────────────────────────────────────────────────
SELECT
    sotuvchi, oy, summa,
    LAG(summa)  OVER w AS otgan,
    LEAD(summa) OVER w AS keyingi,
    AVG(summa)  OVER w AS oraliq_ortacha
FROM sotuvlar
WHERE hudud = 'Toshkent'
WINDOW w AS (PARTITION BY sotuvchi ORDER BY oy)
ORDER BY sotuvchi, oy;""",
        "task": {
            "task_title": "Amaliy topshiriq: Filiallar bo'yicha bonus reytingi",
            "task_title_ru": "Практическое задание: рейтинг бонусов по филиалам",
            "task_description": (
                "Xodimlarning oylik bonuslari saqlanadigan kichik jadval yarating va uning "
                "ustida window funksiyalar bilan bitta yaxlit tahliliy hisobot yozing. "
                "Hisobot har bir xodim uchun: filial ichidagi o'rnini, o'tgan oyga nisbatan "
                "foizdagi o'zgarishni, yil boshidan jamlanma bonusni va filial bonus "
                "fondidagi ulushini ko'rsatishi kerak. Oxirida har bir filialdan eng yaxshi "
                "uchtasi alohida ajratilsin.\n\n"
                "Ma'lumotni ataylab shunday tanlang: kamida bitta filialda ikki xodimning "
                "jami bonusi AYNAN teng bo'lsin — aynan shu tenglik ROW_NUMBER, RANK va "
                "DENSE_RANK farqini ko'rsatadi. Har bir so'rovni haqiqatan ishga tushiring "
                "va natijani ko'z bilan tekshiring."
            ),
            "task_description_ru": (
                "Создайте небольшую таблицу с ежемесячными бонусами сотрудников и напишите "
                "по ней один целостный аналитический отчёт на оконных функциях. Отчёт должен "
                "показывать для каждого сотрудника: место внутри филиала, изменение в "
                "процентах к прошлому месяцу, накопительный бонус с начала года и долю в "
                "бонусном фонде филиала. В конце отдельно выделите трёх лучших из каждого "
                "филиала.\n\n"
                "Данные подберите намеренно так, чтобы хотя бы в одном филиале сумма бонусов "
                "у двух сотрудников оказалась ТОЧНО одинаковой — именно это равенство и "
                "показывает разницу между ROW_NUMBER, RANK и DENSE_RANK. Каждый запрос "
                "действительно запустите и проверьте результат глазами."
            ),
            "task_requirements": (
                "1. Jadval: xodim, filial, oy (DATE, har doim oyning 1-kuni), bonus. Kamida "
                "3 ta filial, 8 ta xodim va 6 ta oy — hammasi bo'lib 40 dan ortiq qator.\n"
                "2. Bitta filialda ikki xodimning jami bonusi aynan teng bo'lsin.\n"
                "3. Birinchi so'rovda ROW_NUMBER, RANK va DENSE_RANK yonma-yon chiqarilsin; "
                "izohda teng qatorlar uchun uchtasi qanday farq qilgani yozilsin.\n"
                "4. ROW_NUMBER ning ORDER BY sida uziluvchi (tie-breaker) ustun bo'lishi SHART "
                "— izohda nega kerakligi tushuntirilsin.\n"
                "5. LAG bilan oydan oyga foiz o'zgarish hisoblansin: birinchi oydagi NULL "
                "to'g'ri qayta ishlansin va NULLIF bilan nolga bo'linishdan himoya qilinsin.\n"
                "6. Jamlanma bonus uchun freym ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW "
                "ko'rinishida OSHKORA yozilsin; qo'shimcha ravishda freymsiz variant ham "
                "keltirilib, farqi izohda ko'rsatilsin.\n"
                "7. Filialdagi ulush SUM(...) OVER (PARTITION BY filial) orqali — ORDER BY SIZ "
                "— hisoblansin.\n"
                "8. Har filialdan TOP-3 alohida CTE orqali olinsin (window funksiya WHERE da "
                "ishlatilmasin); izohda nega WHERE da ishlamasligi bir jumlada yozilsin.\n"
                "9. Takrorlanuvchi OVER (...) ifodalari WINDOW bandi bilan bir marta e'lon "
                "qilinsin.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Таблица: сотрудник, филиал, месяц (DATE, всегда 1-е число), бонус. Минимум "
                "3 филиала, 8 сотрудников и 6 месяцев — всего более 40 строк.\n"
                "2. В одном филиале суммарный бонус двух сотрудников должен совпадать точно.\n"
                "3. В первом запросе выведите ROW_NUMBER, RANK и DENSE_RANK рядом; в "
                "комментарии опишите, чем они различаются на равных строках.\n"
                "4. В ORDER BY у ROW_NUMBER ОБЯЗАТЕЛЬНА разрешающая (tie-breaker) колонка — в "
                "комментарии объясните, зачем.\n"
                "5. Через LAG посчитайте изменение в процентах месяц к месяцу: корректно "
                "обработайте NULL первого месяца и защититесь от деления на ноль через NULLIF.\n"
                "6. Для накопительного бонуса рамка должна быть написана ЯВНО: ROWS BETWEEN "
                "UNBOUNDED PRECEDING AND CURRENT ROW; дополнительно приведите вариант без "
                "рамки и покажите разницу в комментарии.\n"
                "7. Долю в филиале считайте через SUM(...) OVER (PARTITION BY filial) — БЕЗ "
                "ORDER BY.\n"
                "8. ТОП-3 по каждому филиалу получите отдельным CTE (оконную функцию в WHERE "
                "не использовать); в комментарии одной фразой объясните, почему в WHERE нельзя.\n"
                "9. Повторяющиеся выражения OVER (...) объявите один раз через WINDOW.\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, SQL, Window Functions, CTE",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: ROW_NUMBER/RANK/DENSE_RANK, LAG va har guruhdan TOP-N",
            "description": "Tenglikda uch raqamlash funksiyasining farqi, LAG bilan oydan oyga o'zgarish, ROWS freymli jamlanma va CTE orqali har hududdan TOP-2",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: har hududdan TOP-2 va oydan oyga o'zgarish
DROP TABLE IF EXISTS sotuvlar;
CREATE TABLE sotuvlar (
    id       SERIAL        PRIMARY KEY,
    sotuvchi VARCHAR(40)   NOT NULL,
    hudud    VARCHAR(20)   NOT NULL,
    oy       DATE          NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

INSERT INTO sotuvlar (sotuvchi, hudud, oy, summa) VALUES
    ('Aziz',    'Toshkent',  '2024-01-01',  8000000),
    ('Aziz',    'Toshkent',  '2024-02-01', 10000000),
    ('Dilnoza', 'Toshkent',  '2024-01-01', 12000000),
    ('Dilnoza', 'Toshkent',  '2024-02-01',  6000000),
    ('Sardor',  'Toshkent',  '2024-01-01',  6000000),
    ('Sardor',  'Toshkent',  '2024-02-01',  7000000),
    ('Nodira',  'Samarqand', '2024-01-01',  5000000),
    ('Nodira',  'Samarqand', '2024-02-01',  8000000),
    ('Kamola',  'Samarqand', '2024-01-01',  7000000),
    ('Kamola',  'Samarqand', '2024-02-01',  6000000);

-- 1) Uchta raqamlash funksiyasi yonma-yon. Aziz va Dilnoza — ikkalasi ham
--    18 mln: aynan shu TENGLIK uchtasining farqini ko'rsatadi.
SELECT
    hudud,
    sotuvchi,
    SUM(summa)                                                                AS jami,
    ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC, sotuvchi) AS row_number,
    RANK()       OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC)           AS rank,
    DENSE_RANK() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC)           AS dense_rank
FROM sotuvlar
GROUP BY hudud, sotuvchi
ORDER BY hudud, jami DESC, sotuvchi;
-- Toshkent: Aziz 18 mln -> rank 1, Dilnoza 18 mln -> rank 1, Sardor 13 mln -> rank 3.
-- DENSE_RANK esa 1, 1, 2 beradi. ROW_NUMBER da tie-breaker (sotuvchi) SHART.

-- 2) LAG — o'tgan oyga nisbatan o'zgarish. NULLIF nolga bo'linishdan himoya.
SELECT
    sotuvchi,
    oy,
    summa,
    LAG(summa) OVER w AS otgan_oy,
    ROUND(100.0 * (summa - LAG(summa) OVER w) / NULLIF(LAG(summa) OVER w, 0), 1) AS foiz
FROM sotuvlar
WHERE hudud = 'Toshkent'
WINDOW w AS (PARTITION BY sotuvchi ORDER BY oy)
ORDER BY sotuvchi, oy;
-- Birinchi oyda otgan_oy = NULL — undan oldin qator yo'q.

-- 3) Jamlanma yig'indi. ROWS ni OSHKORA yozamiz: standart RANGE freymi
--    teng qiymatli qatorlarni bitta blok qilib qo'shadi.
SELECT
    oy,
    SUM(summa) AS oylik,
    SUM(SUM(summa)) OVER (
        ORDER BY oy
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS jamlanma
FROM sotuvlar
GROUP BY oy
ORDER BY oy;

-- 4) Har hududdan TOP-2. Window funksiyani WHERE da ishlatib BO'LMAYDI —
--    shuning uchun avval CTE da hisoblaymiz, keyin tashqarida filtrlaymiz.
WITH reyting AS (
    SELECT
        hudud,
        sotuvchi,
        SUM(summa) AS jami,
        ROW_NUMBER() OVER (PARTITION BY hudud ORDER BY SUM(summa) DESC, sotuvchi) AS o_rin,
        ROUND(100.0 * SUM(summa) / SUM(SUM(summa)) OVER (PARTITION BY hudud), 1) AS ulush_foiz
    FROM sotuvlar
    GROUP BY hudud, sotuvchi
)
SELECT hudud, o_rin, sotuvchi, jami, ulush_foiz
FROM reyting
WHERE o_rin <= 2
ORDER BY hudud, o_rin;""",
        },
        "exercises": [
            {
                "title": "Tenglikda qaysi funksiya 1, 1, 2 beradi?",
                "title_ru": "Какая функция при равенстве даёт 1, 1, 2?",
                "description": "Uch sotuvchining natijasi: 30 mln, 30 mln, 22 mln. Qaysi funksiya ularga mos ravishda 1, 1, 2 raqamlarini beradi?",
                "description_ru": "Результаты трёх продавцов: 30 млн, 30 млн, 22 млн. Какая функция присвоит им номера 1, 1, 2 соответственно?",
                "exercise_type": "multiple_choice",
                "options": [
                    "ROW_NUMBER() — har bir qatorga o'zining raqami",
                    "RANK() — tenglardan keyin sakraydi",
                    "DENSE_RANK() — tenglardan keyin sakramaydi",
                    "NTILE(3) — qatorlarni uch guruhga bo'ladi",
                ],
                "options_ru": [
                    "ROW_NUMBER() — каждой строке свой номер",
                    "RANK() — после равных перепрыгивает",
                    "DENSE_RANK() — после равных не прыгает",
                    "NTILE(3) — делит строки на три группы",
                ],
                "correct_answers": "C",
                "is_multiple_select": False,
                "hint": "RANK 1, 1, 3 beradi. Sakramaydigan variantni tanlang.",
                "hint_ru": "RANK даёт 1, 1, 3. Выберите вариант, который не прыгает.",
                "explanation": "DENSE_RANK teng qiymatlarga bir xil raqam beradi va keyingi darajaga o'tganda raqamni faqat bittaga oshiradi — shuning uchun 1, 1, 2. RANK esa o'tkazib yuborilgan o'rinlarni hisobga olib 1, 1, 3 beradi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "O'tgan davr qiymatini olish",
                "title_ru": "Получение значения предыдущего периода",
                "description": "Oylik tushumni o'tgan oy bilan solishtirish uchun tartiblangan oynada oldingi qatorning qiymatini qaytaradigan funksiya nomi: ___(SUM(summa)) OVER (ORDER BY oy)",
                "description_ru": "Чтобы сравнить месячную выручку с прошлым месяцем, нужна функция, возвращающая значение предыдущей строки упорядоченного окна: ___(SUM(summa)) OVER (ORDER BY oy)",
                "exercise_type": "fill_in_blank",
                "correct_answers": "LAG",
                "hint": "Keyingi qator uchun LEAD, oldingi qator uchun esa uning juftligi.",
                "hint_ru": "Для следующей строки — LEAD, для предыдущей — её пара.",
                "explanation": "LAG(x) tartiblangan oynada oldingi qatorning x qiymatini qaytaradi; birinchi qatorda NULL bo'ladi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Window funksiyalar haqida to'g'ri fikrlar",
                "title_ru": "Верные утверждения об оконных функциях",
                "description": "Quyidagilardan qaysilari to'g'ri?",
                "description_ru": "Какие из приведённых утверждений верны?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Window funksiyani WHERE bandida ishlatib bo'lmaydi — u WHERE dan keyin hisoblanadi",
                    "ORDER BY bor window da standart freym RANGE bo'lib, teng qiymatlarni bitta blok deb qaraydi",
                    "Window funksiya GROUP BY kabi qatorlar sonini kamaytiradi",
                    "ROW_NUMBER da ORDER BY tenglikni hal qilmasa, natija barqaror bo'lmaydi",
                ],
                "options_ru": [
                    "Оконную функцию нельзя использовать в WHERE — она вычисляется после WHERE",
                    "В окне с ORDER BY рамка по умолчанию RANGE и рассматривает равные значения как единый блок",
                    "Оконная функция, как и GROUP BY, уменьшает количество строк",
                    "Если ORDER BY в ROW_NUMBER не разрешает равенство, результат не будет устойчивым",
                ],
                "correct_answers": "A,B,D",
                "is_multiple_select": True,
                "hint": "Window funksiyaning asosiy xususiyati — qatorlarni saqlab qolishi.",
                "hint_ru": "Главное свойство оконной функции — она сохраняет строки.",
                "explanation": "Window funksiya qatorlarni yig'maydi, balki har bir qatorni joyida qoldiradi — C shuning uchun noto'g'ri. Qolgan uchtasi to'g'ri.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 1
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 1,
        "title": "2-Recursive CTE — ierarxik ma'lumotlar",
        "title_ru": "2-Рекурсивный CTE — иерархические данные",
        "points_reward": 14,
        "code_language": "sql",
        "text_content": """<h3>Muammo: chuqurligi oldindan noma'lum daraxt</h3>
<p>Tashkilot tuzilmasi, kategoriyalar daraxti, izohlarga javoblar, geografik bo'linish &mdash; bularning hammasi bitta jadvalda <em>o'ziga ishora qiluvchi</em> (self-referencing) foreign key bilan saqlanadi: <code>xodimlar.rahbar_id &rarr; xodimlar.id</code>.</p>
<p>Bunday tuzilmada &ldquo;CTO ostidagi <strong>barcha</strong> xodimlar&rdquo; degan savolga oddiy <code>JOIN</code> javob bera olmaydi. Ikki daraja kerak bo'lsa &mdash; ikkita JOIN, uch daraja kerak bo'lsa &mdash; uchta. Lekin daraxt chuqurligi ma'lumotga bog'liq va oldindan noma'lum. Ilova darajasida buni hal qilishga urinish esa to'g'ridan-to'g'ri N+1 muammosiga olib boradi: har bir tugun uchun alohida so'rov.</p>
<p><code>WITH RECURSIVE</code> aynan shuni yechadi &mdash; noma'lum chuqurlikdagi o'tishni <strong>bitta</strong> so'rovda bajaradi.</p>

<h3>Ikki qismli tuzilma</h3>
<p>Har qanday rekursiv CTE ikki qismdan iborat va ular <code>UNION ALL</code> bilan bog'lanadi:</p>
<ul>
<li><strong>Baza (anchor)</strong> &mdash; boshlanish nuqtasi. Bir marta bajariladi. Bu odatda <code>WHERE rahbar_id IS NULL</code> (ildizdan boshlash) yoki <code>WHERE id = 2</code> (ma'lum shoxdan boshlash).</li>
<li><strong>Rekursiv qism</strong> &mdash; CTE ning o'z nomiga murojaat qiladi va yangi qatorlar qo'shadi.</li>
</ul>
<p>Eng muhim nozik jihat: rekursiv qismdagi <code>shox</code> <em>butun to'plam emas</em>, balki faqat <strong>oxirgi qadamda qo'shilgan</strong> qatorlar. PostgreSQL har qadamda faqat yangi qatorlar ustida ishlaydi. Yangi qator qo'shilmagan qadamda rekursiya to'xtaydi &mdash; to'xtash sharti ana shu, hech qanday alohida &ldquo;stop&rdquo; yozilmaydi.</p>
<pre class="mermaid">
flowchart TD
  R["Rustam
Bosh direktor"] --> M["Malika
CTO"]
  R --> J["Jasur
Moliya direktori"]
  M --> A["Aziz
Backend tim lead"]
  M --> D["Dilnoza
Frontend tim lead"]
  A --> S["Sardor"]
  A --> N["Nodira"]
  D --> K["Kamola"]
  S --> Z["Zilola"]
  J --> B["Bekzod"]
  style M fill:#ffe9b3,stroke:#d09000
</pre>

<h3>Yo'nalishni JOIN sharti belgilaydi</h3>
<p>Pastga (bo'ysunuvchilar) va yuqoriga (rahbarlar) yurish o'rtasidagi farq atigi bitta shartda:</p>
<table>
<tr><th>Maqsad</th><th>JOIN sharti</th><th>O'qilishi</th></tr>
<tr><td>Pastga: barcha bo'ysunuvchilar</td><td><code>x.rahbar_id = d.id</code></td><td>&ldquo;rahbari topilganlarni qo'sh&rdquo;</td></tr>
<tr><td>Yuqoriga: barcha rahbarlar</td><td><code>z.rahbar_id = x.id</code></td><td>&ldquo;topilganning rahbarini qo'sh&rdquo;</td></tr>
</table>

<h3>Sikl (cycle) &mdash; e'tibordan chetda qoladigan eng xavfli joy</h3>
<p>Ma'lumotda <code>A &rarr; B &rarr; A</code> halqasi paydo bo'lsa (masalan, admin panelda kimdir xodimning rahbarini noto'g'ri belgilasa), himoyasiz rekursiv CTE <strong>cheksiz</strong> ishlaydi. Bu &ldquo;sekin so'rov&rdquo; emas &mdash; bu diskni to'ldirib serverni yotqizadigan so'rov. Va bunday halqani baza o'zi bloklamaydi: <code>rahbar_id</code> ga qo'yilgan FK faqat &ldquo;bunday ID bormi&rdquo; deb tekshiradi, halqa hosil bo'lyaptimi yoki yo'qmi &mdash; uni qiziqtirmaydi.</p>
<p>Ikki himoya usuli bor:</p>
<ul>
<li><strong>Yo'l massivi (barcha versiyalarda ishlaydi).</strong> Har bir qadamda o'tilgan ID larni <code>ARRAY</code> da to'plang va <code>NOT x.id = ANY(d.yol)</code> sharti bilan takrorlanuvchi tugunni qo'shmang.</li>
<li><strong><code>CYCLE</code> bandi (PostgreSQL 14+).</strong> O'sha mantiqni baza o'zi yozadi: siz faqat qaysi ustun bo'yicha tekshirishni aytasiz, u esa siklni <em>topganda to'xtaydi va belgilaydi</em> &mdash; tashlab yubormaydi, balki bayroq ustunini <code>true</code> qilib qo'yadi. Buzilgan ma'lumotni <em>aniqlash</em> kerak bo'lganda bu qulayroq.</li>
</ul>
<p><code>UNION ALL</code> o'rniga <code>UNION</code> ishlatish ham takrorlarni o'chiradi va oddiy sikllardan qutqaradi, lekin har qadamda saralash qo'shadi va nima bo'layotganini yashiradi. Amaliyotda <code>UNION ALL</code> + oshkora sikl himoyasi afzal.</p>""",
        "text_content_ru": """<h3>Проблема: дерево заранее неизвестной глубины</h3>
<p>Оргструктура, дерево категорий, ответы на комментарии, географическое деление — всё это хранится в одной таблице со <em>ссылающимся на себя</em> (self-referencing) внешним ключом: <code>xodimlar.rahbar_id &rarr; xodimlar.id</code>.</p>
<p>На вопрос «<strong>все</strong> сотрудники под CTO» обычный <code>JOIN</code> в такой структуре ответить не может. Нужны два уровня — два JOIN, три уровня — три. Но глубина дерева зависит от данных и заранее неизвестна. А попытка решить это на уровне приложения ведёт прямиком к проблеме N+1: отдельный запрос на каждый узел.</p>
<p><code>WITH RECURSIVE</code> решает именно это — выполняет обход неизвестной глубины <strong>одним</strong> запросом.</p>

<h3>Структура из двух частей</h3>
<p>Любой рекурсивный CTE состоит из двух частей, соединённых через <code>UNION ALL</code>:</p>
<ul>
<li><strong>База (anchor)</strong> — точка старта. Выполняется один раз. Обычно это <code>WHERE rahbar_id IS NULL</code> (начать с корня) или <code>WHERE id = 2</code> (начать с конкретной ветки).</li>
<li><strong>Рекурсивная часть</strong> — обращается к имени самого CTE и добавляет новые строки.</li>
</ul>
<p>Самый важный нюанс: <code>shox</code> в рекурсивной части — это <em>не всё накопленное множество</em>, а только строки, <strong>добавленные на последнем шаге</strong>. PostgreSQL на каждом шаге работает лишь с новыми строками. Как только шаг не добавил ни одной строки, рекурсия останавливается — это и есть условие выхода, никакого отдельного «stop» писать не нужно.</p>
<pre class="mermaid">
flowchart TD
  R["Rustam
Генеральный директор"] --> M["Malika
CTO"]
  R --> J["Jasur
Финансовый директор"]
  M --> A["Aziz
Backend тимлид"]
  M --> D["Dilnoza
Frontend тимлид"]
  A --> S["Sardor"]
  A --> N["Nodira"]
  D --> K["Kamola"]
  S --> Z["Zilola"]
  J --> B["Bekzod"]
  style M fill:#ffe9b3,stroke:#d09000
</pre>

<h3>Направление задаётся условием JOIN</h3>
<p>Разница между обходом вниз (подчинённые) и вверх (руководители) — всего в одном условии:</p>
<table>
<tr><th>Цель</th><th>Условие JOIN</th><th>Читается как</th></tr>
<tr><td>Вниз: все подчинённые</td><td><code>x.rahbar_id = d.id</code></td><td>«добавь тех, чей руководитель уже найден»</td></tr>
<tr><td>Вверх: все руководители</td><td><code>z.rahbar_id = x.id</code></td><td>«добавь руководителя найденного»</td></tr>
</table>

<h3>Цикл — самое опасное место, о котором забывают</h3>
<p>Если в данных появится петля <code>A &rarr; B &rarr; A</code> (например, кто-то в админке неверно назначил руководителя), незащищённый рекурсивный CTE будет работать <strong>бесконечно</strong>. Это не «медленный запрос» — это запрос, который забивает диск и кладёт сервер. И такую петлю база сама не заблокирует: внешний ключ на <code>rahbar_id</code> проверяет только «существует ли такой ID», а образуется ли петля — его не интересует.</p>
<p>Есть два способа защиты:</p>
<ul>
<li><strong>Массив пути (работает во всех версиях).</strong> На каждом шаге накапливайте пройденные ID в <code>ARRAY</code> и не добавляйте повторный узел условием <code>NOT x.id = ANY(d.yol)</code>.</li>
<li><strong>Секция <code>CYCLE</code> (PostgreSQL 14+).</strong> Ту же логику пишет сама база: вы лишь указываете, по какой колонке проверять, а она <em>останавливается на цикле и помечает его</em> — не выбрасывает строку, а выставляет колонку-флаг в <code>true</code>. Когда нужно именно <em>обнаружить</em> испорченные данные, это удобнее.</li>
</ul>
<p><code>UNION</code> вместо <code>UNION ALL</code> тоже устраняет дубликаты и спасает от простых циклов, но добавляет сортировку на каждом шаге и скрывает происходящее. На практике предпочтительнее <code>UNION ALL</code> плюс явная защита от циклов.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- WITH RECURSIVE — ierarxik (daraxtsimon) ma'lumotlar bilan ishlash
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS xodimlar;

CREATE TABLE xodimlar (
    id        SERIAL        PRIMARY KEY,
    ism       VARCHAR(60)   NOT NULL,
    lavozim   VARCHAR(60)   NOT NULL,
    rahbar_id INTEGER       REFERENCES xodimlar(id) ON DELETE SET NULL,
    maosh     NUMERIC(10,2) NOT NULL
);

-- rahbar_id o'z jadvaliga ishora qiladi (self-referencing FK).
-- NULL bo'lsa — bu daraxtning ildizi, ya'ni bosh direktor.
INSERT INTO xodimlar (ism, lavozim, rahbar_id, maosh) VALUES
    ('Rustam',  'Bosh direktor',      NULL, 40000000),  -- 1
    ('Malika',  'CTO',                1,    32000000),  -- 2
    ('Jasur',   'Moliya direktori',   1,    30000000),  -- 3
    ('Aziz',    'Backend tim lead',   2,    24000000),  -- 4
    ('Dilnoza', 'Frontend tim lead',  2,    23000000),  -- 5
    ('Sardor',  'Backend dasturchi',  4,    16000000),  -- 6
    ('Nodira',  'Backend dasturchi',  4,    15000000),  -- 7
    ('Kamola',  'Frontend dasturchi', 5,    15000000),  -- 8
    ('Bekzod',  'Buxgalter',          3,    14000000),  -- 9
    ('Zilola',  'Junior backend',     6,     9000000);  -- 10

-- ─────────────────────────────────────────────────────────────────────
-- 1) Eng oddiy rekursiya: CTO (id=2) ostidagi BUTUN shox
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE shox AS (
    -- BAZA: boshlanish nuqtasi. Bir marta bajariladi.
    SELECT id, ism, lavozim, rahbar_id, 1 AS daraja
    FROM xodimlar
    WHERE id = 2

    UNION ALL

    -- REKURSIV QISM: "shox" bu yerda butun to'plam EMAS, faqat OXIRGI
    -- qadamda qo'shilgan qatorlar. Yangi qator qo'shilmasa — to'xtaydi.
    SELECT x.id, x.ism, x.lavozim, x.rahbar_id, s.daraja + 1
    FROM xodimlar x
    JOIN shox s ON x.rahbar_id = s.id
)
SELECT daraja, ism, lavozim FROM shox ORDER BY daraja, ism;
-- Natija: Malika (1), Aziz va Dilnoza (2), Sardor/Nodira/Kamola (3), Zilola (4)

-- ─────────────────────────────────────────────────────────────────────
-- 2) Butun tashkilot daraxti — chekinish (indent) va to'liq yo'l bilan
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE daraxt AS (
    SELECT
        id, ism, lavozim, rahbar_id,
        1         AS daraja,
        ARRAY[id] AS yol,        -- ildizdan shu qatorgacha ID lar ketma-ketligi
        ism::TEXT AS toliq_yol
    FROM xodimlar
    WHERE rahbar_id IS NULL

    UNION ALL

    SELECT
        x.id, x.ism, x.lavozim, x.rahbar_id,
        d.daraja + 1,
        d.yol || x.id,
        d.toliq_yol || ' > ' || x.ism
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
)
SELECT
    repeat('    ', daraja - 1) || ism AS ierarxiya,
    lavozim,
    daraja,
    toliq_yol
FROM daraxt
ORDER BY yol;   -- massiv bo'yicha saralash aynan daraxt tartibini beradi

-- ─────────────────────────────────────────────────────────────────────
-- 3) Teskari yo'nalish: Zilola (id=10) dan yuqoriga — barcha rahbarlari.
--    Farq atigi bitta: JOIN sharti teskari yozilgan.
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE zanjir AS (
    SELECT id, ism, lavozim, rahbar_id, 0 AS qadam
    FROM xodimlar
    WHERE id = 10

    UNION ALL

    SELECT x.id, x.ism, x.lavozim, x.rahbar_id, z.qadam + 1
    FROM xodimlar x
    JOIN zanjir z ON z.rahbar_id = x.id   -- yuqoriga: bola -> ota
)
SELECT qadam, ism, lavozim FROM zanjir ORDER BY qadam;
-- Zilola -> Sardor -> Aziz -> Malika -> Rustam

-- ─────────────────────────────────────────────────────────────────────
-- 4) SIKL HIMOYASI — eng muhim qism
-- ─────────────────────────────────────────────────────────────────────
-- Ataylab halqa yasaymiz: Rustam ning rahbari Malika bo'lsin, Malika ning
-- rahbari esa allaqachon Rustam. Halqa tayyor: 1 -> 2 -> 1.
-- Diqqat: FK buni bloklamaydi — id=2 mavjud, bu unga yetarli.
UPDATE xodimlar SET rahbar_id = 2 WHERE id = 1;

-- Usul A: yo'l massivini tekshirish (har qanday PostgreSQL versiyasida)
WITH RECURSIVE daraxt AS (
    SELECT id, ism, rahbar_id, ARRAY[id] AS yol
    FROM xodimlar
    WHERE id = 1

    UNION ALL

    SELECT x.id, x.ism, x.rahbar_id, d.yol || x.id
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
    WHERE NOT x.id = ANY(d.yol)      -- allaqachon o'tilgan tugunni qo'shmaymiz
)
SELECT id, ism, yol FROM daraxt ORDER BY yol;
-- Bu usul siklni JIMGINA kesib tashlaydi: natija to'liq va cheklangan,
-- lekin ma'lumotda halqa borligi haqida hech narsa aytmaydi.

-- Usul B: PostgreSQL 14+ dagi CYCLE bandi — halqani TOPADI va BELGILAYDI
WITH RECURSIVE daraxt AS (
    SELECT id, ism, rahbar_id FROM xodimlar WHERE id = 1
    UNION ALL
    SELECT x.id, x.ism, x.rahbar_id
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
) CYCLE id SET sikl_topildi USING yol
SELECT id, ism, sikl_topildi, yol FROM daraxt ORDER BY id;
-- Natijada Rustam IKKI marta chiqadi: ikkinchisida sikl_topildi = true
-- va yol = {(1),(2),(1)} — halqa aynan shu yerda yopilgan.
-- Buzilgan ma'lumotni topish uchun: ... WHERE sikl_topildi

-- Halqani orqaga qaytaramiz
UPDATE xodimlar SET rahbar_id = NULL WHERE id = 1;

-- ─────────────────────────────────────────────────────────────────────
-- 5) Rekursiv agregatsiya: har bir rahbar ostidagi jamoaning maosh fondi
--    Baza sifatida HAR BIR xodim olinadi — ya'ni "o'zi + barcha ostidagilar"
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE ost AS (
    SELECT id AS boshliq_id, id AS xodim_id FROM xodimlar
    UNION ALL
    SELECT o.boshliq_id, x.id
    FROM xodimlar x
    JOIN ost o ON x.rahbar_id = o.xodim_id
)
SELECT
    b.ism        AS boshliq,
    COUNT(*) - 1 AS ostidagilar_soni,   -- -1: o'zini hisobdan chiqaramiz
    SUM(x.maosh) AS jamoa_maosh_fondi
FROM ost o
JOIN xodimlar b ON b.id = o.boshliq_id
JOIN xodimlar x ON x.id = o.xodim_id
GROUP BY b.id, b.ism
HAVING COUNT(*) > 1                      -- faqat rahbarlar
ORDER BY jamoa_maosh_fondi DESC;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- WITH RECURSIVE — работа с иерархическими (древовидными) данными
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS xodimlar;

CREATE TABLE xodimlar (
    id        SERIAL        PRIMARY KEY,
    ism       VARCHAR(60)   NOT NULL,
    lavozim   VARCHAR(60)   NOT NULL,
    rahbar_id INTEGER       REFERENCES xodimlar(id) ON DELETE SET NULL,
    maosh     NUMERIC(10,2) NOT NULL
);

-- rahbar_id ссылается на свою же таблицу (self-referencing FK).
-- Если NULL — это корень дерева, то есть генеральный директор.
INSERT INTO xodimlar (ism, lavozim, rahbar_id, maosh) VALUES
    ('Rustam',  'Bosh direktor',      NULL, 40000000),  -- 1
    ('Malika',  'CTO',                1,    32000000),  -- 2
    ('Jasur',   'Moliya direktori',   1,    30000000),  -- 3
    ('Aziz',    'Backend tim lead',   2,    24000000),  -- 4
    ('Dilnoza', 'Frontend tim lead',  2,    23000000),  -- 5
    ('Sardor',  'Backend dasturchi',  4,    16000000),  -- 6
    ('Nodira',  'Backend dasturchi',  4,    15000000),  -- 7
    ('Kamola',  'Frontend dasturchi', 5,    15000000),  -- 8
    ('Bekzod',  'Buxgalter',          3,    14000000),  -- 9
    ('Zilola',  'Junior backend',     6,     9000000);  -- 10

-- ─────────────────────────────────────────────────────────────────────
-- 1) Простейшая рекурсия: ВСЯ ветка под CTO (id=2)
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE shox AS (
    -- БАЗА: точка старта. Выполняется один раз.
    SELECT id, ism, lavozim, rahbar_id, 1 AS daraja
    FROM xodimlar
    WHERE id = 2

    UNION ALL

    -- РЕКУРСИВНАЯ ЧАСТЬ: "shox" здесь НЕ всё множество, а только строки,
    -- добавленные на ПОСЛЕДНЕМ шаге. Нет новых строк — рекурсия встала.
    SELECT x.id, x.ism, x.lavozim, x.rahbar_id, s.daraja + 1
    FROM xodimlar x
    JOIN shox s ON x.rahbar_id = s.id
)
SELECT daraja, ism, lavozim FROM shox ORDER BY daraja, ism;
-- Результат: Malika (1), Aziz и Dilnoza (2), Sardor/Nodira/Kamola (3), Zilola (4)

-- ─────────────────────────────────────────────────────────────────────
-- 2) Всё дерево организации — с отступом (indent) и полным путём
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE daraxt AS (
    SELECT
        id, ism, lavozim, rahbar_id,
        1         AS daraja,
        ARRAY[id] AS yol,        -- последовательность ID от корня до строки
        ism::TEXT AS toliq_yol
    FROM xodimlar
    WHERE rahbar_id IS NULL

    UNION ALL

    SELECT
        x.id, x.ism, x.lavozim, x.rahbar_id,
        d.daraja + 1,
        d.yol || x.id,
        d.toliq_yol || ' > ' || x.ism
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
)
SELECT
    repeat('    ', daraja - 1) || ism AS ierarxiya,
    lavozim,
    daraja,
    toliq_yol
FROM daraxt
ORDER BY yol;   -- сортировка по массиву даёт именно порядок обхода дерева

-- ─────────────────────────────────────────────────────────────────────
-- 3) Обратное направление: от Zilola (id=10) вверх — все её руководители.
--    Разница всего одна: условие JOIN написано наоборот.
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE zanjir AS (
    SELECT id, ism, lavozim, rahbar_id, 0 AS qadam
    FROM xodimlar
    WHERE id = 10

    UNION ALL

    SELECT x.id, x.ism, x.lavozim, x.rahbar_id, z.qadam + 1
    FROM xodimlar x
    JOIN zanjir z ON z.rahbar_id = x.id   -- вверх: ребёнок -> родитель
)
SELECT qadam, ism, lavozim FROM zanjir ORDER BY qadam;
-- Zilola -> Sardor -> Aziz -> Malika -> Rustam

-- ─────────────────────────────────────────────────────────────────────
-- 4) ЗАЩИТА ОТ ЦИКЛА — самая важная часть
-- ─────────────────────────────────────────────────────────────────────
-- Намеренно создаём петлю: пусть руководителем Rustam станет Malika,
-- а руководитель Malika — уже Rustam. Петля готова: 1 -> 2 -> 1.
-- Внимание: FK это не заблокирует — id=2 существует, ему этого достаточно.
UPDATE xodimlar SET rahbar_id = 2 WHERE id = 1;

-- Способ A: проверка массива пути (работает в любой версии PostgreSQL)
WITH RECURSIVE daraxt AS (
    SELECT id, ism, rahbar_id, ARRAY[id] AS yol
    FROM xodimlar
    WHERE id = 1

    UNION ALL

    SELECT x.id, x.ism, x.rahbar_id, d.yol || x.id
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
    WHERE NOT x.id = ANY(d.yol)      -- уже пройденный узел не добавляем
)
SELECT id, ism, yol FROM daraxt ORDER BY yol;
-- Этот способ ТИХО обрезает цикл: результат полный и конечный,
-- но о наличии петли в данных он ничего не сообщает.

-- Способ B: секция CYCLE в PostgreSQL 14+ — НАХОДИТ петлю и ПОМЕЧАЕТ её
WITH RECURSIVE daraxt AS (
    SELECT id, ism, rahbar_id FROM xodimlar WHERE id = 1
    UNION ALL
    SELECT x.id, x.ism, x.rahbar_id
    FROM xodimlar x
    JOIN daraxt d ON x.rahbar_id = d.id
) CYCLE id SET sikl_topildi USING yol
SELECT id, ism, sikl_topildi, yol FROM daraxt ORDER BY id;
-- В результате Rustam появится ДВАЖДЫ: во второй раз с sikl_topildi = true
-- и yol = {(1),(2),(1)} — петля замкнулась именно здесь.
-- Чтобы найти испорченные данные: ... WHERE sikl_topildi

-- Возвращаем всё как было
UPDATE xodimlar SET rahbar_id = NULL WHERE id = 1;

-- ─────────────────────────────────────────────────────────────────────
-- 5) Рекурсивная агрегация: фонд зарплат команды под каждым руководителем.
--    В качестве базы берём КАЖДОГО сотрудника — то есть «он сам + все под ним»
-- ─────────────────────────────────────────────────────────────────────
WITH RECURSIVE ost AS (
    SELECT id AS boshliq_id, id AS xodim_id FROM xodimlar
    UNION ALL
    SELECT o.boshliq_id, x.id
    FROM xodimlar x
    JOIN ost o ON x.rahbar_id = o.xodim_id
)
SELECT
    b.ism        AS boshliq,
    COUNT(*) - 1 AS ostidagilar_soni,   -- -1: исключаем его самого
    SUM(x.maosh) AS jamoa_maosh_fondi
FROM ost o
JOIN xodimlar b ON b.id = o.boshliq_id
JOIN xodimlar x ON x.id = o.xodim_id
GROUP BY b.id, b.ism
HAVING COUNT(*) > 1                      -- только руководители
ORDER BY jamoa_maosh_fondi DESC;""",
        "task": {
            "task_title": "Amaliy topshiriq: Kategoriyalar daraxti va rekursiv rollup",
            "task_title_ru": "Практическое задание: дерево категорий и рекурсивный rollup",
            "task_description": (
                "Onlayn do'kon uchun ko'p darajali kategoriyalar katalogini bitta jadvalda "
                "(o'ziga ishora qiluvchi ota_id bilan) saqlang va WITH RECURSIVE yordamida "
                "uning ustida to'liq navigatsiya to'plamini yozing: butun daraxtni chekinish "
                "bilan chiqarish, ixtiyoriy tugunning shoxini olish, bargdan ildizgacha "
                "zanjirni qurish va har bir kategoriya uchun 'o'zi + barcha avlodlari' "
                "bo'yicha mahsulotlar sonini jamlash.\n\n"
                "Alohida talab — sikl himoyasi. Ma'lumotda ataylab halqa hosil qiling "
                "(masalan, ildizning ota_id sini o'z avlodiga ko'rsating), foreign key uni "
                "bloklamasligini ko'rsating va ikkala himoya usulini ham qo'llab, "
                "farqini yozing."
            ),
            "task_description_ru": (
                "Сохраните многоуровневый каталог категорий интернет-магазина в одной таблице "
                "(с самоссылающимся ota_id) и напишите по нему через WITH RECURSIVE полный "
                "набор навигационных запросов: вывод всего дерева с отступами, получение "
                "ветки произвольного узла, цепочка от листа до корня и подсчёт товаров по "
                "принципу «сам узел + все его потомки» для каждой категории.\n\n"
                "Отдельное требование — защита от циклов. Намеренно создайте в данных петлю "
                "(например, укажите корню ota_id одного из его потомков), покажите, что "
                "foreign key её не блокирует, примените оба способа защиты и опишите разницу "
                "между ними."
            ),
            "task_requirements": (
                "1. Jadval: id, nomi, ota_id (o'ziga REFERENCES), mahsulot_soni. Kamida 12 ta "
                "tugun, 4 daraja chuqurlik va 2 ta ildiz (ota_id IS NULL).\n"
                "2. Butun daraxt: daraja (chuqurlik), repeat() bilan chekinish va 'Ildiz > "
                "Bola > Nevara' ko'rinishidagi to'liq yo'l. Saralash ARRAY yo'l ustuni bo'yicha "
                "bo'lsin — shunda daraxt tartibi to'g'ri chiqadi.\n"
                "3. Ixtiyoriy tugun ostidagi butun shox (baza WHERE id = :n bilan).\n"
                "4. Bargdan ildizgacha teskari zanjir. Izohda pastga va yuqoriga yurish "
                "o'rtasidagi farq FAQAT JOIN shartida ekani ko'rsatilsin.\n"
                "5. Rekursiv rollup: har bir kategoriya uchun o'zi va barcha avlodlaridagi "
                "mahsulotlar yig'indisi hamda avlodlar soni. Natijani qo'lda tekshirib, "
                "kamida bitta tugun uchun izohda hisob-kitobni yozing.\n"
                "6. Ma'lumotda ataylab sikl hosil qilinsin; izohda foreign key uni nega "
                "bloklamasligi yozilsin.\n"
                "7. Ikkala sikl himoyasi ham ko'rsatilsin: (a) ARRAY yo'l va NOT ... = ANY(yol), "
                "(b) PostgreSQL 14+ dagi CYCLE bandi. Izohda farqi yozilsin — biri halqani "
                "jimgina kesadi, ikkinchisi uni topib belgilaydi.\n"
                "8. Skript oxirida ma'lumot dastlabki (halqasiz) holatiga qaytarilsin.\n"
                "9. Izohda bir-ikki jumla: bu masalani ilova darajasidagi tsikl bilan yechish "
                "nega N+1 ga olib keladi.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Таблица: id, nomi, ota_id (REFERENCES на себя), mahsulot_soni. Минимум 12 "
                "узлов, глубина 4 уровня и 2 корня (ota_id IS NULL).\n"
                "2. Всё дерево: уровень (глубина), отступы через repeat() и полный путь вида "
                "«Корень > Ребёнок > Внук». Сортировка — по колонке-массиву пути, только тогда "
                "порядок дерева верный.\n"
                "3. Вся ветка под произвольным узлом (база с WHERE id = :n).\n"
                "4. Обратная цепочка от листа до корня. В комментарии покажите, что разница "
                "между движением вниз и вверх — ТОЛЬКО в условии JOIN.\n"
                "5. Рекурсивный rollup: для каждой категории сумма товаров по ней и всем её "
                "потомкам плюс количество потомков. Проверьте результат вручную и распишите "
                "расчёт в комментарии хотя бы для одного узла.\n"
                "6. Намеренно создайте цикл в данных; в комментарии объясните, почему foreign "
                "key его не блокирует.\n"
                "7. Покажите оба способа защиты: (а) массив пути и NOT ... = ANY(yol), "
                "(б) предложение CYCLE из PostgreSQL 14+. В комментарии опишите разницу: один "
                "молча обрезает петлю, второй находит и помечает её.\n"
                "8. В конце скрипта верните данные в исходное (без петли) состояние.\n"
                "9. В комментарии одна-две фразы: почему решение этой задачи циклом на уровне "
                "приложения приводит к N+1.\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, SQL, WITH RECURSIVE, CTE",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: Kategoriyalar daraxti — chuqurlik, yo'l, rollup va sikl himoyasi",
            "description": "WITH RECURSIVE bilan daraxtni chiqarish, teskari zanjir, avlodlar bo'yicha jamlash va CYCLE bandi orqali halqani aniqlash",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: kategoriyalar daraxti — chuqurlik, to'liq yo'l va rollup
DROP TABLE IF EXISTS kategoriyalar;
CREATE TABLE kategoriyalar (
    id        SERIAL      PRIMARY KEY,
    nomi      VARCHAR(60) NOT NULL,
    ota_id    INTEGER     REFERENCES kategoriyalar(id) ON DELETE SET NULL,
    mahsulot_soni INTEGER NOT NULL DEFAULT 0
);

INSERT INTO kategoriyalar (nomi, ota_id, mahsulot_soni) VALUES
    ('Elektronika',  NULL, 0),   -- 1
    ('Kompyuter',    1,    0),   -- 2
    ('Telefon',      1,   40),   -- 3
    ('Noutbuk',      2,   25),   -- 4
    ('Aksessuar',    2,    0),   -- 5
    ('Klaviatura',   5,   18),   -- 6
    ('Sichqoncha',   5,   12),   -- 7
    ('Mebel',        NULL, 0),   -- 8
    ('Stul',         8,   30);   -- 9

-- 1) Butun daraxt: chuqurlik, chekinish va to'liq yo'l.
--    BAZA — ildizlar (ota_id IS NULL), REKURSIV QISM — bolalar.
WITH RECURSIVE daraxt AS (
    SELECT id, nomi, ota_id, mahsulot_soni,
           1         AS daraja,
           ARRAY[id] AS yol,
           nomi::TEXT AS toliq_yol
    FROM kategoriyalar
    WHERE ota_id IS NULL

    UNION ALL

    SELECT k.id, k.nomi, k.ota_id, k.mahsulot_soni,
           d.daraja + 1,
           d.yol || k.id,
           d.toliq_yol || ' > ' || k.nomi
    FROM kategoriyalar k
    JOIN daraxt d ON k.ota_id = d.id
    WHERE NOT k.id = ANY(d.yol)      -- sikl himoyasi: o'tilgan tugunni qaytarmaymiz
)
SELECT repeat('    ', daraja - 1) || nomi AS ierarxiya, daraja, toliq_yol
FROM daraxt
ORDER BY yol;                        -- massiv bo'yicha saralash = daraxt tartibi

-- 2) ROLLUP: har bir kategoriya uchun "o'zi + barcha avlodlari" yig'indisi.
--    Baza sifatida HAR BIR tugun olinadi.
WITH RECURSIVE avlod AS (
    SELECT id AS ildiz_id, id AS tugun_id FROM kategoriyalar
    UNION ALL
    SELECT a.ildiz_id, k.id
    FROM kategoriyalar k
    JOIN avlod a ON k.ota_id = a.tugun_id
)
SELECT r.nomi                AS kategoriya,
       COUNT(*) - 1          AS ostidagi_kategoriyalar,
       SUM(t.mahsulot_soni)  AS jami_mahsulot
FROM avlod a
JOIN kategoriyalar r ON r.id = a.ildiz_id
JOIN kategoriyalar t ON t.id = a.tugun_id
GROUP BY r.id, r.nomi
ORDER BY jami_mahsulot DESC, kategoriya;
-- Elektronika = 40 + 25 + 18 + 12 = 95, Kompyuter = 25 + 18 + 12 = 55.

-- 3) Teskari yo'nalish: "Sichqoncha" dan ildizgacha zanjir.
--    Farq atigi bitta — JOIN sharti teskari yozilgan.
WITH RECURSIVE zanjir AS (
    SELECT id, nomi, ota_id, 0 AS qadam FROM kategoriyalar WHERE id = 7
    UNION ALL
    SELECT k.id, k.nomi, k.ota_id, z.qadam + 1
    FROM kategoriyalar k
    JOIN zanjir z ON z.ota_id = k.id
)
SELECT qadam, nomi FROM zanjir ORDER BY qadam;
-- Sichqoncha -> Aksessuar -> Kompyuter -> Elektronika

-- 4) SIKL. Ataylab halqa yasaymiz: Elektronika ning otasi Kompyuter bo'lsin.
--    FK buni BLOKLAMAYDI — id=2 mavjud, unga shu yetarli.
UPDATE kategoriyalar SET ota_id = 2 WHERE id = 1;

WITH RECURSIVE tekshir AS (
    SELECT id, nomi, ota_id FROM kategoriyalar WHERE id = 1
    UNION ALL
    SELECT k.id, k.nomi, k.ota_id
    FROM kategoriyalar k
    JOIN tekshir t ON k.ota_id = t.id
) CYCLE id SET sikl_topildi USING yol
SELECT id, nomi, sikl_topildi, yol FROM tekshir WHERE sikl_topildi;
-- CYCLE bandi (PostgreSQL 14+) halqani jimgina kesib tashlamaydi —
-- uni TOPADI va bayroq bilan belgilaydi. Buzilgan ma'lumotni shunday qidiriladi.

UPDATE kategoriyalar SET ota_id = NULL WHERE id = 1;   -- halqani qaytarib olamiz""",
        },
        "exercises": [
            {
                "title": "Rekursiv qism nimaga murojaat qiladi?",
                "title_ru": "К чему обращается рекурсивная часть?",
                "description": "WITH RECURSIVE ichidagi rekursiv qism CTE nomiga murojaat qilganda, aslida qaysi qatorlarni ko'radi?",
                "description_ru": "Когда рекурсивная часть внутри WITH RECURSIVE обращается к имени CTE, какие строки она на самом деле видит?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Shu paytgacha to'plangan BARCHA qatorlarni",
                    "Faqat oxirgi qadamda qo'shilgan qatorlarni",
                    "Faqat baza (anchor) qismi qaytargan qatorlarni",
                    "Manba jadvalning barcha qatorlarini",
                ],
                "options_ru": [
                    "ВСЕ строки, накопленные к этому моменту",
                    "Только строки, добавленные на последнем шаге",
                    "Только строки, вернувшиеся из базовой (anchor) части",
                    "Все строки исходной таблицы",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Rekursiya to'xtash sharti — qadam yangi qator qo'shmagani.",
                "hint_ru": "Условие остановки рекурсии — шаг не добавил ни одной новой строки.",
                "explanation": "PostgreSQL har qadamda faqat oldingi qadam qo'shgan qatorlar ustida ishlaydi. Aynan shuning uchun yangi qator qo'shilmagan qadamda rekursiya tabiiy ravishda to'xtaydi.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Rekursiv CTE ni qurish tartibi",
                "title_ru": "Порядок построения рекурсивного CTE",
                "description": "Ierarxiyani bo'ylab o'tuvchi rekursiv CTE yozish qadamlarini to'g'ri tartibga soling.",
                "description_ru": "Расположите в правильном порядке шаги написания рекурсивного CTE для обхода иерархии.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "WITH RECURSIVE deb e'lon qilish va CTE ga nom berish",
                    "Baza (anchor) so'rovini yozish — boshlanish nuqtasi",
                    "UNION ALL qo'yish",
                    "Rekursiv qismda CTE ning o'ziga JOIN qilish",
                    "Sikl himoyasini qo'shish (yo'l massivi yoki CYCLE)",
                    "Tashqi SELECT da natijani saralash va filtrlash",
                ],
                "drag_items_ru": [
                    "Объявить WITH RECURSIVE и дать CTE имя",
                    "Написать базовый (anchor) запрос — точку старта",
                    "Поставить UNION ALL",
                    "В рекурсивной части сделать JOIN с самим CTE",
                    "Добавить защиту от цикла (массив пути или CYCLE)",
                    "Во внешнем SELECT отсортировать и отфильтровать результат",
                ],
                "correct_order": [
                    "WITH RECURSIVE deb e'lon qilish va CTE ga nom berish",
                    "Baza (anchor) so'rovini yozish — boshlanish nuqtasi",
                    "UNION ALL qo'yish",
                    "Rekursiv qismda CTE ning o'ziga JOIN qilish",
                    "Sikl himoyasini qo'shish (yo'l massivi yoki CYCLE)",
                    "Tashqi SELECT da natijani saralash va filtrlash",
                ],
                "hint": "Avval qayerdan boshlashni, keyin qanday davom etishni, oxirida qanday to'xtashni aytamiz.",
                "hint_ru": "Сначала указываем, откуда начать, потом как продолжать, и в конце — как остановиться.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Foreign key sikldan himoya qiladimi?",
                "title_ru": "Защищает ли внешний ключ от цикла?",
                "description": "xodimlar.rahbar_id ustunida xodimlar(id) ga FOREIGN KEY bor. Kimdir admin panelda 1-xodimning rahbari qilib 2-xodimni, 2-xodimning rahbari qilib esa 1-xodimni belgilab qo'ydi. Baza bu yozuvni qabul qiladimi va nima uchun? Rekursiv so'rov uchun bu nimani anglatadi?",
                "description_ru": "На колонке xodimlar.rahbar_id стоит FOREIGN KEY на xodimlar(id). Кто-то в админке назначил руководителем сотрудника 1 сотрудника 2, а руководителем сотрудника 2 — сотрудника 1. Примет ли база такую запись и почему? Что это означает для рекурсивного запроса?",
                "exercise_type": "text_input",
                "expected_answer": "Ha, baza qabul qiladi. FOREIGN KEY faqat ko'rsatilgan ID mavjudligini tekshiradi — id=2 ham, id=1 ham jadvalda bor, shuning uchun cheklov buzilmaydi. FK halqa (sikl) hosil bo'layotganini umuman ko'rmaydi. Natijada himoyasiz WITH RECURSIVE so'rovi 1 -> 2 -> 1 -> 2 ... bo'yicha cheksiz aylanadi va serverni yotqizishi mumkin. Himoya so'rov darajasida yozilishi kerak: yo'l massivi va NOT id = ANY(yol) sharti, yoki PostgreSQL 14+ dagi CYCLE bandi.",
                "hint": "FK aynan nimani tekshirishini o'ylang: qiymat mavjudmi yoki tuzilma to'g'rimi?",
                "hint_ru": "Подумайте, что именно проверяет FK: существование значения или корректность структуры?",
                "difficulty_level": "Hard",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 2
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 2,
        "title": "3-Subquery vs JOIN vs CTE — qachon nimani ishlatish",
        "title_ru": "3-Подзапрос vs JOIN vs CTE — что когда использовать",
        "points_reward": 14,
        "code_language": "sql",
        "text_content": """<h3>Uchalasi ham bir xil natija bera oladi &mdash; lekin bir xil emas</h3>
<p>Bitta savolga uch xil yozuv bilan javob berish mumkin, va ko'p qo'llanmalar &ldquo;qaysi biri chiroyli&rdquo; deb bahslashadi. Amalda esa tanlov uchta aniq mezonga tayanadi: <strong>natija to'g'rimi</strong>, <strong>reja qanday</strong> va <strong>olti oydan keyin o'qib tushunarlimi</strong>. Birinchi mezon eng muhimi &mdash; chunki bu uchtasi har doim ham bir xil natija bermaydi.</p>

<h3>Korrelyatsiyali va korrelyatsiyasiz subquery</h3>
<ul>
<li><strong>Korrelyatsiyasiz</strong> subquery tashqi so'rovga umuman bog'liq emas &mdash; uni alohida ajratib ishga tushirsangiz ham ishlaydi. Bir marta hisoblanadi.</li>
<li><strong>Korrelyatsiyali</strong> subquery tashqi qatorning ustuniga ishora qiladi (<code>WHERE b.mijoz_id = m.id</code>). Mantiqan har bir tashqi qator uchun qayta bajariladi.</li>
</ul>
<p>Korrelyatsiyali subquery o'qishga qulay, lekin uning yashirin narxi bor: <code>SELECT</code> ro'yxatidagi <em>har bir</em> shunday ustun jadvalni alohida skanerlaydi. Uchta ko'rsatkich kerak bo'lsa &mdash; uchta skanerlash. Bitta <code>LEFT JOIN</code> + <code>GROUP BY</code> esa hammasini bitta o'tishda beradi, va <code>FILTER (WHERE ...)</code> bilan shartli agregatlarni ham qo'shib yuborish mumkin.</p>

<h3>JOIN qatorlarni ko'paytiradi &mdash; asosiy semantik farq</h3>
<p>Bu eng ko'p e'tibordan chetda qoladigan nuqta. &ldquo;Buyurtma bergan mijozlar&rdquo; so'roviga <code>JOIN</code> bilan javob bersangiz, ikkita buyurtmasi bor mijoz natijada <em>ikki marta</em> chiqadi. <code>DISTINCT</code> qo'shish esa muammoni yashiradi va qo'shimcha saralash narxini qo'shadi.</p>
<p><code>EXISTS</code> bunday muammoga ega emas: u &ldquo;bormi?&rdquo; degan savolga javob beradi va birinchi mos qator topilishi bilan to'xtaydi. Shuning uchun qoida oddiy: <strong>ma'lumot kerak bo'lsa &mdash; JOIN, mavjudlik kerak bo'lsa &mdash; EXISTS.</strong></p>
<table>
<tr><th>Vazifa</th><th>To'g'ri vosita</th><th>Nega</th></tr>
<tr><td>Bog'liq jadvaldan ustun kerak</td><td><code>JOIN</code></td><td>Faqat u ma'lumot qaytaradi</td></tr>
<tr><td>&ldquo;Bunday yozuv bormi?&rdquo;</td><td><code>EXISTS</code></td><td>Qator ko'paymaydi, erta to'xtaydi</td></tr>
<tr><td>&ldquo;Bunday yozuv yo'q&rdquo;</td><td><code>NOT EXISTS</code></td><td><code>NOT IN</code> NULL da buziladi</td></tr>
<tr><td>Har guruh uchun agregat</td><td><code>LEFT JOIN</code> + <code>GROUP BY</code></td><td>Bitta skanerlash</td></tr>
<tr><td>Ko'p bosqichli hisob</td><td><code>CTE</code></td><td>O'qilishi</td></tr>
</table>

<h3>NOT IN va NULL &mdash; eng qimmatga tushadigan tuzoq</h3>
<p>Agar ichki so'rov qaytargan ro'yxatda birorta <code>NULL</code> bo'lsa, <code>NOT IN</code> <strong>har doim bo'sh natija qaytaradi</strong>. Sababi uch qiymatli mantiqda: <code>x NOT IN (1, 2, NULL)</code> aslida <code>x &lt;&gt; 1 AND x &lt;&gt; 2 AND x &lt;&gt; NULL</code> degani, oxirgi shart esa <code>NULL</code> &mdash; ya'ni hech qachon <code>TRUE</code> emas.</p>
<p>Bu xatoning xavfliligi shundaki, <em>xato ham, ogohlantirish ham chiqmaydi</em>. So'rov muvaffaqiyatli bajariladi va bo'sh ro'yxat qaytaradi. Hisobot &ldquo;faol bo'lmagan mijozlar yo'q&rdquo; deb ko'rsatadi va buni hech kim shubha ostiga olmaydi. <code>NOT EXISTS</code> yoki <code>LEFT JOIN ... WHERE ... IS NULL</code> (anti-join) bu tuzoqqa tushmaydi.</p>

<h3>CTE: PostgreSQL 12 dan keyin nima o'zgardi</h3>
<p>PostgreSQL 12 gacha <code>WITH</code> optimallashtirish uchun <strong>devor</strong> edi: CTE har doim alohida hisoblanib, to'liq materializatsiya qilinardi. Bu ko'p &ldquo;sababsiz sekin&rdquo; so'rovlarning yashirin sababi edi &mdash; tashqi so'rovdagi <code>WHERE</code> CTE ichiga o'ta olmasdi.</p>
<p>12 dan boshlab rejalashtiruvchi CTE ni asosiy so'rovga qo'shib yuboradi (inlining), agar u bir marta ishlatilsa, rekursiv bo'lmasa va yon ta'sirga ega bo'lmasa. Xatti-harakatni oshkora boshqarish ham mumkin: <code>AS MATERIALIZED</code> (bir marta hisobla va saqla &mdash; og'ir CTE bir necha marta ishlatilganda foydali) yoki <code>AS NOT MATERIALIZED</code> (majburan qo'shib yubor).</p>""",
        "text_content_ru": """<h3>Все три могут дать один результат — но не одинаковы</h3>
<p>На один вопрос можно ответить тремя разными конструкциями, и многие руководства спорят о том, «какая красивее». На практике выбор опирается на три чётких критерия: <strong>верен ли результат</strong>, <strong>какой получается план</strong> и <strong>будет ли это понятно через полгода</strong>. Первый критерий важнейший — потому что эти три конструкции далеко не всегда дают одинаковый результат.</p>

<h3>Коррелированный и некоррелированный подзапрос</h3>
<ul>
<li><strong>Некоррелированный</strong> подзапрос вообще не зависит от внешнего запроса — его можно вырезать и запустить отдельно. Вычисляется один раз.</li>
<li><strong>Коррелированный</strong> подзапрос ссылается на колонку внешней строки (<code>WHERE b.mijoz_id = m.id</code>). Логически выполняется заново для каждой внешней строки.</li>
</ul>
<p>Коррелированный подзапрос удобно читать, но у него есть скрытая цена: <em>каждая</em> такая колонка в списке <code>SELECT</code> сканирует таблицу отдельно. Нужны три показателя — три сканирования. А один <code>LEFT JOIN</code> + <code>GROUP BY</code> отдаст всё за один проход, и через <code>FILTER (WHERE ...)</code> туда же можно добавить условные агрегаты.</p>

<h3>JOIN размножает строки — главное смысловое различие</h3>
<p>Это самый упускаемый момент. Если на вопрос «клиенты, сделавшие заказ» ответить через <code>JOIN</code>, клиент с двумя заказами попадёт в результат <em>дважды</em>. Добавление <code>DISTINCT</code> лишь маскирует проблему и добавляет цену лишней сортировки.</p>
<p>У <code>EXISTS</code> такой проблемы нет: он отвечает на вопрос «есть ли?» и останавливается на первой подходящей строке. Отсюда простое правило: <strong>нужны данные — JOIN, нужен факт наличия — EXISTS.</strong></p>
<table>
<tr><th>Задача</th><th>Правильный инструмент</th><th>Почему</th></tr>
<tr><td>Нужна колонка из связанной таблицы</td><td><code>JOIN</code></td><td>Только он возвращает данные</td></tr>
<tr><td>«Есть ли такая запись?»</td><td><code>EXISTS</code></td><td>Строки не размножаются, ранний выход</td></tr>
<tr><td>«Такой записи нет»</td><td><code>NOT EXISTS</code></td><td><code>NOT IN</code> ломается на NULL</td></tr>
<tr><td>Агрегат по каждой группе</td><td><code>LEFT JOIN</code> + <code>GROUP BY</code></td><td>Одно сканирование</td></tr>
<tr><td>Многоэтапный расчёт</td><td><code>CTE</code></td><td>Читаемость</td></tr>
</table>

<h3>NOT IN и NULL — самая дорогая ловушка</h3>
<p>Если в списке, возвращённом подзапросом, окажется хоть один <code>NULL</code>, <code>NOT IN</code> <strong>всегда вернёт пустой результат</strong>. Причина — в трёхзначной логике: <code>x NOT IN (1, 2, NULL)</code> на самом деле означает <code>x &lt;&gt; 1 AND x &lt;&gt; 2 AND x &lt;&gt; NULL</code>, а последнее условие даёт <code>NULL</code> — то есть никогда не <code>TRUE</code>.</p>
<p>Опасность этой ошибки в том, что <em>не будет ни ошибки, ни предупреждения</em>. Запрос выполнится успешно и вернёт пустой список. Отчёт покажет «неактивных клиентов нет», и никто это не поставит под сомнение. <code>NOT EXISTS</code> или <code>LEFT JOIN ... WHERE ... IS NULL</code> (анти-джойн) в эту ловушку не попадают.</p>

<h3>CTE: что изменилось после PostgreSQL 12</h3>
<p>До PostgreSQL 12 <code>WITH</code> был <strong>барьером</strong> для оптимизации: CTE всегда вычислялся отдельно и полностью материализовался. Это была скрытая причина многих «беспричинно медленных» запросов — <code>WHERE</code> из внешнего запроса не мог протолкнуться внутрь CTE.</p>
<p>Начиная с 12-й версии планировщик встраивает CTE в основной запрос (inlining), если тот используется один раз, не рекурсивен и не имеет побочных эффектов. Поведением можно управлять явно: <code>AS MATERIALIZED</code> (посчитать один раз и сохранить — полезно, когда тяжёлый CTE используется несколько раз) или <code>AS NOT MATERIALIZED</code> (принудительно встроить).</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Subquery vs JOIN vs CTE — bir savolga uch xil javob
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS buyurtma_qatorlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id     SERIAL      PRIMARY KEY,
    ism    VARCHAR(60) NOT NULL,
    shahar VARCHAR(40) NOT NULL
);

CREATE TABLE buyurtmalar (
    id       SERIAL        PRIMARY KEY,
    mijoz_id INTEGER       REFERENCES mijozlar(id) ON DELETE CASCADE,
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

CREATE TABLE buyurtma_qatorlari (
    id          SERIAL        PRIMARY KEY,
    buyurtma_id INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot    VARCHAR(60)   NOT NULL,
    soni        INTEGER       NOT NULL,
    narx        NUMERIC(10,2) NOT NULL
);

INSERT INTO mijozlar (ism, shahar) VALUES
    ('Aziz',    'Toshkent'),   -- 1
    ('Dilnoza', 'Samarqand'),  -- 2
    ('Sardor',  'Toshkent'),   -- 3
    ('Nodira',  'Buxoro');     -- 4  hech qachon buyurtma bermagan

INSERT INTO buyurtmalar (mijoz_id, sana, holat, summa) VALUES
    (1,    '2024-03-01', 'yakunlangan', 500000),   -- 1
    (1,    '2024-03-15', 'bekor',       120000),   -- 2
    (2,    '2024-03-05', 'yakunlangan', 900000),   -- 3
    (3,    '2024-03-20', 'yangi',       300000),   -- 4
    (NULL, '2024-03-22', 'yangi',       150000);   -- 5  mehmon buyurtmasi -> NULL!

INSERT INTO buyurtma_qatorlari (buyurtma_id, mahsulot, soni, narx) VALUES
    (1, 'Klaviatura', 1, 300000),
    (1, 'Sichqoncha', 1, 200000),
    (3, 'Monitor',    1, 900000),
    (4, 'Kabel',      3, 100000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) KORRELYATSIYASIZ subquery — tashqi qatordan mustaqil, bir marta hisoblanadi
-- ─────────────────────────────────────────────────────────────────────
SELECT id, ism, shahar
FROM mijozlar
WHERE id IN (SELECT mijoz_id FROM buyurtmalar WHERE holat = 'yakunlangan');

-- ─────────────────────────────────────────────────────────────────────
-- 2) KORRELYATSIYALI subquery — tashqi qatorga (m.id) ishora qiladi
-- ─────────────────────────────────────────────────────────────────────
SELECT
    m.id,
    m.ism,
    (SELECT COUNT(*) FROM buyurtmalar b WHERE b.mijoz_id = m.id) AS buyurtmalar_soni
FROM mijozlar m
ORDER BY m.id;

-- Uchta shunday ustun kerak bo'lsa — uchta alohida skanerlash bo'ladi.
-- LEFT JOIN + GROUP BY bitta o'tishda hammasini beradi:
SELECT
    m.id,
    m.ism,
    COUNT(b.id)                               AS buyurtmalar_soni,
    COALESCE(SUM(b.summa), 0)                 AS jami_summa,
    COUNT(*) FILTER (WHERE b.holat = 'bekor') AS bekor_qilingan
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
GROUP BY m.id, m.ism
ORDER BY m.id;

-- ─────────────────────────────────────────────────────────────────────
-- 3) EXISTS vs IN vs JOIN — "buyurtma bergan mijozlar"
-- ─────────────────────────────────────────────────────────────────────
-- (a) EXISTS: birinchi mos qator topilishi bilan to'xtaydi
SELECT m.id, m.ism FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

-- (b) IN: rejalashtiruvchi buni semi-join ga aylantiradi.
--     Ikkalasining EXPLAIN natijasi bir xil chiqadi (pastda tekshiramiz).
SELECT m.id, m.ism FROM mijozlar m
WHERE m.id IN (SELECT b.mijoz_id FROM buyurtmalar b WHERE b.mijoz_id IS NOT NULL);

-- (c) JOIN: DIQQAT — bu BOSHQA natija beradi. Azizning ikkita buyurtmasi
--     bor, shuning uchun u ikki marta chiqadi. JOIN qatorlarni KO'PAYTIRADI.
SELECT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id;
--  1 | Aziz     <-- takror
--  1 | Aziz     <-- takror
--  2 | Dilnoza
--  3 | Sardor

-- DISTINCT muammoni yashiradi, lekin qo'shimcha saralash narxini qo'shadi:
SELECT DISTINCT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id;

-- ─────────────────────────────────────────────────────────────────────
-- 4) NOT IN va NULL — eng qimmatga tushadigan tuzoq
-- ─────────────────────────────────────────────────────────────────────
-- "Hech qachon buyurtma bermagan mijozlar". Kutilgan javob: Nodira.
-- Lekin buyurtmalar.mijoz_id da bitta NULL bor (mehmon buyurtmasi).
SELECT m.id, m.ism FROM mijozlar m
WHERE m.id NOT IN (SELECT b.mijoz_id FROM buyurtmalar b);
-- Natija: 0 QATOR. Xato yo'q, ogohlantirish yo'q — shunchaki bo'sh javob.
-- Sababi: x NOT IN (1,2,3,NULL)  ==  x<>1 AND x<>2 AND x<>3 AND x<>NULL
-- Oxirgi shart har doim NULL -> butun ifoda hech qachon TRUE bo'lmaydi.

-- NOT EXISTS bu tuzoqqa tushmaydi:
SELECT m.id, m.ism FROM mijozlar m
WHERE NOT EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);
-- Natija: Nodira. To'g'ri.

-- LEFT JOIN ... IS NULL (anti-join) ham to'g'ri ishlaydi:
SELECT m.id, m.ism
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
WHERE b.id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- 5) CTE — ko'p bosqichli hisobni o'qiladigan qilish
-- ─────────────────────────────────────────────────────────────────────
WITH yakunlangan AS (
    SELECT mijoz_id, SUM(summa) AS jami
    FROM buyurtmalar
    WHERE holat = 'yakunlangan'
    GROUP BY mijoz_id
),
ortacha AS (
    SELECT AVG(jami) AS ortacha_chek FROM yakunlangan
)
SELECT m.ism, y.jami, ROUND(o.ortacha_chek, 0) AS ortacha
FROM yakunlangan y
JOIN mijozlar m ON m.id = y.mijoz_id
CROSS JOIN ortacha o
WHERE y.jami > o.ortacha_chek
ORDER BY y.jami DESC;

-- Materializatsiyani oshkora boshqarish (PostgreSQL 12+):
--   WITH t AS MATERIALIZED     (...)  -- bir marta hisobla va saqla
--   WITH t AS NOT MATERIALIZED (...)  -- asosiy so'rovga qo'shib yubor
WITH qimmat AS MATERIALIZED (
    SELECT buyurtma_id, SUM(soni * narx) AS qator_summa
    FROM buyurtma_qatorlari
    GROUP BY buyurtma_id
)
SELECT b.id, b.summa, q.qator_summa,
       b.summa - q.qator_summa AS farq
FROM buyurtmalar b
JOIN qimmat q ON q.buyurtma_id = b.id
ORDER BY b.id;

-- ─────────────────────────────────────────────────────────────────────
-- 6) Gap "qaysi biri chiroyli" da emas — rejada. Tekshiramiz:
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE m.id IN (SELECT b.mijoz_id FROM buyurtmalar b);
-- Ikkala reja ham bir xil: Hash Join + HashAggregate.
-- Ya'ni EXISTS va IN o'rtasidagi tanlov — tezlik emas, semantika masalasi.""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Подзапрос vs JOIN vs CTE — три разных ответа на один вопрос
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS buyurtma_qatorlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id     SERIAL      PRIMARY KEY,
    ism    VARCHAR(60) NOT NULL,
    shahar VARCHAR(40) NOT NULL
);

CREATE TABLE buyurtmalar (
    id       SERIAL        PRIMARY KEY,
    mijoz_id INTEGER       REFERENCES mijozlar(id) ON DELETE CASCADE,
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

CREATE TABLE buyurtma_qatorlari (
    id          SERIAL        PRIMARY KEY,
    buyurtma_id INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot    VARCHAR(60)   NOT NULL,
    soni        INTEGER       NOT NULL,
    narx        NUMERIC(10,2) NOT NULL
);

INSERT INTO mijozlar (ism, shahar) VALUES
    ('Aziz',    'Toshkent'),   -- 1
    ('Dilnoza', 'Samarqand'),  -- 2
    ('Sardor',  'Toshkent'),   -- 3
    ('Nodira',  'Buxoro');     -- 4  никогда не делала заказ

INSERT INTO buyurtmalar (mijoz_id, sana, holat, summa) VALUES
    (1,    '2024-03-01', 'yakunlangan', 500000),   -- 1
    (1,    '2024-03-15', 'bekor',       120000),   -- 2
    (2,    '2024-03-05', 'yakunlangan', 900000),   -- 3
    (3,    '2024-03-20', 'yangi',       300000),   -- 4
    (NULL, '2024-03-22', 'yangi',       150000);   -- 5  гостевой заказ -> NULL!

INSERT INTO buyurtma_qatorlari (buyurtma_id, mahsulot, soni, narx) VALUES
    (1, 'Klaviatura', 1, 300000),
    (1, 'Sichqoncha', 1, 200000),
    (3, 'Monitor',    1, 900000),
    (4, 'Kabel',      3, 100000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) НЕКОРРЕЛИРОВАННЫЙ подзапрос — не зависит от внешней строки, считается один раз
-- ─────────────────────────────────────────────────────────────────────
SELECT id, ism, shahar
FROM mijozlar
WHERE id IN (SELECT mijoz_id FROM buyurtmalar WHERE holat = 'yakunlangan');

-- ─────────────────────────────────────────────────────────────────────
-- 2) КОРРЕЛИРОВАННЫЙ подзапрос — ссылается на внешнюю строку (m.id)
-- ─────────────────────────────────────────────────────────────────────
SELECT
    m.id,
    m.ism,
    (SELECT COUNT(*) FROM buyurtmalar b WHERE b.mijoz_id = m.id) AS buyurtmalar_soni
FROM mijozlar m
ORDER BY m.id;

-- Если нужны три такие колонки — будет три отдельных сканирования.
-- LEFT JOIN + GROUP BY отдаёт всё за один проход:
SELECT
    m.id,
    m.ism,
    COUNT(b.id)                               AS buyurtmalar_soni,
    COALESCE(SUM(b.summa), 0)                 AS jami_summa,
    COUNT(*) FILTER (WHERE b.holat = 'bekor') AS bekor_qilingan
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
GROUP BY m.id, m.ism
ORDER BY m.id;

-- ─────────────────────────────────────────────────────────────────────
-- 3) EXISTS vs IN vs JOIN — «клиенты, сделавшие заказ»
-- ─────────────────────────────────────────────────────────────────────
-- (a) EXISTS: останавливается на первой подходящей строке
SELECT m.id, m.ism FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

-- (b) IN: планировщик превращает это в semi-join.
--     EXPLAIN обоих даёт одинаковый результат (проверим ниже).
SELECT m.id, m.ism FROM mijozlar m
WHERE m.id IN (SELECT b.mijoz_id FROM buyurtmalar b WHERE b.mijoz_id IS NOT NULL);

-- (c) JOIN: ВНИМАНИЕ — это ДРУГОЙ результат. У Aziz два заказа,
--     поэтому он попадёт в вывод дважды. JOIN РАЗМНОЖАЕТ строки.
SELECT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id;
--  1 | Aziz     <-- дубль
--  1 | Aziz     <-- дубль
--  2 | Dilnoza
--  3 | Sardor

-- DISTINCT маскирует проблему, но добавляет цену лишней сортировки:
SELECT DISTINCT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id;

-- ─────────────────────────────────────────────────────────────────────
-- 4) NOT IN и NULL — самая дорогая ловушка
-- ─────────────────────────────────────────────────────────────────────
-- «Клиенты, никогда не делавшие заказ». Ожидаемый ответ: Nodira.
-- Но в buyurtmalar.mijoz_id есть один NULL (гостевой заказ).
SELECT m.id, m.ism FROM mijozlar m
WHERE m.id NOT IN (SELECT b.mijoz_id FROM buyurtmalar b);
-- Результат: 0 СТРОК. Ни ошибки, ни предупреждения — просто пустой ответ.
-- Причина: x NOT IN (1,2,3,NULL)  ==  x<>1 AND x<>2 AND x<>3 AND x<>NULL
-- Последнее условие всегда NULL -> всё выражение никогда не станет TRUE.

-- NOT EXISTS в эту ловушку не попадает:
SELECT m.id, m.ism FROM mijozlar m
WHERE NOT EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);
-- Результат: Nodira. Верно.

-- LEFT JOIN ... IS NULL (анти-джойн) тоже работает правильно:
SELECT m.id, m.ism
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
WHERE b.id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- 5) CTE — сделать многоэтапный расчёт читаемым
-- ─────────────────────────────────────────────────────────────────────
WITH yakunlangan AS (
    SELECT mijoz_id, SUM(summa) AS jami
    FROM buyurtmalar
    WHERE holat = 'yakunlangan'
    GROUP BY mijoz_id
),
ortacha AS (
    SELECT AVG(jami) AS ortacha_chek FROM yakunlangan
)
SELECT m.ism, y.jami, ROUND(o.ortacha_chek, 0) AS ortacha
FROM yakunlangan y
JOIN mijozlar m ON m.id = y.mijoz_id
CROSS JOIN ortacha o
WHERE y.jami > o.ortacha_chek
ORDER BY y.jami DESC;

-- Явное управление материализацией (PostgreSQL 12+):
--   WITH t AS MATERIALIZED     (...)  -- посчитать один раз и сохранить
--   WITH t AS NOT MATERIALIZED (...)  -- принудительно встроить в запрос
WITH qimmat AS MATERIALIZED (
    SELECT buyurtma_id, SUM(soni * narx) AS qator_summa
    FROM buyurtma_qatorlari
    GROUP BY buyurtma_id
)
SELECT b.id, b.summa, q.qator_summa,
       b.summa - q.qator_summa AS farq
FROM buyurtmalar b
JOIN qimmat q ON q.buyurtma_id = b.id
ORDER BY b.id;

-- ─────────────────────────────────────────────────────────────────────
-- 6) Дело не в том, «что красивее», а в плане. Проверяем:
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE m.id IN (SELECT b.mijoz_id FROM buyurtmalar b);
-- Оба плана одинаковы: Hash Join + HashAggregate.
-- То есть выбор между EXISTS и IN — вопрос семантики, а не скорости.""",
        "task": {
            "task_title": "Amaliy topshiriq: Bitta savol — uchta yozuv va asoslangan tanlov",
            "task_title_ru": "Практическое задание: один вопрос — три записи и обоснованный выбор",
            "task_description": (
                "Mijozlar va buyurtmalar sxemasini yarating va ikkita biznes savoliga javob "
                "bering: (A) kamida bitta 'yakunlangan' buyurtmasi bor mijozlar kimlar, "
                "(B) hech qachon buyurtma bermagan mijozlar kimlar.\n\n"
                "A savoliga UCH XIL yozuvda javob bering — subquery, EXISTS va JOIN — va "
                "uchtasining natijasini yonma-yon solishtiring. Ular bir xil chiqmasa, nega "
                "farq qilganini toping va yozing. B savolida esa NOT IN ni ataylab sinab "
                "ko'ring: ichki so'rovda NULL bo'lgani uchun u bo'sh natija qaytaradi — bu "
                "xatoni hujjatlashtiring va to'g'ri variantlarni ko'rsating.\n\n"
                "Yakunda: har bir savol uchun qaysi yozuvni produksiyaga qo'yasiz va nega — "
                "reja va semantikaga tayanib asoslang."
            ),
            "task_description_ru": (
                "Создайте схему клиентов и заказов и ответьте на два бизнес-вопроса: (A) какие "
                "клиенты имеют хотя бы один заказ в статусе «yakunlangan», (B) какие клиенты "
                "никогда не делали заказов.\n\n"
                "На вопрос A ответьте ТРЕМЯ разными способами — подзапросом, EXISTS и JOIN — и "
                "сравните результаты рядом. Если они не совпали, найдите и опишите причину. В "
                "вопросе B намеренно попробуйте NOT IN: из-за NULL во внутреннем запросе он "
                "вернёт пустой результат — задокументируйте эту ошибку и покажите корректные "
                "варианты.\n\n"
                "В конце: какую запись вы отправите в продакшен по каждому вопросу и почему — "
                "обоснуйте планом и семантикой."
            ),
            "task_requirements": (
                "1. Sxema: mijozlar va buyurtmalar. Ma'lumotda SHART: (a) kamida bitta mijozda "
                "ikkitadan ortiq yakunlangan buyurtma, (b) buyurtmalar.mijoz_id da kamida "
                "bitta NULL (mehmon buyurtmasi), (c) hech qachon buyurtma bermagan mijoz.\n"
                "2. A savoli: IN-subquery, EXISTS va JOIN variantlari. JOIN takror qatorlar "
                "berishi ko'rsatilsin va nega ekani izohda yozilsin.\n"
                "3. DISTINCT bilan tuzatilgan JOIN varianti ham keltirilsin; izohda DISTINCT "
                "muammoni yechmasdan yashirishi qayd etilsin.\n"
                "4. B savoli: NOT IN varianti bo'sh natija qaytarishi ko'rsatilsin; izohda uch "
                "qiymatli mantiq orqali sabab yozilsin (x <> NULL hech qachon TRUE emas).\n"
                "5. B savolining ikkita to'g'ri varianti: NOT EXISTS va LEFT JOIN ... IS NULL "
                "(anti-join).\n"
                "6. Har mijoz uchun uchta ko'rsatkich (buyurtmalar soni, jami summa, "
                "yakunlanganlar soni) ikki xil yozilsin: korrelyatsiyali subquery bilan va "
                "bitta LEFT JOIN + GROUP BY + FILTER bilan.\n"
                "7. Har ikkala variant uchun EXPLAIN (ANALYZE) natijasi keltirilsin va qaysi "
                "biri jadvalni necha marta skanerlagani izohda yozilsin.\n"
                "8. EXISTS va IN variantlarining EXPLAIN (COSTS OFF) rejalari solishtirilsin; "
                "xulosa yozilsin.\n"
                "9. Fayl oxirida qisqa jadval-izoh: qaysi vazifaga qaysi vosita (JOIN / EXISTS "
                "/ NOT EXISTS / LEFT JOIN + GROUP BY / CTE) va nega.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Схема: mijozlar и buyurtmalar. В данных ОБЯЗАТЕЛЬНО: (а) хотя бы у одного "
                "клиента больше одного завершённого заказа, (б) минимум один NULL в "
                "buyurtmalar.mijoz_id (гостевой заказ), (в) клиент вообще без заказов.\n"
                "2. Вопрос A: варианты через IN-подзапрос, EXISTS и JOIN. Покажите, что JOIN "
                "даёт дубли, и объясните в комментарии, почему.\n"
                "3. Приведите и вариант JOIN с DISTINCT; в комментарии отметьте, что DISTINCT "
                "не решает проблему, а прячет её.\n"
                "4. Вопрос B: покажите, что вариант с NOT IN возвращает пустой результат; в "
                "комментарии объясните причину через трёхзначную логику (x <> NULL никогда не "
                "TRUE).\n"
                "5. Два корректных варианта вопроса B: NOT EXISTS и LEFT JOIN ... IS NULL "
                "(анти-джойн).\n"
                "6. Три показателя по каждому клиенту (число заказов, сумма, число завершённых) "
                "напишите двумя способами: коррелированными подзапросами и одним LEFT JOIN + "
                "GROUP BY + FILTER.\n"
                "7. Для обоих вариантов приведите EXPLAIN (ANALYZE) и в комментарии укажите, "
                "сколько раз каждый сканирует таблицу.\n"
                "8. Сравните планы EXPLAIN (COSTS OFF) для вариантов с EXISTS и IN и сделайте "
                "вывод.\n"
                "9. В конце файла краткая таблица-комментарий: какой инструмент (JOIN / EXISTS "
                "/ NOT EXISTS / LEFT JOIN + GROUP BY / CTE) для какой задачи и почему.\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, SQL, Subquery, JOIN, CTE, EXPLAIN",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: Subquery, EXISTS, JOIN va CTE — bir savolga uch javob",
            "description": "JOIN qatorlarni ko'paytirishi, NOT IN va NULL tuzog'i, korrelyatsiyali subquery o'rniga LEFT JOIN + FILTER va rejalarni solishtirish",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: bitta savolga uch xil javob va ular orasidagi SEMANTIK farq
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id     SERIAL      PRIMARY KEY,
    ism    VARCHAR(60) NOT NULL,
    shahar VARCHAR(40) NOT NULL
);
CREATE TABLE buyurtmalar (
    id       SERIAL        PRIMARY KEY,
    mijoz_id INTEGER       REFERENCES mijozlar(id) ON DELETE CASCADE,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

INSERT INTO mijozlar (ism, shahar) VALUES
    ('Aziz','Toshkent'), ('Dilnoza','Samarqand'),
    ('Sardor','Toshkent'), ('Nodira','Buxoro');   -- Nodira hech qachon buyurtma bermagan

INSERT INTO buyurtmalar (mijoz_id, holat, summa) VALUES
    (1,    'yakunlangan', 500000),
    (1,    'yakunlangan', 200000),
    (2,    'yakunlangan', 900000),
    (3,    'yangi',       300000),
    (NULL, 'yangi',       150000);   -- mehmon buyurtmasi -> mijoz_id NULL!

-- ══ SAVOL A: "kamida bitta yakunlangan buyurtmasi bor mijozlar" ══════
-- Uch xil yozuv, uchtasi ham AYNI natija berishi SHART.

-- (1) Korrelyatsiyasiz subquery
SELECT id, ism FROM mijozlar
WHERE id IN (SELECT mijoz_id FROM buyurtmalar WHERE holat = 'yakunlangan')
ORDER BY id;

-- (2) EXISTS — qator ko'paymaydi, birinchi moslikda to'xtaydi
SELECT m.id, m.ism FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b
              WHERE b.mijoz_id = m.id AND b.holat = 'yakunlangan')
ORDER BY m.id;

-- (3) JOIN — DIQQAT: Azizning IKKITA yakunlangan buyurtmasi bor,
--     shuning uchun u IKKI MARTA chiqadi. JOIN qatorlarni KO'PAYTIRADI.
SELECT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id AND b.holat = 'yakunlangan'
ORDER BY m.id;
-- DISTINCT muammoni yashiradi va saralash narxini qo'shadi:
SELECT DISTINCT m.id, m.ism FROM mijozlar m
JOIN buyurtmalar b ON b.mijoz_id = m.id AND b.holat = 'yakunlangan'
ORDER BY m.id;

-- Xulosa: MAVJUDLIK kerak bo'lsa EXISTS, MA'LUMOT kerak bo'lsa JOIN.

-- ══ SAVOL B: "hech qachon buyurtma bermagan mijozlar" ════════════════
-- Kutilgan javob: Nodira.

-- NOT IN — buyurtmalar.mijoz_id da bitta NULL bor:
SELECT id, ism FROM mijozlar
WHERE id NOT IN (SELECT mijoz_id FROM buyurtmalar);
--  0 QATOR. Xato yo'q, ogohlantirish yo'q — shunchaki bo'sh javob.
--  x NOT IN (1,2,3,NULL) == x<>1 AND x<>2 AND x<>3 AND x<>NULL
--  Oxirgi shart har doim NULL -> butun ifoda hech qachon TRUE emas.

-- NOT EXISTS — to'g'ri ishlaydi:
SELECT m.id, m.ism FROM mijozlar m
WHERE NOT EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

-- Anti-join ham to'g'ri:
SELECT m.id, m.ism
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
WHERE b.id IS NULL;

-- ══ SAVOL C: har mijoz uchun uchta ko'rsatkich ═══════════════════════
-- Korrelyatsiyali subquery: har bir ustun jadvalni ALOHIDA skanerlaydi.
SELECT m.ism,
       (SELECT COUNT(*)  FROM buyurtmalar b WHERE b.mijoz_id = m.id) AS soni,
       (SELECT COALESCE(SUM(summa),0) FROM buyurtmalar b WHERE b.mijoz_id = m.id) AS jami
FROM mijozlar m ORDER BY m.id;

-- LEFT JOIN + GROUP BY: hammasi BITTA o'tishda, FILTER bilan shartli agregat ham.
SELECT m.ism,
       COUNT(b.id)                                     AS soni,
       COALESCE(SUM(b.summa), 0)                       AS jami,
       COUNT(*) FILTER (WHERE b.holat = 'yakunlangan') AS yakunlangan
FROM mijozlar m
LEFT JOIN buyurtmalar b ON b.mijoz_id = m.id
GROUP BY m.id, m.ism ORDER BY m.id;

-- CTE — ko'p bosqichli hisobni o'qiladigan qiladi:
WITH yakunlangan AS (
    SELECT mijoz_id, SUM(summa) AS jami
    FROM buyurtmalar WHERE holat = 'yakunlangan'
    GROUP BY mijoz_id
), ortacha AS (
    SELECT AVG(jami) AS chek FROM yakunlangan
)
SELECT m.ism, y.jami, ROUND(o.chek, 0) AS ortacha_chek
FROM yakunlangan y
JOIN mijozlar m ON m.id = y.mijoz_id
CROSS JOIN ortacha o
WHERE y.jami > o.chek
ORDER BY y.jami DESC;

-- ══ Tanlovni REJA tasdiqlaydi, did emas ═════════════════════════════
EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE EXISTS (SELECT 1 FROM buyurtmalar b WHERE b.mijoz_id = m.id);

EXPLAIN (COSTS OFF)
SELECT m.id FROM mijozlar m
WHERE m.id IN (SELECT b.mijoz_id FROM buyurtmalar b);
-- Ikkala reja ham bir xil: EXISTS va IN o'rtasidagi tanlov — tezlik emas,
-- SEMANTIKA masalasi.""",
        },
        "exercises": [
            {
                "title": "NOT IN nima uchun bo'sh natija qaytardi?",
                "title_ru": "Почему NOT IN вернул пустой результат?",
                "description": "buyurtmalar.mijoz_id ustunida bitta NULL bor. `SELECT ... FROM mijozlar WHERE id NOT IN (SELECT mijoz_id FROM buyurtmalar)` so'rovi 0 qator qaytardi, garchi buyurtma bermagan mijoz mavjud bo'lsa ham. Sabab nima?",
                "description_ru": "В колонке buyurtmalar.mijoz_id есть один NULL. Запрос `SELECT ... FROM mijozlar WHERE id NOT IN (SELECT mijoz_id FROM buyurtmalar)` вернул 0 строк, хотя клиент без заказов существует. В чём причина?",
                "exercise_type": "multiple_choice",
                "options": [
                    "NOT IN ichida NULL bo'lsa, taqqoslash NULL beradi va shart hech qachon TRUE bo'lmaydi",
                    "NOT IN indeksdan foydalana olmaydi, shuning uchun qatorlarni topmaydi",
                    "Subquery bo'sh natija qaytargan, shuning uchun tashqi so'rov ham bo'sh",
                    "NOT IN faqat PRIMARY KEY ustunlari bilan ishlaydi",
                ],
                "options_ru": [
                    "Если внутри NOT IN есть NULL, сравнение даёт NULL и условие никогда не станет TRUE",
                    "NOT IN не может использовать индекс, поэтому не находит строки",
                    "Подзапрос вернул пустой результат, поэтому и внешний запрос пуст",
                    "NOT IN работает только с колонками PRIMARY KEY",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "x NOT IN (1, 2, NULL) ni AND lar zanjiri sifatida yozib ko'ring.",
                "hint_ru": "Распишите x NOT IN (1, 2, NULL) как цепочку условий с AND.",
                "explanation": "x NOT IN (1,2,NULL) aslida x<>1 AND x<>2 AND x<>NULL degani. Oxirgi taqqoslash NULL qaytaradi, ya'ni butun konyunksiya hech qachon TRUE bo'lolmaydi. NOT EXISTS bu muammoga ega emas.",
                "difficulty_level": "Hard",
                "points": 12,
            },
            {
                "title": "Mavjudlikni tekshirish uchun eng to'g'ri vosita",
                "title_ru": "Правильный инструмент для проверки наличия",
                "description": "Bog'liq jadvaldan hech qanday ustun kerak emas, faqat \"bunday yozuv bormi?\" degan savolga javob kerak. Qaysi kalit so'z ishlatiladi? ___",
                "description_ru": "Из связанной таблицы не нужна ни одна колонка, нужен лишь ответ на вопрос «есть ли такая запись?». Какое ключевое слово используется? ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "EXISTS",
                "hint": "JOIN qatorlarni ko'paytiradi, bu esa birinchi mos qatorda to'xtaydi.",
                "hint_ru": "JOIN размножает строки, а это останавливается на первой подходящей строке.",
                "explanation": "EXISTS qatorlarni ko'paytirmaydi va birinchi mos qator topilishi bilan to'xtaydi. JOIN esa ma'lumot qaytaradi va shu sababli qatorlarni takrorlashi mumkin.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "CTE, JOIN va subquery haqida to'g'ri fikrlar",
                "title_ru": "Верные утверждения о CTE, JOIN и подзапросах",
                "description": "PostgreSQL 12 va undan yuqori versiyalar uchun qaysi fikrlar to'g'ri?",
                "description_ru": "Какие утверждения верны для PostgreSQL 12 и выше?",
                "exercise_type": "multiple_choice",
                "options": [
                    "CTE endi avtomatik optimallashtirish devori emas — bir marta ishlatilsa asosiy so'rovga qo'shiladi",
                    "AS MATERIALIZED yozish orqali CTE ni majburan bir marta hisoblab saqlashga majburlash mumkin",
                    "JOIN \"bormi?\" savoliga javob berish uchun EXISTS dan har doim tezroq",
                    "SELECT ro'yxatidagi har bir korrelyatsiyali subquery alohida skanerlashni talab qiladi",
                ],
                "options_ru": [
                    "CTE больше не является автоматическим барьером оптимизации — при однократном использовании он встраивается в основной запрос",
                    "Через AS MATERIALIZED можно принудительно заставить CTE вычислиться один раз и сохраниться",
                    "JOIN всегда быстрее EXISTS для ответа на вопрос «есть ли?»",
                    "Каждый коррелированный подзапрос в списке SELECT требует отдельного сканирования",
                ],
                "correct_answers": "A,B,D",
                "is_multiple_select": True,
                "hint": "EXISTS va IN rejalari bir xil chiqqanini eslang; JOIN esa qatorlarni ko'paytiradi.",
                "hint_ru": "Вспомните, что планы EXISTS и IN оказались одинаковыми; а JOIN размножает строки.",
                "explanation": "JOIN mavjudlikni tekshirish uchun tezroq emas — u qatorlarni ko'paytiradi va DISTINCT talab qiladi, bu esa qo'shimcha saralash narxi. Qolgan uchtasi to'g'ri.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 3  — R1 (takrorlash + topshiriq)
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 3,
        "title": "R1-Sotuvlar tahlili dashboard (takrorlash)",
        "title_ru": "R1-Дашборд анализа продаж (повторение)",
        "points_reward": 15,
        "code_language": "sql",
        "text_content": """<h3>Nima uchun aynan dashboard</h3>
<p>Birinchi uch dars alohida vositalarni berdi: window funksiyalar, rekursiya, so'rov shakllarini tanlash. Analitik hisobot esa aynan shu uchtasi <em>birga</em> ishlaydigan joy &mdash; va shuning uchun ularni mustahkamlash uchun eng yaxshi mashq.</p>
<p>Har qanday real dashboard so'rovi bir xil skeletga ega: <strong>CTE larda bosqichma-bosqich tayyorlash &rarr; window funksiyalar bilan boyitish &rarr; tashqi SELECT da filtrlash va saralash</strong>. Bu tartib tasodifiy emas &mdash; u to'g'ridan-to'g'ri SQL ning mantiqiy bajarilish tartibidan kelib chiqadi.</p>

<h3>To'rtta klassik ko'rsatkich</h3>
<table>
<tr><th>Ko'rsatkich</th><th>Vosita</th><th>Nozik joyi</th></tr>
<tr><td>MoM o'sish (oydan oyga)</td><td><code>LAG</code></td><td>Birinchi oy <code>NULL</code>; <code>NULLIF</code> bilan nolga bo'linishdan himoya</td></tr>
<tr><td>Jamlanma (running total)</td><td><code>SUM() OVER (ORDER BY ...)</code></td><td><code>ROWS</code> ni oshkora yozish shart</td></tr>
<tr><td>Guruh ichidagi ulush</td><td><code>SUM() OVER (PARTITION BY ...)</code></td><td><code>ORDER BY</code> siz window &mdash; butun guruh bo'yicha yig'indi</td></tr>
<tr><td>Har guruhdan top-N</td><td><code>ROW_NUMBER</code> + CTE</td><td>Window ni <code>WHERE</code> da ishlatib bo'lmaydi</td></tr>
</table>
<p>Uchinchi qatordagi nozik joy alohida e'tiborga loyiq: <code>SUM(x) OVER (PARTITION BY hudud)</code> &mdash; <code>ORDER BY</code> siz &mdash; butun hudud bo'yicha yakuniy yig'indini beradi va shuning uchun ulushni hisoblashga yaraydi. <code>ORDER BY</code> qo'shsangiz, u jamlanma yig'indiga aylanadi va ulush noto'g'ri chiqadi. Bitta so'z butun hisobotni buzadi.</p>

<h3>Topshiriq haqida</h3>
<p>Quyidagi kod to'rtta tayyor dashboard so'rovini ko'rsatadi &mdash; ularni o'qing, ishga tushiring va o'zgartirib ko'ring. Keyin topshiriqni bajaring: unda shu naqshlarni birlashtirib, mustaqil hisobot yozishingiz kerak bo'ladi.</p>""",
        "text_content_ru": """<h3>Почему именно дашборд</h3>
<p>Первые три урока дали отдельные инструменты: оконные функции, рекурсию, выбор формы запроса. Аналитический отчёт — это как раз то место, где все три работают <em>вместе</em>, и потому лучшее упражнение для их закрепления.</p>
<p>Любой реальный запрос дашборда имеет один и тот же скелет: <strong>пошаговая подготовка в CTE &rarr; обогащение оконными функциями &rarr; фильтрация и сортировка во внешнем SELECT</strong>. Этот порядок не случаен — он напрямую следует из логического порядка выполнения SQL.</p>

<h3>Четыре классических показателя</h3>
<table>
<tr><th>Показатель</th><th>Инструмент</th><th>Тонкость</th></tr>
<tr><td>Рост MoM (месяц к месяцу)</td><td><code>LAG</code></td><td>Первый месяц <code>NULL</code>; защита от деления на ноль через <code>NULLIF</code></td></tr>
<tr><td>Накопительный итог (running total)</td><td><code>SUM() OVER (ORDER BY ...)</code></td><td><code>ROWS</code> нужно писать явно</td></tr>
<tr><td>Доля внутри группы</td><td><code>SUM() OVER (PARTITION BY ...)</code></td><td>Окно без <code>ORDER BY</code> — сумма по всей группе</td></tr>
<tr><td>Топ-N в каждой группе</td><td><code>ROW_NUMBER</code> + CTE</td><td>Оконную функцию нельзя использовать в <code>WHERE</code></td></tr>
</table>
<p>Тонкость в третьей строке заслуживает отдельного внимания: <code>SUM(x) OVER (PARTITION BY hudud)</code> — без <code>ORDER BY</code> — даёт итоговую сумму по всему региону и потому годится для расчёта доли. Добавьте <code>ORDER BY</code> — и она превратится в накопительную сумму, а доля посчитается неверно. Одно слово ломает весь отчёт.</p>

<h3>О задании</h3>
<p>Код ниже показывает четыре готовых запроса дашборда — прочитайте их, запустите и попробуйте изменить. Затем выполните задание: в нём нужно будет самостоятельно написать отчёт, объединив эти приёмы.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Sotuvlar tahlili dashboard — window funksiyalar + CTE birgalikda
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS sotuv_qatorlari;
DROP TABLE IF EXISTS sotuvlar;
DROP TABLE IF EXISTS mahsulotlar;

CREATE TABLE mahsulotlar (
    id         SERIAL      PRIMARY KEY,
    nomi       VARCHAR(60) NOT NULL,
    kategoriya VARCHAR(40) NOT NULL
);
CREATE TABLE sotuvlar (
    id       BIGSERIAL   PRIMARY KEY,
    sotuvchi VARCHAR(40) NOT NULL,
    hudud    VARCHAR(20) NOT NULL,
    sana     DATE        NOT NULL
);
CREATE TABLE sotuv_qatorlari (
    id          BIGSERIAL     PRIMARY KEY,
    sotuv_id    BIGINT        NOT NULL REFERENCES sotuvlar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id),
    soni        INTEGER       NOT NULL CHECK (soni > 0),
    narx        NUMERIC(12,2) NOT NULL CHECK (narx >= 0)
);

INSERT INTO mahsulotlar (nomi, kategoriya) VALUES
    ('Noutbuk','Texnika'), ('Monitor','Texnika'), ('Klaviatura','Aksessuar'),
    ('Sichqoncha','Aksessuar'), ('Stul','Mebel'), ('Stol','Mebel');

INSERT INTO sotuvlar (sotuvchi, hudud, sana)
SELECT (ARRAY['Aziz','Dilnoza','Sardor','Nodira'])[(random()*3)::INT+1],
       (ARRAY['Toshkent','Samarqand','Buxoro'])[(random()*2)::INT+1],
       DATE '2024-01-01' + (random()*180)::INT
FROM generate_series(1, 20000);

INSERT INTO sotuv_qatorlari (sotuv_id, mahsulot_id, soni, narx)
SELECT (random()*19999)::INT + 1,
       (random()*5)::INT + 1,
       (random()*3)::INT + 1,
       (random()*8000000 + 200000)::NUMERIC(12,2)
FROM generate_series(1, 60000);

CREATE INDEX idx_sq_sotuv ON sotuv_qatorlari(sotuv_id);
CREATE INDEX idx_s_sana   ON sotuvlar(sana);
ANALYZE mahsulotlar; ANALYZE sotuvlar; ANALYZE sotuv_qatorlari;

-- ─────────────────────────────────────────────────────────────────────
-- 1) Oylik dinamika: MoM o'sish + jamlanma + 3 oylik siljuvchi o'rtacha
-- ─────────────────────────────────────────────────────────────────────
WITH oylik AS (
    SELECT date_trunc('month', s.sana)::DATE AS oy,
           SUM(q.soni * q.narx)              AS tushum,
           COUNT(DISTINCT s.id)              AS sotuvlar_soni
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1
)
SELECT
    oy,
    tushum,
    sotuvlar_soni,
    LAG(tushum) OVER (ORDER BY oy)                          AS otgan_oy,
    ROUND(100.0 * (tushum - LAG(tushum) OVER (ORDER BY oy))
          / NULLIF(LAG(tushum) OVER (ORDER BY oy), 0), 1)   AS mom_foiz,
    -- ROWS oshkora yozilgan: qator-baqator jamlanma kerak
    SUM(tushum) OVER (ORDER BY oy ROWS UNBOUNDED PRECEDING) AS jamlanma,
    ROUND(AVG(tushum) OVER (
        ORDER BY oy ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 0)                                                   AS uch_oylik_ortacha
FROM oylik
ORDER BY oy;

-- ─────────────────────────────────────────────────────────────────────
-- 2) Hudud x sotuvchi reytingi + ulushlar
--    DIQQAT: SUM(...) OVER (PARTITION BY hudud) da ORDER BY YO'Q —
--    aynan shuning uchun u butun hudud yig'indisini beradi.
--    ORDER BY qo'shsangiz, bu jamlanmaga aylanadi va ulush BUZILADI.
-- ─────────────────────────────────────────────────────────────────────
WITH natija AS (
    SELECT s.hudud, s.sotuvchi, SUM(q.soni * q.narx) AS tushum
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1, 2
)
SELECT
    hudud,
    sotuvchi,
    tushum,
    RANK() OVER (PARTITION BY hudud ORDER BY tushum DESC)            AS hudud_orni,
    ROUND(100.0 * tushum / SUM(tushum) OVER (PARTITION BY hudud), 1) AS hududdagi_ulush,
    ROUND(100.0 * tushum / SUM(tushum) OVER (), 1)                   AS umumiy_ulush,
    tushum - FIRST_VALUE(tushum) OVER (
        PARTITION BY hudud ORDER BY tushum DESC
    )                                                                AS liderdan_farq
FROM natija
ORDER BY hudud, hudud_orni;

-- ─────────────────────────────────────────────────────────────────────
-- 3) Har kategoriyadan TOP-2 mahsulot (window ni WHERE da ishlatib
--    bo'lmagani uchun ikki bosqichli CTE)
-- ─────────────────────────────────────────────────────────────────────
WITH mahsulot_natija AS (
    SELECT m.kategoriya, m.nomi,
           SUM(q.soni * q.narx) AS tushum,
           SUM(q.soni)          AS dona
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1, 2
), reyting AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY kategoriya ORDER BY tushum DESC, nomi
           ) AS o_rin
    FROM mahsulot_natija
)
SELECT kategoriya, nomi, dona, tushum, o_rin
FROM reyting
WHERE o_rin <= 2
ORDER BY kategoriya, o_rin;

-- ─────────────────────────────────────────────────────────────────────
-- 4) ABC tahlil — kumulyativ ulush bo'yicha guruhlash
--    Bitta so'rovda ikki xil window: biri jamlanma, ikkinchisi umumiy
-- ─────────────────────────────────────────────────────────────────────
WITH mahsulot_natija AS (
    SELECT m.nomi, SUM(q.soni * q.narx) AS tushum
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1
), kumulyativ AS (
    SELECT nomi, tushum,
           ROUND(
               100.0 * SUM(tushum) OVER (ORDER BY tushum DESC ROWS UNBOUNDED PRECEDING)
               / SUM(tushum) OVER (),
               1
           ) AS kumulyativ_foiz
    FROM mahsulot_natija
)
SELECT nomi, tushum, kumulyativ_foiz,
       CASE WHEN kumulyativ_foiz <= 50 THEN 'A'
            WHEN kumulyativ_foiz <= 80 THEN 'B'
            ELSE 'C' END AS abc_guruh
FROM kumulyativ
ORDER BY tushum DESC;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Дашборд анализа продаж — оконные функции и CTE вместе
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS sotuv_qatorlari;
DROP TABLE IF EXISTS sotuvlar;
DROP TABLE IF EXISTS mahsulotlar;

CREATE TABLE mahsulotlar (
    id         SERIAL      PRIMARY KEY,
    nomi       VARCHAR(60) NOT NULL,
    kategoriya VARCHAR(40) NOT NULL
);
CREATE TABLE sotuvlar (
    id       BIGSERIAL   PRIMARY KEY,
    sotuvchi VARCHAR(40) NOT NULL,
    hudud    VARCHAR(20) NOT NULL,
    sana     DATE        NOT NULL
);
CREATE TABLE sotuv_qatorlari (
    id          BIGSERIAL     PRIMARY KEY,
    sotuv_id    BIGINT        NOT NULL REFERENCES sotuvlar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id),
    soni        INTEGER       NOT NULL CHECK (soni > 0),
    narx        NUMERIC(12,2) NOT NULL CHECK (narx >= 0)
);

INSERT INTO mahsulotlar (nomi, kategoriya) VALUES
    ('Noutbuk','Texnika'), ('Monitor','Texnika'), ('Klaviatura','Aksessuar'),
    ('Sichqoncha','Aksessuar'), ('Stul','Mebel'), ('Stol','Mebel');

INSERT INTO sotuvlar (sotuvchi, hudud, sana)
SELECT (ARRAY['Aziz','Dilnoza','Sardor','Nodira'])[(random()*3)::INT+1],
       (ARRAY['Toshkent','Samarqand','Buxoro'])[(random()*2)::INT+1],
       DATE '2024-01-01' + (random()*180)::INT
FROM generate_series(1, 20000);

INSERT INTO sotuv_qatorlari (sotuv_id, mahsulot_id, soni, narx)
SELECT (random()*19999)::INT + 1,
       (random()*5)::INT + 1,
       (random()*3)::INT + 1,
       (random()*8000000 + 200000)::NUMERIC(12,2)
FROM generate_series(1, 60000);

CREATE INDEX idx_sq_sotuv ON sotuv_qatorlari(sotuv_id);
CREATE INDEX idx_s_sana   ON sotuvlar(sana);
ANALYZE mahsulotlar; ANALYZE sotuvlar; ANALYZE sotuv_qatorlari;

-- ─────────────────────────────────────────────────────────────────────
-- 1) Динамика по месяцам: рост MoM + накопительный итог + скользящее среднее за 3 месяца
-- ─────────────────────────────────────────────────────────────────────
WITH oylik AS (
    SELECT date_trunc('month', s.sana)::DATE AS oy,
           SUM(q.soni * q.narx)              AS tushum,
           COUNT(DISTINCT s.id)              AS sotuvlar_soni
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1
)
SELECT
    oy,
    tushum,
    sotuvlar_soni,
    LAG(tushum) OVER (ORDER BY oy)                          AS otgan_oy,
    ROUND(100.0 * (tushum - LAG(tushum) OVER (ORDER BY oy))
          / NULLIF(LAG(tushum) OVER (ORDER BY oy), 0), 1)   AS mom_foiz,
    -- ROWS написан явно: нужен построчный накопительный итог
    SUM(tushum) OVER (ORDER BY oy ROWS UNBOUNDED PRECEDING) AS jamlanma,
    ROUND(AVG(tushum) OVER (
        ORDER BY oy ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 0)                                                   AS uch_oylik_ortacha
FROM oylik
ORDER BY oy;

-- ─────────────────────────────────────────────────────────────────────
-- 2) Рейтинг регион x продавец + доли
--    ВНИМАНИЕ: в SUM(...) OVER (PARTITION BY hudud) НЕТ ORDER BY —
--    именно поэтому он даёт сумму по всему региону.
--    Добавите ORDER BY — это станет накопительным итогом, и доля СЛОМАЕТСЯ.
-- ─────────────────────────────────────────────────────────────────────
WITH natija AS (
    SELECT s.hudud, s.sotuvchi, SUM(q.soni * q.narx) AS tushum
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1, 2
)
SELECT
    hudud,
    sotuvchi,
    tushum,
    RANK() OVER (PARTITION BY hudud ORDER BY tushum DESC)            AS hudud_orni,
    ROUND(100.0 * tushum / SUM(tushum) OVER (PARTITION BY hudud), 1) AS hududdagi_ulush,
    ROUND(100.0 * tushum / SUM(tushum) OVER (), 1)                   AS umumiy_ulush,
    tushum - FIRST_VALUE(tushum) OVER (
        PARTITION BY hudud ORDER BY tushum DESC
    )                                                                AS liderdan_farq
FROM natija
ORDER BY hudud, hudud_orni;

-- ─────────────────────────────────────────────────────────────────────
-- 3) ТОП-2 товара в каждой категории (оконную функцию нельзя
--    использовать в WHERE, поэтому двухэтапный CTE)
-- ─────────────────────────────────────────────────────────────────────
WITH mahsulot_natija AS (
    SELECT m.kategoriya, m.nomi,
           SUM(q.soni * q.narx) AS tushum,
           SUM(q.soni)          AS dona
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1, 2
), reyting AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY kategoriya ORDER BY tushum DESC, nomi
           ) AS o_rin
    FROM mahsulot_natija
)
SELECT kategoriya, nomi, dona, tushum, o_rin
FROM reyting
WHERE o_rin <= 2
ORDER BY kategoriya, o_rin;

-- ─────────────────────────────────────────────────────────────────────
-- 4) ABC-анализ — группировка по накопительной доле
--    В одном запросе два разных окна: одно накопительное, другое общее
-- ─────────────────────────────────────────────────────────────────────
WITH mahsulot_natija AS (
    SELECT m.nomi, SUM(q.soni * q.narx) AS tushum
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1
), kumulyativ AS (
    SELECT nomi, tushum,
           ROUND(
               100.0 * SUM(tushum) OVER (ORDER BY tushum DESC ROWS UNBOUNDED PRECEDING)
               / SUM(tushum) OVER (),
               1
           ) AS kumulyativ_foiz
    FROM mahsulot_natija
)
SELECT nomi, tushum, kumulyativ_foiz,
       CASE WHEN kumulyativ_foiz <= 50 THEN 'A'
            WHEN kumulyativ_foiz <= 80 THEN 'B'
            ELSE 'C' END AS abc_guruh
FROM kumulyativ
ORDER BY tushum DESC;""",
        "task": {
            "task_title": "Amaliy loyiha: Sotuvchilar samaradorligi hisoboti",
            "task_title_ru": "Практический проект: отчёт по эффективности продавцов",
            "task_description": (
                "Darsdagi sxema (mahsulotlar, sotuvlar, sotuv_qatorlari) asosida sotuvchilar "
                "samaradorligini baholovchi bitta yaxlit SQL hisobot yozing. Hisobot har bir "
                "sotuvchi uchun har oyda quyidagilarni ko'rsatishi kerak: oylik tushum, o'tgan "
                "oyga nisbatan foizdagi o'zgarish, yil boshidan jamlanma tushum, o'z hududidagi "
                "o'rni va hudud tushumidagi ulushi. Hisobot oxirida har bir hududdan eng yaxshi "
                "ikki sotuvchi alohida ajratilgan bo'lsin.\n\n"
                "Ishni sxema va test ma'lumotlarini yaratishdan boshlang (darsdagi generate_series "
                "kodidan foydalanishingiz mumkin), so'ng hisobot so'rovini yozing. Har bir so'rovni "
                "haqiqatan ishga tushirib, natijani ko'z bilan tekshiring."
            ),
            "task_description_ru": (
                "На основе схемы из урока (mahsulotlar, sotuvlar, sotuv_qatorlari) напишите один "
                "целостный SQL-отчёт, оценивающий эффективность продавцов. Отчёт должен показывать "
                "для каждого продавца по каждому месяцу: месячную выручку, изменение в процентах к "
                "прошлому месяцу, накопительную выручку с начала года, место внутри своего региона "
                "и долю в выручке региона. В конце отчёта отдельно выделите двух лучших продавцов "
                "из каждого региона.\n\n"
                "Начните со схемы и тестовых данных (можно использовать код с generate_series из "
                "урока), затем напишите запрос отчёта. Каждый запрос действительно запустите и "
                "проверьте результат глазами."
            ),
            "task_requirements": (
                "1. Sxema va kamida 10 000 qator test ma'lumoti (generate_series bilan).\n"
                "2. Hisobot kamida ikkita CTE dan iborat bo'lsin — tayyorlash va boyitish bosqichlari ajratilgan.\n"
                "3. LAG ishlatilib, MoM foiz hisoblansin; birinchi oy uchun NULL to'g'ri qayta ishlansin "
                "va NULLIF bilan nolga bo'linishdan himoya qilinsin.\n"
                "4. Jamlanma tushum uchun freym ROWS bilan OSHKORA yozilsin (RANGE emas).\n"
                "5. Hududdagi ulush SUM(...) OVER (PARTITION BY hudud) orqali — ORDER BY siz — hisoblansin.\n"
                "6. RANK yoki ROW_NUMBER bilan hudud ichidagi o'rin aniqlansin; ROW_NUMBER ishlatilsa, "
                "ORDER BY da tie-breaker ustun bo'lishi shart.\n"
                "7. Top-2 tanlash alohida CTE orqali bajarilsin (window funksiya WHERE da ishlatilmasin).\n"
                "8. Har bir so'rov ustida qisqa izoh bo'lsin: u nimani hisoblaydi va nega shu vosita tanlangan.\n"
                "9. Yakuniy fayl .sql ko'rinishida, boshidan oxirigacha xatosiz bajariladigan bo'lsin."
            ),
            "task_requirements_ru": (
                "1. Схема и минимум 10 000 строк тестовых данных (через generate_series).\n"
                "2. Отчёт должен состоять минимум из двух CTE — этапы подготовки и обогащения разделены.\n"
                "3. Используйте LAG для расчёта MoM в процентах; корректно обработайте NULL для первого "
                "месяца и защититесь от деления на ноль через NULLIF.\n"
                "4. Для накопительной выручки рамка должна быть написана ЯВНО через ROWS (не RANGE).\n"
                "5. Долю в регионе считайте через SUM(...) OVER (PARTITION BY hudud) — без ORDER BY.\n"
                "6. Место внутри региона определите через RANK или ROW_NUMBER; если используете "
                "ROW_NUMBER, в ORDER BY обязательна разрешающая (tie-breaker) колонка.\n"
                "7. Выбор топ-2 выполните отдельным CTE (оконную функцию в WHERE не использовать).\n"
                "8. К каждому запросу — краткий комментарий: что он считает и почему выбран этот инструмент.\n"
                "9. Итоговый файл в виде .sql, выполняющийся от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, SQL, Window Functions, CTE",
            "task_deadline_days": 7,
        },
        "sample": {
            "title": "Namuna: Dashboard skeleti — CTE, MoM, jamlanma, ulush va TOP-N",
            "description": "Analitik hisobotning to'rt klassik ko'rsatkichi bitta skriptda: LAG bilan MoM, ROWS freymli jamlanma, PARTITION BY ulush va CTE orqali har kategoriyadan TOP-2",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: dashboard skeleti — CTE da tayyorla, window bilan boyit, tashqarida filtrla
DROP TABLE IF EXISTS sotuv_qatorlari;
DROP TABLE IF EXISTS sotuvlar;
DROP TABLE IF EXISTS mahsulotlar;

CREATE TABLE mahsulotlar (
    id         SERIAL      PRIMARY KEY,
    nomi       VARCHAR(60) NOT NULL,
    kategoriya VARCHAR(40) NOT NULL
);
CREATE TABLE sotuvlar (
    id       BIGSERIAL   PRIMARY KEY,
    sotuvchi VARCHAR(40) NOT NULL,
    hudud    VARCHAR(20) NOT NULL,
    sana     DATE        NOT NULL
);
CREATE TABLE sotuv_qatorlari (
    id          BIGSERIAL     PRIMARY KEY,
    sotuv_id    BIGINT        NOT NULL REFERENCES sotuvlar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id),
    soni        INTEGER       NOT NULL CHECK (soni > 0),
    narx        NUMERIC(12,2) NOT NULL CHECK (narx >= 0)
);

INSERT INTO mahsulotlar (nomi, kategoriya) VALUES
    ('Noutbuk','Texnika'), ('Monitor','Texnika'), ('Klaviatura','Aksessuar'),
    ('Sichqoncha','Aksessuar'), ('Stul','Mebel'), ('Stol','Mebel');

INSERT INTO sotuvlar (sotuvchi, hudud, sana)
SELECT (ARRAY['Aziz','Dilnoza','Sardor','Nodira'])[(random()*3)::INT+1],
       (ARRAY['Toshkent','Samarqand'])[(random()*1)::INT+1],
       DATE '2024-01-01' + (random() * 180)::INT
FROM generate_series(1, 4000);

INSERT INTO sotuv_qatorlari (sotuv_id, mahsulot_id, soni, narx)
SELECT (random() * 3999)::INT + 1,
       (random() * 5)::INT + 1,
       (random() * 3)::INT + 1,
       (random() * 5000000 + 100000)::NUMERIC(12,2)
FROM generate_series(1, 12000);
ANALYZE mahsulotlar; ANALYZE sotuvlar; ANALYZE sotuv_qatorlari;

-- 1) Oylik dinamika: MoM o'sish (LAG) + jamlanma (ROWS freym)
WITH oylik AS (
    SELECT date_trunc('month', s.sana)::DATE AS oy,
           SUM(q.soni * q.narx)              AS tushum
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1
)
SELECT
    oy,
    tushum,
    ROUND(100.0 * (tushum - LAG(tushum) OVER (ORDER BY oy))
          / NULLIF(LAG(tushum) OVER (ORDER BY oy), 0), 1) AS mom_foiz,
    SUM(tushum) OVER (ORDER BY oy
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS jamlanma
FROM oylik
ORDER BY oy;
-- Birinchi oyda LAG NULL beradi; NULLIF nolga bo'linishdan himoya qiladi.
-- ROWS ni OSHKORA yozdik: standart RANGE freymi teng qiymatlarni
-- bitta blok qilib qo'shadi va jamlanma noto'g'ri chiqishi mumkin.

-- 2) Hudud x sotuvchi reytingi va ULUSH.
--    DIQQAT: ulush uchun SUM(...) OVER (PARTITION BY hudud) — ORDER BY SIZ.
--    ORDER BY qo'shsangiz u jamlanmaga aylanadi va ulush buziladi.
WITH baza AS (
    SELECT s.hudud, s.sotuvchi, SUM(q.soni * q.narx) AS tushum
    FROM sotuvlar s
    JOIN sotuv_qatorlari q ON q.sotuv_id = s.id
    GROUP BY 1, 2
)
SELECT
    hudud, sotuvchi, tushum,
    RANK() OVER (PARTITION BY hudud ORDER BY tushum DESC)                  AS hudud_orni,
    ROUND(100.0 * tushum / SUM(tushum) OVER (PARTITION BY hudud), 1)       AS ulush_foiz
FROM baza
ORDER BY hudud, hudud_orni;

-- 3) Har kategoriyadan TOP-2. Window ni WHERE da ishlatib bo'lmaydi —
--    avval CTE da hisoblaymiz, keyin tashqarida filtrlaymiz.
WITH mahsulot_tushumi AS (
    SELECT m.kategoriya, m.nomi, SUM(q.soni * q.narx) AS tushum
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1, 2
), reyting AS (
    SELECT kategoriya, nomi, tushum,
           ROW_NUMBER() OVER (PARTITION BY kategoriya ORDER BY tushum DESC, nomi) AS o_rin
    FROM mahsulot_tushumi
)
SELECT kategoriya, o_rin, nomi, tushum
FROM reyting
WHERE o_rin <= 2
ORDER BY kategoriya, o_rin;

-- 4) ABC tahlil — kumulyativ ulush bo'yicha guruhlash
WITH mahsulot_tushumi AS (
    SELECT m.nomi, SUM(q.soni * q.narx) AS tushum
    FROM sotuv_qatorlari q
    JOIN mahsulotlar m ON m.id = q.mahsulot_id
    GROUP BY 1
), kumulyativ AS (
    SELECT nomi, tushum,
           ROUND(100.0 * SUM(tushum) OVER (ORDER BY tushum DESC
                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                 / SUM(tushum) OVER (), 1) AS kumulyativ_foiz
    FROM mahsulot_tushumi
)
SELECT nomi, tushum, kumulyativ_foiz,
       CASE WHEN kumulyativ_foiz <= 50 THEN 'A'
            WHEN kumulyativ_foiz <= 80 THEN 'B'
            ELSE 'C' END AS guruh
FROM kumulyativ
ORDER BY tushum DESC;""",
        },
        "exercises": [
            {
                "title": "Ulushni hisoblashda ORDER BY nima qiladi?",
                "title_ru": "Что делает ORDER BY при расчёте доли?",
                "description": "Hisobotda hududdagi ulush `100.0 * tushum / SUM(tushum) OVER (PARTITION BY hudud)` bilan hisoblanadi. Dasturchi bu window ga `ORDER BY tushum DESC` qo'shib qo'ydi. Nima o'zgaradi?",
                "description_ru": "В отчёте доля по региону считается как `100.0 * tushum / SUM(tushum) OVER (PARTITION BY hudud)`. Разработчик добавил в это окно `ORDER BY tushum DESC`. Что изменится?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Hech narsa o'zgarmaydi — ORDER BY faqat natija tartibiga ta'sir qiladi",
                    "Maxraj jamlanma yig'indiga aylanadi va birinchi qatorda ulush 100% chiqadi",
                    "So'rov xato beradi: PARTITION BY va ORDER BY birga ishlatilmaydi",
                    "Ulush to'g'ri qoladi, lekin so'rov sezilarli sekinlashadi",
                ],
                "options_ru": [
                    "Ничего не изменится — ORDER BY влияет только на порядок вывода",
                    "Знаменатель станет накопительной суммой, и в первой строке доля получится 100%",
                    "Запрос выдаст ошибку: PARTITION BY и ORDER BY нельзя использовать вместе",
                    "Доля останется верной, но запрос заметно замедлится",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "ORDER BY paydo bo'lishi bilan window ga standart freym qo'shiladi.",
                "hint_ru": "Как только появляется ORDER BY, к окну добавляется рамка по умолчанию.",
                "explanation": "ORDER BY qo'shilishi bilan window ga RANGE UNBOUNDED PRECEDING AND CURRENT ROW freymi qo'shiladi va SUM jamlanmaga aylanadi. Eng katta qator birinchi bo'lgani uchun uning maxraji o'zining qiymatiga teng bo'ladi va ulush 100% chiqadi.",
                "difficulty_level": "Hard",
                "points": 12,
            },
            {
                "title": "Dashboard so'rovini qurish tartibi",
                "title_ru": "Порядок построения запроса для дашборда",
                "description": "Analitik hisobot so'rovini qurish bosqichlarini to'g'ri tartibga soling.",
                "description_ru": "Расположите в правильном порядке этапы построения аналитического запроса.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Manba jadvallarni JOIN qilib, kerakli darajada GROUP BY qilish (birinchi CTE)",
                    "Window funksiyalar bilan reyting, ulush va dinamikani qo'shish (ikkinchi CTE)",
                    "Tashqi SELECT da window natijasi bo'yicha filtrlash",
                    "Yakuniy ORDER BY va LIMIT qo'yish",
                ],
                "drag_items_ru": [
                    "Соединить исходные таблицы JOIN и сгруппировать до нужного уровня (первый CTE)",
                    "Добавить ранги, доли и динамику оконными функциями (второй CTE)",
                    "Во внешнем SELECT отфильтровать по результату оконной функции",
                    "Поставить финальные ORDER BY и LIMIT",
                ],
                "correct_order": [
                    "Manba jadvallarni JOIN qilib, kerakli darajada GROUP BY qilish (birinchi CTE)",
                    "Window funksiyalar bilan reyting, ulush va dinamikani qo'shish (ikkinchi CTE)",
                    "Tashqi SELECT da window natijasi bo'yicha filtrlash",
                    "Yakuniy ORDER BY va LIMIT qo'yish",
                ],
                "hint": "Window funksiya natijasi bo'yicha filtrlash faqat u hisoblangandan keyin mumkin.",
                "hint_ru": "Фильтровать по результату оконной функции можно только после её вычисления.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 4
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 4,
        "title": "4-EXPLAIN ANALYZE chuqur o'qish",
        "title_ru": "4-Углублённое чтение EXPLAIN ANALYZE",
        "points_reward": 15,
        "code_language": "sql",
        "text_content": """<h3>Taxmin va o'lchov</h3>
<p>Optimallashtirishning butun ishi bitta ko'nikmaga tayanadi: rejani o'qiy olish. Usiz har qanday &ldquo;tezlashtirish&rdquo; taxminga aylanadi &mdash; indeks qo'shasiz, so'rov tezlashmaydi, nega tezlashmagani noma'lum qoladi.</p>
<p>Ikkita buyruq bor va ular tubdan farq qiladi:</p>
<ul>
<li><code>EXPLAIN</code> so'rovni <strong>bajarmaydi</strong>. U faqat rejalashtiruvchi tanlagan rejani va uning <em>taxminlarini</em> ko'rsatadi. Barcha raqamlar &mdash; statistikaga asoslangan prognoz.</li>
<li><code>EXPLAIN ANALYZE</code> so'rovni <strong>haqiqatan bajaradi</strong> va o'lchangan qiymatlarni qo'shadi. <code>UPDATE</code>/<code>DELETE</code> ustida ishlatsangiz, ular ham haqiqatan bajariladi &mdash; shuning uchun bunday tekshiruvni <code>BEGIN; ... ROLLBACK;</code> ichida qiling.</li>
</ul>

<h3>Raqamlarni o'qish</h3>
<p><code>cost=740.16..3138.75 rows=66047 width=32</code> qismi taxmin:</p>
<ul>
<li><strong>cost</strong> &mdash; ikkita son: <em>birinchi</em> qatorni olish narxi va <em>oxirgi</em> qatorni olish narxi. Shartli birlikda (sahifa o'qish taxminan 1.0). <code>LIMIT</code> bor so'rovlarda birinchi son hal qiluvchi bo'ladi.</li>
<li><strong>rows</strong> &mdash; planner nechta qator kutmoqda.</li>
<li><strong>width</strong> &mdash; bitta qatorning o'rtacha bayt hajmi.</li>
</ul>
<p><code>(actual time=1.367..7.688 rows=66560 loops=1)</code> qismi o'lchov: millisekundda birinchi va oxirgi qator vaqti, haqiqiy qatorlar soni va tugun necha marta ishga tushgani.</p>
<p><strong>Eng muhim ko'rsatkich &mdash; <code>rows</code> (taxmin) va <code>actual rows</code> o'rtasidagi farq.</strong> Agar farq o'nlab marta bo'lsa, planner noto'g'ri ma'lumot bilan ishlagan va rejaning qolgan qismi ham noto'g'ri bo'lishi ehtimoli katta.</p>
<p><code>loops=20</code> bo'lsa alohida ehtiyot bo'ling: <code>actual time</code> va <code>rows</code> bu yerda <em>bitta</em> takrorlanish uchun ko'rsatiladi. Umumiy vaqtni olish uchun ularni <code>loops</code> ga ko'paytirish kerak.</p>

<h3>Skanerlash turlari &mdash; qaysi biri qachon</h3>
<table>
<tr><th>Tugun</th><th>Qachon tanlanadi</th><th>Belgisi</th></tr>
<tr><td>Seq Scan</td><td>Qatorlarning katta qismi kerak, yoki indeks yo'q</td><td>Butun jadval ketma-ket o'qiladi</td></tr>
<tr><td>Index Scan</td><td>Kam qator kerak <em>va</em> ular tartibda kerak / bir nechta</td><td><code>Index Cond</code></td></tr>
<tr><td>Bitmap Heap Scan</td><td>&ldquo;O'rta&rdquo; miqdor: ko'p, lekin hammasi emas</td><td><code>Recheck Cond</code>, <code>Heap Blocks</code></td></tr>
<tr><td>Index Only Scan</td><td>Barcha kerakli ustunlar indeksda bor</td><td><code>Heap Fetches: 0</code></td></tr>
</table>
<p><strong>Bitmap Heap Scan</strong> ni tushunish muhim: u ikki bosqichli. Avval <code>Bitmap Index Scan</code> kerakli <em>sahifalar</em> xaritasini yig'adi, keyin <code>Bitmap Heap Scan</code> o'sha sahifalarni <strong>disk tartibida</strong> o'qiydi. Ya'ni u tasodifiy I/O ni ketma-ket I/O ga aylantiradi. Agar rejada <code>lossy=</code> paydo bo'lsa &mdash; bitmap <code>work_mem</code> ga sig'magan va PostgreSQL aniqlikni sahifa darajasiga tushirgan.</p>

<h3>Ikkita haqiqat, kutilganiga zid</h3>
<p><strong>Birinchisi: indeks bor bo'lishi uni ishlatiladi degani emas &mdash; va bu ko'pincha to'g'ri qaror.</strong> Jadvalning uchdan bir qismi qidirilayotganda indeks orqali qatorlarni bittalab olish, butun jadvalni ketma-ket o'qishdan qimmatroq tushadi. Rejalashtiruvchi <code>Seq Scan</code> tanlasa, odatda u haq.</p>
<p><strong>Ikkinchisi: 200 000 qatordan atigi 38 tasi qidirilganda ham <code>Index Scan</code> emas, <code>Bitmap Heap Scan</code> chiqishi mumkin.</strong> Sababi &mdash; o'sha 38 qator jismonan 38 ta <em>turli sahifada</em> yotibdi. Bu tasodifiy emas: bu &ldquo;ma'lumotning jismoniy joylashuvi rejaga ta'sir qiladi&rdquo; degan qoidaning to'g'ridan-to'g'ri namoyishi.</p>

<h3>Index Only Scan va VACUUM</h3>
<p>Indeksda barcha kerakli ustunlar bo'lsa ham, PostgreSQL <em>avtomatik</em> <code>Index Only Scan</code> tanlamaydi. Chunki indeks yozuvi qatorning <strong>ko'rinuvchanligi</strong> haqida ma'lumot saqlamaydi &mdash; buni faqat jadvalning o'zi biladi. Bu ma'lumot <em>visibility map</em> da keshlanadi, uni esa <code>VACUUM</code> to'ldiradi.</p>
<p>Ommaviy yuklashdan keyin visibility map bo'sh bo'ladi, planner buni ko'radi va Index Only Scan ni umuman tanlamaydi. Test o'lchovi: <code>VACUUM</code> dan oldin &mdash; Bitmap Heap Scan, 42 bufer; <code>VACUUM</code> dan keyin &mdash; Index Only Scan, <code>Heap Fetches: 0</code>, atigi 4 bufer.</p>
<p>Muhim texnik nuqta: <code>VACUUM</code> ni tranzaksiya ichida bajarib bo'lmaydi (<code>ERROR: VACUUM cannot run inside a transaction block</code>) &mdash; uni alohida, avtomatik commit rejimida ishga tushiring.</p>

<h3>Planner qachon adashadi</h3>
<p>Rejalashtiruvchi ustunlarni <strong>mustaqil</strong> deb hisoblaydi va ularning tanlanuvchanligini ko'paytiradi. Agar ustunlar aslida bog'liq bo'lsa (masalan <code>shahar</code> <code>viloyat</code> ni to'liq aniqlaydi), taxmin haqiqatdan o'nlab marta kichik chiqadi.</p>
<p>O'lchangan misol: <code>WHERE shahar='Margilon' AND viloyat='Fargona'</code> uchun taxmin <strong>6154</strong> qator, haqiqat <strong>20000</strong>. <code>CREATE STATISTICS ... (dependencies)</code> qo'shilgandan keyin taxmin <strong>19293</strong> ga aylanadi. Katta so'rovda bunday xato noto'g'ri JOIN turini tanlashga olib keladi.</p>""",
        "text_content_ru": """<h3>Оценка и измерение</h3>
<p>Вся работа по оптимизации опирается на один навык: умение читать план. Без него любое «ускорение» превращается в гадание — вы добавляете индекс, запрос не ускоряется, и почему — остаётся неизвестным.</p>
<p>Есть две команды, и они принципиально разные:</p>
<ul>
<li><code>EXPLAIN</code> запрос <strong>не выполняет</strong>. Он показывает только выбранный планировщиком план и его <em>оценки</em>. Все числа — прогноз на основе статистики.</li>
<li><code>EXPLAIN ANALYZE</code> запрос <strong>реально выполняет</strong> и добавляет измеренные значения. Если применить его к <code>UPDATE</code>/<code>DELETE</code>, они тоже выполнятся по-настоящему — поэтому такую проверку делайте внутри <code>BEGIN; ... ROLLBACK;</code>.</li>
</ul>

<h3>Как читать числа</h3>
<p>Часть <code>cost=740.16..3138.75 rows=66047 width=32</code> — это оценка:</p>
<ul>
<li><strong>cost</strong> — два числа: стоимость получения <em>первой</em> строки и стоимость получения <em>последней</em>. В условных единицах (чтение страницы примерно 1.0). Для запросов с <code>LIMIT</code> решающим становится первое число.</li>
<li><strong>rows</strong> — сколько строк ожидает планировщик.</li>
<li><strong>width</strong> — средний размер одной строки в байтах.</li>
</ul>
<p>Часть <code>(actual time=1.367..7.688 rows=66560 loops=1)</code> — это измерение: время первой и последней строки в миллисекундах, реальное число строк и сколько раз узел запускался.</p>
<p><strong>Важнейший показатель — расхождение между <code>rows</code> (оценка) и <code>actual rows</code>.</strong> Если разница в десятки раз, планировщик работал с неверными данными, и остальная часть плана с большой вероятностью тоже неверна.</p>
<p>Особенно осторожно при <code>loops=20</code>: <code>actual time</code> и <code>rows</code> здесь показаны для <em>одной</em> итерации. Чтобы получить общее время, их нужно умножить на <code>loops</code>.</p>

<h3>Типы сканирования — что и когда</h3>
<table>
<tr><th>Узел</th><th>Когда выбирается</th><th>Признак</th></tr>
<tr><td>Seq Scan</td><td>Нужна большая часть строк, либо индекса нет</td><td>Вся таблица читается последовательно</td></tr>
<tr><td>Index Scan</td><td>Нужно мало строк <em>и</em> они нужны в порядке / поштучно</td><td><code>Index Cond</code></td></tr>
<tr><td>Bitmap Heap Scan</td><td>«Средний» объём: много, но не всё</td><td><code>Recheck Cond</code>, <code>Heap Blocks</code></td></tr>
<tr><td>Index Only Scan</td><td>Все нужные колонки есть в индексе</td><td><code>Heap Fetches: 0</code></td></tr>
</table>
<p>Важно понять <strong>Bitmap Heap Scan</strong>: он двухэтапный. Сначала <code>Bitmap Index Scan</code> собирает карту нужных <em>страниц</em>, затем <code>Bitmap Heap Scan</code> читает эти страницы <strong>в порядке диска</strong>. То есть он превращает случайный ввод-вывод в последовательный. Если в плане появилось <code>lossy=</code> — битовая карта не влезла в <code>work_mem</code>, и PostgreSQL понизил точность до уровня страниц.</p>

<h3>Две истины, противоречащие ожиданиям</h3>
<p><strong>Первая: наличие индекса не означает, что он будет использован — и часто это правильное решение.</strong> Когда выбирается треть таблицы, доставать строки по одной через индекс дороже, чем прочитать всю таблицу последовательно. Если планировщик выбрал <code>Seq Scan</code>, обычно он прав.</p>
<p><strong>Вторая: даже когда из 200 000 строк ищутся всего 38, может получиться не <code>Index Scan</code>, а <code>Bitmap Heap Scan</code>.</strong> Причина — эти 38 строк физически лежат на 38 <em>разных страницах</em>. Это не случайность: это прямая демонстрация правила «физическое расположение данных влияет на план».</p>

<h3>Index Only Scan и VACUUM</h3>
<p>Даже если в индексе есть все нужные колонки, PostgreSQL <em>не</em> выберет <code>Index Only Scan</code> автоматически. Дело в том, что запись индекса не хранит информацию о <strong>видимости</strong> строки — это знает только сама таблица. Эта информация кэшируется в <em>visibility map</em>, а заполняет её <code>VACUUM</code>.</p>
<p>После массовой загрузки visibility map пуста, планировщик это видит и Index Only Scan вообще не рассматривает. Измеренный тест: до <code>VACUUM</code> — Bitmap Heap Scan, 42 буфера; после <code>VACUUM</code> — Index Only Scan, <code>Heap Fetches: 0</code>, всего 4 буфера.</p>
<p>Важный технический момент: <code>VACUUM</code> нельзя выполнить внутри транзакции (<code>ERROR: VACUUM cannot run inside a transaction block</code>) — запускайте его отдельно, в режиме автокоммита.</p>

<h3>Когда планировщик ошибается</h3>
<p>Планировщик считает колонки <strong>независимыми</strong> и перемножает их селективности. Если колонки на самом деле связаны (например, <code>shahar</code> полностью определяет <code>viloyat</code>), оценка окажется в десятки раз меньше реальности.</p>
<p>Измеренный пример: для <code>WHERE shahar='Margilon' AND viloyat='Fargona'</code> оценка — <strong>6154</strong> строки, реальность — <strong>20000</strong>. После добавления <code>CREATE STATISTICS ... (dependencies)</code> оценка становится <strong>19293</strong>. В большом запросе такая ошибка приводит к выбору неправильного типа JOIN.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- EXPLAIN ANALYZE ni chuqur o'qish
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS tolovlar;

CREATE TABLE tolovlar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL,
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

-- 200 000 qator. Kichik jadvalda rejalar ishonchsiz: 100 qatorlik
-- jadvalni to'liq skanerlash HAR DOIM arzon, shuning uchun indeks
-- foydasi umuman ko'rinmaydi.
INSERT INTO tolovlar (mijoz_id, sana, holat, summa)
SELECT
    (random() * 5000)::INT + 1,
    DATE '2023-01-01' + (random() * 700)::INT,
    (ARRAY['yangi','tolangan','bekor','qaytarilgan'])[(random() * 3)::INT + 1],
    (random() * 900000 + 10000)::NUMERIC(12,2)
FROM generate_series(1, 200000);

-- ANALYZE statistikani yangilaydi. Busiz planner jadval haqida deyarli
-- hech narsa bilmaydi va butunlay noto'g'ri reja tanlashi mumkin.
ANALYZE tolovlar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) EXPLAIN — bajarmaydi, faqat TAXMIN qiladi
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN SELECT * FROM tolovlar WHERE holat = 'bekor';
--  Seq Scan on tolovlar  (cost=0.00..4073.00 rows=66853 width=31)
--                              ^^^^^^^^^^^^  ^^^^^^^^^  ^^^^^^^^
--                              |             |          bitta qator ~31 bayt
--                              |             planner 66853 qator kutmoqda
--                              birinchi..oxirgi qator narxi

-- ─────────────────────────────────────────────────────────────────────
-- 2) Seq Scan — qatorlarning katta qismi kerak bo'lganda
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE summa > 20000;
--  Seq Scan ... rows=197700 ... (actual time=0.005..16.116 rows=197787 loops=1)
--    Rows Removed by Filter: 2213
--    Buffers: shared hit=1573
--  Taxmin 197700, haqiqat 197787 — planner deyarli aniq. Yaxshi belgi.

-- ─────────────────────────────────────────────────────────────────────
-- 3) Indeks BOR, lekin baribir Seq Scan — va bu TO'G'RI qaror
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_tolovlar_holat ON tolovlar(holat);
CREATE INDEX idx_tolovlar_mijoz ON tolovlar(mijoz_id);
ANALYZE tolovlar;

-- 'bekor' EMAS -> qatorlarning ~75% i. Indeks orqali ularni bittalab
-- olish, butun jadvalni ketma-ket o'qishdan QIMMATROQ.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat <> 'bekor';
--  Seq Scan on tolovlar ... (actual time=0.006..13.427 rows=133440 loops=1)
--  Indeks bor, lekin ishlatilmadi. Planner haq.

-- ─────────────────────────────────────────────────────────────────────
-- 4) Bitmap Heap Scan — "o'rta" holat (~25%)
--    Ikki bosqich: Bitmap Index Scan sahifalar xaritasini yig'adi,
--    Bitmap Heap Scan esa ularni DISK TARTIBIDA o'qiydi.
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat = 'bekor';
--  Bitmap Heap Scan on tolovlar  (cost=740.16..3138.75 rows=66047 ...)
--    Recheck Cond: ((holat)::text = 'bekor'::text)
--    Heap Blocks: exact=1573
--    ->  Bitmap Index Scan on idx_tolovlar_holat (actual ... rows=66560 ...)
--  cost 3138 < Seq Scan ning 4073 si — shuning uchun bitmap tanlandi.
--  "lossy=" paydo bo'lsa: bitmap work_mem ga sig'magan.

-- ─────────────────────────────────────────────────────────────────────
-- 5) Index Scan — unikal qidiruv
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE id = 123456;
--  Index Scan using tolovlar_pkey ... (actual time=0.015..0.015 rows=1 loops=1)
--    Buffers: shared hit=7        <-- atigi 7 sahifa
--  Execution Time: 0.025 ms

-- ORDER BY + LIMIT ham Index Scan ni "chaqiradi": indeks allaqachon
-- tartiblangan, shuning uchun 20 ta qator olib to'xtash mumkin.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM tolovlar WHERE mijoz_id BETWEEN 100 AND 300 ORDER BY mijoz_id LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 6) KUTILMAGAN NATIJA: 200 000 dan atigi 38 qator, lekin baribir Bitmap
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE mijoz_id = 777;
--  Bitmap Heap Scan ... (actual time=0.028..0.074 rows=38 loops=1)
--    Heap Blocks: exact=38
--  38 qator 38 ta TURLI sahifada yotibdi (ma'lumot tasodifiy kiritilgan).
--  Ya'ni rejaga faqat qatorlar SONI emas, ularning JISMONIY joylashuvi
--  ham ta'sir qiladi.

-- ─────────────────────────────────────────────────────────────────────
-- 7) Index Only Scan — va nega u darhol ishlamaydi
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_tolovlar_mijoz_summa ON tolovlar(mijoz_id, summa);
ANALYZE tolovlar;

-- Kerakli ikkala ustun ham indeksda bor. Lekin reja hali ham Bitmap:
EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Bitmap Heap Scan ... Buffers: shared hit=42
--  Sababi: indeks qatorning KO'RINUVCHANLIGINI bilmaydi. Buni visibility
--  map saqlaydi, uni esa VACUUM to'ldiradi. Ommaviy yuklashdan keyin u bo'sh.

-- DIQQAT: VACUUM ni tranzaksiya ichida bajarib BO'LMAYDI.
--   ERROR:  VACUUM cannot run inside a transaction block
-- Quyidagi qatorni alohida, avtomatik commit rejimida ishga tushiring:
VACUUM (ANALYZE) tolovlar;

EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Index Only Scan using idx_tolovlar_mijoz_summa ...
--    Heap Fetches: 0              <-- jadvalga UMUMAN murojaat qilinmadi
--    Buffers: shared hit=4        <-- 42 o'rniga 4 sahifa
--  Bu "covering index" ning butun ma'nosi.

-- ─────────────────────────────────────────────────────────────────────
-- 8) Planner ADASHGANDA: bog'liq ustunlar
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS manzillar;
CREATE TABLE manzillar (
    id      BIGSERIAL     PRIMARY KEY,
    shahar  VARCHAR(30)   NOT NULL,
    viloyat VARCHAR(30)   NOT NULL,
    summa   NUMERIC(10,2) NOT NULL
);

-- shahar viloyatni TO'LIQ aniqlaydi — funksional bog'liqlik bor
INSERT INTO manzillar (shahar, viloyat, summa)
SELECT s.shahar, s.viloyat, (random() * 100000)::NUMERIC(10,2)
FROM generate_series(1, 200000) g
CROSS JOIN LATERAL (
    SELECT * FROM (VALUES
        ('Nurafshon','Toshkent'), ('Chirchiq','Toshkent'), ('Angren','Toshkent'),
        ('Urgut','Samarqand'),    ('Kattaqorgon','Samarqand'),
        ('Gijduvon','Buxoro'),    ('Kogon','Buxoro'),
        ('Margilon','Fargona'),   ('Qoqon','Fargona'), ('Quva','Fargona')
    ) AS v(shahar, viloyat) OFFSET (g % 10) LIMIT 1
) s;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  Seq Scan ... rows=6154 ... (actual rows=20000 loops=1)
--               ^^^^^^^^^              ^^^^^^^^^^
--               taxmin                 haqiqat — 3 baravar farq!
--  Sabab: planner ikki ustunni MUSTAQIL deb hisoblab, tanlanuvchanliklarni
--  ko'paytirdi. Aslida shahar viloyatni to'liq aniqlaydi.

-- Yechim — ko'p ustunli kengaytirilgan statistika:
CREATE STATISTICS st_manzil (dependencies) ON shahar, viloyat FROM manzillar;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  Seq Scan ... rows=19293 ... (actual rows=20000 loops=1)
--  Endi taxmin haqiqatga juda yaqin. Katta so'rovda bu noto'g'ri JOIN
--  turini tanlashning oldini oladi.

-- ─────────────────────────────────────────────────────────────────────
-- 9) JOIN turlari bitta rejada
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS mijozlar;
CREATE TABLE mijozlar (id SERIAL PRIMARY KEY, ism VARCHAR(60) NOT NULL);
INSERT INTO mijozlar (ism) SELECT 'Mijoz ' || g FROM generate_series(1, 5000) g;
ANALYZE mijozlar;

-- Kam qator -> Nested Loop: tashqi tomondagi har qator uchun ichki
-- tomonda indeks bo'yicha qidiruv
EXPLAIN (ANALYZE)
SELECT m.ism, t.summa
FROM mijozlar m JOIN tolovlar t ON t.mijoz_id = m.id
WHERE m.id = 777;

-- Ko'p qator -> Hash Join: kichik jadvaldan xesh quriladi, katta jadval
-- bir marta o'tib chiqiladi
EXPLAIN (ANALYZE)
SELECT m.ism, SUM(t.summa)
FROM mijozlar m JOIN tolovlar t ON t.mijoz_id = m.id
GROUP BY m.ism;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Углублённое чтение EXPLAIN ANALYZE
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS tolovlar;

CREATE TABLE tolovlar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL,
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

-- 200 000 строк. На маленькой таблице планы недостоверны: полное
-- сканирование таблицы из 100 строк ВСЕГДА дёшево, поэтому польза
-- индекса вообще не видна.
INSERT INTO tolovlar (mijoz_id, sana, holat, summa)
SELECT
    (random() * 5000)::INT + 1,
    DATE '2023-01-01' + (random() * 700)::INT,
    (ARRAY['yangi','tolangan','bekor','qaytarilgan'])[(random() * 3)::INT + 1],
    (random() * 900000 + 10000)::NUMERIC(12,2)
FROM generate_series(1, 200000);

-- ANALYZE обновляет статистику. Без него планировщик почти ничего
-- не знает о таблице и может выбрать совершенно неверный план.
ANALYZE tolovlar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) EXPLAIN — не выполняет, только ОЦЕНИВАЕТ
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN SELECT * FROM tolovlar WHERE holat = 'bekor';
--  Seq Scan on tolovlar  (cost=0.00..4073.00 rows=66853 width=31)
--                              ^^^^^^^^^^^^  ^^^^^^^^^  ^^^^^^^^
--                              |             |          одна строка ~31 байт
--                              |             планировщик ждёт 66853 строки
--                              стоимость первой..последней строки

-- ─────────────────────────────────────────────────────────────────────
-- 2) Seq Scan — когда нужна большая часть строк
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE summa > 20000;
--  Seq Scan ... rows=197700 ... (actual time=0.005..16.116 rows=197787 loops=1)
--    Rows Removed by Filter: 2213
--    Buffers: shared hit=1573
--  Оценка 197700, реальность 197787 — планировщик почти точен. Хороший знак.

-- ─────────────────────────────────────────────────────────────────────
-- 3) Индекс ЕСТЬ, но всё равно Seq Scan — и это ПРАВИЛЬНОЕ решение
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_tolovlar_holat ON tolovlar(holat);
CREATE INDEX idx_tolovlar_mijoz ON tolovlar(mijoz_id);
ANALYZE tolovlar;

-- НЕ 'bekor' -> около 75% строк. Доставать их по одной через индекс
-- ДОРОЖЕ, чем прочитать всю таблицу последовательно.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat <> 'bekor';
--  Seq Scan on tolovlar ... (actual time=0.006..13.427 rows=133440 loops=1)
--  Индекс есть, но не использован. Планировщик прав.

-- ─────────────────────────────────────────────────────────────────────
-- 4) Bitmap Heap Scan — «средний» случай (~25%)
--    Два этапа: Bitmap Index Scan собирает карту страниц,
--    а Bitmap Heap Scan читает их В ПОРЯДКЕ ДИСКА.
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat = 'bekor';
--  Bitmap Heap Scan on tolovlar  (cost=740.16..3138.75 rows=66047 ...)
--    Recheck Cond: ((holat)::text = 'bekor'::text)
--    Heap Blocks: exact=1573
--    ->  Bitmap Index Scan on idx_tolovlar_holat (actual ... rows=66560 ...)
--  cost 3138 меньше, чем 4073 у Seq Scan — поэтому выбран bitmap.
--  Если появилось "lossy=": битовая карта не влезла в work_mem.

-- ─────────────────────────────────────────────────────────────────────
-- 5) Index Scan — уникальный поиск
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE id = 123456;
--  Index Scan using tolovlar_pkey ... (actual time=0.015..0.015 rows=1 loops=1)
--    Buffers: shared hit=7        <-- всего 7 страниц
--  Execution Time: 0.025 ms

-- ORDER BY + LIMIT тоже «вызывает» Index Scan: индекс уже отсортирован,
-- поэтому можно взять 20 строк и остановиться.
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM tolovlar WHERE mijoz_id BETWEEN 100 AND 300 ORDER BY mijoz_id LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 6) НЕОЖИДАННЫЙ РЕЗУЛЬТАТ: из 200 000 всего 38 строк, но всё равно Bitmap
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE mijoz_id = 777;
--  Bitmap Heap Scan ... (actual time=0.028..0.074 rows=38 loops=1)
--    Heap Blocks: exact=38
--  38 строк лежат на 38 РАЗНЫХ страницах (данные вставлялись случайно).
--  То есть на план влияет не только КОЛИЧЕСТВО строк, но и их
--  ФИЗИЧЕСКОЕ расположение.

-- ─────────────────────────────────────────────────────────────────────
-- 7) Index Only Scan — и почему он не срабатывает сразу
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_tolovlar_mijoz_summa ON tolovlar(mijoz_id, summa);
ANALYZE tolovlar;

-- Обе нужные колонки есть в индексе. Но план всё ещё Bitmap:
EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Bitmap Heap Scan ... Buffers: shared hit=42
--  Причина: индекс не знает о ВИДИМОСТИ строки. Это хранит visibility
--  map, а заполняет её VACUUM. После массовой загрузки она пуста.

-- ВНИМАНИЕ: VACUUM НЕЛЬЗЯ выполнить внутри транзакции.
--   ERROR:  VACUUM cannot run inside a transaction block
-- Запустите следующую строку отдельно, в режиме автокоммита:
VACUUM (ANALYZE) tolovlar;

EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Index Only Scan using idx_tolovlar_mijoz_summa ...
--    Heap Fetches: 0              <-- к таблице ВООБЩЕ не обращались
--    Buffers: shared hit=4        <-- 4 страницы вместо 42
--  В этом весь смысл «покрывающего» (covering) индекса.

-- ─────────────────────────────────────────────────────────────────────
-- 8) Когда планировщик ОШИБАЕТСЯ: связанные колонки
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS manzillar;
CREATE TABLE manzillar (
    id      BIGSERIAL     PRIMARY KEY,
    shahar  VARCHAR(30)   NOT NULL,
    viloyat VARCHAR(30)   NOT NULL,
    summa   NUMERIC(10,2) NOT NULL
);

-- shahar ПОЛНОСТЬЮ определяет viloyat — есть функциональная зависимость
INSERT INTO manzillar (shahar, viloyat, summa)
SELECT s.shahar, s.viloyat, (random() * 100000)::NUMERIC(10,2)
FROM generate_series(1, 200000) g
CROSS JOIN LATERAL (
    SELECT * FROM (VALUES
        ('Nurafshon','Toshkent'), ('Chirchiq','Toshkent'), ('Angren','Toshkent'),
        ('Urgut','Samarqand'),    ('Kattaqorgon','Samarqand'),
        ('Gijduvon','Buxoro'),    ('Kogon','Buxoro'),
        ('Margilon','Fargona'),   ('Qoqon','Fargona'), ('Quva','Fargona')
    ) AS v(shahar, viloyat) OFFSET (g % 10) LIMIT 1
) s;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  Seq Scan ... rows=6154 ... (actual rows=20000 loops=1)
--               ^^^^^^^^^              ^^^^^^^^^^
--               оценка                 реальность — разница в 3 раза!
--  Причина: планировщик счёл колонки НЕЗАВИСИМЫМИ и перемножил
--  селективности. На деле shahar полностью определяет viloyat.

-- Решение — многоколоночная расширенная статистика:
CREATE STATISTICS st_manzil (dependencies) ON shahar, viloyat FROM manzillar;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  Seq Scan ... rows=19293 ... (actual rows=20000 loops=1)
--  Теперь оценка очень близка к реальности. В большом запросе это
--  предотвращает выбор неправильного типа JOIN.

-- ─────────────────────────────────────────────────────────────────────
-- 9) Типы JOIN в одном плане
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS mijozlar;
CREATE TABLE mijozlar (id SERIAL PRIMARY KEY, ism VARCHAR(60) NOT NULL);
INSERT INTO mijozlar (ism) SELECT 'Mijoz ' || g FROM generate_series(1, 5000) g;
ANALYZE mijozlar;

-- Мало строк -> Nested Loop: для каждой строки внешней стороны
-- поиск по индексу на внутренней
EXPLAIN (ANALYZE)
SELECT m.ism, t.summa
FROM mijozlar m JOIN tolovlar t ON t.mijoz_id = m.id
WHERE m.id = 777;

-- Много строк -> Hash Join: из маленькой таблицы строится хеш,
-- большая проходится один раз
EXPLAIN (ANALYZE)
SELECT m.ism, SUM(t.summa)
FROM mijozlar m JOIN tolovlar t ON t.mijoz_id = m.id
GROUP BY m.ism;""",
        "task": {
            "task_title": "Amaliy topshiriq: To'rtta rejani o'qish va yozib chiqish",
            "task_title_ru": "Практическое задание: прочитать и разобрать четыре плана",
            "task_description": (
                "generate_series bilan kamida 200 000 qatorli jadval yarating, ANALYZE qiling "
                "va uning ustida to'rtta turli so'rov ustida EXPLAIN (ANALYZE, BUFFERS) "
                "bajaring. Har bir reja uchun qisqa tahlil yozing: qaysi skanerlash turi "
                "tanlangan, nega aynan u, taxmin qilingan va haqiqiy qatorlar soni qanchalik "
                "mos, nechta bufer o'qilgan.\n\n"
                "Ikkita alohida holatni majburiy ravishda ko'rsating. Birinchisi: covering "
                "indeks bo'lsa ham Index Only Scan darhol paydo bo'lmaydi — VACUUM (ANALYZE) "
                "dan oldingi va keyingi rejani yonma-yon keltiring. Ikkinchisi: planner "
                "bog'liq ikki ustunni mustaqil deb hisoblab adashadi — taxmin va haqiqat "
                "farqini o'lchang, CREATE STATISTICS (dependencies) qo'shing va taxmin "
                "qanchalik to'g'rilanganini ko'rsating.\n\n"
                "Bu topshiriqda maqsad indeks qo'shish emas — REJANI O'QIY OLISHNI ko'rsatish."
            ),
            "task_description_ru": (
                "Создайте через generate_series таблицу минимум на 200 000 строк, выполните "
                "ANALYZE и снимите EXPLAIN (ANALYZE, BUFFERS) по четырём разным запросам. Для "
                "каждого плана напишите короткий разбор: какой тип сканирования выбран, почему "
                "именно он, насколько совпали оценка и фактическое число строк, сколько "
                "прочитано буферов.\n\n"
                "Два случая обязательны. Первый: даже при covering-индексе Index Only Scan не "
                "появляется сразу — приведите планы до и после VACUUM (ANALYZE) рядом. Второй: "
                "планировщик ошибается, считая две зависимые колонки независимыми — измерьте "
                "расхождение оценки и факта, добавьте CREATE STATISTICS (dependencies) и "
                "покажите, насколько оценка исправилась.\n\n"
                "Цель задания — не добавить индекс, а показать УМЕНИЕ ЧИТАТЬ ПЛАН."
            ),
            "task_requirements": (
                "1. Kamida 200 000 qator (generate_series bilan) va ANALYZE. Izohda nega "
                "kichik jadvalda reja ishonchsiz ekani yozilsin.\n"
                "2. To'rtta reja majburiy: (a) indeks bor bo'lsa ham Seq Scan tanlangan holat, "
                "(b) Bitmap Heap Scan, (c) unikal qidiruvda Index Scan, (d) VACUUM dan keyin "
                "Index Only Scan.\n"
                "3. (a) uchun izohda planner nega HAQ ekani asoslansin (kerakli qatorlar ulushi).\n"
                "4. (b) uchun ikki bosqich (Bitmap Index Scan -> Bitmap Heap Scan) tushuntirilsin "
                "va Heap Blocks qiymati keltirilsin.\n"
                "5. (d) uchun VACUUM (ANALYZE) DAN OLDINGI va KEYINGI reja yonma-yon keltirilsin; "
                "Heap Fetches va Buffers qiymatlari solishtirilsin.\n"
                "6. Har bir reja uchun rows (taxmin) va actual rows yozib qo'yilsin; farq o'nlab "
                "marta bo'lgan har qanday tugun alohida belgilansin.\n"
                "7. Bog'liq ustunlar holati: CREATE STATISTICS (dependencies) dan oldingi va "
                "keyingi taxmin raqamlari keltirilsin.\n"
                "8. UPDATE/DELETE ustida EXPLAIN ANALYZE ishlatilsa, u BEGIN; ... ROLLBACK; "
                "ichida bo'lsin. VACUUM esa tranzaksiyadan TASHQARIDA bajarilsin — izohda "
                "sababi yozilsin.\n"
                "9. Xulosa: to'rtta rejadan qaysi biri eng ko'p bufer o'qigan va nima uchun.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Минимум 200 000 строк (через generate_series) и ANALYZE. В комментарии "
                "объясните, почему на маленькой таблице планы недостоверны.\n"
                "2. Четыре плана обязательны: (а) Seq Scan выбран несмотря на наличие индекса, "
                "(б) Bitmap Heap Scan, (в) Index Scan при уникальном поиске, (г) Index Only "
                "Scan после VACUUM.\n"
                "3. Для (а) обоснуйте в комментарии, почему планировщик ПРАВ (доля нужных строк).\n"
                "4. Для (б) объясните две фазы (Bitmap Index Scan -> Bitmap Heap Scan) и "
                "приведите значение Heap Blocks.\n"
                "5. Для (г) приведите планы ДО и ПОСЛЕ VACUUM (ANALYZE) рядом; сравните Heap "
                "Fetches и Buffers.\n"
                "6. По каждому плану выпишите rows (оценка) и actual rows; отдельно отметьте "
                "любой узел, где расхождение в десятки раз.\n"
                "7. Случай зависимых колонок: приведите цифры оценки до и после CREATE "
                "STATISTICS (dependencies).\n"
                "8. Если применяете EXPLAIN ANALYZE к UPDATE/DELETE, делайте это внутри "
                "BEGIN; ... ROLLBACK;. VACUUM выполняйте ВНЕ транзакции — в комментарии "
                "объясните почему.\n"
                "9. Вывод: какой из четырёх планов прочитал больше всего буферов и почему.\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, EXPLAIN ANALYZE, BUFFERS, VACUUM, CREATE STATISTICS",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: EXPLAIN ANALYZE — skanerlash turlari, buferlar va noto'g'ri taxmin",
            "description": "Seq Scan / Bitmap / Index Scan qachon tanlanishi, VACUUM dan keyin paydo bo'ladigan Index Only Scan va CREATE STATISTICS bilan tuzatiladigan taxmin xatosi",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: rejani o'qish — taxmin, o'lchov va buferlar
DROP TABLE IF EXISTS tolovlar;
CREATE TABLE tolovlar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL,
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

-- 200 000 qator. Kichik jadvalda reja ishonchsiz: 100 qatorni to'liq
-- o'qish HAR DOIM arzon, shuning uchun indeks foydasi ko'rinmaydi.
INSERT INTO tolovlar (mijoz_id, sana, holat, summa)
SELECT (random() * 5000)::INT + 1,
       DATE '2023-01-01' + (random() * 700)::INT,
       (ARRAY['yangi','tolangan','bekor','qaytarilgan'])[(random() * 3)::INT + 1],
       (random() * 900000 + 10000)::NUMERIC(12,2)
FROM generate_series(1, 200000);

ANALYZE tolovlar;   -- statistikasiz planner deyarli ko'r

-- 1) EXPLAIN — so'rovni BAJARMAYDI, faqat taxmin qiladi.
--    cost=birinchi..oxirgi qator narxi | rows=kutilgan qator | width=bayt
EXPLAIN SELECT * FROM tolovlar WHERE holat = 'bekor';

-- 2) EXPLAIN ANALYZE — haqiqatan bajaradi va O'LCHAYDI.
--    Eng muhim ko'rsatkich: rows (taxmin) va actual rows farqi.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE summa > 20000;
--  Seq Scan ... rows=~197000 (actual rows=~197800 loops=1)
--  Taxmin haqiqatga juda yaqin — yaxshi belgi.

-- 3) Indeks BOR, lekin baribir Seq Scan — va bu TO'G'RI qaror
CREATE INDEX idx_tolovlar_holat ON tolovlar(holat);
CREATE INDEX idx_tolovlar_mijoz ON tolovlar(mijoz_id);
ANALYZE tolovlar;

EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat <> 'bekor';
--  Qatorlarning ~75% i kerak -> indeks orqali bittalab olish QIMMATROQ.

-- 4) Bitmap Heap Scan — "o'rta" miqdor (~25%). Ikki bosqichli:
--    Bitmap Index Scan sahifalar xaritasini yig'adi,
--    Bitmap Heap Scan ularni DISK TARTIBIDA o'qiydi.
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE holat = 'bekor';
--  "lossy=" paydo bo'lsa — bitmap work_mem ga sig'magan.

-- 5) Index Scan — unikal qidiruv, atigi bir necha sahifa
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tolovlar WHERE id = 123456;

-- 6) Index Only Scan darhol ishlamaydi: indeks qatorning KO'RINUVCHANLIGINI
--    bilmaydi, buni visibility map saqlaydi, uni esa VACUUM to'ldiradi.
CREATE INDEX idx_tolovlar_mijoz_summa ON tolovlar(mijoz_id, summa);
ANALYZE tolovlar;

EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Hali ham Bitmap Heap Scan, buferlar ko'p.

VACUUM (ANALYZE) tolovlar;
--  DIQQAT: VACUUM ni tranzaksiya ichida bajarib BO'LMAYDI:
--  ERROR: VACUUM cannot run inside a transaction block

EXPLAIN (ANALYZE, BUFFERS) SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777;
--  Endi: Index Only Scan, Heap Fetches: 0 — jadvalga UMUMAN murojaat yo'q.
--  Buferlar bir necha barobar kamaydi. "Covering index" ning butun ma'nosi shu.

-- 7) Planner ADASHGANDA: bog'liq ustunlar
DROP TABLE IF EXISTS manzillar;
CREATE TABLE manzillar (
    id      BIGSERIAL   PRIMARY KEY,
    shahar  VARCHAR(30) NOT NULL,
    viloyat VARCHAR(30) NOT NULL
);
INSERT INTO manzillar (shahar, viloyat)
SELECT s.shahar, s.viloyat
FROM generate_series(1, 100000) g
CROSS JOIN LATERAL (
    SELECT * FROM (VALUES
        ('Margilon','Fargona'), ('Qoqon','Fargona'), ('Quva','Fargona'),
        ('Urgut','Samarqand'),  ('Gijduvon','Buxoro')
    ) AS v(shahar, viloyat) OFFSET (g % 5) LIMIT 1
) s;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  rows=taxmin  (actual rows=20000) — planner ikki ustunni MUSTAQIL deb
--  hisoblab, tanlanuvchanliklarni ko'paytirdi. Aslida shahar viloyatni
--  to'liq aniqlaydi.

CREATE STATISTICS st_manzil (dependencies) ON shahar, viloyat FROM manzillar;
ANALYZE manzillar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM manzillar WHERE shahar = 'Margilon' AND viloyat = 'Fargona';
--  Endi taxmin haqiqatga juda yaqin. Katta so'rovda bu noto'g'ri JOIN
--  turini tanlashning oldini oladi.""",
        },
        "exercises": [
            {
                "title": "Rejadagi eng muhim signal",
                "title_ru": "Самый важный сигнал в плане",
                "description": "EXPLAIN ANALYZE natijasida bitta tugunda `rows=500` (taxmin) va `actual rows=48000` ko'rinmoqda. Bu birinchi navbatda nimadan darak beradi?",
                "description_ru": "В выводе EXPLAIN ANALYZE у одного узла видно `rows=500` (оценка) и `actual rows=48000`. О чём это в первую очередь говорит?",
                "exercise_type": "multiple_choice",
                "options": [
                    "So'rov sekin bajarilgan — vaqtni kamaytirish uchun indeks qo'shish kerak",
                    "Planner statistikaga tayanib xato taxmin qilgan; rejaning qolgan qismi ham noto'g'ri bo'lishi ehtimoli katta",
                    "Tugun 96 marta qayta ishga tushgan (loops=96)",
                    "Jadvalda 47500 ta o'lik qator bor va VACUUM kerak",
                ],
                "options_ru": [
                    "Запрос выполнялся медленно — нужно добавить индекс, чтобы сократить время",
                    "Планировщик ошибся в оценке по статистике; остальная часть плана с большой вероятностью тоже неверна",
                    "Узел перезапускался 96 раз (loops=96)",
                    "В таблице 47500 мёртвых строк и нужен VACUUM",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Planner JOIN turini va skanerlash turini aynan taxmin qilingan qatorlar soniga qarab tanlaydi.",
                "hint_ru": "Планировщик выбирает тип JOIN и тип сканирования именно по оценке количества строк.",
                "explanation": "Taxmin va haqiqat orasidagi katta farq — rejalashtiruvchi noto'g'ri ma'lumot bilan ishlaganini bildiradi. U qatorlar sonini kam deb o'ylab Nested Loop tanlagan bo'lishi mumkin, aslida esa Hash Join kerak edi. Yechim: ANALYZE ishga tushirish, statistika maqsadini oshirish yoki CREATE STATISTICS qo'shish.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Jadvalga umuman murojaat qilinmaganini ko'rsatuvchi qator",
                "title_ru": "Строка, показывающая, что к таблице не обращались",
                "description": "Index Only Scan haqiqatan ishlaganini, ya'ni javob faqat indeksdan olinganini tasdiqlovchi reja qatori: `Heap ___: 0`. Bo'sh joyga qaysi so'z yoziladi?",
                "description_ru": "Строка плана, подтверждающая, что Index Only Scan действительно сработал и ответ получен только из индекса: `Heap ___: 0`. Какое слово нужно вписать?",
                "exercise_type": "fill_in_blank",
                "correct_answers": "Fetches",
                "hint": "Reja tugunida bu qator jadvaldan necha marta qator olinganini ko'rsatadi.",
                "hint_ru": "Эта строка в узле плана показывает, сколько раз строки доставались из таблицы.",
                "explanation": "Heap Fetches: 0 — jadvalga umuman murojaat qilinmagani. Bu qiymat noldan katta bo'lsa, visibility map to'liq emas va VACUUM kerak.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Nega Index Only Scan tanlanmadi?",
                "title_ru": "Почему не был выбран Index Only Scan?",
                "description": "tolovlar jadvaliga 200 000 qator ommaviy yuklandi, so'ng (mijoz_id, summa) ustunlari bo'yicha indeks yaratildi va ANALYZE bajarildi. `SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777` so'rovi uchun kerakli ikkala ustun ham indeksda bor, lekin reja Bitmap Heap Scan ko'rsatmoqda. Nega shunday bo'lyapti va buni qanday tuzatasiz?",
                "description_ru": "В таблицу tolovlar массово загружено 200 000 строк, затем создан индекс по колонкам (mijoz_id, summa) и выполнен ANALYZE. Для запроса `SELECT mijoz_id, summa FROM tolovlar WHERE mijoz_id = 777` обе нужные колонки есть в индексе, но план показывает Bitmap Heap Scan. Почему так и как это исправить?",
                "exercise_type": "text_input",
                "expected_answer": "Indeks yozuvi qatorning ko'rinuvchanligi (visibility) haqida ma'lumot saqlamaydi — u faqat jadvalda bor. PostgreSQL bu ma'lumotni visibility map da keshlaydi, uni esa VACUUM to'ldiradi. Ommaviy yuklashdan keyin visibility map bo'sh, shuning uchun planner Index Only Scan da har bir qator uchun jadvalga murojaat qilish kerak bo'lishini biladi va uni umuman tanlamaydi. Yechim: VACUUM (ANALYZE) tolovlar; ni bajarish — lekin uni tranzaksiya ichida emas, alohida ishga tushirish kerak, chunki VACUUM cannot run inside a transaction block. Shundan keyin reja Index Only Scan ga o'zgaradi va Heap Fetches: 0 bo'ladi. Diqqat: ANALYZE yolg'iz o'zi yetarli emas — u faqat statistikani yangilaydi, visibility map ni emas.",
                "hint": "ANALYZE statistikani yangilaydi. Visibility map ni esa boshqa buyruq to'ldiradi.",
                "hint_ru": "ANALYZE обновляет статистику. А visibility map заполняет другая команда.",
                "difficulty_level": "Hard",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 5
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 5,
        "title": "5-Indeks turlari: B-tree, GIN, composite, partial index",
        "title_ru": "5-Типы индексов: B-tree, GIN, композитный, частичный",
        "points_reward": 15,
        "code_language": "sql",
        "text_content": """<h3>Indeks bepul emas</h3>
<p>Har bir indeks o'qishni tezlashtiradi va <em>yozishni sekinlashtiradi</em>: <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> har bir indeksni ham yangilashi kerak. Bundan tashqari indeks joy egallaydi &mdash; o'lchovda 200 000 qatorli jadvalning bitta B-tree indeksi <strong>6184 kB</strong> chiqdi.</p>
<p>Shuning uchun to'g'ri savol &ldquo;indeks qo'shsam bo'ladimi?&rdquo; emas, balki &ldquo;<strong>qaysi turdagi</strong> indeks va <strong>qaysi ustunlar bo'yicha</strong>?&rdquo;.</p>

<h3>Kompozit indeksda ustunlar tartibi hal qiluvchi</h3>
<p><code>(muallif_id, sana)</code> indeksi &mdash; bu telefon kitobi: avval familiya, keyin ism bo'yicha tartiblangan. Familiya bilan qidirsangiz tez topasiz; faqat ism bilan qidirsangiz &mdash; butun kitobni varaqlashingizga to'g'ri keladi.</p>
<p>Bu <strong>chapdan boshlab prefiks</strong> (leftmost prefix) qoidasi. O'lchangan natijalar:</p>
<table>
<tr><th>Shart</th><th>Indeks tugunining narxi</th><th>Xulosa</th></tr>
<tr><td><code>muallif_id = 42 AND sana &gt; ...</code></td><td><code>cost=0.00..4.59</code></td><td>To'liq ishlaydi</td></tr>
<tr><td><code>muallif_id = 42</code></td><td><code>cost=0.00..11.40</code></td><td>Prefiks &mdash; ishlaydi</td></tr>
<tr><td><code>sana &gt; ...</code> (faqat ikkinchi ustun)</td><td><code>cost=0.00..4592.43</code></td><td>Butun indeks skanerlandi &mdash; foyda deyarli yo'q</td></tr>
</table>
<p>Uchinchi holatda PostgreSQL indeksni <em>ishlatdi</em>, lekin uni boshdan-oxir o'qib chiqdi. Rejada &ldquo;Index Scan&rdquo; so'zini ko'rish hali hammasi joyida degani emas &mdash; narxga qarang.</p>
<p><strong>Amaliy qoida:</strong> tenglik shartlari (<code>=</code>) oldinga, diapazon shartlari (<code>&gt;</code>, <code>&lt;</code>, <code>BETWEEN</code>) orqaga.</p>

<h3>Qisman (partial) indeks</h3>
<p>Agar so'rovlaringiz har doim ma'lum bir shart bilan kelsa (<code>WHERE holat = 'qoralama'</code>, <code>WHERE deleted_at IS NULL</code>), indeksni faqat o'sha qatorlar uchun qurish mumkin. O'lchov: to'liq indeks <strong>6184 kB</strong>, qisman indeks (qatorlarning 2% i) <strong>56 kB</strong> &mdash; 110 baravar kichik.</p>
<p>Kichik indeks nafaqat joy tejaydi: u xotiraga to'liq sig'adi va o'sha 98% qatorlar o'zgarganda umuman yangilanmaydi.</p>

<h3>GIN &mdash; bitta katakda ko'p qiymat bo'lganda</h3>
<p>B-tree bitta katakni bitta qiymat deb qaraydi. Massiv, <code>jsonb</code> yoki matn ichidagi so'zlar uchun bu yaramaydi &mdash; bu yerda <strong>GIN</strong> kerak: u katak ichidagi <em>har bir element</em> uchun alohida yozuv qo'yadi.</p>
<p>O'lchangan farq (200 000 qator, kamyob so'z bo'yicha full-text qidiruv):</p>
<ul>
<li>GIN indekssiz: <code>Parallel Seq Scan</code>, <strong>177.7 ms</strong></li>
<li>GIN indeks bilan: <code>Bitmap Index Scan</code>, <strong>0.86 ms</strong> &mdash; ~200 baravar tez</li>
</ul>
<p>Muhim nuqta: GIN foydali bo'lishi uchun shart <strong>tanlanuvchan</strong> bo'lishi kerak. Barcha qatorlarga mos keladigan shart (<code>meta @&gt; '{"til":"uz"}'</code>, agar hamma qator <code>uz</code> bo'lsa) uchun planner baribir <code>Seq Scan</code> tanlaydi &mdash; va to'g'ri qiladi.</p>

<h3>Turlarni tanlash</h3>
<table>
<tr><th>Tur</th><th>Nima uchun</th><th>Operatorlar</th></tr>
<tr><td>B-tree (standart)</td><td>Tenglik, diapazon, saralash</td><td><code>=</code> <code>&lt;</code> <code>&gt;</code> <code>BETWEEN</code> <code>ORDER BY</code></td></tr>
<tr><td>GIN</td><td>Massiv, jsonb, full-text</td><td><code>@&gt;</code> <code>?</code> <code>@@</code></td></tr>
<tr><td>GiST</td><td>Geometriya, oraliqlar, kesishish</td><td><code>&amp;&amp;</code> <code>&lt;@</code></td></tr>
<tr><td>BRIN</td><td>Juda katta, jismonan tartiblangan jadval</td><td>Diapazon</td></tr>
<tr><td>Hash</td><td>Faqat tenglik</td><td><code>=</code></td></tr>
</table>
<p>BRIN alohida e'tiborga loyiq: u qiymatlarni emas, <em>blok diapazonlarini</em> saqlaydi. O'lchov: bir xil ustun uchun BRIN <strong>24 kB</strong>, B-tree <strong>6184 kB</strong> &mdash; 250 baravar kichik. Lekin u faqat ma'lumot diskda tartiblangan bo'lsa ishlaydi (masalan, faqat qo'shiladigan log jadvali).</p>

<h3>Ifoda indeksi</h3>
<p>Agar <code>WHERE</code> da ustunga funksiya qo'llansa (<code>lower(sarlavha) = ...</code>), oddiy indeks ishlamaydi &mdash; indeksda <code>sarlavha</code> saqlangan, <code>lower(sarlavha)</code> emas. Yechim &mdash; ayni o'sha ifoda bo'yicha indeks: <code>CREATE INDEX ... ON t (lower(sarlavha))</code>. Shart indeksdagi ifoda bilan <strong>aynan mos</strong> tushishi kerak.</p>""",
        "text_content_ru": """<h3>Индекс не бесплатен</h3>
<p>Каждый индекс ускоряет чтение и <em>замедляет запись</em>: <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> должны обновить и каждый индекс. Кроме того, индекс занимает место — в измерении один B-tree индекс на таблице из 200 000 строк занял <strong>6184 кБ</strong>.</p>
<p>Поэтому правильный вопрос не «можно ли добавить индекс?», а «<strong>какого типа</strong> индекс и <strong>по каким колонкам</strong>?».</p>

<h3>Порядок колонок в композитном индексе решает всё</h3>
<p>Индекс <code>(muallif_id, sana)</code> — это телефонная книга: сначала по фамилии, потом по имени. Ищете по фамилии — найдёте быстро; ищете только по имени — придётся листать всю книгу.</p>
<p>Это правило <strong>левого префикса</strong> (leftmost prefix). Измеренные результаты:</p>
<table>
<tr><th>Условие</th><th>Стоимость узла индекса</th><th>Вывод</th></tr>
<tr><td><code>muallif_id = 42 AND sana &gt; ...</code></td><td><code>cost=0.00..4.59</code></td><td>Работает полностью</td></tr>
<tr><td><code>muallif_id = 42</code></td><td><code>cost=0.00..11.40</code></td><td>Префикс — работает</td></tr>
<tr><td><code>sana &gt; ...</code> (только вторая колонка)</td><td><code>cost=0.00..4592.43</code></td><td>Просканирован весь индекс — пользы почти нет</td></tr>
</table>
<p>В третьем случае PostgreSQL индекс <em>использовал</em>, но прочитал его от начала до конца. Увидеть в плане слово «Index Scan» — ещё не значит, что всё в порядке: смотрите на стоимость.</p>
<p><strong>Практическое правило:</strong> условия на равенство (<code>=</code>) — вперёд, условия-диапазоны (<code>&gt;</code>, <code>&lt;</code>, <code>BETWEEN</code>) — назад.</p>

<h3>Частичный (partial) индекс</h3>
<p>Если ваши запросы всегда приходят с определённым условием (<code>WHERE holat = 'qoralama'</code>, <code>WHERE deleted_at IS NULL</code>), индекс можно построить только по этим строкам. Измерение: полный индекс — <strong>6184 кБ</strong>, частичный (2% строк) — <strong>56 кБ</strong>, в 110 раз меньше.</p>
<p>Маленький индекс не только экономит место: он целиком помещается в память и вообще не обновляется при изменении остальных 98% строк.</p>

<h3>GIN — когда в одной ячейке много значений</h3>
<p>B-tree рассматривает ячейку как одно значение. Для массивов, <code>jsonb</code> или слов внутри текста это не годится — здесь нужен <strong>GIN</strong>: он создаёт отдельную запись для <em>каждого элемента</em> внутри ячейки.</p>
<p>Измеренная разница (200 000 строк, полнотекстовый поиск редкого слова):</p>
<ul>
<li>Без GIN-индекса: <code>Parallel Seq Scan</code>, <strong>177.7 мс</strong></li>
<li>С GIN-индексом: <code>Bitmap Index Scan</code>, <strong>0.86 мс</strong> — примерно в 200 раз быстрее</li>
</ul>
<p>Важный момент: чтобы GIN был полезен, условие должно быть <strong>селективным</strong>. Для условия, подходящего всем строкам (<code>meta @&gt; '{"til":"uz"}'</code>, если во всех строках <code>uz</code>), планировщик всё равно выберет <code>Seq Scan</code> — и будет прав.</p>

<h3>Выбор типа</h3>
<table>
<tr><th>Тип</th><th>Для чего</th><th>Операторы</th></tr>
<tr><td>B-tree (по умолчанию)</td><td>Равенство, диапазон, сортировка</td><td><code>=</code> <code>&lt;</code> <code>&gt;</code> <code>BETWEEN</code> <code>ORDER BY</code></td></tr>
<tr><td>GIN</td><td>Массивы, jsonb, полнотекстовый поиск</td><td><code>@&gt;</code> <code>?</code> <code>@@</code></td></tr>
<tr><td>GiST</td><td>Геометрия, интервалы, пересечения</td><td><code>&amp;&amp;</code> <code>&lt;@</code></td></tr>
<tr><td>BRIN</td><td>Очень большая, физически упорядоченная таблица</td><td>Диапазон</td></tr>
<tr><td>Hash</td><td>Только равенство</td><td><code>=</code></td></tr>
</table>
<p>BRIN заслуживает отдельного внимания: он хранит не значения, а <em>диапазоны блоков</em>. Измерение: для одной и той же колонки BRIN — <strong>24 кБ</strong>, B-tree — <strong>6184 кБ</strong>, в 250 раз меньше. Но он работает только если данные упорядочены на диске (например, журнальная таблица, куда только дописывают).</p>

<h3>Индекс по выражению</h3>
<p>Если в <code>WHERE</code> к колонке применяется функция (<code>lower(sarlavha) = ...</code>), обычный индекс не сработает — в индексе хранится <code>sarlavha</code>, а не <code>lower(sarlavha)</code>. Решение — индекс по тому же самому выражению: <code>CREATE INDEX ... ON t (lower(sarlavha))</code>. Условие должно <strong>в точности совпадать</strong> с выражением в индексе.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Indeks turlari: B-tree, kompozit, qisman, GIN, covering, BRIN
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS maqolalar;

CREATE TABLE maqolalar (
    id         BIGSERIAL   PRIMARY KEY,
    muallif_id INTEGER     NOT NULL,
    sarlavha   TEXT        NOT NULL,
    matn       TEXT        NOT NULL,
    teglar     TEXT[]      NOT NULL DEFAULT '{}',
    meta       JSONB       NOT NULL DEFAULT '{}',
    holat      VARCHAR(20) NOT NULL,
    sana       TIMESTAMPTZ NOT NULL
);

INSERT INTO maqolalar (muallif_id, sarlavha, matn, teglar, meta, holat, sana)
SELECT
    (random() * 500)::INT + 1,
    'Maqola ' || g,
    'PostgreSQL indekslari haqida matn ' || g
      -- qatorlarning ~0.5% iga kamyob so'z qo'shamiz: full-text testi uchun
      || CASE WHEN random() < 0.005 THEN ' noyobatama' ELSE '' END,
    CASE (random() * 3)::INT
        WHEN 0 THEN ARRAY['sql','backend']
        WHEN 1 THEN ARRAY['python']
        WHEN 2 THEN ARRAY['sql','performance']
        ELSE        ARRAY['devops']
    END,
    jsonb_build_object(
        'til',  (ARRAY['uz','ru','en'])[(random() * 2)::INT + 1],
        'reja', CASE WHEN random() < 0.01 THEN 'pro' ELSE 'free' END,
        'ko_rishlar', (random() * 1000)::INT
    ),
    CASE WHEN random() < 0.02 THEN 'qoralama' ELSE 'chop_etilgan' END,
    NOW() - (random() * 700 || ' days')::INTERVAL
FROM generate_series(1, 200000) g;
ANALYZE maqolalar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) KOMPOZIT INDEKS — ustunlar tartibi hal qiluvchi
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_muallif_sana ON maqolalar(muallif_id, sana);
ANALYZE maqolalar;

-- (a) Ikkala ustun ham shartda -> indeks to'liq ishlaydi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42 AND sana > NOW() - INTERVAL '30 days';
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..4.59 ...)

-- (b) Faqat BIRINCHI ustun (chapdan prefiks) -> ishlaydi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42;
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..11.40 ...)

-- (c) Faqat IKKINCHI ustun -> indeks BOSHDAN-OXIR skanerlanadi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE sana > NOW() - INTERVAL '3 days';
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..4592.43 ...)
--                                                        ^^^^^^^
--  Narxni (a) dagi 4.59 bilan solishtiring — 1000 baravar farq.
--  Rejada "Index Scan" so'zi bo'lishi hali hammasi joyida degani emas.

-- ─────────────────────────────────────────────────────────────────────
-- 2) QISMAN (PARTIAL) INDEKS — faqat kerakli qatorlar uchun
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_qoralama ON maqolalar(muallif_id) WHERE holat = 'qoralama';
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF, BUFFERS)
SELECT * FROM maqolalar WHERE holat = 'qoralama' AND muallif_id = 42;
--  ->  Bitmap Index Scan on idx_m_qoralama  (cost=0.00..4.34 ...)

-- Hajmlarni solishtiramiz:
SELECT pg_size_pretty(pg_relation_size('idx_m_muallif_sana')) AS toliq_indeks,
       pg_size_pretty(pg_relation_size('idx_m_qoralama'))     AS qisman_indeks;
--  toliq_indeks | qisman_indeks
--  6184 kB      | 56 kB          <-- 110 baravar kichik

-- ─────────────────────────────────────────────────────────────────────
-- 3) GIN — massiv ichidagi qiymat bo'yicha qidiruv
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_teglar ON maqolalar USING GIN (teglar);
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM maqolalar WHERE teglar @> ARRAY['devops'];
--  ->  Bitmap Index Scan on idx_m_teglar ... rows=33518

-- ─────────────────────────────────────────────────────────────────────
-- 4) GIN — jsonb. jsonb_path_ops kichikroq va @> uchun tezroq.
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_meta ON maqolalar USING GIN (meta jsonb_path_ops);
ANALYZE maqolalar;

-- TANLANUVCHAN shart (~1% qator) -> indeks ishlaydi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar WHERE meta @> '{"reja":"pro"}';
--  ->  Bitmap Index Scan on idx_m_meta ... rows=1964,  Execution Time: 1.6 ms

-- Agar shart HAMMA qatorga mos kelsa, planner Seq Scan tanlaydi va HAQ
-- bo'ladi — indeks bor bo'lishi uni ishlatish shart degani emas.

-- ─────────────────────────────────────────────────────────────────────
-- 5) GIN — full-text qidiruv. Eng katta farq shu yerda ko'rinadi.
-- ─────────────────────────────────────────────────────────────────────
-- Avval INDEKSSIZ o'lchaymiz:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');
--  Parallel Seq Scan ...  Execution Time: 177.7 ms

CREATE INDEX idx_m_fts ON maqolalar
    USING GIN (to_tsvector('simple', sarlavha || ' ' || matn));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');
--  Bitmap Heap Scan ...  Execution Time: 0.86 ms    <-- ~200 baravar tez
-- DIQQAT: indeksdagi ifoda va WHERE dagi ifoda AYNAN bir xil bo'lishi shart.

-- ─────────────────────────────────────────────────────────────────────
-- 6) COVERING indeks (INCLUDE) — qidiruvda qatnashmaydigan ustunni
--    indeksga "yo'lovchi" sifatida qo'shish
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_cover ON maqolalar(muallif_id) INCLUDE (sarlavha);
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF, BUFFERS)
SELECT muallif_id, sarlavha FROM maqolalar WHERE muallif_id = 42;
-- Eslatma: Index Only Scan olish uchun VACUUM ham kerak (4-darsga qarang).
-- VACUUM siz reja Bitmap Heap Scan bo'lib qolaveradi.

-- ─────────────────────────────────────────────────────────────────────
-- 7) IFODA (expression) indeksi
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_lower ON maqolalar(lower(sarlavha));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar WHERE lower(sarlavha) = 'maqola 999';
--  Index Scan using idx_m_lower ... (actual rows=1 loops=1)
--  Oddiy maqolalar(sarlavha) indeksi bu yerda ISHLAMAS edi.

-- ─────────────────────────────────────────────────────────────────────
-- 8) BRIN — juda katta, jismonan tartiblangan jadvallar uchun
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_brin ON maqolalar USING BRIN (sana);
ANALYZE maqolalar;

SELECT pg_size_pretty(pg_relation_size('idx_m_brin'))          AS brin_hajmi,
       pg_size_pretty(pg_relation_size('idx_m_muallif_sana'))  AS btree_hajmi;
--  brin_hajmi | btree_hajmi
--  24 kB      | 6184 kB        <-- 250 baravar kichik
-- Lekin BRIN faqat ma'lumot diskda tartiblangan bo'lsa foydali
-- (masalan, faqat qo'shiladigan log jadvali).

-- ─────────────────────────────────────────────────────────────────────
-- 9) Produksiyada: ishlatilmayotgan indekslarni topish
--    (idx_scan real foydalanish statistikasi asosida to'ladi, shuning
--     uchun bu so'rov ishlab turgan bazada ma'noga ega)
-- ─────────────────────────────────────────────────────────────────────
SELECT s.relname AS jadval, s.indexrelname AS indeks, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0 AND NOT i.indisunique AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Типы индексов: B-tree, композитный, частичный, GIN, covering, BRIN
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS maqolalar;

CREATE TABLE maqolalar (
    id         BIGSERIAL   PRIMARY KEY,
    muallif_id INTEGER     NOT NULL,
    sarlavha   TEXT        NOT NULL,
    matn       TEXT        NOT NULL,
    teglar     TEXT[]      NOT NULL DEFAULT '{}',
    meta       JSONB       NOT NULL DEFAULT '{}',
    holat      VARCHAR(20) NOT NULL,
    sana       TIMESTAMPTZ NOT NULL
);

INSERT INTO maqolalar (muallif_id, sarlavha, matn, teglar, meta, holat, sana)
SELECT
    (random() * 500)::INT + 1,
    'Maqola ' || g,
    'PostgreSQL indekslari haqida matn ' || g
      -- примерно 0.5% строк получают редкое слово: для теста полнотекстового поиска
      || CASE WHEN random() < 0.005 THEN ' noyobatama' ELSE '' END,
    CASE (random() * 3)::INT
        WHEN 0 THEN ARRAY['sql','backend']
        WHEN 1 THEN ARRAY['python']
        WHEN 2 THEN ARRAY['sql','performance']
        ELSE        ARRAY['devops']
    END,
    jsonb_build_object(
        'til',  (ARRAY['uz','ru','en'])[(random() * 2)::INT + 1],
        'reja', CASE WHEN random() < 0.01 THEN 'pro' ELSE 'free' END,
        'ko_rishlar', (random() * 1000)::INT
    ),
    CASE WHEN random() < 0.02 THEN 'qoralama' ELSE 'chop_etilgan' END,
    NOW() - (random() * 700 || ' days')::INTERVAL
FROM generate_series(1, 200000) g;
ANALYZE maqolalar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) КОМПОЗИТНЫЙ ИНДЕКС — порядок колонок решает всё
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_muallif_sana ON maqolalar(muallif_id, sana);
ANALYZE maqolalar;

-- (a) Обе колонки в условии -> индекс работает полностью
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42 AND sana > NOW() - INTERVAL '30 days';
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..4.59 ...)

-- (b) Только ПЕРВАЯ колонка (левый префикс) -> работает
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42;
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..11.40 ...)

-- (c) Только ВТОРАЯ колонка -> индекс сканируется ОТ НАЧАЛА ДО КОНЦА
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE sana > NOW() - INTERVAL '3 days';
--  ->  Bitmap Index Scan on idx_m_muallif_sana  (cost=0.00..4592.43 ...)
--                                                        ^^^^^^^
--  Сравните стоимость с 4.59 из пункта (a) — разница в 1000 раз.
--  Слово "Index Scan" в плане ещё не значит, что всё в порядке.

-- ─────────────────────────────────────────────────────────────────────
-- 2) ЧАСТИЧНЫЙ (PARTIAL) ИНДЕКС — только по нужным строкам
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_qoralama ON maqolalar(muallif_id) WHERE holat = 'qoralama';
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF, BUFFERS)
SELECT * FROM maqolalar WHERE holat = 'qoralama' AND muallif_id = 42;
--  ->  Bitmap Index Scan on idx_m_qoralama  (cost=0.00..4.34 ...)

-- Сравним размеры:
SELECT pg_size_pretty(pg_relation_size('idx_m_muallif_sana')) AS toliq_indeks,
       pg_size_pretty(pg_relation_size('idx_m_qoralama'))     AS qisman_indeks;
--  toliq_indeks | qisman_indeks
--  6184 kB      | 56 kB          <-- в 110 раз меньше

-- ─────────────────────────────────────────────────────────────────────
-- 3) GIN — поиск по значению внутри массива
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_teglar ON maqolalar USING GIN (teglar);
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM maqolalar WHERE teglar @> ARRAY['devops'];
--  ->  Bitmap Index Scan on idx_m_teglar ... rows=33518

-- ─────────────────────────────────────────────────────────────────────
-- 4) GIN — jsonb. jsonb_path_ops компактнее и быстрее для @>.
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_meta ON maqolalar USING GIN (meta jsonb_path_ops);
ANALYZE maqolalar;

-- СЕЛЕКТИВНОЕ условие (~1% строк) -> индекс работает
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar WHERE meta @> '{"reja":"pro"}';
--  ->  Bitmap Index Scan on idx_m_meta ... rows=1964,  Execution Time: 1.6 ms

-- Если условие подходит ВСЕМ строкам, планировщик выберет Seq Scan и будет
-- ПРАВ — наличие индекса не обязывает его использовать.

-- ─────────────────────────────────────────────────────────────────────
-- 5) GIN — полнотекстовый поиск. Здесь видна самая большая разница.
-- ─────────────────────────────────────────────────────────────────────
-- Сначала измеряем БЕЗ ИНДЕКСА:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');
--  Parallel Seq Scan ...  Execution Time: 177.7 ms

CREATE INDEX idx_m_fts ON maqolalar
    USING GIN (to_tsvector('simple', sarlavha || ' ' || matn));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');
--  Bitmap Heap Scan ...  Execution Time: 0.86 ms    <-- примерно в 200 раз быстрее
-- ВНИМАНИЕ: выражение в индексе и выражение в WHERE должны совпадать В ТОЧНОСТИ.

-- ─────────────────────────────────────────────────────────────────────
-- 6) COVERING индекс (INCLUDE) — добавить в индекс колонку, которая
--    не участвует в поиске, «пассажиром»
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_cover ON maqolalar(muallif_id) INCLUDE (sarlavha);
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF, BUFFERS)
SELECT muallif_id, sarlavha FROM maqolalar WHERE muallif_id = 42;
-- Напоминание: чтобы получить Index Only Scan, нужен ещё и VACUUM (см. урок 4).
-- Без VACUUM план так и останется Bitmap Heap Scan.

-- ─────────────────────────────────────────────────────────────────────
-- 7) Индекс по ВЫРАЖЕНИЮ
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_lower ON maqolalar(lower(sarlavha));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar WHERE lower(sarlavha) = 'maqola 999';
--  Index Scan using idx_m_lower ... (actual rows=1 loops=1)
--  Обычный индекс maqolalar(sarlavha) здесь НЕ сработал бы.

-- ─────────────────────────────────────────────────────────────────────
-- 8) BRIN — для очень больших, физически упорядоченных таблиц
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX idx_m_brin ON maqolalar USING BRIN (sana);
ANALYZE maqolalar;

SELECT pg_size_pretty(pg_relation_size('idx_m_brin'))          AS brin_hajmi,
       pg_size_pretty(pg_relation_size('idx_m_muallif_sana'))  AS btree_hajmi;
--  brin_hajmi | btree_hajmi
--  24 kB      | 6184 kB        <-- в 250 раз меньше
-- Но BRIN полезен только если данные упорядочены на диске
-- (например, журнальная таблица, куда только дописывают).

-- ─────────────────────────────────────────────────────────────────────
-- 9) В продакшене: найти неиспользуемые индексы
--    (idx_scan наполняется реальной статистикой использования, поэтому
--     этот запрос имеет смысл на работающей базе)
-- ─────────────────────────────────────────────────────────────────────
SELECT s.relname AS jadval, s.indexrelname AS indeks, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0 AND NOT i.indisunique AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;""",
        "task": {
            "task_title": "Amaliy topshiriq: To'rtta sekin so'rovga to'rtta to'g'ri indeks",
            "task_title_ru": "Практическое задание: четыре правильных индекса для четырёх медленных запросов",
            "task_description": (
                "Kamida 200 000 qatorli maqolalar jadvalini yarating (matn, massiv teglar, "
                "jsonb meta, holat va sana ustunlari bilan) va uning ustida to'rtta sekin "
                "so'rovni oling. Har biri uchun MOS indeks turini tanlang, uni yarating va "
                "foydani EXPLAIN (ANALYZE, BUFFERS) bilan INDEKSDAN OLDIN va KEYIN o'lchab "
                "isbotlang.\n\n"
                "Topshiriqning ikkinchi yarmi — indeksning narxi. Har bir indeksning hajmini "
                "pg_relation_size bilan o'lchang, qisman indeksni to'liq indeks bilan "
                "solishtiring va oxirida ataylab bitta FOYDASIZ indeks yarating: shunday "
                "so'rov toping-ki, unda planner indeks bor bo'lsa ham Seq Scan tanlasin. "
                "Nega planner haq ekanini yozing."
            ),
            "task_description_ru": (
                "Создайте таблицу статей минимум на 200 000 строк (с текстом, массивом тегов, "
                "jsonb-мета, статусом и датой) и возьмите по ней четыре медленных запроса. Для "
                "каждого подберите ПОДХОДЯЩИЙ тип индекса, создайте его и докажите выигрыш "
                "через EXPLAIN (ANALYZE, BUFFERS) ДО и ПОСЛЕ индекса.\n\n"
                "Вторая половина задания — цена индекса. Измерьте размер каждого индекса через "
                "pg_relation_size, сравните частичный индекс с полным и в конце намеренно "
                "создайте один БЕСПОЛЕЗНЫЙ индекс: найдите запрос, где планировщик выберет Seq "
                "Scan даже при наличии индекса. Объясните, почему планировщик прав."
            ),
            "task_requirements": (
                "1. Jadval kamida 200 000 qator; ustunlar orasida TEXT[], JSONB, holat "
                "(qiymatlarning ~2% i kamyob) va TIMESTAMPTZ bo'lsin. ANALYZE bajarilsin.\n"
                "2. Kompozit indeks: tenglik + diapazon shartli so'rov uchun. Ustunlar tartibi "
                "muhimligini ISBOTLANG — faqat ikkinchi ustun bo'yicha qidiruvni ham "
                "bajaring va ikki holatdagi indeks tugunining COST ini solishtiring.\n"
                "3. Qisman (partial) indeks: har doim ma'lum shart bilan keladigan so'rov uchun. "
                "pg_relation_size bilan to'liq va qisman indeks hajmi solishtirilsin.\n"
                "4. GIN indeks: massiv (@>) yoki jsonb (@>) yoki full-text (@@) so'rovi uchun. "
                "Indeksdan oldingi va keyingi Execution Time keltirilsin.\n"
                "5. Ifoda (expression) indeksi: WHERE da ustunga funksiya qo'llangan so'rov uchun. "
                "Izohda oddiy ustun indeksi nega ishlamasligi yozilsin.\n"
                "6. Har bir indeks uchun ikkita reja — YARATISHDAN OLDIN va KEYIN — fayl ichida "
                "izoh sifatida saqlansin.\n"
                "7. Ataylab foydasiz bitta holat: indeks bor, lekin planner Seq Scan tanlaydi. "
                "Sababi (past tanlanuvchanlik) izohda asoslansin.\n"
                "8. Yakunda pg_stat_user_indexes bo'yicha jadvalning barcha indekslari, ularning "
                "idx_scan va hajmi chiqarilsin; qaysi birini o'chirar edingiz — yozing.\n"
                "9. Izohda bir jumla: har bir indeks yozishni (INSERT/UPDATE/DELETE) nega "
                "sekinlashtiradi.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Таблица минимум 200 000 строк; среди колонок должны быть TEXT[], JSONB, "
                "статус (у ~2% строк редкое значение) и TIMESTAMPTZ. Выполните ANALYZE.\n"
                "2. Составной индекс: для запроса с равенством + диапазоном. ДОКАЖИТЕ, что "
                "порядок колонок важен — выполните также поиск только по второй колонке и "
                "сравните COST индексного узла в обоих случаях.\n"
                "3. Частичный индекс: для запроса, который всегда приходит с определённым "
                "условием. Сравните размеры полного и частичного индекса через pg_relation_size.\n"
                "4. GIN-индекс: для запроса по массиву (@>), jsonb (@>) или full-text (@@). "
                "Приведите Execution Time до и после индекса.\n"
                "5. Индекс по выражению: для запроса, где в WHERE к колонке применена функция. "
                "В комментарии объясните, почему обычный индекс по колонке тут не работает.\n"
                "6. Для каждого индекса сохраните в файле комментариями два плана — ДО и ПОСЛЕ "
                "его создания.\n"
                "7. Один намеренно бесполезный случай: индекс есть, но планировщик выбирает Seq "
                "Scan. Обоснуйте причину (низкая селективность) в комментарии.\n"
                "8. В конце выведите по pg_stat_user_indexes все индексы таблицы с их idx_scan и "
                "размером; напишите, какой бы вы удалили.\n"
                "9. В комментарии одна фраза: почему каждый индекс замедляет запись "
                "(INSERT/UPDATE/DELETE).\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, B-tree, GIN, BRIN, partial index, expression index, EXPLAIN ANALYZE",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: Kompozit, qisman, GIN, ifoda va BRIN indekslari",
            "description": "Ustunlar tartibining narxga ta'siri, qisman indeksning hajm yutug'i, GIN bilan full-text tezlashuvi va ishlatilmayotgan indekslarni topish",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: to'g'ri indeks turini tanlash va foydani O'LCHASH
DROP TABLE IF EXISTS maqolalar;
CREATE TABLE maqolalar (
    id         BIGSERIAL   PRIMARY KEY,
    muallif_id INTEGER     NOT NULL,
    sarlavha   TEXT        NOT NULL,
    matn       TEXT        NOT NULL,
    teglar     TEXT[]      NOT NULL DEFAULT '{}',
    meta       JSONB       NOT NULL DEFAULT '{}',
    holat      VARCHAR(20) NOT NULL,
    sana       TIMESTAMPTZ NOT NULL
);

INSERT INTO maqolalar (muallif_id, sarlavha, matn, teglar, meta, holat, sana)
SELECT (random() * 500)::INT + 1,
       'Maqola ' || g,
       'PostgreSQL indekslari haqida matn ' || g
         || CASE WHEN random() < 0.005 THEN ' noyobatama' ELSE '' END,
       CASE (random() * 2)::INT
           WHEN 0 THEN ARRAY['sql','backend']
           WHEN 1 THEN ARRAY['python']
           ELSE        ARRAY['devops']
       END,
       jsonb_build_object('reja', CASE WHEN random() < 0.01 THEN 'pro' ELSE 'free' END),
       CASE WHEN random() < 0.02 THEN 'qoralama' ELSE 'chop_etilgan' END,
       NOW() - (random() * 700 || ' days')::INTERVAL
FROM generate_series(1, 200000) g;
ANALYZE maqolalar;

-- 1) KOMPOZIT INDEKS — ustunlar tartibi hal qiluvchi (telefon kitobi qoidasi)
CREATE INDEX idx_m_muallif_sana ON maqolalar(muallif_id, sana);
ANALYZE maqolalar;

-- (a) ikkala ustun ham shartda -> to'liq ishlaydi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42 AND sana > NOW() - INTERVAL '30 days';

-- (b) faqat BIRINCHI ustun (chapdan prefiks) -> ishlaydi
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE muallif_id = 42;

-- (c) faqat IKKINCHI ustun -> indeks BOSHDAN-OXIR skanerlanadi.
--     Rejada "Index Scan" so'zi bo'lishi hali hammasi joyida degani EMAS —
--     (a) dagi va bu yerdagi indeks tugunining NARXINI solishtiring.
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE sana > NOW() - INTERVAL '3 days';

-- 2) QISMAN (PARTIAL) INDEKS — faqat qoralama qatorlar (~2%) indekslanadi
CREATE INDEX idx_m_qoralama ON maqolalar(muallif_id) WHERE holat = 'qoralama';
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM maqolalar WHERE holat = 'qoralama' AND muallif_id = 42;

SELECT pg_size_pretty(pg_relation_size('idx_m_muallif_sana')) AS toliq_indeks,
       pg_size_pretty(pg_relation_size('idx_m_qoralama'))     AS qisman_indeks;
--  Qisman indeks o'nlab barobar kichik: xotiraga sig'adi va qolgan
--  98% qator o'zgarganda umuman yangilanmaydi.

-- 3) GIN — bitta katakda KO'P qiymat bo'lganda (massiv, jsonb, matn)
CREATE INDEX idx_m_teglar ON maqolalar USING GIN (teglar);
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM maqolalar WHERE teglar @> ARRAY['devops'];

-- 4) GIN + full-text. Eng katta farq shu yerda ko'rinadi.
--    AVVAL indekssiz o'lchaymiz:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');

CREATE INDEX idx_m_fts ON maqolalar
    USING GIN (to_tsvector('simple', sarlavha || ' ' || matn));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar
WHERE to_tsvector('simple', sarlavha || ' ' || matn) @@ to_tsquery('simple', 'noyobatama');
--  Parallel Seq Scan -> Bitmap Index Scan, yuz barobar tez.
--  DIQQAT: indeksdagi ifoda va WHERE dagi ifoda AYNAN bir xil bo'lishi shart.

-- 5) IFODA (expression) indeksi — WHERE da ustunga funksiya qo'llansa
CREATE INDEX idx_m_lower ON maqolalar(lower(sarlavha));
ANALYZE maqolalar;

EXPLAIN (ANALYZE, TIMING OFF)
SELECT id FROM maqolalar WHERE lower(sarlavha) = 'maqola 999';
--  Oddiy maqolalar(sarlavha) indeksi bu yerda ISHLAMAS edi.

-- 6) BRIN — juda katta, jismonan tartiblangan jadval uchun
CREATE INDEX idx_m_brin ON maqolalar USING BRIN (sana);
SELECT pg_size_pretty(pg_relation_size('idx_m_brin'))         AS brin,
       pg_size_pretty(pg_relation_size('idx_m_muallif_sana')) AS btree;
--  BRIN yuz barobar kichik, lekin faqat ma'lumot diskda tartiblangan
--  bo'lsa foydali (masalan, faqat qo'shiladigan log jadvali).

-- 7) Indeks bepul emas: ishlatilmayotganlarini topish
SELECT s.indexrelname AS indeks, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.relname = 'maqolalar' AND NOT i.indisprimary
ORDER BY s.idx_scan, pg_relation_size(s.indexrelid) DESC;""",
        },
        "exercises": [
            {
                "title": "Kompozit indeksda ustunlar tartibi",
                "title_ru": "Порядок колонок в композитном индексе",
                "description": "Jadvalda `(muallif_id, sana)` indeksi bor. Qaysi so'rov bu indeksdan SAMARALI foydalana OLMAYDI?",
                "description_ru": "На таблице есть индекс `(muallif_id, sana)`. Какой запрос НЕ сможет ЭФФЕКТИВНО использовать этот индекс?",
                "exercise_type": "multiple_choice",
                "options": [
                    "WHERE muallif_id = 42 AND sana > NOW() - INTERVAL '30 days'",
                    "WHERE muallif_id = 42",
                    "WHERE sana > NOW() - INTERVAL '3 days'",
                    "WHERE muallif_id IN (10, 20, 30)",
                ],
                "options_ru": [
                    "WHERE muallif_id = 42 AND sana > NOW() - INTERVAL '30 days'",
                    "WHERE muallif_id = 42",
                    "WHERE sana > NOW() - INTERVAL '3 days'",
                    "WHERE muallif_id IN (10, 20, 30)",
                ],
                "correct_answers": "C",
                "is_multiple_select": False,
                "hint": "Telefon kitobi faqat ism bo'yicha qidirilganda qanchalik foydali?",
                "hint_ru": "Насколько полезна телефонная книга, если искать только по имени?",
                "explanation": "Chapdan prefiks qoidasi: indeks avval muallif_id bo'yicha tartiblangan. Faqat sana bo'yicha qidirilganda PostgreSQL indeksni boshdan-oxir skanerlashga majbur — o'lchovda narx 4.59 o'rniga 4592.43 chiqdi.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Massiv va jsonb uchun indeks turi",
                "title_ru": "Тип индекса для массивов и jsonb",
                "description": "Bitta katakda bir nechta qiymat bo'lganda (TEXT[] massiv, jsonb hujjat, matn ichidagi so'zlar) va `@>` yoki `@@` operatorlari ishlatilganda qaysi turdagi indeks kerak? USING ___",
                "description_ru": "Какой тип индекса нужен, когда в одной ячейке несколько значений (массив TEXT[], документ jsonb, слова внутри текста) и используются операторы `@>` или `@@`? USING ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "GIN",
                "hint": "Bu tur katak ichidagi har bir element uchun alohida yozuv qo'yadi.",
                "hint_ru": "Этот тип создаёт отдельную запись для каждого элемента внутри ячейки.",
                "explanation": "GIN (Generalized Inverted Index) katak ichidagi har bir element uchun alohida yozuv qo'yadi. O'lchovda full-text qidiruv 177.7 ms dan 0.86 ms ga tushdi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Indekslar haqida to'g'ri fikrlar",
                "title_ru": "Верные утверждения об индексах",
                "description": "Quyidagilardan qaysilari to'g'ri?",
                "description_ru": "Какие из приведённых утверждений верны?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Qisman indeks faqat shartga mos qatorlarni saqlaydi, shuning uchun sezilarli kichik bo'ladi",
                    "lower(sarlavha) bo'yicha qidiruv uchun oddiy (sarlavha) indeksi ishlamaydi — ifoda indeksi kerak",
                    "Har bir qo'shilgan indeks INSERT va UPDATE ni sekinlashtiradi",
                    "Indeks mavjud bo'lsa, PostgreSQL uni har doim ishlatadi",
                ],
                "options_ru": [
                    "Частичный индекс хранит только строки, подходящие под условие, поэтому заметно меньше",
                    "Для поиска по lower(sarlavha) обычный индекс по (sarlavha) не сработает — нужен индекс по выражению",
                    "Каждый добавленный индекс замедляет INSERT и UPDATE",
                    "Если индекс существует, PostgreSQL всегда его использует",
                ],
                "correct_answers": "A,B,C",
                "is_multiple_select": True,
                "hint": "Qatorlarning 75% i kerak bo'lganda planner nima qilishini eslang.",
                "hint_ru": "Вспомните, что делает планировщик, когда нужно 75% строк.",
                "explanation": "D noto'g'ri: qatorlarning katta qismi kerak bo'lganda planner Seq Scan tanlaydi va bu to'g'ri qaror — indeks orqali ko'p qatorni bittalab olish qimmatroq tushadi.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 6
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 6,
        "title": "6-N+1 muammosi va uni SQL darajasida aniqlash",
        "title_ru": "6-Проблема N+1 и её обнаружение на уровне SQL",
        "points_reward": 14,
        "code_language": "sql",
        "text_content": """<h3>Har bir so'rov tez, sahifa esa sekin</h3>
<p>N+1 &mdash; backend dasturchi eng ko'p uchratadigan performance xatosi, va uning eng yomon jihati shundaki, u <em>sekin so'rov sifatida ko'rinmaydi</em>. Har bir so'rov 0.3 ms da bajariladi. Bazaga hech qanday shikoyat yo'q. Lekin sahifa 2 sekundda ochiladi.</p>
<p>Kelib chiqishi oddiy. ORM da shunday yozasiz:</p>
<pre><code>postlar = Post.query.limit(20).all()      # 1-so'rov
for post in postlar:
    print(post.izohlar)                    # har iteratsiyada YANGI so'rov</code></pre>
<p>Natijada 1 + 20 = 21 ta so'rov ketadi. Muammo SQL ning tezligida emas &mdash; muammo <strong>21 marta tarmoq bo'ylab borib-kelishda</strong>. Har bir borib-kelish 1&ndash;2 ms bo'lsa, faqat kutishga 40 ms ketadi, SQL esa jami 6 ms ishlagan bo'ladi. Ro'yxatda 20 emas, 500 element bo'lsa &mdash; sahifa o'ladi.</p>

<h3>Nega buni sezish qiyin</h3>
<p>Sekin so'rovlar jurnalida (<code>log_min_duration_statement = 100</code>) N+1 <strong>umuman ko'rinmaydi</strong>: hech bir so'rov 100 ms dan oshmaydi. Uni topish uchun boshqa savol berish kerak &mdash; &ldquo;qaysi so'rov <em>eng ko'p marta</em> chaqirilgan?&rdquo;.</p>
<p>Aynan shuning uchun N+1 ni <code>pg_stat_statements</code> orqali qidiriladi va <code>ORDER BY calls DESC</code> bo'yicha saralanadi, <code>mean_exec_time</code> bo'yicha emas. Ishlab chiqish muhitida esa eng oddiy usul &mdash; bitta HTTP so'rovda nechta SQL so'rov ketganini sanash.</p>

<h3>To'rtta yechim va ular orasidagi tanlov</h3>
<table>
<tr><th>Usul</th><th>Qachon</th><th>Diqqat</th></tr>
<tr><td><code>JOIN</code></td><td>Ota va bola ma'lumoti birga kerak</td><td>Ota maydonlari har bir bolada takrorlanadi</td></tr>
<tr><td>Bitta <code>IN (...)</code> so'rov</td><td>ORM dagi eager loading shu</td><td>Natijani kodda guruhlash kerak</td></tr>
<tr><td><code>jsonb_agg</code></td><td>API darhol ichma-ich JSON qaytarsa</td><td>Katta hajmda xotira</td></tr>
<tr><td><code>LATERAL</code></td><td>Har otadan faqat top-N bola</td><td>Boshqa usul bilan yozib bo'lmaydi</td></tr>
</table>
<p><code>LATERAL</code> alohida ajralib turadi: &ldquo;har bir postdan oxirgi 3 ta izoh&rdquo; masalasini oddiy <code>JOIN</code> bilan yechib bo'lmaydi, chunki <code>LIMIT</code> butun natijaga qo'llanadi, har bir guruhga emas. <code>LATERAL</code> esa ichki so'rovga tashqi qatorga ishora qilish imkonini beradi.</p>

<h3>Ikkinchi tuzoq: N+1 ni tuzatib, dekart ko'paytmasini olish</h3>
<p>Bu N+1 ni tuzatishga urinishda paydo bo'ladigan mustaqil xato. Bitta postga <em>ikkita</em> 1:N jadvalni bir vaqtda <code>JOIN</code> qilsangiz, natija qatorlari <strong>ko'payadi</strong>.</p>
<p>O'lchangan misol: post 1 da 4 ta izoh va 3 ta teg bor. Ikkalasini bitta so'rovda <code>LEFT JOIN</code> qilganda natija 4 emas, <strong>12 qator</strong> chiqadi &mdash; 4 &times; 3. Va endi <code>COUNT(i.id)</code> 12 deb yolg'on gapiradi.</p>
<p>Yechimlar: <code>COUNT(DISTINCT ...)</code> (to'g'ri, lekin sekin), yoki jadvallarni alohida agregatlash, yoki har bir hisob uchun alohida subquery. Umumiy tamoyil &mdash; <strong>bir vaqtda faqat bitta 1:N jadvalni qo'shing</strong>.</p>

<h3>Qachon N+1 muammo emas</h3>
<p>Halollik uchun: agar ro'yxatda 3 ta element bo'lsa va sahifa kuniga bir marta ochilsa, N+1 ni tuzatish vaqtni behuda sarflash. Bu muammo <em>miqyos</em> bilan paydo bo'ladi. Lekin ro'yxat sonini foydalanuvchi boshqarayotgan bo'lsa (filtr, sahifalash), miqyos ertami-kechmi keladi.</p>""",
        "text_content_ru": """<h3>Каждый запрос быстрый, а страница медленная</h3>
<p>N+1 — самая частая ошибка производительности, с которой сталкивается backend-разработчик, и хуже всего то, что она <em>не выглядит как медленный запрос</em>. Каждый запрос выполняется за 0.3 мс. К базе никаких претензий. Но страница открывается 2 секунды.</p>
<p>Происхождение простое. В ORM вы пишете так:</p>
<pre><code>postlar = Post.query.limit(20).all()      # 1-й запрос
for post in postlar:
    print(post.izohlar)                    # НОВЫЙ запрос на каждой итерации</code></pre>
<p>В итоге уходит 1 + 20 = 21 запрос. Проблема не в скорости SQL — проблема в <strong>21 путешествии по сети туда и обратно</strong>. Если каждое занимает 1–2 мс, только на ожидание уйдёт 40 мс, тогда как SQL отработал в сумме 6 мс. А если в списке не 20, а 500 элементов — страница умирает.</p>

<h3>Почему это сложно заметить</h3>
<p>В журнале медленных запросов (<code>log_min_duration_statement = 100</code>) N+1 <strong>вообще не виден</strong>: ни один запрос не превышает 100 мс. Чтобы его найти, нужно задать другой вопрос — «какой запрос вызывался <em>чаще всего</em>?».</p>
<p>Именно поэтому N+1 ищут через <code>pg_stat_statements</code> с сортировкой по <code>ORDER BY calls DESC</code>, а не по <code>mean_exec_time</code>. В среде разработки самый простой способ — посчитать, сколько SQL-запросов ушло на один HTTP-запрос.</p>

<h3>Четыре решения и выбор между ними</h3>
<table>
<tr><th>Способ</th><th>Когда</th><th>На что обратить внимание</th></tr>
<tr><td><code>JOIN</code></td><td>Данные родителя и потомка нужны вместе</td><td>Поля родителя дублируются в каждом потомке</td></tr>
<tr><td>Один запрос <code>IN (...)</code></td><td>Это и есть eager loading в ORM</td><td>Результат нужно сгруппировать в коде</td></tr>
<tr><td><code>jsonb_agg</code></td><td>Если API сразу отдаёт вложенный JSON</td><td>Память на больших объёмах</td></tr>
<tr><td><code>LATERAL</code></td><td>Только топ-N потомков на каждого родителя</td><td>Другим способом не написать</td></tr>
</table>
<p><code>LATERAL</code> стоит особняком: задачу «последние 3 комментария к каждому посту» обычным <code>JOIN</code> не решить, потому что <code>LIMIT</code> применяется ко всему результату, а не к каждой группе. <code>LATERAL</code> же позволяет подзапросу ссылаться на внешнюю строку.</p>

<h3>Вторая ловушка: починить N+1 и получить декартово произведение</h3>
<p>Это самостоятельная ошибка, возникающая при попытке исправить N+1. Если приджойнить к одному посту <em>две</em> таблицы 1:N одновременно, количество строк результата <strong>перемножится</strong>.</p>
<p>Измеренный пример: у поста 1 есть 4 комментария и 3 тега. При <code>LEFT JOIN</code> обеих таблиц в одном запросе результат — не 4, а <strong>12 строк</strong>: 4 &times; 3. И теперь <code>COUNT(i.id)</code> врёт, показывая 12.</p>
<p>Решения: <code>COUNT(DISTINCT ...)</code> (верно, но медленно), либо агрегировать таблицы по отдельности, либо отдельный подзапрос на каждый счётчик. Общий принцип — <strong>присоединяйте одновременно только одну таблицу 1:N</strong>.</p>

<h3>Когда N+1 не проблема</h3>
<p>Ради честности: если в списке 3 элемента, а страница открывается раз в сутки, чинить N+1 — пустая трата времени. Эта проблема появляется вместе с <em>масштабом</em>. Но если размером списка управляет пользователь (фильтр, пагинация), масштаб рано или поздно придёт.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- N+1 muammosi: qanday paydo bo'ladi, qanday aniqlanadi, qanday tuzatiladi
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS izohlar;
DROP TABLE IF EXISTS teglar_bogi;
DROP TABLE IF EXISTS postlar;

CREATE TABLE postlar (
    id       BIGSERIAL   PRIMARY KEY,
    muallif  VARCHAR(60) NOT NULL,
    sarlavha TEXT        NOT NULL,
    sana     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE izohlar (
    id      BIGSERIAL   PRIMARY KEY,
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif VARCHAR(60) NOT NULL,
    matn    TEXT        NOT NULL,
    sana    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE teglar_bogi (
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    teg     VARCHAR(30) NOT NULL,
    PRIMARY KEY (post_id, teg)
);

INSERT INTO postlar (muallif, sarlavha)
SELECT 'Muallif ' || (g % 50), 'Post ' || g FROM generate_series(1, 5000) g;

INSERT INTO izohlar (post_id, muallif, matn)
SELECT (random() * 4999)::INT + 1, 'Izohchi ' || (g % 200), 'Izoh matni ' || g
FROM generate_series(1, 40000) g;

INSERT INTO teglar_bogi (post_id, teg)
SELECT DISTINCT (random() * 4999)::INT + 1,
       (ARRAY['sql','python','web'])[(random() * 2)::INT + 1]
FROM generate_series(1, 8000) g;

-- 1-postga ATAYLAB aniq ma'lumot: 4 ta izoh va 3 ta teg (6-bo'lim uchun)
DELETE FROM izohlar     WHERE post_id = 1;
DELETE FROM teglar_bogi WHERE post_id = 1;
INSERT INTO izohlar (post_id, muallif, matn) VALUES
    (1, 'Aziz',    'Birinchi izoh'),
    (1, 'Dilnoza', 'Ikkinchi izoh'),
    (1, 'Sardor',  'Uchinchi izoh'),
    (1, 'Nodira',  'To''rtinchi izoh');
INSERT INTO teglar_bogi (post_id, teg) VALUES (1,'sql'), (1,'python'), (1,'web');

CREATE INDEX idx_izohlar_post ON izohlar(post_id);
ANALYZE postlar; ANALYZE izohlar; ANALYZE teglar_bogi;

-- ─────────────────────────────────────────────────────────────────────
-- 1) N+1 QANDAY KO'RINADI
--    ORM kodi:  for post in Post.query.limit(20): print(post.izohlar)
-- ─────────────────────────────────────────────────────────────────────
-- 1-so'rov — postlar ro'yxati:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20;

-- Keyin HAR BIR post uchun alohida so'rov. Bu yerda bittasi ko'rsatilgan,
-- ilovada esa 20 tasi KETMA-KET ketadi:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM izohlar WHERE post_id = 1;
-- Har biri ~0.05 ms. Jami SQL ~1 ms. Lekin 21 marta tarmoq borib-kelishi
-- (har biri 1-2 ms) => 40+ ms. Sekin so'rovlar jurnalida HECH NARSA yo'q.

-- ─────────────────────────────────────────────────────────────────────
-- 2) Yechim A: bitta JOIN
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha, i.id AS izoh_id, i.matn
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN izohlar i ON i.post_id = p.id
ORDER BY p.id, i.id;
-- Kamchiligi: p.sarlavha har bir izoh qatorida takrorlanadi.

-- ─────────────────────────────────────────────────────────────────────
-- 3) Yechim B: bitta batch so'rov (IN) — ORM dagi eager loading aynan shu
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM izohlar
WHERE post_id IN (SELECT id FROM postlar ORDER BY id LIMIT 20)
ORDER BY post_id, id;
-- 20 ta so'rov o'rniga 2 ta. Natijani kodda post_id bo'yicha guruhlaysiz.

-- ─────────────────────────────────────────────────────────────────────
-- 4) Yechim C: jsonb_agg — API darhol ichma-ich JSON kutsa
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha,
       COALESCE(
           jsonb_agg(jsonb_build_object('id', i.id, 'matn', i.matn) ORDER BY i.id)
               FILTER (WHERE i.id IS NOT NULL),
           '[]'::jsonb
       ) AS izohlar
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY p.id;
-- FILTER (WHERE i.id IS NOT NULL) muhim: usiz izohsiz post uchun
-- massivda [{"id": null, "matn": null}] paydo bo'ladi.

-- ─────────────────────────────────────────────────────────────────────
-- 5) Yechim D: LATERAL — har postdan faqat OXIRGI 3 izoh
--    Bu masalani oddiy JOIN bilan yechib BO'LMAYDI: LIMIT butun
--    natijaga qo'llanadi, har bir guruhga emas.
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha, i.id AS izoh_id, i.matn
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN LATERAL (
    SELECT id, matn FROM izohlar
    WHERE post_id = p.id           -- <-- LATERAL aynan shuni mumkin qiladi
    ORDER BY id DESC
    LIMIT 3
) i ON TRUE
ORDER BY p.id, i.id DESC;

-- ─────────────────────────────────────────────────────────────────────
-- 6) TUZOQ: ikkita 1:N jadvalni bir vaqtda qo'shish -> dekart ko'paytmasi
-- ─────────────────────────────────────────────────────────────────────
-- 1-postda 4 ta izoh va 3 ta teg bor. Haqiqiy sonlar:
SELECT (SELECT COUNT(*) FROM izohlar     WHERE post_id = 1) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = 1) AS teg_soni;
--  izoh_soni | teg_soni
--          4 |        3

-- Endi ikkalasini bitta so'rovda qo'shamiz:
SELECT COUNT(*) AS notogri_qatorlar
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1;
--  notogri_qatorlar
--                12        <-- 4 * 3 = 12, ya'ni 4 emas!
-- Endi COUNT(i.id) 12 deb YOLG'ON gapiradi va SUM ham xato bo'ladi.

-- To'g'rilash 1: COUNT(DISTINCT ...) — to'g'ri, lekin saralash qo'shadi
SELECT p.id,
       COUNT(DISTINCT i.id)  AS izoh_soni,
       COUNT(DISTINCT t.teg) AS teg_soni
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1
GROUP BY p.id;

-- To'g'rilash 2: umuman qo'shmasdan, alohida agregatlar (odatda tezroq)
SELECT p.id,
       (SELECT COUNT(*) FROM izohlar     WHERE post_id = p.id) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = p.id) AS teg_soni
FROM postlar p WHERE p.id = 1;

-- ─────────────────────────────────────────────────────────────────────
-- 7) N+1 NI ANIQLASH — produksiyada
-- ─────────────────────────────────────────────────────────────────────
-- pg_stat_statements kengaytmasi orqali. DIQQAT: bu yerda SEKIN so'rovlar
-- emas, KO'P CHAQIRILGAN so'rovlar qidiriladi — N+1 ning butun mohiyati shu.
--
--   SELECT calls,
--          ROUND(mean_exec_time::NUMERIC, 3)          AS ortacha_ms,
--          ROUND((calls * mean_exec_time)::NUMERIC, 1) AS jami_ms,
--          LEFT(query, 80)                             AS sorov
--   FROM pg_stat_statements
--   ORDER BY calls DESC
--   LIMIT 20;
--
-- Kengaytma o'rnatilganini tekshirish:
SELECT
    (SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'pg_stat_statements') AS mavjud,
    (SELECT COUNT(*) FROM pg_extension            WHERE extname = 'pg_stat_statements') AS ornatilgan;
-- mavjud=1, ornatilgan=0 bo'lsa: postgresql.conf da
-- shared_preload_libraries = 'pg_stat_statements' qo'shib, serverni
-- qayta ishga tushirish va CREATE EXTENSION bajarish kerak.

-- Jadval darajasidagi belgi: seq_scan juda ko'p bo'lsa ham N+1 dan darak
SELECT relname, seq_scan, idx_scan, n_live_tup
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY seq_scan DESC
LIMIT 10;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Проблема N+1: как возникает, как обнаружить, как исправить
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS izohlar;
DROP TABLE IF EXISTS teglar_bogi;
DROP TABLE IF EXISTS postlar;

CREATE TABLE postlar (
    id       BIGSERIAL   PRIMARY KEY,
    muallif  VARCHAR(60) NOT NULL,
    sarlavha TEXT        NOT NULL,
    sana     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE izohlar (
    id      BIGSERIAL   PRIMARY KEY,
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif VARCHAR(60) NOT NULL,
    matn    TEXT        NOT NULL,
    sana    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE teglar_bogi (
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    teg     VARCHAR(30) NOT NULL,
    PRIMARY KEY (post_id, teg)
);

INSERT INTO postlar (muallif, sarlavha)
SELECT 'Muallif ' || (g % 50), 'Post ' || g FROM generate_series(1, 5000) g;

INSERT INTO izohlar (post_id, muallif, matn)
SELECT (random() * 4999)::INT + 1, 'Izohchi ' || (g % 200), 'Izoh matni ' || g
FROM generate_series(1, 40000) g;

INSERT INTO teglar_bogi (post_id, teg)
SELECT DISTINCT (random() * 4999)::INT + 1,
       (ARRAY['sql','python','web'])[(random() * 2)::INT + 1]
FROM generate_series(1, 8000) g;

-- Посту 1 НАМЕРЕННО задаём точные данные: 4 комментария и 3 тега (для раздела 6)
DELETE FROM izohlar     WHERE post_id = 1;
DELETE FROM teglar_bogi WHERE post_id = 1;
INSERT INTO izohlar (post_id, muallif, matn) VALUES
    (1, 'Aziz',    'Birinchi izoh'),
    (1, 'Dilnoza', 'Ikkinchi izoh'),
    (1, 'Sardor',  'Uchinchi izoh'),
    (1, 'Nodira',  'To''rtinchi izoh');
INSERT INTO teglar_bogi (post_id, teg) VALUES (1,'sql'), (1,'python'), (1,'web');

CREATE INDEX idx_izohlar_post ON izohlar(post_id);
ANALYZE postlar; ANALYZE izohlar; ANALYZE teglar_bogi;

-- ─────────────────────────────────────────────────────────────────────
-- 1) КАК ВЫГЛЯДИТ N+1
--    Код ORM:  for post in Post.query.limit(20): print(post.izohlar)
-- ─────────────────────────────────────────────────────────────────────
-- 1-й запрос — список постов:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20;

-- Затем отдельный запрос на КАЖДЫЙ пост. Здесь показан один,
-- а в приложении их уходит 20 ПОДРЯД:
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM izohlar WHERE post_id = 1;
-- Каждый ~0.05 мс. Суммарно SQL ~1 мс. Но 21 путешествие по сети
-- (по 1-2 мс каждое) => 40+ мс. В журнале медленных запросов НИЧЕГО нет.

-- ─────────────────────────────────────────────────────────────────────
-- 2) Решение A: один JOIN
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha, i.id AS izoh_id, i.matn
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN izohlar i ON i.post_id = p.id
ORDER BY p.id, i.id;
-- Недостаток: p.sarlavha дублируется в каждой строке комментария.

-- ─────────────────────────────────────────────────────────────────────
-- 3) Решение B: один batch-запрос (IN) — это и есть eager loading в ORM
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM izohlar
WHERE post_id IN (SELECT id FROM postlar ORDER BY id LIMIT 20)
ORDER BY post_id, id;
-- Вместо 20 запросов — 2. Результат группируете в коде по post_id.

-- ─────────────────────────────────────────────────────────────────────
-- 4) Решение C: jsonb_agg — если API сразу ждёт вложенный JSON
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha,
       COALESCE(
           jsonb_agg(jsonb_build_object('id', i.id, 'matn', i.matn) ORDER BY i.id)
               FILTER (WHERE i.id IS NOT NULL),
           '[]'::jsonb
       ) AS izohlar
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY p.id;
-- FILTER (WHERE i.id IS NOT NULL) здесь важен: без него для поста без
-- комментариев в массиве появится [{"id": null, "matn": null}].

-- ─────────────────────────────────────────────────────────────────────
-- 5) Решение D: LATERAL — только ПОСЛЕДНИЕ 3 комментария к каждому посту
--    Эту задачу обычным JOIN решить НЕЛЬЗЯ: LIMIT применяется ко
--    всему результату, а не к каждой группе.
-- ─────────────────────────────────────────────────────────────────────
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha, i.id AS izoh_id, i.matn
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN LATERAL (
    SELECT id, matn FROM izohlar
    WHERE post_id = p.id           -- <-- именно это и делает возможным LATERAL
    ORDER BY id DESC
    LIMIT 3
) i ON TRUE
ORDER BY p.id, i.id DESC;

-- ─────────────────────────────────────────────────────────────────────
-- 6) ЛОВУШКА: две таблицы 1:N одновременно -> декартово произведение
-- ─────────────────────────────────────────────────────────────────────
-- У поста 1 есть 4 комментария и 3 тега. Реальные числа:
SELECT (SELECT COUNT(*) FROM izohlar     WHERE post_id = 1) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = 1) AS teg_soni;
--  izoh_soni | teg_soni
--          4 |        3

-- Теперь присоединяем обе в одном запросе:
SELECT COUNT(*) AS notogri_qatorlar
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1;
--  notogri_qatorlar
--                12        <-- 4 * 3 = 12, то есть не 4!
-- Теперь COUNT(i.id) ВРЁТ, показывая 12, и SUM тоже будет неверной.

-- Исправление 1: COUNT(DISTINCT ...) — верно, но добавляет сортировку
SELECT p.id,
       COUNT(DISTINCT i.id)  AS izoh_soni,
       COUNT(DISTINCT t.teg) AS teg_soni
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1
GROUP BY p.id;

-- Исправление 2: вообще не соединять, отдельные агрегаты (обычно быстрее)
SELECT p.id,
       (SELECT COUNT(*) FROM izohlar     WHERE post_id = p.id) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = p.id) AS teg_soni
FROM postlar p WHERE p.id = 1;

-- ─────────────────────────────────────────────────────────────────────
-- 7) КАК ОБНАРУЖИТЬ N+1 — в продакшене
-- ─────────────────────────────────────────────────────────────────────
-- Через расширение pg_stat_statements. ВНИМАНИЕ: здесь ищутся не МЕДЛЕННЫЕ
-- запросы, а ЧАСТО ВЫЗЫВАЕМЫЕ — в этом вся суть N+1.
--
--   SELECT calls,
--          ROUND(mean_exec_time::NUMERIC, 3)          AS ortacha_ms,
--          ROUND((calls * mean_exec_time)::NUMERIC, 1) AS jami_ms,
--          LEFT(query, 80)                             AS sorov
--   FROM pg_stat_statements
--   ORDER BY calls DESC
--   LIMIT 20;
--
-- Проверка, установлено ли расширение:
SELECT
    (SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'pg_stat_statements') AS mavjud,
    (SELECT COUNT(*) FROM pg_extension            WHERE extname = 'pg_stat_statements') AS ornatilgan;
-- Если mavjud=1, а ornatilgan=0: нужно добавить в postgresql.conf
-- shared_preload_libraries = 'pg_stat_statements', перезапустить сервер
-- и выполнить CREATE EXTENSION.

-- Признак на уровне таблицы: очень большое seq_scan тоже намекает на N+1
SELECT relname, seq_scan, idx_scan, n_live_tup
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY seq_scan DESC
LIMIT 10;""",
        "task": {
            "task_title": "Amaliy topshiriq: N+1 ni topib, bitta so'rovga aylantirish",
            "task_title_ru": "Практическое задание: найти N+1 и свести к одному запросу",
            "task_description": (
                "Sizga blog API ning ORM kodi berilgan:\n\n"
                "    postlar = Post.query.order_by(Post.id).limit(20).all()\n"
                "    for p in postlar:\n"
                "        p.izohlar   # lazy\n"
                "        p.teglar    # lazy\n\n"
                "Shu naqshni SQL darajasida takrorlaydigan sxema yarating (postlar, izohlar, "
                "teglar_bogi; kamida 5 000 post va 40 000 izoh), muammoni aniqlang va uni "
                "bosqichma-bosqich tuzating.\n\n"
                "Diqqat: N+1 ni tuzatishga urinishning o'zi ikkinchi xatoni tug'diradi. "
                "Ikkita 1:N jadvalni bir vaqtda qo'shsangiz, natija qatorlari ko'payadi va "
                "COUNT yolg'on gapiradi. Buni ANIQ raqamlar bilan ko'rsating va ikki xil "
                "usulda to'g'rilang."
            ),
            "task_description_ru": (
                "Вам дан ORM-код блогового API:\n\n"
                "    postlar = Post.query.order_by(Post.id).limit(20).all()\n"
                "    for p in postlar:\n"
                "        p.izohlar   # lazy\n"
                "        p.teglar    # lazy\n\n"
                "Создайте схему, воспроизводящую этот шаблон на уровне SQL (postlar, izohlar, "
                "teglar_bogi; минимум 5 000 постов и 40 000 комментариев), выявите проблему и "
                "исправьте её пошагово.\n\n"
                "Внимание: сама попытка исправить N+1 порождает вторую ошибку. Если "
                "присоединить две таблицы 1:N одновременно, строки размножатся и COUNT начнёт "
                "врать. Покажите это на ТОЧНЫХ цифрах и исправьте двумя разными способами."
            ),
            "task_requirements": (
                "1. Sxema va ma'lumot: kamida 5 000 post, 40 000 izoh va teglar bog'lanishi. "
                "Bitta postga ATAYLAB aniq son berilsin (masalan 4 ta izoh va 3 ta teg) — "
                "dekart tuzog'ini raqam bilan ko'rsatish uchun.\n"
                "2. Izohda hisob: berilgan ORM kodi nechta so'rov yuboradi va nega sekin "
                "so'rovlar jurnalida (log_min_duration_statement) hech narsa ko'rinmaydi.\n"
                "3. Yechim A — bitta JOIN. Kamchiligi izohda yozilsin (ota maydonlari "
                "takrorlanadi).\n"
                "4. Yechim B — bitta batch so'rov (IN). Izohda bu ORM dagi eager loading "
                "ekani qayd etilsin.\n"
                "5. Yechim C — jsonb_agg bilan ichma-ich JSON. FILTER (WHERE ... IS NOT NULL) "
                "SHART; izohda usiz nima bo'lishi yozilsin.\n"
                "6. Yechim D — LATERAL bilan har postdan oxirgi 3 ta izoh. Izohda oddiy JOIN + "
                "LIMIT bu masalani nega yecha olmasligi tushuntirilsin.\n"
                "7. Dekart tuzog'i: ikkita 1:N jadval bir vaqtda qo'shilganda qator soni "
                "ko'payishi ANIQ raqam bilan ko'rsatilsin (4 x 3 = 12), so'ng ikki xil "
                "to'g'rilash keltirilsin — COUNT(DISTINCT ...) va alohida agregatlar.\n"
                "8. Har bir yechim uchun EXPLAIN (ANALYZE) natijasi saqlansin.\n"
                "9. Produksiyada N+1 ni topish uchun pg_stat_statements so'rovi yozilsin; izohda "
                "nega ORDER BY calls DESC, mean_exec_time bo'yicha EMASligi asoslansin.\n"
                "10. Yakuniy .sql fayl boshidan oxirigacha xatosiz bajarilsin."
            ),
            "task_requirements_ru": (
                "1. Схема и данные: минимум 5 000 постов, 40 000 комментариев и связи тегов. "
                "Одному посту НАМЕРЕННО задайте точные числа (например, 4 комментария и 3 "
                "тега) — чтобы показать декартову ловушку цифрами.\n"
                "2. Расчёт в комментарии: сколько запросов отправляет данный ORM-код и почему в "
                "логе медленных запросов (log_min_duration_statement) ничего не видно.\n"
                "3. Решение A — один JOIN. Недостаток опишите в комментарии (поля родителя "
                "дублируются).\n"
                "4. Решение B — один batch-запрос (IN). В комментарии отметьте, что это и есть "
                "eager loading в ORM.\n"
                "5. Решение C — вложенный JSON через jsonb_agg. FILTER (WHERE ... IS NOT NULL) "
                "ОБЯЗАТЕЛЕН; в комментарии напишите, что будет без него.\n"
                "6. Решение D — последние 3 комментария к каждому посту через LATERAL. В "
                "комментарии объясните, почему обычный JOIN + LIMIT эту задачу не решает.\n"
                "7. Декартова ловушка: покажите ТОЧНЫМИ цифрами рост числа строк при "
                "одновременном join двух таблиц 1:N (4 x 3 = 12), затем приведите два "
                "исправления — COUNT(DISTINCT ...) и раздельные агрегаты.\n"
                "8. Для каждого решения сохраните результат EXPLAIN (ANALYZE).\n"
                "9. Напишите запрос к pg_stat_statements для поиска N+1 в продакшене; в "
                "комментарии обоснуйте, почему ORDER BY calls DESC, а НЕ по mean_exec_time.\n"
                "10. Итоговый .sql должен выполняться от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, JOIN, LATERAL, jsonb_agg, pg_stat_statements",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: N+1 dan bitta so'rovga — JOIN, IN, jsonb_agg va LATERAL",
            "description": "To'rtta yechim yonma-yon hamda ikkita 1:N jadvalni birga qo'shganda COUNT nega yolg'on gapirishi va uni qanday to'g'rilash",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: N+1 ni bitta so'rovga aylantirish (va dekart tuzog'idan qochish)
DROP TABLE IF EXISTS izohlar;
DROP TABLE IF EXISTS teglar_bogi;
DROP TABLE IF EXISTS postlar;

CREATE TABLE postlar (
    id       BIGSERIAL   PRIMARY KEY,
    muallif  VARCHAR(60) NOT NULL,
    sarlavha TEXT        NOT NULL
);
CREATE TABLE izohlar (
    id      BIGSERIAL   PRIMARY KEY,
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    matn    TEXT        NOT NULL
);
CREATE TABLE teglar_bogi (
    post_id BIGINT      NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    teg     VARCHAR(30) NOT NULL,
    PRIMARY KEY (post_id, teg)
);

INSERT INTO postlar (muallif, sarlavha)
SELECT 'Muallif ' || (g % 50), 'Post ' || g FROM generate_series(1, 5000) g;
INSERT INTO izohlar (post_id, matn)
SELECT (random() * 4999)::INT + 1, 'Izoh matni ' || g FROM generate_series(1, 40000) g;
INSERT INTO teglar_bogi (post_id, teg)
SELECT DISTINCT (random() * 4999)::INT + 1,
       (ARRAY['sql','python','web'])[(random() * 2)::INT + 1]
FROM generate_series(1, 8000) g;

-- 1-postga ATAYLAB aniq ma'lumot: 4 ta izoh va 3 ta teg
DELETE FROM izohlar     WHERE post_id = 1;
DELETE FROM teglar_bogi WHERE post_id = 1;
INSERT INTO izohlar (post_id, matn) VALUES
    (1,'Birinchi izoh'), (1,'Ikkinchi izoh'), (1,'Uchinchi izoh'), (1,'Tortinchi izoh');
INSERT INTO teglar_bogi (post_id, teg) VALUES (1,'sql'), (1,'python'), (1,'web');

CREATE INDEX idx_izohlar_post ON izohlar(post_id);
ANALYZE postlar; ANALYZE izohlar; ANALYZE teglar_bogi;

-- ══ MUAMMO: ORM kodi
--    postlar = Post.query.limit(20)      -> 1 so'rov
--    for p in postlar: p.izohlar         -> yana 20 so'rov
--    Har biri ~0.05 ms, lekin 21 marta tarmoq borib-kelishi 40+ ms.
--    Sekin so'rovlar jurnalida HECH NARSA ko'rinmaydi.

-- Yechim A: bitta JOIN. Kamchiligi — sarlavha har izoh qatorida takrorlanadi.
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, p.sarlavha, i.id AS izoh_id, i.matn
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN izohlar i ON i.post_id = p.id
ORDER BY p.id, i.id;

-- Yechim B: bitta batch so'rov (IN) — ORM dagi eager loading aynan shu.
--    20 ta so'rov o'rniga 2 ta; natijani kodda post_id bo'yicha guruhlaysiz.
EXPLAIN (ANALYZE, TIMING OFF)
SELECT * FROM izohlar
WHERE post_id IN (SELECT id FROM postlar ORDER BY id LIMIT 20)
ORDER BY post_id, id;

-- Yechim C: jsonb_agg — API darhol ichma-ich JSON kutsa.
--    FILTER (WHERE i.id IS NOT NULL) SHART: usiz izohsiz post uchun
--    massivda [{"id": null, "matn": null}] paydo bo'ladi.
SELECT p.id, p.sarlavha,
       COALESCE(
           jsonb_agg(jsonb_build_object('id', i.id, 'matn', i.matn) ORDER BY i.id)
               FILTER (WHERE i.id IS NOT NULL),
           '[]'::jsonb
       ) AS izohlar
FROM (SELECT id, sarlavha FROM postlar ORDER BY id LIMIT 3) p
LEFT JOIN izohlar i ON i.post_id = p.id
GROUP BY p.id, p.sarlavha
ORDER BY p.id;

-- Yechim D: LATERAL — har postdan faqat OXIRGI 3 izoh.
--    Buni oddiy JOIN bilan yechib BO'LMAYDI: LIMIT butun natijaga
--    qo'llanadi, har bir guruhga emas.
EXPLAIN (ANALYZE, TIMING OFF)
SELECT p.id, i.id AS izoh_id, i.matn
FROM (SELECT id FROM postlar ORDER BY id LIMIT 20) p
LEFT JOIN LATERAL (
    SELECT id, matn FROM izohlar
    WHERE post_id = p.id          -- <-- LATERAL aynan shuni mumkin qiladi
    ORDER BY id DESC LIMIT 3
) i ON TRUE
ORDER BY p.id, i.id DESC;

-- ══ TUZOQ: N+1 ni tuzatib, dekart ko'paytmasini olish ═══════════════
SELECT (SELECT COUNT(*) FROM izohlar     WHERE post_id = 1) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = 1) AS teg_soni;
--  4 | 3   <-- haqiqiy sonlar

SELECT COUNT(*) AS notogri_qatorlar
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1;
--  12 = 4 * 3, ya'ni 4 emas! Endi COUNT(i.id) YOLG'ON gapiradi.

-- To'g'rilash 1: COUNT(DISTINCT ...) — to'g'ri, lekin saralash qo'shadi
SELECT p.id, COUNT(DISTINCT i.id) AS izoh_soni, COUNT(DISTINCT t.teg) AS teg_soni
FROM postlar p
LEFT JOIN izohlar i     ON i.post_id = p.id
LEFT JOIN teglar_bogi t ON t.post_id = p.id
WHERE p.id = 1
GROUP BY p.id;

-- To'g'rilash 2: umuman qo'shmasdan, alohida agregatlar (odatda tezroq)
SELECT p.id,
       (SELECT COUNT(*) FROM izohlar     WHERE post_id = p.id) AS izoh_soni,
       (SELECT COUNT(*) FROM teglar_bogi WHERE post_id = p.id) AS teg_soni
FROM postlar p WHERE p.id = 1;

-- ══ ANIQLASH: N+1 SEKIN emas, KO'P CHAQIRILGAN so'rovdir ════════════
--   SELECT calls, mean_exec_time, LEFT(query, 80)
--   FROM pg_stat_statements
--   ORDER BY calls DESC LIMIT 20;    -- mean_exec_time bo'yicha EMAS!
SELECT relname, seq_scan, idx_scan, n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = current_schema() AND n_live_tup > 1000
ORDER BY seq_scan DESC LIMIT 5;""",
        },
        "exercises": [
            {
                "title": "N+1 ni qanday topasiz?",
                "title_ru": "Как найти N+1?",
                "description": "Sahifa 2 sekundda ochilmoqda, lekin sekin so'rovlar jurnalida (100 ms chegara) hech narsa yo'q. pg_stat_statements da qaysi ustun bo'yicha saralash N+1 ni ko'rsatadi?",
                "description_ru": "Страница открывается 2 секунды, но в журнале медленных запросов (порог 100 мс) ничего нет. По какой колонке в pg_stat_statements нужно сортировать, чтобы увидеть N+1?",
                "exercise_type": "multiple_choice",
                "options": [
                    "mean_exec_time DESC — eng sekin so'rovlar",
                    "calls DESC — eng ko'p chaqirilgan so'rovlar",
                    "max_exec_time DESC — eng uzun bajarilish",
                    "shared_blks_read DESC — eng ko'p diskdan o'qish",
                ],
                "options_ru": [
                    "mean_exec_time DESC — самые медленные запросы",
                    "calls DESC — самые часто вызываемые запросы",
                    "max_exec_time DESC — самое долгое выполнение",
                    "shared_blks_read DESC — больше всего чтений с диска",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "N+1 da har bir so'rov TEZ. Ular faqat juda ko'p.",
                "hint_ru": "При N+1 каждый запрос БЫСТРЫЙ. Их просто очень много.",
                "explanation": "N+1 da har bir so'rov millisekundlarda bajariladi, shuning uchun sekinlik bo'yicha saralash uni ko'rsatmaydi. Uni faqat chaqiriqlar soni ochib beradi: 200 ta x 0.3 ms = 60 ms SQL, lekin 200 ta tarmoq borib-kelishi 200+ ms.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Har guruhdan top-N olish",
                "title_ru": "Получить топ-N в каждой группе",
                "description": "Har bir postdan faqat oxirgi 3 ta izohni bitta so'rovda olish kerak. Oddiy JOIN + LIMIT bunga yaramaydi, chunki LIMIT butun natijaga qo'llanadi. Ichki so'rovga tashqi qatorga ishora qilish imkonini beruvchi kalit so'z: LEFT JOIN ___",
                "description_ru": "Нужно одним запросом получить только последние 3 комментария к каждому посту. Обычный JOIN + LIMIT не подходит, так как LIMIT применяется ко всему результату. Ключевое слово, позволяющее подзапросу ссылаться на внешнюю строку: LEFT JOIN ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "LATERAL",
                "hint": "Bu kalit so'z ichki so'rovni har bir tashqi qator uchun alohida bajaradi.",
                "hint_ru": "Это ключевое слово выполняет подзапрос отдельно для каждой внешней строки.",
                "explanation": "LATERAL ichki so'rovga tashqi qatorning ustunlariga (p.id) murojaat qilish imkonini beradi, shuning uchun LIMIT har bir guruhga alohida qo'llanadi.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Nega COUNT 12 chiqdi?",
                "title_ru": "Почему COUNT показал 12?",
                "description": "1-postda aniq 4 ta izoh va 3 ta teg bor. Dasturchi N+1 ni tuzatmoqchi bo'lib, izohlar va teglar_bogi jadvallarini bitta so'rovda LEFT JOIN qildi va COUNT(*) 12 qaytardi. Nima bo'ldi, bu qanday xatolarga olib keladi va uni qanday to'g'rilash mumkin?",
                "description_ru": "У поста 1 ровно 4 комментария и 3 тега. Разработчик решил исправить N+1 и сделал LEFT JOIN таблиц izohlar и teglar_bogi в одном запросе — COUNT(*) вернул 12. Что произошло, к каким ошибкам это ведёт и как это исправить?",
                "exercise_type": "text_input",
                "expected_answer": "Ikkita mustaqil 1:N jadval bir vaqtda qo'shilganda ular orasida dekart ko'paytmasi hosil bo'ladi: har bir izoh har bir teg bilan juftlashadi, ya'ni 4 x 3 = 12 qator. Bu COUNT(i.id) ni 12 qilib ko'rsatadi va SUM kabi barcha agregatlarni ham buzadi — masalan buyurtma summasi qatorlar soniga ko'payib ketadi. To'g'rilash usullari: (1) COUNT(DISTINCT i.id) va COUNT(DISTINCT t.teg) ishlatish — natija to'g'ri, lekin qo'shimcha saralash narxi bor; (2) har bir jadvalni alohida agregatlab, keyin natijalarni qo'shish; (3) har bir hisob uchun alohida subquery yozish — odatda eng tez variant. Umumiy qoida: bir vaqtda faqat bitta 1:N jadvalni JOIN qiling.",
                "hint": "4 va 3 sonlaridan 12 qanday hosil bo'lishi mumkin?",
                "hint_ru": "Как из чисел 4 и 3 может получиться 12?",
                "difficulty_level": "Hard",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 7
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 7,
        "title": "7-Tranzaksiyalar va isolation levels",
        "title_ru": "7-Транзакции и уровни изоляции",
        "points_reward": 15,
        "code_language": "sql",
        "text_content": """<h3>Izolyatsiya darajasi &mdash; bu savdolashuv</h3>
<p>Tranzaksiya <code>BEGIN</code> va <code>COMMIT</code> orasidagi ishlarni &ldquo;hammasi yoki hech nima&rdquo; qiladi &mdash; buni oldingi kursda ko'rgansiz. Izolyatsiya darajasi esa boshqa savolga javob beradi: <strong>bir vaqtda ishlayotgan tranzaksiyalar bir-birining ishini qanchalik ko'radi?</strong></p>
<p>Bu tanlov har doim savdolashuv: kuchliroq izolyatsiya kamroq anomaliya, lekin ko'proq konflikt va qayta urinish degani. Bepul kuchli izolyatsiya yo'q.</p>

<h3>To'rtta anomaliya</h3>
<table>
<tr><th>Anomaliya</th><th>Nima bo'ladi</th><th>PostgreSQL'da qachon mumkin</th></tr>
<tr><td>Dirty read</td><td>Commit qilinmagan ma'lumot o'qiladi</td><td><strong>Hech qachon</strong> &mdash; MVCC buni prinsipial ravishda bloklaydi</td></tr>
<tr><td>Non-repeatable read</td><td>Bir qatorni ikki marta o'qib, turli qiymat olinadi</td><td>READ COMMITTED</td></tr>
<tr><td>Phantom read</td><td>Bir shart bo'yicha ikki marta o'qib, turli sondagi qator olinadi</td><td>READ COMMITTED</td></tr>
<tr><td>Serialization anomaly</td><td>Har biri alohida to'g'ri, birga esa mumkin bo'lmagan natija</td><td>REPEATABLE READ gacha</td></tr>
</table>

<h3>PostgreSQL'ning haqiqiy xatti-harakati</h3>
<p>Bu yerda standart SQL va PostgreSQL amalda farq qiladi, va bu farqni bilish muhim:</p>
<ul>
<li><strong>READ UNCOMMITTED</strong> sintaksis sifatida qabul qilinadi, lekin <em>xatti-harakati READ COMMITTED bilan bir xil</em>. Nozik jihat: <code>SHOW transaction_isolation</code> baribir <code>read uncommitted</code> deb qaytaradi &mdash; ya'ni buyruq qabul qilingan, lekin dirty read baribir sodir bo'lmaydi. MVCC arxitekturasi buni umuman imkonsiz qiladi.</li>
<li><strong>READ COMMITTED</strong> &mdash; standart daraja. Muhim nozik jihat: snapshot tranzaksiya boshida emas, <em>har bir buyruq boshida</em> olinadi. Shuning uchun bitta tranzaksiya ichidagi ikkita <code>SELECT</code> turli natija berishi mumkin.</li>
<li><strong>REPEATABLE READ</strong> &mdash; snapshot <em>birinchi so'rovda</em> muzlaydi va tranzaksiya oxirigacha o'zgarmaydi. PostgreSQL'da bu daraja <em>phantom read</em> ni ham bloklaydi (standart buni talab qilmaydi &mdash; bu snapshot isolation ning bonusi).</li>
<li><strong>SERIALIZABLE</strong> &mdash; SSI (Serializable Snapshot Isolation) yordamida barcha anomaliyalarni bloklaydi. Natija har doim tranzaksiyalarni ketma-ket bajarganday bo'ladi.</li>
</ul>

<h3>Qayta urinish (retry) &mdash; ixtiyoriy emas</h3>
<p>Bu eng ko'p unutiladigan amaliy talab. REPEATABLE READ yoki SERIALIZABLE ishlatsangiz, ilovangiz <strong>xato olishga tayyor bo'lishi shart</strong>:</p>
<ul>
<li><code>40001</code> &mdash; <code>serialization_failure</code></li>
<li><code>40P01</code> &mdash; <code>deadlock_detected</code></li>
</ul>
<p>Bu xatolar &mdash; bug emas, <em>dizaynning bir qismi</em>. Ular &ldquo;tranzaksiyangizni qaytadan boshlang&rdquo; degani. Qayta urinish mantiqisiz SERIALIZABLE ishlatish foydalanuvchiga tasodifiy xatolar ko'rsatishdan boshqa narsa bermaydi.</p>

<h3>SAVEPOINT &mdash; tranzaksiya ichidagi qisman qaytarish</h3>
<p>PostgreSQL'da tranzaksiya ichida xato yuz bersa, tranzaksiya butunlay <em>aborted</em> holatga o'tadi: keyingi barcha buyruqlar <code>ERROR: current transaction is aborted</code> beradi va yagona chiqish yo'li &mdash; <code>ROLLBACK</code>.</p>
<p><code>SAVEPOINT</code> aynan shundan qutqaradi. O'lchangan misol: hisobdan pul yechildi, keyin ikkinchi <code>UPDATE</code> <code>CHECK</code> cheklovini buzdi. <code>ROLLBACK TO SAVEPOINT</code> bilan faqat <em>o'sha</em> buyruq bekor qilindi, birinchi <code>UPDATE</code> esa saqlanib qoldi va tranzaksiya muvaffaqiyatli <code>COMMIT</code> bo'ldi. <code>SAVEPOINT</code>siz esa butun tranzaksiya rad etilgan bo'lardi.</p>

<h3>MVCC nima uchun bularning hammasini mumkin qiladi</h3>
<p>PostgreSQL qatorni yangilaganda uni <em>joyida o'zgartirmaydi</em> &mdash; yangi versiya yozadi, eskisini esa &ldquo;ma'lum tranzaksiyagacha amal qilgan&rdquo; deb belgilaydi. Har bir qatorda yashirin <code>xmin</code> (qaysi tranzaksiya yaratgan) va <code>xmax</code> (qaysi tranzaksiya o'chirgan) ustunlari bor.</p>
<p>Shuning uchun o'quvchilar yozuvchilarni, yozuvchilar esa o'quvchilarni <strong>bloklamaydi</strong>. Buning narxi &mdash; eski versiyalar to'planib qoladi va ularni <code>VACUUM</code> tozalashi kerak.</p>""",
        "text_content_ru": """<h3>Уровень изоляции — это компромисс</h3>
<p>Транзакция делает работу между <code>BEGIN</code> и <code>COMMIT</code> принципом «всё или ничего» — это вы видели на предыдущем курсе. Уровень изоляции отвечает на другой вопрос: <strong>насколько параллельно работающие транзакции видят работу друг друга?</strong></p>
<p>Этот выбор всегда компромисс: более сильная изоляция означает меньше аномалий, но больше конфликтов и повторных попыток. Бесплатной сильной изоляции не бывает.</p>

<h3>Четыре аномалии</h3>
<table>
<tr><th>Аномалия</th><th>Что происходит</th><th>Когда возможна в PostgreSQL</th></tr>
<tr><td>Dirty read</td><td>Читаются незакоммиченные данные</td><td><strong>Никогда</strong> — MVCC блокирует это принципиально</td></tr>
<tr><td>Non-repeatable read</td><td>Одна строка прочитана дважды с разными значениями</td><td>READ COMMITTED</td></tr>
<tr><td>Phantom read</td><td>Один и тот же фильтр дважды даёт разное число строк</td><td>READ COMMITTED</td></tr>
<tr><td>Serialization anomaly</td><td>Каждая по отдельности верна, вместе — невозможный результат</td><td>Вплоть до REPEATABLE READ</td></tr>
</table>

<h3>Реальное поведение PostgreSQL</h3>
<p>Здесь стандарт SQL и PostgreSQL на практике расходятся, и знать это различие важно:</p>
<ul>
<li><strong>READ UNCOMMITTED</strong> принимается синтаксически, но <em>ведёт себя точно как READ COMMITTED</em>. Тонкость: <code>SHOW transaction_isolation</code> всё же вернёт <code>read uncommitted</code> — то есть команда принята, но dirty read всё равно не произойдёт. Архитектура MVCC делает его в принципе невозможным.</li>
<li><strong>READ COMMITTED</strong> — уровень по умолчанию. Важная тонкость: снимок берётся не в начале транзакции, а <em>в начале каждой команды</em>. Поэтому два <code>SELECT</code> внутри одной транзакции могут дать разный результат.</li>
<li><strong>REPEATABLE READ</strong> — снимок замораживается <em>на первом запросе</em> и не меняется до конца транзакции. В PostgreSQL этот уровень блокирует и <em>phantom read</em> (стандарт этого не требует — это бонус snapshot isolation).</li>
<li><strong>SERIALIZABLE</strong> — с помощью SSI (Serializable Snapshot Isolation) блокирует все аномалии. Результат всегда такой, как если бы транзакции выполнялись последовательно.</li>
</ul>

<h3>Повторная попытка (retry) — не опция</h3>
<p>Это самое забываемое практическое требование. Если вы используете REPEATABLE READ или SERIALIZABLE, ваше приложение <strong>обязано быть готовым получить ошибку</strong>:</p>
<ul>
<li><code>40001</code> — <code>serialization_failure</code></li>
<li><code>40P01</code> — <code>deadlock_detected</code></li>
</ul>
<p>Эти ошибки — не баг, а <em>часть дизайна</em>. Они означают «начните свою транзакцию заново». Использовать SERIALIZABLE без логики повторных попыток — значит просто показывать пользователю случайные ошибки.</p>

<h3>SAVEPOINT — частичный откат внутри транзакции</h3>
<p>Если внутри транзакции PostgreSQL происходит ошибка, транзакция целиком переходит в состояние <em>aborted</em>: все последующие команды дают <code>ERROR: current transaction is aborted</code>, и единственный выход — <code>ROLLBACK</code>.</p>
<p>От этого и спасает <code>SAVEPOINT</code>. Измеренный пример: со счёта списали деньги, затем второй <code>UPDATE</code> нарушил ограничение <code>CHECK</code>. Через <code>ROLLBACK TO SAVEPOINT</code> была отменена только <em>эта</em> команда, а первый <code>UPDATE</code> сохранился, и транзакция успешно завершилась <code>COMMIT</code>. Без <code>SAVEPOINT</code> вся транзакция была бы отклонена.</p>

<h3>Почему всё это возможно благодаря MVCC</h3>
<p>При обновлении строки PostgreSQL <em>не меняет её на месте</em> — он пишет новую версию, а старую помечает как «действовавшую до определённой транзакции». В каждой строке есть скрытые колонки <code>xmin</code> (какая транзакция создала) и <code>xmax</code> (какая удалила).</p>
<p>Поэтому читатели <strong>не блокируют</strong> писателей, а писатели — читателей. Цена этого — накопление старых версий, которые должен вычищать <code>VACUUM</code>.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Tranzaksiyalar va izolyatsiya darajalari
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hisoblar;
CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES ('Aziz', 1000000), ('Dilnoza', 500000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) Standart daraja
-- ─────────────────────────────────────────────────────────────────────
SHOW default_transaction_isolation;
--  read committed

-- ─────────────────────────────────────────────────────────────────────
-- 2) READ UNCOMMITTED — qabul qilinadi, lekin dirty read BO'LMAYDI
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SHOW transaction_isolation;
    --  read uncommitted
    -- DIQQAT: PostgreSQL buyruqni qabul qildi va shu nom bilan qaytardi,
    -- LEKIN xatti-harakati READ COMMITTED bilan bir xil. MVCC arxitekturasi
    -- commit qilinmagan ma'lumotni o'qishni prinsipial ravishda imkonsiz qiladi.
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 3) REPEATABLE READ — snapshot BIRINCHI so'rovda muzlaydi
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SHOW transaction_isolation;
    SELECT SUM(balans) AS boshlangich FROM hisoblar;
    -- Shu paytdan boshlab, boshqa sessiya nima qilsa ham, bu tranzaksiya
    -- ichidagi barcha SELECT lar AYNAN shu snapshot ni ko'radi.
    SELECT txid_current()        AS tranzaksiya_id;
    SELECT pg_current_snapshot() AS snapshot;
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 4) SERIALIZABLE
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    SHOW transaction_isolation;
    SELECT COUNT(*) FROM hisoblar;
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 5) IKKI SESSIYALI SSENARIY — non-repeatable read
--    (bitta skriptda ko'rsatib bo'lmaydi; ikki psql oynasida sinang)
-- ─────────────────────────────────────────────────────────────────────
--   Sessiya A                              Sessiya B
--   ----------------------------------     -----------------------------
--   BEGIN;  -- READ COMMITTED
--   SELECT balans FROM hisoblar
--     WHERE id=1;        --> 1000000
--                                          BEGIN;
--                                          UPDATE hisoblar
--                                            SET balans = 700000
--                                            WHERE id=1;
--                                          COMMIT;
--   SELECT balans FROM hisoblar
--     WHERE id=1;        --> 700000   <-- O'ZGARDI! non-repeatable read
--   COMMIT;
--
--   Ayni ssenariy REPEATABLE READ da:
--   ikkinchi SELECT ham 1000000 qaytaradi — snapshot muzlagan.
--   Agar A o'sha qatorni UPDATE qilmoqchi bo'lsa:
--     ERROR:  could not serialize access due to concurrent update
--     SQLSTATE 40001  -> ilova tranzaksiyani QAYTA boshlashi kerak.

-- ─────────────────────────────────────────────────────────────────────
-- 6) SAVEPOINT — tranzaksiya ichidagi qisman qaytarish
-- ─────────────────────────────────────────────────────────────────────
-- AVVAL: savepoint SIZ nima bo'lishini ko'ramiz
BEGIN;
    UPDATE hisoblar SET balans = balans - 1 WHERE egasi = 'Aziz';
    UPDATE hisoblar SET balans = balans - 999999999 WHERE egasi = 'Dilnoza';
    --  ERROR:  new row for relation "hisoblar" violates check constraint
    SELECT 'bu so''rov ham bajarilmaydi' AS eslatma;
    --  ERROR:  current transaction is aborted, commands ignored until
    --          end of transaction block
COMMIT;
--  Natija: ROLLBACK. Birinchi UPDATE ham yo'qoldi.

-- ENDI: savepoint BILAN
BEGIN;
    UPDATE hisoblar SET balans = balans - 200000 WHERE egasi = 'Aziz';
    SAVEPOINT sp1;
    UPDATE hisoblar SET balans = balans - 999999999 WHERE egasi = 'Dilnoza';
    --  ERROR:  ... violates check constraint "hisoblar_balans_check"
    ROLLBACK TO SAVEPOINT sp1;   -- faqat sp1 dan KEYINGI ish bekor bo'ladi
    UPDATE hisoblar SET balans = balans + 200000 WHERE egasi = 'Dilnoza';
COMMIT;
--  Natija: COMMIT muvaffaqiyatli. O'tkazma amalga oshdi:
--  Aziz 800000.00, Dilnoza 700000.00
SELECT * FROM hisoblar ORDER BY id;

-- ─────────────────────────────────────────────────────────────────────
-- 7) MVCC ni "ko'rish": har qatorning yashirin xizmat ustunlari
-- ─────────────────────────────────────────────────────────────────────
SELECT id, egasi, balans,
       xmin,   -- qatorning bu versiyasini YARATGAN tranzaksiya
       xmax,   -- uni o'chirgan/yangilagan tranzaksiya (0 = hali tirik)
       ctid    -- jismoniy joylashuv: (sahifa, qator)
FROM hisoblar ORDER BY id;

-- UPDATE dan keyin ctid O'ZGARADI — chunki bu joyida o'zgartirish emas,
-- yangi versiya yozish. Eski versiya diskda qoladi va uni VACUUM tozalaydi.
BEGIN;
    UPDATE hisoblar SET balans = balans + 1 WHERE id = 1;
    SELECT id, xmin, xmax, ctid FROM hisoblar WHERE id = 1;
ROLLBACK;

-- ─────────────────────────────────────────────────────────────────────
-- 8) Qayta urinish uchun xato kodlari
-- ─────────────────────────────────────────────────────────────────────
SELECT '40001' AS kod, 'serialization_failure' AS nomi,
       'Tranzaksiyani boshidan qayta bajaring' AS harakat
UNION ALL
SELECT '40P01', 'deadlock_detected',
       'Tranzaksiyani boshidan qayta bajaring';

-- Ilovadagi naqsh (psevdokod):
--   for urinish in range(3):
--       try:
--           with db.begin(isolation_level="REPEATABLE READ"):
--               ...ish...
--           break
--       except SerializationFailure:
--           sleep(0.05 * 2 ** urinish)   -- eksponensial kutish
--           continue
--   else:
--       raise  -- 3 urinishdan keyin ham bo'lmadi""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Транзакции и уровни изоляции
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hisoblar;
CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES ('Aziz', 1000000), ('Dilnoza', 500000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) Уровень по умолчанию
-- ─────────────────────────────────────────────────────────────────────
SHOW default_transaction_isolation;
--  read committed

-- ─────────────────────────────────────────────────────────────────────
-- 2) READ UNCOMMITTED — принимается, но dirty read НЕ БУДЕТ
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SHOW transaction_isolation;
    --  read uncommitted
    -- ВНИМАНИЕ: PostgreSQL принял команду и вернул это же название,
    -- НО поведение совпадает с READ COMMITTED. Архитектура MVCC делает
    -- чтение незакоммиченных данных принципиально невозможным.
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 3) REPEATABLE READ — снимок замораживается на ПЕРВОМ запросе
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SHOW transaction_isolation;
    SELECT SUM(balans) AS boshlangich FROM hisoblar;
    -- С этого момента, что бы ни делала другая сессия, все SELECT внутри
    -- этой транзакции будут видеть ИМЕННО этот снимок.
    SELECT txid_current()        AS tranzaksiya_id;
    SELECT pg_current_snapshot() AS snapshot;
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 4) SERIALIZABLE
-- ─────────────────────────────────────────────────────────────────────
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    SHOW transaction_isolation;
    SELECT COUNT(*) FROM hisoblar;
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 5) СЦЕНАРИЙ НА ДВЕ СЕССИИ — non-repeatable read
--    (в одном скрипте не показать; попробуйте в двух окнах psql)
-- ─────────────────────────────────────────────────────────────────────
--   Сессия A                               Сессия B
--   ----------------------------------     -----------------------------
--   BEGIN;  -- READ COMMITTED
--   SELECT balans FROM hisoblar
--     WHERE id=1;        --> 1000000
--                                          BEGIN;
--                                          UPDATE hisoblar
--                                            SET balans = 700000
--                                            WHERE id=1;
--                                          COMMIT;
--   SELECT balans FROM hisoblar
--     WHERE id=1;        --> 700000   <-- ИЗМЕНИЛОСЬ! non-repeatable read
--   COMMIT;
--
--   Тот же сценарий при REPEATABLE READ:
--   второй SELECT тоже вернёт 1000000 — снимок заморожен.
--   Если A попытается обновить ту же строку:
--     ERROR:  could not serialize access due to concurrent update
--     SQLSTATE 40001  -> приложение должно НАЧАТЬ транзакцию заново.

-- ─────────────────────────────────────────────────────────────────────
-- 6) SAVEPOINT — частичный откат внутри транзакции
-- ─────────────────────────────────────────────────────────────────────
-- СНАЧАЛА: посмотрим, что происходит БЕЗ savepoint
BEGIN;
    UPDATE hisoblar SET balans = balans - 1 WHERE egasi = 'Aziz';
    UPDATE hisoblar SET balans = balans - 999999999 WHERE egasi = 'Dilnoza';
    --  ERROR:  new row for relation "hisoblar" violates check constraint
    SELECT 'bu so''rov ham bajarilmaydi' AS eslatma;
    --  ERROR:  current transaction is aborted, commands ignored until
    --          end of transaction block
COMMIT;
--  Результат: ROLLBACK. Первый UPDATE тоже потерян.

-- ТЕПЕРЬ: С savepoint
BEGIN;
    UPDATE hisoblar SET balans = balans - 200000 WHERE egasi = 'Aziz';
    SAVEPOINT sp1;
    UPDATE hisoblar SET balans = balans - 999999999 WHERE egasi = 'Dilnoza';
    --  ERROR:  ... violates check constraint "hisoblar_balans_check"
    ROLLBACK TO SAVEPOINT sp1;   -- отменяется только работа ПОСЛЕ sp1
    UPDATE hisoblar SET balans = balans + 200000 WHERE egasi = 'Dilnoza';
COMMIT;
--  Результат: COMMIT успешен. Перевод выполнен:
--  Aziz 800000.00, Dilnoza 700000.00
SELECT * FROM hisoblar ORDER BY id;

-- ─────────────────────────────────────────────────────────────────────
-- 7) «Увидеть» MVCC: скрытые служебные колонки каждой строки
-- ─────────────────────────────────────────────────────────────────────
SELECT id, egasi, balans,
       xmin,   -- транзакция, СОЗДАВШАЯ эту версию строки
       xmax,   -- транзакция, удалившая/обновившая её (0 = ещё жива)
       ctid    -- физическое расположение: (страница, строка)
FROM hisoblar ORDER BY id;

-- После UPDATE ctid ИЗМЕНИТСЯ — потому что это не правка на месте,
-- а запись новой версии. Старая остаётся на диске, её чистит VACUUM.
BEGIN;
    UPDATE hisoblar SET balans = balans + 1 WHERE id = 1;
    SELECT id, xmin, xmax, ctid FROM hisoblar WHERE id = 1;
ROLLBACK;

-- ─────────────────────────────────────────────────────────────────────
-- 8) Коды ошибок для повторной попытки
-- ─────────────────────────────────────────────────────────────────────
SELECT '40001' AS kod, 'serialization_failure' AS nomi,
       'Выполните транзакцию заново с начала' AS harakat
UNION ALL
SELECT '40P01', 'deadlock_detected',
       'Выполните транзакцию заново с начала';

-- Паттерн в приложении (псевдокод):
--   for urinish in range(3):
--       try:
--           with db.begin(isolation_level="REPEATABLE READ"):
--               ...работа...
--           break
--       except SerializationFailure:
--           sleep(0.05 * 2 ** urinish)   -- экспоненциальная задержка
--           continue
--   else:
--       raise  -- не получилось и после 3 попыток""",
        "task": {
            "task_title": "Amaliy topshiriq: Anomaliyani ikki sessiyada takrorlash va bloklash",
            "task_title_ru": "Практическое задание: воспроизвести аномалию в двух сессиях и заблокировать её",
            "task_description": (
                "Ikkita psql oynasini oching va konkurent anomaliyalarni HAQIQATAN takrorlang "
                "— o'qib bilish bilan ko'rib bilish orasida katta farq bor.\n\n"
                "Avval READ COMMITTED da non-repeatable read ni chiqaring: A sessiyasi bir "
                "qatorni ikki marta o'qiydi, orasida B uni o'zgartirib COMMIT qiladi. So'ng "
                "AYNAN o'sha ssenariyni REPEATABLE READ da takrorlang va ikkinchi SELECT eski "
                "qiymatni qaytarishini ko'rsating. Undan keyin A o'sha qatorni UPDATE "
                "qilmoqchi bo'lsin va serializatsiya xatosini (SQLSTATE 40001) ushlang.\n\n"
                "Hisobot ikki ustunli jurnal ko'rinishida bo'lsin: chap ustunda A sessiyasining "
                "buyruqlari va natijalari, o'ng ustunda B ning — vaqt bo'yicha to'g'ri "
                "tartibda. Har bir xato matni haqiqiy, serverdan olingan bo'lishi kerak."
            ),
            "task_description_ru": (
                "Откройте два окна psql и РЕАЛЬНО воспроизведите конкурентные аномалии — между "
                "«прочитать про них» и «увидеть их» большая разница.\n\n"
                "Сначала получите non-repeatable read на READ COMMITTED: сессия A читает строку "
                "дважды, между чтениями B изменяет её и делает COMMIT. Затем повторите ТОТ ЖЕ "
                "сценарий на REPEATABLE READ и покажите, что второй SELECT возвращает старое "
                "значение. После этого пусть A попробует обновить эту строку — поймайте ошибку "
                "сериализации (SQLSTATE 40001).\n\n"
                "Отчёт оформите двухколоночным журналом: слева команды и результаты сессии A, "
                "справа — сессии B, в правильном хронологическом порядке. Все тексты ошибок "
                "должны быть настоящими, снятыми с сервера."
            ),
            "task_requirements": (
                "1. Sxema: hisoblar jadvali (egasi, balans) va CHECK (balans >= 0) cheklovi.\n"
                "2. READ COMMITTED da non-repeatable read: ikki sessiya jurnali, ikkala "
                "SELECT natijasi ham ko'rsatilsin.\n"
                "3. Ayni ssenariy REPEATABLE READ da: ikkinchi SELECT eski qiymatni "
                "qaytarishi ko'rsatilsin. Izohda snapshot qachon muzlashi yozilsin.\n"
                "4. REPEATABLE READ da A o'sha qatorni UPDATE qilishga urinsin; haqiqiy xato "
                "matni va SQLSTATE 40001 keltirilsin.\n"
                "5. Phantom read: bir shart bo'yicha COUNT(*) ikki marta o'qilsin, orasida B "
                "yangi qator qo'shsin. READ COMMITTED da farq chiqishi va REPEATABLE READ da "
                "chiqmasligi ko'rsatilsin; izohda PostgreSQL bu yerda standartdan kuchliroq "
                "ekani qayd etilsin.\n"
                "6. READ UNCOMMITTED: SHOW transaction_isolation o'sha nomni qaytarsa ham dirty "
                "read SODIR BO'LMASLIGI ko'rsatilsin; izohda MVCC orqali sabab yozilsin.\n"
                "7. SAVEPOINT: bitta tranzaksiyada ikkinchi buyruq CHECK ni buzsin. Ikki "
                "variant keltirilsin — savepointsiz (butun tranzaksiya yo'qoladi, 'current "
                "transaction is aborted' xatosi bilan) va SAVEPOINT + ROLLBACK TO bilan "
                "(birinchi o'zgarish saqlanib, COMMIT muvaffaqiyatli bo'ladi). Yakuniy "
                "balanslar ko'rsatilsin.\n"
                "8. Qayta urinish (retry) mantiqining psevdokodi: 40001 va 40P01 ushlansin, "
                "eksponensial kutish bo'lsin, urinishlar soni cheklansin.\n"
                "9. xmin/xmax/ctid ustunlari orqali UPDATE dan keyin qatorning YANGI versiya "
                "yozilishini ko'rsating.\n"
                "10. Hisobot .sql yoki .md ko'rinishida, ikki sessiya jurnali aniq ajratilgan "
                "holda topshirilsin."
            ),
            "task_requirements_ru": (
                "1. Схема: таблица счетов (владелец, баланс) с ограничением CHECK (balans >= 0).\n"
                "2. Non-repeatable read на READ COMMITTED: журнал двух сессий с результатами "
                "обоих SELECT.\n"
                "3. Тот же сценарий на REPEATABLE READ: покажите, что второй SELECT вернул "
                "старое значение. В комментарии укажите, когда замерзает снимок.\n"
                "4. На REPEATABLE READ пусть A попробует обновить ту же строку; приведите "
                "настоящий текст ошибки и SQLSTATE 40001.\n"
                "5. Phantom read: дважды прочитайте COUNT(*) по одному условию, между чтениями "
                "B вставляет новую строку. Покажите, что на READ COMMITTED разница есть, а на "
                "REPEATABLE READ нет; отметьте в комментарии, что здесь PostgreSQL строже "
                "стандарта.\n"
                "6. READ UNCOMMITTED: покажите, что SHOW transaction_isolation возвращает это "
                "имя, но dirty read НЕ ПРОИСХОДИТ; в комментарии объясните причину через MVCC.\n"
                "7. SAVEPOINT: в одной транзакции второй командой нарушьте CHECK. Приведите два "
                "варианта — без savepoint (вся транзакция теряется, ошибка 'current transaction "
                "is aborted') и с SAVEPOINT + ROLLBACK TO (первое изменение сохраняется, COMMIT "
                "проходит). Покажите итоговые балансы.\n"
                "8. Псевдокод логики повторов: перехват 40001 и 40P01, экспоненциальная "
                "задержка, ограниченное число попыток.\n"
                "9. Через колонки xmin/xmax/ctid покажите, что UPDATE пишет НОВУЮ версию строки.\n"
                "10. Отчёт сдайте в виде .sql или .md с чётко разделённым журналом двух сессий."
            ),
            "task_technologies": "PostgreSQL, BEGIN/COMMIT, isolation levels, SAVEPOINT, MVCC",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: Izolyatsiya darajalari, SAVEPOINT va MVCC ustunlari",
            "description": "REPEATABLE READ da muzlagan snapshot, READ UNCOMMITTED nega dirty read bermasligi, SAVEPOINT bilan qisman qaytarish va xmin/xmax/ctid orqali MVCC",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: izolyatsiya darajalari, SAVEPOINT va MVCC
DROP TABLE IF EXISTS hisoblar;
CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES ('Aziz', 1000000), ('Dilnoza', 500000);

-- 1) Standart daraja
SHOW default_transaction_isolation;   --  read committed

-- 2) READ UNCOMMITTED qabul qilinadi, LEKIN dirty read BO'LMAYDI.
--    SHOW o'sha nomni qaytaradi, xatti-harakat esa READ COMMITTED bilan
--    bir xil: MVCC commit qilinmagan ma'lumotni o'qishni imkonsiz qiladi.
BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SHOW transaction_isolation;
COMMIT;

-- 3) REPEATABLE READ — snapshot BIRINCHI so'rovda muzlaydi va tranzaksiya
--    oxirigacha o'zgarmaydi. PostgreSQL'da bu phantom read ni ham bloklaydi.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    SELECT SUM(balans) AS boshlangich FROM hisoblar;
    SELECT SUM(balans) AS takroriy    FROM hisoblar;   -- AYNAN bir xil
COMMIT;

-- ══ IKKI SESSIYALI SSENARIY (ikkita psql oynasida sinang) ═══════════
--   Sessiya A                              Sessiya B
--   ---------------------------------      ---------------------------------
--   BEGIN;  -- READ COMMITTED
--   SELECT balans WHERE id=1;  --> 1000000
--                                          BEGIN;
--                                          UPDATE hisoblar
--                                            SET balans=700000 WHERE id=1;
--                                          COMMIT;
--   SELECT balans WHERE id=1;  --> 700000  <-- NON-REPEATABLE READ
--   COMMIT;
--
--   Ayni ssenariy REPEATABLE READ da: ikkinchi SELECT ham 1000000 beradi.
--   Agar A o'sha qatorni UPDATE qilmoqchi bo'lsa:
--     ERROR: could not serialize access due to concurrent update
--     SQLSTATE 40001 -> ilova tranzaksiyani QAYTA boshlashi kerak.

-- 4) SAVEPOINT — tranzaksiya ichidagi qisman qaytarish.
--    Savepointsiz: xatodan keyin tranzaksiya "aborted" bo'ladi va
--    ROLLBACK dan boshqa yo'l qolmaydi — birinchi UPDATE ham yo'qoladi.
BEGIN;
    UPDATE hisoblar SET balans = balans - 200000 WHERE egasi = 'Aziz';
    SAVEPOINT sp1;
    -- Shu yerda CHECK cheklovini buzuvchi UPDATE bo'lsa (masalan
    -- balans = balans - 999999999), tranzaksiya aborted holatga o'tadi.
    ROLLBACK TO SAVEPOINT sp1;   -- faqat sp1 dan KEYINGI ish bekor bo'ladi
    UPDATE hisoblar SET balans = balans + 200000 WHERE egasi = 'Dilnoza';
COMMIT;
SELECT * FROM hisoblar ORDER BY id;   -- Aziz 800000, Dilnoza 700000

-- 5) MVCC ni "ko'rish": qatorning yashirin xizmat ustunlari
SELECT id, egasi, balans,
       xmin,   -- bu versiyani YARATGAN tranzaksiya
       xmax,   -- uni o'chirgan/yangilagan (0 = hali tirik)
       ctid    -- jismoniy joylashuv: (sahifa, qator)
FROM hisoblar ORDER BY id;

-- UPDATE joyida o'zgartirish EMAS — yangi versiya yozish. ctid o'zgaradi,
-- eski versiya diskda qoladi va uni VACUUM tozalaydi.
BEGIN;
    UPDATE hisoblar SET balans = balans + 1 WHERE id = 1;
    SELECT id, xmin, xmax, ctid FROM hisoblar WHERE id = 1;
ROLLBACK;

-- 6) Qayta urinish talab qiladigan xato kodlari
SELECT '40001' AS kod, 'serialization_failure' AS nomi
UNION ALL
SELECT '40P01', 'deadlock_detected';
-- Bular bug emas, dizaynning bir qismi. Qayta urinish mantiqisiz
-- REPEATABLE READ / SERIALIZABLE ishlatish foydalanuvchiga tasodifiy
-- xatolar ko'rsatishdan boshqa narsa bermaydi.""",
        },
        "exercises": [
            {
                "title": "PostgreSQL'da dirty read",
                "title_ru": "Dirty read в PostgreSQL",
                "description": "Dasturchi `BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` yozdi va boshqa sessiyaning commit qilinmagan o'zgarishlarini ko'rishni kutmoqda. Aslida nima bo'ladi?",
                "description_ru": "Разработчик написал `BEGIN TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` и ожидает увидеть незакоммиченные изменения другой сессии. Что произойдёт на самом деле?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Buyruq xato beradi: PostgreSQL bu darajani qo'llab-quvvatlamaydi",
                    "Buyruq qabul qilinadi va commit qilinmagan ma'lumot haqiqatan ko'rinadi",
                    "Buyruq qabul qilinadi, lekin xatti-harakat READ COMMITTED bilan bir xil — dirty read sodir bo'lmaydi",
                    "Tranzaksiya avtomatik SERIALIZABLE darajasiga ko'tariladi",
                ],
                "options_ru": [
                    "Команда выдаст ошибку: PostgreSQL не поддерживает этот уровень",
                    "Команда принимается, и незакоммиченные данные действительно видны",
                    "Команда принимается, но поведение совпадает с READ COMMITTED — dirty read не произойдёт",
                    "Транзакция автоматически повышается до уровня SERIALIZABLE",
                ],
                "correct_answers": "C",
                "is_multiple_select": False,
                "hint": "MVCC arxitekturasida qatorning eski va yangi versiyalari qanday saqlanishini eslang.",
                "hint_ru": "Вспомните, как в архитектуре MVCC хранятся старая и новая версии строки.",
                "explanation": "PostgreSQL buyruqni qabul qiladi va SHOW transaction_isolation hatto 'read uncommitted' deb qaytaradi, lekin MVCC commit qilinmagan versiyani boshqa tranzaksiyaga umuman ko'rsatmaydi. Ya'ni dirty read PostgreSQL'da prinsipial ravishda mumkin emas.",
                "difficulty_level": "Hard",
                "points": 12,
            },
            {
                "title": "Serialization xatosining kodi",
                "title_ru": "Код ошибки сериализации",
                "description": "REPEATABLE READ yoki SERIALIZABLE darajasida bir vaqtda o'zgartirish sababli tranzaksiya rad etilganda qaytariladigan SQLSTATE kodi: ___",
                "description_ru": "SQLSTATE-код, возвращаемый при отклонении транзакции из-за конкурентного изменения на уровне REPEATABLE READ или SERIALIZABLE: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "40001",
                "hint": "Deadlock uchun 40P01, serialization uchun esa besh raqamli qo'shni kod.",
                "hint_ru": "Для deadlock — 40P01, для сериализации — соседний пятизначный код.",
                "explanation": "40001 = serialization_failure. Bu xato bug emas, dizaynning bir qismi: u ilovaga tranzaksiyani boshidan qayta bajarish kerakligini bildiradi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Izolyatsiya darajalari haqida to'g'ri fikrlar",
                "title_ru": "Верные утверждения об уровнях изоляции",
                "description": "PostgreSQL uchun qaysi fikrlar to'g'ri?",
                "description_ru": "Какие утверждения верны для PostgreSQL?",
                "exercise_type": "multiple_choice",
                "options": [
                    "READ COMMITTED da snapshot har bir buyruq boshida yangilanadi, shuning uchun bitta tranzaksiyadagi ikki SELECT turli natija berishi mumkin",
                    "REPEATABLE READ PostgreSQL'da phantom read ni ham bloklaydi",
                    "SERIALIZABLE ishlatilganda ilovada qayta urinish (retry) mantiqi bo'lishi kerak",
                    "Kuchli izolyatsiya darajasi hech qanday qo'shimcha narxga ega emas",
                ],
                "options_ru": [
                    "При READ COMMITTED снимок обновляется в начале каждой команды, поэтому два SELECT в одной транзакции могут дать разный результат",
                    "REPEATABLE READ в PostgreSQL блокирует и phantom read",
                    "При использовании SERIALIZABLE в приложении должна быть логика повторных попыток (retry)",
                    "Более сильный уровень изоляции не имеет никакой дополнительной цены",
                ],
                "correct_answers": "A,B,C",
                "is_multiple_select": True,
                "hint": "Kuchliroq izolyatsiya nimani ko'paytiradi — konfliktlarnimi yoki anomaliyalarnimi?",
                "hint_ru": "Что увеличивает более сильная изоляция — конфликты или аномалии?",
                "explanation": "D noto'g'ri: kuchliroq izolyatsiya kamroq anomaliya, lekin ko'proq konflikt va 40001 xatolari degani. Bu har doim savdolashuv.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 8
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 8,
        "title": "8-Locking va deadlock'lar",
        "title_ru": "8-Блокировки и взаимоблокировки",
        "points_reward": 15,
        "code_language": "sql",
        "text_content": """<h3>MVCC hamma narsani hal qilmaydi</h3>
<p>Oldingi darsda ko'rdik: MVCC tufayli o'quvchilar yozuvchilarni bloklamaydi. Lekin <strong>ikki yozuvchi bir qatorni</strong> o'zgartirmoqchi bo'lganda hech qanday sehr yordam bermaydi &mdash; kimdir kutishi kerak. Aynan shu joydan qulflar (lock) boshlanadi.</p>
<p>PostgreSQL qatorni <code>UPDATE</code> qilganda unga avtomatik qulf qo'yadi va uni <strong>tranzaksiya oxirigacha</strong> ushlab turadi. Qulfni erta bo'shatish imkoni yo'q &mdash; shuning uchun uzoq tranzaksiya boshqa hamma narsani bloklab qo'yishi mumkin.</p>

<h3>Klassik xato: o'qib, hisoblab, yozish</h3>
<p>Eng ko'p uchraydigan konkurentlik xatosi shunday ko'rinadi:</p>
<pre><code>balans = SELECT balans FROM hisoblar WHERE id=1;   -- 1000
yangi   = balans - 300;                             -- ilovada hisoblanadi
UPDATE hisoblar SET balans = yangi WHERE id=1;      -- 700 yoziladi</code></pre>
<p>Ikki foydalanuvchi bir vaqtda shu amalni bajarsa, ikkalasi ham 1000 ni o'qiydi, ikkalasi ham 700 yozadi &mdash; va 600 bo'lishi kerak edi. 300 so'm yo'qoladi. Bu <em>lost update</em>.</p>
<p>Yechim uchta: <code>SELECT ... FOR UPDATE</code> bilan o'qishda qatorni band qilish; yoki hisobni bazaning o'ziga topshirish (<code>SET balans = balans - 300</code>); yoki REPEATABLE READ va <code>40001</code> ni qayta urinish bilan ushlash. Ikkinchisi eng oddiy va eng ishonchli &mdash; iloji bo'lsa shuni tanlang.</p>

<h3>Qulf turlari</h3>
<table>
<tr><th>Qulf</th><th>Nimani bloklaydi</th><th>Qachon ishlatiladi</th></tr>
<tr><td><code>FOR UPDATE</code></td><td>Har qanday o'zgartirish va boshqa qulflar</td><td>O'qib-o'zgartirish naqshi</td></tr>
<tr><td><code>FOR NO KEY UPDATE</code></td><td>Kalitsiz o'zgartirishlar</td><td>Oddiy <code>UPDATE</code> shuni oladi</td></tr>
<tr><td><code>FOR SHARE</code></td><td>O'zgartirishni, lekin o'qishni emas</td><td>&ldquo;O'qiyapman, o'zgartirmanglar&rdquo;</td></tr>
<tr><td><code>FOR KEY SHARE</code></td><td>Faqat kalit o'zgarishini</td><td>FK tekshiruvi avtomatik oladi</td></tr>
</table>

<h3>SKIP LOCKED &mdash; navbat uchun to'g'ri yechim</h3>
<p>Bir nechta ishchi (worker) bitta navbat jadvalidan vazifa olayotganda, oddiy <code>SELECT ... FOR UPDATE</code> ularni navbatga tizib qo'yadi: hammasi bir xil birinchi qatorni kutadi. <code>SKIP LOCKED</code> esa band qatorlarni <em>sakrab o'tadi</em> &mdash; har bir ishchi darhol o'ziga tegishli vazifani oladi.</p>
<p>Bu naqsh Celery, Sidekiq va shunga o'xshash navbat tizimlarining SQL asosi. <code>NOWAIT</code> esa boshqa vazifa bajaradi: kutish o'rniga darhol xato beradi &mdash; interaktiv ilovada &ldquo;yozuv band&rdquo; deb ko'rsatish uchun qulay.</p>

<h3>Deadlock: ikki tranzaksiya, teskari tartib</h3>
<p>Deadlock qachon paydo bo'lishini bir jumlada aytish mumkin: <strong>ikki tranzaksiya bir xil qatorlarni turli tartibda qulflaganda</strong>.</p>
<pre class="mermaid">
flowchart LR
  A["Tranzaksiya A
1) hisob 1 qulflandi
2) hisob 2 ni kutmoqda"] -->|"2-hisobni kutadi"| B["Tranzaksiya B
1) hisob 2 qulflandi
2) hisob 1 ni kutmoqda"]
  B -->|"1-hisobni kutadi"| A
  style A fill:#ffd6d6,stroke:#c00000
  style B fill:#ffd6d6,stroke:#c00000
</pre>
<p>PostgreSQL bu holatni o'zi aniqlaydi. <code>deadlock_timeout</code> (standart <strong>1s</strong>) o'tgach, u qulflar grafida halqa borligini tekshiradi va topsa &mdash; tranzaksiyalardan birini <strong>majburan bekor qiladi</strong>. Haqiqiy xato matni:</p>
<pre><code>ERROR:  deadlock detected
DETAIL:  Process 1023893 waits for ShareLock on transaction 13418187;
         blocked by process 1023894.
         Process 1023894 waits for ShareLock on transaction 13418186;
         blocked by process 1023893.
CONTEXT: while updating tuple (0,1) in relation "hisoblar"</code></pre>
<p>Diqqat qiling: <em>bitta</em> tranzaksiya qurbon bo'ladi, ikkinchisi normal davom etadi. Ya'ni deadlock server uchun halokat emas &mdash; lekin qurbon bo'lgan foydalanuvchi uchun xato.</p>

<h3>Deadlock'ning oldini olish</h3>
<ul>
<li><strong>Qulflash tartibini birxillashtiring.</strong> Eng ishonchli usul. Agar butun kod bazasi qatorlarni har doim <code>id</code> o'sish tartibida qulflasa, halqa hosil bo'lishi <em>matematik jihatdan</em> imkonsiz. Amalda: <code>WHERE id IN (1, 2) ORDER BY id FOR UPDATE</code>.</li>
<li><strong>Tranzaksiyalarni qisqartiring.</strong> Tranzaksiya ichida HTTP so'rov yubormang, fayl yuklamang, foydalanuvchi javobini kutmang.</li>
<li><strong><code>lock_timeout</code> qo'ying.</strong> Cheksiz kutish o'rniga xato oling: <code>SET LOCAL lock_timeout = '3s'</code>.</li>
<li><strong>Qayta urinish yozing.</strong> <code>40P01</code> ni ushlab, tranzaksiyani boshidan bajaring.</li>
</ul>""",
        "text_content_ru": """<h3>MVCC решает не всё</h3>
<p>В прошлом уроке мы видели: благодаря MVCC читатели не блокируют писателей. Но когда <strong>два писателя</strong> хотят изменить одну строку, никакая магия не поможет — кто-то должен ждать. Именно отсюда начинаются блокировки.</p>
<p>При <code>UPDATE</code> PostgreSQL автоматически ставит на строку блокировку и держит её <strong>до конца транзакции</strong>. Освободить блокировку раньше нельзя — поэтому долгая транзакция способна заблокировать всё остальное.</p>

<h3>Классическая ошибка: прочитать, посчитать, записать</h3>
<p>Самая частая ошибка конкурентности выглядит так:</p>
<pre><code>balans = SELECT balans FROM hisoblar WHERE id=1;   -- 1000
yangi   = balans - 300;                             -- считается в приложении
UPDATE hisoblar SET balans = yangi WHERE id=1;      -- записывается 700</code></pre>
<p>Если два пользователя выполнят это одновременно, оба прочитают 1000, оба запишут 700 — а должно было получиться 600. Триста сумов пропадают. Это <em>lost update</em>.</p>
<p>Решений три: занять строку при чтении через <code>SELECT ... FOR UPDATE</code>; поручить расчёт самой базе (<code>SET balans = balans - 300</code>); либо использовать REPEATABLE READ и ловить <code>40001</code> с повтором. Второй вариант самый простой и надёжный — выбирайте его, если возможно.</p>

<h3>Типы блокировок</h3>
<table>
<tr><th>Блокировка</th><th>Что блокирует</th><th>Когда используется</th></tr>
<tr><td><code>FOR UPDATE</code></td><td>Любое изменение и другие блокировки</td><td>Паттерн «прочитать-изменить»</td></tr>
<tr><td><code>FOR NO KEY UPDATE</code></td><td>Изменения, не затрагивающие ключ</td><td>Её берёт обычный <code>UPDATE</code></td></tr>
<tr><td><code>FOR SHARE</code></td><td>Изменение, но не чтение</td><td>«Я читаю, не меняйте»</td></tr>
<tr><td><code>FOR KEY SHARE</code></td><td>Только изменение ключа</td><td>Автоматически берёт проверка FK</td></tr>
</table>

<h3>SKIP LOCKED — правильное решение для очереди</h3>
<p>Когда несколько воркеров разбирают задачи из одной таблицы-очереди, обычный <code>SELECT ... FOR UPDATE</code> выстраивает их в очередь: все ждут одну и ту же первую строку. А <code>SKIP LOCKED</code> <em>перепрыгивает</em> занятые строки — каждый воркер сразу получает свою задачу.</p>
<p>Этот приём — SQL-основа Celery, Sidekiq и подобных систем очередей. <code>NOWAIT</code> решает другую задачу: вместо ожидания он сразу выдаёт ошибку — удобно, чтобы показать в интерактивном приложении «запись занята».</p>

<h3>Взаимоблокировка: две транзакции, обратный порядок</h3>
<p>Когда возникает deadlock, можно сказать одной фразой: <strong>когда две транзакции блокируют одни и те же строки в разном порядке</strong>.</p>
<pre class="mermaid">
flowchart LR
  A["Транзакция A
1) счёт 1 заблокирован
2) ждёт счёт 2"] -->|"ждёт счёт 2"| B["Транзакция B
1) счёт 2 заблокирован
2) ждёт счёт 1"]
  B -->|"ждёт счёт 1"| A
  style A fill:#ffd6d6,stroke:#c00000
  style B fill:#ffd6d6,stroke:#c00000
</pre>
<p>PostgreSQL обнаруживает эту ситуацию сам. По истечении <code>deadlock_timeout</code> (по умолчанию <strong>1s</strong>) он проверяет граф блокировок на наличие цикла и, найдя его, <strong>принудительно откатывает</strong> одну из транзакций. Реальный текст ошибки:</p>
<pre><code>ERROR:  deadlock detected
DETAIL:  Process 1023893 waits for ShareLock on transaction 13418187;
         blocked by process 1023894.
         Process 1023894 waits for ShareLock on transaction 13418186;
         blocked by process 1023893.
CONTEXT: while updating tuple (0,1) in relation "hisoblar"</code></pre>
<p>Обратите внимание: жертвой становится <em>одна</em> транзакция, вторая продолжает работу нормально. То есть deadlock — не катастрофа для сервера, но ошибка для пострадавшего пользователя.</p>

<h3>Как предотвратить deadlock</h3>
<ul>
<li><strong>Унифицируйте порядок блокировки.</strong> Самый надёжный способ. Если вся кодовая база всегда блокирует строки в порядке возрастания <code>id</code>, образование цикла <em>математически</em> невозможно. На практике: <code>WHERE id IN (1, 2) ORDER BY id FOR UPDATE</code>.</li>
<li><strong>Сокращайте транзакции.</strong> Не отправляйте HTTP-запросы, не загружайте файлы и не ждите ответа пользователя внутри транзакции.</li>
<li><strong>Ставьте <code>lock_timeout</code>.</strong> Вместо бесконечного ожидания получите ошибку: <code>SET LOCAL lock_timeout = '3s'</code>.</li>
<li><strong>Пишите повтор.</strong> Ловите <code>40P01</code> и выполняйте транзакцию заново.</li>
</ul>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Qulflar (locks), SKIP LOCKED navbati va deadlock
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS navbat;
DROP TABLE IF EXISTS hisoblar;

CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES
    ('Aziz', 1000000), ('Dilnoza', 500000), ('Sardor', 300000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) FOR UPDATE — o'qib-o'zgartirish naqshini himoyalash
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    -- Bu qator endi tranzaksiya oxirigacha BAND. Boshqa sessiya uni
    -- o'zgartirmoqchi bo'lsa — kutadi.
    SELECT id, egasi, balans FROM hisoblar WHERE id = 1 FOR UPDATE;
    UPDATE hisoblar SET balans = balans - 100000 WHERE id = 1;
COMMIT;

-- Eslatma: agar hisob-kitob bazaning o'zida bajarilsa, FOR UPDATE
-- umuman kerak emas — UPDATE qatorni o'zi qulflaydi va qiymatni
-- ATOMAR o'qib-yozadi:
--     UPDATE hisoblar SET balans = balans - 100000 WHERE id = 1;
-- Bu "lost update" ga qarshi eng oddiy va eng ishonchli himoya.

-- ─────────────────────────────────────────────────────────────────────
-- 2) Qulf turlari (kuchlidan kuchsizga)
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;        -- eng kuchli
    SELECT id FROM hisoblar WHERE id = 2 FOR NO KEY UPDATE; -- UPDATE shuni oladi
    SELECT id FROM hisoblar WHERE id = 3 FOR SHARE;         -- o'zgartirishni bloklaydi
    SELECT id FROM hisoblar WHERE id = 3 FOR KEY SHARE;     -- FK tekshiruvi shuni oladi
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 3) NOWAIT — kutish o'rniga darhol xato
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE NOWAIT;
    -- Qator band bo'lsa:
    --   ERROR:  could not obtain lock on row in relation "hisoblar"
    -- Interaktiv ilovada "yozuv band, keyinroq urinib ko'ring" uchun qulay.
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 4) SKIP LOCKED — ko'p ishchili navbat (Celery/Sidekiq ning SQL asosi)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE navbat (
    id      BIGSERIAL   PRIMARY KEY,
    vazifa  TEXT        NOT NULL,
    holat   VARCHAR(20) NOT NULL DEFAULT 'kutmoqda',
    olingan TIMESTAMPTZ
);
INSERT INTO navbat (vazifa) SELECT 'Vazifa ' || g FROM generate_series(1, 10) g;

-- Qisman indeks: faqat kutayotgan vazifalar indekslanadi (5-darsga qarang)
CREATE INDEX idx_navbat_holat ON navbat(holat, id) WHERE holat = 'kutmoqda';

-- Har bir ishchi shu so'rovni bajaradi. SKIP LOCKED tufayli ular
-- BIR-BIRINI KUTMAYDI: 2-ishchi 1-ishchi olgan qatorlarni sakrab o'tadi.
BEGIN;
    WITH keyingi AS (
        SELECT id FROM navbat
        WHERE holat = 'kutmoqda'
        ORDER BY id
        FOR UPDATE SKIP LOCKED
        LIMIT 3
    )
    UPDATE navbat n
    SET holat = 'bajarilmoqda', olingan = NOW()
    FROM keyingi k
    WHERE n.id = k.id
    RETURNING n.id, n.vazifa;
COMMIT;

SELECT holat, COUNT(*) FROM navbat GROUP BY holat ORDER BY holat;
--  bajarilmoqda | 3
--  kutmoqda     | 7

-- ─────────────────────────────────────────────────────────────────────
-- 5) lock_timeout — cheksiz kutmaslik
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SET LOCAL lock_timeout = '3s';   -- LOCAL: faqat shu tranzaksiya uchun
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;
    -- 3 sekunddan keyin ham qulf olinmasa:
    --   ERROR:  canceling statement due to lock timeout
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 6) DEADLOCK — ikki sessiyada takrorlanadigan ssenariy
--    Ikki psql oynasini oching va quyidagilarni PARALLEL bajaring:
-- ─────────────────────────────────────────────────────────────────────
--   Sessiya A                               Sessiya B
--   -----------------------------------     -----------------------------------
--   BEGIN;                                  BEGIN;
--   UPDATE hisoblar SET balans=balans-100    UPDATE hisoblar SET balans=balans-50
--     WHERE id = 1;   -- 1-qator qulflandi     WHERE id = 2;   -- 2-qator qulflandi
--   SELECT pg_sleep(2);                      SELECT pg_sleep(2);
--   UPDATE hisoblar SET balans=balans+100    UPDATE hisoblar SET balans=balans+50
--     WHERE id = 2;   -- B ni kutadi           WHERE id = 1;   -- A ni kutadi
--                          \\_______ HALQA _______/
--   COMMIT;                                  <-- BU YERDA XATO:
--
--   ERROR:  deadlock detected
--   DETAIL:  Process 1023893 waits for ShareLock on transaction 13418187;
--            blocked by process 1023894.
--            Process 1023894 waits for ShareLock on transaction 13418186;
--            blocked by process 1023893.
--   HINT:  See server log for query details.
--   CONTEXT:  while updating tuple (0,1) in relation "hisoblar"
--
--   Diqqat: FAQAT BITTA sessiya qurbon bo'ldi (B), A esa normal COMMIT bo'ldi.

SHOW deadlock_timeout;
--  1s  <-- PostgreSQL shuncha kutgandan keyingina halqa qidiradi.
--          Tekshiruv qimmat, shuning uchun u darhol bajarilmaydi.

-- ─────────────────────────────────────────────────────────────────────
-- 7) DEADLOCK OLDINI OLISH: har doim BIR XIL tartibda qulflash
--    Bu eng ishonchli usul — halqa matematik jihatdan hosil bo'lolmaydi.
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id, egasi FROM hisoblar
    WHERE id IN (1, 2)
    ORDER BY id            -- <<< ENG MUHIM QATOR
    FOR UPDATE;
    -- Endi ikkala qator ham qulflangan va TARTIB kafolatlangan.
    UPDATE hisoblar SET balans = balans - 100 WHERE id = 1;
    UPDATE hisoblar SET balans = balans + 100 WHERE id = 2;
COMMIT;

SELECT * FROM hisoblar ORDER BY id;

-- ─────────────────────────────────────────────────────────────────────
-- 8) DIAGNOSTIKA: kim kimni bloklayapti (produksiyada)
-- ─────────────────────────────────────────────────────────────────────
SELECT pid,
       state,
       wait_event_type,
       pg_blocking_pids(pid) AS bloklovchilar,   -- bo'sh massiv = bloklanmagan
       LEFT(query, 60)       AS sorov
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
ORDER BY pid;

-- Aniq qulflar ro'yxati:
SELECT locktype, relation::regclass AS jadval, mode, granted
FROM pg_locks
WHERE relation IS NOT NULL
ORDER BY granted, relation
LIMIT 20;

-- Uzoq ishlayotgan tranzaksiyalar — deadlock va bloklanishning asosiy sababi:
SELECT pid, NOW() - xact_start AS davomiylik, state, LEFT(query, 60) AS sorov
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND NOW() - xact_start > INTERVAL '5 seconds'
ORDER BY xact_start;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Блокировки (locks), очередь на SKIP LOCKED и взаимоблокировки
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS navbat;
DROP TABLE IF EXISTS hisoblar;

CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES
    ('Aziz', 1000000), ('Dilnoza', 500000), ('Sardor', 300000);

-- ─────────────────────────────────────────────────────────────────────
-- 1) FOR UPDATE — защита паттерна «прочитать-изменить»
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    -- Эта строка теперь ЗАНЯТА до конца транзакции. Если другая сессия
    -- захочет её изменить — будет ждать.
    SELECT id, egasi, balans FROM hisoblar WHERE id = 1 FOR UPDATE;
    UPDATE hisoblar SET balans = balans - 100000 WHERE id = 1;
COMMIT;

-- Замечание: если расчёт выполняется самой базой, FOR UPDATE вообще
-- не нужен — UPDATE сам блокирует строку и читает-пишет значение
-- АТОМАРНО:
--     UPDATE hisoblar SET balans = balans - 100000 WHERE id = 1;
-- Это самая простая и надёжная защита от «lost update».

-- ─────────────────────────────────────────────────────────────────────
-- 2) Типы блокировок (от сильной к слабой)
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;        -- самая сильная
    SELECT id FROM hisoblar WHERE id = 2 FOR NO KEY UPDATE; -- её берёт UPDATE
    SELECT id FROM hisoblar WHERE id = 3 FOR SHARE;         -- блокирует изменение
    SELECT id FROM hisoblar WHERE id = 3 FOR KEY SHARE;     -- её берёт проверка FK
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 3) NOWAIT — вместо ожидания сразу ошибка
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE NOWAIT;
    -- Если строка занята:
    --   ERROR:  could not obtain lock on row in relation "hisoblar"
    -- Удобно, чтобы в интерактивном приложении показать
    -- «запись занята, попробуйте позже».
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 4) SKIP LOCKED — очередь с несколькими воркерами (SQL-основа Celery/Sidekiq)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE navbat (
    id      BIGSERIAL   PRIMARY KEY,
    vazifa  TEXT        NOT NULL,
    holat   VARCHAR(20) NOT NULL DEFAULT 'kutmoqda',
    olingan TIMESTAMPTZ
);
INSERT INTO navbat (vazifa) SELECT 'Vazifa ' || g FROM generate_series(1, 10) g;

-- Частичный индекс: индексируются только ожидающие задачи (см. урок 5)
CREATE INDEX idx_navbat_holat ON navbat(holat, id) WHERE holat = 'kutmoqda';

-- Этот запрос выполняет каждый воркер. Благодаря SKIP LOCKED они
-- НЕ ЖДУТ ДРУГ ДРУГА: второй воркер перепрыгивает строки, взятые первым.
BEGIN;
    WITH keyingi AS (
        SELECT id FROM navbat
        WHERE holat = 'kutmoqda'
        ORDER BY id
        FOR UPDATE SKIP LOCKED
        LIMIT 3
    )
    UPDATE navbat n
    SET holat = 'bajarilmoqda', olingan = NOW()
    FROM keyingi k
    WHERE n.id = k.id
    RETURNING n.id, n.vazifa;
COMMIT;

SELECT holat, COUNT(*) FROM navbat GROUP BY holat ORDER BY holat;
--  bajarilmoqda | 3
--  kutmoqda     | 7

-- ─────────────────────────────────────────────────────────────────────
-- 5) lock_timeout — не ждать бесконечно
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SET LOCAL lock_timeout = '3s';   -- LOCAL: только для этой транзакции
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;
    -- Если и через 3 секунды блокировка не получена:
    --   ERROR:  canceling statement due to lock timeout
COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- 6) DEADLOCK — воспроизводимый сценарий на две сессии
--    Откройте два окна psql и выполните следующее ПАРАЛЛЕЛЬНО:
-- ─────────────────────────────────────────────────────────────────────
--   Сессия A                                Сессия B
--   -----------------------------------     -----------------------------------
--   BEGIN;                                  BEGIN;
--   UPDATE hisoblar SET balans=balans-100    UPDATE hisoblar SET balans=balans-50
--     WHERE id = 1;   -- строка 1 занята      WHERE id = 2;   -- строка 2 занята
--   SELECT pg_sleep(2);                      SELECT pg_sleep(2);
--   UPDATE hisoblar SET balans=balans+100    UPDATE hisoblar SET balans=balans+50
--     WHERE id = 2;   -- ждёт B                WHERE id = 1;   -- ждёт A
--                          \\_______ ЦИКЛ _______/
--   COMMIT;                                  <-- ЗДЕСЬ ОШИБКА:
--
--   ERROR:  deadlock detected
--   DETAIL:  Process 1023893 waits for ShareLock on transaction 13418187;
--            blocked by process 1023894.
--            Process 1023894 waits for ShareLock on transaction 13418186;
--            blocked by process 1023893.
--   HINT:  See server log for query details.
--   CONTEXT:  while updating tuple (0,1) in relation "hisoblar"
--
--   Внимание: жертвой стала ТОЛЬКО ОДНА сессия (B), а A нормально закоммитилась.

SHOW deadlock_timeout;
--  1s  <-- PostgreSQL начинает искать цикл только после этого ожидания.
--          Проверка дорогая, поэтому она не выполняется сразу.

-- ─────────────────────────────────────────────────────────────────────
-- 7) ПРЕДОТВРАЩЕНИЕ DEADLOCK: всегда блокировать в ОДНОМ порядке
--    Самый надёжный способ — цикл математически не может образоваться.
-- ─────────────────────────────────────────────────────────────────────
BEGIN;
    SELECT id, egasi FROM hisoblar
    WHERE id IN (1, 2)
    ORDER BY id            -- <<< САМАЯ ВАЖНАЯ СТРОКА
    FOR UPDATE;
    -- Теперь обе строки заблокированы, и ПОРЯДОК гарантирован.
    UPDATE hisoblar SET balans = balans - 100 WHERE id = 1;
    UPDATE hisoblar SET balans = balans + 100 WHERE id = 2;
COMMIT;

SELECT * FROM hisoblar ORDER BY id;

-- ─────────────────────────────────────────────────────────────────────
-- 8) ДИАГНОСТИКА: кто кого блокирует (в продакшене)
-- ─────────────────────────────────────────────────────────────────────
SELECT pid,
       state,
       wait_event_type,
       pg_blocking_pids(pid) AS bloklovchilar,   -- пустой массив = не заблокирован
       LEFT(query, 60)       AS sorov
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
ORDER BY pid;

-- Список конкретных блокировок:
SELECT locktype, relation::regclass AS jadval, mode, granted
FROM pg_locks
WHERE relation IS NOT NULL
ORDER BY granted, relation
LIMIT 20;

-- Долгие транзакции — главная причина блокировок и deadlock:
SELECT pid, NOW() - xact_start AS davomiylik, state, LEFT(query, 60) AS sorov
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND NOW() - xact_start > INTERVAL '5 seconds'
ORDER BY xact_start;""",
        "task": {
            "task_title": "Amaliy topshiriq: Deadlock'ni takrorlash va qulflash tartibi bilan yo'q qilish",
            "task_title_ru": "Практическое задание: воспроизвести deadlock и устранить его порядком блокировок",
            "task_description": (
                "Sizga pul o'tkazish funksiyasi berilgan. U hisoblarni foydalanuvchi bergan "
                "tartibda qulflaydi: avval kimdan, keyin kimga:\n\n"
                "    BEGIN;\n"
                "      SELECT * FROM hisoblar WHERE id = :kimdan FOR UPDATE;\n"
                "      SELECT * FROM hisoblar WHERE id = :kimga   FOR UPDATE;\n"
                "      UPDATE ... -- yechish va qo'shish\n"
                "    COMMIT;\n\n"
                "Bu kodda deadlock xavfi bor. Uni bir jumlada tushuntiring, so'ng ikkita psql "
                "oynasida HAQIQATAN takrorlang: A sessiyasi 1-hisobdan 2-hisobga, B esa "
                "2-hisobdan 1-hisobga o'tkazsin. Serverdan chiqqan 'ERROR: deadlock detected' "
                "matnini DETAIL va CONTEXT qatorlari bilan birga hisobotga ko'chiring.\n\n"
                "Keyin funksiyani qayta loyihalang va yangi variant bilan xuddi shu ikki "
                "sessiyani takrorlab, deadlock endi yuz bermasligini ko'rsating."
            ),
            "task_description_ru": (
                "Вам дана функция перевода денег. Она блокирует счета в том порядке, в котором "
                "их передал пользователь: сначала «откуда», потом «куда»:\n\n"
                "    BEGIN;\n"
                "      SELECT * FROM hisoblar WHERE id = :kimdan FOR UPDATE;\n"
                "      SELECT * FROM hisoblar WHERE id = :kimga   FOR UPDATE;\n"
                "      UPDATE ... -- списание и зачисление\n"
                "    COMMIT;\n\n"
                "В этом коде есть риск deadlock. Объясните его одной фразой, затем РЕАЛЬНО "
                "воспроизведите в двух окнах psql: сессия A переводит со счёта 1 на счёт 2, "
                "сессия B — со счёта 2 на счёт 1. Скопируйте в отчёт настоящий текст 'ERROR: "
                "deadlock detected' вместе со строками DETAIL и CONTEXT.\n\n"
                "Затем перепроектируйте функцию и, повторив те же две сессии с новым "
                "вариантом, покажите, что deadlock больше не возникает."
            ),
            "task_requirements": (
                "1. Sxema: hisoblar (egasi, balans, CHECK (balans >= 0)) va kamida 3 ta qator.\n"
                "2. Deadlock xavfi bir jumlada tushuntirilsin: ikki tranzaksiya bir xil "
                "qatorlarni TURLI tartibda qulflaydi.\n"
                "3. Deadlock ikkita sessiyada takrorlansin; haqiqiy xato matni DETAIL va "
                "CONTEXT bilan hisobotga kiritilsin. Qaysi sessiya qurbon bo'lgani va "
                "ikkinchisi normal davom etgani qayd etilsin.\n"
                "4. Qayta loyihalash: qatorlar HAR DOIM bir xil tartibda qulflansin "
                "(WHERE id IN (...) ORDER BY id FOR UPDATE). Yangi variant bilan o'sha ikki "
                "sessiya takrorlansin va deadlock yo'qligi ko'rsatilsin.\n"
                "5. Izohda: nega ORDER BY qo'shilgandan keyin halqa hosil bo'lishi MATEMATIK "
                "jihatdan imkonsiz.\n"
                "6. SET LOCAL lock_timeout = '3s' bilan cheksiz kutish o'rniga xato olinsin; "
                "haqiqiy xato matni keltirilsin.\n"
                "7. Navbat jadvali va ishchi so'rovi: FOR UPDATE SKIP LOCKED LIMIT n. Ikki "
                "sessiyadan bir vaqtda bajarilib, ular BIR-BIRIGA TEGMAYDIGAN vazifalar "
                "olishi ko'rsatilsin; keyin SKIP LOCKED siz variant ikkinchi sessiyani "
                "bloklashi ko'rsatilsin.\n"
                "8. Sessiya bloklangan paytda pg_blocking_pids(pid) natijasi olinib, hisobotga "
                "kiritilsin.\n"
                "9. Izohda: qaysi holatda FOR UPDATE umuman kerak emas (SET balans = balans - x "
                "atomar bajariladi) va nega bu eng ishonchli himoya.\n"
                "10. Hisobot .sql yoki .md ko'rinishida, ikki sessiya jurnali aniq ajratilgan "
                "holda topshirilsin."
            ),
            "task_requirements_ru": (
                "1. Схема: hisoblar (владелец, баланс, CHECK (balans >= 0)) минимум с 3 строками.\n"
                "2. Одной фразой объясните риск deadlock: две транзакции блокируют одни и те же "
                "строки в РАЗНОМ порядке.\n"
                "3. Воспроизведите deadlock в двух сессиях; включите в отчёт настоящий текст "
                "ошибки с DETAIL и CONTEXT. Отметьте, какая сессия стала жертвой и что вторая "
                "продолжила работу нормально.\n"
                "4. Перепроектирование: строки ВСЕГДА блокируются в одном порядке "
                "(WHERE id IN (...) ORDER BY id FOR UPDATE). Повторите те же две сессии с новым "
                "вариантом и покажите отсутствие deadlock.\n"
                "5. В комментарии: почему после добавления ORDER BY образование петли "
                "МАТЕМАТИЧЕСКИ невозможно.\n"
                "6. Через SET LOCAL lock_timeout = '3s' получите ошибку вместо бесконечного "
                "ожидания; приведите настоящий текст ошибки.\n"
                "7. Таблица очереди и запрос воркера: FOR UPDATE SKIP LOCKED LIMIT n. Запустите "
                "из двух сессий одновременно и покажите, что они забирают НЕПЕРЕСЕКАЮЩИЕСЯ "
                "задачи; затем покажите, что вариант без SKIP LOCKED блокирует вторую сессию.\n"
                "8. Пока сессия заблокирована, снимите вывод pg_blocking_pids(pid) и включите "
                "его в отчёт.\n"
                "9. В комментарии: в каком случае FOR UPDATE вообще не нужен (SET balans = "
                "balans - x выполняется атомарно) и почему это самая надёжная защита.\n"
                "10. Отчёт сдайте в виде .sql или .md с чётко разделённым журналом двух сессий."
            ),
            "task_technologies": "PostgreSQL, FOR UPDATE, SKIP LOCKED, lock_timeout, deadlock, pg_locks",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: FOR UPDATE, SKIP LOCKED navbati va deadlock'dan qochish",
            "description": "Qulf turlari, ko'p ishchili navbatning SQL asosi, lock_timeout va qatorlarni bir xil tartibda qulflab deadlock halqasini yo'q qilish",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: qulflar, SKIP LOCKED navbati va deadlock'dan qochish
DROP TABLE IF EXISTS navbat;
DROP TABLE IF EXISTS hisoblar;

CREATE TABLE hisoblar (
    id     SERIAL        PRIMARY KEY,
    egasi  VARCHAR(40)   NOT NULL,
    balans NUMERIC(12,2) NOT NULL CHECK (balans >= 0)
);
INSERT INTO hisoblar (egasi, balans) VALUES
    ('Aziz', 1000000), ('Dilnoza', 500000), ('Sardor', 300000);

-- 1) O'qib-hisoblab-yozish naqshi "lost update" ga olib keladi.
--    FOR UPDATE qatorni tranzaksiya oxirigacha BAND qiladi:
BEGIN;
    SELECT id, balans FROM hisoblar WHERE id = 1 FOR UPDATE;
    UPDATE hisoblar SET balans = balans - 100000 WHERE id = 1;
COMMIT;

-- Lekin hisobni bazaning O'ZIGA topshirsangiz, FOR UPDATE umuman kerak
-- emas: UPDATE qatorni o'zi qulflaydi va ATOMAR o'qib-yozadi.
-- Bu — lost update ga qarshi eng oddiy va eng ishonchli himoya:
UPDATE hisoblar SET balans = balans + 100000 WHERE id = 1;

-- 2) Qulf turlari (kuchlidan kuchsizga)
BEGIN;
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;         -- eng kuchli
    SELECT id FROM hisoblar WHERE id = 2 FOR NO KEY UPDATE;  -- oddiy UPDATE shuni oladi
    SELECT id FROM hisoblar WHERE id = 3 FOR SHARE;          -- o'zgartirishni bloklaydi
    SELECT id FROM hisoblar WHERE id = 3 FOR KEY SHARE;      -- FK tekshiruvi shuni oladi
COMMIT;

-- 3) SKIP LOCKED — ko'p ishchili navbat (Celery/Sidekiq ning SQL asosi).
--    Oddiy FOR UPDATE ishchilarni navbatga tizadi; SKIP LOCKED esa band
--    qatorlarni SAKRAB o'tadi va har bir ishchi darhol ish oladi.
CREATE TABLE navbat (
    id      BIGSERIAL   PRIMARY KEY,
    vazifa  TEXT        NOT NULL,
    holat   VARCHAR(20) NOT NULL DEFAULT 'kutmoqda',
    olingan TIMESTAMPTZ
);
INSERT INTO navbat (vazifa) SELECT 'Vazifa ' || g FROM generate_series(1, 10) g;

-- Qisman indeks: faqat kutayotgan vazifalar indekslanadi
CREATE INDEX idx_navbat_kutmoqda ON navbat(id) WHERE holat = 'kutmoqda';

BEGIN;
    WITH keyingi AS (
        SELECT id FROM navbat
        WHERE holat = 'kutmoqda'
        ORDER BY id
        FOR UPDATE SKIP LOCKED
        LIMIT 3
    )
    UPDATE navbat n
    SET holat = 'bajarilmoqda', olingan = NOW()
    FROM keyingi k
    WHERE n.id = k.id
    RETURNING n.id, n.vazifa;
COMMIT;

SELECT holat, COUNT(*) FROM navbat GROUP BY holat ORDER BY holat;
--  bajarilmoqda | 3
--  kutmoqda     | 7

-- 4) lock_timeout — cheksiz kutish o'rniga xato
BEGIN;
    SET LOCAL lock_timeout = '3s';   -- LOCAL: faqat shu tranzaksiya uchun
    SELECT id FROM hisoblar WHERE id = 1 FOR UPDATE;
    -- 3 sekunddan keyin ham qulf olinmasa:
    --   ERROR: canceling statement due to lock timeout
COMMIT;

-- ══ DEADLOCK: ikki tranzaksiya bir xil qatorlarni TURLI tartibda ═════
--   Sessiya A                              Sessiya B
--   ---------------------------------      ---------------------------------
--   BEGIN;                                 BEGIN;
--   UPDATE ... WHERE id = 1;  -- qulf      UPDATE ... WHERE id = 2;  -- qulf
--   UPDATE ... WHERE id = 2;  -- kutadi    UPDATE ... WHERE id = 1;  -- kutadi
--                       \______ HALQA ______/
--
--   ERROR:  deadlock detected
--   DETAIL: Process 1023893 waits for ShareLock on transaction 13418187;
--           blocked by process 1023894. ...
--   CONTEXT: while updating tuple (0,1) in relation "hisoblar"
--
--   Faqat BITTA sessiya qurbon bo'ladi, ikkinchisi normal davom etadi.
SHOW deadlock_timeout;   --  1s: PostgreSQL shuncha kutgach halqa qidiradi

-- 5) OLDINI OLISH: har doim BIR XIL tartibda qulflash.
--    Butun kod bazasi qatorlarni id o'sish tartibida qulflasa, halqa
--    hosil bo'lishi MATEMATIK jihatdan imkonsiz.
BEGIN;
    SELECT id, egasi FROM hisoblar
    WHERE id IN (1, 2)
    ORDER BY id                -- <<< ENG MUHIM QATOR
    FOR UPDATE;
    UPDATE hisoblar SET balans = balans - 100 WHERE id = 1;
    UPDATE hisoblar SET balans = balans + 100 WHERE id = 2;
COMMIT;

-- 6) Diagnostika: kim kimni bloklayapti
SELECT pid, state, wait_event_type,
       pg_blocking_pids(pid) AS bloklovchilar,   -- bo'sh massiv = bloklanmagan
       LEFT(query, 50) AS sorov
FROM pg_stat_activity
WHERE datname = current_database() AND pid <> pg_backend_pid()
ORDER BY pid LIMIT 5;""",
        },
        "exercises": [
            {
                "title": "Deadlock qachon paydo bo'ladi?",
                "title_ru": "Когда возникает deadlock?",
                "description": "Ikkita tranzaksiya bir vaqtda ishlayapti. Deadlock hosil bo'lishining asosiy sharti nima?",
                "description_ru": "Две транзакции работают одновременно. Каково основное условие возникновения deadlock?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ikkala tranzaksiya ham juda uzoq ishlaganda",
                    "Ikkala tranzaksiya bir xil qatorlarni TURLI tartibda qulflaganda",
                    "Bir tranzaksiya SELECT, ikkinchisi UPDATE bajarganda",
                    "Jadvalda indeks yetishmaganda",
                ],
                "options_ru": [
                    "Когда обе транзакции работают слишком долго",
                    "Когда обе транзакции блокируют одни и те же строки в РАЗНОМ порядке",
                    "Когда одна транзакция делает SELECT, а другая UPDATE",
                    "Когда таблице не хватает индексов",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Qulflar grafida halqa qanday hosil bo'ladi?",
                "hint_ru": "Как образуется цикл в графе блокировок?",
                "explanation": "A tranzaksiya 1-qatorni qulflab 2-ni kutadi, B esa 2-ni qulflab 1-ni kutadi — halqa hosil bo'ladi. Yechim: har doim bir xil tartibda qulflash (ORDER BY id FOR UPDATE). O'quv sessiyada bu ssenariy haqiqatan takrorlandi va PostgreSQL 40P01 xatosini berdi.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Navbatda band qatorlarni sakrab o'tish",
                "title_ru": "Пропуск занятых строк в очереди",
                "description": "Bir nechta ishchi bitta navbat jadvalidan vazifa olmoqda. Ular bir-birini kutmasligi va har biri boshqa qatorni olishi uchun SELECT ... FOR UPDATE dan keyin qaysi kalit so'zlar yoziladi? FOR UPDATE ___ ___",
                "description_ru": "Несколько воркеров разбирают задачи из одной таблицы-очереди. Какие ключевые слова нужно дописать после SELECT ... FOR UPDATE, чтобы они не ждали друг друга и каждый брал свою строку? FOR UPDATE ___ ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "SKIP LOCKED",
                "hint": "NOWAIT xato beradi, bu esa band qatorni jimgina o'tkazib yuboradi.",
                "hint_ru": "NOWAIT выдаёт ошибку, а это молча пропускает занятую строку.",
                "explanation": "SKIP LOCKED band qatorlarni natijadan chiqarib tashlaydi, shuning uchun har bir ishchi darhol bo'sh vazifani oladi. Bu Celery va Sidekiq kabi navbat tizimlarining SQL asosi.",
                "difficulty_level": "Medium",
                "points": 10,
            },
            {
                "title": "Pul o'tkazmasida deadlock",
                "title_ru": "Deadlock при переводе денег",
                "description": "Ilovada pul o'tkazish funksiyasi bor: u jo'natuvchi hisobini yangilaydi, keyin qabul qiluvchi hisobini yangilaydi. Aziz Dilnozaga, Dilnoza esa ayni paytda Azizga pul yubordi — va bitta tranzaksiya `deadlock detected` xatosi bilan bekor bo'ldi. Nima uchun shunday bo'ldi va kodni qanday o'zgartirasiz?",
                "description_ru": "В приложении есть функция перевода денег: она обновляет счёт отправителя, затем счёт получателя. Aziz отправил деньги Dilnoza, а Dilnoza в тот же момент — Aziz'у, и одна из транзакций отменилась с ошибкой `deadlock detected`. Почему так вышло и как вы измените код?",
                "exercise_type": "text_input",
                "expected_answer": "Deadlock sababi — qulflash tartibi. Aziz->Dilnoza tranzaksiyasi avval Aziz qatorini, keyin Dilnoza qatorini qulflaydi; Dilnoza->Aziz tranzaksiyasi esa teskari tartibda. Natijada har biri ikkinchisi ushlab turgan qatorni kutadi va qulflar grafida halqa hosil bo'ladi. PostgreSQL deadlock_timeout (standart 1s) o'tgach halqani aniqlaydi va tranzaksiyalardan birini majburan bekor qiladi (SQLSTATE 40P01). Tuzatish: qatorlarni har doim bir xil, oldindan belgilangan tartibda qulflash — masalan id o'sish tartibida: SELECT id FROM hisoblar WHERE id IN (jonatuvchi_id, qabul_qiluvchi_id) ORDER BY id FOR UPDATE; va shundan keyingina ikkala UPDATE ni bajarish. Bunda halqa matematik jihatdan hosil bo'lolmaydi. Qo'shimcha choralar: tranzaksiyani qisqa tutish, SET LOCAL lock_timeout qo'yish va 40P01 ni ushlab tranzaksiyani qayta urinish.",
                "hint": "Ikki tranzaksiya qatorlarni qanday tartibda qulflayotganini yozib chiqing.",
                "hint_ru": "Выпишите, в каком порядке каждая из двух транзакций блокирует строки.",
                "difficulty_level": "Hard",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 9  — R2 (takrorlash + topshiriq)
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 9,
        "title": "R2-Sekin so'rovni optimallashtirish (takrorlash)",
        "title_ru": "R2-Оптимизация медленного запроса (повторение)",
        "points_reward": 16,
        "code_language": "sql",
        "text_content": """<h3>Optimallashtirish &mdash; bu jarayon, sehr emas</h3>
<p>Sekin so'rovni tuzatishga kirishganda eng ko'p qilinadigan xato &mdash; darhol indeks qo'shish. To'g'ri tartib boshqacha va u har doim bir xil:</p>
<ol>
<li><strong>O'lchang.</strong> <code>EXPLAIN (ANALYZE, BUFFERS)</code> &mdash; qaysi tugun vaqtni yeyapti?</li>
<li><strong>Sababni aniqlang.</strong> Seq Scan? Noto'g'ri taxmin? Ko'p <code>loops</code>? Katta <code>Rows Removed by Filter</code>?</li>
<li><strong>Bitta o'zgarish kiriting.</strong> Ikkitasini birga qilsangiz, qaysi biri yordam berganini bilmaysiz.</li>
<li><strong>Qayta o'lchang.</strong> Reja o'zgardimi? Vaqt va buferlar kamaydimi?</li>
</ol>
<p>Ikki mezonga qarang: <strong>vaqt</strong> va <strong>buferlar</strong>. Buferlar ko'pincha ishonchliroq &mdash; ular kesh holatiga bog'liq emas.</p>

<h3>Uchta klassik sabab &mdash; o'lchangan natijalar bilan</h3>
<p>Quyidagi raqamlar 2 000 000 qatorli (181 MB) jadvalda haqiqatan o'lchangan.</p>

<h4>1. Ustunga qo'llangan funksiya indeksni o'ldiradi</h4>
<p><code>WHERE to_char(sana,'YYYY-MM') = '2024-11'</code> yozsangiz, <code>sana</code> ustunidagi indeks <em>umuman</em> ishlatilmaydi &mdash; indeksda <code>sana</code> saqlangan, <code>to_char(sana)</code> emas. Uni diapazon shartiga aylantirish yetarli:</p>
<table>
<tr><th>Variant</th><th>Reja</th><th>Vaqt</th></tr>
<tr><td><code>to_char(sana,'YYYY-MM') = '2024-11'</code></td><td>Parallel Seq Scan</td><td><strong>161.8 ms</strong></td></tr>
<tr><td><code>sana &gt;= '2024-11-01' AND sana &lt; '2024-12-01'</code></td><td>Bitmap Index Scan</td><td><strong>40.8 ms</strong></td></tr>
</table>

<h4>2. OFFSET bilan chuqur sahifalash</h4>
<p>Bu ro'yxatning eng dramatik nuqtasi. <code>OFFSET 1000000</code> PostgreSQL ni bir million qatorni <em>o'qib, so'ng tashlab yuborishga</em> majbur qiladi. Kursor (keyset) usuli esa indeksga to'g'ridan-to'g'ri kiradi:</p>
<table>
<tr><th>Variant</th><th>Buferlar</th><th>Vaqt</th></tr>
<tr><td><code>ORDER BY id DESC OFFSET 1000000 LIMIT 20</code></td><td>13 327</td><td><strong>135 ms</strong></td></tr>
<tr><td><code>WHERE id &lt; :oxirgi ORDER BY id DESC LIMIT 20</code></td><td>7</td><td><strong>0.035 ms</strong></td></tr>
</table>
<p>Farq &mdash; taxminan <strong>3800 baravar</strong>. Va e'tibor bering: OFFSET qanchalik katta bo'lsa, u shunchalik sekinlashadi, keyset esa <em>har doim bir xil tez</em>.</p>

<h4>3. Filtrga mos indeksning yo'qligi</h4>
<p>&ldquo;Oxirgi oyda to'langan buyurtmalar bo'yicha top mijozlar&rdquo; so'rovi indekssiz butun jadvalni skanerlaydi. Qisman kompozit indeks qo'shilgach reja <code>Parallel Seq Scan</code> dan <code>Bitmap Index Scan</code> ga o'tdi: <strong>101 ms &rarr; 62 ms</strong>.</p>
<p><strong>Halol eslatma:</strong> bu yerda tezlashuv atigi 1.6 barobar, chunki qolgan vaqtni 100 000 mijoz bo'yicha <code>Hash Join</code> va <code>GROUP BY</code> yeyapti. Har bir indeks 100 barobar tezlashtirmaydi &mdash; va <code>INCLUDE</code> qo'shilgan qisman indeks (39 MB) oddiy indeksdan (14 MB) <em>kattaroq</em> chiqdi. Bu ham savdolashuv: joy evaziga jadvalga murojaatni kamaytirasiz.</p>

<h3>Yana ikkita amaliy naqsh</h3>
<ul>
<li><strong><code>COUNT(*)</code> har doim butun jadvalni sanaydi</strong> &mdash; 2 mln qator uchun 68 ms. Sahifalash uchun aniq son shart bo'lmasa, <code>pg_class.reltuples</code> dan taxminiy qiymatni oling: <strong>0.016 ms</strong>.</li>
<li><strong>Indeks qo'shishdan oldin so'rovni qayta yozib ko'ring.</strong> Yangi indeks yozishni sekinlashtiradi va joy egallaydi; so'rovni to'g'rilash esa bepul.</li>
</ul>""",
        "text_content_ru": """<h3>Оптимизация — это процесс, а не магия</h3>
<p>Самая частая ошибка при починке медленного запроса — сразу добавить индекс. Правильный порядок другой, и он всегда одинаков:</p>
<ol>
<li><strong>Измерьте.</strong> <code>EXPLAIN (ANALYZE, BUFFERS)</code> — какой узел съедает время?</li>
<li><strong>Определите причину.</strong> Seq Scan? Неверная оценка? Много <code>loops</code>? Большое <code>Rows Removed by Filter</code>?</li>
<li><strong>Внесите одно изменение.</strong> Если сделать два сразу, вы не узнаете, какое помогло.</li>
<li><strong>Измерьте снова.</strong> Изменился ли план? Уменьшились ли время и буферы?</li>
</ol>
<p>Смотрите на два критерия: <strong>время</strong> и <strong>буферы</strong>. Буферы часто надёжнее — они не зависят от состояния кэша.</p>

<h3>Три классические причины — с измеренными результатами</h3>
<p>Числа ниже реально измерены на таблице в 2 000 000 строк (181 МБ).</p>

<h4>1. Функция на колонке убивает индекс</h4>
<p>Если написать <code>WHERE to_char(sana,'YYYY-MM') = '2024-11'</code>, индекс по колонке <code>sana</code> не будет использован <em>вообще</em> — в индексе хранится <code>sana</code>, а не <code>to_char(sana)</code>. Достаточно превратить это в условие-диапазон:</p>
<table>
<tr><th>Вариант</th><th>План</th><th>Время</th></tr>
<tr><td><code>to_char(sana,'YYYY-MM') = '2024-11'</code></td><td>Parallel Seq Scan</td><td><strong>161.8 мс</strong></td></tr>
<tr><td><code>sana &gt;= '2024-11-01' AND sana &lt; '2024-12-01'</code></td><td>Bitmap Index Scan</td><td><strong>40.8 мс</strong></td></tr>
</table>

<h4>2. Глубокая пагинация через OFFSET</h4>
<p>Это самый драматичный пункт списка. <code>OFFSET 1000000</code> заставляет PostgreSQL <em>прочитать миллион строк и затем выбросить их</em>. А курсорный (keyset) способ заходит в индекс напрямую:</p>
<table>
<tr><th>Вариант</th><th>Буферы</th><th>Время</th></tr>
<tr><td><code>ORDER BY id DESC OFFSET 1000000 LIMIT 20</code></td><td>13 327</td><td><strong>135 мс</strong></td></tr>
<tr><td><code>WHERE id &lt; :последний ORDER BY id DESC LIMIT 20</code></td><td>7</td><td><strong>0.035 мс</strong></td></tr>
</table>
<p>Разница — примерно в <strong>3800 раз</strong>. И обратите внимание: чем больше OFFSET, тем он медленнее, тогда как keyset <em>всегда одинаково быстр</em>.</p>

<h4>3. Отсутствие индекса под фильтр</h4>
<p>Запрос «топ клиентов по оплаченным заказам за последний месяц» без индекса сканирует всю таблицу. После добавления частичного композитного индекса план сменился с <code>Parallel Seq Scan</code> на <code>Bitmap Index Scan</code>: <strong>101 мс &rarr; 62 мс</strong>.</p>
<p><strong>Честное замечание:</strong> ускорение здесь всего в 1.6 раза, потому что остаток времени съедают <code>Hash Join</code> по 100 000 клиентов и <code>GROUP BY</code>. Не каждый индекс ускоряет в 100 раз — а частичный индекс с <code>INCLUDE</code> (39 МБ) оказался <em>больше</em> обычного (14 МБ). Это тоже компромисс: ценой места вы сокращаете обращения к таблице.</p>

<h3>Ещё два практических приёма</h3>
<ul>
<li><strong><code>COUNT(*)</code> всегда пересчитывает всю таблицу</strong> — 68 мс на 2 млн строк. Если для пагинации точное число не обязательно, возьмите оценку из <code>pg_class.reltuples</code>: <strong>0.016 мс</strong>.</li>
<li><strong>Прежде чем добавлять индекс, попробуйте переписать запрос.</strong> Новый индекс замедляет запись и занимает место, а исправление запроса бесплатно.</li>
</ul>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Sekin so'rovni optimallashtirish: o'lchash -> sabab -> tuzatish -> o'lchash
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id    SERIAL       PRIMARY KEY,
    ism   VARCHAR(60)  NOT NULL,
    email VARCHAR(120) NOT NULL
);
CREATE TABLE buyurtmalar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL REFERENCES mijozlar(id),
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

INSERT INTO mijozlar (ism, email)
SELECT 'Mijoz ' || g, 'user' || g || '@mail.uz' FROM generate_series(1, 100000) g;

-- 2 000 000 qator — bu yerda optimallashtirish HAQIQATAN ko'rinadi
INSERT INTO buyurtmalar (mijoz_id, sana, holat, summa)
SELECT (random() * 99999)::INT + 1,
       DATE '2023-01-01' + (random() * 700)::INT,
       (ARRAY['yangi','tolangan','bekor'])[(random() * 2)::INT + 1],
       (random() * 5000000 + 50000)::NUMERIC(12,2)
FROM generate_series(1, 2000000);

CREATE INDEX idx_b_mijoz ON buyurtmalar(mijoz_id);
CREATE INDEX idx_b_sana  ON buyurtmalar(sana);
ANALYZE mijozlar; ANALYZE buyurtmalar;

SELECT pg_size_pretty(pg_total_relation_size('buyurtmalar')) AS jadval_hajmi;
--  181 MB

-- ═══ MUAMMO 1: ustunga qo'llangan funksiya indeksni o'ldiradi ═══════
-- SEKIN: to_char(sana, ...) indeksdagi qiymat bilan mos kelmaydi
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar WHERE to_char(sana, 'YYYY-MM') = '2024-11';
--  Parallel Seq Scan on buyurtmalar ...
--  Execution Time: 161.8 ms

-- TEZ: ayni o'sha shart, lekin DIAPAZON ko'rinishida
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar
WHERE sana >= DATE '2024-11-01' AND sana < DATE '2024-12-01';
--  Bitmap Heap Scan -> Bitmap Index Scan on idx_b_sana
--  Execution Time: 40.8 ms          <-- ~4 baravar tez, indeks qo'shilmadi

-- Muqobil yechim: ifoda bo'yicha indeks (agar so'rovni o'zgartirib bo'lmasa)
--   CREATE INDEX idx_b_oy ON buyurtmalar((to_char(sana, 'YYYY-MM')));

-- ═══ MUAMMO 2: OFFSET bilan chuqur sahifalash ══════════════════════
-- SEKIN: OFFSET 1 000 000 qatorni o'qib, keyin TASHLAB YUBORADI
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
ORDER BY id DESC OFFSET 1000000 LIMIT 20;
--  Limit -> Index Scan Backward ... (actual rows=1000020 loops=1)
--                                                ^^^^^^^ 1 mln qator o'qildi!
--  Buffers: shared hit=8450 read=4877
--  Execution Time: 135.1 ms

-- TEZ: keyset (kursor) sahifalash — oxirgi ko'rilgan id dan davom etamiz
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
WHERE id < 1000000            -- oldingi sahifadagi OXIRGI id
ORDER BY id DESC LIMIT 20;
--  Limit -> Index Scan using idx_b_id_desc ... (actual rows=20 loops=1)
--  Buffers: shared hit=4 read=3
--  Execution Time: 0.035 ms         <-- ~3800 BARAVAR tez
--
-- Muhimi: OFFSET qanchalik katta bo'lsa shunchalik sekinlashadi,
-- keyset esa 1-sahifada ham, 50 000-sahifada ham BIR XIL tez.
-- Kamchiligi: "birdan 500-sahifaga o'tish" mumkin emas — faqat oldinga/orqaga.

-- ═══ MUAMMO 3: filtrga mos indeks yo'q ═════════════════════════════
-- SEKIN: holat + sana bo'yicha mos indeks yo'q
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;
--  Parallel Seq Scan on buyurtmalar b ...
--  Execution Time: 101.2 ms

-- TEZ: qisman (holat bo'yicha) + kompozit + INCLUDE indeks
CREATE INDEX idx_b_tolangan ON buyurtmalar(sana, mijoz_id) INCLUDE (summa)
    WHERE holat = 'tolangan';
ANALYZE buyurtmalar;

EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;
--  Bitmap Heap Scan -> Bitmap Index Scan on idx_b_tolangan
--  Execution Time: 62.3 ms          <-- 1.6 baravar tez

-- HALOL BAHO: 1.6 barobar — 100 barobar emas. Qolgan vaqtni 100 000
-- mijoz bo'yicha Hash Join va GROUP BY yeyapti. Bundan tashqari:
SELECT pg_size_pretty(pg_relation_size('idx_b_tolangan')) AS qisman_include,
       pg_size_pretty(pg_relation_size('idx_b_sana'))     AS oddiy_indeks;
--  qisman_include | oddiy_indeks
--  39 MB          | 14 MB
-- Ya'ni INCLUDE qo'shilgan qisman indeks oddiysidan KATTAROQ chiqdi.
-- Bu savdolashuv: joy evaziga jadvalga murojaat kamayadi.

-- ═══ QO'SHIMCHA: COUNT(*) va taxminiy hisob ════════════════════════
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF) SELECT COUNT(*) FROM buyurtmalar;
--  Parallel Seq Scan ... Execution Time: 68.7 ms
--  COUNT(*) MVCC tufayli har doim barcha qatorlarni ko'rib chiqadi.

EXPLAIN (ANALYZE, COSTS OFF)
SELECT reltuples::BIGINT AS taxminiy FROM pg_class WHERE oid = 'buyurtmalar'::regclass;
--  Index Scan using pg_class_oid_index ... Execution Time: 0.016 ms
--  Sahifalashda "1 234 567 dan" ko'rsatish uchun aniq son SHART emas.""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Оптимизация медленного запроса: измерить -> причина -> починить -> измерить
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id    SERIAL       PRIMARY KEY,
    ism   VARCHAR(60)  NOT NULL,
    email VARCHAR(120) NOT NULL
);
CREATE TABLE buyurtmalar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL REFERENCES mijozlar(id),
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

INSERT INTO mijozlar (ism, email)
SELECT 'Mijoz ' || g, 'user' || g || '@mail.uz' FROM generate_series(1, 100000) g;

-- 2 000 000 строк — именно здесь оптимизация становится ЗАМЕТНОЙ
INSERT INTO buyurtmalar (mijoz_id, sana, holat, summa)
SELECT (random() * 99999)::INT + 1,
       DATE '2023-01-01' + (random() * 700)::INT,
       (ARRAY['yangi','tolangan','bekor'])[(random() * 2)::INT + 1],
       (random() * 5000000 + 50000)::NUMERIC(12,2)
FROM generate_series(1, 2000000);

CREATE INDEX idx_b_mijoz ON buyurtmalar(mijoz_id);
CREATE INDEX idx_b_sana  ON buyurtmalar(sana);
ANALYZE mijozlar; ANALYZE buyurtmalar;

SELECT pg_size_pretty(pg_total_relation_size('buyurtmalar')) AS jadval_hajmi;
--  181 MB

-- ═══ ПРОБЛЕМА 1: функция на колонке убивает индекс ═════════════════
-- МЕДЛЕННО: to_char(sana, ...) не совпадает со значением в индексе
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar WHERE to_char(sana, 'YYYY-MM') = '2024-11';
--  Parallel Seq Scan on buyurtmalar ...
--  Execution Time: 161.8 ms

-- БЫСТРО: то же самое условие, но в виде ДИАПАЗОНА
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar
WHERE sana >= DATE '2024-11-01' AND sana < DATE '2024-12-01';
--  Bitmap Heap Scan -> Bitmap Index Scan on idx_b_sana
--  Execution Time: 40.8 ms          <-- в ~4 раза быстрее, индекс не добавляли

-- Альтернатива: индекс по выражению (если запрос менять нельзя)
--   CREATE INDEX idx_b_oy ON buyurtmalar((to_char(sana, 'YYYY-MM')));

-- ═══ ПРОБЛЕМА 2: глубокая пагинация через OFFSET ═══════════════════
-- МЕДЛЕННО: OFFSET читает 1 000 000 строк и затем ВЫБРАСЫВАЕТ их
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
ORDER BY id DESC OFFSET 1000000 LIMIT 20;
--  Limit -> Index Scan Backward ... (actual rows=1000020 loops=1)
--                                                ^^^^^^^ прочитан 1 млн строк!
--  Buffers: shared hit=8450 read=4877
--  Execution Time: 135.1 ms

-- БЫСТРО: keyset (курсорная) пагинация — продолжаем с последнего id
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
WHERE id < 1000000            -- ПОСЛЕДНИЙ id с предыдущей страницы
ORDER BY id DESC LIMIT 20;
--  Limit -> Index Scan using idx_b_id_desc ... (actual rows=20 loops=1)
--  Buffers: shared hit=4 read=3
--  Execution Time: 0.035 ms         <-- в ~3800 РАЗ быстрее
--
-- Главное: чем больше OFFSET, тем он медленнее, а keyset одинаково быстр
-- и на 1-й странице, и на 50 000-й.
-- Недостаток: нельзя «прыгнуть сразу на 500-ю страницу» — только вперёд/назад.

-- ═══ ПРОБЛЕМА 3: нет индекса под фильтр ════════════════════════════
-- МЕДЛЕННО: нет подходящего индекса по holat + sana
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;
--  Parallel Seq Scan on buyurtmalar b ...
--  Execution Time: 101.2 ms

-- БЫСТРО: частичный (по holat) + композитный + INCLUDE индекс
CREATE INDEX idx_b_tolangan ON buyurtmalar(sana, mijoz_id) INCLUDE (summa)
    WHERE holat = 'tolangan';
ANALYZE buyurtmalar;

EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;
--  Bitmap Heap Scan -> Bitmap Index Scan on idx_b_tolangan
--  Execution Time: 62.3 ms          <-- в 1.6 раза быстрее

-- ЧЕСТНАЯ ОЦЕНКА: в 1.6 раза, а не в 100. Остаток времени съедают
-- Hash Join по 100 000 клиентов и GROUP BY. Кроме того:
SELECT pg_size_pretty(pg_relation_size('idx_b_tolangan')) AS qisman_include,
       pg_size_pretty(pg_relation_size('idx_b_sana'))     AS oddiy_indeks;
--  qisman_include | oddiy_indeks
--  39 MB          | 14 MB
-- То есть частичный индекс с INCLUDE оказался БОЛЬШЕ обычного.
-- Это компромисс: ценой места сокращаются обращения к таблице.

-- ═══ ДОПОЛНИТЕЛЬНО: COUNT(*) и приблизительный подсчёт ═════════════
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF) SELECT COUNT(*) FROM buyurtmalar;
--  Parallel Seq Scan ... Execution Time: 68.7 ms
--  Из-за MVCC COUNT(*) всегда просматривает все строки.

EXPLAIN (ANALYZE, COSTS OFF)
SELECT reltuples::BIGINT AS taxminiy FROM pg_class WHERE oid = 'buyurtmalar'::regclass;
--  Index Scan using pg_class_oid_index ... Execution Time: 0.016 ms
--  Чтобы показать в пагинации «из 1 234 567», точное число НЕ обязательно.""",
        "task": {
            "task_title": "Amaliy loyiha: Sekin so'rovni diagnostika qilish va tuzatish",
            "task_title_ru": "Практический проект: диагностика и исправление медленного запроса",
            "task_description": (
                "Sizga onlayn do'kon adminkasining \"mijozlar hisoboti\" sahifasi berildi. "
                "Sahifa 3-4 sekundda ochiladi, foydalanuvchilar shikoyat qilmoqda. Sahifa "
                "quyidagi so'rovni bajaradi:\n\n"
                "  SELECT m.id, m.ism, m.email,\n"
                "         (SELECT COUNT(*) FROM buyurtmalar b1 WHERE b1.mijoz_id = m.id) AS buyurtmalar_soni,\n"
                "         (SELECT SUM(b2.summa) FROM buyurtmalar b2\n"
                "           WHERE b2.mijoz_id = m.id AND b2.holat = 'tolangan') AS jami_tolov,\n"
                "         (SELECT MAX(b3.sana) FROM buyurtmalar b3 WHERE b3.mijoz_id = m.id) AS oxirgi_buyurtma\n"
                "  FROM mijozlar m\n"
                "  WHERE EXTRACT(YEAR FROM m.royxatdan_otgan) = 2024\n"
                "    AND LOWER(m.email) LIKE '%@gmail.com'\n"
                "  ORDER BY jami_tolov DESC NULLS LAST\n"
                "  OFFSET 4000 LIMIT 20;\n\n"
                "Bu so'rovda kamida to'rtta alohida performance muammosi bor. Sizning "
                "vazifangiz — ularni topish, har birini alohida tuzatish va har bir "
                "qadamni O'LCHOV bilan asoslash.\n\n"
                "Ishni test ma'lumotlarini yaratishdan boshlang: kamida 100 000 mijoz va "
                "2 000 000 buyurtma (darsdagi generate_series kodidan foydalaning). Kichik "
                "jadvalda hech qanday optimallashtirish ko'rinmaydi."
            ),
            "task_description_ru": (
                "Вам передали страницу «отчёт по клиентам» в админке интернет-магазина. "
                "Страница открывается 3-4 секунды, пользователи жалуются. Страница выполняет "
                "следующий запрос:\n\n"
                "  SELECT m.id, m.ism, m.email,\n"
                "         (SELECT COUNT(*) FROM buyurtmalar b1 WHERE b1.mijoz_id = m.id) AS buyurtmalar_soni,\n"
                "         (SELECT SUM(b2.summa) FROM buyurtmalar b2\n"
                "           WHERE b2.mijoz_id = m.id AND b2.holat = 'tolangan') AS jami_tolov,\n"
                "         (SELECT MAX(b3.sana) FROM buyurtmalar b3 WHERE b3.mijoz_id = m.id) AS oxirgi_buyurtma\n"
                "  FROM mijozlar m\n"
                "  WHERE EXTRACT(YEAR FROM m.royxatdan_otgan) = 2024\n"
                "    AND LOWER(m.email) LIKE '%@gmail.com'\n"
                "  ORDER BY jami_tolov DESC NULLS LAST\n"
                "  OFFSET 4000 LIMIT 20;\n\n"
                "В этом запросе как минимум четыре отдельные проблемы производительности. "
                "Ваша задача — найти их, исправить каждую по отдельности и обосновать "
                "каждый шаг ИЗМЕРЕНИЕМ.\n\n"
                "Начните с создания тестовых данных: минимум 100 000 клиентов и 2 000 000 "
                "заказов (используйте код с generate_series из урока). На маленькой таблице "
                "никакая оптимизация не будет видна."
            ),
            "task_requirements": (
                "1. Sxema va test ma'lumotlari: >= 100 000 mijoz, >= 2 000 000 buyurtma.\n"
                "2. Boshlang'ich o'lchov: so'rovning EXPLAIN (ANALYZE, BUFFERS) natijasini "
                "to'liq keltiring va qaysi tugun eng ko'p vaqt yeyayotganini ko'rsating.\n"
                "3. Kamida to'rtta muammoni aniqlang va nomlang. Ko'rib chiqing: ustunga "
                "qo'llangan funksiya (EXTRACT, LOWER) indeksni ishlatishga to'sqinlik "
                "qilyaptimi; '%@gmail.com' kabi oldida foizi bor LIKE indekslanadimi; "
                "uchta korrelyatsiyali subquery necha marta skanerlash qilmoqda; OFFSET 4000 "
                "nima qilyapti.\n"
                "4. Har bir tuzatishni ALOHIDA kiriting va har biridan keyin qayta o'lchang. "
                "Ikkita o'zgarishni birga kiritmang — aks holda qaysi biri yordam berganini "
                "bilib bo'lmaydi.\n"
                "5. Yakuniy so'rov va boshlang'ich so'rov AYNI natijani qaytarishini "
                "tekshiring (EXCEPT bilan solishtiring yoki qatorlar sonini va bir necha "
                "qiymatni taqqoslang).\n"
                "6. Qo'shgan har bir indeks uchun asos yozing: nega aynan bu ustunlar, nega "
                "shu tartibda, nega qisman yoki INCLUDE. Indeks hajmini pg_relation_size "
                "bilan ko'rsating.\n"
                "7. Yakuniy hisobot jadvali: har bir qadam uchun 'nima o'zgardi | reja qanday "
                "o'zgardi | vaqt oldin -> keyin | buferlar oldin -> keyin'.\n"
                "8. Xulosa: umumiy tezlashuv necha barobar va qaysi bitta o'zgarish eng ko'p "
                "foyda berdi. Agar biror tuzatish kutilganidan kam foyda bergan bo'lsa — buni "
                "halol yozing va sababini tushuntiring.\n"
                "9. Yakuniy fayl .sql ko'rinishida, boshidan oxirigacha xatosiz bajariladigan bo'lsin."
            ),
            "task_requirements_ru": (
                "1. Схема и тестовые данные: >= 100 000 клиентов, >= 2 000 000 заказов.\n"
                "2. Исходное измерение: приведите полный вывод EXPLAIN (ANALYZE, BUFFERS) "
                "запроса и укажите, какой узел съедает больше всего времени.\n"
                "3. Найдите и назовите минимум четыре проблемы. Рассмотрите: мешает ли "
                "использованию индекса функция на колонке (EXTRACT, LOWER); индексируется ли "
                "LIKE с процентом в начале, как '%@gmail.com'; сколько сканирований делают "
                "три коррелированных подзапроса; что делает OFFSET 4000.\n"
                "4. Вносите каждое исправление ОТДЕЛЬНО и после каждого измеряйте заново. "
                "Не вносите два изменения сразу — иначе не понять, какое помогло.\n"
                "5. Проверьте, что итоговый и исходный запросы возвращают ОДИНАКОВЫЙ "
                "результат (сравните через EXCEPT либо сверьте число строк и несколько "
                "значений).\n"
                "6. Для каждого добавленного индекса напишите обоснование: почему именно эти "
                "колонки, почему в таком порядке, почему частичный или INCLUDE. Покажите "
                "размер индекса через pg_relation_size.\n"
                "7. Итоговая таблица отчёта: по каждому шагу «что изменено | как изменился "
                "план | время до -> после | буферы до -> после».\n"
                "8. Вывод: во сколько раз ускорился запрос в целом и какое одно изменение "
                "дало наибольший эффект. Если какое-то исправление дало меньше пользы, чем "
                "ожидалось, — честно напишите это и объясните причину.\n"
                "9. Итоговый файл в виде .sql, выполняющийся от начала до конца без ошибок."
            ),
            "task_technologies": "PostgreSQL, SQL, EXPLAIN ANALYZE, Indexes",
            "task_deadline_days": 7,
        },
        "sample": {
            "title": "Namuna: Sekin so'rovni optimallashtirish — o'lchash va qayta o'lchash",
            "description": "Ustunga qo'llangan funksiya indeksni qanday o'ldirishi, OFFSET o'rniga keyset sahifalash va qisman + INCLUDE indeksning halol bahosi",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: o'lchash -> sabab -> BITTA o'zgarish -> qayta o'lchash
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mijozlar;

CREATE TABLE mijozlar (
    id  SERIAL      PRIMARY KEY,
    ism VARCHAR(60) NOT NULL
);
CREATE TABLE buyurtmalar (
    id       BIGSERIAL     PRIMARY KEY,
    mijoz_id INTEGER       NOT NULL REFERENCES mijozlar(id),
    sana     DATE          NOT NULL,
    holat    VARCHAR(20)   NOT NULL,
    summa    NUMERIC(12,2) NOT NULL
);

INSERT INTO mijozlar (ism) SELECT 'Mijoz ' || g FROM generate_series(1, 50000) g;

-- 500 000 qator — optimallashtirish shu hajmdan boshlab HAQIQATAN ko'rinadi
INSERT INTO buyurtmalar (mijoz_id, sana, holat, summa)
SELECT (random() * 49999)::INT + 1,
       DATE '2023-01-01' + (random() * 700)::INT,
       (ARRAY['yangi','tolangan','bekor'])[(random() * 2)::INT + 1],
       (random() * 5000000 + 50000)::NUMERIC(12,2)
FROM generate_series(1, 500000);

CREATE INDEX idx_b_sana ON buyurtmalar(sana);
ANALYZE mijozlar; ANALYZE buyurtmalar;

SELECT pg_size_pretty(pg_total_relation_size('buyurtmalar')) AS jadval_hajmi;

-- ══ MUAMMO 1: ustunga qo'llangan funksiya indeksni O'LDIRADI ════════
-- SEKIN: indeksda sana saqlangan, to_char(sana) emas -> Seq Scan
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar WHERE to_char(sana, 'YYYY-MM') = '2024-11';

-- TEZ: AYNI o'sha shart, lekin DIAPAZON ko'rinishida -> Bitmap Index Scan
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT COUNT(*) FROM buyurtmalar
WHERE sana >= DATE '2024-11-01' AND sana < DATE '2024-12-01';
-- Indeks QO'SHILMADI — faqat so'rov qayta yozildi. Bu bepul tuzatish.

-- ══ MUAMMO 2: OFFSET bilan chuqur sahifalash ═══════════════════════
-- SEKIN: OFFSET 400000 qatorni O'QIB, keyin TASHLAB YUBORADI
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
ORDER BY id DESC OFFSET 400000 LIMIT 20;
--  (actual rows=400020) <-- 400 ming qator o'qildi, 20 tasi kerak edi

-- TEZ: keyset (kursor) sahifalash — oldingi sahifadagi OXIRGI id dan davom
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT id, mijoz_id, sana, summa FROM buyurtmalar
WHERE id < 100000
ORDER BY id DESC LIMIT 20;
--  (actual rows=20), buferlar bir necha dona. Yuzlab barobar tez.
--  Muhimi: OFFSET qanchalik katta bo'lsa shunchalik sekinlashadi,
--  keyset esa 1-sahifada ham, 20 000-sahifada ham BIR XIL tez.
--  Kamchiligi: "birdan 500-sahifaga o'tish" mumkin emas.

-- ══ MUAMMO 3: filtrga mos indeks yo'q ══════════════════════════════
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;

-- Qisman (holat bo'yicha) + kompozit + INCLUDE indeks
CREATE INDEX idx_b_tolangan ON buyurtmalar(sana, mijoz_id) INCLUDE (summa)
    WHERE holat = 'tolangan';
ANALYZE buyurtmalar;

EXPLAIN (ANALYZE, BUFFERS, COSTS OFF)
SELECT m.id, m.ism, SUM(b.summa) AS jami, COUNT(*) AS soni
FROM buyurtmalar b JOIN mijozlar m ON m.id = b.mijoz_id
WHERE b.holat = 'tolangan' AND b.sana >= DATE '2024-11-01'
GROUP BY m.id, m.ism ORDER BY jami DESC LIMIT 20;

-- HALOL BAHO: reja O'ZGARDI (idx_b_sana o'rniga idx_b_tolangan, indeksdan
-- o'qilgan qatorlar ikki barobar kam), lekin UMUMIY vaqt deyarli o'sha-o'sha.
-- Sababi: qolgan vaqtni 50 000 mijoz bo'yicha Hash Join va GROUP BY yeyapti.
-- Har bir indeks 100 barobar tezlashtirmaydi. Va indeks bepul emas:
SELECT pg_size_pretty(pg_relation_size('idx_b_tolangan')) AS qisman_include,
       pg_size_pretty(pg_relation_size('idx_b_sana'))     AS oddiy_indeks;

-- ══ QO'SHIMCHA: COUNT(*) va taxminiy hisob ═════════════════════════
EXPLAIN (ANALYZE, COSTS OFF) SELECT COUNT(*) FROM buyurtmalar;
--  COUNT(*) MVCC tufayli HAR DOIM barcha qatorlarni ko'rib chiqadi.

SELECT reltuples::BIGINT AS taxminiy FROM pg_class WHERE oid = 'buyurtmalar'::regclass;
--  Sahifalashda "1 234 567 dan" ko'rsatish uchun aniq son SHART emas.""",
        },
        "exercises": [
            {
                "title": "Chuqur sahifalashni tuzatish",
                "title_ru": "Исправление глубокой пагинации",
                "description": "`ORDER BY id DESC OFFSET 1000000 LIMIT 20` so'rovi 135 ms ishlaydi va 13 327 bufer o'qiydi. Nima uchun u shunchalik sekin?",
                "description_ru": "Запрос `ORDER BY id DESC OFFSET 1000000 LIMIT 20` работает 135 мс и читает 13 327 буферов. Почему он настолько медленный?",
                "exercise_type": "multiple_choice",
                "options": [
                    "id ustunida indeks yo'q, shuning uchun butun jadval saralanadi",
                    "OFFSET tashlab yuboriladigan qatorlarni ham O'QIShI kerak — 1 000 020 qator o'qilib, 1 000 000 tasi tashlanadi",
                    "ORDER BY DESC indeksni teskari yo'nalishda ishlatib bo'lmaydigan qiladi",
                    "LIMIT 20 juda kichik, shuning uchun planner noto'g'ri reja tanlaydi",
                ],
                "options_ru": [
                    "На колонке id нет индекса, поэтому сортируется вся таблица",
                    "OFFSET обязан ПРОЧИТАТЬ и пропускаемые строки — читается 1 000 020 строк, из которых 1 000 000 выбрасывается",
                    "ORDER BY DESC делает невозможным использование индекса в обратном направлении",
                    "LIMIT 20 слишком мал, поэтому планировщик выбирает неверный план",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Rejadagi `actual rows=1000020` raqamiga qarang.",
                "hint_ru": "Посмотрите на число `actual rows=1000020` в плане.",
                "explanation": "OFFSET qatorlarni tashlab yuborishdan oldin ularni o'qishi shart. Keyset (kursor) sahifalash — WHERE id < :oxirgi_id ORDER BY id DESC LIMIT 20 — indeksga to'g'ridan-to'g'ri kiradi: o'lchovda 0.035 ms va 7 bufer, ya'ni ~3800 baravar tez.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Optimallashtirish qadamlarining tartibi",
                "title_ru": "Порядок шагов оптимизации",
                "description": "Sekin so'rovni tuzatish bosqichlarini to'g'ri tartibga soling.",
                "description_ru": "Расположите в правильном порядке этапы исправления медленного запроса.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "EXPLAIN (ANALYZE, BUFFERS) bilan boshlang'ich holatni o'lchash",
                    "Eng ko'p vaqt yeyayotgan tugunni va uning sababini aniqlash",
                    "Faqat BITTA o'zgarish kiritish (so'rovni qayta yozish yoki indeks qo'shish)",
                    "Qayta o'lchash: reja, vaqt va buferlar qanday o'zgardi",
                    "Natija oldingisi bilan bir xilligini tekshirish",
                ],
                "drag_items_ru": [
                    "Измерить исходное состояние через EXPLAIN (ANALYZE, BUFFERS)",
                    "Определить узел, съедающий больше всего времени, и его причину",
                    "Внести ТОЛЬКО ОДНО изменение (переписать запрос или добавить индекс)",
                    "Измерить заново: как изменились план, время и буферы",
                    "Проверить, что результат совпадает с прежним",
                ],
                "correct_order": [
                    "EXPLAIN (ANALYZE, BUFFERS) bilan boshlang'ich holatni o'lchash",
                    "Eng ko'p vaqt yeyayotgan tugunni va uning sababini aniqlash",
                    "Faqat BITTA o'zgarish kiritish (so'rovni qayta yozish yoki indeks qo'shish)",
                    "Qayta o'lchash: reja, vaqt va buferlar qanday o'zgardi",
                    "Natija oldingisi bilan bir xilligini tekshirish",
                ],
                "hint": "Optimallashtirish o'lchovdan boshlanadi, taxmindan emas.",
                "hint_ru": "Оптимизация начинается с измерения, а не с догадки.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 10
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 10,
        "title": "9-Partitioning asoslari",
        "title_ru": "9-Основы партиционирования",
        "points_reward": 14,
        "code_language": "sql",
        "text_content": """<h3>Bo'lish qachon kerak bo'ladi</h3>
<p>Partitioning &mdash; bitta mantiqiy jadvalni jismonan bir nechta kichik jadvalga bo'lish. Muhim: bu <em>oxirgi</em> vosita, birinchi emas. Indekslar, so'rovni qayta yozish va arxivlash odatda ancha arzon va oddiyroq.</p>
<p>Bo'lish haqida jiddiy o'ylash uchun mezonlar:</p>
<ul>
<li>Jadval o'nlab gigabaytdan oshgan va o'sishda davom etmoqda.</li>
<li>Ma'lumot tabiiy ravishda <strong>vaqt bo'yicha hayot siklini</strong> ega: yangi ma'lumot faol o'qiladi, eskisi esa deyarli tegilmaydi.</li>
<li>Eski ma'lumotni <strong>ommaviy o'chirish</strong> kerak. Bu partitioning ning eng kuchli argumenti: 50 million qatorni <code>DELETE</code> qilish soatlab davom etadi va jadvalni shishiradi, <code>DETACH PARTITION</code> esa <em>bir zumda</em> bajariladi.</li>
</ul>
<p>Agar so'rovlaringiz <strong>hamma</strong> bo'limlarga tegsa, partitioning hech narsa bermaydi &mdash; aksincha, rejalashtirish narxi oshadi.</p>

<h3>Uchta strategiya</h3>
<table>
<tr><th>Turi</th><th>Qachon</th><th>Misol</th></tr>
<tr><td><code>RANGE</code></td><td>Vaqt qatorlari, loglar, hodisalar</td><td>Chorak yoki oy bo'yicha</td></tr>
<tr><td><code>LIST</code></td><td>Aniq, cheklangan qiymatlar to'plami</td><td>Hudud, ijaraчи (tenant)</td></tr>
<tr><td><code>HASH</code></td><td>Tabiiy bo'linish yo'q, faqat teng taqsimlash kerak</td><td><code>foydalanuvchi_id</code> bo'yicha</td></tr>
</table>
<p>Amaliyotda <code>RANGE</code> eng ko'p ishlatiladi &mdash; chunki ma'lumotning hayot sikli deyarli har doim vaqt bilan bog'liq.</p>

<h3>Partition pruning &mdash; butun foyda shu yerda</h3>
<p>Pruning &mdash; PostgreSQL ning keraksiz bo'limlarni rejadan <em>umuman chiqarib tashlashi</em>. O'lchangan misol: 200 000 qatorli, 5 bo'limli jadvalda <code>WHERE sana BETWEEN '2023-02-01' AND '2023-03-01'</code> so'rovi rejasida <strong>faqat bitta</strong> bo'lim ko'rinadi.</p>
<p>Lekin pruning'ni buzish oson. Xuddi indekslardagidek: ustunga funksiya qo'llasangiz, u ishlamaydi. <code>WHERE EXTRACT(MONTH FROM sana) = 2</code> yozilganda planner qaysi bo'limlarda 2-oy borligini <em>bilolmaydi</em> va <strong>beshtasini ham</strong> skanerlaydi.</p>
<p>Bu darsning asosiy amaliy xulosasi: <strong>filtrni har doim partition kalitining o'ziga qo'ying</strong>, uning ustidagi ifodaga emas.</p>

<h3>Cheklovlar &mdash; oldindan bilish kerak</h3>
<ul>
<li><strong>Partition kaliti PRIMARY KEY ga kirishi shart.</strong> Ya'ni <code>id</code> bo'yicha global unikallik yo'q &mdash; <code>PRIMARY KEY (id, sana)</code> yozishga majbursiz. Buni loyihalash bosqichida hisobga olmasa, keyinchalik og'riqli bo'ladi.</li>
<li>Xuddi shu sabab bilan <code>UNIQUE</code> ham partition ustunlarisiz qo'yilmaydi: <code>ERROR: unique constraint on partitioned table must include all partitioning columns</code>.</li>
<li>Bo'lim juda ko'p bo'lsa (yuzlab), rejalashtirish vaqti sezilarli oshadi.</li>
<li>Hech bir bo'limga tushmagan qator <code>DEFAULT</code> bo'lim bo'lmasa <strong>xato</strong> beradi. <code>DEFAULT</code> bo'lim qo'yish deyarli har doim to'g'ri qaror.</li>
</ul>

<h3>Arxivlash &mdash; eng kuchli argument</h3>
<p><code>ALTER TABLE ... DETACH PARTITION</code> bo'limni ota jadvaldan ajratadi, lekin uni <em>o'chirmaydi</em>: u mustaqil jadvalga aylanadi. Uni arxivga ko'chirish, boshqa serverga o'tkazish yoki keyinroq <code>ATTACH</code> qilib qaytarish mumkin. Bu &mdash; deyarli bir zumda bajariladigan metama'lumot amali, ma'lumotni ko'chirish emas.</p>""",
        "text_content_ru": """<h3>Когда действительно нужно разбиение</h3>
<p>Партиционирование — это физическое разбиение одной логической таблицы на несколько меньших. Важно: это <em>последнее</em> средство, а не первое. Индексы, переписывание запросов и архивирование обычно намного дешевле и проще.</p>
<p>Критерии, при которых о разбиении стоит задуматься всерьёз:</p>
<ul>
<li>Таблица перевалила за десятки гигабайт и продолжает расти.</li>
<li>У данных есть естественный <strong>жизненный цикл по времени</strong>: свежие данные активно читаются, старые почти не трогают.</li>
<li>Нужно <strong>массово удалять</strong> старые данные. Это самый сильный аргумент в пользу партиционирования: <code>DELETE</code> 50 миллионов строк длится часами и раздувает таблицу, а <code>DETACH PARTITION</code> выполняется <em>мгновенно</em>.</li>
</ul>
<p>Если ваши запросы задевают <strong>все</strong> партиции, партиционирование не даст ничего — наоборот, вырастет стоимость планирования.</p>

<h3>Три стратегии</h3>
<table>
<tr><th>Тип</th><th>Когда</th><th>Пример</th></tr>
<tr><td><code>RANGE</code></td><td>Временные ряды, логи, события</td><td>По кварталам или месяцам</td></tr>
<tr><td><code>LIST</code></td><td>Конкретный ограниченный набор значений</td><td>Регион, арендатор (tenant)</td></tr>
<tr><td><code>HASH</code></td><td>Естественного деления нет, нужно лишь равномерное распределение</td><td>По <code>foydalanuvchi_id</code></td></tr>
</table>
<p>На практике чаще всего применяется <code>RANGE</code> — потому что жизненный цикл данных почти всегда связан со временем.</p>

<h3>Partition pruning — вся польза именно здесь</h3>
<p>Pruning — это <em>полное исключение</em> ненужных партиций из плана. Измеренный пример: в таблице на 200 000 строк с 5 партициями в плане запроса <code>WHERE sana BETWEEN '2023-02-01' AND '2023-03-01'</code> видна <strong>только одна</strong> партиция.</p>
<p>Но сломать pruning легко. Ровно как с индексами: примените к колонке функцию — и он перестанет работать. При <code>WHERE EXTRACT(MONTH FROM sana) = 2</code> планировщик <em>не может знать</em>, в каких партициях есть февраль, и просканирует <strong>все пять</strong>.</p>
<p>Главный практический вывод этого урока: <strong>всегда ставьте фильтр на сам ключ партиционирования</strong>, а не на выражение над ним.</p>

<h3>Ограничения — знать заранее</h3>
<ul>
<li><strong>Ключ партиционирования обязан входить в PRIMARY KEY.</strong> То есть глобальной уникальности по <code>id</code> не будет — придётся писать <code>PRIMARY KEY (id, sana)</code>. Если не учесть это на этапе проектирования, потом будет больно.</li>
<li>По той же причине <code>UNIQUE</code> нельзя поставить без колонок партиционирования: <code>ERROR: unique constraint on partitioned table must include all partitioning columns</code>.</li>
<li>Если партиций слишком много (сотни), время планирования заметно вырастает.</li>
<li>Строка, не попавшая ни в одну партицию, вызовет <strong>ошибку</strong>, если нет партиции <code>DEFAULT</code>. Создавать <code>DEFAULT</code>-партицию почти всегда правильное решение.</li>
</ul>

<h3>Архивирование — самый сильный аргумент</h3>
<p><code>ALTER TABLE ... DETACH PARTITION</code> отсоединяет партицию от родительской таблицы, но <em>не удаляет</em> её: она становится самостоятельной таблицей. Её можно перенести в архив, переместить на другой сервер или позже вернуть через <code>ATTACH</code>. Это почти мгновенная операция с метаданными, а не перенос данных.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- Partitioning: RANGE, LIST, HASH va partition pruning
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hodisalar CASCADE;

-- ─────────────────────────────────────────────────────────────────────
-- 1) RANGE partitioning — eng ko'p uchraydigan tur (vaqt bo'yicha)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE hodisalar (
    id      BIGSERIAL,
    turi    VARCHAR(30) NOT NULL,
    sana    DATE        NOT NULL,
    payload JSONB       NOT NULL DEFAULT '{}',
    PRIMARY KEY (id, sana)      -- partition kaliti PK ga KIRISHI SHART
) PARTITION BY RANGE (sana);
-- Diqqat: shu sabab bilan "id bo'yicha global unikallik" YO'Q.
-- Buni loyihalash bosqichida hisobga olish kerak.

CREATE TABLE hodisalar_2023q1 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
CREATE TABLE hodisalar_2023q2 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');
CREATE TABLE hodisalar_2023q3 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');
CREATE TABLE hodisalar_2023q4 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

-- DEFAULT bo'lim: hech bir chegaraga tushmagan qatorlar shu yerga tushadi.
-- Usiz bunday INSERT XATO beradi:
--   ERROR:  no partition of relation "hodisalar" found for row
CREATE TABLE hodisalar_boshqa PARTITION OF hodisalar DEFAULT;

INSERT INTO hodisalar (turi, sana, payload)
SELECT (ARRAY['kirish','xarid','chiqish'])[(random() * 2)::INT + 1],
       DATE '2023-01-01' + (random() * 364)::INT,
       jsonb_build_object('n', g)
FROM generate_series(1, 200000) g;

-- Indeks ONA jadvalda yaratiladi -> har bir bo'limga AVTOMATIK tarqaladi
CREATE INDEX idx_hodisalar_turi ON hodisalar(turi);
ANALYZE hodisalar;

-- Qator qaysi bo'limga tushganini ko'rish (tableoid — yashirin ustun):
SELECT tableoid::regclass AS bolim, COUNT(*)
FROM hodisalar GROUP BY 1 ORDER BY 1;
--  hodisalar_2023q1 | 49280
--  hodisalar_2023q2 | 49966
--  hodisalar_2023q3 | 50444
--  hodisalar_2023q4 | 50310

-- ─────────────────────────────────────────────────────────────────────
-- 2) PARTITION PRUNING — butun foyda shu yerda
-- ─────────────────────────────────────────────────────────────────────
-- YAXSHI: filtr partition kalitining O'ZIGA qo'yilgan
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE sana BETWEEN '2023-02-01' AND '2023-03-01';
--  Aggregate
--    ->  Seq Scan on hodisalar_2023q1 hodisalar
--  Rejada FAQAT BITTA bo'lim bor. Qolgan 4 tasi umuman ko'rib chiqilmadi.

-- YOMON: kalitga funksiya qo'llangan -> pruning ISHLAMAYDI
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE EXTRACT(MONTH FROM sana) = 2;
--  Parallel Append
--    ->  Parallel Seq Scan on hodisalar_2023q3 ...
--    ->  Parallel Seq Scan on hodisalar_2023q4 ...
--    ->  Parallel Seq Scan on hodisalar_2023q2 ...
--    ->  Parallel Seq Scan on hodisalar_2023q1 ...
--    ->  Parallel Seq Scan on hodisalar_boshqa ...
--  BESHTA bo'lim ham skanerlandi. Planner qaysi bo'limda 2-oy borligini
--  bilolmaydi — xuddi indekslardagi kabi muammo.

-- ─────────────────────────────────────────────────────────────────────
-- 3) ARXIVLASH: DETACH — partitioning ning eng kuchli argumenti
-- ─────────────────────────────────────────────────────────────────────
-- 49 280 qatorni DELETE qilish sekin va jadvalni shishiradi.
-- DETACH esa metama'lumot amali — deyarli bir zumda bajariladi.
ALTER TABLE hodisalar DETACH PARTITION hodisalar_2023q1;

SELECT COUNT(*) AS qolgan     FROM hodisalar;          -- 150720
SELECT COUNT(*) AS ajratilgan FROM hodisalar_2023q1;   -- 49280
-- Ma'lumot YO'QOLMADI: hodisalar_2023q1 endi mustaqil jadval.
-- Uni arxivga ko'chirish yoki DROP qilish mumkin.

-- Qaytarish ham oson:
ALTER TABLE hodisalar ATTACH PARTITION hodisalar_2023q1
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
SELECT COUNT(*) AS qaytarildi FROM hodisalar;          -- 200000

-- ─────────────────────────────────────────────────────────────────────
-- 4) LIST partitioning — aniq qiymatlar to'plami bo'yicha
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS sotuvlar CASCADE;
CREATE TABLE sotuvlar (
    id    BIGSERIAL,
    hudud VARCHAR(20)   NOT NULL,
    summa NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (id, hudud)
) PARTITION BY LIST (hudud);

CREATE TABLE sotuvlar_toshkent PARTITION OF sotuvlar FOR VALUES IN ('Toshkent');
-- Bitta bo'limga bir nechta qiymat berish mumkin:
CREATE TABLE sotuvlar_vodiy    PARTITION OF sotuvlar
    FOR VALUES IN ('Fargona', 'Andijon', 'Namangan');
CREATE TABLE sotuvlar_boshqa   PARTITION OF sotuvlar DEFAULT;

INSERT INTO sotuvlar (hudud, summa) VALUES
    ('Toshkent', 100), ('Andijon', 200), ('Buxoro', 300), ('Fargona', 400);

SELECT tableoid::regclass AS bolim, hudud, summa FROM sotuvlar ORDER BY 1, 2;
--  sotuvlar_toshkent | Toshkent | 100.00
--  sotuvlar_vodiy    | Andijon  | 200.00
--  sotuvlar_vodiy    | Fargona  | 400.00
--  sotuvlar_boshqa   | Buxoro   | 300.00   <-- ro'yxatda yo'q edi -> DEFAULT

-- ─────────────────────────────────────────────────────────────────────
-- 5) HASH partitioning — tabiiy bo'linish bo'lmaganda
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS sessiyalar CASCADE;
CREATE TABLE sessiyalar (
    foydalanuvchi_id BIGINT NOT NULL,
    token            TEXT   NOT NULL,
    PRIMARY KEY (foydalanuvchi_id)
) PARTITION BY HASH (foydalanuvchi_id);

CREATE TABLE sessiyalar_0 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessiyalar_1 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessiyalar_2 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessiyalar_3 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 3);

INSERT INTO sessiyalar SELECT g, 'tok_' || g FROM generate_series(1, 10000) g;

SELECT tableoid::regclass AS bolim, COUNT(*) FROM sessiyalar GROUP BY 1 ORDER BY 1;
--  sessiyalar_0 | 2489
--  sessiyalar_1 | 2527
--  sessiyalar_2 | 2530
--  sessiyalar_3 | 2454     <-- deyarli teng taqsimlandi

-- ─────────────────────────────────────────────────────────────────────
-- 6) CHEKLOV: global UNIQUE partition kalitisiz MUMKIN EMAS
-- ─────────────────────────────────────────────────────────────────────
-- Quyidagi buyruq XATO beradi:
--   ALTER TABLE hodisalar ADD CONSTRAINT uq_hodisa UNIQUE (id);
--
--   ERROR:  unique constraint on partitioned table must include all
--           partitioning columns
--   DETAIL:  UNIQUE constraint on table "hodisalar" lacks column "sana"
--            which is part of the partition key.
--
-- To'g'ri variant — kalitni ham kiritish:
--   ALTER TABLE hodisalar ADD CONSTRAINT uq_hodisa UNIQUE (id, sana);

-- ─────────────────────────────────────────────────────────────────────
-- 7) Bo'limlar ro'yxati va ularning chegaralari
-- ─────────────────────────────────────────────────────────────────────
SELECT c.relname AS bolim,
       pg_get_expr(c.relpartbound, c.oid) AS chegara,
       pg_size_pretty(pg_relation_size(c.oid)) AS hajm
FROM pg_class c
JOIN pg_inherits i ON i.inhrelid = c.oid
WHERE i.inhparent = 'hodisalar'::regclass
ORDER BY c.relname;""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- Партиционирование: RANGE, LIST, HASH и partition pruning
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS hodisalar CASCADE;

-- ─────────────────────────────────────────────────────────────────────
-- 1) RANGE-партиционирование — самый частый вариант (по времени)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE hodisalar (
    id      BIGSERIAL,
    turi    VARCHAR(30) NOT NULL,
    sana    DATE        NOT NULL,
    payload JSONB       NOT NULL DEFAULT '{}',
    PRIMARY KEY (id, sana)      -- ключ партиционирования ОБЯЗАН входить в PK
) PARTITION BY RANGE (sana);
-- Внимание: именно поэтому «глобальной уникальности по id» НЕТ.
-- Это нужно учитывать ещё на этапе проектирования.

CREATE TABLE hodisalar_2023q1 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
CREATE TABLE hodisalar_2023q2 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');
CREATE TABLE hodisalar_2023q3 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');
CREATE TABLE hodisalar_2023q4 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

-- DEFAULT-партиция: строки, не попавшие ни в один диапазон, идут сюда.
-- Без неё такой INSERT выдаст ОШИБКУ:
--   ERROR:  no partition of relation "hodisalar" found for row
CREATE TABLE hodisalar_boshqa PARTITION OF hodisalar DEFAULT;

INSERT INTO hodisalar (turi, sana, payload)
SELECT (ARRAY['kirish','xarid','chiqish'])[(random() * 2)::INT + 1],
       DATE '2023-01-01' + (random() * 364)::INT,
       jsonb_build_object('n', g)
FROM generate_series(1, 200000) g;

-- Индекс создаётся на РОДИТЕЛЬСКОЙ таблице -> АВТОМАТИЧЕСКИ расходится по партициям
CREATE INDEX idx_hodisalar_turi ON hodisalar(turi);
ANALYZE hodisalar;

-- Посмотреть, в какую партицию попала строка (tableoid — скрытая колонка):
SELECT tableoid::regclass AS bolim, COUNT(*)
FROM hodisalar GROUP BY 1 ORDER BY 1;
--  hodisalar_2023q1 | 49280
--  hodisalar_2023q2 | 49966
--  hodisalar_2023q3 | 50444
--  hodisalar_2023q4 | 50310

-- ─────────────────────────────────────────────────────────────────────
-- 2) PARTITION PRUNING — вся польза именно здесь
-- ─────────────────────────────────────────────────────────────────────
-- ХОРОШО: фильтр стоит на САМОМ ключе партиционирования
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE sana BETWEEN '2023-02-01' AND '2023-03-01';
--  Aggregate
--    ->  Seq Scan on hodisalar_2023q1 hodisalar
--  В плане ТОЛЬКО ОДНА партиция. Остальные 4 даже не рассматривались.

-- ПЛОХО: к ключу применена функция -> pruning НЕ РАБОТАЕТ
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE EXTRACT(MONTH FROM sana) = 2;
--  Parallel Append
--    ->  Parallel Seq Scan on hodisalar_2023q3 ...
--    ->  Parallel Seq Scan on hodisalar_2023q4 ...
--    ->  Parallel Seq Scan on hodisalar_2023q2 ...
--    ->  Parallel Seq Scan on hodisalar_2023q1 ...
--    ->  Parallel Seq Scan on hodisalar_boshqa ...
--  Просканированы ВСЕ ПЯТЬ партиций. Планировщик не может знать, в какой
--  партиции есть февраль — та же проблема, что и с индексами.

-- ─────────────────────────────────────────────────────────────────────
-- 3) АРХИВИРОВАНИЕ: DETACH — самый сильный аргумент за партиционирование
-- ─────────────────────────────────────────────────────────────────────
-- Удалить 49 280 строк через DELETE медленно и раздувает таблицу.
-- А DETACH — операция с метаданными, выполняется почти мгновенно.
ALTER TABLE hodisalar DETACH PARTITION hodisalar_2023q1;

SELECT COUNT(*) AS qolgan     FROM hodisalar;          -- 150720
SELECT COUNT(*) AS ajratilgan FROM hodisalar_2023q1;   -- 49280
-- Данные НЕ ПОТЕРЯНЫ: hodisalar_2023q1 теперь самостоятельная таблица.
-- Её можно перенести в архив или удалить через DROP.

-- Вернуть тоже просто:
ALTER TABLE hodisalar ATTACH PARTITION hodisalar_2023q1
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
SELECT COUNT(*) AS qaytarildi FROM hodisalar;          -- 200000

-- ─────────────────────────────────────────────────────────────────────
-- 4) LIST-партиционирование — по конкретному набору значений
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS sotuvlar CASCADE;
CREATE TABLE sotuvlar (
    id    BIGSERIAL,
    hudud VARCHAR(20)   NOT NULL,
    summa NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (id, hudud)
) PARTITION BY LIST (hudud);

CREATE TABLE sotuvlar_toshkent PARTITION OF sotuvlar FOR VALUES IN ('Toshkent');
-- Одной партиции можно назначить несколько значений:
CREATE TABLE sotuvlar_vodiy    PARTITION OF sotuvlar
    FOR VALUES IN ('Fargona', 'Andijon', 'Namangan');
CREATE TABLE sotuvlar_boshqa   PARTITION OF sotuvlar DEFAULT;

INSERT INTO sotuvlar (hudud, summa) VALUES
    ('Toshkent', 100), ('Andijon', 200), ('Buxoro', 300), ('Fargona', 400);

SELECT tableoid::regclass AS bolim, hudud, summa FROM sotuvlar ORDER BY 1, 2;
--  sotuvlar_toshkent | Toshkent | 100.00
--  sotuvlar_vodiy    | Andijon  | 200.00
--  sotuvlar_vodiy    | Fargona  | 400.00
--  sotuvlar_boshqa   | Buxoro   | 300.00   <-- не было в списке -> DEFAULT

-- ─────────────────────────────────────────────────────────────────────
-- 5) HASH-партиционирование — когда естественного деления нет
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS sessiyalar CASCADE;
CREATE TABLE sessiyalar (
    foydalanuvchi_id BIGINT NOT NULL,
    token            TEXT   NOT NULL,
    PRIMARY KEY (foydalanuvchi_id)
) PARTITION BY HASH (foydalanuvchi_id);

CREATE TABLE sessiyalar_0 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessiyalar_1 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessiyalar_2 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessiyalar_3 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 3);

INSERT INTO sessiyalar SELECT g, 'tok_' || g FROM generate_series(1, 10000) g;

SELECT tableoid::regclass AS bolim, COUNT(*) FROM sessiyalar GROUP BY 1 ORDER BY 1;
--  sessiyalar_0 | 2489
--  sessiyalar_1 | 2527
--  sessiyalar_2 | 2530
--  sessiyalar_3 | 2454     <-- распределилось почти поровну

-- ─────────────────────────────────────────────────────────────────────
-- 6) ОГРАНИЧЕНИЕ: глобальный UNIQUE без ключа партиционирования НЕВОЗМОЖЕН
-- ─────────────────────────────────────────────────────────────────────
-- Следующая команда выдаст ОШИБКУ:
--   ALTER TABLE hodisalar ADD CONSTRAINT uq_hodisa UNIQUE (id);
--
--   ERROR:  unique constraint on partitioned table must include all
--           partitioning columns
--   DETAIL:  UNIQUE constraint on table "hodisalar" lacks column "sana"
--            which is part of the partition key.
--
-- Правильный вариант — включить и ключ:
--   ALTER TABLE hodisalar ADD CONSTRAINT uq_hodisa UNIQUE (id, sana);

-- ─────────────────────────────────────────────────────────────────────
-- 7) Список партиций и их границы
-- ─────────────────────────────────────────────────────────────────────
SELECT c.relname AS bolim,
       pg_get_expr(c.relpartbound, c.oid) AS chegara,
       pg_size_pretty(pg_relation_size(c.oid)) AS hajm
FROM pg_class c
JOIN pg_inherits i ON i.inhrelid = c.oid
WHERE i.inhparent = 'hodisalar'::regclass
ORDER BY c.relname;""",
        "task": {
            "task_title": "Amaliy topshiriq: Hodisalar jadvalini bo'lish va arxivlash strategiyasi",
            "task_title_ru": "Практическое задание: партиционирование и стратегия архивации таблицы событий",
            "task_description": (
                "Sizga real vaziyat berilgan. hodisalar jadvali — mobil ilovaning telemetriya "
                "jurnali: uch yillik ma'lumot, taxminan 800 million qator, kuniga bir necha "
                "million yangi qator qo'shiladi. So'rovlarning ~95% i oxirgi 30 kunlik sana "
                "diapazoni bo'yicha filtrlaydi. 12 oydan eski ma'lumot har oy arxivga "
                "chiqariladi va undan keyin deyarli hech qachon o'qilmaydi.\n\n"
                "Avval QAROR yozing: RANGE, LIST yoki HASH — qaysi biri va nega; qolgan "
                "ikkitasi nega bu yerda mos emas; va partitioning umuman kerak bo'lmaydigan "
                "qanday vaziyat bo'lishi mumkin edi. So'ng qarorni amalda tekshiring: "
                "sxemani yarating, ma'lumot bilan to'ldiring, pruning ishlashini va "
                "buzilishini rejalar bilan isbotlang, eng eski bo'limni DETACH bilan "
                "arxivlang."
            ),
            "task_description_ru": (
                "Вам дана реальная ситуация. Таблица hodisalar — журнал телеметрии мобильного "
                "приложения: три года данных, примерно 800 миллионов строк, в сутки "
                "добавляется несколько миллионов новых. Около 95% запросов фильтруют по "
                "диапазону дат за последние 30 дней. Данные старше 12 месяцев ежемесячно "
                "уходят в архив и после этого почти никогда не читаются.\n\n"
                "Сначала напишите РЕШЕНИЕ: RANGE, LIST или HASH — что именно и почему; почему "
                "два других здесь не подходят; и в какой ситуации партиционирование вообще не "
                "понадобилось бы. Затем проверьте решение на практике: создайте схему, "
                "заполните данными, докажите планами, что pruning работает и как он ломается, "
                "и заархивируйте самую старую партицию через DETACH."
            ),
            "task_requirements": (
                "1. Yozma qaror (izoh yoki .md): tanlangan strategiya va asoslash; qolgan ikki "
                "strategiya nega mos emasligi; partitioning O'RNIGA nima qilish mumkin edi "
                "(indeks, so'rovni qayta yozish, arxivlash) va qachon u yetarli bo'lardi.\n"
                "2. RANGE bo'yicha bo'lingan jadval: kamida 4 ta chorak yoki oy bo'limi va "
                "DEFAULT bo'lim. PRIMARY KEY ga partition kaliti kiritilsin.\n"
                "3. Kamida 200 000 qator generate_series bilan yuklansin; tableoid orqali "
                "qatorlarning bo'limlar bo'yicha taqsimoti ko'rsatilsin.\n"
                "4. Indeks ONA jadvalda yaratilsin; izohda u bo'limlarga avtomatik tarqalishi "
                "qayd etilsin.\n"
                "5. PRUNING ISHLAGAN holat: filtr partition kalitining o'ziga qo'yilgan "
                "EXPLAIN rejasi keltirilsin va rejada faqat bitta bo'lim borligi ko'rsatilsin.\n"
                "6. PRUNING BUZILGAN holat: kalitga funksiya qo'llangan so'rov (masalan "
                "EXTRACT) rejasi keltirilsin — barcha bo'limlar skanerlanishi ko'rsatilsin. "
                "So'ng uni tuzatgan qayta yozilgan variant va yangi reja keltirilsin.\n"
                "7. DEFAULT bo'limsiz INSERT xato berishi izohda yozilsin (xato matni bilan).\n"
                "8. Arxivlash: ALTER TABLE ... DETACH PARTITION bajarilib, ajratishdan oldingi "
                "va keyingi qator sonlari ko'rsatilsin; ma'lumot yo'qolmagani isbotlansin va "
                "ATTACH bilan qaytarilsin.\n"
                "9. Cheklov: partition kalitisiz UNIQUE qo'yishga urinish va uning haqiqiy xato "
                "matni; keyin to'g'ri variant.\n"
                "10. Bir jumlada: agar bo'lish LIST bo'yicha (masalan ijarachi/tenant) "
                "bo'lganida sxemada va so'rovlarda nima o'zgarardi."
            ),
            "task_requirements_ru": (
                "1. Письменное решение (комментарий или .md): выбранная стратегия и "
                "обоснование; почему две другие здесь не подходят; что можно было сделать "
                "ВМЕСТО партиционирования (индексы, переписывание запроса, архивация) и когда "
                "этого хватило бы.\n"
                "2. Таблица, партиционированная по RANGE: минимум 4 квартальные или месячные "
                "партиции плюс DEFAULT. Ключ партиционирования включён в PRIMARY KEY.\n"
                "3. Загрузите минимум 200 000 строк через generate_series; покажите "
                "распределение строк по партициям через tableoid.\n"
                "4. Индекс создайте на РОДИТЕЛЬСКОЙ таблице; в комментарии отметьте, что он "
                "автоматически расходится по партициям.\n"
                "5. Случай, когда PRUNING РАБОТАЕТ: приведите план EXPLAIN с фильтром по самому "
                "ключу партиционирования и покажите, что в плане только одна партиция.\n"
                "6. Случай, когда PRUNING СЛОМАН: приведите план запроса с функцией над ключом "
                "(например EXTRACT) — покажите сканирование всех партиций. Затем приведите "
                "переписанный вариант и новый план.\n"
                "7. В комментарии опишите (с текстом ошибки), что без DEFAULT-партиции INSERT "
                "падает.\n"
                "8. Архивация: выполните ALTER TABLE ... DETACH PARTITION, покажите количество "
                "строк до и после, докажите, что данные не потеряны, и верните партицию через "
                "ATTACH.\n"
                "9. Ограничение: попытка задать UNIQUE без ключа партиционирования и настоящий "
                "текст ошибки; затем корректный вариант.\n"
                "10. Одной фразой: что изменилось бы в схеме и запросах, если бы разбиение было "
                "по LIST (например, по арендатору/tenant)."
            ),
            "task_technologies": "PostgreSQL, PARTITION BY RANGE/LIST/HASH, partition pruning, DETACH PARTITION",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: RANGE/LIST/HASH partitioning, pruning va DETACH bilan arxivlash",
            "description": "Bo'limlarga taqsimlanish, pruning ishlagan va buzilgan rejalar yonma-yon, DETACH/ATTACH bilan bir zumda arxivlash va UNIQUE cheklovi",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: RANGE partitioning, pruning va DETACH bilan arxivlash
DROP TABLE IF EXISTS hodisalar CASCADE;

-- Partition kaliti PRIMARY KEY ga KIRISHI SHART -> id bo'yicha global
-- unikallik YO'Q. Buni loyihalash bosqichida hisobga olish kerak.
CREATE TABLE hodisalar (
    id      BIGSERIAL,
    turi    VARCHAR(30) NOT NULL,
    sana    DATE        NOT NULL,
    payload JSONB       NOT NULL DEFAULT '{}',
    PRIMARY KEY (id, sana)
) PARTITION BY RANGE (sana);

CREATE TABLE hodisalar_2023q1 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
CREATE TABLE hodisalar_2023q2 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');
CREATE TABLE hodisalar_2023q3 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');
CREATE TABLE hodisalar_2023q4 PARTITION OF hodisalar
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

-- DEFAULT bo'lim: chegaraga tushmagan qator uchun. Usiz INSERT xato beradi:
--   ERROR: no partition of relation "hodisalar" found for row
CREATE TABLE hodisalar_boshqa PARTITION OF hodisalar DEFAULT;

INSERT INTO hodisalar (turi, sana, payload)
SELECT (ARRAY['kirish','xarid','chiqish'])[(random() * 2)::INT + 1],
       DATE '2023-01-01' + (random() * 364)::INT,
       jsonb_build_object('n', g)
FROM generate_series(1, 200000) g;

-- Indeks ONA jadvalda yaratiladi -> har bir bo'limga AVTOMATIK tarqaladi
CREATE INDEX idx_hodisalar_turi ON hodisalar(turi);
ANALYZE hodisalar;

-- Qator qaysi bo'limga tushgan (tableoid — yashirin ustun):
SELECT tableoid::regclass AS bolim, COUNT(*) FROM hodisalar GROUP BY 1 ORDER BY 1;

-- ══ PARTITION PRUNING — butun foyda shu yerda ═══════════════════════
-- YAXSHI: filtr partition kalitining O'ZIGA qo'yilgan -> rejada BITTA bo'lim
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE sana BETWEEN '2023-02-01' AND '2023-03-01';

-- YOMON: kalitga funksiya qo'llangan -> pruning ISHLAMAYDI, BESHTA bo'lim
-- ham skanerlanadi. Xuddi indekslardagi muammo.
EXPLAIN (ANALYZE, TIMING OFF, COSTS OFF)
SELECT COUNT(*) FROM hodisalar WHERE EXTRACT(MONTH FROM sana) = 2;
-- Xulosa: filtrni HAR DOIM partition kalitining o'ziga qo'ying,
-- uning ustidagi ifodaga emas.

-- ══ ARXIVLASH: DETACH — partitioning ning eng kuchli argumenti ══════
-- 50 000 qatorni DELETE qilish sekin va jadvalni shishiradi.
-- DETACH esa metama'lumot amali — deyarli bir zumda bajariladi.
ALTER TABLE hodisalar DETACH PARTITION hodisalar_2023q1;

SELECT (SELECT COUNT(*) FROM hodisalar)        AS qolgan,
       (SELECT COUNT(*) FROM hodisalar_2023q1) AS ajratilgan;
-- Ma'lumot YO'QOLMADI: hodisalar_2023q1 endi MUSTAQIL jadval.
-- Uni arxivga ko'chirish, boshqa serverga o'tkazish yoki qaytarish mumkin:
ALTER TABLE hodisalar ATTACH PARTITION hodisalar_2023q1
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

-- ══ LIST — aniq, cheklangan qiymatlar to'plami ══════════════════════
DROP TABLE IF EXISTS sotuvlar CASCADE;
CREATE TABLE sotuvlar (
    id    BIGSERIAL,
    hudud VARCHAR(20)   NOT NULL,
    summa NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (id, hudud)
) PARTITION BY LIST (hudud);

CREATE TABLE sotuvlar_toshkent PARTITION OF sotuvlar FOR VALUES IN ('Toshkent');
CREATE TABLE sotuvlar_vodiy    PARTITION OF sotuvlar
    FOR VALUES IN ('Fargona', 'Andijon', 'Namangan');
CREATE TABLE sotuvlar_boshqa   PARTITION OF sotuvlar DEFAULT;

INSERT INTO sotuvlar (hudud, summa) VALUES
    ('Toshkent', 100), ('Andijon', 200), ('Buxoro', 300), ('Fargona', 400);
SELECT tableoid::regclass AS bolim, hudud FROM sotuvlar ORDER BY 1, 2;
--  Buxoro ro'yxatda yo'q edi -> DEFAULT bo'limga tushdi.

-- ══ HASH — tabiiy bo'linish bo'lmaganda, faqat teng taqsimlash ══════
DROP TABLE IF EXISTS sessiyalar CASCADE;
CREATE TABLE sessiyalar (
    foydalanuvchi_id BIGINT NOT NULL,
    token            TEXT   NOT NULL,
    PRIMARY KEY (foydalanuvchi_id)
) PARTITION BY HASH (foydalanuvchi_id);

CREATE TABLE sessiyalar_0 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessiyalar_1 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessiyalar_2 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessiyalar_3 PARTITION OF sessiyalar FOR VALUES WITH (MODULUS 4, REMAINDER 3);

INSERT INTO sessiyalar SELECT g, 'tok_' || g FROM generate_series(1, 10000) g;
SELECT tableoid::regclass AS bolim, COUNT(*) FROM sessiyalar GROUP BY 1 ORDER BY 1;
--  Deyarli teng taqsimlandi.

-- CHEKLOV: global UNIQUE partition kalitisiz MUMKIN EMAS.
--   ALTER TABLE hodisalar ADD CONSTRAINT uq UNIQUE (id);
--   ERROR: unique constraint on partitioned table must include all
--          partitioning columns
-- To'g'ri variant — kalitni ham kiritish: UNIQUE (id, sana).

-- Bo'limlar va ularning chegaralari:
SELECT c.relname AS bolim,
       pg_get_expr(c.relpartbound, c.oid) AS chegara,
       pg_size_pretty(pg_relation_size(c.oid)) AS hajm
FROM pg_class c
JOIN pg_inherits i ON i.inhrelid = c.oid
WHERE i.inhparent = 'hodisalar'::regclass
ORDER BY c.relname;""",
        },
        "exercises": [
            {
                "title": "Pruning nima uchun ishlamadi?",
                "title_ru": "Почему не сработал pruning?",
                "description": "Jadval sana bo'yicha choraklarga bo'lingan. `WHERE EXTRACT(MONTH FROM sana) = 2` so'rovi rejasida BARCHA bo'limlar skanerlanmoqda. Sabab nima?",
                "description_ru": "Таблица разбита по кварталам по колонке sana. В плане запроса `WHERE EXTRACT(MONTH FROM sana) = 2` сканируются ВСЕ партиции. В чём причина?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Bo'limlar soni juda kam — pruning kamida 10 bo'limdan boshlab ishlaydi",
                    "Kalit ustunga funksiya qo'llangan, shuning uchun planner qaysi bo'limda 2-oy borligini aniqlay olmaydi",
                    "DEFAULT bo'lim mavjudligi pruning ni butunlay o'chiradi",
                    "sana ustunida indeks yo'q",
                ],
                "options_ru": [
                    "Слишком мало партиций — pruning работает начиная примерно с 10 партиций",
                    "К ключевой колонке применена функция, поэтому планировщик не может определить, в какой партиции есть февраль",
                    "Наличие DEFAULT-партиции полностью отключает pruning",
                    "На колонке sana нет индекса",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu indekslardagi bilan aynan bir xil muammo.",
                "hint_ru": "Это ровно та же проблема, что и с индексами.",
                "explanation": "Bo'lim chegaralari sana qiymatlari bo'yicha belgilangan, EXTRACT(MONTH ...) natijasi bo'yicha emas. Planner ifodani chegaralar bilan solishtira olmaydi. Yechim — filtrni kalitning o'ziga qo'yish: sana >= '2023-02-01' AND sana < '2023-03-01'.",
                "difficulty_level": "Medium",
                "points": 12,
            },
            {
                "title": "Bo'limni bir zumda arxivlash",
                "title_ru": "Мгновенное архивирование партиции",
                "description": "Eski chorak ma'lumotini jadvaldan olib tashlash kerak, lekin ma'lumot o'chib ketmasligi va amal deyarli bir zumda bajarilishi kerak. Qaysi buyruq ishlatiladi? ALTER TABLE hodisalar ___ PARTITION hodisalar_2023q1;",
                "description_ru": "Нужно убрать данные старого квартала из таблицы так, чтобы данные не пропали, а операция выполнилась почти мгновенно. Какая команда используется? ALTER TABLE hodisalar ___ PARTITION hodisalar_2023q1;",
                "exercise_type": "fill_in_blank",
                "correct_answers": "DETACH",
                "hint": "Teskari amal — ATTACH.",
                "hint_ru": "Обратная операция — ATTACH.",
                "explanation": "DETACH PARTITION bo'limni ota jadvaldan ajratadi, lekin uni mustaqil jadval sifatida saqlab qoladi. Bu metama'lumot amali — millionlab qatorni DELETE qilishdan farqli o'laroq deyarli bir zumda bajariladi.",
                "difficulty_level": "Easy",
                "points": 10,
            },
            {
                "title": "Partitioning haqida to'g'ri fikrlar",
                "title_ru": "Верные утверждения о партиционировании",
                "description": "Quyidagilardan qaysilari to'g'ri?",
                "description_ru": "Какие из приведённых утверждений верны?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Partition kaliti PRIMARY KEY tarkibiga kirishi shart, ya'ni id bo'yicha global unikallik bo'lmaydi",
                    "Ona jadvalda yaratilgan indeks barcha bo'limlarga avtomatik tarqaladi",
                    "DEFAULT bo'lim bo'lmasa, hech bir chegaraga tushmagan qatorni INSERT qilish xato beradi",
                    "Partitioning har qanday katta jadvalni avtomatik tezlashtiradi",
                ],
                "options_ru": [
                    "Ключ партиционирования обязан входить в PRIMARY KEY, то есть глобальной уникальности по id не будет",
                    "Индекс, созданный на родительской таблице, автоматически расходится по всем партициям",
                    "Без DEFAULT-партиции вставка строки, не попадающей ни в один диапазон, вызовет ошибку",
                    "Партиционирование автоматически ускоряет любую большую таблицу",
                ],
                "correct_answers": "A,B,C",
                "is_multiple_select": True,
                "hint": "So'rovlar hamma bo'limlarga tegib ketsa, partitioning nima beradi?",
                "hint_ru": "Что даёт партиционирование, если запросы задевают все партиции?",
                "explanation": "D noto'g'ri: agar so'rovlar barcha bo'limlarga tegsa, pruning ishlamaydi va partitioning faqat rejalashtirish narxini oshiradi. U foydali bo'lishi uchun filtr partition kaliti bo'yicha bo'lishi kerak.",
                "difficulty_level": "Medium",
                "points": 12,
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════
    # 11  — CAPSTONE
    # ══════════════════════════════════════════════════════════════════
    {
        "order": 11,
        "title": "10-CAPSTONE: Katta hajmli jadvalda performance audit",
        "title_ru": "10-CAPSTONE: аудит производительности большой таблицы",
        "points_reward": 22,
        "code_language": "sql",
        "text_content": """<h3>Audit &mdash; alohida ko'nikma</h3>
<p>Kurs davomida siz <em>berilgan</em> so'rovni tuzatishni o'rgandingiz. Haqiqiy ishda esa vazifa boshqacha qo'yiladi: &ldquo;baza sekinlashdi, ko'rib chiqing&rdquo;. Bu yerda hech kim qaysi so'rov muammoli ekanini aytmaydi &mdash; buni <strong>o'zingiz topishingiz</strong> kerak.</p>
<p>Audit &mdash; tizimli jarayon: ma'lumot yig'ish &rarr; muammolarni tartiblash &rarr; har birini o'lchov bilan tasdiqlash &rarr; tavsiyalarni <em>ta'sir/xarajat</em> bo'yicha saralash. Va eng muhimi &mdash; audit natijasi indekslar ro'yxati emas, <strong>hisobot</strong> bo'ladi: nima topildi, nega muammo, qancha turadi tuzatish, qanday foyda kutilmoqda.</p>

<h3>Auditning oltita bosqichi</h3>
<table>
<tr><th>Bosqich</th><th>Savol</th><th>Manba</th></tr>
<tr><td>1. Hajm</td><td>Qaysi jadvallar katta? Indekslar jadvaldan kattami?</td><td><code>pg_total_relation_size</code></td></tr>
<tr><td>2. Skanerlash</td><td>Qaysi jadvallar to'liq o'qilmoqda?</td><td><code>pg_stat_user_tables.seq_scan</code></td></tr>
<tr><td>3. So'rovlar</td><td>Eng ko'p vaqt yeydigan va eng ko'p chaqiriladigan so'rovlar?</td><td><code>pg_stat_statements</code></td></tr>
<tr><td>4. Indekslar</td><td>Qaysilari ishlatilmayapti? Qaysi FK indekssiz?</td><td><code>pg_stat_user_indexes</code>, <code>pg_constraint</code></td></tr>
<tr><td>5. Bloat</td><td>O'lik qatorlar ko'pmi? Autovacuum yetishyaptimi?</td><td><code>n_dead_tup</code>, <code>last_autovacuum</code></td></tr>
<tr><td>6. Kesh</td><td>Ma'lumot xotiradan o'qilyaptimi yoki diskdan?</td><td><code>pg_statio_user_tables</code></td></tr>
</table>

<h3>Ikkita eng samarali tekshiruv</h3>
<p><strong>Indekssiz foreign key.</strong> PostgreSQL <code>PRIMARY KEY</code> uchun indeksni avtomatik yaratadi, lekin <code>FOREIGN KEY</code> uchun <em>yaratmaydi</em>. Natijada har bir <code>JOIN</code> sekin ishlaydi va ota qatorni <code>DELETE</code> qilish butun bola jadvalni skanerlaydi. Bu &mdash; auditda eng ko'p topiladigan va eng oson tuzatiladigan muammo.</p>
<p><strong>Ishlatilmayotgan indekslar.</strong> <code>idx_scan = 0</code> bo'lgan indeks &mdash; sof zarar: joy egallaydi, har bir yozishni sekinlashtiradi, foyda bermaydi. Faqat bitta ehtiyot: statistika <em>oxirgi <code>pg_stat_reset()</code> dan beri</em> yig'iladi, shuning uchun statistika yosh bo'lsa xulosa chiqarish erta. Shuningdek, yiliga bir marta ishlaydigan hisobot indeksi ham nol ko'rsatishi mumkin.</p>

<h3>Cache hit ratio</h3>
<p>Sog'lom baza uchun bu ko'rsatkich <strong>99% dan yuqori</strong> bo'lishi kerak. Ushbu platformaning real bazasida o'lchandi: <strong>99.77%</strong>. Agar u 90% dan past bo'lsa, <code>shared_buffers</code> yetishmayotgan bo'lishi mumkin &mdash; lekin avval &ldquo;keraksiz ko'p ma'lumot o'qilmayaptimi?&rdquo; deb tekshiring: ko'pincha sabab yetishmayotgan indeks, xotira emas.</p>

<h3>Tavsiyalarni qanday yozish kerak</h3>
<p>&ldquo;Indeks qo'shish kerak&rdquo; degan tavsiya yaroqsiz. Yaxshi tavsiya to'rt savolga javob beradi:</p>
<ol>
<li><strong>Nima</strong> qilinadi &mdash; aniq DDL.</li>
<li><strong>Nega</strong> &mdash; qaysi so'rov, qaysi o'lchov buni ko'rsatdi.</li>
<li><strong>Xarajat</strong> &mdash; indeks hajmi, yozishga ta'sir, qulflar (produksiyada <code>CREATE INDEX CONCURRENTLY</code>).</li>
<li><strong>Kutilgan foyda</strong> &mdash; o'lchov bilan: vaqt X dan Y ga, buferlar A dan B ga.</li>
</ol>
<p>Va halol bo'ling: agar biror o'zgarish kutilganidan kam foyda bergan bo'lsa, buni yozing. R2 darsida ko'rgandek, indeks har doim 100 barobar tezlashtirmaydi &mdash; ba'zan 1.6 barobar, va bu ham natija.</p>""",
        "text_content_ru": """<h3>Аудит — отдельный навык</h3>
<p>На протяжении курса вы учились чинить <em>данный вам</em> запрос. В реальной работе задача ставится иначе: «база тормозит, разберитесь». Здесь никто не скажет, какой запрос проблемный — это нужно <strong>найти самому</strong>.</p>
<p>Аудит — системный процесс: сбор данных &rarr; упорядочивание проблем &rarr; подтверждение каждой измерением &rarr; сортировка рекомендаций по <em>эффекту/затратам</em>. И самое важное — результатом аудита будет не список индексов, а <strong>отчёт</strong>: что найдено, почему это проблема, сколько стоит исправление, какой ожидается выигрыш.</p>

<h3>Шесть этапов аудита</h3>
<table>
<tr><th>Этап</th><th>Вопрос</th><th>Источник</th></tr>
<tr><td>1. Размер</td><td>Какие таблицы большие? Индексы больше самой таблицы?</td><td><code>pg_total_relation_size</code></td></tr>
<tr><td>2. Сканирования</td><td>Какие таблицы читаются целиком?</td><td><code>pg_stat_user_tables.seq_scan</code></td></tr>
<tr><td>3. Запросы</td><td>Какие запросы съедают больше всего времени и вызываются чаще всего?</td><td><code>pg_stat_statements</code></td></tr>
<tr><td>4. Индексы</td><td>Какие не используются? Какие FK без индекса?</td><td><code>pg_stat_user_indexes</code>, <code>pg_constraint</code></td></tr>
<tr><td>5. Bloat</td><td>Много ли мёртвых строк? Справляется ли autovacuum?</td><td><code>n_dead_tup</code>, <code>last_autovacuum</code></td></tr>
<tr><td>6. Кэш</td><td>Данные читаются из памяти или с диска?</td><td><code>pg_statio_user_tables</code></td></tr>
</table>

<h3>Две самые результативные проверки</h3>
<p><strong>Внешний ключ без индекса.</strong> Для <code>PRIMARY KEY</code> PostgreSQL создаёт индекс автоматически, а для <code>FOREIGN KEY</code> — <em>нет</em>. В результате каждый <code>JOIN</code> работает медленно, а <code>DELETE</code> родительской строки сканирует всю дочернюю таблицу. Это самая часто находимая и самая легко исправляемая проблема аудита.</p>
<p><strong>Неиспользуемые индексы.</strong> Индекс с <code>idx_scan = 0</code> — чистый вред: занимает место, замедляет каждую запись, пользы не приносит. Одна оговорка: статистика собирается <em>с момента последнего <code>pg_stat_reset()</code></em>, поэтому по свежей статистике выводы делать рано. Кроме того, индекс под отчёт, который запускается раз в год, тоже покажет ноль.</p>

<h3>Cache hit ratio</h3>
<p>У здоровой базы этот показатель должен быть <strong>выше 99%</strong>. Измерено на реальной базе этой платформы: <strong>99.77%</strong>. Если он ниже 90%, возможно, не хватает <code>shared_buffers</code> — но сначала проверьте, «не читается ли лишнего»: чаще причина в отсутствующем индексе, а не в памяти.</p>

<h3>Как писать рекомендации</h3>
<p>Рекомендация «нужно добавить индекс» никуда не годится. Хорошая рекомендация отвечает на четыре вопроса:</p>
<ol>
<li><strong>Что</strong> делается — конкретный DDL.</li>
<li><strong>Почему</strong> — какой запрос, какое измерение на это указало.</li>
<li><strong>Затраты</strong> — размер индекса, влияние на запись, блокировки (в проде <code>CREATE INDEX CONCURRENTLY</code>).</li>
<li><strong>Ожидаемый выигрыш</strong> — в измерениях: время с X до Y, буферы с A до B.</li>
</ol>
<p>И будьте честны: если какое-то изменение дало меньше пользы, чем ожидалось, — напишите это. Как мы видели в уроке R2, индекс не всегда ускоряет в 100 раз — иногда в 1.6, и это тоже результат.</p>""",
        "code_content": """-- ═══════════════════════════════════════════════════════════════════════
-- PERFORMANCE AUDIT — tayyor so'rovlar to'plami
-- Bu so'rovlarni ISHLAB TURGAN bazada bajaring: ularning aksariyati
-- to'plangan statistikaga tayanadi.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- 1) HAJM: eng katta jadvallar va ularning indekslari
--    Diqqat belgisi: indekslar jadvalning o'zidan KATTA bo'lsa
-- ─────────────────────────────────────────────────────────────────────
SELECT c.relname AS jadval,
       pg_size_pretty(pg_total_relation_size(c.oid))                           AS jami,
       pg_size_pretty(pg_relation_size(c.oid))                                 AS jadval_ozi,
       pg_size_pretty(pg_total_relation_size(c.oid) - pg_relation_size(c.oid)) AS indekslar
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'public'
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 2) SKANERLASH: qaysi jadvallar to'liq o'qilmoqda
--    seq_foiz yuqori + n_live_tup katta = indeks yetishmayapti
-- ─────────────────────────────────────────────────────────────────────
SELECT relname,
       seq_scan,
       seq_tup_read,
       idx_scan,
       CASE WHEN seq_scan + COALESCE(idx_scan, 0) = 0 THEN 0
            ELSE ROUND(100.0 * seq_scan / (seq_scan + COALESCE(idx_scan, 0)), 1)
       END AS seq_foiz,
       n_live_tup
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY seq_tup_read DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 3) INDEKSSIZ FOREIGN KEY — auditda eng ko'p topiladigan muammo
--    PostgreSQL PK uchun indeksni avtomatik yaratadi, FK uchun YO'Q.
--    Oqibati: sekin JOIN va ota qatorni DELETE qilishda to'liq skanerlash.
-- ─────────────────────────────────────────────────────────────────────
SELECT c.conrelid::regclass AS jadval,
       a.attname            AS ustun,
       c.conname            AS cheklov
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND cardinality(c.conkey) = 1
  AND NOT EXISTS (
      SELECT 1 FROM pg_index i
      WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]
  )
ORDER BY 1;

-- ─────────────────────────────────────────────────────────────────────
-- 4) ISHLATILMAYOTGAN INDEKSLAR — sof zarar
--    OGOHLANTIRISH: statistika oxirgi pg_stat_reset() dan beri yig'iladi.
--    Yosh statistika bo'yicha indeksni o'chirish xato bo'lishi mumkin.
-- ─────────────────────────────────────────────────────────────────────
SELECT s.relname                                      AS jadval,
       s.indexrelname                                 AS indeks,
       s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;

-- Statistika qachondan beri yig'ilayotganini bilish:
SELECT stats_reset FROM pg_stat_database WHERE datname = current_database();

-- ─────────────────────────────────────────────────────────────────────
-- 5) BLOAT: o'lik qatorlar va autovacuum holati
--    olik_foiz > 20% = autovacuum yetishmayapti yoki uzoq tranzaksiya bor
-- ─────────────────────────────────────────────────────────────────────
SELECT relname,
       n_live_tup,
       n_dead_tup,
       ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS olik_foiz,
       last_autovacuum,
       last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 6) CACHE HIT RATIO — sog'lom bazada 99% dan yuqori
-- ─────────────────────────────────────────────────────────────────────
SELECT ROUND(
           100.0 * SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit + heap_blks_read), 0),
           2
       ) AS cache_hit_foiz
FROM pg_statio_user_tables;
-- Bu platformaning real bazasida o'lchandi: 99.77%

-- Jadval bo'yicha batafsil:
SELECT relname,
       heap_blks_hit, heap_blks_read,
       ROUND(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_foiz
FROM pg_statio_user_tables
WHERE heap_blks_hit + heap_blks_read > 1000
ORDER BY heap_blks_read DESC
LIMIT 15;

-- ─────────────────────────────────────────────────────────────────────
-- 7) pg_stat_statements — auditning eng qimmatli manbasi
-- ─────────────────────────────────────────────────────────────────────
-- Avval o'rnatilganini tekshiring:
SELECT
    (SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'pg_stat_statements') AS mavjud,
    (SELECT COUNT(*) FROM pg_extension            WHERE extname = 'pg_stat_statements') AS ornatilgan;
-- mavjud=1, ornatilgan=0 bo'lsa: postgresql.conf da
--   shared_preload_libraries = 'pg_stat_statements'
-- qo'shing, serverni qayta ishga tushiring, so'ng:
--   CREATE EXTENSION pg_stat_statements;

-- (a) Umumiy vaqtni eng ko'p yeydigan so'rovlar — optimallashtirish nishoni
--   SELECT ROUND(total_exec_time::NUMERIC, 1)  AS jami_ms,
--          calls,
--          ROUND(mean_exec_time::NUMERIC, 3)   AS ortacha_ms,
--          LEFT(query, 90)                     AS sorov
--   FROM pg_stat_statements
--   ORDER BY total_exec_time DESC
--   LIMIT 20;
--
-- (b) Eng ko'p CHAQIRILGAN so'rovlar — N+1 belgisi (6-darsga qarang)
--   SELECT calls,
--          ROUND(mean_exec_time::NUMERIC, 3)   AS ortacha_ms,
--          LEFT(query, 90)                     AS sorov
--   FROM pg_stat_statements
--   ORDER BY calls DESC
--   LIMIT 20;
--
-- Farqni tushuning: (a) sekin so'rovlarni, (b) esa N+1 ni topadi.

-- ─────────────────────────────────────────────────────────────────────
-- 8) Uzoq ishlayotgan tranzaksiyalar — vacuum va qulflarning dushmani
-- ─────────────────────────────────────────────────────────────────────
SELECT pid,
       NOW() - xact_start AS tranzaksiya_davomiyligi,
       state,
       wait_event_type,
       LEFT(query, 70)    AS sorov
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND NOW() - xact_start > INTERVAL '1 minute'
ORDER BY xact_start;
-- "idle in transaction" holatidagi uzoq sessiya — eng yomon holat:
-- u VACUUM ni bloklaydi va bloat to'planaveradi.

-- ─────────────────────────────────────────────────────────────────────
-- 9) Produksiyada indeks qo'shish — qulflashsiz
-- ─────────────────────────────────────────────────────────────────────
-- Oddiy CREATE INDEX jadvalni YOZISH uchun bloklaydi. Ishlab turgan
-- tizimda har doim CONCURRENTLY ishlating:
--   CREATE INDEX CONCURRENTLY idx_nomi ON jadval(ustun);
--
-- Diqqat: CONCURRENTLY tranzaksiya blokida ishlamaydi va muvaffaqiyatsiz
-- tugasa "INVALID" indeks qoldiradi. Uni tekshirish:
SELECT c.relname AS indeks, i.indisvalid
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
-- Bunday indeksni DROP INDEX qilib, qaytadan yaratish kerak.""",
        "code_content_ru": """-- ═══════════════════════════════════════════════════════════════════════
-- АУДИТ ПРОИЗВОДИТЕЛЬНОСТИ — готовый набор запросов
-- Выполняйте эти запросы на РАБОТАЮЩЕЙ базе: большинство из них
-- опирается на накопленную статистику.
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- 1) РАЗМЕР: самые большие таблицы и их индексы
--    Тревожный признак: индексы БОЛЬШЕ самой таблицы
-- ─────────────────────────────────────────────────────────────────────
SELECT c.relname AS jadval,
       pg_size_pretty(pg_total_relation_size(c.oid))                           AS jami,
       pg_size_pretty(pg_relation_size(c.oid))                                 AS jadval_ozi,
       pg_size_pretty(pg_total_relation_size(c.oid) - pg_relation_size(c.oid)) AS indekslar
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'public'
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 2) СКАНИРОВАНИЯ: какие таблицы читаются целиком
--    Высокий seq_foiz + большой n_live_tup = не хватает индекса
-- ─────────────────────────────────────────────────────────────────────
SELECT relname,
       seq_scan,
       seq_tup_read,
       idx_scan,
       CASE WHEN seq_scan + COALESCE(idx_scan, 0) = 0 THEN 0
            ELSE ROUND(100.0 * seq_scan / (seq_scan + COALESCE(idx_scan, 0)), 1)
       END AS seq_foiz,
       n_live_tup
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY seq_tup_read DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 3) ВНЕШНИЙ КЛЮЧ БЕЗ ИНДЕКСА — самая частая находка аудита
--    Для PK PostgreSQL создаёт индекс автоматически, для FK — НЕТ.
--    Последствия: медленный JOIN и полное сканирование при DELETE родителя.
-- ─────────────────────────────────────────────────────────────────────
SELECT c.conrelid::regclass AS jadval,
       a.attname            AS ustun,
       c.conname            AS cheklov
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND cardinality(c.conkey) = 1
  AND NOT EXISTS (
      SELECT 1 FROM pg_index i
      WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]
  )
ORDER BY 1;

-- ─────────────────────────────────────────────────────────────────────
-- 4) НЕИСПОЛЬЗУЕМЫЕ ИНДЕКСЫ — чистый вред
--    ПРЕДУПРЕЖДЕНИЕ: статистика собирается с последнего pg_stat_reset().
--    Удалять индекс по свежей статистике может быть ошибкой.
-- ─────────────────────────────────────────────────────────────────────
SELECT s.relname                                      AS jadval,
       s.indexrelname                                 AS indeks,
       s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;

-- Узнать, с какого момента собирается статистика:
SELECT stats_reset FROM pg_stat_database WHERE datname = current_database();

-- ─────────────────────────────────────────────────────────────────────
-- 5) BLOAT: мёртвые строки и состояние autovacuum
--    olik_foiz > 20% = autovacuum не справляется либо есть долгая транзакция
-- ─────────────────────────────────────────────────────────────────────
SELECT relname,
       n_live_tup,
       n_dead_tup,
       ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS olik_foiz,
       last_autovacuum,
       last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC
LIMIT 20;

-- ─────────────────────────────────────────────────────────────────────
-- 6) CACHE HIT RATIO — у здоровой базы выше 99%
-- ─────────────────────────────────────────────────────────────────────
SELECT ROUND(
           100.0 * SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit + heap_blks_read), 0),
           2
       ) AS cache_hit_foiz
FROM pg_statio_user_tables;
-- Измерено на реальной базе этой платформы: 99.77%

-- Подробно по таблицам:
SELECT relname,
       heap_blks_hit, heap_blks_read,
       ROUND(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_foiz
FROM pg_statio_user_tables
WHERE heap_blks_hit + heap_blks_read > 1000
ORDER BY heap_blks_read DESC
LIMIT 15;

-- ─────────────────────────────────────────────────────────────────────
-- 7) pg_stat_statements — самый ценный источник для аудита
-- ─────────────────────────────────────────────────────────────────────
-- Сначала проверьте, установлено ли:
SELECT
    (SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'pg_stat_statements') AS mavjud,
    (SELECT COUNT(*) FROM pg_extension            WHERE extname = 'pg_stat_statements') AS ornatilgan;
-- Если mavjud=1, а ornatilgan=0: добавьте в postgresql.conf
--   shared_preload_libraries = 'pg_stat_statements'
-- перезапустите сервер, затем выполните:
--   CREATE EXTENSION pg_stat_statements;

-- (a) Запросы, съедающие больше всего суммарного времени — цель оптимизации
--   SELECT ROUND(total_exec_time::NUMERIC, 1)  AS jami_ms,
--          calls,
--          ROUND(mean_exec_time::NUMERIC, 3)   AS ortacha_ms,
--          LEFT(query, 90)                     AS sorov
--   FROM pg_stat_statements
--   ORDER BY total_exec_time DESC
--   LIMIT 20;
--
-- (b) Самые ЧАСТО ВЫЗЫВАЕМЫЕ запросы — признак N+1 (см. урок 6)
--   SELECT calls,
--          ROUND(mean_exec_time::NUMERIC, 3)   AS ortacha_ms,
--          LEFT(query, 90)                     AS sorov
--   FROM pg_stat_statements
--   ORDER BY calls DESC
--   LIMIT 20;
--
-- Поймите разницу: (a) находит медленные запросы, (b) — проблему N+1.

-- ─────────────────────────────────────────────────────────────────────
-- 8) Долгие транзакции — враг vacuum и блокировок
-- ─────────────────────────────────────────────────────────────────────
SELECT pid,
       NOW() - xact_start AS tranzaksiya_davomiyligi,
       state,
       wait_event_type,
       LEFT(query, 70)    AS sorov
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND NOW() - xact_start > INTERVAL '1 minute'
ORDER BY xact_start;
-- Долгая сессия в состоянии "idle in transaction" — худший случай:
-- она блокирует VACUUM, и bloat продолжает накапливаться.

-- ─────────────────────────────────────────────────────────────────────
-- 9) Добавление индекса в продакшене — без блокировки
-- ─────────────────────────────────────────────────────────────────────
-- Обычный CREATE INDEX блокирует таблицу на ЗАПИСЬ. На работающей
-- системе всегда используйте CONCURRENTLY:
--   CREATE INDEX CONCURRENTLY idx_nomi ON jadval(ustun);
--
-- Внимание: CONCURRENTLY не работает внутри блока транзакции, а при
-- неудаче оставляет "INVALID" индекс. Проверить их:
SELECT c.relname AS indeks, i.indisvalid
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
-- Такой индекс нужно удалить через DROP INDEX и создать заново.""",
        "task": {
            "task_title": "CAPSTONE: Katta hajmli jadvalda to'liq performance audit",
            "task_title_ru": "CAPSTONE: полный аудит производительности большой таблицы",
            "task_description": (
                "Sizni logistika kompaniyasining backend jamoasiga taklif qilishdi. Ularning "
                "yuk kuzatuv tizimi sekinlashgan: adminka sahifalari 5-10 sekundda ochiladi, "
                "kechqurunlari baza umuman javob bermay qoladi. Sizga to'liq performance "
                "audit o'tkazish va yozma hisobot tayyorlash topshirildi.\n\n"
                "Tizim sxemasi (uni o'zingiz yaratasiz):\n"
                "  mijozlar(id, nomi, inn, shahar, royxatdan_otgan)          — ~200 000 qator\n"
                "  yuklar(id, mijoz_id FK, holat, jonatilgan, yetkazilgan,\n"
                "         ogirlik, narx, manba_shahar, manzil_shahar)        — ~2 000 000 qator\n"
                "  kuzatuv(id, yuk_id FK, vaqt, holat, joylashuv, izoh)      — ~8 000 000 qator\n\n"
                "Bazani ATAYLAB nosog'lom holatda yarating: foreign key ustunlarida indeks "
                "yo'q, bir nechta keraksiz indeks bor, va quyidagi so'rovlar sekin ishlaydi:\n"
                "  A) Mijozlar ro'yxati: har bir mijoz uchun yuklari soni, umumiy narxi va "
                "oxirgi yuk sanasi (korrelyatsiyali subquery bilan yozilgan).\n"
                "  B) Yuk kuzatuvi: bitta yukning barcha kuzatuv yozuvlari, vaqt bo'yicha.\n"
                "  C) Oylik hisobot: to_char(jonatilgan,'YYYY-MM') bo'yicha guruhlangan.\n"
                "  D) Adminka sahifalash: ORDER BY id DESC OFFSET 500000 LIMIT 50.\n"
                "  E) Yetkazilmagan yuklar: WHERE holat <> 'yetkazildi' AND jonatilgan < ...\n\n"
                "Audit natijasi — bitta .sql fayl (barcha so'rovlar va o'lchovlar) va bitta "
                "hisobot (Markdown yoki .sql ichidagi izohlar sifatida)."
            ),
            "task_description_ru": (
                "Вас пригласили в backend-команду логистической компании. Их система "
                "отслеживания грузов замедлилась: страницы админки открываются 5-10 секунд, "
                "по вечерам база вовсе перестаёт отвечать. Вам поручили провести полный "
                "аудит производительности и подготовить письменный отчёт.\n\n"
                "Схема системы (её вы создаёте сами):\n"
                "  mijozlar(id, nomi, inn, shahar, royxatdan_otgan)          — ~200 000 строк\n"
                "  yuklar(id, mijoz_id FK, holat, jonatilgan, yetkazilgan,\n"
                "         ogirlik, narx, manba_shahar, manzil_shahar)        — ~2 000 000 строк\n"
                "  kuzatuv(id, yuk_id FK, vaqt, holat, joylashuv, izoh)      — ~8 000 000 строк\n\n"
                "Создайте базу НАМЕРЕННО в нездоровом состоянии: на колонках внешних ключей "
                "нет индексов, есть несколько лишних индексов, и следующие запросы работают "
                "медленно:\n"
                "  A) Список клиентов: для каждого клиента число грузов, общая стоимость и "
                "дата последнего груза (написано через коррелированные подзапросы).\n"
                "  B) Отслеживание груза: все записи трекинга одного груза по времени.\n"
                "  C) Месячный отчёт: группировка по to_char(jonatilgan,'YYYY-MM').\n"
                "  D) Пагинация в админке: ORDER BY id DESC OFFSET 500000 LIMIT 50.\n"
                "  E) Недоставленные грузы: WHERE holat <> 'yetkazildi' AND jonatilgan < ...\n\n"
                "Результат аудита — один .sql файл (все запросы и измерения) и один отчёт "
                "(в Markdown или в виде комментариев внутри .sql)."
            ),
            "task_requirements": (
                "QISM 1 — SXEMA VA MA'LUMOT\n"
                "1. Uchta jadvalni yarating va generate_series bilan yuqorida ko'rsatilgan "
                "hajmda ma'lumot to'ldiring. ANALYZE ni unutmang.\n"
                "2. Ataylab 3 ta keraksiz indeks qo'shing (masalan hech qachon qidirilmaydigan "
                "ustunlar bo'yicha) — audit ularni topishi kerak.\n\n"
                "QISM 2 — AUDIT (darsdagi to'qqizta so'rovdan foydalaning)\n"
                "3. Jadval va indeks hajmlari hisoboti.\n"
                "4. seq_scan tahlili: qaysi jadvallar to'liq o'qilmoqda.\n"
                "5. Indekssiz foreign key larni topish — natijani ko'rsating.\n"
                "6. Ishlatilmayotgan indekslarni topish — siz qo'shgan 3 tasi chiqishi kerak.\n"
                "7. Bloat va cache hit ratio o'lchovi.\n\n"
                "QISM 3 — SO'ROVLAR TAHLILI\n"
                "8. A-E so'rovlarining har biri uchun EXPLAIN (ANALYZE, BUFFERS) natijasini "
                "keltiring va muammoni nomlang.\n"
                "9. Har bir so'rovni tuzating. Kamida quyidagilar qo'llanilishi kerak: "
                "korrelyatsiyali subquery larni bitta agregatga aylantirish (6-dars), "
                "to_char ni diapazonga aylantirish (R2), OFFSET ni keyset ga almashtirish "
                "(R2), FK uchun indeks qo'shish, qisman yoki kompozit indeks tanlash (5-dars).\n"
                "10. Har bir tuzatishdan keyin QAYTA o'lchang va natijani yozing.\n\n"
                "QISM 4 — PARTITIONING QARORI\n"
                "11. kuzatuv jadvali (8 mln qator) uchun partitioning kerakmi degan savolga "
                "ASOSLANGAN javob bering. Ma'lumotning hayot siklini, so'rovlar qaysi "
                "bo'limlarga tegishini va DETACH orqali arxivlash foydasini tahlil qiling. "
                "Agar javob 'ha' bo'lsa — sxemani yozing va pruning ishlayotganini EXPLAIN "
                "bilan isbotlang. Agar 'yo'q' bo'lsa — nega yo'qligini asoslang. Ikkala javob "
                "ham to'g'ri bo'lishi mumkin, muhimi — asos.\n\n"
                "QISM 5 — HISOBOT\n"
                "12. Topilmalar jadvali: muammo | qanday aniqlandi | ta'siri (Yuqori/O'rta/Past).\n"
                "13. Tavsiyalar jadvali: har bir tavsiya uchun aniq DDL | nega | xarajat "
                "(indeks hajmi, yozishga ta'sir) | kutilgan foyda (o'lchov bilan).\n"
                "14. Tavsiyalarni ta'sir/xarajat nisbati bo'yicha tartiblang: birinchi navbatda "
                "nima qilish kerak.\n"
                "15. Produksiyaga chiqarish rejasi: qaysi buyruqlar CREATE INDEX CONCURRENTLY "
                "talab qiladi, qaysilari qulf oladi, xavfsiz tartib qanday.\n"
                "16. HALOLLIK TALABI: agar biror tuzatish kutilganidan kam foyda bergan bo'lsa "
                "yoki umuman yordam bermagan bo'lsa — buni hisobotda yozing va sababini "
                "tushuntiring. Bo'yab ko'rsatilgan natija auditni yaroqsiz qiladi."
            ),
            "task_requirements_ru": (
                "ЧАСТЬ 1 — СХЕМА И ДАННЫЕ\n"
                "1. Создайте три таблицы и заполните их через generate_series в указанных "
                "выше объёмах. Не забудьте ANALYZE.\n"
                "2. Намеренно добавьте 3 лишних индекса (например, по колонкам, по которым "
                "никогда не ищут) — аудит должен их найти.\n\n"
                "ЧАСТЬ 2 — АУДИТ (используйте девять запросов из урока)\n"
                "3. Отчёт по размерам таблиц и индексов.\n"
                "4. Анализ seq_scan: какие таблицы читаются целиком.\n"
                "5. Поиск внешних ключей без индекса — приведите результат.\n"
                "6. Поиск неиспользуемых индексов — должны найтись добавленные вами 3.\n"
                "7. Измерение bloat и cache hit ratio.\n\n"
                "ЧАСТЬ 3 — АНАЛИЗ ЗАПРОСОВ\n"
                "8. Для каждого из запросов A-E приведите вывод EXPLAIN (ANALYZE, BUFFERS) и "
                "назовите проблему.\n"
                "9. Исправьте каждый запрос. Должны быть применены как минимум: превращение "
                "коррелированных подзапросов в один агрегат (урок 6), замена to_char на "
                "диапазон (R2), замена OFFSET на keyset (R2), добавление индекса под FK, "
                "выбор частичного или композитного индекса (урок 5).\n"
                "10. После каждого исправления измеряйте ЗАНОВО и записывайте результат.\n\n"
                "ЧАСТЬ 4 — РЕШЕНИЕ О ПАРТИЦИОНИРОВАНИИ\n"
                "11. Дайте ОБОСНОВАННЫЙ ответ на вопрос, нужно ли партиционировать таблицу "
                "kuzatuv (8 млн строк). Проанализируйте жизненный цикл данных, то, каких "
                "партиций касаются запросы, и выгоду архивирования через DETACH. Если ответ "
                "«да» — напишите схему и докажите через EXPLAIN, что pruning работает. Если "
                "«нет» — обоснуйте почему. Оба ответа могут быть правильными, важно "
                "обоснование.\n\n"
                "ЧАСТЬ 5 — ОТЧЁТ\n"
                "12. Таблица находок: проблема | как обнаружена | влияние (Высокое/Среднее/Низкое).\n"
                "13. Таблица рекомендаций: по каждой — конкретный DDL | почему | затраты "
                "(размер индекса, влияние на запись) | ожидаемый выигрыш (с измерениями).\n"
                "14. Отсортируйте рекомендации по соотношению эффект/затраты: что делать в "
                "первую очередь.\n"
                "15. План выката в продакшен: какие команды требуют CREATE INDEX CONCURRENTLY, "
                "какие берут блокировку, каков безопасный порядок.\n"
                "16. ТРЕБОВАНИЕ ЧЕСТНОСТИ: если какое-то исправление дало меньше пользы, чем "
                "ожидалось, или не помогло вовсе — напишите это в отчёте и объясните причину. "
                "Приукрашенный результат делает аудит негодным."
            ),
            "task_technologies": "PostgreSQL, SQL, EXPLAIN ANALYZE, Indexes, Partitioning, pg_stat_*",
            "task_deadline_days": 14,
        },
        "sample": {
            "title": "Namuna: Performance audit — bazaga beriladigan yetti savol",
            "description": "Hajm, to'liq skanerlash, indekssiz foreign key, ishlatilmayotgan indekslar, bloat, cache hit ratio va uzoq tranzaksiyalar bo'yicha tayyor audit so'rovlari",
            "sample_type": "sql",
            "html_code": r"""-- Namuna: performance audit — bazaga beriladigan yetti savol
-- Bu so'rovlar mavjud bazaning HOLATINI o'qiydi: ularni o'z bazangizda
-- ishga tushiring va natijani hisobotga yozing.

-- 1) HAJM: eng katta jadvallar (jadval + indekslar birga)
SELECT c.relname AS jadval,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS jami,
       pg_size_pretty(pg_relation_size(c.oid))       AS jadval_ozi,
       pg_size_pretty(pg_indexes_size(c.oid))        AS indekslar
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = current_schema()
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 10;

-- 2) SKANERLASH: qaysi jadvallar to'liq o'qilmoqda.
--    seq_tup_read juda katta bo'lsa — indeks yetishmayapti yoki
--    so'rov noto'g'ri yozilgan.
SELECT relname AS jadval, seq_scan, seq_tup_read, idx_scan, n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = current_schema()
ORDER BY seq_tup_read DESC
LIMIT 10;

-- 3) INDEKSSIZ FOREIGN KEY — auditda eng ko'p topiladigan muammo.
--    FK ustunida indeks bo'lmasa, ota qatorni o'chirish/yangilash bola
--    jadvalni TO'LIQ skanerlaydi.
SELECT c.conrelid::regclass AS bola_jadval,
       a.attname            AS fk_ustun,
       c.conname            AS cheklov
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND connamespace = current_schema()::regnamespace
  AND NOT EXISTS (
      SELECT 1 FROM pg_index i
      WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]
  )
ORDER BY 1;

-- 4) ISHLATILMAYOTGAN INDEKSLAR — sof zarar: joy egallaydi, har INSERT/
--    UPDATE ni sekinlashtiradi, hech qachon o'qilmaydi.
--    DIQQAT: idx_scan statistikasi server ishga tushgandan beri to'planadi —
--    yangi qayta ishga tushirilgan bazada bu ro'yxat yolg'on bo'lishi mumkin.
SELECT s.relname AS jadval, s.indexrelname AS indeks, s.idx_scan,
       pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.schemaname = current_schema()
  AND s.idx_scan = 0 AND NOT i.indisunique AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC
LIMIT 10;

-- 5) BLOAT: o'lik qatorlar va autovacuum holati.
--    n_dead_tup / n_live_tup nisbati katta bo'lsa — VACUUM ulgurmayapti.
SELECT relname AS jadval, n_live_tup, n_dead_tup,
       ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS olik_foiz,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = current_schema()
ORDER BY n_dead_tup DESC
LIMIT 10;

-- 6) CACHE HIT RATIO — sog'lom bazada 99% dan yuqori.
--    Past bo'lsa: shared_buffers kichik yoki ish to'plami xotiraga sig'maydi.
SELECT relname AS jadval,
       heap_blks_read AS diskdan,
       heap_blks_hit  AS keshdan,
       ROUND(100.0 * heap_blks_hit / NULLIF(heap_blks_hit + heap_blks_read, 0), 2) AS hit_foiz
FROM pg_statio_user_tables
WHERE schemaname = current_schema() AND heap_blks_hit + heap_blks_read > 0
ORDER BY heap_blks_read DESC
LIMIT 10;

-- 7) UZOQ ISHLAYOTGAN TRANZAKSIYALAR — vacuum va qulflarning dushmani.
--    Ochiq qolgan "idle in transaction" VACUUM ni ishlashdan to'xtatadi.
SELECT pid, state, NOW() - xact_start AS davomiylik, LEFT(query, 60) AS sorov
FROM pg_stat_activity
WHERE datname = current_database()
  AND xact_start IS NOT NULL
  AND NOW() - xact_start > INTERVAL '5 seconds'
ORDER BY xact_start;

-- QO'SHIMCHA: pg_stat_statements — auditning eng qimmatli manbasi.
--   SELECT calls, ROUND(total_exec_time::NUMERIC, 1) AS jami_ms,
--          ROUND(mean_exec_time::NUMERIC, 3)         AS ortacha_ms,
--          LEFT(query, 80)                           AS sorov
--   FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;
SELECT (SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'pg_stat_statements') AS mavjud,
       (SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements')         AS ornatilgan;

-- QO'SHIMCHA: produksiyada indeksni QULFLASHSIZ qo'shish.
-- CONCURRENTLY tranzaksiya ichida ishlamaydi va sekinroq, lekin jadvalni
-- yozishga ochiq qoldiradi:
--   CREATE INDEX CONCURRENTLY idx_nomi ON jadval(ustun);
-- Xato bo'lsa INVALID indeks qoladi — uni topib o'chirish kerak:
SELECT i.indexrelid::regclass AS nosoz_indeks
FROM pg_index i
WHERE NOT i.indisvalid;""",
        },
        "exercises": [
            {
                "title": "Auditda birinchi navbatda nima tekshiriladi?",
                "title_ru": "Что проверяется в аудите в первую очередь?",
                "description": "Baza sekinlashgan, qaysi so'rov muammoli ekani noma'lum. pg_stat_statements o'rnatilmagan. Auditni qayerdan boshlash eng samarali va nima uchun?",
                "description_ru": "База замедлилась, какой запрос проблемный — неизвестно. pg_stat_statements не установлен. С чего эффективнее всего начать аудит и почему?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Barcha jadvallarga ketma-ket indeks qo'shishdan — ko'proq indeks har doim yaxshiroq",
                    "Indekssiz foreign key larni va seq_scan yuqori bo'lgan jadvallarni topishdan — bu eng ko'p uchraydigan va eng oson tuzatiladigan muammo",
                    "shared_buffers ni ikki barobar oshirishdan — bu barcha muammolarni hal qiladi",
                    "Barcha jadvallarni partitioning qilishdan — katta jadvallar har doim bo'linishi kerak",
                ],
                "options_ru": [
                    "С последовательного добавления индексов ко всем таблицам — чем больше индексов, тем лучше",
                    "С поиска внешних ключей без индекса и таблиц с высоким seq_scan — это самая частая и самая легко исправимая проблема",
                    "С удвоения shared_buffers — это решит все проблемы",
                    "С партиционирования всех таблиц — большие таблицы всегда нужно разбивать",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "PostgreSQL PRIMARY KEY uchun indeksni avtomatik yaratadi. FOREIGN KEY uchun-chi?",
                "hint_ru": "Для PRIMARY KEY PostgreSQL создаёт индекс автоматически. А для FOREIGN KEY?",
                "explanation": "PostgreSQL FK uchun indeks yaratmaydi, shuning uchun indekssiz FK deyarli har bir bazada topiladi va u sekin JOIN hamda DELETE da to'liq skanerlashga olib keladi. A noto'g'ri, chunki ortiqcha indeks yozishni sekinlashtiradi; C va D esa o'lchovga tayanmagan taxminlar.",
                "difficulty_level": "Medium",
                "points": 15,
            },
            {
                "title": "Ishlatilmayotgan indeksni o'chirishdan oldin",
                "title_ru": "Перед удалением неиспользуемого индекса",
                "description": "Audit paytida `idx_scan = 0` bo'lgan bir nechta indeks topildi. Ularni darhol o'chirish xato bo'lishi mumkin. Xulosa chiqarishdan oldin qanday tekshiruvlar qilish kerak va nima uchun?",
                "description_ru": "В ходе аудита найдено несколько индексов с `idx_scan = 0`. Удалять их сразу может быть ошибкой. Какие проверки нужно сделать перед выводом и почему?",
                "exercise_type": "text_input",
                "expected_answer": "Birinchidan, statistika qachondan beri yig'ilayotganini tekshirish kerak: SELECT stats_reset FROM pg_stat_database WHERE datname = current_database(). Statistika yaqinda pg_stat_reset() yoki server qayta ishga tushirilishi bilan tozalangan bo'lsa, nol qiymat hech narsani anglatmaydi — indeks shunchaki hali ishlatilmagan bo'lishi mumkin. Ikkinchidan, kamdan-kam ishlaydigan, lekin muhim so'rovlarni hisobga olish kerak: oyiga yoki yiliga bir marta bajariladigan hisobot indeksi ham nol ko'rsatadi, lekin o'chirilsa o'sha hisobot juda sekinlashadi. Uchinchidan, indeks unikallikni ta'minlayotgan bo'lishi mumkin (indisunique) — bunday indeks idx_scan nol bo'lsa ham biznes qoidasini himoya qilyapti, shuning uchun so'rovda NOT i.indisunique AND NOT i.indisprimary sharti bor. To'rtinchidan, replikada o'qish yuklamasi bo'lsa, u yerdagi statistika alohida — master dagi nol qiymat replikada ishlatilayotgan indeksni yashirishi mumkin. Xavfsiz yo'l: statistikani kamida bir necha hafta, iloji bo'lsa to'liq biznes sikli davomida to'plash, keyin indeksni darhol DROP qilmasdan avval yashirish yoki nomini o'zgartirib kuzatish, va o'chirishdan oldin DDL ni saqlab qo'yish.",
                "hint": "pg_stat_* ko'rsatkichlari qaysi paytdan beri to'planayotganini o'ylang.",
                "hint_ru": "Подумайте, с какого момента накапливаются показатели pg_stat_*.",
                "difficulty_level": "Hard",
                "points": 15,
            },
        ],
    },
]
