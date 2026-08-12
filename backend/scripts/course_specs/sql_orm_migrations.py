"""Course 4 (final) of the SQL track: SQL + Python ORM va Migratsiyalar.

Bridges raw SQL (courses 41/98/107) to how real applications talk to a
database: SQLAlchemy 2.x async ORM (the same library this very platform's
backend uses — app/models/*.py, app/services/*.py are live reference
material) plus Alembic migrations. prerequisite_course_id=107.

Built with the course_builder scaffold (see course_builder/__init__.py for
the spec contract). Two gaps found in course 107 after the fact and fixed
here from the start:
  1. text_content density must match courses 41/98 (~4200-6700 chars/lesson),
     not course 107's ~3988 average.
  2. EVERY lesson gets both task + sample, not just review/capstone lessons.

is_published stays False — a human reviews before publishing.
"""

COURSE = {
    "title": "SQL + Python ORM va Migratsiyalar",
    "description": (
        "SQL trekining yakuniy kursi: xom SQL so'rovlardan ilova qatlamiga — "
        "Python + SQLAlchemy 2.x (async) ORM orqali ma'lumotlar bazasi bilan "
        "qanday ishlash, jadval-obyekt nomuvofiqligini (impedance mismatch) "
        "qanday yechish, munosabatlarni modellashtirish, N+1 muammosini ORM "
        "darajasida oldini olish, tranzaksiya va sessiyalarni boshqarish, "
        "hamda Alembic bilan production sxemasini xavfsiz o'zgartirish "
        "(migratsiyalar, backfill, zero-downtime, rollback). Namunalar aynan "
        "shu platformaning o'z backendida ishlatiladigan kod uslubiga "
        "asoslangan."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 5,
    "max_points": 230,
    "category_id": 10,
    "prerequisite_course_id": 107,
    "display_order": 503,
    "image_url": "https://www.sqlalchemy.org/img/sqla_logo.png",
    "thumbnail_url": "https://icon.icepanel.io/Technology/svg/SQLAlchemy.svg",
    "is_active": True,
    "is_published": False,
}

# ---------------------------------------------------------------------------
# Lesson 0 — ORM nima va impedance mismatch muammosi
# ---------------------------------------------------------------------------

L0_TEXT = """
<h3>Ilova va ma'lumotlar bazasi orasidagi devor</h3>
<p>Oldingi uchta kursda (41, 98, 107) siz SQL so'rovlarini to'g'ridan-to'g'ri
psql konsolida yoki DBeaver kabi vositada yozdingiz. Ammo haqiqiy backend
serverida hech kim har bir amal uchun qo'lda SQL matnini terib o'tirmaydi —
buning o'rniga <strong>ORM</strong> (Object-Relational Mapper — obyekt-relyatsion
xaritalovchi) degan qatlam ishlatiladi. Bu kurs xuddi shu platformaning o'zi
ishlatadigan yondashuvni ko'rsatadi: backend/app/models/ papkasidagi har bir
fayl — Course, Lesson, Exercise, Student — SQLAlchemy 2.x'ning deklarativ ORM
klasslari sifatida yozilgan, va backend/alembic/versions/ papkasida 60 dan
ortiq haqiqiy migratsiya fayli mavjud. Bu — o'ylab topilgan misol emas, siz
hozir foydalanayotgan platformaning bevosita ishlaydigan kodi.</p>

<h3>"Impedance mismatch" nima?</h3>
<p>Relyatsion baza <em>qatorlar va jadvallar</em> bilan fikrlaydi, Python esa
<em>klasslar va obyektlar</em> bilan. Ikkalasi orasidagi tabiiy nomuvofiqlik
"object-relational impedance mismatch" deb ataladi va bir nechta aniq
joyda namoyon bo'ladi:</p>
<ul>
<li><strong>Identity</strong> — baza qatorni PRIMARY KEY orqali aniqlaydi, Python
obyekti esa xotiradagi manzil (identity) orqali. Ikkitasi bir xil qatorni
ifodalaganida ular <em>bir xil obyekt</em> bo'lishi kerakmi? (Javob: ha, va
buni Session'ning "identity map"i hal qiladi — 6-darsda ko'ramiz.)</li>
<li><strong>Munosabatlar</strong> — baza FOREIGN KEY ustuni orqali bog'laydi
(lessons.course_id), Python esa <code>lesson.course</code> kabi ichma-ich
atribut orqali obyektlarni bog'laydi — bular ikki xil mental model.</li>
<li><strong>Granularity</strong> — bitta mantiqiy obyekt bir nechta jadvaldan
yig'ilishi mumkin (masalan, Student + StudentDegree + StudentAchievement).</li>
<li><strong>Turlar</strong> — Python'dagi <code>datetime</code>, <code>Enum</code>,
<code>list</code> kabi turlar bazada boshqacha (TIMESTAMP, VARCHAR, JSON)
saqlanadi va ikki tomonlama aylantirish kerak.</li>
</ul>

<h3>Nega hamma narsani qo'lda SQL bilan yozmaymiz?</h3>
<p>Xom SQL string konkatensiyasi orqali yozish bir nechta real muammoni
keltirib chiqaradi: SQL-in'ektsiya xavfi (parametrlashtirilmagan qiymatlar),
har bir so'rov natijasini qo'lda dict/obyektga aylantirish zarurati, refaktoring
paytida "bu ustun qayerlarda ishlatilgan" degan savolga javob topishning
qiyinligi (oddiy matn qidiruvi, IDE yordamisiz), va bazalar orasida ko'chganda
(masalan test uchun SQLite, production uchun PostgreSQL) sintaksis farqlarini
qo'lda tuzatish zarurati. ORM bularning barchasini bitta qatlamda hal qiladi —
lekin SQL'ni "yashirmaydi": yaxshi ORM foydalanuvchisi hosil bo'lgan so'rovni
har doim ko'ra olishi va tushunishi kerak (<code>echo=True</code> yoki
<code>str(statement)</code> orqali).</p>

<h3>Ikki asosiy ORM naqshi: Active Record va Data Mapper</h3>
<p><strong>Active Record</strong> (Django ORM, Ruby on Rails) — obyektning o'zida
<code>save()</code>/<code>delete()</code> metodlari bo'ladi, obyekt o'zini qanday
saqlashni biladi. <strong>Data Mapper</strong> (SQLAlchemy) — obyekt sof Python
klassi, saqlash mantig'i undan butunlay ajratilgan <code>Session</code> orqali
boshqariladi. Bu kursda SQLAlchemy'ni tanlaymiz, chunki (1) bu platformaning
backendi aynan shundan foydalanadi, (2) Data Mapper yondashuvi domain
obyektlarini bazadan mustaqil qilib, testlashni osonlashtiradi, (3)
SQLAlchemy Core so'rov qurish tilini ham, to'liq ORM'ni ham bitta kutubxonada
beradi — 107-kursda o'rgangan murakkab JOIN va window function'laringizni
Python kodida qayta yozishga imkon beradi.</p>

<h3>Keng tarqalgan noto'g'ri tushunchalar</h3>
<ul>
<li>"ORM sekin" — noto'g'ri umumlashtirish; sekinlik ORM'ning o'zida emas, uni
noto'g'ri ishlatishda (N+1 so'rovlar, ortiqcha yuklash — 5 va 11-darslarda
ko'ramiz).</li>
<li>"ORM = faqat oddiy CRUD" — SQLAlchemy Core murakkab join, subquery,
CTE va window function'larni ham to'liq qo'llab-quvvatlaydi.</li>
<li>"ORM ishlatsam SQL bilmasam ham bo'ladi" — aksincha, ORM samarali
ishlatish uchun SQL asoslarini (41-98-107 kurslarida o'rganganlaringizni)
tushunish shart, chunki ORM oxir-oqibat SQL generatsiya qiladi.</li>
</ul>

<h3>Impedance mismatch amalda qanday ko'rinadi</h3>
<p>Aytaylik, sizga "talabaning barcha yakunlagan kurslari, har birining o'rtacha
bahosi bilan" degan hisobot kerak. SQL darajasida bu — JOIN, GROUP BY va AVG()
bilan bitta so'rov. Python darajasida esa bu — Student obyekti, uning ichida
ro'yxat (list) ko'rinishidagi Course obyektlari, har birining ichida yana
Grade obyektlari yig'indisi. Ikkala tasvir ham "to'g'ri", lekin ular orasidagi
xaritalashni kimdir amalga oshirishi kerak — aynan shu ishni ORM avtomatik
bajaradi, siz esa faqat munosabatlarni (<code>relationship()</code>) bir marta
e'lon qilasiz.</p>

<h3>Kurs davomida qanday kodlash uslubi ishlatiladi</h3>
<p>Har bir darsda kod namunasi ushbu platformaning haqiqiy uslubiga mos
yoziladi: <code>async def</code> funksiyalar, <code>await db.execute(select(...))</code>
so'rov shakli, <code>Mapped[...]</code> annotatsiyali ustunlar. Bu tasodifiy
tanlov emas — bu xuddi backend/app/ papkasidagi ishlab chiqarish kodining
o'zi. Kursni tugatgach, siz shu platformaning o'z modellarini (Course, Lesson,
Exercise) ochib, ularni allaqachon tanish uslub sifatida o'qiy olishingiz
kerak.</p>
""".strip()

L0_TEXT_RU = """
<h3>Стена между приложением и базой данных</h3>
<p>В предыдущих трёх курсах (41, 98, 107) вы писали SQL-запросы напрямую в
консоли psql или в инструменте вроде DBeaver. Но в реальном backend-сервере
никто не набирает вручную SQL-текст для каждой операции — вместо этого
используется слой <strong>ORM</strong> (Object-Relational Mapper —
объектно-реляционный преобразователь). Этот курс показывает именно тот
подход, который использует сама эта платформа: каждый файл в
backend/app/models/ — Course, Lesson, Exercise, Student — написан как
декларативный ORM-класс SQLAlchemy 2.x, а в папке backend/alembic/versions/
находится более 60 реальных файлов миграций. Это не выдуманный пример, а
непосредственно работающий код платформы, которой вы сейчас пользуетесь.</p>

<h3>Что такое "impedance mismatch"?</h3>
<p>Реляционная база мыслит <em>строками и таблицами</em>, а Python — <em>классами
и объектами</em>. Естественное несоответствие между ними называется
"object-relational impedance mismatch" и проявляется в нескольких конкретных
местах:</p>
<ul>
<li><strong>Идентичность</strong> — база определяет строку через PRIMARY KEY, а
объект Python — через адрес в памяти (identity). Должны ли они считаться
<em>одним и тем же объектом</em>, если представляют одну строку? (Ответ: да,
и это решает "identity map" объекта Session — увидим в уроке 6.)</li>
<li><strong>Связи</strong> — база связывает через колонку FOREIGN KEY
(lessons.course_id), а Python связывает объекты через вложенный атрибут
вроде <code>lesson.course</code> — это две разные ментальные модели.</li>
<li><strong>Гранулярность</strong> — один логический объект может собираться
из нескольких таблиц (например, Student + StudentDegree + StudentAchievement).</li>
<li><strong>Типы</strong> — типы Python вроде <code>datetime</code>, <code>Enum</code>,
<code>list</code> хранятся в базе иначе (TIMESTAMP, VARCHAR, JSON), и
требуется преобразование в обе стороны.</li>
</ul>

<h3>Почему не писать всё вручную на SQL?</h3>
<p>Написание через конкатенацию SQL-строк порождает несколько реальных
проблем: риск SQL-инъекции (непараметризованные значения), необходимость
вручную превращать результат каждого запроса в dict/объект, сложность
ответить на вопрос "где ещё используется эта колонка" при рефакторинге
(обычный текстовый поиск без помощи IDE), и необходимость вручную устранять
синтаксические различия при переходе между базами (например, SQLite для
тестов, PostgreSQL для production). ORM решает всё это в одном слое — но не
"прячет" SQL: хороший пользователь ORM всегда должен уметь увидеть и понять
получившийся запрос (через <code>echo=True</code> или <code>str(statement)</code>).</p>

<h3>Два основных паттерна ORM: Active Record и Data Mapper</h3>
<p><strong>Active Record</strong> (Django ORM, Ruby on Rails) — сам объект имеет
методы <code>save()</code>/<code>delete()</code>, объект знает, как себя
сохранять. <strong>Data Mapper</strong> (SQLAlchemy) — объект это чистый класс
Python, логика сохранения полностью отделена и управляется через
<code>Session</code>. В этом курсе мы выбираем SQLAlchemy, потому что (1)
именно её использует backend этой платформы, (2) подход Data Mapper делает
доменные объекты независимыми от базы, упрощая тестирование, (3) SQLAlchemy
Core даёт и язык построения запросов, и полноценный ORM в одной библиотеке —
позволяя переписать на Python сложные JOIN и оконные функции, изученные в
курсе 107.</p>

<h3>Распространённые заблуждения</h3>
<ul>
<li>"ORM медленный" — неверное обобщение; медленность не в самом ORM, а в
его неправильном использовании (N+1 запросы, избыточная загрузка — увидим
в уроках 5 и 11).</li>
<li>"ORM = только простой CRUD" — SQLAlchemy Core полностью поддерживает
сложные join, подзапросы, CTE и оконные функции.</li>
<li>"Используя ORM, можно не знать SQL" — наоборот, для эффективного
использования ORM необходимо понимать основы SQL (изученные в курсах
41-98-107), поскольку ORM в итоге генерирует именно SQL.</li>
</ul>

<h3>Как impedance mismatch выглядит на практике</h3>
<p>Допустим, вам нужен отчёт "все завершённые курсы студента со средней
оценкой по каждому". На уровне SQL это один запрос с JOIN, GROUP BY и
AVG(). На уровне Python это — объект Student, внутри которого список
объектов Course, а внутри каждого — сумма объектов Grade. Оба представления
"верны", но кто-то должен реализовать преобразование между ними — именно эту
работу ORM выполняет автоматически, а вы лишь один раз объявляете связи
(<code>relationship()</code>).</p>

<h3>Какой стиль кода используется в течение курса</h3>
<p>В каждом уроке пример кода написан в том же реальном стиле, что и эта
платформа: функции <code>async def</code>, форма запроса <code>await
db.execute(select(...))</code>, колонки с аннотацией <code>Mapped[...]</code>.
Это не случайный выбор — это стиль самого production-кода в папке
backend/app/. Завершив курс, вы сможете открыть собственные модели этой
платформы (Course, Lesson, Exercise) и читать их уже как знакомый стиль.</p>
""".strip()

L0_CODE = """
-- ============================================================
-- 1) Xom SQL yondashuvi (107-kursda ko'rgan uslub)
-- ============================================================
SELECT l.id, l.title, l."order", c.title AS course_title
FROM lessons l
JOIN courses c ON c.id = l.course_id
WHERE l.course_id = 41
ORDER BY l."order";

-- Python tomonida natijani QO'LDA obyektga aylantirish kerak bo'ladi:
-- rows = await conn.execute(text(raw_sql))
-- lessons = []
-- for row in rows:
--     lessons.append({"id": row.id, "title": row.title, "course_title": row.course_title})
-- Bu ishlaydi, lekin har bir so'rov uchun shu aylantirish qayta-qayta yoziladi.

-- ============================================================
-- 2) Xuddi shu narsa — SQLAlchemy 2.x deklarativ ORM bilan
-- ============================================================
from __future__ import annotations
from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # Ushbu platformaning app/db/base_class.py'dagi Base'iga o'xshash —
    # barcha modellar shundan meros oladi.
    pass


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))

    # Munosabat: bitta kursning ko'p darsi bor (one-to-many).
    # Bu Python atributi, jadvalda ustun EMAS — 3-darsda batafsil ko'ramiz.
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    order: Mapped[int] = mapped_column(Integer, default=0)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))

    course: Mapped["Course"] = relationship(back_populates="lessons")


# ============================================================
# 3) So'rov — endi SQL matni emas, Python obyekti qaytadi
# ============================================================
from sqlalchemy import select

stmt = select(Lesson).where(Lesson.course_id == 41).order_by(Lesson.order)
result = await db.execute(stmt)
lessons = result.scalars().all()

for lesson in lessons:
    # .course — bu FOREIGN KEY emas, munosabat orqali AVTOMATIK yuklangan obyekt
    print(lesson.title, "|", lesson.course.title)

# Hosil bo'lgan haqiqiy SQL'ni har doim ko'rish mumkin — ORM hech narsani
# yashirmaydi, faqat qo'lda yozishdan qutqaradi:
print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
# -> SELECT lessons.id, lessons.title, lessons."order", lessons.course_id
#    FROM lessons WHERE lessons.course_id = 41 ORDER BY lessons."order"

# ============================================================
# 4) Identity map — impedance mismatch'ning "identity" muammosini
#    Session qanday yechadi (6-darsda chuqurroq)
# ============================================================
lesson_a = (await db.execute(select(Lesson).where(Lesson.id == 1))).scalar_one()
lesson_b = (await db.execute(select(Lesson).where(Lesson.id == 1))).scalar_one()
assert lesson_a is lesson_b  # bir xil Session ichida — bir xil Python obyekti!
# Bu shunchaki tasodif emas: Session har bir qatorni faqat bir marta
# xotiraga yuklaydi va keyingi so'rovlarda xuddi shu obyektni qaytaradi.

# ============================================================
# 5) "Talabaning yakunlagan kurslari + o'rtacha bahosi" — impedance
#    mismatch'ning aynan matnda tasvirlangan misoli, ikki usulda
# ============================================================

# --- Xom SQL: bitta JOIN + GROUP BY, natija tekis jadval ---
REPORT_SQL = '''
SELECT c.title, AVG(g.score) AS avg_score
FROM courses c
JOIN student_courses sc ON sc.course_id = c.id
JOIN grades g ON g.course_id = c.id AND g.student_id = sc.student_id
WHERE sc.student_id = :student_id
GROUP BY c.title;
'''

# --- ORM: xuddi shu ma'lumot, lekin natija ichma-ich obyektlar sifatida ---
from sqlalchemy import func

stmt = (
    select(Course.title, func.avg(Grade.score).label("avg_score"))
    .join(student_courses, student_courses.c.course_id == Course.id)
    .join(Grade, (Grade.course_id == Course.id) & (Grade.student_id == student_courses.c.student_id))
    .where(student_courses.c.student_id == 7)
    .group_by(Course.title)
)
# rows = (await db.execute(stmt)).all()
# for title, avg_score in rows:
#     print(f"{title}: {avg_score:.1f}")
# Diqqat: bu yerda ham natija hali ham "tekis" qator — chunki aggregatsiya
# qilingan so'rov ORM'da ham Core kabi Row qaytaradi, to'liq obyekt daraxti
# emas. To'liq ichma-ich obyekt daraxti kerak bo'lsa, relationship() orqali
# navigatsiya qilinadi (3-4-darslarda).

# ============================================================
# 6) Identity amalda — aynan shu platformaning identity map misoli
# ============================================================
# app/services/lesson_service.py bitta HTTP so'rov davomida ikki marta
# chaqiriladi (masalan logging middleware + endpoint'ning o'zi):
first_call = await get_lesson_by_id(db, lesson_id=5)
second_call = await get_lesson_by_id(db, lesson_id=5)
assert first_call is second_call
# Ikkalasi ham AYNAN BIR XIL Python obyektini qaytaradi — Session ikkinchi
# marta yangi Lesson(5) yaratmaydi, uni identity map'dan oladi. Aynan shu
# mexanizm ORM darsning boshida tasvirlangan impedance mismatch'ning
# "identity muammosi"ni bitta ham qo'shimcha kod qatorisiz yechadi.
""".strip()

L0_CODE_RU = """
-- ============================================================
-- 1) Подход с чистым SQL (стиль курса 107)
-- ============================================================
SELECT l.id, l.title, l."order", c.title AS course_title
FROM lessons l
JOIN courses c ON c.id = l.course_id
WHERE l.course_id = 41
ORDER BY l."order";

-- На стороне Python результат приходится ВРУЧНУЮ превращать в объект:
-- rows = await conn.execute(text(raw_sql))
-- lessons = []
-- for row in rows:
--     lessons.append({"id": row.id, "title": row.title, "course_title": row.course_title})
-- Это работает, но такое превращение пишется заново для каждого запроса.

-- ============================================================
-- 2) То же самое — через декларативный ORM SQLAlchemy 2.x
-- ============================================================
from __future__ import annotations
from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # Похож на Base из app/db/base_class.py этой платформы —
    # все модели наследуются от него.
    pass


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))

    # Связь: у одного курса много уроков (one-to-many).
    # Это атрибут Python, а НЕ колонка в таблице — подробно в уроке 3.
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    order: Mapped[int] = mapped_column(Integer, default=0)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))

    course: Mapped["Course"] = relationship(back_populates="lessons")


# ============================================================
# 3) Запрос — теперь возвращается не текст SQL, а объект Python
# ============================================================
from sqlalchemy import select

stmt = select(Lesson).where(Lesson.course_id == 41).order_by(Lesson.order)
result = await db.execute(stmt)
lessons = result.scalars().all()

for lesson in lessons:
    # .course — это не FOREIGN KEY, а объект, загруженный АВТОМАТИЧЕСКИ через связь
    print(lesson.title, "|", lesson.course.title)

# Получившийся реальный SQL всегда можно увидеть — ORM ничего не прячет,
# а лишь избавляет от ручного написания:
print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
# -> SELECT lessons.id, lessons.title, lessons."order", lessons.course_id
#    FROM lessons WHERE lessons.course_id = 41 ORDER BY lessons."order"

# ============================================================
# 4) Identity map — как Session решает проблему "идентичности"
#    из impedance mismatch (подробнее в уроке 6)
# ============================================================
lesson_a = (await db.execute(select(Lesson).where(Lesson.id == 1))).scalar_one()
lesson_b = (await db.execute(select(Lesson).where(Lesson.id == 1))).scalar_one()
assert lesson_a is lesson_b  # в рамках одной Session — один и тот же объект Python!
# Это не совпадение: Session загружает каждую строку в память только один
# раз и возвращает тот же объект при последующих запросах.

# ============================================================
# 5) "Завершённые курсы студента + средняя оценка" — тот самый пример
#    impedance mismatch из текста урока, двумя способами
# ============================================================

# --- Чистый SQL: один JOIN + GROUP BY, результат — плоская таблица ---
REPORT_SQL = '''
SELECT c.title, AVG(g.score) AS avg_score
FROM courses c
JOIN student_courses sc ON sc.course_id = c.id
JOIN grades g ON g.course_id = c.id AND g.student_id = sc.student_id
WHERE sc.student_id = :student_id
GROUP BY c.title;
'''

# --- ORM: те же данные, но результат как вложенные объекты ---
from sqlalchemy import func

stmt = (
    select(Course.title, func.avg(Grade.score).label("avg_score"))
    .join(student_courses, student_courses.c.course_id == Course.id)
    .join(Grade, (Grade.course_id == Course.id) & (Grade.student_id == student_courses.c.student_id))
    .where(student_courses.c.student_id == 7)
    .group_by(Course.title)
)
# rows = (await db.execute(stmt)).all()
# for title, avg_score in rows:
#     print(f"{title}: {avg_score:.1f}")
# Внимание: и здесь результат всё ещё "плоский" — потому что агрегирующий
# запрос в ORM тоже возвращает Row, как и в Core, а не полное дерево
# объектов. Если нужно именно дерево вложенных объектов — используется
# навигация через relationship() (уроки 3-4).

# ============================================================
# 6) Идентичность в действии — тот самый identity map этой платформы
# ============================================================
# app/services/lesson_service.py вызывается дважды за один HTTP-запрос
# (например middleware логирования + сам обработчик эндпоинта):
first_call = await get_lesson_by_id(db, lesson_id=5)
second_call = await get_lesson_by_id(db, lesson_id=5)
assert first_call is second_call
# Оба вызова возвращают ОДИН И ТОТ ЖЕ объект Python — Session не создаёт
# новый Lesson(5) во второй раз, а достаёт его из identity map. Именно
# этот механизм ORM решает "проблему идентичности" impedance mismatch,
# описанную в начале урока — без единой дополнительной строки кода.
""".strip()

L0_TASK = {
    "task_title": "Impedance mismatch'ni topib ko'rsating",
    "task_title_ru": "Найдите и покажите impedance mismatch",
    "task_description": (
        "Ushbu platformaning haqiqiy app/models/course.py va app/models/lesson.py "
        "fayllarini oching (yoki repo topilmasa, darsdagi Course/Lesson misolidan "
        "foydalaning). Har biriga mos keladigan CREATE TABLE SQL bayonotini qo'lda "
        "yozing, so'ngra qisqa hisobot tayyorlang: modelning qaysi qismi to'g'ridan-"
        "to'g'ri ustunga mos keladi, qaysi qismi (masalan, relationship()) jadvalda "
        "umuman ustun sifatida mavjud emasligini aniq ko'rsating."
    ),
    "task_description_ru": (
        "Откройте настоящие файлы app/models/course.py и app/models/lesson.py этой "
        "платформы (или, если репозиторий недоступен, используйте пример Course/"
        "Lesson из урока). Для каждого вручную напишите соответствующий SQL-оператор "
        "CREATE TABLE, затем подготовьте короткий отчёт: какая часть модели напрямую "
        "соответствует колонке, а какая (например, relationship()) вообще не "
        "существует в таблице как колонка — покажите это явно."
    ),
    "task_requirements": (
        "1) Ikkita CREATE TABLE bayonoti (courses, lessons) FOREIGN KEY bilan. "
        "2) Har bir model atributi uchun jadval: 'ORM atributi' | 'Jadval ustuni "
        "yoki YO'Q'. 3) Kamida 3 ta impedance mismatch holatini (identity, "
        "munosabat, granularity yoki turlar) o'z so'zlaringiz bilan tushuntiring."
    ),
    "task_requirements_ru": (
        "1) Два оператора CREATE TABLE (courses, lessons) с FOREIGN KEY. "
        "2) Таблица для каждого атрибута модели: 'атрибут ORM' | 'колонка таблицы "
        "или НЕТ'. 3) Объясните своими словами минимум 3 случая impedance "
        "mismatch (идентичность, связь, гранулярность или типы)."
    ),
    "task_technologies": "PostgreSQL, SQLAlchemy 2.x, Python",
    "task_deadline_days": 3,
}

L0_SAMPLE = {
    "title": "Namuna: Course/Lesson — SQL va ORM yonma-yon",
    "description": (
        "Bir xil ikkita jadval (courses, lessons) uchun xom SQL CREATE TABLE va "
        "unga mos SQLAlchemy 2.x deklarativ modeli, hamda ularning farqini "
        "ko'rsatuvchi izohli jadval."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "schema.sql",
            "language": "sql",
            "code": (
                "CREATE TABLE courses (\n"
                "    id SERIAL PRIMARY KEY,\n"
                "    title VARCHAR(150) NOT NULL\n"
                ");\n\n"
                "CREATE TABLE lessons (\n"
                "    id SERIAL PRIMARY KEY,\n"
                "    title VARCHAR(500) NOT NULL,\n"
                "    \"order\" INTEGER DEFAULT 0,\n"
                "    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE\n"
                ");\n"
            ),
        },
        {
            "filename": "models.py",
            "language": "python",
            "code": (
                "from typing import List\n"
                "from sqlalchemy import String, Integer, ForeignKey\n"
                "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n\n\n"
                "class Base(DeclarativeBase):\n"
                "    pass\n\n\n"
                "class Course(Base):\n"
                "    __tablename__ = \"courses\"\n\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    title: Mapped[str] = mapped_column(String(150))\n"
                "    # relationship() — bu Python atributi, jadvalda ustun EMAS.\n"
                "    lessons: Mapped[List[\"Lesson\"]] = relationship(back_populates=\"course\")\n\n\n"
                "class Lesson(Base):\n"
                "    __tablename__ = \"lessons\"\n\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    title: Mapped[str] = mapped_column(String(500))\n"
                "    order: Mapped[int] = mapped_column(Integer, default=0)\n"
                "    course_id: Mapped[int] = mapped_column(ForeignKey(\"courses.id\", ondelete=\"CASCADE\"))\n"
                "    course: Mapped[\"Course\"] = relationship(back_populates=\"lessons\")\n"
            ),
        },
        {
            "filename": "MISMATCH_NOTES.md",
            "language": "markdown",
            "code": (
                "| ORM atributi        | Jadval ustuni?                       |\n"
                "|---------------------|---------------------------------------|\n"
                "| Course.id           | courses.id                            |\n"
                "| Course.title        | courses.title                         |\n"
                "| Course.lessons      | YO'Q — faqat Python munosabati        |\n"
                "| Lesson.course_id    | lessons.course_id                     |\n"
                "| Lesson.course       | YO'Q — course_id orqali hisoblanadi    |\n"
            ),
        },
    ],
}

L0_EXERCISES = [
    {
        "title": "Impedance mismatch nima?",
        "title_ru": "Что такое impedance mismatch?",
        "description": "Quyidagilardan qaysi biri 'object-relational impedance mismatch' ta'rifiga to'g'ri keladi?",
        "description_ru": "Какое из следующих определений верно описывает 'object-relational impedance mismatch'?",
        "exercise_type": "multiple_choice",
        "options": [
            "Relyatsion baza va obyektga yo'naltirilgan til orasidagi tabiiy modellashtirish nomuvofiqligi",
            "SQL so'rovining bajarilish vaqti uzoq bo'lishi",
            "Python va PostgreSQL versiyalari mos kelmasligi",
            "ORM kutubxonasining tarmoq protokoli xatosi",
        ],
        "options_ru": [
            "Естественное несоответствие моделирования между реляционной базой и объектно-ориентированным языком",
            "Долгое время выполнения SQL-запроса",
            "Несовместимость версий Python и PostgreSQL",
            "Ошибка сетевого протокола библиотеки ORM",
        ],
        "correct_answers": "A",
        "hint": "Bu atama ikki xil 'fikrlash modeli' (qator/jadval vs obyekt/klass) orasidagi farqga tegishli.",
        "hint_ru": "Этот термин относится к разнице между двумя 'моделями мышления' (строка/таблица против объекта/класса).",
        "explanation": "Impedance mismatch — bazaning relyatsion modeli bilan OOP tilining obyekt modeli orasidagi tabiiy farq.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "ORM afzalliklarini tartiblang",
        "title_ru": "Расположите этапы работы с ORM в правильном порядке",
        "description": "Yangi darsni bazaga qo'shishning ORM orqali odatiy oqimini to'g'ri tartibga joylashtiring.",
        "description_ru": "Расположите типичный порядок добавления нового урока в базу через ORM правильно.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Lesson(...) obyektini yaratish",
            "db.add(lesson) bilan sessiyaga qo'shish",
            "await db.commit() bilan saqlash",
            "lesson.id orqali yangi ID'ni o'qish",
        ],
        "drag_items_ru": [
            "Создать объект Lesson(...)",
            "Добавить в сессию через db.add(lesson)",
            "Сохранить через await db.commit()",
            "Прочитать новый ID через lesson.id",
        ],
        "correct_order": [
            "Lesson(...) obyektini yaratish",
            "db.add(lesson) bilan sessiyaga qo'shish",
            "await db.commit() bilan saqlash",
            "lesson.id orqali yangi ID'ni o'qish",
        ],
        "hint": "Avval Python obyekti yaratiladi, keyin sessiyaga bildiriladi, keyin bazaga yuboriladi.",
        "hint_ru": "Сначала создаётся объект Python, потом он сообщается сессии, затем отправляется в базу.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Data Mapper naqshi",
        "title_ru": "Паттерн Data Mapper",
        "description": "SQLAlchemy qanday ORM naqshiga amal qiladi, unda obyektning o'zida save() metodi YO'Q, saqlash alohida qatlam orqali boradi: ___",
        "description_ru": "Какому паттерну ORM следует SQLAlchemy, где у объекта НЕТ метода save(), а сохранение идёт через отдельный слой: ___",
        "exercise_type": "fill_in_blank",
        "correct_answers": "Data Mapper",
        "correct_answers_ru": "Data Mapper",
        "hint": "Ikkinchi so'z 'Mapper' bilan tugaydi (Active Record'ga qarama-qarshi).",
        "hint_ru": "Второе слово заканчивается на 'Mapper' (в противоположность Active Record).",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 1 — SQLAlchemy: Core va ORM
# ---------------------------------------------------------------------------

L1_TEXT = """
<h3>SQLAlchemy'ning ikki qatlami</h3>
<p>SQLAlchemy aslida ikkita alohida, lekin bir-biriga bog'liq kutubxonadan
iborat: <strong>SQLAlchemy Core</strong> va <strong>SQLAlchemy ORM</strong>. Core —
bu SQL so'rovlarni Python obyektlari sifatida qurish tili: <code>Table</code>,
<code>Column</code>, <code>select()</code>, <code>insert()</code>. ORM esa Core
ustiga qurilgan yuqori darajadagi qatlam: sizga jadval o'rniga Python
klassini, qator o'rniga obyektni beradi. Muhim narsa — ORM Core'ni
<em>almashtirmaydi</em>, balki uning ustiga qo'shimcha xarita (mapping)
qo'shadi. Har qanday ORM so'rovi ichida Core ifodasi yashiringan.</p>

<h3>Qachon Core, qachon ORM ishlatiladi?</h3>
<p>Ushbu platformaning backendida ikkalasi ham ishlatiladi: app/models/*.py
fayllarida <code>Mapped[...]</code> bilan yozilgan ORM klasslari bor (masalan
Course, Lesson), lekin app/models/course.py'dagi <code>student_courses</code>
jadvali esa <code>Table(...)</code> orqali to'g'ridan-to'g'ri Core darajasida
e'lon qilingan — chunki bu jadval faqat bog'lovchi (association) jadval, unga
mos alohida Python klassi kerak emas. Umumiy qoida: domenning asosiy
obyektlari (Course, Lesson, Student) uchun ORM klassi, faqat bog'lovchi
jadval yoki ommaviy (bulk) operatsiyalar uchun Core ishlatiladi.</p>

<h3>Engine — bazaga ulanishning yagona nuqtasi</h3>
<p><code>Engine</code> — SQLAlchemy'ning bazaga ulanish pool'ini boshqaruvchi
obyekti. Bu platformada u app/db/database.py faylida bir marta yaratiladi:
<code>create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG,
future=True)</code>. Engine hech qachon so'rov ichida qayta yaratilmaydi — u
butun ilova hayoti davomida bitta bo'lishi kerak, chunki u ichida connection
pool'ni saqlaydi (12-darsda pool tugashi degan real muammoni ko'ramiz).</p>

<h3>Session — ORM'ning ish birligi (Unit of Work)</h3>
<p>Engine'dan farqli o'laroq, <code>Session</code> — qisqa muddatli, odatda bitta
so'rov (request) davomida yashaydigan obyekt. U <code>async_sessionmaker</code>
orqali "fabrika" sifatida tayyorlanadi va har bir so'rov uchun yangi Session
ochiladi. Bu platformada bu FastAPI'ning dependency injection orqali amalga
oshadi — har bir endpoint funksiyasi <code>db: AsyncSession = Depends(get_db)</code>
parametrini oladi. Session — sizning o'zgarishlaringizni (add, delete,
update) kuzatib boradigan va ularni bitta tranzaksiyada bazaga jo'natadigan
"ish birligi".</p>

<h3>Sinxron va asinxron: nega "async" muhim</h3>
<p>SQLAlchemy 1.4'gacha faqat sinxron (blocking) API bor edi. 2.x versiyasi
to'liq <code>asyncio</code>'ni qo'llab-quvvatlaydi: <code>create_async_engine</code>,
<code>AsyncSession</code>, <code>await db.execute(...)</code>. FastAPI kabi
asinxron framework bilan ishlaganda sinxron SQLAlchemy ishlatish — bitta
sekin so'rov butun serverni bloklab qo'yishi mumkin degani. Shuning uchun bu
platforma asyncpg drayveri bilan to'liq async stackdan foydalanadi — kursning
barcha misollari ham shu uslubda yoziladi (<code>async def</code>, <code>await</code>,
<code>AsyncSession</code>).</p>

<h3>Deklarativ baza (DeclarativeBase)</h3>
<p>Har bir ORM modeli bitta umumiy ota-klassdan meros oladi — bu platformada
u <code>app/db/base_class.py</code>'dagi <code>Base(DeclarativeBase)</code>.
Barcha modellar shu <code>Base</code>'ning metadatasiga ro'yxatdan o'tadi,
shuning uchun <code>Base.metadata.create_all()</code> (yoki Alembic) barcha
jadvallarni bir joyda bilishi mumkin bo'ladi.</p>

<h3>Bulk operatsiyalar uchun nega ba'zan Core afzal</h3>
<p>ORM har bir qatorni to'liq Python obyektiga aylantirish uchun narx
to'laydi: identity map'ga yozish, atributlarni kuzatish, munosabatlarni
tayyorlash. Bitta qatorni o'qish/yozishda bu narx sezilmaydi, lekin 5000
qatorni bir vaqtda yangilashda sezilarli bo'lib qoladi. Shuning uchun katta
hajmdagi (bulk) UPDATE/INSERT operatsiyalari uchun ko'pincha to'g'ridan-
to'g'ri Core <code>update()</code>/<code>insert()</code> ishlatiladi — bitta
SQL bayonoti, minglab Python obyektisiz. Bu — "ORM har doim ORM darajasida
qilinishi kerak" degan noto'g'ri qoidaning aniq istisnosi.</p>

<h3>echo=True — ORM "qora quti" emasligining isboti</h3>
<p>Har qanday paytda Engine'ni <code>echo=True</code> bilan yaratsangiz,
SQLAlchemy hosil qilgan HAR BIR SQL bayonotini va uning parametrlarini
konsolga chiqaradi. Bu platformada bu <code>settings.DEBUG</code> orqali
boshqariladi. Yangi boshlovchilar ko'pincha ORM'ni "SQL'ni yashiradigan sehr"
deb noto'g'ri tushunishadi — aslida esa har bir ORM chaqiruvi ortida aniq,
ko'rish mumkin bo'lgan SQL bayonoti yotadi, va tajribali dasturchi
muammoni tuzatishda birinchi navbatda aynan shu bayonotni tekshiradi.</p>
""".strip()

L1_TEXT_RU = """
<h3>Два слоя SQLAlchemy</h3>
<p>SQLAlchemy на самом деле состоит из двух отдельных, но связанных между
собой библиотек: <strong>SQLAlchemy Core</strong> и <strong>SQLAlchemy ORM</strong>.
Core — это язык построения SQL-запросов как объектов Python:
<code>Table</code>, <code>Column</code>, <code>select()</code>,
<code>insert()</code>. ORM — это слой более высокого уровня, построенный
поверх Core: вместо таблицы вы получаете класс Python, вместо строки —
объект. Важно понимать — ORM <em>не заменяет</em> Core, а добавляет над ним
дополнительную карту (mapping). Внутри любого ORM-запроса скрыто выражение
Core.</p>

<h3>Когда использовать Core, а когда ORM?</h3>
<p>В backend этой платформы используются оба: в файлах app/models/*.py есть
ORM-классы, написанные через <code>Mapped[...]</code> (например Course,
Lesson), но таблица <code>student_courses</code> в app/models/course.py
объявлена напрямую на уровне Core через <code>Table(...)</code> — потому что
это лишь связующая (association) таблица, отдельный класс Python ей не
нужен. Общее правило: для основных объектов домена (Course, Lesson, Student)
используется ORM-класс, а только для связующих таблиц или массовых (bulk)
операций — Core.</p>

<h3>Engine — единая точка подключения к базе</h3>
<p><code>Engine</code> — объект SQLAlchemy, управляющий пулом подключений к
базе. На этой платформе он создаётся один раз в файле app/db/database.py:
<code>create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG,
future=True)</code>. Engine никогда не создаётся заново внутри запроса — он
должен быть один на весь жизненный цикл приложения, поскольку внутри хранит
пул подключений (реальную проблему исчерпания пула увидим в уроке 12).</p>

<h3>Session — единица работы (Unit of Work) в ORM</h3>
<p>В отличие от Engine, <code>Session</code> — короткоживущий объект, обычно
существующий в рамках одного запроса. Он готовится как "фабрика" через
<code>async_sessionmaker</code>, и для каждого запроса открывается новая
Session. На этой платформе это происходит через dependency injection
FastAPI — каждая функция-эндпоинт получает параметр <code>db: AsyncSession =
Depends(get_db)</code>. Session — это "единица работы", отслеживающая ваши
изменения (add, delete, update) и отправляющая их в базу одной транзакцией.</p>

<h3>Синхронность и асинхронность: почему "async" важен</h3>
<p>До версии 1.4 у SQLAlchemy был только синхронный (блокирующий) API.
Версия 2.x полностью поддерживает <code>asyncio</code>: <code>create_async_engine</code>,
<code>AsyncSession</code>, <code>await db.execute(...)</code>. Использование
синхронного SQLAlchemy с асинхронным фреймворком вроде FastAPI означает, что
один медленный запрос может заблокировать весь сервер. Поэтому эта платформа
использует полностью асинхронный стек с драйвером asyncpg — все примеры
курса написаны в том же стиле (<code>async def</code>, <code>await</code>,
<code>AsyncSession</code>).</p>

<h3>Декларативная база (DeclarativeBase)</h3>
<p>Каждая ORM-модель наследуется от одного общего родительского класса — на
этой платформе это <code>Base(DeclarativeBase)</code> в
<code>app/db/base_class.py</code>. Все модели регистрируются в метаданных
этого <code>Base</code>, поэтому <code>Base.metadata.create_all()</code>
(или Alembic) может знать обо всех таблицах в одном месте.</p>

<h3>Почему для массовых операций иногда предпочтительнее Core</h3>
<p>ORM платит цену за превращение каждой строки в полноценный объект Python:
запись в identity map, отслеживание атрибутов, подготовка связей. При
чтении/записи одной строки эта цена незаметна, но при обновлении 5000 строк
одновременно она становится значимой. Поэтому для операций большого объёма
(bulk) часто используется напрямую Core <code>update()</code>/<code>insert()</code>
— один SQL-оператор, без тысяч объектов Python. Это явное исключение из
неверного правила "всё всегда нужно делать через ORM".</p>

<h3>echo=True — доказательство того, что ORM не "чёрный ящик"</h3>
<p>В любой момент, создав Engine с <code>echo=True</code>, вы увидите в
консоли КАЖДЫЙ сгенерированный SQLAlchemy SQL-оператор вместе с его
параметрами. На этой платформе это управляется через
<code>settings.DEBUG</code>. Новички часто ошибочно считают ORM "магией,
прячущей SQL" — на самом деле за каждым вызовом ORM стоит конкретный,
видимый SQL-оператор, и опытный разработчик при отладке проблемы в первую
очередь проверяет именно его.</p>
""".strip()

L1_CODE = """
# ============================================================
# 1) Core darajasi — jadval va so'rovni QO'LDA, klasssiz qurish
# ============================================================
from sqlalchemy import MetaData, Table, Column, Integer, String, select

metadata = MetaData()

courses_table = Table(
    "courses", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(150), nullable=False),
)

# Core so'rovi — natija Python klassi emas, "Row" obyektlari qaytadi:
core_stmt = select(courses_table.c.id, courses_table.c.title).where(courses_table.c.id == 41)
# result = await conn.execute(core_stmt)
# row = result.first()  # row.id, row.title — lekin bu Course obyekti EMAS

# ============================================================
# 2) Bog'lovchi (association) jadval — bu platformada Core darajasida
#    e'lon qilingan haqiqiy misol (app/models/course.py'dan soddalashtirilgan)
# ============================================================
from sqlalchemy import ForeignKey, Table as CoreTable

student_courses = CoreTable(
    "student_courses", metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)
# Nega Core? Chunki bu jadvalning o'ziga xos xatti-harakati yo'q — u faqat
# ikkita ID juftligini saqlaydi. Alohida Python klassi keraksiz murakkablik
# qo'shgan bo'lardi.

# ============================================================
# 3) ORM darajasi — xuddi shu Course, endi to'liq deklarativ klass sifatida
# ============================================================
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))


orm_stmt = select(Course).where(Course.id == 41)
# result = await db.execute(orm_stmt)
# course = result.scalar_one()   # course — bu HAQIQIY Course obyekti, course.title ishlaydi

# ============================================================
# 4) Engine — app/db/database.py'dagi HAQIQIY sozlash (soddalashtirilgan)
# ============================================================
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/student_platform"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,      # True bo'lsa — har bir hosil bo'lgan SQL konsolga chiqadi
    future=True,
)

# Session — "fabrika", har bir so'rov uchun YANGI instansiya yaratadi:
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # commit'dan keyin ham obyekt atributlariga kirish mumkin
    autoflush=True,
)


# ============================================================
# 5) FastAPI dependency — har bir HTTP so'rovi uchun bitta Session
# ============================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        # `async with` blokidan chiqishda Session avtomatik yopiladi —
        # ochiq qolgan Session'lar connection pool'ni tugatib qo'yadi (12-dars).


# Endpoint misoli:
# @router.get("/courses/{course_id}")
# async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Course).where(Course.id == course_id))
#     return result.scalar_one_or_none()

# ============================================================
# 6) Ommaviy (bulk) operatsiyalar uchun Core tanlanadi, ORM emas
# ============================================================
# 5000 ta talaba uchun "eslatma yuborildi" belgisini yangilash kerak bo'lsa,
# ORM orqali 5000 ta obyektni yuklab, birma-bir o'zgartirib, keyin commit
# qilish — 5000 ta obyektni xotiraga yuklaydi va identity map'ni to'ldiradi.
# Core orqali esa BITTA UPDATE bayonoti yetarli:
from sqlalchemy import update

bulk_stmt = (
    update(student_courses)
    .where(student_courses.c.course_id == 41)
    .values(reminder_sent=True)
)
# await db.execute(bulk_stmt)
# await db.commit()
# Bu — ORM'ning "har doim yaxshi" emasligining aniq misoli: yozish
# ko'lami katta bo'lsa, Core to'g'ridan-to'g'ri bitta SQL bayonoti hosil
# qiladi, ORM esa har bir qatorni Python obyektiga aylantirish narxini
# to'laydi.

# ============================================================
# 7) echo=True qanday ko'rinishda ishlaydi — ORM hech narsani yashirmaydi
# ============================================================
debug_engine = create_async_engine(DATABASE_URL, echo=True)
# Shu Engine bilan yuqoridagi orm_stmt bajarilsa, konsolga aynan shunday
# chiqadi:
#
# INFO sqlalchemy.engine.Engine SELECT courses.id, courses.title
# INFO sqlalchemy.engine.Engine FROM courses
# INFO sqlalchemy.engine.Engine WHERE courses.id = $1::INTEGER
# INFO sqlalchemy.engine.Engine [generated in 0.00021s] (41,)
#
# Bu — production'da DEBUG rejimida (settings.DEBUG orqali) yoqiladigan
# aynan shu chiqish; har qanday "sirli" ORM xatti-harakatini shu orqali
# tekshirish mumkin.

# ============================================================
# 8) Mini-solishtiruv: bir xil vazifa uchun qancha kod kerak
# ============================================================
# Xom SQL (psycopg2, ORM'siz):
#   cur.execute("SELECT id, title FROM courses WHERE id = %s", (41,))
#   row = cur.fetchone()
#   course = {"id": row[0], "title": row[1]}   # dict'ga qo'lda aylantirish
#
# SQLAlchemy Core:
#   row = (await conn.execute(select(courses_table).where(courses_table.c.id == 41))).first()
#   # baribir Row, lekin so'rov qurilishi turdosh (type-safe) va kompozitsiyalanadigan
#
# SQLAlchemy ORM:
#   course = (await db.execute(select(Course).where(Course.id == 41))).scalar_one()
#   # course.title darhol mavjud, munosabatlar course.lessons ham shunday
#
# Farq "sehr"da emas — balki bazaning qatorini Python obyektiga
# aylantirish rutinasini kim o'z zimmasiga olishida: siz qo'lda, Core
# qisman, ORM to'liq.
""".strip()

L1_CODE_RU = """
# ============================================================
# 1) Уровень Core — построение таблицы и запроса ВРУЧНУЮ, без классов
# ============================================================
from sqlalchemy import MetaData, Table, Column, Integer, String, select

metadata = MetaData()

courses_table = Table(
    "courses", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(150), nullable=False),
)

# Запрос Core — результат это не класс Python, возвращаются объекты "Row":
core_stmt = select(courses_table.c.id, courses_table.c.title).where(courses_table.c.id == 41)
# result = await conn.execute(core_stmt)
# row = result.first()  # row.id, row.title — но это НЕ объект Course

# ============================================================
# 2) Связующая (association) таблица — реальный пример на этой платформе,
#    объявленный на уровне Core (упрощено из app/models/course.py)
# ============================================================
from sqlalchemy import ForeignKey, Table as CoreTable

student_courses = CoreTable(
    "student_courses", metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)
# Почему Core? Потому что у этой таблицы нет собственного поведения — она
# лишь хранит пару ID. Отдельный класс Python добавил бы лишнюю сложность.

# ============================================================
# 3) Уровень ORM — тот же Course, теперь как полноценный декларативный класс
# ============================================================
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))


orm_stmt = select(Course).where(Course.id == 41)
# result = await db.execute(orm_stmt)
# course = result.scalar_one()   # course — это НАСТОЯЩИЙ объект Course, course.title работает

# ============================================================
# 4) Engine — РЕАЛЬНАЯ настройка из app/db/database.py (упрощено)
# ============================================================
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/student_platform"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,      # если True — каждый сгенерированный SQL выводится в консоль
    future=True,
)

# Session — "фабрика", создающая НОВЫЙ экземпляр для каждого запроса:
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # доступ к атрибутам объекта возможен даже после commit
    autoflush=True,
)


# ============================================================
# 5) Зависимость FastAPI — одна Session на каждый HTTP-запрос
# ============================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        # При выходе из блока `async with` Session закрывается автоматически —
        # незакрытые Session исчерпывают пул подключений (урок 12).


# Пример эндпоинта:
# @router.get("/courses/{course_id}")
# async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Course).where(Course.id == course_id))
#     return result.scalar_one_or_none()

# ============================================================
# 6) Для массовых (bulk) операций выбирается Core, а не ORM
# ============================================================
# Если нужно обновить флаг "напоминание отправлено" для 5000 студентов,
# загрузка 5000 объектов через ORM, изменение каждого по отдельности и
# затем commit — загружает 5000 объектов в память и заполняет identity map.
# Через Core достаточно ОДНОГО оператора UPDATE:
from sqlalchemy import update

bulk_stmt = (
    update(student_courses)
    .where(student_courses.c.course_id == 41)
    .values(reminder_sent=True)
)
# await db.execute(bulk_stmt)
# await db.commit()
# Это наглядный пример того, что ORM не всегда "лучше": при большом объёме
# записи Core генерирует один SQL-оператор напрямую, тогда как ORM платит
# цену превращения каждой строки в объект Python.

# ============================================================
# 7) Как выглядит echo=True — ORM ничего не прячет
# ============================================================
debug_engine = create_async_engine(DATABASE_URL, echo=True)
# С этим Engine при выполнении orm_stmt выше в консоль выведется именно это:
#
# INFO sqlalchemy.engine.Engine SELECT courses.id, courses.title
# INFO sqlalchemy.engine.Engine FROM courses
# INFO sqlalchemy.engine.Engine WHERE courses.id = $1::INTEGER
# INFO sqlalchemy.engine.Engine [generated in 0.00021s] (41,)
#
# Именно этот вывод включается в production в режиме DEBUG (через
# settings.DEBUG) — так можно проверить любое "загадочное" поведение ORM.

# ============================================================
# 8) Мини-сравнение: сколько кода нужно для одной и той же задачи
# ============================================================
# Чистый SQL (psycopg2, без ORM):
#   cur.execute("SELECT id, title FROM courses WHERE id = %s", (41,))
#   row = cur.fetchone()
#   course = {"id": row[0], "title": row[1]}   # ручное превращение в dict
#
# SQLAlchemy Core:
#   row = (await conn.execute(select(courses_table).where(courses_table.c.id == 41))).first()
#   # тоже Row, но конструкция запроса типобезопасна и композируема
#
# SQLAlchemy ORM:
#   course = (await db.execute(select(Course).where(Course.id == 41))).scalar_one()
#   # course.title сразу доступен, отношения course.lessons тоже
#
# Разница не в "магии" — а в том, кто берёт на себя рутинное превращение
# строки базы в объект Python: вы вручную, Core частично, ORM полностью.
""".strip()

L1_TASK = {
    "task_title": "Core va ORM'ni bitta skriptda solishtiring",
    "task_title_ru": "Сравните Core и ORM в одном скрипте",
    "task_description": (
        "students va student_courses jadvallari uchun (1) Core darajasida "
        "Table(...) e'lonlarini yozing va Core select() bilan bitta talabaning "
        "barcha kurslarini oling; (2) xuddi shu natijani ORM Student/Course "
        "klasslari va relationship() bilan oling. Ikkala usulning hosil "
        "bo'lgan SQL matnini solishtirib, farqni tushuntiring."
    ),
    "task_description_ru": (
        "Для таблиц students и student_courses (1) напишите объявления "
        "Table(...) на уровне Core и получите все курсы одного студента через "
        "Core select(); (2) получите тот же результат через ORM-классы Student/"
        "Course и relationship(). Сравните получившийся SQL-текст обоих "
        "способов и объясните разницу."
    ),
    "task_requirements": (
        "1) Core: Table() e'lonlari + select() so'rovi. 2) ORM: DeclarativeBase "
        "klasslari + relationship() + select() so'rovi. 3) Ikkala so'rovning "
        "str(stmt.compile(...)) natijasini yozma taqqoslash bilan keltiring."
    ),
    "task_requirements_ru": (
        "1) Core: объявления Table() + запрос select(). 2) ORM: классы "
        "DeclarativeBase + relationship() + запрос select(). 3) Приведите "
        "результат str(stmt.compile(...)) обоих запросов с письменным "
        "сравнением."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x Core+ORM, PostgreSQL",
    "task_deadline_days": 4,
}

L1_SAMPLE = {
    "title": "Namuna: Bitta natija, ikki yo'l (Core va ORM)",
    "description": "students/courses uchun Core Table() e'lonlari va ORM klasslari bir faylda, ikkalasining so'rovi bilan.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "core_vs_orm.py",
            "language": "python",
            "code": (
                "from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select\n"
                "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n"
                "from typing import List\n\n"
                "metadata = MetaData()\n\n"
                "# --- Core darajasi ---\n"
                "students_core = Table(\n"
                "    \"students\", metadata,\n"
                "    Column(\"id\", Integer, primary_key=True),\n"
                "    Column(\"username\", String(80)),\n"
                ")\n"
                "student_courses_core = Table(\n"
                "    \"student_courses\", metadata,\n"
                "    Column(\"student_id\", ForeignKey(\"students.id\"), primary_key=True),\n"
                "    Column(\"course_id\", ForeignKey(\"courses.id\"), primary_key=True),\n"
                ")\n\n"
                "core_stmt = (\n"
                "    select(students_core.c.username)\n"
                "    .join(student_courses_core, student_courses_core.c.student_id == students_core.c.id)\n"
                "    .where(student_courses_core.c.course_id == 41)\n"
                ")\n\n\n"
                "# --- ORM darajasi ---\n"
                "class Base(DeclarativeBase):\n"
                "    pass\n\n\n"
                "class Student(Base):\n"
                "    __tablename__ = \"students\"\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    username: Mapped[str] = mapped_column(String(80))\n"
                "    courses: Mapped[List[\"Course\"]] = relationship(secondary=\"student_courses\")\n\n\n"
                "class Course(Base):\n"
                "    __tablename__ = \"courses\"\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    title: Mapped[str] = mapped_column(String(150))\n\n\n"
                "orm_stmt = select(Student).join(Student.courses).where(Course.id == 41)\n\n"
                "print(\"CORE SQL:\", str(core_stmt))\n"
                "print(\"ORM  SQL:\", str(orm_stmt))\n"
            ),
        },
    ],
}

L1_EXERCISES = [
    {
        "title": "Core va ORM munosabati",
        "title_ru": "Отношение Core и ORM",
        "description": "SQLAlchemy ORM haqida qaysi ta'rif to'g'ri?",
        "description_ru": "Какое утверждение о SQLAlchemy ORM верно?",
        "exercise_type": "multiple_choice",
        "options": [
            "ORM Core ustiga qurilgan qo'shimcha qatlam, Core'ni almashtirmaydi",
            "ORM va Core butunlay bog'liq bo'lmagan ikki alohida kutubxona",
            "Core faqat eski SQLAlchemy versiyalarida mavjud edi",
            "ORM ishlatilganda Core kodi umuman ishlamaydi",
        ],
        "options_ru": [
            "ORM — это дополнительный слой поверх Core, не заменяющий его",
            "ORM и Core — два полностью независимых друг от друга модуля",
            "Core существовал только в старых версиях SQLAlchemy",
            "При использовании ORM код Core вообще не выполняется",
        ],
        "correct_answers": "A",
        "hint": "Har qanday ORM so'rovi ichida Core ifodasi bor.",
        "hint_ru": "Внутри любого ORM-запроса есть выражение Core.",
        "explanation": "ORM — Core ustiga qurilgan xarita (mapping) qatlami; ikkalasi bir kutubxonaning qismlari.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Engine yashash muddati",
        "title_ru": "Время жизни Engine",
        "description": "create_async_engine() odatda ilova hayotida necha marta chaqiriladi?",
        "description_ru": "Сколько раз обычно вызывается create_async_engine() за время жизни приложения?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir marta, ilova ishga tushganda",
            "Har bir HTTP so'rovi uchun bir marta",
            "Har bir SQL so'rovi uchun bir marta",
            "Har foydalanuvchi sessiyasi uchun bir marta",
        ],
        "options_ru": [
            "Один раз, при запуске приложения",
            "Один раз на каждый HTTP-запрос",
            "Один раз на каждый SQL-запрос",
            "Один раз на каждую пользовательскую сессию",
        ],
        "correct_answers": "A",
        "hint": "Engine connection pool'ni saqlaydi — pool har so'rovda qayta yaratilmaydi.",
        "hint_ru": "Engine хранит пул подключений — пул не создаётся заново при каждом запросе.",
        "explanation": "Engine butun ilova hayoti davomida bitta bo'lishi kerak; Session esa har so'rov uchun yangi ochiladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Deklarativ ota-klass",
        "title_ru": "Декларативный родительский класс",
        "description": "Barcha ORM modellari meros oladigan umumiy ota-klass odatda qanday nomlanadi: class ___(DeclarativeBase)?",
        "description_ru": "Как обычно называется общий родительский класс, от которого наследуются все ORM-модели: class ___(DeclarativeBase)?",
        "exercise_type": "fill_in_blank",
        "correct_answers": "Base",
        "hint": "Bu platformada app/db/base_class.py faylida aynan shu nom ishlatilgan.",
        "hint_ru": "На этой платформе в файле app/db/base_class.py используется именно это имя.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 2 — Modellar va Mapping: jadvallardan Python klasslarga
# ---------------------------------------------------------------------------

L2_TEXT = """
<h3>Deklarativ model — jadval ta'rifi va Python klassi bir joyda</h3>
<p>SQLAlchemy 2.x'ning deklarativ uslubida bitta klass bir vaqtning o'zida
ikki narsani ifodalaydi: jadval sxemasi VA Python obyekti shakli. Bu
platformaning <code>app/models/lesson.py</code> faylidagi <code>Lesson</code>
klassi — aynan shunday: <code>__tablename__ = "lessons"</code> jadval nomini
belgilaydi, har bir <code>mapped_column(...)</code> esa bitta ustunni ham,
bitta Python atributini ham bir vaqtda ta'riflaydi. Bu ikkilik — aynan
"mapping" so'zining ma'nosi: bitta joyda yozilgan ta'rif ikki dunyoga
(baza sxemasi va Python turi) bir vaqtda xizmat qiladi.</p>

<h3>Mapped[...] va mapped_column() — SQLAlchemy 2.x'ning yangi uslubi</h3>
<p>1.4 versiyagacha ustunlar oddiy <code>Column(Integer, ...)</code> sifatida
yozilar edi, turlar esa faqat runtime'da tekshirilar edi. 2.x'da
<code>Mapped[int]</code>, <code>Mapped[Optional[str]]</code> kabi Python
type hint'lar qo'shildi — bu IDE'ga va mypy'ga ustunning Python tomonidagi
turini oldindan aytadi. Masalan, <code>app/models/lesson.py</code>'da:
<code>title: Mapped[str] = mapped_column(String(500), nullable=False)</code> —
bu yerda <code>Mapped[str]</code> Python tomonidagi turni, <code>String(500)</code>
esa PostgreSQL tomonidagi <code>VARCHAR(500)</code> ustunini bildiradi.
<code>Optional[str]</code> ishlatilsa, ustun <code>nullable=True</code>
bo'lishi kerakligini SQLAlchemy avtomatik his qiladi (garchi aniqlik uchun
baribir yozib qo'yish yaxshi amaliyot).</p>

<h3>default va server_default — ikkita turli qiymat manbai</h3>
<p>Bu ikkitasi tez-tez chalkashtiriladi: <code>default=</code> — Python
tomonida INSERT vaqtida qo'llanadigan qiymat (masalan
<code>points_reward: Mapped[int] = mapped_column(Integer, default=10)</code>
— agar Python kodi qiymat bermasa, ORM o'zi <code>10</code>ni qo'yadi).
<code>server_default=</code> esa bazaning o'zida DEFAULT sifatida saqlanadi —
hatto ORM'dan chetlab, to'g'ridan-to'g'ri SQL orqali (yoki boshqa ilova
orqali) INSERT qilinganda ham ishlaydi. Bu platformada
<code>points_reward: Mapped[int] = mapped_column(Integer, default=10,
server_default="10")</code> kabi ikkalasi birga ishlatiladi — bu ataylab:
ORM tezkor default'ni beradi, server_default esa har qanday yo'l bilan
kiritilgan qatorlar uchun kafolat beradi (9-darsda migratsiya paytida
server_default'ning nega majburiyligini ko'ramiz).</p>

<h3>Constraint'lar — ma'lumot to'g'riligini baza darajasida kafolatlash</h3>
<p>ORM darajasidagi validatsiya (masalan Pydantic sxemasi) faqat O'SHA ilova
orqali kirgan yozuvlarni tekshiradi. Agar boshqa xizmat yoki qo'lda SQL
skripti bazaga yozsa, ilova darajasidagi tekshiruv chetlab o'tiladi. Shuning
uchun muhim qoidalar baza darajasida ham: <code>nullable=False</code>,
<code>unique=True</code>, <code>ForeignKey(..., ondelete="CASCADE")</code>,
<code>UniqueConstraint(...)</code>. Bu platformada
<code>LessonSample.lesson_id</code> ustuni <code>unique=True</code> bilan
belgilangan — bitta darsda faqat bitta namuna bo'lishi mumkinligini ORM
darajasida emas, PostgreSQL darajasida kafolatlaydi.</p>

<h3>TYPE_CHECKING va oldinga havolalar (forward references)</h3>
<p>Modellar bir-birini import qilganda aylanma import (circular import)
muammosi yuzaga kelishi mumkin: Course Lesson'ni, Lesson esa Course'ni
bilishi kerak. Bu platforma buni <code>if TYPE_CHECKING:</code> bloki va
satr ichida qo'shtirnoqli tur ("Lesson") orqali yechadi — bu faqat statik
tahlil (mypy, IDE) uchun ishlaydi, runtime'da hech qanday import sodir
bo'lmaydi.</p>

<h3>__table_args__ — bir nechta ustunga tegishli qoidalar</h3>
<p>Bitta ustunga tegishli cheklov <code>mapped_column(unique=True)</code>
orqali yoziladi, lekin bir nechta ustunga birga tegishli qoida (masalan
"bitta talaba bitta darsga faqat bitta eslatma qoldira oladi") uchun
<code>__table_args__ = (UniqueConstraint("student_id", "lesson_id"),)</code>
ishlatiladi — bu 107-kursda ko'rgan <code>CREATE UNIQUE INDEX ON
(student_id, lesson_id)</code>'ning ORM ekvivalenti. Xuddi shu joyda
<code>Index("ix_lesson_course_order", "course_id", "order")</code> kabi
kompozit indekslar ham e'lon qilinadi — ya'ni 107-kursda o'rgangan
indekslash mantig'i ORM darajasida ham yo'qolmaydi, faqat Python sintaksisi
bilan yoziladi.</p>

<h3>Migratsiya bilan bog'liqlik — modelni o'zgartirish yetarli emas</h3>
<p>Muhim tushuncha: <code>mapped_column(...)</code>'ga yangi ustun qo'shish
faqat Python klassini o'zgartiradi — production bazasidagi haqiqiy jadval
o'zgarmaydi. Model — bu "bazaning qanday bo'lishi kerakligi" haqidagi
deklaratsiya, Alembic migratsiyasi esa — "bazani shunga qanday
o'zgartirish" haqidagi buyruq. Bu ikkalasi doim sinxron bo'lishi kerak — bu
farq va nega u muhimligi 8-9-10-darslarda batafsil ochib beriladi.</p>
""".strip()

L2_TEXT_RU = """
<h3>Декларативная модель — определение таблицы и класс Python в одном месте</h3>
<p>В декларативном стиле SQLAlchemy 2.x один класс одновременно представляет
две вещи: схему таблицы И форму объекта Python. Класс <code>Lesson</code> в
файле <code>app/models/lesson.py</code> этой платформы — именно такой:
<code>__tablename__ = "lessons"</code> задаёт имя таблицы, а каждый
<code>mapped_column(...)</code> одновременно определяет и колонку, и атрибут
Python. Эта двойственность — и есть смысл слова "mapping": одно
определение служит сразу двум мирам (схеме базы и типу Python).</p>

<h3>Mapped[...] и mapped_column() — новый стиль SQLAlchemy 2.x</h3>
<p>До версии 1.4 колонки писались просто как <code>Column(Integer, ...)</code>,
а типы проверялись только во время выполнения. В 2.x добавлены подсказки
типов Python вроде <code>Mapped[int]</code>, <code>Mapped[Optional[str]]</code>
— они заранее сообщают IDE и mypy тип колонки со стороны Python. Например,
в <code>app/models/lesson.py</code>: <code>title: Mapped[str] =
mapped_column(String(500), nullable=False)</code> — здесь
<code>Mapped[str]</code> обозначает тип со стороны Python, а
<code>String(500)</code> — колонку <code>VARCHAR(500)</code> со стороны
PostgreSQL. Если используется <code>Optional[str]</code>, SQLAlchemy
автоматически понимает, что колонка должна быть <code>nullable=True</code>
(хотя для ясности всё равно рекомендуется указывать явно).</p>

<h3>default и server_default — два разных источника значения</h3>
<p>Эти два часто путают: <code>default=</code> — значение, применяемое на
стороне Python при INSERT (например <code>points_reward: Mapped[int] =
mapped_column(Integer, default=10)</code> — если код Python не передаёт
значение, ORM сам подставит <code>10</code>). <code>server_default=</code>
хранится в самой базе как DEFAULT — работает даже если INSERT выполняется
в обход ORM, напрямую через SQL (или из другого приложения). На этой
платформе часто используются оба вместе:
<code>points_reward: Mapped[int] = mapped_column(Integer, default=10,
server_default="10")</code> — это намеренно: ORM даёт быстрый default, а
server_default гарантирует значение для строк, вставленных любым путём
(в уроке 9 увидим, почему server_default обязателен при миграциях).</p>

<h3>Ограничения (constraints) — гарантия корректности данных на уровне базы</h3>
<p>Валидация на уровне ORM (например, схема Pydantic) проверяет только
записи, пришедшие через ЭТО приложение. Если другой сервис или ручной
SQL-скрипт пишет в базу напрямую, проверка на уровне приложения обходится.
Поэтому важные правила должны быть и на уровне базы: <code>nullable=False</code>,
<code>unique=True</code>, <code>ForeignKey(..., ondelete="CASCADE")</code>,
<code>UniqueConstraint(...)</code>. На этой платформе колонка
<code>LessonSample.lesson_id</code> помечена как <code>unique=True</code> —
это гарантирует, что у урока может быть только один пример, не на уровне
ORM, а на уровне самого PostgreSQL.</p>

<h3>TYPE_CHECKING и прямые ссылки (forward references)</h3>
<p>Когда модели импортируют друг друга, может возникнуть проблема
циклического импорта: Course должен знать Lesson, а Lesson — знать Course.
Эта платформа решает это через блок <code>if TYPE_CHECKING:</code> и тип в
кавычках внутри строки ("Lesson") — это работает только для статического
анализа (mypy, IDE), во время выполнения никакого импорта не происходит.</p>

<h3>__table_args__ — правила, относящиеся сразу к нескольким колонкам</h3>
<p>Ограничение для одной колонки пишется через <code>mapped_column(unique=True)</code>,
но правило, относящееся сразу к нескольким колонкам (например "один студент
может оставить только одну заметку к одному уроку"), задаётся через
<code>__table_args__ = (UniqueConstraint("student_id", "lesson_id"),)</code>
— это ORM-эквивалент <code>CREATE UNIQUE INDEX ON (student_id, lesson_id)</code>
из курса 107. Там же объявляются и составные индексы вроде
<code>Index("ix_lesson_course_order", "course_id", "order")</code> — то есть
логика индексирования, изученная в курсе 107, никуда не исчезает на уровне
ORM, а лишь записывается на синтаксисе Python.</p>

<h3>Связь с миграциями — изменения модели недостаточно</h3>
<p>Важное понимание: добавление нового <code>mapped_column(...)</code>
изменяет только класс Python — реальная таблица в production-базе не
меняется. Модель — это декларация "какой должна быть база", а миграция
Alembic — команда "как именно изменить базу под это". Эти два всегда
должны быть синхронизированы — эта разница и то, почему она важна,
подробно раскрывается в уроках 8-9-10.</p>
""".strip()

L2_CODE = """
# ============================================================
# 1) Lesson modeli — bu platformaning HAQIQIY app/models/lesson.py'idan
#    soddalashtirilgan, lekin muhim qismlari o'zgartirilmagan
# ============================================================
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

if TYPE_CHECKING:
    from app.models.course import Course  # faqat statik tahlil uchun — aylanma import yo'q


class Base(DeclarativeBase):
    pass


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # default — Python tomonida INSERT vaqtida qo'yiladi
    # server_default — bazaning o'zida DEFAULT sifatida saqlanadi (ORM'ni chetlab
    # o'tgan INSERT'lar uchun ham ishlaydi)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    points_reward: Mapped[int] = mapped_column(Integer, default=10, server_default="10")

    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="lessons")


# ============================================================
# 2) default vs server_default — amalda farq
# ============================================================
new_lesson = Lesson(course_id=41, title="Yangi dars")
# new_lesson.order hali None — lekin flush/commit vaqtida ORM `default=0`ni qo'yadi
# db.add(new_lesson)
# await db.flush()
# assert new_lesson.order == 0  # Python tomonidagi default ishladi

# Endi tasavvur qiling: boshqa xizmat to'g'ridan-to'g'ri SQL orqali yozadi:
RAW_INSERT = "INSERT INTO lessons (course_id, title) VALUES (41, 'Boshqa xizmat dars')"
# Bu yerda Python default HECH QACHON ishga tushmaydi — lekin server_default="0"
# tufayli baza o'zi order=0 ni qo'yadi. Agar faqat default= bo'lganda edi
# (server_default'siz), bu qator order=NULL bilan yozilgan bo'lardi.

# ============================================================
# 3) Constraint'lar — LessonSample.lesson_id unique misoli
# ============================================================
class LessonSample(Base):
    __tablename__ = "lesson_samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        unique=True,   # bitta darsda faqat bitta namuna — BAZA darajasida kafolatlanadi
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500))

# Ikkinchi marta bir xil lesson_id bilan qo'shishga urinish:
# db.add(LessonSample(lesson_id=1, title="Ikkinchi namuna"))
# await db.commit()
# -> sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint
# Bu xato Python validatsiyasida emas, PostgreSQL'ning o'zida sodir bo'ladi —
# hatto kimdir Pydantic tekshiruvini chetlab o'tsa ham, baza himoyalangan.

# ============================================================
# 4) Mapped[Optional[...]] va nullable — moslik
# ============================================================
class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    # Optional[int] + nullable=True — ikkalasi mos bo'lishi kerak, aks holda
    # runtime xatosi emas, faqat mypy ogohlantirishi beriladi:
    prerequisite_course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )


# ============================================================
# 5) __table_args__ — kompozit unique va indeks, 107-kursdagi
#    CREATE UNIQUE INDEX / CREATE INDEX'ning ORM ekvivalenti
# ============================================================
from sqlalchemy import Index, UniqueConstraint


class StudentNote(Base):
    __tablename__ = "student_notes"
    __table_args__ = (
        # "bitta talaba — bitta darsga — bitta eslatma" qoidasi
        UniqueConstraint("student_id", "lesson_id", name="uq_student_note_per_lesson"),
        # kurs ichidagi darslarni tezkor tartiblab olish uchun kompozit indeks
        Index("ix_note_student_created", "student_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    note_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Bu ikkalasi ham Alembic migratsiyasi orqali BAZAGA yozilishi kerak —
# modelga qo'shish yetarli emas (8-darsda ko'ramiz):
#   op.create_unique_constraint("uq_student_note_per_lesson", "student_notes", ["student_id", "lesson_id"])
#   op.create_index("ix_note_student_created", "student_notes", ["student_id", "created_at"])

# ============================================================
# 6) Ushbu platformaning haqiqiy modelidan misol — Student.username/email
# ============================================================
class StudentReal(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # unique=True + index=True birga — ustun bir vaqtda ham noyob, ham
    # tezkor qidiruv uchun o'z indeksiga ega (app/models/user.py'dagi
    # haqiqiy qator):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
# unique=True o'zi allaqachon PostgreSQL'da indeks yaratadi — lekin aniq
# index=True aniqlik uchun qoldirilgan va Alembic autogenerate bilan mos
# keladi, aks holda u kod kutayotgan indeksni "ko'rmasligi" mumkin.
""".strip()

L2_CODE_RU = """
# ============================================================
# 1) Модель Lesson — упрощена из РЕАЛЬНОГО app/models/lesson.py этой
#    платформы, но важные части не изменены
# ============================================================
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

if TYPE_CHECKING:
    from app.models.course import Course  # только для статического анализа — без циклического импорта


class Base(DeclarativeBase):
    pass


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # default — применяется на стороне Python при INSERT
    # server_default — хранится в самой базе как DEFAULT (работает и для
    # INSERT в обход ORM)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    points_reward: Mapped[int] = mapped_column(Integer, default=10, server_default="10")

    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_published: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="lessons")


# ============================================================
# 2) default против server_default — разница на практике
# ============================================================
new_lesson = Lesson(course_id=41, title="Новый урок")
# new_lesson.order пока None — но при flush/commit ORM подставит `default=0`
# db.add(new_lesson)
# await db.flush()
# assert new_lesson.order == 0  # сработал default со стороны Python

# Теперь представьте: другой сервис пишет напрямую через SQL:
RAW_INSERT = "INSERT INTO lessons (course_id, title) VALUES (41, 'Урок от другого сервиса')"
# Здесь default Python НИКОГДА не срабатывает — но благодаря
# server_default="0" сама база подставит order=0. Если бы был только
# default= (без server_default), эта строка была бы записана с order=NULL.

# ============================================================
# 3) Ограничения — пример LessonSample.lesson_id unique
# ============================================================
class LessonSample(Base):
    __tablename__ = "lesson_samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        unique=True,   # только один пример на урок — гарантируется на уровне БАЗЫ
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500))

# Попытка добавить второй раз с тем же lesson_id:
# db.add(LessonSample(lesson_id=1, title="Второй пример"))
# await db.commit()
# -> sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint
# Эта ошибка происходит не в валидации Python, а в самом PostgreSQL —
# даже если кто-то обойдёт проверку Pydantic, база защищена.

# ============================================================
# 4) Mapped[Optional[...]] и nullable — соответствие
# ============================================================
class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    # Optional[int] + nullable=True — должны соответствовать друг другу,
    # иначе не ошибка времени выполнения, а лишь предупреждение mypy:
    prerequisite_course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses.id", ondelete="SET NULL"), nullable=True
    )


# ============================================================
# 5) __table_args__ — составной unique и индекс, ORM-эквивалент
#    CREATE UNIQUE INDEX / CREATE INDEX из курса 107
# ============================================================
from sqlalchemy import Index, UniqueConstraint


class StudentNote(Base):
    __tablename__ = "student_notes"
    __table_args__ = (
        # правило "один студент — один урок — одна заметка"
        UniqueConstraint("student_id", "lesson_id", name="uq_student_note_per_lesson"),
        # составной индекс для быстрой сортировки заметок студента
        Index("ix_note_student_created", "student_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    note_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# Оба должны быть записаны в базу через миграцию Alembic — одного
# добавления в модель недостаточно (увидим в уроке 8):
#   op.create_unique_constraint("uq_student_note_per_lesson", "student_notes", ["student_id", "lesson_id"])
#   op.create_index("ix_note_student_created", "student_notes", ["student_id", "created_at"])

# ============================================================
# 6) Пример из реальной модели этой платформы — Student.username/email
# ============================================================
class StudentReal(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # unique=True + index=True вместе — колонка одновременно уникальна
    # и имеет собственный индекс для быстрого поиска (реальная строка
    # из app/models/user.py):
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
# unique=True само по себе уже создаёт индекс в PostgreSQL — но явный
# index=True здесь оставлен для ясности и совместим с автогенерацией
# Alembic, которая иначе могла бы "не увидеть" индекс, ожидаемый кодом.
""".strip()

L2_TASK = {
    "task_title": "O'z modelingizni yozing: StudentNote",
    "task_title_ru": "Напишите свою модель: StudentNote",
    "task_description": (
        "Talaba har bir darsga shaxsiy eslatma yozib qo'ya oladigan StudentNote "
        "modelini SQLAlchemy 2.x deklarativ uslubida yozing: student_id va "
        "lesson_id (ikkalasi ham FOREIGN KEY, CASCADE bilan), note_text (Text, "
        "bo'sh bo'lmasligi shart), is_pinned (Boolean, default=False, "
        "server_default bilan), created_at (server_default=func.now()). Bitta "
        "talaba bitta darsga faqat bitta eslatma yoza olishi kerak."
    ),
    "task_description_ru": (
        "Напишите модель StudentNote в декларативном стиле SQLAlchemy 2.x, "
        "позволяющую студенту оставлять личную заметку к каждому уроку: "
        "student_id и lesson_id (оба FOREIGN KEY с CASCADE), note_text (Text, "
        "обязательно непустой), is_pinned (Boolean, default=False, с "
        "server_default), created_at (server_default=func.now()). Один "
        "студент должен иметь возможность оставить только одну заметку к "
        "одному уроку."
    ),
    "task_requirements": (
        "1) Mapped[...] annotatsiyalari to'g'ri qo'yilgan. 2) Ikkita "
        "ForeignKey, ikkalasi ham ondelete='CASCADE'. 3) (student_id, "
        "lesson_id) juftligi uchun UniqueConstraint yoki unique index. 4) "
        "default va server_default farqini kod izohida tushuntiring."
    ),
    "task_requirements_ru": (
        "1) Корректно расставленные аннотации Mapped[...]. 2) Два "
        "ForeignKey, оба с ondelete='CASCADE'. 3) UniqueConstraint или "
        "уникальный индекс для пары (student_id, lesson_id). 4) Объясните в "
        "комментарии к коду разницу между default и server_default."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM, PostgreSQL",
    "task_deadline_days": 4,
}

L2_SAMPLE = {
    "title": "Namuna: StudentNote modeli va uning UniqueConstraint'i",
    "description": "To'liq StudentNote modeli — Mapped annotatsiyalari, default/server_default, va (student_id, lesson_id) uchun UniqueConstraint bilan.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "student_note.py",
            "language": "python",
            "code": (
                "from datetime import datetime\n"
                "from sqlalchemy import Integer, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint\n"
                "from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase\n\n\n"
                "class Base(DeclarativeBase):\n"
                "    pass\n\n\n"
                "class StudentNote(Base):\n"
                "    __tablename__ = \"student_notes\"\n"
                "    __table_args__ = (\n"
                "        UniqueConstraint(\"student_id\", \"lesson_id\", name=\"uq_student_note_per_lesson\"),\n"
                "    )\n\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    student_id: Mapped[int] = mapped_column(\n"
                "        Integer, ForeignKey(\"students.id\", ondelete=\"CASCADE\"), nullable=False\n"
                "    )\n"
                "    lesson_id: Mapped[int] = mapped_column(\n"
                "        Integer, ForeignKey(\"lessons.id\", ondelete=\"CASCADE\"), nullable=False\n"
                "    )\n"
                "    note_text: Mapped[str] = mapped_column(Text, nullable=False)\n"
                "    # default — Python tomonida INSERT vaqtida; server_default — bazaning\n"
                "    # o'zida, ORM'ni chetlab o'tgan yozuvlar uchun ham amal qiladi.\n"
                "    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default=\"false\")\n"
                "    created_at: Mapped[datetime] = mapped_column(\n"
                "        DateTime(timezone=True), server_default=func.now()\n"
                "    )\n"
            ),
        },
    ],
}

L2_EXERCISES = [
    {
        "title": "default vs server_default",
        "title_ru": "default против server_default",
        "description": "Boshqa xizmat bazaga to'g'ridan-to'g'ri SQL orqali (ORM'siz) yozganda, qaysi default turi baribir ishlaydi?",
        "description_ru": "Когда другой сервис пишет в базу напрямую через SQL (без ORM), какой тип default всё равно сработает?",
        "exercise_type": "multiple_choice",
        "options": ["server_default", "default", "Ikkalasi ham ishlaydi", "Hech biri ishlamaydi"],
        "options_ru": ["server_default", "default", "Оба сработают", "Ни один не сработает"],
        "correct_answers": "A",
        "hint": "default= faqat SQLAlchemy ORM orqali INSERT bo'lganda ishlaydi.",
        "hint_ru": "default= работает только при INSERT через сам SQLAlchemy ORM.",
        "explanation": "server_default bazaning o'z DEFAULT mexanizmi bo'lgani uchun har qanday yo'l bilan kiritilgan yozuvga ham qo'llanadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Modelni to'g'ri tartibda quring",
        "title_ru": "Постройте модель в правильном порядке",
        "description": "Yangi ORM modelini yozishning odatiy qadamlarini tartibga joylashtiring.",
        "description_ru": "Расположите типичные шаги написания новой ORM-модели в правильном порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "__tablename__ ni belgilash",
            "Har bir ustun uchun Mapped[...] + mapped_column() yozish",
            "ForeignKey va constraint'larni qo'shish",
            "relationship() orqali munosabatlarni e'lon qilish",
        ],
        "drag_items_ru": [
            "Указать __tablename__",
            "Написать Mapped[...] + mapped_column() для каждой колонки",
            "Добавить ForeignKey и ограничения",
            "Объявить связи через relationship()",
        ],
        "correct_order": [
            "__tablename__ ni belgilash",
            "Har bir ustun uchun Mapped[...] + mapped_column() yozish",
            "ForeignKey va constraint'larni qo'shish",
            "relationship() orqali munosabatlarni e'lon qilish",
        ],
        "hint": "Avval jadval nomi, keyin ustunlar, keyin cheklovlar, oxirida Python-only munosabatlar.",
        "hint_ru": "Сначала имя таблицы, потом колонки, потом ограничения, в конце связи только для Python.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "unique constraint ma'nosi",
        "title_ru": "Значение unique constraint",
        "description": "LessonSample.lesson_id ustunidagi unique=True nimani kafolatlaydi: har bir darsda faqat bitta ___ bo'lishi mumkin.",
        "description_ru": "Что гарантирует unique=True на колонке LessonSample.lesson_id: у каждого урока может быть только один ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "namuna",
        "correct_answers_ru": "образец",
        "hint": "Bu LessonSample jadvalining vazifasi haqida — u nima saqlaydi?",
        "hint_ru": "Подумайте о назначении таблицы LessonSample — что она хранит?",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 3 — Munosabatlar (Relationships): one-to-many va many-to-many
# ---------------------------------------------------------------------------

L3_TEXT = """
<h3>relationship() — Python atributi, jadval ustuni EMAS</h3>
<p>Bu darsning eng muhim tushunchasi: <code>relationship()</code> hech qanday
ustunga mos KELMAYDI. U faqat ORM'ga "shu ikki klass orasida FOREIGN KEY
orqali bog'lanish bor, shuni Python navigatsiyasiga aylantir" deb aytadi.
Haqiqiy bog'lanish har doim biror ustun (masalan <code>lesson.course_id</code>)
yoki bog'lovchi jadval (masalan <code>student_courses</code>) orqali amalga
oshadi — <code>relationship()</code> esa shu ustinlar ustiga qurilgan
"qulay yo'l", xolos.</p>

<h3>One-to-many: bitta kursning ko'p darsi</h3>
<p>Bu — eng keng tarqalgan munosabat turi. FOREIGN KEY har doim "ko'p"
tomonda joylashadi: <code>lessons.course_id</code> ustuni har bir darsning
qaysi kursga tegishli ekanini bildiradi. ORM darajasida ikki tomonlama
e'lon qilinadi: <code>Course.lessons: Mapped[List["Lesson"]] =
relationship(back_populates="lessons")</code> va <code>Lesson.course:
Mapped["Course"] = relationship(back_populates="course")</code>.
<code>back_populates</code> ikkala tomonni bir-biriga bog'laydi — bitta
tomonni o'zgartirsangiz (masalan <code>lesson.course = new_course</code>),
ikkinchi tomon (<code>new_course.lessons</code>) ham avtomatik yangilanadi,
xotirada — hali bazaga yozilmasdan turib ham.</p>

<h3>Many-to-many: talaba va kurslar orasidagi bog'lovchi jadval</h3>
<p>Talaba bir nechta kursga yozilishi, bitta kursga bir nechta talaba
yozilishi mumkin — bu klassik many-to-many. Bunday holatda FOREIGN KEY
birortasida ham to'g'ridan-to'g'ri joylashmaydi, buning o'rniga alohida
bog'lovchi jadval kerak: bu platformada bu — <code>student_courses</code>
(ikkita ustun: student_id, course_id, ikkalasi ham PRIMARY KEY qismi).
ORM darajasida bu <code>secondary="student_courses"</code> parametri orqali
ko'rsatiladi — <code>app/models/user.py</code>'dagi haqiqiy misol:
<code>enrolled_courses: Mapped[List["Course"]] = relationship("Course",
secondary="student_courses", back_populates="students", lazy="selectin")</code>.</p>

<h3>cascade — bog'liq qatorlar bilan nima qilish kerak</h3>
<p><code>cascade="all, delete-orphan"</code> — bu ota obyekt o'chirilganda
(yoki bola ro'yxatdan chiqarilganda) bola qatorlar bilan nima bo'lishini
belgilaydi. Bu platformada <code>Student.projects</code> munosabati aynan
shu cascade bilan e'lon qilingan: talaba o'chirilsa, uning barcha loyihalari
ham o'chadi (yetim — orphan — qatorlar qolmasligi uchun). Bu — baza
darajasidagi <code>ON DELETE CASCADE</code>'ga o'xshaydi, lekin muhim farq
bor: FOREIGN KEY'dagi <code>ondelete="CASCADE"</code> bazaning o'zida
ishlaydi (ORM'siz ham), <code>cascade=</code> esa faqat ORM Session ichida,
Python darajasida ishlaydi. Ikkalasi ham kerak bo'lishi mumkin — biri
xavfsizlik tarmog'i, ikkinchisi Python obyekt grafigi uchun.</p>

<h3>lazy — munosabat qachon yuklanadi</h3>
<p><code>lazy="selectin"</code> — munosabat asosiy obyekt yuklanganidan
keyin, alohida (lekin samarali, IN(...) orqali) so'rov bilan darhol
yuklanadi. Bu platformada <code>Student.groups</code> va
<code>Student.enrolled_courses</code> aynan shu bilan belgilangan — chunki
bu ma'lumotlar deyarli har doim kerak bo'ladi. <code>lazy</code>'ning boshqa
qiymatlari (default "select", "joined", "subquery") va ular orasidagi farq
— aynan keyingi darsning (5-dars: Eager vs Lazy Loading) mavzusi.</p>

<h3>uselist=False — one-to-one munosabat</h3>
<p>Ba'zan munosabat ro'yxat emas, yagona obyekt bo'lishi kerak: bir talabaning
bitta Ranking yozuvi bor. Bu platformada:
<code>ranking: Mapped[Optional["Ranking"]] = relationship("Ranking",
back_populates="student", uselist=False, cascade="all, delete-orphan")</code>
— <code>uselist=False</code> ORM'ga "bu munosabat List emas, yagona obyekt
(yoki None)" deb aytadi.</p>

<h3>Self-referential munosabat va foreign_keys= aniqlashtirishi</h3>
<p>Ba'zan bir klass o'ziga ishora qiladi — masalan <code>Course.prerequisite_course_id</code>
o'zi <code>courses.id</code>ga ishora qiladi (107-kurs 98-kursni,
98-kurs 41-kursni prerequisite sifatida ko'rsatadi). Bunday holatlarda
SQLAlchemy avtomatik qaysi FOREIGN KEY ishlatilishini bilolmasligi mumkin,
agar bitta klassda bir nechta FOREIGN KEY bir xil jadvalga ishora qilsa —
shuning uchun <code>relationship(..., foreign_keys=[Course.prerequisite_course_id])</code>
orqali aniq ko'rsatish kerak bo'ladi. <code>Group.teacher</code> misolida ham
xuddi shunday: <code>teacher_id</code> ham <code>students</code> jadvaliga
ishora qiladi, lekin Group klassida boshqa FOREIGN KEY yo'q bo'lsa ham,
aniqlik uchun <code>foreign_keys=</code> yozish yaxshi amaliyot hisoblanadi.</p>

<h3>Munosabatni tanlashda xatolik: qachon relationship() ORTIQCHA</h3>
<p>Har bir FOREIGN KEY uchun relationship() yozish shart emas. Agar Python
kodida hech qachon <code>lesson.course</code> orqali navigatsiya qilinmasa
(faqat <code>lesson.course_id</code> qiymati kifoya bo'lsa), qo'shimcha
relationship() faqat keraksiz murakkablik va potensial N+1 xavfini
qo'shadi. Qoida: relationship() faqat haqiqiy navigatsiya ehtiyoji borida
qo'shiladi, "balki kerak bo'lar" degan taxmin bilan emas.</p>
""".strip()

L3_TEXT_RU = """
<h3>relationship() — атрибут Python, а НЕ колонка таблицы</h3>
<p>Самое важное понятие этого урока: <code>relationship()</code> вообще НЕ
соответствует никакой колонке. Он лишь сообщает ORM: "между этими двумя
классами есть связь через FOREIGN KEY, преврати это в навигацию Python".
Реальная связь всегда реализуется через какую-то колонку (например
<code>lesson.course_id</code>) или связующую таблицу (например
<code>student_courses</code>) — а <code>relationship()</code> лишь
"удобный путь", построенный поверх этих колонок.</p>

<h3>One-to-many: у одного курса много уроков</h3>
<p>Это самый распространённый тип связи. FOREIGN KEY всегда находится на
стороне "много": колонка <code>lessons.course_id</code> указывает, какому
курсу принадлежит каждый урок. На уровне ORM объявляется в обе стороны:
<code>Course.lessons: Mapped[List["Lesson"]] =
relationship(back_populates="lessons")</code> и <code>Lesson.course:
Mapped["Course"] = relationship(back_populates="course")</code>.
<code>back_populates</code> связывает обе стороны друг с другом — изменив
одну сторону (например <code>lesson.course = new_course</code>), вы
автоматически обновите и другую (<code>new_course.lessons</code>), в
памяти — ещё до записи в базу.</p>

<h3>Many-to-many: связующая таблица между студентом и курсами</h3>
<p>Студент может записаться на несколько курсов, на один курс может
записаться несколько студентов — это классический many-to-many. В таком
случае FOREIGN KEY не находится напрямую ни в одной из сторон, вместо
этого нужна отдельная связующая таблица: на этой платформе это —
<code>student_courses</code> (две колонки: student_id, course_id, обе часть
PRIMARY KEY). На уровне ORM это указывается через параметр
<code>secondary="student_courses"</code> — реальный пример из
<code>app/models/user.py</code>: <code>enrolled_courses: Mapped[List["Course"]]
= relationship("Course", secondary="student_courses",
back_populates="students", lazy="selectin")</code>.</p>

<h3>cascade — что делать со связанными строками</h3>
<p><code>cascade="all, delete-orphan"</code> определяет, что произойдёт с
дочерними строками при удалении родительского объекта (или при исключении
дочернего из списка). На этой платформе связь <code>Student.projects</code>
объявлена именно с этим cascade: при удалении студента удаляются и все его
проекты (чтобы не оставались "осиротевшие" — orphan — строки). Это похоже
на <code>ON DELETE CASCADE</code> на уровне базы, но есть важная разница:
<code>ondelete="CASCADE"</code> в FOREIGN KEY работает в самой базе (даже
без ORM), а <code>cascade=</code> работает только внутри ORM Session, на
уровне Python. Оба могут понадобиться одновременно — один как сеть
безопасности, другой для графа объектов Python.</p>

<h3>lazy — когда загружается связь</h3>
<p><code>lazy="selectin"</code> — связь загружается сразу после основного
объекта отдельным (но эффективным, через IN(...)) запросом. На этой
платформе именно так помечены <code>Student.groups</code> и
<code>Student.enrolled_courses</code> — потому что эти данные нужны почти
всегда. Другие значения <code>lazy</code> (по умолчанию "select", "joined",
"subquery") и разница между ними — тема следующего урока (урок 5: Eager
против Lazy Loading).</p>

<h3>uselist=False — связь one-to-one</h3>
<p>Иногда связь должна быть не списком, а единственным объектом: у одного
студента есть одна запись Ranking. На этой платформе:
<code>ranking: Mapped[Optional["Ranking"]] = relationship("Ranking",
back_populates="student", uselist=False, cascade="all, delete-orphan")</code>
— <code>uselist=False</code> сообщает ORM: "это не List, а единственный
объект (или None)".</p>

<h3>Self-referential связь и уточнение через foreign_keys=</h3>
<p>Иногда класс ссылается сам на себя — например
<code>Course.prerequisite_course_id</code> сам ссылается на
<code>courses.id</code> (курс 107 указывает курс 98, курс 98 указывает курс
41 как prerequisite). В таких случаях SQLAlchemy может не суметь
автоматически определить, какой FOREIGN KEY использовать, если в одном
классе несколько FOREIGN KEY указывают на одну и ту же таблицу — тогда
нужно явно указать через <code>relationship(..., foreign_keys=[Course.prerequisite_course_id])</code>.
То же самое в примере <code>Group.teacher</code>: <code>teacher_id</code>
тоже ссылается на таблицу <code>students</code>, и хотя в классе Group
больше нет других FOREIGN KEY, для ясности хорошей практикой считается
всё равно писать <code>foreign_keys=</code>.</p>

<h3>Ошибка выбора связи: когда relationship() ИЗЛИШЕН</h3>
<p>Не для каждого FOREIGN KEY обязательно писать relationship(). Если в
коде Python никогда не используется навигация через <code>lesson.course</code>
(достаточно только значения <code>lesson.course_id</code>), лишний
relationship() добавляет только ненужную сложность и потенциальный риск
N+1. Правило: relationship() добавляется только при реальной потребности
в навигации, а не по предположению "может понадобиться".</p>
""".strip()

L3_CODE = """
# ============================================================
# 1) One-to-many — Course <-> Lesson, ikki tomonlama back_populates
# ============================================================
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))

    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))

    course: Mapped["Course"] = relationship(back_populates="lessons")


# back_populates ikki tomonni xotirada sinxronlaydi — hali commit qilinmasdan:
new_lesson = Lesson(title="Yangi dars")
course = Course(title="Test kurs")
new_lesson.course = course
assert new_lesson in course.lessons  # avtomatik — Python darajasida, bazaga tegmasdan

# ============================================================
# 2) Many-to-many — Student <-> Course, bog'lovchi jadval orqali
#    (app/models/user.py'dagi HAQIQIY yondashuv, soddalashtirilgan)
# ============================================================
student_courses = Table(
    "student_courses", Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # HAQIQIY misol: app/models/user.py'dagi Student.enrolled_courses
    enrolled_courses: Mapped[List["Course"]] = relationship(
        "Course", secondary=student_courses, back_populates="students", lazy="selectin"
    )


# Course klassiga mos qarshi tomonni qo'shamiz:
Course.students = relationship(
    "Student", secondary=student_courses, back_populates="enrolled_courses", lazy="selectin"
)

# Foydalanish — hech qanday JOIN yozilmaydi, faqat navigatsiya:
# student = (await db.execute(select(Student).where(Student.id == 7))).scalar_one()
# for c in student.enrolled_courses:
#     print(c.title)

# ============================================================
# 3) cascade="all, delete-orphan" — Student.projects HAQIQIY misoli
# ============================================================
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))


Student.projects = relationship(
    "Project", back_populates="student", cascade="all, delete-orphan"
)
# Talaba o'chirilsa (yoki student.projects.remove(p) qilinsa va commit
# bo'lsa) — bog'liq Project qatorlari ORM darajasida ham o'chadi.
# ondelete="CASCADE" — bazaning o'zida (ORM'siz ham) himoya beradi.
# cascade="all, delete-orphan" — Python Session darajasida, "yetim" obyekt
# qolib ketmasligini kafolatlaydi (masalan ro'yxatdan olib tashlanganda).

# ============================================================
# 4) uselist=False — one-to-one, Student.ranking HAQIQIY misoli
# ============================================================
class Ranking(Base):
    __tablename__ = "rankings"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    position: Mapped[int] = mapped_column(Integer)


Student.ranking = relationship(
    "Ranking", back_populates="student", uselist=False, cascade="all, delete-orphan"
)
# student.ranking -> bitta Ranking obyekti yoki None (RO'YXAT emas)

# ============================================================
# 5) Self-referential munosabat — Course.prerequisite_course_id
#    (41 <- 98 <- 107 <- bu kurs zanjiri, haqiqiy misol)
# ============================================================
class CourseWithPrereq(Base):
    __tablename__ = "courses_v2"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    prerequisite_course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses_v2.id", ondelete="SET NULL"), nullable=True
    )
    # foreign_keys= — SQLAlchemy'ga AYNAN qaysi ustun ishlatilishini aytadi,
    # bir xil jadvalga bir nechta FOREIGN KEY bo'lganda bu shart bo'lib qoladi:
    prerequisite: Mapped[Optional["CourseWithPrereq"]] = relationship(
        "CourseWithPrereq", remote_side=[id], foreign_keys=[prerequisite_course_id]
    )

# 107-kursning prerequisite'i 98, 98-ning prerequisite'i 41:
# course_107.prerequisite  -> course_98  (obyekt, ID emas)
# course_107.prerequisite.prerequisite -> course_41

# ============================================================
# 6) secondary= yetarli bo'lmagan holat — bog'lovchi jadvalda qo'shimcha
#    ma'lumot kerak bo'lganda
# ============================================================
# Agar review_helpful_votes uchun (capstone'da ko'ramiz) ovozning
# created_at vaqtini ham saqlash kerak bo'lsa, oddiy secondary= jadval
# yetarli emas — u bog'lovchi jadvalning o'z ustunlariga kirish imkonini
# bermaydi. Bunday holda bog'lovchi jadval TO'LIQ model sifatida, ikkita
# relationship() bilan yoziladi:
class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes_v2"
    review_id: Mapped[int] = mapped_column(ForeignKey("course_reviews.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Endi nafaqat "kim ovoz bergani", balki "qachon" ekanini ham bilish
    # mumkin — bog'lovchi Table() bilan secondary= bunday imkoniyat bermaydi.
""".strip()

L3_CODE_RU = """
# ============================================================
# 1) One-to-many — Course <-> Lesson, двусторонний back_populates
# ============================================================
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))

    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))

    course: Mapped["Course"] = relationship(back_populates="lessons")


# back_populates синхронизирует обе стороны в памяти — ещё до commit:
new_lesson = Lesson(title="Новый урок")
course = Course(title="Тестовый курс")
new_lesson.course = course
assert new_lesson in course.lessons  # автоматически — на уровне Python, без обращения к базе

# ============================================================
# 2) Many-to-many — Student <-> Course, через связующую таблицу
#    (упрощено из РЕАЛЬНОГО подхода app/models/user.py)
# ============================================================
student_courses = Table(
    "student_courses", Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # РЕАЛЬНЫЙ пример: Student.enrolled_courses из app/models/user.py
    enrolled_courses: Mapped[List["Course"]] = relationship(
        "Course", secondary=student_courses, back_populates="students", lazy="selectin"
    )


# Добавляем обратную сторону в класс Course:
Course.students = relationship(
    "Student", secondary=student_courses, back_populates="enrolled_courses", lazy="selectin"
)

# Использование — никакой JOIN не пишется, только навигация:
# student = (await db.execute(select(Student).where(Student.id == 7))).scalar_one()
# for c in student.enrolled_courses:
#     print(c.title)

# ============================================================
# 3) cascade="all, delete-orphan" — РЕАЛЬНЫЙ пример Student.projects
# ============================================================
class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))


Student.projects = relationship(
    "Project", back_populates="student", cascade="all, delete-orphan"
)
# При удалении студента (или если student.projects.remove(p) и commit) —
# связанные строки Project удаляются и на уровне ORM.
# ondelete="CASCADE" — защита в самой базе (даже без ORM).
# cascade="all, delete-orphan" — на уровне Python Session, гарантирует
# отсутствие "осиротевших" объектов (например при удалении из списка).

# ============================================================
# 4) uselist=False — one-to-one, РЕАЛЬНЫЙ пример Student.ranking
# ============================================================
class Ranking(Base):
    __tablename__ = "rankings"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    position: Mapped[int] = mapped_column(Integer)


Student.ranking = relationship(
    "Ranking", back_populates="student", uselist=False, cascade="all, delete-orphan"
)
# student.ranking -> один объект Ranking или None (НЕ список)

# ============================================================
# 5) Self-referential связь — Course.prerequisite_course_id
#    (цепочка 41 <- 98 <- 107 <- этот курс, реальный пример)
# ============================================================
class CourseWithPrereq(Base):
    __tablename__ = "courses_v2"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    prerequisite_course_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("courses_v2.id", ondelete="SET NULL"), nullable=True
    )
    # foreign_keys= — сообщает SQLAlchemy ТОЧНО какую колонку использовать,
    # это обязательно, когда в одной таблице несколько FOREIGN KEY:
    prerequisite: Mapped[Optional["CourseWithPrereq"]] = relationship(
        "CourseWithPrereq", remote_side=[id], foreign_keys=[prerequisite_course_id]
    )

# У курса 107 prerequisite — курс 98, у курса 98 prerequisite — курс 41:
# course_107.prerequisite  -> course_98  (объект, а не ID)
# course_107.prerequisite.prerequisite -> course_41

# ============================================================
# 6) Реальный пример secondary= с дополнительными данными в связующей
#    таблице — когда простого secondary= уже недостаточно
# ============================================================
# Если для review_helpful_votes (увидим в capstone) нужно хранить ещё и
# created_at голоса, простой secondary= таблица не подходит — она не
# даёт доступа к собственным колонкам связующей таблицы. Тогда связующая
# таблица оформляется как ПОЛНОЦЕННАЯ модель с двумя relationship():
class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes_v2"
    review_id: Mapped[int] = mapped_column(ForeignKey("course_reviews.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Теперь можно узнать не только "кто голосовал", но и "когда" —
    # secondary= со связующей Table() такой возможности не даёт.
""".strip()

L3_TASK = {
    "task_title": "Group <-> Student munosabatlarini modellashtirish",
    "task_title_ru": "Смоделируйте связи Group <-> Student",
    "task_description": (
        "Ushbu platformaning haqiqiy Group va Student modellariga asoslanib, "
        "quyidagi ikkala munosabatni yozing: (1) Group.teacher — bitta guruhning "
        "bitta (ixtiyoriy) o'qituvchisi, one-to-many'ning 'bir' tomoni sifatida "
        "Student'ga ishora qiladi; (2) Group.students <-> Student.groups — "
        "many-to-many, student_groups bog'lovchi jadvali orqali. Har ikkala "
        "tomon uchun ham to'g'ri back_populates/secondary yozing."
    ),
    "task_description_ru": (
        "Основываясь на реальных моделях Group и Student этой платформы, "
        "напишите обе следующие связи: (1) Group.teacher — один (необязательный) "
        "учитель группы, ссылающийся на Student как сторона 'один' в "
        "one-to-many; (2) Group.students <-> Student.groups — many-to-many "
        "через связующую таблицу student_groups. Для обеих сторон правильно "
        "укажите back_populates/secondary."
    ),
    "task_requirements": (
        "1) teacher_id: Mapped[Optional[int]] ForeignKey('students.id', "
        "ondelete='SET NULL'). 2) Group.teacher relationship() (uselist kerak "
        "emas — bu allaqachon yagona). 3) students_groups Table() Core "
        "darajasida. 4) Group.students va Student.groups ikkalasi "
        "secondary= va back_populates= bilan."
    ),
    "task_requirements_ru": (
        "1) teacher_id: Mapped[Optional[int]] ForeignKey('students.id', "
        "ondelete='SET NULL'). 2) relationship() для Group.teacher (uselist не "
        "нужен — это уже единственное значение). 3) Table() student_groups на "
        "уровне Core. 4) Group.students и Student.groups оба с secondary= и "
        "back_populates=."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM, PostgreSQL",
    "task_deadline_days": 5,
}

L3_SAMPLE = {
    "title": "Namuna: Group — bir vaqtda one-to-many va many-to-many",
    "description": "Group.teacher (one-to-many'ning 'bir' tomoni) va Group.students <-> Student.groups (many-to-many) bitta faylda.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "group_relationships.py",
            "language": "python",
            "code": (
                "from typing import List, Optional\n"
                "from sqlalchemy import String, Integer, ForeignKey, Table, Column\n"
                "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship\n\n\n"
                "class Base(DeclarativeBase):\n"
                "    pass\n\n\n"
                "student_groups = Table(\n"
                "    \"student_groups\", Base.metadata,\n"
                "    Column(\"student_id\", ForeignKey(\"students.id\", ondelete=\"CASCADE\"), primary_key=True),\n"
                "    Column(\"group_id\", ForeignKey(\"groups.id\", ondelete=\"CASCADE\"), primary_key=True),\n"
                ")\n\n\n"
                "class Student(Base):\n"
                "    __tablename__ = \"students\"\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    username: Mapped[str] = mapped_column(String(50), unique=True)\n\n"
                "    groups: Mapped[List[\"Group\"]] = relationship(\n"
                "        \"Group\", secondary=student_groups, back_populates=\"students\", lazy=\"selectin\"\n"
                "    )\n\n\n"
                "class Group(Base):\n"
                "    __tablename__ = \"groups\"\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    name: Mapped[str] = mapped_column(String(100), unique=True)\n\n"
                "    # one-to-many'ning 'bir' tomoni: bitta (ixtiyoriy) o'qituvchi\n"
                "    teacher_id: Mapped[Optional[int]] = mapped_column(\n"
                "        Integer, ForeignKey(\"students.id\", ondelete=\"SET NULL\"), nullable=True\n"
                "    )\n"
                "    teacher: Mapped[Optional[\"Student\"]] = relationship(\"Student\", foreign_keys=[teacher_id])\n\n"
                "    # many-to-many: guruhdagi barcha talabalar\n"
                "    students: Mapped[List[\"Student\"]] = relationship(\n"
                "        \"Student\", secondary=student_groups, back_populates=\"groups\", lazy=\"selectin\"\n"
                "    )\n"
            ),
        },
    ],
}

L3_EXERCISES = [
    {
        "title": "relationship() nimaga mos keladi?",
        "title_ru": "Чему соответствует relationship()?",
        "description": "relationship() atributi jadvalda qanday elementga mos keladi?",
        "description_ru": "Какому элементу таблицы соответствует атрибут relationship()?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech qanday ustunga — bu faqat Python navigatsiyasi",
            "Har doim yangi ustun sifatida saqlanadi",
            "Faqat many-to-many'da ustun bo'ladi",
            "U har doim indeks yaratadi",
        ],
        "options_ru": [
            "Ни одной колонке — это только навигация Python",
            "Всегда сохраняется как новая колонка",
            "Становится колонкой только в many-to-many",
            "Он всегда создаёт индекс",
        ],
        "correct_answers": "A",
        "hint": "Haqiqiy bog'lanish FOREIGN KEY yoki bog'lovchi jadval orqali, relationship() esa ustiga qurilgan qulaylik.",
        "hint_ru": "Реальная связь через FOREIGN KEY или связующую таблицу, а relationship() — удобство поверх неё.",
        "explanation": "relationship() bazada hech qanday ustun yaratmaydi — u faqat ORM'ga mavjud FOREIGN KEY orqali qanday navigatsiya qilishni aytadi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Munosabat turini aniqlang",
        "title_ru": "Определите тип связи",
        "description": "secondary= parametri odatda qaysi munosabat turida ishlatiladi?",
        "description_ru": "В каком типе связи обычно используется параметр secondary=?",
        "exercise_type": "multiple_choice",
        "options": ["many-to-many", "one-to-many", "one-to-one", "self-referential"],
        "options_ru": ["many-to-many", "one-to-many", "one-to-one", "self-referential"],
        "correct_answers": "A",
        "is_multiple_select": False,
        "hint": "Bog'lovchi jadval ikkita ko'p tomon orasida ishlatiladi.",
        "hint_ru": "Связующая таблица используется между двумя сторонами 'много'.",
        "explanation": "secondary= bog'lovchi jadval orqali many-to-many munosabatni bildiradi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "cascade qadamlarini tartiblang",
        "title_ru": "Расположите шаги cascade по порядку",
        "description": "cascade='all, delete-orphan' bilan talaba o'chirilganda sodir bo'ladigan voqealar ketma-ketligini joylashtiring.",
        "description_ru": "Расположите последовательность событий при удалении студента с cascade='all, delete-orphan'.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "db.delete(student) chaqiriladi",
            "ORM student.projects ro'yxatini tekshiradi",
            "Har bir bog'liq Project ham o'chirish uchun belgilanadi",
            "await db.commit() — barchasi bitta tranzaksiyada o'chadi",
        ],
        "drag_items_ru": [
            "Вызывается db.delete(student)",
            "ORM проверяет список student.projects",
            "Каждый связанный Project также помечается на удаление",
            "await db.commit() — всё удаляется в одной транзакции",
        ],
        "correct_order": [
            "db.delete(student) chaqiriladi",
            "ORM student.projects ro'yxatini tekshiradi",
            "Har bir bog'liq Project ham o'chirish uchun belgilanadi",
            "await db.commit() — barchasi bitta tranzaksiyada o'chadi",
        ],
        "hint": "Avval delete chaqiriladi, keyin ORM munosabatni tekshiradi, keyin commit bilan hammasi bajariladi.",
        "hint_ru": "Сначала вызывается delete, потом ORM проверяет связь, затем всё выполняется при commit.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 4 — ORM orqali so'rovlar: filter, join, select()
# ---------------------------------------------------------------------------

L4_TEXT = """
<h3>select() — 107-kursdagi SELECT'ning Python ifodasi</h3>
<p>ORM'da har bir so'rov <code>select()</code> funksiyasidan boshlanadi —
bu 107-kursda yozgan <code>SELECT ... FROM ... WHERE ...</code>'ning
to'g'ridan-to'g'ri Python ifodasi. Farq shundaki, <code>select(Lesson)</code>
"SELECT * FROM lessons" emas — bu "Lesson klassining barcha ustunlarini
tanlab, natijani Lesson obyektiga aylantir" degani. Bu platformaning haqiqiy
<code>app/services/lesson_service.py</code> faylida bu naqsh doimiy
ishlatiladi: <code>select(Lesson).where(Lesson.course_id == course_id,
Lesson.is_active == True).order_by(Lesson.order)</code>.</p>

<h3>.where() — bir nechta shart, AND va OR</h3>
<p><code>.where()</code>ga vergul bilan ajratilgan bir nechta shart berish —
ularni AND bilan bog'lash bilan bir xil (yuqoridagi misolda
<code>course_id == ...</code> VA <code>is_active == True</code>). OR uchun
esa <code>or_()</code> funksiyasi kerak: <code>or_(Lesson.order == 0,
Lesson.order == 1)</code>. Murakkab shartlar uchun <code>and_()</code> va
<code>or_()</code> birlashtiriladi — bu 107-kursdagi qavslangan
<code>WHERE (a AND b) OR (c AND d)</code>'ning Python ekvivalenti.</p>

<h3>.join() — munosabatdan foydalanib yoki ustunlar orqali qo'lda</h3>
<p>ORM'da join ikki yo'l bilan yozilishi mumkin: (1) <code>relationship()</code>
orqali avtomatik — <code>select(Lesson).join(Lesson.course)</code>, ORM
FOREIGN KEY'ni o'zi topadi; (2) qo'lda, ustunlarni ko'rsatib —
<code>select(Lesson).join(Course, Course.id == Lesson.course_id)</code>. Ikkinchi
usul relationship() bo'lmagan yoki murakkab (bir nechta shart bilan)
join'lar uchun kerak bo'ladi. Ikkalasi ham xuddi 107-kursdagi
<code>JOIN courses ON courses.id = lessons.course_id</code>'ni hosil
qiladi.</p>

<h3>order_by, limit, offset — sahifalash (pagination)</h3>
<p>107-kursda o'rgangan <code>ORDER BY ... LIMIT ... OFFSET ...</code>
to'g'ridan-to'g'ri ko'chiriladi: <code>.order_by(Lesson.order).limit(10).offset(20)</code>.
Muhim eslatma: <code>LIMIT</code>siz so'rov production'da xavfli — agar
jadvalda million qator bo'lsa, ORM ularning barchasini Python obyektiga
aylantirishga urinadi va xotirani tugatib qo'yishi mumkin (11-darsda bu
"over-fetching" muammosi sifatida chuqurroq ko'riladi).</p>

<h3>scalar_one, scalar_one_or_none, scalars().all() — natijani olish shakllari</h3>
<p>So'rov natijasini olishning bir nechta usuli bor, va noto'g'ri tanlash
aniq xatoga olib keladi: <code>scalar_one()</code> — aniq bitta natija
kutiladi, topilmasa yoki bir nechta topilsa xato beradi (masalan ID bo'yicha
qidiruvda). <code>scalar_one_or_none()</code> — bitta yoki hech nima
kutiladi (masalan ixtiyoriy qidiruv). <code>scalars().all()</code> — bir
nechta natija kutiladi, ro'yxat qaytadi. <code>.first()</code> esa "birinchi
topilganini olib, qolganini e'tiborsiz qoldir" — lekin bu ko'pincha noto'g'ri
tanlov, chunki u kutilmagan takrorlanishlarni yashiradi.</p>

<h3>func.count(), func.avg() — agregatsiya ORM darajasida</h3>
<p>107-kursdagi <code>COUNT()</code>, <code>AVG()</code>, <code>SUM()</code>
funksiyalari <code>sqlalchemy.func</code> orqali chaqiriladi:
<code>select(func.count(Lesson.id)).where(Lesson.course_id == 41)</code>. Bu
Python funksiyasi emas — u SQL'ga tarjima qilinadigan maxsus obyekt, xuddi
<code>select()</code>ning o'zi kabi.</p>

<h3>ilike, in_(), not_() — matn qidiruvi va ro'yxat bilan solishtirish</h3>
<p>107-kursda o'rgangan <code>ILIKE '%so'z%'</code> ORM'da
<code>Course.title.ilike("%SQL%")</code> shaklida yoziladi. Bir nechta
qiymatdan birortasiga tenglikni tekshirish uchun
<code>Course.id.in_([41, 98, 107])</code> — bu 107-kursdagi
<code>WHERE id IN (41, 98, 107)</code>'ga mos keladi. Inkor uchun esa
<code>~Lesson.is_active</code> (tilda belgisi) yoki <code>not_(Lesson.is_active)</code>
ishlatiladi. Bu operatorlarning barchasi Python operatorlari EMAS — ular
<code>Column</code> klassida qayta belgilangan (overload qilingan) maxsus
metodlar, shuning uchun <code>Lesson.id == 5</code> aslida taqqoslash emas,
SQL ifodasi hosil qiluvchi chaqiruv.</p>

<h3>Subquery va exists() — ichma-ich so'rovlar</h3>
<p>"Hech qanday namunasi yo'q darslarni top" kabi savol subquery talab
qiladi. ORM'da bu <code>~select(LessonSample.id).where(LessonSample.lesson_id
== Lesson.id).exists()</code> shaklida yoziladi — 107-kursdagi
<code>WHERE NOT EXISTS (SELECT 1 FROM lesson_samples WHERE lesson_id = lessons.id)</code>
ning aynan o'zi, faqat Python sintaksisida. <code>.exists()</code> —
subquery natijasini "bor/yo'q" mantiqiy qiymatga aylantiradi, butun
natijani yuklamasdan.</p>
""".strip()

L4_TEXT_RU = """
<h3>select() — выражение Python для SELECT из курса 107</h3>
<p>В ORM каждый запрос начинается с функции <code>select()</code> — это
прямое выражение на Python того <code>SELECT ... FROM ... WHERE ...</code>,
который вы писали в курсе 107. Разница в том, что <code>select(Lesson)</code>
— это не "SELECT * FROM lessons" — это "выбери все колонки класса Lesson и
преврати результат в объект Lesson". В реальном файле
<code>app/services/lesson_service.py</code> этой платформы этот паттерн
используется постоянно: <code>select(Lesson).where(Lesson.course_id ==
course_id, Lesson.is_active == True).order_by(Lesson.order)</code>.</p>

<h3>.where() — несколько условий, AND и OR</h3>
<p>Передача нескольких условий в <code>.where()</code> через запятую
равносильна их соединению через AND (в примере выше — <code>course_id ==
...</code> И <code>is_active == True</code>). Для OR нужна функция
<code>or_()</code>: <code>or_(Lesson.order == 0, Lesson.order == 1)</code>.
Для сложных условий <code>and_()</code> и <code>or_()</code> объединяются —
это Python-эквивалент скобочного <code>WHERE (a AND b) OR (c AND d)</code>
из курса 107.</p>

<h3>.join() — через связь или вручную по колонкам</h3>
<p>В ORM join можно написать двумя способами: (1) автоматически через
<code>relationship()</code> — <code>select(Lesson).join(Lesson.course)</code>,
ORM сам находит FOREIGN KEY; (2) вручную, указав колонки —
<code>select(Lesson).join(Course, Course.id == Lesson.course_id)</code>.
Второй способ нужен для join без relationship() или для сложных join с
несколькими условиями. Оба варианта дают тот же
<code>JOIN courses ON courses.id = lessons.course_id</code>, что и в курсе
107.</p>

<h3>order_by, limit, offset — пагинация</h3>
<p>Изученный в курсе 107 <code>ORDER BY ... LIMIT ... OFFSET ...</code>
переносится напрямую: <code>.order_by(Lesson.order).limit(10).offset(20)</code>.
Важное замечание: запрос без <code>LIMIT</code> опасен в production — если
в таблице миллион строк, ORM попытается превратить их все в объекты Python
и может исчерпать память (подробнее эта проблема "over-fetching"
рассматривается в уроке 11).</p>

<h3>scalar_one, scalar_one_or_none, scalars().all() — формы получения результата</h3>
<p>Существует несколько способов получить результат запроса, и неверный
выбор приводит к явной ошибке: <code>scalar_one()</code> — ожидается ровно
один результат, если не найден или найдено несколько — выдаётся ошибка
(например при поиске по ID). <code>scalar_one_or_none()</code> — ожидается
один или ни одного (например при необязательном поиске).
<code>scalars().all()</code> — ожидается несколько результатов,
возвращается список. <code>.first()</code> же означает "взять первый
найденный, остальные проигнорировать" — но это часто неверный выбор,
поскольку скрывает неожиданные дубликаты.</p>

<h3>func.count(), func.avg() — агрегация на уровне ORM</h3>
<p>Функции <code>COUNT()</code>, <code>AVG()</code>, <code>SUM()</code> из
курса 107 вызываются через <code>sqlalchemy.func</code>:
<code>select(func.count(Lesson.id)).where(Lesson.course_id == 41)</code>.
Это не функция Python — это специальный объект, переводимый в SQL, точно
как и сам <code>select()</code>.</p>

<h3>ilike, in_(), not_() — текстовый поиск и сравнение со списком</h3>
<p>Изученный в курсе 107 <code>ILIKE '%слово%'</code> в ORM пишется как
<code>Course.title.ilike("%SQL%")</code>. Для проверки принадлежности
одному из нескольких значений — <code>Course.id.in_([41, 98, 107])</code>
— это соответствует <code>WHERE id IN (41, 98, 107)</code> из курса 107.
Для отрицания используется <code>~Lesson.is_active</code> (символ тильды)
или <code>not_(Lesson.is_active)</code>. Все эти операторы — НЕ обычные
операторы Python, они переопределены (overload) в классе <code>Column</code>
как специальные методы, поэтому <code>Lesson.id == 5</code> на самом деле
не сравнение, а вызов, порождающий SQL-выражение.</p>

<h3>Subquery и exists() — вложенные запросы</h3>
<p>Вопрос вроде "найти уроки без примера" требует subquery. В ORM это
пишется как <code>~select(LessonSample.id).where(LessonSample.lesson_id ==
Lesson.id).exists()</code> — это в точности
<code>WHERE NOT EXISTS (SELECT 1 FROM lesson_samples WHERE lesson_id = lessons.id)</code>
из курса 107, только на синтаксисе Python. <code>.exists()</code>
превращает результат subquery в логическое значение "есть/нет", не
загружая весь результат целиком.</p>
""".strip()

L4_CODE = """
# ============================================================
# HAQIQIY misol: app/services/lesson_service.py'dagi get_lessons_by_course
# (soddalashtirilgan, lekin naqsh o'zgarmagan)
# ============================================================
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional


async def get_lessons_by_course(db, course_id: int) -> List["Lesson"]:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id, Lesson.is_active == True)  # AND — vergul bilan
        .order_by(Lesson.order)
    )
    return result.scalars().all()   # bir nechta natija -> ro'yxat


# ============================================================
# 1) .where() — AND (vergul) va OR (or_())
# ============================================================
and_stmt = select(Lesson).where(Lesson.course_id == 41, Lesson.points_reward >= 15)
or_stmt = select(Lesson).where(or_(Lesson.order == 0, Lesson.order == 1))
combined_stmt = select(Lesson).where(
    and_(Lesson.course_id == 41, or_(Lesson.order == 0, Lesson.points_reward > 20))
)
# 107-kursdagi: WHERE course_id = 41 AND (order = 0 OR points_reward > 20)

# ============================================================
# 2) .join() — ikki usul
# ============================================================
# (a) relationship() orqali — ORM FOREIGN KEY'ni o'zi topadi:
join_via_rel = select(Lesson).join(Lesson.course).where(Course.title.ilike("%SQL%"))

# (b) qo'lda, ustun orqali — relationship() bo'lmasa yoki murakkab shart kerak bo'lsa:
join_manual = select(Lesson).join(Course, Course.id == Lesson.course_id).where(Course.id == 41)

# ============================================================
# 3) order_by + limit + offset — sahifalash
# ============================================================
PAGE_SIZE = 10
page_2 = (
    select(Lesson)
    .where(Lesson.course_id == 41)
    .order_by(Lesson.order)
    .limit(PAGE_SIZE)
    .offset(PAGE_SIZE * 1)   # 2-sahifa
)
# LIMIT'siz so'rov — production'da xavfli: agar jadvalda 1 000 000 qator
# bo'lsa, ORM ularning HAMMASINI Python obyektiga aylantirishga urinadi.

# ============================================================
# 4) Natijani olish shakllari — noto'g'ri tanlov aniq xatoga olib keladi
# ============================================================
# Aniq bitta natija kutilganda (masalan ID bo'yicha):
one_lesson = (await db.execute(select(Lesson).where(Lesson.id == 5))).scalar_one()
# -> topilmasa: NoResultFound, bir nechtasi topilsa: MultipleResultsFound

# Bitta yoki hech nima (masalan ixtiyoriy qidiruv):
maybe_lesson = (await db.execute(select(Lesson).where(Lesson.id == 999))).scalar_one_or_none()
# -> topilmasa: None (xato emas)

# Bir nechta natija kutilganda:
all_lessons = (await db.execute(select(Lesson).where(Lesson.course_id == 41))).scalars().all()

# ============================================================
# 5) func.count / func.avg — agregatsiya
# ============================================================
lesson_count = (await db.execute(
    select(func.count(Lesson.id)).where(Lesson.course_id == 41)
)).scalar_one()

avg_points = (await db.execute(
    select(func.avg(Lesson.points_reward)).where(Lesson.course_id == 41)
)).scalar_one()

print(f"Kurs 41: {lesson_count} ta dars, o'rtacha {avg_points:.1f} ball")

# ============================================================
# 6) ilike / in_ / not_ — matn qidiruvi va ro'yxat bilan solishtirish
# ============================================================
text_search = select(Course).where(Course.title.ilike("%SQL%"))
id_in_list = select(Course).where(Course.id.in_([41, 98, 107]))
negation = select(Lesson).where(~Lesson.is_active)   # yoki not_(Lesson.is_active)

# ============================================================
# 7) exists() — "hech qanday namunasi yo'q darslarni top"
# ============================================================
from sqlalchemy import exists

no_sample_stmt = select(Lesson).where(
    ~exists().where(LessonSample.lesson_id == Lesson.id)
)
# 107-kursdagi: WHERE NOT EXISTS (SELECT 1 FROM lesson_samples WHERE lesson_id = lessons.id)
# .exists() natijani "bor/yo'q"ga aylantiradi — bazaga butun subquery natijasini
# emas, faqat mantiqiy javobni so'raydi.

# ============================================================
# 8) To'liq funksiya — filtr, join, sahifalash va agregatsiyani birlashtiradi
# ============================================================
async def list_lessons_with_progress(db, course_id: int, student_id: int, page: int = 1, page_size: int = 10):
    \"\"\"Kurs darslari ro'yxati, har bir dars uchun shu talaba nechta
    mashqni to'g'ri yechganini ko'rsatuvchi — kurs sahifasida tipik
    so'rov.\"\"\"
    completed_subq = (
        select(func.count(ExerciseAttempt.id))
        .where(
            ExerciseAttempt.student_id == student_id,
            ExerciseAttempt.exercise_id.in_(
                select(Exercise.id).where(Exercise.lesson_id == Lesson.id)
            ),
            ExerciseAttempt.is_correct == True,
        )
        .correlate(Lesson)
        .scalar_subquery()
    )
    stmt = (
        select(Lesson.id, Lesson.title, Lesson.order, completed_subq.label("completed_count"))
        .where(Lesson.course_id == course_id, Lesson.is_active == True)
        .order_by(Lesson.order)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    return (await db.execute(stmt)).all()
    # Har bir qator: (id, title, order, completed_count) — Lesson obyekti
    # EMAS, Row — chunki bu yerda faqat ro'yxat ko'rinishi uchun kerakli
    # yassi ma'lumot kifoya (11-darsdagi over-fetching mavzusiga bog'liq).
""".strip()

L4_CODE_RU = """
# ============================================================
# РЕАЛЬНЫЙ пример: get_lessons_by_course из app/services/lesson_service.py
# (упрощено, но паттерн не изменён)
# ============================================================
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional


async def get_lessons_by_course(db, course_id: int) -> List["Lesson"]:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id, Lesson.is_active == True)  # AND — через запятую
        .order_by(Lesson.order)
    )
    return result.scalars().all()   # несколько результатов -> список


# ============================================================
# 1) .where() — AND (запятая) и OR (or_())
# ============================================================
and_stmt = select(Lesson).where(Lesson.course_id == 41, Lesson.points_reward >= 15)
or_stmt = select(Lesson).where(or_(Lesson.order == 0, Lesson.order == 1))
combined_stmt = select(Lesson).where(
    and_(Lesson.course_id == 41, or_(Lesson.order == 0, Lesson.points_reward > 20))
)
# Из курса 107: WHERE course_id = 41 AND (order = 0 OR points_reward > 20)

# ============================================================
# 2) .join() — два способа
# ============================================================
# (a) через relationship() — ORM сам находит FOREIGN KEY:
join_via_rel = select(Lesson).join(Lesson.course).where(Course.title.ilike("%SQL%"))

# (b) вручную, через колонки — когда нет relationship() или нужно сложное условие:
join_manual = select(Lesson).join(Course, Course.id == Lesson.course_id).where(Course.id == 41)

# ============================================================
# 3) order_by + limit + offset — пагинация
# ============================================================
PAGE_SIZE = 10
page_2 = (
    select(Lesson)
    .where(Lesson.course_id == 41)
    .order_by(Lesson.order)
    .limit(PAGE_SIZE)
    .offset(PAGE_SIZE * 1)   # 2-я страница
)
# Запрос без LIMIT опасен в production: если в таблице 1 000 000 строк,
# ORM попытается превратить их ВСЕ в объекты Python.

# ============================================================
# 4) Формы получения результата — неверный выбор ведёт к явной ошибке
# ============================================================
# Ожидается ровно один результат (например по ID):
one_lesson = (await db.execute(select(Lesson).where(Lesson.id == 5))).scalar_one()
# -> не найдено: NoResultFound, найдено несколько: MultipleResultsFound

# Один или ни одного (например при необязательном поиске):
maybe_lesson = (await db.execute(select(Lesson).where(Lesson.id == 999))).scalar_one_or_none()
# -> не найдено: None (не ошибка)

# Ожидается несколько результатов:
all_lessons = (await db.execute(select(Lesson).where(Lesson.course_id == 41))).scalars().all()

# ============================================================
# 5) func.count / func.avg — агрегация
# ============================================================
lesson_count = (await db.execute(
    select(func.count(Lesson.id)).where(Lesson.course_id == 41)
)).scalar_one()

avg_points = (await db.execute(
    select(func.avg(Lesson.points_reward)).where(Lesson.course_id == 41)
)).scalar_one()

print(f"Курс 41: {lesson_count} уроков, в среднем {avg_points:.1f} баллов")

# ============================================================
# 6) ilike / in_ / not_ — текстовый поиск и сравнение со списком
# ============================================================
text_search = select(Course).where(Course.title.ilike("%SQL%"))
id_in_list = select(Course).where(Course.id.in_([41, 98, 107]))
negation = select(Lesson).where(~Lesson.is_active)   # или not_(Lesson.is_active)

# ============================================================
# 7) exists() — "найти уроки без примера"
# ============================================================
from sqlalchemy import exists

no_sample_stmt = select(Lesson).where(
    ~exists().where(LessonSample.lesson_id == Lesson.id)
)
# Из курса 107: WHERE NOT EXISTS (SELECT 1 FROM lesson_samples WHERE lesson_id = lessons.id)
# .exists() превращает результат в "есть/нет" — от базы запрашивается не
# весь результат subquery, а только логический ответ.

# ============================================================
# 8) Полная функция — объединяет фильтры, join, пагинацию и агрегацию
# ============================================================
async def list_lessons_with_progress(db, course_id: int, student_id: int, page: int = 1, page_size: int = 10):
    \"\"\"Список уроков курса с указанием, сколько упражнений каждого урока
    уже решено данным студентом — типичный запрос для страницы курса.\"\"\"
    completed_subq = (
        select(func.count(ExerciseAttempt.id))
        .where(
            ExerciseAttempt.student_id == student_id,
            ExerciseAttempt.exercise_id.in_(
                select(Exercise.id).where(Exercise.lesson_id == Lesson.id)
            ),
            ExerciseAttempt.is_correct == True,
        )
        .correlate(Lesson)
        .scalar_subquery()
    )
    stmt = (
        select(Lesson.id, Lesson.title, Lesson.order, completed_subq.label("completed_count"))
        .where(Lesson.course_id == course_id, Lesson.is_active == True)
        .order_by(Lesson.order)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    return (await db.execute(stmt)).all()
    # Каждая строка: (id, title, order, completed_count) — не объект
    # Lesson, а Row — потому что здесь достаточно только плоских данных
    # для списка (связано с темой over-fetching из урока 11).
""".strip()

L4_TASK = {
    "task_title": "Kurslar katalogi uchun filtrlash+sahifalash funksiyasi",
    "task_title_ru": "Функция фильтрации+пагинации для каталога курсов",
    "task_description": (
        "list_courses(db, difficulty=None, category_id=None, page=1, page_size=12) "
        "funksiyasini yozing: agar difficulty berilsa — shu bo'yicha filtrlaydi, "
        "agar category_id berilsa — shu bo'yicha ham filtrlaydi (ikkalasi ham "
        "berilishi mumkin — AND bilan), natijalarni display_order bo'yicha "
        "tartiblab, page/page_size asosida LIMIT/OFFSET qo'llaydi. Qo'shimcha "
        "ravishda jami mos kelgan kurslar sonini (LIMIT'siz) qaytaring."
    ),
    "task_description_ru": (
        "Напишите функцию list_courses(db, difficulty=None, category_id=None, "
        "page=1, page_size=12): если задан difficulty — фильтрует по нему, если "
        "задан category_id — фильтрует и по нему (оба могут быть заданы "
        "одновременно — через AND), сортирует результаты по display_order, "
        "применяет LIMIT/OFFSET на основе page/page_size. Дополнительно "
        "верните общее число подходящих курсов (без LIMIT)."
    ),
    "task_requirements": (
        "1) select(Course) + shartli .where() qo'shish (faqat berilgan "
        "parametrlar uchun). 2) .order_by(Course.display_order). 3) .limit()/"
        ".offset() page asosida. 4) Alohida func.count() so'rovi jami sonni "
        "olish uchun (bir xil filtrlar bilan, lekin LIMIT'siz)."
    ),
    "task_requirements_ru": (
        "1) select(Course) + условное добавление .where() (только для "
        "заданных параметров). 2) .order_by(Course.display_order). 3) "
        ".limit()/.offset() на основе page. 4) Отдельный запрос func.count() "
        "для получения общего числа (с теми же фильтрами, но без LIMIT)."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 5,
}

L4_SAMPLE = {
    "title": "Namuna: list_courses — filtrlash, tartiblash, sahifalash",
    "description": "Ixtiyoriy filtrlar (difficulty, category_id), tartiblash va LIMIT/OFFSET sahifalashni birlashtirgan to'liq funksiya.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "list_courses.py",
            "language": "python",
            "code": (
                "from typing import Optional\n"
                "from sqlalchemy import select, func\n"
                "from sqlalchemy.ext.asyncio import AsyncSession\n\n\n"
                "async def list_courses(\n"
                "    db: AsyncSession,\n"
                "    difficulty: Optional[str] = None,\n"
                "    category_id: Optional[int] = None,\n"
                "    page: int = 1,\n"
                "    page_size: int = 12,\n"
                "):\n"
                "    base_stmt = select(Course)\n"
                "    count_stmt = select(func.count(Course.id))\n\n"
                "    # Faqat berilgan filtrlar qo'shiladi — bo'sh filtr WHERE'ga tushmaydi\n"
                "    if difficulty is not None:\n"
                "        base_stmt = base_stmt.where(Course.difficulty_level == difficulty)\n"
                "        count_stmt = count_stmt.where(Course.difficulty_level == difficulty)\n"
                "    if category_id is not None:\n"
                "        base_stmt = base_stmt.where(Course.category_id == category_id)\n"
                "        count_stmt = count_stmt.where(Course.category_id == category_id)\n\n"
                "    base_stmt = (\n"
                "        base_stmt.order_by(Course.display_order)\n"
                "        .limit(page_size)\n"
                "        .offset((page - 1) * page_size)\n"
                "    )\n\n"
                "    courses = (await db.execute(base_stmt)).scalars().all()\n"
                "    total = (await db.execute(count_stmt)).scalar_one()\n"
                "    return {\"items\": courses, \"total\": total, \"page\": page, \"page_size\": page_size}\n"
            ),
        },
    ],
}

L4_EXERCISES = [
    {
        "title": "AND vs OR",
        "title_ru": "AND против OR",
        "description": ".where(A, B) yozilsa, bu qanday mantiqiy amalga mos keladi?",
        "description_ru": "Какой логической операции соответствует .where(A, B)?",
        "exercise_type": "multiple_choice",
        "options": ["AND", "OR", "XOR", "NOT"],
        "options_ru": ["AND", "OR", "XOR", "NOT"],
        "correct_answers": "A",
        "hint": "Vergul bilan ajratilgan shartlar birlashtiriladi, ajratilmaydi.",
        "hint_ru": "Условия через запятую объединяются, а не разделяются.",
        "explanation": ".where()ga vergul bilan berilgan shartlar AND bilan bog'lanadi; OR uchun or_() kerak.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "To'g'ri natija olish usulini tanlang",
        "title_ru": "Выберите правильный способ получения результата",
        "description": "ID bo'yicha aniq bitta qatorni qidirayotganda va topilmasa xato kutilganda qaysi metod ishlatiladi?",
        "description_ru": "Какой метод используется при поиске ровно одной строки по ID, когда при отсутствии ожидается ошибка?",
        "exercise_type": "multiple_choice",
        "options": ["scalar_one()", "scalar_one_or_none()", "scalars().all()", "first()"],
        "options_ru": ["scalar_one()", "scalar_one_or_none()", "scalars().all()", "first()"],
        "correct_answers": "A",
        "hint": "Nom o'zi 'bitta' (one) kutilishini va xato berishini bildiradi.",
        "hint_ru": "Само название означает 'один' (one) и подразумевает ошибку при несоответствии.",
        "explanation": "scalar_one() aniq bitta natija kutadi — topilmasa yoki bir nechta bo'lsa xato beradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Sahifalash qadamlarini tartiblang",
        "title_ru": "Расположите шаги пагинации по порядку",
        "description": "list_courses funksiyasidagi so'rov qurilish qadamlarini to'g'ri tartibga joylashtiring.",
        "description_ru": "Расположите шаги построения запроса в функции list_courses в правильном порядке.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "select(Course) bilan boshlash",
            "Shartli .where() filtrlarini qo'shish",
            ".order_by(Course.display_order) qo'shish",
            ".limit() va .offset() qo'llash",
        ],
        "drag_items_ru": [
            "Начать с select(Course)",
            "Добавить условные фильтры .where()",
            "Добавить .order_by(Course.display_order)",
            "Применить .limit() и .offset()",
        ],
        "correct_order": [
            "select(Course) bilan boshlash",
            "Shartli .where() filtrlarini qo'shish",
            ".order_by(Course.display_order) qo'shish",
            ".limit() va .offset() qo'llash",
        ],
        "hint": "Avval nima tanlanishi, keyin qanday filtrlanishi, keyin tartibi, oxirida sahifa chegarasi.",
        "hint_ru": "Сначала что выбирается, потом как фильтруется, потом порядок, в конце границы страницы.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 5 — Eager vs Lazy Loading: N+1 muammosi qaytadan
# ---------------------------------------------------------------------------

L5_TEXT = """
<h3>107-kursdagi N+1'ni eslang — endi u ORM darajasida qanday paydo bo'ladi</h3>
<p>107-kursda N+1 muammosini SQL darajasida ko'rgan edingiz: har bir talaba
uchun alohida "uning kurslarini olib kel" so'rovi yuborilishi, natijada 1
ta talabalar so'rovi + N ta qo'shimcha so'rov. ORM'da bu muammo yashirinroq
shaklda paydo bo'ladi — chunki <code>student.courses</code>ga murojaat
qilish oddiy atributga murojaat qilishdek ko'rinadi, lekin sahna ortida u
YANGI SQL so'rovini ishga tushirishi mumkin. Bu — ORM'ning eng ko'p
tanqid qilinadigan, lekin aslida to'g'ri tushunilsa oson oldini olinadigan
muammosi.</p>

<h3>Lazy loading — sukut bo'yicha xatti-harakat</h3>
<p><code>relationship()</code>da <code>lazy=</code> ko'rsatilmasa, standart
qiymat "select" (lazy loading) bo'ladi: munosabat FAQAT unga birinchi marta
murojaat qilinganda yuklanadi, alohida so'rov bilan. Agar siklda 50 ta
talabaning har biri uchun <code>student.courses</code>ga murojaat qilsangiz
— 50 ta qo'shimcha SQL so'rovi yuboriladi, garchi barcha kerakli
ma'lumotni BITTA so'rovda olish mumkin bo'lsa ham. Bu — aynan N+1'ning
o'zi, faqat "select() yozmadim" degan tuyg'u bilan yashiringan holda.</p>

<h3>selectinload() — eng ko'p tavsiya etiladigan yechim</h3>
<p><code>selectinload()</code> — asosiy so'rov bilan BIRGA, lekin ALOHIDA
ikkinchi so'rov yuboradi: <code>SELECT * FROM courses WHERE id IN (1, 2, 3,
...)</code> — barcha kerakli munosabatlarni bitta IN(...) so'rovida oladi.
Natijada N+1 o'rniga har doim aniq 2 ta so'rov bo'ladi (asosiy + munosabat),
qancha qator bo'lishidan qat'iy nazar. Bu platformaning haqiqiy
<code>app/services/lesson_service.py</code> faylida bu naqsh doimiy
ishlatiladi: <code>select(Lesson).options(selectinload(Lesson.exercises),
selectinload(Lesson.files))</code>.</p>

<h3>joinedload() — bitta so'rov, lekin ehtiyot bilan</h3>
<p><code>joinedload()</code> LEFT OUTER JOIN orqali hammasini BITTA so'rovda
oladi. Bu ba'zan tezroq (bitta round-trip), lekin xavfli tomoni bor: agar
bitta talabaning 100 ta kursi bo'lsa, natija 100 marta takrorlangan talaba
ma'lumotini o'z ichiga oladi (JOIN'ning tabiati shunday) — bu "cartesian
ko'payish" deb ataladi va katta to'plamlarda tarmoq trafigini keraksiz
oshiradi. Qoida: bitta-ga-bir (one-to-one) yoki kichik ro'yxatlar uchun
joinedload, katta ro'yxatlar uchun selectinload afzal.</p>

<h3>lazy="raise" — N+1'ni ishlab chiqishda ushlab qolish</h3>
<p>Eng samarali himoya — muammoni production'da emas, development'da
topish. <code>relationship(..., lazy="raise")</code> — agar kimdir shu
munosabatga eager loading'siz murojaat qilsa, jim qolib qo'shimcha so'rov
yubormaydi, balki DARHOL xato tashlaydi. Bu — "sukut bo'yicha xavfsiz"
falsafasi: N+1 xatosi test bosqichida qattiq xato sifatida ko'rinadi,
production monitoring'da sekin so'rov sifatida emas.</p>

<h3>Qachon lazy loading aslida to'g'ri tanlov</h3>
<p>Har doim eager loading kerak emas — agar munosabatga faqat kamdan-kam
va shartli holatlarda (masalan faqat admin panelida) murojaat qilinsa,
har bir asosiy so'rovga uni majburiy qo'shish ortiqcha ma'lumotni oldindan
yuklashga (over-fetching, 11-darsda) olib keladi. Qoida oddiy: agar
munosabat DEYARLI HAR DOIM kerak bo'lsa — eager (selectinload/joinedload);
agar kamdan-kam kerak bo'lsa — lazy, lekin N+1'ga aylanib ketmasligini
tekshirish sharti bilan.</p>

<h3>N+1'ni production'da qanday sezish mumkin</h3>
<p>Agar <code>lazy="raise"</code> hamma joyda ishlatilmagan bo'lsa, N+1
production'da odatda sekinlik sifatida namoyon bo'ladi: bitta endpoint
kutilganidan 10-20 barobar ko'p vaqt oladi, lekin xato chiqarmaydi. Buni
topishning ikki asosiy yo'li: (1) <code>echo=True</code> yoki APM vositasi
(masalan Sentry, DataDog) orqali bitta so'rov davomida nechta SQL bajarilganini
sanash; (2) PostgreSQL'ning <code>pg_stat_statements</code> jadvalida bir xil
so'rov shablonining g'ayrioddiy ko'p marta takrorlanganini ko'rish (107-kursda
o'rgangan EXPLAIN ANALYZE'ga o'xshash diagnostika mantig'i). Ikkalasi ham
"bitta HTTP so'rovi uchun necha marta bir xil SQL shabloni bajarildi"
degan savolga javob beradi.</p>

<h3>contains_eager() — allaqachon JOIN qilingan ustunlarni qayta ishlatish</h3>
<p>Ba'zan siz allaqachon <code>.join()</code> yozgan bo'lasiz (masalan
filtrlash uchun), va shu JOIN natijasidan munosabatni ham to'ldirish
mumkin — bu holda <code>selectinload()</code> yoki <code>joinedload()</code>
YANA bir marta JOIN qilib, ortiqcha ish qiladi. <code>contains_eager()</code>
esa ORM'ga "bu munosabat uchun MEN ALLAQACHON join qilganman, uni qayta
so'ramay, shu natijadan foydalan" deydi — bu 11-darsda ko'radigan
"ortiqcha yuklash" (over-fetching)ning teskarisi: kamroq emas, ANIQ ROQ
so'rov.</p>
""".strip()

L5_TEXT_RU = """
<h3>Вспомните N+1 из курса 107 — теперь посмотрим, как это выглядит на уровне ORM</h3>
<p>В курсе 107 вы видели проблему N+1 на уровне SQL: для каждого студента
отправлялся отдельный запрос "получить его курсы", в итоге 1 запрос
студентов + N дополнительных запросов. В ORM эта проблема проявляется
скрытнее — потому что обращение к <code>student.courses</code> выглядит
как обычное обращение к атрибуту, но за кулисами оно может запустить НОВЫЙ
SQL-запрос. Это самая критикуемая, но при правильном понимании легко
предотвратимая проблема ORM.</p>

<h3>Lazy loading — поведение по умолчанию</h3>
<p>Если в <code>relationship()</code> не указан <code>lazy=</code>, значение
по умолчанию — "select" (lazy loading): связь загружается ТОЛЬКО при первом
обращении к ней, отдельным запросом. Если в цикле для каждого из 50
студентов обратиться к <code>student.courses</code> — отправится 50
дополнительных SQL-запросов, даже если все нужные данные можно было бы
получить ОДНИМ запросом. Это и есть N+1, только скрытый за ощущением
"я же не писал select()".</p>

<h3>selectinload() — наиболее рекомендуемое решение</h3>
<p><code>selectinload()</code> отправляет ВТОРОЙ, ОТДЕЛЬНЫЙ запрос вместе с
основным: <code>SELECT * FROM courses WHERE id IN (1, 2, 3, ...)</code> —
получает все нужные связи одним запросом IN(...). В итоге вместо N+1
всегда получается ровно 2 запроса (основной + связь), независимо от
количества строк. На этой платформе, в реальном
<code>app/services/lesson_service.py</code>, этот паттерн используется
постоянно: <code>select(Lesson).options(selectinload(Lesson.exercises),
selectinload(Lesson.files))</code>.</p>

<h3>joinedload() — один запрос, но с осторожностью</h3>
<p><code>joinedload()</code> получает всё ОДНИМ запросом через LEFT OUTER
JOIN. Иногда это быстрее (один round-trip), но есть опасная сторона: если
у одного студента 100 курсов, результат будет содержать данные студента,
повторённые 100 раз (такова природа JOIN) — это называется "декартовым
раздуванием" и излишне увеличивает сетевой трафик на больших наборах.
Правило: для one-to-one или маленьких списков — joinedload, для больших
списков — предпочтительнее selectinload.</p>

<h3>lazy="raise" — ловим N+1 ещё на этапе разработки</h3>
<p>Самая эффективная защита — находить проблему не в production, а в
разработке. <code>relationship(..., lazy="raise")</code> — если кто-то
обратится к этой связи без eager loading, ORM не промолчит и не отправит
дополнительный запрос, а НЕМЕДЛЕННО выбросит ошибку. Это философия
"безопасно по умолчанию": ошибка N+1 видна на этапе тестов как явный сбой,
а не в production-мониторинге как медленный запрос.</p>

<h3>Когда lazy loading на самом деле правильный выбор</h3>
<p>Eager loading нужен не всегда — если к связи обращаются редко и
условно (например только в админ-панели), обязательное добавление её к
каждому основному запросу приведёт к избыточной предзагрузке данных
(over-fetching, урок 11). Правило простое: если связь нужна ПОЧТИ ВСЕГДА
— eager (selectinload/joinedload); если нужна редко — lazy, но с проверкой,
что это не превращается в N+1.</p>

<h3>Как обнаружить N+1 в production</h3>
<p>Если <code>lazy="raise"</code> используется не везде, N+1 в production
обычно проявляется как медленность: один эндпоинт занимает в 10-20 раз
больше времени, чем ожидается, но не выдаёт ошибку. Два основных способа
найти это: (1) через <code>echo=True</code> или инструмент APM (например
Sentry, DataDog) подсчитать, сколько SQL-запросов выполняется за один
запрос; (2) в таблице <code>pg_stat_statements</code> PostgreSQL увидеть
аномально частое повторение одного и того же шаблона запроса (логика
диагностики похожа на изученный в курсе 107 EXPLAIN ANALYZE). Оба способа
отвечают на вопрос "сколько раз один и тот же SQL-шаблон выполнился за
один HTTP-запрос".</p>

<h3>contains_eager() — переиспользование уже выполненного JOIN</h3>
<p>Иногда вы уже написали <code>.join()</code> (например для фильтрации), и
из результата этого JOIN можно заполнить и саму связь — в этом случае
<code>selectinload()</code> или <code>joinedload()</code> выполнили бы JOIN
ЕЩЁ РАЗ, впустую. <code>contains_eager()</code> говорит ORM: "я УЖЕ сделал
join для этой связи, не запрашивай её снова, используй этот результат" —
это противоположность "избыточной загрузки" (over-fetching) из урока 11:
не меньше данных, а ТОЧНЕЕ запрос.</p>
""".strip()

L5_CODE = """
# ============================================================
# 1) N+1 — muammoning o'zi (lazy loading sukut bo'yicha)
# ============================================================
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, joinedload, Mapped
from typing import List

# lazy= ko'rsatilmagan — sukut bo'yicha "select" (lazy):
class StudentLazy(Base):
    __tablename__ = "students_lazy"
    id: Mapped[int] = mapped_column(primary_key=True)
    enrolled_courses: Mapped[List["Course"]] = relationship(secondary=student_courses)


# XATO NAQSH — bu 50 ta talaba uchun 1 + 50 = 51 ta so'rov yuboradi:
students = (await db.execute(select(StudentLazy))).scalars().all()   # so'rov #1
for s in students:
    print(s.username, len(s.enrolled_courses))   # HAR BIR s uchun YANGI so'rov!

# ============================================================
# 2) selectinload() — 51 ta so'rov o'rniga aniq 2 ta
# ============================================================
stmt = select(StudentLazy).options(selectinload(StudentLazy.enrolled_courses))
students = (await db.execute(stmt)).scalars().all()
# Sahna ortida ikkita so'rov:
#   SELECT * FROM students_lazy
#   SELECT * FROM courses JOIN student_courses ON ... WHERE student_courses.student_id IN (1, 2, 3, ..., 50)
for s in students:
    print(s.username, len(s.enrolled_courses))   # YANGI so'rov YO'Q — allaqachon xotirada

# ============================================================
# 3) HAQIQIY misol: app/services/lesson_service.py'dagi naqsh
# ============================================================
async def get_lesson_by_id(db, lesson_id: int):
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.exercises),   # bitta darsning barcha mashqlari
            selectinload(Lesson.files),        # bitta darsning barcha fayllari
        )
    )
    return result.scalar_one_or_none()
# Bu ikki relationship() eager qilinmasa, har bir /lessons/{id} so'rovi
# darsning har bir mashqi va fayli uchun QO'SHIMCHA so'rov yuborar edi.

# ============================================================
# 4) joinedload() — bitta JOIN so'rovi, lekin cartesian ko'payish xavfi bilan
# ============================================================
one_to_one_stmt = select(StudentLazy).options(joinedload(StudentLazy.ranking))
# Ranking — uselist=False (one-to-one), shuning uchun joinedload xavfsiz:
# natijada takrorlanish yo'q, bitta JOIN yetarli.

# XATO ISHLATISH: katta ro'yxat uchun joinedload — 100 ta kursga yozilgan
# talaba uchun natija 100 marta takrorlangan talaba qatorini o'z ichiga oladi:
risky_stmt = select(StudentLazy).options(joinedload(StudentLazy.enrolled_courses))  # XATO NAQSH

# ============================================================
# 5) lazy="raise" — N+1'ni development bosqichida ushlash
# ============================================================
class StudentSafe(Base):
    __tablename__ = "students_safe"
    id: Mapped[int] = mapped_column(primary_key=True)
    enrolled_courses: Mapped[List["Course"]] = relationship(
        secondary=student_courses, lazy="raise"
    )

# students = (await db.execute(select(StudentSafe))).scalars().all()
# for s in students:
#     print(s.enrolled_courses)
# -> sqlalchemy.exc.InvalidRequestError: 'StudentSafe.enrolled_courses' is not
#    available due to lazy='raise' — .options(selectinload(...)) yozishni
#    UNUTGANINGIZNI darhol, test bosqichida ko'rsatadi.

# ============================================================
# 6) contains_eager() — allaqachon join qilingan natijadan foydalanish
# ============================================================
from sqlalchemy.orm import contains_eager

# Filtrlash uchun join allaqachon yozilgan — shu natijadan Course'ni ham to'ldiramiz:
already_joined_stmt = (
    select(StudentLazy)
    .join(StudentLazy.enrolled_courses)
    .where(Course.difficulty_level == "Advanced")
    .options(contains_eager(StudentLazy.enrolled_courses))
)
# selectinload() ishlatilganda bu yerda IKKINCHI marta join bajarilar edi —
# contains_eager() ORM'ga "join natijasi allaqachon bor, qayta so'rama" deydi.

# ============================================================
# 7) So'rovlar sonini taxminiy solishtirish — oldin/keyin
# ============================================================
# Stsenariy: 30 ta guruh ro'yxati sahifasi, har biri uchun a'zolar soni kerak.
#
# lazy (sukut bo'yicha), eager loading'siz:
#   1 so'rov (guruhlar) + 30 so'rov (har bir group.students uchun bittadan) = 31 so'rov
#
# selectinload():
#   1 so'rov (guruhlar) + 1 so'rov (barcha guruhlarning barcha a'zolari IN(...) orqali) = 2 so'rov
#
# joinedload() (xavfsiz, chunki guruhlar ro'yxati kichik):
#   1 so'rov (JOIN darhol barcha ma'lumotni keltiradi) = 1 so'rov,
#   lekin guruh ma'lumotini takrorlaydigan talaba qatorlari bilan (yuqoridagi 4-band).
#
# Xulosa: 31 va 2 so'rov orasidagi farq gipotetik emas — tarmoq kechikishi
# ~5ms/so'rov bo'lganda, bu farq faqat shu bitta endpoint uchun ~155ms va
# ~10ms orasidagi farq degani.

# ============================================================
# 8) Bir necha munosabatni bitta chaqiruvda — selectinload().selectinload()
# ============================================================
deep_stmt = (
    select(Course)
    .options(
        selectinload(Course.lessons).selectinload(Lesson.exercises)
    )
)
# Bu Course -> Lesson -> Exercise'ni aynan 3 ta so'rovda yuklaydi (daraxt
# darajasining har biriga bittadan), agar har bir daraja ichma-ich
# sikllarda lazy yuklansa kelib chiqadigan N+1+1 so'rov o'rniga.
""".strip()

L5_CODE_RU = """
# ============================================================
# 1) N+1 — сама проблема (lazy loading по умолчанию)
# ============================================================
from sqlalchemy import select
from sqlalchemy.orm import relationship, selectinload, joinedload, Mapped
from typing import List

# lazy= не указан — по умолчанию "select" (lazy):
class StudentLazy(Base):
    __tablename__ = "students_lazy"
    id: Mapped[int] = mapped_column(primary_key=True)
    enrolled_courses: Mapped[List["Course"]] = relationship(secondary=student_courses)


# НЕВЕРНЫЙ ПАТТЕРН — для 50 студентов отправит 1 + 50 = 51 запрос:
students = (await db.execute(select(StudentLazy))).scalars().all()   # запрос #1
for s in students:
    print(s.username, len(s.enrolled_courses))   # для КАЖДОГО s — НОВЫЙ запрос!

# ============================================================
# 2) selectinload() — вместо 51 запроса ровно 2
# ============================================================
stmt = select(StudentLazy).options(selectinload(StudentLazy.enrolled_courses))
students = (await db.execute(stmt)).scalars().all()
# За кулисами два запроса:
#   SELECT * FROM students_lazy
#   SELECT * FROM courses JOIN student_courses ON ... WHERE student_courses.student_id IN (1, 2, 3, ..., 50)
for s in students:
    print(s.username, len(s.enrolled_courses))   # НОВОГО запроса НЕТ — уже в памяти

# ============================================================
# 3) РЕАЛЬНЫЙ пример: паттерн из app/services/lesson_service.py
# ============================================================
async def get_lesson_by_id(db, lesson_id: int):
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.exercises),   # все упражнения одного урока
            selectinload(Lesson.files),        # все файлы одного урока
        )
    )
    return result.scalar_one_or_none()
# Без eager loading этих двух relationship() каждый запрос /lessons/{id}
# отправлял бы ДОПОЛНИТЕЛЬНЫЙ запрос на каждое упражнение и файл урока.

# ============================================================
# 4) joinedload() — один JOIN-запрос, но с риском декартова раздувания
# ============================================================
one_to_one_stmt = select(StudentLazy).options(joinedload(StudentLazy.ranking))
# Ranking — uselist=False (one-to-one), поэтому joinedload безопасен:
# дублирования нет, достаточно одного JOIN.

# НЕВЕРНОЕ ИСПОЛЬЗОВАНИЕ: joinedload для большого списка — для студента,
# записанного на 100 курсов, результат будет содержать строку студента,
# повторённую 100 раз:
risky_stmt = select(StudentLazy).options(joinedload(StudentLazy.enrolled_courses))  # НЕВЕРНЫЙ ПАТТЕРН

# ============================================================
# 5) lazy="raise" — ловим N+1 ещё на этапе разработки
# ============================================================
class StudentSafe(Base):
    __tablename__ = "students_safe"
    id: Mapped[int] = mapped_column(primary_key=True)
    enrolled_courses: Mapped[List["Course"]] = relationship(
        secondary=student_courses, lazy="raise"
    )

# students = (await db.execute(select(StudentSafe))).scalars().all()
# for s in students:
#     print(s.enrolled_courses)
# -> sqlalchemy.exc.InvalidRequestError: 'StudentSafe.enrolled_courses' is not
#    available due to lazy='raise' — сразу покажет, что вы ЗАБЫЛИ написать
#    .options(selectinload(...)), ещё на этапе тестов.

# ============================================================
# 6) contains_eager() — использование уже выполненного join
# ============================================================
from sqlalchemy.orm import contains_eager

# join для фильтрации уже написан — заполняем Course из этого же результата:
already_joined_stmt = (
    select(StudentLazy)
    .join(StudentLazy.enrolled_courses)
    .where(Course.difficulty_level == "Advanced")
    .options(contains_eager(StudentLazy.enrolled_courses))
)
# При использовании selectinload() здесь выполнился бы ВТОРОЙ join —
# contains_eager() говорит ORM: "результат join уже есть, не запрашивай снова".

# ============================================================
# 7) Приблизительное сравнение количества запросов — до/после
# ============================================================
# Сценарий: страница со списком из 30 групп, для каждой нужно число участников.
#
# lazy (по умолчанию), БЕЗ eager loading:
#   1 запрос (группы) + 30 запросов (по одному на group.students) = 31 запрос
#
# selectinload():
#   1 запрос (группы) + 1 запрос (все участники всех групп через IN(...)) = 2 запроса
#
# joinedload() (безопасно, поскольку список групп небольшой):
#   1 запрос (JOIN сразу приносит все данные) = 1 запрос,
#   но со строками студентов, дублирующими данные группы (см. пункт 4 выше).
#
# Вывод: разница между 31 и 2 запросами не гипотетическая — при задержке
# сети ~5мс на запрос это разница между ~155мс и ~10мс только на этом
# одном эндпоинте.

# ============================================================
# 8) Несколько связей за один вызов — selectinload().selectinload()
# ============================================================
deep_stmt = (
    select(Course)
    .options(
        selectinload(Course.lessons).selectinload(Lesson.exercises)
    )
)
# Это загружает Course -> Lesson -> Exercise ровно в 3 запроса (по одному
# на каждый уровень дерева), а не в N+1+1 запросов, если бы каждый
# уровень загружался лениво внутри вложенных циклов.
""".strip()

L5_TASK = {
    "task_title": "N+1'ni toping va selectinload() bilan tuzating",
    "task_title_ru": "Найдите N+1 и исправьте через selectinload()",
    "task_description": (
        "Quyidagi funksiya N+1 muammosiga ega: barcha faol guruhlarni olib, "
        "har biri uchun guruh a'zolari sonini chiqaradi "
        "(group.students ro'yxatiga har bir guruh uchun alohida murojaat "
        "qilinadi). Funksiyani tuzating: selectinload() bilan eager loading "
        "qo'shing, va aynan nechta SQL so'rovi kamayganini (oldingi/keyingi "
        "sonlarni) yozma tushuntiring."
    ),
    "task_description_ru": (
        "Следующая функция страдает от N+1: получает все активные группы и "
        "для каждой выводит количество участников (список group.students "
        "запрашивается отдельно для каждой группы). Исправьте функцию: "
        "добавьте eager loading через selectinload(), и письменно объясните, "
        "на сколько именно сократилось число SQL-запросов (до/после)."
    ),
    "task_requirements": (
        "1) Muammoli kodni keltiring (lazy loading bilan). 2) Tuzatilgan "
        "kodni keltiring (selectinload() bilan). 3) Ikkalasining SQL so'rovlar "
        "sonini solishtirib yozing (masalan '1+20=21 -> 2'). 4) lazy='raise' "
        "qo'shilsa, qaysi qatorda xato chiqishini ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Приведите проблемный код (с lazy loading). 2) Приведите "
        "исправленный код (с selectinload()). 3) Сравните число SQL-запросов "
        "до/после (например '1+20=21 -> 2'). 4) Покажите, в какой строке "
        "возникла бы ошибка при добавлении lazy='raise'."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 4,
}

L5_SAMPLE = {
    "title": "Namuna: N+1'dan oldin va keyin — Group + students",
    "description": "Bir xil funksiyaning ikki versiyasi: lazy loading bilan N+1 va selectinload() bilan tuzatilgan holati, so'rov sonlari izohi bilan.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "before_n_plus_1.py",
            "language": "python",
            "code": (
                "from sqlalchemy import select\n\n\n"
                "async def group_member_counts_SLOW(db):\n"
                "    # 1-so'rov: barcha faol guruhlarni olish\n"
                "    groups = (await db.execute(select(Group).where(Group.is_active == True))).scalars().all()\n"
                "    result = {}\n"
                "    for g in groups:\n"
                "        # HAR BIR guruh uchun YANGI so'rov (lazy loading) — N+1!\n"
                "        result[g.name] = len(g.students)\n"
                "    return result\n"
                "    # 20 ta guruh bo'lsa: 1 + 20 = 21 ta SQL so'rovi\n"
            ),
        },
        {
            "filename": "after_selectinload.py",
            "language": "python",
            "code": (
                "from sqlalchemy import select\n"
                "from sqlalchemy.orm import selectinload\n\n\n"
                "async def group_member_counts_FAST(db):\n"
                "    stmt = (\n"
                "        select(Group)\n"
                "        .where(Group.is_active == True)\n"
                "        .options(selectinload(Group.students))\n"
                "    )\n"
                "    groups = (await db.execute(stmt)).scalars().all()\n"
                "    result = {}\n"
                "    for g in groups:\n"
                "        # so'rov YO'Q — students allaqachon 2-so'rov orqali yuklangan\n"
                "        result[g.name] = len(g.students)\n"
                "    return result\n"
                "    # 20 ta guruh bo'lsa ham: doim aniq 2 ta SQL so'rovi\n"
            ),
        },
    ],
}

L5_EXERCISES = [
    {
        "title": "N+1 qachon sodir bo'ladi?",
        "title_ru": "Когда возникает N+1?",
        "description": "lazy= ko'rsatilmagan relationship()ga siklda har bir obyekt uchun murojaat qilinsa, nima sodir bo'ladi?",
        "description_ru": "Что происходит, если в цикле обращаться к relationship() без lazy= для каждого объекта?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir obyekt uchun alohida qo'shimcha SQL so'rovi yuboriladi",
            "Barcha ma'lumot bitta so'rovda avtomatik keladi",
            "SQLAlchemy xato beradi va to'xtaydi",
            "Munosabat har doim bo'sh qaytadi",
        ],
        "options_ru": [
            "Для каждого объекта отправляется отдельный дополнительный SQL-запрос",
            "Все данные автоматически приходят одним запросом",
            "SQLAlchemy выдаёт ошибку и останавливается",
            "Связь всегда возвращается пустой",
        ],
        "correct_answers": "A",
        "hint": "Sukut bo'yicha lazy='select' — har bir birinchi murojaat yangi so'rov ochadi.",
        "hint_ru": "По умолчанию lazy='select' — каждое первое обращение открывает новый запрос.",
        "explanation": "Bu aynan N+1 muammosi — 1 ta asosiy so'rov + har bir qator uchun 1 tadan qo'shimcha so'rov.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "selectinload vs joinedload",
        "title_ru": "selectinload против joinedload",
        "description": "Bitta talabaning 200 ta kursi bor deb faraz qiling. Qaysi yuklash usuli 'cartesian ko'payish' xavfidan XOLI?",
        "description_ru": "Предположим, у студента 200 курсов. Какой способ загрузки БЕЗ риска 'декартова раздувания'?",
        "exercise_type": "multiple_choice",
        "options": ["selectinload()", "joinedload()", "Ikkalasi ham xavfsiz", "Ikkalasi ham xavfli"],
        "options_ru": ["selectinload()", "joinedload()", "Оба безопасны", "Оба опасны"],
        "correct_answers": "A",
        "hint": "joinedload LEFT JOIN orqali ishlaydi — katta ro'yxatlarda asosiy qator takrorlanadi.",
        "hint_ru": "joinedload работает через LEFT JOIN — на больших списках основная строка дублируется.",
        "explanation": "selectinload alohida IN(...) so'rovi yuboradi, natijada takrorlanish bo'lmaydi; joinedload esa katta to'plamlarda takrorlanadi.",
        "difficulty_level": "Hard",
        "points": 10,
    },
    {
        "title": "N+1'ni tuzatish qadamlari",
        "title_ru": "Шаги исправления N+1",
        "description": "Kodda N+1 muammosini topib tuzatishning odatiy qadamlarini tartibga joylashtiring.",
        "description_ru": "Расположите типичные шаги обнаружения и исправления N+1 в коде.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "echo=True bilan ortiqcha so'rovlarni ko'rish",
            "Qaysi relationship() lazy ekanini aniqlash",
            ".options(selectinload(...)) qo'shish",
            "So'rovlar sonini qayta tekshirish",
        ],
        "drag_items_ru": [
            "Увидеть лишние запросы через echo=True",
            "Определить, какой relationship() загружается lazy",
            "Добавить .options(selectinload(...))",
            "Повторно проверить количество запросов",
        ],
        "correct_order": [
            "echo=True bilan ortiqcha so'rovlarni ko'rish",
            "Qaysi relationship() lazy ekanini aniqlash",
            ".options(selectinload(...)) qo'shish",
            "So'rovlar sonini qayta tekshirish",
        ],
        "hint": "Avval muammoni ko'rish, keyin sababni topish, keyin tuzatish, oxirida tekshirish.",
        "hint_ru": "Сначала увидеть проблему, потом найти причину, потом исправить, в конце проверить.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 6 — Tranzaksiyalar va Sessiyalar: Unit of Work
# ---------------------------------------------------------------------------

L6_TEXT = """
<h3>Session — bu shunchaki "ulanish" emas, "ish birligi"</h3>
<p>Yangi boshlovchilar ko'pincha <code>Session</code>ni bazaga ulanish
(connection) bilan adashtiradi. Aslida Session — <strong>Unit of Work</strong>
(ish birligi) naqshini amalga oshiradi: u sizning barcha o'zgarishlaringizni
(qo'shilgan, o'zgartirilgan, o'chirilgan obyektlar) xotirada kuzatib boradi
va faqat <code>commit()</code> chaqirilganda ularning barchasini BITTA
tranzaksiyada bazaga yuboradi. Bu platformada har bir HTTP so'rovi o'zining
Session'iga ega — <code>app/dependencies.py</code>'dagi
<code>get_db()</code> orqali.</p>

<h3>flush() vs commit() — ikki xil "bazaga yuborish"</h3>
<p><code>flush()</code> — Session'dagi kutilayotgan o'zgarishlarni bazaga
YUBORADI (INSERT/UPDATE bajaradi), lekin tranzaksiyani YAKUNLAMAYDI — hali
<code>ROLLBACK</code> qilish mumkin. <code>commit()</code> esa avval
avtomatik flush qiladi, SO'NGRA tranzaksiyani <code>COMMIT</code> bilan
yakunlaydi — bundan keyin o'zgarishlarni qaytarib bo'lmaydi. Yangi
qo'shilgan obyektning ID'sini commit'dan OLDIN bilish kerak bo'lsa (masalan
boshqa obyektga FOREIGN KEY sifatida berish uchun), <code>await
db.flush()</code> yetarli — butun tranzaksiyani yakunlash shart emas.</p>

<h3>Tranzaksiya chegaralari — bitta so'rov, bitta "hammasi yoki hech nima"</h3>
<p>107-kursda <code>BEGIN; ... COMMIT;</code> orqali ko'rgan atomiklik
tushunchasi ORM'da ham xuddi shunday ishlaydi: agar bitta so'rovda 3 ta
jadvalga yozish kerak bo'lsa (masalan yangi Submission + Student ballarini
yangilash + Achievement tekshiruvi) va uchinchisi xato bersa, birinchi
ikkitasi ham COMMIT bo'lmasligi kerak. Bu platformaning haqiqiy
<code>exercise_service.py</code>'sida bu naqsh aniq ko'rinadi: agar
<code>bump_streak()</code> xato bersa, faqat SHU qo'shimcha amal
<code>rollback()</code> qilinadi, asosiy submission esa allaqachon alohida
commit qilingan bo'ladi — bu ataylab qilingan qaror, chunki ikkalasi
mustaqil ish birligi hisoblanadi.</p>

<h3>IntegrityError va rollback — poyga holatlarini (race condition) boshqarish</h3>
<p>Bir vaqtning o'zida ikkita so'rov bir xil UniqueConstraint'ni buzishga
urinishi mumkin (masalan ikkala so'rov ham "bu darsni birinchi marta
tugatdim" deb his qilib, ball qo'shishga urinadi). Bunday holatda
PostgreSQL <code>IntegrityError</code> tashlaydi — bu platformada bu holat
maxsus <code>try/except IntegrityError: await db.rollback()</code> orqali
ushlanadi: "ikkinchi so'rov yutqazdi" degani, va bu XATO emas, kutilgan
poyga holati natijasi. rollback — Session'ni "toza" holatga qaytaradi,
keyingi operatsiyalar buzilgan tranzaksiya holatida davom etmaydi.</p>

<h3>expire_on_commit=False — nega bu platformada ishlatiladi</h3>
<p>Standart holatda, <code>commit()</code>dan keyin Session barcha
obyektlarni "eskirgan" (expired) deb belgilaydi — keyingi murojaatda ularni
QAYTA bazadan o'qiydi. Bu ba'zan kerak, lekin FastAPI'da endpoint
<code>commit()</code>dan keyin obyekt atributlarini javobga qo'shishi kerak
bo'lganda muammo tug'diradi (Session allaqachon yopilgan bo'lishi mumkin).
Shuning uchun <code>async_sessionmaker(..., expire_on_commit=False)</code>
ishlatiladi — commit'dan keyin ham obyekt atributlariga xotiradan
(bazaga qayta murojaatsiz) kirish mumkin bo'ladi.</p>

<h3>Context manager — Session har doim yopilishini kafolatlash</h3>
<p><code>async with AsyncSessionLocal() as session:</code> — bu blok
tugaganda (xato bo'lsa ham) Session avtomatik yopiladi. Bu — 12-darsda
ko'radigan "connection pool tugashi" muammosining oldini oluvchi eng muhim
qoida: agar Session qo'lda yopilmasa (masalan try/finally'siz), u
connection pool'dan bitta ulanishni abadiy egallab qoladi.</p>

<h3>Ichma-ich tranzaksiyalar — begin_nested() va SAVEPOINT</h3>
<p>Ba'zan katta tranzaksiya ichida faqat bir qismini bekor qilish kerak
bo'ladi, hammasini emas. PostgreSQL'ning <code>SAVEPOINT</code> mexanizmi
buni imkon beradi, ORM darajasida esa <code>async with
db.begin_nested():</code> orqali ishlatiladi. Masalan: asosiy submission
saqlanadi, so'ngra ixtiyoriy "bonus tekshiruvi" ichki savepoint ichida
ishga tushiriladi — agar bonus tekshiruvi xato bersa, faqat SHU qism
bekor bo'ladi, asosiy submission esa tashqi tranzaksiyada saqlanib qoladi.</p>

<h3>db.get() vs select().where(id ==) — bir xil natija, ikki yo'l</h3>
<p><code>await db.get(Student, 7)</code> — bu PRIMARY KEY bo'yicha qidiruv
uchun maxsus qisqartma: agar shu ID Session'ning identity map'ida
allaqachon bo'lsa, ORM hatto bazaga so'rov HAM yubormaydi (0-darsdagi
identity map misolini eslang). <code>select(Student).where(Student.id ==
7)</code> esa har doim so'rov yuboradi, hatto obyekt xotirada bo'lsa ham
— chunki bu umumiy so'rov mexanizmi, identity map'ni "qisqa yo'l" sifatida
ishlatmaydi.</p>
""".strip()

L6_TEXT_RU = """
<h3>Session — это не просто "подключение", а "единица работы"</h3>
<p>Новички часто путают <code>Session</code> с подключением (connection) к
базе. На самом деле Session реализует паттерн <strong>Unit of Work</strong>
(единица работы): он отслеживает в памяти все ваши изменения (добавленные,
изменённые, удалённые объекты) и отправляет их все ОДНОЙ транзакцией в базу
только при вызове <code>commit()</code>. На этой платформе каждый
HTTP-запрос получает свою Session — через <code>get_db()</code> в
<code>app/dependencies.py</code>.</p>

<h3>flush() против commit() — два разных вида "отправки в базу"</h3>
<p><code>flush()</code> ОТПРАВЛЯЕТ ожидающие изменения Session в базу
(выполняет INSERT/UPDATE), но НЕ завершает транзакцию — откат (ROLLBACK)
всё ещё возможен. <code>commit()</code> же сначала автоматически делает
flush, а ЗАТЕМ завершает транзакцию через <code>COMMIT</code> — после
этого откатить изменения нельзя. Если ID только что добавленного объекта
нужен ДО commit (например чтобы передать его как FOREIGN KEY другому
объекту), достаточно <code>await db.flush()</code> — завершать всю
транзакцию не обязательно.</p>

<h3>Границы транзакции — один запрос, одно "всё или ничего"</h3>
<p>Изученное в курсе 107 через <code>BEGIN; ... COMMIT;</code> понятие
атомарности в ORM работает точно так же: если в одном запросе нужно
записать в 3 таблицы (например новый Submission + обновление баллов
студента + проверку достижений) и третья операция даёт сбой, первые две
тоже не должны быть COMMIT. В реальном <code>exercise_service.py</code>
этой платформы этот паттерн виден явно: если <code>bump_streak()</code>
выдаёт ошибку, откатывается (<code>rollback()</code>) только ЭТА
дополнительная операция, а основной submission уже был закоммичен
отдельно — это намеренное решение, поскольку обе операции считаются
независимыми единицами работы.</p>

<h3>IntegrityError и rollback — управление гонками (race conditions)</h3>
<p>Два запроса одновременно могут попытаться нарушить один и тот же
UniqueConstraint (например оба запроса думают "я первый завершаю этот
урок" и пытаются добавить баллы). В этом случае PostgreSQL выбрасывает
<code>IntegrityError</code> — на этой платформе это обрабатывается через
<code>try/except IntegrityError: await db.rollback()</code>: это означает
"второй запрос проиграл гонку", и это не ошибка, а ожидаемый результат
гонки. rollback возвращает Session в "чистое" состояние, чтобы следующие
операции не продолжались в состоянии сломанной транзакции.</p>

<h3>expire_on_commit=False — почему используется на этой платформе</h3>
<p>По умолчанию после <code>commit()</code> Session помечает все объекты
как "устаревшие" (expired) — при следующем обращении они будут ЗАНОВО
прочитаны из базы. Иногда это нужно, но в FastAPI это создаёт проблему,
когда эндпоинту нужно добавить атрибуты объекта в ответ после
<code>commit()</code> (Session может быть уже закрыта). Поэтому
используется <code>async_sessionmaker(..., expire_on_commit=False)</code>
— доступ к атрибутам объекта из памяти (без повторного обращения к базе)
остаётся возможным даже после commit.</p>

<h3>Контекстный менеджер — гарантия закрытия Session</h3>
<p><code>async with AsyncSessionLocal() as session:</code> — при выходе из
этого блока (даже при ошибке) Session автоматически закрывается. Это
важнейшее правило, предотвращающее проблему "исчерпания пула подключений"
из урока 12: если Session не закрыта вручную (например без try/finally),
она навсегда займёт одно подключение из пула.</p>

<h3>Вложенные транзакции — begin_nested() и SAVEPOINT</h3>
<p>Иногда внутри большой транзакции нужно отменить только часть, а не всё
целиком. Механизм <code>SAVEPOINT</code> в PostgreSQL позволяет это, а на
уровне ORM используется через <code>async with db.begin_nested():</code>.
Например: основной submission сохраняется, затем необязательная "проверка
бонуса" запускается внутри вложенного savepoint — если проверка бонуса
даёт сбой, отменяется только ЭТА часть, а основной submission остаётся
сохранённым во внешней транзакции.</p>

<h3>db.get() против select().where(id ==) — одинаковый результат, два пути</h3>
<p><code>await db.get(Student, 7)</code> — это специальное сокращение для
поиска по PRIMARY KEY: если этот ID уже есть в identity map Session, ORM
даже НЕ отправит запрос к базе (вспомните пример identity map из урока 0).
<code>select(Student).where(Student.id == 7)</code> же всегда отправляет
запрос, даже если объект уже в памяти — потому что это общий механизм
запросов, не использующий identity map как "короткий путь".</p>
""".strip()

L6_CODE = """
# ============================================================
# 1) flush() vs commit() — ID kerak, lekin hali commit qilmoqchi emassiz
# ============================================================
new_course = Course(title="Yangi kurs", instructor_id=2, difficulty_level="Advanced",
                     duration_weeks=4, max_points=100)
db.add(new_course)
await db.flush()          # INSERT bajarildi, ID mavjud, lekin hali ROLLBACK mumkin
print(new_course.id)       # allaqachon mavjud — masalan 501

new_lesson = Lesson(course_id=new_course.id, title="1-dars", order=0)
db.add(new_lesson)
await db.commit()          # ENDI hammasi (course + lesson) BITTA tranzaksiyada yakunlanadi

# ============================================================
# 2) Tranzaksiya atomikligi — hammasi yoki hech nima
# ============================================================
try:
    db.add(Submission(student_id=7, project_id=3, status="pending"))
    await db.flush()
    student = await db.get(Student, 7)
    student.total_points += 50   # xato shu yerda bo'lsa...
    await db.commit()            # ...bu qator HECH QACHON bajarilmaydi
except Exception:
    await db.rollback()          # Submission ham, ball ham bazaga yozilmaydi

# ============================================================
# 3) HAQIQIY misol: exercise_service.py'dagi mustaqil ish birliklari
# ============================================================
async def submit_exercise(db, student_id: int, exercise_id: int, answer: str):
    submission = Submission(student_id=student_id, exercise_id=exercise_id, answer=answer)
    db.add(submission)
    await db.commit()   # asosiy submission — o'z ish birligi, mustaqil commit

    try:
        # streak yangilash — ALOHIDA, kichikroq ish birligi
        await bump_streak(db, student_id)
        await db.commit()
    except Exception:
        await db.rollback()   # faqat streak urinishi bekor bo'ladi, submission qoladi

    return submission

# ============================================================
# 4) IntegrityError — poyga holati (race condition) kutilgan xato sifatida
# ============================================================
from sqlalchemy.exc import IntegrityError

async def award_completion_points(db, student_id: int, lesson_id: int, points: int):
    db.add(LessonCompletion(student_id=student_id, lesson_id=lesson_id))  # UniqueConstraint bor
    student = await db.get(Student, student_id)
    student.total_points += points
    try:
        await db.commit()
    except IntegrityError:
        # Boshqa parallel so'rov bu yerni BIRINCHI bo'lib to'ldirgan —
        # bu XATO emas, kutilgan poyga natijasi.
        await db.rollback()

# ============================================================
# 5) expire_on_commit=False — commit'dan keyin ham atributlar o'qiladi
# ============================================================
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
# expire_on_commit=False BO'LMASA:
#   await db.commit()
#   print(new_course.title)   # -> yana bir SELECT yuboradi (obyekt "eskirgan")
# expire_on_commit=False BILAN:
#   await db.commit()
#   print(new_course.title)   # -> xotiradan, qo'shimcha so'rovsiz

# ============================================================
# 6) Context manager — Session har doim yopilishini kafolatlash
# ============================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()   # xato bo'lsa ham — ulanish pool'ga qaytadi

# ============================================================
# 7) begin_nested() — faqat bir qismini bekor qilish (SAVEPOINT)
# ============================================================
async def submit_with_optional_bonus_check(db, student_id: int, exercise_id: int):
    submission = Submission(student_id=student_id, exercise_id=exercise_id)
    db.add(submission)
    await db.flush()   # asosiy submission tashqi tranzaksiyada

    try:
        async with db.begin_nested():   # SAVEPOINT ochiladi
            bonus = await check_bonus_eligibility(db, student_id)   # xato berishi mumkin
            if bonus:
                db.add(BonusAward(student_id=student_id, amount=bonus))
    except Exception:
        pass   # faqat SAVEPOINT ichidagi qism bekor bo'ladi — submission qoladi

    await db.commit()   # submission (va muvaffaqiyatli bo'lsa BonusAward) saqlanadi

# ============================================================
# 8) db.get() — identity map orqali qisqa yo'l
# ============================================================
student = await db.get(Student, 7)          # identity map'da bo'lsa — SQL YO'Q
same_student = (await db.execute(
    select(Student).where(Student.id == 7)
)).scalar_one()                              # bu HAR DOIM SQL yuboradi
assert student is same_student               # ikkalasi ham bir xil Python obyekti

# ============================================================
# 9) FastAPI endpoint ichida to'liq tranzaksiya hayotiy tsikli
# ============================================================
@router.post("/exercises/{exercise_id}/submit")
async def submit_exercise_endpoint(
    exercise_id: int, answer: str, student_id: int, db: AsyncSession = Depends(get_db)
):
    is_correct = check_answer(exercise_id, answer)
    submission = ExerciseAttempt(student_id=student_id, exercise_id=exercise_id, is_correct=is_correct)
    db.add(submission)
    await db.commit()   # birinchi ish birligi — javob urinishining o'zi

    if is_correct:
        try:
            await bump_streak(db, student_id)
            await db.commit()   # ikkinchi, mustaqil ish birligi
        except Exception:
            await db.rollback()  # streak muhim emas — javob urinishi allaqachon saqlangan

    return {"correct": is_correct}
# E'tibor bering: agar ikkalasi BITTA tranzaksiyada bo'lganida va
# bump_streak() xato bersa, javob urinishining o'zi ham bekor bo'lardi —
# talaba haqiqiy xatosi bo'lmagan joyda xato ko'rgan bo'lardi.
""".strip()

L6_CODE_RU = """
# ============================================================
# 1) flush() против commit() — нужен ID, но commit ещё не хотите делать
# ============================================================
new_course = Course(title="Новый курс", instructor_id=2, difficulty_level="Advanced",
                     duration_weeks=4, max_points=100)
db.add(new_course)
await db.flush()          # INSERT выполнен, ID есть, но ROLLBACK всё ещё возможен
print(new_course.id)       # уже доступен — например 501

new_lesson = Lesson(course_id=new_course.id, title="Урок 1", order=0)
db.add(new_lesson)
await db.commit()          # ТЕПЕРЬ всё (course + lesson) завершается одной транзакцией

# ============================================================
# 2) Атомарность транзакции — всё или ничего
# ============================================================
try:
    db.add(Submission(student_id=7, project_id=3, status="pending"))
    await db.flush()
    student = await db.get(Student, 7)
    student.total_points += 50   # если ошибка здесь...
    await db.commit()            # ...эта строка НИКОГДА не выполнится
except Exception:
    await db.rollback()          # ни Submission, ни баллы не запишутся в базу

# ============================================================
# 3) РЕАЛЬНЫЙ пример: независимые единицы работы в exercise_service.py
# ============================================================
async def submit_exercise(db, student_id: int, exercise_id: int, answer: str):
    submission = Submission(student_id=student_id, exercise_id=exercise_id, answer=answer)
    db.add(submission)
    await db.commit()   # основной submission — своя единица работы, отдельный commit

    try:
        # обновление streak — ОТДЕЛЬНАЯ, меньшая единица работы
        await bump_streak(db, student_id)
        await db.commit()
    except Exception:
        await db.rollback()   # отменяется только попытка streak, submission остаётся

    return submission

# ============================================================
# 4) IntegrityError — гонка (race condition) как ожидаемая ошибка
# ============================================================
from sqlalchemy.exc import IntegrityError

async def award_completion_points(db, student_id: int, lesson_id: int, points: int):
    db.add(LessonCompletion(student_id=student_id, lesson_id=lesson_id))  # есть UniqueConstraint
    student = await db.get(Student, student_id)
    student.total_points += points
    try:
        await db.commit()
    except IntegrityError:
        # Другой параллельный запрос заполнил это ПЕРВЫМ —
        # это НЕ ошибка, а ожидаемый результат гонки.
        await db.rollback()

# ============================================================
# 5) expire_on_commit=False — доступ к атрибутам и после commit
# ============================================================
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
# БЕЗ expire_on_commit=False:
#   await db.commit()
#   print(new_course.title)   # -> отправит ещё один SELECT (объект "устарел")
# С expire_on_commit=False:
#   await db.commit()
#   print(new_course.title)   # -> из памяти, без дополнительного запроса

# ============================================================
# 6) Контекстный менеджер — гарантия закрытия Session
# ============================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()   # даже при ошибке — подключение вернётся в пул

# ============================================================
# 7) begin_nested() — отмена только части (SAVEPOINT)
# ============================================================
async def submit_with_optional_bonus_check(db, student_id: int, exercise_id: int):
    submission = Submission(student_id=student_id, exercise_id=exercise_id)
    db.add(submission)
    await db.flush()   # основной submission во внешней транзакции

    try:
        async with db.begin_nested():   # открывается SAVEPOINT
            bonus = await check_bonus_eligibility(db, student_id)   # может дать сбой
            if bonus:
                db.add(BonusAward(student_id=student_id, amount=bonus))
    except Exception:
        pass   # отменяется только часть внутри SAVEPOINT — submission остаётся

    await db.commit()   # submission (и BonusAward при успехе) сохраняются

# ============================================================
# 8) db.get() — короткий путь через identity map
# ============================================================
student = await db.get(Student, 7)          # если есть в identity map — SQL НЕ отправляется
same_student = (await db.execute(
    select(Student).where(Student.id == 7)
)).scalar_one()                              # это ВСЕГДА отправляет SQL
assert student is same_student               # оба — один и тот же объект Python

# ============================================================
# 9) Полный жизненный цикл транзакции внутри одного эндпоинта FastAPI
# ============================================================
@router.post("/exercises/{exercise_id}/submit")
async def submit_exercise_endpoint(
    exercise_id: int, answer: str, student_id: int, db: AsyncSession = Depends(get_db)
):
    is_correct = check_answer(exercise_id, answer)
    submission = ExerciseAttempt(student_id=student_id, exercise_id=exercise_id, is_correct=is_correct)
    db.add(submission)
    await db.commit()   # первая единица работы — сама попытка

    if is_correct:
        try:
            await bump_streak(db, student_id)
            await db.commit()   # вторая, независимая единица работы
        except Exception:
            await db.rollback()  # streak не критичен — сама попытка уже сохранена

    return {"correct": is_correct}
# Обратите внимание на границу: если бы обе операции были в ОДНОЙ
# транзакции и bump_streak() дал сбой, откатилась бы и сама попытка —
# студент увидел бы ошибку там, где реального сбоя в его ответе не было.
""".strip()

L6_TASK = {
    "task_title": "Ballarni tranzaksiya ichida xavfsiz qo'shish",
    "task_title_ru": "Безопасное начисление баллов внутри транзакции",
    "task_description": (
        "award_project_points(db, student_id, project_id, points) funksiyasini "
        "yozing: (1) ProjectCompletion qatorini qo'shadi (student_id+project_id "
        "uchun UniqueConstraint bor — bir loyiha uchun bir marta ball beriladi); "
        "(2) Student.total_points'ni oshiradi; (3) IntegrityError kelsa (poyga "
        "holati — boshqa so'rov ulgurgan), faqat shu urinishni bekor qiladi, "
        "xatoni yuqoriga tashlamaydi."
    ),
    "task_description_ru": (
        "Напишите функцию award_project_points(db, student_id, project_id, "
        "points): (1) добавляет строку ProjectCompletion (есть UniqueConstraint "
        "на student_id+project_id — баллы начисляются один раз за проект); (2) "
        "увеличивает Student.total_points; (3) при IntegrityError (гонка — "
        "другой запрос успел раньше) отменяет только эту попытку, не "
        "пробрасывая ошибку выше."
    ),
    "task_requirements": (
        "1) db.add() + db.flush()/commit() ketma-ketligi to'g'ri. 2) try/except "
        "IntegrityError bloki bilan rollback(). 3) Funksiya muvaffaqiyatli/"
        "muvaffaqiyatsiz holatni (bool yoki None) qaytaradi. 4) Kodda flush() "
        "va commit() farqini izohda tushuntiring."
    ),
    "task_requirements_ru": (
        "1) Правильная последовательность db.add() + db.flush()/commit(). 2) "
        "Блок try/except IntegrityError с rollback(). 3) Функция возвращает "
        "статус успеха/неуспеха (bool или None). 4) Объясните в комментарии "
        "разницу между flush() и commit()."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 4,
}

L6_SAMPLE = {
    "title": "Namuna: award_project_points — tranzaksiya va poyga holati",
    "description": "IntegrityError'ni to'g'ri ushlaydigan, mustaqil ish birligi sifatida ball qo'shuvchi to'liq funksiya.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "award_points.py",
            "language": "python",
            "code": (
                "from sqlalchemy.exc import IntegrityError\n"
                "from sqlalchemy.ext.asyncio import AsyncSession\n\n\n"
                "async def award_project_points(\n"
                "    db: AsyncSession, student_id: int, project_id: int, points: int\n"
                ") -> bool:\n"
                "    db.add(ProjectCompletion(student_id=student_id, project_id=project_id))\n"
                "    try:\n"
                "        await db.flush()  # UniqueConstraint shu yerda tekshiriladi\n"
                "    except IntegrityError:\n"
                "        await db.rollback()\n"
                "        return False  # allaqachon ball berilgan — bu xato emas\n\n"
                "    student = await db.get(Student, student_id)\n"
                "    student.total_points += points\n"
                "    await db.commit()\n"
                "    return True\n"
            ),
        },
    ],
}

L6_EXERCISES = [
    {
        "title": "flush() nima qiladi?",
        "title_ru": "Что делает flush()?",
        "description": "flush() chaqirilganda nima sodir bo'ladi?",
        "description_ru": "Что происходит при вызове flush()?",
        "exercise_type": "multiple_choice",
        "options": [
            "O'zgarishlar bazaga yuboriladi, lekin tranzaksiya hali yakunlanmagan",
            "Tranzaksiya to'liq yakunlanadi, rollback endi mumkin emas",
            "Hech narsa qilinmaydi, faqat keshni tozalaydi",
            "Session butunlay yopiladi",
        ],
        "options_ru": [
            "Изменения отправляются в базу, но транзакция ещё не завершена",
            "Транзакция полностью завершается, rollback больше невозможен",
            "Ничего не делает, только очищает кэш",
            "Session полностью закрывается",
        ],
        "correct_answers": "A",
        "hint": "commit() = flush() + COMMIT. flush() yolg'iz — faqat birinchi qism.",
        "hint_ru": "commit() = flush() + COMMIT. Один flush() — только первая часть.",
        "explanation": "flush() INSERT/UPDATE'larni bazaga yuboradi, lekin COMMIT qilmaydi — hali rollback qilish mumkin.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "IntegrityError qachon kutilgan xato?",
        "title_ru": "Когда IntegrityError — ожидаемая ошибка?",
        "description": "Ikki parallel so'rov bir xil UniqueConstraint'ni buzishga urinsa, bu holat ___ deb ataladi.",
        "description_ru": "Когда два параллельных запроса пытаются нарушить один и тот же UniqueConstraint, эта ситуация называется ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "poyga holati",
        "correct_answers_ru": "гонка",
        "hint": "Ingliz tilida 'race condition' deb ataladi.",
        "hint_ru": "По-английски это называется 'race condition'.",
        "difficulty_level": "Hard",
        "points": 10,
    },
    {
        "title": "Session yopilishini kafolatlash",
        "title_ru": "Гарантия закрытия Session",
        "description": "Session har doim (xato bo'lsa ham) yopilishini kafolatlash uchun qaysi konstruksiya ishlatiladi?",
        "description_ru": "Какая конструкция используется, чтобы гарантировать закрытие Session даже при ошибке?",
        "exercise_type": "multiple_choice",
        "options": ["async with / try-finally", "oddiy if sharti", "faqat commit() chaqirish", "global o'zgaruvchi"],
        "options_ru": ["async with / try-finally", "обычное условие if", "просто вызов commit()", "глобальная переменная"],
        "correct_answers": "A",
        "hint": "Kontekst menejeri blokdan chiqishda (xato bilan ham) tozalashni kafolatlaydi.",
        "hint_ru": "Контекстный менеджер гарантирует очистку при выходе из блока (даже с ошибкой).",
        "explanation": "async with AsyncSessionLocal() as session: ... — bloqdan har qanday holatda chiqilganda ham Session yopiladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 7 — R1: Takrorlash — ORM asoslari bo'yicha amaliyot
# ---------------------------------------------------------------------------

L7_TEXT = """
<h3>Yo'lning yarmi — nimalarni bilib oldingiz</h3>
<p>0-6-darslarda siz ORM'ning butun "asoslar" qismini bosib o'tdingiz:
impedance mismatch nima ekanidan (0-dars) boshlab, SQLAlchemy'ning ikki
qatlami (1-dars), deklarativ modellar va mapping (2-dars), munosabatlar
(3-dars), so'rovlar (4-dars), N+1 va eager/lazy loading (5-dars), va
nihoyat tranzaksiya/Session boshqaruvi (6-dars). Bu — ORM bilan ishlashning
to'liq "kunlik tsikli": model yozish -> munosabat qurish -> so'rov yozish
-> samarali yuklash -> xavfsiz saqlash. Keyingi 8-11-darslar butunlay
boshqa mavzuga — migratsiyalarga — o'tadi, shuning uchun bu checkpoint
oxirgi imkoniyat: asoslarni mustahkamlab, keyin oldinga siljish.</p>

<h3>Eng ko'p uchraydigan xatolar — qayta ko'rib chiqing</h3>
<ul>
<li><strong>relationship() ni ustunga aylantirib tushunish</strong> (2-3-dars) —
u FOREIGN KEY o'rniga emas, uning USTIGA qo'yiladi.</li>
<li><strong>lazy loading'ni siklda ishlatish</strong> (5-dars) — bu N+1'ning
eng keng tarqalgan sababi; selectinload()siz production kodini yozmang.</li>
<li><strong>commit()ni juda kech yoki juda erta chaqirish</strong> (6-dars) —
mustaqil ish birliklarini bir-biriga aralashtirib yubormaslik kerak.</li>
<li><strong>Core va ORM'ni chalkashtirish</strong> (1-dars) — bulk operatsiya
uchun ORM, bitta obyekt uchun Core ishlatish — ikkalasi ham noto'g'ri
tanlov bo'lishi mumkin, kontekstga qarab tanlanadi.</li>
</ul>

<h3>Bu darsning loyihasi — hammasi birlashadi</h3>
<p>Bugungi amaliy loyihada siz kichik, lekin TO'LIQ domenni
modellashtirasiz: talaba fikr-mulohaza (feedback) tizimi. Bu loyihada
0-6-darslarning barcha tushunchalari kerak bo'ladi — model yozish,
munosabat, to'g'ri yuklash strategiyasi va tranzaksiya xavfsizligi. Bu —
"nazariyani bilaman" bilan "amalda to'g'ri qo'llay olaman" orasidagi
farqni ko'rsatadigan checkpoint.</p>

<h3>Keyingi bosqichga tayyorgarlik</h3>
<p>8-darsdan boshlab e'tibor modeldan — migratsiyaga o'tadi: "modelni
qanday yozish" emas, "production bazasini modelga MOS qilib QANDAY
o'zgartirish" savoliga javob beriladi. Bu ikkinchi yarim — Alembic,
xavfsiz migratsiyalar, backfill, zero-downtime va performance — birinchi
yarimda o'rgangan modellaringizni HAQIQIY bazaga aylantirish haqida.</p>

<h3>O'z-o'zini tekshirish ro'yxati (self-check)</h3>
<p>Loyihangizni topshirishdan oldin quyidagi savollarga "ha" deb javob
bera olishingiz kerak: Modelingizda har bir FOREIGN KEY uchun
<code>ondelete=</code> aniq ko'rsatilganmi? Munosabatlarning har biri
haqiqatan ham kerakmi, yoki ba'zilari ortiqcha (3-dars oxiridagi
ogohlantirish)? So'rovlaringizda ro'yxat qaytaradigan joylarda
<code>selectinload()</code> bormi? Tranzaksiya ichida bir nechta jadvalga
yozayotgan bo'lsangiz, xato holatida <code>rollback()</code> chaqirilishini
tekshirdingizmi? Bu ro'yxat — checkpoint'ning haqiqiy maqsadi: bilim emas,
odat sifatida tekshirish.</p>

<h3>Nega aynan "feedback tizimi" tanlandi</h3>
<p>Bu domen ataylab tanlangan: unda one-to-many EMAS, balki ikkita
mustaqil FOREIGN KEY (student_id va lesson_id) bitta jadvalda birlashadi,
composite UniqueConstraint talab qiladi, va agregatsiya (o'rtacha baho)
tabiiy ravishda kerak bo'ladi. Bu — 2, 3, 4 va 6-darslarning barcha
tushunchalarini majburiy ravishda birlashtiruvchi minimal, lekin real
misol.</p>

<h3>Har bir darsning bir jumlada xulosasi</h3>
<ul>
<li><strong>0-dars:</strong> ORM — bazaning qator/jadval modelini Python'ning
obyekt/klass modeliga bog'lovchi qatlam.</li>
<li><strong>1-dars:</strong> Core — SQL qurish tili, ORM — uning ustidagi
xarita; Engine bitta, Session har so'rov uchun yangi.</li>
<li><strong>2-dars:</strong> mapped_column bitta joyda ham ustunni, ham
Python turini belgilaydi; server_default ORM'ni chetlab o'tgan yozuvlar
uchun ham ishlaydi.</li>
<li><strong>3-dars:</strong> relationship() ustun emas — FOREIGN KEY yoki
bog'lovchi jadval ustiga qurilgan navigatsiya.</li>
<li><strong>4-dars:</strong> select().where().join().order_by() — 107-kursdagi
SQL'ning to'g'ridan-to'g'ri Python ifodasi.</li>
<li><strong>5-dars:</strong> lazy loading siklda ishlatilsa N+1 beradi;
selectinload() buni 2 ta so'rovga tushiradi.</li>
<li><strong>6-dars:</strong> Session — Unit of Work; flush ≠ commit;
IntegrityError ba'zan kutilgan poyga natijasi, xato emas.</li>
</ul>
""".strip()

L7_TEXT_RU = """
<h3>Половина пути — что вы уже освоили</h3>
<p>В уроках 0-6 вы прошли всю "базовую" часть работы с ORM: начиная с того,
что такое impedance mismatch (урок 0), два слоя SQLAlchemy (урок 1),
декларативные модели и mapping (урок 2), связи (урок 3), запросы (урок 4),
N+1 и eager/lazy loading (урок 5), и наконец управление транзакциями/
Session (урок 6). Это — полный "ежедневный цикл" работы с ORM: написание
модели -> построение связи -> написание запроса -> эффективная загрузка ->
безопасное сохранение. Следующие уроки 8-11 переходят к совершенно другой
теме — миграциям, поэтому этот checkpoint — последняя возможность закрепить
основы перед продвижением дальше.</p>

<h3>Самые частые ошибки — пересмотрите ещё раз</h3>
<ul>
<li><strong>Восприятие relationship() как колонки</strong> (уроки 2-3) — он
ставится не ВМЕСТО FOREIGN KEY, а ПОВЕРХ него.</li>
<li><strong>Использование lazy loading в цикле</strong> (урок 5) — самая
частая причина N+1; не пишите production-код без selectinload().</li>
<li><strong>Вызов commit() слишком поздно или слишком рано</strong> (урок 6)
— нельзя смешивать независимые единицы работы друг с другом.</li>
<li><strong>Путаница Core и ORM</strong> (урок 1) — использование ORM для
массовой операции или Core для одного объекта — оба могут быть неверным
выбором, зависит от контекста.</li>
</ul>

<h3>Проект этого урока — всё объединяется</h3>
<p>В сегодняшнем практическом проекте вы смоделируете небольшой, но ПОЛНЫЙ
домен: систему обратной связи (feedback) студентов. В этом проекте
понадобятся все понятия уроков 0-6 — написание модели, связи, правильная
стратегия загрузки и безопасность транзакций. Это checkpoint, показывающий
разницу между "я знаю теорию" и "я умею правильно применять её на
практике".</p>

<h3>Подготовка к следующему этапу</h3>
<p>Начиная с урока 8 фокус смещается с модели на миграцию: вопрос уже не
"как написать модель", а "как ИЗМЕНИТЬ production-базу так, чтобы она
СООТВЕТСТВОВАЛА модели". Эта вторая половина — Alembic, безопасные
миграции, backfill, zero-downtime и производительность — про превращение
изученных вами моделей в РЕАЛЬНУЮ базу данных.</p>

<h3>Чек-лист самопроверки (self-check)</h3>
<p>Перед сдачей проекта вы должны быть в состоянии ответить "да" на
следующие вопросы: явно ли указан <code>ondelete=</code> для каждого
FOREIGN KEY в вашей модели? Действительно ли нужна каждая связь, или
некоторые из них избыточны (предупреждение в конце урока 3)? Есть ли
<code>selectinload()</code> там, где запрос возвращает список? Если вы
пишете в несколько таблиц внутри транзакции, проверили ли вы вызов
<code>rollback()</code> при ошибке? Этот чек-лист — истинная цель
checkpoint'а: не знание, а проверка как привычка.</p>

<h3>Почему выбрана именно "система обратной связи"</h3>
<p>Этот домен выбран намеренно: в нём НЕ one-to-many, а два независимых
FOREIGN KEY (student_id и lesson_id) объединяются в одной таблице,
требуется составной UniqueConstraint, и естественным образом нужна
агрегация (средняя оценка). Это минимальный, но реальный пример,
обязательно объединяющий все понятия уроков 2, 3, 4 и 6.</p>

<h3>Итог каждого урока одной фразой</h3>
<ul>
<li><strong>Урок 0:</strong> ORM — слой, связывающий модель строк/таблиц
базы с моделью объектов/классов Python.</li>
<li><strong>Урок 1:</strong> Core — язык построения SQL, ORM — карта поверх
него; Engine один, Session новая на каждый запрос.</li>
<li><strong>Урок 2:</strong> mapped_column в одном месте определяет и
колонку, и тип Python; server_default работает и для записей в обход
ORM.</li>
<li><strong>Урок 3:</strong> relationship() не колонка — навигация,
построенная поверх FOREIGN KEY или связующей таблицы.</li>
<li><strong>Урок 4:</strong> select().where().join().order_by() — прямое
выражение на Python SQL из курса 107.</li>
<li><strong>Урок 5:</strong> lazy loading в цикле даёт N+1; selectinload()
сводит это к 2 запросам.</li>
<li><strong>Урок 6:</strong> Session — Unit of Work; flush ≠ commit;
IntegrityError иногда ожидаемый результат гонки, а не ошибка.</li>
</ul>

<p>Держите этот список под рукой во время работы над сегодняшним
проектом — каждая строка соответствует конкретному разделу кода в
модуле LessonFeedback ниже. Если какой-то пункт непонятен, вернитесь к
соответствующему уроку перед тем, как приступать к практике.</p>
""".strip()

L7_CODE = """
# ============================================================
# Bugungi loyiha uchun tayanch: barcha 0-6-darslar tushunchalari
# bitta kichik domenda — talaba fikr-mulohaza (feedback) tizimi
# ============================================================
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

# --- 2-dars: model + mapping ---
class LessonFeedback(Base):
    __tablename__ = "lesson_feedback_r1"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- 3-dars: munosabat ---
    student: Mapped["Student"] = relationship(back_populates="feedback_entries")
    lesson: Mapped["Lesson"] = relationship(back_populates="feedback_entries")


# --- 4+5-dars: to'g'ri so'rov + eager loading ---
async def get_lesson_feedback(db, lesson_id: int) -> List[LessonFeedback]:
    stmt = (
        select(LessonFeedback)
        .where(LessonFeedback.lesson_id == lesson_id)
        .order_by(LessonFeedback.created_at.desc())
        .options(selectinload(LessonFeedback.student))   # N+1'ning oldini olish
    )
    return (await db.execute(stmt)).scalars().all()


# --- 6-dars: tranzaksiya xavfsizligi ---
from sqlalchemy.exc import IntegrityError

async def submit_feedback(db, student_id: int, lesson_id: int, rating: int, comment: str):
    db.add(LessonFeedback(student_id=student_id, lesson_id=lesson_id, rating=rating, comment=comment))
    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()   # masalan bitta talaba bitta darsga bitta fikr — takroriy urinish
        return False


# --- 4-dars: agregatsiya — o'rtacha bahoni hisoblash ---
from sqlalchemy import func as sa_func

async def average_rating(db, lesson_id: int) -> float:
    return (await db.execute(
        select(sa_func.avg(LessonFeedback.rating)).where(LessonFeedback.lesson_id == lesson_id)
    )).scalar_one() or 0.0


# ============================================================
# Self-check: N+1 yo'qligini echo=True bilan qo'lda tekshirish
# ============================================================
# debug_engine = create_async_engine(DATABASE_URL, echo=True)
# feedback_list = await get_lesson_feedback(db, lesson_id=41)
# for f in feedback_list:
#     print(f.student.username, f.rating)   # selectinload tufayli YANGI so'rov YO'Q
#
# Konsolda ko'rilishi kerak: aynan IKKITA SELECT (LessonFeedback + Student
# IN(...)), feedback yozuvlari sonidan qat'iy nazar. Agar ko'proq SELECT
# ko'rinsa — bu selectinload() unutilgan yoki noto'g'ri joyga qo'yilgan
# degani.

# ============================================================
# Self-check: har bir dars uchun qisqa "yaxshi/yomon" kod solishtiruvi
# ============================================================
# 3-dars — relationship() haqiqatan kerakmi?
# YOMON: faqat count() uchun butun ro'yxatni yuklash
bad_count = len((await db.execute(select(LessonFeedback).where(LessonFeedback.lesson_id == 41))).scalars().all())
# YAXSHI: to'g'ridan-to'g'ri COUNT() ishlatish, obyekt yuklamasdan
good_count = (await db.execute(select(func.count(LessonFeedback.id)).where(LessonFeedback.lesson_id == 41))).scalar_one()

# 6-dars — mustaqil ish birliklarini aralashtirmaslik
# YOMON: bitta katta tranzaksiyada bog'liq bo'lmagan ikkita amal
# YAXSHI: har biri o'z commit()iga ega (yuqoridagi submit_feedback misoli kabi)

# ============================================================
# LessonFeedback modulining to'liq xulosasi — barcha qismlar birga
# ============================================================
# 1. Model (2-dars): LessonFeedback, UniqueConstraint(student_id, lesson_id) bilan
# 2. Munosabatlar (3-dars): student/lesson, back_populates orqali
# 3. So'rov (4-dars): select().where().order_by() sana bo'yicha tartiblash bilan
# 4. Eager loading (5-dars): selectinload(LessonFeedback.student) — N+1 o'rniga 2 so'rov
# 5. Tranzaksiya (6-dars): submit_feedback()da try/except IntegrityError + rollback()
# 6. Agregatsiya (4-dars): average_rating()da func.avg()
#
# Agar yechimingizda shu oltita bandning biri yetishmasa — loyihani
# topshirishdan oldin tegishli darsga qaytib chiqing.

# ============================================================
# N+1 uchun mini-test — o'zingiz ishga tushira oladigan oddiy tekshiruv
# ============================================================
import logging

def count_queries_during(coro_factory):
    \"\"\"Berilgan korutina ishlashi davomida bajarilgan SQL so'rovlari
    sonini SQLAlchemy Engine loglarini o'qib hisoblaydi.\"\"\"
    count = 0

    class _CountingHandler(logging.Handler):
        def emit(self, record):
            nonlocal count
            if "SELECT" in record.getMessage() or "INSERT" in record.getMessage():
                count += 1

    logger = logging.getLogger("sqlalchemy.engine")
    handler = _CountingHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        return count
    finally:
        logger.removeHandler(handler)

# get_lesson_feedback() uchun kutilgan natija: AYNAN 2 ta so'rov
# (LessonFeedback + Student IN(...) orqali), yozuvlar sonidan qat'iy
# nazar — agar ko'proq chiqsa, demak biror joyda selectinload() unutilgan.
""".strip()

L7_CODE_RU = """
# ============================================================
# Основа для сегодняшнего проекта: понятия уроков 0-6 в одном
# небольшом домене — система обратной связи (feedback) студентов
# ============================================================
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

# --- Урок 2: модель + mapping ---
class LessonFeedback(Base):
    __tablename__ = "lesson_feedback_r1"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Урок 3: связь ---
    student: Mapped["Student"] = relationship(back_populates="feedback_entries")
    lesson: Mapped["Lesson"] = relationship(back_populates="feedback_entries")


# --- Уроки 4+5: правильный запрос + eager loading ---
async def get_lesson_feedback(db, lesson_id: int) -> List[LessonFeedback]:
    stmt = (
        select(LessonFeedback)
        .where(LessonFeedback.lesson_id == lesson_id)
        .order_by(LessonFeedback.created_at.desc())
        .options(selectinload(LessonFeedback.student))   # предотвращение N+1
    )
    return (await db.execute(stmt)).scalars().all()


# --- Урок 6: безопасность транзакции ---
from sqlalchemy.exc import IntegrityError

async def submit_feedback(db, student_id: int, lesson_id: int, rating: int, comment: str):
    db.add(LessonFeedback(student_id=student_id, lesson_id=lesson_id, rating=rating, comment=comment))
    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()   # например один студент — один урок — одна оценка, повторная попытка
        return False


# --- Урок 4: агрегация — вычисление средней оценки ---
from sqlalchemy import func as sa_func

async def average_rating(db, lesson_id: int) -> float:
    return (await db.execute(
        select(sa_func.avg(LessonFeedback.rating)).where(LessonFeedback.lesson_id == lesson_id)
    )).scalar_one() or 0.0


# ============================================================
# Self-check: вручную проверить отсутствие N+1 через echo=True
# ============================================================
# debug_engine = create_async_engine(DATABASE_URL, echo=True)
# feedback_list = await get_lesson_feedback(db, lesson_id=41)
# for f in feedback_list:
#     print(f.student.username, f.rating)   # благодаря selectinload — НОВОГО запроса нет
#
# В консоли должно быть видно РОВНО ДВА SELECT (LessonFeedback + Student
# IN(...)), независимо от числа записей feedback. Если SELECT больше —
# значит selectinload() забыт или поставлен не в том месте.

# ============================================================
# Self-check: короткое сравнение "плохо/хорошо" для каждого урока
# ============================================================
# Урок 3 — действительно ли нужен relationship()?
# ПЛОХО: загружать весь список только ради count()
bad_count = len((await db.execute(select(LessonFeedback).where(LessonFeedback.lesson_id == 41))).scalars().all())
# ХОРОШО: использовать COUNT() напрямую, не загружая объекты
good_count = (await db.execute(select(func.count(LessonFeedback.id)).where(LessonFeedback.lesson_id == 41))).scalar_one()

# Урок 6 — не смешивать независимые единицы работы
# ПЛОХО: два несвязанных действия в одной большой транзакции
# ХОРОШО: у каждого свой commit() (как в примере submit_feedback выше)

# ============================================================
# Полная сводка модуля LessonFeedback — все части вместе
# ============================================================
# 1. Модель (урок 2): LessonFeedback с UniqueConstraint(student_id, lesson_id)
# 2. Связи (урок 3): student/lesson через back_populates
# 3. Запрос (урок 4): select().where().order_by() с сортировкой по дате
# 4. Eager loading (урок 5): selectinload(LessonFeedback.student) — 2 запроса
#    вместо N+1
# 5. Транзакция (урок 6): try/except IntegrityError + rollback() в
#    submit_feedback()
# 6. Агрегация (урок 4): func.avg() в average_rating()
#
# Если в вашем решении отсутствует один из этих шести пунктов — вернитесь
# к соответствующему уроку перед сдачей проекта.

# ============================================================
# Мини-тест на N+1 — простая проверка, которую можно запустить самому
# ============================================================
import logging

def count_queries_during(coro_factory):
    \"\"\"Подсчитывает число SQL-запросов, выполненных за время работы
    переданной корутины, читая логи движка SQLAlchemy.\"\"\"
    count = 0

    class _CountingHandler(logging.Handler):
        def emit(self, record):
            nonlocal count
            if "SELECT" in record.getMessage() or "INSERT" in record.getMessage():
                count += 1

    logger = logging.getLogger("sqlalchemy.engine")
    handler = _CountingHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        return count
    finally:
        logger.removeHandler(handler)

# Ожидание для get_lesson_feedback(): РОВНО 2 запроса (LessonFeedback +
# Student через IN(...)), независимо от числа записей — если получилось
# больше, значит selectinload() где-то забыт.
""".strip()

L7_TASK = {
    "task_title": "Checkpoint loyiha: LessonFeedback tizimi",
    "task_title_ru": "Проект-checkpoint: система LessonFeedback",
    "task_description": (
        "0-6-darslarda o'rgangan barcha tushunchalarni birlashtirib, to'liq "
        "LessonFeedback modulini yozing: (1) model — student_id, lesson_id, "
        "rating (1-5), comment, (student_id, lesson_id) uchun "
        "UniqueConstraint; (2) ikkala tomonlama relationship() (Student va "
        "Lesson bilan); (3) get_lesson_feedback() — selectinload() bilan "
        "N+1'siz; (4) submit_feedback() — IntegrityError'ni to'g'ri "
        "ushlaydigan tranzaksiya xavfsizligi bilan; (5) average_rating() — "
        "func.avg() bilan agregatsiya."
    ),
    "task_description_ru": (
        "Объединив все понятия из уроков 0-6, напишите полный модуль "
        "LessonFeedback: (1) модель — student_id, lesson_id, rating (1-5), "
        "comment, UniqueConstraint на (student_id, lesson_id); (2) "
        "двусторонний relationship() (со Student и Lesson); (3) "
        "get_lesson_feedback() — без N+1, через selectinload(); (4) "
        "submit_feedback() — с безопасностью транзакции, корректно ловящий "
        "IntegrityError; (5) average_rating() — агрегация через func.avg()."
    ),
    "task_requirements": (
        "1) To'liq model kodi (Mapped[...] annotatsiyalari bilan). 2) "
        "UniqueConstraint __table_args__ orqali. 3) Kamida uchta funksiya: "
        "get_lesson_feedback, submit_feedback, average_rating. 4) Har bir "
        "funksiyada qaysi darsning tushunchasi ishlatilganini izohda "
        "ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Полный код модели (с аннотациями Mapped[...]). 2) "
        "UniqueConstraint через __table_args__. 3) Минимум три функции: "
        "get_lesson_feedback, submit_feedback, average_rating. 4) В "
        "комментарии к каждой функции укажите, понятие какого урока "
        "используется."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 6,
}

L7_SAMPLE = {
    "title": "Namuna: to'liq LessonFeedback moduli",
    "description": "0-6-darslarning barcha tushunchalarini birlashtiruvchi to'liq, ishga tayyor modul: model, munosabat, so'rov, tranzaksiya.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "lesson_feedback.py",
            "language": "python",
            "code": (
                "from typing import List, Optional\n"
                "from datetime import datetime\n"
                "from sqlalchemy import Integer, Text, ForeignKey, DateTime, UniqueConstraint, func, select\n"
                "from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload\n"
                "from sqlalchemy.exc import IntegrityError\n\n\n"
                "class LessonFeedback(Base):\n"
                "    __tablename__ = \"lesson_feedback\"\n"
                "    __table_args__ = (UniqueConstraint(\"student_id\", \"lesson_id\"),)\n\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    student_id: Mapped[int] = mapped_column(ForeignKey(\"students.id\", ondelete=\"CASCADE\"))\n"
                "    lesson_id: Mapped[int] = mapped_column(ForeignKey(\"lessons.id\", ondelete=\"CASCADE\"))\n"
                "    rating: Mapped[int] = mapped_column(Integer)\n"
                "    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)\n"
                "    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())\n\n"
                "    student: Mapped[\"Student\"] = relationship(back_populates=\"feedback_entries\")\n"
                "    lesson: Mapped[\"Lesson\"] = relationship(back_populates=\"feedback_entries\")\n\n\n"
                "async def get_lesson_feedback(db, lesson_id: int) -> List[LessonFeedback]:\n"
                "    stmt = (\n"
                "        select(LessonFeedback)\n"
                "        .where(LessonFeedback.lesson_id == lesson_id)\n"
                "        .order_by(LessonFeedback.created_at.desc())\n"
                "        .options(selectinload(LessonFeedback.student))\n"
                "    )\n"
                "    return (await db.execute(stmt)).scalars().all()\n\n\n"
                "async def submit_feedback(db, student_id: int, lesson_id: int, rating: int, comment: str) -> bool:\n"
                "    db.add(LessonFeedback(student_id=student_id, lesson_id=lesson_id, rating=rating, comment=comment))\n"
                "    try:\n"
                "        await db.commit()\n"
                "        return True\n"
                "    except IntegrityError:\n"
                "        await db.rollback()\n"
                "        return False\n\n\n"
                "async def average_rating(db, lesson_id: int) -> float:\n"
                "    return (await db.execute(\n"
                "        select(func.avg(LessonFeedback.rating)).where(LessonFeedback.lesson_id == lesson_id)\n"
                "    )).scalar_one() or 0.0\n"
            ),
        },
    ],
}

L7_EXERCISES = [
    {
        "title": "Eng katta xato manbai",
        "title_ru": "Главный источник ошибок",
        "description": "0-6-darslarda o'rganilganlar orasida N+1'ning ENG KENG TARQALGAN sababi nima?",
        "description_ru": "Что из изученного в уроках 0-6 является САМОЙ РАСПРОСТРАНЁННОЙ причиной N+1?",
        "exercise_type": "multiple_choice",
        "options": [
            "Siklda lazy relationship()ga eager loading'siz murojaat qilish",
            "__tablename__ ni noto'g'ri yozish",
            "Core'da Table() e'lon qilish",
            "db.flush() chaqirish",
        ],
        "options_ru": [
            "Обращение к lazy relationship() в цикле без eager loading",
            "Неправильное написание __tablename__",
            "Объявление Table() в Core",
            "Вызов db.flush()",
        ],
        "correct_answers": "A",
        "hint": "5-darsni eslang — sukut bo'yicha xatti-harakat lazy.",
        "hint_ru": "Вспомните урок 5 — поведение по умолчанию lazy.",
        "explanation": "lazy loading'ni siklda ishlatish — ORM'dagi N+1'ning eng keng tarqalgan sababi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "O'z so'zlaringiz bilan: flush vs commit",
        "title_ru": "Своими словами: flush против commit",
        "description": "flush() va commit() orasidagi farqni, ID olish misoli bilan, o'z so'zlaringiz bilan tushuntiring.",
        "description_ru": "Объясните своими словами разницу между flush() и commit(), приведя пример с получением ID.",
        "exercise_type": "text_input",
        "expected_answer": (
            "flush() o'zgarishlarni bazaga yuboradi (INSERT/UPDATE bajaradi) lekin "
            "tranzaksiyani yakunlamaydi — hali rollback mumkin; shu bosqichda "
            "yangi obyektning ID'si allaqachon mavjud bo'ladi. commit() esa avval "
            "flush qiladi, so'ngra tranzaksiyani COMMIT bilan yakunlaydi — bundan "
            "keyin rollback qilib bo'lmaydi."
        ),
        "hint": "ID qachon mavjud bo'lishini va tranzaksiya qachon 'yakunlanmas' holatga o'tishini o'ylang.",
        "hint_ru": "Подумайте, когда появляется ID и когда транзакция становится 'необратимой'.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 8 — Migratsiyalarga kirish: Alembic nima va nega kerak
# ---------------------------------------------------------------------------

L8_TEXT = """
<h3>2-darsdagi eslatmani eslang: model o'zgarishi baza o'zgarishi EMAS</h3>
<p>2-darsda ta'kidlagan edik: <code>mapped_column(...)</code>ga yangi
ustun qo'shish faqat Python klassini o'zgartiradi, production bazasidagi
haqiqiy jadval esa o'zgarmaydi. Bu ikkisi orasidagi ko'prik —
<strong>migratsiya</strong>. Migratsiya — bu "bazani hozirgi holatdan
kerakli holatga qanday o'zgartirish" haqidagi aniq, versiyalangan
buyruqlar to'plami. Bu platformada bu vazifani <strong>Alembic</strong>
bajaradi — SQLAlchemy'ning rasmiy migratsiya vositasi, va
<code>backend/alembic/versions/</code> papkasida 60 dan ortiq haqiqiy
migratsiya fayli mavjud — bu platformaning butun sxema tarixi.</p>

<h3>Nega qo'lda ALTER TABLE yozish yetarli emas</h3>
<p>Production bazasiga to'g'ridan-to'g'ri <code>ALTER TABLE</code>
yozish bir nechta muammoni keltirib chiqaradi: (1) qaysi o'zgarish qachon
qo'llanilgani hech qayerda yozilmaydi — 6 oydan keyin "bu ustun qachon va
nega qo'shilgan" savoliga javob yo'q; (2) development, staging va
production bazalari sinxronlanmay qoladi — kimdir bitta joyda ustun
qo'shadi, boshqa joyda unutadi; (3) rollback (orqaga qaytarish) qo'lda
yozilmagan bo'lsa, xato ro'y berganda tuzatish imkoni yo'q. Alembic
bularning barchasini hal qiladi: har bir o'zgarish bitta fayl, versiya
ID'si bilan, <code>upgrade()</code> VA <code>downgrade()</code> funksiyalari
bilan.</p>

<h3>Revision zanjiri — har bir migratsiya oldingisiga bog'langan</h3>
<p>Har bir Alembic fayli ikkita muhim maydonga ega: <code>revision</code>
(shu faylning o'zi ID'si) va <code>down_revision</code> (undan OLDINGI
migratsiyaning ID'si). Bu — bog'langan ro'yxat (linked list): Alembic har
doim qaysi migratsiyalar allaqachon qo'llanilgani va qaysilari hali
qo'llanilmaganini shu zanjir orqali biladi. Bu platformaning haqiqiy
misolida: <code>ff2233445566</code> (achievements'ga category/icon
qo'shish) <code>down_revision = 'ee11223344aa'</code>ga ishora qiladi —
demak bu migratsiya faqat o'shandan keyin qo'llaniladi.</p>

<h3>upgrade() va downgrade() — ikki yo'nalishli o'zgarish</h3>
<p>Har bir migratsiya ikkita funksiyaga ega: <code>upgrade()</code> —
o'zgarishni QO'LLASH (masalan ustun qo'shish), <code>downgrade()</code> —
uni ORQAGA QAYTARISH (masalan ustunni o'chirish). Bu platformaning haqiqiy
<code>widen_phone_column_to_50</code> migratsiyasida bu naqsh aniq
ko'rinadi: <code>upgrade()</code> ustun uzunligini 20'dan 50'ga
kengaytiradi, <code>downgrade()</code> esa uni qaytadan 20'ga toraytiradi
— ikkalasi ham <code>op.alter_column()</code>ning bir xil chaqiruvi,
faqat <code>type_=</code> va <code>existing_type=</code> almashtirilgan.</p>

<h3>autogenerate — yordamchi, lekin ko'r-ko'rona ishonib bo'lmaydigan vosita</h3>
<p>Alembic <code>alembic revision --autogenerate</code> orqali modellar va
haqiqiy baza sxemasini solishtirib, farqni avtomatik migratsiya sifatida
taklif qila oladi. Bu FOYDALI, lekin har doim QO'LDA tekshirilishi shart:
autogenerate ustun nomi o'zgarishini har doim "eski ustunni o'chirish +
yangi ustun qo'shish" deb tushunadi — bu esa MA'LUMOT YO'QOTISHGA olib
keladi (o'zgartirish o'rniga o'chirish+yaratish). 10-darsda bu xato aynan
shu platformaning haqiqiy migratsiya tarixidan misol bilan ko'rsatiladi.</p>

<h3>Migratsiyalar odatda SINXRON ishlaydi, hatto async ilovada ham</h3>
<p>Bu platformaning ilova qatlami to'liq asinxron (asyncpg, AsyncSession)
bo'lsa-da, Alembic migratsiyalari odatda SINXRON drayver (masalan
<code>psycopg2</code>) orqali ishga tushiriladi. Buning sababi oddiy:
migratsiya — bitta martalik, ketma-ket bajariladigan operatsiya, unda
parallellik yoki kutish samaradorligi kerak emas, aksincha soddalik va
ishonchlilik muhimroq. Shuning uchun <code>alembic.ini</code> ko'pincha
ilovaning asosiy <code>DATABASE_URL</code>'idan farqli, sinxron
ulanish satrini ishlatadi.</p>

<h3>Migratsiyani qanday sinash kerak — production'dan oldin</h3>
<p>Har qanday migratsiya avval mahalliy yoki staging bazada sinaladi:
<code>alembic upgrade head</code> keyin <code>alembic downgrade -1</code>
keyin yana <code>alembic upgrade head</code> — bu "round-trip" tekshiruvi
downgrade()ning haqiqatan ham to'g'ri yozilganini (masalan barcha
ustunlar/constraint'lar to'g'ri qaytarilishini) tasdiqlaydi. Bu qadamni
o'tkazib yuborish — 10-darsda ko'radigan "orqaga qaytarib bo'lmaydigan
migratsiya" xatosining eng keng tarqalgan sababi.</p>
""".strip()

L8_TEXT_RU = """
<h3>Вспомните напоминание из урока 2: изменение модели — не изменение базы</h3>
<p>В уроке 2 подчёркивалось: добавление нового столбца в
<code>mapped_column(...)</code> изменяет только класс Python, реальная
таблица в production-базе не меняется. Мост между ними —
<strong>миграция</strong>. Миграция — это точный, версионированный набор
команд "как изменить базу из текущего состояния в нужное". На этой
платформе эту задачу выполняет <strong>Alembic</strong> — официальный
инструмент миграций SQLAlchemy, и в папке
<code>backend/alembic/versions/</code> находится более 60 реальных файлов
миграций — вся история схемы этой платформы.</p>

<h3>Почему недостаточно писать ALTER TABLE вручную</h3>
<p>Написание <code>ALTER TABLE</code> напрямую в production-базе порождает
несколько проблем: (1) нигде не записано, какое изменение когда было
применено — через 6 месяцев нет ответа на вопрос "когда и почему добавлена
эта колонка"; (2) базы development, staging и production рассинхронизируются
— кто-то добавляет колонку в одном месте, забывает в другом; (3) если
откат (rollback) не написан вручную, при ошибке нет способа исправить.
Alembic решает всё это: каждое изменение — отдельный файл с ID версии,
функциями <code>upgrade()</code> И <code>downgrade()</code>.</p>

<h3>Цепочка revision — каждая миграция связана с предыдущей</h3>
<p>Каждый файл Alembic имеет два важных поля: <code>revision</code> (ID
самого этого файла) и <code>down_revision</code> (ID ПРЕДЫДУЩЕЙ миграции).
Это связный список (linked list): Alembic всегда знает через эту цепочку,
какие миграции уже применены, а какие ещё нет. В реальном примере этой
платформы: <code>ff2233445566</code> (добавление category/icon в
achievements) ссылается на <code>down_revision = 'ee11223344aa'</code> —
значит эта миграция применяется только после той.</p>

<h3>upgrade() и downgrade() — изменение в двух направлениях</h3>
<p>Каждая миграция имеет две функции: <code>upgrade()</code> — ПРИМЕНИТЬ
изменение (например добавить колонку), <code>downgrade()</code> —
ОТКАТИТЬ его (например удалить колонку). В реальной миграции
<code>widen_phone_column_to_50</code> этой платформы этот паттерн виден
явно: <code>upgrade()</code> расширяет длину колонки с 20 до 50,
<code>downgrade()</code> же снова сужает её до 20 — оба используют один и
тот же вызов <code>op.alter_column()</code>, только с переставленными
<code>type_=</code> и <code>existing_type=</code>.</p>

<h3>autogenerate — полезный, но не заслуживающий слепого доверия инструмент</h3>
<p>Alembic через <code>alembic revision --autogenerate</code> может
сравнить модели и реальную схему базы и автоматически предложить разницу
как миграцию. Это ПОЛЕЗНО, но всегда требует РУЧНОЙ проверки: autogenerate
всегда воспринимает переименование колонки как "удалить старую колонку +
добавить новую" — а это приводит к ПОТЕРЕ ДАННЫХ (удаление+создание вместо
изменения). В уроке 10 эта ошибка будет показана на реальном примере из
истории миграций именно этой платформы.</p>

<h3>Миграции обычно выполняются СИНХРОННО, даже в асинхронном приложении</h3>
<p>Хотя слой приложения этой платформы полностью асинхронный (asyncpg,
AsyncSession), миграции Alembic обычно запускаются через СИНХРОННЫЙ
драйвер (например <code>psycopg2</code>). Причина проста: миграция — это
одноразовая, последовательная операция, где параллелизм или эффективность
ожидания не нужны, важнее простота и надёжность. Поэтому
<code>alembic.ini</code> часто использует синхронную строку подключения,
отличную от основного <code>DATABASE_URL</code> приложения.</p>

<h3>Как тестировать миграцию — перед production</h3>
<p>Любая миграция сначала тестируется на локальной или staging базе:
<code>alembic upgrade head</code>, затем <code>alembic downgrade -1</code>,
затем снова <code>alembic upgrade head</code> — эта проверка "туда-обратно"
подтверждает, что downgrade() действительно написан правильно (например
все колонки/ограничения корректно восстанавливаются). Пропуск этого шага —
самая частая причина ошибки "необратимой миграции", которую увидим в
уроке 10.</p>

<h3>Именование файлов миграций — читаемость истории схемы</h3>
<p>Alembic автоматически генерирует имя файла из revision ID и сообщения
(<code>-m "widen phone column to 50"</code>). Осмысленное сообщение —
не формальность: через год именно оно поможет быстро понять историю
схемы при просмотре <code>alembic history --verbose</code>, не открывая
каждый файл по отдельности.</p>
""".strip()

L8_CODE = """
# ============================================================
# HAQIQIY misol: backend/alembic/versions/ff0011223344_widen_phone_column_to_50.py
# (aynan shu fayl, izohlar qo'shilgan)
# ============================================================
\"\"\"widen phone column to 50

Revision ID: aa11bb22cc33
Revises: aabb11223344
Create Date: 2026-07-10

Gennis API'dan keladigan telefon raqamlari eski 20-belgili chegaradan
oshib ketishi mumkin, bu esa login paytida StringDataRightTruncationError
xatosiga olib keladi.
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff0011223344'          # shu faylning o'ziga xos ID'si
down_revision = 'aabb11223344'     # bu migratsiya QAYSI migratsiyadan keyin keladi


def upgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(20),   # bazadagi HOZIRGI holat
        type_=sa.String(50),           # YANGI holat
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(50),   # HOZIRGI (upgrade'dan keyingi) holat
        type_=sa.String(20),           # ORQAGA qaytariladigan holat
        existing_nullable=True,
    )

# ============================================================
# 1) Alembic buyruqlari — kunlik ish oqimi
# ============================================================
# Yangi bo'sh migratsiya yaratish (qo'lda yozish uchun):
#   alembic revision -m "widen phone column to 50"
#
# Modelga asoslanib avtomatik migratsiya TAKLIF qildirish (QAYTA TEKSHIRISH SHART):
#   alembic revision --autogenerate -m "add is_pinned to student_notes"
#
# Barcha kutilayotgan migratsiyalarni qo'llash:
#   alembic upgrade head
#
# Bitta migratsiyani orqaga qaytarish:
#   alembic downgrade -1
#
# Hozirgi holatni ko'rish:
#   alembic current
#   alembic history --verbose

# ============================================================
# 2) Revision zanjiri — nima uchun down_revision muhim
# ============================================================
# migratsiya A: revision="aaa111", down_revision=None            (birinchi migratsiya)
# migratsiya B: revision="bbb222", down_revision="aaa111"        (A'dan keyin)
# migratsiya C: revision="ccc333", down_revision="bbb222"        (B'dan keyin)
#
# `alembic upgrade head` — A -> B -> C tartibida, ZANJIR bo'yicha qo'llaydi.
# Agar ikkita migratsiya bir xil down_revision'ga ishora qilsa (ikki
# dasturchi parallel branch'da yozgan) — Alembic "multiple heads" xatosini
# beradi, buni `alembic merge` bilan hal qilish kerak.

# ============================================================
# 3) Round-trip tekshiruvi — production'dan OLDIN har doim bajariladi
# ============================================================
#   alembic upgrade head       # yangi migratsiyani qo'llash
#   alembic downgrade -1       # orqaga qaytarish — downgrade() ishlaydimi?
#   alembic upgrade head       # yana oldinga — hech narsa buzilmadimi?
#
# Agar ikkinchi qadamda xato chiqsa (masalan downgrade() yozilmagan yoki
# noto'g'ri) — bu migratsiya production'ga HALI tayyor emas.

# ============================================================
# 4) alembic.ini — ko'pincha ilova URL'idan farqli, SINXRON ulanish
# ============================================================
# alembic.ini:
#   sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/student_platform
#
# app/db/database.py (ilovaning o'zi):
#   DATABASE_URL = postgresql+asyncpg://user:pass@localhost/student_platform
#
# Diqqat: drayver farqli (+psycopg2 vs +asyncpg), lekin baza bir xil.
# Bu ataylab — migratsiya kodi sinxron, oddiy va bashoratlanadigan bo'lishi
# uchun, ilova esa yuqori parallellik uchun asinxron qoladi.

# ============================================================
# 5) Yana bir haqiqiy misol — bu platformaning o'z tarixidan,
#    achievements jadvaliga category/icon qo'shish
# ============================================================
\"\"\"add category and icon to achievements

Revision ID: ff2233445566
Revises: ee11223344aa
Create Date: 2026-06-17
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff2233445566'
down_revision = 'ee11223344aa'


def upgrade() -> None:
    op.add_column('achievements', sa.Column('category', sa.String(50), nullable=True, server_default='general'))
    op.add_column('achievements', sa.Column('icon', sa.String(20), nullable=True, server_default='🏆'))


def downgrade() -> None:
    op.drop_column('achievements', 'icon')
    op.drop_column('achievements', 'category')

# Diqqat: downgrade() ustunlarni QO'SHISHGA teskari tartibda o'chiradi
# (avval icon, keyin category) — bu bir-biriga bog'liq har qanday
# operatsiyalar ketma-ketligi uchun umumiy qoida.

# ============================================================
# Foydali alembic history buyruqlari — sxema tarixini o'qish
# ============================================================
#   alembic history --verbose          # barcha xabarlar bilan to'liq zanjir
#   alembic history -r ee11223344aa:   # aniq revisiondan boshlab hammasi
#   alembic show ff2233445566          # aniq migratsiyaning tarkibi
#   alembic heads                       # bir nechta "bosh" borligini tekshirish
#                                        # (birlashtirilmagan parallel branch belgisi)

# ============================================================
# 6) alembic.ini — haqiqatan ishlatiladigan minimal sozlamalar to'plami
# ============================================================
# [alembic]
# script_location = alembic
# sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/student_platform
#
# [loggers]
# keys = root,sqlalchemy,alembic
#
# Diqqat: bu yerdagi sqlalchemy.url ilovaning settings.DATABASE_URL'idan
# ALOHIDA sozlanadi (odatda env.py ichida, muhit o'zgaruvchilarini
# o'qiydigan qayta yozish orqali) — bu ataylab: migratsiyalarni ilovaning
# to'liq konfiguratsiyasi mavjud bo'lmagan joyda ham (masalan alohida CI
# bosqichida) ishga tushirish mumkin bo'lishi uchun.
""".strip()

L8_CODE_RU = """
# ============================================================
# РЕАЛЬНЫЙ пример: backend/alembic/versions/ff0011223344_widen_phone_column_to_50.py
# (тот же файл, с добавленными комментариями)
# ============================================================
\"\"\"widen phone column to 50

Revision ID: aa11bb22cc33
Revises: aabb11223344
Create Date: 2026-07-10

Номера телефонов из Gennis API могут превышать старый лимит в 20 символов,
что приводит к ошибке StringDataRightTruncationError при входе.
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff0011223344'          # уникальный ID самого этого файла
down_revision = 'aabb11223344'     # ПОСЛЕ какой миграции идёт эта


def upgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(20),   # ТЕКУЩЕЕ состояние в базе
        type_=sa.String(50),           # НОВОЕ состояние
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'students', 'phone',
        existing_type=sa.String(50),   # ТЕКУЩЕЕ (после upgrade) состояние
        type_=sa.String(20),           # состояние, к которому ОТКАТЫВАЕМСЯ
        existing_nullable=True,
    )

# ============================================================
# 1) Команды Alembic — повседневный рабочий процесс
# ============================================================
# Создать новую пустую миграцию (для ручного написания):
#   alembic revision -m "widen phone column to 50"
#
# ПРЕДЛОЖИТЬ автоматическую миграцию на основе модели (ОБЯЗАТЕЛЬНО ПРОВЕРИТЬ):
#   alembic revision --autogenerate -m "add is_pinned to student_notes"
#
# Применить все ожидающие миграции:
#   alembic upgrade head
#
# Откатить одну миграцию:
#   alembic downgrade -1
#
# Посмотреть текущее состояние:
#   alembic current
#   alembic history --verbose

# ============================================================
# 2) Цепочка revision — почему важен down_revision
# ============================================================
# миграция A: revision="aaa111", down_revision=None            (первая миграция)
# миграция B: revision="bbb222", down_revision="aaa111"        (после A)
# миграция C: revision="ccc333", down_revision="bbb222"        (после B)
#
# `alembic upgrade head` — применяет в порядке A -> B -> C, по ЦЕПОЧКЕ.
# Если две миграции ссылаются на один down_revision (два разработчика
# писали в параллельных ветках) — Alembic выдаёт ошибку "multiple heads",
# её нужно решать через `alembic merge`.

# ============================================================
# 3) Проверка round-trip — всегда выполняется ПЕРЕД production
# ============================================================
#   alembic upgrade head       # применить новую миграцию
#   alembic downgrade -1       # откатить — работает ли downgrade()?
#   alembic upgrade head       # снова вперёд — ничего не сломалось?
#
# Если на втором шаге ошибка (например downgrade() не написан или неверен)
# — эта миграция ЕЩЁ НЕ готова для production.

# ============================================================
# 4) alembic.ini — часто отличается от URL приложения, СИНХРОННОЕ подключение
# ============================================================
# alembic.ini:
#   sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/student_platform
#
# app/db/database.py (само приложение):
#   DATABASE_URL = postgresql+asyncpg://user:pass@localhost/student_platform
#
# Обратите внимание: драйвер разный (+psycopg2 против +asyncpg), но база
# одна и та же. Это намеренно — чтобы код миграций оставался синхронным,
# простым и предсказуемым, а приложение оставалось асинхронным ради
# высокого параллелизма.

# ============================================================
# 5) Ещё один реальный пример из истории этой платформы —
#    достижения (achievements) с category/icon
# ============================================================
\"\"\"add category and icon to achievements

Revision ID: ff2233445566
Revises: ee11223344aa
Create Date: 2026-06-17
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff2233445566'
down_revision = 'ee11223344aa'


def upgrade() -> None:
    op.add_column('achievements', sa.Column('category', sa.String(50), nullable=True, server_default='general'))
    op.add_column('achievements', sa.Column('icon', sa.String(20), nullable=True, server_default='🏆'))


def downgrade() -> None:
    op.drop_column('achievements', 'icon')
    op.drop_column('achievements', 'category')

# Обратите внимание: downgrade() удаляет колонки в ОБРАТНОМ порядке
# добавления (сначала icon, потом category) — это общее правило для
# любой последовательности операций, зависящих друг от друга.

# ============================================================
# Полезные команды alembic history — чтение истории схемы
# ============================================================
#   alembic history --verbose          # полная цепочка со всеми сообщениями
#   alembic history -r ee11223344aa:   # всё начиная с конкретной ревизии
#   alembic show ff2233445566          # содержимое конкретной миграции
#   alembic heads                       # проверка на несколько "голов"
#                                        # (признак незамерженных параллельных веток)

# ============================================================
# 6) alembic.ini — минимальный набор реально используемых настроек
# ============================================================
# [alembic]
# script_location = alembic
# sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/student_platform
#
# [loggers]
# keys = root,sqlalchemy,alembic
#
# Обратите внимание: sqlalchemy.url здесь настраивается ОТДЕЛЬНО от
# settings.DATABASE_URL приложения (обычно через переопределение в
# env.py, читающее переменные окружения) — это намеренно, чтобы миграции
# можно было запускать даже там, где полный конфиг приложения недоступен
# (например в отдельном CI-шаге).
""".strip()

L8_TASK = {
    "task_title": "StudentNote uchun birinchi migratsiyani yozing",
    "task_title_ru": "Напишите первую миграцию для StudentNote",
    "task_description": (
        "2-darsda yozgan StudentNote modeli uchun Alembic migratsiyasini "
        "qo'lda yozing (autogenerate ishlatmasdan): jadval yaratish, ikkita "
        "FOREIGN KEY (CASCADE bilan), UniqueConstraint (student_id, "
        "lesson_id), va created_at server_default=func.now() bilan. "
        "downgrade() jadvalni to'liq o'chirishi kerak."
    ),
    "task_description_ru": (
        "Для модели StudentNote из урока 2 вручную напишите миграцию "
        "Alembic (без использования autogenerate): создание таблицы, два "
        "FOREIGN KEY (с CASCADE), UniqueConstraint (student_id, lesson_id), "
        "и created_at с server_default=func.now(). downgrade() должен "
        "полностью удалить таблицу."
    ),
    "task_requirements": (
        "1) revision/down_revision to'g'ri to'ldirilgan (down_revision "
        "sifatida oxirgi mavjud migratsiyani ko'rsating yoki placeholder "
        "yozing). 2) op.create_table() to'liq ustunlar bilan. 3) "
        "op.create_unique_constraint() yoki table_args ichida "
        "UniqueConstraint. 4) downgrade() da op.drop_table()."
    ),
    "task_requirements_ru": (
        "1) Корректно заполнены revision/down_revision (в качестве "
        "down_revision укажите последнюю существующую миграцию или "
        "плейсхолдер). 2) op.create_table() со всеми колонками. 3) "
        "op.create_unique_constraint() или UniqueConstraint внутри "
        "table_args. 4) op.drop_table() в downgrade()."
    ),
    "task_technologies": "Python, Alembic, SQLAlchemy 2.x, PostgreSQL",
    "task_deadline_days": 4,
}

L8_SAMPLE = {
    "title": "Namuna: student_notes jadvali uchun to'liq migratsiya",
    "description": "op.create_table(), FOREIGN KEY, UniqueConstraint va to'liq downgrade() bilan haqiqiy Alembic migratsiya fayli.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "xxxx_create_student_notes.py",
            "language": "python",
            "code": (
                "\"\"\"create student_notes table\n\n"
                "Revision ID: bb22cc33dd44\n"
                "Revises: ff0011223344\n"
                "Create Date: 2026-07-15\n"
                "\"\"\"\n"
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'bb22cc33dd44'\n"
                "down_revision = 'ff0011223344'\n"
                "branch_labels = None\n"
                "depends_on = None\n\n\n"
                "def upgrade() -> None:\n"
                "    op.create_table(\n"
                "        'student_notes',\n"
                "        sa.Column('id', sa.Integer(), primary_key=True),\n"
                "        sa.Column('student_id', sa.Integer(),\n"
                "                  sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),\n"
                "        sa.Column('lesson_id', sa.Integer(),\n"
                "                  sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),\n"
                "        sa.Column('note_text', sa.Text(), nullable=False),\n"
                "        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),\n"
                "        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),\n"
                "    )\n"
                "    op.create_unique_constraint(\n"
                "        'uq_student_note_per_lesson', 'student_notes', ['student_id', 'lesson_id']\n"
                "    )\n\n\n"
                "def downgrade() -> None:\n"
                "    op.drop_table('student_notes')\n"
            ),
        },
    ],
}

L8_EXERCISES = [
    {
        "title": "Migratsiya kerakligining sababi",
        "title_ru": "Почему нужна миграция",
        "description": "Qo'lda ALTER TABLE yozishning ENG KATTA muammosi nima?",
        "description_ru": "В чём САМАЯ большая проблема ручного написания ALTER TABLE?",
        "exercise_type": "multiple_choice",
        "options": [
            "O'zgarish tarixi va rollback imkoniyati yo'qoladi",
            "ALTER TABLE PostgreSQL'da umuman ishlamaydi",
            "Bu Python kodidan sekinroq ishlaydi",
            "ALTER TABLE faqat MySQL'da mavjud",
        ],
        "options_ru": [
            "Теряется история изменений и возможность отката",
            "ALTER TABLE вообще не работает в PostgreSQL",
            "Это работает медленнее, чем код Python",
            "ALTER TABLE существует только в MySQL",
        ],
        "correct_answers": "A",
        "hint": "Alembic har bir o'zgarishni versiya sifatida, upgrade/downgrade bilan saqlaydi.",
        "hint_ru": "Alembic сохраняет каждое изменение как версию, с upgrade/downgrade.",
        "explanation": "Qo'lda yozilgan ALTER TABLE hech qayerda ro'yxatga olinmaydi va orqaga qaytarish uchun alohida kod yozish kerak bo'ladi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "down_revision vazifasi",
        "title_ru": "Роль down_revision",
        "description": "down_revision maydoni nimani ko'rsatadi: bu migratsiya qaysi migratsiyadan ___ kelishini.",
        "description_ru": "Что указывает поле down_revision: после какой миграции идёт эта — ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "keyin",
        "correct_answers_ru": "после",
        "hint": "Bu — bog'langan ro'yxatdagi 'oldingi element'ga ishora.",
        "hint_ru": "Это ссылка на 'предыдущий элемент' в связном списке.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Alembic ish oqimini tartiblang",
        "title_ru": "Расположите рабочий процесс Alembic по порядку",
        "description": "Modelga yangi ustun qo'shishdan production'ga yetkazishgacha bo'lgan qadamlarni joylashtiring.",
        "description_ru": "Расположите шаги от добавления новой колонки в модель до доставки в production.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "mapped_column() bilan modelga ustun qo'shish",
            "alembic revision --autogenerate bilan migratsiya taklifini olish",
            "Taklif qilingan migratsiyani qo'lda tekshirish va tuzatish",
            "alembic upgrade head bilan bazaga qo'llash",
        ],
        "drag_items_ru": [
            "Добавить колонку в модель через mapped_column()",
            "Получить предложенную миграцию через alembic revision --autogenerate",
            "Вручную проверить и исправить предложенную миграцию",
            "Применить к базе через alembic upgrade head",
        ],
        "correct_order": [
            "mapped_column() bilan modelga ustun qo'shish",
            "alembic revision --autogenerate bilan migratsiya taklifini olish",
            "Taklif qilingan migratsiyani qo'lda tekshirish va tuzatish",
            "alembic upgrade head bilan bazaga qo'llash",
        ],
        "hint": "Avval model, keyin taklif, keyin tekshirish, oxirida qo'llash.",
        "hint_ru": "Сначала модель, потом предложение, потом проверка, в конце применение.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 9 — Xavfsiz migratsiyalar: default, backfill, zero-downtime
# ---------------------------------------------------------------------------

L9_TEXT = """
<h3>Nega "oddiy" ustun qo'shish production'da xavfli bo'lib qolishi mumkin</h3>
<p>Kichik jadvalda <code>ALTER TABLE ... ADD COLUMN new_col INTEGER NOT
NULL DEFAULT 0</code> zararsizdek tuyuladi. Ammo bu platformadagi kabi
millionlab qatorli jadvalda (masalan submissions yoki exercise_attempts)
eski PostgreSQL versiyalarida bu buyruq BUTUN jadvalni qayta yozishga
majbur qilardi — bu esa daqiqalab davom etadigan EXCLUSIVE LOCK degani,
va shu vaqt ichida jadvalga hech kim (hatto SELECT ham) murojaat qila
olmaydi. PostgreSQL 11+ versiyasida sobit (doimiy) DEFAULT qiymatlar bilan
bu muammo hal qilingan, lekin NOT NULL + DEFAULT'ning kombinatsiyasi va
eski versiyalar bilan ishlashda bu qoidani bilish hayotiy zarur.</p>

<h3>To'g'ri qadam: avval nullable, keyin backfill, keyin NOT NULL</h3>
<p>Xavfsiz naqsh uch bosqichga bo'linadi — har biri ALOHIDA migratsiya
sifatida: (1) ustunni <code>nullable=True</code> bilan qo'shish (tezkor,
qulflashsiz); (2) mavjud qatorlarni KICHIK partiyalarda (batch) yangi
qiymat bilan to'ldirish — bu <strong>backfill</strong> deb ataladi; (3)
barcha qatorlar to'ldirilgach, ustunni <code>NOT NULL</code>ga
o'zgartirish. Bu uch bosqichni BITTA migratsiyada qilish — xuddi
"oddiy" usul kabi xavfli, chunki backfill vaqtida (millionlab qatorda
daqiqalar yoki soatlar davom etishi mumkin) butun tranzaksiya ochiq qolib,
lock'ni ushlab turadi.</p>

<h3>server_default — nega u shunchaki "qulaylik" emas</h3>
<p>2-darsda ko'rgan <code>server_default</code> bu yerda hayotiy ahamiyat
kasb etadi: yangi ustun <code>server_default="0"</code> bilan qo'shilsa,
PostgreSQL yangi qatorlar uchun qiymatni METADATA darajasida (jismoniy
qayta yozishsiz) qo'llaydi — bu operatsiya deyarli DARHOL bajariladi,
qulflash minimal. Agar faqat ORM darajasidagi <code>default=</code>
ishlatilsa (server_default'siz), migratsiya paytida ORM'dan tashqarida
(masalan boshqa xizmat yoki to'g'ridan-to'g'ri SQL orqali) yozilgan
qatorlar NULL qiymat bilan qolib ketishi mumkin.</p>

<h3>Batch backfill — nega UPDATE bir yo'la emas, bo'lib-bo'lib bajariladi</h3>
<p>10 million qatorli jadvalda bitta <code>UPDATE table SET col = ...
WHERE col IS NULL</code> — bu BITTA ulkan tranzaksiya, u boshqa
yozuvlarni bloklaydi va agar uzilib qolsa, HAMMASINI qaytadan boshlash
kerak bo'ladi. Buning o'rniga <code>LIMIT 1000</code> bilan siklda,
har bitta partiyadan keyin qisqa pauza bilan (boshqa so'rovlarga vaqt
berish uchun) bajariladi — bu 11-darsda ko'radigan "connection pool"
resurslarini boshqarish tamoyili bilan bevosita bog'liq.</p>

<h3>Zero-downtime deploy — kod va sxema mos kelmasligi davri</h3>
<p>Eng muhim tushuncha: deploy paytida ESKI kod va YANGI sxema (yoki
aksincha) bir necha soniya-daqiqa davomida BIRGA ishlaydi — chunki
migratsiya va kod deploy'i bir vaqtda, bir zumda almashmaydi. Shuning
uchun qoida: migratsiya HAR DOIM ESKI kod bilan ham mos (backward
compatible) bo'lishi kerak. Masalan, ustun nomini o'zgartirish
o'rniga — yangi ustun qo'shish, ikkalasiga ham yozish, keyin eski
kodni yangisiga o'tkazish, faqat SHUNDAN KEYIN eski ustunni o'chirish —
bu 10-darsda "irreversible migration" mavzusida yanada chuqurroq
ochiladi.</p>

<h3>NOT VALID — CHECK constraint qo'shishning xavfsiz usuli</h3>
<p>Yangi <code>CHECK</code> cheklovi qo'shilganda ham xuddi shu muammo
takrorlanadi: PostgreSQL sukut bo'yicha darhol BARCHA mavjud qatorlarni
tekshiradi, bu esa katta jadvalda uzoq qulflashga olib keladi. Yechim —
ikki bosqich: avval <code>ADD CONSTRAINT ... NOT VALID</code> (bu DARHOL
bajariladi, faqat yangi/o'zgargan qatorlar tekshiriladi), so'ngra alohida
<code>VALIDATE CONSTRAINT</code> buyrug'i (bu mavjud qatorlarni tekshiradi,
lekin faqat SHARED LOCK bilan — boshqa yozuvlarni bloklamaydi). Bu naqsh —
xuddi NOT NULL uch bosqichli naqshining CHECK constraint uchun ekvivalenti.</p>

<h3>Migratsiyadan oldin qulflarni tekshirish — pg_stat_activity</h3>
<p>107-kursda o'rgangan diagnostika mahoratini bu yerda ham qo'llash
mumkin: katta migratsiyani ishga tushirishdan oldin
<code>SELECT * FROM pg_stat_activity WHERE state != 'idle'</code> orqali
hozirda qanday so'rovlar faol ekanini ko'rish tavsiya etiladi — agar
allaqachon uzoq so'rov ishlab turgan bo'lsa (masalan katta hisobot),
migratsiya SHU so'rov bilan qulf uchun poyga holatiga tushib qolishi
mumkin. Xavfsiz amaliyot: migratsiyani tinch soatda (kam trafik paytida)
va <code>lock_timeout</code> bilan ishga tushirish — agar qulf kutilganidan
uzoq davom etsa, migratsiya abadiy osilib qolish o'rniga xato bilan
to'xtaydi.</p>
""".strip()

L9_TEXT_RU = """
<h3>Почему "простое" добавление колонки может быть опасным в production</h3>
<p>На маленькой таблице <code>ALTER TABLE ... ADD COLUMN new_col INTEGER
NOT NULL DEFAULT 0</code> кажется безобидным. Но на таблице с миллионами
строк (как submissions или exercise_attempts на этой платформе) в старых
версиях PostgreSQL эта команда заставляла ПЕРЕПИСАТЬ ВСЮ таблицу — а это
означает EXCLUSIVE LOCK на несколько минут, в течение которых никто (даже
SELECT) не может обратиться к таблице. В PostgreSQL 11+ эта проблема
решена для константных значений DEFAULT, но знание комбинации NOT NULL +
DEFAULT и работы со старыми версиями жизненно важно.</p>

<h3>Правильный порядок: сначала nullable, потом backfill, потом NOT NULL</h3>
<p>Безопасный паттерн разбивается на три этапа — каждый ОТДЕЛЬНОЙ
миграцией: (1) добавить колонку с <code>nullable=True</code> (быстро, без
блокировки); (2) заполнить существующие строки МАЛЕНЬКИМИ партиями
(batch) новым значением — это называется <strong>backfill</strong>; (3)
после заполнения всех строк изменить колонку на <code>NOT NULL</code>.
Делать все три этапа В ОДНОЙ миграции так же опасно, как "простой" способ,
потому что во время backfill (может занять минуты или часы на миллионах
строк) вся транзакция остаётся открытой, удерживая блокировку.</p>

<h3>server_default — почему это не просто "удобство"</h3>
<p>Изученный в уроке 2 <code>server_default</code> здесь имеет
принципиальное значение: если новая колонка добавлена с
<code>server_default="0"</code>, PostgreSQL применяет значение для новых
строк на уровне МЕТАДАННЫХ (без физической перезаписи) — эта операция
выполняется почти МГНОВЕННО, блокировка минимальна. Если используется
только <code>default=</code> на уровне ORM (без server_default), строки,
записанные в обход ORM во время миграции (например другим сервисом или
напрямую через SQL), могут остаться с NULL.</p>

<h3>Пакетный backfill — почему UPDATE выполняется не разом, а частями</h3>
<p>На таблице с 10 миллионами строк один <code>UPDATE table SET col = ...
WHERE col IS NULL</code> — это ОДНА огромная транзакция, блокирующая
другие записи, и если она прервётся, придётся начинать ВСЁ заново. Вместо
этого выполняется в цикле с <code>LIMIT 1000</code>, с короткой паузой
после каждой партии (чтобы дать время другим запросам) — это напрямую
связано с принципом управления ресурсами "пула подключений", который
увидим в уроке 11.</p>

<h3>Zero-downtime деплой — период несовместимости кода и схемы</h3>
<p>Важнейшее понимание: во время деплоя СТАРЫЙ код и НОВАЯ схема (или
наоборот) работают ВМЕСТЕ несколько секунд-минут — потому что миграция и
деплой кода не переключаются одновременно, мгновенно. Поэтому правило:
миграция ВСЕГДА должна быть совместима (backward compatible) со СТАРЫМ
кодом. Например, вместо переименования колонки — добавляется новая
колонка, запись идёт в обе, затем старый код переводится на новую, и
ТОЛЬКО ПОСЛЕ ЭТОГО старая колонка удаляется — это подробнее раскрывается
в уроке 10 в теме "необратимая миграция".</p>

<h3>NOT VALID — безопасный способ добавления CHECK constraint</h3>
<p>При добавлении нового ограничения <code>CHECK</code> повторяется та же
проблема: PostgreSQL по умолчанию сразу проверяет ВСЕ существующие строки,
что на большой таблице приводит к долгой блокировке. Решение — два этапа:
сначала <code>ADD CONSTRAINT ... NOT VALID</code> (выполняется МГНОВЕННО,
проверяются только новые/изменённые строки), затем отдельная команда
<code>VALIDATE CONSTRAINT</code> (проверяет существующие строки, но только
с SHARED LOCK — не блокирует другие записи). Этот паттерн — эквивалент
трёхэтапного паттерна NOT NULL, только для CHECK constraint.</p>

<h3>Проверка блокировок перед миграцией — pg_stat_activity</h3>
<p>Навык диагностики из курса 107 применим и здесь: перед запуском большой
миграции рекомендуется через
<code>SELECT * FROM pg_stat_activity WHERE state != 'idle'</code>
посмотреть, какие запросы сейчас активны — если уже выполняется долгий
запрос (например большой отчёт), миграция может попасть в гонку за
блокировку именно с ним. Безопасная практика: запускать миграцию в тихий
час (при низком трафике) и с <code>lock_timeout</code> — если блокировка
длится дольше ожидаемого, миграция завершится с ошибкой, а не зависнет
навсегда.</p>
""".strip()

L9_CODE = """
# ============================================================
# XATO NAQSH — bitta migratsiyada NOT NULL + DEFAULT, katta jadvalda xavfli
# ============================================================
def upgrade_BAD() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=False, server_default='0'),
    )
    # Eski PostgreSQL versiyalarida (yoki DEFAULT'ni keyinroq murakkab
    # hisoblash orqali to'ldirish kerak bo'lganda) bu millionlab qatorli
    # jadvalda uzoq EXCLUSIVE LOCK'ga olib kelishi mumkin.

# ============================================================
# TO'G'RI NAQSH — 3 ta ALOHIDA migratsiya
# ============================================================

# --- Migratsiya 1: nullable ustun qo'shish (tez, qulflashsiz) ---
def upgrade_step1() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=True, server_default='0'),
    )

def downgrade_step1() -> None:
    op.drop_column('exercise_attempts', 'difficulty_score')


# --- Migratsiya 2: backfill — kichik partiyalarda ---
def upgrade_step2() -> None:
    connection = op.get_bind()
    while True:
        result = connection.execute(sa.text(
            \"\"\"
            UPDATE exercise_attempts
            SET difficulty_score = 0
            WHERE id IN (
                SELECT id FROM exercise_attempts
                WHERE difficulty_score IS NULL
                LIMIT 1000
            )
            \"\"\"
        ))
        if result.rowcount == 0:
            break   # barcha qatorlar to'ldirildi

def downgrade_step2() -> None:
    pass   # backfill'ni orqaga qaytarish shart emas — qiymatlar qoladi


# --- Migratsiya 3: NOT NULL qilish — faqat backfill tugagach ---
def upgrade_step3() -> None:
    op.alter_column('exercise_attempts', 'difficulty_score', nullable=False)

def downgrade_step3() -> None:
    op.alter_column('exercise_attempts', 'difficulty_score', nullable=True)

# ============================================================
# Zero-downtime: ustun nomini o'zgartirish — TO'G'RI usul
# ============================================================
# 1-deploy: yangi ustun qo'shiladi, ESKI kod hali eski ustunga yozadi:
#   op.add_column('courses', sa.Column('image_url', sa.String(500), nullable=True))
#
# 2-deploy: ilova kodi IKKALASIGA ham yozadigan qilib yangilanadi
#   (eski_ustun = qiymat; yangi_ustun = qiymat) — bu davrda eski VA yangi
#   kod versiyalari birga ishlashi mumkin.
#
# 3-deploy: barcha o'qish yangi ustundan bo'lishi ta'minlangach,
#   eski ustun endi HECH QAYERDA o'qilmaydi.
#
# 4-migratsiya: faqat SHUNDAN KEYIN eski ustun o'chiriladi:
#   op.drop_column('courses', 'cover_image_url')

# ============================================================
# NOT VALID CHECK constraint — cheklovni ham 2 bosqichda qo'shish
# ============================================================
# Yangi CHECK constraint qo'shish ham xuddi shu muammoga ega: PostgreSQL
# sukut bo'yicha BARCHA mavjud qatorlarni darhol tekshiradi. NOT VALID
# bilan bu tekshiruv KECHIKTIRILADI:
def upgrade_check_step1() -> None:
    op.execute(
        "ALTER TABLE exercise_attempts "
        "ADD CONSTRAINT ck_score_non_negative CHECK (difficulty_score >= 0) NOT VALID"
    )
    # Bu DARHOL bajariladi — faqat YANGI/o'zgargan qatorlar tekshiriladi.

def upgrade_check_step2() -> None:
    op.execute("ALTER TABLE exercise_attempts VALIDATE CONSTRAINT ck_score_non_negative")
    # Bu ROW-darajasidagi SHARED LOCK bilan ishlaydi (EXCLUSIVE emas) —
    # boshqa yozuvlarni bloklamaydi, faqat mavjud qatorlarni tekshiradi.

# ============================================================
# To'liq, HAQIQIY fayl formatidagi migratsiya — 1-bosqich (nullable qo'shish)
# ============================================================
\"\"\"add difficulty_score to exercise_attempts (step 1 of 3)

Revision ID: aa11bb22cc00
Revises: ff0011223344
Create Date: 2026-07-20
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'aa11bb22cc00'
down_revision = 'ff0011223344'


def upgrade() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=True, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('exercise_attempts', 'difficulty_score')

# ============================================================
# Backfill vaqtini baholash — sikl qancha davom etishini oldindan bilish
# ============================================================
# Agar jadvalda 5 000 000 qator bo'lsa va har bir partiya (1000 qator)
# ~50ms davom etsa:
#   5_000_000 / 1000 = 5000 ta partiya
#   5000 * 50ms = 250 000ms = ~4.2 daqiqa
# Bu hisob-kitob — backfill migratsiyasini tinch soatga rejalashtirish
# yoki uni fon jarayoni (background job) sifatida bajarish kerakligini
# oldindan aniqlashga yordam beradi.

# ============================================================
# Partiyalar orasida pauza — doimiy yuklamani oldini olish
# ============================================================
import time

def upgrade_backfill_with_pause() -> None:
    connection = op.get_bind()
    while True:
        result = connection.execute(sa.text(
            "UPDATE exercise_attempts SET difficulty_score = 0 "
            "WHERE id IN (SELECT id FROM exercise_attempts "
            "WHERE difficulty_score IS NULL LIMIT 1000)"
        ))
        if result.rowcount == 0:
            break
        time.sleep(0.1)   # qisqa pauza — partiyalar orasida boshqa so'rovlarga vaqt beradi
# Pauzasiz backfill tezroq tugashi mumkin, lekin butun migratsiya
# davomida disk/CPU'ga uzluksiz yuklama beradi, ilovaning odatiy trafigi
# bilan raqobatlashadi.
""".strip()

L9_CODE_RU = """
# ============================================================
# НЕВЕРНЫЙ ПАТТЕРН — NOT NULL + DEFAULT в одной миграции, опасно на большой таблице
# ============================================================
def upgrade_BAD() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=False, server_default='0'),
    )
    # В старых версиях PostgreSQL (или когда DEFAULT нужно вычислить сложным
    # способом позже) это может привести к долгой EXCLUSIVE LOCK на таблице
    # с миллионами строк.

# ============================================================
# ПРАВИЛЬНЫЙ ПАТТЕРН — 3 ОТДЕЛЬНЫЕ миграции
# ============================================================

# --- Миграция 1: добавить nullable колонку (быстро, без блокировки) ---
def upgrade_step1() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=True, server_default='0'),
    )

def downgrade_step1() -> None:
    op.drop_column('exercise_attempts', 'difficulty_score')


# --- Миграция 2: backfill — маленькими партиями ---
def upgrade_step2() -> None:
    connection = op.get_bind()
    while True:
        result = connection.execute(sa.text(
            \"\"\"
            UPDATE exercise_attempts
            SET difficulty_score = 0
            WHERE id IN (
                SELECT id FROM exercise_attempts
                WHERE difficulty_score IS NULL
                LIMIT 1000
            )
            \"\"\"
        ))
        if result.rowcount == 0:
            break   # все строки заполнены

def downgrade_step2() -> None:
    pass   # откатывать backfill не нужно — значения останутся


# --- Миграция 3: сделать NOT NULL — только после завершения backfill ---
def upgrade_step3() -> None:
    op.alter_column('exercise_attempts', 'difficulty_score', nullable=False)

def downgrade_step3() -> None:
    op.alter_column('exercise_attempts', 'difficulty_score', nullable=True)

# ============================================================
# Zero-downtime: переименование колонки — ПРАВИЛЬНЫЙ способ
# ============================================================
# Деплой 1: добавляется новая колонка, СТАРЫЙ код всё ещё пишет в старую:
#   op.add_column('courses', sa.Column('image_url', sa.String(500), nullable=True))
#
# Деплой 2: код приложения обновляется писать в ОБЕ
#   (старая_колонка = значение; новая_колонка = значение) — в этот период
#   старая И новая версии кода могут работать одновременно.
#
# Деплой 3: после того как всё чтение гарантированно идёт из новой колонки,
#   старая колонка больше НИГДЕ не читается.
#
# Миграция 4: ТОЛЬКО ПОСЛЕ ЭТОГО старая колонка удаляется:
#   op.drop_column('courses', 'cover_image_url')

# ============================================================
# NOT VALID CHECK constraint — добавление ограничения тоже в 2 этапа
# ============================================================
# Добавление нового CHECK constraint страдает той же проблемой: PostgreSQL
# по умолчанию сразу проверяет ВСЕ существующие строки. С NOT VALID эта
# проверка ОТКЛАДЫВАЕТСЯ:
def upgrade_check_step1() -> None:
    op.execute(
        "ALTER TABLE exercise_attempts "
        "ADD CONSTRAINT ck_score_non_negative CHECK (difficulty_score >= 0) NOT VALID"
    )
    # Это выполняется МГНОВЕННО — проверяются только НОВЫЕ/изменённые строки.

def upgrade_check_step2() -> None:
    op.execute("ALTER TABLE exercise_attempts VALIDATE CONSTRAINT ck_score_non_negative")
    # Работает с SHARED LOCK на уровне строк (не EXCLUSIVE) — не блокирует
    # другие записи, только проверяет существующие строки.

# ============================================================
# Полная миграция в РЕАЛЬНОМ формате файла — этап 1 (добавление nullable)
# ============================================================
\"\"\"add difficulty_score to exercise_attempts (step 1 of 3)

Revision ID: aa11bb22cc00
Revises: ff0011223344
Create Date: 2026-07-20
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'aa11bb22cc00'
down_revision = 'ff0011223344'


def upgrade() -> None:
    op.add_column(
        'exercise_attempts',
        sa.Column('difficulty_score', sa.Integer(), nullable=True, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('exercise_attempts', 'difficulty_score')

# ============================================================
# Оценка времени backfill — заранее понять, сколько продлится цикл
# ============================================================
# Если в таблице 5 000 000 строк и каждая партия (1000 строк) занимает
# ~50мс:
#   5_000_000 / 1000 = 5000 партий
#   5000 * 50мс = 250 000мс = ~4.2 минуты
# Этот расчёт помогает заранее понять, нужно ли планировать миграцию
# backfill на тихий час или выполнять её как фоновую задачу (background job).

# ============================================================
# Пауза между партиями — чтобы не создавать постоянную нагрузку
# ============================================================
import time

def upgrade_backfill_with_pause() -> None:
    connection = op.get_bind()
    while True:
        result = connection.execute(sa.text(
            "UPDATE exercise_attempts SET difficulty_score = 0 "
            "WHERE id IN (SELECT id FROM exercise_attempts "
            "WHERE difficulty_score IS NULL LIMIT 1000)"
        ))
        if result.rowcount == 0:
            break
        time.sleep(0.1)   # короткая пауза — даёт время другим запросам между партиями
# Без паузы backfill может выполниться быстрее, но создаёт непрерывную
# нагрузку на диск/CPU в течение всей миграции, конкурируя с обычным
# трафиком приложения.
""".strip()

L9_TASK = {
    "task_title": "Katta jadvalga xavfsiz ustun qo'shish rejasi",
    "task_title_ru": "План безопасного добавления колонки в большую таблицу",
    "task_description": (
        "exercise_attempts jadvaliga (millionlab qator deb faraz qiling) "
        "yangi 'hint_used' (Boolean, NOT NULL, default False) ustunini "
        "qo'shish uchun UCH BOSQICHLI migratsiya rejasini yozing: (1) "
        "nullable ustun + server_default, (2) batch backfill (LIMIT bilan "
        "sikl), (3) NOT NULL qilish. Har bir bosqich uchun alohida "
        "upgrade()/downgrade() juftligi yozing."
    ),
    "task_description_ru": (
        "Для таблицы exercise_attempts (представьте миллионы строк) "
        "напишите ТРЁХЭТАПНЫЙ план миграции для добавления новой колонки "
        "'hint_used' (Boolean, NOT NULL, default False): (1) nullable "
        "колонка + server_default, (2) пакетный backfill (цикл с LIMIT), "
        "(3) установка NOT NULL. Для каждого этапа напишите отдельную пару "
        "upgrade()/downgrade()."
    ),
    "task_requirements": (
        "1) 3 ta alohida migratsiya fayli/funksiya (bitta faylda ham "
        "bo'lishi mumkin, lekin aniq ajratilgan). 2) Backfill LIMIT bilan "
        "sikl shaklida, bitta ulkan UPDATE emas. 3) server_default va "
        "default= farqini izohda tushuntiring. 4) Har bir bosqichning "
        "nega alohida ekanini yozma asoslang."
    ),
    "task_requirements_ru": (
        "1) 3 отдельных файла/функции миграции (можно и в одном файле, но "
        "чётко разделены). 2) Backfill в виде цикла с LIMIT, не одним "
        "огромным UPDATE. 3) Объясните в комментарии разницу server_default "
        "и default=. 4) Письменно обоснуйте, почему каждый этап отдельный."
    ),
    "task_technologies": "Python, Alembic, SQLAlchemy 2.x, PostgreSQL",
    "task_deadline_days": 5,
}

L9_SAMPLE = {
    "title": "Namuna: hint_used ustuni uchun 3-bosqichli xavfsiz migratsiya",
    "description": "nullable qo'shish, batch backfill va NOT NULL qilishning to'liq, alohida migratsiya fayllari.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "step1_add_nullable.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'aa00bb11cc22'\n"
                "down_revision = 'bb22cc33dd44'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.add_column(\n"
                "        'exercise_attempts',\n"
                "        sa.Column('hint_used', sa.Boolean(), nullable=True, server_default='false'),\n"
                "    )\n\n\n"
                "def downgrade() -> None:\n"
                "    op.drop_column('exercise_attempts', 'hint_used')\n"
            ),
        },
        {
            "filename": "step2_backfill.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'bb11cc22dd33'\n"
                "down_revision = 'aa00bb11cc22'\n\n\n"
                "def upgrade() -> None:\n"
                "    connection = op.get_bind()\n"
                "    while True:\n"
                "        result = connection.execute(sa.text(\n"
                "            \"\"\"\n"
                "            UPDATE exercise_attempts\n"
                "            SET hint_used = false\n"
                "            WHERE id IN (\n"
                "                SELECT id FROM exercise_attempts\n"
                "                WHERE hint_used IS NULL\n"
                "                LIMIT 1000\n"
                "            )\n"
                "            \"\"\"\n"
                "        ))\n"
                "        if result.rowcount == 0:\n"
                "            break\n\n\n"
                "def downgrade() -> None:\n"
                "    pass\n"
            ),
        },
        {
            "filename": "step3_not_null.py",
            "language": "python",
            "code": (
                "from alembic import op\n\n"
                "revision = 'cc22dd33ee44'\n"
                "down_revision = 'bb11cc22dd33'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.alter_column('exercise_attempts', 'hint_used', nullable=False)\n\n\n"
                "def downgrade() -> None:\n"
                "    op.alter_column('exercise_attempts', 'hint_used', nullable=True)\n"
            ),
        },
    ],
}

L9_EXERCISES = [
    {
        "title": "Xavfli birlashtirilgan migratsiya",
        "title_ru": "Опасная объединённая миграция",
        "description": "Katta jadvalda NOT NULL + DEFAULT'ni BITTA migratsiyada qo'shish nega xavfli?",
        "description_ru": "Почему опасно добавлять NOT NULL + DEFAULT ОДНОЙ миграцией на большой таблице?",
        "exercise_type": "multiple_choice",
        "options": [
            "Butun jadvalni uzoq vaqt qulflab qo'yishi mumkin",
            "PostgreSQL bunday buyruqni umuman qabul qilmaydi",
            "Bu ORM'ni butunlay buzadi",
            "Bu faqat SQLite'da muammo, PostgreSQL'da xavfsiz",
        ],
        "options_ru": [
            "Может надолго заблокировать всю таблицу",
            "PostgreSQL вообще не принимает такую команду",
            "Это полностью ломает ORM",
            "Это проблема только в SQLite, в PostgreSQL безопасно",
        ],
        "correct_answers": "A",
        "hint": "Eski satrlarni to'ldirish uchun butun jadvalni qayta yozish kerak bo'lishi mumkin.",
        "hint_ru": "Может понадобиться переписать всю таблицу, чтобы заполнить старые строки.",
        "explanation": "Katta jadvalda bu operatsiya EXCLUSIVE LOCK bilan uzoq davom etishi mumkin — shu vaqt boshqa so'rovlar kutadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "3 bosqichli xavfsiz naqshni tartiblang",
        "title_ru": "Расположите 3-этапный безопасный паттерн по порядку",
        "description": "Katta jadvalga yangi NOT NULL ustun qo'shishning xavfsiz qadamlarini tartibga joylashtiring.",
        "description_ru": "Расположите безопасные шаги добавления новой NOT NULL колонки в большую таблицу.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "nullable=True bilan ustun qo'shish",
            "Batch backfill — mavjud qatorlarni to'ldirish",
            "Barcha qatorlar to'lganini tekshirish",
            "nullable=False ga o'zgartirish",
        ],
        "drag_items_ru": [
            "Добавить колонку с nullable=True",
            "Пакетный backfill — заполнить существующие строки",
            "Проверить, что все строки заполнены",
            "Изменить на nullable=False",
        ],
        "correct_order": [
            "nullable=True bilan ustun qo'shish",
            "Batch backfill — mavjud qatorlarni to'ldirish",
            "Barcha qatorlar to'lganini tekshirish",
            "nullable=False ga o'zgartirish",
        ],
        "hint": "Avval bo'sh joy ochiladi, keyin to'ldiriladi, keyin tekshiriladi, oxirida majburiy qilinadi.",
        "hint_ru": "Сначала открывается место, потом заполняется, потом проверяется, в конце становится обязательным.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "server_default'ning migratsiyadagi roli",
        "title_ru": "Роль server_default в миграциях",
        "description": "server_default ishlatilganda yangi ustun qiymati qayerda qo'llaniladi: Python kodida emas, ___ darajasida.",
        "description_ru": "При использовании server_default значение новой колонки применяется не в коде Python, а на уровне ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "baza",
        "correct_answers_ru": "базы",
        "hint": "Bu ORM'dan tashqarida yozilgan qatorlar uchun ham ishlaydi.",
        "hint_ru": "Это работает и для строк, записанных в обход ORM.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 10 — Migratsiya xatoliklari: qulflash, qaytarib bo'lmaydigan o'zgarishlar
# ---------------------------------------------------------------------------

L10_TEXT = """
<h3>Haqiqiy voqea: bu platformaning o'z migratsiya tarixidagi xato</h3>
<p>Bu — o'ylab topilgan misol emas. Bu platformaning
<code>backend/alembic/versions/</code> papkasida "rename course image
fields to image_url" nomli bir nechta migratsiya fayli mavjud — bu
o'zi allaqachon signal: bitta o'zgarish bir necha marta "tuzatilgan".
Ulardan birida <code>autogenerate</code> quyidagini taklif qilgan edi:
<code>op.add_column('courses', sa.Column('img_url', ...))</code> so'ngra
<code>op.drop_column('courses', 'cover_image_url')</code>,
<code>op.drop_column('courses', 'syllabus_url')</code>,
<code>op.drop_column('courses', 'thumbnail_url')</code> va
<code>op.drop_column('courses', 'video_intro_url')</code> — barchasi BITTA
migratsiyada. Bu — nomni o'zgartirish emas, TO'RTTA USTUNNI O'CHIRISH edi,
ularda saqlangan HAMMA ma'lumot bilan birga. Agar bu migratsiya ko'rib
chiqilmasdan qo'llanilganida, mavjud kurslarning rasm URL'lari abadiy
yo'qolardi.</p>

<h3>autogenerate nega bunday xato qiladi</h3>
<p>8-darsda aytilganidek, Alembic autogenerate model va bazani
SOLISHTIRADI — u "bu ustun nomi o'zgardi" degan tushunchaga EGA EMAS, u
faqat "model bo'yicha bu ustun kerak, bazada esa yo'q" (=> ADD) va "bazada
bu ustun bor, modelda esa yo'q" (=> DROP) deb ko'radi. Agar dasturchi
modelda <code>cover_image_url</code>ni <code>image_url</code>ga
o'zgartirsa, autogenerate buni "eski o'chirilgan + yangi qo'shilgan" deb
talqin qiladi — semantik jihatdan bu noto'g'ri, lekin SINTAKTIK jihatdan
to'liq to'g'ri ko'rinadi.</p>

<h3>Qulflash (locking) — qaysi buyruqlar qanchalik xavfli</h3>
<p>PostgreSQL'dagi turli DDL buyruqlari turli darajadagi qulf talab
qiladi: <code>ADD COLUMN nullable</code> (metadata-only, deyarli
zararsiz) < <code>CREATE INDEX CONCURRENTLY</code> (indeksni qulflashsiz
qurish, lekin sekinroq) < <code>CREATE INDEX</code> (oddiy, WRITE'larni
bloklaydi) < <code>ALTER COLUMN TYPE</code> (ko'pincha butun jadvalni
qayta yozadi) < <code>ADD COLUMN NOT NULL DEFAULT (murakkab hisoblash)</code>
(eng og'iri). Har bir migratsiya yozishdan oldin "bu buyruq qaysi turdagi
qulfni talab qiladi" degan savolni berish kerak.</p>

<h3>Qaytarib bo'lmaydigan (irreversible) migratsiyalar</h3>
<p>Ba'zi operatsiyalar tabiiy ravishda ma'lumot yo'qotadi: ustunni
o'chirish, jadval nomini o'zgartirish (agar boshqa joyda hali eski nom
ishlatilsa), yoki ustun turini toraytirish (masalan VARCHAR(500)dan
VARCHAR(50)ga — uzun matnlar KESILADI). Bunday hollarda
<code>downgrade()</code> texnik jihatdan yozilishi mumkin (masalan ustunni
qayta qo'shish), lekin YO'QOLGAN MA'LUMOTNI qaytara olmaydi — bu
"qaytarib bo'lmaydigan" degani aynan shu ma'noda. Qoida: agar migratsiya
ma'lumot yo'qotishi mumkin bo'lsa, avval BACKUP olinadi, so'ngra
staging'da sinaladi, faqat SHUNDAN KEYIN production'ga qo'llaniladi.</p>

<h3>Xavfsizlik to'ri: migratsiyani ko'rib chiqish qoidalari</h3>
<p>Har bir <code>--autogenerate</code> natijasi qo'lda ko'rib chiqilishi
kerak, quyidagi savollar bilan: Bu <code>drop_column</code> haqiqatan ham
kerakmi, yoki bu rename edi? Bu ustunda HOZIRDA production ma'lumoti
bormi? Agar bor bo'lsa, uni saqlab qolish uchun migratsiyadan OLDIN backup
yoki ko'chirish kerakmi? Bu — 8-darsda aytilgan "autogenerate'ga ko'r-ko'rona
ishonmaslik" tamoyilining amaliy qo'llanilishi.</p>

<h3>CREATE INDEX CONCURRENTLY — nega tranzaksiya ichida ishlamaydi</h3>
<p>Yana bir keng tarqalgan xato: <code>op.create_index(...,
postgresql_concurrently=True)</code> PostgreSQL'ning tranzaksiya BLOKidan
tashqarida ishga tushirilishi SHART — chunki CONCURRENTLY o'zi bir nechta
ichki bosqichni alohida tranzaksiyalarda bajaradi. Alembic'da bu
<code>with op.get_context().autocommit_block():</code> orqali hal qilinadi.
Agar bu unutilsa, Alembic <code>CREATE INDEX CONCURRENTLY cannot run
inside a transaction block</code> degan xatoni beradi — bu xato xabari
o'zi ham diagnostika: u qulflash bilan bog'liq muammoni ANIQ ko'rsatib
turadi.</p>

<h3>Ustun turini toraytirish — jimgina ma'lumot kesilishi</h3>
<p><code>VARCHAR(500)</code>dan <code>VARCHAR(50)</code>ga o'tish — bu
"kichikroq qiladi" degandek zararsiz tuyulishi mumkin, lekin agar mavjud
qatorlarda 50 belgidan uzun matn bo'lsa, PostgreSQL migratsiyani XATO bilan
to'xtatadi (agar mavjud qiymatlar tekshirilsa) yoki — yomonroq holatda —
ba'zi drayverlar/vositalar bu tekshiruvni chetlab, matnni jimgina KESADI.
Bunday migratsiyadan oldin har doim
<code>SELECT max(length(col)) FROM table</code> orqali eng uzun mavjud
qiymatni tekshirish kerak.</p>
""".strip()

L10_TEXT_RU = """
<h3>Реальный случай: ошибка из истории миграций именно этой платформы</h3>
<p>Это не выдуманный пример. В папке
<code>backend/alembic/versions/</code> этой платформы существует
несколько файлов миграций с названием "rename course image fields to
image_url" — само это уже сигнал: одно изменение "исправлялось"
несколько раз. В одном из них <code>autogenerate</code> предложил
следующее: <code>op.add_column('courses', sa.Column('img_url', ...))</code>,
затем <code>op.drop_column('courses', 'cover_image_url')</code>,
<code>op.drop_column('courses', 'syllabus_url')</code>,
<code>op.drop_column('courses', 'thumbnail_url')</code> и
<code>op.drop_column('courses', 'video_intro_url')</code> — всё в ОДНОЙ
миграции. Это было не переименование, а УДАЛЕНИЕ ЧЕТЫРЁХ КОЛОНОК вместе
со ВСЕМИ хранившимися в них данными. Если бы эта миграция была применена
без рассмотрения, URL изображений существующих курсов были бы потеряны
навсегда.</p>

<h3>Почему autogenerate совершает такую ошибку</h3>
<p>Как говорилось в уроке 8, Alembic autogenerate СРАВНИВАЕТ модель и
базу — у него НЕТ понятия "это имя колонки изменилось", он видит только
"по модели эта колонка нужна, а в базе её нет" (=> ADD) и "в базе эта
колонка есть, а в модели нет" (=> DROP). Если разработчик переименовал в
модели <code>cover_image_url</code> в <code>image_url</code>, autogenerate
интерпретирует это как "старая удалена + новая добавлена" — семантически
это неверно, но СИНТАКСИЧЕСКИ выглядит полностью корректно.</p>

<h3>Блокировки (locking) — насколько опасна каждая команда</h3>
<p>Разные DDL-команды в PostgreSQL требуют разного уровня блокировки:
<code>ADD COLUMN nullable</code> (только метаданные, почти безвредно) <
<code>CREATE INDEX CONCURRENTLY</code> (построение индекса без блокировки,
но медленнее) < <code>CREATE INDEX</code> (обычный, блокирует WRITE) <
<code>ALTER COLUMN TYPE</code> (часто переписывает всю таблицу) <
<code>ADD COLUMN NOT NULL DEFAULT (сложное вычисление)</code> (самая
тяжёлая). Перед написанием каждой миграции нужно задавать вопрос "какой
уровень блокировки требует эта команда".</p>

<h3>Необратимые (irreversible) миграции</h3>
<p>Некоторые операции по своей природе теряют данные: удаление колонки,
переименование таблицы (если где-то ещё используется старое имя), или
сужение типа колонки (например с VARCHAR(500) до VARCHAR(50) — длинные
тексты ОБРЕЗАЮТСЯ). В таких случаях <code>downgrade()</code> технически
можно написать (например снова добавить колонку), но он НЕ МОЖЕТ вернуть
ПОТЕРЯННЫЕ ДАННЫЕ — именно в этом смысле "необратимая". Правило: если
миграция может потерять данные, сначала делается BACKUP, затем тестируется
на staging, и ТОЛЬКО ПОСЛЕ ЭТОГО применяется в production.</p>

<h3>Сеть безопасности: правила проверки миграции</h3>
<p>Результат каждого <code>--autogenerate</code> должен проверяться
вручную, со следующими вопросами: действительно ли нужен этот
<code>drop_column</code>, или это было переименование? Есть ли СЕЙЧАС в
этой колонке production-данные? Если есть, нужен ли backup или перенос
данных ДО миграции, чтобы их сохранить? Это — практическое применение
принципа "не доверять autogenerate вслепую" из урока 8.</p>

<h3>CREATE INDEX CONCURRENTLY — почему не работает внутри транзакции</h3>
<p>Ещё одна распространённая ошибка: <code>op.create_index(...,
postgresql_concurrently=True)</code> ДОЛЖНА запускаться вне блока
транзакции PostgreSQL — потому что CONCURRENTLY сама выполняет несколько
внутренних этапов в отдельных транзакциях. В Alembic это решается через
<code>with op.get_context().autocommit_block():</code>. Если это забыть,
Alembic выдаст ошибку <code>CREATE INDEX CONCURRENTLY cannot run inside a
transaction block</code> — само это сообщение об ошибке уже диагностика:
оно чётко указывает на проблему с блокировкой.</p>

<h3>Сужение типа колонки — тихая потеря данных</h3>
<p>Переход с <code>VARCHAR(500)</code> на <code>VARCHAR(50)</code> может
казаться безобидным "уменьшением", но если в существующих строках есть
текст длиннее 50 символов, PostgreSQL остановит миграцию с ОШИБКОЙ (если
проверяются существующие значения) или — что хуже — некоторые
драйверы/инструменты обходят эту проверку и тихо ОБРЕЗАЮТ текст. Перед
такой миграцией всегда нужно проверить самое длинное существующее
значение через <code>SELECT max(length(col)) FROM table</code>.</p>
""".strip()

L10_CODE = """
# ============================================================
# HAQIQIY XATO: bu platformaning migratsiya tarixidan (soddalashtirilgan)
# "rename course image fields to image_url" — aslida MA'LUMOT YO'QOTISH
# ============================================================
def upgrade_DANGEROUS() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('img_url', sa.String(length=500), nullable=True))
    op.drop_column('courses', 'cover_image_url')     # <- MA'LUMOT YO'QOLADI
    op.drop_column('courses', 'syllabus_url')        # <- MA'LUMOT YO'QOLADI
    op.drop_column('courses', 'video_intro_url')     # <- MA'LUMOT YO'QOLADI
    op.drop_column('courses', 'thumbnail_url')       # <- MA'LUMOT YO'QOLADI
    # ### end Alembic commands ###
    # autogenerate BUNI "img_url qo'shildi + 4 ta eski ustun kerak emas"
    # deb ko'rdi — u "bular aslida BIR XIL ma'lumot, faqat nom o'zgardi"
    # degan tushunchaga EGA EMAS.

# ============================================================
# TO'G'RI TUZATISH — nomni o'zgartirish uchun DROP emas, RENAME
# ============================================================
def upgrade_SAFE() -> None:
    op.alter_column('courses', 'cover_image_url', new_column_name='image_url')
    # Ma'lumot SAQLANADI — faqat ustun nomi o'zgaradi, jismoniy qayta
    # yozish yo'q (metadata-only operatsiya).

def downgrade_SAFE() -> None:
    op.alter_column('courses', 'image_url', new_column_name='cover_image_url')

# ============================================================
# Qulflash darajalari — xavfsizdan xavflisigacha
# ============================================================
# 1) op.add_column(..., nullable=True)                    -> metadata-only, deyarli zararsiz
# 2) op.create_index(..., postgresql_concurrently=True)    -> sekin, lekin qulflashsiz
# 3) op.create_index(...)                                   -> WRITE'larni bloklaydi
# 4) op.alter_column(..., type_=...)                        -> ko'pincha jadvalni qayta yozadi
# 5) op.add_column(..., nullable=False, server_default=...) -> eng og'ir (murakkab hollarda)

# ============================================================
# Migratsiyani qo'llashdan OLDIN — nima tekshirish kerak
# ============================================================
# 1. Bu drop_column/rename haqiqatan ham to'g'rimi — model diff'ini o'qing:
#    git diff HEAD~1 -- app/models/course.py
#
# 2. Bu ustunda HOZIRGI production ma'lumoti bormi?
#    SELECT count(*) FROM courses WHERE cover_image_url IS NOT NULL;
#
# 3. Agar ha bo'lsa — avval BACKUP:
#    pg_dump -t courses student_platform > courses_backup.sql
#
# 4. Staging'da to'liq round-trip sinovi (8-darsdagi kabi):
#    alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# ============================================================
# CREATE INDEX CONCURRENTLY — tranzaksiyadan tashqarida ishga tushirish
# ============================================================
def upgrade_concurrent_index() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_exercise_attempts_student_id",
            "exercise_attempts",
            ["student_id"],
            postgresql_concurrently=True,
        )
    # autocommit_block()siz: "CREATE INDEX CONCURRENTLY cannot run inside
    # a transaction block" xatosi chiqadi — Alembic har bir migratsiyani
    # sukut bo'yicha bitta tranzaksiyaga o'raydi.

# ============================================================
# Ustun turini toraytirishdan OLDIN — mavjud ma'lumotni tekshirish
# ============================================================
# alembic revision yozishdan oldin, qo'lda:
#   SELECT max(length(bio)) FROM students;
# Agar natija 50 dan katta bo'lsa, VARCHAR(50)ga toraytirish xavfli —
# avval uzun qiymatlarni tekshirib, ular bilan nima qilish kerakligini
# (kesish? xato berish? migratsiyani bekor qilish?) hal qilish kerak.

# ============================================================
# Yana bir qaytarib bo'lmaydigan xato — sababini tekshirmasdan NOT NULL'ni olib tashlash
# ============================================================
def upgrade_removes_not_null_BLIND() -> None:
    # Kimdir "null value in column violates not-null constraint" xatosini
    # ko'rib, uni SABABINI aniqlamasdan (kod xatosimi? poyga holatimi?
    # formadagi unutilgan maydonmi?) shunchaki cheklovni olib tashlab
    # "hal qiladi":
    op.alter_column('students', 'email', nullable=True)   # tahlilsiz XAVFLI

# TO'G'RI yondashuv: avval NULL'ning manbasini topish, ilova kodida
# tuzatish, va faqat agar NULL biznes mantig'i bo'yicha HAQIQATAN ham
# ruxsat etilgan bo'lsa — cheklovni ongli ravishda, migratsiya xabarida
# yozma asos bilan olib tashlash.

# ============================================================
# Asosiy branch'ga qo'shishdan oldingi tekshiruv ro'yxati
# ============================================================
# [ ] revision/down_revision aniq mavjud oxirgi migratsiyaga to'g'ri ishora qiladi
# [ ] downgrade() yozilgan va sinalgan (8-darsdagi round-trip)
# [ ] o'zgartirilayotgan ustunlarda production ma'lumoti bor-yo'qligi tekshirilgan
# [ ] katta jadvallar uchun 3 bosqichli naqsh (9-dars) qo'llanilgan, bitta migratsiya emas
# [ ] katta jadvalda indeks yaratilayotgan bo'lsa CONCURRENTLY ishlatilgan

# ============================================================
# Yana bir xato turi — jadval nomini hali o'qilayotgan paytda o'zgartirish
# ============================================================
def upgrade_renames_table_TOO_EARLY() -> None:
    op.rename_table('lesson_feedback', 'course_lesson_feedback')
    # Agar bosqichma-bosqich deploy paytida eski kodning kamida bitta
    # ishlab turgan nusxasi hali ham `SELECT * FROM lesson_feedback`
    # bajarayotgan bo'lsa, u darhol "relation does not exist" xatosini
    # oladi — bu 9-darsdagi kod-sxema mosligining aynan o'zi buzilishi.

# XAVFSIZROQ: o'tish davri uchun eski nom bilan SQL VIEW yaratish
def upgrade_renames_table_SAFE() -> None:
    op.rename_table('lesson_feedback', 'course_lesson_feedback')
    op.execute("CREATE VIEW lesson_feedback AS SELECT * FROM course_lesson_feedback")
    # Eski kod VIEW orqali o'zgarishsiz o'qishda davom etadi; butun kod
    # yangi nomga o'tgach, VIEW alohida, keyingi migratsiyada o'chiriladi.
""".strip()

L10_CODE_RU = """
# ============================================================
# РЕАЛЬНАЯ ОШИБКА: из истории миграций этой платформы (упрощено)
# "rename course image fields to image_url" — на деле ПОТЕРЯ ДАННЫХ
# ============================================================
def upgrade_DANGEROUS() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('img_url', sa.String(length=500), nullable=True))
    op.drop_column('courses', 'cover_image_url')     # <- ДАННЫЕ ТЕРЯЮТСЯ
    op.drop_column('courses', 'syllabus_url')        # <- ДАННЫЕ ТЕРЯЮТСЯ
    op.drop_column('courses', 'video_intro_url')     # <- ДАННЫЕ ТЕРЯЮТСЯ
    op.drop_column('courses', 'thumbnail_url')       # <- ДАННЫЕ ТЕРЯЮТСЯ
    # ### end Alembic commands ###
    # autogenerate УВИДЕЛ ЭТО как "добавлен img_url + 4 старые колонки не
    # нужны" — у него НЕТ понятия, что это на самом деле ОДНИ И ТЕ ЖЕ
    # данные, просто переименованные.

# ============================================================
# ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ — для переименования RENAME, а не DROP
# ============================================================
def upgrade_SAFE() -> None:
    op.alter_column('courses', 'cover_image_url', new_column_name='image_url')
    # Данные СОХРАНЯЮТСЯ — меняется только имя колонки, без физической
    # перезаписи (операция только на уровне метаданных).

def downgrade_SAFE() -> None:
    op.alter_column('courses', 'image_url', new_column_name='cover_image_url')

# ============================================================
# Уровни блокировки — от безопасного к опасному
# ============================================================
# 1) op.add_column(..., nullable=True)                    -> только метаданные, почти безвредно
# 2) op.create_index(..., postgresql_concurrently=True)    -> медленно, но без блокировки
# 3) op.create_index(...)                                   -> блокирует WRITE
# 4) op.alter_column(..., type_=...)                        -> часто переписывает таблицу
# 5) op.add_column(..., nullable=False, server_default=...) -> самое тяжёлое (в сложных случаях)

# ============================================================
# Что проверить ПЕРЕД применением миграции
# ============================================================
# 1. Действительно ли верен этот drop_column/rename — прочитайте diff модели:
#    git diff HEAD~1 -- app/models/course.py
#
# 2. Есть ли СЕЙЧАС в этой колонке production-данные?
#    SELECT count(*) FROM courses WHERE cover_image_url IS NOT NULL;
#
# 3. Если да — сначала BACKUP:
#    pg_dump -t courses student_platform > courses_backup.sql
#
# 4. Полный round-trip тест на staging (как в уроке 8):
#    alembic upgrade head && alembic downgrade -1 && alembic upgrade head

# ============================================================
# CREATE INDEX CONCURRENTLY — запуск вне транзакции
# ============================================================
def upgrade_concurrent_index() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_exercise_attempts_student_id",
            "exercise_attempts",
            ["student_id"],
            postgresql_concurrently=True,
        )
    # Без autocommit_block(): ошибка "CREATE INDEX CONCURRENTLY cannot
    # run inside a transaction block" — Alembic по умолчанию оборачивает
    # каждую миграцию в одну транзакцию.

# ============================================================
# Перед сужением типа колонки — проверка существующих данных
# ============================================================
# Перед написанием alembic revision, вручную:
#   SELECT max(length(bio)) FROM students;
# Если результат больше 50, сужение до VARCHAR(50) опасно — сначала нужно
# проверить длинные значения и решить, что с ними делать (обрезать?
# выдать ошибку? отменить миграцию?).

# ============================================================
# Ещё одна необратимая ошибка — удаление NOT NULL без проверки причины
# ============================================================
def upgrade_removes_not_null_BLIND() -> None:
    # Кто-то видит ошибку "null value in column violates not-null
    # constraint" и "решает" её, просто убрав ограничение — не выяснив,
    # ПОЧЕМУ появляются NULL (баг в коде? гонка? забытое поле формы?):
    op.alter_column('students', 'email', nullable=True)   # ОПАСНО без анализа причины

# ПРАВИЛЬНЫЙ подход: сначала найти источник NULL, исправить его в коде
# приложения, и только если NULL действительно допустимо по бизнес-логике
# — сознательно снять ограничение с письменным обоснованием в сообщении
# миграции.

# ============================================================
# Контрольный список перед слиянием (merge) миграции в основную ветку
# ============================================================
# [ ] revision/down_revision корректно указывают на актуальную головную миграцию
# [ ] downgrade() написан и протестирован (round-trip из урока 8)
# [ ] проверено, есть ли в изменяемых колонках production-данные
# [ ] для больших таблиц применён 3-этапный паттерн (урок 9), а не одна миграция
# [ ] CONCURRENTLY использован там, где создаётся индекс на большой таблице

# ============================================================
# Ещё один класс ошибок — переименование таблицы, когда её ещё где-то читают
# ============================================================
def upgrade_renames_table_TOO_EARLY() -> None:
    op.rename_table('lesson_feedback', 'course_lesson_feedback')
    # Если хотя бы одна работающая копия старого кода (во время
    # постепенного деплоя) всё ещё выполняет `SELECT * FROM lesson_feedback`,
    # она немедленно начнёт получать "relation does not exist" — тот самый
    # разрыв совместимости кода и схемы из урока 9.

# БЕЗОПАСНЕЕ: создать SQL VIEW со старым именем на переходный период
def upgrade_renames_table_SAFE() -> None:
    op.rename_table('lesson_feedback', 'course_lesson_feedback')
    op.execute("CREATE VIEW lesson_feedback AS SELECT * FROM course_lesson_feedback")
    # Старый код читает через VIEW без изменений; когда весь код перейдёт
    # на новое имя, VIEW удаляется отдельной, последующей миграцией.
""".strip()

L10_TASK = {
    "task_title": "Xavfli migratsiyani toping va tuzating",
    "task_title_ru": "Найдите и исправьте опасную миграцию",
    "task_description": (
        "Sizga autogenerate taklif qilgan quyidagi migratsiya berilgan: "
        "Student modelida 'phone_number' ustuni 'phone'ga o'zgartirilgan, "
        "va autogenerate buni op.add_column('students', 'phone') + "
        "op.drop_column('students', 'phone_number') deb taklif qilgan. "
        "(1) Bu nega xavfli ekanini tushuntiring; (2) to'g'ri, ma'lumot "
        "yo'qotmaydigan tuzatilgan migratsiyani yozing; (3) bu ustunda "
        "hozirda ma'lumot bor-yo'qligini tekshiruvchi SQL so'rovini "
        "keltiring."
    ),
    "task_description_ru": (
        "Дана следующая миграция, предложенная autogenerate: в модели "
        "Student колонка 'phone_number' переименована в 'phone', и "
        "autogenerate предложил это как op.add_column('students', 'phone') "
        "+ op.drop_column('students', 'phone_number'). (1) Объясните, "
        "почему это опасно; (2) напишите правильную, не теряющую данные "
        "миграцию; (3) приведите SQL-запрос, проверяющий, есть ли сейчас "
        "данные в этой колонке."
    ),
    "task_requirements": (
        "1) Yozma tushuntirish: nega drop+add ma'lumot yo'qotadi. 2) "
        "op.alter_column(..., new_column_name=...) orqali to'g'ri "
        "migratsiya. 3) downgrade() ham to'g'ri yozilgan. 4) Tekshiruv "
        "uchun SELECT count(*) so'rovi."
    ),
    "task_requirements_ru": (
        "1) Письменное объяснение: почему drop+add теряет данные. 2) "
        "Правильная миграция через op.alter_column(..., "
        "new_column_name=...). 3) Корректно написан downgrade(). 4) "
        "Запрос SELECT count(*) для проверки."
    ),
    "task_technologies": "Python, Alembic, SQLAlchemy 2.x, PostgreSQL",
    "task_deadline_days": 5,
}

L10_SAMPLE = {
    "title": "Namuna: xavfli va xavfsiz migratsiya solishtiruvi",
    "description": "phone_number -> phone o'zgarishi uchun autogenerate'ning xavfli taklifi va uning xavfsiz tuzatilgan versiyasi.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "dangerous_autogenerate.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'dd33ee44ff55'\n"
                "down_revision = 'cc22dd33ee44'\n\n\n"
                "def upgrade() -> None:\n"
                "    # ### commands auto generated by Alembic - please adjust! ###\n"
                "    op.add_column('students', sa.Column('phone', sa.String(length=50), nullable=True))\n"
                "    op.drop_column('students', 'phone_number')  # XATO: ma'lumot yo'qoladi\n"
                "    # ### end Alembic commands ###\n"
            ),
        },
        {
            "filename": "safe_rename.py",
            "language": "python",
            "code": (
                "from alembic import op\n\n"
                "revision = 'dd33ee44ff55'\n"
                "down_revision = 'cc22dd33ee44'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.alter_column('students', 'phone_number', new_column_name='phone')\n\n\n"
                "def downgrade() -> None:\n"
                "    op.alter_column('students', 'phone', new_column_name='phone_number')\n\n\n"
                "# Tekshiruv: migratsiyadan OLDIN bu ustunda ma'lumot borligini bilish:\n"
                "# SELECT count(*) FROM students WHERE phone_number IS NOT NULL;\n"
            ),
        },
    ],
}

L10_EXERCISES = [
    {
        "title": "autogenerate nima uchun rename'ni drop+add deb ko'radi",
        "title_ru": "Почему autogenerate видит rename как drop+add",
        "description": "Alembic autogenerate ustun nomi o'zgarishini nega har doim 'eski o'chirish + yangi qo'shish' deb talqin qiladi?",
        "description_ru": "Почему Alembic autogenerate всегда интерпретирует переименование колонки как 'удалить старую + добавить новую'?",
        "exercise_type": "multiple_choice",
        "options": [
            "U faqat model va bazani solishtiradi, 'rename' tushunchasiga ega emas",
            "Bu PostgreSQL'ning cheklovi, Alembic bilan bog'liq emas",
            "Bu faqat eski Alembic versiyalarida sodir bo'ladi",
            "Bu Python versiyasiga bog'liq muammo",
        ],
        "options_ru": [
            "Он только сравнивает модель и базу, не имеет понятия 'переименование'",
            "Это ограничение PostgreSQL, не связанное с Alembic",
            "Это происходит только в старых версиях Alembic",
            "Это проблема, зависящая от версии Python",
        ],
        "correct_answers": "A",
        "hint": "8-darsda aytilgan: autogenerate faqat 'bor/yo'q' farqini ko'radi.",
        "hint_ru": "Как говорилось в уроке 8: autogenerate видит только разницу 'есть/нет'.",
        "explanation": "autogenerate model va bazadagi ustunlar ro'yxatini solishtiradi — semantik ma'noni (rename) tushunmaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Qulflash darajasini tartiblang",
        "title_ru": "Расположите уровни блокировки по порядку",
        "description": "Quyidagi operatsiyalarni ENG XAVFSIZDAN ENG XAVFLIGA qarab tartiblang.",
        "description_ru": "Расположите следующие операции от САМОЙ БЕЗОПАСНОЙ к САМОЙ ОПАСНОЙ.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "ADD COLUMN nullable=True",
            "CREATE INDEX CONCURRENTLY",
            "CREATE INDEX (oddiy)",
            "ALTER COLUMN TYPE (katta jadval)",
        ],
        "drag_items_ru": [
            "ADD COLUMN nullable=True",
            "CREATE INDEX CONCURRENTLY",
            "CREATE INDEX (обычный)",
            "ALTER COLUMN TYPE (большая таблица)",
        ],
        "correct_order": [
            "ADD COLUMN nullable=True",
            "CREATE INDEX CONCURRENTLY",
            "CREATE INDEX (oddiy)",
            "ALTER COLUMN TYPE (katta jadval)",
        ],
        "hint": "Metadata-only operatsiyalar eng xavfsiz, jadvalni qayta yozadiganlar eng xavfli.",
        "hint_ru": "Операции только с метаданными безопаснее всего, переписывающие таблицу — опаснее всего.",
        "difficulty_level": "Hard",
        "points": 10,
    },
    {
        "title": "Nomi o'zgargan ustun uchun to'g'ri buyruq",
        "title_ru": "Правильная команда для переименованной колонки",
        "description": "Ustun nomini ma'lumotni yo'qotmasdan o'zgartirish uchun op.alter_column(..., new_column_name=...) ishlatiladi, DROP+ADD emas. Bu op.___() metodining bir qismi.",
        "description_ru": "Для переименования колонки без потери данных используется op.alter_column(..., new_column_name=...), а не DROP+ADD. Это часть метода op.___().",
        "exercise_type": "fill_in_blank",
        "correct_answers": "alter_column",
        "hint": "Bu Python metod nomi — kod tokeni, tarjima qilinmaydi.",
        "hint_ru": "Это имя метода Python — код-токен, не переводится.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 11 — ORM performance muammolari: over-fetching va connection pool
# ---------------------------------------------------------------------------

L11_TEXT = """
<h3>N+1'dan tashqari: over-fetching — kerakmaganidan ko'proq olish</h3>
<p>5-darsda N+1'ni ko'rdik — "juda ko'p KICHIK so'rov". Over-fetching esa
qarama-qarshi muammo: "BITTA, lekin KERAKMAGANDAN KO'P ma'lumot olib
keluvchi so'rov". Masalan, <code>select(Course)</code> — bu Course'ning
BARCHA ustunlarini oladi, hatto agar frontend faqat <code>title</code> va
<code>id</code>ni ko'rsatsa ham. Katta <code>description</code> yoki
<code>text_content</code> ustunlari (bu platformada ular Text turida,
minglab belgigacha bo'lishi mumkin) har bir so'rovda keraksiz tarmoq
trafigi va xotira sarflaydi.</p>

<h3>load_only() — faqat kerakli ustunlarni tanlash</h3>
<p>ORM'da butun obyekt o'rniga faqat kerakli ustunlarni yuklash uchun
<code>.options(load_only(Course.id, Course.title))</code> ishlatiladi.
Bu ayniqsa ro'yxat sahifalarida (masalan kurslar katalogi) muhim — u
yerda foydalanuvchi <code>text_content</code>ning to'liq matnini emas,
faqat sarlavha va qisqa tavsifni ko'radi. Muqobil yechim — umuman ORM
obyektini yuklamasdan, faqat kerakli ustunlarni <code>select(Course.id,
Course.title)</code> orqali olish — bu holda natija Course obyekti emas,
Row bo'ladi (4-darsni eslang).</p>

<h3>Connection pool — nega u cheksiz emas</h3>
<p>1-darsda ko'rgan Engine ichida connection pool bor — PostgreSQL'ga
oldindan ochilgan, qayta ishlatiladigan ulanishlar to'plami. Bu pool
CHEKLANGAN (odatda 5-20 ta ulanish). Agar Session'lar to'g'ri
yopilmasa (6-darsdagi context manager qoidasi buzilsa) yoki bitta so'rov
juda uzoq davom etsa, pool tugab qoladi — yangi so'rovlar "ulanish
kutmoqda" holatida abadiy osilib qoladi, bu esa butun serverni to'xtatishi
mumkin.</p>

<h3>Pool tugashi — sabablari va belgilari</h3>
<p>Pool tugashining eng keng tarqalgan sabablari: (1) Session ochiq
qolib, hech qachon yopilmasligi (masalan xato tufayli <code>finally</code>
bloki chetlab o'tilishi); (2) bitta so'rov ichida ortiqcha ko'p alohida
Session ochilishi; (3) uzoq davom etadigan tranzaksiyalar (masalan
9-darsdagi noto'g'ri, bir yo'la bajariladigan backfill) boshqa
so'rovlarning ulanish olishiga to'sqinlik qilishi. Belgisi — production
loglarida <code>QueuePool limit of size N overflow O reached</code> kabi
xato.</p>

<h3>pool_size va pool_timeout — sozlash parametrlari</h3>
<p><code>create_async_engine(url, pool_size=10, max_overflow=5,
pool_timeout=30)</code> — <code>pool_size</code> doimiy ulanishlar sonini,
<code>max_overflow</code> vaqtinchalik qo'shimcha ulanishlarni,
<code>pool_timeout</code> esa bo'sh ulanish kutish vaqtini belgilaydi.
Bu sonlarni oshirish "tuzatish" emas — agar Session'lar to'g'ri
yopilmasa, kattaroq pool ham oxir-oqibat tugaydi, faqat kechroq. Haqiqiy
yechim — Session yashash muddatini qisqartirish va N+1/over-fetching'ni
yo'qotish.</p>

<h3>Uzoq tranzaksiyalar ichida tashqi chaqiruvlar — yashirin pool yeyuvchisi</h3>
<p>Tranzaksiya ichida tashqi API chaqiruvi (masalan Gennis sinxronizatsiyasi
kabi) yoki uzoq hisoblash bajarish — pool'ni band qilib turishning eng
yashirin sababi. Tranzaksiya ochiq turgan har bir millisekund — ulanish
boshqa so'rovlarga bo'shamaydi degani. Qoida: tashqi tarmoq chaqiruvlari
HAR DOIM tranzaksiyadan TASHQARIDA bajariladi, faqat natijalar tayyor
bo'lgach, qisqa tranzaksiya ichida bazaga yoziladi.</p>

<h3>EXPLAIN ANALYZE — ORM so'rovini ham 107-kursdagi vosita bilan tekshirish</h3>
<p>ORM qanchalik "qulay" bo'lmasin, hosil bo'lgan SQL'ni 107-kursda
o'rgangan <code>EXPLAIN ANALYZE</code> bilan tekshirish printsipi
o'zgarmaydi: <code>str(stmt.compile(compile_kwargs={"literal_binds":
True}))</code> orqali haqiqiy SQL matnini oling, so'ngra uni to'g'ridan-
to'g'ri psql'da <code>EXPLAIN ANALYZE</code> bilan ishga tushiring. Bu —
"ORM sekin ishlayapti" degan noaniq shikoyatni "bu SO'ROV sekin, sababi
mana bu" degan aniq diagnostikaga aylantiradi.</p>

<h3>Bu darsning R2 checkpoint'i bilan bog'liqligi</h3>
<p>Over-fetching, connection pool va uzoq tranzaksiyalar — bularning
barchasi 12-darsdagi R2 checkpoint loyihasida sinaladigan tushunchalar.
Ular 8-11-darslarning "ikkinchi yarim" mavzusini yakunlaydi: model
yozishdan (birinchi yarim) production bazasini xavfsiz va samarali
boshqarishga (ikkinchi yarim) o'tish. Keyingi darsda shu barcha
tushunchalarni birlashtiruvchi amaliy loyiha kutmoqda.</p>
""".strip()

L11_TEXT_RU = """
<h3>Помимо N+1: over-fetching — получение больше, чем нужно</h3>
<p>В уроке 5 мы видели N+1 — "слишком много МАЛЕНЬКИХ запросов".
Over-fetching — противоположная проблема: "ОДИН запрос, но приносящий
БОЛЬШЕ данных, чем нужно". Например, <code>select(Course)</code> получает
ВСЕ колонки Course, даже если frontend показывает только <code>title</code>
и <code>id</code>. Большие колонки <code>description</code> или
<code>text_content</code> (на этой платформе они типа Text, могут быть до
тысяч символов) тратят ненужный сетевой трафик и память при каждом
запросе.</p>

<h3>load_only() — выбор только нужных колонок</h3>
<p>В ORM для загрузки только нужных колонок вместо всего объекта
используется <code>.options(load_only(Course.id, Course.title))</code>.
Это особенно важно на страницах со списками (например каталог курсов),
где пользователь видит не полный текст <code>text_content</code>, а
только заголовок и краткое описание. Альтернативное решение — вообще не
загружать объект ORM, а получить только нужные колонки через
<code>select(Course.id, Course.title)</code> — в этом случае результат не
объект Course, а Row (вспомните урок 4).</p>

<h3>Connection pool — почему он не бесконечен</h3>
<p>Внутри Engine из урока 1 есть пул подключений — набор заранее открытых,
переиспользуемых подключений к PostgreSQL. Этот пул ОГРАНИЧЕН (обычно
5-20 подключений). Если Session не закрываются правильно (нарушено
правило контекстного менеджера из урока 6) или один запрос выполняется
слишком долго, пул исчерпывается — новые запросы навсегда зависают в
состоянии "ожидание подключения", что может остановить весь сервер.</p>

<h3>Исчерпание пула — причины и признаки</h3>
<p>Самые частые причины исчерпания пула: (1) Session остаётся открытой и
никогда не закрывается (например блок <code>finally</code> обойдён
из-за ошибки); (2) в рамках одного запроса открывается слишком много
отдельных Session; (3) долго выполняющиеся транзакции (например неверный,
выполняемый разом backfill из урока 9) мешают другим запросам получить
подключение. Признак — ошибка вида
<code>QueuePool limit of size N overflow O reached</code> в
production-логах.</p>

<h3>pool_size и pool_timeout — параметры настройки</h3>
<p><code>create_async_engine(url, pool_size=10, max_overflow=5,
pool_timeout=30)</code> — <code>pool_size</code> задаёт число постоянных
подключений, <code>max_overflow</code> — временные дополнительные,
<code>pool_timeout</code> — время ожидания свободного подключения.
Увеличение этих чисел — не "исправление": если Session не закрываются
правильно, даже больший пул в итоге исчерпается, просто позже. Настоящее
решение — сократить время жизни Session и устранить N+1/over-fetching.</p>

<h3>Внешние вызовы внутри транзакций — скрытый пожиратель пула</h3>
<p>Вызов внешнего API внутри транзакции (например синхронизация с Gennis)
или долгое вычисление — самая скрытая причина занятости пула. Каждая
миллисекунда, пока транзакция открыта, означает, что подключение не
освобождается для других запросов. Правило: внешние сетевые вызовы ВСЕГДА
выполняются ВНЕ транзакции, и только когда результаты готовы, они
записываются в базу в короткой транзакции.</p>

<h3>EXPLAIN ANALYZE — проверка ORM-запроса тем же инструментом из курса 107</h3>
<p>Каким бы "удобным" ни был ORM, принцип проверки получившегося SQL через
изученный в курсе 107 <code>EXPLAIN ANALYZE</code> не меняется: получите
реальный текст SQL через <code>str(stmt.compile(compile_kwargs=
{"literal_binds": True}))</code>, затем запустите его напрямую в psql с
<code>EXPLAIN ANALYZE</code>. Это превращает расплывчатую жалобу "ORM
работает медленно" в точную диагностику "медленный именно ЭТОТ запрос, по
такой-то причине".</p>

<h3>Связь этого урока с checkpoint'ом R2</h3>
<p>Over-fetching, connection pool и долгие транзакции — все эти понятия
будут проверены в проекте checkpoint'а R2 в уроке 12. Они завершают тему
"второй половины" уроков 8-11: переход от написания моделей (первая
половина) к безопасному и эффективному управлению production-базой
(вторая половина). В следующем уроке ждёт практический проект,
объединяющий все эти понятия.</p>

<h3>Краткое правило для повседневной работы</h3>
<p>Если приходится запомнить только одно правило из этого урока: у
списковых запросов всегда должен быть явный список нужных колонок
(load_only или select(колонки)), а Session должна открываться и
закрываться в максимально узкой области видимости — только там, где
она действительно используется.</p>
""".strip()

L11_CODE = """
# ============================================================
# 1) Over-fetching — kerakmagan ustunlarni ham yuklash
# ============================================================
from sqlalchemy.orm import load_only

# XATO NAQSH — kurslar katalogi uchun BARCHA ustunlar yuklanadi:
all_columns_stmt = select(Course).order_by(Course.display_order).limit(20)
# Har bir Course obyektida description, text_content kabi katta ustunlar
# ham keladi — garchi katalog sahifasi faqat title/thumbnail ko'rsatsa ham.

# TO'G'RI NAQSH — faqat kerakli ustunlar:
catalog_stmt = (
    select(Course)
    .options(load_only(Course.id, Course.title, Course.thumbnail_url, Course.difficulty_level))
    .order_by(Course.display_order)
    .limit(20)
)
# Yoki umuman ORM obyektisiz, Core-uslubidagi so'rov (Row qaytadi):
lightweight_stmt = (
    select(Course.id, Course.title, Course.thumbnail_url)
    .order_by(Course.display_order)
    .limit(20)
)

# ============================================================
# 2) Connection pool — sozlash va monitoring
# ============================================================
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # doimiy ulanishlar soni
    max_overflow=5,       # vaqtinchalik qo'shimcha (yuqori yuklamada)
    pool_timeout=30,      # bo'sh ulanishni kutish vaqti (soniya)
    pool_pre_ping=True,   # ulanish ishlatishdan oldin "tirikligini" tekshiradi
)

# ============================================================
# 3) XATO NAQSH — Session yopilmay qolishi (pool tugashiga olib keladi)
# ============================================================
async def leaky_endpoint_BAD(course_id: int):
    session = AsyncSessionLocal()          # context manager ISHLATILMAGAN!
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    return course
    # session HECH QACHON yopilmaydi — ulanish pool'da abadiy band bo'lib qoladi.
    # Xato yoki erta return bo'lsa ham xuddi shu muammo takrorlanadi.

# TO'G'RI NAQSH — 6-darsdagi context manager qoidasi:
async def safe_endpoint_GOOD(course_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()
    # `async with` blokidan chiqishda — xato bo'lsa ham — ulanish pool'ga qaytadi.

# ============================================================
# 4) Uzoq tranzaksiya — pool'ni band qilib qo'yish
# ============================================================
async def slow_transaction_BAD(db):
    async with db.begin():
        courses = (await db.execute(select(Course))).scalars().all()
        for c in courses:
            await slow_external_api_call(c)   # HAR BIR kurs uchun tashqi API — SEKIN!
            c.last_synced_at = datetime.utcnow()
        # Tranzaksiya BUTUN sikl davomida ochiq qoladi — bu vaqtda ulanish
        # boshqa so'rovlar uchun bo'shamaydi.

# TO'G'RI: tashqi chaqiruvlarni tranzaksiyadan TASHQARIDA bajarish
async def fast_transaction_GOOD(db):
    courses = (await db.execute(select(Course))).scalars().all()
    results = [await slow_external_api_call(c) for c in courses]   # tranzaksiyasiz
    async with db.begin():
        for c, synced_at in zip(courses, results):
            c.last_synced_at = synced_at
        # Endi tranzaksiya QISQA — faqat yozish uchun ochiladi.

# ============================================================
# 5) Pool holatini monitoring qilish — muammoni oldindan sezish
# ============================================================
def log_pool_status(engine) -> None:
    pool = engine.pool
    print(
        f"pool size={pool.size()} "
        f"checked_out={pool.checkedout()} "   # hozir band bo'lgan ulanishlar
        f"overflow={pool.overflow()} "         # vaqtinchalik qo'shimcha ulanishlar
        f"checked_in={pool.checkedin()}"        # bo'sh, qayta ishlatishga tayyor
    )
# Agar checked_out doimiy ravishda pool_size'ga teng bo'lib qolsa (hech
# qachon pastga tushmasa) — bu Session'lar yopilmayotganining aniq belgisi.

# ============================================================
# 6) load_only() bilan avval/keyin — taxminiy trafik solishtiruvi
# ============================================================
# Faraz qilaylik: description ~800 belgi, text_content ~4500 belgi.
# 20 ta kurs uchun:
#   load_only() SIZ: 20 * (800 + 4500 + boshqa ustunlar) ≈ 110 000+ belgi
#   load_only() BILAN (faqat id, title, thumbnail_url, difficulty_level):
#       20 * ~150 belgi ≈ 3 000 belgi
# Bu — ro'yxat sahifasida 30 baravargacha kamroq trafik va xotira degani,
# hech qanday funksional yo'qotishsiz (chunki text_content baribir shu
# sahifada ko'rsatilmaydi).

# ============================================================
# 7) Haqiqiy production sozlashiga yaqinlashtirilgan Engine namunasi
# ============================================================
production_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # ko'proq uvicorn worker — ko'proq ulanish kerak
    max_overflow=10,
    pool_timeout=10,        # sukut bo'yichadan qisqaroq — muammoni tezroq bildiradi
    pool_recycle=1800,      # ulanishlarni har 30 daqiqada qayta ochish (baza tomonidan uzilishdan himoya)
    pool_pre_ping=True,
)
# pool_size uvicorn/gunicorn worker soni va PostgreSQL'ning o'zining
# max_connections chegarasi bilan mos kelishi kerak — agar 4 worker *
# pool_size=20 bazaning max_connections'idan oshib ketsa, ilova muammo
# kodga yetib bormasdan turib ulanish xatolarini olishni boshlaydi.

# ============================================================
# 8) OFFSET o'rniga kursor bilan sahifalash — yuklamani kamaytirishning yana bir yo'li
# ============================================================
# Katta jadvalda .offset(10000) PostgreSQL'ga kerakli sahifani qaytarishdan
# oldin 10000 qatorni o'tkazib yuborishga (o'qib, tashlab yuborishga)
# majbur qiladi — bu ham over-fetching'ga qarindosh ortiqcha ish turi.
async def get_courses_after_cursor(db, last_id: Optional[int], page_size: int = 20):
    stmt = select(Course).order_by(Course.id).limit(page_size)
    if last_id is not None:
        stmt = stmt.where(Course.id > last_id)   # OFFSET'siz — to'g'ridan-to'g'ri kerakli joydan
    return (await db.execute(stmt)).scalars().all()
# Kursor bilan sahifalash ayniqsa "cheksiz skroll" API'lari uchun foydali
# — 500-sahifa 1-sahifa kabi tez ishlaydi.
""".strip()

L11_CODE_RU = """
# ============================================================
# 1) Over-fetching — загрузка ненужных колонок
# ============================================================
from sqlalchemy.orm import load_only

# НЕВЕРНЫЙ ПАТТЕРН — для каталога курсов загружаются ВСЕ колонки:
all_columns_stmt = select(Course).order_by(Course.display_order).limit(20)
# В каждом объекте Course приходят и большие колонки вроде description,
# text_content — хотя страница каталога показывает только title/thumbnail.

# ПРАВИЛЬНЫЙ ПАТТЕРН — только нужные колонки:
catalog_stmt = (
    select(Course)
    .options(load_only(Course.id, Course.title, Course.thumbnail_url, Course.difficulty_level))
    .order_by(Course.display_order)
    .limit(20)
)
# Или вообще без объекта ORM, запрос в стиле Core (возвращается Row):
lightweight_stmt = (
    select(Course.id, Course.title, Course.thumbnail_url)
    .order_by(Course.display_order)
    .limit(20)
)

# ============================================================
# 2) Connection pool — настройка и мониторинг
# ============================================================
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # число постоянных подключений
    max_overflow=5,       # временные дополнительные (при высокой нагрузке)
    pool_timeout=30,      # время ожидания свободного подключения (секунды)
    pool_pre_ping=True,   # проверяет "живость" подключения перед использованием
)

# ============================================================
# 3) НЕВЕРНЫЙ ПАТТЕРН — незакрытая Session (ведёт к исчерпанию пула)
# ============================================================
async def leaky_endpoint_BAD(course_id: int):
    session = AsyncSessionLocal()          # контекстный менеджер НЕ ИСПОЛЬЗОВАН!
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    return course
    # session НИКОГДА не закрывается — подключение навсегда занято в пуле.
    # При ошибке или раннем return проблема повторяется точно так же.

# ПРАВИЛЬНЫЙ ПАТТЕРН — правило контекстного менеджера из урока 6:
async def safe_endpoint_GOOD(course_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()
    # При выходе из блока `async with` — даже при ошибке — подключение возвращается в пул.

# ============================================================
# 4) Долгая транзакция — занимает пул
# ============================================================
async def slow_transaction_BAD(db):
    async with db.begin():
        courses = (await db.execute(select(Course))).scalars().all()
        for c in courses:
            await slow_external_api_call(c)   # внешний API для КАЖДОГО курса — МЕДЛЕННО!
            c.last_synced_at = datetime.utcnow()
        # Транзакция остаётся открытой на ВЕСЬ цикл — в это время подключение
        # не освобождается для других запросов.

# ПРАВИЛЬНО: внешние вызовы выполняются ВНЕ транзакции
async def fast_transaction_GOOD(db):
    courses = (await db.execute(select(Course))).scalars().all()
    results = [await slow_external_api_call(c) for c in courses]   # без транзакции
    async with db.begin():
        for c, synced_at in zip(courses, results):
            c.last_synced_at = synced_at
        # Теперь транзакция КОРОТКАЯ — открывается только для записи.

# ============================================================
# 5) Мониторинг состояния пула — обнаружение проблемы заранее
# ============================================================
def log_pool_status(engine) -> None:
    pool = engine.pool
    print(
        f"pool size={pool.size()} "
        f"checked_out={pool.checkedout()} "   # сейчас занятые подключения
        f"overflow={pool.overflow()} "         # временные дополнительные подключения
        f"checked_in={pool.checkedin()}"        # свободные, готовые к переиспользованию
    )
# Если checked_out постоянно равен pool_size (никогда не снижается) —
# это явный признак того, что Session не закрываются.

# ============================================================
# 6) load_only() до/после — приблизительное сравнение трафика
# ============================================================
# Предположим: description ~800 символов, text_content ~4500 символов.
# Для 20 курсов:
#   БЕЗ load_only(): 20 * (800 + 4500 + другие колонки) ≈ 110 000+ символов
#   С load_only() (только id, title, thumbnail_url, difficulty_level):
#       20 * ~150 символов ≈ 3 000 символов
# Это означает до 30 раз меньше трафика и памяти на странице списка, без
# потери функциональности (поскольку text_content всё равно не
# показывается на этой странице).

# ============================================================
# 7) Пример настройки Engine, приближённой к реальной production-конфигурации
# ============================================================
production_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # больше воркеров uvicorn — больше нужно подключений
    max_overflow=10,
    pool_timeout=10,        # короче, чем по умолчанию — быстрее сигнализирует о проблеме
    pool_recycle=1800,      # переоткрывать подключения раз в 30 минут (защита от разрыва со стороны БД)
    pool_pre_ping=True,
)
# pool_size должен соотноситься с числом воркеров uvicorn/gunicorn и
# лимитом max_connections самого PostgreSQL — если 4 воркера * pool_size=20
# превышают max_connections базы, приложение будет получать ошибки
# подключения ещё до того, как проблема дойдёт до кода.

# ============================================================
# 8) Пагинация с курсором вместо OFFSET — ещё один способ снизить нагрузку
# ============================================================
# .offset(10000) на большой таблице заставляет PostgreSQL пропустить
# (прочитать и отбросить) 10000 строк перед тем, как вернуть нужную
# страницу — это тоже вид избыточной работы, родственный over-fetching.
async def get_courses_after_cursor(db, last_id: Optional[int], page_size: int = 20):
    stmt = select(Course).order_by(Course.id).limit(page_size)
    if last_id is not None:
        stmt = stmt.where(Course.id > last_id)   # без OFFSET — сразу с нужного места
    return (await db.execute(stmt)).scalars().all()
# Курсорная пагинация особенно полезна для API с "бесконечной прокруткой",
# где страница 500 так же быстра, как страница 1.
""".strip()

L11_TASK = {
    "task_title": "Kurslar katalogini over-fetching'siz optimallashtirish",
    "task_title_ru": "Оптимизация каталога курсов без over-fetching",
    "task_description": (
        "get_course_catalog(db, page, page_size) funksiyasini yozing: "
        "faqat katalog kartochkasi uchun kerakli ustunlarni (id, title, "
        "thumbnail_url, difficulty_level, duration_weeks) yuklaydigan, "
        "load_only() yoki select(ustunlar) orqali. Funksiyani "
        "'to'liq obyekt yuklovchi' versiyasi bilan solishtirib, nechta "
        "baytga yaqin trafik tejalganini (taxminan) hisoblab ko'rsating."
    ),
    "task_description_ru": (
        "Напишите функцию get_course_catalog(db, page, page_size): "
        "загружает только нужные для карточки каталога колонки (id, "
        "title, thumbnail_url, difficulty_level, duration_weeks), через "
        "load_only() или select(колонки). Сравните с версией, 'загружающей "
        "полный объект', и приблизительно посчитайте, сколько байт трафика "
        "экономится."
    ),
    "task_requirements": (
        "1) load_only() yoki select(ustunlar) ishlatilgan. 2) .limit()/"
        ".offset() sahifalash bilan. 3) 'to'liq yuklash' vs 'optimallashtirilgan' "
        "versiyalarni yonma-yon keltiring. 4) description/text_content "
        "ustunlari o'rtacha necha belgi ekanini (taxminiy) hisobga olib, "
        "tejalgan trafikni baholang."
    ),
    "task_requirements_ru": (
        "1) Использован load_only() или select(колонки). 2) Пагинация "
        "через .limit()/.offset(). 3) Приведите рядом версии 'полная "
        "загрузка' vs 'оптимизированная'. 4) Оцените сэкономленный трафик, "
        "учитывая примерную длину колонок description/text_content."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 4,
}

L11_SAMPLE = {
    "title": "Namuna: over-fetching'siz katalog + xavfsiz Session",
    "description": "load_only() bilan optimallashtirilgan katalog so'rovi va context manager orqali xavfsiz Session boshqaruvi.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "course_catalog.py",
            "language": "python",
            "code": (
                "from sqlalchemy import select\n"
                "from sqlalchemy.orm import load_only\n"
                "from sqlalchemy.ext.asyncio import AsyncSession\n\n\n"
                "async def get_course_catalog(db: AsyncSession, page: int = 1, page_size: int = 12):\n"
                "    stmt = (\n"
                "        select(Course)\n"
                "        .options(load_only(\n"
                "            Course.id, Course.title, Course.thumbnail_url,\n"
                "            Course.difficulty_level, Course.duration_weeks,\n"
                "        ))\n"
                "        .order_by(Course.display_order)\n"
                "        .limit(page_size)\n"
                "        .offset((page - 1) * page_size)\n"
                "    )\n"
                "    return (await db.execute(stmt)).scalars().all()\n"
                "    # description va text_content kabi katta ustunlar YUKLANMAYDI —\n"
                "    # ularga murojaat qilinsa, ORM keyinroq alohida so'rov yuboradi\n"
                "    # (bu 'deferred column' xatti-harakati, N+1'ga o'xshaydi — shuning\n"
                "    # uchun katalog sahifasida ularga HECH QACHON murojaat qilinmasligi kerak).\n"
            ),
        },
    ],
}

L11_EXERCISES = [
    {
        "title": "N+1 vs over-fetching",
        "title_ru": "N+1 против over-fetching",
        "description": "Over-fetching N+1'dan qanday farq qiladi?",
        "description_ru": "Чем over-fetching отличается от N+1?",
        "exercise_type": "multiple_choice",
        "options": [
            "Over-fetching — bitta so'rovda ortiqcha ma'lumot, N+1 — juda ko'p kichik so'rov",
            "Ular bir xil muammoning ikki nomi",
            "Over-fetching faqat Core'da, N+1 faqat ORM'da bo'ladi",
            "Over-fetching xavfsiz, N+1 esa har doim xato",
        ],
        "options_ru": [
            "Over-fetching — избыток данных в одном запросе, N+1 — слишком много маленьких запросов",
            "Это два названия одной и той же проблемы",
            "Over-fetching бывает только в Core, N+1 только в ORM",
            "Over-fetching безопасен, а N+1 всегда ошибка",
        ],
        "correct_answers": "A",
        "hint": "Bittasi 'juda ko'p so'rov' sonini, ikkinchisi 'bitta so'rovdagi ortiqcha ma'lumot'ni bildiradi.",
        "hint_ru": "Одна проблема про 'слишком много запросов', другая — про 'избыток данных в одном запросе'.",
        "explanation": "N+1 — ko'p sonli kichik so'rovlar; over-fetching — bitta so'rovda kerakmagan ko'p ustun/qator.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Pool tugashining asosiy sababi",
        "title_ru": "Основная причина исчерпания пула",
        "description": "Connection pool tugashining ENG KENG TARQALGAN sababi nima?",
        "description_ru": "Какая САМАЯ распространённая причина исчерпания connection pool?",
        "exercise_type": "multiple_choice",
        "options": [
            "Session'lar to'g'ri yopilmasligi (context manager ishlatilmasligi)",
            "PostgreSQL'ning o'zi juda sekin ishlashi",
            "Juda ko'p relationship() e'lon qilinishi",
            "Model fayllarining juda katta bo'lishi",
        ],
        "options_ru": [
            "Session не закрываются правильно (не используется контекстный менеджер)",
            "Сам PostgreSQL работает слишком медленно",
            "Объявлено слишком много relationship()",
            "Слишком большой размер файлов моделей",
        ],
        "correct_answers": "A",
        "hint": "6-dars — Session xavfsizligi va 11-dars bir-biriga bevosita bog'liq.",
        "hint_ru": "Урок 6 — безопасность Session — напрямую связан с уроком 11.",
        "explanation": "Yopilmagan Session ulanishni pool'ga qaytarmaydi — bu pool tugashining eng keng tarqalgan sababi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Optimallashtirish qadamlarini tartiblang",
        "title_ru": "Расположите шаги оптимизации по порядку",
        "description": "Sekin endpoint'ni diagnostika qilish va tuzatishning odatiy qadamlarini joylashtiring.",
        "description_ru": "Расположите типичные шаги диагностики и исправления медленного эндпоинта.",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "echo=True bilan bajarilgan SQL sonini ko'rish",
            "N+1 yoki over-fetching ekanini aniqlash",
            "selectinload() yoki load_only() qo'shish",
            "Connection pool ko'rsatkichlarini qayta tekshirish",
        ],
        "drag_items_ru": [
            "Посмотреть число выполненных SQL через echo=True",
            "Определить, N+1 это или over-fetching",
            "Добавить selectinload() или load_only()",
            "Повторно проверить показатели connection pool",
        ],
        "correct_order": [
            "echo=True bilan bajarilgan SQL sonini ko'rish",
            "N+1 yoki over-fetching ekanini aniqlash",
            "selectinload() yoki load_only() qo'shish",
            "Connection pool ko'rsatkichlarini qayta tekshirish",
        ],
        "hint": "Avval kuzatish, keyin diagnostika, keyin tuzatish, oxirida natijani tekshirish.",
        "hint_ru": "Сначала наблюдение, потом диагностика, потом исправление, в конце проверка результата.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 12 — R2: Takrorlash — migratsiya va performance bo'yicha amaliyot
# ---------------------------------------------------------------------------

L12_TEXT = """
<h3>Ikkinchi yarim yakunlandi — modeldan production'gacha</h3>
<p>8-11-darslarda siz butunlay yangi mas'uliyat qatlamini o'rgandingiz:
model yozish yetarli emas, uni HAQIQIY, ishlab turgan production bazasiga
XAVFSIZ yetkazish kerak. Alembic'ning revision zanjiri (8-dars), uch
bosqichli xavfsiz ustun qo'shish (9-dars), autogenerate'ning haqiqiy
xatolari (10-dars, aynan shu platformaning o'z tarixidan), va nihoyat
ORM'ning performance tuzoqlari — over-fetching va connection pool
(11-dars). Bu — "men modelni to'g'ri yozaman" bilan "men production'ni
buzmayman" orasidagi farqni beruvchi bilim.</p>

<h3>Eng ko'p uchraydigan xatolar — ikkinchi yarim bo'yicha</h3>
<ul>
<li><strong>Bitta katta migratsiyada hammasini qilish</strong> (9-dars) —
nullable qo'shish, backfill va NOT NULL qilish ALOHIDA migratsiyalarda
bo'lishi kerak.</li>
<li><strong>autogenerate'ni ko'rmasdan qo'llash</strong> (10-dars) — rename
har doim drop+add sifatida taklif qilinishi mumkin, bu MA'LUMOT YO'QOTADI.</li>
<li><strong>Session'ni yopmasdan qoldirish</strong> (11-dars) — bu pool
tugashiga va butun serverning to'xtashiga olib kelishi mumkin.</li>
<li><strong>Tranzaksiya ichida tashqi chaqiruv qilish</strong> (11-dars) —
ulanishni keraksiz uzoq band qilib qo'yadi.</li>
</ul>

<h3>Bu darsning loyihasi — migratsiya + performance birgalikda</h3>
<p>Bugungi amaliy loyihada siz R1'dagi LessonFeedback tizimiga yangi
funksiya qo'shasiz: <code>helpful_count</code> ustuni (boshqa talabalar
"foydali" deb belgilagan fikrlar soni). Bu ustunni XAVFSIZ qo'shish
(9-dars naqshi bo'yicha), so'ngra uni ko'rsatuvchi so'rovni
over-fetching'siz yozish (11-dars) — ikkala yarimni bitta amaliy vazifada
birlashtiradi.</p>

<h3>Kurs oxiriga tayyorgarlik</h3>
<p>13-dars — capstone — butun kursning yakuniy sinovi: yangi funksiya
uchun to'liq ORM sxemasi VA migratsiya rejasini boshidan oxirigacha
loyihalash. U yerda 0-12-darslarning barcha tushunchalari kerak bo'ladi —
bu darsning maqsadi shu oxirgi qadam uchun tayyorgarlik ko'rishdir.</p>

<h3>Nega bu ikkita mavzu (migratsiya + performance) birga tekshiriladi</h3>
<p>Real loyihalarda bu ikkalasi kamdan-kam alohida uchraydi: yangi ustun
qo'shish (migratsiya masalasi) deyarli har doim "bu ustunni qanday
samarali o'qish kerak" (performance masalasi) degan savol bilan birga
keladi. Shuning uchun bu checkpoint ularni ATAYLAB birlashtirgan holda
sinaydi — xuddi production'da bo'lgani kabi, ikkalasi bir vaqtda hal
qilinishi kerak bo'lgan yagona vazifa sifatida.</p>

<h3>O'z-o'zini tekshirish: ikkinchi yarim uchun</h3>
<p>Loyihani topshirishdan oldin: har bir migratsiyangiz alohida-alohida
<code>downgrade()</code>ga egami? Katta jadval uchun mo'ljallangan
o'zgarishlarni 3 bosqichga bo'ldingizmi? So'rovlaringizda faqat kerakli
ustunlar yuklanadimi? Session'lar har doim <code>async with</code> orqali
yopiladimi? Bu savollarning har biriga "ha" deb javob bera olish — bu
darsning haqiqiy maqsadi.</p>

<h3>Har bir darsning bir jumlada xulosasi (8-11-darslar)</h3>
<ul>
<li><strong>8-dars:</strong> migratsiya — modeldan production bazasigacha
bo'lgan versiyalangan ko'prik; revision zanjiri qaysi tartibda
qo'llanishini belgilaydi.</li>
<li><strong>9-dars:</strong> katta jadvalga NOT NULL ustun qo'shish —
har doim nullable+backfill+NOT NULL uch bosqichida, BITTA migratsiyada
emas.</li>
<li><strong>10-dars:</strong> autogenerate rename'ni drop+add deb ko'radi
— bu ma'lumot yo'qotadi; har bir taklif qo'lda tekshirilishi shart.</li>
<li><strong>11-dars:</strong> over-fetching — kerakmagan ustunlarni ham
yuklash; connection pool cheklangan, Session yopilmasa u tugaydi.</li>
</ul>

<h3>Nega aynan helpful_count tanlandi</h3>
<p>Bu misol ataylab tanlangan: u YANGI ustun qo'shishni (migratsiya),
uni over-fetching'siz ko'rsatishni (performance) va poyga holatidan
xavfsiz oshirishni (tranzaksiya) bitta kichik, lekin real vazifada
birlashtiradi — xuddi production'da haqiqiy funksiya so'ralganda
bo'lgani kabi.</p>

<h3>Nima uchun checkpoint loyihalari kichik, lekin to'liq bo'ladi</h3>
<p>R1 va R2'dagi loyihalar ataylab kichik hajmda saqlanadi — maqsad
"ko'p kod yozish" emas, balki "har bir tushunchani to'g'ri joyida
qo'llash"ni tekshirishdir. Kichik hajm katta ma'noni yashirmaydi: bitta
UniqueConstraint noto'g'ri qo'yilgan bo'lsa, yoki bitta selectinload()
unutilgan bo'lsa, bu kichik loyihada ham xuddi katta production kodidagi
kabi aniq ko'rinadi.</p>
""".strip()

L12_TEXT_RU = """
<h3>Вторая половина завершена — от модели до production</h3>
<p>В уроках 8-11 вы освоили совершенно новый уровень ответственности:
недостаточно написать модель — её нужно БЕЗОПАСНО довести до РЕАЛЬНОЙ,
работающей production-базы. Цепочка revision Alembic (урок 8),
трёхэтапное безопасное добавление колонки (урок 9), реальные ошибки
autogenerate (урок 10, из истории именно этой платформы), и наконец
ловушки производительности ORM — over-fetching и connection pool (урок
11). Это знание, дающее разницу между "я правильно пишу модель" и "я не
ломаю production".</p>

<h3>Самые частые ошибки — по второй половине</h3>
<ul>
<li><strong>Делать всё в одной большой миграции</strong> (урок 9) —
добавление nullable, backfill и установка NOT NULL должны быть ОТДЕЛЬНЫМИ
миграциями.</li>
<li><strong>Применять autogenerate не глядя</strong> (урок 10) —
переименование может быть предложено как drop+add, а это ТЕРЯЕТ ДАННЫЕ.</li>
<li><strong>Оставлять Session незакрытой</strong> (урок 11) — это может
привести к исчерпанию пула и остановке всего сервера.</li>
<li><strong>Делать внешний вызов внутри транзакции</strong> (урок 11) —
без нужды надолго занимает подключение.</li>
</ul>

<h3>Проект этого урока — миграция + производительность вместе</h3>
<p>В сегодняшнем практическом проекте вы добавите новую функцию в систему
LessonFeedback из R1: колонку <code>helpful_count</code> (число других
студентов, отметивших отзыв как "полезный"). Нужно БЕЗОПАСНО добавить эту
колонку (по паттерну урока 9), а затем написать запрос, показывающий её
без over-fetching (урок 11) — это объединяет обе половины в одной
практической задаче.</p>

<h3>Подготовка к финалу курса</h3>
<p>Урок 13 — capstone — финальное испытание всего курса: спроектировать
полную ORM-схему И план миграции для новой функции от начала до конца.
Там понадобятся все понятия уроков 0-12 — цель этого урока — подготовка к
этому последнему шагу.</p>

<h3>Почему эти две темы (миграция + производительность) проверяются вместе</h3>
<p>В реальных проектах они редко встречаются по отдельности: добавление
новой колонки (вопрос миграции) почти всегда сопровождается вопросом "как
эффективно читать эту колонку" (вопрос производительности). Поэтому этот
checkpoint НАМЕРЕННО объединяет их — как это происходит в production,
где оба вопроса решаются как одна общая задача.</p>

<h3>Самопроверка: по второй половине курса</h3>
<p>Перед сдачей проекта: у каждой вашей миграции есть отдельный
<code>downgrade()</code>? Изменения для большой таблицы разбиты на 3
этапа? В запросах загружаются только нужные колонки? Session всегда
закрывается через <code>async with</code>? Умение ответить "да" на каждый
из этих вопросов — истинная цель этого урока.</p>

<h3>Итог каждого урока одной фразой (уроки 8-11)</h3>
<ul>
<li><strong>Урок 8:</strong> миграция — версионированный мост от модели к
production-базе; цепочка revision определяет порядок применения.</li>
<li><strong>Урок 9:</strong> добавление NOT NULL колонки в большую
таблицу — всегда в 3 этапа (nullable+backfill+NOT NULL), а не в ОДНОЙ
миграции.</li>
<li><strong>Урок 10:</strong> autogenerate видит переименование как
drop+add — это теряет данные; каждое предложение нужно проверять
вручную.</li>
<li><strong>Урок 11:</strong> over-fetching — загрузка ненужных колонок;
connection pool ограничен, если Session не закрыта, он исчерпается.</li>
</ul>

<h3>Почему выбран именно helpful_count</h3>
<p>Этот пример выбран намеренно: он объединяет добавление НОВОЙ колонки
(миграция), её отображение без over-fetching (производительность) и
безопасное при гонке увеличение (транзакция) в одной небольшой, но
реальной задаче — именно так, как это происходит, когда в production
запрашивают настоящую функцию.</p>

<h3>Почему проекты checkpoint небольшие, но полные</h3>
<p>Проекты в R1 и R2 намеренно небольшие по объёму — цель не "написать
много кода", а проверить "правильное применение каждого понятия на своём
месте". Небольшой объём не скрывает большого смысла: если один
UniqueConstraint задан неверно или забыт один selectinload(), это видно
в маленьком проекте так же чётко, как и в большом production-коде.
Именно поэтому проверяющий агент читает не только "работает ли код", но
и каждое отдельное архитектурное решение.</p>
""".strip()

L12_CODE = """
# ============================================================
# Bugungi loyiha: helpful_count — 9-dars (xavfsiz migratsiya) +
# 11-dars (over-fetching'siz so'rov) birgalikda
# ============================================================

# --- 9-dars naqshi: 3 bosqichli xavfsiz ustun qo'shish ---
# Migratsiya 1:
def upgrade_add_helpful_count() -> None:
    op.add_column(
        'lesson_feedback',
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
    )

# Migratsiya 2 — backfill (aslida barchasi 0 bo'lgani uchun bu holatda
# server_default allaqachon yetarli, lekin agar boshqa jadvaldan
# hisoblash kerak bo'lsa — bu qadam ZARUR bo'lardi):
def upgrade_backfill_helpful_count() -> None:
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE lesson_feedback SET helpful_count = 0 WHERE helpful_count IS NULL"
    ))

# Migratsiya 3:
def upgrade_finalize_helpful_count() -> None:
    op.alter_column('lesson_feedback', 'helpful_count', nullable=False)


# --- 11-dars naqshi: over-fetching'siz ko'rsatish ---
from sqlalchemy.orm import load_only

async def get_top_helpful_feedback(db, lesson_id: int, limit: int = 5):
    stmt = (
        select(LessonFeedback)
        .where(LessonFeedback.lesson_id == lesson_id)
        .options(load_only(LessonFeedback.id, LessonFeedback.rating, LessonFeedback.helpful_count))
        .order_by(LessonFeedback.helpful_count.desc())
        .limit(limit)
    )
    return (await db.execute(stmt)).scalars().all()
    # comment ustuni (potentsial uzun matn) YUKLANMAYDI — faqat ro'yxat
    # ko'rinishida kerak bo'lgan qisqa maydonlar keladi.


# --- 6-dars naqshi: helpful_count'ni xavfsiz oshirish (poyga holati) ---
from sqlalchemy import update

async def mark_feedback_helpful(db, feedback_id: int) -> bool:
    stmt = (
        update(LessonFeedback)
        .where(LessonFeedback.id == feedback_id)
        .values(helpful_count=LessonFeedback.helpful_count + 1)   # DB darajasida +1 — poyga xavfsiz
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
    # Diqqat: bu yerda avval o'qib, keyin +1 qilib yozish (read-modify-write)
    # o'RNIGA to'g'ridan-to'g'ri UPDATE ... SET x = x + 1 ishlatildi — bu
    # ikkita parallel so'rov bir-birining ustidan yozib yubormasligini
    # kafolatlaydi (Core darajasidagi atomik operatsiya, 1-darsni eslang).

# ============================================================
# To'liq Alembic migratsiya fayli — 3 bosqichni HAQIQIY fayl formatida
# (odatda bular 3 ta ALOHIDA fayl bo'ladi, bu yerda o'quv maqsadida
# ketma-ket bitta faylda ko'rsatilgan)
# ============================================================
\"\"\"add helpful_count to lesson_feedback (3-step safe pattern)

Revision ID: ff66aa77bb88
Revises: ee55ff66aa77
Create Date: 2026-08-01
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff66aa77bb88'
down_revision = 'ee55ff66aa77'


def upgrade() -> None:
    # 1-bosqich: nullable ustun, server_default bilan (deyarli zararsiz)
    op.add_column(
        'lesson_feedback',
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
    )
    # 2-bosqich: backfill — bu holatda server_default allaqachon 0 qo'ygani
    # uchun texnik jihatdan ortiqcha, lekin naqshni ko'rsatish uchun qoldirilgan
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE lesson_feedback SET helpful_count = 0 WHERE helpful_count IS NULL"
    ))
    # 3-bosqich: endi hammasi to'lgani aniq — NOT NULL qilish xavfsiz
    op.alter_column('lesson_feedback', 'helpful_count', nullable=False)


def downgrade() -> None:
    op.drop_column('lesson_feedback', 'helpful_count')

# ============================================================
# Round-trip sinovi — production'ga qo'llashdan OLDIN (8-dars naqshi)
# ============================================================
#   alembic upgrade head
#   alembic downgrade -1
#   alembic upgrade head
# Uchala buyruq ham xatosiz o'tishi kerak — aks holda downgrade() da xato bor.

# ============================================================
# To'liq hayotiy tsikl: FastAPI endpoint'idan xavfsiz yozishgacha
# ============================================================
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/lessons/{lesson_id}/feedback/{feedback_id}/helpful")
async def mark_helpful_endpoint(
    lesson_id: int, feedback_id: int, db: AsyncSession = Depends(get_db)
):
    ok = await mark_feedback_helpful(db, feedback_id)
    return {"success": ok}
    # `db` — Depends(get_db) orqali Session (6-dars), funksiya qisqa va
    # atomik UPDATE ishlatadi (6-dars), ortiqcha ustunlarni o'qimaydi
    # (11-dars), va ustunning o'zi xavfsiz 3 bosqichli migratsiya bilan
    # qo'shilgan (9-dars). Bitta kichik endpoint — lekin unda kursning
    # besh darsi mujassam.

# ============================================================
# Atomik UPDATE'siz muqobil — nega undan qochiladi
# ============================================================
async def mark_feedback_helpful_RISKY(db, feedback_id: int) -> bool:
    feedback = await db.get(LessonFeedback, feedback_id)
    if feedback is None:
        return False
    feedback.helpful_count = feedback.helpful_count + 1   # Python'da read-modify-write
    await db.commit()
    return True
# Agar ikkita so'rov bir vaqtda helpful_count=5'ni o'qisa, ikkalasi ham
# 6'ni hisoblab, 6'ni yozadi — garchi to'g'ri natija 7 bo'lishi kerak
# bo'lsa ham. Bu xato hech qanday istisno (exception) tashlamaydi va
# loglarda ko'rinmaydi — bitta "foydali" ovoz jimgina yo'qoladi. Aynan
# shuning uchun yuqoridagi mark_feedback_helpful()da baza darajasidagi
# UPDATE ... SET x = x + 1 ishlatiladi, bu versiya emas.
""".strip()

L12_CODE_RU = """
# ============================================================
# Проект урока: helpful_count — урок 9 (безопасная миграция) +
# урок 11 (запрос без over-fetching) вместе
# ============================================================

# --- Паттерн урока 9: безопасное добавление колонки в 3 этапа ---
# Миграция 1:
def upgrade_add_helpful_count() -> None:
    op.add_column(
        'lesson_feedback',
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
    )

# Миграция 2 — backfill (в данном случае все и так будут 0 благодаря
# server_default, но если бы значение нужно было вычислить из другой
# таблицы — этот шаг был бы НЕОБХОДИМ):
def upgrade_backfill_helpful_count() -> None:
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE lesson_feedback SET helpful_count = 0 WHERE helpful_count IS NULL"
    ))

# Миграция 3:
def upgrade_finalize_helpful_count() -> None:
    op.alter_column('lesson_feedback', 'helpful_count', nullable=False)


# --- Паттерн урока 11: отображение без over-fetching ---
from sqlalchemy.orm import load_only

async def get_top_helpful_feedback(db, lesson_id: int, limit: int = 5):
    stmt = (
        select(LessonFeedback)
        .where(LessonFeedback.lesson_id == lesson_id)
        .options(load_only(LessonFeedback.id, LessonFeedback.rating, LessonFeedback.helpful_count))
        .order_by(LessonFeedback.helpful_count.desc())
        .limit(limit)
    )
    return (await db.execute(stmt)).scalars().all()
    # Колонка comment (потенциально длинный текст) НЕ ЗАГРУЖАЕТСЯ —
    # приходят только короткие поля, нужные для списка.


# --- Паттерн урока 6: безопасное увеличение helpful_count (гонка) ---
from sqlalchemy import update

async def mark_feedback_helpful(db, feedback_id: int) -> bool:
    stmt = (
        update(LessonFeedback)
        .where(LessonFeedback.id == feedback_id)
        .values(helpful_count=LessonFeedback.helpful_count + 1)   # +1 на уровне БД — безопасно при гонке
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
    # Внимание: вместо чтения, затем +1 и записи (read-modify-write)
    # используется прямой UPDATE ... SET x = x + 1 — это гарантирует, что
    # два параллельных запроса не перезапишут друг друга (атомарная
    # операция на уровне Core, вспомните урок 1).

# ============================================================
# Полный файл миграции Alembic — 3 этапа в РЕАЛЬНОМ формате файла
# (обычно это 3 ОТДЕЛЬНЫХ файла, здесь для учебных целей показаны
# последовательно в одном)
# ============================================================
\"\"\"add helpful_count to lesson_feedback (3-step safe pattern)

Revision ID: ff66aa77bb88
Revises: ee55ff66aa77
Create Date: 2026-08-01
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = 'ff66aa77bb88'
down_revision = 'ee55ff66aa77'


def upgrade() -> None:
    # Этап 1: nullable колонка, с server_default (почти безвредно)
    op.add_column(
        'lesson_feedback',
        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),
    )
    # Этап 2: backfill — в данном случае технически излишен, так как
    # server_default уже поставил 0, но оставлен для демонстрации паттерна
    connection = op.get_bind()
    connection.execute(sa.text(
        "UPDATE lesson_feedback SET helpful_count = 0 WHERE helpful_count IS NULL"
    ))
    # Этап 3: теперь точно всё заполнено — установка NOT NULL безопасна
    op.alter_column('lesson_feedback', 'helpful_count', nullable=False)


def downgrade() -> None:
    op.drop_column('lesson_feedback', 'helpful_count')

# ============================================================
# Проверка round-trip — ПЕРЕД применением в production (паттерн урока 8)
# ============================================================
#   alembic upgrade head
#   alembic downgrade -1
#   alembic upgrade head
# Все три команды должны пройти без ошибок — иначе в downgrade() есть ошибка.

# ============================================================
# Полный жизненный цикл: от эндпоинта FastAPI до безопасной записи
# ============================================================
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/lessons/{lesson_id}/feedback/{feedback_id}/helpful")
async def mark_helpful_endpoint(
    lesson_id: int, feedback_id: int, db: AsyncSession = Depends(get_db)
):
    ok = await mark_feedback_helpful(db, feedback_id)
    return {"success": ok}
    # `db` — Session через Depends(get_db) (урок 6), функция короткая и
    # использует атомарный UPDATE (урок 6), не читает лишние колонки
    # (урок 11), а сама колонка добавлена безопасной 3-этапной миграцией
    # (урок 9). Один маленький эндпоинт — но в нём пять уроков курса.

# ============================================================
# Альтернатива without atomic UPDATE — почему её избегают
# ============================================================
async def mark_feedback_helpful_RISKY(db, feedback_id: int) -> bool:
    feedback = await db.get(LessonFeedback, feedback_id)
    if feedback is None:
        return False
    feedback.helpful_count = feedback.helpful_count + 1   # read-modify-write в Python
    await db.commit()
    return True
# Если два запроса одновременно прочитают helpful_count=5, оба вычислят
# 6 и запишут 6 — хотя правильный результат должен быть 7. Такая ошибка
# не выдаёт исключения и не попадает в логи — просто тихо теряется один
# "полезный" голос. Именно поэтому в mark_feedback_helpful() выше
# используется UPDATE ... SET x = x + 1 на уровне базы, а не эта версия.
""".strip()

L12_TASK = {
    "task_title": "Checkpoint loyiha: helpful_count — migratsiya + so'rov",
    "task_title_ru": "Проект-checkpoint: helpful_count — миграция + запрос",
    "task_description": (
        "R1'dagi LessonFeedback tizimiga helpful_count (Integer, NOT NULL, "
        "default 0) ustunini XAVFSIZ qo'shing: (1) 3 bosqichli migratsiya "
        "rejasi (9-dars naqshi); (2) get_top_helpful_feedback() — "
        "load_only() bilan over-fetching'siz (11-dars); (3) "
        "mark_feedback_helpful() — UPDATE ... SET x = x + 1 orqali poyga "
        "holatidan xavfsiz oshirish (6-dars)."
    ),
    "task_description_ru": (
        "БЕЗОПАСНО добавьте в систему LessonFeedback из R1 колонку "
        "helpful_count (Integer, NOT NULL, default 0): (1) план миграции "
        "из 3 этапов (паттерн урока 9); (2) get_top_helpful_feedback() — "
        "без over-fetching через load_only() (урок 11); (3) "
        "mark_feedback_helpful() — безопасное при гонке увеличение через "
        "UPDATE ... SET x = x + 1 (урок 6)."
    ),
    "task_requirements": (
        "1) 3 ta alohida migratsiya funksiyasi/fayli. 2) load_only() "
        "ishlatilgan so'rov. 3) UPDATE orqali atomik +1 (read-modify-write "
        "EMAS). 4) Har bir qismning qaysi darsga tegishli ekanini izohda "
        "ko'rsating."
    ),
    "task_requirements_ru": (
        "1) 3 отдельные функции/файла миграции. 2) Запрос с "
        "использованием load_only(). 3) Атомарное +1 через UPDATE (НЕ "
        "read-modify-write). 4) В комментарии укажите, к какому уроку "
        "относится каждая часть."
    ),
    "task_technologies": "Python, Alembic, SQLAlchemy 2.x ORM (async), PostgreSQL",
    "task_deadline_days": 6,
}

L12_SAMPLE = {
    "title": "Namuna: helpful_count — to'liq migratsiya + so'rov + atomik yangilash",
    "description": "8-11-darslarning barcha tushunchalarini birlashtiruvchi to'liq, ishga tayyor modul.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "helpful_count_migration.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'ee44ff55aa66'\n"
                "down_revision = 'dd33ee44ff55'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.add_column(\n"
                "        'lesson_feedback',\n"
                "        sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'),\n"
                "    )\n"
                "    connection = op.get_bind()\n"
                "    connection.execute(sa.text(\n"
                "        \"UPDATE lesson_feedback SET helpful_count = 0 WHERE helpful_count IS NULL\"\n"
                "    ))\n"
                "    op.alter_column('lesson_feedback', 'helpful_count', nullable=False)\n\n\n"
                "def downgrade() -> None:\n"
                "    op.drop_column('lesson_feedback', 'helpful_count')\n"
            ),
        },
        {
            "filename": "helpful_count_queries.py",
            "language": "python",
            "code": (
                "from sqlalchemy import select, update\n"
                "from sqlalchemy.orm import load_only\n\n\n"
                "async def get_top_helpful_feedback(db, lesson_id: int, limit: int = 5):\n"
                "    stmt = (\n"
                "        select(LessonFeedback)\n"
                "        .where(LessonFeedback.lesson_id == lesson_id)\n"
                "        .options(load_only(LessonFeedback.id, LessonFeedback.rating, LessonFeedback.helpful_count))\n"
                "        .order_by(LessonFeedback.helpful_count.desc())\n"
                "        .limit(limit)\n"
                "    )\n"
                "    return (await db.execute(stmt)).scalars().all()\n\n\n"
                "async def mark_feedback_helpful(db, feedback_id: int) -> bool:\n"
                "    stmt = (\n"
                "        update(LessonFeedback)\n"
                "        .where(LessonFeedback.id == feedback_id)\n"
                "        .values(helpful_count=LessonFeedback.helpful_count + 1)\n"
                "    )\n"
                "    result = await db.execute(stmt)\n"
                "    await db.commit()\n"
                "    return result.rowcount > 0\n"
            ),
        },
    ],
}

L12_EXERCISES = [
    {
        "title": "helpful_count'ni oshirishning xavfsiz usuli",
        "title_ru": "Безопасный способ увеличить helpful_count",
        "description": "Poyga holatidan xavfsiz bo'lish uchun ustunni oshirishning ENG TO'G'RI usuli qaysi?",
        "description_ru": "Какой способ увеличения колонки САМЫЙ ПРАВИЛЬНЫЙ с точки зрения безопасности при гонке?",
        "exercise_type": "multiple_choice",
        "options": [
            "UPDATE ... SET x = x + 1 (bazada, atomik)",
            "Avval o'qib, +1 qilib, keyin yozish (Python'da)",
            "Har doim butun jadvalni qayta hisoblash",
            "Faqat frontend'da hisoblab, bazaga tegmaslik",
        ],
        "options_ru": [
            "UPDATE ... SET x = x + 1 (в базе, атомарно)",
            "Сначала прочитать, +1 в Python, потом записать",
            "Всегда пересчитывать всю таблицу заново",
            "Считать только на frontend, не трогая базу",
        ],
        "correct_answers": "A",
        "hint": "Read-modify-write ikkita parallel so'rovda bir-birini yo'qotib qo'yishi mumkin.",
        "hint_ru": "Read-modify-write может привести к потере одного из двух параллельных обновлений.",
        "explanation": "UPDATE ... SET x = x + 1 — bazaning o'zida atomik bajariladi, poyga holatidan xoli.",
        "difficulty_level": "Hard",
        "points": 10,
    },
    {
        "title": "O'z so'zlaringiz bilan: nega 3 bosqich",
        "title_ru": "Своими словами: почему 3 этапа",
        "description": "Katta jadvalga NOT NULL ustun qo'shishni nega 3 ta alohida migratsiyaga bo'lish kerak, o'z so'zlaringiz bilan tushuntiring.",
        "description_ru": "Объясните своими словами, почему добавление NOT NULL колонки в большую таблицу нужно разбивать на 3 отдельные миграции.",
        "exercise_type": "text_input",
        "expected_answer": (
            "Bitta katta migratsiyada NOT NULL + DEFAULT qo'shish butun jadvalni "
            "uzoq vaqt qulflab qo'yishi mumkin (ayniqsa eski PostgreSQL yoki "
            "murakkab hisoblash kerak bo'lsa); shuning uchun avval nullable ustun "
            "tez qo'shiladi, keyin mavjud qatorlar kichik partiyalarda backfill "
            "qilinadi (uzoq tranzaksiyadan qochish uchun), va faqat barcha "
            "qatorlar to'lgach NOT NULL qo'yiladi — har bir bosqich qisqa va "
            "kam qulflovchi bo'ladi."
        ),
        "hint": "Qulflash muddati va backfill vaqtini bog'lab tushuntiring.",
        "hint_ru": "Свяжите в объяснении время блокировки и время backfill.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 13 — Capstone: yangi funksiya uchun ORM sxema va migratsiya rejasi
# ---------------------------------------------------------------------------

L13_TEXT = """
<h3>Capstone vazifasi: "Kurs sharhlari" (Course Reviews) funksiyasi</h3>
<p>Butun kurs davomida siz LessonFeedback (bitta darsga fikr) tizimini
qurdingiz. Capstone'da undan bir daraja yuqoriga chiqamiz: talaba butun
KURSNI tugatgandan keyin unga umumiy sharh va bahoQ qoldiradigan
<strong>Course Review</strong> tizimini — modeldan production'gacha,
to'liq — loyihalaysiz. Bu vazifa ataylab kattaroq: unda moderatsiya holati
(yangi sharh avval "kutilmoqda", keyin "tasdiqlangan" bo'ladi), bitta
kursga ko'p sharh, bitta sharhga ko'p "foydali ovoz" kabi bir necha
munosabat qatlami bor — bu 0-12-darslarning HAMMASINI talab qiladigan
minimal, lekin real domen.</p>

<h3>1-qadam: talablarni modelga aylantirish (0-3-darslar)</h3>
<p>Har qanday real loyiha talablardan boshlanadi: "talaba faqat
TUGATGAN kursiga sharh yoza oladi" (bu — Enrollment bilan bog'liqlik,
constraint emas, business logic); "bitta talaba bitta kursga faqat bitta
sharh yozadi" (bu — UniqueConstraint, 2-darsdagi kabi); "sharh 1-5 baho
va matn ega" (oddiy ustunlar); "moderatorlar sharhni tasdiqlashi yoki rad
etishi kerak" (status ustuni + enum); "boshqa talabalar sharhni foydali
deb belgilashi mumkin" (bu ALOHIDA jadval — many-to-many, 3-darsdagi
kabi, chunki "kim qaysi sharhni foydali deb belgiladi" ma'lumoti kerak,
shunchaki son emas).</p>

<h3>2-qadam: so'rov naqshlarini oldindan loyihalash (4-6-darslar)</h3>
<p>Model yozishdan oldin "bu ma'lumot qanday o'qiladi" savolini berish
kerak: kurs sahifasida so'nggi tasdiqlangan sharhlar ro'yxati (sahifalash
bilan, 4-dars), har bir sharh muallifi ismi bilan birga (N+1'siz
selectinload, 5-dars), yangi sharh qo'shish va moderatsiya holatini
o'zgartirish (tranzaksiya xavfsizligi, 6-dars). Bu savollarga oldindan
javob berish — keyinchalik "modelni to'g'ri yozdim, lekin so'rov yozish
qiyin" degan holatning oldini oladi.</p>

<h3>3-qadam: migratsiya rejasini bosqichlarga bo'lish (8-10-darslar)</h3>
<p>Yangi funksiya odatda BITTA emas, bir NECHTA migratsiyani talab qiladi:
(1) asosiy <code>course_reviews</code> jadvalini yaratish (yangi jadval —
xavfsiz, mavjud ma'lumotga ta'sir qilmaydi); (2) <code>review_helpful_votes</code>
bog'lovchi jadvalini yaratish; (3) agar keyinchalik <code>helpful_count</code>
kabi hisoblangan ustun qo'shilsa — 9-darsdagi 3 bosqichli naqsh. Har bir
migratsiya <code>downgrade()</code>ga ega bo'lishi va round-trip sinovidan
(8-dars) o'tishi kerak.</p>

<h3>4-qadam: performance xavfsizlik chegaralarini belgilash (11-dars)</h3>
<p>Loyihalash bosqichidayoq performance qoidalarini yozib qo'yish kerak:
kurs sahifasidagi sharhlar ro'yxati <code>load_only()</code> bilan faqat
kerakli ustunlarni oladi (to'liq matn emas, qisqa preview); muallif
ma'lumoti <code>selectinload()</code> bilan eager yuklanadi; moderatsiya
paneli (ko'p sharhni ko'radigan joy) uchun alohida, kattaroq sahifalash
chegarasi qo'yiladi. Bu qoidalar — kodni yozishdan OLDIN qog'ozda
belgilangan bo'lishi kerak, keyin emas.</p>

<h3>Nega bu "capstone" — nima uni maxsus qiladi</h3>
<p>Bu loyiha boshqa darslardan farqli o'laroq bitta tushunchani emas,
BUTUN JARAYONNI sinaydi: talabdan modelgacha, modeldan migratsiyagacha,
migratsiyadan xavfsiz so'rovgacha. Real ish joyida "ORM'ni bilaman"
kamdan-kam alohida talab qilinadi — o'rniga "yangi funksiyani boshidan
oxirigacha, xavfsiz va samarali qura olaman" talab qilinadi. Shu — aynan
ushbu darsning maqsadi.</p>

<h3>Nega Course Review, LessonFeedback emas — domenlarni ataylab farqlash</h3>
<p>R1/R2'da siz LessonFeedback (bitta darsga, oddiy) tizimini qurdingiz.
Capstone'da esa ataylab murakkabroq domen tanlangan: Course Review'da
moderatsiya holati (uch xil qiymat — statik ikki qiymat emas) va IKKINCHI
darajali munosabat (kim qaysi sharhni foydali deb belgiladi) bor. Bu farq
ataylab — capstone shunchaki oldingi loyihani takrorlash emas, balki
undan bir necha qadam murakkabroq real vaziyatga tayyorlaydi.</p>

<h3>Yakuniy baholash mezoni — nima "yaxshi yechim"ni belgilaydi</h3>
<p>Bu loyihada eng muhim narsa — kodning "ishlashi" emas (garchi bu ham
zarur), balki HAR BIR QARORNING asoslanganligi: nega aynan shu
constraint, nega aynan shu yuklash strategiyasi, nega migratsiya aynan
shu tartibda bo'lingan. Yakuniy hisobot — bu texnik bilimni og'zaki
tushuntira olish qobiliyatini sinovdan o'tkazadi, bu esa haqiqiy jamoada
ishlashning ajralmas qismi.</p>
""".strip()

L13_TEXT_RU = """
<h3>Задача Capstone: функция "Отзывы о курсе" (Course Reviews)</h3>
<p>На протяжении всего курса вы строили систему LessonFeedback (отзыв к
одному уроку). В capstone мы поднимаемся на уровень выше: спроектируете
от модели до production полноценную систему <strong>Course Review</strong>,
где студент после завершения ВСЕГО курса оставляет общий отзыв и оценку.
Задача намеренно крупнее: в ней есть статус модерации (новый отзыв сначала
"на рассмотрении", затем "одобрен"), несколько уровней связей — много
отзывов на один курс, много "полезных голосов" на один отзыв — это
минимальный, но реальный домен, требующий ВСЕГО материала уроков 0-12.</p>

<h3>Шаг 1: превращение требований в модель (уроки 0-3)</h3>
<p>Любой реальный проект начинается с требований: "студент может оставить
отзыв только на ЗАВЕРШЁННЫЙ курс" (это связано с Enrollment — бизнес-
логика, а не constraint); "один студент пишет только один отзыв на один
курс" (это UniqueConstraint, как в уроке 2); "отзыв имеет оценку 1-5 и
текст" (обычные колонки); "модераторы должны одобрять или отклонять отзыв"
(колонка статуса + enum); "другие студенты могут отметить отзыв как
полезный" (это ОТДЕЛЬНАЯ таблица — many-to-many, как в уроке 3, поскольку
нужны данные "кто именно отметил какой отзыв полезным", а не просто
число).</p>

<h3>Шаг 2: заранее спроектировать паттерны запросов (уроки 4-6)</h3>
<p>Перед написанием модели нужно задать вопрос "как эти данные будут
читаться": список последних одобренных отзывов на странице курса (с
пагинацией, урок 4), каждый отзыв вместе с именем автора (без N+1, через
selectinload, урок 5), добавление нового отзыва и изменение статуса
модерации (безопасность транзакции, урок 6). Заблаговременный ответ на эти
вопросы предотвращает ситуацию "модель написана правильно, но запрос
писать сложно".</p>

<h3>Шаг 3: разбиение плана миграции на этапы (уроки 8-10)</h3>
<p>Новая функция обычно требует НЕСКОЛЬКИХ миграций, а не ОДНОЙ: (1)
создание основной таблицы <code>course_reviews</code> (новая таблица —
безопасно, не влияет на существующие данные); (2) создание связующей
таблицы <code>review_helpful_votes</code>; (3) если позже добавляется
вычисляемая колонка вроде <code>helpful_count</code> — трёхэтапный
паттерн из урока 9. Каждая миграция должна иметь <code>downgrade()</code>
и проходить проверку round-trip (урок 8).</p>

<h3>Шаг 4: заранее определить границы производительности (урок 11)</h3>
<p>Ещё на этапе проектирования нужно записать правила производительности:
список отзывов на странице курса получает через <code>load_only()</code>
только нужные колонки (не полный текст, а короткий превью); данные автора
загружаются eager через <code>selectinload()</code>; для панели модерации
(где видно много отзывов) задаётся отдельная, большая граница пагинации.
Эти правила должны быть зафиксированы на бумаге ДО написания кода, а не
после.</p>

<h3>Почему это "capstone" — что делает его особенным</h3>
<p>Этот проект, в отличие от других уроков, проверяет не одно понятие, а
ВЕСЬ ПРОЦЕСС: от требования к модели, от модели к миграции, от миграции к
безопасному запросу. На реальной работе "я знаю ORM" редко требуется само
по себе — вместо этого требуется "я могу построить новую функцию от
начала до конца, безопасно и эффективно". Именно это — цель данного
урока.</p>

<h3>Почему Course Review, а не LessonFeedback — намеренное усложнение домена</h3>
<p>В R1/R2 вы строили систему LessonFeedback (простую, для одного урока).
В capstone намеренно выбран более сложный домен: в Course Review есть
статус модерации (три значения, а не статичные два) и связь ВТОРОГО
уровня (кто именно отметил какой отзыв полезным). Эта разница намеренная
— capstone не просто повторяет предыдущий проект, а готовит к реальной
ситуации на несколько шагов сложнее.</p>

<h3>Итоговый критерий оценки — что определяет "хорошее решение"</h3>
<p>Самое важное в этом проекте — не то, что код "работает" (хотя это тоже
необходимо), а то, ОБОСНОВАНО ЛИ КАЖДОЕ РЕШЕНИЕ: почему именно это
ограничение, почему именно эта стратегия загрузки, почему миграция
разбита именно так. Итоговый отчёт проверяет умение объяснить техническое
решение словами — а это неотъемлемая часть работы в настоящей команде.</p>

<h3>Поздравление с завершением трека</h3>
<p>После этого урока пройден весь путь трека SQL: от основ SQL и
PostgreSQL (курс 41), через проектирование базы данных (курс 98) и
продвинутые запросы с производительностью (курс 107), до применения SQL
из кода приложения через ORM и миграции (этот курс). Это полный цикл
знаний, необходимых для работы с данными в реальном production-проекте.</p>
""".strip()

L13_CODE = """
# ============================================================
# 1-qadam: modellar — talablardan kelib chiqqan holda (0-3-darslar)
# ============================================================
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint,
    CheckConstraint, Index, func, select, update,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload, load_only


class ReviewStatus(str, enum.Enum):
    pending = "pending"      # yangi sharh — moderatsiya kutmoqda
    approved = "approved"    # tasdiqlangan — jamoat ko'radi
    rejected = "rejected"    # rad etilgan


class CourseReview(Base):
    __tablename__ = "course_reviews"
    __table_args__ = (
        # "bitta talaba — bitta kurs — bitta sharh" (talab #2)
        UniqueConstraint("student_id", "course_id", name="uq_review_per_student_course"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        Index("ix_review_course_status", "course_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.pending, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship(back_populates="course_reviews")
    course: Mapped["Course"] = relationship(back_populates="reviews")


# Ko'p-ko'p munosabat: "kim qaysi sharhni foydali deb belgiladi" (talab #5)
review_helpful_votes = Table(
    "review_helpful_votes", Base.metadata,
    Column("review_id", ForeignKey("course_reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# 2-qadam: so'rov naqshlari — oldindan loyihalangan (4-6-darslar)
# ============================================================
async def get_approved_reviews(db, course_id: int, page: int = 1, page_size: int = 10):
    stmt = (
        select(CourseReview)
        .where(CourseReview.course_id == course_id, CourseReview.status == ReviewStatus.approved)
        .order_by(CourseReview.created_at.desc())
        .options(
            load_only(CourseReview.id, CourseReview.rating, CourseReview.review_text, CourseReview.created_at),
            selectinload(CourseReview.student).load_only(Student.username, Student.avatar_url),
        )
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    return (await db.execute(stmt)).scalars().all()


async def submit_review(db, student_id: int, course_id: int, rating: int, text: str) -> bool:
    from sqlalchemy.exc import IntegrityError
    db.add(CourseReview(student_id=student_id, course_id=course_id, rating=rating, review_text=text))
    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()   # UniqueConstraint buzilgan — allaqachon sharh bor
        return False


async def moderate_review(db, review_id: int, approve: bool) -> None:
    new_status = ReviewStatus.approved if approve else ReviewStatus.rejected
    await db.execute(update(CourseReview).where(CourseReview.id == review_id).values(status=new_status))
    await db.commit()

# ============================================================
# 3-qadam: migratsiya rejasi (8-10-darslar) — bosqichlar ro'yxati
# ============================================================
# Migratsiya A: course_reviews jadvalini yaratish (yangi jadval — xavfsiz)
# Migratsiya B: review_helpful_votes bog'lovchi jadvalini yaratish
# Migratsiya C (kelajakda, agar kerak bo'lsa): helpful_count ustuni —
#   9-darsdagi 3 bosqichli naqsh (nullable -> backfill -> NOT NULL)
#
# Har biri: alohida revision, downgrade() bilan, round-trip sinovidan
# o'tgan (8-dars).

# ============================================================
# 4-qadam: performance chegaralari (11-dars) — kod yozishdan OLDIN qaror
# ============================================================
MAX_REVIEWS_PAGE_SIZE = 20          # kurs sahifasi uchun
MAX_MODERATION_PAGE_SIZE = 100      # moderatsiya paneli uchun (ko'proq ma'lumot kerak)
# review_text to'liq matn sifatida FAQAT bitta sharh ochilganda yuklanadi,
# ro'yxat ko'rinishida emas (over-fetching'dan qochish, 11-dars).

# ============================================================
# Yakuniy qarorlar xaritasi — qaysi loyihaviy qaror qaysi darsga tegishli
# ============================================================
# UniqueConstraint(student_id, course_id)      -> 2-dars (baza darajasidagi cheklov)
# CheckConstraint(rating BETWEEN 1 AND 5)      -> 2-dars (baza darajasidagi validatsiya)
# review_helpful_votes alohida jadval sifatida -> 3-dars (many-to-many, Integer emas)
# selectinload(CourseReview.student)           -> 5-dars (N+1'dan himoya)
# load_only(...) get_approved_reviews ichida   -> 11-dars (over-fetching'dan himoya)
# submit_review'da try/except IntegrityError   -> 6-dars (tranzaksiya xavfsizligi)
# 2 ta alohida migratsiya (A va B)             -> 8-9-dars (tartib va xavfsizlik)
# async with AsyncSessionLocal() hamma joyda   -> 11-dars (pool tugashining oldini olish)
#
# Bu xarita shunchaki rasmiyat emas — aynan shu darsning topshirig'i talab
# qiladigan yakuniy yozma hisobotning asosini tashkil qiladi.
""".strip()

L13_CODE_RU = """
# ============================================================
# Шаг 1: модели — исходя из требований (уроки 0-3)
# ============================================================
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint,
    CheckConstraint, Index, func, select, update,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload, load_only


class ReviewStatus(str, enum.Enum):
    pending = "pending"      # новый отзыв — ожидает модерации
    approved = "approved"    # одобрен — виден всем
    rejected = "rejected"    # отклонён


class CourseReview(Base):
    __tablename__ = "course_reviews"
    __table_args__ = (
        # "один студент — один курс — один отзыв" (требование №2)
        UniqueConstraint("student_id", "course_id", name="uq_review_per_student_course"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        Index("ix_review_course_status", "course_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    rating: Mapped[int] = mapped_column(Integer)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.pending, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship(back_populates="course_reviews")
    course: Mapped["Course"] = relationship(back_populates="reviews")


# Связь many-to-many: "кто именно отметил какой отзыв полезным" (требование №5)
review_helpful_votes = Table(
    "review_helpful_votes", Base.metadata,
    Column("review_id", ForeignKey("course_reviews.id", ondelete="CASCADE"), primary_key=True),
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
)


# ============================================================
# Шаг 2: паттерны запросов — спроектированы заранее (уроки 4-6)
# ============================================================
async def get_approved_reviews(db, course_id: int, page: int = 1, page_size: int = 10):
    stmt = (
        select(CourseReview)
        .where(CourseReview.course_id == course_id, CourseReview.status == ReviewStatus.approved)
        .order_by(CourseReview.created_at.desc())
        .options(
            load_only(CourseReview.id, CourseReview.rating, CourseReview.review_text, CourseReview.created_at),
            selectinload(CourseReview.student).load_only(Student.username, Student.avatar_url),
        )
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    return (await db.execute(stmt)).scalars().all()


async def submit_review(db, student_id: int, course_id: int, rating: int, text: str) -> bool:
    from sqlalchemy.exc import IntegrityError
    db.add(CourseReview(student_id=student_id, course_id=course_id, rating=rating, review_text=text))
    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()   # нарушен UniqueConstraint — отзыв уже есть
        return False


async def moderate_review(db, review_id: int, approve: bool) -> None:
    new_status = ReviewStatus.approved if approve else ReviewStatus.rejected
    await db.execute(update(CourseReview).where(CourseReview.id == review_id).values(status=new_status))
    await db.commit()

# ============================================================
# Шаг 3: план миграции (уроки 8-10) — список этапов
# ============================================================
# Миграция A: создание таблицы course_reviews (новая таблица — безопасно)
# Миграция B: создание связующей таблицы review_helpful_votes
# Миграция C (в будущем, если понадобится): колонка helpful_count —
#   трёхэтапный паттерн из урока 9 (nullable -> backfill -> NOT NULL)
#
# Каждая: отдельный revision, с downgrade(), прошедший проверку round-trip
# (урок 8).

# ============================================================
# Шаг 4: границы производительности (урок 11) — решение ДО написания кода
# ============================================================
MAX_REVIEWS_PAGE_SIZE = 20          # для страницы курса
MAX_MODERATION_PAGE_SIZE = 100      # для панели модерации (нужно больше данных)
# review_text как полный текст загружается ТОЛЬКО при открытии одного
# отзыва, не в виде списка (избегание over-fetching, урок 11).

# ============================================================
# Итоговая карта решений — какое проектное решение к какому уроку относится
# ============================================================
# UniqueConstraint(student_id, course_id)      -> урок 2 (ограничения на уровне базы)
# CheckConstraint(rating BETWEEN 1 AND 5)      -> урок 2 (валидация на уровне базы)
# review_helpful_votes как отдельная таблица   -> урок 3 (many-to-many, а не Integer)
# selectinload(CourseReview.student)           -> урок 5 (защита от N+1)
# load_only(...) в get_approved_reviews        -> урок 11 (защита от over-fetching)
# try/except IntegrityError в submit_review    -> урок 6 (безопасность транзакции)
# 2 отдельные миграции (A и B)                 -> урок 8-9 (порядок и безопасность)
# async with AsyncSessionLocal() everywhere     -> урок 11 (предотвращение исчерпания пула)
#
# Такая карта — не формальность: именно она составит основу итогового
# письменного отчёта, который требует задание этого урока.
""".strip()

L13_TASK = {
    "task_title": "Capstone: Course Review tizimini boshidan oxirigacha loyihalash",
    "task_title_ru": "Capstone: спроектировать систему Course Review от начала до конца",
    "task_description": (
        "To'liq Course Review funksiyasini loyihalang va yozing: (1) "
        "CourseReview modeli + review_helpful_votes bog'lovchi jadvali, "
        "barcha talab qilingan constraint'lar bilan; (2) ikkita alohida "
        "Alembic migratsiyasi (jadvallar uchun), har biri downgrade() "
        "bilan; (3) uchta funksiya: get_approved_reviews (over-fetching'siz, "
        "sahifalash bilan), submit_review (tranzaksiya xavfsizligi bilan), "
        "moderate_review; (4) qisqa yozma hisobot: har bir loyihaviy qaror "
        "qaysi darsning tushunchasiga asoslanganini ko'rsating."
    ),
    "task_description_ru": (
        "Спроектируйте и напишите полную функцию Course Review: (1) модель "
        "CourseReview + связующая таблица review_helpful_votes, со всеми "
        "требуемыми ограничениями; (2) две отдельные миграции Alembic (для "
        "таблиц), каждая с downgrade(); (3) три функции: "
        "get_approved_reviews (без over-fetching, с пагинацией), "
        "submit_review (с безопасностью транзакции), moderate_review; (4) "
        "короткий письменный отчёт: укажите, на понятии какого урока "
        "основано каждое проектное решение."
    ),
    "task_requirements": (
        "1) To'liq model kodi (UniqueConstraint, CheckConstraint, Index). "
        "2) 2 ta Alembic migratsiya fayli, downgrade() bilan. 3) 3 ta "
        "funksiya: get_approved_reviews, submit_review, moderate_review. "
        "4) Yozma hisobot — kamida 6 ta loyihaviy qarorni tegishli darsga "
        "bog'lab tushuntiring (masalan: 'UniqueConstraint — 2-dars', "
        "'selectinload — 5-dars')."
    ),
    "task_requirements_ru": (
        "1) Полный код модели (UniqueConstraint, CheckConstraint, Index). "
        "2) 2 файла миграции Alembic, с downgrade(). 3) 3 функции: "
        "get_approved_reviews, submit_review, moderate_review. 4) "
        "Письменный отчёт — объясните минимум 6 проектных решений, "
        "привязав их к соответствующему уроку (например: "
        "'UniqueConstraint — урок 2', 'selectinload — урок 5')."
    ),
    "task_technologies": "Python, SQLAlchemy 2.x ORM (async), Alembic, PostgreSQL",
    "task_deadline_days": 10,
}

L13_SAMPLE = {
    "title": "Namuna: to'liq Course Review tizimi (model + migratsiya + so'rovlar)",
    "description": "0-12-darslarning barcha tushunchalarini birlashtiruvchi, ishga tayyor to'liq loyihaviy misol.",
    "sample_type": "code",
    "code_files": [
        {
            "filename": "models_course_review.py",
            "language": "python",
            "code": (
                "import enum\n"
                "from datetime import datetime\n"
                "from typing import Optional\n"
                "from sqlalchemy import (\n"
                "    String, Text, Integer, DateTime, ForeignKey, Table, Column,\n"
                "    UniqueConstraint, CheckConstraint, Index, func,\n"
                ")\n"
                "from sqlalchemy.orm import Mapped, mapped_column, relationship\n\n\n"
                "class ReviewStatus(str, enum.Enum):\n"
                "    pending = \"pending\"\n"
                "    approved = \"approved\"\n"
                "    rejected = \"rejected\"\n\n\n"
                "class CourseReview(Base):\n"
                "    __tablename__ = \"course_reviews\"\n"
                "    __table_args__ = (\n"
                "        UniqueConstraint(\"student_id\", \"course_id\", name=\"uq_review_per_student_course\"),\n"
                "        CheckConstraint(\"rating BETWEEN 1 AND 5\", name=\"ck_review_rating_range\"),\n"
                "        Index(\"ix_review_course_status\", \"course_id\", \"status\"),\n"
                "    )\n\n"
                "    id: Mapped[int] = mapped_column(primary_key=True)\n"
                "    student_id: Mapped[int] = mapped_column(ForeignKey(\"students.id\", ondelete=\"CASCADE\"))\n"
                "    course_id: Mapped[int] = mapped_column(ForeignKey(\"courses.id\", ondelete=\"CASCADE\"))\n"
                "    rating: Mapped[int] = mapped_column(Integer)\n"
                "    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)\n"
                "    status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.pending, server_default=\"pending\")\n"
                "    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())\n\n"
                "    student: Mapped[\"Student\"] = relationship(back_populates=\"course_reviews\")\n"
                "    course: Mapped[\"Course\"] = relationship(back_populates=\"reviews\")\n\n\n"
                "review_helpful_votes = Table(\n"
                "    \"review_helpful_votes\", Base.metadata,\n"
                "    Column(\"review_id\", ForeignKey(\"course_reviews.id\", ondelete=\"CASCADE\"), primary_key=True),\n"
                "    Column(\"student_id\", ForeignKey(\"students.id\", ondelete=\"CASCADE\"), primary_key=True),\n"
                ")\n"
            ),
        },
        {
            "filename": "migration_a_create_course_reviews.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'ff55aa66bb77'\n"
                "down_revision = 'ee44ff55aa66'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.create_table(\n"
                "        'course_reviews',\n"
                "        sa.Column('id', sa.Integer(), primary_key=True),\n"
                "        sa.Column('student_id', sa.Integer(),\n"
                "                  sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),\n"
                "        sa.Column('course_id', sa.Integer(),\n"
                "                  sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),\n"
                "        sa.Column('rating', sa.Integer(), nullable=False),\n"
                "        sa.Column('review_text', sa.Text(), nullable=True),\n"
                "        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),\n"
                "        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),\n"
                "        sa.UniqueConstraint('student_id', 'course_id', name='uq_review_per_student_course'),\n"
                "        sa.CheckConstraint('rating BETWEEN 1 AND 5', name='ck_review_rating_range'),\n"
                "    )\n"
                "    op.create_index('ix_review_course_status', 'course_reviews', ['course_id', 'status'])\n\n\n"
                "def downgrade() -> None:\n"
                "    op.drop_table('course_reviews')\n"
            ),
        },
        {
            "filename": "migration_b_create_helpful_votes.py",
            "language": "python",
            "code": (
                "from alembic import op\n"
                "import sqlalchemy as sa\n\n"
                "revision = 'aa66bb77cc88'\n"
                "down_revision = 'ff55aa66bb77'\n\n\n"
                "def upgrade() -> None:\n"
                "    op.create_table(\n"
                "        'review_helpful_votes',\n"
                "        sa.Column('review_id', sa.Integer(),\n"
                "                  sa.ForeignKey('course_reviews.id', ondelete='CASCADE'), primary_key=True),\n"
                "        sa.Column('student_id', sa.Integer(),\n"
                "                  sa.ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),\n"
                "    )\n\n\n"
                "def downgrade() -> None:\n"
                "    op.drop_table('review_helpful_votes')\n"
            ),
        },
    ],
}

L13_EXERCISES = [
    {
        "title": "Bog'lovchi jadval qachon kerak",
        "title_ru": "Когда нужна связующая таблица",
        "description": "review_helpful_votes uchun nega oddiy helpful_count Integer ustuni EMAS, alohida jadval ishlatildi?",
        "description_ru": "Почему для review_helpful_votes использована отдельная таблица, а НЕ простая колонка helpful_count Integer?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki 'kim ovoz bergani' ma'lumoti ham kerak, shunchaki son emas",
            "Chunki Integer ustuni PostgreSQL'da ishlamaydi",
            "Chunki many-to-many har doim tezroq ishlaydi",
            "Chunki bu ORM talabi, biznes talab emas",
        ],
        "options_ru": [
            "Потому что нужны данные 'кто именно проголосовал', а не просто число",
            "Потому что колонка Integer не работает в PostgreSQL",
            "Потому что many-to-many всегда работает быстрее",
            "Потому что это требование ORM, а не бизнес-требование",
        ],
        "correct_answers": "A",
        "hint": "Agar faqat son kerak bo'lsa, Integer yetarli edi; lekin 'bir talaba ikki marta ovoz bermasin' talabi bor.",
        "hint_ru": "Если нужно было бы только число, хватило бы Integer; но есть требование 'один студент не может проголосовать дважды'.",
        "explanation": "Kim aynan ovoz berganini bilish va takroriy ovozning oldini olish uchun alohida jadval (bog'lovchi) kerak.",
        "difficulty_level": "Hard",
        "points": 10,
    },
    {
        "title": "Loyihalash qadamlarini tartiblang",
        "title_ru": "Расположите шаги проектирования по порядку",
        "description": "Yangi funksiyani loyihalashning to'g'ri qadamlarini (capstone darsida ko'rilgan) tartibga joylashtiring.",
        "description_ru": "Расположите правильные шаги проектирования новой функции (рассмотренные в capstone).",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Talablarni modelga aylantirish",
            "So'rov naqshlarini oldindan loyihalash",
            "Migratsiya rejasini bosqichlarga bo'lish",
            "Performance chegaralarini belgilash",
        ],
        "drag_items_ru": [
            "Превратить требования в модель",
            "Заранее спроектировать паттерны запросов",
            "Разбить план миграции на этапы",
            "Определить границы производительности",
        ],
        "correct_order": [
            "Talablarni modelga aylantirish",
            "So'rov naqshlarini oldindan loyihalash",
            "Migratsiya rejasini bosqichlarga bo'lish",
            "Performance chegaralarini belgilash",
        ],
        "hint": "Avval NIMA saqlanishi, keyin QANDAY o'qilishi, keyin QANDAY yetkazilishi, oxirida QANCHA samarali bo'lishi.",
        "hint_ru": "Сначала ЧТО хранится, потом КАК читается, потом КАК доставляется, в конце НАСКОЛЬКО эффективно.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Capstone yakuniy mulohaza",
        "title_ru": "Capstone: итоговое размышление",
        "description": "Butun kurs davomida o'rgangan eng muhim BITTA saboqni tanlang va uni haqiqiy loyihada qanday qo'llashingizni tushuntiring.",
        "description_ru": "Выберите ОДИН самый важный урок, изученный за весь курс, и объясните, как вы примените его в реальном проекте.",
        "exercise_type": "text_input",
        "expected_answer": (
            "Har qanday izchil, asosli javob qabul qilinadi — masalan N+1'ni "
            "selectinload() bilan oldini olish, yoki migratsiyani har doim "
            "kichik, qaytarib bo'ladigan bosqichlarga bo'lish, yoki "
            "autogenerate natijasini har doim qo'lda tekshirish. Muhimi — "
            "tanlangan saboqning nega muhimligini va uni qanday amalda "
            "qo'llashni aniq tushuntirish."
        ),
        "hint": "Kursning 0-12-darslaridan birini tanlang va uni real loyihaga bog'lang.",
        "hint_ru": "Выберите один из уроков 0-12 курса и свяжите его с реальным проектом.",
        "difficulty_level": "Medium",
        "points": 10,
    },
]

LESSONS = [
    {
        "order": 0,
        "title": "ORM nima va impedance mismatch muammosi",
        "title_ru": "Что такое ORM и проблема impedance mismatch",
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
        "title": "SQLAlchemy: Core va ORM — ikki qatlam",
        "title_ru": "SQLAlchemy: Core и ORM — два слоя",
        "points_reward": 15,
        "text_content": L1_TEXT,
        "text_content_ru": L1_TEXT_RU,
        "code_content": L1_CODE,
        "code_content_ru": L1_CODE_RU,
        "code_language": "python",
        "task": L1_TASK,
        "sample": L1_SAMPLE,
        "exercises": L1_EXERCISES,
    },
    {
        "order": 2,
        "title": "Modellar va Mapping: jadvallardan Python klasslarga",
        "title_ru": "Модели и Mapping: от таблиц к классам Python",
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
        "title": "Munosabatlar: one-to-many va many-to-many",
        "title_ru": "Связи: one-to-many и many-to-many",
        "points_reward": 15,
        "text_content": L3_TEXT,
        "text_content_ru": L3_TEXT_RU,
        "code_content": L3_CODE,
        "code_content_ru": L3_CODE_RU,
        "code_language": "python",
        "task": L3_TASK,
        "sample": L3_SAMPLE,
        "exercises": L3_EXERCISES,
    },
    {
        "order": 4,
        "title": "ORM orqali so'rovlar: filter, join, select()",
        "title_ru": "Запросы через ORM: filter, join, select()",
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
        "title": "Eager vs Lazy Loading: N+1 muammosi qaytadan",
        "title_ru": "Eager и Lazy Loading: снова о проблеме N+1",
        "points_reward": 15,
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
        "title": "Tranzaksiyalar va Sessiyalar: Unit of Work",
        "title_ru": "Транзакции и Session: Unit of Work",
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
        "title": "R1 — Takrorlash: ORM asoslari bo'yicha amaliyot",
        "title_ru": "R1 — Повторение: практика по основам ORM",
        "points_reward": 20,
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
        "title": "Migratsiyalarga kirish: Alembic nima va nega kerak",
        "title_ru": "Введение в миграции: что такое Alembic и зачем он нужен",
        "points_reward": 15,
        "text_content": L8_TEXT,
        "text_content_ru": L8_TEXT_RU,
        "code_content": L8_CODE,
        "code_content_ru": L8_CODE_RU,
        "code_language": "python",
        "task": L8_TASK,
        "sample": L8_SAMPLE,
        "exercises": L8_EXERCISES,
    },
    {
        "order": 9,
        "title": "Xavfsiz migratsiyalar: default, backfill, zero-downtime",
        "title_ru": "Безопасные миграции: default, backfill, zero-downtime",
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
        "title": "Migratsiya xatoliklari: qulflash, qaytarib bo'lmaydigan o'zgarishlar",
        "title_ru": "Ошибки миграций: блокировки, необратимые изменения",
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
        "title": "ORM performance muammolari: over-fetching va connection pool",
        "title_ru": "Проблемы производительности ORM: over-fetching и connection pool",
        "points_reward": 15,
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
        "title": "R2 — Takrorlash: migratsiya va performance bo'yicha amaliyot",
        "title_ru": "R2 — Повторение: практика по миграциям и производительности",
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
        "title": "Capstone: yangi funksiya uchun ORM sxema va migratsiya rejasi",
        "title_ru": "Capstone: ORM-схема и план миграции для новой функции",
        "points_reward": 25,
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
