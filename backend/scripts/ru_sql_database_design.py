"""Hand-authored Russian translations for course 98
"SQL: Ma'lumotlar Bazasi Dizayni" (13 lessons, 36 exercises).

Writes directly into translation_cache via write_ru_translations.py helpers,
exactly like the ru_algo_lesson_XX.py scripts do — one section_map per
lesson covering every string _collect_translatable_strings finds in
sections_json, plus the flat lesson fields and the exercise rows.

Note: exercise `options` and `drag_items` are deliberately NOT translated.
_NEVER_TRANSLATE_KEYS excludes them from sections_json (the render path),
and drag_and_drop grading compares the submitted items against the Uzbek
`correct_order`, so translating them would break grading.

Usage:
    cd backend
    python scripts/ru_sql_database_design.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

COURSE_ID = 98


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 826 — 1NF
# ═════════════════════════════════════════════════════════════════════════════
L1 = {
    "lesson_id": 826,
    "title": "1-Что такое нормализация и зачем она нужна (1NF)",
    "text": """\
<h3>Что такое нормализация?</h3>
<p><strong>Нормализация</strong> &mdash; это процесс такой перестройки таблиц, при котором каждый факт хранится в базе <em>ровно в одном месте</em>. Дело не в «красивой схеме». Если один факт (например, телефон клиента) продублирован в десяти строках, то рано или поздно девять из них обновят, а одну забудут &mdash; и ваша база начнёт противоречить сама себе.</p>
<p>В предыдущем курсе вы научились делать <code>SELECT</code> из готовой схемы. Этот курс отвечает на другой вопрос: <strong>почему</strong> та схема была устроена именно так?</p>

<h3>Зачем это нужно: три аномалии</h3>
<p>Плохо спроектированная таблица порождает три проблемы. В учебниках их называют «аномалиями»:</p>
<ul>
<li><strong>Аномалия вставки (INSERT)</strong> &mdash; чтобы записать новый факт, требуется другой факт, которого у вас ещё нет. Например, нельзя сохранить нового клиента, ещё не сделавшего ни одного заказа, потому что данные о клиенте живут только в таблице заказов.</li>
<li><strong>Аномалия обновления (UPDATE)</strong> &mdash; чтобы изменить один факт, нужно обновить несколько строк. Забудете одну &mdash; данные станут противоречивыми.</li>
<li><strong>Аномалия удаления (DELETE)</strong> &mdash; удаление одной строки уничтожает факт, который вы удалять не собирались. Удалите последний заказ клиента &mdash; и сам клиент исчезнет из базы.</li>
</ul>
<p>Нормализация &mdash; это оружие именно против этих трёх аномалий. И ни против чего другого.</p>

<h3>Первая нормальная форма (1NF)</h3>
<p>Таблица находится в 1NF, если:</p>
<ul>
<li>Значение в каждой ячейке <strong>атомарно</strong> (неделимо) &mdash; внутри не прячется список через запятую или JSON-массив.</li>
<li>В таблице нет <strong>повторяющихся групп</strong> &mdash; то есть нет пронумерованных колонок вида <code>товар_1</code>, <code>товар_2</code>, <code>товар_3</code>.</li>
<li>Каждая строка уникальна &mdash; то есть у таблицы есть первичный ключ (PRIMARY KEY).</li>
</ul>

<h3>До и после</h3>
<table>
<tr><th>Характеристика</th><th>До нормализации</th><th>После 1NF</th></tr>
<tr><td>Товары</td><td>в одной колонке TEXT: 'iPhone 15, Чехол'</td><td>каждый в отдельной строке</td></tr>
<tr><td>«Сколько чехлов продано?»</td><td><code>LIKE '%Chexol%'</code> &mdash; неверный результат</td><td><code>SUM(miqdor)</code> &mdash; точный ответ</td></tr>
<tr><td>Изменить количество</td><td>парсить текст вручную</td><td>обычный <code>UPDATE</code></td></tr>
<tr><td>Наложить ограничение</td><td>невозможно</td><td><code>CHECK (miqdor &gt; 0)</code></td></tr>
<tr><td>Индекс</td><td>бесполезен (поиск внутри текста)</td><td>прямо по колонке</td></tr>
</table>

<pre class="mermaid">
flowchart LR
  A["buyurtmalar_xom
mahsulotlar = 'iPhone 15, Chexol, Quloqchin'
miqdorlar = '1, 2, 1'"] -->|"1NF: каждое значение атомарно,
каждая строка уникальна"| B["buyurtma_qatorlari
1 строка = 1 товар
PRIMARY KEY (buyurtma_id, mahsulot_nomi)"]
</pre>

<h3>Самая частая ошибка</h3>
<p>Новички часто рассуждают так: «Запишу товары через запятую в одну колонку, а в приложении сделаю <code>split(',')</code> &mdash; так быстрее». Это использование базы данных как обычного файла. Вы моментально теряете: <code>JOIN</code>, <code>SUM</code>, <code>GROUP BY</code>, <code>FOREIGN KEY</code>, <code>CHECK</code>, индексы и транзакционную целостность. То есть весь смысл выбора базы данных.</p>
<p>Замечание: в PostgreSQL есть типы массивов (<code>text[]</code>) и <code>JSONB</code>, и в реальных проектах их используют &mdash; но не для <em>связываемых сущностей</em>, а для дополнительных данных с заранее неизвестной структурой, которые никогда не участвуют в <code>JOIN</code>. Товар &mdash; это сущность, поэтому он должен жить в отдельной строке.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- 1NF: до и после нормализации — реальный пример
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- ШАГ 1: «плохая» таблица. Товары через запятую в одной колонке TEXT.
-- Это повторяющаяся группа, то есть 1NF нарушена.
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtmalar_xom;

CREATE TABLE buyurtmalar_xom (
    buyurtma_id   INTEGER PRIMARY KEY,
    mijoz_ism     VARCHAR(60),
    mijoz_telefon VARCHAR(20),
    mahsulotlar   TEXT,   -- 'iPhone 15, Chexol, Quloqchin'  <- НЕ атомарно
    miqdorlar     TEXT    -- '1, 2, 1'                       <- НЕ атомарно
);

INSERT INTO buyurtmalar_xom VALUES
    (1, 'Aziz Karimov',     '+998901112233', 'iPhone 15, Chexol, Quloqchin', '1, 2, 1'),
    (2, 'Dilnoza Rasulova', '+998907778899', 'MacBook Pro',                  '1'),
    (3, 'Aziz Karimov',     '+998901112233', 'Chexol, Quloqchin',           '3, 2');

-- Вопрос: сколько всего продано «чехлов»? В этой таблице точного ответа НЕТ.
-- LIKE считает только СТРОКИ, а не количество:
SELECT COUNT(*) AS chexol_bor_buyurtmalar
FROM buyurtmalar_xom
WHERE mahsulotlar LIKE '%Chexol%';
-- Результат: 2. Но реально продано 2 + 3 = 5 штук.
-- Ещё хуже: если появится товар 'Chexol Pro', LIKE посчитает и его.
-- То есть ответ не просто неверный — он неверный молча.

-- Аномалия UPDATE: при смене телефона Азиза его нужно обновить в ДВУХ
-- строках. Забудете одну — в базе окажутся два разных телефона.
UPDATE buyurtmalar_xom
SET mijoz_telefon = '+998901110000'
WHERE buyurtma_id = 1;   -- заказ 3 остался со старым номером!

SELECT DISTINCT mijoz_ism, mijoz_telefon FROM buyurtmalar_xom;
-- Aziz Karimov выводится с двумя разными телефонами — данные испорчены.

-- ─────────────────────────────────────────────────────────────────────
-- ШАГ 2: приводим к 1NF. Каждый товар — отдельная строка.
-- Теперь в каждой ячейке одно неделимое (атомарное) значение.
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtma_qatorlari;

CREATE TABLE buyurtma_qatorlari (
    buyurtma_id   INTEGER      NOT NULL,
    mahsulot_nomi VARCHAR(60)  NOT NULL,
    miqdor        INTEGER      NOT NULL CHECK (miqdor > 0),
    mijoz_ism     VARCHAR(60)  NOT NULL,
    mijoz_telefon VARCHAR(20)  NOT NULL,
    -- Составной первичный ключ: в одном заказе товар встречается один раз
    PRIMARY KEY (buyurtma_id, mahsulot_nomi)
);

INSERT INTO buyurtma_qatorlari VALUES
    (1, 'iPhone 15',  1, 'Aziz Karimov',     '+998901112233'),
    (1, 'Chexol',     2, 'Aziz Karimov',     '+998901112233'),
    (1, 'Quloqchin',  1, 'Aziz Karimov',     '+998901112233'),
    (2, 'MacBook Pro',1, 'Dilnoza Rasulova', '+998907778899'),
    (3, 'Chexol',     3, 'Aziz Karimov',     '+998901112233'),
    (3, 'Quloqchin',  2, 'Aziz Karimov',     '+998901112233');

-- Теперь на вопрос есть ТОЧНЫЙ ответ — достаточно обычного агрегата:
SELECT mahsulot_nomi, SUM(miqdor) AS jami_sotilgan
FROM buyurtma_qatorlari
GROUP BY mahsulot_nomi
ORDER BY jami_sotilgan DESC;
-- Chexol -> 5. Правильный ответ.

-- Бонус: теперь работают и ограничения. Отрицательное количество база
-- отвергнет сама:
-- INSERT INTO buyurtma_qatorlari VALUES (4, 'Chexol', -1, 'X', '+998900000000');
-- ERROR:  new row violates check constraint "buyurtma_qatorlari_miqdor_check"

-- ─────────────────────────────────────────────────────────────────────
-- ВАЖНО: эта таблица уже в 1NF, НО всё ещё не идеальна.
-- mijoz_ism и mijoz_telefon дублируются в каждой строке — аномалия
-- UPDATE никуда не делась. Её решают 2NF и 3NF (следующий урок).
-- ─────────────────────────────────────────────────────────────────────
SELECT buyurtma_id, mijoz_ism, COUNT(*) AS takrorlanish
FROM buyurtma_qatorlari
GROUP BY buyurtma_id, mijoz_ism
ORDER BY buyurtma_id;
""",
    "exercises": {
        4746: {
            "title": "Главное требование 1NF",
            "description": "Какими должны быть значения в колонках, чтобы таблица находилась в Первой нормальной форме (1NF)?",
            "hint": "Если в одной ячейке лежит список через запятую — это требование нарушено.",
            "explanation": "Главное требование 1NF — атомарность: в каждой ячейке должно находиться только одно неделимое значение. Список вида 'iPhone, Chexol, Quloqchin' это требование нарушает.",
        },
        4747: {
            "title": "Название аномалии",
            "description": "Телефон клиента продублирован в 10 строках. При смене номера обновились 9 строк, а одна осталась со старым значением — в базе возникло противоречие. Как называется эта аномалия? Заполните пропуск одним словом: аномалия ___.",
            "hint": "Проблема возникает в момент изменения данных.",
            "explanation": "Если для изменения одного факта нужно обновить несколько строк и одну из них забыли — это аномалия UPDATE (обновления).",
        },
        4748: {
            "title": "Шаги приведения к 1NF",
            "description": "Расположите в правильном порядке шаги приведения к 1NF таблицы, хранящей список через запятую.",
            "hint": "Сначала находим проблему, затем разносим по строкам, затем ключ и ограничения.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 827 — 2NF и 3NF
# ═════════════════════════════════════════════════════════════════════════════
L2 = {
    "lesson_id": 827,
    "title": "2-2NF и 3NF — избавляемся от дублирования данных",
    "text": """\
<h3>1NF оказалось недостаточно</h3>
<p>В прошлом уроке мы привели таблицу к 1NF, но проблема осталась: <code>mijoz_ism</code> и <code>mijoz_telefon</code> продолжали дублироваться в каждой строке. Именно это дублирование устраняют 2NF и 3NF.</p>
<p>Обе формы &mdash; это два этапа одной идеи: <strong>каждая неключевая колонка должна зависеть от всего первичного ключа, только от него и ни от чего больше</strong>.</p>

<h3>Функциональная зависимость &mdash; ключевое понятие</h3>
<p>Если значение колонки <code>A</code> однозначно определяет значение колонки <code>B</code>, это записывают как <code>A &rarr; B</code> и говорят «B функционально зависит от A». Например, <code>mijoz_id &rarr; mijoz_telefon</code>: зная номер клиента, мы знаем и его телефон.</p>

<h3>Вторая нормальная форма (2NF): устраняем частичную зависимость</h3>
<p>2NF имеет смысл только для таблиц с <strong>составным</strong> (из нескольких колонок) первичным ключом. Правило: ни одна неключевая колонка не должна зависеть от <em>части</em> ключа.</p>
<p>Пример: в таблице с <code>PRIMARY KEY (buyurtma_id, mahsulot_nomi)</code> есть колонка <code>mahsulot_narxi</code>. Цена зависит только от <code>mahsulot_nomi</code> и вообще не связана с <code>buyurtma_id</code> &mdash; это <strong>частичная зависимость</strong> (partial dependency). В результате цена одного товара дублируется в десятках строк.</p>

<h3>Третья нормальная форма (3NF): устраняем транзитивную зависимость</h3>
<p>Правило 3NF: ни одна неключевая колонка не должна быть связана с ключом через другую неключевую колонку.</p>
<p>Пример: <code>buyurtmalar(buyurtma_id PK, mijoz_id, mijoz_shahri, shahar_viloyati)</code>. Здесь есть цепочка <code>buyurtma_id &rarr; mijoz_shahri &rarr; shahar_viloyati</code>. Область на самом деле зависит не от заказа, а от города &mdash; это <strong>транзитивная зависимость</strong> (transitive dependency).</p>

<h3>Коротко, чтобы запомнить</h3>
<table>
<tr><th>Форма</th><th>Что требует</th><th>Что устраняет</th></tr>
<tr><td>1NF</td><td>Атомарные значения, нет повторяющихся групп</td><td>Колонки, хранящие списки</td></tr>
<tr><td>2NF</td><td>1NF + нет зависимости от части ключа</td><td>Частичную зависимость</td></tr>
<tr><td>3NF</td><td>2NF + нет зависимости неключевая &rarr; неключевая</td><td>Транзитивную зависимость</td></tr>
</table>
<p>Классическая мнемоника: <em>«каждая неключевая колонка зависит от ключа, от всего ключа и только от ключа»</em>. «От ключа» &mdash; 1NF, «от всего ключа» &mdash; 2NF, «только от ключа» &mdash; 3NF.</p>

<pre class="mermaid">
flowchart TB
  A["buyurtma_qatorlari (1NF)
buyurtma_id, mahsulot_nomi, miqdor,
mahsulot_narxi, mijoz_ism, mijoz_telefon, mijoz_shahri, shahar_viloyati"]
  A -->|"2NF: mahsulot_narxi зависит
только от mahsulot_nomi"| B["mahsulotlar
id PK, nomi, narx"]
  A -->|"3NF: область зависит от города,
город — от клиента"| C["mijozlar
id PK, ism, telefon, shahar_id"]
  C --> D["shaharlar
id PK, nomi, viloyat"]
  A -->|"остаток"| E["buyurtma_elementlari
buyurtma_id, mahsulot_id, miqdor"]
</pre>

<h3>Практическая польза</h3>
<p>После нормализации изменение цены товара &mdash; это один <code>UPDATE mahsulotlar SET narx = ... WHERE id = ...</code>. До нормализации пришлось бы обновлять сотни строк, и одну из них всегда забывали. Это не теория &mdash; это самая частая причина порчи данных в реальных проектах.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- 2NF и 3NF: пошаговая нормализация плоской таблицы
-- ═══════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────
-- ИСХОДНОЕ СОСТОЯНИЕ: в 1NF, но 2NF и 3NF нарушены
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS buyurtmalar_yassi;

CREATE TABLE buyurtmalar_yassi (
    buyurtma_id     INTEGER      NOT NULL,
    mahsulot_nomi   VARCHAR(60)  NOT NULL,
    miqdor          INTEGER      NOT NULL CHECK (miqdor > 0),
    -- Нарушение 2NF: цена зависит ТОЛЬКО от части ключа (mahsulot_nomi)
    mahsulot_narxi  NUMERIC(12,2) NOT NULL,
    -- Нарушение 3NF: город зависит от клиента, а область — от города
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

-- Показываем проблему: цена iPhone продублирована в 2 строках, цена
-- чехла — тоже в 2. Чтобы поднять цену, нужно обновить ВСЕ строки.
SELECT mahsulot_nomi, COUNT(*) AS narx_necha_marta_takrorlangan
FROM buyurtmalar_yassi
GROUP BY mahsulot_nomi;

-- ─────────────────────────────────────────────────────────────────────
-- 2NF: выносим частичную зависимость -> товары в отдельную таблицу
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
-- 3NF: выносим транзитивную зависимость.
-- shahar_viloyati -> в таблицу shaharlar, город -> в таблицу mijozlar.
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

-- Связующая таблица: остались только колонки, зависящие от ПОЛНОГО
-- составного ключа
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER NOT NULL REFERENCES mahsulotlar(id),
    miqdor      INTEGER NOT NULL CHECK (miqdor > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)
);

-- ── Переносим данные ─────────────────────────────────────────────────
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

-- Сдвигаем счётчик SERIAL за пределы вручную вставленных id
SELECT setval('buyurtmalar_id_seq', (SELECT MAX(id) FROM buyurtmalar));

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor)
SELECT y.buyurtma_id, p.id, y.miqdor
FROM buyurtmalar_yassi y
JOIN mahsulotlar p ON p.nomi = y.mahsulot_nomi;

-- ─────────────────────────────────────────────────────────────────────
-- РЕЗУЛЬТАТ: цена теперь в ОДНОМ месте. Один UPDATE — изменилось везде.
-- ─────────────────────────────────────────────────────────────────────
UPDATE mahsulotlar SET narx = 16000000 WHERE nomi = 'iPhone 15';

-- Собираем прежнее плоское представление обратно через JOIN —
-- данные не потерялись, они просто разложены по своим местам.
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
""",
    "exercises": {
        4749: {
            "title": "Какую нормальную форму нарушает частичная зависимость?",
            "description": "В таблице с PRIMARY KEY (buyurtma_id, mahsulot_id) есть колонка mahsulot_narxi, которая зависит только от mahsulot_id. Требование какой нормальной формы это нарушает?",
            "hint": "Зависимость от части ключа — как называется такая зависимость?",
            "explanation": "Если неключевая колонка зависит только от части составного ключа — это частичная зависимость (partial dependency), и она нарушает именно требование 2NF.",
        },
        4750: {
            "title": "Название транзитивной зависимости",
            "description": "В таблице buyurtmalar(buyurtma_id PK, mijoz_shahri, shahar_viloyati) есть цепочка buyurtma_id -> mijoz_shahri -> shahar_viloyati. Как называется такая зависимость? (напишите двумя словами)",
            "hint": "Неключевая колонка связана с ключом через другую неключевую колонку.",
            "expected_answer": "транзитивная зависимость",
        },
        4751: {
            "title": "Верные утверждения о 3NF",
            "description": "Какие из утверждений о 3NF верны?",
            "hint": "Одно из них про ограничение UNIQUE — оно вообще не имеет отношения к нормализации.",
            "explanation": "Нормальные формы идут последовательно: 3NF прежде всего требует 2NF, запрещает (транзитивную) зависимость между неключевыми колонками и тем самым уменьшает аномалию UPDATE. Требования делать все колонки UNIQUE нет ни в одной нормальной форме.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 828 — BCNF
# ═════════════════════════════════════════════════════════════════════════════
L3 = {
    "lesson_id": 828,
    "title": "3-BCNF и границы нормализации",
    "text": """\
<h3>Случай, когда 3NF недостаточно</h3>
<p>3NF очень сильна, но оставляет одну лазейку. Правило 3NF проверяет неключевые колонки &mdash; однако если в <em>левой части</em> зависимости стоит неключевая колонка, а в правой &mdash; часть ключа, 3NF этого просто не замечает.</p>
<p>Правило <strong>нормальной формы Бойса-Кодда (BCNF)</strong> гораздо проще и строже: <em>в любой функциональной зависимости <code>X &rarr; Y</code> величина <code>X</code> обязана быть потенциальным ключом (candidate key)</em>. Если это не так &mdash; таблица не в BCNF.</p>

<h3>Классический пример: преподаватель &rarr; предмет</h3>
<p>Рассмотрим университетскую таблицу <code>darslar(talaba_id, fan, oqituvchi)</code>.</p>
<p>Бизнес-правила:</p>
<ul>
<li>Один студент изучает один предмет только у одного преподавателя &rarr; <code>(talaba_id, fan) &rarr; oqituvchi</code></li>
<li>Каждый преподаватель ведёт только один предмет &rarr; <code>oqituvchi &rarr; fan</code></li>
</ul>
<p>Потенциальные ключи: <code>(talaba_id, fan)</code> и <code>(talaba_id, oqituvchi)</code>. Неключевых колонок в таблице нет вообще &mdash; значит, 3NF <strong>не нарушена</strong>. Но левая часть зависимости <code>oqituvchi &rarr; fan</code> (то есть <code>oqituvchi</code>) ключом не является. Значит, BCNF нарушена.</p>
<p>Последствия очевидны: факт «Каримов &mdash; преподаватель физики» дублируется для каждого записанного к нему студента. Если Каримов перейдёт на химию, придётся обновить десятки строк. И самое неприятное: нового преподавателя, у которого ещё нет ни одного студента, вообще невозможно завести в базе (аномалия INSERT).</p>

<h3>Решение</h3>
<p>Разбиваем таблицу надвое: <code>oqituvchilar(oqituvchi PK, fan)</code> и <code>royxat(talaba_id, oqituvchi)</code>. Теперь обе таблицы в BCNF.</p>
<p>Стоит быть честным: это разбиение кое-что <em>теряет</em>. Правило «студент не изучает один предмет у двух преподавателей» больше нельзя обеспечить одной лишь структурой таблиц &mdash; для него нужен отдельный <code>UNIQUE</code> или триггер. Это известная цена BCNF: она не всегда сохраняет зависимости (dependency preservation).</p>

<table>
<tr><th>Форма</th><th>Правило</th><th>Насколько нужна на практике</th></tr>
<tr><td>1NF</td><td>Атомарные значения</td><td>Обязательна всегда</td></tr>
<tr><td>2NF</td><td>Нет частичных зависимостей</td><td>Обязательна всегда</td></tr>
<tr><td>3NF</td><td>Нет транзитивных зависимостей</td><td>Практический стандарт &mdash; 95% проектов останавливаются здесь</td></tr>
<tr><td>BCNF</td><td>Каждый детерминант &mdash; потенциальный ключ</td><td>Когда есть несколько перекрывающихся потенциальных ключей</td></tr>
<tr><td>4NF / 5NF</td><td>Многозначные зависимости</td><td>Редко, в основном теория</td></tr>
</table>

<h3>Избыточная нормализация &mdash; поговорим честно</h3>
<p>Нормализация не бесплатна. Каждая новая таблица &mdash; это ещё один <code>JOIN</code> в каждом запросе. В следующих случаях разумно остановиться:</p>
<ul>
<li><strong>Чрезмерное дробление адреса.</strong> Таблицы <code>shaharlar</code>, <code>tumanlar</code>, <code>ko'chalar</code>, <code>uylar</code> &mdash; если вы не считаете статистику по областям, это даёт лишь 4 лишних <code>JOIN</code> и ничего больше.</li>
<li><strong>Исторические значения.</strong> Хранить <code>narx_birlik</code> в строке заказа &mdash; это не дублирование, а <em>другой факт</em>: «цена на момент продажи». Если цена товара потом изменится, сумма в старом чеке измениться не должна. Называть это «денормализацией» неверно.</li>
<li><strong>Справочники на 1&ndash;2 значения.</strong> Вместо отдельной таблицы для <code>jins</code> или <code>holat</code> часто достаточно <code>CHECK (holat IN (...))</code> или <code>ENUM</code> &mdash; и читается это гораздо лучше.</li>
</ul>
<p><strong>Практический совет:</strong> нормализуйте до 3NF &mdash; это почти всегда правильный ответ. BCNF применяйте только при нескольких перекрывающихся потенциальных ключах. Всё, что выше (4NF, 5NF), в реальных проектах почти никогда не требуется. А о денормализации задумывайтесь только при измеренной проблеме производительности &mdash; об этом поговорим в 9-м уроке.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- BCNF: таблица, которая находится в 3NF, но нарушает BCNF
-- ═══════════════════════════════════════════════════════════════════════

-- Бизнес-правила:
--   1) (talaba_id, fan) -> oqituvchi   [студент изучает предмет у одного]
--   2) oqituvchi -> fan                [преподаватель ведёт один предмет]
-- Потенциальные ключи: (talaba_id, fan) И (talaba_id, oqituvchi)
-- Неключевых колонок НЕТ -> 3NF не нарушена. Но «oqituvchi» ключом не
-- является, поэтому зависимость «oqituvchi -> fan» нарушает BCNF.

DROP TABLE IF EXISTS darslar;

CREATE TABLE darslar (
    talaba_id INTEGER     NOT NULL,
    fan       VARCHAR(40) NOT NULL,
    oqituvchi VARCHAR(40) NOT NULL,
    PRIMARY KEY (talaba_id, fan),
    -- второй потенциальный ключ тоже обеспечивается ограничением
    UNIQUE (talaba_id, oqituvchi)
);

INSERT INTO darslar VALUES
    (1, 'Fizika', 'Karimov'),
    (2, 'Fizika', 'Karimov'),
    (3, 'Fizika', 'Karimov'),
    (1, 'Kimyo',  'Rasulova'),
    (2, 'Kimyo',  'Rasulova');

-- ПРОБЛЕМА 1 — дублирование: факт «Каримов ведёт физику» записан 3 раза
SELECT oqituvchi, fan, COUNT(*) AS necha_marta_takrorlangan
FROM darslar
GROUP BY oqituvchi, fan
ORDER BY oqituvchi;

-- ПРОБЛЕМА 2 — аномалия UPDATE: если Каримов перейдёт на химию,
-- изменятся 3 строки, и если одну забыть, он окажется ведущим
-- два предмета одновременно.

-- ПРОБЛЕМА 3 — аномалия INSERT: нового преподавателя без студентов
-- нельзя занести в базу, ведь talaba_id NOT NULL и входит в ключ.

-- ─────────────────────────────────────────────────────────────────────
-- РЕШЕНИЕ ПО BCNF: делаем каждый детерминант ключом своей таблицы
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS royxat;
DROP TABLE IF EXISTS oqituvchilar;

-- Зависимость «oqituvchi -> fan»: теперь oqituvchi — ПЕРВИЧНЫЙ КЛЮЧ
CREATE TABLE oqituvchilar (
    oqituvchi VARCHAR(40) PRIMARY KEY,
    fan       VARCHAR(40) NOT NULL
);

-- к какому преподавателю записан студент
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

-- Теперь «Каримов перешёл на химию» — меняется ОДНА строка:
UPDATE oqituvchilar SET fan = 'Kimyo' WHERE oqituvchi = 'Karimov';
UPDATE oqituvchilar SET fan = 'Fizika' WHERE oqituvchi = 'Karimov';  -- вернули

-- И нового преподавателя без студентов заводим свободно (аномалии INSERT нет):
INSERT INTO oqituvchilar VALUES ('Toshmatov', 'Matematika');

-- Прежнее представление восстанавливаем через JOIN
SELECT r.talaba_id, o.fan, r.oqituvchi
FROM royxat r
JOIN oqituvchilar o ON o.oqituvchi = r.oqituvchi
ORDER BY r.talaba_id, o.fan;

-- ─────────────────────────────────────────────────────────────────────
-- ЦЕНА BCNF: правило «студент не изучает один предмет у двух
-- преподавателей» больше не обеспечивается структурой АВТОМАТИЧЕСКИ.
-- После разбиения на две таблицы это правило не поместилось ни в одну
-- из них — в учебниках это называют «потерей сохранения зависимостей»
-- (dependency preservation).
--
-- Решение: переносим колонку fan в таблицу royxat и «пришиваем» её
-- составным внешним ключом к oqituvchilar — тогда значение fan никогда
-- не сможет противоречить реальному предмету преподавателя.
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE royxat ADD COLUMN fan VARCHAR(40);
UPDATE royxat r SET fan = o.fan FROM oqituvchilar o WHERE o.oqituvchi = r.oqituvchi;
ALTER TABLE royxat ALTER COLUMN fan SET NOT NULL;

ALTER TABLE oqituvchilar ADD CONSTRAINT oqituvchilar_oqituvchi_fan_uq
    UNIQUE (oqituvchi, fan);

ALTER TABLE royxat DROP CONSTRAINT royxat_oqituvchi_fkey;
ALTER TABLE royxat ADD CONSTRAINT royxat_oqituvchi_fan_fkey
    FOREIGN KEY (oqituvchi, fan) REFERENCES oqituvchilar (oqituvchi, fan);

-- Теперь UNIQUE обеспечивает это правило, а колонка fan защищена FK:
CREATE UNIQUE INDEX royxat_talaba_fan_uq ON royxat (talaba_id, fan);

-- ВЫВОД: BCNF не всегда бесплатна. 3NF — практический стандарт,
-- а BCNF нужна только при перекрывающихся потенциальных ключах.
""",
    "exercises": {
        4752: {
            "title": "Главное правило BCNF",
            "description": "Чтобы таблица находилась в BCNF, какой должна быть величина X в любой функциональной зависимости X -> Y?",
            "hint": "BCNF — про детерминанты: чем должна быть левая часть зависимости?",
            "explanation": "Правило BCNF: каждый детерминант (левая часть зависимости) обязан быть потенциальным ключом. Иначе таблица не находится в BCNF.",
        },
        4753: {
            "title": "Практический стандарт нормальной формы",
            "description": "На какой нормальной форме останавливается большинство реальных проектов, считая её практическим стандартом? Заполните пропуск: ___ (например: 1NF).",
            "hint": "Форма, устраняющая транзитивную зависимость.",
            "explanation": "3NF — практический стандарт. BCNF нужна только в особых случаях с несколькими перекрывающимися потенциальными ключами, а 4NF и 5NF в реальных проектах почти не применяются.",
        },
        4754: {
            "title": "Цена в заказе — это дублирование?",
            "description": "В таблице buyurtma_elementlari хранится колонка narx_birlik, хотя цена есть и в таблице mahsulotlar. Почему это не денормализация, а правильный дизайн? Объясните кратко (1-2 предложения).",
            "hint": "Если завтра цена товара вырастет, должна ли измениться сумма во вчерашнем чеке?",
            "expected_answer": "Потому что narx_birlik — это другой факт: историческая цена на момент продажи. Даже если цена товара потом изменится, сумма в старом заказе меняться не должна, поэтому её необходимо хранить вместе с чеком.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 829 — 1:1 и 1:N
# ═════════════════════════════════════════════════════════════════════════════
L4 = {
    "lesson_id": 829,
    "title": "4-Связи: 1:1 и 1:N",
    "text": """\
<h3>Что такое связь (relationship)?</h3>
<p>Нормализация <em>разделила</em> таблицы. Теперь их нужно <em>связать</em> обратно. Инструмент для этого один &mdash; <strong>FOREIGN KEY</strong>. Весь вопрос лишь в том, в какую таблицу поместить внешний ключ и будет ли на нём <code>UNIQUE</code>. Именно эти два решения и определяют тип связи.</p>

<h3>1:N (один-ко-многим) &mdash; самый частый тип</h3>
<p>Один автор пишет много книг, но у каждой книги один автор. У одного клиента много заказов, но каждый заказ принадлежит одному клиенту.</p>
<p><strong>Правило:</strong> внешний ключ всегда находится на <em>стороне «многие»</em>. То есть в таблице <code>kitoblar</code> будет колонка <code>muallif_id</code>, а в таблице <code>mualliflar</code> колонки <code>kitob_id</code> не будет. Причина проста: в одну ячейку не поместить несколько ID книг &mdash; это привело бы нас прямиком к нарушению 1NF.</p>

<h3>1:1 (один-к-одному) &mdash; реже, но нужен</h3>
<p>1:1 &mdash; это технически тот же 1:N, к которому добавили <code>UNIQUE</code>. Поставьте <code>UNIQUE</code> на колонку внешнего ключа &mdash; и «многие» автоматически превратятся в «один».</p>
<p>Возникает логичный вопрос: если связь 1:1, почему бы просто не объединить обе таблицы? Есть веские причины:</p>
<ul>
<li><strong>Необязательные данные.</strong> Профиль (био, аватар, дата рождения) есть далеко не у каждого пользователя. Если добавить их в <code>users</code>, во множестве строк накопятся <code>NULL</code>.</li>
<li><strong>Разный уровень доступа.</strong> Паспортные данные или банковскую карту безопаснее держать в отдельной таблице с отдельными правами.</li>
<li><strong>Редко читаемые тяжёлые колонки.</strong> Если вынести большие <code>TEXT</code> или <code>BYTEA</code>, которые нужны не в каждом запросе, строка основной таблицы станет компактнее и будет читаться быстрее.</li>
</ul>

<h3>Таблица сравнения</h3>
<table>
<tr><th>Характеристика</th><th>1:1</th><th>1:N</th></tr>
<tr><td>Пример</td><td>users &harr; user_profiles</td><td>mualliflar &rarr; kitoblar</td></tr>
<tr><td>Где внешний ключ</td><td>на зависимой (необязательной) стороне</td><td>на стороне «многие»</td></tr>
<tr><td>UNIQUE на колонке FK</td><td>Да (или FK = PK)</td><td>Нет</td></tr>
<tr><td>Нужна ли доп. таблица</td><td>Нет</td><td>Нет</td></tr>
<tr><td>Типичный ON DELETE</td><td>CASCADE</td><td>RESTRICT или SET NULL</td></tr>
</table>

<pre class="mermaid">
flowchart LR
  U["users
id PK"] ---|"1 : 1"| P["user_profiles
user_id — PK и FK одновременно
(UNIQUE автоматически)"]
  A["mualliflar
id PK"] ---|"1 : N"| B["kitoblar
id PK
muallif_id FK (без UNIQUE)"]
</pre>

<h3>Два способа реализовать 1:1</h3>
<ul>
<li><strong>Общий первичный ключ (shared PK).</strong> Колонка <code>user_profiles.user_id</code> одновременно и PRIMARY KEY, и FOREIGN KEY. Самый чистый вариант: уникальность обеспечивается автоматически, лишней колонки <code>id</code> нет.</li>
<li><strong>Отдельный id + UNIQUE на FK.</strong> <code>user_profiles(id PK, user_id FK UNIQUE)</code>. ORM (Django, SQLAlchemy) нередко предпочитают именно это, поскольку отдельные их части рассчитывают на наличие колонки <code>id</code> в каждой таблице.</li>
</ul>
<p><strong>Самая частая ошибка:</strong> забыть поставить <code>UNIQUE</code> на колонку FK в связи 1:1. Тогда база молча позволит записать одному пользователю два профиля &mdash; и выяснится это лишь спустя месяцы, когда <code>get_profile()</code> вернёт две строки.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Связи 1:1 и 1:N — где стоит внешний ключ и какова роль UNIQUE
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS kitoblar;
DROP TABLE IF EXISTS mualliflar;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;

-- ─────────────────────────────────────────────────────────────────────
-- 1:1 — пользователь и его профиль
-- Способ: общий первичный ключ (shared primary key).
-- user_id одновременно PK и FK -> уникальность гарантируется сама собой.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE users (
    id         SERIAL       PRIMARY KEY,
    email      VARCHAR(120) NOT NULL UNIQUE,
    parol_hash VARCHAR(255) NOT NULL,
    yaratilgan TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
    -- PK и FK в одной колонке: у пользователя не более одного профиля
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

-- Третий пользователь ещё не заполнил профиль — это нормально.
-- Именно поэтому профиль в отдельной таблице: в users не копятся NULL.
INSERT INTO user_profiles (user_id, tolik_ism, bio) VALUES
    (1, 'Aziz Karimov',     'Backend dasturchi'),
    (2, 'Dilnoza Rasulova', 'Data analitik');

-- Второй профиль база ЗАПИСАТЬ НЕ ДАСТ — его блокирует PK:
-- INSERT INTO user_profiles (user_id, tolik_ism) VALUES (1, 'Ikkinchi profil');
-- ERROR:  duplicate key value violates unique constraint "user_profiles_pkey"

-- Чтобы увидеть и тех, у кого профиля нет, нужен LEFT JOIN:
SELECT u.id, u.email, p.tolik_ism, p.bio
FROM users u
LEFT JOIN user_profiles p ON p.user_id = u.id
ORDER BY u.id;

-- ─────────────────────────────────────────────────────────────────────
-- 1:N — один автор, много книг. FK на стороне «многие»: kitoblar.muallif_id
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE mualliflar (
    id           SERIAL      PRIMARY KEY,
    ism          VARCHAR(80) NOT NULL,
    tugilgan_yil INTEGER     CHECK (tugilgan_yil BETWEEN 1000 AND 2100)
);

CREATE TABLE kitoblar (
    id          SERIAL      PRIMARY KEY,
    -- UNIQUE НЕТ — поэтому у одного автора может быть много книг
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

-- Проверяем 1:N — сколько книг у каждого автора
SELECT a.ism, COUNT(k.id) AS kitoblar_soni
FROM mualliflar a
LEFT JOIN kitoblar k ON k.muallif_id = a.id
GROUP BY a.id, a.ism
ORDER BY kitoblar_soni DESC;

-- Убеждаемся, что защита FK работает: несуществующий автор
-- INSERT INTO kitoblar (muallif_id, sarlavha) VALUES (999, 'Sehrli kitob');
-- ERROR:  insert or update on table "kitoblar" violates foreign key constraint

-- ON DELETE RESTRICT: автора, у которого есть книги, удалить нельзя
-- DELETE FROM mualliflar WHERE id = 1;
-- ERROR:  update or delete on table "mualliflar" violates foreign key constraint

-- Проверяем работу ON DELETE CASCADE на стороне 1:1:
DELETE FROM users WHERE id = 2;
SELECT COUNT(*) AS qolgan_profillar FROM user_profiles;  -- остался 1

-- ─────────────────────────────────────────────────────────────────────
-- ВАЖНО: если построить 1:1 без UNIQUE, он молча превратится в 1:N.
-- Разница между двумя определениями колонки — это весь тип связи:
--   muallif_id INTEGER REFERENCES mualliflar(id)          -> 1:N
--   muallif_id INTEGER UNIQUE REFERENCES mualliflar(id)   -> 1:1
-- ─────────────────────────────────────────────────────────────────────
""",
    "exercises": {
        4755: {
            "title": "В какой таблице находится внешний ключ?",
            "description": "В связи 1:N (один автор — много книг) в какую таблицу помещается колонка FOREIGN KEY?",
            "hint": "В одну ячейку не поместить несколько ID — это нарушило бы 1NF.",
            "explanation": "Внешний ключ всегда находится на стороне «многие», то есть это kitoblar.muallif_id. Иначе пришлось бы записывать в одну ячейку несколько ID книг, а это нарушение 1NF.",
        },
        4756: {
            "title": "Превращаем 1:N в 1:1",
            "description": "Какое ограничение нужно добавить на колонку FK, чтобы превратить связь 1:N в 1:1? Заполните пропуск (одно слово заглавными буквами): ___.",
            "hint": "Это ограничение гарантирует, что значение не встретится в колонке дважды.",
            "explanation": "Если поставить UNIQUE на колонку FK, одной «родительской» строке сможет соответствовать не более одной «дочерней» — то есть 1:N автоматически превращается в 1:1. Альтернативный вариант: сделать колонку FK одновременно PRIMARY KEY.",
        },
        4757: {
            "title": "Причины вынести 1:1 в отдельную таблицу",
            "description": "Какие из перечисленных являются вескими причинами вынести связь 1:1 в отдельную таблицу?",
            "hint": "Само по себе количество колонок никогда не является причиной делить таблицу.",
            "explanation": "Три веские причины вынести 1:1: необязательные данные (накопление NULL), разный уровень доступа и редко читаемые тяжёлые колонки. Количество колонок само по себе причиной не является — широкая таблица в 3NF совершенно нормальна.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 830 — N:N и junction-таблицы
# ═════════════════════════════════════════════════════════════════════════════
L5 = {
    "lesson_id": 830,
    "title": "5-Связи: N:N и junction-таблицы",
    "text": """\
<h3>N:N &mdash; почему её нельзя построить напрямую</h3>
<p>Один студент записывается на много курсов, и на одном курсе учится много студентов. Это связь <strong>многие-ко-многим</strong> (N:N).</p>
<p>Попробуйте построить её двумя таблицами &mdash; и сразу упрётесь в стену:</p>
<ul>
<li>Добавим <code>talabalar.kurs_id</code> &mdash; студент сможет записаться только на один курс.</li>
<li>Добавим <code>kurslar.talaba_id</code> &mdash; на курсе окажется только один студент.</li>
<li>Напишем <code>talabalar.kurs_idlar = '1,3,7'</code> &mdash; это явное нарушение 1NF, и все проблемы из первого урока возвращаются.</li>
</ul>
<p>Единственное правильное решение &mdash; <strong>junction-таблица</strong> (её также называют связующей, bridge или associative table). Она объединяет две связи 1:N и тем самым образует N:N.</p>

<h3>Устройство junction-таблицы</h3>
<p>Как минимум она состоит из двух внешних ключей, которые вместе образуют составной первичный ключ:</p>
<ul>
<li><code>talaba_id</code> &rarr; <code>talabalar(id)</code></li>
<li><code>kurs_id</code> &rarr; <code>kurslar(id)</code></li>
<li><code>PRIMARY KEY (talaba_id, kurs_id)</code> &mdash; студент не может записаться на один курс дважды.</li>
</ul>

<h3>Junction-таблица &mdash; это не просто «техническая» таблица</h3>
<p>Это самая важная мысль урока. Новички считают junction-таблицу чем-то вроде «просто связать два ID». На практике же она почти всегда оказывается <em>самостоятельной сущностью со своими атрибутами</em>:</p>
<table>
<tr><th>Связь N:N</th><th>Junction-таблица</th><th>Её собственные атрибуты</th></tr>
<tr><td>студенты &harr; курсы</td><td>royxatlar (enrollments)</td><td>дата записи, оценка, статус</td></tr>
<tr><td>заказы &harr; товары</td><td>buyurtma_elementlari</td><td>количество, цена за единицу, скидка</td></tr>
<tr><td>пользователи &harr; роли</td><td>user_roles</td><td>дата выдачи, кто выдал</td></tr>
<tr><td>посты &harr; теги</td><td>post_tags</td><td>(часто пусто &mdash; чистая связь)</td></tr>
</table>
<p>Поэтому давайте junction-таблице осмысленное имя. Не <code>talaba_kurs</code>, а <code>royxatlar</code>. Не <code>buyurtma_mahsulot</code>, а <code>buyurtma_elementlari</code>. Если имя раскрывает суть, добавлять в такую таблицу колонки потом кажется естественным.</p>

<pre class="mermaid">
flowchart LR
  T["talabalar
id PK"] -->|"1 : N"| R["royxatlar
talaba_id FK
kurs_id FK
PK (talaba_id, kurs_id)
+ дата записи, оценка"]
  K["kurslar
id PK"] -->|"1 : N"| R
</pre>

<h3>Составной ключ или суррогатный id?</h3>
<p>Можно добавить в junction-таблицу <code>id SERIAL PRIMARY KEY</code>, а на пару <code>(talaba_id, kurs_id)</code> поставить <code>UNIQUE</code>. Оба варианта корректны, выбор зависит от контекста:</p>
<ul>
<li><strong>Составной ключ</strong> &mdash; предпочтителен в чистых SQL-проектах: лишней колонки нет, а сам ключ выражает бизнес-правило.</li>
<li><strong>Суррогатный id + UNIQUE</strong> &mdash; если на эти строки ссылается другая таблица (например, <code>baholar.royxat_id</code>) или этого требует ORM. Важно: <em>не забудьте</em> и в этом случае добавить <code>UNIQUE (talaba_id, kurs_id)</code>, иначе появятся дубликаты.</li>
</ul>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Связь N:N и junction-таблица — talabalar / kurslar / royxatlar
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
-- JUNCTION-ТАБЛИЦА. Обратите внимание: это не просто «связка» —
-- у неё есть СВОИ атрибуты: дата записи, оценка и статус.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE royxatlar (
    talaba_id      INTEGER NOT NULL REFERENCES talabalar(id) ON DELETE CASCADE,
    kurs_id        INTEGER NOT NULL REFERENCES kurslar(id)   ON DELETE RESTRICT,
    yozilgan_sana  DATE    NOT NULL DEFAULT CURRENT_DATE,
    baho           INTEGER CHECK (baho BETWEEN 0 AND 100),
    holat          VARCHAR(16) NOT NULL DEFAULT 'faol'
                   CHECK (holat IN ('faol', 'tugatgan', 'tashlab_ketgan')),
    -- Составной первичный ключ: студент записывается на курс ОДИН раз
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

-- Составной ключ блокирует дубликат:
-- INSERT INTO royxatlar (talaba_id, kurs_id) VALUES (1, 1);
-- ERROR:  duplicate key value violates unique constraint "royxatlar_pkey"

-- ─────────────────────────────────────────────────────────────────────
-- Читаем связь N:N в обе стороны
-- ─────────────────────────────────────────────────────────────────────

-- 1) На каких курсах учится студент?
SELECT t.ism, k.nomi AS kurs, r.holat, r.baho
FROM royxatlar r
JOIN talabalar t ON t.id = r.talaba_id
JOIN kurslar   k ON k.id = r.kurs_id
WHERE t.email = 'aziz@edu.uz'
ORDER BY k.nomi;

-- 2) Какие студенты на одном курсе?
SELECT k.nomi AS kurs, t.ism, r.yozilgan_sana
FROM royxatlar r
JOIN kurslar   k ON k.id = r.kurs_id
JOIN talabalar t ON t.id = r.talaba_id
WHERE k.nomi = 'SQL Asoslari'
ORDER BY t.ism;

-- 3) Отчёт, возможный благодаря атрибутам junction-таблицы:
--    средняя оценка по курсу и доля завершивших
SELECT k.nomi                                        AS kurs,
       COUNT(*)                                      AS jami_yozilgan,
       COUNT(*) FILTER (WHERE r.holat = 'tugatgan')  AS tugatgan,
       ROUND(AVG(r.baho), 1)                         AS ortacha_baho
FROM kurslar k
JOIN royxatlar r ON r.kurs_id = k.id
GROUP BY k.id, k.nomi
ORDER BY kurs;

-- 4) Курсы, на которые никто не записался (LEFT JOIN + IS NULL)
SELECT k.nomi
FROM kurslar k
LEFT JOIN royxatlar r ON r.kurs_id = k.id
WHERE r.kurs_id IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- АЛЬТЕРНАТИВНЫЙ ВАРИАНТ: суррогатный id + UNIQUE.
-- Удобнее, когда на конкретную строку записи должна ссылаться другая
-- таблица (например, если оценка за каждое задание хранится отдельно).
-- ─────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS royxatlar_v2;

CREATE TABLE royxatlar_v2 (
    id            SERIAL  PRIMARY KEY,
    talaba_id     INTEGER NOT NULL REFERENCES talabalar(id) ON DELETE CASCADE,
    kurs_id       INTEGER NOT NULL REFERENCES kurslar(id)   ON DELETE RESTRICT,
    yozilgan_sana DATE    NOT NULL DEFAULT CURRENT_DATE,
    -- НЕ ЗАБУДЬТЕ про UNIQUE — без него дубликаты пройдут свободно!
    UNIQUE (talaba_id, kurs_id)
);

INSERT INTO royxatlar_v2 (talaba_id, kurs_id) VALUES (1, 1), (2, 1);

-- Индексы на колонки FK: PK покрывает первую колонку, но для запроса
-- «кто на этом курсе?» нужен отдельный индекс по kurs_id.
CREATE INDEX royxatlar_kurs_id_idx ON royxatlar (kurs_id);
""",
    "exercises": {
        4758: {
            "title": "Как реализуется связь N:N?",
            "description": "Как в PostgreSQL реализуется связь многие-ко-многим (N:N) между студентами и курсами?",
            "hint": "N:N — это на самом деле объединение двух связей 1:N.",
            "explanation": "N:N строится только через junction-таблицу: она хранит два внешних ключа и тем самым объединяет две связи 1:N в N:N. Остальные варианты либо нарушают 1NF, либо ограничивают связь до 1:N.",
        },
        4759: {
            "title": "Ключ junction-таблицы",
            "description": "Какой ключ образуют обе колонки junction-таблицы royxatlar(talaba_id, kurs_id), чтобы студент не мог записаться на один курс дважды? Заполните пропуск: ___ первичный ключ (одно слово).",
            "hint": "Так называется ключ, состоящий из нескольких колонок.",
            "explanation": "PRIMARY KEY (talaba_id, kurs_id) — это составной (композитный) первичный ключ. Он блокирует дубликаты на уровне базы данных.",
        },
        4760: {
            "title": "Когда в junction-таблицу добавлен суррогатный id",
            "description": "В junction-таблицу добавили id SERIAL PRIMARY KEY, и обе колонки FK стали обычными колонками. Какое ограничение обязательно нужно добавить, чтобы не появились дубликаты? Напишите в виде SQL (например: UNIQUE (a, b)).",
            "hint": "После удаления составного PK его гарантию нужно вернуть другим ограничением.",
            "expected_answer": "UNIQUE (talaba_id, kurs_id)",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 831 — R1 библиотека
# ═════════════════════════════════════════════════════════════════════════════
R1 = {
    "lesson_id": 831,
    "title": "R1-Проектирование схемы библиотечной системы (повторение)",
    "text": """\
<h2>R1 &mdash; повторение модуля 1: схема библиотечной системы</h2>
<p>Объединяем всё, что изучили в первых 5 уроках &mdash; 1NF, 2NF, 3NF, 1:1, 1:N и N:N &mdash; в одной реальной схеме.</p>
<p>Представьте: городская библиотека попросила у вас систему. Сейчас они ведут всё в Excel-таблице такого вида:</p>

<table>
<tr><th>книга</th><th>автор</th><th>год_рожд_автора</th><th>читатель</th><th>тел_читателя</th><th>выдана</th><th>возвращена</th></tr>
<tr><td>O'tkan kunlar</td><td>Abdulla Qodiriy</td><td>1894</td><td>Aziz K</td><td>+998901112233</td><td>2026-01-10</td><td>2026-01-24</td></tr>
<tr><td>O'tkan kunlar</td><td>Abdulla Qodiriy</td><td>1894</td><td>Dilnoza R</td><td>+998907778899</td><td>2026-02-01</td><td></td></tr>
<tr><td>Clean Code</td><td>Robert Martin</td><td>1952</td><td>Aziz K</td><td>+998901112233</td><td>2026-01-15</td><td>2026-02-15</td></tr>
</table>

<h3>Перечислите проблемы этой таблицы</h3>
<ul>
<li>Год рождения автора дублируется для каждой пары «книга-читатель» &mdash; <strong>транзитивная зависимость</strong> (нарушена 3NF).</li>
<li>Телефон читателя дублируется в каждой выдаче &mdash; аномалия UPDATE.</li>
<li>Нельзя сохранить читателя, ещё не бравшего книг, или книгу, которую никто не брал &mdash; аномалия INSERT.</li>
<li>Если у книги несколько экземпляров, различить их невозможно.</li>
<li>Если у книги несколько авторов &mdash; эта схема вообще не работает.</li>
</ul>

<h3>Схема, которая от вас ожидается</h3>
<p>Как минимум должны быть следующие сущности. Тип связи для каждой определите сами:</p>
<table>
<tr><th>Таблица</th><th>Назначение</th><th>Связь</th></tr>
<tr><td><code>mualliflar</code></td><td>Факт об авторе в одном месте</td><td>N:N с книгами</td></tr>
<tr><td><code>kitoblar</code></td><td>Произведение (название, ISBN, год издания)</td><td>&mdash;</td></tr>
<tr><td><code>kitob_mualliflari</code></td><td>Junction: у книги может быть несколько авторов</td><td>раскрывает N:N</td></tr>
<tr><td><code>nusxalar</code></td><td>Физический экземпляр на полке (инвентарный номер)</td><td>1:N с книгами</td></tr>
<tr><td><code>azolar</code></td><td>Читатель библиотеки</td><td>&mdash;</td></tr>
<tr><td><code>azo_profillari</code></td><td>Адрес, паспорт &mdash; необязательные конфиденциальные данные</td><td>1:1 с читателями</td></tr>
<tr><td><code>qarzlar</code></td><td>Кто, какой экземпляр, когда взял/вернул</td><td>N:N с экземплярами и читателями</td></tr>
</table>

<h3>Сложное решение, на которое стоит обратить внимание</h3>
<p>Почему <code>kitoblar</code> и <code>nusxalar</code> разделены? Потому что «O'tkan kunlar» &mdash; это <em>произведение</em>, а 5 томов на полке &mdash; это <em>5 отдельных физических объектов</em>. Выдаётся конкретный физический экземпляр, а не произведение. Не увидеть этой разницы &mdash; самая частая ошибка в схеме библиотеки: без неё вы не сможете ответить на вопрос «сколько экземпляров этой книги свободно?».</p>

<pre class="mermaid">
flowchart TB
  M["mualliflar"] --> KM["kitob_mualliflari
(junction, N:N)"]
  K["kitoblar"] --> KM
  K -->|"1 : N"| N["nusxalar
(инвентарный номер)"]
  A["azolar"] -->|"1 : 1"| AP["azo_profillari"]
  N --> Q["qarzlar
(дата выдачи, дата возврата)"]
  A --> Q
</pre>

<h3>Контрольные вопросы</h3>
<ol>
<li>Каков первичный ключ каждой таблицы? Какие из них составные?</li>
<li>Верно ли будет поставить в таблице <code>qarzlar</code> ключ <code>PRIMARY KEY (nusxa_id, azo_id)</code>? (Подсказка: может ли один читатель взять одну и ту же книгу дважды?)</li>
<li>Что должно происходить с выдачами при удалении читателя &mdash; <code>CASCADE</code> или <code>RESTRICT</code>?</li>
<li>Как вы напишете запрос «экземпляры, которые сейчас на руках»?</li>
</ol>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- R1 — схема библиотеки: СТАРТОВЫЙ НАБОР
-- Ниже дана часть схемы. Остальное вы пишете сами.
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS qarzlar;
DROP TABLE IF EXISTS nusxalar;
DROP TABLE IF EXISTS kitob_mualliflari;
DROP TABLE IF EXISTS kitoblar;
DROP TABLE IF EXISTS mualliflar;
DROP TABLE IF EXISTS azo_profillari;
DROP TABLE IF EXISTS azolar;

-- ── Авторы (3NF: факт об авторе в одном месте) ────────────────────────
CREATE TABLE mualliflar (
    id           SERIAL      PRIMARY KEY,
    ism          VARCHAR(80) NOT NULL,
    tugilgan_yil INTEGER     CHECK (tugilgan_yil BETWEEN 1000 AND 2100)
);

-- ── Книга = ПРОИЗВЕДЕНИЕ (не физический экземпляр!) ───────────────────
CREATE TABLE kitoblar (
    id         SERIAL       PRIMARY KEY,
    sarlavha   VARCHAR(200) NOT NULL,
    isbn       CHAR(13)     UNIQUE,
    nashr_yili INTEGER      CHECK (nashr_yili BETWEEN 1000 AND 2100)
);

-- ── Junction N:N: у книги может быть несколько авторов ────────────────
CREATE TABLE kitob_mualliflari (
    kitob_id   INTEGER NOT NULL REFERENCES kitoblar(id)   ON DELETE CASCADE,
    muallif_id INTEGER NOT NULL REFERENCES mualliflar(id) ON DELETE RESTRICT,
    -- порядок авторов важен: первый автор стоит первым на обложке
    tartib     SMALLINT NOT NULL DEFAULT 1 CHECK (tartib > 0),
    PRIMARY KEY (kitob_id, muallif_id)
);

-- ── 1:N — физические экземпляры произведения на полке ─────────────────
CREATE TABLE nusxalar (
    id              SERIAL      PRIMARY KEY,
    kitob_id        INTEGER     NOT NULL REFERENCES kitoblar(id) ON DELETE RESTRICT,
    inventar_raqami VARCHAR(20) NOT NULL UNIQUE,
    holati          VARCHAR(12) NOT NULL DEFAULT 'yaxshi'
                    CHECK (holati IN ('yaxshi', 'eskirgan', 'yaroqsiz'))
);

-- ── Читатели ──────────────────────────────────────────────────────────
CREATE TABLE azolar (
    id            SERIAL       PRIMARY KEY,
    ism           VARCHAR(80)  NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    azolik_sanasi DATE         NOT NULL DEFAULT CURRENT_DATE
);

-- ── 1:1 — необязательные и более конфиденциальные данные отдельно ──────
CREATE TABLE azo_profillari (
    azo_id         INTEGER PRIMARY KEY REFERENCES azolar(id) ON DELETE CASCADE,
    telefon        VARCHAR(20),
    manzil         TEXT,
    pasport_raqami VARCHAR(20) UNIQUE
);

-- ─────────────────────────────────────────────────────────────────────
-- ЗАДАНИЕ: таблицу qarzlar напишите САМИ.
--
-- Подумайте:
--   * PRIMARY KEY (nusxa_id, azo_id) НЕВЕРЕН — почему?
--     Потому что один читатель может брать одну книгу несколько раз
--     в течение года. В ключ нужно добавить дату выдачи либо
--     использовать суррогатный id.
--   * qaytarilgan_sana должна допускать NULL — «ещё не возвращена».
--   * Дата возврата не может быть раньше даты выдачи -> CHECK.
--   * Что станет с историей выдач при удалении читателя? CASCADE или RESTRICT?
--
-- Образцовое решение (сравните после того, как напишете своё):
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

-- Один физический экземпляр в один момент времени может быть только
-- у ОДНОГО человека. Обеспечиваем это частичным (partial) unique-индексом:
CREATE UNIQUE INDEX qarzlar_faol_nusxa_uq
    ON qarzlar (nusxa_id)
    WHERE qaytarilgan_sana IS NULL;

-- ── Тестовые данные ───────────────────────────────────────────────────
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
    (2, 3, 2);   -- второй автор — возможен благодаря N:N

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

-- Один экземпляр не может быть у двух людей — блокирует частичный индекс:
-- INSERT INTO qarzlar (nusxa_id, azo_id, qaytarish_muddati)
-- VALUES (2, 1, CURRENT_DATE + 14);
-- ERROR:  duplicate key value violates unique constraint "qarzlar_faol_nusxa_uq"

-- ── Отчёты, подтверждающие работоспособность схемы ────────────────────

-- 1) Экземпляры, которые сейчас на руках
SELECT k.sarlavha, n.inventar_raqami, a.ism, q.qaytarish_muddati
FROM qarzlar q
JOIN nusxalar n ON n.id = q.nusxa_id
JOIN kitoblar k ON k.id = n.kitob_id
JOIN azolar   a ON a.id = q.azo_id
WHERE q.qaytarilgan_sana IS NULL
ORDER BY q.qaytarish_muddati;

-- 2) Сколько экземпляров каждого произведения свободно
SELECT k.sarlavha,
       COUNT(n.id)                                          AS jami_nusxa,
       COUNT(n.id) - COUNT(q.id)                            AS bosh_nusxa
FROM kitoblar k
LEFT JOIN nusxalar n ON n.kitob_id = k.id
LEFT JOIN qarzlar  q ON q.nusxa_id = n.id AND q.qaytarilgan_sana IS NULL
GROUP BY k.id, k.sarlavha
ORDER BY k.sarlavha;

-- 3) Книги с несколькими авторами — доказывает, что N:N работает
SELECT k.sarlavha, STRING_AGG(m.ism, ', ' ORDER BY km.tartib) AS mualliflar
FROM kitoblar k
JOIN kitob_mualliflari km ON km.kitob_id = k.id
JOIN mualliflar m ON m.id = km.muallif_id
GROUP BY k.id, k.sarlavha
HAVING COUNT(*) > 1;
""",
    "task_title": "🔁 R1: Схема библиотечной системы",
    "task_description": (
        "Спроектируйте с нуля полностью нормализованную схему для городской "
        "библиотеки: в одном проекте должны быть задействованы 1NF-3NF, а также "
        "связи 1:1, 1:N и N:N. Результат — один запускаемый .sql файл."
    ),
    "task_requirements": (
        "• Не менее 7 таблиц: mualliflar, kitoblar, kitob_mualliflari, nusxalar, azolar, azo_profillari, qarzlar\n"
        "• PRIMARY KEY в каждой таблице; в junction-таблице — составной ключ\n"
        "• N:N: у книги должно быть возможно несколько авторов\n"
        "• 1:1: azo_profillari (паспорт, адрес) — через UNIQUE или PK=FK\n"
        "• 1:N: несколько физических экземпляров одного произведения\n"
        "• qarzlar: один читатель должен иметь возможность брать один экземпляр повторно в разные даты\n"
        "• Один физический экземпляр в один момент времени только у одного человека — обеспечьте это индексом или ограничением\n"
        "• CHECK: qaytarish_muddati > olingan_sana, qaytarilgan_sana >= olingan_sana\n"
        "• Для каждого FK выберите стратегию ON DELETE и ОБОСНУЙТЕ её в комментарии --\n"
        "• Тестовые данные: 5+ авторов, 5+ книг, 10+ экземпляров, 5+ читателей, 8+ выдач\n"
        "• 5 отчётов: экземпляры на руках; просроченные выдачи; количество свободных "
        "экземпляров по каждому произведению; 3 самых активных читателя; произведения, которые никогда не брали\n"
        "• Бонус: в начале схемы напишите в комментарии, какую нормальную форму где "
        "вы применили (например: \"muallif_tugilgan_yil -> mualliflar: 3NF, транзитивная зависимость\")"
    ),
    "task_technologies": (
        "PostgreSQL, нормализация (1NF/2NF/3NF), CREATE TABLE, PRIMARY KEY, "
        "FOREIGN KEY, составной ключ, junction-таблица, CHECK, UNIQUE, partial index, JOIN"
    ),
    "exercises": {
        4761: {
            "title": "Верные решения в схеме библиотеки",
            "description": "Какие из утверждений о схеме библиотеки верны?",
            "hint": "Сколько раз в течение года один читатель может взять одну и ту же книгу?",
            "explanation": "Произведение и физический экземпляр — разные сущности; поскольку у книги может быть несколько авторов, нужна junction-таблица N:N; профиль — связь 1:1. А вот PRIMARY KEY (nusxa_id, azo_id) — ОШИБКА, ведь один читатель может брать один экземпляр несколько раз: в ключ нужно добавить дату либо использовать суррогатный id.",
        },
        4762: {
            "title": "Порядок проектирования схемы",
            "description": "Расположите в правильном порядке шаги перехода от Excel-таблицы к нормализованной схеме.",
            "hint": "Сначала выясняем, что вообще есть, затем как оно связано, и в конце — правила.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 832 — ключи и ON DELETE
# ═════════════════════════════════════════════════════════════════════════════
L6 = {
    "lesson_id": 832,
    "title": "6-Стратегии первичных и внешних ключей, ON DELETE CASCADE/SET NULL",
    "text": """\
<h3>Выбор первичного ключа: натуральный или суррогатный?</h3>
<p><strong>Натуральный ключ</strong> &mdash; значение, которое уже присутствует в самих данных и уникально по своей природе: ISBN, номер паспорта, email, код страны.</p>
<p><strong>Суррогатный ключ</strong> &mdash; искусственное значение, созданное исключительно для идентификации: <code>SERIAL</code>, <code>IDENTITY</code>, <code>UUID</code>. Бизнес-смысла у него нет.</p>

<table>
<tr><th>Критерий</th><th>Натуральный ключ</th><th>Суррогатный ключ</th></tr>
<tr><td>Читаемость</td><td>Хорошая: <code>WHERE isbn = '978...'</code></td><td>Хуже: <code>WHERE id = 4821</code></td></tr>
<tr><td>Риск изменения</td><td>Высокий &mdash; email и телефон меняются</td><td>Нулевой &mdash; не меняется никогда</td></tr>
<tr><td>Размер</td><td>Может быть большим (CHAR(13))</td><td>4&ndash;8 байт</td></tr>
<tr><td>Колонки FK</td><td>Дублируют весь ключ</td><td>Одно компактное число</td></tr>
<tr><td>Скорость JOIN</td><td>Ниже (длинный ключ)</td><td>Выше</td></tr>
<tr><td>Утечка информации</td><td>Если PK виден в URL &mdash; риск</td><td>SERIAL тоже раскрывает счётчик; UUID &mdash; нет</td></tr>
</table>

<p><strong>Практический совет:</strong> в качестве первичного ключа используйте суррогатный (<code>SERIAL</code>/<code>IDENTITY</code>), а натуральный ключ сохраняйте как ограничение <code>UNIQUE</code>. Так вы получите оба преимущества: стабильный внутренний идентификатор и бизнес-уникальность, обеспеченную на уровне базы.</p>
<p>Почему делать email первичным ключом &mdash; плохая идея? Когда пользователь изменит email, придётся обновить все строки во всех таблицах, связанных с ним внешним ключом (или полагаться на <code>ON UPDATE CASCADE</code>). При суррогатном id не меняется ничего &mdash; обновляется только колонка <code>users.email</code>.</p>

<h3>SERIAL, IDENTITY или UUID?</h3>
<ul>
<li><code>SERIAL</code> &mdash; старый, привычный способ PostgreSQL. Внутри создаёт последовательность.</li>
<li><code>GENERATED ALWAYS AS IDENTITY</code> &mdash; стандарт SQL, рекомендуемый в PostgreSQL 10+. Защищает от случайной ручной вставки <code>id</code>.</li>
<li><code>UUID</code> &mdash; в распределённых системах или когда ID виден в URL (чтобы конкурент не узнал, сколько у вас заказов). Цена: 16 байт и фрагментация индекса из-за случайного порядка (это решают <code>uuid_generate_v7</code> или <code>ULID</code>).</li>
</ul>

<h3>Ссылочная целостность и ON DELETE</h3>
<p><code>FOREIGN KEY</code> &mdash; это не просто документация, а <em>гарантия на уровне базы данных</em>: заказ несуществующему клиенту записать нельзя. От проверки в коде приложения он отличается тем, что его невозможно обойти &mdash; ни другим микросервисом, ни миграционным скриптом, ни запросом, набранным вручную в <code>psql</code>.</p>
<p>Главный вопрос: что произойдёт с дочерними строками при удалении родительской? Это определяет <code>ON DELETE</code>.</p>

<table>
<tr><th>Стратегия</th><th>Что делает</th><th>Когда применяется</th></tr>
<tr><td><code>RESTRICT</code> / <code>NO ACTION</code></td><td>Блокирует удаление, если есть дочерние строки</td><td>Защита по умолчанию. Не удалять клиента с заказами</td></tr>
<tr><td><code>CASCADE</code></td><td>Удаляет и дочерние строки</td><td>Когда дочерняя строка без родителя бессмысленна: buyurtma_elementlari, профиль</td></tr>
<tr><td><code>SET NULL</code></td><td>Записывает NULL в колонку FK</td><td>Когда связь необязательна: сотрудник уволился, задача осталась</td></tr>
<tr><td><code>SET DEFAULT</code></td><td>Записывает в FK значение DEFAULT</td><td>Редко: перевод в категорию «Архив»</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  D["DELETE FROM mijozlar WHERE id = 5"] --> Q{"Стратегия FK
buyurtmalar.mijoz_id?"}
  Q -->|"RESTRICT"| R["ОШИБКА: удаление заблокировано.
Клиент и его история сохранены."]
  Q -->|"CASCADE"| C["Удалены клиент + все его заказы
+ все buyurtma_elementlari.
Финансовая история потеряна!"]
  Q -->|"SET NULL"| S["Заказы остались,
но mijoz_id = NULL.
«Чьи они?» — теперь неизвестно."]
</pre>

<h3>Реальные последствия: удаление клиента</h3>
<p>Это самая частая и самая дорогая ошибка. Допустим, на <code>buyurtmalar.mijoz_id</code> стоит <code>ON DELETE CASCADE</code>. Сотрудник поддержки в ответ на просьбу «удалить аккаунт» пишет один <code>DELETE</code> &mdash; и вместе с этим мгновенно исчезают три года истории продаж, бухгалтерская отчётность и статистика месячной выручки. Без единого предупреждения.</p>
<p><strong>Правильный подход:</strong> для данных с финансовым смыслом ставьте <code>ON DELETE RESTRICT</code>, а вместо удаления используйте <em>мягкое удаление</em> (soft delete) &mdash; колонку <code>ochirilgan_sana TIMESTAMPTZ</code>. Для приложения клиента «нет», но история заказов и отчёты остаются на месте.</p>
<p><code>CASCADE</code> применяйте только тогда, когда дочерняя строка действительно бессмысленна без родителя: <code>buyurtma_elementlari</code> без удалённого заказа, <code>user_profiles</code> без удалённого пользователя, <code>post_tags</code> без удалённого поста &mdash; ни одна из них не имеет самостоятельной ценности.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Стратегии ключей и ON DELETE — смотрим на последствия каждой
-- ═══════════════════════════════════════════════════════════════════════

DROP TABLE IF EXISTS vazifalar;
DROP TABLE IF EXISTS xodimlar;
DROP TABLE IF EXISTS buyurtma_elementlari;
DROP TABLE IF EXISTS buyurtmalar;
DROP TABLE IF EXISTS mahsulotlar;
DROP TABLE IF EXISTS mijozlar;

-- ─────────────────────────────────────────────────────────────────────
-- 1) Суррогатный PK + натуральный ключ как UNIQUE — рекомендуемый способ
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE mijozlar (
    -- IDENTITY: стандарт SQL, безопаснее SERIAL (нельзя вставить id
    -- вручную, поэтому последовательность никогда не «собьётся»)
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- натуральный ключ: не PK, но уникален на уровне базы
    email           VARCHAR(120) NOT NULL UNIQUE,
    ism             VARCHAR(80)  NOT NULL,
    -- мягкое удаление: вместо удаления ставим дату
    ochirilgan_sana TIMESTAMPTZ
);

CREATE TABLE mahsulotlar (
    id   INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi VARCHAR(80)   NOT NULL,
    narx NUMERIC(12,2) NOT NULL CHECK (narx > 0)
);

-- ─────────────────────────────────────────────────────────────────────
-- 2) ON DELETE RESTRICT — защищает финансовую историю
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE buyurtmalar (
    id         INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- RESTRICT: клиента, у которого есть заказы, удалить НЕЛЬЗЯ
    mijoz_id   INTEGER     NOT NULL REFERENCES mijozlar(id) ON DELETE RESTRICT,
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────
-- 3) ON DELETE CASCADE — когда дочерняя строка без родителя бессмысленна
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    -- а на товар — RESTRICT: удаление проданного товара из каталога
    -- испортило бы историю
    mahsulot_id INTEGER NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor      INTEGER NOT NULL CHECK (miqdor > 0),
    -- ИСТОРИЧЕСКАЯ цена: даже если цена товара изменится, чек не изменится
    narx_birlik NUMERIC(12,2) NOT NULL CHECK (narx_birlik > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)
);

-- ─────────────────────────────────────────────────────────────────────
-- 4) ON DELETE SET NULL — когда связь необязательна
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE xodimlar (
    id  INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ism VARCHAR(80) NOT NULL
);

CREATE TABLE vazifalar (
    id        INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sarlavha  VARCHAR(150) NOT NULL,
    -- чтобы SET NULL работал, колонка ОБЯЗАНА допускать NULL
    xodim_id  INTEGER      REFERENCES xodimlar(id) ON DELETE SET NULL,
    muddat    DATE
);

-- ── Тестовые данные ───────────────────────────────────────────────────
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
-- ЭКСПЕРИМЕНТ 1: убеждаемся, что RESTRICT действительно защищает
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    DELETE FROM mijozlar WHERE id = 1;
    RAISE NOTICE 'Клиент удалён — это НЕОЖИДАННЫЙ результат!';
EXCEPTION WHEN foreign_key_violation THEN
    RAISE NOTICE 'RESTRICT сработал: клиент с заказами не удалён.';
END $$;

-- Правильный подход — мягкое удаление. История сохраняется, клиент «исчезает»:
UPDATE mijozlar SET ochirilgan_sana = NOW() WHERE id = 1;

SELECT id, ism, ochirilgan_sana IS NOT NULL AS ochirilganmi FROM mijozlar ORDER BY id;

-- Приложение теперь выбирает только активных клиентов:
SELECT id, ism FROM mijozlar WHERE ochirilgan_sana IS NULL;

-- ─────────────────────────────────────────────────────────────────────
-- ЭКСПЕРИМЕНТ 2: CASCADE — удаляем заказ, вместе с ним уходят элементы
-- ─────────────────────────────────────────────────────────────────────
SELECT COUNT(*) AS elementlar_ochirishdan_oldin FROM buyurtma_elementlari;

DELETE FROM buyurtmalar WHERE id = 2;

SELECT COUNT(*) AS elementlar_ochirishdan_keyin FROM buyurtma_elementlari;
-- 4 -> 3. CASCADE отработал автоматически, «осиротевших» строк не осталось.

-- ─────────────────────────────────────────────────────────────────────
-- ЭКСПЕРИМЕНТ 3: SET NULL — сотрудник уволился, задачи остались
-- ─────────────────────────────────────────────────────────────────────
DELETE FROM xodimlar WHERE id = 1;

SELECT sarlavha, xodim_id, muddat FROM vazifalar ORDER BY id;
-- У двух задач xodim_id = NULL. Работа не потерялась, просто осталась без
-- исполнителя — менеджер может переназначить её.

-- ─────────────────────────────────────────────────────────────────────
-- ВАЖНОЕ ЗАМЕЧАНИЕ: PostgreSQL НЕ СОЗДАЁТ индекс для колонки FK
-- автоматически. Индекс получают только PRIMARY KEY и UNIQUE. Без индекса
-- на FK каждое удаление родительской строки приводит к полному
-- сканированию дочерней таблицы.
-- ─────────────────────────────────────────────────────────────────────
CREATE INDEX buyurtmalar_mijoz_id_idx  ON buyurtmalar (mijoz_id);
CREATE INDEX vazifalar_xodim_id_idx    ON vazifalar (xodim_id);
CREATE INDEX bel_mahsulot_id_idx       ON buyurtma_elementlari (mahsulot_id);
""",
    "exercises": {
        4763: {
            "title": "Email в роли PRIMARY KEY",
            "description": "Почему делать email пользователя первичным ключом — плохая идея?",
            "hint": "Важнейшее свойство первичного ключа — стабильность.",
            "explanation": "Главная проблема натурального ключа — изменчивость. При смене email придётся обновить значения во всех таблицах, связанных внешним ключом. Суррогатный id не меняется никогда, поэтому правильнее хранить email как ограничение UNIQUE.",
        },
        4764: {
            "title": "Верная стратегия при удалении клиента",
            "description": "Какая стратегия ON DELETE для buyurtmalar.mijoz_id защищает финансовую историю и рекомендуется в связке с мягким удалением?",
            "hint": "Клиента, у которого есть заказы, вообще не должно быть возможно удалить.",
            "explanation": "RESTRICT блокирует удаление клиента, у которого есть заказы, и тем самым сохраняет историю продаж. CASCADE в этом случае уничтожил бы всю финансовую историю.",
        },
        4765: {
            "title": "Колонка FK и индекс",
            "description": "Создаёт ли PostgreSQL индекс для колонки FOREIGN KEY автоматически? Ответьте одним словом (ha / yo'q).",
            "hint": "Автоматический индекс появляется только у ограничений PRIMARY KEY и UNIQUE.",
            "explanation": "PostgreSQL не создаёт индекс для колонки FK — это нужно делать вручную. Иначе при каждом удалении или обновлении родительской строки дочерняя таблица сканируется целиком.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 833 — ограничения
# ═════════════════════════════════════════════════════════════════════════════
L7 = {
    "lesson_id": 833,
    "title": "7-Ограничения CHECK и UNIQUE, значения по умолчанию",
    "text": """\
<h3>Где должно жить бизнес-правило?</h3>
<p>«Цена должна быть положительной» &mdash; куда мы запишем это правило? Большинство ответит: в код приложения, в функцию валидации. Этого ответа недостаточно.</p>
<p>База данных общается не с одним приложением. С ней работают: веб-бэкенд, мобильный API, cron-скрипт, ETL-загрузка данных, файл миграции, написанный вручную <code>UPDATE</code> аналитика и скрипт-заплатка, запущенный в полночь. Валидация в приложении покрывает лишь одного из них.</p>
<p><strong>Ограничение на уровне базы &mdash; последняя и единственная надёжная линия обороны.</strong> Чтобы его обойти, ограничение нужно намеренно отключить.</p>

<h3>Четыре основных ограничения</h3>
<table>
<tr><th>Ограничение</th><th>Что гарантирует</th><th>Пример</th></tr>
<tr><td><code>NOT NULL</code></td><td>Значение обязательно</td><td><code>email VARCHAR(120) NOT NULL</code></td></tr>
<tr><td><code>DEFAULT</code></td><td>Какое значение подставить, если не указано</td><td><code>holat VARCHAR(12) DEFAULT 'yangi'</code></td></tr>
<tr><td><code>UNIQUE</code></td><td>Значение не повторяется</td><td><code>UNIQUE (email)</code></td></tr>
<tr><td><code>CHECK</code></td><td>Произвольное логическое условие</td><td><code>CHECK (narx &gt; 0)</code></td></tr>
</table>

<h3>NULL &mdash; ловушка при работе с UNIQUE и CHECK</h3>
<p>Это место, где новички ошибаются чаще всего, поэтому запомните точно:</p>
<ul>
<li><strong><code>UNIQUE</code> и NULL:</strong> в SQL <code>NULL = NULL</code> даёт не истину, а <code>NULL</code>. Поэтому в колонку с <code>UNIQUE</code> <strong>может попасть несколько <code>NULL</code></strong>. Если вас это не устраивает &mdash; добавьте <code>NOT NULL</code> или используйте <code>UNIQUE NULLS NOT DISTINCT</code> в PostgreSQL 15+.</li>
<li><strong><code>CHECK</code> и NULL:</strong> если условие <code>CHECK</code> возвращает <code>NULL</code> (неизвестно), ограничение считается <strong>не нарушенным</strong>. То есть в колонку с <code>CHECK (yosh &gt;= 18)</code> спокойно запишется <code>NULL</code>. Строку отвергает только <code>FALSE</code>.</li>
</ul>

<h3>Когда применяется DEFAULT</h3>
<p>DEFAULT срабатывает только тогда, когда колонка <em>вообще не указана</em> в <code>INSERT</code>. Если вы явно записываете <code>NULL</code> &mdash; DEFAULT не применяется и в колонку попадает <code>NULL</code>. Эта разница часто становится источником проблем при импорте данных.</p>

<pre class="mermaid">
flowchart TB
  I["Пришёл запрос INSERT"] --> N{"Колонка указана?"}
  N -->|"Нет"| D["Подставляется значение DEFAULT"]
  N -->|"Да, записан NULL"| NL["Записывается NULL — DEFAULT НЕ РАБОТАЕТ"]
  N -->|"Да, есть значение"| V["Берётся значение"]
  D --> C{"Проверка
NOT NULL / CHECK / UNIQUE"}
  NL --> C
  V --> C
  C -->|"Все условия TRUE или NULL"| OK["Строка записана"]
  C -->|"Какое-то условие FALSE"| ERR["ERROR — строка отвергнута"]
</pre>

<h3>Практические советы</h3>
<ul>
<li><strong>Давайте ограничениям имена.</strong> <code>CONSTRAINT mahsulotlar_narx_musbat CHECK (narx &gt; 0)</code>. Автоматическое имя (<code>mahsulotlar_narx_check</code>) ничего не говорит пользователю в тексте ошибки, и найти его в миграциях сложнее.</li>
<li><strong>Для колонок-статусов пишите <code>CHECK (holat IN (...))</code>.</strong> Это гибче <code>ENUM</code>: чтобы добавить новое значение, достаточно <code>ALTER TABLE ... DROP CONSTRAINT / ADD CONSTRAINT</code>, тогда как <code>ENUM</code> требует изменения типа.</li>
<li><strong>Не бойтесь <code>CHECK</code>, связывающих несколько колонок:</strong> <code>CHECK (tugash_sanasi &gt; boshlanish_sanasi)</code>. Это ограничение уровня таблицы, и оно полностью устраняет самые частые ошибки с датами в приложении.</li>
<li><strong>Для условной уникальности &mdash; частичный unique-индекс:</strong> <code>CREATE UNIQUE INDEX ... WHERE ochirilgan_sana IS NULL</code>. Тогда удалённые записи не занимают уникальное значение.</li>
</ul>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Ограничения: бизнес-правила обеспечивает не приложение, а БАЗА
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

    -- Даём ограничению ИМЯ: текст ошибки станет понятным
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
-- holat не указан -> подставлено значение DEFAULT 'bosh'

SELECT raqami, qavat, sigim, narx, holat FROM xonalar ORDER BY raqami;

-- ─────────────────────────────────────────────────────────────────────
-- Проверяем, что каждое ограничение действительно работает.
-- Внутри блока DO перехватываем ошибку и выводим NOTICE.
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx) VALUES ('999', 45, 2, 500000);
    RAISE NOTICE 'ОШИБКА: 45-й этаж был принят!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK сработал: 45-й этаж отвергнут (допустимо 1..30).';
END $$;

DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx) VALUES ('102', 1, 2, 450000);
    RAISE NOTICE 'ОШИБКА: повторный номер комнаты был принят!';
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'UNIQUE сработал: комната 102 не создана дважды.';
END $$;

DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx, holat)
    VALUES ('401', 4, 2, 500000, 'tozalanmoqda');
    RAISE NOTICE 'ОШИБКА: неизвестный статус был принят!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK IN сработал: статус "tozalanmoqda" не разрешён.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- CHECK по нескольким колонкам: логика дат на уровне базы данных
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
    RAISE NOTICE 'ОШИБКА: бронь с выездом раньше заезда была принята!';
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'CHECK сработал: дата выезда не может быть раньше заезда.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- ЛОВУШКИ NULL — обязательно попробуйте их сами
-- ─────────────────────────────────────────────────────────────────────

-- 1) В колонку с UNIQUE ПОПАДАЁТ несколько NULL, потому что NULL != NULL
ALTER TABLE xonalar ADD COLUMN qayd_raqami VARCHAR(20);
ALTER TABLE xonalar ADD CONSTRAINT xonalar_qayd_uq UNIQUE (qayd_raqami);

UPDATE xonalar SET qayd_raqami = NULL;   -- везде NULL
SELECT COUNT(*) AS null_qatorlar FROM xonalar WHERE qayd_raqami IS NULL;
-- 4 строки, все NULL — и UNIQUE не возразил ни разу!

-- 2) Если условие CHECK вернуло NULL, ограничение считается НЕ нарушенным
ALTER TABLE xonalar ADD COLUMN yosh_chegarasi SMALLINT;
ALTER TABLE xonalar ADD CONSTRAINT xonalar_yosh_check
    CHECK (yosh_chegarasi >= 18);

INSERT INTO xonalar (raqami, qavat, sigim, narx, yosh_chegarasi)
VALUES ('501', 5, 2, 600000, NULL);   -- NULL проходит свободно!

SELECT raqami, yosh_chegarasi FROM xonalar WHERE raqami = '501';
-- Если значение обязательно, CHECK недостаточно — нужен ещё и NOT NULL.

-- ─────────────────────────────────────────────────────────────────────
-- Ловушка DEFAULT: при явно указанном NULL значение DEFAULT НЕ работает
-- ─────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    INSERT INTO xonalar (raqami, qavat, sigim, narx, holat)
    VALUES ('502', 5, 2, 600000, NULL);
    RAISE NOTICE 'ОШИБКА: NULL в статусе был принят!';
EXCEPTION WHEN not_null_violation THEN
    RAISE NOTICE 'NOT NULL сработал: при явном NULL значение DEFAULT не применяется.';
END $$;

-- ─────────────────────────────────────────────────────────────────────
-- ЧАСТИЧНЫЙ UNIQUE-ИНДЕКС: условная уникальность.
-- Отменённые брони не должны занимать уникальное значение
-- ─────────────────────────────────────────────────────────────────────
CREATE UNIQUE INDEX bronlar_faol_xona_sana_uq
    ON bronlar (xona_id, kirish_sanasi)
    WHERE bekor_qilingan = FALSE;

-- На ту же дату, что и у отменённой брони, новую записать МОЖНО:
UPDATE bronlar SET bekor_qilingan = TRUE WHERE id = 1;
INSERT INTO bronlar (xona_id, mehmon_email, kirish_sanasi, chiqish_sanasi)
VALUES (1, 'yangi@mail.uz', DATE '2026-08-01', DATE '2026-08-04');

SELECT id, xona_id, mehmon_email, kirish_sanasi, bekor_qilingan
FROM bronlar ORDER BY id;
""",
    "exercises": {
        4766: {
            "title": "UNIQUE и NULL",
            "description": "Сколько значений NULL можно вставить в колонку с ограничением UNIQUE (в PostgreSQL, при настройках по умолчанию)?",
            "hint": "В SQL выражение NULL = NULL возвращает не TRUE, а NULL.",
            "explanation": "В SQL сравнение NULL = NULL возвращает NULL (неизвестно), поэтому ограничение UNIQUE допускает несколько значений NULL. Если это не нужно — добавьте NOT NULL или используйте UNIQUE NULLS NOT DISTINCT в PostgreSQL 15+.",
        },
        4767: {
            "title": "Когда условие CHECK возвращает NULL",
            "description": "Что произойдёт, если в колонку с ограничением CHECK (yosh >= 18) записать значение NULL? Заполните пропуск: строка ___ (принимается / отвергается).",
            "hint": "CHECK отвергает строку только при результате FALSE.",
            "explanation": "Если условие CHECK возвращает NULL (неизвестно), ограничение считается не нарушенным и строка принимается. Если значение обязательно, одного CHECK мало — нужно добавить и NOT NULL.",
        },
        4768: {
            "title": "Порядок уровней проверки",
            "description": "В каком порядке PostgreSQL обрабатывает пришедший запрос INSERT? Расположите шаги правильно.",
            "hint": "Сначала формируется значение, затем проверки уровня колонки, в конце — межтабличные.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 834 — ER-диаграммы
# ═════════════════════════════════════════════════════════════════════════════
L8 = {
    "lesson_id": 834,
    "title": "8-ER-диаграммы — от проекта к коду",
    "text": """\
<h3>Почему сначала рисуют диаграмму</h3>
<p>Нарисовать схему до написания <code>CREATE TABLE</code> &mdash; это не про экономию времени, а про то, чтобы <em>найти ошибку на дешёвом этапе</em>. Изменить связь на диаграмме &mdash; 10 секунд. В работающей базе то же самое &mdash; это миграция, перенос данных, правка кода приложения и деплой.</p>
<p><strong>ER-диаграмма</strong> (Entity-Relationship) показывает три вещи: какие есть сущности, какие у них атрибуты и как они связаны между собой.</p>

<h3>Нотация «вороньей лапки» (crow's foot)</h3>
<p>Самый распространённый способ обозначения. Каждый конец линии состоит из двух символов: первый &mdash; <em>минимум</em> (0 или 1), второй &mdash; <em>максимум</em> (1 или много).</p>
<table>
<tr><th>Обозначение</th><th>Запись в mermaid</th><th>Значение</th></tr>
<tr><td>Один (ровно)</td><td><code>||</code></td><td>Ровно один</td></tr>
<tr><td>Ноль или один</td><td><code>o|</code></td><td>Необязательно, не более одного</td></tr>
<tr><td>Один или много</td><td><code>}|</code></td><td>Как минимум один</td></tr>
<tr><td>Ноль или много</td><td><code>}o</code></td><td>Необязательно, без ограничений</td></tr>
</table>
<p>Самые употребимые сочетания:</p>
<ul>
<li><code>MIJOZLAR ||--o{ BUYURTMALAR</code> &mdash; у клиента ноль или много заказов; у каждого заказа ровно один клиент.</li>
<li><code>USERS ||--o| PROFILLAR</code> &mdash; 1:1, профиль необязателен.</li>
<li><code>BUYURTMALAR ||--|{ ELEMENTLAR</code> &mdash; в заказе должен быть хотя бы один элемент.</li>
</ul>

<h3>Полный пример: небольшой e-commerce</h3>
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

<h3>От диаграммы к коду: механический перевод</h3>
<p>Если ER-диаграмма нарисована правильно, написание <code>CREATE TABLE</code> перестаёт быть творчеством &mdash; это механический перевод. Правила:</p>
<table>
<tr><th>На диаграмме</th><th>В коде</th></tr>
<tr><td>Сущность (прямоугольник)</td><td><code>CREATE TABLE</code></td></tr>
<tr><td>Пометка <code>PK</code></td><td><code>PRIMARY KEY</code></td></tr>
<tr><td>Пометка <code>UK</code></td><td>ограничение <code>UNIQUE</code></td></tr>
<tr><td>Пометка <code>FK</code></td><td><code>REFERENCES boshqa_jadval(id)</code></td></tr>
<tr><td><code>||--o{</code> (1:N)</td><td>FK в таблице на стороне «многие»</td></tr>
<tr><td><code>||--o|</code> (1:1)</td><td>FK + <code>UNIQUE</code> (или FK = PK)</td></tr>
<tr><td>Связь N:N</td><td>Junction-таблица, составной PK</td></tr>
<tr><td><code>||</code> слева (обязательно)</td><td><code>NOT NULL</code> на колонке FK</td></tr>
<tr><td><code>o|</code> слева (необязательно)</td><td>колонка FK допускает <code>NULL</code></td></tr>
</table>
<p>Обратите внимание: в mermaid <code>erDiagram</code> связь N:N <em>можно</em> нарисовать как <code>}o--o{</code>, но в коде она никогда не реализуется напрямую. Поэтому рисуйте её сразу с junction-таблицей &mdash; тогда диаграмма будет отражать настоящую схему, а не её упрощённую фантазию.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- От ER-диаграммы к CREATE TABLE — механический перевод
-- Проследите шаг за шагом, как каждое обозначение с диаграммы
-- выше выглядит в коде.
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
    email           VARCHAR(120) NOT NULL UNIQUE,   -- UK с диаграммы
    ism             VARCHAR(80)  NOT NULL,
    ochirilgan_sana TIMESTAMPTZ
);

-- ── MIJOZLAR ||--o| MIJOZ_PROFILLARI ──────────────────────────────────
-- «o|» = ноль или один -> 1:1, профиль необязателен.
-- Способ PK = FK: уникальность обеспечивается автоматически.
CREATE TABLE mijoz_profillari (
    mijoz_id INTEGER PRIMARY KEY REFERENCES mijozlar(id) ON DELETE CASCADE,
    telefon  VARCHAR(20),
    manzil   TEXT
);

-- ── KATEGORIYALAR ||--o{ MAHSULOTLAR ──────────────────────────────────
-- «||» слева = у каждого товара РОВНО ОДНА категория -> FK NOT NULL
-- «o{» справа = у категории ноль или много товаров -> UNIQUE на FK нет
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
-- «|{» = должен быть хотя бы ОДИН элемент.
-- Внимание: сам по себе CREATE TABLE обеспечить это правило НЕ МОЖЕТ —
-- оно достигается только логикой приложения или отложенной (DEFERRABLE)
-- проверкой. Это одно из немногих мест, где ER-диаграмма не совпадает
-- с кодом на 100%.
CREATE TABLE buyurtma_elementlari (
    buyurtma_id INTEGER       NOT NULL REFERENCES buyurtmalar(id) ON DELETE CASCADE,
    mahsulot_id INTEGER       NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    miqdor      INTEGER       NOT NULL CHECK (miqdor > 0),
    narx_birlik NUMERIC(12,2) NOT NULL CHECK (narx_birlik > 0),
    PRIMARY KEY (buyurtma_id, mahsulot_id)   -- составной PK, junction N:N
);

-- Индексы на колонки FK (PK покрывает первую колонку, вторую — нет)
CREATE INDEX mahsulotlar_kategoriya_idx ON mahsulotlar (kategoriya_id);
CREATE INDEX buyurtmalar_mijoz_idx      ON buyurtmalar (mijoz_id);
CREATE INDEX bel_mahsulot_idx           ON buyurtma_elementlari (mahsulot_id);

-- ── Тестовые данные ───────────────────────────────────────────────────
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
-- ОБРАТНОЕ НАПРАВЛЕНИЕ: восстанавливаем диаграмму из существующей базы.
-- Запрос ниже выводит все связи FK в виде «вороньей лапки» — первый
-- запрос, который запускают, попав в чужой проект.
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

-- Список ограничений по каждой таблице — для проверки дизайна
SELECT conrelid::regclass AS jadval,
       conname            AS cheklov_nomi,
       CASE contype WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'c' THEN 'CHECK' END AS turi
FROM pg_constraint
WHERE connamespace = current_schema()::regnamespace
ORDER BY jadval, turi;
""",
    "exercises": {
        4769: {
            "title": "Воронья лапка: что означает ||--o{?",
            "description": "Какую связь обозначает запись MIJOZLAR ||--o{ BUYURTMALAR в mermaid erDiagram?",
            "hint": "'o' — ноль (необязательно), '{' — много, '||' — ровно один.",
            "explanation": "|| слева означает «ровно один», а o{ справа — «ноль или много». То есть классическая связь 1:N: у каждого заказа один клиент, а у клиента заказов может не быть вовсе.",
        },
        4770: {
            "title": "Переводим 1:1 в код",
            "description": "На ER-диаграмме показана связь USERS ||--o| PROFILLAR. Как вы объявите колонку user_id в таблице PROFILLAR на SQL? Напишите одной строкой (в виде определения колонки).",
            "hint": "Для 1:1 нужно либо сделать колонку FK одновременно PRIMARY KEY, либо добавить к ней UNIQUE.",
            "expected_answer": "user_id INTEGER PRIMARY KEY REFERENCES users(id)",
        },
        4771: {
            "title": "Порядок перехода от диаграммы к коду",
            "description": "Расположите в правильном порядке шаги превращения ER-диаграммы в работающую схему.",
            "hint": "Чтобы FK работал, родительская таблица должна существовать заранее; индексы — в конце.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 835 — денормализация
# ═════════════════════════════════════════════════════════════════════════════
L9 = {
    "lesson_id": 835,
    "title": "9-Денормализация — когда и зачем нарушать правила",
    "text": """\
<h3>Восемь уроков мы нормализовали. Теперь поговорим, когда стоит нарушить правила</h3>
<p>Начнём честно: <strong>денормализация &mdash; это оптимизация, а не проектирование.</strong> Её применяют, начав с нормальной схемы и только увидев измеренную проблему. «Мне кажется, это будет работать медленно» &mdash; не основание. Основание &mdash; результат <code>EXPLAIN ANALYZE</code>.</p>
<p>И второе честное замечание: денормализация <em>не бесплатна</em>. Вы покупаете <strong>скорость чтения</strong>, а расплачиваетесь <strong>риском нарушения целостности данных</strong>. Продублированное значение &mdash; это значение, которое рано или поздно перестанет совпадать с оригиналом. Вопрос лишь в том, выгодна ли вам такая сделка.</p>

<h3>Когда денормализация оправдана</h3>
<ul>
<li><strong>Чтений в 100 раз больше, чем записей.</strong> Число лайков под постом показывается на каждой странице, но меняется несколько раз в день.</li>
<li><strong>Агрегат каждый раз сканирует всю таблицу.</strong> «Сумма лайков по 40 000 постов этого пользователя» &mdash; считать это через <code>COUNT</code> в каждом запросе просто глупо.</li>
<li><strong>Отчёт не обязан быть в реальном времени.</strong> Если дневной дашборд отстаёт на 15 минут, этого никто не заметит. Идеальный случай для <code>MATERIALIZED VIEW</code>.</li>
<li><strong>Глубина JOIN превысила 5&ndash;6 таблиц</strong>, и запрос находится на самом горячем пути.</li>
</ul>

<h3>Когда денормализацию делать НЕ надо</h3>
<ul>
<li><strong>В начале проекта.</strong> У вас ещё нет ни данных, ни измерений. Это чистая догадка.</li>
<li><strong>Когда достаточно обычного индекса.</strong> Перед денормализацией всегда попробуйте индекс, переписывание запроса и <code>EXPLAIN ANALYZE</code>. На практике большинство «медленных запросов» вызвано именно отсутствующим индексом.</li>
<li><strong>Когда данные имеют финансовое или юридическое значение</strong>, а вы не уверены, что сумеете держать их синхронными.</li>
</ul>

<h3>Три практических способа</h3>
<table>
<tr><th>Способ</th><th>Обновление</th><th>Актуальность данных</th><th>Риск</th></tr>
<tr><td>Вычисляемая колонка + <code>TRIGGER</code></td><td>Автоматически, в той же транзакции</td><td>Всегда точна</td><td>Низкий &mdash; но каждая запись чуть дороже</td></tr>
<tr><td>Вычисляемая колонка + код приложения</td><td>Вручную, в приложении</td><td>Зависит от кода</td><td><strong>Высокий</strong> &mdash; достаточно одного забытого места</td></tr>
<tr><td><code>MATERIALIZED VIEW</code></td><td>Через <code>REFRESH</code></td><td>Отстаёт</td><td>Низкий &mdash; исходные данные не портятся</td></tr>
<tr><td>Историческая копия (narx_birlik)</td><td>Пишется один раз</td><td>Намеренно «старая»</td><td>Нулевой &mdash; это не денормализация</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  S["Запрос работает медленно"] --> E["Измерьте через EXPLAIN ANALYZE"]
  E --> I{"Не хватает индекса?"}
  I -->|"Да"| IX["Добавьте индекс. ГОТОВО —
денормализация не нужна."]
  I -->|"Нет"| Q{"Поможет ли переписать
запрос?"}
  Q -->|"Да"| QR["CTE / порядок JOIN / оконные функции.
ГОТОВО."]
  Q -->|"Нет"| F{"Данные обязаны быть
в реальном времени?"}
  F -->|"Нет"| MV["MATERIALIZED VIEW +
REFRESH по расписанию"]
  F -->|"Да"| TR["Вычисляемая колонка + TRIGGER
(коду приложения НЕ ДОВЕРЯЙТЕ)"]
</pre>

<h3>Самое важное правило</h3>
<p>Если вы добавили вычисляемую колонку, она <strong>никогда</strong> не должна обновляться кодом приложения. В приложении десятки мест: веб-API, админка, скрипт импорта, миграция, ручная правка. Одно из них забудет сделать <code>UPDATE</code> &mdash; и у вас появится ошибка «лайков 47, а на самом деле 52», которую никто не заметит годами.</p>
<p>Решение &mdash; <code>TRIGGER</code>. Он написан в одном месте, работает внутри транзакции, и обойти его нельзя. И обязательно: напишите <em>проверочный запрос</em>, сравнивающий вычисленное значение с исходными данными, и запускайте его время от времени.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Денормализация: вычисляемая колонка, TRIGGER и MATERIALIZED VIEW
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
    -- ── ДЕНОРМАЛИЗАЦИЯ: вычисляемая колонка ──────────────────────────
    -- Источник истины — таблица layklar. Эта колонка — её КЭШ.
    -- Обновляет её только триггер; код приложения к ней НЕ ПРИКАСАЕТСЯ.
    layklar_soni INTEGER NOT NULL DEFAULT 0 CHECK (layklar_soni >= 0)
);

CREATE TABLE layklar (
    post_id       INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    foydalanuvchi_id INTEGER  NOT NULL REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bosilgan      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- один человек ставит лайк одному посту один раз
    PRIMARY KEY (post_id, foydalanuvchi_id)
);

CREATE INDEX layklar_foydalanuvchi_idx ON layklar (foydalanuvchi_id);

-- ─────────────────────────────────────────────────────────────────────
-- TRIGGER: обновляет вычисляемую колонку АВТОМАТИЧЕСКИ и в той же транзакции
-- ─────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION layklar_sonini_yangilash() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE postlar SET layklar_soni = layklar_soni + 1 WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE postlar SET layklar_soni = layklar_soni - 1 WHERE id = OLD.post_id;
    END IF;
    RETURN NULL;   -- для AFTER-триггера возвращаемое значение не важно
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER layklar_soni_trigger
    AFTER INSERT OR DELETE ON layklar
    FOR EACH ROW EXECUTE FUNCTION layklar_sonini_yangilash();

-- ── Тестовые данные ───────────────────────────────────────────────────
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

-- Триггер отработал сам — никто не писал UPDATE вручную:
SELECT id, LEFT(matn, 40) AS post, layklar_soni FROM postlar ORDER BY id;

-- При удалении лайка счётчик тоже остаётся верным:
DELETE FROM layklar WHERE post_id = 1 AND foydalanuvchi_id = 4;
SELECT id, layklar_soni FROM postlar WHERE id = 1;   -- 3 -> 2

-- ─────────────────────────────────────────────────────────────────────
-- ПРОВЕРОЧНЫЙ ЗАПРОС: сверяем кэш с источником истины.
-- Запускайте его по cron раз в неделю. Результат должен быть пустым;
-- если он не пуст — проблема в триггере или в миграции.
-- ─────────────────────────────────────────────────────────────────────
SELECT p.id,
       p.layklar_soni       AS keshdagi_qiymat,
       COUNT(l.post_id)     AS haqiqiy_qiymat
FROM postlar p
LEFT JOIN layklar l ON l.post_id = p.id
GROUP BY p.id, p.layklar_soni
HAVING p.layklar_soni <> COUNT(l.post_id);
-- Пустой результат = кэш верен.

-- ─────────────────────────────────────────────────────────────────────
-- ПОЧЕМУ НЕЛЬЗЯ ДОВЕРЯТЬ КОДУ ПРИЛОЖЕНИЯ — живая демонстрация.
-- Представьте, что админка запустила скрипт «очистка спам-лайков»
-- и ЗАБЫЛА обновить layklar_soni:
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE layklar DISABLE TRIGGER layklar_soni_trigger;
DELETE FROM layklar WHERE post_id = 3;           -- триггер отключён!
ALTER TABLE layklar ENABLE TRIGGER layklar_soni_trigger;

-- Теперь проверочный запрос НАХОДИТ проблему:
SELECT p.id, p.layklar_soni AS keshdagi, COUNT(l.post_id) AS haqiqiy
FROM postlar p
LEFT JOIN layklar l ON l.post_id = p.id
GROUP BY p.id, p.layklar_soni
HAVING p.layklar_soni <> COUNT(l.post_id);
-- post 3: в кэше 2, на самом деле 0. Это и есть цена денормализации.

-- Исправляем:
UPDATE postlar p
SET layklar_soni = sub.haqiqiy
FROM (SELECT p2.id, COUNT(l.post_id) AS haqiqiy
      FROM postlar p2 LEFT JOIN layklar l ON l.post_id = p2.id
      GROUP BY p2.id) sub
WHERE p.id = sub.id AND p.layklar_soni <> sub.haqiqiy;

-- ─────────────────────────────────────────────────────────────────────
-- MATERIALIZED VIEW: самая безопасная денормализация для тяжёлых отчётов.
-- Исходные таблицы остаются чистыми, а кэш живёт в отдельном объекте.
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

-- Для REFRESH нужен UNIQUE-индекс (чтобы работал вариант CONCURRENTLY)
CREATE UNIQUE INDEX muallif_statistikasi_pk ON muallif_statistikasi (muallif_id);

SELECT * FROM muallif_statistikasi ORDER BY jami_layklar DESC;

-- Добавляем новые данные — VIEW пока остаётся в СТАРОМ состоянии:
INSERT INTO postlar (muallif_id, matn) VALUES (3, 'Denormalizatsiya — ehtiyotkorlik bilan.');
SELECT username, postlar_soni FROM muallif_statistikasi WHERE username = 'sardor';  -- 0

REFRESH MATERIALIZED VIEW muallif_statistikasi;
SELECT username, postlar_soni FROM muallif_statistikasi WHERE username = 'sardor';  -- 1

-- ВЫВОД: сначала индекс, затем переписывание запроса, затем
-- MATERIALIZED VIEW, и только в последнюю очередь — вычисляемая
-- колонка с триггером.
""",
    "exercises": {
        4772: {
            "title": "Что делать до денормализации?",
            "description": "Запрос работает медленно. Какие шаги нужно попробовать ДО перехода к денормализации?",
            "hint": "Один из вариантов — именно последняя мера, а не первая.",
            "explanation": "Сначала измерить, затем добавить индекс, затем переписать запрос. На практике большинство медленных запросов вызвано отсутствующим индексом. Вычисляемая колонка — крайняя мера, и обновлять её должен триггер, а не код приложения.",
        },
        4773: {
            "title": "Кто обновляет вычисляемую колонку?",
            "description": "Какой механизм наиболее надёжен для обновления вычисляемой колонки вроде postlar.layklar_soni? Напишите одним словом.",
            "hint": "Он написан в одном месте, работает внутри транзакции, и обойти его нельзя.",
            "explanation": "TRIGGER — самый надёжный вариант, потому что он живёт в самой базе и одинаково работает для ЛЮБОГО клиента, который в неё пишет (веб-API, скрипт, ручной запрос). Расчёт на код приложения рано или поздно приведёт к расхождению кэша с исходными данными.",
        },
        4774: {
            "title": "narx_birlik — это денормализация?",
            "description": "Считается ли колонка buyurtma_elementlari.narx_birlik денормализацией? Обоснуйте свой ответ в 1-2 предложениях.",
            "hint": "Кэш должен обновляться при изменении исходного значения. А должна ли обновляться narx_birlik?",
            "expected_answer": "Нет. narx_birlik — это не кэш цены товара, а отдельный исторический факт: цена на момент продажи. Даже если цена товара потом изменится, эта величина меняться не должна, поэтому речь не о дублировании, а о правильном дизайне.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 836 — R2 социальная сеть
# ═════════════════════════════════════════════════════════════════════════════
R2 = {
    "lesson_id": 836,
    "title": "R2-Схема БД социальной сети (повторение)",
    "text": """\
<h2>R2 &mdash; повторение модуля 2: схема социальной сети</h2>
<p>Объединяем всё изученное в уроках 6&ndash;9 &mdash; стратегии ключей, <code>ON DELETE</code>, ограничения, ER-диаграммы и денормализацию &mdash; в одной сложной схеме.</p>
<p>Задача: база данных для социальной сети типа Instagram/Twitter. В этой схеме есть одна сложность, которая не встречалась в предыдущих проектах.</p>

<h3>Новая сложность: self-referential N:N</h3>
<p>Посмотрите на связь подписки (follow): <strong>пользователь подписывается на пользователя</strong>. То есть обе стороны связи N:N &mdash; это одна и та же таблица <code>foydalanuvchilar</code>.</p>
<p>Junction-таблица выглядит так:</p>
<ul>
<li><code>obunachi_id</code> &rarr; <code>foydalanuvchilar(id)</code> &mdash; кто подписывается</li>
<li><code>obuna_bolingan_id</code> &rarr; <code>foydalanuvchilar(id)</code> &mdash; на кого подписывается</li>
<li><code>PRIMARY KEY (obunachi_id, obuna_bolingan_id)</code></li>
<li><code>CHECK (obunachi_id &lt;&gt; obuna_bolingan_id)</code> &mdash; <strong>нельзя подписаться на самого себя</strong></li>
</ul>
<p>Поскольку оба внешних ключа указывают на одну таблицу, имена колонок обязаны выражать <em>роль</em>. Назвать их <code>user_id_1</code> и <code>user_id_2</code> &mdash; гарантированный способ добиться того, что через полгода никто не вспомнит, кто из них кто.</p>
<p>Ещё один важный момент: подписка &mdash; <strong>направленная</strong> (directed) связь. Азиз может быть подписан на Дилнозу, а Дилноза на Азиза &mdash; нет. Это не дружба &mdash; для дружбы понадобились бы оба направления.</p>

<h3>Ожидаемая схема</h3>
<table>
<tr><th>Таблица</th><th>Назначение</th><th>На что обратить внимание</th></tr>
<tr><td><code>foydalanuvchilar</code></td><td>Аккаунт</td><td>username UNIQUE, мягкое удаление</td></tr>
<tr><td><code>profillar</code></td><td>Био, аватар &mdash; 1:1</td><td>PK = FK</td></tr>
<tr><td><code>postlar</code></td><td>Публикация</td><td>muallif_id 1:N, кэш layklar_soni</td></tr>
<tr><td><code>izohlar</code></td><td>Комментарий под постом</td><td>ota_izoh_id &mdash; ссылка на себя (threaded)</td></tr>
<tr><td><code>layklar</code></td><td>Кто что лайкнул</td><td>составной PK, N:N</td></tr>
<tr><td><code>obunalar</code></td><td>Кто на кого подписан</td><td>self-referential N:N + CHECK</td></tr>
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

<h3>Сложные вопросы, на которые от вас ждут ответа</h3>
<ol>
<li>Что должно происходить с постами, комментариями и лайками пользователя при удалении аккаунта? Что вы выберете для каждого случая &mdash; <code>CASCADE</code>, <code>RESTRICT</code> или <code>SET NULL</code> &mdash; и почему?</li>
<li>Колонка <code>izohlar.ota_izoh_id</code> ссылается на собственную таблицу. Что произойдёт с ответами при удалении родительского комментария &mdash; <code>CASCADE</code> (удалится вся ветка) или <code>SET NULL</code> (ответы поднимутся наверх)?</li>
<li>Как вы напишете запрос «посты тех, на кого подписан Азиз» (лента)?</li>
<li>Будете ли вы считать число подписчиков через <code>COUNT</code> или кэшировать его в вычисляемой колонке? В каких случаях достаточно первого варианта?</li>
</ol>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- R2 — схема социальной сети: СТАРТОВЫЙ НАБОР
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

-- 1:1 — профиль необязателен, PK = FK
CREATE TABLE profillar (
    foydalanuvchi_id INTEGER PRIMARY KEY
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    tolik_ism        VARCHAR(80),
    bio              VARCHAR(300),
    avatar_url       VARCHAR(255),
    sayt             VARCHAR(255)
);

-- 1:N — посты
CREATE TABLE postlar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    muallif_id   INTEGER     NOT NULL
                 REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    matn         VARCHAR(2200) NOT NULL,
    rasm_url     VARCHAR(255),
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- денормализация: обновляется триггером (см. урок 9)
    layklar_soni INTEGER     NOT NULL DEFAULT 0 CHECK (layklar_soni >= 0),
    CONSTRAINT postlar_matn_bosh_emas CHECK (LENGTH(TRIM(matn)) > 0)
);

-- SELF-REFERENTIAL 1:N — ответ на комментарий (threaded comments)
CREATE TABLE izohlar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id      INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    muallif_id   INTEGER     NOT NULL
                 REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    -- ссылка на собственную таблицу. NULL = это комментарий верхнего уровня.
    -- CASCADE: при удалении родителя удаляется и вся ветка ответов.
    ota_izoh_id  INTEGER     REFERENCES izohlar(id) ON DELETE CASCADE,
    matn         VARCHAR(1000) NOT NULL,
    yaratilgan   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- N:N — лайки
CREATE TABLE layklar (
    post_id          INTEGER     NOT NULL REFERENCES postlar(id) ON DELETE CASCADE,
    foydalanuvchi_id INTEGER     NOT NULL
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bosilgan         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (post_id, foydalanuvchi_id)
);

-- ─────────────────────────────────────────────────────────────────────
-- SELF-REFERENTIAL N:N — подписки. Главная новинка этого урока.
-- Оба внешних ключа указывают на одну таблицу, поэтому имена колонок
-- выражают РОЛЬ: кто подписался и на кого.
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE obunalar (
    obunachi_id        INTEGER NOT NULL
                       REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    obuna_bolingan_id  INTEGER NOT NULL
                       REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    boshlangan         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (obunachi_id, obuna_bolingan_id),
    -- НА СЕБЯ ПОДПИСАТЬСЯ НЕЛЬЗЯ — без этого схема ломается молча
    CONSTRAINT obunalar_ozi_emas CHECK (obunachi_id <> obuna_bolingan_id)
);

-- Индекс для обратного направления: запрос «кто подписан на меня?»
CREATE INDEX obunalar_obuna_bolingan_idx ON obunalar (obuna_bolingan_id);
CREATE INDEX izohlar_post_idx            ON izohlar (post_id);
CREATE INDEX izohlar_ota_idx             ON izohlar (ota_izoh_id);
CREATE INDEX layklar_foydalanuvchi_idx   ON layklar (foydalanuvchi_id);
CREATE INDEX postlar_muallif_vaqt_idx    ON postlar (muallif_id, yaratilgan DESC);

-- ── Тестовые данные ───────────────────────────────────────────────────
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
    (1, 3, 1,    'Qo''shilaman'),      -- ответ на комментарий 1
    (2, 1, NULL, 'Zo''r mavzu');

INSERT INTO layklar (post_id, foydalanuvchi_id) VALUES
    (1, 2), (1, 3), (2, 1), (3, 1), (3, 4);

INSERT INTO obunalar (obunachi_id, obuna_bolingan_id) VALUES
    (1, 2),   -- aziz -> dilnoza
    (1, 3),   -- aziz -> sardor
    (2, 1),   -- dilnoza -> aziz (взаимная подписка)
    (4, 2),   -- madina -> dilnoza
    (3, 2);   -- sardor -> dilnoza

-- Подписка на самого себя блокируется:
-- INSERT INTO obunalar (obunachi_id, obuna_bolingan_id) VALUES (1, 1);
-- ERROR:  new row violates check constraint "obunalar_ozi_emas"

-- ── Отчёты, подтверждающие схему ──────────────────────────────────────

-- 1) ЛЕНТА: посты тех, на кого подписан aziz
SELECT p.id, f.username AS muallif, p.matn, p.yaratilgan
FROM obunalar o
JOIN postlar p ON p.muallif_id = o.obuna_bolingan_id
JOIN foydalanuvchilar f ON f.id = p.muallif_id
WHERE o.obunachi_id = (SELECT id FROM foydalanuvchilar WHERE username = 'aziz')
ORDER BY p.yaratilgan DESC;

-- 2) Число подписчиков и подписок каждого пользователя
SELECT f.username,
       (SELECT COUNT(*) FROM obunalar WHERE obuna_bolingan_id = f.id) AS obunachilar,
       (SELECT COUNT(*) FROM obunalar WHERE obunachi_id = f.id)       AS obunalari
FROM foydalanuvchilar f
ORDER BY obunachilar DESC;

-- 3) ВЗАИМНЫЕ подписки (друзья) — self JOIN
SELECT a.username AS birinchi, b.username AS ikkinchi
FROM obunalar o1
JOIN obunalar o2
  ON o1.obunachi_id = o2.obuna_bolingan_id
 AND o1.obuna_bolingan_id = o2.obunachi_id
JOIN foydalanuvchilar a ON a.id = o1.obunachi_id
JOIN foydalanuvchilar b ON b.id = o1.obuna_bolingan_id
WHERE o1.obunachi_id < o1.obuna_bolingan_id;   -- чтобы пара не вышла дважды

-- 4) Threaded-комментарии — через рекурсивный CTE
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
""",
    "task_title": "🔁 R2: Схема БД социальной сети",
    "task_description": (
        "Спроектируйте полную схему для социальной сети типа Instagram/Twitter. "
        "Основная сложность — self-referential N:N (подписки) и self-referential "
        "1:N (ответ на комментарий). Результат — запускаемый .sql файл и ER-диаграмма."
    ),
    "task_requirements": (
        "• 6 таблиц: foydalanuvchilar, profillar, postlar, izohlar, layklar, obunalar\n"
        "• profillar — связь 1:1 с foydalanuvchilar (PK = FK или UNIQUE FK)\n"
        "• obunalar — self-referential N:N; имена колонок должны выражать РОЛЬ "
        "(obunachi_id / obuna_bolingan_id, а НЕ user_id_1 / user_id_2)\n"
        "• CHECK (obunachi_id <> obuna_bolingan_id) — запретить подписку на самого себя\n"
        "• izohlar.ota_izoh_id — ссылка на собственную таблицу (threaded-комментарии)\n"
        "• layklar — составной PK, один человек лайкает один пост один раз\n"
        "• UNIQUE и CHECK формата (regex) для username\n"
        "• Для каждого FK выберите стратегию ON DELETE и ОБОСНУЙТЕ её в комментарии --\n"
        "• postlar.layklar_soni — вычисляемая колонка, обновляемая триггером\n"
        "• Напишите проверочный запрос, сверяющий кэш с исходными данными\n"
        "• Индексы на все колонки FK и под запрос ленты\n"
        "• Тестовые данные: 6+ пользователей, 15+ постов, 20+ комментариев (минимум "
        "2 уровня вложенности), 30+ лайков, 15+ подписок\n"
        "• 6 отчётов: лента пользователя; взаимные подписки (self JOIN); "
        "ТОП-5 популярных постов; 3 пользователя с наибольшим числом подписчиков; "
        "threaded-комментарии (рекурсивный CTE); пользователи, на которых никто не подписан\n"
        "• Нарисуйте схему в виде mermaid erDiagram и добавьте её в .md файл"
    ),
    "task_technologies": (
        "PostgreSQL, self-referential FK, junction-таблица, составной ключ, CHECK, "
        "UNIQUE, partial/составной индекс, TRIGGER, рекурсивный CTE, self JOIN, mermaid erDiagram"
    ),
    "exercises": {
        4775: {
            "title": "Обязательное ограничение в self-referential N:N",
            "description": "В таблице obunalar(obunachi_id, obuna_bolingan_id) оба внешних ключа указывают на таблицу foydalanuvchilar. Какое ограничение в этой схеме ОБЯЗАТЕЛЬНО и о котором чаще всего забывают?",
            "hint": "Когда обе колонки ссылаются на одну таблицу, они могут оказаться равными.",
            "explanation": "В self-referential связи оба внешних ключа могут указывать на одну и ту же строку. Без CHECK (obunachi_id <> obuna_bolingan_id) пользователь сможет подписаться на самого себя и накрутить число подписчиков.",
        },
        4776: {
            "title": "Порядок создания схемы социальной сети",
            "description": "Расположите шаги создания схемы социальной сети в правильном порядке (учитывайте зависимости по внешним ключам).",
            "hint": "Чтобы FK работал, родительская таблица должна быть создана раньше; индексы — в конце.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 837 — редизайн e-commerce
# ═════════════════════════════════════════════════════════════════════════════
L10 = {
    "lesson_id": 837,
    "title": "10-Реальный кейс: перепроектируем схему e-commerce с нуля",
    "text": """\
<h3>Время покритиковать собственный код</h3>
<p>В финальном проекте курса «SQL va PostgreSQL Asoslari» вы построили аналитическую систему для интернет-магазина. Та схема выглядела так:</p>

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

<p>Для того курса эта схема была <em>вполне достаточной</em>: его целью было научить <code>JOIN</code>, <code>GROUP BY</code> и оконным функциям, а не проектированию схем. Теперь же у вас есть взгляд проектировщика. Посмотрим на ту же схему заново.</p>

<h3>Сначала &mdash; что сделано правильно</h3>
<ul>
<li><strong><code>buyurtma_elementlari.narx_birlik</code></strong> &mdash; самое важное верное решение. Это не копия цены товара, а <em>историческая цена на момент продажи</em>. Если завтра цена товара вырастет, вчерашний чек не изменится. Как мы видели в 3-м уроке, это не денормализация &mdash; это другой факт.</li>
<li><strong><code>ON DELETE RESTRICT</code> для товара и клиента</strong> &mdash; защищает историю продаж.</li>
<li><strong><code>ON DELETE CASCADE</code> для элементов заказа</strong> &mdash; верно: элемент без заказа бессмыслен.</li>
<li><strong><code>CHECK (holat IN (...))</code></strong> &mdash; колонка статуса не превратилась в текстовую свалку.</li>
<li><strong>Деньги в <code>NUMERIC</code>, время в <code>TIMESTAMPTZ</code></strong> &mdash; а не <code>FLOAT</code> и <code>TIMESTAMP</code>. Правильно.</li>
</ul>

<h3>А теперь &mdash; шесть серьёзных проблем</h3>

<h4>1. В <code>buyurtma_elementlari</code> открыт путь дубликатам</h4>
<p>В таблице есть <code>id SERIAL PRIMARY KEY</code>, но нет <code>UNIQUE (buyurtma_id, mahsulot_id)</code>. То есть один товар может оказаться в одном заказе <strong>дважды, отдельными строками</strong> &mdash; возможно, с разной ценой. Это настоящая ошибка: ваши отчёты начнут молча выдавать неверные цифры. Как мы видели в 5-м уроке, при добавлении суррогатного <code>id</code> ограничение <code>UNIQUE</code> нужно <em>обязательно</em> вернуть.</p>

<h4>2. <code>ec_mijozlar.shahar VARCHAR(50)</code> &mdash; свободный текст</h4>
<p>«Toshkent», «toshkent», «Tashkent», «Toshkent sh.» &mdash; для базы это четыре разных города. А отчёт по областям вообще невозможен, потому что данных об области нет. Как мы видели во 2-м уроке, это транзитивная зависимость: <code>город &rarr; область</code>. Решение &mdash; справочная таблица <code>shaharlar</code>.</p>

<h4>3. Адрес доставки отсутствует вообще</h4>
<p>В реальном e-commerce заказ куда-то доставляется. И здесь есть тонкость: брать адрес через <code>JOIN</code> из таблицы <code>mijozlar</code> &mdash; <strong>ошибка</strong>. Если клиент через год переедет, ваша трёхлетняя история доставок мгновенно станет ложной. Адрес должен записываться в строку заказа <em>копией</em> &mdash; точно так же, как <code>narx_birlik</code>.</p>

<h4>4. <code>NUMERIC(10,2)</code> &mdash; мало для сумов</h4>
<p><code>NUMERIC(10,2)</code> вмещает максимум 99 999 999.99 &mdash; то есть менее 100 миллионов сумов. Один ноутбук туда поместится, а вот дорогая техника, комплект мебели или крупный оптовый заказ <em>не поместятся</em>, и база упадёт с ошибкой <code>numeric field overflow</code>. Для системы, работающей в сумах, нужен как минимум <code>NUMERIC(14,2)</code>.</p>

<h4>5. <code>holat</code> смешивает два разных понятия</h4>
<p>В значениях <code>'kutmoqda'</code>, <code>'tasdiqlangan'</code>, <code>'yetkazildi'</code>, <code>'bekor'</code> спрятаны и статус <em>выполнения</em> заказа, и статус <em>оплаты</em>. Состояние «доставлено, но ещё не оплачено» в этой схеме выразить невозможно. Оплата &mdash; отдельная сущность: у неё есть сумма, способ, время и идентификатор транзакции.</p>

<h4>6. <code>mahsulotlar.zaxira</code> &mdash; скрытая денормализация</h4>
<p>Остаток на складе &mdash; это на самом деле <em>вычисляемая величина</em>: приход минус расход. Хранить его в одной колонке само по себе не ошибка (как мы видели в 9-м уроке, это допустимая оптимизация), но менять его простым <code>UPDATE</code> означает уничтожать историю: на вопрос «почему на складе на 3 штуки меньше?» вы никогда не ответите. Правильное решение &mdash; таблица <code>zaxira_harakatlari</code> и кэш поверх неё.</p>

<h3>Дополнительные мелкие недостатки</h3>
<table>
<tr><th>Проблема</th><th>Последствие</th><th>Решение</th></tr>
<tr><td>Категории плоские (нет родителя)</td><td>Нельзя построить иерархию «Телефоны &rarr; Смартфоны»</td><td><code>ota_id</code> &mdash; self-referential 1:N</td></tr>
<tr><td>Товар невозможно удалить (RESTRICT)</td><td>Устаревший товар остаётся в каталоге навсегда</td><td><code>faol BOOLEAN</code> или <code>ochirilgan_sana</code></td></tr>
<tr><td>Нет колонки <code>yangilangan</code></td><td>Неизвестно, что и когда менялось</td><td><code>yangilangan TIMESTAMPTZ</code> + триггер</td></tr>
<tr><td>Нет индексов на FK</td><td>Каждый <code>JOIN</code> и <code>DELETE</code> &mdash; полное сканирование</td><td><code>CREATE INDEX</code> на каждый FK</td></tr>
<tr><td><code>VARCHAR(50)</code> для имени</td><td>Длинное имя обрежется или вызовет ошибку</td><td><code>VARCHAR(120)</code> или <code>TEXT</code></td></tr>
</table>

<h3>Схема v2</h3>
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
<p>Обратите внимание: таблица <code>manzillar</code> <em>есть</em>, но <code>buyurtmalar</code> не связана с ней внешним ключом &mdash; заказ хранит <strong>копию текста</strong> адреса. Это сделано намеренно: даже если адрес потом изменится, история о том, куда была произведена доставка, меняться не должна.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- Схема e-commerce v2 — перепроектируем схему capstone-проекта из курса
-- «Asoslari», применяя всё изученное в этом курсе
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

-- ── ИСПРАВЛЕНИЕ 2: город не свободный текст, а справочник (3NF) ────────
CREATE TABLE shaharlar (
    id       INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi     VARCHAR(60) NOT NULL,
    viloyati VARCHAR(60) NOT NULL,
    CONSTRAINT shaharlar_nomi_viloyat_uq UNIQUE (nomi, viloyati)
);

CREATE TABLE mijozlar (
    id              INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- ИСПРАВЛЕНИЕ: достаточная длина для имени
    ism             VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL,
    shahar_id       INTEGER      REFERENCES shaharlar(id) ON DELETE SET NULL,
    royxatdan       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- ИСПРАВЛЕНИЕ: мягкое удаление — «скрыть» клиента, не удаляя его
    ochirilgan_sana TIMESTAMPTZ,
    CONSTRAINT mijozlar_email_uq  UNIQUE (email),
    CONSTRAINT mijozlar_email_fmt CHECK (email LIKE '%_@_%._%')
);

-- ── ИСПРАВЛЕНИЕ: иерархия категорий (self-referential 1:N) ────────────
CREATE TABLE kategoriyalar (
    id     INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ota_id INTEGER     REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi   VARCHAR(60) NOT NULL,
    CONSTRAINT kategoriyalar_nomi_uq UNIQUE (nomi),
    -- категория не может быть собственным родителем
    CONSTRAINT kategoriyalar_ota_ozi_emas CHECK (ota_id IS NULL OR ota_id <> id)
);

CREATE TABLE mahsulotlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kategoriya_id INTEGER       NOT NULL REFERENCES kategoriyalar(id) ON DELETE RESTRICT,
    nomi          VARCHAR(150)  NOT NULL,
    -- ИСПРАВЛЕНИЕ 4: NUMERIC(10,2) мало для сумов -> NUMERIC(14,2)
    narx          NUMERIC(14,2) NOT NULL CHECK (narx > 0),
    -- ИСПРАВЛЕНИЕ 6: zaxira — это КЭШ поверх zaxira_harakatlari.
    -- Обновляет его только триггер, а не код приложения.
    zaxira        INTEGER       NOT NULL DEFAULT 0 CHECK (zaxira >= 0),
    -- ИСПРАВЛЕНИЕ: мягкое удаление для снятия товара с продажи
    faol          BOOLEAN       NOT NULL DEFAULT TRUE,
    yaratilgan    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    yangilangan   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ── ИСПРАВЛЕНИЕ 3: сохранённые адреса клиента (1:N) ───────────────────
CREATE TABLE manzillar (
    id          INTEGER      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijoz_id    INTEGER      NOT NULL REFERENCES mijozlar(id) ON DELETE CASCADE,
    shahar_id   INTEGER      NOT NULL REFERENCES shaharlar(id) ON DELETE RESTRICT,
    kocha_uy    VARCHAR(200) NOT NULL,
    telefon     VARCHAR(20)  NOT NULL,
    asosiy      BOOLEAN      NOT NULL DEFAULT FALSE
);

-- У клиента только ОДИН основной адрес — частичный unique-индекс
CREATE UNIQUE INDEX manzillar_bitta_asosiy
    ON manzillar (mijoz_id) WHERE asosiy;

CREATE TABLE buyurtmalar (
    id           INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mijoz_id     INTEGER     NOT NULL REFERENCES mijozlar(id) ON DELETE RESTRICT,
    -- ИСПРАВЛЕНИЕ 5: статус выполнения и статус оплаты РАЗДЕЛЕНЫ
    holat        VARCHAR(20) NOT NULL DEFAULT 'yangi'
                 CHECK (holat IN ('yangi','yigilmoqda','jonatildi','yetkazildi','bekor')),
    -- ИСПРАВЛЕНИЕ 3: адрес не FK, а КОПИЯ. Даже если клиент переедет,
    -- место доставки этого заказа не изменится.
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
    -- ИСПРАВЛЕНИЕ 1: самое важное исправление. Без него один товар мог
    -- дважды попасть в один заказ и испортить отчёты.
    CONSTRAINT bel_buyurtma_mahsulot_uq UNIQUE (buyurtma_id, mahsulot_id)
);

-- ── ИСПРАВЛЕНИЕ 5: оплата — самостоятельная сущность ──────────────────
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
    -- идентификатор во внешней платёжной системе не должен повторяться
    CONSTRAINT tolovlar_tranzaksiya_uq UNIQUE (tranzaksiya_id)
);

-- ── ИСПРАВЛЕНИЕ 6: движение склада — история прихода и расхода ────────
CREATE TABLE zaxira_harakatlari (
    id          INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mahsulot_id INTEGER     NOT NULL REFERENCES mahsulotlar(id) ON DELETE RESTRICT,
    -- положительное = приход (поставка), отрицательное = расход (продажа)
    ozgarish    INTEGER     NOT NULL CHECK (ozgarish <> 0),
    sabab       VARCHAR(20) NOT NULL
                CHECK (sabab IN ('kirim','sotuv','qaytarish','inventarizatsiya','yaroqsiz')),
    buyurtma_id INTEGER     REFERENCES buyurtmalar(id) ON DELETE SET NULL,
    vaqti       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Триггер, удерживающий колонку-кэш в синхроне с движениями
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

-- ── Индексы: на каждый FK + на часто используемые фильтры ─────────────
CREATE INDEX mijozlar_shahar_idx        ON mijozlar (shahar_id);
CREATE INDEX kategoriyalar_ota_idx      ON kategoriyalar (ota_id);
CREATE INDEX mahsulotlar_kategoriya_idx ON mahsulotlar (kategoriya_id);
CREATE INDEX manzillar_mijoz_idx        ON manzillar (mijoz_id);
CREATE INDEX buyurtmalar_mijoz_vaqt_idx ON buyurtmalar (mijoz_id, yaratilgan DESC);
CREATE INDEX bel_mahsulot_idx           ON buyurtma_elementlari (mahsulot_id);
CREATE INDEX tolovlar_buyurtma_idx      ON tolovlar (buyurtma_id);
CREATE INDEX zaxira_mahsulot_vaqt_idx   ON zaxira_harakatlari (mahsulot_id, vaqti DESC);

-- ═══════════════════════════════════════════════════════════════════════
-- Тестовые данные
-- ═══════════════════════════════════════════════════════════════════════
INSERT INTO shaharlar (nomi, viloyati) VALUES
    ('Toshkent',  'Toshkent shahri'),
    ('Samarqand', 'Samarqand viloyati'),
    ('Buxoro',    'Buxoro viloyati');

INSERT INTO mijozlar (ism, email, shahar_id) VALUES
    ('Aziz Karimov',     'aziz@shop.uz',   1),
    ('Dilnoza Rasulova', 'dilya@shop.uz',  2),
    ('Sardor Tursunov',  'sardor@shop.uz', 1);

-- Иерархические категории
INSERT INTO kategoriyalar (ota_id, nomi) VALUES (NULL, 'Elektronika');
INSERT INTO kategoriyalar (ota_id, nomi) VALUES (1, 'Telefonlar'), (1, 'Noutbuklar');

INSERT INTO mahsulotlar (kategoriya_id, nomi, narx) VALUES
    (2, 'iPhone 15',      15000000),
    (2, 'Samsung S24',    12000000),
    (3, 'MacBook Pro 14', 22000000);

-- Склад меняется только через движения — триггер обновляет кэш
INSERT INTO zaxira_harakatlari (mahsulot_id, ozgarish, sabab) VALUES
    (1, 10, 'kirim'), (2, 8, 'kirim'), (3, 5, 'kirim');

SELECT nomi, zaxira FROM mahsulotlar ORDER BY id;   -- 10, 8, 5

INSERT INTO manzillar (mijoz_id, shahar_id, kocha_uy, telefon, asosiy) VALUES
    (1, 1, 'Amir Temur ko''chasi, 15-uy', '+998901112233', TRUE),
    (1, 1, 'Yunusobod 4-kvartal, 22-uy',  '+998901112233', FALSE),
    (2, 2, 'Registon ko''chasi, 7-uy',    '+998907778899', TRUE);

-- Второй «основной» адрес блокируется:
-- UPDATE manzillar SET asosiy = TRUE WHERE id = 2;
-- ERROR:  duplicate key value violates unique constraint "manzillar_bitta_asosiy"

-- Заказ: адрес записывается КОПИЕЙ, а не внешним ключом
INSERT INTO buyurtmalar (mijoz_id, holat, yetkazish_manzili, yetkazish_telefoni) VALUES
    (1, 'yetkazildi', 'Toshkent, Amir Temur ko''chasi, 15-uy', '+998901112233'),
    (2, 'yigilmoqda', 'Samarqand, Registon ko''chasi, 7-uy',   '+998907778899');

INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik) VALUES
    (1, 1, 1, 15000000),
    (1, 3, 1, 22000000),
    (2, 2, 2, 12000000);

-- Дубликат теперь БЛОКИРУЕТСЯ (в v1 он проходил свободно):
-- INSERT INTO buyurtma_elementlari (buyurtma_id, mahsulot_id, miqdor, narx_birlik)
-- VALUES (1, 1, 5, 14000000);
-- ERROR:  duplicate key value violates unique constraint "bel_buyurtma_mahsulot_uq"

-- Продажа создаёт расход на складе
INSERT INTO zaxira_harakatlari (mahsulot_id, ozgarish, sabab, buyurtma_id) VALUES
    (1, -1, 'sotuv', 1), (3, -1, 'sotuv', 1), (2, -2, 'sotuv', 2);

SELECT nomi, zaxira FROM mahsulotlar ORDER BY id;   -- 9, 6, 4

INSERT INTO tolovlar (buyurtma_id, summa, usul, holat, tranzaksiya_id) VALUES
    (1, 37000000, 'click', 'tasdiqlandi', 'CLK-2026-0001'),
    (2, 12000000, 'karta', 'tasdiqlandi', 'CRD-2026-0002');
-- Обратите внимание: заказ 2 оплачен частично (12 млн из 24 млн).
-- В схеме v1 выразить это было НЕВОЗМОЖНО.

-- ═══════════════════════════════════════════════════════════════════════
-- Новые возможности, которые открыла схема v2
-- ═══════════════════════════════════════════════════════════════════════

-- 1) Выручка по областям — в v1 это было НЕВОЗМОЖНО (область не хранилась)
SELECT s.viloyati,
       COUNT(DISTINCT b.id)              AS buyurtmalar,
       SUM(e.miqdor * e.narx_birlik)     AS daromad
FROM buyurtmalar b
JOIN mijozlar m  ON m.id = b.mijoz_id
JOIN shaharlar s ON s.id = m.shahar_id
JOIN buyurtma_elementlari e ON e.buyurtma_id = b.id
GROUP BY s.viloyati
ORDER BY daromad DESC;

-- 2) Не полностью оплаченные заказы — в v1 это было НЕВОЗМОЖНО
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

-- 3) История склада — ответ на вопрос «почему на 3 меньше?». В v1 НЕВОЗМОЖНО.
SELECT p.nomi, z.vaqti, z.ozgarish, z.sabab, z.buyurtma_id
FROM zaxira_harakatlari z
JOIN mahsulotlar p ON p.id = z.mahsulot_id
ORDER BY p.nomi, z.vaqti;

-- 4) Иерархия категорий — рекурсивный CTE. В v1 НЕВОЗМОЖНО.
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

-- 5) Проверка кэша: совпадает ли mahsulotlar.zaxira с движениями?
SELECT p.id, p.nomi, p.zaxira AS keshdagi,
       COALESCE(SUM(z.ozgarish), 0) AS haqiqiy
FROM mahsulotlar p
LEFT JOIN zaxira_harakatlari z ON z.mahsulot_id = p.id
GROUP BY p.id, p.nomi, p.zaxira
HAVING p.zaxira <> COALESCE(SUM(z.ozgarish), 0);
-- Пустой результат = кэш верен.
""",
    "exercises": {
        4777: {
            "title": "Настоящие ошибки в схеме v1",
            "description": "Какие из перечисленного являются настоящими ошибками проектирования в схеме e-commerce (v1) из курса «Асослари»?",
            "hint": "Одно из решений на самом деле верное — сохранение исторического факта.",
            "explanation": "Отсутствие UNIQUE, город в виде свободного текста и полное отсутствие адреса — настоящие ошибки. А вот narx_birlik, наоборот, верное решение: это не кэш цены товара, а историческая цена на момент продажи.",
        },
        4778: {
            "title": "Предел NUMERIC(10,2)",
            "description": "Напишите наибольшее значение, которое может хранить тип NUMERIC(10,2) (в виде, например: 999.99).",
            "hint": "Всего 10 цифр, из них 2 — в дробной части.",
            "expected_answer": "99999999.99",
        },
        4779: {
            "title": "Адрес доставки: FK или копия?",
            "description": "Как следует хранить адрес доставки в заказе?",
            "hint": "Та же логика, что и с narx_birlik: это исторический факт.",
            "explanation": "Адрес доставки — исторический факт на момент заказа, точно так же как narx_birlik. Если связать его внешним ключом, то при изменении адреса клиентом вся история доставок станет ложной. Поэтому он записывается в строку заказа копией.",
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson 838 — CAPSTONE
# ═════════════════════════════════════════════════════════════════════════════
C1 = {
    "lesson_id": 838,
    "title": "11-CAPSTONE: многотабличная система бронирования",
    "text": """\
<h2>🚀 CAPSTONE: многотабличная система бронирования</h2>

<p>Это финальный проект курса. Задача &mdash; <strong>с нуля</strong> спроектировать полную схему базы данных для системы бронирования типа Booking.com или Airbnb. Готовой схемы вам здесь не дадут: вы строите её сами, а каждое решение обязаны обосновать письменно.</p>

<h3>Сущности, которые нужно охватить</h3>
<table>
<tr><th>Сущность</th><th>Зачем нужна</th><th>Какие связи</th></tr>
<tr><td><code>foydalanuvchilar</code></td><td>И гость, и владелец жилья</td><td>1:1 с профилем</td></tr>
<tr><td><code>obyektlar</code> (listings)</td><td>Сдаваемый объект</td><td>1:N с владельцем</td></tr>
<tr><td><code>obyekt_qulayliklari</code></td><td>Wi-Fi, парковка, бассейн</td><td>N:N с объектами</td></tr>
<tr><td><code>bronlar</code></td><td>Кто, какой объект, на какие даты</td><td>N:N с обеими сторонами</td></tr>
<tr><td><code>tolovlar</code></td><td>Частичная оплата, возврат</td><td>1:N с бронями</td></tr>
<tr><td><code>sharhlar</code></td><td>Оценка и отзыв</td><td>1:1 с бронью</td></tr>
</table>

<h3>⚠️ Намеренно усложнённые проектные решения</h3>
<p>На следующие четыре вопроса вы должны дать <strong>письменный ответ</strong>. Для каждого обоснуйте выбранный вариант и объясните, почему не выбрали другой. Верных ответов может быть больше одного &mdash; оценивается <em>качество обоснования</em>.</p>

<h4>1. Как вы заблокируете пересечение дат?</h4>
<p>Один объект не должен быть забронирован двумя людьми одновременно. Обычный <code>UNIQUE</code> здесь не работает, потому что проблема не в точном равенстве, а в <em>пересечении интервалов</em>: брони 1&ndash;5 августа и 3&ndash;8 августа пересекаются, хотя значения их колонок не совпадают. Варианты:</p>
<ul>
<li>ограничение <code>EXCLUDE USING gist</code> с типом <code>daterange</code> (и расширением <code>btree_gist</code>) &mdash; полная гарантия на уровне базы;</li>
<li>проверка в коде приложения внутри транзакции с <code>SELECT ... FOR UPDATE</code>;</li>
<li>проверка пересечения внутри триггера.</li>
</ul>
<p>Что вы выберете и почему? В каком случае проверка на уровне приложения перестанет работать?</p>

<h4>2. Где хранится цена?</h4>
<p>Цена объекта за сутки со временем меняется (сезон, скидки). Если после бронирования цена изменится, сумма старой брони меняться не должна. Кроме того, нужна возможность заранее внести «цены на будущее лето». Достаточно ли одной колонки <code>obyektlar.narx</code>? Нужна ли таблица <code>narx_kalendari</code>? Хватит ли записи копии цены в строку брони?</p>

<h4>3. Как вы ограничите право писать отзыв?</h4>
<p>Отзыв должен иметь возможность написать только тот гость, который <em>действительно проживал</em> &mdash; то есть бронь существует и завершена. Как обеспечить это на уровне схемы? Достаточно ли сделать <code>sharhlar.bron_id</code> ключом <code>UNIQUE</code>? Можно ли выразить условие «бронь завершена» через <code>CHECK</code> (напоминание: <code>CHECK</code> не может обращаться к другой таблице)?</p>

<h4>4. Где живёт история отмен?</h4>
<p>При отмене брони вы делаете <code>DELETE</code> или ставите <code>holat = 'bekor'</code>? Что произойдёт, если оплата уже прошла? Даты отменённой брони должны немедленно освободиться &mdash; как это согласуется с ограничением на пересечение из первого вопроса?</p>

<h3>Технические требования</h3>
<ul>
<li>✅ Не менее 8 таблиц; все в 3NF (исключения обоснуйте)</li>
<li>✅ 1:1, 1:N и N:N &mdash; должны быть задействованы все три</li>
<li>✅ Как минимум одна self-referential связь</li>
<li>✅ Для каждого FK выбрана стратегия <code>ON DELETE</code> и обоснована в комментарии <code>--</code></li>
<li>✅ Деньги &mdash; <code>NUMERIC(14,2)</code>, время &mdash; <code>TIMESTAMPTZ</code>, интервал дат &mdash; <code>DATE</code> или <code>daterange</code></li>
<li>✅ Не менее 6 именованных ограничений <code>CHECK</code></li>
<li>✅ Как минимум один частичный или составной unique-индекс</li>
<li>✅ Индексы на все колонки FK</li>
<li>✅ Механизм, блокирующий пересечение дат (обоснуйте свой выбор)</li>
<li>✅ Тестовые данные: 10+ пользователей, 8+ объектов, 25+ броней (минимум 3 отменённые), 20+ платежей, 10+ отзывов</li>
<li>✅ Не менее 8 отчётов (список ниже)</li>
<li>✅ Схема в виде mermaid <code>erDiagram</code></li>
<li>✅ Файл <code>DIZAYN.md</code>: письменные ответы на 4 сложных вопроса выше</li>
</ul>

<h3>Требуемые отчёты</h3>
<ol>
<li>Свободные объекты в заданном интервале дат</li>
<li>Процент загрузки каждого объекта (за последние 90 дней)</li>
<li>Рейтинг владельцев по доходу</li>
<li>ТОП-5 объектов с наивысшей средней оценкой (среди имеющих не менее 3 отзывов)</li>
<li>Частично оплаченные или вовсе неоплаченные брони</li>
<li>Доля отмен (cancellation rate) &mdash; по гостям</li>
<li>Какие удобства сопутствуют высокой оценке (N:N + агрегат)</li>
<li>Помесячный тренд дохода и процент роста (оконная функция, <code>LAG</code>)</li>
</ol>

<h3>Бонус (по желанию)</h3>
<ul>
<li>🎯 Блокировка пересечения дат на уровне базы через <code>EXCLUDE USING gist</code></li>
<li>📈 <code>MATERIALIZED VIEW</code> для дашборда загрузки</li>
<li>🔁 Триггер, проверяющий право на написание отзыва</li>
<li>💸 Политика отмены: сколько возвращается (в зависимости от разницы дат)</li>
<li>🔍 Измерить два самых тяжёлых отчёта через <code>EXPLAIN ANALYZE</code> и ускорить их индексами</li>
</ul>

<h3>📌 Заключительное слово</h3>
<p>В начале курса вы смотрели на схему с вопросом «как это работает». Теперь вы смотрите на неё с вопросом «почему именно так» &mdash; и разница между этими двумя взглядами и есть разница между разработчиком и проектировщиком баз данных.</p>
<p>Запомните: хорошая схема <em>не даёт возможности сохранить</em> неверные данные. Каждый раз, когда возникает мысль «проверим это в приложении», спросите себя: а сработает ли эта проверка, если завтра в базу напишет другой сервис, другой скрипт или я сам в полночь через <code>psql</code>? Если ответ «нет» &mdash; эта проверка должна жить в базе данных.</p>
""",
    "code": """\
-- ═══════════════════════════════════════════════════════════════════════
-- 🚀 CAPSTONE: система бронирования — СТАРТОВЫЙ НАБОР
--
-- Ниже дан ТОЛЬКО фундамент схемы. Остальное вы строите сами.
-- Каждое решение сопровождайте обоснованием в комментарии --.
-- ═══════════════════════════════════════════════════════════════════════

-- Нужно для ограничения на интервалы дат (бонусное задание)
CREATE EXTENSION IF NOT EXISTS btree_gist;

DROP TABLE IF EXISTS sharhlar;
DROP TABLE IF EXISTS tolovlar;
DROP TABLE IF EXISTS bronlar;
DROP TABLE IF EXISTS obyekt_qulayliklari;
DROP TABLE IF EXISTS qulayliklar;
DROP TABLE IF EXISTS obyektlar;
DROP TABLE IF EXISTS profillar;
DROP TABLE IF EXISTS foydalanuvchilar;

-- ── Пользователь: может быть и гостем, и владельцем жилья ─────────────
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

-- ── 1:1 — необязательный профиль ──────────────────────────────────────
CREATE TABLE profillar (
    foydalanuvchi_id INTEGER PRIMARY KEY
                     REFERENCES foydalanuvchilar(id) ON DELETE CASCADE,
    bio              VARCHAR(500),
    avatar_url       VARCHAR(255),
    tasdiqlangan     BOOLEAN NOT NULL DEFAULT FALSE
);

-- ── 1:N — объект и его владелец ───────────────────────────────────────
CREATE TABLE obyektlar (
    id            INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- RESTRICT: пользователя, у которого есть объекты, удалить нельзя,
    -- иначе исчезла бы история броней и платежей
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

-- ── N:N — объект и удобства ───────────────────────────────────────────
CREATE TABLE qulayliklar (
    id   INTEGER     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nomi VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE obyekt_qulayliklari (
    obyekt_id   INTEGER NOT NULL REFERENCES obyektlar(id)   ON DELETE CASCADE,
    qulaylik_id INTEGER NOT NULL REFERENCES qulayliklar(id) ON DELETE RESTRICT,
    PRIMARY KEY (obyekt_id, qulaylik_id)
);

-- ── Брони: в этой таблице встречаются все понятия курса ───────────────
CREATE TABLE bronlar (
    id             INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    obyekt_id      INTEGER       NOT NULL REFERENCES obyektlar(id) ON DELETE RESTRICT,
    mehmon_id      INTEGER       NOT NULL
                   REFERENCES foydalanuvchilar(id) ON DELETE RESTRICT,
    kirish_sanasi  DATE          NOT NULL,
    chiqish_sanasi DATE          NOT NULL,
    mehmonlar_soni SMALLINT      NOT NULL DEFAULT 1 CHECK (mehmonlar_soni > 0),
    -- ИСТОРИЧЕСКАЯ цена: копия суточной цены на момент бронирования.
    -- Даже если цена объекта потом изменится, сумма брони не изменится.
    kunlik_narx    NUMERIC(14,2) NOT NULL CHECK (kunlik_narx > 0),
    holat          VARCHAR(15)   NOT NULL DEFAULT 'kutmoqda'
                   CHECK (holat IN ('kutmoqda','tasdiqlangan','yashab_chiqdi','bekor')),
    yaratilgan     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT bronlar_sana_tartibi CHECK (chiqish_sanasi > kirish_sanasi),
    -- ⚠️ ГЛАВНОЕ СЛОЖНОЕ РЕШЕНИЕ: блокировка пересечения дат.
    -- Обычный UNIQUE здесь не работает — проблема не в равенстве,
    -- а в ПЕРЕСЕЧЕНИИ интервалов. Это решает EXCLUDE USING gist.
    -- Условие WHERE: отменённые брони даты не занимают.
    CONSTRAINT bronlar_kesishmasin EXCLUDE USING gist (
        obyekt_id WITH =,
        daterange(kirish_sanasi, chiqish_sanasi, '[)') WITH &&
    ) WHERE (holat <> 'bekor')
);

-- ── 1:N — платежи (возможны частичная оплата и возврат) ───────────────
CREATE TABLE tolovlar (
    id          INTEGER       GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bron_id     INTEGER       NOT NULL REFERENCES bronlar(id) ON DELETE RESTRICT,
    summa       NUMERIC(14,2) NOT NULL CHECK (summa <> 0),  -- отрицательное = возврат
    usul        VARCHAR(20)   NOT NULL CHECK (usul IN ('karta','click','payme','naqd')),
    vaqti       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ── 1:1 — на каждую бронь не более одного отзыва ──────────────────────
CREATE TABLE sharhlar (
    -- bron_id как PK = связь 1:1 и гарантия «отзыв только при наличии брони»
    bron_id    INTEGER  PRIMARY KEY REFERENCES bronlar(id) ON DELETE CASCADE,
    baho       SMALLINT NOT NULL CHECK (baho BETWEEN 1 AND 5),
    matn       VARCHAR(1000),
    yaratilgan TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Индексы ───────────────────────────────────────────────────────────
CREATE INDEX obyektlar_egasi_idx      ON obyektlar (egasi_id);
CREATE INDEX obyektlar_shahar_idx     ON obyektlar (shahar) WHERE faol;
CREATE INDEX bronlar_obyekt_sana_idx  ON bronlar (obyekt_id, kirish_sanasi);
CREATE INDEX bronlar_mehmon_idx       ON bronlar (mehmon_id);
CREATE INDEX tolovlar_bron_idx        ON tolovlar (bron_id);
CREATE INDEX oq_qulaylik_idx          ON obyekt_qulayliklari (qulaylik_id);

-- ── Минимальные тестовые данные (вы их расширите) ─────────────────────
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

-- Пересекающаяся бронь БЛОКИРУЕТСЯ — работает ограничение EXCLUDE:
-- INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
--                      kunlik_narx) VALUES (1, 3, '2026-08-03', '2026-08-07', 450000);
-- ERROR:  conflicting key value violates exclusion constraint "bronlar_kesishmasin"

-- Отменённая бронь даты НЕ ЗАНИМАЕТ (благодаря условию WHERE):
INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
                     kunlik_narx, holat)
VALUES (1, 3, DATE '2026-09-01', DATE '2026-09-05', 450000, 'bekor');
INSERT INTO bronlar (obyekt_id, mehmon_id, kirish_sanasi, chiqish_sanasi,
                     kunlik_narx, holat)
VALUES (1, 2, DATE '2026-09-01', DATE '2026-09-05', 450000, 'tasdiqlangan');

INSERT INTO tolovlar (bron_id, summa, usul) VALUES
    (1, 1800000, 'click'),
    (2,  900000, 'karta'),   -- частичная оплата (из 1 800 000)
    (3, 4000000, 'payme');

INSERT INTO sharhlar (bron_id, baho, matn) VALUES
    (1, 5, 'Ajoyib joy, hamma narsa tasvirdagidek edi.');

-- ── Образец отчёта: загрузка и доход ──────────────────────────────────
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

-- ── Образец отчёта: не полностью оплаченные брони ─────────────────────
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

-- ── ДАЛЬШЕ ПРОДОЛЖАЕТЕ ВЫ ─────────────────────────────────────────────
-- 1. Таблица narx_kalendari (сезонные цены) — нужна ли? Обоснуйте.
-- 2. Триггер, проверяющий право на отзыв (отзыв разрешён, только если
--    бронь в статусе 'yashab_chiqdi').
-- 3. Политика отмены: сколько возвращается?
-- 4. Остальные 6 отчётов.
-- 5. mermaid erDiagram и DIZAYN.md — ответы на 4 сложных вопроса.
""",
    "task_title": "🚀 CAPSTONE: Схема системы бронирования",
    "task_description": (
        "Финальный проект курса: спроектируйте с нуля полную схему базы данных "
        "для системы бронирования типа Booking.com / Airbnb. Готовой схемы вам не "
        "дают — вы строите её сами и письменно обосновываете каждое проектное "
        "решение. Результат: запускаемый .sql файл, mermaid erDiagram и документ DIZAYN.md."
    ),
    "task_requirements": (
        "• Не менее 8 таблиц: foydalanuvchilar, profillar, obyektlar, qulayliklar, "
        "obyekt_qulayliklari, bronlar, tolovlar, sharhlar\n"
        "• Должны быть задействованы все три типа связей: 1:1, 1:N и N:N\n"
        "• Как минимум одна self-referential связь (например: ответ на отзыв или "
        "иерархия объектов)\n"
        "• Все таблицы в 3NF; если делаете исключение — напишите причину в комментарии\n"
        "• Деньги — NUMERIC(14,2), время — TIMESTAMPTZ, даты — DATE/daterange\n"
        "• Не менее 6 ИМЕНОВАННЫХ ограничений CHECK\n"
        "• Как минимум один частичный или составной unique-индекс\n"
        "• Для каждого FK выбрана стратегия ON DELETE и ОБОСНОВАНА в комментарии --\n"
        "• Индексы на все колонки FK\n"
        "• Механизм, гарантирующий, что один объект не будет забронирован двумя "
        "людьми одновременно (рекомендуется EXCLUDE USING gist), и обоснование выбора\n"
        "• Цена брони должна храниться как историческая копия (чтобы при изменении "
        "цены сумма старой брони не менялась)\n"
        "• Тестовые данные: 10+ пользователей, 8+ объектов, 25+ броней (минимум 3 отменённые), "
        "20+ платежей, 10+ отзывов\n"
        "• 8 отчётов: свободные объекты в интервале дат; процент загрузки (90 дней); "
        "рейтинг владельцев по доходу; ТОП-5 объектов по средней оценке (с 3+ отзывами); "
        "частично/неоплаченные брони; доля отмен по гостям; связь удобств и оценки "
        "(N:N + агрегат); помесячный тренд дохода (LAG)\n"
        "• В DIZAYN.md — письменные ответы на 4 сложных вопроса:\n"
        "   1) Как вы блокируете пересечение дат и почему выбрали именно этот способ?\n"
        "   2) Где хранится цена — в объекте, в календаре цен или в брони? Почему?\n"
        "   3) Как вы ограничите право писать отзыв (только реально проживавший гость)?\n"
        "   4) Отменённая бронь удаляется через DELETE или помечается статусом? "
        "Что происходит, если оплата уже прошла?\n"
        "• Бонус: дашборд загрузки через MATERIALIZED VIEW; триггер проверки права "
        "на отзыв; оптимизация 2 самых тяжёлых отчётов через EXPLAIN ANALYZE"
    ),
    "task_technologies": (
        "PostgreSQL, полное проектирование схемы, нормализация (1NF/2NF/3NF/BCNF), "
        "1:1 / 1:N / N:N, junction-таблица, self-referential FK, составной и частичный "
        "unique-индекс, CHECK, EXCLUDE USING gist, daterange, btree_gist, TRIGGER, "
        "MATERIALIZED VIEW, рекурсивный CTE, оконные функции, EXPLAIN ANALYZE, mermaid erDiagram"
    ),
    "exercises": {
        4780: {
            "title": "Блокировка пересечения дат",
            "description": "Какой механизм уровня базы данных наиболее надёжен в PostgreSQL, чтобы один объект не был забронирован двумя людьми одновременно?",
            "hint": "Проблема не в точном равенстве, а в пересечении интервалов.",
            "explanation": "UNIQUE блокирует только одинаковые значения, но не пересекающиеся интервалы (1-5 и 3-8 августа пересекаются, хотя значения разные). CHECK же работает лишь внутри одной строки. EXCLUDE USING gist в связке с оператором && для daterange создан именно для этой задачи и надёжно работает даже при параллельных транзакциях.",
        },
        4781: {
            "title": "Как хранится цена брони?",
            "description": "Суточная цена объекта со временем меняется. Если после бронирования цена вырастет, сумма старой брони меняться не должна. Что для этого должно быть в таблице броней и почему? Ответьте в 2-3 предложениях.",
            "hint": "Тот же принцип, что и с narx_birlik и адресом доставки.",
            "expected_answer": "В таблице bronlar должна быть колонка kunlik_narx — копия цены на момент бронирования. Она не связывается с obyektlar.narx ни внешним ключом, ни через JOIN, потому что это исторический факт: даже при изменении цены сумма брони меняться не должна. Это та же логика, что и у buyurtma_elementlari.narx_birlik.",
        },
    },
}


LESSONS = [L1, L2, L3, L4, L5, R1, L6, L7, L8, L9, R2, L10, C1]

# Lesson columns the read path (app/api/v1/endpoints/lessons.py) translates:
# title, chapter, text_content, task_title, task_description,
# task_requirements, task_technologies, sections_json. `chapter` is NULL for
# every lesson in this course, so it is not listed here.
TASK_FIELDS = (
    "task_title", "task_description", "task_requirements", "task_technologies",
)

# Exercise columns we translate. `options` / `drag_items` are intentionally
# excluded: sections_json never translates them (_NEVER_TRANSLATE_KEYS) and
# drag_and_drop grading compares submitted items against the Uzbek
# `correct_order`, so translating them would break grading.
EX_FIELDS = ("title", "description", "hint", "explanation", "expected_answer")

# Section labels build_sections_json() writes — already Russian.
LABELS = {"Текст": "Текст", "Код": "Код", "Упражнения": "Упражнения"}


async def _run() -> None:
    async with AsyncSessionLocal() as db:
        total_lessons = total_ex = total_strings = 0

        for spec in LESSONS:
            lesson_id = spec["lesson_id"]
            lesson = (
                await db.execute(select(Lesson).where(Lesson.id == lesson_id))
            ).scalar_one()
            ex_rows = (
                await db.execute(select(Exercise).where(Exercise.lesson_id == lesson_id))
            ).scalars().all()

            # ── every string _collect_translatable_strings() will find ──
            section_map = dict(LABELS)
            section_map[lesson.text_content] = spec["text"]
            section_map[lesson.code_content] = spec["code"]
            if lesson.task_title:
                section_map[lesson.task_title] = spec["task_title"]
            if lesson.task_description:
                section_map[lesson.task_description] = spec["task_description"]

            ex_translations: dict[int, dict[str, str]] = {}
            for ex in ex_rows:
                if ex.id not in spec["exercises"]:
                    raise ValueError(
                        f"lesson {lesson_id}: no RU translation for exercise {ex.id} "
                        f"({ex.title!r})"
                    )
                fields = spec["exercises"][ex.id]
                row: dict[str, str] = {}
                for field_name in EX_FIELDS:
                    source = getattr(ex, field_name)
                    if not source or not source.strip():
                        continue
                    if field_name not in fields:
                        raise ValueError(
                            f"exercise {ex.id}: field {field_name!r} has source text "
                            f"but no RU translation"
                        )
                    row[field_name] = fields[field_name]
                    section_map[source] = fields[field_name]
                ex_translations[ex.id] = row

            # NOTE: the spec dicts key the lesson body as "text", while the
            # Lesson column is "text_content" — map it explicitly.
            flat_fields = {"title": spec["title"], "text_content": spec["text"]}
            for name in TASK_FIELDS:
                if getattr(lesson, name, None):
                    if not spec.get(name):
                        raise ValueError(
                            f"lesson {lesson_id}: column {name!r} has source text "
                            f"but no RU translation"
                        )
                    flat_fields[name] = spec[name]

            await translate_lesson(
                db, lesson_id,
                flat_fields=flat_fields,
                section_translations=section_map,
            )
            await translate_exercises(db, ex_translations)

            total_lessons += 1
            total_ex += len(ex_translations)
            total_strings += len(section_map)
            print(f"  lesson {lesson_id}  {spec['title'][:52]:<52}  "
                  f"flat={len(flat_fields)}  exercises={len(ex_translations)}  "
                  f"section strings={len(section_map)}")

        await db.commit()
        print(f"\nTranslated {total_lessons} lessons, {total_ex} exercises, "
              f"{total_strings} section strings (committed).")


if __name__ == "__main__":
    asyncio.run(_run())
