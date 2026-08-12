"""RAG va Vektor Qidiruv — second course in the "AI Integration" category
(category_id=13), prerequisite_course_id=135 ("AI API'larni Loyihalarga
Ulash"). Course 135 already taught how to call an LLM API reliably
(request/response shape, free-tier keys, prompt engineering, JSON parsing,
the multi-provider call_chain fallback, error handling, streaming, function
calling, rate limits/retry, token budgets, security, the real FastAPI
ai_review.py endpoint). This course does NOT repeat any of that — its job
is retrieval: how an AI feature answers questions about a student's OWN
data instead of only what the model memorized during training.

Every concrete example is grounded either in this platform's own real
schema/code or in this platform's own real data:
  - app/models/lesson.py's Lesson.text_content column — 516 published
    lessons, real bilingual (UZ+RU) HTML lesson text, used as the actual
    corpus for the chunking and semantic-search worked examples (L2, L6).
  - app/services/grok_ai_client.py's call_chain() — reused, not
    reimplemented, as the "generate" step of the RAG pipeline (L8, L13).
  - app/config.py's real AI_PROVIDER_CHAIN / GEMINI_API_KEY settings.
  - A read-only check confirmed via SQLAlchemy that this database does NOT
    currently have the pgvector extension enabled (`SELECT * FROM
    pg_extension WHERE extname = 'vector'` returned zero rows). L5 teaches
    `CREATE EXTENSION IF NOT EXISTS vector;` and the accompanying column/
    index SQL as something a student runs in THEIR OWN project database —
    this course does not enable it here, deliberately, per the instruction
    to default to teaching schema DDL rather than executing it live against
    a shared production database.

No fabricated numbers: Pinecone/Gemini-embedding pricing, rate limits, and
free-tier quotas are described qualitatively ("has a free tier", "check
current limits in the provider's dashboard") rather than with specific
numbers that could go stale or be wrong, same convention course 135 used
for its free-tier-keys lesson.

Built with the course_builder scaffold — see course_builder/__init__.py for
the spec contract. Every lesson gets both task + sample from the start,
full UZ+RU authored here (not machine-translated), Mermaid diagrams where
pedagogically justified (11 of 14 lessons — skipped on L4, a pure
options-comparison lesson with nothing to flow-chart, and on the two review
lessons L7/L12, which are recap/task lessons with no new flow to diagram).
is_published stays False — human review first.
"""

COURSE = {
    "title": "RAG va Vektor Qidiruv: Hujjatlar Asosida AI",
    "title_ru": "RAG и векторный поиск: AI на основе документов",
    "description": (
        "135-kursda siz LLM API'siga qanday so'rov yuborish, javobni qanday "
        "o'qish va provider ishlamay qolganda qanday fallback qilishni "
        "o'rgangan edingiz. Lekin bitta muammo qoladi: LLM faqat o'zining "
        "o'qitilgan (training) ma'lumotlarini biladi — agar siz undan "
        "ushbu platformaning o'z kurs katalogi yoki o'zingizning shaxsiy "
        "hujjatlaringiz haqida so'rasangiz, u hech narsa bilmaydi yoki "
        "o'ylab topadi (gallyutsinatsiya qiladi). Bu kurs aynan shu "
        "muammoni hal qiladi — RAG (Retrieval-Augmented Generation): "
        "hujjatlaringizni vektorlarga aylantirish (embedding), ularni "
        "qidiriladigan shaklda saqlash (pgvector, Chroma), so'rovga eng "
        "mos qismlarni topish (cosine similarity) va ularni LLM promptiga "
        "qo'shib, haqiqiy ma'lumotga asoslangan javob olish. Kurs davomida "
        "o'ylab topilgan generik hujjatlar emas, balki ushbu platformaning "
        "o'zida saqlanayotgan 500dan ortiq haqiqiy, published dars matni "
        "(lessons.text_content) haqiqiy qidiruv korpusi sifatida "
        "ishlatiladi, va yakuniy RAG pipeline 135-kursning haqiqiy "
        "call_chain() fallback zanjirini qayta ishlatadi — uni qaytadan "
        "yozish emas. Kurs 135-kursni prerequisite sifatida talab qiladi — "
        "LLM API chaqirig'ini ishonchli bajarish ko'nikmasi allaqachon "
        "borligini taxmin qiladi."
    ),
    "description_ru": (
        "В курсе 135 вы научились отправлять запросы к LLM API, читать "
        "ответ и переключаться на другого провайдера при сбое. Но остаётся "
        "одна проблема: LLM знает только то, на чём обучалась — если "
        "спросить её о собственном каталоге курсов этой платформы или о "
        "ваших личных документах, она либо не знает, либо выдумывает "
        "(галлюцинирует). Этот курс решает именно эту проблему — RAG "
        "(Retrieval-Augmented Generation, генерация с дополненным "
        "поиском): превращение документов в векторы (эмбеддинги), их "
        "хранение в доступной для поиска форме (pgvector, Chroma), поиск "
        "наиболее релевантных частей по запросу (косинусное сходство) и "
        "добавление их в промпт LLM для получения ответа, основанного на "
        "реальных данных. На протяжении курса используются не выдуманные "
        "общие документы, а более 500 реальных, опубликованных текстов "
        "уроков этой платформы (lessons.text_content) в качестве "
        "настоящего корпуса для поиска, а финальный RAG pipeline повторно "
        "использует реальную цепочку отказоустойчивости call_chain() из "
        "курса 135 — а не переписывает её заново. Курс требует курс 135 "
        "как обязательный предварительный — предполагается, что навык "
        "надёжного вызова LLM API уже есть."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 4,
    "max_points": 0,  # computed at the bottom of this file from LESSONS
    "category_id": 13,
    "prerequisite_course_id": 135,
    "display_order": 801,
    "image_url": "https://raw.githubusercontent.com/gilbarbara/logos/main/logos/postgresql.svg",
    "thumbnail_url": "https://raw.githubusercontent.com/primer/octicons/main/icons/search-24.svg",
    "is_active": True,
    "is_published": False,
}

# ---------------------------------------------------------------------------
# Lesson 0 — RAG nima va nega LLM'ning o'z bilimi yetarli emas
# ---------------------------------------------------------------------------

L0_TEXT = """
<h3>Muammo: LLM sizning ma'lumotlaringizni bilmaydi</h3>
<p>135-kursda siz LLM API'siga so'rov yuborishni o'rgandingiz. Lekin bir narsani
sinab ko'ring: shu platformaning haqiqiy AI provider'iga (masalan Gemini yoki
Groq) to'g'ridan-to'g'ri <code>"Bu platformada nechta kurs bor va ular qaysi
kategoriyalarga bo'lingan?"</code> deb so'rang. Model sizga ishonchli ohangda
javob beradi — lekin bu javob <strong>o'ylab topilgan</strong> bo'ladi, chunki
model hech qachon ushbu platformaning courses jadvalini ko'rmagan. Bu hodisa
<strong>gallyutsinatsiya</strong> deb ataladi: model "bilmayman" deyish
o'rniga ishonchli tarzda noto'g'ri javob generatsiya qiladi.</p>

<p>Sabab oddiy: LLM faqat <strong>training paytida</strong> ko'rgan matnni
"biladi". Bu bilim muzlatilgan (frozen) — model chiqarilgandan keyin qo'shilgan
hech qanday ma'lumot (yangi kurslar, sizning shaxsiy fayllaringiz, bugungi
yangiliklar) modelning "xotirasida" yo'q. Buni context window orqali "hozir"
yuborish mumkin — lekin qanday qilib to'g'ri hujjatni topib, aynan shuni
promptga qo'shamiz? Butun platformaning barcha darslarini (500dan ortiq,
minglab belgidan iborat) har bir so'rovga qo'shib yuborish mumkin emas —
narx, tezlik va context window chegarasi buni taqiqlaydi.</p>

<h3>Yechim: RAG (Retrieval-Augmented Generation)</h3>
<p>RAG — uchta bosqichdan iborat oddiy g'oya:</p>
<ol>
<li><strong>Retrieve (qidirish)</strong> — foydalanuvchi savoliga eng mos
keladigan hujjat qismlarini (chunk) sizning o'z ma'lumotlar bazangizdan
topasiz — butun bazani emas, faqat eng mos 3-5 ta bo'lakni.</li>
<li><strong>Augment (boyitish)</strong> — topilgan bo'laklarni LLM promptiga
"bu yerda foydalanuvchi savoliga tegishli ma'lumot bor" deb qo'shasiz.</li>
<li><strong>Generate (generatsiya)</strong> — LLM endi o'zining umumiy
bilimiga emas, balki siz bergan HAQIQIY ma'lumotga asoslanib javob beradi.</li>
</ol>
<p>Muhim farq: RAG modelni qayta o'qitmaydi (fine-tuning emas) — u shunchaki
har bir so'rov paytida kerakli ma'lumotni "eslatib qo'yadi". Shuning uchun
yangi hujjat qo'shish uchun modelni qayta o'qitish shart emas — shunchaki
yangi hujjatni ham qidiriladigan bazaga qo'shasiz.</p>

<h3>Nega "shunchaki matn qidirish" (Ctrl+F) yetarli emas</h3>
<p>Klassik matn qidirish (SQL <code>LIKE '%so'z%'</code> yoki full-text search)
faqat ANIQ so'zlarni topadi. Agar foydalanuvchi <code>"backend qanday
sozlanadi"</code> deb so'rasa-yu, dars matnida <code>"server konfiguratsiyasi"</code>
deb yozilgan bo'lsa, klassik qidiruv hech narsa topmaydi — so'zlar boshqacha,
lekin MA'NOSI bir xil. RAG'ning markazidagi g'oya — <strong>semantik
qidiruv</strong>: so'zlarni emas, MA'NOni solishtirish. Buning uchun matnni
raqamlar ro'yxatiga (vektorga) aylantiramiz — bu keyingi darsning mavzusi
(embedding'lar).</p>

<h3>Bu kursning haqiqiy misoli</h3>
<p>Bu kurs davomida siz o'ylab topilgan "hujjatlar to'plami" bilan emas, balki
ushbu platformaning o'zida saqlanayotgan haqiqiy ma'lumot bilan ishlaysiz:
<code>lessons</code> jadvalidagi <code>text_content</code> ustuni — 500dan
ortiq published, haqiqiy dars matni (HTML). Yakuniy loyihada siz "Bu
platformada Python haqida qanday darslar bor?" kabi savolga, aynan shu real
matn ustidan qidirilgan va topilgan bo'laklar asosida javob beradigan mini
chatbot quramiz.</p>

<h3>RAG'siz va RAG bilan: ikki yo'lni solishtirish</h3>
<pre class="mermaid">
flowchart TB
  Q["Foydalanuvchi savoli:
'Platformada nechta AI kursi bor?'"]
  Q -->|"to'g'ridan-to'g'ri"| LLM1["LLM (faqat training bilimi)"]
  LLM1 -->|"ma'lumot yo'q, lekin javob berishi kerak"| HALLU["Gallyutsinatsiya:
ishonchli, lekin noto'g'ri javob"]

  Q -->|"RAG orqali"| RET["1. Retrieve:
courses jadvalidan mos yozuvlarni topish"]
  RET -->|"topilgan haqiqiy qatorlar"| AUG["2. Augment:
promptga haqiqiy ma'lumotni qo'shish"]
  AUG --> GEN["3. Generate:
LLM haqiqiy ma'lumot asosida javob beradi"]
  GEN --> GOOD["To'g'ri, tekshirilishi mumkin javob"]
</pre>
<p>Diagramma shuni ko'rsatadi: bir xil savol, bir xil model — lekin RAG
qatnashganda LLM "taxmin qilish" o'rniga haqiqiy ma'lumotdan foydalanadi.
Farq modelning o'zida emas, unga NIMA berilishida.</p>

<h3>RAG va bu kursning tuzilishi</h3>
<p>Quyidagi darslar RAG pipeline'ning har bir bosqichini alohida chuqur
o'rganadi: embedding'lar (matnni vektorga aylantirish), chunking (hujjatni
qidiriladigan bo'laklarga bo'lish), vektor o'xshashligi matematikasi,
vektor bazalari (pgvector/Chroma/Pinecone), so'ngra hammasini bitta ishlaydigan
pipeline'ga birlashtiramiz — va buning uchun 135-kursdagi <code>call_chain()</code>
fallback zanjirini qaytadan yozmasdan, aynan o'sha kodni qayta ishlatamiz.</p>
"""

L0_TEXT_RU = """
<h3>Проблема: LLM не знает ваши данные</h3>
<p>В курсе 135 вы научились отправлять запросы к LLM API. Но попробуйте вот
что: спросите реального AI-провайдера этой платформы (например, Gemini или
Groq) напрямую: <code>"Сколько курсов на этой платформе и по каким
категориям они распределены?"</code>. Модель ответит уверенным тоном — но
этот ответ будет <strong>выдуманным</strong>, потому что модель никогда не
видела таблицу courses этой платформы. Это явление называется
<strong>галлюцинацией</strong>: вместо "я не знаю" модель уверенно
генерирует неверный ответ.</p>

<p>Причина проста: LLM "знает" только то, что видела <strong>во время
обучения</strong>. Эти знания заморожены — любая информация, добавленная
после выпуска модели (новые курсы, ваши личные файлы, сегодняшние новости),
отсутствует в "памяти" модели. Это можно передать "сейчас" через context
window — но как найти правильный документ и добавить именно его в промпт?
Отправлять все документы платформы (500+, тысячи символов) при каждом
запросе невозможно — цена, скорость и лимит context window это запрещают.</p>

<h3>Решение: RAG (Retrieval-Augmented Generation)</h3>
<p>RAG — простая идея из трёх этапов:</p>
<ol>
<li><strong>Retrieve (поиск)</strong> — находите части документов (chunk),
наиболее релевантные вопросу пользователя, из вашей собственной базы данных
— не всю базу, а только 3-5 наиболее подходящих фрагментов.</li>
<li><strong>Augment (дополнение)</strong> — добавляете найденные фрагменты
в промпт LLM: "вот информация, относящаяся к вопросу пользователя".</li>
<li><strong>Generate (генерация)</strong> — LLM теперь отвечает не на
основе своих общих знаний, а на основе РЕАЛЬНЫХ данных, которые вы
предоставили.</li>
</ol>
<p>Важное отличие: RAG не переобучает модель (это не fine-tuning) — она
просто "напоминает" нужную информацию при каждом запросе. Поэтому для
добавления нового документа не нужно переобучать модель — достаточно
добавить новый документ в базу для поиска.</p>

<h3>Почему "простого поиска текста" (Ctrl+F) недостаточно</h3>
<p>Классический поиск текста (SQL <code>LIKE '%слово%'</code> или
полнотекстовый поиск) находит только ТОЧНЫЕ слова. Если пользователь
спрашивает <code>"как настроить backend"</code>, а в тексте урока написано
<code>"конфигурация сервера"</code>, классический поиск ничего не найдёт —
слова разные, но СМЫСЛ одинаковый. Центральная идея RAG —
<strong>семантический поиск</strong>: сравнение не слов, а СМЫСЛА. Для
этого мы превращаем текст в список чисел (вектор) — это тема следующего
урока (эмбеддинги).</p>

<h3>Реальный пример этого курса</h3>
<p>На протяжении этого курса вы работаете не с выдуманным "набором
документов", а с реальными данными, хранящимися на самой платформе:
столбец <code>text_content</code> таблицы <code>lessons</code> — более 500
опубликованных, реальных текстов уроков (HTML). В финальном проекте вы
построите мини-чат-бота, который отвечает на вопрос вроде "Какие уроки есть
про Python на этой платформе?" на основе реально найденных фрагментов
этого текста.</p>

<h3>Без RAG и с RAG: сравнение двух путей</h3>
<pre class="mermaid">
flowchart TB
  Q["Вопрос пользователя:
'Сколько AI-курсов на платформе?'"]
  Q -->|"напрямую"| LLM1["LLM (только знания из обучения)"]
  LLM1 -->|"данных нет, но ответить нужно"| HALLU["Галлюцинация:
уверенный, но неверный ответ"]

  Q -->|"через RAG"| RET["1. Retrieve:
поиск подходящих записей в таблице courses"]
  RET -->|"найденные реальные строки"| AUG["2. Augment:
добавление реальных данных в промпт"]
  AUG --> GEN["3. Generate:
LLM отвечает на основе реальных данных"]
  GEN --> GOOD["Верный, проверяемый ответ"]
</pre>
<p>Диаграмма показывает: один и тот же вопрос, одна и та же модель — но при
использовании RAG LLM использует реальные данные вместо "угадывания".
Разница не в самой модели, а в том, ЧТО ей передают.</p>

<h3>RAG и структура этого курса</h3>
<p>Следующие уроки подробно разбирают каждый этап RAG pipeline: эмбеддинги
(превращение текста в вектор), chunking (разбиение документа на фрагменты
для поиска), математику векторного сходства, векторные базы (pgvector/
Chroma/Pinecone), а затем мы объединяем всё в один рабочий pipeline — и для
этого мы не переписываем заново цепочку отказоустойчивости
<code>call_chain()</code> из курса 135, а повторно используем именно этот
код.</p>
"""

L0_CODE = """
# Namuna: "RAG'siz" LLM chaqiruvi platforma ma'lumotlari haqida
# nima uchun ishonchsiz javob berishini ko'rsatadi (135-kursdagi
# _ask_ai() ORQALI — biz uni qaytadan yozmaymiz, faqat import qilamiz).

import asyncio
from app.services.grok_ai_client import _ask_ai


async def ask_without_rag(question: str) -> str | None:
    \"\"\"RAG'siz to'g'ridan-to'g'ri savol — modelning javobi platformaning
    HAQIQIY ma'lumotlariga emas, o'zining umumiy "bilimi"ga asoslanadi.\"\"\"
    prompt = (
        f"Savol: {question}\\n\\n"
        "Iltimos aniq va qisqa javob ber."
    )
    return await _ask_ai(prompt)


async def main() -> None:
    question = "Ushbu talaba platformasida nechta kurs bor va ular qaysi kategoriyalarga bo'lingan?"
    answer = await ask_without_rag(question)
    print("Savol:", question)
    print("Model javobi (RAG'siz):", answer)
    print(
        "\\nDIQQAT: bu javob ishonchli ko'rinishi mumkin, lekin model "
        "hech qachon ushbu platformaning courses jadvalini ko'rmagan — "
        "u statistik ehtimollik asosida matn generatsiya qilmoqda, "
        "haqiqiy ma'lumotni qaytarmoqda emas. Bu — gallyutsinatsiya."
    )


if __name__ == "__main__":
    asyncio.run(main())


# ---------------------------------------------------------------------------
# Taqqoslash uchun: RAG variantda promptga HAQIQIY ma'lumot qo'shiladi.
# (Keyingi darslarda buni to'liq quramiz — bu yerda faqat farqni ko'ramiz.)
# ---------------------------------------------------------------------------

async def ask_with_manual_context(question: str, real_facts: str) -> str | None:
    \"\"\"RAG'ning eng oddiy shakli: hali qidiruv yo'q, lekin haqiqiy
    faktlarni promptga qo'lda qo'shib qo'yish orqali javob sifati keskin
    o'zgarishini ko'rish mumkin.\"\"\"
    prompt = (
        "Quyidagi HAQIQIY ma'lumotdan foydalanib savolga javob ber. "
        "Agar ma'lumotda javob bo'lmasa, 'ma'lumotda bu haqida yo'q' deb ayt "
        "— o'ylab topma.\\n\\n"
        f"MA'LUMOT:\\n{real_facts}\\n\\n"
        f"SAVOL: {question}"
    )
    return await _ask_ai(prompt)
"""

L0_CODE_RU = """
# Пример: вызов LLM "без RAG" показывает, почему ответ о данных
# платформы получается ненадёжным (ЧЕРЕЗ _ask_ai() из курса 135 —
# мы не переписываем её, а импортируем).

import asyncio
from app.services.grok_ai_client import _ask_ai


async def ask_without_rag(question: str) -> str | None:
    \"\"\"Прямой вопрос без RAG — ответ модели основан не на РЕАЛЬНЫХ
    данных платформы, а на её общих "знаниях".\"\"\"
    prompt = (
        f"Вопрос: {question}\\n\\n"
        "Пожалуйста, дай точный и краткий ответ."
    )
    return await _ask_ai(prompt)


async def main() -> None:
    question = "Сколько курсов на этой студенческой платформе и по каким категориям они распределены?"
    answer = await ask_without_rag(question)
    print("Вопрос:", question)
    print("Ответ модели (без RAG):", answer)
    print(
        "\\nВНИМАНИЕ: этот ответ может выглядеть уверенно, но модель "
        "никогда не видела таблицу courses этой платформы — она "
        "генерирует текст на основе статистической вероятности, а не "
        "возвращает реальные данные. Это — галлюцинация."
    )


if __name__ == "__main__":
    asyncio.run(main())


# ---------------------------------------------------------------------------
# Для сравнения: в варианте с RAG в промпт добавляются РЕАЛЬНЫЕ данные.
# (Полностью построим это в следующих уроках — здесь только видим разницу.)
# ---------------------------------------------------------------------------

async def ask_with_manual_context(question: str, real_facts: str) -> str | None:
    \"\"\"Простейшая форма RAG: поиска ещё нет, но добавление реальных
    фактов вручную в промпт резко меняет качество ответа.\"\"\"
    prompt = (
        "Используя следующие РЕАЛЬНЫЕ данные, ответь на вопрос. Если в "
        "данных нет ответа, скажи 'в данных об этом нет информации' — "
        "не выдумывай.\\n\\n"
        f"ДАННЫЕ:\\n{real_facts}\\n\\n"
        f"ВОПРОС: {question}"
    )
    return await _ask_ai(prompt)
"""

L0_TASK = {
    "task_title": "RAG'siz va RAG bilan javoblarni solishtiring",
    "task_title_ru": "Сравните ответы без RAG и с RAG",
    "task_description": (
        "Ikkita funksiya yozing: `ask_without_rag(question)` — savolni "
        "to'g'ridan-to'g'ri _ask_ai()ga yuboradi, va "
        "`ask_with_manual_context(question, real_facts)` — real_facts "
        "matnini promptga qo'shib yuboradi. Ikkalasini ham ushbu platforma "
        "haqidagi bitta savol bilan sinab ko'ring (masalan kurslar soni "
        "yoki bitta kursning tavsifi haqida) va ikki javobni solishtiring."
    ),
    "task_description_ru": (
        "Напишите две функции: `ask_without_rag(question)` — отправляет "
        "вопрос напрямую в _ask_ai(), и `ask_with_manual_context(question, "
        "real_facts)` — добавляет текст real_facts в промпт. Проверьте обе "
        "на одном вопросе об этой платформе (например, о количестве "
        "курсов или описании одного курса) и сравните два ответа."
    ),
    "task_requirements": (
        "1) ask_without_rag hech qanday qo'shimcha kontekstsiz ishlashi "
        "kerak. 2) ask_with_manual_context promptda aniq 'MA'LUMOT:' "
        "bo'limi bo'lishi kerak. 3) Natijada ikki javob konsolga chiqarilib, "
        "qaysi biri haqiqatga yaqinroq ekani izohlansin (komment sifatida)."
    ),
    "task_requirements_ru": (
        "1) ask_without_rag должна работать без какого-либо "
        "дополнительного контекста. 2) ask_with_manual_context должна "
        "содержать в промпте явный раздел 'ДАННЫЕ:'. 3) Оба ответа должны "
        "быть выведены в консоль с комментарием о том, какой из них ближе "
        "к истине."
    ),
    "task_technologies": "Python",
    "task_deadline_days": 3,
}

L0_SAMPLE = {
    "title": "Namuna: gallyutsinatsiyani ko'rsatish",
    "description": (
        "Bitta savolni ikki xil usulda so'rab, RAG'siz javob qanday "
        "ishonchli, lekin noto'g'ri bo'lishi mumkinligini ko'rsatadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "hallucination_demo.py",
            "language": "python",
            "code": (
                "import asyncio\n"
                "from app.services.grok_ai_client import _ask_ai\n\n\n"
                "async def compare(question: str, real_facts: str) -> None:\n"
                "    without = await _ask_ai(f\"Savol: {question}\")\n"
                "    with_ctx = await _ask_ai(\n"
                "        f\"MA'LUMOT:\\n{real_facts}\\n\\nSAVOL: {question}\\n\"\n"
                "        \"Faqat MA'LUMOT asosida javob ber.\"\n"
                "    )\n"
                "    print('--- RAG siz ---')\n"
                "    print(without)\n"
                "    print('--- RAG bilan (qo\\'lda qo\\'shilgan kontekst) ---')\n"
                "    print(with_ctx)\n\n\n"
                "if __name__ == '__main__':\n"
                "    asyncio.run(compare(\n"
                "        question='Bu kursning nechinchi haftaligi va qiyinlik darajasi qanday?',\n"
                "        real_facts='Kurs 4 haftalik, qiyinlik darajasi: Advanced.',\n"
                "    ))\n"
            ),
        },
    ],
}

L0_EXERCISES = [
    {
        "title": "RAG nima uchun kerak",
        "title_ru": "Зачем нужен RAG",
        "description": "LLM ushbu platformaning courses jadvali haqida to'g'ridan-to'g'ri so'ralganda nega noto'g'ri (lekin ishonchli) javob berishi mumkin?",
        "description_ru": "Почему LLM может дать неверный (но уверенный) ответ, если её напрямую спросить о таблице courses этой платформы?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki model courses jadvalini hech qachon ko'rmagan — u faqat training paytidagi bilimga tayanadi",
            "Chunki model courses so'zini tushunmaydi",
            "Chunki API kaliti noto'g'ri",
            "Chunki temperature juda past",
        ],
        "options_ru": [
            "Потому что модель никогда не видела таблицу courses — она опирается только на знания из обучения",
            "Потому что модель не понимает слово courses",
            "Потому что неверный API-ключ",
            "Потому что temperature слишком низкая",
        ],
        "correct_answers": "A",
        "hint": "Modelning \"bilimi\" qachon shakllangan va u qachon muzlaydi?",
        "hint_ru": "Когда формируются 'знания' модели и когда они замораживаются?",
        "explanation": "LLM faqat training paytida ko'rgan matnni biladi; production ma'lumotlar bazasi bu bilimning bir qismi emas.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "RAG'ning uch bosqichi",
        "title_ru": "Три этапа RAG",
        "description": "RAG pipeline'ning ikkinchi bosqichi (topilgan bo'laklarni promptga qo'shish) ___ deb ataladi.",
        "description_ru": "Второй этап RAG pipeline (добавление найденных фрагментов в промпт) называется ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "augment",
        "hint": "Retrieve -> ___ -> Generate",
        "hint_ru": "Retrieve -> ___ -> Generate",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Semantik qidiruv vs klassik qidiruv",
        "title_ru": "Семантический поиск против классического",
        "description": "Foydalanuvchi \"backend qanday sozlanadi\" deb so'raydi, dars matnida esa \"server konfiguratsiyasi\" deb yozilgan. Klassik LIKE '%so'z%' qidiruvi bu holatda nima qiladi?",
        "description_ru": "Пользователь спрашивает \"как настроить backend\", а в тексте урока написано \"конфигурация сервера\". Что сделает классический поиск LIKE '%слово%' в этом случае?",
        "exercise_type": "multiple_choice",
        "options": [
            "Hech narsa topmaydi — so'zlar boshqacha, garchi ma'nosi bir xil bo'lsa ham",
            "Ma'noni tushunib, dars matnini topadi",
            "Xato chiqaradi",
            "Barcha darslarni qaytaradi",
        ],
        "options_ru": [
            "Ничего не найдёт — слова разные, хотя смысл одинаковый",
            "Поймёт смысл и найдёт текст урока",
            "Выдаст ошибку",
            "Вернёт все уроки",
        ],
        "correct_answers": "A",
        "hint": "Klassik qidiruv so'zlarni solishtiradimi yoki ma'noni?",
        "hint_ru": "Классический поиск сравнивает слова или смысл?",
        "explanation": "Klassik matn qidirish faqat aniq so'zlarni topadi; semantik qidiruv esa ma'noni (vektor orqali) solishtiradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "RAG pipeline bosqichlari",
        "title_ru": "Этапы RAG pipeline",
        "description": "Bosqichlarni to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Foydalanuvchi savol beradi",
            "Retrieve: mos hujjat bo'laklari topiladi",
            "Augment: bo'laklar promptga qo'shiladi",
            "Generate: LLM haqiqiy ma'lumot asosida javob beradi",
        ],
        "drag_items_ru": [
            "Пользователь задаёт вопрос",
            "Retrieve: находятся подходящие фрагменты документов",
            "Augment: фрагменты добавляются в промпт",
            "Generate: LLM отвечает на основе реальных данных",
        ],
        "correct_order": [
            "Foydalanuvchi savol beradi",
            "Retrieve: mos hujjat bo'laklari topiladi",
            "Augment: bo'laklar promptga qo'shiladi",
            "Generate: LLM haqiqiy ma'lumot asosida javob beradi",
        ],
        "hint": "Darsdagi diagrammani eslang: savol -> retrieve -> augment -> generate.",
        "hint_ru": "Вспомните диаграмму из урока: вопрос -> retrieve -> augment -> generate.",
        "difficulty_level": "Easy",
        "points": 6,
    },
]

# ---------------------------------------------------------------------------
# Lesson 1 — Embedding'lar 101: matnni vektorga aylantirish
# ---------------------------------------------------------------------------

L1_TEXT = """
<h3>Embedding — matnni "ma'no koordinatalariga" aylantirish</h3>
<p>Oldingi darsda aytdik: semantik qidiruv uchun matnni raqamlarga aylantirish
kerak. <strong>Embedding</strong> — bu aynan shu: matn (so'z, jumla, butun
paragraf) kirish sifatida beriladi, natijada uzunligi doim bir xil bo'lgan
suzuvchi nuqta (float) sonlar ro'yxati — <strong>vektor</strong> — chiqadi.
Masalan <code>"Python funksiyalari"</code> jumlasi 384 o'lchamli (dimension)
modelda <code>[0.021, -0.114, 0.087, ..., 0.003]</code> kabi 384 ta sondan
iborat vektorga aylanadi. Bu sonlarning o'zi inson uchun ma'nosiz — lekin
ularning bir-biriga NISBATAN joylashuvi ma'noni ifodalaydi.</p>

<h3>Nega bu ishlaydi: ma'no bo'yicha yaqinlik</h3>
<p>Embedding modeli shunday o'qitilganki, MA'NOSI yaqin matnlar vektor
fazosida ham bir-biriga YAQIN joylashadi. <code>"itni sevaman"</code> va
<code>"kuchukni yaxshi ko'raman"</code> jumlalari boshqa-boshqa so'zlardan
iborat, lekin ularning vektorlari fazoda bir-biriga yaqin bo'ladi — chunki
ma'nosi yaqin. Aksincha, <code>"itni sevaman"</code> va
<code>"pomidor narxi oshdi"</code> vektorlari fazoda uzoq joylashadi. Keyingi
darsda aynan shu "yaqinlik"ni sonlar bilan qanday o'lchashni (cosine
similarity) ko'ramiz — bu darsda faqat vektorni QANDAY olishga e'tibor
qaratamiz.</p>

<h3>Ikki yo'l: mahalliy model vs hosted API</h3>
<p>Embedding olish uchun ikkita asosiy yondashuv bor:</p>
<ul>
<li><strong>Mahalliy model (masalan <code>sentence-transformers</code>
kutubxonasi, <code>all-MiniLM-L6-v2</code> modeli)</strong> — API kaliti
kerak emas, internet aloqasi kerak emas (model bir marta yuklab olinadi),
har qanday chegarasiz miqdorda matnni bepul embedding qilish mumkin. Kamchilik:
modelni serveringizga o'rnatish, xotira sarflash kerak (kichik modellar ham
bir necha yuz megabayt).</li>
<li><strong>Hosted API (masalan Gemini'ning <code>text-embedding-004</code>
modeli)</strong> — API kaliti orqali HTTP so'rov yuborasiz, model sizning
serveringizda emas, Google serverida ishlaydi. Bepul tarif mavjud (aniq
chegaralarni provider dashboard'ida tekshiring — bu son vaqt o'tishi bilan
o'zgarishi mumkin). Kamchilik: internet, API kaliti va rate limit'ga
bog'liqlik.</li>
</ul>
<p>Ikkalasi ham bir xil natija beradi: matn -> son vektor. Farq faqat QAYERDA
hisoblash bajarilishida (sizning mashinangizda yoki provider serverida).</p>

<h3>Muhim qoida: bir xil model, doim</h3>
<p>Qidiruv ishlashi uchun HAM hujjatlar, HAM foydalanuvchi so'rovi <strong>bir
xil embedding modeli</strong> bilan vektorlanishi shart. Agar hujjatlarni
<code>all-MiniLM-L6-v2</code> bilan (384 o'lcham) vektorlagan bo'lsangiz-u,
so'rovni Gemini'ning <code>text-embedding-004</code> bilan (768 o'lcham)
vektorlasangiz — o'lchamlar mos kelmaydi va solishtirish matematik jihatdan
ma'nosiz bo'ladi (hatto kod ishlab tursa ham, natija to'g'ri bo'lmaydi).</p>

<h3>Vektor fazosi — geometrik tasavvur</h3>
<pre class="mermaid">
flowchart LR
  T1["'Python funksiyasi qanday yoziladi'"] -->|"embed()"| V1["[0.02, -0.11, 0.08, ...]"]
  T2["'def kalit so'zi bilan funksiya e'lon qilinadi'"] -->|"embed()"| V2["[0.03, -0.09, 0.07, ...]"]
  T3["'Pitsa retsepti: xamir va pomidor sousi'"] -->|"embed()"| V3["[0.71, 0.44, -0.20, ...]"]
  V1 -.->|"vektor fazosida YAQIN
(ma'nosi yaqin)"| V2
  V1 -.->|"vektor fazosida UZOQ
(ma'nosi boshqa)"| V3
</pre>
<p>V1 va V2 — ikkalasi ham Python funksiyalari haqida, shuning uchun ularning
vektorlari fazoda yaqin. V3 — butunlay boshqa mavzu (pitsa retsepti), shuning
uchun uzoq. Bu — RAG'ning butun asosi: MA'NOSI yaqin narsalarni GEOMETRIK
yaqinlik orqali topish.</p>

<h3>O'lcham (dimension) haqida: nima uchun bu raqam muhim</h3>
<p>Har bir embedding modelining o'z FIKS o'lchami bor: masalan
<code>all-MiniLM-L6-v2</code> — 384, Gemini'ning <code>text-embedding-004</code>
— 768. Ko'proq o'lcham ko'pincha ko'proq nuance (nozik farq)ni ushlab qola
oladi, lekin narxi bor: saqlash uchun ko'proq joy (har bir hujjat uchun
768 ta float 384 tadan ikki baravar ko'p joy egallaydi) va solishtirish
biroz sekinroq bo'ladi. Kichik loyihalar uchun 384 o'lcham odatda yetarli;
juda katta, nozik farqlangan korpus uchun kattaroq o'lcham foyda berishi
mumkin. Bu — narx/aniqlik savdolashuvi, "har doim kattaroq yaxshi" degani
emas.</p>

<h3>Bu kursda qaysi yondashuvni tanlaymiz</h3>
<p>Keyingi darslarda (ayniqsa amaliy semantik qidiruv darsida) biz mahalliy
<code>sentence-transformers</code> yondashuvini afzal ko'ramiz — chunki u
API kaliti va tarmoq bog'liqligisiz, deterministik ishlaydi, bu esa
o'quv/demo muhitida qulayroq. Lekin production loyihada ikkala variant ham
haqiqiy variant — tanlov xotira/tezlik va operatsion murakkablik
o'rtasidagi savdolashuvga bog'liq.</p>
"""

L1_TEXT_RU = """
<h3>Эмбеддинг — превращение текста в "координаты смысла"</h3>
<p>В прошлом уроке мы сказали: для семантического поиска текст нужно
превратить в числа. <strong>Эмбеддинг</strong> — это именно это: на вход
подаётся текст (слово, фраза, целый абзац), а на выходе получается список
чисел с плавающей точкой (float) ВСЕГДА одинаковой длины —
<strong>вектор</strong>. Например, фраза <code>"функции Python"</code> в
модели с 384 измерениями (dimension) превращается в вектор из 384 чисел,
например <code>[0.021, -0.114, 0.087, ..., 0.003]</code>. Сами эти числа
бессмысленны для человека — но их расположение ОТНОСИТЕЛЬНО друг друга
выражает смысл.</p>

<h3>Почему это работает: близость по смыслу</h3>
<p>Модель эмбеддинга обучена так, что тексты с БЛИЗКИМ смыслом располагаются
в векторном пространстве БЛИЗКО друг к другу. Фразы <code>"я люблю
собак"</code> и <code>"мне нравятся щенки"</code> состоят из разных слов, но
их векторы в пространстве оказываются близко — потому что смысл близкий. И
наоборот, векторы <code>"я люблю собак"</code> и <code>"цена на помидоры
выросла"</code> располагаются в пространстве далеко. В следующем уроке мы
увидим, как именно измерить эту "близость" числами (косинусное сходство) —
в этом уроке фокус на том, КАК получить вектор.</p>

<h3>Два пути: локальная модель против hosted API</h3>
<p>Есть два основных подхода к получению эмбеддинга:</p>
<ul>
<li><strong>Локальная модель (например, библиотека
<code>sentence-transformers</code>, модель
<code>all-MiniLM-L6-v2</code>)</strong> — API-ключ не нужен, интернет не
нужен (модель загружается один раз), можно бесплатно векторизовать любое
количество текста без ограничений. Недостаток: нужно установить модель на
сервер, требуется память (даже маленькие модели — несколько сотен
мегабайт).</li>
<li><strong>Hosted API (например, модель Gemini
<code>text-embedding-004</code>)</strong> — вы отправляете HTTP-запрос с
API-ключом, модель работает не на вашем сервере, а на сервере Google. Есть
бесплатный тариф (точные лимиты проверяйте в дашборде провайдера — эти
числа могут меняться со временем). Недостаток: зависимость от интернета,
API-ключа и rate limit.</li>
</ul>
<p>Оба подхода дают одинаковый результат: текст -> числовой вектор. Разница
только в том, ГДЕ выполняется вычисление (на вашей машине или на сервере
провайдера).</p>

<h3>Важное правило: всегда одна и та же модель</h3>
<p>Чтобы поиск работал, И документы, И запрос пользователя должны быть
векторизованы <strong>одной и той же моделью эмбеддинга</strong>. Если вы
векторизовали документы моделью <code>all-MiniLM-L6-v2</code> (384
измерения), а запрос — моделью Gemini <code>text-embedding-004</code> (768
измерений) — размерности не совпадут, и сравнение станет математически
бессмысленным (даже если код формально выполнится, результат будет
неверным).</p>

<h3>Векторное пространство — геометрическое представление</h3>
<pre class="mermaid">
flowchart LR
  T1["'Как пишется функция в Python'"] -->|"embed()"| V1["[0.02, -0.11, 0.08, ...]"]
  T2["'Функция объявляется ключевым словом def'"] -->|"embed()"| V2["[0.03, -0.09, 0.07, ...]"]
  T3["'Рецепт пиццы: тесто и томатный соус'"] -->|"embed()"| V3["[0.71, 0.44, -0.20, ...]"]
  V1 -.->|"БЛИЗКО в векторном пространстве
(смысл похожий)"| V2
  V1 -.->|"ДАЛЕКО в векторном пространстве
(смысл другой)"| V3
</pre>
<p>V1 и V2 — оба про функции Python, поэтому их векторы близки в
пространстве. V3 — совсем другая тема (рецепт пиццы), поэтому далеко. Это —
вся основа RAG: находить БЛИЗКИЕ по смыслу вещи через ГЕОМЕТРИЧЕСКУЮ
близость.</p>

<h3>О размерности (dimension): почему это число важно</h3>
<p>У каждой модели эмбеддинга своя ФИКСИРОВАННАЯ размерность: например,
<code>all-MiniLM-L6-v2</code> — 384, у Gemini <code>text-embedding-004</code>
— 768. Больше размерность часто может уловить больше нюансов (тонких
различий), но за это есть цена: больше места для хранения (768 float на
документ занимают вдвое больше места, чем 384) и сравнение работает чуть
медленнее. Для небольших проектов 384 измерений обычно достаточно; для
очень большого, тонко различающегося корпуса больше измерений может дать
пользу. Это — компромисс цена/точность, а не "чем больше, тем всегда
лучше".</p>

<h3>Какой подход выбираем в этом курсе</h3>
<p>В следующих уроках (особенно в уроке практического семантического
поиска) мы предпочитаем локальный подход
<code>sentence-transformers</code> — потому что он работает
детерминированно, без API-ключа и зависимости от сети, что удобнее в
учебной/демо-среде. Но в production-проекте оба варианта реальны — выбор
зависит от компромисса между памятью/скоростью и операционной
сложностью.</p>
"""

L1_CODE = """
# Ikkala yondashuvni ham ko'ramiz: mahalliy (sentence-transformers) va
# hosted API (Gemini). Ikkalasi ham bir xil natija turi qaytaradi:
# suzuvchi sonlar ro'yxati (vektor).

from __future__ import annotations
import math


# ---------------------------------------------------------------------------
# 1) Mahalliy model bilan (production'da haqiqiy kutubxona shunday ishlatiladi)
# ---------------------------------------------------------------------------
#
#   from sentence_transformers import SentenceTransformer
#   model = SentenceTransformer("all-MiniLM-L6-v2")   # bir marta yuklanadi
#   vector = model.encode("Python funksiyalari qanday e'lon qilinadi")
#   # vector — 384 ta floatdan iborat numpy array
#
# Bu kursda haqiqiy og'ir modelni yuklamasdan, PRINSIPNI ko'rsatish uchun
# oddiy, deterministik "soxta embedding" funksiyasidan foydalanamiz — u
# so'zlarning belgi-darajasidagi xususiyatlaridan foydalanib past o'lchamli
# vektor yasaydi. Bu HAQIQIY semantik model emas (faqat harf statistikasiga
# asoslangan), lekin vektor SHAKLI va API'si bir xil — shuning uchun
# quyidagi cosine_similarity, chunking va pgvector darslari xuddi shu
# funksiya ustida ishlaydi.

def fake_embed(text: str, dims: int = 32) -> list[float]:
    \"\"\"Deterministik, kichik o'lchamli "o'quv uchun" embedding — haqiqiy
    modeldagi kabi og'ir emas, lekin xuddi shunday: matn -> son vektori.\"\"\"
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        idx = (ord(ch) + i) % dims
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]  # normallashtirilgan (uzunligi 1) vektor


# ---------------------------------------------------------------------------
# 2) Hosted API bilan (Gemini text-embedding-004) — haqiqiy HTTP so'rov shakli
# ---------------------------------------------------------------------------

import httpx
from app.config import settings


async def gemini_embed(text: str) -> list[float] | None:
    \"\"\"Gemini'ning embedding endpoint'iga haqiqiy so'rov shakli.
    API kaliti bo'lmasa None qaytaradi (135-kursdagi ProviderError
    uslubiga o'xshab) — chaqiruvchi kod fallback qila oladi.\"\"\"
    if not settings.GEMINI_API_KEY:
        return None
    url = (
        f"{settings.GEMINI_API_URL.rstrip('/')}/text-embedding-004:embedContent"
        f"?key={settings.GEMINI_API_KEY}"
    )
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json={"content": {"parts": [{"text": text}]}})
        if resp.status_code >= 400:
            return None
        data = resp.json()
        return data.get("embedding", {}).get("values")


if __name__ == "__main__":
    v1 = fake_embed("Python funksiyasi qanday yoziladi")
    v2 = fake_embed("def kalit so'zi bilan funksiya e'lon qilinadi")
    v3 = fake_embed("Pitsa retsepti: xamir va pomidor sousi")
    print("V1 o'lchami:", len(v1))
    print("V1[:5]:", [round(x, 3) for x in v1[:5]])
    print("V2[:5]:", [round(x, 3) for x in v2[:5]])
    print("V3[:5]:", [round(x, 3) for x in v3[:5]])
"""

L1_CODE_RU = """
# Рассмотрим оба подхода: локальный (sentence-transformers) и hosted API
# (Gemini). Оба возвращают один и тот же тип результата: список чисел
# с плавающей точкой (вектор).

from __future__ import annotations
import math


# ---------------------------------------------------------------------------
# 1) С локальной моделью (в production используется реальная библиотека)
# ---------------------------------------------------------------------------
#
#   from sentence_transformers import SentenceTransformer
#   model = SentenceTransformer("all-MiniLM-L6-v2")   # загружается один раз
#   vector = model.encode("Как объявляются функции в Python")
#   # vector — numpy array из 384 float-чисел
#
# В этом курсе, не загружая тяжёлую реальную модель, для ДЕМОНСТРАЦИИ
# ПРИНЦИПА используем простую, детерминированную "фейковую эмбеддинг"
# функцию — она строит вектор малой размерности на основе посимвольной
# статистики. Это НЕ настоящая семантическая модель (основана только на
# статистике букв), но ФОРМА и API вектора те же — поэтому следующие уроки
# про cosine_similarity, chunking и pgvector работают именно с этой
# функцией.

def fake_embed(text: str, dims: int = 32) -> list[float]:
    \"\"\"Детерминированный, малоразмерный "учебный" эмбеддинг — не такой
    тяжёлый, как настоящая модель, но по сути то же самое: текст -> вектор
    чисел.\"\"\"
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        idx = (ord(ch) + i) % dims
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]  # нормализованный вектор (длина 1)


# ---------------------------------------------------------------------------
# 2) С hosted API (Gemini text-embedding-004) — реальная форма HTTP-запроса
# ---------------------------------------------------------------------------

import httpx
from app.config import settings


async def gemini_embed(text: str) -> list[float] | None:
    \"\"\"Реальная форма запроса к embedding-эндпоинту Gemini. Если нет
    API-ключа, возвращает None (в стиле ProviderError из курса 135) —
    вызывающий код может сделать fallback.\"\"\"
    if not settings.GEMINI_API_KEY:
        return None
    url = (
        f"{settings.GEMINI_API_URL.rstrip('/')}/text-embedding-004:embedContent"
        f"?key={settings.GEMINI_API_KEY}"
    )
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json={"content": {"parts": [{"text": text}]}})
        if resp.status_code >= 400:
            return None
        data = resp.json()
        return data.get("embedding", {}).get("values")


if __name__ == "__main__":
    v1 = fake_embed("Как пишется функция в Python")
    v2 = fake_embed("Функция объявляется ключевым словом def")
    v3 = fake_embed("Рецепт пиццы: тесто и томатный соус")
    print("Размер V1:", len(v1))
    print("V1[:5]:", [round(x, 3) for x in v1[:5]])
    print("V2[:5]:", [round(x, 3) for x in v2[:5]])
    print("V3[:5]:", [round(x, 3) for x in v3[:5]])
"""

L1_TASK = {
    "task_title": "O'z fake_embed funksiyangizni yozing va sinang",
    "task_title_ru": "Напишите и протестируйте свою функцию fake_embed",
    "task_description": (
        "Darsdagi `fake_embed` funksiyasini asos qilib olib, kamida 5 ta "
        "jumlani (2 tasi bir mavzuda, 3 tasi boshqa mavzularda) "
        "vektorlashtiring va har bir vektorning uzunligini hamda birinchi "
        "5 elementini chiqaring."
    ),
    "task_description_ru": (
        "Взяв за основу функцию `fake_embed` из урока, векторизуйте не "
        "менее 5 предложений (2 на одну тему, 3 на разные темы) и выведите "
        "длину каждого вектора и первые 5 его элементов."
    ),
    "task_requirements": (
        "1) Kamida 5 ta jumla ishlatilsin. 2) Har bir vektorning uzunligi "
        "(dims) bir xil bo'lishi shart. 3) Natijalar konsolga chiroyli "
        "formatda chiqarilsin (jumla + vektor boshi)."
    ),
    "task_requirements_ru": (
        "1) Должно быть использовано не менее 5 предложений. 2) Длина "
        "(dims) каждого вектора обязана быть одинаковой. 3) Результаты "
        "должны быть аккуратно выведены в консоль (предложение + начало "
        "вектора)."
    ),
    "task_technologies": "Python",
    "task_deadline_days": 3,
}

L1_SAMPLE = {
    "title": "Namuna: bir nechta jumlani vektorlashtirish",
    "description": (
        "fake_embed yordamida bir nechta jumlani vektorlashtiradi va "
        "vektorlar o'lchamini tekshiradi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "embed_sentences.py",
            "language": "python",
            "code": (
                "import math\n\n\n"
                "def fake_embed(text: str, dims: int = 32) -> list[float]:\n"
                "    text = text.lower().strip()\n"
                "    vector = [0.0] * dims\n"
                "    for i, ch in enumerate(text):\n"
                "        idx = (ord(ch) + i) % dims\n"
                "        vector[idx] += 1.0\n"
                "    norm = math.sqrt(sum(v * v for v in vector)) or 1.0\n"
                "    return [v / norm for v in vector]\n\n\n"
                "sentences = [\n"
                "    \"Python funksiyasi def bilan e'lon qilinadi\",\n"
                "    \"Funksiyalarni def kalit so'zi bilan yozamiz\",\n"
                "    \"Osmon bugun juda bulutli\",\n"
                "]\n\n"
                "for s in sentences:\n"
                "    v = fake_embed(s)\n"
                "    print(f\"{s!r} -> dims={len(v)} boshi={[round(x, 3) for x in v[:5]]}\")\n"
            ),
        },
    ],
}

L1_EXERCISES = [
    {
        "title": "Embedding nima",
        "title_ru": "Что такое эмбеддинг",
        "description": "Embedding — bu qanday jarayon?",
        "description_ru": "Что такое эмбеддинг как процесс?",
        "exercise_type": "multiple_choice",
        "options": [
            "Matnni doim bir xil uzunlikdagi son vektoriga aylantirish",
            "Matnni faylga saqlash",
            "Matnni boshqa tilga tarjima qilish",
            "Matndagi xatolarni tuzatish",
        ],
        "options_ru": [
            "Превращение текста в числовой вектор всегда одинаковой длины",
            "Сохранение текста в файл",
            "Перевод текста на другой язык",
            "Исправление ошибок в тексте",
        ],
        "correct_answers": "A",
        "hint": "Darsdagi ta'rifni eslang: kirish matn, chiqish — ?",
        "hint_ru": "Вспомните определение из урока: вход — текст, выход — ?",
        "explanation": "Embedding — matnni doim bir xil o'lchamdagi float sonlar ro'yxatiga aylantiruvchi jarayon.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Ma'no yaqinligi",
        "title_ru": "Близость по смыслу",
        "description": "Embedding modeli ma'nosi yaqin ikki jumlaning vektorlarini vektor fazosida qanday joylashtiradi?",
        "description_ru": "Как модель эмбеддинга располагает в векторном пространстве векторы двух предложений с близким смыслом?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bir-biriga yaqin",
            "Bir-biridan uzoq",
            "Har doim bir xil nuqtada",
            "Tasodifiy joyda",
        ],
        "options_ru": [
            "Близко друг к другу",
            "Далеко друг от друга",
            "Всегда в одной точке",
            "В случайном месте",
        ],
        "correct_answers": "A",
        "hint": "\"itni sevaman\" va \"kuchukni yaxshi ko'raman\" misolini eslang.",
        "hint_ru": "Вспомните пример 'я люблю собак' и 'мне нравятся щенки'.",
        "explanation": "Ma'nosi yaqin matnlar embedding fazosida geometrik jihatdan yaqin joylashadi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Bir xil model qoidasi",
        "title_ru": "Правило одной модели",
        "description": "Hujjatlar va so'rov qidiruv ishlashi uchun ___ embedding modeli bilan vektorlashtirilishi shart.",
        "description_ru": "Чтобы поиск работал, документы и запрос должны быть векторизованы ___ моделью эмбеддинга.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "bir xil",
        "correct_answers_ru": "одной и той же",
        "hint": "Agar o'lchamlar mos kelmasa, solishtirish matematik jihatdan nima bo'ladi?",
        "hint_ru": "Если размерности не совпадают, чем становится сравнение математически?",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Mahalliy vs hosted embedding",
        "title_ru": "Локальный против hosted эмбеддинга",
        "description": "Xususiyatlarni to'g'ri toifaga mos qo'ying (tartibda joylashtiring: avval mahalliy modelga, keyin hosted API'ga xos xususiyat)",
        "description_ru": "Расположите характеристики по порядку (сначала — свойство локальной модели, затем — свойство hosted API)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "API kaliti kerak emas",
            "Internet aloqasi shart emas",
            "Rate limit'ga bog'liq",
            "Modelni serverga o'rnatish shart emas",
        ],
        "drag_items_ru": [
            "API-ключ не нужен",
            "Интернет не обязателен",
            "Зависит от rate limit",
            "Не нужно устанавливать модель на сервер",
        ],
        "correct_order": [
            "API kaliti kerak emas",
            "Internet aloqasi shart emas",
            "Rate limit'ga bog'liq",
            "Modelni serverga o'rnatish shart emas",
        ],
        "hint": "Birinchi ikkitasi mahalliy modelga, keyingi ikkitasi hosted API'ga xos.",
        "hint_ru": "Первые два — про локальную модель, следующие два — про hosted API.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 2 — Hujjatlarni chunk'larga bo'lish (chunking)
# ---------------------------------------------------------------------------

L2_TEXT = """
<h3>Nega butun hujjatni bitta vektorga aylantirib bo'lmaydi</h3>
<p>Bu platformaning <code>lessons</code> jadvalidagi ba'zi darslar juda uzun
— masalan platformadagi eng uzun published dars matni 40,000dan ortiq
belgidan iborat. Agar shu butun matnni BITTA embedding vektoriga aylantirsak,
vektor "o'rtacha ma'no"ni ifodalaydi — dars ichidagi 10 xil kichik mavzuning
(masalan HTML, CSS, JS) barchasi bitta "aralash" vektorga siqiladi. Natijada
foydalanuvchi "CSS Flexbox qanday ishlaydi" deb so'raganda, qidiruv butun
darsni topadi (chunki u mos), lekin LLM'ga faqat kerakli 500 belgi o'rniga
40,000 belgi yuboriladi — bu ham narxni oshiradi, ham LLM'ning diqqatini
tarqatadi ("lost in the middle" muammosi — uzun kontekstda LLM o'rtadagi
ma'lumotni ko'pincha e'tibordan chetda qoldiradi).</p>

<p>Yechim: hujjatni <strong>chunk</strong> (bo'lak)larga bo'lish — har bir
chunk alohida vektorlashtiriladi va alohida saqlanadi. Qidiruv paytida butun
dars emas, faqat ENG MOS chunk(lar) topiladi va LLM'ga yuboriladi.</p>

<h3>Chunk o'lchami: juda kichik va juda katta muammolari</h3>
<ul>
<li><strong>Juda kichik chunk</strong> (masalan bitta jumla) — kontekstni
yo'qotadi. "Buni <code>flex-direction: column</code> bilan qiling" jumlasi
alohida olinganda, "buni" nimani anglatishi noaniq bo'lib qoladi — oldingi
jumla kontekstisiz ma'no yo'qoladi.</li>
<li><strong>Juda katta chunk</strong> (butun dars) — birinchi paragraf
yuqorida aytilgani kabi, LLM'ning diqqatini tarqatadi va narxni oshiradi,
bundan tashqari BIR chunk ICHIDA bir nechta boshqa-boshqa mavzu bo'lsa,
embedding "aralash" bo'lib, qidiruv aniqligi pasayadi.</li>
</ul>
<p>Amaliyotda odatiy boshlang'ich nuqta — taxminan 200-500 so'z (yoki
500-1500 belgi) atrofidagi chunk, lekin bu QATTIQ qoida emas — hujjat
tuzilishiga (masalan HTML <code>&lt;h3&gt;</code> sarlavhalari, paragraflar)
qarab moslashtiriladi.</p>

<h3>Overlap (qoplanish): nega chegarada kesish xavfli</h3>
<p>Agar chunk'larni qattiq chegaralar bilan kessak (masalan har 500-belgida),
muhim gap chunk chegarasida ikkiga bo'linib ketishi mumkin — masalan bitta
chunk "...natijada funksiya" bilan tugab, keyingi chunk "chaqirilganda xato
yuz beradi..." bilan boshlansa, ikkalasi alohida hech narsa anglatmaydi.
Yechim — <strong>overlap</strong>: har bir keyingi chunk oldingisining oxirgi
qismini (masalan 50-100 belgi) qaytadan o'z ichiga oladi. Bu ba'zi matnni
ikki marta saqlash degani (bir oz ortiqcha joy), lekin chegaradagi ma'noni
yo'qotmaslikni kafolatlaydi.</p>

<h3>Chunking strategiyalari</h3>
<ul>
<li><strong>Fixed-size (qattiq o'lcham)</strong> — har N belgidan/tokendan
keyin kesish, overlap bilan. Eng oddiy, tez ishlaydi, lekin gaplarni
o'rtadan kesishi mumkin.</li>
<li><strong>Sentence-aware (jumlaga moslashgan)</strong> — jumla oxirigacha
(nuqta, undov belgisi) kutib, keyin kesish — gapni ikkiga bo'lmaydi.</li>
<li><strong>Structure-aware (tuzilishga moslashgan)</strong> — HTML
<code>&lt;h3&gt;</code>/<code>&lt;p&gt;</code> chegaralaridan foydalanish —
har bir bo'lim (masalan darsdagi bitta <code>&lt;h3&gt;</code> ostidagi
matn) alohida chunk bo'ladi. Bu ko'pincha ENG YAXSHI natija beradi, chunki
muallif (o'qituvchi) allaqachon mantiqiy bo'limlarga ajratib qo'ygan.</li>
</ul>

<h3>Chunking diagrammasi: haqiqiy dars matni misolida</h3>
<pre class="mermaid">
flowchart TB
  DOC["lessons.text_content
(masalan: 'CSS Flexbox' darsi, ~3000 belgi)"]
  DOC --> C1["Chunk 1: h3 'Flexbox nima' + paragraf"]
  DOC --> C2["Chunk 2: h3 'flex-direction xususiyati' + paragraf
(oxiri C1'ning oxirgi jumlasi bilan overlap)"]
  DOC --> C3["Chunk 3: h3 'justify-content va align-items' + paragraf"]
  C1 --> E1["embed() -> vektor 1"]
  C2 --> E2["embed() -> vektor 2"]
  C3 --> E3["embed() -> vektor 3"]
</pre>
<p>Har bir chunk endi alohida qidiriladigan birlik: agar foydalanuvchi
"flex-direction nima qiladi" deb so'rasa, faqat Chunk 2 topiladi — butun
dars emas.</p>

<h3>Bu kursdagi haqiqiy misol</h3>
<p>Keyingi amaliy darsda (semantik qidiruv) biz aynan shu strategiyani
ushbu platformaning haqiqiy <code>lessons.text_content</code> ustunidagi HTML
matnga qo'llaymiz — structure-aware chunking, <code>&lt;h3&gt;</code> teglari
bo'yicha bo'lish, so'ngra har bir bo'limni alohida vektorlashtirish.</p>
"""

L2_TEXT_RU = """
<h3>Почему нельзя превратить весь документ в один вектор</h3>
<p>Некоторые уроки в таблице <code>lessons</code> этой платформы очень
длинные — например, самый длинный опубликованный текст урока содержит
более 40 000 символов. Если превратить весь этот текст в ОДИН вектор
эмбеддинга, вектор будет отражать "усреднённый смысл" — все 10 разных
подтем внутри урока (например, HTML, CSS, JS) сожмутся в один "смешанный"
вектор. В результате, когда пользователь спрашивает "как работает CSS
Flexbox", поиск найдёт весь урок (потому что он подходит), но LLM получит
не нужные 500 символов, а все 40 000 — это увеличивает цену и рассеивает
внимание LLM (проблема "lost in the middle" — в длинном контексте LLM часто
упускает информацию из середины).</p>

<p>Решение: разбить документ на <strong>chunk</strong> (фрагменты) — каждый
фрагмент векторизуется и сохраняется отдельно. При поиске находится не весь
урок, а только НАИБОЛЕЕ подходящий(е) фрагмент(ы), который(е) отправляется
LLM.</p>

<h3>Размер фрагмента: проблемы слишком маленького и слишком большого</h3>
<ul>
<li><strong>Слишком маленький фрагмент</strong> (например, одно
предложение) — теряет контекст. Предложение "Сделайте это с помощью
<code>flex-direction: column</code>" отдельно взятое становится
неоднозначным — "это" без предыдущего предложения теряет смысл.</li>
<li><strong>Слишком большой фрагмент</strong> (весь урок) — как сказано
выше, рассеивает внимание LLM и увеличивает цену, а также если ВНУТРИ
одного фрагмента несколько разных тем, эмбеддинг становится "смешанным",
снижая точность поиска.</li>
</ul>
<p>На практике типичная отправная точка — фрагмент примерно 200-500 слов
(или 500-1500 символов), но это НЕ жёсткое правило — оно подстраивается
под структуру документа (например, заголовки <code>&lt;h3&gt;</code>,
абзацы в HTML).</p>

<h3>Overlap (перекрытие): почему резать на границе опасно</h3>
<p>Если резать фрагменты жёсткими границами (например, каждые 500 символов),
важная мысль может разделиться пополам на границе фрагмента — например,
один фрагмент заканчивается "...в результате функция", а следующий
начинается "при вызове возникает ошибка..." — по отдельности оба не имеют
смысла. Решение — <strong>overlap</strong>: каждый следующий фрагмент
повторно включает конец предыдущего (например, 50-100 символов). Это
означает сохранение части текста дважды (немного лишнего места), но
гарантирует, что смысл на границе не потеряется.</p>

<h3>Стратегии chunking</h3>
<ul>
<li><strong>Fixed-size (фиксированный размер)</strong> — резать после каждых
N символов/токенов, с overlap. Самый простой, быстрый, но может разрезать
предложение посередине.</li>
<li><strong>Sentence-aware (с учётом предложений)</strong> — резать только
после конца предложения (точка, восклицательный знак) — предложение не
разрывается.</li>
<li><strong>Structure-aware (с учётом структуры)</strong> — использование
границ HTML <code>&lt;h3&gt;</code>/<code>&lt;p&gt;</code> — каждый раздел
(например, текст под одним <code>&lt;h3&gt;</code> в уроке) становится
отдельным фрагментом. Часто даёт ЛУЧШИЙ результат, потому что автор
(преподаватель) уже разделил материал на логические разделы.</li>
</ul>

<h3>Диаграмма chunking на примере реального текста урока</h3>
<pre class="mermaid">
flowchart TB
  DOC["lessons.text_content
(например: урок 'CSS Flexbox', ~3000 символов)"]
  DOC --> C1["Chunk 1: h3 'Что такое Flexbox' + абзац"]
  DOC --> C2["Chunk 2: h3 'Свойство flex-direction' + абзац
(начало — overlap с концом C1)"]
  DOC --> C3["Chunk 3: h3 'justify-content и align-items' + абзац"]
  C1 --> E1["embed() -> вектор 1"]
  C2 --> E2["embed() -> вектор 2"]
  C3 --> E3["embed() -> вектор 3"]
</pre>
<p>Теперь каждый фрагмент — отдельная единица поиска: если пользователь
спрашивает "что делает flex-direction", найдётся только Chunk 2 — а не
весь урок.</p>

<h3>Реальный пример в этом курсе</h3>
<p>В следующем практическом уроке (семантический поиск) мы применим именно
эту стратегию к реальному HTML-тексту столбца <code>lessons.text_content</code>
этой платформы — structure-aware chunking, разбиение по тегам
<code>&lt;h3&gt;</code>, затем векторизация каждого раздела отдельно.</p>
"""

L2_CODE = """
# Chunking funksiyalari: fixed-size (overlap bilan) va structure-aware
# (HTML h3 teglariga asoslangan). Ikkinchisi haqiqiy lessons.text_content
# ustida ishlaydi.

from __future__ import annotations
import re


def fixed_size_chunks(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    \"\"\"Eng oddiy strategiya: har chunk_size belgidan keyin kesadi, har
    keyingi chunk oldingisining oxirgi `overlap` belgisini qaytadan
    o'z ichiga oladi.\"\"\"
    if overlap >= chunk_size:
        raise ValueError("overlap chunk_size'dan kichik bo'lishi shart")

    chunks: list[str] = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap  # oldingi chunk oxiridan overlap miqdorida orqaga qaytish
    return [c for c in chunks if c]


def structure_aware_chunks(html: str) -> list[dict]:
    \"\"\"lessons.text_content kabi HTML matnni <h3> sarlavhalari bo'yicha
    bo'laklarga ajratadi — har bir bo'lim (sarlavha + undan keyingi matn)
    alohida chunk bo'ladi. Production'da BeautifulSoup ishlatilardi;
    bu yerda tushunarli bo'lishi uchun oddiy regex ishlatamiz.\"\"\"
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(sarlavhasiz)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        chunks.append({"heading": heading, "text": plain_text})
    return chunks


if __name__ == "__main__":
    # Haqiqiy lessons.text_content'dan olingan qisqartirilgan namuna —
    # o'zbekcha "CSS Flexbox" darsining shakli:
    sample_lesson_html = (
        "<h3>Flexbox nima</h3><p>Flexbox — elementlarni bir qatorda yoki "
        "ustunda tekis joylashtirish uchun CSS xususiyati.</p>"
        "<h3>flex-direction xususiyati</h3><p>flex-direction: column "
        "elementlarni tepadan pastga joylashtiradi.</p>"
        "<h3>justify-content va align-items</h3><p>Bu ikkalasi elementlarni "
        "gorizontal va vertikal tekislash uchun ishlatiladi.</p>"
    )

    print("--- Fixed-size chunking (overlap=20) ---")
    for i, c in enumerate(fixed_size_chunks(sample_lesson_html, chunk_size=80, overlap=20)):
        print(f"chunk {i}: {c[:70]!r}...")

    print("\\n--- Structure-aware chunking (h3 asosida) ---")
    for i, c in enumerate(structure_aware_chunks(sample_lesson_html)):
        print(f"chunk {i} [{c['heading']}]: {c['text']}")
"""

L2_CODE_RU = """
# Функции chunking: fixed-size (с overlap) и structure-aware (на основе
# HTML-тегов h3). Второй вариант работает на реальном lessons.text_content.

from __future__ import annotations
import re


def fixed_size_chunks(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    \"\"\"Простейшая стратегия: режет после каждых chunk_size символов,
    каждый следующий фрагмент повторно включает последние `overlap`
    символов предыдущего.\"\"\"
    if overlap >= chunk_size:
        raise ValueError("overlap должен быть меньше chunk_size")

    chunks: list[str] = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap  # возврат назад на overlap от конца предыдущего фрагмента
    return [c for c in chunks if c]


def structure_aware_chunks(html: str) -> list[dict]:
    \"\"\"Разбивает HTML-текст (как в lessons.text_content) по заголовкам
    <h3> — каждый раздел (заголовок + следующий за ним текст) становится
    отдельным фрагментом. В production использовался бы BeautifulSoup;
    здесь для наглядности используем простое регулярное выражение.\"\"\"
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(без заголовка)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        chunks.append({"heading": heading, "text": plain_text})
    return chunks


if __name__ == "__main__":
    # Сокращённый пример в форме реального lessons.text_content —
    # русская версия урока "CSS Flexbox":
    sample_lesson_html = (
        "<h3>Что такое Flexbox</h3><p>Flexbox — свойство CSS для ровного "
        "расположения элементов в строку или колонку.</p>"
        "<h3>Свойство flex-direction</h3><p>flex-direction: column "
        "располагает элементы сверху вниз.</p>"
        "<h3>justify-content и align-items</h3><p>Эти два свойства "
        "используются для горизонтального и вертикального выравнивания.</p>"
    )

    print("--- Fixed-size chunking (overlap=20) ---")
    for i, c in enumerate(fixed_size_chunks(sample_lesson_html, chunk_size=80, overlap=20)):
        print(f"chunk {i}: {c[:70]!r}...")

    print("\\n--- Structure-aware chunking (на основе h3) ---")
    for i, c in enumerate(structure_aware_chunks(sample_lesson_html)):
        print(f"chunk {i} [{c['heading']}]: {c['text']}")
"""

L2_TASK = {
    "task_title": "Haqiqiy dars matnini chunk'larga bo'ling",
    "task_title_ru": "Разбейте реальный текст урока на фрагменты",
    "task_description": (
        "Darsdagi `structure_aware_chunks` funksiyasini o'zingiz istagan "
        "kamida 3 ta <h3> bo'limi bor HTML matn ustida ishlating (o'zingiz "
        "yozgan yoki darsdagi namunani kengaytirgan holda), so'ngra "
        "`fixed_size_chunks` bilan solishtiring va qaysi biri ma'noni "
        "yaxshiroq saqlab qolganini izohlang."
    ),
    "task_description_ru": (
        "Примените функцию `structure_aware_chunks` из урока к HTML-тексту "
        "с не менее чем 3 разделами <h3> (написанному вами или "
        "расширенному примеру из урока), затем сравните с "
        "`fixed_size_chunks` и объясните, какой вариант лучше сохранил "
        "смысл."
    ),
    "task_requirements": (
        "1) Kamida 3 ta h3 bo'limi bo'lgan HTML ishlatilsin. 2) Ikkala "
        "chunking natijasi konsolga chiqarilsin. 3) Qaysi strategiya "
        "yaxshiroq ekani haqida kamida 2 jumlali izoh yozilsin (kod ichida "
        "komment sifatida yoki print orqali)."
    ),
    "task_requirements_ru": (
        "1) Должен использоваться HTML с не менее чем 3 разделами h3. "
        "2) Результаты обоих способов chunking должны быть выведены в "
        "консоль. 3) Должно быть написано пояснение (не менее 2 "
        "предложений) о том, какая стратегия оказалась лучше — комментарием "
        "в коде или через print."
    ),
    "task_technologies": "Python",
    "task_deadline_days": 4,
}

L2_SAMPLE = {
    "title": "Namuna: overlap'ning ta'sirini ko'rish",
    "description": (
        "Bir xil matnni overlap bilan va overlapsiz bo'lib, natijalar "
        "orasidagi farqni ko'rsatadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "overlap_demo.py",
            "language": "python",
            "code": (
                "def fixed_size_chunks(text: str, chunk_size: int, overlap: int) -> list[str]:\n"
                "    if overlap >= chunk_size:\n"
                "        raise ValueError(\"overlap chunk_size'dan kichik bo'lishi shart\")\n"
                "    chunks, start = [], 0\n"
                "    text = text.strip()\n"
                "    while start < len(text):\n"
                "        end = start + chunk_size\n"
                "        chunks.append(text[start:end])\n"
                "        start = end - overlap\n"
                "    return chunks\n\n\n"
                "text = (\n"
                "    \"Funksiya chaqirilganda argumentlar tartibda uzatiladi va natijada \"\n"
                "    \"funksiya ichidagi kod bajariladi va qiymat qaytariladi.\"\n"
                ")\n\n"
                "print('--- overlap YO\\'Q (overlap=0 emas, minimal 1) ---')\n"
                "for c in fixed_size_chunks(text, chunk_size=40, overlap=1):\n"
                "    print(repr(c))\n\n"
                "print('\\n--- overlap=15 bilan ---')\n"
                "for c in fixed_size_chunks(text, chunk_size=40, overlap=15):\n"
                "    print(repr(c))\n"
            ),
        },
    ],
}

L2_EXERCISES = [
    {
        "title": "Chunking nima uchun kerak",
        "title_ru": "Зачем нужен chunking",
        "description": "40,000 belgili darsni BITTA vektorga aylantirishning asosiy kamchiligi nima?",
        "description_ru": "Какой основной недостаток превращения урока из 40 000 символов в ОДИН вектор?",
        "exercise_type": "multiple_choice",
        "options": [
            "Vektor \"aralash\" o'rtacha ma'noni ifodalaydi va LLM'ga keraksiz ko'p matn yuboriladi",
            "Vektor hisoblanmaydi",
            "Model xato beradi",
            "Narx pasayadi",
        ],
        "options_ru": [
            "Вектор отражает 'смешанный' усреднённый смысл, и LLM отправляется слишком много лишнего текста",
            "Вектор не вычисляется",
            "Модель выдаёт ошибку",
            "Цена снижается",
        ],
        "correct_answers": "A",
        "hint": "\"Lost in the middle\" muammosini va aralash vektorni eslang.",
        "hint_ru": "Вспомните проблему 'lost in the middle' и смешанный вектор.",
        "explanation": "Butun hujjatni bitta vektorga aylantirish ma'noni suyultiradi va LLM'ga ortiqcha matn yuboradi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Overlap maqsadi",
        "title_ru": "Цель overlap",
        "description": "Chunk chegarasida gap ikkiga bo'linib, ma'no yo'qolishining oldini olish uchun ___ ishlatiladi.",
        "description_ru": "Чтобы предложение не разрывалось на границе фрагмента и не терялся смысл, используется ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "overlap",
        "hint": "Har keyingi chunk oldingisining bir qismini qaytadan o'z ichiga oladi.",
        "hint_ru": "Каждый следующий фрагмент повторно включает часть предыдущего.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Eng yaxshi chunking strategiyasi",
        "title_ru": "Лучшая стратегия chunking",
        "description": "lessons.text_content kabi <h3> sarlavhali HTML matn uchun odatda qaysi chunking strategiyasi eng yaxshi natija beradi?",
        "description_ru": "Для HTML-текста с заголовками <h3>, как в lessons.text_content, какая стратегия chunking обычно даёт лучший результат?",
        "exercise_type": "multiple_choice",
        "options": [
            "Structure-aware — h3 chegaralari bo'yicha bo'lish",
            "Fixed-size — har 10 belgida kesish",
            "Har bir harfni alohida chunk qilish",
            "Umuman bo'lmaslik",
        ],
        "options_ru": [
            "Structure-aware — разбиение по границам h3",
            "Fixed-size — резать каждые 10 символов",
            "Сделать каждую букву отдельным фрагментом",
            "Вообще не разбивать",
        ],
        "correct_answers": "A",
        "hint": "Muallif allaqachon mantiqiy bo'limlarga ajratib qo'yganini eslang.",
        "hint_ru": "Вспомните, что автор уже разделил материал на логические разделы.",
        "explanation": "Structure-aware chunking muallif tomonidan qo'yilgan mantiqiy chegaralardan foydalanadi, bu ko'pincha eng aniq natija beradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Chunk o'lchami savdolashuvi",
        "title_ru": "Компромисс размера фрагмента",
        "description": "Holatlarni oqibati bilan mos qo'ying (avval juda kichik chunk oqibati, keyin juda katta chunk oqibati)",
        "description_ru": "Сопоставьте ситуации с последствиями (сначала — последствие слишком маленького фрагмента, затем — слишком большого)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Kontekst yo'qoladi, \"buni\" nimani anglatishi noaniq bo'ladi",
            "LLM diqqati tarqaladi va narx oshadi",
        ],
        "drag_items_ru": [
            "Теряется контекст, неясно, что означает 'это'",
            "Внимание LLM рассеивается, цена растёт",
        ],
        "correct_order": [
            "Kontekst yo'qoladi, \"buni\" nimani anglatishi noaniq bo'ladi",
            "LLM diqqati tarqaladi va narx oshadi",
        ],
        "hint": "Darsdagi ikkita ro'yxat bandini eslang: juda kichik va juda katta.",
        "hint_ru": "Вспомните два пункта из урока: слишком маленький и слишком большой.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 3 — Vektor o'xshashligi matematikasi: cosine similarity
# ---------------------------------------------------------------------------

L3_TEXT = """
<h3>Ikki vektor qanchalik "yaqin": o'lchash kerak</h3>
<p>Oldingi darslarda "ma'nosi yaqin matnlarning vektorlari fazoda yaqin
joylashadi" dedik — lekin "yaqin"ni SON bilan qanday ifodalaymiz? Bu darsda
RAG qidiruvining matematik yuragi — <strong>cosine similarity</strong>
(kosinus o'xshashligi)ni ko'ramiz.</p>

<h3>Dot product (nuqta ko'paytma) — asos</h3>
<p>Ikki vektorning dot product'i — mos elementlarni ko'paytirib, yig'indisini
olish: <code>a · b = a[0]*b[0] + a[1]*b[1] + ... + a[n]*b[n]</code>. Bu
o'z-o'zicha "o'xshashlik" emas — chunki uzun vektor (masalan uzunligi 100
bo'lgan matn) qisqa vektorga (10 so'zlik matn) qaraganda tabiiy ravishda
kattaroq dot product'ga ega bo'lishi mumkin, garchi ma'no jihatidan farq
qilmasa ham.</p>

<h3>Cosine similarity: yo'nalishni solishtirish, uzunlikni emas</h3>
<p>Cosine similarity buni tuzatadi — u ikki vektor orasidagi BURCHAKNI
o'lchaydi, ularning UZUNLIGINI emas:</p>
<pre><code>cosine_similarity(a, b) = (a · b) / (|a| * |b|)</code></pre>
<p>Bu yerda <code>|a|</code> — vektorning uzunligi (magnitude), ya'ni
<code>sqrt(a[0]^2 + a[1]^2 + ... + a[n]^2)</code>. Natija har doim -1 dan 1
gacha oraliqda:</p>
<ul>
<li><strong>1</strong> — vektorlar bir xil yo'nalishda (ma'no juda yaqin)</li>
<li><strong>0</strong> — vektorlar bir-biriga perpendikulyar (bog'liq emas)</li>
<li><strong>-1</strong> — vektorlar qarama-qarshi yo'nalishda (kamdan-kam
uchraydi matn embedding'larida, chunki ko'p modellar manfiy bo'lmagan
qiymatlarga moyil)</li>
</ul>
<p>Amaliyotda embedding qidiruvida deyarli har doim 0 bilan 1 orasidagi
qiymatlar ko'riladi — 1'ga qancha yaqin bo'lsa, ma'no shuncha yaqin.</p>

<h3>Qo'lda hisoblash: kichik misol</h3>
<p>Ikki oddiy 2-o'lchamli vektor bilan qo'lda hisoblab ko'ramiz:
<code>a = [1, 2]</code>, <code>b = [2, 4]</code> (b — a'ning aynan 2 baravari,
demak bir xil yo'nalishda). <code>a · b = 1*2 + 2*4 = 10</code>.
<code>|a| = sqrt(1+4) = sqrt(5) ≈ 2.236</code>. <code>|b| = sqrt(4+16) =
sqrt(20) ≈ 4.472</code>. <code>cosine = 10 / (2.236 * 4.472) ≈ 10 / 10 = 1.0</code>
— to'g'ri, chunki b aynan a'ning yo'nalishida (faqat 2 marta uzunroq),
demak ular "bir xil ma'no"ni ifodalaydi (masshtabdan qat'iy nazar).</p>

<h3>Brute-force qidiruv: eng oddiy, lekin sekin</h3>
<p>Eng oddiy qidiruv usuli — <strong>brute-force</strong>: so'rov vektorini
BAZADAGI HAR BIR hujjat vektori bilan solishtirib, cosine similarity'ni
hisoblash, so'ngra eng yuqori natijali top-K tasini olish. Bu 100-1000 ta
hujjat uchun juda tez ishlaydi (mikrosekundlar), lekin million(lar)ga yetganda
har bir so'rov uchun millionlab solishtirish kerak bo'lib qoladi — sekinlashadi.</p>

<h3>Indekslangan qidiruv: nega kerak bo'ladi</h3>
<p>Katta hajmda (masalan millionlab vektor) <strong>approximate nearest
neighbor (ANN)</strong> indekslar ishlatiladi — ular HAR BIR vektorni emas,
faqat "eng ehtimoliy" nomzodlarni tekshiradi, shu orqali tezlikni oshiradi,
aniqlikni ozgina (odatda sezilmas darajada) qurbon qilib. pgvector'ning
<code>ivfflat</code>/<code>hnsw</code> indekslari — aynan shunday ANN
mexanizmlari (5-darsda ko'ramiz). Bu kursning miqyosida (yuzlab-minglab
hujjat) brute-force ham to'liq amaliy yechim — indekslash faqat katta
miqyosda zarur bo'ladi.</p>

<h3>Geometrik intuitsiya</h3>
<pre class="mermaid">
flowchart LR
  ORIGIN(("boshlanish nuqtasi"))
  ORIGIN -->|"vektor A
'Python funksiyasi'"| A["A"]
  ORIGIN -->|"vektor B
'def bilan funksiya'
kichik burchak (θ≈0)"| B["B"]
  ORIGIN -.->|"vektor C
'pitsa retsepti'
katta burchak (θ≈90)"| C["C"]
</pre>
<p>A va B orasidagi burchak KICHIK — cosine similarity 1'ga yaqin (ma'no
yaqin). A va C orasidagi burchak KATTA (deyarli to'g'ri burchak) — cosine
similarity 0'ga yaqin (ma'no bog'liq emas). Qidiruv algoritmi aynan shu
burchaklarni hisoblab, ENG KICHIK burchakli (demak eng o'xshash) hujjatlarni
tanlaydi.</p>

<h3>Cosine vs Euclidean masofa — qaysi birini tanlash</h3>
<p>Boshqa keng tarqalgan o'lchov — <strong>Euclidean masofa</strong> (ikki
nuqta orasidagi "to'g'ridan-to'g'ri chiziq" masofasi). Farqi: Euclidean
vektorning UZUNLIGINI ham hisobga oladi, cosine esa faqat YO'NALISHNI. Matn
embedding'lari uchun odatda cosine afzal ko'riladi, chunki ikki matnning
"ma'nosi" ko'pincha vektor uzunligiga emas, yo'nalishiga bog'liq bo'ladi
(qisqa va uzun jumla bir xil ma'noni ifodalashi mumkin). Shuning uchun
pgvector'da <code>&lt;=&gt;</code> operatori (cosine masofasi) matn qidiruvda
eng ko'p ishlatiladigan operator — buni 5-darsda haqiqiy SQL so'rovida
ko'ramiz.</p>
"""

L3_TEXT_RU = """
<h3>Насколько "близки" два вектора: нужно измерить</h3>
<p>В прошлых уроках мы сказали "векторы текстов с близким смыслом
располагаются в пространстве близко" — но как выразить "близость" ЧИСЛОМ?
В этом уроке — математическое сердце поиска RAG:
<strong>cosine similarity</strong> (косинусное сходство).</p>

<h3>Dot product (скалярное произведение) — основа</h3>
<p>Скалярное произведение двух векторов — это сумма произведений
соответствующих элементов: <code>a · b = a[0]*b[0] + a[1]*b[1] + ... +
a[n]*b[n]</code>. Само по себе это НЕ "сходство" — потому что длинный
вектор (например, текст длиной 100) может естественно иметь большее dot
product, чем короткий вектор (текст из 10 слов), даже если по смыслу они
не отличаются.</p>

<h3>Cosine similarity: сравнение направления, а не длины</h3>
<p>Косинусное сходство исправляет это — оно измеряет УГОЛ между двумя
векторами, а не их ДЛИНУ:</p>
<pre><code>cosine_similarity(a, b) = (a · b) / (|a| * |b|)</code></pre>
<p>Здесь <code>|a|</code> — длина вектора (magnitude), то есть
<code>sqrt(a[0]^2 + a[1]^2 + ... + a[n]^2)</code>. Результат всегда лежит в
диапазоне от -1 до 1:</p>
<ul>
<li><strong>1</strong> — векторы в одном направлении (смысл очень близкий)</li>
<li><strong>0</strong> — векторы перпендикулярны (не связаны)</li>
<li><strong>-1</strong> — векторы в противоположных направлениях (редко
встречается в текстовых эмбеддингах, так как многие модели склонны к
неотрицательным значениям)</li>
</ul>
<p>На практике в поиске по эмбеддингам почти всегда видны значения между 0
и 1 — чем ближе к 1, тем ближе смысл.</p>

<h3>Ручной расчёт: небольшой пример</h3>
<p>Посчитаем вручную на двух простых 2-мерных векторах:
<code>a = [1, 2]</code>, <code>b = [2, 4]</code> (b — ровно в 2 раза больше
a, значит в том же направлении). <code>a · b = 1*2 + 2*4 = 10</code>.
<code>|a| = sqrt(1+4) = sqrt(5) ≈ 2.236</code>. <code>|b| = sqrt(4+16) =
sqrt(20) ≈ 4.472</code>. <code>cosine = 10 / (2.236 * 4.472) ≈ 10 / 10 =
1.0</code> — верно, потому что b находится точно в направлении a (только в
2 раза длиннее), значит они выражают "один и тот же смысл" (независимо от
масштаба).</p>

<h3>Brute-force поиск: самый простой, но медленный</h3>
<p>Самый простой способ поиска — <strong>brute-force</strong>: сравнить
вектор запроса с ВЕКТОРОМ КАЖДОГО документа в базе, вычислить cosine
similarity, затем взять top-K с наивысшим результатом. Это работает очень
быстро для 100-1000 документов (микросекунды), но при достижении
миллиона(ов) на каждый запрос требуются миллионы сравнений — становится
медленно.</p>

<h3>Индексированный поиск: зачем он понадобится</h3>
<p>При больших объёмах (например, миллионы векторов) используются индексы
<strong>approximate nearest neighbor (ANN)</strong> — они проверяют не
КАЖДЫЙ вектор, а только "наиболее вероятных" кандидатов, тем самым повышая
скорость ценой небольшой (обычно незаметной) потери точности. Индексы
pgvector <code>ivfflat</code>/<code>hnsw</code> — именно такие механизмы ANN
(увидим в уроке 5). В масштабе этого курса (сотни-тысячи документов)
brute-force тоже полностью практичное решение — индексирование нужно
только при большом масштабе.</p>

<h3>Геометрическая интуиция</h3>
<pre class="mermaid">
flowchart LR
  ORIGIN(("точка начала"))
  ORIGIN -->|"вектор A
'функция Python'"| A["A"]
  ORIGIN -->|"вектор B
'функция с def'
малый угол (θ≈0)"| B["B"]
  ORIGIN -.->|"вектор C
'рецепт пиццы'
большой угол (θ≈90)"| C["C"]
</pre>
<p>Угол между A и B МАЛЕНЬКИЙ — cosine similarity близко к 1 (смысл
близкий). Угол между A и C БОЛЬШОЙ (почти прямой) — cosine similarity
близко к 0 (смысл не связан). Алгоритм поиска именно вычисляет эти углы и
выбирает документы с САМЫМ МАЛЕНЬКИМ углом (то есть наиболее похожие).</p>

<h3>Cosine против Euclidean расстояния — что выбрать</h3>
<p>Другая распространённая метрика — <strong>Euclidean расстояние</strong>
(расстояние "по прямой" между двумя точками). Отличие: Euclidean учитывает
и ДЛИНУ вектора, а cosine — только НАПРАВЛЕНИЕ. Для текстовых эмбеддингов
обычно предпочитают cosine, потому что "смысл" двух текстов чаще зависит от
направления вектора, а не от его длины (короткое и длинное предложение
могут выражать один и тот же смысл). Поэтому оператор <code>&lt;=&gt;</code>
в pgvector (косинусное расстояние) — самый используемый оператор для
текстового поиска — увидим его в реальном SQL-запросе в уроке 5.</p>
"""

L3_CODE = """
# Cosine similarity: avval qo'lda (faqat math moduli bilan), keyin
# numpy bilan tezroq/qisqaroq shaklda. Ikkalasi ham BIR XIL natijani
# berishi kerak — bu haqiqiy o'zaro tekshiruv (sanity check).

from __future__ import annotations
import math


def dot_product(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def magnitude(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    \"\"\"Qo'lda, faqat asosiy Python bilan hisoblangan cosine similarity —
    -1..1 oralig'ida, 1 — bir xil yo'nalish (ma'no juda yaqin).\"\"\"
    mag_a, mag_b = magnitude(a), magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0  # nol vektor bilan solishtirish ma'nosiz — 0 qaytaramiz
    return dot_product(a, b) / (mag_a * mag_b)


def top_k_similar(query_vector: list[float], candidates: dict[str, list[float]], k: int = 3) -> list[tuple[str, float]]:
    \"\"\"Brute-force qidiruv: HAR BIR nomzod bilan solishtiradi, eng
    yuqori cosine similarity'ga ega top-k tasini qaytaradi.\"\"\"
    scored = [(name, cosine_similarity(query_vector, vec)) for name, vec in candidates.items()]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    # Qo'lda tekshirilgan misol (darsdagi hisob-kitobga mos):
    a = [1.0, 2.0]
    b = [2.0, 4.0]  # b = 2*a -> bir xil yo'nalish -> cosine ≈ 1.0
    print(f"cosine_similarity(a, b) = {cosine_similarity(a, b):.4f}  (kutilgan: ~1.0)")

    # numpy bilan bir xil natija — production kodda odatda shu ishlatiladi:
    import numpy as np
    a_np, b_np = np.array(a), np.array(b)
    cosine_np = np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))
    print(f"numpy bilan:              {cosine_np:.4f}  (bir xil natija bo'lishi kerak)")

    # Brute-force qidiruv namunasi:
    candidates = {
        "Python funksiyalari haqida dars": [0.9, 0.1, 0.3],
        "CSS Flexbox haqida dars": [0.1, 0.9, 0.2],
        "Pitsa retsepti (mos emas)": [0.05, 0.02, 0.99],
    }
    query = [0.85, 0.15, 0.25]  # "funksiya qanday yoziladi" so'roviga o'xshash vektor
    print("\\nTop-2 natija:")
    for name, score in top_k_similar(query, candidates, k=2):
        print(f"  {score:.4f}  {name}")
"""

L3_CODE_RU = """
# Cosine similarity: сначала вручную (только модулем math), затем с
# numpy быстрее/короче. Оба варианта должны давать ОДИНАКОВЫЙ
# результат — это настоящая взаимная проверка (sanity check).

from __future__ import annotations
import math


def dot_product(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def magnitude(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    \"\"\"Косинусное сходство, вычисленное вручную, только базовым
    Python — в диапазоне -1..1, 1 — одно направление (смысл очень
    близкий).\"\"\"
    mag_a, mag_b = magnitude(a), magnitude(b)
    if mag_a == 0 or mag_b == 0:
        return 0.0  # сравнение с нулевым вектором бессмысленно — возвращаем 0
    return dot_product(a, b) / (mag_a * mag_b)


def top_k_similar(query_vector: list[float], candidates: dict[str, list[float]], k: int = 3) -> list[tuple[str, float]]:
    \"\"\"Brute-force поиск: сравнивает с КАЖДЫМ кандидатом, возвращает
    top-k с наивысшим cosine similarity.\"\"\"
    scored = [(name, cosine_similarity(query_vector, vec)) for name, vec in candidates.items()]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    # Пример, проверенный вручную (соответствует расчёту из урока):
    a = [1.0, 2.0]
    b = [2.0, 4.0]  # b = 2*a -> то же направление -> cosine ≈ 1.0
    print(f"cosine_similarity(a, b) = {cosine_similarity(a, b):.4f}  (ожидается: ~1.0)")

    # Тот же результат с numpy — в production обычно используется именно это:
    import numpy as np
    a_np, b_np = np.array(a), np.array(b)
    cosine_np = np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))
    print(f"с numpy:                  {cosine_np:.4f}  (должен быть тот же результат)")

    # Пример brute-force поиска:
    candidates = {
        "Урок про функции Python": [0.9, 0.1, 0.3],
        "Урок про CSS Flexbox": [0.1, 0.9, 0.2],
        "Рецепт пиццы (не подходит)": [0.05, 0.02, 0.99],
    }
    query = [0.85, 0.15, 0.25]  # вектор, похожий на запрос "как пишется функция"
    print("\\nТоп-2 результата:")
    for name, score in top_k_similar(query, candidates, k=2):
        print(f"  {score:.4f}  {name}")
"""

L3_TASK = {
    "task_title": "Qo'lda cosine similarity hisoblang va tekshiring",
    "task_title_ru": "Вычислите cosine similarity вручную и проверьте",
    "task_description": (
        "Darsdagi `cosine_similarity` funksiyasidan foydalanib, kamida 3 "
        "juft vektor bilan sinang: bittasi bir xil yo'nalishda (natija "
        "~1.0 bo'lishi kutiladi), bittasi perpendikulyar (natija ~0.0), "
        "bittasi o'zingiz tanlagan. Har bir natijani numpy natijasi bilan "
        "solishtirib tasdiqlang."
    ),
    "task_description_ru": (
        "Используя функцию `cosine_similarity` из урока, протестируйте "
        "минимум на 3 парах векторов: одна пара — в одном направлении "
        "(ожидается результат ~1.0), одна — перпендикулярна (~0.0), одна "
        "— на ваш выбор. Подтвердите каждый результат сравнением с "
        "результатом numpy."
    ),
    "task_requirements": (
        "1) Kamida 3 juft vektor sinalsin. 2) Har bir juftlik uchun qo'lda "
        "yozilgan va numpy natijalari bir-biriga mos kelishi (farq 0.0001 "
        "dan kichik) tekshirilsin (assert yoki print orqali). 3) Natijalar "
        "izohlansin (nima uchun bunday natija chiqdi)."
    ),
    "task_requirements_ru": (
        "1) Должно быть протестировано минимум 3 пары векторов. 2) Для "
        "каждой пары должно быть проверено (через assert или print), что "
        "результаты ручной реализации и numpy совпадают (разница меньше "
        "0.0001). 3) Результаты должны быть прокомментированы (почему "
        "получился именно такой результат)."
    ),
    "task_technologies": "Python, numpy",
    "task_deadline_days": 4,
}

L3_SAMPLE = {
    "title": "Namuna: brute-force top-K qidiruv",
    "description": (
        "Kichik \"hujjatlar bazasi\" ustida cosine similarity orqali "
        "eng mos top-2 natijani topadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "brute_force_search.py",
            "language": "python",
            "code": (
                "import math\n\n\n"
                "def cosine_similarity(a: list[float], b: list[float]) -> float:\n"
                "    dot = sum(x * y for x, y in zip(a, b))\n"
                "    mag_a = math.sqrt(sum(x * x for x in a))\n"
                "    mag_b = math.sqrt(sum(x * x for x in b))\n"
                "    if mag_a == 0 or mag_b == 0:\n"
                "        return 0.0\n"
                "    return dot / (mag_a * mag_b)\n\n\n"
                "documents = {\n"
                "    \"1-dars: Python o'zgaruvchilari\": [0.9, 0.2, 0.1],\n"
                "    \"2-dars: Python funksiyalari\": [0.85, 0.25, 0.05],\n"
                "    \"3-dars: CSS Grid\": [0.1, 0.9, 0.3],\n"
                "    \"4-dars: SQL JOIN\": [0.2, 0.1, 0.95],\n"
                "}\n\n"
                "query_vector = [0.88, 0.22, 0.08]  # \"funksiya qanday e'lon qilinadi\"\n\n"
                "scored = sorted(\n"
                "    ((name, cosine_similarity(query_vector, vec)) for name, vec in documents.items()),\n"
                "    key=lambda pair: pair[1],\n"
                "    reverse=True,\n"
                ")\n\n"
                "print(\"Top-2 eng mos dars:\")\n"
                "for name, score in scored[:2]:\n"
                "    print(f\"  {score:.4f}  {name}\")\n"
            ),
        },
    ],
}

L3_EXERCISES = [
    {
        "title": "Cosine similarity oralig'i",
        "title_ru": "Диапазон cosine similarity",
        "description": "Cosine similarity qaysi son oralig'ida natija beradi?",
        "description_ru": "В каком числовом диапазоне даёт результат cosine similarity?",
        "exercise_type": "multiple_choice",
        "options": ["-1 dan 1 gacha", "0 dan 100 gacha", "0 dan 1 gacha (har doim musbat)", "Cheksiz"],
        "options_ru": ["От -1 до 1", "От 0 до 100", "От 0 до 1 (всегда положительный)", "Без ограничений"],
        "correct_answers": "A",
        "hint": "1 — bir xil yo'nalish, -1 — qarama-qarshi.",
        "hint_ru": "1 — одно направление, -1 — противоположное.",
        "explanation": "Cosine similarity matematik ta'rifi bo'yicha -1 dan 1 gacha bo'lishi mumkin, amaliyotda matn embedding'larida odatda 0..1.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Dot product yetarli emas",
        "title_ru": "Dot product недостаточно",
        "description": "Cosine similarity formulasi: (a · b) / (|a| * |b|). Bu yerda |a| va |b| vektorning ___ deb ataladi.",
        "description_ru": "Формула cosine similarity: (a · b) / (|a| * |b|). Здесь |a| и |b| называются ___ вектора.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "magnitude",
        "hint": "Formuladagi maxrajni eslang: |a| * |b|",
        "hint_ru": "Вспомните знаменатель формулы: |a| * |b|",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Brute-force qidiruv cheklovi",
        "title_ru": "Ограничение brute-force поиска",
        "description": "Nima uchun brute-force qidiruv millionlab hujjat bo'lganda muammoli bo'lib qoladi?",
        "description_ru": "Почему brute-force поиск становится проблематичным при миллионах документов?",
        "exercise_type": "multiple_choice",
        "options": [
            "Har bir so'rov uchun HAR BIR hujjat bilan solishtirish kerak bo'lib, sekinlashadi",
            "Cosine similarity formulasi ishlamay qoladi",
            "Vektorlar noto'g'ri hisoblanadi",
            "Xotira umuman ishlatilmaydi",
        ],
        "options_ru": [
            "На каждый запрос нужно сравнение с КАЖДЫМ документом, что замедляет работу",
            "Формула cosine similarity перестаёт работать",
            "Векторы вычисляются неверно",
            "Память вообще не используется",
        ],
        "correct_answers": "A",
        "hint": "Solishtirishlar soni hujjatlar soniga chiziqli bog'liq.",
        "hint_ru": "Количество сравнений линейно зависит от числа документов.",
        "explanation": "Brute-force qidiruv O(n) murakkablikka ega — hujjatlar soni oshgani sari sekinlashadi, shuning uchun katta miqyosda ANN indekslar kerak bo'ladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Qidiruv jarayoni bosqichlari",
        "title_ru": "Этапы процесса поиска",
        "description": "Brute-force qidiruv bosqichlarini to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы brute-force поиска в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "So'rovni vektorlashtirish (embed)",
            "Har bir hujjat vektori bilan cosine similarity hisoblash",
            "Natijalarni ballga qarab saralash",
            "Eng yuqori ballli top-K tasini tanlash",
        ],
        "drag_items_ru": [
            "Векторизация запроса (embed)",
            "Вычисление cosine similarity с каждым вектором документа",
            "Сортировка результатов по баллу",
            "Выбор top-K с наивысшим баллом",
        ],
        "correct_order": [
            "So'rovni vektorlashtirish (embed)",
            "Har bir hujjat vektori bilan cosine similarity hisoblash",
            "Natijalarni ballga qarab saralash",
            "Eng yuqori ballli top-K tasini tanlash",
        ],
        "hint": "Avval so'rovni ham vektorga aylantirish kerakligini unutmang.",
        "hint_ru": "Не забывайте, что запрос тоже сначала превращается в вектор.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 4 — Vektor bazalari taqqoslash: pgvector, Chroma, Pinecone
# ---------------------------------------------------------------------------

L4_TEXT = """
<h3>Vektorlarni QAYERDA saqlaymiz</h3>
<p>Oldingi darslarda embedding va cosine similarity'ni ko'rdik — endi savol:
minglab (yoki millionlab) vektorni qayerda va qanday saqlash kerak, shunda
qidiruv tez va ishonchli ishlaydi? Uchta keng tarqalgan variantni ko'ramiz:
<strong>pgvector</strong> (Postgres kengaytmasi), <strong>Chroma</strong>
(mahalliy, fayl-asosli vektor bazasi) va <strong>Pinecone</strong> (to'liq
boshqariladigan, bulutli vektor bazasi). Bu yerda aniq narx yoki rate limit
raqamlarini keltirmaymiz — ular vaqt o'tishi bilan o'zgaradi; har doim
provider'ning rasmiy dashboard/hujjatidan joriy shartlarni tekshiring.</p>

<h3>pgvector — Postgres'ning o'zida vektor</h3>
<p>pgvector — PostgreSQL uchun kengaytma (extension) bo'lib, yangi ma'lumot
turi (<code>vector</code>) va maxsus indekslarni (<code>ivfflat</code>,
<code>hnsw</code>) qo'shadi. <strong>Eng katta afzalligi</strong>: agar
loyihangiz allaqachon Postgres ishlatsa (bu platforma kabi), vektorlarni
ALOHIDA bazaga ko'chirish shart emas — bir xil jadvalda oddiy ustunlar
(masalan <code>title</code>, <code>course_id</code>) bilan bir qatorda
<code>embedding vector(384)</code> ustuni ham bo'lishi mumkin, va bitta SQL
so'rovida ham oddiy filtrlash (<code>WHERE course_id = 5</code>), ham vektor
qidiruvni birlashtirish mumkin. Kamchiligi: juda katta miqyosda (o'nlab
millionlab vektor) maxsus vektor bazalari ko'proq optimallashtirilgan
bo'lishi mumkin.</p>

<h3>Chroma — mahalliy, sodda, bepul</h3>
<p>Chroma — Python-birinchi, ochiq manba (open-source) vektor bazasi bo'lib,
alohida server o'rnatmasdan ham (fayl tizimida saqlanadigan "embedded" rejim)
ishlaydi. Kichik loyihalar, prototip va o'quv maqsadlari uchun juda qulay —
o'rnatish bir necha qatorli kod. Kamchiligi: production'da ko'p foydalanuvchi
bir vaqtda yozish/o'qishi kerak bo'lgan katta tizimlar uchun Postgres/
pgvector kabi to'liq DBMS xususiyatlari (tranzaksiyalar, backup, kirish
nazorati) yetishmasligi mumkin.</p>

<h3>Pinecone — to'liq boshqariladigan bulutli xizmat</h3>
<p>Pinecone — faqat vektor qidiruv uchun mo'ljallangan, to'liq boshqariladigan
(managed) bulutli xizmat: server o'rnatish, indeks sozlash, masshtablashni
o'zi bajaradi. Bepul tarif mavjud (aniq chegaralarni Pinecone'ning rasmiy
saytida tekshiring). Afzalligi: operatsion tashvishlarsiz juda katta miqyosda
ishlaydi. Kamchiligi: alohida tashqi xizmat — internet aloqasi, alohida API
kaliti, va ma'lumotlaringiz o'z serveringizdan tashqarida saqlanadi (ba'zi
loyihalar uchun bu muhim cheklov bo'lishi mumkin).</p>

<h3>Taqqoslash jadvali</h3>
<table>
<tr><th>Xususiyat</th><th>pgvector</th><th>Chroma</th><th>Pinecone</th></tr>
<tr><td>Qayerda ishlaydi</td><td>Sizning Postgres serveringizda</td><td>Mahalliy fayl/server</td><td>Bulutda (managed)</td></tr>
<tr><td>Alohida infrastruktura kerakmi</td><td>Yo'q (Postgres bor bo'lsa)</td><td>Yo'q</td><td>Ha (tashqi xizmat)</td></tr>
<tr><td>SQL bilan birlashish</td><td>To'liq (bir xil so'rovda)</td><td>Yo'q</td><td>Yo'q</td></tr>
<tr><td>Eng mos holat</td><td>Postgres allaqachon bor loyihalar</td><td>Prototip, kichik loyiha, o'quv</td><td>Katta miqyosli, boshqaruvsiz production</td></tr>
</table>

<h3>Qaror qabul qilish uchun savollar</h3>
<p>Amaliyotda tanlov ko'pincha shu savollarga javob berish orqali qilinadi:
Loyihada allaqachon Postgres bormi (bo'lsa — pgvector kuchli nomzod)?
Prototip yoki kichik jamoa loyihasimi, tezda ishga tushirish kerakmi (bo'lsa
— Chroma qulay)? Vektorlar soni o'nlab millionlarga yetadimi va operatsion
yukni tashqi xizmatga topshirish istalgan holatmi (bo'lsa — Pinecone kabi
managed xizmat)? Bu savollarga aniq "har doim to'g'ri" javob yo'q — javob
loyihaning o'ziga bog'liq, va vaqt o'tishi bilan (masalan loyiha kichik
prototipdan katta production'ga o'sganda) tanlov o'zgarishi ham normal.</p>

<h3>Bu kurs uchun tanlov</h3>
<p>Ushbu platforma allaqachon PostgreSQL ishlatadi (barcha jadvallar —
<code>courses</code>, <code>lessons</code>, <code>students</code> — shu
bazada). Shuning uchun keyingi darslarda (5 va 6) biz <strong>pgvector</strong>
yo'lini tanlaymiz — infratuzilmani ikkilantirmasdan, mavjud bazaga tabiiy
kengaytma sifatida. Bu "eng yaxshi" universal tanlov degani emas — har bir
loyiha o'z sharoitiga qarab boshqa variantni tanlashi mumkin; bu yerdagi
tanlov aynan SHU platformaning arxitekturasiga mos kelgani uchun.</p>
"""

L4_TEXT_RU = """
<h3>ГДЕ хранить векторы</h3>
<p>В прошлых уроках мы разобрали эмбеддинги и cosine similarity — теперь
вопрос: где и как хранить тысячи (или миллионы) векторов, чтобы поиск
работал быстро и надёжно? Рассмотрим три распространённых варианта:
<strong>pgvector</strong> (расширение Postgres), <strong>Chroma</strong>
(локальная, файловая векторная база) и <strong>Pinecone</strong> (полностью
управляемая облачная векторная база). Здесь мы не приводим точные цифры цен
или rate limit — они меняются со временем; всегда проверяйте актуальные
условия в официальном дашборде/документации провайдера.</p>

<h3>pgvector — вектор прямо в Postgres</h3>
<p>pgvector — расширение (extension) для PostgreSQL, добавляющее новый тип
данных (<code>vector</code>) и специальные индексы (<code>ivfflat</code>,
<code>hnsw</code>). <strong>Главное преимущество</strong>: если ваш проект
уже использует Postgres (как эта платформа), не нужно переносить векторы в
ОТДЕЛЬНУЮ базу — в той же таблице рядом с обычными столбцами (например
<code>title</code>, <code>course_id</code>) может быть столбец
<code>embedding vector(384)</code>, и в одном SQL-запросе можно объединить
и обычную фильтрацию (<code>WHERE course_id = 5</code>), и векторный поиск.
Недостаток: при очень большом масштабе (десятки миллионов векторов)
специализированные векторные базы могут быть более оптимизированы.</p>

<h3>Chroma — локальная, простая, бесплатная</h3>
<p>Chroma — Python-first, open-source векторная база, работающая даже без
установки отдельного сервера ("embedded" режим с хранением в файловой
системе). Очень удобна для небольших проектов, прототипов и учебных целей —
установка занимает несколько строк кода. Недостаток: в production для
больших систем с многопользовательской одновременной записью/чтением может
не хватать полноценных возможностей СУБД (транзакции, backup, контроль
доступа), которые есть у Postgres/pgvector.</p>

<h3>Pinecone — полностью управляемый облачный сервис</h3>
<p>Pinecone — облачный сервис, полностью управляемый (managed) и
предназначенный только для векторного поиска: установку сервера, настройку
индекса, масштабирование он делает сам. Есть бесплатный тариф (точные
лимиты проверяйте на официальном сайте Pinecone). Преимущество: работает в
очень большом масштабе без операционных забот. Недостаток: отдельный
внешний сервис — нужен интернет, отдельный API-ключ, и ваши данные хранятся
вне вашего собственного сервера (для некоторых проектов это может быть
важным ограничением).</p>

<h3>Сравнительная таблица</h3>
<table>
<tr><th>Характеристика</th><th>pgvector</th><th>Chroma</th><th>Pinecone</th></tr>
<tr><td>Где работает</td><td>На вашем сервере Postgres</td><td>Локальный файл/сервер</td><td>В облаке (managed)</td></tr>
<tr><td>Нужна отдельная инфраструктура</td><td>Нет (если Postgres уже есть)</td><td>Нет</td><td>Да (внешний сервис)</td></tr>
<tr><td>Объединение с SQL</td><td>Полное (в одном запросе)</td><td>Нет</td><td>Нет</td></tr>
<tr><td>Лучше всего подходит</td><td>Проекты, где уже есть Postgres</td><td>Прототип, малый проект, обучение</td><td>Крупный масштаб, production без операционных забот</td></tr>
</table>

<h3>Вопросы для принятия решения</h3>
<p>На практике выбор часто делается через ответы на такие вопросы: уже есть
ли в проекте Postgres (если да — pgvector сильный кандидат)? Это прототип
или небольшой командный проект, нужно быстро запустить (тогда удобна
Chroma)? Достигает ли число векторов десятков миллионов, и хочется ли
передать операционную нагрузку внешнему сервису (тогда managed-сервис вроде
Pinecone)? На эти вопросы нет единственно "всегда верного" ответа — ответ
зависит от самого проекта, и нормально, что выбор меняется со временем
(например, когда проект вырастает из маленького прототипа в крупный
production).</p>

<h3>Выбор для этого курса</h3>
<p>Эта платформа уже использует PostgreSQL (все таблицы — <code>courses</code>,
<code>lessons</code>, <code>students</code> — в этой же базе). Поэтому в
следующих уроках (5 и 6) мы выбираем путь <strong>pgvector</strong> — не
дублируя инфраструктуру, а как естественное расширение существующей базы.
Это не значит, что pgvector — "лучший" универсальный выбор — каждый проект
может выбрать другой вариант в зависимости от своих условий; выбор здесь
сделан именно потому, что он подходит архитектуре ИМЕННО этой платформы.</p>
"""

L4_CODE = """
# Uchala variantning ham ulanish/qidiruv kodi qanday ko'rinishini
# solishtirish — konseptual, ishga tushirilmaydi (API kalitlar yo'q),
# lekin har birining haqiqiy Python client kutubxonasi shaklini aks ettiradi.

# ---------------------------------------------------------------------------
# 1) pgvector — oddiy SQL orqali, mavjud SQLAlchemy sessiyasidan foydalanib
# ---------------------------------------------------------------------------

PGVECTOR_EXAMPLE = '''
from sqlalchemy import text

async def search_pgvector(db, query_vector: list[float], k: int = 3):
    rows = await db.execute(
        text(
            "SELECT id, title, embedding <=> :qv AS distance "
            "FROM lesson_embeddings "
            "ORDER BY embedding <=> :qv LIMIT :k"
        ),
        {"qv": str(query_vector), "k": k},
    )
    return rows.fetchall()
'''

# ---------------------------------------------------------------------------
# 2) Chroma — o'z Python client kutubxonasi orqali (chromadb paketi)
# ---------------------------------------------------------------------------

CHROMA_EXAMPLE = '''
import chromadb

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("lessons")

collection.add(
    ids=["lesson_7", "lesson_11"],
    embeddings=[[0.1, 0.2, 0.3], [0.4, 0.1, 0.2]],
    documents=["Class ID haqida dars", "Display Flex haqida dars"],
)

results = collection.query(query_embeddings=[[0.12, 0.19, 0.28]], n_results=3)
'''

# ---------------------------------------------------------------------------
# 3) Pinecone — tashqi bulutli xizmat, o'z Python SDK'si orqali
# ---------------------------------------------------------------------------

PINECONE_EXAMPLE = '''
from pinecone import Pinecone

pc = Pinecone(api_key="...")
index = pc.Index("lessons-index")

index.upsert(vectors=[
    {"id": "lesson_7", "values": [0.1, 0.2, 0.3]},
    {"id": "lesson_11", "values": [0.4, 0.1, 0.2]},
])

matches = index.query(vector=[0.12, 0.19, 0.28], top_k=3)
'''


def print_comparison() -> None:
    print("=== pgvector (SQL, mavjud Postgres bazasida) ===")
    print(PGVECTOR_EXAMPLE)
    print("=== Chroma (mahalliy, chromadb paketi) ===")
    print(CHROMA_EXAMPLE)
    print("=== Pinecone (bulutli, tashqi xizmat) ===")
    print(PINECONE_EXAMPLE)
    print(
        "DIQQAT: uchala kod ham konseptual — API kalitlari/paketlar "
        "o'rnatilmagan, shuning uchun ishga tushirilmaydi. Maqsad — "
        "SHAKLNI solishtirish: pgvector oddiy SQL, Chroma mahalliy client, "
        "Pinecone tashqi bulutli SDK."
    )


if __name__ == "__main__":
    print_comparison()
"""

L4_CODE_RU = """
# Сравнение того, как выглядит код подключения/поиска для всех трёх
# вариантов — концептуально, не запускается (нет API-ключей), но
# отражает реальную форму Python-клиента каждого варианта.

# ---------------------------------------------------------------------------
# 1) pgvector — через обычный SQL, используя существующую сессию SQLAlchemy
# ---------------------------------------------------------------------------

PGVECTOR_EXAMPLE = '''
from sqlalchemy import text

async def search_pgvector(db, query_vector: list[float], k: int = 3):
    rows = await db.execute(
        text(
            "SELECT id, title, embedding <=> :qv AS distance "
            "FROM lesson_embeddings "
            "ORDER BY embedding <=> :qv LIMIT :k"
        ),
        {"qv": str(query_vector), "k": k},
    )
    return rows.fetchall()
'''

# ---------------------------------------------------------------------------
# 2) Chroma — через собственную Python-библиотеку клиента (пакет chromadb)
# ---------------------------------------------------------------------------

CHROMA_EXAMPLE = '''
import chromadb

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("lessons")

collection.add(
    ids=["lesson_7", "lesson_11"],
    embeddings=[[0.1, 0.2, 0.3], [0.4, 0.1, 0.2]],
    documents=["Урок про Class ID", "Урок про Display Flex"],
)

results = collection.query(query_embeddings=[[0.12, 0.19, 0.28]], n_results=3)
'''

# ---------------------------------------------------------------------------
# 3) Pinecone — внешний облачный сервис, через собственный Python SDK
# ---------------------------------------------------------------------------

PINECONE_EXAMPLE = '''
from pinecone import Pinecone

pc = Pinecone(api_key="...")
index = pc.Index("lessons-index")

index.upsert(vectors=[
    {"id": "lesson_7", "values": [0.1, 0.2, 0.3]},
    {"id": "lesson_11", "values": [0.4, 0.1, 0.2]},
])

matches = index.query(vector=[0.12, 0.19, 0.28], top_k=3)
'''


def print_comparison() -> None:
    print("=== pgvector (SQL, в существующей базе Postgres) ===")
    print(PGVECTOR_EXAMPLE)
    print("=== Chroma (локально, пакет chromadb) ===")
    print(CHROMA_EXAMPLE)
    print("=== Pinecone (облачно, внешний сервис) ===")
    print(PINECONE_EXAMPLE)
    print(
        "ВНИМАНИЕ: весь код концептуальный — API-ключи/пакеты не "
        "установлены, поэтому не запускается. Цель — сравнить ФОРМУ: "
        "pgvector — обычный SQL, Chroma — локальный клиент, Pinecone — "
        "внешний облачный SDK."
    )


if __name__ == "__main__":
    print_comparison()
"""

L4_TASK = {
    "task_title": "Loyihangiz uchun vektor bazasini tanlang va asoslang",
    "task_title_ru": "Выберите и обоснуйте векторную базу для вашего проекта",
    "task_description": (
        "O'zingiz o'ylab topgan (yoki haqiqiy) kichik loyiha uchun "
        "pgvector, Chroma yoki Pinecone'dan birini tanlang. Yozma ravishda "
        "(matn fayl yoki komment sifatida) kamida 4 jumlada: nega aynan shu "
        "variant, qanday sharoit buni talab qiladi, va boshqa ikkita "
        "variant nega mos kelmasligini tushuntiring."
    ),
    "task_description_ru": (
        "Для придуманного (или реального) небольшого проекта выберите "
        "одну из pgvector, Chroma или Pinecone. Письменно (текстовый файл "
        "или комментарий) минимум в 4 предложениях объясните: почему "
        "именно этот вариант, какие условия это требуют, и почему два "
        "других варианта не подходят."
    ),
    "task_requirements": (
        "1) Loyiha qisqacha tasvirlansin (1-2 jumla). 2) Tanlangan variant "
        "va sabab aniq yozilsin. 3) Boshqa ikki variant nega rad etilgani "
        "izohlansin — bo'sh \"chunki yaxshiroq\" emas, aniq mezon bilan."
    ),
    "task_requirements_ru": (
        "1) Проект кратко описан (1-2 предложения). 2) Выбранный вариант и "
        "причина чётко указаны. 3) Объяснено, почему отклонены два других "
        "варианта — не просто 'потому что лучше', а с конкретным "
        "критерием."
    ),
    "task_technologies": "Matn/tahlil (kod shart emas)",
    "task_deadline_days": 3,
}

L4_SAMPLE = {
    "title": "Namuna: uchta variant kodining shakli yonma-yon",
    "description": (
        "Bir xil \"vektor qo'shish + qidirish\" amalining pgvector, "
        "Chroma va Pinecone'da qanday ko'rinishini solishtiradi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "pgvector_style.sql",
            "language": "sql",
            "code": (
                "-- pgvector: mavjud jadvalga vektor ustuni + oddiy SQL qidiruv\n"
                "SELECT id, title, embedding <=> '[0.1,0.2,0.3]' AS distance\n"
                "FROM lesson_embeddings\n"
                "WHERE course_id = 5\n"
                "ORDER BY embedding <=> '[0.1,0.2,0.3]'\n"
                "LIMIT 3;\n"
            ),
        },
        {
            "filename": "chroma_style.py",
            "language": "python",
            "code": (
                "import chromadb\n\n"
                "client = chromadb.PersistentClient(path='./chroma_data')\n"
                "collection = client.get_or_create_collection('lessons')\n"
                "results = collection.query(query_embeddings=[[0.1, 0.2, 0.3]], n_results=3)\n"
            ),
        },
        {
            "filename": "pinecone_style.py",
            "language": "python",
            "code": (
                "from pinecone import Pinecone\n\n"
                "pc = Pinecone(api_key='...')\n"
                "index = pc.Index('lessons-index')\n"
                "matches = index.query(vector=[0.1, 0.2, 0.3], top_k=3)\n"
            ),
        },
    ],
}

L4_EXERCISES = [
    {
        "title": "pgvector'ning asosiy afzalligi",
        "title_ru": "Главное преимущество pgvector",
        "description": "pgvector'ning eng katta afzalligi nima, agar loyiha allaqachon Postgres ishlatsa?",
        "description_ru": "В чём главное преимущество pgvector, если проект уже использует Postgres?",
        "exercise_type": "multiple_choice",
        "options": [
            "Alohida infratuzilma kerak emas — bitta SQL so'rovida oddiy filtr va vektor qidiruvni birlashtirish mumkin",
            "U doim eng tez ishlaydi",
            "U bepul cheksiz xotira beradi",
            "Uni sozlash uchun kod yozish shart emas",
        ],
        "options_ru": [
            "Не нужна отдельная инфраструктура — можно объединить обычный фильтр и векторный поиск в одном SQL-запросе",
            "Он всегда работает быстрее всех",
            "Он даёт бесплатную неограниченную память",
            "Для настройки не нужно писать код",
        ],
        "correct_answers": "A",
        "hint": "Darsda \"ikkilantirmasdan\" so'zini eslang.",
        "hint_ru": "Вспомните слово 'не дублируя' из урока.",
        "explanation": "pgvector mavjud Postgres bazasiga tabiiy kengaytma sifatida qo'shiladi, shuning uchun alohida infratuzilma shart emas.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Chroma qachon qulay",
        "title_ru": "Когда удобна Chroma",
        "description": "Chroma qanday holatda ayniqsa qulay?",
        "description_ru": "В какой ситуации Chroma особенно удобна?",
        "exercise_type": "multiple_choice",
        "options": [
            "Prototip yoki kichik loyihada tez boshlash kerak bo'lganda",
            "Millionlab foydalanuvchi bir vaqtda yozganda",
            "Bank tizimida tranzaksiya kerak bo'lganda",
            "Postgres allaqachon mavjud bo'lganda",
        ],
        "options_ru": [
            "Когда нужно быстро начать с прототипом или небольшим проектом",
            "Когда миллионы пользователей пишут одновременно",
            "Когда в банковской системе нужны транзакции",
            "Когда Postgres уже есть",
        ],
        "correct_answers": "A",
        "hint": "Chroma'ning \"embedded\" rejimini eslang — alohida server shart emas.",
        "hint_ru": "Вспомните 'embedded' режим Chroma — отдельный сервер не нужен.",
        "explanation": "Chroma sodda o'rnatilishi tufayli prototip va kichik loyihalar uchun juda qulay.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Pinecone'ning tabiati",
        "title_ru": "Природа Pinecone",
        "description": "Pinecone — bu to'liq ___ qilinadigan bulutli xizmat.",
        "description_ru": "Pinecone — это полностью ___ облачный сервис.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "boshqariladigan",
        "correct_answers_ru": "управляемый",
        "hint": "\"Managed\" so'zining o'zbekcha/ruscha ekvivalentini eslang.",
        "hint_ru": "Вспомните эквивалент слова 'managed'.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Vektor bazasi va xususiyatini bog'lash",
        "title_ru": "Сопоставление векторной базы и характеристики",
        "description": "Har bir vektor bazasini ENG mos xususiyati bilan tartibda joylashtiring (pgvector, Chroma, Pinecone tartibida)",
        "description_ru": "Расположите каждую векторную базу с НАИБОЛЕЕ подходящей характеристикой (в порядке pgvector, Chroma, Pinecone)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Mavjud Postgres bazasiga tabiiy kengaytma",
            "Fayl-asosli, server o'rnatmasdan ishlaydigan mahalliy variant",
            "To'liq boshqariladigan, tashqi bulutli xizmat",
        ],
        "drag_items_ru": [
            "Естественное расширение существующей базы Postgres",
            "Файловый локальный вариант без установки сервера",
            "Полностью управляемый внешний облачный сервис",
        ],
        "correct_order": [
            "Mavjud Postgres bazasiga tabiiy kengaytma",
            "Fayl-asosli, server o'rnatmasdan ishlaydigan mahalliy variant",
            "To'liq boshqariladigan, tashqi bulutli xizmat",
        ],
        "hint": "Tartib: pgvector, Chroma, Pinecone.",
        "hint_ru": "Порядок: pgvector, Chroma, Pinecone.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 5 — pgvector'ni sozlash: Postgres'ga vektor qo'shish
# ---------------------------------------------------------------------------

L5_TEXT = """
<h3>Muhim eslatma: bu darsda o'rgatilgan SQL — sizning O'Z loyihangiz uchun</h3>
<p>Bu darsdagi barcha SQL buyruqlari — <strong>o'z shaxsiy/o'quv loyihangiz
uchun</strong> qo'llash uchun mo'ljallangan. Ushbu platformaning haqiqiy
production bazasida pgvector kengaytmasi hozircha <strong>YOQILMAGAN</strong>
(buni SQLAlchemy orqali <code>SELECT * FROM pg_extension WHERE extname =
'vector'</code> so'rovi bilan tekshirib ko'rildi) — va bu dars uni yoqishni
TAVSIYA QILMAYDI: umumiy production bazasiga kengaytma qo'shish — bu
qaytarib bo'lmaydigan (yoki qiyin qaytariladigan) sxema o'zgarishi, buni
faqat rejalashtirilgan migratsiya orqali, jamoaviy qaror bilan qilish kerak.
Shuning uchun bu dars — QANDAY qilishni ko'rsatadi, sizning O'Z loyihangizda
sinab ko'rish uchun.</p>

<h3>1-qadam: kengaytmani yoqish</h3>
<p>PostgreSQL'da pgvector standart o'rnatilmagan — avval server darajasida
kutubxona o'rnatilgan bo'lishi kerak (masalan <code>apt install
postgresql-16-pgvector</code> yoki managed xizmatlarda (Supabase, RDS)
odatda bir tugma bilan yoqiladi), so'ngra bazada:</p>
<pre><code>CREATE EXTENSION IF NOT EXISTS vector;</code></pre>
<p><code>IF NOT EXISTS</code> — bu buyruqni xavfsiz qayta ishga tushirish
mumkinligini bildiradi (agar allaqachon yoqilgan bo'lsa, xato bermaydi).</p>

<h3>2-qadam: vektor ustunli jadval yaratish</h3>
<p>Endi oddiy jadvalga <code>vector(N)</code> turidagi ustun qo'shish mumkin
— <code>N</code> bu embedding modelingizning o'lchami (masalan
<code>all-MiniLM-L6-v2</code> uchun 384):</p>
<pre><code>CREATE TABLE lesson_embeddings (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_heading VARCHAR(500),
    embedding vector(384) NOT NULL
);</code></pre>
<p>Diqqat qiling: bu jadval <code>lessons</code> jadvaliga
<code>lesson_id</code> orqali <strong>bog'langan</strong> — har bir dars
bir nechta chunk'ga (va shuning uchun bir nechta qatorga) ega bo'lishi
mumkin, xuddi 2-darsda ko'rgan chunking mantig'iga mos.</p>

<p>Muhim: <code>vector(384)</code> dagi 384 raqami QATTIQ belgilangan — agar
keyinchalik boshqa o'lchamli modelga (masalan 768 o'lchamli) o'tsangiz, ustun
turi ham mos ravishda o'zgartirilishi (yoki jadval qayta yaratilishi) kerak
bo'ladi. Bitta jadvalda ikki xil o'lchamdagi vektorni saqlab bo'lmaydi — bu
1-darsdagi "bir xil model, doim" qoidasining sxema darajasidagi ko'rinishi.</p>

<h3>3-qadam: indeks qo'shish (katta miqyos uchun)</h3>
<p>Kichik jadvallar uchun (bir necha ming qator) indekssiz ham brute-force
qidiruv tez ishlaydi. Lekin katta miqyosda ANN indeks tezlikni oshiradi:</p>
<pre><code>CREATE INDEX ON lesson_embeddings
USING hnsw (embedding vector_cosine_ops);</code></pre>
<p><code>vector_cosine_ops</code> — indeks cosine masofasi bo'yicha
qidiruvga moslashtirilganini bildiradi (3-darsda ko'rgan
<code>&lt;=&gt;</code> operatoriga mos).</p>

<h3>4-qadam: qidiruv so'rovi</h3>
<p>Vektorni topib bo'lgach, eng mos chunk'larni topish uchun oddiy SQL
ishlatiladi — <code>&lt;=&gt;</code> operatori cosine MASOFASINI qaytaradi
(kichikroq — yaqinroq, shuning uchun <code>ORDER BY ... ASC</code>):</p>
<pre><code>SELECT lesson_id, chunk_text, embedding &lt;=&gt; :query_vector AS distance
FROM lesson_embeddings
ORDER BY embedding &lt;=&gt; :query_vector
LIMIT 5;</code></pre>
<p>Diqqat: bu — cosine MASOFASI (distance), cosine O'XSHASHLIGI (similarity)
emas — masofa kichik bo'lsa, o'xshashlik yuqori. Ko'p pgvector implementatsiyasida
<code>similarity = 1 - distance</code> munosabati bilan bog'liq.</p>

<h3>Vektor qo'shish (INSERT)</h3>
<p>Har bir yangi chunk uchun embedding hisoblanadi va oddiy INSERT orqali
saqlanadi:</p>
<pre><code>INSERT INTO lesson_embeddings (lesson_id, chunk_text, chunk_heading, embedding)
VALUES (:lesson_id, :chunk_text, :heading, :embedding);</code></pre>

<h3>Sxema diagrammasi</h3>
<pre class="mermaid">
erDiagram
  lessons ||--o{ lesson_embeddings : "1 dars -> ko'p chunk"
  lessons {
    int id PK
    text text_content
    string title
  }
  lesson_embeddings {
    int id PK
    int lesson_id FK
    text chunk_text
    string chunk_heading
    vector embedding
  }
</pre>
<p>Bu — 2-darsdagi chunking va 5-darsdagi saqlashning bog'lanishi: har bir
<code>lessons</code> qatori ko'p <code>lesson_embeddings</code> qatoriga
ega bo'ladi (bitta chunk — bitta qator), va har bir qatorda qidiriladigan
vektor saqlanadi.</p>
"""

L5_TEXT_RU = """
<h3>Важное замечание: SQL из этого урока — для ВАШЕГО проекта</h3>
<p>Все SQL-команды в этом уроке предназначены для применения в <strong>вашем
собственном/учебном проекте</strong>. В реальной production-базе этой
платформы расширение pgvector пока <strong>НЕ ВКЛЮЧЕНО</strong> (это
проверено через SQLAlchemy запросом <code>SELECT * FROM pg_extension WHERE
extname = 'vector'</code>) — и этот урок НЕ РЕКОМЕНДУЕТ включать его здесь:
добавление расширения в общую production-базу — это необратимое (или
труднообратимое) изменение схемы, которое должно выполняться только через
запланированную миграцию, по командному решению. Поэтому этот урок
показывает, КАК это сделать, чтобы вы попробовали в СВОЁМ проекте.</p>

<h3>Шаг 1: включение расширения</h3>
<p>В PostgreSQL pgvector не установлен по умолчанию — сначала на уровне
сервера должна быть установлена библиотека (например
<code>apt install postgresql-16-pgvector</code>, либо в managed-сервисах
(Supabase, RDS) обычно включается одной кнопкой), затем в базе:</p>
<pre><code>CREATE EXTENSION IF NOT EXISTS vector;</code></pre>
<p><code>IF NOT EXISTS</code> означает, что команду можно безопасно
запускать повторно (если уже включено, ошибки не будет).</p>

<h3>Шаг 2: создание таблицы со столбцом-вектором</h3>
<p>Теперь в обычную таблицу можно добавить столбец типа <code>vector(N)</code>
— где <code>N</code> — размерность вашей модели эмбеддинга (например 384
для <code>all-MiniLM-L6-v2</code>):</p>
<pre><code>CREATE TABLE lesson_embeddings (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_heading VARCHAR(500),
    embedding vector(384) NOT NULL
);</code></pre>
<p>Обратите внимание: эта таблица <strong>связана</strong> с таблицей
<code>lessons</code> через <code>lesson_id</code> — у каждого урока может
быть несколько фрагментов (и, следовательно, несколько строк), что
соответствует логике chunking из урока 2.</p>

<p>Важно: число 384 в <code>vector(384)</code> ЖЁСТКО зафиксировано — если
позже вы перейдёте на модель другой размерности (например, 768 измерений),
тип столбца тоже нужно будет изменить (или пересоздать таблицу). В одной
таблице нельзя хранить векторы разных размерностей — это отражение правила
"всегда одна и та же модель" из урока 1 на уровне схемы.</p>

<h3>Шаг 3: добавление индекса (для большого масштаба)</h3>
<p>Для небольших таблиц (несколько тысяч строк) brute-force поиск быстро
работает даже без индекса. Но при большом масштабе ANN-индекс повышает
скорость:</p>
<pre><code>CREATE INDEX ON lesson_embeddings
USING hnsw (embedding vector_cosine_ops);</code></pre>
<p><code>vector_cosine_ops</code> означает, что индекс настроен для поиска
по косинусному расстоянию (соответствует оператору <code>&lt;=&gt;</code>
из урока 3).</p>

<h3>Шаг 4: запрос поиска</h3>
<p>После получения вектора для поиска наиболее подходящих фрагментов
используется обычный SQL — оператор <code>&lt;=&gt;</code> возвращает
косинусное РАССТОЯНИЕ (меньше — ближе, поэтому <code>ORDER BY ...
ASC</code>):</p>
<pre><code>SELECT lesson_id, chunk_text, embedding &lt;=&gt; :query_vector AS distance
FROM lesson_embeddings
ORDER BY embedding &lt;=&gt; :query_vector
LIMIT 5;</code></pre>
<p>Внимание: это косинусное РАССТОЯНИЕ (distance), а не косинусное СХОДСТВО
(similarity) — чем меньше расстояние, тем выше сходство. Во многих
реализациях pgvector связаны соотношением
<code>similarity = 1 - distance</code>.</p>

<h3>Добавление вектора (INSERT)</h3>
<p>Для каждого нового фрагмента вычисляется эмбеддинг и сохраняется обычным
INSERT:</p>
<pre><code>INSERT INTO lesson_embeddings (lesson_id, chunk_text, chunk_heading, embedding)
VALUES (:lesson_id, :chunk_text, :heading, :embedding);</code></pre>

<h3>Диаграмма схемы</h3>
<pre class="mermaid">
erDiagram
  lessons ||--o{ lesson_embeddings : "1 урок -> много фрагментов"
  lessons {
    int id PK
    text text_content
    string title
  }
  lesson_embeddings {
    int id PK
    int lesson_id FK
    text chunk_text
    string chunk_heading
    vector embedding
  }
</pre>
<p>Это — связь между chunking из урока 2 и хранением из урока 5: каждая
строка <code>lessons</code> имеет много строк <code>lesson_embeddings</code>
(один фрагмент — одна строка), и в каждой строке хранится вектор для
поиска.</p>
"""

L5_CODE = '''
# Konseptual (haqiqiy DB'da ishga TUSHIRILMAYDI) — pgvector sozlash va
# ishlatishning to'liq Python + SQLAlchemy shakli. Buni O'Z loyihangizning
# migratsiya faylida yoki alohida sozlash skriptida ishlating.

PGVECTOR_SETUP_SQL = """
-- 1) Kengaytmani yoqish (server darajasida kutubxona o'rnatilgan bo'lishi kerak)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2) Vektor ustunli jadval
CREATE TABLE IF NOT EXISTS lesson_embeddings (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_heading VARCHAR(500),
    embedding vector(384) NOT NULL
);

-- 3) ANN indeks (katta miqyos uchun; kichik jadvalda shart emas)
CREATE INDEX IF NOT EXISTS lesson_embeddings_hnsw_idx
    ON lesson_embeddings USING hnsw (embedding vector_cosine_ops);
"""


async def insert_chunk_embedding(db, lesson_id: int, chunk_text: str, heading: str, embedding: list[float]) -> None:
    \"\"\"O'z loyihangizda: bitta chunk + uning embeddingini saqlaydi.
    `db` — mavjud AsyncSession (bu platformadagi barcha skriptlar
    ishlatadigan xuddi shu pattern).\"\"\"
    from sqlalchemy import text
    await db.execute(
        text(
            "INSERT INTO lesson_embeddings (lesson_id, chunk_text, chunk_heading, embedding) "
            "VALUES (:lesson_id, :chunk_text, :heading, :embedding)"
        ),
        {
            "lesson_id": lesson_id,
            "chunk_text": chunk_text,
            "heading": heading,
            "embedding": str(embedding),  # pgvector matn shaklidagi '[0.1,0.2,...]'ni kutadi
        },
    )


async def search_lesson_embeddings(db, query_vector: list[float], k: int = 5) -> list:
    \"\"\"Eng mos k ta chunk'ni qaytaradi, masofa (distance) bo'yicha
    o'sish tartibida (kichikroq masofa = yaqinroq ma'no).\"\"\"
    from sqlalchemy import text
    rows = await db.execute(
        text(
            "SELECT lesson_id, chunk_text, chunk_heading, "
            "embedding <=> :qv AS distance "
            "FROM lesson_embeddings "
            "ORDER BY embedding <=> :qv "
            "LIMIT :k"
        ),
        {"qv": str(query_vector), "k": k},
    )
    return rows.fetchall()


if __name__ == "__main__":
    print("Bu modul faqat namuna kodini o'z ichiga oladi — DB'ga ulanmaydi.")
    print("O'Z loyihangizda ishlatish uchun PGVECTOR_SETUP_SQL'ni migratsiya sifatida ishga tushiring.")
    print(PGVECTOR_SETUP_SQL)
'''

L5_CODE_RU = '''
# Концептуально (НЕ ЗАПУСКАЕТСЯ на реальной БД) — полная форма настройки
# и использования pgvector на Python + SQLAlchemy. Используйте это в
# файле миграции ВАШЕГО проекта или в отдельном скрипте настройки.

PGVECTOR_SETUP_SQL = """
-- 1) Включение расширения (на уровне сервера библиотека должна быть установлена)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2) Таблица со столбцом-вектором
CREATE TABLE IF NOT EXISTS lesson_embeddings (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_heading VARCHAR(500),
    embedding vector(384) NOT NULL
);

-- 3) ANN-индекс (для большого масштаба; для маленькой таблицы не обязателен)
CREATE INDEX IF NOT EXISTS lesson_embeddings_hnsw_idx
    ON lesson_embeddings USING hnsw (embedding vector_cosine_ops);
"""


async def insert_chunk_embedding(db, lesson_id: int, chunk_text: str, heading: str, embedding: list[float]) -> None:
    \"\"\"В вашем проекте: сохраняет один фрагмент + его эмбеддинг.
    `db` — существующая AsyncSession (тот же паттерн, что используют
    все скрипты этой платформы).\"\"\"
    from sqlalchemy import text
    await db.execute(
        text(
            "INSERT INTO lesson_embeddings (lesson_id, chunk_text, chunk_heading, embedding) "
            "VALUES (:lesson_id, :chunk_text, :heading, :embedding)"
        ),
        {
            "lesson_id": lesson_id,
            "chunk_text": chunk_text,
            "heading": heading,
            "embedding": str(embedding),  # pgvector ожидает текстовую форму '[0.1,0.2,...]'
        },
    )


async def search_lesson_embeddings(db, query_vector: list[float], k: int = 5) -> list:
    \"\"\"Возвращает k наиболее подходящих фрагментов в порядке
    возрастания расстояния (меньшее расстояние = ближе по смыслу).\"\"\"
    from sqlalchemy import text
    rows = await db.execute(
        text(
            "SELECT lesson_id, chunk_text, chunk_heading, "
            "embedding <=> :qv AS distance "
            "FROM lesson_embeddings "
            "ORDER BY embedding <=> :qv "
            "LIMIT :k"
        ),
        {"qv": str(query_vector), "k": k},
    )
    return rows.fetchall()


if __name__ == "__main__":
    print("Этот модуль содержит только пример кода — не подключается к БД.")
    print("Для использования в СВОЁМ проекте запустите PGVECTOR_SETUP_SQL как миграцию.")
    print(PGVECTOR_SETUP_SQL)
'''

L5_TASK = {
    "task_title": "O'z loyihangiz uchun pgvector migratsiya faylini yozing",
    "task_title_ru": "Напишите файл миграции pgvector для вашего проекта",
    "task_description": (
        "Darsdagi SQL asosida, o'z (haqiqiy yoki o'quv) loyihangiz uchun "
        "to'liq migratsiya faylini (SQL yoki Alembic upgrade() funksiyasi "
        "shaklida) yozing: CREATE EXTENSION, CREATE TABLE (kamida "
        "lesson_id/document_id, chunk_text, embedding ustunlari bilan) va "
        "CREATE INDEX. Bu faylni HECH QAYERGA ishga tushirmang — faqat "
        "matn sifatida yozing va topshiring."
    ),
    "task_description_ru": (
        "На основе SQL из урока напишите полный файл миграции (в виде SQL "
        "или функции Alembic upgrade()) для вашего (реального или "
        "учебного) проекта: CREATE EXTENSION, CREATE TABLE (минимум со "
        "столбцами lesson_id/document_id, chunk_text, embedding) и CREATE "
        "INDEX. НЕ запускайте этот файл нигде — просто напишите его как "
        "текст и сдайте."
    ),
    "task_requirements": (
        "1) CREATE EXTENSION IF NOT EXISTS vector bo'lishi shart. 2) "
        "Jadvalda kamida bitta foreign key va bitta vector(N) ustuni "
        "bo'lsin. 3) Indeks yaratilishi va vector_cosine_ops "
        "ishlatilganini ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Обязателен CREATE EXTENSION IF NOT EXISTS vector. 2) В "
        "таблице должен быть минимум один foreign key и один столбец "
        "vector(N). 3) Покажите создание индекса с использованием "
        "vector_cosine_ops."
    ),
    "task_technologies": "SQL, PostgreSQL, pgvector",
    "task_deadline_days": 5,
}

L5_SAMPLE = {
    "title": "Namuna: to'liq pgvector migratsiyasi (o'z loyiha uchun)",
    "description": (
        "Kengaytmadan tortib indeksgacha — o'z loyihangizga tayyor "
        "ishlatish uchun to'liq SQL migratsiya namunasi."
    ),
    "sample_type": "sql",
    "code_files": [
        {
            "filename": "001_add_pgvector.sql",
            "language": "sql",
            "code": (
                "-- O'Z loyihangiz uchun — bu faylni ushbu platformaning\n"
                "-- production bazasida ISHGA TUSHIRMANG.\n\n"
                "CREATE EXTENSION IF NOT EXISTS vector;\n\n"
                "CREATE TABLE IF NOT EXISTS document_embeddings (\n"
                "    id SERIAL PRIMARY KEY,\n"
                "    document_id INTEGER NOT NULL,\n"
                "    chunk_text TEXT NOT NULL,\n"
                "    chunk_order INTEGER NOT NULL DEFAULT 0,\n"
                "    embedding vector(384) NOT NULL,\n"
                "    created_at TIMESTAMPTZ NOT NULL DEFAULT now()\n"
                ");\n\n"
                "CREATE INDEX IF NOT EXISTS document_embeddings_hnsw_idx\n"
                "    ON document_embeddings USING hnsw (embedding vector_cosine_ops);\n\n"
                "-- Qidiruv namunasi (parametr sifatida vektor beriladi):\n"
                "-- SELECT document_id, chunk_text, embedding <=> $1 AS distance\n"
                "-- FROM document_embeddings ORDER BY embedding <=> $1 LIMIT 5;\n"
            ),
        },
    ],
}

L5_EXERCISES = [
    {
        "title": "pgvector kengaytmasi",
        "title_ru": "Расширение pgvector",
        "description": "PostgreSQL'da vector turini ishlatish uchun avval qanday buyruq bajarilishi kerak?",
        "description_ru": "Какую команду нужно выполнить первой, чтобы использовать тип vector в PostgreSQL?",
        "exercise_type": "multiple_choice",
        "options": [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE TABLE vector;",
            "IMPORT vector;",
            "ALTER DATABASE ENABLE vector;",
        ],
        "options_ru": [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE TABLE vector;",
            "IMPORT vector;",
            "ALTER DATABASE ENABLE vector;",
        ],
        "correct_answers": "A",
        "hint": "Bu — PostgreSQL kengaytma tizimining standart sintaksisi.",
        "hint_ru": "Это стандартный синтаксис системы расширений PostgreSQL.",
        "explanation": "vector turi va operatorlarini yoqish uchun CREATE EXTENSION IF NOT EXISTS vector; bajarilishi kerak.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Cosine masofa operatori",
        "title_ru": "Оператор косинусного расстояния",
        "description": "pgvector'da cosine masofasini hisoblash uchun ___ operatori ishlatiladi.",
        "description_ru": "В pgvector для вычисления косинусного расстояния используется оператор ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "<=>",
        "hint": "3-darsda ko'rgan cosine masofasi operatorini eslang.",
        "hint_ru": "Вспомните оператор косинусного расстояния из урока 3.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Vektor o'lchamini o'zgartirish",
        "title_ru": "Изменение размерности вектора",
        "description": "Agar embedding modelini 384 o'lchamdan 768 o'lchamga almashtirsangiz, jadval ustuniga nima bo'ladi?",
        "description_ru": "Если вы смените модель эмбеддинга с 384 на 768 измерений, что произойдёт со столбцом таблицы?",
        "exercise_type": "multiple_choice",
        "options": [
            "vector(N) turi ham mos ravishda o'zgartirilishi (yoki jadval qayta yaratilishi) kerak bo'ladi",
            "Hech narsa o'zgarmaydi, avtomatik moslashadi",
            "Faqat indeks o'chiriladi, ustun o'zi o'zgaradi",
            "PostgreSQL xato beradi va butun bazani o'chirib tashlaydi",
        ],
        "options_ru": [
            "Тип vector(N) тоже нужно будет изменить (или пересоздать таблицу)",
            "Ничего не меняется, всё подстраивается автоматически",
            "Удаляется только индекс, столбец меняется сам",
            "PostgreSQL выдаёт ошибку и удаляет всю базу",
        ],
        "correct_answers": "A",
        "hint": "Bir jadvalda ikki xil o'lchamdagi vektorni saqlab bo'ladimi?",
        "hint_ru": "Можно ли в одной таблице хранить векторы разных размерностей?",
        "explanation": "vector(N) o'lchami qattiq belgilangan — model o'zgarsa, sxema ham mos ravishda o'zgartirilishi shart.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "pgvector sozlash bosqichlari",
        "title_ru": "Этапы настройки pgvector",
        "description": "Bosqichlarni to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE TABLE ... embedding vector(384) ...;",
            "CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);",
            "INSERT ... so'ngra SELECT ... ORDER BY embedding <=> ...;",
        ],
        "drag_items_ru": [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE TABLE ... embedding vector(384) ...;",
            "CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);",
            "INSERT ..., затем SELECT ... ORDER BY embedding <=> ...;",
        ],
        "correct_order": [
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "CREATE TABLE ... embedding vector(384) ...;",
            "CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);",
            "INSERT ... so'ngra SELECT ... ORDER BY embedding <=> ...;",
        ],
        "hint": "Avval kengaytma, keyin jadval, keyin indeks, so'ngra ma'lumot va qidiruv.",
        "hint_ru": "Сначала расширение, потом таблица, потом индекс, затем данные и поиск.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 6 — Amaliy semantik qidiruv: platformaning o'z darslari ustida
# ---------------------------------------------------------------------------

L6_TEXT = """
<h3>Endi hammasini birlashtiramiz — haqiqiy ma'lumot ustida</h3>
<p>Oldingi 5 ta darsda embedding, chunking, cosine similarity va vektor
saqlashni alohida-alohida ko'rdik. Bu darsda ularni BIR JOYGA yig'ib,
ushbu platformaning HAQIQIY <code>lessons</code> jadvali ustida ishlaydigan
mini semantik qidiruv tizimini quramiz — o'ylab topilgan misol emas, balki
500dan ortiq haqiqiy, published dars matni ustida.</p>

<h3>Nega pgvector emas, mahalliy Python</h3>
<p>5-darsda ko'rganimizdek, bu platformaning production bazasida pgvector
kengaytmasi HALI yoqilmagan, va uni shu yerda yoqish bu darsning maqsadi
emas. Shuning uchun bu amaliy misol <strong>butunlay mahalliy Python
xotirasida</strong> ishlaydi: darslarni oddiy SQLAlchemy SELECT so'rovi
bilan o'qib olamiz (faqat o'qish — hech qanday yozish yo'q), ularni chunk'larga
bo'lamiz, har birini vektorlashtiramiz va natijalarni Python ro'yxatida
saqlab, brute-force cosine qidiruv qilamiz. Bu — 3-darsda ko'rgan
"kichik/o'rta miqyosda brute-force to'liq amaliy" tamoyilining aynan o'zi:
yuzlab dars uchun bu juda tez ishlaydi, pgvector yoki boshqa maxsus vektor
bazasi shart emas.</p>

<h3>Pipeline: to'rt bosqich</h3>
<pre class="mermaid">
flowchart TB
  DB[("lessons jadvali
(faqat o'qish)")]
  DB -->|"SELECT id, title, text_content
WHERE is_published=true"| RAW["Xom dars matnlari (HTML)"]
  RAW -->|"2-darsdagi
structure_aware_chunks()"| CHUNKS["Chunk'lar ro'yxati
(har biri: dars_id, sarlavha, matn)"]
  CHUNKS -->|"1-darsdagi
fake_embed()"| INDEX["Xotiradagi indeks:
[(chunk, vektor), ...]"]
  QUERY["Foydalanuvchi so'rovi:
'Python funksiyalari haqida dars bormi?'"] -->|"fake_embed()"| QVEC["So'rov vektori"]
  QVEC -->|"3-darsdagi
cosine_similarity() har biriga"| INDEX
  INDEX -->|"top-K saralash"| RESULT["Eng mos 3 ta chunk"]
</pre>

<h3>Real kodning tuzilishi</h3>
<p>Quyidagi kod bo'limida <code>build_search_index()</code> funksiyasi
haqiqiy <code>AsyncSessionLocal</code> orqali <code>lessons</code> jadvalidan
published darslarni o'qiydi (faqat SELECT — bu skript hech qanday yozish
amalini bajarmaydi), so'ngra har birini <code>structure_aware_chunks()</code>
bilan bo'ladi va <code>fake_embed()</code> bilan vektorlashtiradi. Natijada
xotirada oddiy ro'yxat hosil bo'ladi: <code>[(lesson_id, title, chunk_text,
vector), ...]</code>. <code>semantic_search()</code> funksiyasi esa foydalanuvchi
so'rovini xuddi shunday vektorlashtirib, HAR BIR chunk bilan cosine
solishtiradi va eng yuqori ballli top-K tasini qaytaradi.</p>

<h3>Nega bu haqiqiy misol, "o'ylab topilgan" emas</h3>
<p>Bu darsning boshqa RAG darslaridan (yoki boshqa kurslardagi o'ylab
topilgan "hujjatlar to'plami" misollaridan) farqi shunda: qidiruv HAQIQIY
production ma'lumotlar bazasidagi HAQIQIY, talabalar hozir o'qiyotgan dars
matnlari ustida ishlaydi. Agar siz "CSS Grid haqida dars bormi" deb so'rasangiz,
natija — bu platformada HAQIQATDA mavjud bo'lgan darsning ID'si va sarlavhasi
bo'ladi, ular bilan to'g'ridan-to'g'ri tekshirib ko'rish mumkin (masalan
platforma frontendida shu dars ID'sini ochib).</p>

<h3>Cheklov: fake_embed haqiqiy semantik model emasligini eslatib qo'yish</h3>
<p>Muhim ogohlantirish: 1-darsda aytilganidek, <code>fake_embed</code> —
harf statistikasiga asoslangan oddiy funksiya, HAQIQIY semantik tushunish
qobiliyatiga ega emas (masalan "it" va "kuchuk" so'zlarini sinonim sifatida
tan olmaydi, chunki harflar boshqacha). Production loyihada bu o'rinda
<code>sentence-transformers</code> yoki Gemini embedding API ishlatiladi —
lekin pipeline'ning STRUKTURASI (chunk -> embed -> saqlash -> so'rovni
embed qilish -> cosine solishtirish -> top-K) BIR XIL qoladi, faqat
<code>embed()</code> funksiyasining ICHKI ishlashi almashadi.</p>

<h3>Natijalar sifatini qanday baholash mumkin: haqiqiy misol</h3>
<p>Yuqoridagi pipeline'ni ushbu platformaning HAQIQIY bazasida ishga
tushirganda ("Python funksiyalari qanday e'lon qilinadi" so'rovi bilan)
qiziq va o'rgatuvchi natija chiqdi: eng yuqori ballli (0.8077) natija Python
haqida emas, balki #498-dars "Pozitsiyalash va Z-index" (CSS
<code>position: relative</code> haqida) bo'lib chiqdi! Bu —
<code>fake_embed</code>'ning harf-statistikasiga asoslanganligining aniq
oqibati: ikkala matnda ham o'xshash harf chastotalari (masalan "o", "n",
"i" harflari) ko'p uchraydi, garchi mavzular butunlay boshqa bo'lsa ham. Bu
— L11'da chuqurroq o'rganiladigan "retrieved ≠ correct" muammosining JONLI
namunasi: cosine ball YUQORI chiqishi mumkin, lekin natija baribir
NOTO'G'RI bo'lishi mumkin.</p>
<p>Bunday holatlarni qanday aniqlash mumkin? Eng oddiy usul — natijalarni
QO'LDA ko'zdan kechirish: har bir topilgan chunk'ning sarlavhasi va matni
so'rovga haqiqatan mos keladimi, tekshirish. Agar top-3 natijaning
aksariyati mavzu jihatidan mos kelmasa (yuqoridagi misoldagi kabi), bu
embedding sifatining YETARLI emasligidan dalolat beradi — HAQIQIY loyihada
bu holat <code>sentence-transformers</code> yoki Gemini embedding'ga
o'tish zarurligini ko'rsatuvchi aniq signal bo'lardi.</p>
"""

L6_TEXT_RU = """
<h3>Теперь объединяем всё вместе — на реальных данных</h3>
<p>В прошлых 5 уроках мы по отдельности разобрали эмбеддинги, chunking,
cosine similarity и хранение векторов. В этом уроке мы объединим их В ОДНОМ
МЕСТЕ и построим мини-систему семантического поиска, работающую на
РЕАЛЬНОЙ таблице <code>lessons</code> этой платформы — не на выдуманном
примере, а на более чем 500 реальных, опубликованных текстах уроков.</p>

<h3>Почему не pgvector, а локальный Python</h3>
<p>Как мы видели в уроке 5, в production-базе этой платформы расширение
pgvector пока НЕ включено, и включать его здесь — не цель этого урока.
Поэтому этот практический пример работает <strong>полностью в локальной
памяти Python</strong>: читаем уроки обычным SELECT-запросом SQLAlchemy
(только чтение — никакой записи), разбиваем их на фрагменты, векторизуем
каждый и сохраняем результаты в списке Python, выполняя brute-force
косинусный поиск. Это — то же самое правило из урока 3 "для маленького/
среднего масштаба brute-force полностью практичен": для сотен уроков это
работает очень быстро, pgvector или другая специализированная векторная
база не нужны.</p>

<h3>Pipeline: четыре этапа</h3>
<pre class="mermaid">
flowchart TB
  DB[("таблица lessons
(только чтение)")]
  DB -->|"SELECT id, title, text_content
WHERE is_published=true"| RAW["Сырые тексты уроков (HTML)"]
  RAW -->|"structure_aware_chunks()
из урока 2"| CHUNKS["Список фрагментов
(каждый: id_урока, заголовок, текст)"]
  CHUNKS -->|"fake_embed()
из урока 1"| INDEX["Индекс в памяти:
[(фрагмент, вектор), ...]"]
  QUERY["Запрос пользователя:
'Есть ли урок про функции Python?'"] -->|"fake_embed()"| QVEC["Вектор запроса"]
  QVEC -->|"cosine_similarity()
из урока 3 к каждому"| INDEX
  INDEX -->|"сортировка top-K"| RESULT["3 наиболее подходящих фрагмента"]
</pre>

<h3>Структура реального кода</h3>
<p>В следующем блоке кода функция <code>build_search_index()</code> читает
опубликованные уроки из таблицы <code>lessons</code> через реальную
<code>AsyncSessionLocal</code> (только SELECT — этот скрипт не выполняет
никакой записи), затем разбивает каждый на фрагменты через
<code>structure_aware_chunks()</code> и векторизует через
<code>fake_embed()</code>. В результате в памяти создаётся простой список:
<code>[(lesson_id, title, chunk_text, vector), ...]</code>. Функция
<code>semantic_search()</code> векторизует запрос пользователя таким же
образом, сравнивает через cosine с КАЖДЫМ фрагментом и возвращает top-K с
наивысшим баллом.</p>

<h3>Почему это реальный пример, а не "выдуманный"</h3>
<p>Отличие этого урока от других уроков RAG (или выдуманных примеров
"набора документов" в других курсах) в том, что поиск работает на РЕАЛЬНОЙ
production базе данных, на РЕАЛЬНЫХ текстах уроков, которые студенты
изучают прямо сейчас. Если вы спросите "есть ли урок про CSS Grid",
результатом будет ID и заголовок урока, который ДЕЙСТВИТЕЛЬНО существует
на этой платформе, и его можно напрямую проверить (например, открыв этот
урок во фронтенде платформы).</p>

<h3>Ограничение: напоминание, что fake_embed — не настоящая семантическая модель</h3>
<p>Важное предупреждение: как говорилось в уроке 1, <code>fake_embed</code>
— простая функция на основе буквенной статистики, у неё НЕТ настоящей
способности семантического понимания (например, она не распознаёт "собака"
и "щенок" как синонимы, потому что буквы разные). В production-проекте
здесь использовались бы <code>sentence-transformers</code> или Gemini
embedding API — но СТРУКТУРА pipeline (chunk -> embed -> хранение -> embed
запроса -> cosine сравнение -> top-K) остаётся ТОЙ ЖЕ, меняется только
ВНУТРЕННЯЯ работа функции <code>embed()</code>.</p>

<h3>Как оценить качество результатов: реальный пример</h3>
<p>При запуске указанного выше pipeline на РЕАЛЬНОЙ базе этой платформы (с
запросом "Как объявляются функции в Python") получился интересный и
поучительный результат: результат с наивысшим баллом (0.8077) оказался
вовсе не про Python, а урок #498 "Позиционирование и Z-index" (про CSS
<code>position: relative</code>)! Это — прямое следствие того, что
<code>fake_embed</code> основан на буквенной статистике: в обоих текстах
часто встречаются похожие частоты букв (например "о", "н", "и"), хотя темы
совершенно разные. Это — ЖИВОЙ пример проблемы "найдено ≠ верно", которую
мы подробнее разберём в уроке 11: балл cosine может быть ВЫСОКИМ, но
результат всё равно может быть НЕВЕРНЫМ.</p>
<p>Как обнаружить такие случаи? Самый простой способ — вручную просмотреть
результаты: проверить, действительно ли заголовок и текст каждого
найденного фрагмента соответствуют запросу. Если большинство top-3
результатов не подходят по теме (как в примере выше), это явный сигнал о
НЕДОСТАТОЧНОМ качестве эмбеддинга — в РЕАЛЬНОМ проекте это стало бы явным
сигналом о необходимости перехода на <code>sentence-transformers</code>
или Gemini embedding.</p>
"""

L6_CODE = """
# To'liq mini semantik qidiruv tizimi — HAQIQIY lessons jadvali ustida
# (faqat o'qish). db_helpers.py'dagi barcha skriptlar ishlatadigan
# xuddi shu AsyncSessionLocal patterni.

from __future__ import annotations
import math
import re

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db import base as _base  # noqa: F401 — barcha modellarni ro'yxatdan o'tkazadi
from app.models.lesson import Lesson


# --- 1-darsdan: embedding ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        idx = (ord(ch) + i) % dims
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# --- 2-darsdan: structure-aware chunking ---
def structure_aware_chunks(html: str) -> list[dict]:
    if not html:
        return []
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(sarlavhasiz)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        if plain_text:
            chunks.append({"heading": heading, "text": plain_text})
    return chunks


# --- 3-darsdan: cosine similarity ---
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


async def build_search_index(limit_lessons: int = 30) -> list[dict]:
    \"\"\"HAQIQIY lessons jadvalidan (faqat o'qish!) published darslarni
    oladi, chunk'larga bo'ladi va vektorlashtiradi. Xotirada saqlanadigan
    oddiy indeks qaytaradi.\"\"\"
    index: list[dict] = []
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Lesson.id, Lesson.title, Lesson.text_content)
                .where(Lesson.is_published == True, Lesson.text_content.isnot(None))
                .limit(limit_lessons)
            )
        ).all()

    for lesson_id, title, text_content in rows:
        for chunk in structure_aware_chunks(text_content):
            index.append({
                "lesson_id": lesson_id,
                "lesson_title": title,
                "heading": chunk["heading"],
                "text": chunk["text"],
                "vector": fake_embed(chunk["text"]),
            })
    return index


def semantic_search(query: str, index: list[dict], k: int = 3) -> list[dict]:
    \"\"\"Foydalanuvchi so'rovini vektorlashtiradi va indeksdagi HAR BIR
    chunk bilan cosine solishtirib, eng mos top-k tasini qaytaradi.\"\"\"
    query_vector = fake_embed(query)
    scored = [
        {**entry, "score": cosine_similarity(query_vector, entry["vector"])}
        for entry in index
    ]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return scored[:k]


async def main() -> None:
    print("Indeks qurilmoqda (haqiqiy lessons jadvalidan, faqat o'qish)...")
    index = await build_search_index(limit_lessons=30)
    print(f"Jami {len(index)} ta chunk indekslandi.\\n")

    query = "Python funksiyalari qanday e'lon qilinadi"
    results = semantic_search(query, index, k=3)
    print(f"So'rov: {query!r}\\n")
    for r in results:
        print(f"  [{r['score']:.4f}] dars #{r['lesson_id']} {r['lesson_title']!r} — {r['heading']!r}")
        print(f"           {r['text'][:120]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

L6_CODE_RU = """
# Полная мини-система семантического поиска — на РЕАЛЬНОЙ таблице
# lessons (только чтение). Тот же паттерн AsyncSessionLocal, что
# используют все скрипты в db_helpers.py.

from __future__ import annotations
import math
import re

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db import base as _base  # noqa: F401 — регистрирует все модели
from app.models.lesson import Lesson


# --- из урока 1: эмбеддинг ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        idx = (ord(ch) + i) % dims
        vector[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# --- из урока 2: structure-aware chunking ---
def structure_aware_chunks(html: str) -> list[dict]:
    if not html:
        return []
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(без заголовка)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        if plain_text:
            chunks.append({"heading": heading, "text": plain_text})
    return chunks


# --- из урока 3: cosine similarity ---
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


async def build_search_index(limit_lessons: int = 30) -> list[dict]:
    \"\"\"Берёт РЕАЛЬНЫЕ (только чтение!) опубликованные уроки из таблицы
    lessons, разбивает на фрагменты и векторизует. Возвращает простой
    индекс, хранящийся в памяти.\"\"\"
    index: list[dict] = []
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Lesson.id, Lesson.title, Lesson.text_content)
                .where(Lesson.is_published == True, Lesson.text_content.isnot(None))
                .limit(limit_lessons)
            )
        ).all()

    for lesson_id, title, text_content in rows:
        for chunk in structure_aware_chunks(text_content):
            index.append({
                "lesson_id": lesson_id,
                "lesson_title": title,
                "heading": chunk["heading"],
                "text": chunk["text"],
                "vector": fake_embed(chunk["text"]),
            })
    return index


def semantic_search(query: str, index: list[dict], k: int = 3) -> list[dict]:
    \"\"\"Векторизует запрос пользователя и сравнивает через cosine с
    КАЖДЫМ фрагментом индекса, возвращая top-k с наивысшим баллом.\"\"\"
    query_vector = fake_embed(query)
    scored = [
        {**entry, "score": cosine_similarity(query_vector, entry["vector"])}
        for entry in index
    ]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return scored[:k]


async def main() -> None:
    print("Строим индекс (из реальной таблицы lessons, только чтение)...")
    index = await build_search_index(limit_lessons=30)
    print(f"Всего проиндексировано {len(index)} фрагментов.\\n")

    query = "Как объявляются функции в Python"
    results = semantic_search(query, index, k=3)
    print(f"Запрос: {query!r}\\n")
    for r in results:
        print(f"  [{r['score']:.4f}] урок #{r['lesson_id']} {r['lesson_title']!r} — {r['heading']!r}")
        print(f"           {r['text'][:120]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

L6_TASK = {
    "task_title": "O'z semantik qidiruv so'rovingizni sinang",
    "task_title_ru": "Проверьте свой запрос к семантическому поиску",
    "task_description": (
        "Darsdagi `build_search_index` va `semantic_search` "
        "funksiyalaridan foydalanib, kamida 3 xil so'rov bilan qidiruv "
        "qiling (masalan \"CSS haqida dars bormi\", \"ma'lumotlar bazasi "
        "haqida nima bor\"), har birining top-3 natijasini chiqaring va "
        "natijalar mantiqan to'g'ri ko'rinadimi (yoki fake_embed "
        "cheklovi tufayli noaniqmi) izohlang."
    ),
    "task_description_ru": (
        "Используя функции `build_search_index` и `semantic_search` из "
        "урока, выполните поиск минимум по 3 разным запросам (например "
        "\"есть ли урок про CSS\", \"что есть про базы данных\"), выведите "
        "top-3 результата для каждого и прокомментируйте, выглядят ли "
        "результаты логичными (или неточными из-за ограничения "
        "fake_embed)."
    ),
    "task_requirements": (
        "1) Kamida 3 xil so'rov sinalsin. 2) Har birining top-3 natijasi "
        "(dars ID, sarlavha, ball) chiqarilsin. 3) Har bir natija haqida "
        "kamida bitta jumlali izoh yozilsin."
    ),
    "task_requirements_ru": (
        "1) Должно быть проверено минимум 3 разных запроса. 2) Для "
        "каждого должны быть выведены top-3 результата (ID урока, "
        "заголовок, балл). 3) К каждому результату должен быть написан "
        "минимум один комментарий-предложение."
    ),
    "task_technologies": "Python, SQLAlchemy",
    "task_deadline_days": 5,
}

L6_SAMPLE = {
    "title": "Namuna: bitta so'rov bilan to'liq qidiruv",
    "description": (
        "build_search_index va semantic_search'ni chaqirib, bitta "
        "so'rov uchun eng mos 3 ta chunk'ni topib beradi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "run_search.py",
            "language": "python",
            "code": (
                "import asyncio\n"
                "from search_index import build_search_index, semantic_search  # darsdagi modul\n\n\n"
                "async def main():\n"
                "    index = await build_search_index(limit_lessons=20)\n"
                "    print(f\"{len(index)} ta chunk indekslandi\")\n\n"
                "    for query in [\n"
                "        \"Ma'lumotlar bazasi bilan qanday ishlash mumkin\",\n"
                "        \"CSS orqali elementlarni tekislash\",\n"
                "    ]:\n"
                "        print(f\"\\n--- So'rov: {query!r} ---\")\n"
                "        for r in semantic_search(query, index, k=3):\n"
                "            print(f\"  [{r['score']:.4f}] dars #{r['lesson_id']} {r['lesson_title']!r}\")\n\n\n"
                "if __name__ == '__main__':\n"
                "    asyncio.run(main())\n"
            ),
        },
    ],
}

L6_EXERCISES = [
    {
        "title": "Nega mahalliy Python, pgvector emas",
        "title_ru": "Почему локальный Python, а не pgvector",
        "description": "Bu darsdagi amaliy misol nega pgvector emas, mahalliy Python xotirasida ishlaydi?",
        "description_ru": "Почему практический пример в этом уроке работает в локальной памяти Python, а не через pgvector?",
        "exercise_type": "multiple_choice",
        "options": [
            "Chunki bu platformaning production bazasida pgvector hali yoqilmagan va uni shu yerda yoqish kursning maqsadi emas",
            "Chunki pgvector umuman ishlamaydi",
            "Chunki Python xotirasi doim tezroq",
            "Chunki lessons jadvali juda kichik",
        ],
        "options_ru": [
            "Потому что в production-базе этой платформы pgvector ещё не включён, и включать его здесь — не цель курса",
            "Потому что pgvector вообще не работает",
            "Потому что память Python всегда быстрее",
            "Потому что таблица lessons слишком маленькая",
        ],
        "correct_answers": "A",
        "hint": "5-darsdagi SQLAlchemy tekshiruvining natijasini eslang.",
        "hint_ru": "Вспомните результат проверки через SQLAlchemy в уроке 5.",
        "explanation": "pgvector kengaytmasi hozircha yoqilmagan va uni yoqish alohida, rejalashtirilgan qaror bo'lishi kerak — shuning uchun bu dars mahalliy Python bilan cheklanadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Pipeline'ning to'rt bosqichi",
        "title_ru": "Четыре этапа pipeline",
        "description": "Bosqichlarni to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "lessons jadvalidan matnlarni o'qish (faqat SELECT)",
            "Har bir matnni chunk'larga bo'lish",
            "Har bir chunk'ni vektorlashtirish",
            "So'rovni vektorlashtirib, cosine bo'yicha top-K topish",
        ],
        "drag_items_ru": [
            "Чтение текстов из таблицы lessons (только SELECT)",
            "Разбиение каждого текста на фрагменты",
            "Векторизация каждого фрагмента",
            "Векторизация запроса и поиск top-K по cosine",
        ],
        "correct_order": [
            "lessons jadvalidan matnlarni o'qish (faqat SELECT)",
            "Har bir matnni chunk'larga bo'lish",
            "Har bir chunk'ni vektorlashtirish",
            "So'rovni vektorlashtirib, cosine bo'yicha top-K topish",
        ],
        "hint": "Darsdagi pipeline diagrammasini eslang.",
        "hint_ru": "Вспомните диаграмму pipeline из урока.",
        "difficulty_level": "Easy",
        "points": 6,
    },
    {
        "title": "fake_embed cheklovi",
        "title_ru": "Ограничение fake_embed",
        "description": "fake_embed nima uchun HAQIQIY semantik model emas?",
        "description_ru": "Почему fake_embed НЕ является настоящей семантической моделью?",
        "exercise_type": "multiple_choice",
        "options": [
            "U harf statistikasiga asoslangan, ma'noni haqiqatan tushunmaydi (masalan sinonimlarni tanimaydi)",
            "U hech qanday vektor qaytarmaydi",
            "U faqat inglizcha matn bilan ishlaydi",
            "U internetga ulanishni talab qiladi",
        ],
        "options_ru": [
            "Она основана на буквенной статистике и не понимает смысл по-настоящему (например, не распознаёт синонимы)",
            "Она вообще не возвращает вектор",
            "Она работает только с английским текстом",
            "Она требует подключения к интернету",
        ],
        "correct_answers": "A",
        "hint": "1-darsdagi \"it\" va \"kuchuk\" misolini eslang.",
        "hint_ru": "Вспомните пример 'собака' и 'щенок' из урока 1.",
        "explanation": "fake_embed faqat harf-daraja statistikasidan foydalanadi, haqiqiy modeldagi kabi ma'no tushunishga ega emas — lekin pipeline strukturasi bir xil qoladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Indeksni qayta qurish shartmi",
        "title_ru": "Нужно ли перестраивать индекс",
        "description": "Agar lessons jadvaliga yangi dars qo'shilsa, semantik qidiruv uni topishi uchun nima qilish kerak?",
        "description_ru": "Если в таблицу lessons добавлен новый урок, что нужно сделать, чтобы семантический поиск мог его найти?",
        "exercise_type": "text_input",
        "expected_answer": (
            "Yangi darsni ham chunk'larga bo'lib, vektorlashtirib, "
            "indeksga (yoki pgvector jadvaliga) qo'shish kerak — "
            "build_search_index qayta ishga tushirilishi yoki indeks "
            "inkremental yangilanishi kerak."
        ),
        "hint": "Indeks qanday qurilganini (build_search_index) eslang — u statik ro'yxatmi yoki avtomatik yangilanadimi?",
        "hint_ru": "Вспомните, как строится индекс (build_search_index) — это статический список или он обновляется автоматически?",
        "difficulty_level": "Hard",
        "points": 10,
    },
]

# ---------------------------------------------------------------------------
# Lesson 7 — R1: Takrorlash — Embedding'dan qidiruvgacha
# ---------------------------------------------------------------------------

L7_TEXT = """
<h3>R1 — Takrorlash darsi</h3>
<p>Bu — takrorlash (review) darsi, shuning uchun bu yerda yangi tushuncha
YO'Q — faqat 0-6 darslarda o'rgangan hamma narsani bir joyga yig'ib,
amaliy vazifa orqali mustahkamlaymiz. Shu sababli matn boshqa darslarga
qaraganda ataylab qisqaroq — asosiy e'tibor pastdagi amaliy vazifada.</p>

<h3>0-6 darslarda nimalarni o'rgandik</h3>
<ul>
<li><strong>L0:</strong> RAG nima va nega LLM'ning o'z bilimi yetarli emas
— gallyutsinatsiya muammosi va uch bosqichli yechim (retrieve-augment-generate).</li>
<li><strong>L1:</strong> Embedding — matnni doim bir xil o'lchamdagi son
vektoriga aylantirish; mahalliy model vs hosted API.</li>
<li><strong>L2:</strong> Chunking — hujjatni qidiriladigan bo'laklarga
bo'lish, overlap va structure-aware strategiya.</li>
<li><strong>L3:</strong> Cosine similarity — ikki vektor orasidagi burchakni
o'lchash, brute-force qidiruv.</li>
<li><strong>L4:</strong> Vektor bazalari — pgvector, Chroma, Pinecone
o'rtasidagi haqiqiy savdolashuvlar.</li>
<li><strong>L5:</strong> pgvector'ni sozlash — CREATE EXTENSION, vector
ustuni, HNSW indeks, SQL qidiruv.</li>
<li><strong>L6:</strong> Hammasini birlashtirib, ushbu platformaning
HAQIQIY dars matnlari ustida ishlaydigan mini semantik qidiruv qurdik.</li>
</ul>

<h3>Nega bu tartib muhim edi</h3>
<p>Har bir dars keyingisi uchun ASOS bo'ldi: embedding'siz cosine similarity
ma'nosiz (nimani solishtiramiz?), chunking'siz embedding foydasiz (butun
hujjat bitta "aralash" vektorga aylanadi), va vektor bazasi(pgvector/Chroma)
sizga bu operatsiyalarni QAYERDA saqlashni tanlashga yordam beradi. L6 —
shu zanjirning YAKUNIY natijasi: HAQIQIY, ishlaydigan, boshidan oxirigacha
kod.</p>

<h3>Keyingi darslarga ko'prik</h3>
<p>Keyingi darslarda (8-13) biz bu "qidiruv" qismini LLM chaqiruvi bilan
BIRLASHTIRAMIZ — ya'ni to'liq RAG pipeline (8-dars), token byudjeti
boshqaruvi chunked retrieval bilan (9-dars), suhbat xotirasi (10-dars), RAG
sifatini baholash (11-dars) va yakuniy capstone (13-dars). Shuning uchun bu
darsdagi amaliy vazifa keyingi darslar uchun ASOS bo'ladi — uni puxta
bajarib olish tavsiya etiladi.</p>
"""

L7_TEXT_RU = """
<h3>R1 — Урок повторения</h3>
<p>Это — урок повторения (review), поэтому здесь НЕТ новых понятий — мы
только собираем воедино всё, что изучили в уроках 0-6, и закрепляем это
через практическое задание. Поэтому текст намеренно короче, чем в других
уроках — основной фокус на практическом задании ниже.</p>

<h3>Что мы изучили в уроках 0-6</h3>
<ul>
<li><strong>L0:</strong> Что такое RAG и почему собственных знаний LLM
недостаточно — проблема галлюцинации и решение из трёх этапов
(retrieve-augment-generate).</li>
<li><strong>L1:</strong> Эмбеддинг — превращение текста в вектор чисел
всегда одинаковой длины; локальная модель против hosted API.</li>
<li><strong>L2:</strong> Chunking — разбиение документа на фрагменты для
поиска, overlap и стратегия structure-aware.</li>
<li><strong>L3:</strong> Cosine similarity — измерение угла между двумя
векторами, brute-force поиск.</li>
<li><strong>L4:</strong> Векторные базы — реальные компромиссы между
pgvector, Chroma, Pinecone.</li>
<li><strong>L5:</strong> Настройка pgvector — CREATE EXTENSION, столбец
vector, индекс HNSW, SQL-поиск.</li>
<li><strong>L6:</strong> Объединив всё, мы построили мини-систему
семантического поиска, работающую на РЕАЛЬНЫХ текстах уроков этой
платформы.</li>
</ul>

<h3>Почему этот порядок был важен</h3>
<p>Каждый урок стал ОСНОВОЙ для следующего: без эмбеддинга cosine
similarity бессмысленно (что сравнивать?), без chunking эмбеддинг
бесполезен (весь документ превращается в один "смешанный" вектор), а
векторная база (pgvector/Chroma) помогает выбрать, ГДЕ хранить эти
операции. L6 — итоговый результат этой цепочки: РЕАЛЬНЫЙ, работающий, код
от начала до конца.</p>

<h3>Мост к следующим урокам</h3>
<p>В следующих уроках (8-13) мы ОБЪЕДИНИМ эту часть "поиска" с вызовом LLM
— то есть полный RAG pipeline (урок 8), управление бюджетом токенов при
chunked retrieval (урок 9), память диалога (урок 10), оценка качества RAG
(урок 11) и финальный capstone (урок 13). Поэтому практическое задание в
этом уроке станет ОСНОВОЙ для следующих уроков — рекомендуется выполнить
его тщательно.</p>
"""

L7_TASK = {
    "task_title": "Mini-capstone: 3-so'rovli semantik qidiruv hisoboti",
    "task_title_ru": "Мини-капстоун: отчёт семантического поиска по 3 запросам",
    "task_description": (
        "L6'dagi to'liq pipeline'ni (build_search_index + semantic_search) "
        "ishlatib, 5 ta turli so'rov bilan qidiruv qiling. Har bir so'rov "
        "uchun top-3 natijani (dars ID, sarlavha, ball) va sizning "
        "fikringizcha natija to'g'ri yoki noto'g'ri ekanini yozing. Bu "
        "hisobot keyingi darslarda (RAG pipeline, sifat baholash) qayta "
        "ishlatiladi."
    ),
    "task_description_ru": (
        "Используя полный pipeline из L6 (build_search_index + "
        "semantic_search), выполните поиск по 5 разным запросам. Для "
        "каждого запроса запишите top-3 результата (ID урока, заголовок, "
        "балл) и своё мнение о том, верен ли результат. Этот отчёт "
        "будет использоваться повторно в следующих уроках (RAG pipeline, "
        "оценка качества)."
    ),
    "task_requirements": (
        "1) Aynan 5 ta so'rov ishlatilsin, turli mavzularda. 2) Har biri "
        "uchun top-3 natija va ball chiqarilsin. 3) Har bir so'rov uchun "
        "kamida bitta jumlali baho (to'g'ri/noto'g'ri va nega) yozilsin."
    ),
    "task_requirements_ru": (
        "1) Должно использоваться ровно 5 запросов на разные темы. 2) Для "
        "каждого выведены top-3 результата и балл. 3) Для каждого запроса "
        "написана минимум одна оценка-предложение (верно/неверно и "
        "почему)."
    ),
    "task_technologies": "Python, SQLAlchemy",
    "task_deadline_days": 5,
}

L7_SAMPLE = {
    "title": "Namuna: 0-6 darslardagi barcha funksiyalarni bitta faylda",
    "description": (
        "Embedding, chunking, cosine similarity va qidiruvni bitta "
        "kompakt modulda birlashtirgan qisqa recap."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "recap_pipeline.py",
            "language": "python",
            "code": (
                "import math\n\n\n"
                "def fake_embed(text, dims=32):\n"
                "    text = text.lower().strip()\n"
                "    vector = [0.0] * dims\n"
                "    for i, ch in enumerate(text):\n"
                "        vector[(ord(ch) + i) % dims] += 1.0\n"
                "    norm = math.sqrt(sum(v * v for v in vector)) or 1.0\n"
                "    return [v / norm for v in vector]\n\n\n"
                "def cosine_similarity(a, b):\n"
                "    dot = sum(x * y for x, y in zip(a, b))\n"
                "    mag_a = math.sqrt(sum(x * x for x in a))\n"
                "    mag_b = math.sqrt(sum(x * x for x in b))\n"
                "    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0\n\n\n"
                "# Recap: kichik \"mini baza\" ustida to'liq oqim\n"
                "mini_docs = {\n"
                "    \"Python asoslari\": \"funksiya def bilan e'lon qilinadi\",\n"
                "    \"CSS asoslari\": \"flexbox elementlarni tekislaydi\",\n"
                "}\n"
                "index = {name: fake_embed(text) for name, text in mini_docs.items()}\n\n"
                "query = \"funksiya qanday yoziladi\"\n"
                "qvec = fake_embed(query)\n"
                "ranked = sorted(index.items(), key=lambda kv: cosine_similarity(qvec, kv[1]), reverse=True)\n"
                "for name, vec in ranked:\n"
                "    print(f\"{cosine_similarity(qvec, vec):.4f}  {name}\")\n"
            ),
        },
    ],
}

L7_EXERCISES = [
    {
        "title": "Zanjirning asosi",
        "title_ru": "Основа цепочки",
        "description": "Chunking'siz embedding nega foydasiz bo'lib qoladi?",
        "description_ru": "Почему без chunking эмбеддинг становится бесполезным?",
        "exercise_type": "multiple_choice",
        "options": [
            "Butun hujjat bitta \"aralash\" vektorga aylanib, ma'no suyultiriladi",
            "Embedding umuman ishlamay qoladi",
            "Vektor hisoblanmaydi",
            "Narx keskin oshadi",
        ],
        "options_ru": [
            "Весь документ превращается в один 'смешанный' вектор, смысл размывается",
            "Эмбеддинг вообще перестаёт работать",
            "Вектор не вычисляется",
            "Цена резко возрастает",
        ],
        "correct_answers": "A",
        "hint": "2-darsdagi \"nega butun hujjatni bitta vektorga aylantirib bo'lmaydi\" bo'limini eslang.",
        "hint_ru": "Вспомните раздел 'почему нельзя превратить весь документ в один вектор' из урока 2.",
        "explanation": "Chunking'siz embedding butun hujjatning aralash o'rtacha ma'nosini ifodalaydi, bu qidiruv aniqligini pasaytiradi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "L0-L6 zanjiri",
        "title_ru": "Цепочка L0-L6",
        "description": "Darslarni to'g'ri tartibga joylashtiring (L0'dan L6'gacha mantiqiy ketma-ketlik)",
        "description_ru": "Расположите уроки в правильном порядке (логическая последовательность от L0 до L6)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "RAG nima va nega kerak (L0)",
            "Embedding — matnni vektorga aylantirish (L1)",
            "Chunking — hujjatni bo'laklarga bo'lish (L2)",
            "Cosine similarity — o'xshashlikni o'lchash (L3)",
            "Vektor bazasi tanlash va pgvector sozlash (L4-L5)",
            "Haqiqiy ma'lumot ustida to'liq qidiruv (L6)",
        ],
        "drag_items_ru": [
            "Что такое RAG и зачем он нужен (L0)",
            "Эмбеддинг — превращение текста в вектор (L1)",
            "Chunking — разбиение документа на фрагменты (L2)",
            "Cosine similarity — измерение сходства (L3)",
            "Выбор векторной базы и настройка pgvector (L4-L5)",
            "Полный поиск на реальных данных (L6)",
        ],
        "correct_order": [
            "RAG nima va nega kerak (L0)",
            "Embedding — matnni vektorga aylantirish (L1)",
            "Chunking — hujjatni bo'laklarga bo'lish (L2)",
            "Cosine similarity — o'xshashlikni o'lchash (L3)",
            "Vektor bazasi tanlash va pgvector sozlash (L4-L5)",
            "Haqiqiy ma'lumot ustida to'liq qidiruv (L6)",
        ],
        "hint": "Darsdagi ro'yxatni tartibda eslang.",
        "hint_ru": "Вспомните список из урока по порядку.",
        "difficulty_level": "Easy",
        "points": 6,
    },
    {
        "title": "Keyingi bosqich",
        "title_ru": "Следующий этап",
        "description": "Keyingi darslarda qidiruv (retrieval) qismi ___ chaqirig'i bilan birlashtirilib, to'liq RAG pipeline hosil qilinadi.",
        "description_ru": "В следующих уроках часть поиска (retrieval) будет объединена с вызовом ___, образуя полный RAG pipeline.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "LLM",
        "hint": "8-darsning nomini eslang: to'liq RAG pipeline.",
        "hint_ru": "Вспомните название урока 8: полный RAG pipeline.",
        "difficulty_level": "Easy",
        "points": 5,
    },
]

# ---------------------------------------------------------------------------
# Lesson 8 — To'liq RAG pipeline: retrieve -> augment -> generate
# ---------------------------------------------------------------------------

L8_TEXT = """
<h3>Endi haqiqiy RAG: qidiruv + LLM chaqiruvi</h3>
<p>R1 darsida biz qidiruv qismini (retrieve) mustahkamladik. Bu darsda esa
0-darsdan beri va'da qilingan narsani bajaramiz: qidiruv natijalarini LLM
chaqiruviga ulaymiz va HAQIQIY, to'liq RAG pipeline'ni quramiz. Muhim qoida:
LLM chaqirig'i uchun biz 135-kursdagi <code>call_chain()</code> funksiyasini
QAYTA ISHLATAMIZ — uni qaytadan yozmaymiz. Bu — kod takrorlanmasligi
(DRY) tamoyilining amaliy namunasi: fallback mantiq, xatolarni boshqarish,
provider tanlash — bularning barchasi allaqachon 135-kursda yozilgan va
sinovdan o'tgan.</p>

<h3>To'liq pipeline: uch funksiya</h3>
<p>RAG pipeline'ni uchta aniq funksiyaga bo'lish mumkin — har biri bitta
mas'uliyatga ega (single responsibility):</p>
<ol>
<li><strong>retrieve(query, index, k)</strong> — L6'dagi
<code>semantic_search</code>ning o'zi: so'rovga eng mos top-k chunk'ni
topadi.</li>
<li><strong>build_augmented_prompt(query, chunks)</strong> — topilgan
chunk'larni "MA'LUMOT:" bo'limi sifatida formatlab, LLM'ga aniq
ko'rsatma bilan birga promptga qo'shadi (0-darsdagi
<code>ask_with_manual_context</code>ning to'liq, avtomatlashtirilgan
shakli).</li>
<li><strong>generate(prompt)</strong> — 135-kursdagi
<code>call_chain()</code>ni chaqiradi; agar bitta provider ishlamasa,
avtomatik boshqasiga o'tadi (135-kursdagi fallback mantig'i o'zgarishsiz
ishlaydi).</li>
</ol>

<h3>Prompt qurish: nega aniq ko'rsatma muhim</h3>
<p>Shunchaki chunk'larni promptga "yopishtirib qo'yish" yetarli emas — LLM'ga
ANIQ ko'rsatma berish kerak: "faqat quyidagi ma'lumotdan foydalan",
"agar ma'lumotda javob bo'lmasa, shuni ayt, o'ylab topma". Bu ko'rsatmasiz
LLM baribir o'zining umumiy bilimini aralashtirib yuborishi mumkin — bu esa
RAG'ning butun maqsadini (faqat haqiqiy ma'lumotga tayanish) buzadi.</p>

<h3>To'liq RAG pipeline diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  Q["Foydalanuvchi so'rovi"]
  Q -->|"retrieve()"| IDX[("Xotiradagi indeks
(L6'dan)")]
  IDX -->|"top-K chunk"| CHUNKS["Topilgan chunk'lar"]
  CHUNKS -->|"build_augmented_prompt()"| PROMPT["To'liq prompt:
ko'rsatma + MA'LUMOT + SAVOL"]
  PROMPT -->|"generate()
call_chain() orqali
(135-kurs)"| CHAIN{"call_chain:
groq -> gemini -> openai"}
  CHAIN -->|"birinchi muvaffaqiyatli"| ANSWER["Haqiqiy ma'lumotga
asoslangan javob"]
</pre>
<p>Diqqat: <code>CHAIN</code> bloki — 135-kursda batafsil o'rgangan
zanjirning AYNAN O'ZI. Bu darsda biz uni qayta yozmaymiz, faqat import
qilib chaqiramiz.</p>

<h3>Nega bu "chin" RAG, oldingi darslardan farqi</h3>
<p>0-darsda biz qo'lda kontekst qo'shishni ko'rgandik (real_facts parametri
orqali). Bu yerdagi farq — kontekst endi QO'LDA emas, AVTOMATIK: har qanday
yangi savol uchun retrieve() avtomatik ravishda eng mos ma'lumotni topadi,
va bu jarayon kod ichida to'liq avtomatlashgan. Foydalanuvchi hech qachon
"qaysi hujjatni qo'shish kerak" deb o'ylashi shart emas — pipeline buni
o'zi hal qiladi.</p>

<h3>Xatolarni boshqarish: retrieve bo'sh qaytarsa nima bo'ladi</h3>
<p>Agar hech qanday mos chunk topilmasa (masalan juda past cosine ball),
pipeline LLM'ga "ma'lumot yo'q" prompt yubormasligi kerak — buning o'rniga
foydalanuvchiga to'g'ridan-to'g'ri "bu haqida ma'lumot topilmadi" deb
javob berish tavsiya etiladi. Bu — 135-kursdagi "graceful degradation"
tamoyilining RAG kontekstidagi ko'rinishi: LLM'ni chaqirmaslik ham,
noto'g'ri prompt yuborishdan ko'ra, ba'zan to'g'riroq yechim.</p>

<h3>Temperature: RAG uchun nega past qiymat afzal</h3>
<p>135-kursda <code>temperature</code> parametrini ko'rgan edingiz — RAG
kontekstida past temperature (masalan 0.1-0.3) ayniqsa muhim: RAG'ning
maqsadi — LLM'ni ijodkorlikka emas, berilgan MA'LUMOTGA sodiq qolishga
undash. Yuqori temperature (masalan 0.9) LLM'ni ko'proq "erkin" javob
berishga undaydi — bu esa aynan RAG'ning oldini olishga harakat qilayotgan
narsa (ma'lumotdan chetga chiqib, o'ylab topish). Shuning uchun
<code>generate()</code> funksiyasida <code>call_chain()</code>ga past
temperature bilan chaqiruv yuborish tavsiya etiladi (135-kursdagi
<code>_call_groq</code>/<code>_call_gemini</code> allaqachon 0.3
standart qiymatini ishlatadi — bu RAG uchun ham mos boshlang'ich nuqta).</p>

<h3>Chuqurroq misol: bo'sh retrieval holatini qadam-baqadam kuzatish</h3>
<p>Keling, <code>min_score=0.3</code> chegarasi bilan aniq bir stsenariyni
qadam-baqadam ko'ramiz. Foydalanuvchi "kosmik kemalar qanday uchadi" deb
so'raydi. <code>retrieve()</code> baribir top-3 natijani QAYTARADI (chunki
u eng yuqori ballli 3 tani tanlaydi, ular qanchalik past ballli bo'lishidan
qat'iy nazar) — lekin ularning barchasining balli, aytaylik, 0.12-0.18
oralig'ida bo'lsin. <code>min_score=0.3</code> filtri ULARNING BARCHASINI
chiqarib tashlaydi, natijada <code>chunks</code> ro'yxati BO'SH qoladi. Aynan
shu yerda <code>rag_answer()</code>dagi <code>if not chunks:</code> tekshiruvi
ishga tushadi — LLM chaqirilmaydi, foydalanuvchiga darhol halol javob
qaytariladi.</p>
<p>Bu yerda muhim amaliy savol tug'iladi: <code>min_score</code> chegarasini
QANDAY tanlash kerak? Juda YUQORI chegara (masalan 0.6) haqiqatan mos
bo'lgan, lekin sal past ballli chunk'larni ham rad etib, foydali javob
o'rniga keraksiz "topilmadi" xabarini ko'paytirib yuborishi mumkin. Juda
PAST chegara (masalan 0.05) esa deyarli hech qachon bo'sh natija bermaydi
— lekin bu ayni 6-darsda ko'rgan "Pozitsiyalash va Z-index" kabi mavzuga
umuman aloqasi yo'q chunk'larni ham LLM'ga yuborishga olib keladi.
Amaliyotda bu chegara qattiq formula bilan emas, balki L11'dagi golden set
orqali TAJRIBA asosida sozlanadi — turli chegara qiymatlari bilan sinab,
qaysi biri eng kam noto'g'ri-ijobiy (false positive) va noto'g'ri-manfiy
(false negative) berishini o'lchab.</p>
"""

L8_TEXT_RU = """
<h3>Теперь настоящий RAG: поиск + вызов LLM</h3>
<p>В уроке R1 мы закрепили часть поиска (retrieve). В этом уроке мы
выполняем то, что было обещано с урока 0: подключаем результаты поиска к
вызову LLM и строим РЕАЛЬНЫЙ, полный RAG pipeline. Важное правило: для
вызова LLM мы ПОВТОРНО ИСПОЛЬЗУЕМ функцию <code>call_chain()</code> из
курса 135 — не переписываем её заново. Это — практический пример принципа
неповторения кода (DRY): логика fallback, обработка ошибок, выбор
провайдера — всё это уже написано и проверено в курсе 135.</p>

<h3>Полный pipeline: три функции</h3>
<p>RAG pipeline можно разделить на три чёткие функции — каждая с одной
ответственностью (single responsibility):</p>
<ol>
<li><strong>retrieve(query, index, k)</strong> — та же
<code>semantic_search</code> из L6: находит top-k фрагментов, наиболее
подходящих запросу.</li>
<li><strong>build_augmented_prompt(query, chunks)</strong> — форматирует
найденные фрагменты как раздел "ДАННЫЕ:" и добавляет их в промпт вместе с
чёткой инструкцией для LLM (полная, автоматизированная форма
<code>ask_with_manual_context</code> из урока 0).</li>
<li><strong>generate(prompt)</strong> — вызывает <code>call_chain()</code>
из курса 135; если один провайдер не работает, автоматически переключается
на другого (логика fallback из курса 135 работает без изменений).</li>
</ol>

<h3>Построение промпта: почему важна чёткая инструкция</h3>
<p>Просто "приклеить" фрагменты в промпт недостаточно — LLM нужно дать
ЧЁТКУЮ инструкцию: "используй только следующие данные", "если в данных нет
ответа, скажи об этом, не выдумывай". Без этой инструкции LLM всё равно
может смешать свои общие знания — а это нарушает саму цель RAG (опираться
только на реальные данные).</p>

<h3>Диаграмма полного RAG pipeline</h3>
<pre class="mermaid">
flowchart TB
  Q["Запрос пользователя"]
  Q -->|"retrieve()"| IDX[("Индекс в памяти
(из L6)")]
  IDX -->|"top-K фрагментов"| CHUNKS["Найденные фрагменты"]
  CHUNKS -->|"build_augmented_prompt()"| PROMPT["Полный промпт:
инструкция + ДАННЫЕ + ВОПРОС"]
  PROMPT -->|"generate()
через call_chain()
(курс 135)"| CHAIN{"call_chain:
groq -> gemini -> openai"}
  CHAIN -->|"первый успешный"| ANSWER["Ответ на основе
реальных данных"]
</pre>
<p>Внимание: блок <code>CHAIN</code> — это ТА ЖЕ САМАЯ цепочка, что мы
подробно изучали в курсе 135. В этом уроке мы её не переписываем, а только
импортируем и вызываем.</p>

<h3>Почему это "настоящий" RAG, отличие от предыдущих уроков</h3>
<p>В уроке 0 мы видели ручное добавление контекста (через параметр
real_facts). Отличие здесь — контекст теперь добавляется не ВРУЧНУЮ, а
АВТОМАТИЧЕСКИ: для любого нового вопроса retrieve() автоматически находит
наиболее подходящую информацию, и весь этот процесс полностью
автоматизирован в коде. Пользователю никогда не нужно думать "какой
документ добавить" — pipeline решает это сам.</p>

<h3>Обработка ошибок: что если retrieve вернёт пусто</h3>
<p>Если не найдено ни одного подходящего фрагмента (например, слишком
низкий балл cosine), pipeline не должен отправлять LLM промпт "данных нет"
— вместо этого рекомендуется сразу ответить пользователю "информация по
этому вопросу не найдена". Это — проявление принципа "graceful
degradation" из курса 135 в контексте RAG: иногда не вызывать LLM — более
правильное решение, чем отправлять неверный промпт.</p>

<h3>Temperature: почему для RAG предпочтительно низкое значение</h3>
<p>В курсе 135 вы видели параметр <code>temperature</code> — в контексте
RAG низкая temperature (например 0.1-0.3) особенно важна: цель RAG —
побудить LLM не к творчеству, а к верности предоставленным ДАННЫМ. Высокая
temperature (например 0.9) побуждает LLM отвечать более "свободно" — а это
именно то, что RAG пытается предотвратить (отход от данных, выдумывание).
Поэтому в функции <code>generate()</code> рекомендуется вызывать
<code>call_chain()</code> с низкой temperature (в курсе 135
<code>_call_groq</code>/<code>_call_gemini</code> уже используют
стандартное значение 0.3 — это подходящая отправная точка и для RAG).</p>

<h3>Более глубокий пример: пошаговый разбор пустого retrieval</h3>
<p>Разберём пошагово конкретный сценарий с порогом <code>min_score=0.3</code>.
Пользователь спрашивает "как летают космические корабли".
<code>retrieve()</code> всё равно ВЕРНЁТ top-3 результата (потому что она
выбирает 3 с наивысшим баллом, независимо от того, насколько они низкие)
— но балл каждого из них, скажем, окажется в диапазоне 0.12-0.18.
Порог <code>min_score=0.3</code> ОТБРОСИТ их ВСЕ, и в результате список
<code>chunks</code> останется ПУСТЫМ. Именно здесь срабатывает проверка
<code>if not chunks:</code> в <code>rag_answer()</code> — LLM не
вызывается, пользователю сразу возвращается честный ответ.</p>
<p>Здесь возникает важный практический вопрос: КАК выбрать порог
<code>min_score</code>? Слишком ВЫСОКИЙ порог (например 0.6) может
отклонить и действительно подходящие, но чуть менее релевантные
фрагменты, увеличивая число ненужных сообщений "не найдено" вместо
полезного ответа. Слишком НИЗКИЙ порог (например 0.05) почти никогда не
даёт пустой результат — но это приводит к отправке в LLM фрагментов,
вообще не относящихся к теме, как в примере "Позиционирование и Z-index"
из урока 6. На практике этот порог настраивается не жёсткой формулой, а
ЭКСПЕРИМЕНТАЛЬНО через golden set из урока 11 — пробуя разные значения
порога и измеряя, какое даёт меньше всего ложно-положительных (false
positive) и ложно-отрицательных (false negative) результатов.</p>
"""

L8_CODE = """
# To'liq RAG pipeline: retrieve -> augment -> generate. generate() qismi
# 135-kursdagi HAQIQIY call_chain()ni chaqiradi — qayta yozilmaydi.

from __future__ import annotations
import math

from app.services.grok_ai_client import call_chain, ProviderError


# --- L6'dan: retrieve uchun kerakli funksiyalar ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        vector[(ord(ch) + i) % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


def retrieve(query: str, index: list[dict], k: int = 3, min_score: float = 0.3) -> list[dict]:
    \"\"\"L6'dagi semantic_search'ning o'zi, faqat MIN_SCORE chegarasi
    qo'shilgan — juda past ballli (mos kelmaydigan) natijalarni chiqarib
    tashlaydi, shunda pipeline "hech narsa yo'q" holatini bilib oladi.\"\"\"
    query_vector = fake_embed(query)
    scored = [
        {**entry, "score": cosine_similarity(query_vector, entry["vector"])}
        for entry in index
    ]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return [e for e in scored[:k] if e["score"] >= min_score]


def build_augmented_prompt(query: str, chunks: list[dict]) -> str:
    \"\"\"Topilgan chunk'larni aniq ko'rsatma bilan promptga qo'shadi —
    0-darsdagi ask_with_manual_context'ning avtomatlashtirilgan shakli.\"\"\"
    context_block = "\\n\\n".join(
        f"[Dars #{c['lesson_id']} — {c['lesson_title']}]\\n{c['text']}"
        for c in chunks
    )
    return (
        "Quyidagi MA'LUMOT asosida savolga javob ber. Faqat shu ma'lumotdan "
        "foydalan. Agar javob ma'lumotda bo'lmasa, aniq ayt: "
        "'Bu haqida ma'lumot topilmadi' — o'ylab topma.\\n\\n"
        f"MA'LUMOT:\\n{context_block}\\n\\n"
        f"SAVOL: {query}"
    )


async def generate(prompt: str) -> str:
    \"\"\"135-kursdagi call_chain()ni AYNAN o'zi chaqiriladi — qayta
    yozilmaydi. ProviderError chiqsa, chaqiruvchi kod uni ushlab, foydalanuvchiga
    tushunarli xabar ko'rsatishi kerak (135-kursdagi graceful degradation).\"\"\"
    text, _, provider, attempts = await call_chain(prompt, max_tokens=400)
    return text


async def rag_answer(query: str, index: list[dict]) -> str:
    \"\"\"To'liq pipeline: retrieve -> augment -> generate. Agar retrieve
    hech narsa topmasa, LLM'ni umuman chaqirmaydi — noto'g'ri prompt
    yuborishdan ko'ra to'g'riroq yechim.\"\"\"
    chunks = retrieve(query, index, k=3)
    if not chunks:
        return "Kechirasiz, bu savolga tegishli ma'lumot platformada topilmadi."

    prompt = build_augmented_prompt(query, chunks)
    try:
        return await generate(prompt)
    except ProviderError as e:
        return f"AI xizmati vaqtincha ishlamayapti: {e}"


if __name__ == "__main__":
    # index — L6'dagi build_search_index() natijasi (bu yerda qisqartirilgan namuna):
    demo_index = [
        {"lesson_id": 7, "lesson_title": "4-dars Class id", "text": "Python'da funksiya def kalit so'zi bilan e'lon qilinadi.", "vector": fake_embed("funksiya def kalit so'zi bilan e'lon qilinadi")},
    ]
    import asyncio
    print(asyncio.run(rag_answer("Python'da funksiya qanday e'lon qilinadi?", demo_index)))
"""

L8_CODE_RU = """
# Полный RAG pipeline: retrieve -> augment -> generate. Часть generate()
# вызывает РЕАЛЬНУЮ call_chain() из курса 135 — не переписывается заново.

from __future__ import annotations
import math

from app.services.grok_ai_client import call_chain, ProviderError


# --- из L6: функции, нужные для retrieve ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        vector[(ord(ch) + i) % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


def retrieve(query: str, index: list[dict], k: int = 3, min_score: float = 0.3) -> list[dict]:
    \"\"\"Та же semantic_search из L6, но с добавленным порогом MIN_SCORE
    — отбрасывает результаты со слишком низким баллом (не подходящие),
    чтобы pipeline мог распознать ситуацию 'ничего не найдено'.\"\"\"
    query_vector = fake_embed(query)
    scored = [
        {**entry, "score": cosine_similarity(query_vector, entry["vector"])}
        for entry in index
    ]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return [e for e in scored[:k] if e["score"] >= min_score]


def build_augmented_prompt(query: str, chunks: list[dict]) -> str:
    \"\"\"Добавляет найденные фрагменты в промпт с чёткой инструкцией —
    автоматизированная форма ask_with_manual_context из урока 0.\"\"\"
    context_block = "\\n\\n".join(
        f"[Урок #{c['lesson_id']} — {c['lesson_title']}]\\n{c['text']}"
        for c in chunks
    )
    return (
        "Ответь на вопрос, используя следующие ДАННЫЕ. Используй только эти "
        "данные. Если ответа в данных нет, честно скажи: 'Информация об "
        "этом не найдена' — не выдумывай.\\n\\n"
        f"ДАННЫЕ:\\n{context_block}\\n\\n"
        f"ВОПРОС: {query}"
    )


async def generate(prompt: str) -> str:
    \"\"\"Вызывается ИМЕННО call_chain() из курса 135 — не переписывается.
    При ProviderError вызывающий код должен поймать её и показать
    пользователю понятное сообщение (graceful degradation из курса 135).\"\"\"
    text, _, provider, attempts = await call_chain(prompt, max_tokens=400)
    return text


async def rag_answer(query: str, index: list[dict]) -> str:
    \"\"\"Полный pipeline: retrieve -> augment -> generate. Если retrieve
    ничего не находит, LLM вообще не вызывается — это правильнее, чем
    отправлять неверный промпт.\"\"\"
    chunks = retrieve(query, index, k=3)
    if not chunks:
        return "Извините, информация по этому вопросу на платформе не найдена."

    prompt = build_augmented_prompt(query, chunks)
    try:
        return await generate(prompt)
    except ProviderError as e:
        return f"Сервис AI временно недоступен: {e}"


if __name__ == "__main__":
    # index — результат build_search_index() из L6 (здесь сокращённый пример):
    demo_index = [
        {"lesson_id": 7, "lesson_title": "Урок про Class id", "text": "Функция в Python объявляется ключевым словом def.", "vector": fake_embed("функция объявляется ключевым словом def")},
    ]
    import asyncio
    print(asyncio.run(rag_answer("Как объявляется функция в Python?", demo_index)))
"""

L8_TASK = {
    "task_title": "To'liq RAG pipeline'ni ishga tushiring",
    "task_title_ru": "Запустите полный RAG pipeline",
    "task_description": (
        "L6'dagi `build_search_index`'ni va darsdagi `rag_answer`'ni "
        "birlashtirib, HAQIQIY ma'lumot ustida (lessons jadvali) to'liq "
        "RAG so'rovini bajaring. Kamida 2 ta savol bilan sinang: bittasi "
        "platformada mavjud mavzu haqida, bittasi platformada UMUMAN "
        "yo'q mavzu haqida (masalan \"kosmik kemalar qanday uchadi\") — "
        "ikkinchisida `rag_answer` \"ma'lumot topilmadi\" javobini "
        "berishi kerak."
    ),
    "task_description_ru": (
        "Объединив `build_search_index` из L6 и `rag_answer` из урока, "
        "выполните полный RAG-запрос на РЕАЛЬНЫХ данных (таблица lessons). "
        "Проверьте минимум на 2 вопросах: один — по теме, реально "
        "существующей на платформе, второй — по теме, которой на "
        "платформе ВООБЩЕ нет (например, \"как летают космические "
        "корабли\") — во втором случае `rag_answer` должна ответить "
        "'информация не найдена'."
    ),
    "task_requirements": (
        "1) Haqiqiy build_search_index ishlatilsin. 2) Kamida 2 savol "
        "sinalsin (bo'lgan mavzu + yo'q mavzu). 3) Ikkinchi savol uchun "
        "LLM chaqirilmasligini (yoki 'ma'lumot topilmadi' javobi "
        "qaytarilishini) tekshirib ko'rsating."
    ),
    "task_requirements_ru": (
        "1) Должна использоваться реальная build_search_index. 2) "
        "Проверено минимум 2 вопроса (существующая тема + отсутствующая). "
        "3) Для второго вопроса показано, что LLM не вызывается (или "
        "возвращается ответ 'информация не найдена')."
    ),
    "task_technologies": "Python, SQLAlchemy, httpx",
    "task_deadline_days": 5,
}

L8_SAMPLE = {
    "title": "Namuna: retrieve + augment, generate'siz (offline test)",
    "description": (
        "LLM chaqiruvisiz (API kaliti kerak emas) retrieve va prompt "
        "qurish qismini sinash — CI/test muhitida foydali pattern."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "test_retrieve_augment.py",
            "language": "python",
            "code": (
                "import math\n\n\n"
                "def fake_embed(text, dims=32):\n"
                "    text = text.lower().strip()\n"
                "    vector = [0.0] * dims\n"
                "    for i, ch in enumerate(text):\n"
                "        vector[(ord(ch) + i) % dims] += 1.0\n"
                "    norm = math.sqrt(sum(v * v for v in vector)) or 1.0\n"
                "    return [v / norm for v in vector]\n\n\n"
                "def cosine_similarity(a, b):\n"
                "    dot = sum(x * y for x, y in zip(a, b))\n"
                "    mag_a = math.sqrt(sum(x * x for x in a))\n"
                "    mag_b = math.sqrt(sum(x * x for x in b))\n"
                "    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0\n\n\n"
                "def retrieve(query, index, k=3, min_score=0.3):\n"
                "    qv = fake_embed(query)\n"
                "    scored = [{**e, 'score': cosine_similarity(qv, e['vector'])} for e in index]\n"
                "    scored.sort(key=lambda e: e['score'], reverse=True)\n"
                "    return [e for e in scored[:k] if e['score'] >= min_score]\n\n\n"
                "def build_augmented_prompt(query, chunks):\n"
                "    ctx = '\\n\\n'.join(f\"[{c['lesson_title']}]\\n{c['text']}\" for c in chunks)\n"
                "    return f\"MA'LUMOT:\\n{ctx}\\n\\nSAVOL: {query}\"\n\n\n"
                "if __name__ == '__main__':\n"
                "    index = [\n"
                "        {'lesson_id': 1, 'lesson_title': 'Python funksiyalari', 'text': \"def bilan e'lon qilinadi\", 'vector': fake_embed(\"def bilan e'lon qilinadi\")},\n"
                "    ]\n"
                "    chunks = retrieve(\"funksiya qanday yoziladi\", index)\n"
                "    print(build_augmented_prompt(\"funksiya qanday yoziladi\", chunks))\n"
            ),
        },
    ],
}

L8_EXERCISES = [
    {
        "title": "RAG pipeline'ning uchta funksiyasi",
        "title_ru": "Три функции RAG pipeline",
        "description": "Bosqichlarni to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": ["retrieve()", "build_augmented_prompt()", "generate()"],
        "drag_items_ru": ["retrieve()", "build_augmented_prompt()", "generate()"],
        "correct_order": ["retrieve()", "build_augmented_prompt()", "generate()"],
        "hint": "Darsdagi uch bosqichni eslang: qidirish, boyitish, generatsiya.",
        "hint_ru": "Вспомните три этапа из урока: поиск, дополнение, генерация.",
        "difficulty_level": "Easy",
        "points": 6,
    },
    {
        "title": "call_chain qayta ishlatiladi",
        "title_ru": "call_chain используется повторно",
        "description": "Bu darsda generate() funksiyasi qaysi kursning qaysi funksiyasini QAYTA ISHLATADI (qaytadan yozmasdan)?",
        "description_ru": "В этом уроке функция generate() ПОВТОРНО ИСПОЛЬЗУЕТ (не переписывая) какую функцию из какого курса?",
        "exercise_type": "multiple_choice",
        "options": [
            "135-kursdagi call_chain() funksiyasini",
            "O'zining yangi LLM klientini",
            "Gemini'ning rasmiy SDK'sini",
            "133-kursdagi boshqa funksiyani",
        ],
        "options_ru": [
            "Функцию call_chain() из курса 135",
            "Свой новый LLM-клиент",
            "Официальный SDK Gemini",
            "Другую функцию из курса 133",
        ],
        "correct_answers": "A",
        "hint": "Darsning boshida aytilgan DRY tamoyilini eslang.",
        "hint_ru": "Вспомните принцип DRY, упомянутый в начале урока.",
        "explanation": "generate() 135-kursdagi call_chain()ni import qilib chaqiradi — fallback mantiqni qaytadan yozmaydi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Aniq ko'rsatma zarurati",
        "title_ru": "Необходимость чёткой инструкции",
        "description": "Prompt qurishda LLM'ga aniq ko'rsatma (\"faqat ma'lumotdan foydalan\") bermasak, nima xavfi bor?",
        "description_ru": "Какая опасность, если при построении промпта не дать LLM чёткую инструкцию ('используй только данные')?",
        "exercise_type": "multiple_choice",
        "options": [
            "LLM o'zining umumiy bilimini aralashtirib, RAG'ning maqsadini buzishi mumkin",
            "Kod xato beradi",
            "Prompt juda qisqa bo'lib qoladi",
            "Hech qanday xavf yo'q",
        ],
        "options_ru": [
            "LLM может смешать свои общие знания, нарушив саму цель RAG",
            "Код выдаст ошибку",
            "Промпт станет слишком коротким",
            "Никакой опасности нет",
        ],
        "correct_answers": "A",
        "hint": "RAG'ning maqsadi nima edi — faqat qanday ma'lumotga tayanish?",
        "hint_ru": "Какова была цель RAG — опираться только на какие данные?",
        "explanation": "Aniq ko'rsatmasiz LLM o'z umumiy bilimidan foydalanishi mumkin, bu esa gallyutsinatsiya xavfini qaytarib olib keladi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Retrieve bo'sh natija berganda",
        "title_ru": "Когда retrieve возвращает пусто",
        "description": "Agar retrieve() hech qanday mos chunk topmasa, pipeline nima qilishi ___ (bitta so'z: LLM'ni chaqirish yoki chaqirmaslik)?",
        "description_ru": "Если retrieve() не находит ни одного подходящего фрагмента, что должен сделать pipeline — ___ LLM (одно слово: вызвать или не вызывать)?",
        "exercise_type": "fill_in_blank",
        "correct_answers": "chaqirmasligi",
        "correct_answers_ru": "не вызывать",
        "hint": "Darsdagi graceful degradation bo'limini eslang.",
        "hint_ru": "Вспомните раздел про graceful degradation из урока.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 9 — Kontekst oynasi va prompt byudjeti chunked retrieval bilan
# ---------------------------------------------------------------------------

L9_TEXT = """
<h3>135-kursdagi token byudjetini eslang</h3>
<p>135-kursning token byudjeti darsida siz <code>max_tokens</code>ning narx
va tezlikka ta'sirini, hamda bu platformaning haqiqiy kod bazasida
<code>explain_word_with_ai()</code> kabi funksiyalar <code>max_tokens=1000</code>
qattiq belgilanganini ko'rgan edingiz. RAG'da yangi muammo qo'shiladi:
endi promptga nafaqat foydalanuvchi savoli, balki QIDIRUV orqali topilgan
chunk'lar HAM kiradi — va bu chunk'lar hajmi o'zgaruvchan (1 ta chunk yoki
10 ta chunk bo'lishi mumkin).</p>

<h3>Context window — qattiq chegara</h3>
<p>Har bir LLM modelining context window'i bor — bu bitta so'rovda
qabul qilinadigan JAMI token miqdori (prompt + kutilayotgan javob). Agar
siz juda ko'p chunk qo'shsangiz (masalan 20 ta, har biri 500 token bo'lsa
— 10,000 token), context window'dan oshib ketishi yoki (agar oshmasa ham)
narx keskin ko'tarilishi mumkin. Shuning uchun RAG pipeline'da
<strong>nechta chunk qo'shish</strong> (top-K qiymati) — bu shunchaki
"K=3 yaxshi tuyuladi" degan tasodifiy tanlov emas, balki ANIQ hisob-kitobga
asoslangan qaror bo'lishi kerak.</p>

<h3>"Lost in the middle" muammosi — 2-darsdan eslatma</h3>
<p>2-darsda aytgan edik: uzun kontekstda LLM ko'pincha o'rtadagi ma'lumotni
e'tibordan chetda qoldiradi. Bu RAG uchun muhim oqibatga ega: ko'proq
chunk qo'shish HAR DOIM yaxshiroq javob demak EMAS — ba'zida 3 ta ANIQ
mos chunk 10 ta "yarim mos" chunk'dan yaxshiroq natija beradi, chunki LLM
diqqati tarqalmaydi.</p>

<h3>Token byudjetini hisoblash: amaliy formula</h3>
<p>Oddiy qoida: <code>jami_token_byudjeti = system_instruction_tokenlari +
sum(chunk_tokenlari) + savol_tokenlari + kutilayotgan_javob_tokenlari</code>.
Bu yig'indi modelning context window'idan (masalan ba'zi modellarda bir
necha ming token) kichik bo'lishi shart. Amaliy yondashuv: chunk'larni
COSINE BALLI bo'yicha saralab, YUQORIDAN pastga qarab qo'shib borish, har
safar joriy token hisobini tekshirib, byudjetga sig'maydigan chunk'ni
qo'shmaslik.</p>

<h3>Byudjet boshqaruvi diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  CHUNKS["Saralangan chunk'lar
(cosine balliga ko'ra, eng yuqoridan)"]
  CHUNKS --> CHECK{"Joriy token yig'indisi +
keyingi chunk <= byudjet?"}
  CHECK -->|"Ha"| ADD["Chunk'ni promptga qo'shish"]
  ADD --> CHECK
  CHECK -->|"Yo'q"| STOP["To'xtatish — qolgan chunk'lar
tashlab yuboriladi"]
  STOP --> FINAL["Yakuniy prompt: byudjet ichida,
eng mos chunk'lar bilan"]
</pre>

<h3>Taxminiy token hisoblash: aniq kutubxonasiz</h3>
<p>Aniq token hisoblash uchun modelning o'z tokenizatorini (masalan
<code>tiktoken</code> OpenAI uchun) ishlatish kerak — lekin tez, taxminiy
baholash uchun keng tarqalgan qoida: <strong>ingliz tilida taxminan 4
belgi = 1 token</strong> (o'zbek/rus tilida bu nisbat biroz farq qilishi
mumkin, chunki kirill/lotin belgilari boshqacha tokenlashishi mumkin —
shuning uchun bu FAQAT taxminiy baholash, aniq hisob emas). Production
kodda har doim modelning haqiqiy javobidagi <code>usage.total_tokens</code>
maydonini tekshirish kerak (135-kursda ko'rgan haqiqiy javob shaklini
eslang).</p>

<h3>Nega bu RAG'ga xos muammo</h3>
<p>Oddiy (RAG'siz) LLM chaqiruvida token byudjeti nisbatan barqaror — siz
promptni o'zingiz yozasiz va uning uzunligini nazorat qilasiz. RAG'da esa
prompt hajmi QIDIRUV NATIJASIGA bog'liq — har xil savol har xil sonli va
uzunlikdagi chunk qaytarishi mumkin. Shuning uchun RAG pipeline HAR DOIM
dinamik token byudjeti nazoratiga ega bo'lishi kerak — 135-kursdagi statik
<code>max_tokens=1000</code> kabi qattiq raqamlar yetarli emas.</p>

<h3>Providerlar orasidagi farq</h3>
<p>135-kursda ko'rganingizdek, <code>call_chain()</code> bir nechta
provider orasida almashadi (Groq, Gemini, OpenAI). Muhim eslatma: har bir
provider/modelning context window'i BOSHQACHA bo'lishi mumkin — bitta
modelda ishlagan token byudjeti boshqasida context window'dan oshib
ketishi mumkin. Shuning uchun token byudjeti hisob-kitobini "eng
KICHIK" context window'ga ega providerga mo'ljallab qilish xavfsizroq —
aks holda fallback ketma-ketligida keyingi provider'ga o'tganda kutilmagan
xato chiqishi mumkin.</p>

<h3>Qo'lda hisoblangan aniq misol: raqamlar bilan</h3>
<p>Quyidagi kod bo'limidagi <code>ranked_chunks</code> ro'yxati bilan qadam-
baqadam hisoblab ko'ramiz. To'rtta chunk mavjud: 800, 1200, 2000 va 400
belgidan iborat. <code>estimate_tokens</code> qoidasi bo'yicha (~4 belgi =
1 token) bular mos ravishda ~200, ~300, ~500 va ~100 tokenga teng.
<code>reserved_for_answer=300</code> va <code>reserved_for_instruction=60</code>
standart qiymatlari bilan, <code>token_budget=700</code> bo'lganda:
<code>available = 700 - 300 - 60 = 340</code> token. Birinchi chunk (200
token) qo'shiladi: <code>used = 200</code> (340 dan kichik, sig'adi).
Ikkinchi chunk (300 token) qo'shilsa: <code>200 + 300 = 500</code> — bu 340
dan KATTA, shuning uchun ALGORITM TO'XTAYDI va faqat 1 ta chunk byudjetga
sig'adi. Endi <code>token_budget=2000</code> bilan solishtiramiz:
<code>available = 2000 - 360 = 1640</code>. Barcha to'rtta chunk ketma-ket
qo'shilganda: <code>200 -&gt; 500 -&gt; 1000 -&gt; 1100</code> — barchasi
1640 dan kichik, demak BARCHA 4 ta chunk sig'adi. Bu misol shuni ko'rsatadi:
bir xil chunk to'plami, ikki xil byudjet — butunlay boshqa natija.</p>
"""

L9_TEXT_RU = """
<h3>Вспомним бюджет токенов из курса 135</h3>
<p>В уроке про бюджет токенов курса 135 вы видели влияние
<code>max_tokens</code> на цену и скорость, а также что в реальной
кодовой базе этой платформы функции вроде
<code>explain_word_with_ai()</code> имеют жёстко заданное
<code>max_tokens=1000</code>. В RAG добавляется новая проблема: теперь в
промпт входит не только вопрос пользователя, но и фрагменты, найденные
ПОИСКОМ — а их объём переменный (может быть 1 фрагмент, а может быть 10).</p>

<h3>Context window — жёсткая граница</h3>
<p>У каждой модели LLM есть context window — это ОБЩЕЕ количество токенов,
принимаемых за один запрос (промпт + ожидаемый ответ). Если вы добавите
слишком много фрагментов (например 20, по 500 токенов каждый — 10 000
токенов), можно выйти за пределы context window или (даже если не выйти)
цена резко возрастёт. Поэтому в RAG pipeline <strong>сколько фрагментов
добавить</strong> (значение top-K) — это не случайный выбор "K=3 выглядит
неплохо", а решение, основанное на ТОЧНОМ расчёте.</p>

<h3>Проблема "lost in the middle" — напоминание из урока 2</h3>
<p>В уроке 2 мы говорили: в длинном контексте LLM часто упускает
информацию из середины. Это имеет важное следствие для RAG: добавление
большего числа фрагментов НЕ ВСЕГДА означает лучший ответ — иногда 3 точно
подходящих фрагмента дают лучший результат, чем 10 "наполовину подходящих",
потому что внимание LLM не рассеивается.</p>

<h3>Расчёт бюджета токенов: практическая формула</h3>
<p>Простое правило: <code>общий_бюджет_токенов = токены_системной_инструкции
+ sum(токены_фрагментов) + токены_вопроса +
токены_ожидаемого_ответа</code>. Эта сумма обязана быть меньше context
window модели (у некоторых моделей — несколько тысяч токенов). Практический
подход: отсортировать фрагменты по баллу cosine, добавлять СВЕРХУ ВНИЗ,
каждый раз проверяя текущий подсчёт токенов, не добавляя фрагмент, который
не помещается в бюджет.</p>

<h3>Диаграмма управления бюджетом</h3>
<pre class="mermaid">
flowchart TB
  CHUNKS["Отсортированные фрагменты
(по баллу cosine, сверху вниз)"]
  CHUNKS --> CHECK{"Текущая сумма токенов +
следующий фрагмент <= бюджет?"}
  CHECK -->|"Да"| ADD["Добавить фрагмент в промпт"]
  ADD --> CHECK
  CHECK -->|"Нет"| STOP["Остановка — оставшиеся
фрагменты отбрасываются"]
  STOP --> FINAL["Итоговый промпт: в рамках бюджета,
с наиболее подходящими фрагментами"]
</pre>

<h3>Приблизительный подсчёт токенов: без точной библиотеки</h3>
<p>Для точного подсчёта токенов нужен собственный токенизатор модели
(например <code>tiktoken</code> для OpenAI) — но для быстрой,
приблизительной оценки распространено правило: <strong>в английском
тексте примерно 4 символа = 1 токен</strong> (в узбекском/русском это
соотношение может немного отличаться, так как кириллические/латинские
символы токенизируются иначе — поэтому это ТОЛЬКО приблизительная оценка,
не точный расчёт). В production-коде всегда нужно проверять поле
<code>usage.total_tokens</code> реального ответа модели (вспомните
реальную форму ответа из курса 135).</p>

<h3>Почему это проблема, специфичная для RAG</h3>
<p>В обычном (без RAG) вызове LLM бюджет токенов относительно стабилен —
вы сами пишете промпт и контролируете его длину. В RAG же размер промпта
зависит от РЕЗУЛЬТАТА ПОИСКА — разные вопросы могут вернуть разное
количество и длину фрагментов. Поэтому RAG pipeline ВСЕГДА должен иметь
динамический контроль бюджета токенов — статичных чисел вроде
<code>max_tokens=1000</code> из курса 135 недостаточно.</p>

<h3>Различие между провайдерами</h3>
<p>Как вы видели в курсе 135, <code>call_chain()</code> переключается
между несколькими провайдерами (Groq, Gemini, OpenAI). Важное замечание:
context window у каждого провайдера/модели МОЖЕТ ОТЛИЧАТЬСЯ — бюджет
токенов, работавший на одной модели, может превысить context window на
другой. Поэтому безопаснее рассчитывать бюджет токенов, ориентируясь на
провайдера с САМЫМ МАЛЕНЬКИМ context window — иначе при переключении на
следующего провайдера в цепочке fallback может возникнуть неожиданная
ошибка.</p>

<h3>Расчёт вручную: конкретный пример с числами</h3>
<p>Посчитаем пошагово на списке <code>ranked_chunks</code> из блока кода
ниже. Есть четыре фрагмента длиной 800, 1200, 2000 и 400 символов. По
правилу <code>estimate_tokens</code> (~4 символа = 1 токен) это составляет
примерно 200, 300, 500 и 100 токенов соответственно. При стандартных
значениях <code>reserved_for_answer=300</code> и
<code>reserved_for_instruction=60</code>, при <code>token_budget=700</code>:
<code>available = 700 - 300 - 60 = 340</code> токенов. Первый фрагмент (200
токенов) добавляется: <code>used = 200</code> (меньше 340, помещается).
Если добавить второй фрагмент (300 токенов): <code>200 + 300 = 500</code>
— это БОЛЬШЕ 340, поэтому АЛГОРИТМ ОСТАНАВЛИВАЕТСЯ, и в бюджет помещается
только 1 фрагмент. Теперь сравним с <code>token_budget=2000</code>:
<code>available = 2000 - 360 = 1640</code>. При последовательном добавлении
всех четырёх фрагментов: <code>200 -&gt; 500 -&gt; 1000 -&gt; 1100</code> —
всё меньше 1640, значит помещаются ВСЕ 4 фрагмента. Этот пример
показывает: один и тот же набор фрагментов, два разных бюджета — совсем
разный результат.</p>
"""

L9_CODE = """
# Token byudjetini dinamik boshqarish: chunk'larni cosine balliga ko'ra
# saralab, byudjetga sig'guncha qo'shib borish.

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    \"\"\"Taxminiy token soni — aniq tokenizator o'rniga tezkor baholash
    (~4 belgi = 1 token). Production'da tiktoken kabi haqiqiy
    tokenizatordan foydalaning; bu FAQAT tezkor taxmin.\"\"\"
    return max(1, len(text) // 4)


def fit_chunks_to_budget(
    chunks: list[dict],
    *,
    token_budget: int,
    reserved_for_answer: int = 300,
    reserved_for_instruction: int = 60,
) -> list[dict]:
    \"\"\"Chunk'larni (allaqachon cosine balliga ko'ra saralangan deb
    faraz qilinadi) YUQORIDAN pastga qarab qo'shib boradi, har safar
    joriy token yig'indisini tekshirib. Byudjetga sig'maydigan chunk
    uchrasa — TO'XTAYDI (keyingi, balki balandroq ballli bo'lmagan
    chunk'larni ham sinab ko'rmaydi — bu chunk'lar allaqachon ball
    bo'yicha saralangani uchun keyingilari ham kamroq mos).\"\"\"
    available = token_budget - reserved_for_answer - reserved_for_instruction
    if available <= 0:
        raise ValueError("token_budget juda kichik — javob va ko'rsatma uchun joy qolmadi")

    selected: list[dict] = []
    used = 0
    for chunk in chunks:
        chunk_tokens = estimate_tokens(chunk["text"])
        if used + chunk_tokens > available:
            break
        selected.append(chunk)
        used += chunk_tokens
    return selected


if __name__ == "__main__":
    # Cosine balliga ko'ra allaqachon saralangan chunk'lar namunasi:
    ranked_chunks = [
        {"heading": "1", "text": "A" * 800, "score": 0.91},   # ~200 token
        {"heading": "2", "text": "B" * 1200, "score": 0.85},  # ~300 token
        {"heading": "3", "text": "C" * 2000, "score": 0.60},  # ~500 token
        {"heading": "4", "text": "D" * 400, "score": 0.40},   # ~100 token
    ]

    # Kichik byudjet (masalan 700 token) bilan sinaymiz:
    fitted = fit_chunks_to_budget(ranked_chunks, token_budget=700)
    print(f"Byudjet=700 tokenda {len(fitted)} ta chunk sig'di:")
    for c in fitted:
        print(f"  heading={c['heading']} score={c['score']} ~{estimate_tokens(c['text'])} token")

    # Kattaroq byudjet bilan solishtirish:
    fitted_big = fit_chunks_to_budget(ranked_chunks, token_budget=2000)
    print(f"\\nByudjet=2000 tokenda {len(fitted_big)} ta chunk sig'di.")
"""

L9_CODE_RU = """
# Динамическое управление бюджетом токенов: сортировка фрагментов по
# баллу cosine и добавление, пока помещается в бюджет.

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    \"\"\"Приблизительное число токенов — быстрая оценка вместо точного
    токенизатора (~4 символа = 1 токен). В production используйте
    настоящий токенизатор вроде tiktoken; это ТОЛЬКО быстрая оценка.\"\"\"
    return max(1, len(text) // 4)


def fit_chunks_to_budget(
    chunks: list[dict],
    *,
    token_budget: int,
    reserved_for_answer: int = 300,
    reserved_for_instruction: int = 60,
) -> list[dict]:
    \"\"\"Добавляет фрагменты (предполагается, что они уже отсортированы
    по баллу cosine) СВЕРХУ ВНИЗ, каждый раз проверяя текущую сумму
    токенов. При первом фрагменте, не помещающемся в бюджет —
    ОСТАНАВЛИВАЕТСЯ (не пробует следующие — так как фрагменты уже
    отсортированы по баллу, следующие тоже менее релевантны).\"\"\"
    available = token_budget - reserved_for_answer - reserved_for_instruction
    if available <= 0:
        raise ValueError("token_budget слишком мал — не остаётся места для ответа и инструкции")

    selected: list[dict] = []
    used = 0
    for chunk in chunks:
        chunk_tokens = estimate_tokens(chunk["text"])
        if used + chunk_tokens > available:
            break
        selected.append(chunk)
        used += chunk_tokens
    return selected


if __name__ == "__main__":
    # Пример фрагментов, уже отсортированных по баллу cosine:
    ranked_chunks = [
        {"heading": "1", "text": "A" * 800, "score": 0.91},   # ~200 токенов
        {"heading": "2", "text": "B" * 1200, "score": 0.85},  # ~300 токенов
        {"heading": "3", "text": "C" * 2000, "score": 0.60},  # ~500 токенов
        {"heading": "4", "text": "D" * 400, "score": 0.40},   # ~100 токенов
    ]

    # Пробуем с небольшим бюджетом (например 700 токенов):
    fitted = fit_chunks_to_budget(ranked_chunks, token_budget=700)
    print(f"При бюджете=700 токенов поместилось {len(fitted)} фрагментов:")
    for c in fitted:
        print(f"  heading={c['heading']} score={c['score']} ~{estimate_tokens(c['text'])} токенов")

    # Сравнение с большим бюджетом:
    fitted_big = fit_chunks_to_budget(ranked_chunks, token_budget=2000)
    print(f"\\nПри бюджете=2000 токенов поместилось {len(fitted_big)} фрагментов.")
"""

L9_TASK = {
    "task_title": "Token byudjetiga sig'dirish funksiyasini sinang",
    "task_title_ru": "Протестируйте функцию, укладывающуюся в бюджет токенов",
    "task_description": (
        "Darsdagi `fit_chunks_to_budget` funksiyasidan foydalanib, "
        "kamida 6 ta turli uzunlik va balldagi chunk bilan sinang. Kichik "
        "(masalan 500) va katta (masalan 3000) byudjet bilan solishtiring "
        "va nechta chunk sig'ganini, qaysilari tashlab yuborilganini "
        "chiqaring."
    ),
    "task_description_ru": (
        "Используя функцию `fit_chunks_to_budget` из урока, "
        "протестируйте минимум на 6 фрагментах разной длины и балла. "
        "Сравните с маленьким (например 500) и большим (например 3000) "
        "бюджетом, выведите, сколько фрагментов поместилось и какие "
        "были отброшены."
    ),
    "task_requirements": (
        "1) Kamida 6 ta chunk ishlatilsin. 2) Ikki xil byudjet bilan "
        "solishtirilsin. 3) Tashlab yuborilgan chunk'lar aniq "
        "ko'rsatilsin (masalan sarlavhasi bilan)."
    ),
    "task_requirements_ru": (
        "1) Должно использоваться минимум 6 фрагментов. 2) Сравнение с "
        "двумя разными бюджетами. 3) Отброшенные фрагменты явно указаны "
        "(например, по заголовку)."
    ),
    "task_technologies": "Python",
    "task_deadline_days": 4,
}

L9_SAMPLE = {
    "title": "Namuna: taxminiy token hisoblash solishtiruvi",
    "description": (
        "estimate_tokens funksiyasini turli uzunlikdagi matnlarda sinab, "
        "taxminiy natijani ko'rsatadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "estimate_demo.py",
            "language": "python",
            "code": (
                "def estimate_tokens(text: str) -> int:\n"
                "    return max(1, len(text) // 4)\n\n\n"
                "samples = [\n"
                "    \"Salom\",\n"
                "    \"Bu o'rtacha uzunlikdagi jumla, taxminan 50 belgi atrofida.\",\n"
                "    \"A\" * 2000,\n"
                "]\n\n"
                "for s in samples:\n"
                "    print(f\"{len(s):>5} belgi -> ~{estimate_tokens(s)} token\")\n"
            ),
        },
    ],
}

L9_EXERCISES = [
    {
        "title": "Context window nima",
        "title_ru": "Что такое context window",
        "description": "Context window nimani anglatadi?",
        "description_ru": "Что означает context window?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bitta so'rovda qabul qilinadigan jami token miqdorining chegarasi (prompt + javob)",
            "Modelning narxi",
            "API kaliti amal qilish muddati",
            "Serverning RAM hajmi",
        ],
        "options_ru": [
            "Граница общего количества токенов, принимаемых за один запрос (промпт + ответ)",
            "Цена модели",
            "Срок действия API-ключа",
            "Объём оперативной памяти сервера",
        ],
        "correct_answers": "A",
        "hint": "Bu — modelning \"bir martalik xotira\" chegarasi.",
        "hint_ru": "Это граница 'единовременной памяти' модели.",
        "explanation": "Context window — modelning bir so'rovda qabul qila oladigan jami token chegarasi.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "\"Lost in the middle\" oqibati",
        "title_ru": "Последствие 'lost in the middle'",
        "description": "Nima uchun ko'proq chunk qo'shish har doim yaxshiroq javob demak emas?",
        "description_ru": "Почему добавление большего числа фрагментов не всегда означает лучший ответ?",
        "exercise_type": "multiple_choice",
        "options": [
            "Uzun kontekstda LLM ko'pincha o'rtadagi ma'lumotni e'tibordan chetda qoldiradi",
            "Ko'proq chunk har doim xato beradi",
            "API buni umuman qabul qilmaydi",
            "Bu narxga umuman ta'sir qilmaydi",
        ],
        "options_ru": [
            "В длинном контексте LLM часто упускает информацию из середины",
            "Больше фрагментов всегда даёт ошибку",
            "API вообще не принимает это",
            "Это вообще не влияет на цену",
        ],
        "correct_answers": "A",
        "hint": "2-darsdagi \"lost in the middle\" atamasini eslang.",
        "hint_ru": "Вспомните термин 'lost in the middle' из урока 2.",
        "explanation": "\"Lost in the middle\" tufayli ortiqcha chunk qo'shish LLM diqqatini tarqatib, natijani yomonlashtirishi mumkin.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Taxminiy token qoidasi",
        "title_ru": "Правило приблизительного подсчёта токенов",
        "description": "Tezkor taxminlash uchun keng tarqalgan qoida: taxminan 4 ___ = 1 token.",
        "description_ru": "Для быстрой оценки распространено правило: примерно 4 ___ = 1 токен.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "belgi",
        "correct_answers_ru": "символа",
        "hint": "Bu — harflar/belgilar sonini nazarda tutadi.",
        "hint_ru": "Это про количество букв/символов.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Dinamik byudjet boshqaruvi bosqichlari",
        "title_ru": "Этапы динамического управления бюджетом",
        "description": "Bosqichlarni to'g'ri tartibga joylashtiring",
        "description_ru": "Расположите этапы в правильном порядке",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Chunk'larni cosine balliga ko'ra saralash",
            "Har bir chunk uchun taxminiy token sonini hisoblash",
            "Byudjetga sig'guncha yuqoridan pastga qo'shib borish",
            "Sig'maydigan chunk uchraganda to'xtatish",
        ],
        "drag_items_ru": [
            "Сортировка фрагментов по баллу cosine",
            "Подсчёт приблизительного числа токенов для каждого фрагмента",
            "Добавление сверху вниз, пока помещается в бюджет",
            "Остановка при первом не помещающемся фрагменте",
        ],
        "correct_order": [
            "Chunk'larni cosine balliga ko'ra saralash",
            "Har bir chunk uchun taxminiy token sonini hisoblash",
            "Byudjetga sig'guncha yuqoridan pastga qo'shib borish",
            "Sig'maydigan chunk uchraganda to'xtatish",
        ],
        "hint": "Darsdagi fit_chunks_to_budget funksiyasi mantig'ini eslang.",
        "hint_ru": "Вспомните логику функции fit_chunks_to_budget из урока.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 10 — Suhbat xotirasi: chat tarixi + retrieval
# ---------------------------------------------------------------------------

L10_TEXT = """
<h3>Muammo: har bir savol "yolg'iz" emas</h3>
<p>8-darsdagi <code>rag_answer()</code> funksiyasi har bir so'rovni ALOHIDA,
avvalgi suhbatni eslamasdan ishlaydi. Lekin haqiqiy chatbot suhbatida
foydalanuvchi ko'pincha oldingi javobga ISHORA qiladi: "Bu darsda nima
haqida gap ketadi?" -> javob keladi -> "Uning ikkinchi qismi-chi?". Ikkinchi
savolda "uning" so'zi nimani anglatishini bilish uchun BIRINCHI savol va
javobni "eslash" kerak. Bu — <strong>suhbat xotirasi</strong> muammosi.</p>

<h3>Ikki xil "xotira": chat tarixi vs retrieval</h3>
<p>RAG chatbotida ikki xil ma'lumot manbai bor, va ularni aralashtirib
yubormaslik kerak:</p>
<ul>
<li><strong>Chat tarixi (conversation history)</strong> — foydalanuvchi
bilan LLM orasidagi oldingi xabarlar ro'yxati. Bu — QISQA MUDDATLI xotira,
faqat shu suhbat davomida mavjud.</li>
<li><strong>Retrieval (qidiruv)</strong> — 6-8 darslarda ko'rgan, hujjatlar
bazasidan topilgan ma'lumot. Bu — UZOQ MUDDATLI, doimiy bilim manbai
(masalan platformaning barcha darslari).</li>
</ul>
<p>To'liq RAG chatbot ikkalasini ham promptga qo'shadi: "oldin nima
gaplashgan edik" (tarix) + "bu savolga tegishli haqiqiy ma'lumot" (retrieval).</p>

<h3>Muammo: savolni qanday qidirish kerak</h3>
<p>Agar foydalanuvchi "uning ikkinchi qismi-chi?" deb so'rasa-yu, buni
to'g'ridan-to'g'ri <code>retrieve()</code>ga yuborsak — "uning ikkinchi
qismi" iborasi hech qanday ma'noli embedding bermaydi (nimaning ekani
noaniq). Yechim: <strong>savolni qayta yozish (query rewriting)</strong> —
chat tarixidan foydalanib, savolni "to'liq, mustaqil" shaklga keltirish:
"CSS Flexbox darsining ikkinchi qismi nima haqida?" Bu qadam ko'pincha
LLM'ning o'ziga ("quyidagi suhbat tarixidan kelib chiqib, oxirgi savolni
to'liq, mustaqil savolga aylantir") ishonib topshiriladi.</p>

<h3>To'liq oqim: xotira + retrieval + generatsiya</h3>
<pre class="mermaid">
flowchart TB
  HIST[("Chat tarixi
(oldingi xabarlar)")]
  NEWQ["Yangi savol: 'uning ikkinchi qismi-chi?'"]
  HIST --> REWRITE["Savolni qayta yozish
(tarix asosida to'liq savol yasash)"]
  NEWQ --> REWRITE
  REWRITE --> FULLQ["To'liq savol: 'CSS Flexbox
darsining ikkinchi qismi nima haqida?'"]
  FULLQ --> RET["retrieve() — 8-darsdagi kabi"]
  RET --> AUG["build_augmented_prompt()
+ chat tarixi ham qo'shiladi"]
  AUG --> GEN["generate() — call_chain()"]
  GEN --> ANSWER["Javob"]
  ANSWER -->|"tarixga qo'shiladi"| HIST
</pre>

<h3>Xotira hajmini cheklash — 9-darsdagi bilim bilan bog'liq</h3>
<p>Chat tarixi CHEKSIZ o'sib bormaydi — uzoq suhbatda tarixning o'zi ham
token byudjetini yeyishi mumkin (9-darsda ko'rgan muammo aynan shu yerda
qaytadan paydo bo'ladi). Amaliy yechim: faqat OXIRGI N ta xabar juftligini
(masalan oxirgi 5 ta savol-javob) saqlash, undan eskisini "unutish". Bu —
production chatbotlarida keng qo'llaniladigan oddiy, amaliy kompromis.</p>

<h3>Nega bu alohida dars: retrieval'dan farqi</h3>
<p>E'tibor bering: chat tarixi HAM, retrieval HAM promptga "ma'lumot"
qo'shadi, lekin ular BOSHQA-BOSHQA muammoni hal qiladi — tarix "biz
nimalar haqida gaplashdik" savoliga, retrieval esa "haqiqatda nima
to'g'ri" savoliga javob beradi. Ikkalasini aralashtirib yuborish (masalan
tarixni "haqiqat manbai" sifatida ishlatish) xato natijaga olib kelishi
mumkin — LLM oldingi (balki noto'g'ri yoki eskirgan) javobini "haqiqat"
sifatida qayta ishlatishi mumkin.</p>

<h3>Xavfsizlik eslatmasi: xotirada nima saqlanadi</h3>
<p>135-kursdagi xavfsizlik darsini eslang: API kalitlari va maxfiy
ma'lumotlarni hech qachon promptga qattiq yozib qo'ymaslik kerak edi. Xuddi
shunday ehtiyotkorlik suhbat xotirasiga ham tegishli — agar foydalanuvchi
tasodifan shaxsiy yoki maxfiy ma'lumot yozsa (masalan parol yoki karta
raqami), bu <code>ConversationMemory</code> ichida saqlanib qoladi va
keyingi so'rovlarda promptga qayta yuborilishi mumkin. Production
tizimlarda bunday ma'lumotni suhbat xotirasidan avtomatik filtrlash yoki
foydalanuvchini ogohlantirish tavsiya etiladi — bu real xavfsizlik
masalasi, nazariy emas.</p>

<h3>Nosozlik holati: xotira cheksiz o'sib ketishi</h3>
<p><code>ConversationMemory.max_turns</code> chegarasi qo'yilmasa, nima
sodir bo'lishini ko'rib chiqamiz — bu haqiqiy production'da uchraydigan
nosozlik holati. Foydalanuvchi soatlab suhbatlashsa, <code>turns</code>
ro'yxati yuzlab yozuvga yetishi mumkin. Har bir yangi so'rovda BUTUN tarix
<code>as_history_text()</code> orqali promptga qo'shiladi — bu esa 9-darsda
ko'rgan token byudjeti muammosini keskinlashtiradi: tarixning o'zi
byudjetning katta qismini yeb qo'yib, retrieval'dan kelgan HAQIQIY
ma'lumotga joy qolmasligi mumkin. Yomonroq holatda, agar tarix context
window'dan oshib ketsa, LLM chaqiruvi butunlay xato bilan yakunlanadi.</p>

<h3>Ikki amaliy yechim: sliding window va xulosalash</h3>
<p>Bu nosozlikning ikkita keng tarqalgan yechimi bor. <strong>Sliding
window (siljiydigan oyna)</strong> — darsdagi <code>ConversationMemory</code>
allaqachon shu yondashuvni qo'llaydi: faqat OXIRGI <code>max_turns</code>
juftlikni saqlaydi, eskisini "unutadi". Bu oddiy va tezkor, lekin bir
kamchiligi bor — agar foydalanuvchi suhbatning BOSHIDA muhim narsa aytgan
bo'lsa (masalan ismini), oyna siljigach bu ma'lumot butunlay yo'qoladi.
Ikkinchi yondashuv — <strong>xulosalash (summarization)</strong>: eski
xabarlarni butunlay tashlab yuborish o'rniga, ularni LLM yordamida qisqa
xulosaga aylantirib, shu xulosani doimiy saqlash. Bu ko'proq token
sarflaydi (xulosalash uchun qo'shimcha LLM chaqiruvi kerak) va murakkabroq,
lekin uzoq muddatli kontekstni butunlay yo'qotmaydi. Amaliy loyihalarda
tanlov suhbatning tabiatiga bog'liq: qisqa, operatsion suhbatlar uchun
sliding window yetarli; uzoq, shaxsiylashtirilgan yordamchilar uchun
xulosalash ko'proq foyda beradi.</p>
"""

L10_TEXT_RU = """
<h3>Проблема: каждый вопрос не "одинок"</h3>
<p>Функция <code>rag_answer()</code> из урока 8 обрабатывает каждый запрос
ОТДЕЛЬНО, не помня предыдущий разговор. Но в реальном диалоге с чат-ботом
пользователь часто ССЫЛАЕТСЯ на предыдущий ответ: "О чём этот урок?" ->
приходит ответ -> "А что насчёт его второй части?". Чтобы понять, что
означает "его" во втором вопросе, нужно "помнить" первый вопрос и ответ.
Это — проблема <strong>памяти диалога</strong>.</p>

<h3>Два вида "памяти": история чата против retrieval</h3>
<p>В RAG-чат-боте есть два разных источника информации, и их нельзя
путать:</p>
<ul>
<li><strong>История чата (conversation history)</strong> — список
предыдущих сообщений между пользователем и LLM. Это — КРАТКОСРОЧНАЯ
память, существующая только в рамках этого диалога.</li>
<li><strong>Retrieval (поиск)</strong> — информация, найденная в базе
документов, как в уроках 6-8. Это — ДОЛГОСРОЧНЫЙ, постоянный источник
знаний (например, все уроки платформы).</li>
</ul>
<p>Полноценный RAG-чат-бот добавляет в промпт оба: "о чём говорили раньше"
(история) + "реальные данные по этому вопросу" (retrieval).</p>

<h3>Проблема: как искать по такому вопросу</h3>
<p>Если пользователь спрашивает "а что насчёт его второй части?", и мы
отправим это напрямую в <code>retrieve()</code> — фраза "его вторая часть"
не даст осмысленный эмбеддинг (неясно, чьё "его"). Решение:
<strong>переписывание запроса (query rewriting)</strong> — используя
историю чата, привести вопрос к "полной, самостоятельной" форме: "О чём
вторая часть урока про CSS Flexbox?" Этот шаг часто поручается самой LLM
("исходя из следующей истории диалога, преврати последний вопрос в полный,
самостоятельный вопрос").</p>

<h3>Полный поток: память + retrieval + генерация</h3>
<pre class="mermaid">
flowchart TB
  HIST[("История чата
(предыдущие сообщения)")]
  NEWQ["Новый вопрос: 'а что насчёт его второй части?'"]
  HIST --> REWRITE["Переписывание вопроса
(построение полного вопроса на основе истории)"]
  NEWQ --> REWRITE
  REWRITE --> FULLQ["Полный вопрос: 'О чём вторая
часть урока про CSS Flexbox?'"]
  FULLQ --> RET["retrieve() — как в уроке 8"]
  RET --> AUG["build_augmented_prompt()
+ также добавляется история чата"]
  AUG --> GEN["generate() — call_chain()"]
  GEN --> ANSWER["Ответ"]
  ANSWER -->|"добавляется в историю"| HIST
</pre>

<h3>Ограничение объёма памяти — связь со знаниями урока 9</h3>
<p>История чата НЕ растёт бесконечно — в длинном диалоге сама история
может "съедать" бюджет токенов (та же проблема из урока 9 возникает здесь
снова). Практическое решение: сохранять только ПОСЛЕДНИЕ N пар сообщений
(например последние 5 пар вопрос-ответ), "забывая" более старые. Это —
простой, практический компромисс, широко применяемый в production
чат-ботах.</p>

<h3>Почему это отдельный урок: отличие от retrieval</h3>
<p>Обратите внимание: и история чата, И retrieval добавляют "информацию" в
промпт, но они решают РАЗНЫЕ задачи — история отвечает на вопрос "о чём мы
говорили", а retrieval — на вопрос "что на самом деле верно". Их смешивание
(например, использование истории как "источника истины") может привести к
неверному результату — LLM может повторно использовать свой предыдущий
(возможно неверный или устаревший) ответ как "истину".</p>

<h3>Замечание по безопасности: что хранится в памяти</h3>
<p>Вспомните урок безопасности из курса 135: API-ключи и конфиденциальные
данные никогда нельзя жёстко вписывать в промпт. Та же осторожность
относится и к памяти диалога — если пользователь случайно напишет личную
или конфиденциальную информацию (например, пароль или номер карты), она
сохранится внутри <code>ConversationMemory</code> и может быть повторно
отправлена в промпт при следующих запросах. В production-системах
рекомендуется автоматически фильтровать такую информацию из памяти
диалога или предупреждать пользователя — это реальный вопрос
безопасности, а не теоретический.</p>

<h3>Сценарий сбоя: неограниченный рост памяти</h3>
<p>Рассмотрим, что произойдёт, если не установить ограничение
<code>ConversationMemory.max_turns</code> — это реальный сценарий сбоя,
встречающийся в production. Если пользователь общается часами, список
<code>turns</code> может достичь сотен записей. При каждом новом запросе
ВСЯ история добавляется в промпт через <code>as_history_text()</code> — а
это усугубляет проблему бюджета токенов из урока 9: сама история может
"съесть" большую часть бюджета, не оставив места для РЕАЛЬНЫХ данных из
retrieval. В худшем случае, если история превысит context window, вызов
LLM полностью завершится ошибкой.</p>

<h3>Два практических решения: sliding window и суммаризация</h3>
<p>У этой проблемы есть два распространённых решения. <strong>Sliding
window (скользящее окно)</strong> — <code>ConversationMemory</code> из
урока уже применяет этот подход: хранит только ПОСЛЕДНИЕ
<code>max_turns</code> пар, "забывая" более старые. Это просто и быстро,
но есть недостаток — если пользователь сказал что-то важное В НАЧАЛЕ
диалога (например, своё имя), после сдвига окна эта информация полностью
теряется. Второй подход — <strong>суммаризация (summarization)</strong>:
вместо полного отбрасывания старых сообщений, они с помощью LLM сжимаются
в краткое резюме, которое хранится постоянно. Это расходует больше
токенов (нужен дополнительный вызов LLM для суммаризации) и сложнее, но не
теряет долгосрочный контекст полностью. В реальных проектах выбор зависит
от природы диалога: для коротких, операционных разговоров достаточно
sliding window; для длинных, персонализированных ассистентов суммаризация
даёт больше пользы.</p>
"""

L10_CODE = """
# Suhbat xotirasi bilan RAG: chat tarixini saqlash, savolni qayta yozish
# (query rewriting) va 8-darsdagi rag_answer() bilan birlashtirish.

from __future__ import annotations
from dataclasses import dataclass, field

from app.services.grok_ai_client import call_chain, ProviderError


@dataclass(frozen=True)
class ChatTurn:
    \"\"\"Bitta savol-javob juftligi — immutable (o'zgarmas), 2-darsdagi
    kabi yangi holatni MUTATSIYA qilish o'rniga yangi nusxa yaratamiz.\"\"\"
    question: str
    answer: str


@dataclass(frozen=True)
class ConversationMemory:
    \"\"\"Suhbat xotirasi — faqat OXIRGI max_turns juftlikni saqlaydi.
    Immutable: add_turn() joriy obyektni o'zgartirmaydi, YANGI nusxa
    qaytaradi.\"\"\"
    turns: tuple[ChatTurn, ...] = field(default_factory=tuple)
    max_turns: int = 5

    def add_turn(self, question: str, answer: str) -> "ConversationMemory":
        new_turns = (*self.turns, ChatTurn(question, answer))
        if len(new_turns) > self.max_turns:
            new_turns = new_turns[-self.max_turns:]  # eng eskisini "unutish"
        return ConversationMemory(turns=new_turns, max_turns=self.max_turns)

    def as_history_text(self) -> str:
        if not self.turns:
            return "(hozircha suhbat tarixi yo'q)"
        return "\\n".join(f"Savol: {t.question}\\nJavob: {t.answer}" for t in self.turns)


async def rewrite_query(new_question: str, memory: ConversationMemory) -> str:
    \"\"\"Chat tarixidan foydalanib, "uning", "u" kabi ishoralarni
    to'liq, mustaqil savolga aylantiradi. Agar tarix bo'sh bo'lsa,
    LLM'ni chaqirmasdan savolni o'zgarishsiz qaytaradi (keraksiz
    chaqiruvdan saqlanish).\"\"\"
    if not memory.turns:
        return new_question

    prompt = (
        "Quyidagi suhbat tarixidan foydalanib, OXIRGI savolni to'liq, "
        "mustaqil (tarixsiz ham tushunarli) savolga qayta yoz. Faqat "
        "qayta yozilgan savolni qaytar, boshqa hech narsa yozma.\\n\\n"
        f"TARIX:\\n{memory.as_history_text()}\\n\\n"
        f"OXIRGI SAVOL: {new_question}"
    )
    rewritten, _, _, _ = await call_chain(prompt, max_tokens=100)
    return rewritten.strip() or new_question


async def chat_with_memory(new_question: str, memory: ConversationMemory, index: list[dict]) -> tuple[str, ConversationMemory]:
    \"\"\"To'liq oqim: savolni qayta yozish -> retrieve -> augment ->
    generate -> xotirani yangilash (yangi, immutable nusxa qaytariladi).\"\"\"
    from math import sqrt  # noqa: F401 — retrieve() 8-darsdagidek ishlatiladi deb faraz qilinadi

    full_question = await rewrite_query(new_question, memory)

    # 8-darsdagi retrieve/build_augmented_prompt shu yerda chaqiriladi deb faraz qilamiz:
    # chunks = retrieve(full_question, index)
    # prompt = build_augmented_prompt(full_question, chunks) + memory.as_history_text()
    prompt = f"TARIX:\\n{memory.as_history_text()}\\n\\nSAVOL: {full_question}"

    try:
        answer, _, _, _ = await call_chain(prompt, max_tokens=400)
    except ProviderError as e:
        answer = f"AI xizmati vaqtincha ishlamayapti: {e}"

    new_memory = memory.add_turn(new_question, answer)
    return answer, new_memory
"""

L10_CODE_RU = """
# RAG с памятью диалога: сохранение истории чата, переписывание вопроса
# (query rewriting) и объединение с rag_answer() из урока 8.

from __future__ import annotations
from dataclasses import dataclass, field

from app.services.grok_ai_client import call_chain, ProviderError


@dataclass(frozen=True)
class ChatTurn:
    \"\"\"Одна пара вопрос-ответ — immutable (неизменяемая), как в уроке 2
    мы создаём НОВУЮ копию вместо мутации текущего состояния.\"\"\"
    question: str
    answer: str


@dataclass(frozen=True)
class ConversationMemory:
    \"\"\"Память диалога — хранит только ПОСЛЕДНИЕ max_turns пар.
    Immutable: add_turn() не изменяет текущий объект, а возвращает
    НОВУЮ копию.\"\"\"
    turns: tuple[ChatTurn, ...] = field(default_factory=tuple)
    max_turns: int = 5

    def add_turn(self, question: str, answer: str) -> "ConversationMemory":
        new_turns = (*self.turns, ChatTurn(question, answer))
        if len(new_turns) > self.max_turns:
            new_turns = new_turns[-self.max_turns:]  # "забываем" самые старые
        return ConversationMemory(turns=new_turns, max_turns=self.max_turns)

    def as_history_text(self) -> str:
        if not self.turns:
            return "(истории диалога пока нет)"
        return "\\n".join(f"Вопрос: {t.question}\\nОтвет: {t.answer}" for t in self.turns)


async def rewrite_query(new_question: str, memory: ConversationMemory) -> str:
    \"\"\"Используя историю чата, превращает такие слова, как 'его', 'он',
    в полный, самостоятельный вопрос. Если история пуста, возвращает
    вопрос без изменений, не вызывая LLM (избегаем лишнего вызова).\"\"\"
    if not memory.turns:
        return new_question

    prompt = (
        "Используя следующую историю диалога, перепиши ПОСЛЕДНИЙ вопрос "
        "в полный, самостоятельный (понятный и без истории) вопрос. "
        "Верни только переписанный вопрос, ничего больше.\\n\\n"
        f"ИСТОРИЯ:\\n{memory.as_history_text()}\\n\\n"
        f"ПОСЛЕДНИЙ ВОПРОС: {new_question}"
    )
    rewritten, _, _, _ = await call_chain(prompt, max_tokens=100)
    return rewritten.strip() or new_question


async def chat_with_memory(new_question: str, memory: ConversationMemory, index: list[dict]) -> tuple[str, ConversationMemory]:
    \"\"\"Полный поток: переписывание вопроса -> retrieve -> augment ->
    generate -> обновление памяти (возвращается новая, immutable копия).\"\"\"
    from math import sqrt  # noqa: F401 — предполагается, что retrieve() используется как в уроке 8

    full_question = await rewrite_query(new_question, memory)

    # Предполагается, что здесь вызываются retrieve/build_augmented_prompt из урока 8:
    # chunks = retrieve(full_question, index)
    # prompt = build_augmented_prompt(full_question, chunks) + memory.as_history_text()
    prompt = f"ИСТОРИЯ:\\n{memory.as_history_text()}\\n\\nВОПРОС: {full_question}"

    try:
        answer, _, _, _ = await call_chain(prompt, max_tokens=400)
    except ProviderError as e:
        answer = f"Сервис AI временно недоступен: {e}"

    new_memory = memory.add_turn(new_question, answer)
    return answer, new_memory
"""

L10_TASK = {
    "task_title": "Ko'p bosqichli suhbatni sinang",
    "task_title_ru": "Протестируйте многошаговый диалог",
    "task_description": (
        "Darsdagi `ConversationMemory` va `chat_with_memory`'dan "
        "foydalanib, kamida 3 bosqichli suhbat qiling — ikkinchi va "
        "uchinchi savolda ataylab \"u\", \"uning\" kabi ishoralardan "
        "foydalaning (masalan avval \"Python funksiyalari haqida "
        "gapir\", keyin \"uning parametrlari haqida-chi?\"). "
        "`rewrite_query` bu ishoralarni qanday to'liq savolga "
        "aylantirganini ko'rsating."
    ),
    "task_description_ru": (
        "Используя `ConversationMemory` и `chat_with_memory` из урока, "
        "проведите диалог минимум из 3 шагов — во втором и третьем "
        "вопросе намеренно используйте ссылки вроде 'он', 'его' "
        "(например сначала 'расскажи про функции Python', затем 'а что "
        "насчёт его параметров?'). Покажите, как `rewrite_query` "
        "превратила эти ссылки в полный вопрос."
    ),
    "task_requirements": (
        "1) Kamida 3 bosqichli suhbat bo'lsin. 2) Kamida bitta savolda "
        "ishora so'z ishlatilsin. 3) rewrite_query natijasi (to'liq "
        "qayta yozilgan savol) konsolga chiqarilsin."
    ),
    "task_requirements_ru": (
        "1) Диалог должен состоять минимум из 3 шагов. 2) Минимум в "
        "одном вопросе должно быть слово-ссылка. 3) Результат "
        "rewrite_query (полностью переписанный вопрос) должен быть "
        "выведен в консоль."
    ),
    "task_technologies": "Python, httpx",
    "task_deadline_days": 5,
}

L10_SAMPLE = {
    "title": "Namuna: immutable xotira qanday ishlaydi",
    "description": (
        "ConversationMemory'ning immutable ekanligini — add_turn har "
        "doim YANGI nusxa qaytarishini ko'rsatadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "memory_immutability_demo.py",
            "language": "python",
            "code": (
                "from dataclasses import dataclass, field\n\n\n"
                "@dataclass(frozen=True)\n"
                "class ChatTurn:\n"
                "    question: str\n"
                "    answer: str\n\n\n"
                "@dataclass(frozen=True)\n"
                "class ConversationMemory:\n"
                "    turns: tuple = field(default_factory=tuple)\n"
                "    max_turns: int = 5\n\n"
                "    def add_turn(self, question, answer):\n"
                "        new_turns = (*self.turns, ChatTurn(question, answer))\n"
                "        if len(new_turns) > self.max_turns:\n"
                "            new_turns = new_turns[-self.max_turns:]\n"
                "        return ConversationMemory(turns=new_turns, max_turns=self.max_turns)\n\n\n"
                "original = ConversationMemory()\n"
                "updated = original.add_turn(\"Python nima?\", \"Dasturlash tili.\")\n\n"
                "print(\"original.turns:\", original.turns)  # bo'sh qoladi — o'zgartirilmagan\n"
                "print(\"updated.turns:\", updated.turns)    # yangi nusxada 1 ta yozuv bor\n"
            ),
        },
    ],
}

L10_EXERCISES = [
    {
        "title": "Ikki xil xotira",
        "title_ru": "Два вида памяти",
        "description": "Chat tarixi va retrieval'ni farqlarga mos qo'ying (avval chat tarixi, keyin retrieval)",
        "description_ru": "Сопоставьте историю чата и retrieval с их характеристиками (сначала история чата, затем retrieval)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Qisqa muddatli, faqat shu suhbat davomida mavjud",
            "Uzoq muddatli, doimiy bilim manbai",
        ],
        "drag_items_ru": [
            "Краткосрочная, существует только в рамках этого диалога",
            "Долгосрочный, постоянный источник знаний",
        ],
        "correct_order": [
            "Qisqa muddatli, faqat shu suhbat davomida mavjud",
            "Uzoq muddatli, doimiy bilim manbai",
        ],
        "hint": "Darsdagi ikkita ro'yxat bandini eslang.",
        "hint_ru": "Вспомните два пункта списка из урока.",
        "difficulty_level": "Easy",
        "points": 6,
    },
    {
        "title": "Query rewriting maqsadi",
        "title_ru": "Цель query rewriting",
        "description": "\"Uning ikkinchi qismi-chi?\" kabi savolni qidiruvga yuborishdan oldin ___ qilish kerak.",
        "description_ru": "Прежде чем отправить в поиск вопрос вроде 'а что насчёт его второй части?', его нужно ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "qayta yozish",
        "correct_answers_ru": "переписать",
        "hint": "Darsdagi \"query rewriting\" atamasini eslang.",
        "hint_ru": "Вспомните термин 'query rewriting' из урока.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Xotira hajmini cheklash",
        "title_ru": "Ограничение объёма памяти",
        "description": "Nima uchun chat tarixini cheksiz saqlab bo'lmaydi?",
        "description_ru": "Почему нельзя хранить историю чата бесконечно?",
        "exercise_type": "multiple_choice",
        "options": [
            "Uzoq tarix o'zi ham token byudjetini yeb qo'yishi mumkin",
            "Bu texnik jihatdan imkonsiz",
            "LLM buni umuman qabul qilmaydi",
            "Bu narxga hech qanday ta'sir qilmaydi",
        ],
        "options_ru": [
            "Длинная история сама может 'съедать' бюджет токенов",
            "Это технически невозможно",
            "LLM вообще это не принимает",
            "Это никак не влияет на цену",
        ],
        "correct_answers": "A",
        "hint": "9-darsdagi token byudjeti muammosini eslang.",
        "hint_ru": "Вспомните проблему бюджета токенов из урока 9.",
        "explanation": "Chat tarixi ham promptning bir qismi, shuning uchun u ham token byudjetiga hisoblanadi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Immutable xotira",
        "title_ru": "Immutable память",
        "description": "ConversationMemory.add_turn() chaqirilganda nima sodir bo'ladi?",
        "description_ru": "Что происходит при вызове ConversationMemory.add_turn()?",
        "exercise_type": "multiple_choice",
        "options": [
            "Joriy obyekt o'zgarmaydi — yangi ConversationMemory nusxasi qaytariladi",
            "Joriy obyektning turns maydoni joyida (in-place) o'zgartiriladi",
            "Xatolik chiqadi",
            "Hech narsa qaytmaydi",
        ],
        "options_ru": [
            "Текущий объект не изменяется — возвращается новый экземпляр ConversationMemory",
            "Поле turns текущего объекта изменяется на месте (in-place)",
            "Возникает ошибка",
            "Ничего не возвращается",
        ],
        "correct_answers": "A",
        "hint": "@dataclass(frozen=True) nimani anglatishini eslang.",
        "hint_ru": "Вспомните, что означает @dataclass(frozen=True).",
        "explanation": "frozen=True dataclass o'zgarmas (immutable) — add_turn har doim yangi nusxa yaratadi, joriysini o'zgartirmaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 11 — RAG sifatini halol baholash
# ---------------------------------------------------------------------------

L11_TEXT = """
<h3>"Ishlayapti" va "to'g'ri ishlayapti" — ikki xil narsa</h3>
<p>Hozirgacha biz RAG pipeline'ni QURDIK va u kod xatosiz ishga tushishini
ko'rdik. Lekin bu "to'g'ri javob beryapti" degani emas. Bu darsda RAG
sifatini HALOL baholashni — ya'ni "ishlayapti" tuyulgan narsaning
haqiqatan qanchalik ISHONCHLI ekanini tekshirishni — o'rganamiz.</p>

<h3>Retrieval sifati: precision va recall</h3>
<p>Qidiruv (retrieve) bosqichini ikkita klassik metrika bilan baholash
mumkin:</p>
<ul>
<li><strong>Precision (aniqlik)</strong> — topilgan natijalarning necha
foizi HAQIQATAN mos? Agar top-5 natijadan faqat 2 tasi haqiqatan savolga
tegishli bo'lsa, precision = 2/5 = 40%.</li>
<li><strong>Recall (qamrov)</strong> — bazadagi BARCHA mos hujjatlardan
necha foizi topildi? Agar bazada 10 ta mos hujjat bo'lsa-yu, faqat 3 tasi
top-K ichiga tushsa, recall = 3/10 = 30%.</li>
</ul>
<p>Bu ikkisi ko'pincha bir-biriga QARSHI: K qiymatini oshirish (ko'proq
natija olish) recall'ni oshiradi, lekin precision'ni pasaytirishi mumkin
(ko'proq mos kelmagan natija ham qo'shiladi) — 9-darsda ko'rgan "ko'proq
chunk har doim yaxshi emas" tamoyilining metrik ko'rinishi.</p>

<h3>Eng xavfli illyuziya: "retrieved ≠ correct"</h3>
<p>Bu darsning eng muhim ogohlantirishi: <strong>qidiruv biror narsa
TOPGANI, u to'g'ri ekanini KAFOLATLAMAYDI</strong>. Cosine similarity yuqori
bo'lgan chunk baribir savolga to'liq javob bermasligi mumkin (masalan
mavzu jihatdan yaqin, lekin ANIQ so'ralgan detalni o'z ichiga olmaydi). Va
undan-da xavfliroq: LLM chunk'ni oladi, lekin baribir GALLYUTSINATSIYA
qilishi mumkin — ya'ni haqiqiy ma'lumot berilgan bo'lsa ham, LLM undan
noto'g'ri xulosa chiqarishi yoki chunk bilan bog'liq bo'lmagan qo'shimcha
"fakt" o'ylab topishi mumkin. Bu — "retrieval to'g'ri ishladi, lekin
generatsiya baribir noto'g'ri" holati, va bu RAG loyihalarida haqiqiy,
tez-tez uchraydigan muammo.</p>

<h3>RAG'ning keng tarqalgan nosozlik turlari</h3>
<ul>
<li><strong>Noto'g'ri retrieval</strong> — savolga umuman tegishli
bo'lmagan chunk topiladi (masalan chunking yomon qilingan yoki embedding
sifatsiz).</li>
<li><strong>To'g'ri retrieval, noto'g'ri generatsiya</strong> — to'g'ri
chunk topildi, lekin LLM baribir uni noto'g'ri talqin qildi yoki
e'tiborsiz qoldirdi.</li>
<li><strong>Qisman ma'lumot</strong> — savolga TO'LIQ javob berish uchun
2-3 xil chunk kerak, lekin faqat 1 tasi topildi — javob to'liqsiz chiqadi.</li>
<li><strong>Eskirgan ma'lumot</strong> — hujjat bazasi yangilanmagan, LLM
eski (endi noto'g'ri) ma'lumotga asoslanadi.</li>
</ul>

<h3>Baholash oqimi diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  TESTQ["Test so'rovlar to'plami
(ma'lum to'g'ri javob bilan)"]
  TESTQ --> RUN["Har birini RAG pipeline orqali o'tkazish"]
  RUN --> CHECK1{"Retrieval to'g'ri
chunk'ni topdimi?"}
  CHECK1 -->|"Yo'q"| BUG1["Nosozlik: chunking/embedding sifatini tekshirish"]
  CHECK1 -->|"Ha"| CHECK2{"Generatsiya chunk asosida
to'g'ri javob berdimi?"}
  CHECK2 -->|"Yo'q"| BUG2["Nosozlik: prompt/ko'rsatmani tekshirish"]
  CHECK2 -->|"Ha"| OK["To'g'ri ishladi — ikkala bosqich ham"]
</pre>

<h3>Amaliy yondashuv: kichik "oltin to'plam" (golden set)</h3>
<p>Production'da RAG sifatini muntazam baholash uchun kichik, qo'lda
tekshirilgan test savollari to'plami ("golden set") tuziladi — har biri
uchun "qaysi hujjat/chunk to'g'ri javob berishi kerak" oldindan ma'lum.
Pipeline o'zgargan sari (masalan chunk o'lchami yoki embedding modeli
almashtirilganda) shu to'plam qayta ishga tushiriladi va precision/recall
solishtiriladi — bu subyektiv "menimcha yaxshi ishlayapti" taassurotidan
ko'ra ancha ishonchli usul.</p>

<h3>Generatsiya sifatini tekshirish: "groundedness"</h3>
<p>Retrieval metrikalaridan tashqari, generatsiya natijasini ham tekshirish
mumkin — bu ko'pincha <strong>groundedness</strong> (asoslanganlik) deb
ataladi: LLM javobidagi HAR BIR da'vo topilgan chunk'larda haqiqatan
tasdiqlanadimi? Buni qo'lda (inson tekshiruvi orqali) yoki hatto boshqa
LLM chaqiruvi orqali ("quyidagi javob quyidagi ma'lumotga asoslanganmi?
Ha/Yo'q va nega") baholash mumkin. To'liq avtomatlashtirilgan groundedness
tekshiruvi murakkab mavzu — bu yerda faqat printsipni tanishtiramiz: RAG
sifatini baholash faqat retrieval bilan tugamaydi, generatsiya natijasi
ham alohida tekshiriladigan bosqich.</p>
"""

L11_TEXT_RU = """
<h3>"Работает" и "работает правильно" — две разные вещи</h3>
<p>До сих пор мы СТРОИЛИ RAG pipeline и видели, что код запускается без
ошибок. Но это не значит "даёт правильный ответ". В этом уроке мы научимся
ЧЕСТНО оценивать качество RAG — то есть проверять, насколько
"работающее на вид" на самом деле НАДЁЖНО.</p>

<h3>Качество retrieval: precision и recall</h3>
<p>Этап поиска (retrieve) можно оценить двумя классическими метриками:</p>
<ul>
<li><strong>Precision (точность)</strong> — какой процент найденных
результатов ДЕЙСТВИТЕЛЬНО подходит? Если из top-5 результатов только 2
реально относятся к вопросу, precision = 2/5 = 40%.</li>
<li><strong>Recall (полнота)</strong> — какой процент ВСЕХ подходящих
документов в базе был найден? Если в базе 10 подходящих документов, а в
top-K попали только 3, recall = 3/10 = 30%.</li>
</ul>
<p>Эти две метрики часто ПРОТИВОРЕЧАТ друг другу: увеличение K (получение
большего числа результатов) повышает recall, но может снизить precision
(добавляется больше неподходящих результатов) — метрическое выражение
принципа "больше фрагментов не всегда лучше" из урока 9.</p>

<h3>Самая опасная иллюзия: "найдено ≠ верно"</h3>
<p>Самое важное предупреждение этого урока: <strong>то, что поиск ЧТО-ТО
НАШЁЛ, не ГАРАНТИРУЕТ, что это верно</strong>. Фрагмент с высоким cosine
similarity всё равно может не полностью отвечать на вопрос (например,
близок по теме, но не содержит ТОЧНО запрошенную деталь). И ещё опаснее:
LLM получает фрагмент, но всё равно может ГАЛЛЮЦИНИРОВАТЬ — то есть даже
при наличии реальных данных LLM может сделать из них неверный вывод или
выдумать дополнительный "факт", не связанный с фрагментом. Это — ситуация
"retrieval сработал правильно, но генерация всё равно неверна", и это
реальная, часто встречающаяся проблема в RAG-проектах.</p>

<h3>Распространённые типы сбоев RAG</h3>
<ul>
<li><strong>Неверный retrieval</strong> — находится фрагмент, вообще не
относящийся к вопросу (например, плохой chunking или некачественный
эмбеддинг).</li>
<li><strong>Верный retrieval, неверная генерация</strong> — найден
правильный фрагмент, но LLM всё равно неверно его интерпретировала или
проигнорировала.</li>
<li><strong>Частичная информация</strong> — для полного ответа на вопрос
нужно 2-3 разных фрагмента, но найден только 1 — ответ получается
неполным.</li>
<li><strong>Устаревшая информация</strong> — база документов не
обновлена, LLM опирается на старые (уже неверные) данные.</li>
</ul>

<h3>Диаграмма процесса оценки</h3>
<pre class="mermaid">
flowchart TB
  TESTQ["Набор тестовых вопросов
(с известным верным ответом)"]
  TESTQ --> RUN["Прогон каждого через RAG pipeline"]
  RUN --> CHECK1{"Retrieval нашёл
верный фрагмент?"}
  CHECK1 -->|"Нет"| BUG1["Сбой: проверить качество chunking/эмбеддинга"]
  CHECK1 -->|"Да"| CHECK2{"Генерация дала верный ответ
на основе фрагмента?"}
  CHECK2 -->|"Нет"| BUG2["Сбой: проверить промпт/инструкцию"]
  CHECK2 -->|"Да"| OK["Сработало правильно — оба этапа"]
</pre>

<h3>Практический подход: небольшой "золотой набор" (golden set)</h3>
<p>В production для регулярной оценки качества RAG составляется небольшой,
вручную проверенный набор тестовых вопросов ("golden set") — для каждого
заранее известно, "какой документ/фрагмент должен дать верный ответ". При
изменении pipeline (например, смене размера фрагмента или модели
эмбеддинга) этот набор запускается заново, и сравниваются precision/
recall — это намного надёжнее, чем субъективное впечатление "мне кажется,
работает хорошо".</p>

<h3>Проверка качества генерации: "groundedness"</h3>
<p>Помимо метрик retrieval, можно проверять и результат генерации — это
часто называется <strong>groundedness</strong> (обоснованность): КАЖДОЕ ли
утверждение в ответе LLM действительно подтверждается найденными
фрагментами? Это можно оценивать вручную (проверкой человеком) или даже
через ещё один вызов LLM ("основан ли следующий ответ на следующих
данных? Да/Нет и почему"). Полностью автоматизированная проверка
groundedness — сложная тема — здесь мы знакомимся только с принципом:
оценка качества RAG не заканчивается на retrieval, результат генерации —
тоже отдельный этап, который нужно проверять.</p>
"""

L11_CODE = """
# Kichik "golden set" baholash harnessi: har bir test savoli uchun QAYSI
# dars ID'lari to'g'ri deb kutilishini oldindan belgilab, retrieval
# precision/recall'ni hisoblaymiz.

from __future__ import annotations


def precision_at_k(retrieved_ids: list[int], relevant_ids: set[int]) -> float:
    \"\"\"Topilganlarning necha qismi haqiqatan mos (relevant_ids ichida).\"\"\"
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)
    return hits / len(retrieved_ids)


def recall_at_k(retrieved_ids: list[int], relevant_ids: set[int]) -> float:
    \"\"\"Barcha mos hujjatlardan necha qismi topildi.\"\"\"
    if not relevant_ids:
        return 1.0  # mos hujjat umuman yo'q bo'lsa, "hammasi topildi" deb hisoblanadi
    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)
    return hits / len(relevant_ids)


# Golden set: har bir test savoli uchun "to'g'ri" dars ID'lari oldindan
# qo'lda aniqlangan (haqiqiy loyihada bu qo'lda ko'rib chiqilgan, ishonchli
# ro'yxat bo'lishi kerak).
GOLDEN_SET = [
    {"query": "Python funksiyasi qanday e'lon qilinadi", "relevant_ids": {12, 45}},
    {"query": "CSS flexbox bilan tekislash", "relevant_ids": {7, 11}},
    {"query": "SQL JOIN turlari", "relevant_ids": {88}},
]


def evaluate_retrieval(retrieve_fn, golden_set: list[dict], k: int = 5) -> dict:
    \"\"\"Har bir golden set yozuvi uchun retrieve_fn(query, k)ni chaqiradi
    (bu funksiya lesson_id larni qaytaradi deb faraz qilinadi), so'ngra
    o'rtacha precision/recall'ni hisoblaydi.\"\"\"
    precisions, recalls = [], []
    for item in golden_set:
        retrieved = retrieve_fn(item["query"], k)
        retrieved_ids = [r["lesson_id"] for r in retrieved]
        precisions.append(precision_at_k(retrieved_ids, item["relevant_ids"]))
        recalls.append(recall_at_k(retrieved_ids, item["relevant_ids"]))

    return {
        "avg_precision": sum(precisions) / len(precisions),
        "avg_recall": sum(recalls) / len(recalls),
        "per_query": list(zip((i["query"] for i in golden_set), precisions, recalls)),
    }


if __name__ == "__main__":
    # Soxta retrieve_fn — haqiqiy loyihada bu 8-darsdagi retrieve() bo'lardi:
    def fake_retrieve_fn(query: str, k: int) -> list[dict]:
        fake_results = {
            "Python funksiyasi qanday e'lon qilinadi": [{"lesson_id": 12}, {"lesson_id": 99}],
            "CSS flexbox bilan tekislash": [{"lesson_id": 7}, {"lesson_id": 11}],
            "SQL JOIN turlari": [{"lesson_id": 55}],  # noto'g'ri — 88 kutilgan edi
        }
        return fake_results.get(query, [])[:k]

    report = evaluate_retrieval(fake_retrieve_fn, GOLDEN_SET, k=5)
    print(f"O'rtacha precision: {report['avg_precision']:.2%}")
    print(f"O'rtacha recall:    {report['avg_recall']:.2%}")
    for query, p, r in report["per_query"]:
        print(f"  {query!r}: precision={p:.2f} recall={r:.2f}")
"""

L11_CODE_RU = """
# Небольшой harness оценки "golden set": для каждого тестового вопроса
# заранее указано, КАКИЕ ID уроков считаются верными, вычисляем
# precision/recall retrieval.

from __future__ import annotations


def precision_at_k(retrieved_ids: list[int], relevant_ids: set[int]) -> float:
    \"\"\"Какая доля найденного действительно подходит (входит в relevant_ids).\"\"\"
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)
    return hits / len(retrieved_ids)


def recall_at_k(retrieved_ids: list[int], relevant_ids: set[int]) -> float:
    \"\"\"Какая доля всех подходящих документов была найдена.\"\"\"
    if not relevant_ids:
        return 1.0  # если подходящих документов вообще нет, считаем "всё найдено"
    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)
    return hits / len(relevant_ids)


# Golden set: для каждого тестового вопроса заранее вручную определены
# "верные" ID уроков (в реальном проекте это должен быть проверенный
# вручную, надёжный список).
GOLDEN_SET = [
    {"query": "Как объявляется функция в Python", "relevant_ids": {12, 45}},
    {"query": "Выравнивание с помощью CSS flexbox", "relevant_ids": {7, 11}},
    {"query": "Типы SQL JOIN", "relevant_ids": {88}},
]


def evaluate_retrieval(retrieve_fn, golden_set: list[dict], k: int = 5) -> dict:
    \"\"\"Для каждой записи golden set вызывает retrieve_fn(query, k)
    (предполагается, что эта функция возвращает lesson_id), затем
    вычисляет среднюю precision/recall.\"\"\"
    precisions, recalls = [], []
    for item in golden_set:
        retrieved = retrieve_fn(item["query"], k)
        retrieved_ids = [r["lesson_id"] for r in retrieved]
        precisions.append(precision_at_k(retrieved_ids, item["relevant_ids"]))
        recalls.append(recall_at_k(retrieved_ids, item["relevant_ids"]))

    return {
        "avg_precision": sum(precisions) / len(precisions),
        "avg_recall": sum(recalls) / len(recalls),
        "per_query": list(zip((i["query"] for i in golden_set), precisions, recalls)),
    }


if __name__ == "__main__":
    # Фейковая retrieve_fn — в реальном проекте это была бы retrieve() из урока 8:
    def fake_retrieve_fn(query: str, k: int) -> list[dict]:
        fake_results = {
            "Как объявляется функция в Python": [{"lesson_id": 12}, {"lesson_id": 99}],
            "Выравнивание с помощью CSS flexbox": [{"lesson_id": 7}, {"lesson_id": 11}],
            "Типы SQL JOIN": [{"lesson_id": 55}],  # неверно — ожидался 88
        }
        return fake_results.get(query, [])[:k]

    report = evaluate_retrieval(fake_retrieve_fn, GOLDEN_SET, k=5)
    print(f"Средняя precision: {report['avg_precision']:.2%}")
    print(f"Средний recall:    {report['avg_recall']:.2%}")
    for query, p, r in report["per_query"]:
        print(f"  {query!r}: precision={p:.2f} recall={r:.2f}")
"""

L11_TASK = {
    "task_title": "O'z golden set'ingizni tuzing va baholang",
    "task_title_ru": "Составьте свой golden set и оцените",
    "task_description": (
        "Darsdagi `evaluate_retrieval` funksiyasidan foydalanib, kamida 5 "
        "ta test savoli va ularning \"to'g'ri\" dars ID'laridan iborat "
        "o'z golden set'ingizni tuzing (haqiqiy yoki L6'dagi indeks "
        "asosida). Natijaviy precision/recall'ni hisoblang va kamida "
        "bitta savol uchun nima uchun past ball chiqqanini tahlil qiling."
    ),
    "task_description_ru": (
        "Используя функцию `evaluate_retrieval` из урока, составьте свой "
        "golden set минимум из 5 тестовых вопросов и их 'верных' ID уроков "
        "(реальных или на основе индекса из L6). Вычислите итоговые "
        "precision/recall и проанализируйте, почему хотя бы для одного "
        "вопроса получился низкий балл."
    ),
    "task_requirements": (
        "1) Kamida 5 ta test savoli bo'lsin. 2) O'rtacha precision va "
        "recall hisoblansin va chiqarilsin. 3) Kamida bitta past ballli "
        "savol uchun sabab tahlili yozilsin (masalan chunking yomonmi, "
        "embedding yetarli emasmi)."
    ),
    "task_requirements_ru": (
        "1) Должно быть минимум 5 тестовых вопросов. 2) Должны быть "
        "вычислены и выведены средние precision и recall. 3) Для "
        "минимум одного вопроса с низким баллом должен быть написан "
        "анализ причины (например, плохой chunking или недостаточный "
        "эмбеддинг)."
    ),
    "task_technologies": "Python",
    "task_deadline_days": 5,
}

L11_SAMPLE = {
    "title": "Namuna: precision/recall qo'lda hisoblash",
    "description": (
        "Ikki xil top-K qiymati bilan precision/recall qanday "
        "o'zgarishini ko'rsatadi."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "precision_recall_demo.py",
            "language": "python",
            "code": (
                "def precision_at_k(retrieved_ids, relevant_ids):\n"
                "    if not retrieved_ids:\n"
                "        return 0.0\n"
                "    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)\n"
                "    return hits / len(retrieved_ids)\n\n\n"
                "def recall_at_k(retrieved_ids, relevant_ids):\n"
                "    if not relevant_ids:\n"
                "        return 1.0\n"
                "    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)\n"
                "    return hits / len(relevant_ids)\n\n\n"
                "relevant = {1, 2, 3, 4}  # bazada haqiqatan 4 ta mos hujjat bor\n\n"
                "# Kichik K (2 ta natija):\n"
                "small_k = [1, 5]\n"
                "print('K=2:', 'precision=', precision_at_k(small_k, relevant), 'recall=', recall_at_k(small_k, relevant))\n\n"
                "# Kattaroq K (6 ta natija):\n"
                "big_k = [1, 2, 3, 5, 6, 7]\n"
                "print('K=6:', 'precision=', precision_at_k(big_k, relevant), 'recall=', recall_at_k(big_k, relevant))\n"
            ),
        },
    ],
}

L11_EXERCISES = [
    {
        "title": "Precision ta'rifi",
        "title_ru": "Определение precision",
        "description": "Precision (aniqlik) nimani o'lchaydi?",
        "description_ru": "Что измеряет precision (точность)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Topilgan natijalarning necha foizi haqiqatan mos",
            "Bazadagi barcha mos hujjatlarning necha foizi topildi",
            "Qidiruv necha soniyada bajarildi",
            "Nechta hujjat bazada saqlangan",
        ],
        "options_ru": [
            "Какой процент найденных результатов действительно подходит",
            "Какой процент всех подходящих документов в базе был найден",
            "За сколько секунд выполнился поиск",
            "Сколько документов хранится в базе",
        ],
        "correct_answers": "A",
        "hint": "Precision — \"topilganlar ichida to'g'rilari qancha\".",
        "hint_ru": "Precision — 'сколько из найденного верно'.",
        "explanation": "Precision = to'g'ri topilganlar soni / jami topilganlar soni.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Recall ta'rifi",
        "title_ru": "Определение recall",
        "description": "Recall (qamrov) nimani o'lchaydi?",
        "description_ru": "Что измеряет recall (полнота)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Bazadagi barcha mos hujjatlarning necha foizi topildi",
            "Topilgan natijalarning necha foizi haqiqatan mos",
            "LLM javobining uzunligi",
            "API kalitining amal qilish muddati",
        ],
        "options_ru": [
            "Какой процент всех подходящих документов в базе был найден",
            "Какой процент найденных результатов действительно подходит",
            "Длина ответа LLM",
            "Срок действия API-ключа",
        ],
        "correct_answers": "A",
        "hint": "Recall — \"bor bo'lganlar ichida qanchasi topildi\".",
        "hint_ru": "Recall — 'сколько из существующего было найдено'.",
        "explanation": "Recall = to'g'ri topilganlar soni / bazadagi barcha mos hujjatlar soni.",
        "difficulty_level": "Easy",
        "points": 5,
    },
    {
        "title": "Eng xavfli illyuziya",
        "title_ru": "Самая опасная иллюзия",
        "description": "Darsdagi eng muhim ogohlantirish: qidiruv biror narsa topgani, uning ___ ekanini kafolatlamaydi.",
        "description_ru": "Важнейшее предупреждение из урока: то, что поиск что-то нашёл, не гарантирует, что это ___.",
        "exercise_type": "fill_in_blank",
        "correct_answers": "to'g'ri",
        "correct_answers_ru": "верно",
        "hint": "\"retrieved ≠ correct\" bo'limini eslang.",
        "hint_ru": "Вспомните раздел 'retrieved ≠ correct'.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "RAG nosozlik turlarini bog'lash",
        "title_ru": "Сопоставление типов сбоев RAG",
        "description": "Nosozlik turlarini tartibda joylashtiring (darsdagi ro'yxat tartibida)",
        "description_ru": "Расположите типы сбоев по порядку (в порядке списка из урока)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Noto'g'ri retrieval — mavzuga umuman tegishli emas",
            "To'g'ri retrieval, noto'g'ri generatsiya",
            "Qisman ma'lumot — javob to'liqsiz",
            "Eskirgan ma'lumot",
        ],
        "drag_items_ru": [
            "Неверный retrieval — вообще не относится к теме",
            "Верный retrieval, неверная генерация",
            "Частичная информация — ответ неполный",
            "Устаревшая информация",
        ],
        "correct_order": [
            "Noto'g'ri retrieval — mavzuga umuman tegishli emas",
            "To'g'ri retrieval, noto'g'ri generatsiya",
            "Qisman ma'lumot — javob to'liqsiz",
            "Eskirgan ma'lumot",
        ],
        "hint": "Darsdagi to'rtta ro'yxat bandini tartibda eslang.",
        "hint_ru": "Вспомните четыре пункта списка из урока по порядку.",
        "difficulty_level": "Medium",
        "points": 8,
    },
]

# ---------------------------------------------------------------------------
# Lesson 12 — R2: Takrorlash — To'liq RAG va sifat baholash
# ---------------------------------------------------------------------------

L12_TEXT = """
<h3>R2 — Takrorlash darsi</h3>
<p>Bu — ikkinchi takrorlash darsi (R1'dan farqli o'laroq, endi to'liq RAG
pipeline, xotira va sifat baholashni qamrab oladi). R1'dagi kabi, bu yerda
ham yangi tushuncha YO'Q — matn ataylab qisqaroq, asosiy e'tibor pastdagi
yakuniy amaliy vazifada, u sizni 13-darsdagi capstone'ga tayyorlaydi.</p>

<h3>8-11 darslarda nimalarni o'rgandik</h3>
<ul>
<li><strong>L8:</strong> To'liq RAG pipeline — retrieve, augment, generate;
generate() 135-kursdagi call_chain()ni qayta ishlatadi, qaytadan yozmaydi.</li>
<li><strong>L9:</strong> Token byudjeti chunked retrieval bilan — chunk'larni
cosine balliga ko'ra saralab, byudjetga sig'guncha qo'shish; "lost in the
middle" tufayli ko'proq chunk har doim yaxshi emas.</li>
<li><strong>L10:</strong> Suhbat xotirasi — chat tarixi (qisqa muddatli)
va retrieval (uzoq muddatli) ikki xil narsa; query rewriting orqali
ishoralarni to'liq savolga aylantirish; immutable ConversationMemory.</li>
<li><strong>L11:</strong> RAG sifatini halol baholash — precision/recall,
"retrieved ≠ correct" illyuziyasi, golden set orqali muntazam tekshiruv.</li>
</ul>

<h3>Butun kursning yakuniy zanjiri</h3>
<p>Endi L0'dan L11'gacha bo'lgan BARCHA bo'laklar bir-biriga ulangan holda
mavjud: RAG nima ekanidan (L0) tortib, embedding (L1), chunking (L2),
cosine similarity (L3), vektor bazasi tanlash (L4-L5), haqiqiy qidiruv
(L6), to'liq pipeline (L8), byudjet boshqaruvi (L9), xotira (L10) va sifat
baholash (L11) — bularning barchasi 13-darsdagi yakuniy capstone loyihada
BIR JOYGA yig'iladi.</p>

<h3>Capstone'ga tayyorgarlik</h3>
<p>13-darsda siz "platformaning o'z ma'lumotlari haqida savol-javob
chatboti"ni quramiz — bu shunchaki yangi kod yozish emas, balki hozirgacha
qurgan HAMMA narsani (L6'dagi qidiruv indeksi, L8'dagi pipeline, L9'dagi
byudjet boshqaruvi, L10'dagi xotira) BITTA ishlaydigan feature'ga
birlashtirish. Shuning uchun quyidagi amaliy vazifa — ushbu barcha
qismlarni bitta faylda qayta yig'ish mashqi.</p>
"""

L12_TEXT_RU = """
<h3>R2 — Урок повторения</h3>
<p>Это — второй урок повторения (в отличие от R1, теперь охватывает
полный RAG pipeline, память и оценку качества). Как и в R1, здесь тоже НЕТ
новых понятий — текст намеренно короче, основной фокус на финальном
практическом задании ниже, которое подготовит вас к capstone в уроке 13.</p>

<h3>Что мы изучили в уроках 8-11</h3>
<ul>
<li><strong>L8:</strong> Полный RAG pipeline — retrieve, augment,
generate; generate() повторно использует call_chain() из курса 135, не
переписывая её.</li>
<li><strong>L9:</strong> Бюджет токенов при chunked retrieval — сортировка
фрагментов по баллу cosine и добавление, пока помещается в бюджет; из-за
"lost in the middle" больше фрагментов не всегда лучше.</li>
<li><strong>L10:</strong> Память диалога — история чата (краткосрочная) и
retrieval (долгосрочный) — это разные вещи; переписывание запроса
превращает ссылки в полный вопрос; immutable ConversationMemory.</li>
<li><strong>L11:</strong> Честная оценка качества RAG — precision/recall,
иллюзия "найдено ≠ верно", регулярная проверка через golden set.</li>
</ul>

<h3>Итоговая цепочка всего курса</h3>
<p>Теперь ВСЕ части от L0 до L11 связаны друг с другом: от того, что такое
RAG (L0), через эмбеддинг (L1), chunking (L2), cosine similarity (L3),
выбор векторной базы (L4-L5), реальный поиск (L6), полный pipeline (L8),
управление бюджетом (L9), память (L10) и оценку качества (L11) — всё это
объединяется в одном финальном проекте capstone в уроке 13.</p>

<h3>Подготовка к capstone</h3>
<p>В уроке 13 мы построим "чат-бота вопрос-ответ по собственным данным
платформы" — это не просто написание нового кода, а объединение ВСЕГО, что
вы построили до сих пор (индекс поиска из L6, pipeline из L8, управление
бюджетом из L9, память из L10) в ОДНУ работающую функцию. Поэтому
практическое задание ниже — это упражнение по повторной сборке всех этих
частей в одном файле.</p>
"""

L12_TASK = {
    "task_title": "Mini-capstone: barcha qismlarni bitta faylda birlashtirish",
    "task_title_ru": "Мини-капстоун: объединение всех частей в одном файле",
    "task_description": (
        "L6, L8, L9 va L10'dagi funksiyalarni (build_search_index, "
        "retrieve, build_augmented_prompt, fit_chunks_to_budget, "
        "ConversationMemory) BITTA Python faylida birlashtiring va "
        "kamida 2 bosqichli suhbatni ishga tushiring (birinchi savol "
        "haqiqiy dars mavzusi haqida, ikkinchisi birinchisiga ishora "
        "qiluvchi savol)."
    ),
    "task_description_ru": (
        "Объедините функции из L6, L8, L9 и L10 (build_search_index, "
        "retrieve, build_augmented_prompt, fit_chunks_to_budget, "
        "ConversationMemory) в ОДНОМ файле Python и запустите диалог "
        "минимум из 2 шагов (первый вопрос — по реальной теме урока, "
        "второй — вопрос, ссылающийся на первый)."
    ),
    "task_requirements": (
        "1) Barcha funksiyalar bitta faylda, import xatolarisiz "
        "ishlashi kerak. 2) Kamida 2 bosqichli suhbat ishga tushirilsin. "
        "3) Token byudjeti nazorati (fit_chunks_to_budget) qo'llanilsin."
    ),
    "task_requirements_ru": (
        "1) Все функции должны работать в одном файле без ошибок "
        "импорта. 2) Должен быть запущен диалог минимум из 2 шагов. "
        "3) Должен применяться контроль бюджета токенов "
        "(fit_chunks_to_budget)."
    ),
    "task_technologies": "Python, SQLAlchemy, httpx",
    "task_deadline_days": 6,
}

L12_SAMPLE = {
    "title": "Namuna: 8-11 darslar funksiyalarining qisqa recap'i",
    "description": (
        "retrieve, byudjet nazorati va xotirani bitta oddiy misolda "
        "ko'rsatadi (LLM chaqiruvisiz, offline)."
    ),
    "sample_type": "python",
    "code_files": [
        {
            "filename": "recap_full_pipeline.py",
            "language": "python",
            "code": (
                "def estimate_tokens(text):\n"
                "    return max(1, len(text) // 4)\n\n\n"
                "def fit_chunks_to_budget(chunks, token_budget, reserved=100):\n"
                "    available = token_budget - reserved\n"
                "    selected, used = [], 0\n"
                "    for c in chunks:\n"
                "        t = estimate_tokens(c['text'])\n"
                "        if used + t > available:\n"
                "            break\n"
                "        selected.append(c)\n"
                "        used += t\n"
                "    return selected\n\n\n"
                "chunks = [\n"
                "    {'heading': 'A', 'text': 'x' * 400, 'score': 0.9},\n"
                "    {'heading': 'B', 'text': 'y' * 800, 'score': 0.7},\n"
                "]\n\n"
                "fitted = fit_chunks_to_budget(chunks, token_budget=300)\n"
                "print(f\"{len(fitted)} ta chunk byudjetga sig'di\")\n"
                "for c in fitted:\n"
                "    print(f\"  {c['heading']} (score={c['score']})\")\n"
            ),
        },
    ],
}

L12_EXERCISES = [
    {
        "title": "Zanjirning yakuniy tuzilishi",
        "title_ru": "Итоговая структура цепочки",
        "description": "13-darsdagi capstone qaysi darslarning natijalarini birlashtiradi?",
        "description_ru": "Результаты каких уроков объединяет capstone в уроке 13?",
        "exercise_type": "multiple_choice",
        "options": [
            "L6 (qidiruv), L8 (pipeline), L9 (byudjet), L10 (xotira)",
            "Faqat L0 va L1",
            "Faqat L4 va L5",
            "Hech biri, u butunlay yangi kod",
        ],
        "options_ru": [
            "L6 (поиск), L8 (pipeline), L9 (бюджет), L10 (память)",
            "Только L0 и L1",
            "Только L4 и L5",
            "Ни один, это совершенно новый код",
        ],
        "correct_answers": "A",
        "hint": "Darsdagi \"Capstone'ga tayyorgarlik\" bo'limini eslang.",
        "hint_ru": "Вспомните раздел 'Подготовка к capstone' из урока.",
        "explanation": "Capstone hozirgacha qurilgan qidiruv, pipeline, byudjet va xotira qismlarini bitta feature'ga birlashtiradi.",
        "difficulty_level": "Easy",
        "points": 6,
    },
    {
        "title": "call_chain qayta ishlatilishi",
        "title_ru": "Повторное использование call_chain",
        "description": "L8'dagi generate() funksiyasi 135-kursdagi call_chain()ni ___ (qaytadan yozadimi yoki import qilib chaqiradimi)?",
        "description_ru": "Функция generate() из L8 ___ call_chain() из курса 135 (переписывает заново или импортирует и вызывает)?",
        "exercise_type": "fill_in_blank",
        "correct_answers": "import qilib chaqiradi",
        "correct_answers_ru": "импортирует и вызывает",
        "hint": "DRY tamoyilini eslang.",
        "hint_ru": "Вспомните принцип DRY.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "R1 va R2 farqi",
        "title_ru": "Отличие R1 от R2",
        "description": "R1 va R2 darslarini qamrab olgan mavzulariga mos qo'ying (avval R1, keyin R2)",
        "description_ru": "Сопоставьте уроки R1 и R2 с охваченными темами (сначала R1, затем R2)",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Embedding, chunking, cosine similarity, vektor bazasi va qidiruv (L0-L6)",
            "To'liq pipeline, byudjet, xotira va sifat baholash (L8-L11)",
        ],
        "drag_items_ru": [
            "Эмбеддинг, chunking, cosine similarity, векторная база и поиск (L0-L6)",
            "Полный pipeline, бюджет, память и оценка качества (L8-L11)",
        ],
        "correct_order": [
            "Embedding, chunking, cosine similarity, vektor bazasi va qidiruv (L0-L6)",
            "To'liq pipeline, byudjet, xotira va sifat baholash (L8-L11)",
        ],
        "hint": "R1 birinchi yarmini, R2 ikkinchi yarmini qamraydi.",
        "hint_ru": "R1 охватывает первую половину, R2 — вторую.",
        "difficulty_level": "Easy",
        "points": 6,
    },
]

# ---------------------------------------------------------------------------
# Lesson 13 — Yakuniy capstone: platforma ma'lumotlari bo'yicha savol-javob chatboti
# ---------------------------------------------------------------------------

L13_TEXT = """
<h3>Yakuniy capstone: nima quramiz</h3>
<p>Bu kursning yakuniy loyihasi — ushbu platformaning HAQIQIY ma'lumotlari
(darslari) haqida savol-javob bera oladigan mini chatbot feature. Bu
o'ylab topilgan "demo" emas — bu 0-darsda va'da qilingan narsaning
to'liq bajarilishi: "platformaning o'z kurs katalogi haqida so'rasangiz, u
hech narsa bilmaydi" muammosining HAQIQIY yechimi.</p>

<h3>Capstone talablari</h3>
<p>Yakuniy feature quyidagilarni QAMRAB olishi kerak — har biri
allaqachon alohida darsda qurilgan, endi ularni BIRLASHTIRISH vazifasi:</p>
<ul>
<li><strong>Qidiruv (L6):</strong> lessons jadvalidan haqiqiy matnni
o'qish, chunk'larga bo'lish, vektorlashtirish.</li>
<li><strong>To'liq pipeline (L8):</strong> retrieve -> augment -> generate,
generate() 135-kursdagi <code>call_chain()</code>ni qayta ishlatadi.</li>
<li><strong>Token byudjeti (L9):</strong> topilgan chunk'larni byudjetga
sig'dirish, ortiqchasini tashlab yuborish.</li>
<li><strong>Suhbat xotirasi (L10):</strong> ko'p bosqichli savol-javobni
qo'llab-quvvatlash, immutable ConversationMemory bilan.</li>
<li><strong>Xatolarni boshqarish (135-kurs + L8):</strong> agar hech qanday
mos ma'lumot topilmasa YOKI barcha LLM provider'lar ishlamay qolsa,
foydalanuvchiga tushunarli, halol xabar berish (hech qachon jim
qolmaslik yoki soxta javob bermaslik).</li>
</ul>

<h3>Yakuniy arxitektura diagrammasi</h3>
<pre class="mermaid">
flowchart TB
  USER["Foydalanuvchi savoli"]
  USER --> REWRITE["1. Savolni qayta yozish
(agar tarix mavjud bo'lsa)"]
  REWRITE --> RETRIEVE["2. retrieve()
lessons jadvalidan (faqat o'qish)"]
  RETRIEVE --> BUDGET["3. Token byudjetiga sig'dirish
(fit_chunks_to_budget)"]
  BUDGET --> CHECK{"Mos chunk topildimi?"}
  CHECK -->|"Yo'q"| NOINFO["Halol javob:
'ma'lumot topilmadi'"]
  CHECK -->|"Ha"| PROMPT["4. build_augmented_prompt()
+ chat tarixi"]
  PROMPT --> CHAIN["5. call_chain()
(135-kurs — groq/gemini/openai)"]
  CHAIN -->|"muvaffaqiyatli"| ANSWER["Haqiqiy ma'lumotga
asoslangan javob"]
  CHAIN -->|"barcha provider xato"| FAIL["Halol xabar:
'AI xizmati vaqtincha ishlamayapti'"]
  ANSWER --> MEMORY["6. Xotirani yangilash
(yangi immutable nusxa)"]
</pre>
<p>Bu diagramma — butun kursning YAKUNIY natijasi: har bir raqamlangan
qadam biror darsda alohida o'rganilgan, endi ular bitta chiziqqa
tizilgan.</p>

<h3>FastAPI integratsiyasi: 135-kursdagi haqiqiy pattern</h3>
<p>135-kursning oxirgi darsida siz <code>app/api/v1/endpoints/ai_review.py</code>
faylidagi haqiqiy FastAPI endpoint tuzilishini ko'rgan edingiz — router,
<code>Depends(get_current_student)</code>, <code>Depends(get_db)</code>,
xatolarni <code>HTTPException</code>ga aylantirish. Bu capstone'ning
haqiqiy production loyihasida shu xuddi shu pattern qo'llaniladi: yangi
endpoint (masalan <code>POST /courses/ask</code>) yaratilib, ichida
yuqoridagi RAG pipeline chaqiriladi, natija esa oddiy JSON javob sifatida
qaytariladi.</p>

<h3>Nima UCHUN bu capstone, oddiy mashq emas</h3>
<p>Bu loyihaning boshqa amaliy vazifalardan farqi — u BIR NARSANI emas,
BUTUN KURS davomida qurilgan hamma narsani sinaydi. Agar biror qism
(masalan chunking yomon, yoki token byudjeti noto'g'ri hisoblangan)
ishlamasa, bu yakuniy natijada KO'RINADI — masalan LLM juda uzun yoki
juda qisqa kontekst bilan ishlab, sifatsiz javob berishi mumkin. Shu
sababli capstone — nafaqat kod yozish mashqi, balki BUTUN pipeline
qanchalik puxta qurilganini tekshirish vositasi.</p>

<h3>Capstone'dan keyin: production'da yana nima qo'shiladi</h3>
<p>Bu capstone o'quv maqsadida to'liq, ishlaydigan pipeline'ni ko'rsatadi
— lekin haqiqiy production loyihada yana bir necha narsa qo'shilardi:
<code>fake_embed</code> o'rniga haqiqiy <code>sentence-transformers</code>
yoki Gemini embedding API (1-dars), xotirada saqlash o'rniga pgvector
jadvali (5-dars, sizning O'Z loyihangizda), va L11'dagi golden set orqali
muntazam sifat monitoringi. Bu kurs sizga PIPELINE'NING STRUKTURASINI va
HAR BIR bo'lakning NEGA kerakligini o'rgatdi — bu struktura har qanday
haqiqiy loyihada (fake_embed o'rniga haqiqiy modelni qo'yib) to'g'ridan-
to'g'ri qo'llanadi.</p>

<h3>Capstone'ni qanday tekshirish kerak: qisqa test ro'yxati</h3>
<p>"Ishga tushdi" va "to'g'ri ishlayapti" — 11-darsda ko'rganimizdek, ikki
xil narsa. Capstone'ni topshirishdan oldin quyidagi kichik test ro'yxatini
o'zingiz qo'lda bajarib ko'ring — bu L11'dagi golden set g'oyasining
capstone miqyosidagi soddalashtirilgan shakli:</p>
<ul>
<li><strong>Mavjud mavzu testi:</strong> platformada HAQIQATDA mavjud bo'lgan
mavzu haqida so'rang (masalan "Python funksiyalari haqida dars bormi?") —
javobda ko'rsatilgan dars ID'sini platformaning o'zida ochib, haqiqatan
mos ekanini tekshiring.</li>
<li><strong>Yo'q mavzu testi:</strong> platformada UMUMAN yo'q mavzu haqida
so'rang (masalan "Marsda uy qurish qanday" haqida) — javob halol
"ma'lumot topilmadi" bo'lishi kerak, LLM o'ylab topmasligi kerak.</li>
<li><strong>Xotira testi:</strong> ikki bosqichli suhbat qiling, ikkinchi
savolda "uning", "u" kabi ishoralardan foydalaning — javob birinchi savolga
tegishli ekanini tekshiring.</li>
<li><strong>Nosozlikka chidamlilik testi:</strong> (ixtiyoriy, agar
imkoniyat bo'lsa) barcha API kalitlarini vaqtincha o'chirib sinab ko'ring
— natija jim qolish yoki xato bilan yiqilish o'rniga halol xabar
qaytarishi kerak.</li>
</ul>
<p>Agar ushbu to'rt test ham kutilganidek o'tsa, capstone nafaqat "kod
xatosiz ishga tushadi", balki "0-darsda va'da qilingan narsani haqiqatan
bajaradi" darajasida tekshirilgan bo'ladi.</p>
"""

L13_TEXT_RU = """
<h3>Финальный capstone: что строим</h3>
<p>Финальный проект этого курса — мини-функция чат-бота, способная
отвечать на вопросы о РЕАЛЬНЫХ данных (уроках) этой платформы. Это не
выдуманное "демо" — это полное выполнение обещания из урока 0: РЕАЛЬНОЕ
решение проблемы "если спросить про собственный каталог курсов
платформы, она ничего не знает".</p>

<h3>Требования capstone</h3>
<p>Финальная функция должна ОХВАТЫВАТЬ следующее — каждое уже построено в
отдельном уроке, теперь задача — ОБЪЕДИНИТЬ их:</p>
<ul>
<li><strong>Поиск (L6):</strong> чтение реального текста из таблицы
lessons, разбиение на фрагменты, векторизация.</li>
<li><strong>Полный pipeline (L8):</strong> retrieve -> augment ->
generate, generate() повторно использует <code>call_chain()</code> из
курса 135.</li>
<li><strong>Бюджет токенов (L9):</strong> укладывание найденных
фрагментов в бюджет, отбрасывание лишнего.</li>
<li><strong>Память диалога (L10):</strong> поддержка многошагового
вопроса-ответа с immutable ConversationMemory.</li>
<li><strong>Обработка ошибок (курс 135 + L8):</strong> если не найдено
подходящих данных ИЛИ все провайдеры LLM недоступны — дать пользователю
понятное, честное сообщение (никогда не молчать и не давать выдуманный
ответ).</li>
</ul>

<h3>Диаграмма итоговой архитектуры</h3>
<pre class="mermaid">
flowchart TB
  USER["Вопрос пользователя"]
  USER --> REWRITE["1. Переписывание вопроса
(если есть история)"]
  REWRITE --> RETRIEVE["2. retrieve()
из таблицы lessons (только чтение)"]
  RETRIEVE --> BUDGET["3. Укладывание в бюджет токенов
(fit_chunks_to_budget)"]
  BUDGET --> CHECK{"Найден подходящий фрагмент?"}
  CHECK -->|"Нет"| NOINFO["Честный ответ:
'информация не найдена'"]
  CHECK -->|"Да"| PROMPT["4. build_augmented_prompt()
+ история чата"]
  PROMPT --> CHAIN["5. call_chain()
(курс 135 — groq/gemini/openai)"]
  CHAIN -->|"успешно"| ANSWER["Ответ на основе
реальных данных"]
  CHAIN -->|"все провайдеры дали сбой"| FAIL["Честное сообщение:
'сервис AI временно недоступен'"]
  ANSWER --> MEMORY["6. Обновление памяти
(новая immutable копия)"]
</pre>
<p>Эта диаграмма — ИТОГОВЫЙ результат всего курса: каждый пронумерованный
шаг был изучен отдельно в своём уроке, теперь они выстроены в одну
линию.</p>

<h3>Интеграция с FastAPI: реальный паттерн из курса 135</h3>
<p>В последнем уроке курса 135 вы видели реальную структуру FastAPI
endpoint в файле <code>app/api/v1/endpoints/ai_review.py</code> — router,
<code>Depends(get_current_student)</code>, <code>Depends(get_db)</code>,
превращение ошибок в <code>HTTPException</code>. В реальном
production-проекте этого capstone применяется ТОТ ЖЕ паттерн: создаётся
новый endpoint (например <code>POST /courses/ask</code>), внутри
вызывается описанный выше RAG pipeline, а результат возвращается как
обычный JSON-ответ.</p>

<h3>ПОЧЕМУ это capstone, а не обычное упражнение</h3>
<p>Отличие этого проекта от других практических заданий — он проверяет не
ОДНУ вещь, а ВСЁ, что было построено на протяжении ВСЕГО курса. Если
какая-то часть (например, плохой chunking или неверно рассчитанный бюджет
токенов) не работает, это БУДЕТ ВИДНО в итоговом результате — например,
LLM работает со слишком длинным или слишком коротким контекстом и даёт
некачественный ответ. Поэтому capstone — это не просто упражнение по
написанию кода, а инструмент проверки того, насколько тщательно построен
ВЕСЬ pipeline.</p>

<h3>После capstone: что ещё добавляется в production</h3>
<p>Этот capstone показывает полный, работающий pipeline в учебных целях —
но в реальном production-проекте добавилось бы ещё несколько вещей:
настоящая <code>sentence-transformers</code> или Gemini embedding API
вместо <code>fake_embed</code> (урок 1), таблица pgvector вместо хранения
в памяти (урок 5, в ВАШЕМ собственном проекте), и регулярный мониторинг
качества через golden set из урока 11. Этот курс научил вас СТРУКТУРЕ
pipeline и ПОЧЕМУ нужна каждая часть — эта структура напрямую применима в
любом реальном проекте (просто подставив настоящую модель вместо
fake_embed).</p>

<h3>Как проверить capstone: краткий чек-лист тестирования</h3>
<p>"Запустилось" и "работает правильно" — как мы видели в уроке 11, это
две разные вещи. Перед сдачей capstone вручную пройдите следующий
короткий чек-лист — это упрощённая, капстоун-масштабная форма идеи golden
set из урока 11:</p>
<ul>
<li><strong>Тест существующей темы:</strong> спросите про тему, которая
ДЕЙСТВИТЕЛЬНО есть на платформе (например "Есть ли урок про функции
Python?") — откройте указанный в ответе ID урока на самой платформе и
проверьте, что он действительно соответствует.</li>
<li><strong>Тест отсутствующей темы:</strong> спросите про тему, которой
на платформе ВООБЩЕ нет (например про "строительство дома на Марсе") —
ответ должен быть честным "информация не найдена", LLM не должна
выдумывать.</li>
<li><strong>Тест памяти:</strong> проведите диалог из двух шагов, во
втором вопросе используйте ссылки вроде "его", "он" — проверьте, что
ответ относится к первому вопросу.</li>
<li><strong>Тест устойчивости к сбоям:</strong> (опционально, если есть
возможность) временно отключите все API-ключи — результатом должно быть
честное сообщение, а не молчание или падение с ошибкой.</li>
</ul>
<p>Если все четыре теста проходят как ожидается, capstone проверен не
просто на уровне "код запускается без ошибок", а на уровне "действительно
выполняет то, что было обещано в уроке 0".</p>
"""

L13_CODE = """
# YAKUNIY CAPSTONE: barcha darslarning (L1, L2, L3, L6, L8, L9, L10)
# funksiyalarini bitta ishlaydigan chatbot feature'ga birlashtiradi.
# generate() qismi 135-kursdagi HAQIQIY call_chain()ni chaqiradi.

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db import base as _base  # noqa: F401
from app.models.lesson import Lesson
from app.services.grok_ai_client import call_chain, ProviderError


# --- L1: embedding ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        vector[(ord(ch) + i) % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# --- L2: chunking ---
def structure_aware_chunks(html: str) -> list[dict]:
    if not html:
        return []
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(sarlavhasiz)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        if plain_text:
            chunks.append({"heading": heading, "text": plain_text})
    return chunks


# --- L3: cosine similarity ---
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


# --- L6: indeks qurish (faqat o'qish) ---
async def build_search_index(limit_lessons: int = 30) -> list[dict]:
    index: list[dict] = []
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Lesson.id, Lesson.title, Lesson.text_content)
                .where(Lesson.is_published == True, Lesson.text_content.isnot(None))
                .limit(limit_lessons)
            )
        ).all()
    for lesson_id, title, text_content in rows:
        for chunk in structure_aware_chunks(text_content):
            index.append({
                "lesson_id": lesson_id, "lesson_title": title,
                "heading": chunk["heading"], "text": chunk["text"],
                "vector": fake_embed(chunk["text"]),
            })
    return index


# --- L8: retrieve + augment ---
def retrieve(query: str, index: list[dict], k: int = 3, min_score: float = 0.3) -> list[dict]:
    qv = fake_embed(query)
    scored = [{**e, "score": cosine_similarity(qv, e["vector"])} for e in index]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return [e for e in scored[:k] if e["score"] >= min_score]


# --- L9: token byudjeti ---
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def fit_chunks_to_budget(chunks: list[dict], *, token_budget: int, reserved: int = 300) -> list[dict]:
    available = token_budget - reserved
    selected, used = [], 0
    for c in chunks:
        t = estimate_tokens(c["text"])
        if used + t > available:
            break
        selected.append(c)
        used += t
    return selected


def build_augmented_prompt(query: str, chunks: list[dict], history_text: str) -> str:
    context_block = "\\n\\n".join(f"[Dars #{c['lesson_id']} — {c['lesson_title']}]\\n{c['text']}" for c in chunks)
    return (
        "Quyidagi MA'LUMOT va SUHBAT TARIXI asosida savolga javob ber. "
        "Faqat shu ma'lumotdan foydalan. Agar javob ma'lumotda bo'lmasa, "
        "aniq ayt: 'Bu haqida ma'lumot topilmadi' — o'ylab topma.\\n\\n"
        f"SUHBAT TARIXI:\\n{history_text}\\n\\n"
        f"MA'LUMOT:\\n{context_block}\\n\\n"
        f"SAVOL: {query}"
    )


# --- L10: immutable suhbat xotirasi ---
@dataclass(frozen=True)
class ChatTurn:
    question: str
    answer: str


@dataclass(frozen=True)
class ConversationMemory:
    turns: tuple[ChatTurn, ...] = field(default_factory=tuple)
    max_turns: int = 5

    def add_turn(self, question: str, answer: str) -> "ConversationMemory":
        new_turns = (*self.turns, ChatTurn(question, answer))
        if len(new_turns) > self.max_turns:
            new_turns = new_turns[-self.max_turns:]
        return ConversationMemory(turns=new_turns, max_turns=self.max_turns)

    def as_history_text(self) -> str:
        if not self.turns:
            return "(hozircha suhbat tarixi yo'q)"
        return "\\n".join(f"Savol: {t.question}\\nJavob: {t.answer}" for t in self.turns)


# --- YAKUNIY: butun capstone feature ---
async def ask_platform_data(query: str, index: list[dict], memory: ConversationMemory) -> tuple[str, ConversationMemory]:
    \"\"\"To'liq capstone pipeline: retrieve -> byudjet -> augment (xotira
    bilan) -> generate (135-kursdagi call_chain() orqali) -> xotirani
    yangilash. Har ikkala nosozlik holati ham (ma'lumot topilmadi, LLM
    ishlamadi) HALOL xabar bilan qaytariladi — hech qachon jim
    qolinmaydi yoki soxta javob berilmaydi.\"\"\"
    ranked = retrieve(query, index, k=5)
    budgeted = fit_chunks_to_budget(ranked, token_budget=1500)

    if not budgeted:
        answer = "Kechirasiz, bu savolga tegishli ma'lumot platformada topilmadi."
        return answer, memory.add_turn(query, answer)

    prompt = build_augmented_prompt(query, budgeted, memory.as_history_text())
    try:
        answer, _, provider, _ = await call_chain(prompt, max_tokens=400)
    except ProviderError as e:
        answer = f"AI xizmati vaqtincha ishlamayapti (barcha providerlar xato berdi): {e}"

    return answer, memory.add_turn(query, answer)


async def main() -> None:
    print("Indeks qurilmoqda (haqiqiy lessons jadvalidan, faqat o'qish)...")
    index = await build_search_index(limit_lessons=30)
    print(f"{len(index)} ta chunk indekslandi.\\n")

    memory = ConversationMemory()
    for question in [
        "Python funksiyalari qanday e'lon qilinadi?",
        "Uning parametrlari haqida ko'proq ayting",
    ]:
        answer, memory = await ask_platform_data(question, index, memory)
        print(f"Savol: {question}")
        print(f"Javob: {answer}\\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

L13_CODE_RU = """
# ФИНАЛЬНЫЙ CAPSTONE: объединяет функции из всех уроков (L1, L2, L3, L6,
# L8, L9, L10) в одну работающую функцию чат-бота. Часть generate()
# вызывает РЕАЛЬНУЮ call_chain() из курса 135.

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db import base as _base  # noqa: F401
from app.models.lesson import Lesson
from app.services.grok_ai_client import call_chain, ProviderError


# --- из L1: эмбеддинг ---
def fake_embed(text: str, dims: int = 32) -> list[float]:
    text = text.lower().strip()
    vector = [0.0] * dims
    for i, ch in enumerate(text):
        vector[(ord(ch) + i) % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# --- из L2: chunking ---
def structure_aware_chunks(html: str) -> list[dict]:
    if not html:
        return []
    parts = re.split(r"(?=<h3>)", html)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.search(r"<h3>(.*?)</h3>", part)
        heading = heading_match.group(1) if heading_match else "(без заголовка)"
        plain_text = re.sub(r"<[^>]+>", " ", part)
        plain_text = re.sub(r"\\s+", " ", plain_text).strip()
        if plain_text:
            chunks.append({"heading": heading, "text": plain_text})
    return chunks


# --- из L3: cosine similarity ---
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


# --- из L6: построение индекса (только чтение) ---
async def build_search_index(limit_lessons: int = 30) -> list[dict]:
    index: list[dict] = []
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Lesson.id, Lesson.title, Lesson.text_content)
                .where(Lesson.is_published == True, Lesson.text_content.isnot(None))
                .limit(limit_lessons)
            )
        ).all()
    for lesson_id, title, text_content in rows:
        for chunk in structure_aware_chunks(text_content):
            index.append({
                "lesson_id": lesson_id, "lesson_title": title,
                "heading": chunk["heading"], "text": chunk["text"],
                "vector": fake_embed(chunk["text"]),
            })
    return index


# --- из L8: retrieve + augment ---
def retrieve(query: str, index: list[dict], k: int = 3, min_score: float = 0.3) -> list[dict]:
    qv = fake_embed(query)
    scored = [{**e, "score": cosine_similarity(qv, e["vector"])} for e in index]
    scored.sort(key=lambda e: e["score"], reverse=True)
    return [e for e in scored[:k] if e["score"] >= min_score]


# --- из L9: бюджет токенов ---
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def fit_chunks_to_budget(chunks: list[dict], *, token_budget: int, reserved: int = 300) -> list[dict]:
    available = token_budget - reserved
    selected, used = [], 0
    for c in chunks:
        t = estimate_tokens(c["text"])
        if used + t > available:
            break
        selected.append(c)
        used += t
    return selected


def build_augmented_prompt(query: str, chunks: list[dict], history_text: str) -> str:
    context_block = "\\n\\n".join(f"[Урок #{c['lesson_id']} — {c['lesson_title']}]\\n{c['text']}" for c in chunks)
    return (
        "Ответь на вопрос, используя следующие ДАННЫЕ и ИСТОРИЮ ДИАЛОГА. "
        "Используй только эти данные. Если ответа в данных нет, честно "
        "скажи: 'Информация об этом не найдена' — не выдумывай.\\n\\n"
        f"ИСТОРИЯ ДИАЛОГА:\\n{history_text}\\n\\n"
        f"ДАННЫЕ:\\n{context_block}\\n\\n"
        f"ВОПРОС: {query}"
    )


# --- из L10: immutable память диалога ---
@dataclass(frozen=True)
class ChatTurn:
    question: str
    answer: str


@dataclass(frozen=True)
class ConversationMemory:
    turns: tuple[ChatTurn, ...] = field(default_factory=tuple)
    max_turns: int = 5

    def add_turn(self, question: str, answer: str) -> "ConversationMemory":
        new_turns = (*self.turns, ChatTurn(question, answer))
        if len(new_turns) > self.max_turns:
            new_turns = new_turns[-self.max_turns:]
        return ConversationMemory(turns=new_turns, max_turns=self.max_turns)

    def as_history_text(self) -> str:
        if not self.turns:
            return "(истории диалога пока нет)"
        return "\\n".join(f"Вопрос: {t.question}\\nОтвет: {t.answer}" for t in self.turns)


# --- ФИНАЛ: вся capstone-функция ---
async def ask_platform_data(query: str, index: list[dict], memory: ConversationMemory) -> tuple[str, ConversationMemory]:
    \"\"\"Полный capstone pipeline: retrieve -> бюджет -> augment (с
    историей) -> generate (через call_chain() из курса 135) -> обновление
    памяти. Оба случая сбоя (данные не найдены, LLM не сработала)
    возвращаются с ЧЕСТНЫМ сообщением — никогда не молчим и не даём
    выдуманный ответ.\"\"\"
    ranked = retrieve(query, index, k=5)
    budgeted = fit_chunks_to_budget(ranked, token_budget=1500)

    if not budgeted:
        answer = "Извините, информация по этому вопросу на платформе не найдена."
        return answer, memory.add_turn(query, answer)

    prompt = build_augmented_prompt(query, budgeted, memory.as_history_text())
    try:
        answer, _, provider, _ = await call_chain(prompt, max_tokens=400)
    except ProviderError as e:
        answer = f"Сервис AI временно недоступен (все провайдеры дали сбой): {e}"

    return answer, memory.add_turn(query, answer)


async def main() -> None:
    print("Строим индекс (из реальной таблицы lessons, только чтение)...")
    index = await build_search_index(limit_lessons=30)
    print(f"Проиндексировано {len(index)} фрагментов.\\n")

    memory = ConversationMemory()
    for question in [
        "Как объявляются функции в Python?",
        "Расскажи подробнее про его параметры",
    ]:
        answer, memory = await ask_platform_data(question, index, memory)
        print(f"Вопрос: {question}")
        print(f"Ответ: {answer}\\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""

L13_TASK = {
    "task_title": "Yakuniy capstone: platforma ma'lumotlari bo'yicha chatbot",
    "task_title_ru": "Финальный capstone: чат-бот по данным платформы",
    "task_description": (
        "Darsdagi to'liq `ask_platform_data` pipeline'ini ishga tushiring: "
        "kamida 3 bosqichli suhbat o'tkazing, ulardan kamida bittasi "
        "platformada UMUMAN mavjud bo'lmagan mavzu haqida bo'lsin "
        "(halol \"ma'lumot topilmadi\" javobini tekshirish uchun), va "
        "yakunda FastAPI endpoint sifatida qanday joylashtirilishi "
        "mumkinligini (router, Depends, HTTPException) qisqacha "
        "loyihalashtirib yozing (kod yozish shart emas, tuzilish "
        "yetarli)."
    ),
    "task_description_ru": (
        "Запустите полный pipeline `ask_platform_data` из урока: "
        "проведите диалог минимум из 3 шагов, минимум один из которых — "
        "по теме, которой на платформе ВООБЩЕ нет (чтобы проверить "
        "честный ответ 'информация не найдена'), и в конце кратко "
        "спроектируйте (без обязательного кода — достаточно структуры), "
        "как это можно разместить как FastAPI endpoint (router, Depends, "
        "HTTPException)."
    ),
    "task_requirements": (
        "1) Kamida 3 bosqichli suhbat, ConversationMemory bilan. 2) "
        "Kamida bitta savol \"ma'lumot topilmadi\" holatini keltirib "
        "chiqarsin. 3) FastAPI endpoint tuzilishi (router nomi, "
        "dependency'lar, javob shakli) qisqacha yozilsin."
    ),
    "task_requirements_ru": (
        "1) Минимум 3 шага диалога с ConversationMemory. 2) Минимум "
        "один вопрос должен вызвать ситуацию 'информация не найдена'. "
        "3) Кратко описана структура FastAPI endpoint (имя router, "
        "зависимости, форма ответа)."
    ),
    "task_technologies": "Python, FastAPI, SQLAlchemy, httpx",
    "task_deadline_days": 7,
}

L13_SAMPLE = {
    "title": "Namuna: FastAPI endpoint sifatida joylashtirish",
    "description": (
        "135-kursdagi ai_review.py pattern'iga mos, capstone pipeline'ni "
        "chaqiruvchi yangi endpoint namunasi."
    ),
    "sample_type": "code",
    "code_files": [
        {
            "filename": "ask_endpoint.py",
            "language": "python",
            "code": (
                "from fastapi import APIRouter, Depends, HTTPException\n"
                "from sqlalchemy.ext.asyncio import AsyncSession\n\n"
                "from app.dependencies import get_current_student, get_db\n"
                "from app.models.user import Student\n"
                "# from app.services.rag_service import ask_platform_data, build_search_index\n\n"
                "router = APIRouter()\n\n\n"
                "@router.post('/courses/ask')\n"
                "async def ask_about_courses(\n"
                "    question: str,\n"
                "    current_student: Student = Depends(get_current_student),\n"
                "    db: AsyncSession = Depends(get_db),\n"
                "):\n"
                "    \"\"\"135-kursdagi ai_review.py pattern'iga mos: router,\n"
                "    Depends orqali autentifikatsiya, xatolarni HTTPException'ga\n"
                "    aylantirish.\"\"\"\n"
                "    if not question.strip():\n"
                "        raise HTTPException(status_code=400, detail=\"Savol bo'sh bo'lishi mumkin emas\")\n\n"
                "    # index odatda ilova ishga tushganda bir marta quriladi va keshlanadi\n"
                "    # index = await build_search_index()\n"
                "    # answer, _ = await ask_platform_data(question, index, ConversationMemory())\n"
                "    answer = \"(namuna: bu yerda haqiqiy pipeline chaqiriladi)\"\n\n"
                "    return {\"question\": question, \"answer\": answer}\n"
            ),
        },
    ],
}

L13_EXERCISES = [
    {
        "title": "Capstone'ning barcha qismlari",
        "title_ru": "Все части capstone",
        "description": "Yakuniy capstone qaysi darslarning funksiyalarini birlashtiradi?",
        "description_ru": "Функции каких уроков объединяет финальный capstone?",
        "exercise_type": "multiple_choice",
        "options": [
            "L1 (embedding), L2 (chunking), L3 (cosine), L6 (qidiruv), L8 (pipeline), L9 (byudjet), L10 (xotira)",
            "Faqat L0",
            "Faqat L4 va L5",
            "Hech biri — bu butunlay yangi, bog'liq bo'lmagan kod",
        ],
        "options_ru": [
            "L1 (эмбеддинг), L2 (chunking), L3 (cosine), L6 (поиск), L8 (pipeline), L9 (бюджет), L10 (память)",
            "Только L0",
            "Только L4 и L5",
            "Ни один — это совершенно новый, несвязанный код",
        ],
        "correct_answers": "A",
        "hint": "Darsdagi kod qismidagi kommentlarni (\"L1'dan\", \"L6'dan\" va h.k.) eslang.",
        "hint_ru": "Вспомните комментарии в коде урока ('из L1', 'из L6' и т.д.).",
        "explanation": "Capstone kodi har bir funksiyani tegishli darsdan (L1-L10) qayta ishlatadi, hech narsani qaytadan yozmaydi.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Ikkita halol nosozlik holati",
        "title_ru": "Два честных сценария сбоя",
        "description": "Nosozlik holatlarini ularning sabablariga mos qo'ying (avval \"ma'lumot topilmadi\", keyin \"AI xizmati ishlamayapti\")",
        "description_ru": "Сопоставьте сценарии сбоя с их причинами (сначала 'информация не найдена', затем 'сервис AI недоступен')",
        "exercise_type": "drag_and_drop",
        "drag_items": [
            "Byudjetga sig'gan mos chunk topilmadi",
            "Barcha LLM providerlar (groq, gemini, openai) xato berdi",
        ],
        "drag_items_ru": [
            "Не найден подходящий фрагмент, укладывающийся в бюджет",
            "Все провайдеры LLM (groq, gemini, openai) дали сбой",
        ],
        "correct_order": [
            "Byudjetga sig'gan mos chunk topilmadi",
            "Barcha LLM providerlar (groq, gemini, openai) xato berdi",
        ],
        "hint": "ask_platform_data funksiyasidagi ikkita if/except blokini eslang.",
        "hint_ru": "Вспомните два блока if/except в функции ask_platform_data.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "FastAPI pattern",
        "title_ru": "Паттерн FastAPI",
        "description": "Capstone'ni FastAPI endpoint sifatida joylashtirishda foydalanuvchini tekshirish uchun qaysi mexanizm ishlatiladi (135-kursdagi ai_review.py'dagi kabi)?",
        "description_ru": "Какой механизм используется для проверки пользователя при размещении capstone как FastAPI endpoint (как в ai_review.py из курса 135)?",
        "exercise_type": "multiple_choice",
        "options": [
            "Depends(get_current_student)",
            "Global o'zgaruvchi",
            "Cookie'ni qo'lda o'qish",
            "Hech qanday tekshiruv kerak emas",
        ],
        "options_ru": [
            "Depends(get_current_student)",
            "Глобальная переменная",
            "Ручное чтение cookie",
            "Никакая проверка не нужна",
        ],
        "correct_answers": "A",
        "hint": "135-kursdagi ai_review.py endpoint'ini eslang.",
        "hint_ru": "Вспомните endpoint ai_review.py из курса 135.",
        "explanation": "FastAPI'da Depends(get_current_student) orqali joriy autentifikatsiyalangan foydalanuvchi olinadi — bu 135-kursda ko'rgan haqiqiy pattern.",
        "difficulty_level": "Medium",
        "points": 8,
    },
    {
        "title": "Butun kursning yakuniy xulosasi",
        "title_ru": "Итоговый вывод всего курса",
        "description": "O'z so'zlaringiz bilan tushuntiring: bu capstone loyihasi RAG'ning qaysi asosiy g'oyasini (0-darsdan boshlab) HAQIQIY, ishlaydigan kodda namoyish etadi, va nima uchun bu \"o'ylab topilgan misol\" emas?",
        "description_ru": "Объясните своими словами: какую основную идею RAG (начиная с урока 0) демонстрирует этот capstone-проект в РЕАЛЬНОМ, работающем коде, и почему это не 'выдуманный пример'?",
        "exercise_type": "text_input",
        "expected_answer": (
            "Talaba RAG'ning asosiy g'oyasini (LLM'ni haqiqiy ma'lumotga "
            "asoslash, gallyutsinatsiyani kamaytirish) va bu loyihaning "
            "ushbu platformaning HAQIQIY lessons jadvali ustida "
            "ishlashini (o'ylab topilgan hujjatlar emas) tushuntirishi "
            "kerak."
        ),
        "hint": "0-darsdagi gallyutsinatsiya muammosini va L6/L13'dagi haqiqiy lessons jadvalini eslang.",
        "hint_ru": "Вспомните проблему галлюцинации из урока 0 и реальную таблицу lessons из L6/L13.",
        "difficulty_level": "Hard",
        "points": 12,
    },
]

# ---------------------------------------------------------------------------
# LESSONS
# ---------------------------------------------------------------------------

LESSONS = [
    {
        "order": 0,
        "title": "RAG nima va nega LLM'ning o'z bilimi yetarli emas",
        "title_ru": "Что такое RAG и почему знаний LLM недостаточно",
        "points_reward": 10,
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
        "title": "Embedding'lar 101: matnni vektorga aylantirish",
        "title_ru": "Эмбеддинги 101: превращение текста в вектор",
        "points_reward": 10,
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
        "title": "Hujjatlarni chunk'larga bo'lish",
        "title_ru": "Разбиение документов на чанки",
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
        "title": "Vektor o'xshashligi matematikasi: cosine similarity",
        "title_ru": "Математика векторного сходства: косинусное сходство",
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
        "title": "Vektor bazalari taqqoslash: pgvector, Chroma, Pinecone",
        "title_ru": "Сравнение векторных баз: pgvector, Chroma, Pinecone",
        "points_reward": 10,
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
        "title": "pgvector'ni sozlash: Postgres'ga vektor qo'shish",
        "title_ru": "Настройка pgvector: добавление векторов в Postgres",
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
        "title": "Amaliy semantik qidiruv: platformaning o'z darslari ustida",
        "title_ru": "Практический семантический поиск по урокам платформы",
        "points_reward": 20,
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
        "title": "R1: Takrorlash — Embedding'dan qidiruvgacha",
        "title_ru": "R1: Повторение — от эмбеддингов до поиска",
        "points_reward": 15,
        "text_content": L7_TEXT,
        "text_content_ru": L7_TEXT_RU,
        "code_content": None,
        "code_content_ru": None,
        "code_language": None,
        "task": L7_TASK,
        "sample": L7_SAMPLE,
        "exercises": L7_EXERCISES,
    },
    {
        "order": 8,
        "title": "To'liq RAG pipeline: retrieve -> augment -> generate",
        "title_ru": "Полный RAG pipeline: retrieve -> augment -> generate",
        "points_reward": 20,
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
        "title": "Kontekst oynasi va prompt byudjeti chunked retrieval bilan",
        "title_ru": "Окно контекста и бюджет промпта при chunked retrieval",
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
        "title": "Suhbat xotirasi: chat tarixi + retrieval",
        "title_ru": "Память диалога: история чата + retrieval",
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
        "title": "RAG sifatini halol baholash",
        "title_ru": "Честная оценка качества RAG",
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
        "title": "R2: Takrorlash — To'liq RAG va sifat baholash",
        "title_ru": "R2: Повторение — полный RAG и оценка качества",
        "points_reward": 15,
        "text_content": L12_TEXT,
        "text_content_ru": L12_TEXT_RU,
        "code_content": None,
        "code_content_ru": None,
        "code_language": None,
        "task": L12_TASK,
        "sample": L12_SAMPLE,
        "exercises": L12_EXERCISES,
    },
    {
        "order": 13,
        "title": "Yakuniy capstone: platforma ma'lumotlari bo'yicha savol-javob chatboti",
        "title_ru": "Финальный capstone: чат-бот вопрос-ответ по данным платформы",
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
# convention as course 135 and earlier courses — submission tasks aren't
# separately points-scored beyond the lesson's own points_reward).
_lesson_points = sum(l.get("points_reward", 10) for l in LESSONS)
_exercise_points = sum(
    ex.get("points", 10) for l in LESSONS for ex in (l.get("exercises") or [])
)
COURSE["max_points"] = _lesson_points + _exercise_points
