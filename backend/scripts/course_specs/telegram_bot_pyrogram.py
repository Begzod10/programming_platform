"""Telegram Bot Track: Pyrogram — zamonaviy MTProto kutubxonasi.

Pure-data course spec — see course_builder/__init__.py for the contract.
Prerequisite: course 48 (Telegram Bot aiogram) — talaba Bot API asoslarini
(handlerlar, klaviaturalar, FSM, webhook) allaqachon biladi deb hisoblanadi,
shuning uchun bu yerda ular qayta o'qitilmaydi.

Pyrogram — Telegram'ning xom MTProto protokoli ustida ishlaydigan kutubxona
(aiogram kabi Bot API wrapper emas, Telethon kabi to'g'ridan-to'g'ri
protokol darajasida ishlaydi). Kursning markaziy farqlovchi xususiyati —
bitta Client klassi ham bot sifatida (bot_token), ham oddiy foydalanuvchi
sifatida (telefon raqami orqali) ishga tushirilishi mumkin. Boshqa
o'ziga xos jihatlar: dekorator-asosidagi handlerlar (@app.on_message),
filters tizimi (& / | bilan birlashtiriladigan), plugins orqali katta
botlarni modullarga bo'lish, va TgCrypto — tezkor shifrlash kutubxonasi.

MTProto asoslari bo'yicha Telethon kursi bilan ba'zi umumiylik bor
(kutilgan holat — ikkala kurs ham MTProto ustida ishlaydi), lekin bu kurs
Pyrogram'ning o'z API'si, idiomalari va farqlovchi xususiyatlariga
(dual-mode, dekoratorlar, filters, plugins, TgCrypto) e'tibor qaratadi.

Build with:
    cd backend
    python scripts/build_course.py course_specs/telegram_bot_pyrogram.py --dry-run
    python scripts/build_course.py course_specs/telegram_bot_pyrogram.py
"""

COURSE = {
    "title": "Pyrogram: Zamonaviy Telegram Client Kutubxonasi",
    "title_ru": "Pyrogram: современная библиотека Telegram-клиента",
    "description": (
        "aiogram kursidan keyingi muqobil yo'nalish: Pyrogram — Telegram'ning xom MTProto "
        "protokoli ustida ishlaydigan kutubxona. Bitta Client klassi bilan ham bot "
        "(bot_token), ham oddiy foydalanuvchi hisobi (telefon raqami) sifatida ishlash, "
        "dekorator-asosidagi handlerlar, filters tizimi (& / | bilan birlashtirish), "
        "sessiya xavfsizligi, boy xabarlar va media guruhlari, callback/inline query'lar, "
        "katta hajmdagi chat tarixi va a'zolar bo'yicha async iteratsiya, plugins orqali "
        "katta botlarni tashkil qilish, xom MTProto chaqiruvlari (invoke), TgCrypto va "
        "unumdorlik, xavfsiz deploy, va yakuniy dual-mode (bot + ixtiyoriy userbot) capstone."
    ),
    "description_ru": (
        "Альтернативное направление после курса aiogram: Pyrogram — библиотека, работающая "
        "поверх «сырого» протокола MTProto Telegram. Один класс Client для запуска и как бот "
        "(bot_token), и как обычный пользовательский аккаунт (номер телефона), обработчики "
        "на основе декораторов, система фильтров (объединение через & / |), безопасность "
        "сессий, насыщенные сообщения и медиа-группы, callback/inline query, асинхронная "
        "итерация по большой истории чата и участникам, система плагинов для организации "
        "крупных ботов, «сырые» вызовы MTProto (invoke), TgCrypto и производительность, "
        "безопасный деплой и финальный dual-mode (бот + опциональный userbot) капстоун."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 4,
    "max_points": 500,
    "category_id": 12,
    "prerequisite_course_id": 48,
    "display_order": 703,
    "image_url": "https://docs.pyrogram.org/_static/pyrogram.png",
    "thumbnail_url": "https://docs.pyrogram.org/_static/pyrogram.png",
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    {
        "order": 0,
        "title": "1-Pyrogram sarhisobi: MTProto, aiogram va Telethon bilan solishtirish",
        "title_ru": "1-Обзор Pyrogram: сравнение с MTProto, aiogram и Telethon",
        "points_reward": 14,
        "code_language": "python",
        "text_content": """<h3>Pyrogram nima va u qanday darajada ishlaydi?</h3>
<p>48-kursda siz <strong>aiogram</strong> bilan ishladingiz — bu kutubxona Telegram'ning rasmiy
<strong>Bot API</strong>'si ustiga qurilgan HTTP wrapper: bot serverga so'rov yuboradi, Telegram
serveri javob qaytaradi, hammasi oddiy HTTP(S) orqali. <strong>Pyrogram</strong> butunlay boshqa
darajada ishlaydi — u Telegram'ning rasmiy ilovalari (mobil ilova, Telegram Desktop) foydalanadigan
xom <strong>MTProto</strong> protokolini o'zi amalga oshiradi va to'g'ridan-to'g'ri Telegram
serverlariga TCP orqali ulanadi, Bot API'ni butunlay chetlab o'tadi. Bu Pyrogram'ga Bot API orqali
umuman ochiq bo'lmagan imkoniyatlarni beradi — masalan, chatning to'liq tarixini sahifalab o'qish,
kanal a'zolarining to'liq ro'yxatini olish, yoki oddiy foydalanuvchi sifatida harakat qilish.</p>

<h3>Bitta kutubxona — ikki xil "shaxsga kirish" rejimi</h3>
<p>Pyrogram'ning kursimiz davomida markaziy o'rin tutadigan farqlovchi xususiyati shu: bitta
<code>Client</code> klassi ham <strong>bot</strong> sifatida (<code>bot_token=</code> parametri
bilan, BotFather'dan olingan token), ham oddiy <strong>foydalanuvchi hisobi</strong> sifatida
(telefon raqami orqali kirish, ko'pincha "userbot" deb ataladi) ishga tushirilishi mumkin. Kod
darajasida farq atigi konstruktorga qaysi parametr uzatilishida — qolgan hammasi (handlerlar,
filters, xabar yuborish metodlari) bir xil qoladi. aiogram'da bunday narsa tamoman yo'q — u faqat
Bot API bilan ishlaydi, va Bot API faqat bot tokenlarini qabul qiladi, foydalanuvchi hisobi bilan
umuman kira olmaysiz.</p>

<h3>Telethon bilan qanday farq bor?</h3>
<p>Telethon ham xuddi Pyrogram kabi MTProto ustida ishlaydi va ham bot, ham userbot rejimini
qo'llab-quvvatlaydi — shu jihatdan ikkalasi bir-biriga aiogram'dan ko'ra yaqinroq. Lekin ular
API dizayni bo'yicha farq qiladi: Pyrogram dekorator-asosidagi <code>@app.on_message(filters...)</code>
uslubini va <code>filters</code> modulini (& / | bilan birlashtiriladigan) markaziy qiladi, hamda
o'zining <code>plugins</code> tizimi va <strong>TgCrypto</strong> deb ataladigan C-kengaytmali
tezkor shifrlash kutubxonasi bilan keladi. Kursimiz davomida asosiy e'tibor aynan shu
Pyrogram'ga xos jihatlarga qaratiladi — MTProto'ning umumiy tarixi va ichki tuzilishi emas.</p>

<h3>Uchta kutubxona — bir joyda solishtirish</h3>
<table>
<tr><th>Xususiyat</th><th>aiogram</th><th>Pyrogram</th><th>Telethon</th></tr>
<tr><td>Protokol qatlami</td><td>Bot API (HTTP)</td><td>MTProto (TCP)</td><td>MTProto (TCP)</td></tr>
<tr><td>Kirish rejimlari</td><td>Faqat bot</td><td>Bot + userbot (bitta klass)</td><td>Bot + userbot</td></tr>
<tr><td>Handler uslubi</td><td>Router + filter obyektlari</td><td>Dekoratorlar (@app.on_message)</td><td>Dekoratorlar (@client.on)</td></tr>
<tr><td>Filterlash</td><td>magic filter / F obyekti</td><td>filters moduli, & / | operatorlari</td><td>events sinflari</td></tr>
<tr><td>Modullarga bo'lish</td><td>Router qo'lda ulanadi</td><td>Built-in plugins= parametri</td><td>Qo'lda tashkil etiladi</td></tr>
<tr><td>Shifrlash tezlashtirish</td><td>Kerak emas (HTTP)</td><td>TgCrypto (ixtiyoriy, tavsiya etiladi)</td><td>cryptg (ixtiyoriy)</td></tr>
</table>

<h3>Nega bir loyiha aynan Pyrogram'ni tanlashi mumkin</h3>
<ul>
<li>Bitta kod bazasida ham bot, ham (ixtiyoriy) userbot funksiyasini birga ishlatish kerak bo'lganda</li>
<li>Bot API'da yo'q imkoniyatlar kerak bo'lganda: chuqur tarix skanerlash, katta kanallar a'zolarini sahifalab o'qish</li>
<li>Dekorator-asosidagi, o'qilishi oson va qisqa kod uslubi afzal ko'rilsa</li>
<li>Katta bot kodini <code>plugins</code> orqali fayllarga tabiiy bo'lib ajratish muhim bo'lsa</li>
<li>TgCrypto orqali yuqori tezlikda ishlaydigan, ko'p update qabul qiladigan bot kerak bo'lsa</li>
</ul>

<pre class="mermaid">
flowchart TB
  T["Telegram server"]
  T -->|"HTTP Bot API"| A["aiogram
(faqat bot rejimi)"]
  T -->|"MTProto (TCP)"| P["Pyrogram
Client(bot_token=...)
yoki
Client(phone_number=...)"]
  T -->|"MTProto (TCP)"| TH["Telethon
(bot yoki userbot)"]
  A --> AH["@router.message()
filter obyektlari"]
  P --> PH["@app.on_message()
filters.command & filters.chat"]
  TH --> THH["@client.on(events.NewMessage)"]
</pre>
<p>Diagram uchta kutubxonaning protokol darajasidagi joylashuvini va handler ro'yxatga olish
uslubidagi farqini ko'rsatadi — aiogram HTTP Bot API ustida, Pyrogram va Telethon esa
to'g'ridan-to'g'ri MTProto ustida ishlaydi.</p>

<h3>Kurs davomida nimalarni o'rganamiz</h3>
<p>Keyingi darslarda ketma-ket: <code>api_id</code>/<code>api_hash</code> olish va Client'ni ikkala
rejimda sozlash, dekorator-asosidagi handlerlar, filters tizimi, sessiya xavfsizligi, boy xabarlar
va media guruhlari, callback/inline query'lar, katta hajmdagi ma'lumotlar bo'yicha async
iteratsiya, plugins tizimi, xom MTProto chaqiruvlari (<code>invoke()</code>), TgCrypto va
unumdorlik, xavfsiz deploy, va nihoyat — bot hamda ixtiyoriy userbot rejimini birlashtirgan
yakuniy capstone loyiha.</p>""",
        "text_content_ru": """<h3>Что такое Pyrogram и на каком уровне он работает?</h3>
<p>В курсе 48 вы работали с <strong>aiogram</strong> — эта библиотека построена поверх
официального HTTP-обёртки Telegram <strong>Bot API</strong>: бот отправляет запрос на сервер,
сервер Telegram возвращает ответ, всё через обычный HTTP(S). <strong>Pyrogram</strong> работает
на совершенно другом уровне — он сам реализует «сырой» протокол <strong>MTProto</strong>,
который используют официальные приложения Telegram (мобильное приложение, Telegram Desktop), и
подключается напрямую к серверам Telegram по TCP, полностью минуя Bot API. Это даёт Pyrogram
доступ к возможностям, вообще не открытым через Bot API — например, постраничное чтение полной
истории чата, получение полного списка участников канала или работа в качестве обычного
пользователя.</p>

<h3>Одна библиотека — два режима «входа»</h3>
<p>Ключевая отличительная особенность Pyrogram, центральная для всего курса: один класс
<code>Client</code> может быть запущен как <strong>бот</strong> (с параметром
<code>bot_token=</code>, токен от BotFather), так и как обычный <strong>пользовательский
аккаунт</strong> (вход по номеру телефона, часто называемый «юзербот»). На уровне кода разница
только в том, какой параметр передан в конструктор — всё остальное (обработчики, фильтры, методы
отправки сообщений) остаётся одинаковым. В aiogram такого вообще нет — он работает только с
Bot API, а Bot API принимает только токены ботов, войти пользовательским аккаунтом там нельзя
в принципе.</p>

<h3>В чём разница с Telethon?</h3>
<p>Telethon, как и Pyrogram, работает поверх MTProto и тоже поддерживает и бот-режим, и
юзербот-режим — в этом смысле они ближе друг к другу, чем к aiogram. Но они различаются по
дизайну API: Pyrogram делает центральным декораторный стиль <code>@app.on_message(filters...)</code>
и модуль <code>filters</code> (объединяемый через & / |), плюс собственную систему
<code>plugins</code> и <strong>TgCrypto</strong> — быстрая библиотека шифрования на C-расширении.
На протяжении курса основное внимание уделяется именно этим особенностям Pyrogram — а не общей
истории и внутреннему устройству MTProto.</p>

<h3>Три библиотеки — сравнение в одном месте</h3>
<table>
<tr><th>Свойство</th><th>aiogram</th><th>Pyrogram</th><th>Telethon</th></tr>
<tr><td>Уровень протокола</td><td>Bot API (HTTP)</td><td>MTProto (TCP)</td><td>MTProto (TCP)</td></tr>
<tr><td>Режимы входа</td><td>Только бот</td><td>Бот + юзербот (один класс)</td><td>Бот + юзербот</td></tr>
<tr><td>Стиль обработчиков</td><td>Router + объекты фильтров</td><td>Декораторы (@app.on_message)</td><td>Декораторы (@client.on)</td></tr>
<tr><td>Фильтрация</td><td>magic filter / объект F</td><td>модуль filters, операторы & / |</td><td>классы events</td></tr>
<tr><td>Разбиение на модули</td><td>Router подключается вручную</td><td>Встроенный параметр plugins=</td><td>Организуется вручную</td></tr>
<tr><td>Ускорение шифрования</td><td>Не нужно (HTTP)</td><td>TgCrypto (опционально, рекомендуется)</td><td>cryptg (опционально)</td></tr>
</table>

<h3>Почему проект может выбрать именно Pyrogram</h3>
<ul>
<li>Когда в одной кодовой базе нужно совместить и бот, и (опционально) юзербот-функциональность</li>
<li>Когда нужны возможности, которых нет в Bot API: глубокое сканирование истории, постраничное чтение участников больших каналов</li>
<li>Когда предпочтителен декораторный, легко читаемый и лаконичный стиль кода</li>
<li>Когда важно естественно разбить большой код бота на модули через <code>plugins</code></li>
<li>Когда нужен бот с высокой производительностью, обрабатывающий много обновлений, с TgCrypto</li>
</ul>

<pre class="mermaid">
flowchart TB
  T["Telegram server"]
  T -->|"HTTP Bot API"| A["aiogram
(только бот-режим)"]
  T -->|"MTProto (TCP)"| P["Pyrogram
Client(bot_token=...)
или
Client(phone_number=...)"]
  T -->|"MTProto (TCP)"| TH["Telethon
(бот или юзербот)"]
  A --> AH["@router.message()
объекты фильтров"]
  P --> PH["@app.on_message()
filters.command & filters.chat"]
  TH --> THH["@client.on(events.NewMessage)"]
</pre>
<p>Диаграмма показывает расположение трёх библиотек на уровне протокола и разницу в стиле
регистрации обработчиков — aiogram работает поверх HTTP Bot API, а Pyrogram и Telethon —
напрямую поверх MTProto.</p>

<h3>Что мы изучим в течение курса</h3>
<p>В следующих уроках последовательно: получение <code>api_id</code>/<code>api_hash</code> и
настройка Client в обоих режимах, обработчики на основе декораторов, система фильтров,
безопасность сессий, насыщенные сообщения и медиа-группы, callback/inline query, асинхронная
итерация по большим объёмам данных, система plugins, «сырые» вызовы MTProto (<code>invoke()</code>),
TgCrypto и производительность, безопасный деплой, и наконец — финальный капстоун, объединяющий
бота и опциональный режим юзербота.</p>""",
        "code_content": """# O'RNATISH: pip install pyrogram tgcrypto
#
# Bu darsda hali Client'ni to'liq sozlamaymiz (keyingi darsda batafsil) —
# lekin uchta kutubxonaning "salom dunyo" darajasidagi farqini his qilish
# uchun qisqacha taqqoslash keltirilgan. Faqat Pyrogram qismi shu kursda
# to'liq ishlaydigan holatga keladi.

# --- Pyrogram (shu kurs markazi) ---
from pyrogram import Client, filters

app = Client("my_account")  # nomi bilan session fayli yaratiladi


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message):
    await message.reply_text(
        f"Salom, {message.from_user.first_name}! Men Pyrogram orqali ishlayapman."
    )


if __name__ == "__main__":
    app.run()  # ichkarida connect() -> idle() -> disconnect() ni boshqaradi


# --- Solishtirish uchun: aiogram'da xuddi shu handler (Bot API, HTTP) ---
#
# from aiogram import Bot, Dispatcher, F
# from aiogram.filters import Command
#
# bot = Bot(token="...")
# dp = Dispatcher()
#
# @dp.message(Command("start"))
# async def start_handler(message):
#     await message.answer(f"Salom, {message.from_user.first_name}!")
#
# aiogram'da faqat bot_token bor — foydalanuvchi hisobi sifatida kira olmaysiz.


# --- Solishtirish uchun: Telethon'da xuddi shu handler (MTProto, ham dual-mode) ---
#
# from telethon import TelegramClient, events
#
# client = TelegramClient("my_account", api_id, api_hash)
#
# @client.on(events.NewMessage(pattern="/start"))
# async def start_handler(event):
#     await event.reply("Salom!")
#
# client.start()  # yoki client.start(bot_token="...") — bot rejimi uchun
# client.run_until_disconnected()
""",
        "code_content_ru": """# УСТАНОВКА: pip install pyrogram tgcrypto
#
# В этом уроке мы ещё не настраиваем Client полностью (подробно — в
# следующем уроке) — но приведено краткое сравнение уровня «hello world»
# для трёх библиотек. Полностью рабочей в рамках этого курса становится
# только часть с Pyrogram.

# --- Pyrogram (центр этого курса) ---
from pyrogram import Client, filters

app = Client("my_account")  # по имени создаётся файл сессии


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message):
    await message.reply_text(
        f"Привет, {message.from_user.first_name}! Я работаю через Pyrogram."
    )


if __name__ == "__main__":
    app.run()  # внутри управляет connect() -> idle() -> disconnect()


# --- Для сравнения: тот же обработчик в aiogram (Bot API, HTTP) ---
#
# from aiogram import Bot, Dispatcher, F
# from aiogram.filters import Command
#
# bot = Bot(token="...")
# dp = Dispatcher()
#
# @dp.message(Command("start"))
# async def start_handler(message):
#     await message.answer(f"Привет, {message.from_user.first_name}!")
#
# В aiogram есть только bot_token — войти пользовательским аккаунтом нельзя.


# --- Для сравнения: тот же обработчик в Telethon (MTProto, тоже dual-mode) ---
#
# from telethon import TelegramClient, events
#
# client = TelegramClient("my_account", api_id, api_hash)
#
# @client.on(events.NewMessage(pattern="/start"))
# async def start_handler(event):
#     await event.reply("Привет!")
#
# client.start()  # или client.start(bot_token="...") — для режима бота
# client.run_until_disconnected()
""",
        "video_url": None,
        "task": {
            "task_title": "Taqqoslash jadvali: loyihangiz uchun to'g'ri tanlov",
            "task_title_ru": "Сравнительная таблица: правильный выбор для вашего проекта",
            "task_description": (
                "Qisqa (5-8 band) taqqoslash hisobotini yozing: aiogram, Pyrogram va Telethon "
                "orasidan tasavvuriy loyiha (masalan, 'katta ochiq kanal statistikasini yig'uvchi "
                "va shaxsiy chatlarda savol-javob beruvchi bot') uchun qaysi biri tanlanadi va nega. "
                "Har bir kutubxonaning kamida bitta aniq afzalligini va kamida bitta cheklovini "
                "sanab bering."
            ),
            "task_description_ru": (
                "Напишите краткий (5-8 пунктов) сравнительный отчёт: для гипотетического проекта "
                "(например, 'бот, собирающий статистику большого открытого канала и отвечающий на "
                "вопросы в личных чатах') какая из библиотек — aiogram, Pyrogram или Telethon — "
                "будет выбрана и почему. Укажите хотя бы одно явное преимущество и хотя бы одно "
                "ограничение для каждой библиотеки."
            ),
            "task_requirements": (
                "Barcha uchta kutubxona muhokama qilinishi kerak; xulosa aniq bitta tanlov bilan "
                "yakunlanishi kerak, sabab ko'rsatilgan holda."
            ),
            "task_requirements_ru": (
                "Должны быть обсуждены все три библиотеки; вывод должен заканчиваться конкретным "
                "выбором с указанием причины."
            ),
            "task_technologies": "Pyrogram, aiogram, Telethon (nazariy taqqoslash)",
            "task_deadline_days": 2,
        },
        "sample": {
            "title": "Namuna: minimal Pyrogram echo-bot",
            "title_ru": "Пример: минимальный эхо-бот на Pyrogram",
            "description": "Eng oddiy ishlaydigan Pyrogram boti — /start buyrug'iga javob beradi.",
            "description_ru": "Простейший рабочий бот на Pyrogram — отвечает на команду /start.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "bot.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters

# BotFather'dan bot_token, my.telegram.org'dan api_id/api_hash olinadi
app = Client(
    "echo_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Salom! Menga har qanday matn yuboring, men uni qaytaraman.")


@app.on_message(filters.text & ~filters.command("start"))
async def echo(client, message):
    await message.reply_text(message.text)


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Pyrogram qaysi protokol ustida ishlaydi",
                "title_ru": "На каком протоколе работает Pyrogram",
                "description": "Pyrogram to'g'ridan-to'g'ri qaysi protokol bilan ishlaydi?",
                "description_ru": "С каким протоколом Pyrogram работает напрямую?",
                "exercise_type": "multiple_choice",
                "options": ["Bot API (HTTP)", "MTProto (TCP)", "WebSocket", "gRPC"],
                "options_ru": ["Bot API (HTTP)", "MTProto (TCP)", "WebSocket", "gRPC"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "aiogram bilan Pyrogram'ning asosiy farqini eslang.",
                "hint_ru": "Вспомните основное отличие Pyrogram от aiogram.",
                "explanation": "Pyrogram Telegram mijozlari foydalanadigan xom MTProto protokolini o'zi amalga oshiradi, Bot API'ni chetlab o'tadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Dual-mode Client parametri",
                "title_ru": "Параметр dual-mode Client",
                "description": "Pyrogram Client'ni bot sifatida ishga tushirish uchun qaysi parametr beriladi: Client(___=\"...\")",
                "description_ru": "Какой параметр передаётся, чтобы запустить Pyrogram Client как бота: Client(___=\"...\")",
                "exercise_type": "fill_in_blank",
                "correct_answers": "bot_token",
                "hint": "BotFather'dan olingan qatorni saqlaydigan parametr nomi.",
                "hint_ru": "Название параметра, хранящего строку, полученную от BotFather.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kutubxonalarni xususiyatlariga mos qo'ying",
                "title_ru": "Сопоставьте библиотеки с их особенностями",
                "description": "Har bir kutubxonani unga eng mos xususiyat bilan tartibga joylashtiring (aiogram, Pyrogram, Telethon tartibida emas — tavsiflarni to'g'ri ketma-ketlikda joylashtiring)",
                "description_ru": "Расположите описания в порядке, соответствующем aiogram, Pyrogram, Telethon",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "Faqat Bot API (HTTP), faqat bot rejimi",
                    "MTProto, dual-mode, plugins va TgCrypto bilan",
                    "MTProto, dual-mode, events-asosidagi API",
                ],
                "drag_items_ru": [
                    "Только Bot API (HTTP), только режим бота",
                    "MTProto, dual-mode, с plugins и TgCrypto",
                    "MTProto, dual-mode, API на основе events",
                ],
                "correct_order": [
                    "Faqat Bot API (HTTP), faqat bot rejimi",
                    "MTProto, dual-mode, plugins va TgCrypto bilan",
                    "MTProto, dual-mode, events-asosidagi API",
                ],
                "hint": "Birinchisi aiogram, ikkinchisi Pyrogram, uchinchisi Telethon haqida.",
                "hint_ru": "Первое — об aiogram, второе — о Pyrogram, третье — о Telethon.",
                "difficulty_level": "Medium",
                "points": 8,
            },
            {
                "title": "Userbot nima ekanini tushuntiring",
                "title_ru": "Объясните, что такое юзербот",
                "description": "O'z so'zlaringiz bilan tushuntiring: Pyrogram kontekstida 'userbot' atamasi nimani anglatadi va u oddiy botdan nimasi bilan farq qiladi?",
                "description_ru": "Своими словами объясните: что означает термин 'юзербот' в контексте Pyrogram и чем он отличается от обычного бота?",
                "exercise_type": "text_input",
                "expected_answer": "Userbot — Pyrogram Client'ni bot_token o'rniga telefon raqami bilan ishga tushirib, oddiy foydalanuvchi hisobi sifatida ishlatish; u foydalanuvchiga xos imkoniyatlarga (masalan, boshqa botlarga xabar yozish, guruhga oddiy a'zo sifatida qo'shilish) ega bo'ladi, bot esa BotFather cheklovlariga bo'ysunadi.",
                "hint": "bot_token va phone_number farqini, va foydalanuvchi hisobi nimalar qila olishini o'ylab ko'ring.",
                "hint_ru": "Подумайте о разнице bot_token и phone_number, и о том, что может пользовательский аккаунт.",
                "difficulty_level": "Medium",
                "points": 7,
            },
        ],
    },
    {
        "order": 1,
        "title": "2-api_id/api_hash olish va birinchi Client: bot rejimi va foydalanuvchi rejimi",
        "title_ru": "2-Получение api_id/api_hash и первый Client: режим бота и режим пользователя",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>api_id va api_hash — nima uchun kerak va qayerdan olinadi</h3>
<p>Bot API'da faqat bitta narsa kerak edi — BotFather'dan bot tokeni. Pyrogram MTProto darajasida
ishlagani uchun yana bitta narsa talab qiladi: <strong>api_id</strong> (raqam) va
<strong>api_hash</strong> (satr) — bu Telegram tomonidan har bir "ilova"ga beriladigan
identifikatorlar, https://my.telegram.org saytida shaxsiy Telegram hisobingiz bilan kirib,
"API development tools" bo'limida yangi ilova ro'yxatdan o'tkazish orqali olinadi (ilova nomi va
qisqa tavsif kifoya). Bu qadam <em>ham bot, ham userbot rejimi uchun bir xil</em> — ikkalasida
ham api_id/api_hash kerak, chunki ular MTProto ulanishini identifikatsiya qiladi, bot_token esa
faqat MTProto ustida qaysi "shaxs" sifatida kirishni bildiradi.</p>

<h3>Client konstruktorining umumiy skeleti</h3>
<pre><code>from pyrogram import Client

app = Client(
    "session_nomi",       # session fayli shu nom bilan saqlanadi (masalan session_nomi.session)
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="./sessions", # ixtiyoriy — session fayllari qayerda saqlanishini bildiradi
)</code></pre>
<p>Bu yerga qo'shimcha bitta parametr qo'shilsa — kirish rejimi belgilanadi.</p>

<h3>1-rejim: Bot sifatida kirish</h3>
<p>BotFather'dan olingan tokenni <code>bot_token=</code> parametriga uzating:</p>
<pre><code>app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)</code></pre>
<p>Birinchi <code>app.run()</code> chaqirilganda Pyrogram bot nomidan avtorizatsiya qiladi va
<code>my_bot.session</code> faylini yaratadi — keyingi ishga tushirishlarda qayta login talab
qilinmaydi, chunki sessiya fayl ichida saqlangan.</p>

<h3>2-rejim: Foydalanuvchi (userbot) sifatida kirish</h3>
<p><code>bot_token</code> o'rniga hech narsa bermang (yoki <code>phone_number=</code> bering) —
Pyrogram konsolda interaktiv login jarayonini boshlaydi:</p>
<pre><code>app = Client("my_account", api_id=API_ID, api_hash=API_HASH)
# birinchi ishga tushirishda konsolda so'raladi:
#   1) Telefon raqami (+998...)
#   2) Telegram yuborgan tasdiqlash kodi (SMS yoki ilova orqali)
#   3) Agar ikki bosqichli tasdiqlash (2FA) yoqilgan bo'lsa — parol</code></pre>
<p>Bu jarayon <strong>faqat birinchi marta</strong> sodir bo'ladi — muvaffaqiyatli login
<code>my_account.session</code> fayliga yoziladi, va keyingi ishga tushirishlar hech qanday
so'rovsiz, session fayldan darhol ulanadi. Aynan shu sabab bilan session fayl juda qadrli va
xavfiy ma'lumot hisoblanadi (keyingi darsda batafsil).</p>

<h3>Ikkala rejim orasidagi amaliy farqlar</h3>
<table>
<tr><th>Jihat</th><th>Bot rejimi</th><th>Foydalanuvchi (userbot) rejimi</th></tr>
<tr><td>Kirish uchun kerak</td><td>bot_token</td><td>Telefon raqami + SMS kod (+ 2FA)</td></tr>
<tr><td>Kimning nomidan harakat qiladi</td><td>Bot (alohida "shaxs")</td><td>Sizning shaxsiy hisobingiz</td></tr>
<tr><td>Guruhga qo'shilish</td><td>Faqat taklif qilinganda</td><td>O'zi istalgan ochiq guruhga qo'shilishi mumkin</td></tr>
<tr><td>Flood/limitlar</td><td>Bot API limitlariga yaqin, ancha yumshoq</td><td>Odatiy foydalanuvchi limitlariga bo'ysunadi, qattiqroq</td></tr>
<tr><td>Xavf darajasi</td><td>Token oshkor bo'lsa — botni qayta yaratsa bo'ladi</td><td>Sessiya oshkor bo'lsa — butun hisobingiz egallanadi</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  S["Client('nomi', api_id, api_hash, ...)"]
  S -->|"+ bot_token=BOT_TOKEN"| B["Bot rejimi
BotFather tokeni bilan
darhol avtorizatsiya"]
  S -->|"parametrsiz (yoki phone_number=)"| U["Foydalanuvchi rejimi
birinchi marta:
telefon -> SMS kod -> (2FA)"]
  B --> SESS1["bot_nomi.session fayli"]
  U --> SESS2["akkaunt_nomi.session fayli"]
  SESS1 --> RUN["app.run() — keyingi ishga tushirishlarda
qayta login SO'RALMAYDI"]
  SESS2 --> RUN
</pre>
<p>Diagram bitta <code>Client</code> konstruktoridan ikki xil parametr bilan ikki mutlaqo xil
avtorizatsiya yo'liga qanday bo'linishini, va ikkala holatda ham natija — qayta ishlatiladigan
session fayl — ekanini ko'rsatadi.</p>

<h3>app.run() ichida nima sodir bo'ladi</h3>
<p><code>app.run()</code> — bu qulaylik uchun beriladigan qisqartma: u ichkarida
<code>await app.start()</code> (ulanish + avtorizatsiya), keyin handlerlar ishlashi uchun
<code>idle()</code> (Ctrl+C bosilguncha kutish), va nihoyat <code>await app.stop()</code>ni
chaqiradi. Agar dasturingizda boshqa async kod ham bo'lsa (masalan FastAPI bilan bir jarayonda),
<code>run()</code> o'rniga shu uch qadamni qo'lda, o'z event loop'ingiz ichida chaqirasiz.</p>""",
        "text_content_ru": """<h3>api_id и api_hash — зачем нужны и откуда берутся</h3>
<p>В Bot API нужна была только одна вещь — токен бота от BotFather. Так как Pyrogram работает на
уровне MTProto, требуется ещё кое-что: <strong>api_id</strong> (число) и <strong>api_hash</strong>
(строка) — идентификаторы, которые Telegram выдаёт каждому «приложению», их получают на сайте
https://my.telegram.org, войдя со своим личным Telegram-аккаунтом, в разделе «API development
tools» (достаточно указать название приложения и краткое описание). Этот шаг
<em>одинаков и для режима бота, и для режима пользователя</em> — в обоих случаях нужны
api_id/api_hash, так как они идентифицируют само MTProto-соединение, а bot_token лишь указывает,
от чьего имени входить поверх этого соединения.</p>

<h3>Общий скелет конструктора Client</h3>
<pre><code>from pyrogram import Client

app = Client(
    "session_name",       # файл сессии сохранится под этим именем (например session_name.session)
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="./sessions", # опционально — где хранить файлы сессий
)</code></pre>
<p>Достаточно добавить сюда один параметр — и определится режим входа.</p>

<h3>Режим 1: Вход как бот</h3>
<p>Передайте токен от BotFather в параметр <code>bot_token=</code>:</p>
<pre><code>app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)</code></pre>
<p>При первом вызове <code>app.run()</code> Pyrogram авторизуется от имени бота и создаст файл
<code>my_bot.session</code> — при последующих запусках повторный вход не потребуется, так как
сессия сохранена в файле.</p>

<h3>Режим 2: Вход как пользователь (юзербот)</h3>
<p>Не передавайте <code>bot_token</code> (или передайте <code>phone_number=</code>) — Pyrogram
начнёт интерактивный вход в консоли:</p>
<pre><code>app = Client("my_account", api_id=API_ID, api_hash=API_HASH)
# при первом запуске в консоли спросит:
#   1) Номер телефона (+998...)
#   2) Код подтверждения, отправленный Telegram (SMS или через приложение)
#   3) Если включена двухфакторная аутентификация (2FA) — пароль</code></pre>
<p>Этот процесс происходит <strong>только один раз</strong> — успешный вход записывается в файл
<code>my_account.session</code>, и последующие запуски подключаются мгновенно из файла сессии,
без каких-либо запросов. Именно поэтому файл сессии — крайне ценные и опасные данные (подробнее
в следующем уроке).</p>

<h3>Практические отличия между режимами</h3>
<table>
<tr><th>Аспект</th><th>Режим бота</th><th>Режим пользователя (юзербот)</th></tr>
<tr><td>Нужно для входа</td><td>bot_token</td><td>Номер телефона + SMS-код (+ 2FA)</td></tr>
<tr><td>От чьего имени действует</td><td>Бот (отдельная «личность»)</td><td>Ваш личный аккаунт</td></tr>
<tr><td>Вступление в группу</td><td>Только по приглашению</td><td>Может сам вступить в открытую группу</td></tr>
<tr><td>Flood/лимиты</td><td>Близко к лимитам Bot API, мягче</td><td>Подчиняется обычным лимитам пользователя, строже</td></tr>
<tr><td>Уровень риска</td><td>Токен раскрыт — бота можно пересоздать</td><td>Сессия раскрыта — захватывается весь аккаунт</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  S["Client('name', api_id, api_hash, ...)"]
  S -->|"+ bot_token=BOT_TOKEN"| B["Режим бота
токен BotFather
мгновенная авторизация"]
  S -->|"без параметра (или phone_number=)"| U["Режим пользователя
впервые:
телефон -> SMS-код -> (2FA)"]
  B --> SESS1["файл bot_name.session"]
  U --> SESS2["файл account_name.session"]
  SESS1 --> RUN["app.run() — при следующих запусках
повторный вход НЕ требуется"]
  SESS2 --> RUN
</pre>
<p>Диаграмма показывает, как из одного конструктора <code>Client</code> с разными параметрами
получаются два совершенно разных пути авторизации, и как в обоих случаях результат — переиспользуемый
файл сессии.</p>

<h3>Что происходит внутри app.run()</h3>
<p><code>app.run()</code> — это удобное сокращение: внутри он вызывает <code>await app.start()</code>
(подключение + авторизация), затем <code>idle()</code> для работы обработчиков (ожидание до
Ctrl+C), и наконец <code>await app.stop()</code>. Если в вашей программе есть другой async-код
(например, в одном процессе с FastAPI), вместо <code>run()</code> вы вызываете эти три шага вручную,
внутри своего event loop.</p>""",
        "code_content": """# pip install pyrogram tgcrypto python-dotenv
import os
from pyrogram import Client

from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.environ["TG_API_ID"])       # my.telegram.org'dan
API_HASH = os.environ["TG_API_HASH"]        # my.telegram.org'dan
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")  # bo'lsa — bot rejimi, bo'lmasa — foydalanuvchi rejimi


def build_client() -> Client:
    \"\"\"Bitta funksiya — ikkala rejimni ham qo'llab-quvvatlaydi.
    BOT_TOKEN mavjud bo'lsa bot sifatida, aks holda interaktiv
    foydalanuvchi (userbot) sifatida ulanadi.\"\"\"
    if BOT_TOKEN:
        return Client(
            "bot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workdir="./sessions",
        )
    return Client(
        "user_session",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="./sessions",
    )


app = build_client()


@app.on_message()
async def whoami(client: Client, message):
    me = await client.get_me()
    mode = "BOT" if me.is_bot else "USER"
    await message.reply_text(
        f"Men [{mode}] rejimida ishlayapman: @{me.username or me.id}"
    )


if __name__ == "__main__":
    app.run()
""",
        "code_content_ru": """# pip install pyrogram tgcrypto python-dotenv
import os
from pyrogram import Client

from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.environ["TG_API_ID"])       # с my.telegram.org
API_HASH = os.environ["TG_API_HASH"]        # с my.telegram.org
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")  # если есть — режим бота, если нет — режим пользователя


def build_client() -> Client:
    \"\"\"Одна функция — поддерживает оба режима. Если есть BOT_TOKEN,
    подключается как бот, иначе — как интерактивный пользователь
    (юзербот).\"\"\"
    if BOT_TOKEN:
        return Client(
            "bot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workdir="./sessions",
        )
    return Client(
        "user_session",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="./sessions",
    )


app = build_client()


@app.on_message()
async def whoami(client: Client, message):
    me = await client.get_me()
    mode = "BOT" if me.is_bot else "USER"
    await message.reply_text(
        f"Я работаю в режиме [{mode}]: @{me.username or me.id}"
    )


if __name__ == "__main__":
    app.run()
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: dual-mode Client ishga tushiring",
            "task_title_ru": "Практика: запустите dual-mode Client",
            "task_description": (
                "my.telegram.org'dan api_id/api_hash oling. build_client() uslubidagi funksiya "
                "yozing: BOT_TOKEN muhit o'zgaruvchisi mavjud bo'lsa bot sifatida, bo'lmasa "
                "foydalanuvchi (userbot) sifatida ulanadigan Client qaytarsin. get_me() orqali "
                "kim sifatida ulanganini konsolga chiqaring."
            ),
            "task_description_ru": (
                "Получите api_id/api_hash на my.telegram.org. Напишите функцию в стиле "
                "build_client(): она должна возвращать Client, который подключается как бот, если "
                "задана переменная окружения BOT_TOKEN, и как пользователь (юзербот), если нет. "
                "Выведите в консоль через get_me(), от чьего имени произошло подключение."
            ),
            "task_requirements": (
                "api_id/api_hash muhit o'zgaruvchisidan o'qilishi kerak (hardcode qilinmasin); "
                "ikkala rejim ham kamida bir marta sinovdan o'tkazilishi kerak; get_me().is_bot "
                "natijasi ishlatilishi kerak."
            ),
            "task_requirements_ru": (
                "api_id/api_hash должны читаться из переменных окружения (не хардкодить); оба "
                "режима должны быть протестированы хотя бы по разу; должен использоваться "
                "результат get_me().is_bot."
            ),
            "task_technologies": "Pyrogram, python-dotenv",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: dual-mode Client fabrikasi",
            "title_ru": "Пример: фабрика dual-mode Client",
            "description": "BOT_TOKEN mavjudligiga qarab bot yoki foydalanuvchi rejimini tanlaydigan Client fabrikasi.",
            "description_ru": "Фабрика Client, выбирающая режим бота или пользователя в зависимости от наличия BOT_TOKEN.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "client_factory.py",
                    "language": "python",
                    "code": """import os
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")


def build_client(session_name: str = "default") -> Client:
    kwargs = dict(api_id=API_ID, api_hash=API_HASH, workdir="./sessions")
    if BOT_TOKEN:
        return Client(f"{session_name}_bot", bot_token=BOT_TOKEN, **kwargs)
    return Client(f"{session_name}_user", **kwargs)


async def main():
    async with build_client() as app:
        me = await app.get_me()
        print("Ulandi:", "BOT" if me.is_bot else "USER", me.id)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "api_id/api_hash qayerdan olinadi",
                "title_ru": "Откуда берутся api_id/api_hash",
                "description": "api_id va api_hash odatda qaysi sayt orqali olinadi?",
                "description_ru": "Через какой сайт обычно получают api_id и api_hash?",
                "exercise_type": "multiple_choice",
                "options": ["t.me/BotFather", "my.telegram.org", "core.telegram.org/bots/api", "web.telegram.org"],
                "options_ru": ["t.me/BotFather", "my.telegram.org", "core.telegram.org/bots/api", "web.telegram.org"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu BotFather emas — u faqat bot_token beradi.",
                "hint_ru": "Это не BotFather — он выдаёт только bot_token.",
                "explanation": "api_id/api_hash my.telegram.org saytida 'API development tools' bo'limi orqali olinadi, har ikkala kirish rejimi uchun ham kerak.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bot rejimini yoqadigan parametr",
                "title_ru": "Параметр, включающий режим бота",
                "description": "Client(...) konstruktorida bot rejimini yoqish uchun ___ parametri beriladi",
                "description_ru": "В конструкторе Client(...) для включения режима бота передаётся параметр ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "bot_token",
                "hint": "BotFather'dan olingan tokenni saqlaydigan parametr.",
                "hint_ru": "Параметр, хранящий токен, полученный от BotFather.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Birinchi userbot login qadamlari",
                "title_ru": "Шаги первого входа юзербота",
                "description": "bot_token berilmagan Client birinchi marta ishga tushganda so'raladigan qadamlarni to'g'ri tartibga joylashtiring",
                "description_ru": "Расположите шаги, запрашиваемые при первом запуске Client без bot_token, в правильном порядке",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Telefon raqamini kiritish", "SMS/ilova orqali kelgan kodni kiritish", "2FA yoqilgan bo'lsa parolni kiritish", "session fayl yaratiladi"],
                "drag_items_ru": ["Ввод номера телефона", "Ввод кода, пришедшего по SMS/в приложении", "Ввод пароля, если включена 2FA", "создаётся файл сессии"],
                "correct_order": ["Telefon raqamini kiritish", "SMS/ilova orqali kelgan kodni kiritish", "2FA yoqilgan bo'lsa parolni kiritish", "session fayl yaratiladi"],
                "hint": "Kod tasdiqlangandan keyingina 2FA so'raladi (agar yoqilgan bo'lsa), va faqat muvaffaqiyatli login session faylga yoziladi.",
                "hint_ru": "2FA запрашивается только после подтверждения кода (если включена), и только успешный вход записывается в файл сессии.",
                "difficulty_level": "Medium",
                "points": 8,
            },
            {
                "title": "app.run() nimalarni bajaradi",
                "title_ru": "Что делает app.run()",
                "description": "app.run() metodi ichkarida qanday uch bosqichni ketma-ket bajarishini o'z so'zlaringiz bilan tushuntiring.",
                "description_ru": "Своими словами объясните, какие три шага последовательно выполняет метод app.run() внутри себя.",
                "exercise_type": "text_input",
                "expected_answer": "app.run() ichkarida await app.start() (ulanish va avtorizatsiya) ni chaqiradi, keyin idle() orqali handlerlar ishlashi uchun Ctrl+C bosilguncha kutadi, va nihoyat await app.stop() ni chaqirib ulanishni yopadi.",
                "hint": "start/idle/stop ketma-ketligini eslang.",
                "hint_ru": "Вспомните последовательность start/idle/stop.",
                "difficulty_level": "Medium",
                "points": 7,
            },
        ],
    },
    {
        "order": 2,
        "title": "3-Dekorator-asosidagi handlerlar: @app.on_message va ro'yxatga olish tartibi",
        "title_ru": "3-Обработчики на основе декораторов: @app.on_message и порядок регистрации",
        "points_reward": 15,
        "code_language": "python",
        "text_content": """<h3>aiogram Router'idan Pyrogram dekoratoriga</h3>
<p>aiogram'da siz <code>Router</code> obyekti yaratib, unga <code>@router.message(Command("start"))</code>
kabi dekoratorlar bilan handler qo'shib, keyin <code>dp.include_router(router)</code> orqali
Dispatcher'ga ulagansiz. Pyrogram'da bunday oraliq "Router" qatlami shart emas — funksiyani
to'g'ridan-to'g'ri <code>Client</code> obyektining o'ziga dekoratsiya qilasiz:</p>
<pre><code>@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("Salom!")</code></pre>
<p>Dekorator chaqirilganda funksiya <code>app</code>'ning ichki handlerlar ro'yxatiga
qo'shiladi — hech qanday alohida "ro'yxatdan o'tkazish" chaqiruvi kerak emas, modul import
qilinganidayoq handler faol bo'ladi.</p>

<h3>Asosiy handler turlari</h3>
<table>
<tr><th>Dekorator</th><th>Qachon ishga tushadi</th></tr>
<tr><td><code>@app.on_message()</code></td><td>Yangi xabar kelganda (matn, media, hujjat...)</td></tr>
<tr><td><code>@app.on_callback_query()</code></td><td>Inline tugma bosilganda</td></tr>
<tr><td><code>@app.on_inline_query()</code></td><td>Foydalanuvchi @bot so'z yozganda (inline rejim)</td></tr>
<tr><td><code>@app.on_edited_message()</code></td><td>Xabar tahrirlanganda</td></tr>
<tr><td><code>@app.on_deleted_messages()</code></td><td>Xabar(lar) o'chirilganda</td></tr>
<tr><td><code>@app.on_chat_member_updated()</code></td><td>Guruh a'zoligi holati o'zgarganda (qo'shildi/chiqdi/ban)</td></tr>
</table>
<p>Har birining ichida <code>filters=</code> argumenti orqali qaysi update'lar ushbu funksiyaga
yetib borishini cheklash mumkin (keyingi darsda batafsil).</p>

<h3>Ro'yxatga olish tartibi nega muhim</h3>
<p>aiogram'da middleware/filter zanjiri ko'proq deklarativ ko'rinsada, Pyrogram'da handlerlar
<strong>ro'yxatga olingan tartibda</strong>, yuqoridan pastga tekshiriladi — birinchi mos kelgan
filter ishlaydi va (standart holatda) qolganlariga signal <em>yetib bormaydi</em>. Bu shuni
anglatadiki: tor (aniqroq) filterli handlerlarni <strong>avval</strong>, keng (umumiy) filterli
handlerlarni <strong>keyin</strong> ro'yxatga olish kerak — aks holda umumiy handler barcha
xabarlarni "yutib qo'yadi" va tor handler hech qachon ishga tushmaydi.</p>

<h3>group= parametri: bir update bir nechta handler tomonidan ko'rilishi</h3>
<p>Ba'zan bitta update'ni bir nechta mustaqil handler ko'rishi kerak bo'ladi (masalan: birinchisi
logging qiladi, ikkinchisi haqiqiy javob beradi). Buning uchun <code>group=</code> parametri
bor — turli guruhdagi handlerlar mustaqil ishlaydi, hattoki birinchisi ichida
<code>message.stop_propagation()</code> chaqirilmasa:</p>
<pre><code>@app.on_message(group=0)
async def log_all(client, message):
    print("Kelgan update:", message.id)
    # standart holatda shu guruh ichida keyingisiga o'tmaydi, agar mos kelsa

@app.on_message(filters.command("start"), group=1)
async def start_handler(client, message):
    await message.reply_text("Salom!")</code></pre>
<p>Bitta guruh ichida esa birinchi mos kelgan handlerdan keyin, xohlasangiz
<code>continue_propagation()</code> chaqirib, o'sha guruh ichidagi keyingi mos handlerga ham
signal berishingiz mumkin.</p>

<h3>Eng ko'p uchraydigan xato</h3>
<p>Yangi boshlovchilar ko'pincha <code>@app.on_message()</code> (filtersiz, hamma narsaga mos
keladigan) handlerni <strong>eng birinchi</strong> ro'yxatga oladi &mdash; natijada undan keyingi
barcha tor handlerlar hech qachon ishga tushmaydi, chunki ularga signal yetib bormaydi. Qoida
oddiy: har doim <em>eng tor filterli handlerlarni yuqorida, eng keng (yoki filtersiz)
handlerlarni pastda</em> ro'yxatga oling &mdash; xuddi <code>except</code> bloklarida aniq
exception turlarini umumiy <code>Exception</code>dan avval yozganingizdek.</p>

<pre class="mermaid">
flowchart TB
  M["Yangi update keladi"]
  M --> G0["group=0 handlerlari
(ro'yxatga olingan tartibda)"]
  G0 -->|"mos keldi, davom etmadi"| STOP0["shu guruhda to'xtaydi"]
  G0 -->|"continue_propagation()"| NEXT0["shu guruhdagi
keyingi handler"]
  STOP0 --> G1["group=1 handlerlari"]
  NEXT0 --> G1
  G1 --> G2["group=2 handlerlari"]
</pre>
<p>Diagram bitta update turli guruhlar bo'ylab qanday "oqishini" va bitta guruh ichida esa
birinchi mos handlerdan keyin (agar continue_propagation chaqirilmasa) to'xtab, keyingi guruhga
o'tishini ko'rsatadi.</p>

<h3>aiogram bilan yakuniy solishtirish</h3>
<p>aiogram'da Router'lar orasidagi tartib <code>include_router()</code> chaqirilish tartibi bilan
belgilanadi, Pyrogram'da esa bevosita dekorator chaqirilish (import) tartibi bilan — kontseptual
jihatdan bir xil g'oya (birinchi mos keluvchi g'olib chiqadi), lekin Pyrogram buni qo'shimcha
Router obyektisiz, to'g'ridan-to'g'ri Client darajasida amalga oshiradi.</p>""",
        "text_content_ru": """<h3>От Router aiogram к декоратору Pyrogram</h3>
<p>В aiogram вы создавали объект <code>Router</code>, добавляли в него обработчики через
декораторы вроде <code>@router.message(Command("start"))</code>, а затем подключали к Dispatcher
через <code>dp.include_router(router)</code>. В Pyrogram такой промежуточный слой «Router» не
нужен — функция декорируется напрямую на самом объекте <code>Client</code>:</p>
<pre><code>@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text("Привет!")</code></pre>
<p>Когда декоратор вызывается, функция добавляется во внутренний список обработчиков
<code>app</code> — никакого отдельного вызова «регистрации» не нужно, обработчик становится
активным сразу при импорте модуля.</p>

<h3>Основные типы обработчиков</h3>
<table>
<tr><th>Декоратор</th><th>Когда срабатывает</th></tr>
<tr><td><code>@app.on_message()</code></td><td>При новом сообщении (текст, медиа, документ...)</td></tr>
<tr><td><code>@app.on_callback_query()</code></td><td>При нажатии inline-кнопки</td></tr>
<tr><td><code>@app.on_inline_query()</code></td><td>Когда пользователь пишет @bot слово (inline-режим)</td></tr>
<tr><td><code>@app.on_edited_message()</code></td><td>При редактировании сообщения</td></tr>
<tr><td><code>@app.on_deleted_messages()</code></td><td>При удалении сообщения(й)</td></tr>
<tr><td><code>@app.on_chat_member_updated()</code></td><td>При изменении статуса участника группы (вступил/вышел/бан)</td></tr>
</table>
<p>Внутри каждого через аргумент <code>filters=</code> можно ограничить, какие обновления
доходят до конкретной функции (подробнее в следующем уроке).</p>

<h3>Почему важен порядок регистрации</h3>
<p>Если в aiogram цепочка middleware/фильтров выглядит более декларативно, то в Pyrogram
обработчики проверяются <strong>в порядке регистрации</strong>, сверху вниз — первый подошедший
фильтр срабатывает, и (по умолчанию) остальным сигнал <em>не доходит</em>. Это значит: узкие
(более конкретные) обработчики нужно регистрировать <strong>раньше</strong>, широкие (общие) —
<strong>позже</strong>, иначе общий обработчик «поглотит» все сообщения, и узкий никогда не
сработает.</p>

<h3>Параметр group=: один update видят несколько обработчиков</h3>
<p>Иногда один update должны увидеть несколько независимых обработчиков (например: первый
логирует, второй реально отвечает). Для этого есть параметр <code>group=</code> — обработчики
из разных групп работают независимо, даже если в первой не вызван
<code>message.stop_propagation()</code>:</p>
<pre><code>@app.on_message(group=0)
async def log_all(client, message):
    print("Пришёл update:", message.id)
    # по умолчанию в этой группе не идёт дальше, если подошёл

@app.on_message(filters.command("start"), group=1)
async def start_handler(client, message):
    await message.reply_text("Привет!")</code></pre>
<p>А внутри одной группы после первого подошедшего обработчика можно, при желании, вызвать
<code>continue_propagation()</code>, чтобы сигнал дошёл и до следующего подходящего обработчика
в той же группе.</p>

<h3>Самая частая ошибка</h3>
<p>Новички часто регистрируют <code>@app.on_message()</code> (без фильтра, подходящий под
всё) обработчик <strong>самым первым</strong> — в результате все последующие узкие обработчики
никогда не срабатывают, потому что до них не доходит сигнал. Правило простое: всегда
регистрируйте <em>обработчики с самым узким фильтром сверху, самые широкие (или без фильтра) —
снизу</em> — точно так же, как в блоках <code>except</code> сначала пишут конкретные типы
исключений, а уже потом общий <code>Exception</code>.</p>

<pre class="mermaid">
flowchart TB
  M["Приходит update"]
  M --> G0["обработчики group=0
(в порядке регистрации)"]
  G0 -->|"подошёл, не продолжил"| STOP0["останавливается в этой группе"]
  G0 -->|"continue_propagation()"| NEXT0["следующий обработчик
в этой же группе"]
  STOP0 --> G1["обработчики group=1"]
  NEXT0 --> G1
  G1 --> G2["обработчики group=2"]
</pre>
<p>Диаграмма показывает, как один update «протекает» через разные группы, и как внутри одной
группы после первого подходящего обработчика (если не вызван continue_propagation) поток
останавливается и переходит к следующей группе.</p>

<h3>Итоговое сравнение с aiogram</h3>
<p>В aiogram порядок между Router определяется порядком вызовов <code>include_router()</code>,
в Pyrogram — порядком вызова декораторов (импорта) — концептуально та же идея (побеждает первый
подошедший), но Pyrogram реализует это без дополнительного объекта Router, прямо на уровне
Client.</p>""",
        "code_content": """from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

app = Client("handlers_demo")


# Узкий (специфичный) handler — регистрируется ПЕРВЫМ
@app.on_message(filters.command("start"), group=0)
async def start_handler(client, message):
    await message.reply_text("Bu /start uchun maxsus handler.")


# Log qiluvchi handler — mustaqil guruhda, HAR BIR xabarni ko'radi
@app.on_message(group=-1)
async def logger(client, message):
    print(f"[LOG] chat={message.chat.id} matn={message.text!r}")
    message.continue_propagation()  # shu guruhdagi keyingisiga ham bersin


# Keng (umumiy) handler — ATAYLAB oxirida, aks holda hammasini "yutib qo'yadi"
@app.on_message(filters.text, group=0)
async def fallback_handler(client, message):
    await message.reply_text(f"Tushunmadim: {message.text}")


@app.on_callback_query()
async def on_button(client, callback_query):
    await callback_query.answer("Tugma bosildi!")


# Xabar tahrirlanganda ishga tushadi — jadvaldagi yana bir handler turi
@app.on_edited_message(filters.text)
async def on_edit(client, message):
    print(f"[EDIT] chat={message.chat.id} yangi matn: {message.text!r}")


# Xabar(lar) o'chirilganda ishga tushadi
@app.on_deleted_messages()
async def on_delete(client, messages):
    ids = [m.id for m in messages]
    print(f"[DELETE] o'chirilgan xabar id'lari: {ids}")


# Guruhga a'zo qo'shildi/chiqdi/ban bo'ldi — moderatsiya uchun foydali
@app.on_chat_member_updated()
async def on_member_change(client, update):
    if update.new_chat_member and update.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = update.new_chat_member.user
        print(f"[JOIN] {user.first_name} guruhga qo'shildi")


if __name__ == "__main__":
    app.run()
""",
        "code_content_ru": """from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus

app = Client("handlers_demo")


# Узкий (специфичный) handler — регистрируется ПЕРВЫМ
@app.on_message(filters.command("start"), group=0)
async def start_handler(client, message):
    await message.reply_text("Это специальный обработчик для /start.")


# Логирующий handler — в независимой группе, видит КАЖДОЕ сообщение
@app.on_message(group=-1)
async def logger(client, message):
    print(f"[LOG] chat={message.chat.id} text={message.text!r}")
    message.continue_propagation()  # передать и следующему в этой же группе


# Общий handler — НАРОЧНО в конце, иначе он "поглотит" всё
@app.on_message(filters.text, group=0)
async def fallback_handler(client, message):
    await message.reply_text(f"Не понял: {message.text}")


@app.on_callback_query()
async def on_button(client, callback_query):
    await callback_query.answer("Кнопка нажата!")


# Срабатывает при редактировании сообщения — ещё один тип из таблицы
@app.on_edited_message(filters.text)
async def on_edit(client, message):
    print(f"[EDIT] chat={message.chat.id} новый текст: {message.text!r}")


# Срабатывает при удалении сообщения(й)
@app.on_deleted_messages()
async def on_delete(client, messages):
    ids = [m.id for m in messages]
    print(f"[DELETE] id удалённых сообщений: {ids}")


# Вступление/выход/бан участника группы — полезно для модерации
@app.on_chat_member_updated()
async def on_member_change(client, update):
    if update.new_chat_member and update.new_chat_member.status == ChatMemberStatus.MEMBER:
        user = update.new_chat_member.user
        print(f"[JOIN] {user.first_name} вступил в группу")


if __name__ == "__main__":
    app.run()
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: uch qatlamli handler zanjiri",
            "task_title_ru": "Практика: трёхуровневая цепочка обработчиков",
            "task_description": (
                "Bitta bot yozing: (1) group=-1 ichida barcha update'larni konsolga logging "
                "qiluvchi handler, continue_propagation() bilan; (2) group=0 ichida /help "
                "buyrug'iga maxsus javob beruvchi tor handler, u AVVAL ro'yxatga olinsin; (3) "
                "group=0 ichida, undan KEYIN, har qanday matnga umumiy javob beruvchi keng "
                "handler."
            ),
            "task_description_ru": (
                "Напишите бота: (1) обработчик в group=-1, логирующий все update в консоль, с "
                "continue_propagation(); (2) узкий обработчик в group=0 для команды /help, "
                "зарегистрированный ПЕРВЫМ; (3) в group=0, ПОСЛЕ него, общий обработчик, "
                "отвечающий на любой текст."
            ),
            "task_requirements": (
                "Uchala handler ham ishlashi va tartib buzilmasligi kerak (tor handler keng "
                "handlerdan avval ro'yxatga olingan bo'lishi shart); logging handler "
                "continue_propagation() chaqirishi kerak."
            ),
            "task_requirements_ru": (
                "Все три обработчика должны работать, порядок не должен нарушаться (узкий "
                "обработчик обязан быть зарегистрирован раньше общего); логирующий обработчик "
                "должен вызывать continue_propagation()."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: log + tor + keng handlerlar zanjiri",
            "title_ru": "Пример: цепочка log + узкий + общий обработчики",
            "description": "group= parametri va continue_propagation() ishlatilgan to'liq ishlaydigan misol.",
            "description_ru": "Полностью рабочий пример с параметром group= и continue_propagation().",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "handler_chain.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters

app = Client("chain_demo")


@app.on_message(group=-1)
async def audit_log(client, message):
    print(f"[AUDIT] {message.chat.id}: {message.text!r}")
    message.continue_propagation()


@app.on_message(filters.command("help"), group=0)
async def help_handler(client, message):
    await message.reply_text("Buyruqlar: /help, /start")


@app.on_message(filters.text & ~filters.command(["help", "start"]), group=0)
async def generic_handler(client, message):
    await message.reply_text("Umumiy javob: xabaringiz qabul qilindi.")


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Handlerlar qanday tartibda tekshiriladi",
                "title_ru": "В каком порядке проверяются обработчики",
                "description": "Bir xil group ichidagi handlerlar qaysi tartibda tekshiriladi?",
                "description_ru": "В каком порядке проверяются обработчики внутри одной группы?",
                "exercise_type": "multiple_choice",
                "options": ["Tasodifiy tartibda", "Ro'yxatga olingan (dekoratsiya qilingan) tartibda", "Alifbo tartibida", "Filter murakkabligiga qarab"],
                "options_ru": ["В случайном порядке", "В порядке регистрации (декорирования)", "В алфавитном порядке", "По сложности фильтра"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Modul import qilinganda funksiyalar qanday tartibda dekoratsiya qilinishini eslang.",
                "hint_ru": "Вспомните, в каком порядке функции декорируются при импорте модуля.",
                "explanation": "Bitta group ichida handlerlar aynan ro'yxatga olingan (kod bo'ylab dekoratsiya qilingan) tartibda, yuqoridan pastga tekshiriladi.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Keyingi guruhga o'tkazish metodi",
                "title_ru": "Метод передачи в следующую группу",
                "description": "Bitta guruh ichida keyingi mos handlerga ham signal berish uchun message.___() chaqiriladi",
                "description_ru": "Чтобы передать сигнал следующему подходящему обработчику в той же группе, вызывают message.___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "continue_propagation",
                "hint": "Nomi 'davom ettirish' ma'nosini bildiradi.",
                "hint_ru": "Название означает 'продолжить'.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Handlerlarni to'g'ri tartibga joylashtiring",
                "title_ru": "Расположите обработчики в правильном порядке",
                "description": "Umumiy handler tor handlerni 'yutib qo'ymasligi' uchun handlerlarni ro'yxatga olish ketma-ketligini joylashtiring",
                "description_ru": "Расположите порядок регистрации обработчиков так, чтобы общий не «поглощал» узкий",
                "exercise_type": "drag_and_drop",
                "drag_items": ["filters.command(\"start\") uchun tor handler", "filters.text uchun umumiy handler"],
                "drag_items_ru": ["Узкий handler для filters.command(\"start\")", "Общий handler для filters.text"],
                "correct_order": ["filters.command(\"start\") uchun tor handler", "filters.text uchun umumiy handler"],
                "hint": "Aniqroq filter har doim avval kelishi kerak.",
                "hint_ru": "Более конкретный фильтр всегда должен идти первым.",
                "difficulty_level": "Easy",
                "points": 5,
            },
        ],
    },
    {
        "order": 3,
        "title": "4-Filters tizimi: filters.command, filters.chat va & / | bilan birlashtirish",
        "title_ru": "4-Система фильтров: filters.command, filters.chat и объединение через & / |",
        "points_reward": 15,
        "code_language": "python",
        "text_content": """<h3>filters moduli — Pyrogram'ning "kim ko'radi" mantiqi</h3>
<p><code>pyrogram.filters</code> moduli — bu handler ichiga qaysi update'lar yetib borishini
belgilaydigan qurilish bloklari to'plami. Har bir filter — chaqirilganda <code>Filter</code>
obyektini qaytaradigan funksiya (yoki tayyor obyekt), va bu obyektlarni Python'ning oddiy
mantiqiy operatorlari <strong>& (VA)</strong>, <strong>| (YOKI)</strong> va <strong>~ (EMAS)</strong>
bilan bemalol birlashtirish mumkin — bu Pyrogram'ning eng qulay tomonlaridan biri.</p>

<h3>Eng ko'p ishlatiladigan tayyor filterlar</h3>
<table>
<tr><th>Filter</th><th>Nimaga mos keladi</th></tr>
<tr><td><code>filters.command("start")</code></td><td>Aynan <code>/start</code> buyrug'i (prefiks, argumentlarni ham ajratib beradi)</td></tr>
<tr><td><code>filters.text</code></td><td>Har qanday matnli xabar</td></tr>
<tr><td><code>filters.private</code></td><td>Faqat shaxsiy chat</td></tr>
<tr><td><code>filters.group</code></td><td>Oddiy guruh yoki supergroup</td></tr>
<tr><td><code>filters.channel</code></td><td>Kanal xabari</td></tr>
<tr><td><code>filters.chat(chat_id)</code></td><td>Faqat ko'rsatilgan chat(lar)dan</td></tr>
<tr><td><code>filters.user(user_id)</code></td><td>Faqat ko'rsatilgan foydalanuvchi(lar)dan</td></tr>
<tr><td><code>filters.photo</code> / <code>filters.video</code> / <code>filters.document</code></td><td>Media turi bo'yicha</td></tr>
<tr><td><code>filters.reply</code></td><td>Boshqa xabarga javob (reply) bo'lgan xabar</td></tr>
</table>

<h3>Operatorlar bilan birlashtirish</h3>
<pre><code># VA — ikkalasi ham to'g'ri bo'lishi kerak
filters.command("ban") & filters.group

# YOKI — kamida bittasi to'g'ri bo'lsa yetarli
filters.photo | filters.video

# EMAS — inkor qilish
~filters.command("start")

# Uchtasini birga: shaxsiy chatda, matn, lekin /start emas
filters.private & filters.text & ~filters.command("start")</code></pre>
<p>Bu yozuv aiogram'dagi <code>F.text & ~F.text.startswith("/")</code> uslubidagi magic filter'ga
juda o'xshaydi — farqi shundaki, Pyrogram'da bu birlashtirish handler darajasida, oddiy Python
mantiqiy operatorlari orqali, qo'shimcha maxsus sintaksissiz ishlaydi.</p>

<h3>O'z filteringizni yaratish: filters.create</h3>
<p>Tayyor filterlar yetmasa, <code>filters.create()</code> orqali o'zingiznikini yozasiz —
u har qanday <code>Client, update -> bool</code> shaklidagi funksiyani filterga aylantiradi:</p>
<pre><code>async def _is_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

is_admin = filters.create(_is_admin)

@app.on_message(filters.command("ban") & is_admin)
async def ban_handler(client, message):
    ...</code></pre>
<p>Bu filter endi boshqa har qanday tayyor filter kabi <code>&</code>/<code>|</code> bilan
birlashtirilishi mumkin — Pyrogram maxsus/custom filterlarni ikkinchi darajali fuqaro qilib
qo'ymaydi.</p>

<pre class="mermaid">
flowchart TB
  MSG["Kelgan xabar"]
  MSG --> F1{"filters.private?"}
  F1 -->|"yo'q"| REJECT["handler chaqirilmaydi"]
  F1 -->|"ha"| F2{"filters.text?"}
  F2 -->|"yo'q"| REJECT
  F2 -->|"ha"| F3{"~filters.command('start')?"}
  F3 -->|"yo'q (bu /start)"| REJECT
  F3 -->|"ha"| RUN["handler chaqiriladi"]
</pre>
<p>Diagram <code>filters.private & filters.text & ~filters.command("start")</code> ifodasi
amalda qanday ketma-ket AND zanjiri sifatida baholanishini ko'rsatadi — birortasi mos kelmasa,
handler umuman chaqirilmaydi.</p>

<h3>Filter va handler bir xil emas</h3>
<p>Muhim tushuncha: filter — bu faqat "ha/yo'q" javob beruvchi sof funksiya, u hech qanday javob
yubormaydi va state saqlamaydi. Barcha haqiqiy ish (xabar yuborish, DB'ga yozish) handler
funksiyasining o'zida bo'ladi. Bu ajratish filterlarni qayta ishlatish va test qilishni
osonlashtiradi — <code>is_admin</code> kabi filterni istalgan sondagi handlerga qo'shishingiz
mumkin, hech narsani takrorlamasdan.</p>

<h3>Amaliy maslahat: qimmat filterlarni oxiriga qo'ying</h3>
<p><code>is_admin</code> kabi custom filterlar ko'pincha ichida tarmoq so'rovi (masalan
<code>get_chat_member</code>) yuboradi &mdash; bu arzon emas. & operatori Python'dagi kabi
<strong>qisqa tutashuv (short-circuit)</strong> tamoyili bilan ishlaydi: chapdan o'ngga
baholanadi va birinchi <code>False</code> uchraganda qolganlari umuman chaqirilmaydi. Shuning
uchun arzon filterlarni (<code>filters.group</code>, <code>filters.command(...)</code>) chap
tomonga, qimmat (tarmoqqa murojaat qiluvchi) filterlarni esa o'ng tomonga qo'ying &mdash;
shunda mos kelmagan xabarlar uchun qimmat tekshiruv umuman bajarilmaydi.</p>""",
        "text_content_ru": """<h3>Модуль filters — логика «кто это увидит» в Pyrogram</h3>
<p>Модуль <code>pyrogram.filters</code> — это набор строительных блоков, определяющих, какие
update дойдут до конкретного обработчика. Каждый фильтр — функция (или готовый объект), при
вызове возвращающая объект <code>Filter</code>, и эти объекты можно свободно объединять обычными
логическими операторами Python: <strong>& (И)</strong>, <strong>| (ИЛИ)</strong> и
<strong>~ (НЕ)</strong> — это одна из самых удобных сторон Pyrogram.</p>

<h3>Самые часто используемые готовые фильтры</h3>
<table>
<tr><th>Фильтр</th><th>Чему соответствует</th></tr>
<tr><td><code>filters.command("start")</code></td><td>Именно команда <code>/start</code> (разбирает префикс и аргументы)</td></tr>
<tr><td><code>filters.text</code></td><td>Любое текстовое сообщение</td></tr>
<tr><td><code>filters.private</code></td><td>Только личный чат</td></tr>
<tr><td><code>filters.group</code></td><td>Обычная группа или супергруппа</td></tr>
<tr><td><code>filters.channel</code></td><td>Сообщение канала</td></tr>
<tr><td><code>filters.chat(chat_id)</code></td><td>Только из указанного чата(ов)</td></tr>
<tr><td><code>filters.user(user_id)</code></td><td>Только от указанного пользователя(ей)</td></tr>
<tr><td><code>filters.photo</code> / <code>filters.video</code> / <code>filters.document</code></td><td>По типу медиа</td></tr>
<tr><td><code>filters.reply</code></td><td>Сообщение, являющееся ответом (reply) на другое</td></tr>
</table>

<h3>Объединение через операторы</h3>
<pre><code># И — оба условия должны быть верны
filters.command("ban") & filters.group

# ИЛИ — достаточно хотя бы одного
filters.photo | filters.video

# НЕ — отрицание
~filters.command("start")

# Все три вместе: в личном чате, текст, но не /start
filters.private & filters.text & ~filters.command("start")</code></pre>
<p>Эта запись очень похожа на magic filter в aiogram вроде
<code>F.text & ~F.text.startswith("/")</code> — разница в том, что в Pyrogram это объединение
происходит на уровне обработчика, через обычные логические операторы Python, без
дополнительного специального синтаксиса.</p>

<h3>Создание своего фильтра: filters.create</h3>
<p>Если готовых фильтров не хватает, вы пишете свой через <code>filters.create()</code> — он
превращает в фильтр любую функцию вида <code>Client, update -> bool</code>:</p>
<pre><code>async def _is_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

is_admin = filters.create(_is_admin)

@app.on_message(filters.command("ban") & is_admin)
async def ban_handler(client, message):
    ...</code></pre>
<p>Этот фильтр теперь можно объединять через <code>&</code>/<code>|</code> точно так же, как
любой готовый — Pyrogram не делает кастомные фильтры гражданами второго сорта.</p>

<pre class="mermaid">
flowchart TB
  MSG["Пришло сообщение"]
  MSG --> F1{"filters.private?"}
  F1 -->|"нет"| REJECT["обработчик не вызывается"]
  F1 -->|"да"| F2{"filters.text?"}
  F2 -->|"нет"| REJECT
  F2 -->|"да"| F3{"~filters.command('start')?"}
  F3 -->|"нет (это /start)"| REJECT
  F3 -->|"да"| RUN["обработчик вызывается"]
</pre>
<p>Диаграмма показывает, как выражение
<code>filters.private & filters.text & ~filters.command("start")</code> на практике вычисляется
как последовательная цепочка AND — если хоть одно условие не выполнено, обработчик вообще не
вызывается.</p>

<h3>Фильтр и обработчик — не одно и то же</h3>
<p>Важное понимание: фильтр — это чистая функция, отвечающая только «да/нет», она не отправляет
никаких ответов и не хранит состояние. Вся реальная работа (отправка сообщений, запись в БД)
происходит в самой функции-обработчике. Такое разделение упрощает переиспользование и
тестирование фильтров — фильтр вроде <code>is_admin</code> можно добавить к любому количеству
обработчиков, ничего не дублируя.</p>

<h3>Практический совет: дорогие фильтры — в конец</h3>
<p>Кастомные фильтры вроде <code>is_admin</code> часто внутри делают сетевой запрос (например
<code>get_chat_member</code>) — это недёшево. Оператор & работает по принципу
<strong>короткого замыкания (short-circuit)</strong>, как и в Python: вычисляется слева направо,
и при первом <code>False</code> остальные вообще не вызываются. Поэтому дешёвые фильтры
(<code>filters.group</code>, <code>filters.command(...)</code>) ставьте слева, а дорогие
(обращающиеся к сети) — справа — тогда для неподходящих сообщений дорогая проверка вообще не
выполнится.</p>""",
        "code_content": """from pyrogram import Client, filters

app = Client("filters_demo")


async def _is_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")


is_admin = filters.create(_is_admin)


@app.on_message(filters.command("ban") & filters.group & is_admin)
async def ban_handler(client, message):
    await message.reply_text("Foydalanuvchi ban qilindi (demo).")


@app.on_message(filters.command("ban") & filters.group & ~is_admin)
async def ban_denied(client, message):
    await message.reply_text("Sizda /ban buyrug'i uchun huquq yo'q.")


@app.on_message(filters.photo | filters.video)
async def media_handler(client, message):
    kind = "rasm" if message.photo else "video"
    await message.reply_text(f"{kind.capitalize()} qabul qilindi.")


@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def private_text(client, message):
    await message.reply_text(f"Shaxsiy xabar: {message.text}")


if __name__ == "__main__":
    app.run()
""",
        "code_content_ru": """from pyrogram import Client, filters

app = Client("filters_demo")


async def _is_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")


is_admin = filters.create(_is_admin)


@app.on_message(filters.command("ban") & filters.group & is_admin)
async def ban_handler(client, message):
    await message.reply_text("Пользователь забанен (демо).")


@app.on_message(filters.command("ban") & filters.group & ~is_admin)
async def ban_denied(client, message):
    await message.reply_text("У вас нет прав на команду /ban.")


@app.on_message(filters.photo | filters.video)
async def media_handler(client, message):
    kind = "фото" if message.photo else "видео"
    await message.reply_text(f"{kind.capitalize()} получено.")


@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def private_text(client, message):
    await message.reply_text(f"Личное сообщение: {message.text}")


if __name__ == "__main__":
    app.run()
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: is_admin custom filter va uni birlashtirish",
            "task_title_ru": "Практика: custom-фильтр is_admin и его объединение",
            "task_description": (
                "filters.create() yordamida is_admin filterini yozing (get_chat_member orqali). "
                "Uni /ban buyrug'i bilan & orqali birlashtiring: admin bo'lsa bajarsin, bo'lmasa "
                "'ruxsat yo'q' desin. Qo'shimcha ravishda filters.photo | filters.video "
                "birlashmasi bilan istalgan media xabarga javob beruvchi handler yozing."
            ),
            "task_description_ru": (
                "Напишите фильтр is_admin через filters.create() (используя get_chat_member). "
                "Объедините его с командой /ban через &: если админ — выполнить, если нет — "
                "'нет прав'. Дополнительно напишите обработчик, отвечающий на любое медиа-сообщение "
                "через комбинацию filters.photo | filters.video."
            ),
            "task_requirements": (
                "is_admin filters.create() orqali yozilgan bo'lishi kerak; & va | operatorlari "
                "kamida bir marta ishlatilgan bo'lishi kerak; ~ operatori kamida bir joyda "
                "ishlatilishi kerak."
            ),
            "task_requirements_ru": (
                "is_admin должен быть написан через filters.create(); операторы & и | должны "
                "быть использованы хотя бы раз; оператор ~ должен быть использован хотя бы в "
                "одном месте."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: is_admin custom filter",
            "title_ru": "Пример: custom-фильтр is_admin",
            "description": "filters.create() bilan yaratilgan va & / ~ operatorlari bilan ishlatilgan admin-tekshiruvchi filter.",
            "description_ru": "Фильтр проверки админа, созданный через filters.create() и используемый с операторами & / ~.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "admin_filter.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters

app = Client("admin_filter_demo")


async def _check_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")


is_admin = filters.create(_check_admin)


@app.on_message(filters.command("settings") & filters.group & is_admin)
async def settings_admin(client, message):
    await message.reply_text("Guruh sozlamalari (faqat adminlar uchun).")


@app.on_message(filters.command("settings") & filters.group & ~is_admin)
async def settings_denied(client, message):
    await message.reply_text("Bu buyruq faqat adminlar uchun.")


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Filterlarni birlashtirish operatori",
                "title_ru": "Оператор объединения фильтров",
                "description": "Ikkala filter ham to'g'ri bo'lishi kerak bo'lgan holatda qaysi operator ishlatiladi?",
                "description_ru": "Какой оператор используется, когда должны быть верны оба фильтра?",
                "exercise_type": "multiple_choice",
                "options": ["+", "&", "|", "and_()"],
                "options_ru": ["+", "&", "|", "and_()"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu Python'ning bitwise AND operatori, lekin Filter obyektlari uchun overload qilingan.",
                "hint_ru": "Это bitwise-оператор AND в Python, но перегруженный для объектов Filter.",
                "explanation": "& operatori ikkala filter ham to'g'ri bo'lishini talab qiladi (mantiqiy VA), | esa kamida bittasi to'g'ri bo'lishini.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Custom filter yaratish funksiyasi",
                "title_ru": "Функция создания custom-фильтра",
                "description": "Tayyor filterlar yetmasa, o'z filteringizni yaratish uchun filters.___() chaqiriladi",
                "description_ru": "Если готовых фильтров не хватает, для создания своего вызывают filters.___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "create",
                "hint": "Ingliz tilida 'yaratish' so'zi.",
                "hint_ru": "Английское слово 'создать'.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Filter va handler mas'uliyatini mos qo'ying",
                "title_ru": "Сопоставьте ответственность фильтра и обработчика",
                "description": "Tavsiflarni tartibga joylashtiring: avval filterning vazifasi, keyin handlerning vazifasi",
                "description_ru": "Расположите описания по порядку: сначала задача фильтра, затем задача обработчика",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Faqat true/false qaytaradi, state saqlamaydi", "Haqiqiy ishni bajaradi: xabar yuboradi, DB'ga yozadi"],
                "drag_items_ru": ["Возвращает только true/false, не хранит состояние", "Выполняет реальную работу: отправляет сообщения, пишет в БД"],
                "correct_order": ["Faqat true/false qaytaradi, state saqlamaydi", "Haqiqiy ishni bajaradi: xabar yuboradi, DB'ga yozadi"],
                "hint": "Filter — sof funksiya, handler — samarali ta'sir (side effect) joyi.",
                "hint_ru": "Фильтр — чистая функция, обработчик — место для побочных эффектов.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "filters.create imzosi",
                "title_ru": "Сигнатура filters.create",
                "description": "filters.create() ga uzatiladigan funksiyaning imzosi qanday shaklda bo'lishi kerak va nima qaytarishi kerak? O'z so'zlaringiz bilan tushuntiring.",
                "description_ru": "В каком виде должна быть сигнатура функции, передаваемой в filters.create(), и что она должна возвращать? Объясните своими словами.",
                "exercise_type": "text_input",
                "expected_answer": "Funksiya (_, client, message) yoki shunga o'xshash uch argument qabul qilishi va bool (True/False) qaytarishi kerak — True bo'lsa handler chaqiriladi, False bo'lsa chaqirilmaydi.",
                "hint": "Birinchi argument odatda ishlatilmaydigan filter obyektining o'zi bo'ladi.",
                "hint_ru": "Первый аргумент обычно неиспользуемый сам объект фильтра.",
                "difficulty_level": "Hard",
                "points": 8,
            },
        ],
    },
    {
        "order": 4,
        "title": "5-Sessiya boshqaruvi: workdir, in-memory session va xavfsizlik",
        "title_ru": "5-Управление сессиями: workdir, in-memory сессии и безопасность",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>Session fayl aslida nima?</h3>
<p>2-darsda ko'rganingizdek, muvaffaqiyatli login (bot ham, foydalanuvchi ham) natijasi &mdash;
<code>.session</code> kengaytmali fayl (SQLite formatida). Bu fayl ichida MTProto
<strong>auth_key</strong> &mdash; sizning hisobingiz (yoki botingiz) nomidan Telegram
serveriga ulanish uchun yetarli bo'lgan shifrlash kaliti saqlanadi. Bu <em>parolning o'zi
emas</em>, lekin amalda undan farqi yo'q &mdash; kimdir bu faylni olsa, sizning login/parolingizni
bilmasdan turib, xuddi siz kabi hisobga (yoki botga) kira oladi, hech qanday qo'shimcha SMS kod
yoki 2FA so'ralmaydi.</p>

<h3>Nega bu Bot API tokenidan ham xavfliroq</h3>
<p>Bot tokeni oshkor bo'lsa &mdash; BotFather orqali <code>/revoke</code> qilib, yangi token olish
mumkin, zarar cheklangan (faqat bot funksiyalari). Lekin <strong>userbot session fayli</strong>
oshkor bo'lsa &mdash; bu butun shaxsiy Telegram hisobingizni yo'qotish bilan tengdir: sizning
barcha xabarlaringiz, kontaktlaringiz, kanallaringiz boshqa birovning nazoratiga o'tadi, va
buni "revoke" qilishning yagona yo'li &mdash; boshqa qurilmadan barcha faol seanslarni
Telegram sozlamalaridan majburan tugatish (Settings &rarr; Devices &rarr; Terminate all other
sessions).</p>

<h3>workdir &mdash; session fayllar qayerda saqlanadi</h3>
<pre><code>app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",  # standart holatda joriy papka
)</code></pre>
<p><code>workdir</code> &mdash; bu oddiy fayl tizimi papkasi, va u <strong>version control'ga
(git) hech qachon qo'shilmasligi kerak</strong> &mdash; <code>.gitignore</code>'ga
<code>*.session</code> va <code>*.session-journal</code> qo'shing. Serverga deploy qilganda ham
bu papka faqat serverning o'zida, mahalliy diskda, tegishli fayl ruxsatlari (masalan
<code>chmod 600</code>) bilan saqlanishi kerak.</p>

<h3>In-memory session: fayl umuman yozilmasin desangiz</h3>
<p>Ba'zi holatlarda (masalan, konteynerlashtirilgan qisqa muddatli muhit, yoki sinov skripti)
sessiyani diskka umuman yozmaslik afzal &mdash; buning uchun <code>in_memory=True</code>:</p>
<pre><code>app = Client("temp", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)</code></pre>
<p>Bu holda avtorizatsiya har safar jarayon qayta ishga tushganda qaytadan sodir bo'ladi (bot
uchun arzon, chunki bot_token bilan darhol bo'ladi; foydalanuvchi rejimi uchun esa har safar
SMS kod so'raladi &mdash; shuning uchun in-memory ko'proq bot yoki qisqa muddatli skriptlar
uchun mos).</p>

<h3>session_string: faylsiz, ko'chiriladigan sessiya</h3>
<p>Foydalanuvchi rejimida sessiyani boshqa muhitga (masalan CI yoki boshqa server) ko'chirish
kerak bo'lsa, <code>export_session_string()</code> orqali butun sessiyani bitta uzun matn
qatoriga aylantirish mumkin, keyin uni <code>session_string=</code> parametri orqali (muhit
o'zgaruvchisi sifatida, hech qachon kodga hardcode qilmasdan) boshqa joyda ishlatasiz. Bu matn
ham xuddi <code>.session</code> fayl kabi &mdash; to'liq hisobga kirish huquqi &mdash; shuning
uchun uni faqat maxfiy o'zgaruvchilar menejeri (masalan CI secrets) orqali saqlang, hech qachon
log'larga chiqarmang yoki repo'ga committing qilmang.</p>

<pre class="mermaid">
flowchart LR
  LEAK["session fayli / session_string
oshkor bo'ldi"]
  LEAK --> RISK1["Hujumchi sizning hisobingiz
nomidan MTProto'ga ulanadi"]
  RISK1 --> RISK2["SMS kod yoki 2FA
SO'RALMAYDI &mdash; to'liq kirish"]
  RISK2 --> FIX["Yagona davo:
Telegram Settings &rarr; Devices &rarr;
Terminate all other sessions"]
</pre>
<p>Diagram shuni ko'rsatadiki, sessiya oshkor bo'lganda hujumchi hech qanday qo'shimcha
tasdiqlashsiz to'liq kirish huquqiga ega bo'ladi, va yagona chora &mdash; barcha faol
seanslarni majburan tugatish, chunki auth_key'ni "bekor qilish" imkoni yo'q, faqat
tugatish mumkin.</p>

<h3>Amaliy xavfsizlik qoidalari</h3>
<ul>
<li><code>*.session*</code> fayllarni har doim <code>.gitignore</code>'ga qo'shing</li>
<li>session_string'ni faqat maxfiy muhit o'zgaruvchisi sifatida saqlang, hech qachon konsolga chiqarmang</li>
<li>Production serverida session fayl faqat botni ishga tushiruvchi foydalanuvchiga o'qilishi mumkin bo'lsin (fayl ruxsatlari)</li>
<li>Shubha bo'lsa &mdash; darhol Telegram Settings orqali barcha seanslarni tugating</li>
<li>Session fayl yoki session_string'ni hech qachon "qo'llab-quvvatlash" chatiga yubormang, hatto so'ralsa ham &mdash; Telegram'ning haqiqiy qo'llab-quvvatlash xizmati buni hech qachon talab qilmaydi</li>
</ul>""",
        "text_content_ru": """<h3>Что такое файл сессии на самом деле?</h3>
<p>Как вы видели в уроке 2, результат успешного входа (и бота, и пользователя) &mdash; файл
с расширением <code>.session</code> (в формате SQLite). Внутри этого файла хранится MTProto
<strong>auth_key</strong> &mdash; ключ шифрования, достаточный для подключения к серверу
Telegram от имени вашего аккаунта (или бота). Это <em>не сам пароль</em>, но на практике разницы
нет &mdash; если кто-то получит этот файл, он сможет войти как вы, не зная логина/пароля, без
запроса SMS-кода или 2FA.</p>

<h3>Почему это опаснее, чем токен Bot API</h3>
<p>Если токен бота раскрыт &mdash; можно через BotFather сделать <code>/revoke</code> и получить
новый, ущерб ограничен (только функциональность бота). Но если раскрыт <strong>файл сессии
юзербота</strong> &mdash; это равносильно потере всего личного Telegram-аккаунта: все ваши
сообщения, контакты, каналы переходят под контроль другого человека, и единственный способ
это «отозвать» &mdash; принудительно завершить все активные сеансы с другого устройства через
настройки Telegram (Settings &rarr; Devices &rarr; Terminate all other sessions).</p>

<h3>workdir &mdash; где хранятся файлы сессий</h3>
<pre><code>app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",  # по умолчанию — текущая папка
)</code></pre>
<p><code>workdir</code> &mdash; это обычная папка файловой системы, и она
<strong>никогда не должна попадать в систему контроля версий (git)</strong> &mdash; добавьте в
<code>.gitignore</code> <code>*.session</code> и <code>*.session-journal</code>. При деплое на
сервер эта папка должна храниться только на самом сервере, на локальном диске, с
соответствующими правами доступа (например <code>chmod 600</code>).</p>

<h3>In-memory сессия: если файл вообще не нужен</h3>
<p>В некоторых случаях (например, кратковременное контейнеризированное окружение или тестовый
скрипт) предпочтительнее вообще не писать сессию на диск &mdash; для этого
<code>in_memory=True</code>:</p>
<pre><code>app = Client("temp", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)</code></pre>
<p>В этом случае авторизация происходит заново при каждом перезапуске процесса (для бота это
дёшево, так как с bot_token это происходит мгновенно; для режима пользователя же каждый раз
будет запрашиваться SMS-код &mdash; поэтому in-memory больше подходит для ботов или
краткосрочных скриптов).</p>

<h3>session_string: сессия без файла, переносимая</h3>
<p>Если в режиме пользователя сессию нужно перенести в другое окружение (например CI или другой
сервер), через <code>export_session_string()</code> можно превратить всю сессию в одну длинную
строку, а затем использовать её в другом месте через параметр <code>session_string=</code> (как
переменную окружения, никогда не хардкодя в код). Эта строка так же, как и файл
<code>.session</code> &mdash; полный доступ к аккаунту &mdash; поэтому храните её только через
менеджер секретов (например CI secrets), никогда не выводите в логи и не коммитьте в репозиторий.</p>

<pre class="mermaid">
flowchart LR
  LEAK["файл сессии / session_string
раскрыт"]
  LEAK --> RISK1["Злоумышленник подключается к MTProto
от имени вашего аккаунта"]
  RISK1 --> RISK2["SMS-код или 2FA
НЕ ЗАПРАШИВАЮТСЯ &mdash; полный доступ"]
  RISK2 --> FIX["Единственное лекарство:
Telegram Settings &rarr; Devices &rarr;
Terminate all other sessions"]
</pre>
<p>Диаграмма показывает, что при раскрытии сессии злоумышленник получает полный доступ без
дополнительных подтверждений, и единственная мера &mdash; принудительно завершить все активные
сеансы, так как «отозвать» auth_key нельзя, можно только завершить сеанс.</p>

<h3>Практические правила безопасности</h3>
<ul>
<li>Всегда добавляйте файлы <code>*.session*</code> в <code>.gitignore</code></li>
<li>Храните session_string только как секретную переменную окружения, никогда не выводите в консоль</li>
<li>На продакшн-сервере файл сессии должен быть доступен для чтения только пользователю, запускающему бота (права доступа)</li>
<li>При малейшем подозрении &mdash; немедленно завершите все сеансы через настройки Telegram</li>
<li>Никогда не отправляйте файл сессии или session_string в чат поддержки, даже если попросят — легитимная поддержка Telegram никогда этого не требует</li>
</ul>""",
        "code_content": """import os
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

# 1) Fayl-asosli sessiya, alohida papkada (git'ga qo'shilmaydi)
app_persistent = Client(
    "prod_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",  # .gitignore: sessions/*.session*
)

# 2) In-memory sessiya — diskka hech narsa yozilmaydi (masalan, testlar uchun)
app_ephemeral = Client(
    "test_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
)


async def export_portable_session():
    \"\"\"Foydalanuvchi rejimidagi sessiyani boshqa muhitga ko'chirish uchun
    bitta matn qatoriga aylantiradi. Bu qatorni FAQAT maxfiy o'zgaruvchi
    sifatida saqlang (masalan CI secrets), hech qachon logga chiqarmang.\"\"\"
    async with Client("user_account", api_id=API_ID, api_hash=API_HASH) as user_app:
        session_string = await user_app.export_session_string()
        # Bu yerda print() ATAYLAB yo'q — production kodida session_string
        # hech qachon konsolga yoki logga chiqarilmaydi.
        return session_string


async def restore_from_string(session_string: str) -> Client:
    \"\"\"Boshqa muhitda faylsiz, session_string orqali qayta ulanish.\"\"\"
    app = Client("restored", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
    await app.start()
    return app
""",
        "code_content_ru": """import os
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

# 1) Сессия на основе файла, в отдельной папке (не добавляется в git)
app_persistent = Client(
    "prod_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",  # .gitignore: sessions/*.session*
)

# 2) In-memory сессия — на диск ничего не пишется (например, для тестов)
app_ephemeral = Client(
    "test_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
)


async def export_portable_session():
    \"\"\"Превращает сессию режима пользователя в одну строку для переноса в
    другое окружение. Храните эту строку ТОЛЬКО как секретную переменную
    (например CI secrets), никогда не выводите в лог.\"\"\"
    async with Client("user_account", api_id=API_ID, api_hash=API_HASH) as user_app:
        session_string = await user_app.export_session_string()
        # print() здесь НАРОЧНО нет — в продакшене session_string никогда
        # не выводится в консоль или лог.
        return session_string


async def restore_from_string(session_string: str) -> Client:
    \"\"\"Повторное подключение без файла, через session_string, в другом окружении.\"\"\"
    app = Client("restored", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
    await app.start()
    return app
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: xavfsiz sessiya sozlamalarini qo'llang",
            "task_title_ru": "Практика: примените безопасные настройки сессии",
            "task_description": (
                "Mavjud (yoki yangi) botingizga workdir='./sessions' qo'shing, .gitignore "
                "faylida *.session va *.session-journal borligini tekshiring (yo'q bo'lsa "
                "qo'shing). Qo'shimcha ravishda in_memory=True bilan alohida test Client "
                "yozing va ikkalasining farqini (fayl bor/yo'qligini) amalda ko'rsating."
            ),
            "task_description_ru": (
                "Добавьте в существующего (или нового) бота workdir='./sessions', проверьте "
                "наличие *.session и *.session-journal в .gitignore (добавьте, если их нет). "
                "Дополнительно напишите отдельный тестовый Client с in_memory=True и покажите "
                "на практике разницу (наличие/отсутствие файла)."
            ),
            "task_requirements": (
                ".gitignore session fayllarini chetlab o'tishi kerak; workdir aniq ko'rsatilgan "
                "bo'lishi kerak; in_memory=True bilan ishlaydigan Client namunasi bo'lishi kerak."
            ),
            "task_requirements_ru": (
                ".gitignore должен исключать файлы сессий; workdir должен быть явно указан; "
                "должен быть пример работающего Client с in_memory=True."
            ),
            "task_technologies": "Pyrogram, git",
            "task_deadline_days": 2,
        },
        "sample": {
            "title": "Namuna: .gitignore va sessiya konfiguratsiyasi",
            "title_ru": "Пример: .gitignore и конфигурация сессии",
            "description": "Xavfsiz workdir sozlamasi va session fayllarni git'dan chetlashtiruvchi .gitignore namunasi.",
            "description_ru": "Пример безопасной настройки workdir и .gitignore, исключающего файлы сессий из git.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": ".gitignore",
                    "language": "text",
                    "code": """# Pyrogram session fayllari — HECH QACHON git'ga qo'shilmasin
sessions/*.session
sessions/*.session-journal
*.session
*.session-journal

# Muhit o'zgaruvchilari (api_id/api_hash/session_string shu yerda)
.env
""",
                },
                {
                    "filename": "bot.py",
                    "language": "python",
                    "code": """import os
from pyrogram import Client

app = Client(
    "prod_bot",
    api_id=int(os.environ["TG_API_ID"]),
    api_hash=os.environ["TG_API_HASH"],
    bot_token=os.environ["TG_BOT_TOKEN"],
    workdir="./sessions",  # .gitignore bilan himoyalangan
)

app.run()
""",
                },
            ],
        },
        "exercises": [
            {
                "title": "Session fayl ichida nima saqlanadi",
                "title_ru": "Что хранится внутри файла сессии",
                "description": "Pyrogram session faylida asosan nima saqlanadi?",
                "description_ru": "Что в основном хранится в файле сессии Pyrogram?",
                "exercise_type": "multiple_choice",
                "options": ["Telegram parolingiz", "MTProto auth_key (ulanish kaliti)", "Telefon raqamingiz matni", "Bot buyruqlari ro'yxati"],
                "options_ru": ["Ваш пароль Telegram", "MTProto auth_key (ключ подключения)", "Текст вашего номера телефона", "Список команд бота"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu shifrlash kaliti, parolning o'zi emas.",
                "hint_ru": "Это ключ шифрования, а не сам пароль.",
                "explanation": "Session fayl MTProto auth_key'ni saqlaydi — bu kalit orqali qayta SMS/2FA'siz ulanish mumkin.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Diskka yozmaydigan sessiya parametri",
                "title_ru": "Параметр сессии, не пишущей на диск",
                "description": "Sessiyani diskka umuman yozmaslik uchun Client(..., ___=True) parametri beriladi",
                "description_ru": "Чтобы вообще не писать сессию на диск, передаётся параметр Client(..., ___=True)",
                "exercise_type": "fill_in_blank",
                "correct_answers": "in_memory",
                "hint": "'Xotirada' degan ma'noni bildiruvchi ingliz iborasi.",
                "hint_ru": "Английское выражение, означающее 'в памяти'.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sessiya oshkor bo'lganda harakatlar ketma-ketligi",
                "title_ru": "Порядок действий при утечке сессии",
                "description": "Sessiya (fayl yoki session_string) oshkor bo'lgani aniqlanganda bajarilishi kerak bo'lgan qadamlarni to'g'ri tartibga joylashtiring",
                "description_ru": "Расположите шаги, которые нужно предпринять при обнаружении утечки сессии, в правильном порядке",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Muammoni aniqlash (kutilmagan harakatlar ko'rinishi)", "Telegram Settings > Devices ga kirish", "Terminate all other sessions bosish", "Yangi, toza sessiya bilan qayta ulanish"],
                "drag_items_ru": ["Обнаружение проблемы (неожиданные действия)", "Переход в Telegram Settings > Devices", "Нажать Terminate all other sessions", "Повторное подключение с новой чистой сессией"],
                "correct_order": ["Muammoni aniqlash (kutilmagan harakatlar ko'rinishi)", "Telegram Settings > Devices ga kirish", "Terminate all other sessions bosish", "Yangi, toza sessiya bilan qayta ulanish"],
                "hint": "Avval muammoni bilish kerak, keyingina uni bartaraf etish mumkin.",
                "hint_ru": "Сначала нужно узнать о проблеме, только потом можно её устранить.",
                "difficulty_level": "Medium",
                "points": 7,
            },
            {
                "title": "session_string nima uchun xavfli hisoblanadi",
                "title_ru": "Почему session_string считается опасным",
                "description": "export_session_string() natijasida olingan matn nima uchun bot_token bilan bir xil ehtiyotkorlik talab qilishini, hattoki undan ham ko'proq bo'lishi mumkinligini tushuntiring.",
                "description_ru": "Объясните, почему строка, полученная через export_session_string(), требует такой же (а возможно, и большей) осторожности, что и bot_token.",
                "exercise_type": "text_input",
                "expected_answer": "session_string butun MTProto auth_key'ni o'zida saqlaydi, xuddi .session fayl kabi — uni olgan kishi hech qanday qo'shimcha tasdiqlashsiz to'liq hisobga (foydalanuvchi rejimida esa butun shaxsiy akkauntga) kira oladi; bot_token faqat bot funksiyalarini beradi va oson revoke qilinadi, lekin session_string/faylni 'revoke' qilib bo'lmaydi, faqat barcha seanslarni tugatish mumkin.",
                "hint": "Nima kirish huquqini beradi va uni bekor qilish qanchalik oson yoki qiyinligini solishtiring.",
                "hint_ru": "Сравните, какой доступ даёт каждый из них и насколько легко или сложно его отозвать.",
                "difficulty_level": "Hard",
                "points": 8,
            },
        ],
    },
    {
        "order": 5,
        "title": "6-Boy xabarlar: inline klaviaturalar, media guruhlari va formatlash",
        "title_ru": "6-Насыщенные сообщения: inline-клавиатуры, медиа-группы и форматирование",
        "points_reward": 15,
        "code_language": "python",
        "text_content": """<h3>InlineKeyboardMarkup — aiogram'ga tanish, sintaksisi biroz boshqacha</h3>
<p>48-kursda ko'rgan tugmalar mantig'i xuddi shu, faqat klass nomlari va joylashuvi biroz farq
qiladi. Pyrogram'da <code>pyrogram.types</code> ichidan import qilinadi:</p>
<pre><code>from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Ha", callback_data="confirm_yes"),
     InlineKeyboardButton("Yo'q", callback_data="confirm_no")],
    [InlineKeyboardButton("Bekor qilish", callback_data="confirm_cancel")],
])

await message.reply_text("Tasdiqlaysizmi?", reply_markup=keyboard)</code></pre>
<p>Tashqi ro'yxat &mdash; qatorlar, ichki ro'yxat &mdash; bitta qatordagi tugmalar. URL tugmasi
uchun <code>InlineKeyboardButton("Sayt", url="https://...")</code>, web_app tugmasi uchun
<code>InlineKeyboardButton("Ochish", web_app=WebAppInfo(url="..."))</code> ishlatiladi.</p>

<h3>Matn formatlash: parse_mode va enums</h3>
<p>Pyrogram Markdown va HTML formatlashning ikkalasini ham qo'llab-quvvatlaydi. Standart
holatda <code>ParseMode.MARKDOWN</code> ishlatiladi, lekin uni aniq belgilash tavsiya etiladi:</p>
<pre><code>from pyrogram.enums import ParseMode

await message.reply_text(
    "**Qalin matn**, __kursiv__, `kod`, [havola](https://example.com)",
    parse_mode=ParseMode.MARKDOWN,
)

await message.reply_text(
    "&lt;b&gt;Qalin&lt;/b&gt;, &lt;i&gt;kursiv&lt;/i&gt;, &lt;code&gt;kod&lt;/code&gt;",
    parse_mode=ParseMode.HTML,
)</code></pre>
<p>Muhim: foydalanuvchi kiritgan matnni formatlangan xabar ichiga to'g'ridan-to'g'ri qo'yishdan
saqlaning &mdash; agar u Markdown/HTML maxsus belgilar (masalan <code>*</code>, <code>_</code>,
<code>&lt;</code>) tutsa, xabar buzilib ketishi yoki hatto xato berishi mumkin. Kerak bo'lsa
<code>parse_mode=ParseMode.DISABLED</code> bilan xom matn sifatida yuboring.</p>

<h3>Media guruhlari: bir nechta rasm/videoni bitta albom sifatida</h3>
<p><code>send_media_group()</code> orqali 2 dan 10 tagacha media faylni bitta "albom" sifatida
yuborish mumkin &mdash; foydalanuvchi ularni Telegram'da bitta guruhlangan blok sifatida ko'radi:</p>
<pre><code>from pyrogram.types import InputMediaPhoto, InputMediaVideo

await client.send_media_group(
    chat_id,
    [
        InputMediaPhoto("photo1.jpg", caption="Albom tavsifi shu yerda"),
        InputMediaPhoto("photo2.jpg"),
        InputMediaVideo("clip.mp4"),
    ],
)</code></pre>
<p>Muhim cheklov: <code>caption</code> faqat <strong>birinchi</strong> elementga qo'yiladi
&mdash; u butun albom uchun umumiy tavsif bo'lib xizmat qiladi, qolganlariga caption berilsa
e'tiborga olinmaydi.</p>

<h3>Reply klaviatura vs inline klaviatura</h3>
<table>
<tr><th>Turi</th><th>Klass</th><th>Xatti-harakati</th></tr>
<tr><td>Reply</td><td><code>ReplyKeyboardMarkup</code></td><td>Klaviatura o'rnini egallaydi, tugma bosilganda oddiy matn xabar sifatida keladi</td></tr>
<tr><td>Inline</td><td><code>InlineKeyboardMarkup</code></td><td>Xabarning o'zida ko'rinadi, bosilganda <code>callback_query</code> update keladi (keyingi darsda)</td></tr>
<tr><td>Olib tashlash</td><td><code>ReplyKeyboardRemove()</code></td><td>Reply klaviaturani ekrandan olib tashlaydi</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  MSG["message.reply_text(..., reply_markup=?)"]
  MSG --> RK["ReplyKeyboardMarkup
pastda ko'rinadi"]
  MSG --> IK["InlineKeyboardMarkup
xabar ichida ko'rinadi"]
  RK -->|"tugma bosildi"| TXT["Oddiy matnli message
(filters.text bilan ushlanadi)"]
  IK -->|"tugma bosildi"| CB["callback_query update
(alohida handler kerak)"]
</pre>
<p>Diagram ikkala klaviatura turining tugma bosilgandan keyin <em>butunlay boshqa</em> update
turini yuborishini ko'rsatadi &mdash; bu keyingi darsda callback_query handlerini alohida
o'rganish sababini tushuntiradi.</p>

<h3>Fayl yuborishning uch usuli</h3>
<p>Media yuborishda uchta manba qabul qilinadi: mahalliy fayl yo'li (<code>"rasm.jpg"</code>),
tayyor <code>file_id</code> (Telegram serverida allaqachon bor faylga havola &mdash; qayta
yuklashga hojat yo'q, tezroq) yoki to'g'ridan-to'g'ri URL. Katta fayllarni tez-tez qayta
yuborsangiz, birinchi yuborishdan qaytgan <code>message.photo.file_id</code>ni saqlab qo'yish
va keyingi safar shuni ishlatish &mdash; qayta yuklashdan ko'ra sezilarli tezroq.</p>""",
        "text_content_ru": """<h3>InlineKeyboardMarkup — знакомо по aiogram, синтаксис немного другой</h3>
<p>Логика кнопок, которую вы видели в курсе 48, та же самая, только названия классов и их
расположение немного отличаются. В Pyrogram импортируется из <code>pyrogram.types</code>:</p>
<pre><code>from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Да", callback_data="confirm_yes"),
     InlineKeyboardButton("Нет", callback_data="confirm_no")],
    [InlineKeyboardButton("Отмена", callback_data="confirm_cancel")],
])

await message.reply_text("Подтверждаете?", reply_markup=keyboard)</code></pre>
<p>Внешний список &mdash; строки, внутренний список &mdash; кнопки в одной строке. Для кнопки
со ссылкой используется <code>InlineKeyboardButton("Сайт", url="https://...")</code>, для кнопки
web_app &mdash; <code>InlineKeyboardButton("Открыть", web_app=WebAppInfo(url="..."))</code>.</p>

<h3>Форматирование текста: parse_mode и enums</h3>
<p>Pyrogram поддерживает и Markdown, и HTML форматирование. По умолчанию используется
<code>ParseMode.MARKDOWN</code>, но рекомендуется указывать его явно:</p>
<pre><code>from pyrogram.enums import ParseMode

await message.reply_text(
    "**Жирный текст**, __курсив__, `код`, [ссылка](https://example.com)",
    parse_mode=ParseMode.MARKDOWN,
)

await message.reply_text(
    "&lt;b&gt;Жирный&lt;/b&gt;, &lt;i&gt;курсив&lt;/i&gt;, &lt;code&gt;код&lt;/code&gt;",
    parse_mode=ParseMode.HTML,
)</code></pre>
<p>Важно: избегайте прямой вставки текста, введённого пользователем, внутрь форматированного
сообщения &mdash; если он содержит специальные символы Markdown/HTML (например <code>*</code>,
<code>_</code>, <code>&lt;</code>), сообщение может сломаться или даже вызвать ошибку. При
необходимости отправляйте как обычный текст через <code>parse_mode=ParseMode.DISABLED</code>.</p>

<h3>Медиа-группы: несколько фото/видео как один альбом</h3>
<p>Через <code>send_media_group()</code> можно отправить от 2 до 10 медиафайлов как один
«альбом» &mdash; пользователь увидит их в Telegram как единый сгруппированный блок:</p>
<pre><code>from pyrogram.types import InputMediaPhoto, InputMediaVideo

await client.send_media_group(
    chat_id,
    [
        InputMediaPhoto("photo1.jpg", caption="Здесь описание альбома"),
        InputMediaPhoto("photo2.jpg"),
        InputMediaVideo("clip.mp4"),
    ],
)</code></pre>
<p>Важное ограничение: <code>caption</code> ставится только на <strong>первый</strong> элемент
&mdash; он служит общим описанием для всего альбома, если задать caption для остальных, он
будет проигнорирован.</p>

<h3>Reply-клавиатура vs inline-клавиатура</h3>
<table>
<tr><th>Тип</th><th>Класс</th><th>Поведение</th></tr>
<tr><td>Reply</td><td><code>ReplyKeyboardMarkup</code></td><td>Занимает место клавиатуры, при нажатии приходит обычное текстовое сообщение</td></tr>
<tr><td>Inline</td><td><code>InlineKeyboardMarkup</code></td><td>Отображается прямо в сообщении, при нажатии приходит update <code>callback_query</code> (следующий урок)</td></tr>
<tr><td>Убрать</td><td><code>ReplyKeyboardRemove()</code></td><td>Убирает reply-клавиатуру с экрана</td></tr>
</table>

<pre class="mermaid">
flowchart TB
  MSG["message.reply_text(..., reply_markup=?)"]
  MSG --> RK["ReplyKeyboardMarkup
видна внизу"]
  MSG --> IK["InlineKeyboardMarkup
видна внутри сообщения"]
  RK -->|"кнопка нажата"| TXT["Обычное текстовое message
(ловится через filters.text)"]
  IK -->|"кнопка нажата"| CB["update callback_query
(нужен отдельный обработчик)"]
</pre>
<p>Диаграмма показывает, что оба типа клавиатур после нажатия кнопки отправляют <em>совершенно
разный</em> тип update — это объясняет, почему в следующем уроке callback_query изучается
отдельно.</p>

<h3>Три способа отправки файла</h3>
<p>При отправке медиа принимаются три источника: локальный путь к файлу (<code>"photo.jpg"</code>),
готовый <code>file_id</code> (ссылка на уже существующий на сервере Telegram файл &mdash;
повторная загрузка не нужна, быстрее) или прямой URL. Если вы часто повторно отправляете
большой файл, сохраните <code>message.photo.file_id</code>, полученный при первой отправке, и
используйте его в следующий раз &mdash; это заметно быстрее повторной загрузки.</p>""",
        "code_content": """from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto,
)
from pyrogram.enums import ParseMode

app = Client("rich_messages_demo")


@app.on_message(filters.command("menu"))
async def show_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Katalog", callback_data="menu_catalog"),
         InlineKeyboardButton("Buyurtmalarim", callback_data="menu_orders")],
        [InlineKeyboardButton("Bizning sayt", url="https://example.com")],
    ])
    await message.reply_text(
        "**Asosiy menyu**\\nKerakli bo'limni tanlang:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


@app.on_message(filters.command("album"))
async def send_album(client, message):
    await client.send_media_group(
        message.chat.id,
        [
            InputMediaPhoto("images/product1.jpg", caption="Yangi kolleksiya — 3 ta mahsulot"),
            InputMediaPhoto("images/product2.jpg"),
            InputMediaPhoto("images/product3.jpg"),
        ],
    )


# file_id'ni keshlash — qayta yuklashdan qochish
_cached_banner_id: str | None = None


@app.on_message(filters.command("banner"))
async def send_banner(client, message):
    global _cached_banner_id
    if _cached_banner_id:
        await message.reply_photo(_cached_banner_id)
        return
    sent = await message.reply_photo("images/banner.jpg", caption="Bizning banner")
    _cached_banner_id = sent.photo.file_id


if __name__ == "__main__":
    app.run()
""",
        "code_content_ru": """from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto,
)
from pyrogram.enums import ParseMode

app = Client("rich_messages_demo")


@app.on_message(filters.command("menu"))
async def show_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Каталог", callback_data="menu_catalog"),
         InlineKeyboardButton("Мои заказы", callback_data="menu_orders")],
        [InlineKeyboardButton("Наш сайт", url="https://example.com")],
    ])
    await message.reply_text(
        "**Главное меню**\\nВыберите нужный раздел:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


@app.on_message(filters.command("album"))
async def send_album(client, message):
    await client.send_media_group(
        message.chat.id,
        [
            InputMediaPhoto("images/product1.jpg", caption="Новая коллекция — 3 товара"),
            InputMediaPhoto("images/product2.jpg"),
            InputMediaPhoto("images/product3.jpg"),
        ],
    )


# Кеширование file_id — избегаем повторной загрузки
_cached_banner_id: str | None = None


@app.on_message(filters.command("banner"))
async def send_banner(client, message):
    global _cached_banner_id
    if _cached_banner_id:
        await message.reply_photo(_cached_banner_id)
        return
    sent = await message.reply_photo("images/banner.jpg", caption="Наш баннер")
    _cached_banner_id = sent.photo.file_id


if __name__ == "__main__":
    app.run()
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: menyu, albom va file_id keshlash",
            "task_title_ru": "Практика: меню, альбом и кеширование file_id",
            "task_description": (
                "Bot yozing: /menu buyrug'i inline klaviatura (kamida 3 tugma, biri url= bilan) "
                "ko'rsatsin; /album buyrug'i send_media_group orqali kamida 3 ta rasmni albom "
                "sifatida yuborsin (faqat birinchisida caption bo'lsin); /banner buyrug'i "
                "birinchi safar faylni yuklab, file_id'ni keshlab qo'ysin va keyingi "
                "chaqiruvlarda o'sha file_id'dan foydalansin."
            ),
            "task_description_ru": (
                "Напишите бота: команда /menu показывает inline-клавиатуру (минимум 3 кнопки, "
                "одна с url=); команда /album через send_media_group отправляет минимум 3 фото "
                "как альбом (caption только у первого); команда /banner в первый раз загружает "
                "файл и кеширует file_id, а при следующих вызовах использует этот file_id."
            ),
            "task_requirements": (
                "InlineKeyboardMarkup kamida 3 ta tugma bilan ishlatilishi kerak; "
                "send_media_group kamida 3 elementli bo'lishi kerak; file_id keshlash mantiqi "
                "amalda ishlashi kerak (ikkinchi chaqiruvda qayta yuklanmasligi)."
            ),
            "task_requirements_ru": (
                "InlineKeyboardMarkup должна использоваться минимум с 3 кнопками; "
                "send_media_group должна содержать минимум 3 элемента; логика кеширования "
                "file_id должна реально работать (без повторной загрузки при втором вызове)."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: inline menyu va media albom",
            "title_ru": "Пример: inline-меню и медиа-альбом",
            "description": "InlineKeyboardMarkup, parse_mode va send_media_group ishlatilgan to'liq misol.",
            "description_ru": "Полный пример с InlineKeyboardMarkup, parse_mode и send_media_group.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "rich_menu.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.enums import ParseMode

app = Client("rich_menu_demo")


@app.on_message(filters.command("start"))
async def start(client, message):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Katalog", callback_data="catalog")],
        [InlineKeyboardButton("Bizning sayt", url="https://example.com")],
    ])
    await message.reply_text(
        "**Xush kelibsiz!**\\nQuyidagi tugmalardan birini tanlang.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb,
    )


@app.on_message(filters.command("catalog_photos"))
async def catalog_photos(client, message):
    await client.send_media_group(
        message.chat.id,
        [
            InputMediaPhoto("images/1.jpg", caption="Katalog — 3 ta namuna mahsulot"),
            InputMediaPhoto("images/2.jpg"),
            InputMediaPhoto("images/3.jpg"),
        ],
    )


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Callback tugmasi qaysi klass orqali yaratiladi",
                "title_ru": "Через какой класс создаётся callback-кнопка",
                "description": "callback_data bilan tugma yaratish uchun qaysi klass ishlatiladi?",
                "description_ru": "Какой класс используется для создания кнопки с callback_data?",
                "exercise_type": "multiple_choice",
                "options": ["ReplyKeyboardButton", "InlineKeyboardButton", "MenuButton", "CallbackButton"],
                "options_ru": ["ReplyKeyboardButton", "InlineKeyboardButton", "MenuButton", "CallbackButton"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "callback_data faqat xabar ichida ko'rinadigan klaviatura turida bo'ladi.",
                "hint_ru": "callback_data бывает только у клавиатуры, отображаемой прямо внутри сообщения.",
                "explanation": "InlineKeyboardButton callback_data, url yoki web_app parametrlaridan birini qabul qiladi; ReplyKeyboardButton esa oddiy matn tugmalari uchun.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "send_media_group elementlar soni",
                "title_ru": "Количество элементов в send_media_group",
                "description": "send_media_group() metodi bitta chaqiruvda kamida nechta va ko'pi bilan nechta media qabul qiladi? Javobni 'kamida-ko'pi' shaklida yozing, masalan: ___",
                "description_ru": "Сколько минимум и максимум медиа принимает send_media_group() за один вызов? Запишите ответ в формате 'минимум-максимум', например: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "2-10",
                "hint": "Bitta media uchun bu metod shart emas, oddiy send_photo yetarli.",
                "hint_ru": "Для одного медиа этот метод не нужен, достаточно обычного send_photo.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Reply va inline klaviatura tugma bosilganda nima yuboradi",
                "title_ru": "Что отправляет нажатие кнопки reply и inline клавиатуры",
                "description": "Har bir klaviatura turini tugma bosilgandan keyin yuboradigan update turi bilan mos tartibda joylashtiring",
                "description_ru": "Расположите типы клавиатур в порядке, соответствующем типу update после нажатия кнопки",
                "exercise_type": "drag_and_drop",
                "drag_items": ["ReplyKeyboardMarkup -> oddiy matnli message", "InlineKeyboardMarkup -> callback_query update"],
                "drag_items_ru": ["ReplyKeyboardMarkup -> обычное текстовое message", "InlineKeyboardMarkup -> update callback_query"],
                "correct_order": ["ReplyKeyboardMarkup -> oddiy matnli message", "InlineKeyboardMarkup -> callback_query update"],
                "hint": "Reply klaviatura shunchaki matn yuboradi, xuddi foydalanuvchi o'zi yozgandek.",
                "hint_ru": "Reply-клавиатура просто отправляет текст, как будто пользователь написал его сам.",
                "difficulty_level": "Medium",
                "points": 6,
            },
        ],
    },
    {
        "order": 6,
        "title": "7-Callback query va inline query'larni qayta ishlash",
        "title_ru": "7-Обработка callback query и inline query",
        "points_reward": 15,
        "code_language": "python",
        "text_content": """<h3>Callback query: inline tugma bosilganda nima keladi</h3>
<p>Foydalanuvchi <code>InlineKeyboardButton(callback_data="...")</code> tugmasini bosganda, bot
tomonga <strong>alohida update turi</strong> &mdash; <code>callback_query</code> &mdash; keladi
(oddiy message emas). Uni ushlash uchun alohida dekorator kerak:</p>
<pre><code>from pyrogram import Client, filters

@app.on_callback_query(filters.regex("^menu_"))
async def on_menu_button(client, callback_query):
    action = callback_query.data  # masalan "menu_catalog"
    await callback_query.answer()  # MAJBURIY — "yuklanmoqda" belgisini olib tashlaydi
    await callback_query.message.edit_text(f"Siz tanladingiz: {action}")</code></pre>
<p><code>callback_query.answer()</code> ni chaqirish <strong>shart</strong> &mdash; aks holda
foydalanuvchi tugmasi cheksiz "yuklanmoqda" holatida (soat belgisi) qolib ketadi, hattoki
handler o'z ishini bajargan bo'lsa ham. <code>answer(text="...", show_alert=True)</code> orqali
qisqa xabar yoki modal oynani ham ko'rsatish mumkin &mdash; bu Bot API'dagi
<code>answerCallbackQuery</code>ning aynan o'zi.</p>

<h3>edit_text vs yangi xabar yuborish</h3>
<p>Callback handler ichida ko'pincha yangi xabar yuborish o'rniga <strong>mavjud xabarni
tahrirlash</strong> afzalroq &mdash; <code>callback_query.message.edit_text(...)</code> yoki
<code>edit_reply_markup(...)</code> orqali. Bu chatni keraksiz yangi xabarlar bilan
to'ldirmaydi va foydalanuvchiga "menyu joyida yangilanadi" tuyg'usini beradi.</p>

<h3>callback_data'ning 64 baytlik cheklovi</h3>
<p>Muhim texnik cheklov: <code>callback_data</code> maydoni <strong>64 baytdan oshmasligi</strong>
kerak. Murakkab holat (masalan, mahsulot ID + amal turi) uchun butun JSON obyektini emas, qisqa
kodlangan format ishlatiladi: <code>f"prod:{action}:{product_id}"</code>, keyin handler ichida
<code>callback_query.data.split(":")</code> orqali ajratiladi.</p>

<h3>Inline query: @bot so'z formatidagi qidiruv</h3>
<p>Foydalanuvchi istalgan chatda <code>@sizning_botingiz so'rov</code> deb yozganda, bot
<code>inline_query</code> update oladi &mdash; bu Bot API'dagi inline mode bilan bir xil
kontseptsiya. Bot <code>answer_inline_query()</code> orqali natijalar ro'yxatini qaytaradi:</p>
<pre><code>from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

@app.on_inline_query()
async def search_handler(client, inline_query):
    query_text = inline_query.query
    results = [
        InlineQueryResultArticle(
            title=f"Natija: {query_text}",
            input_message_content=InputTextMessageContent(f"Siz qidirdingiz: {query_text}"),
        )
    ]
    await inline_query.answer(results, cache_time=1)</code></pre>
<p><code>cache_time</code> &mdash; Telegram serveri natijalarni necha soniya keshlab turishini
belgilaydi; tez o'zgaruvchi natijalar uchun (masalan real vaqtdagi narx) uni kichik (0-1)
qilib qo'yish kerak.</p>

<pre class="mermaid">
sequenceDiagram
  participant U as Foydalanuvchi
  participant T as Telegram server
  participant B as Bot (Pyrogram)
  U->>T: Inline tugmani bosadi
  T->>B: callback_query update
  B->>B: callback_query.answer()
  B->>T: message.edit_text(...)
  T->>U: Xabar yangilanadi, "yuklanmoqda" yo'qoladi
</pre>
<p>Diagram callback_query'ning to'liq hayotiy siklini ko'rsatadi: tugma bosilishidan
<code>answer()</code> chaqirilishigacha (soat belgisini olib tashlash uchun majburiy), so'ngra
xabarni tahrirlashgacha.</p>

<h3>Ikkalasi orasidagi asosiy farq</h3>
<table>
<tr><th></th><th>callback_query</th><th>inline_query</th></tr>
<tr><td>Qachon keladi</td><td>Botning o'z xabaridagi tugma bosilganda</td><td>Istalgan chatda @bot yozilganda</td></tr>
<tr><td>Javob metodi</td><td>callback_query.answer()</td><td>inline_query.answer(results)</td></tr>
<tr><td>Majburiymi</td><td>Ha &mdash; aks holda tugma abadiy "yuklanmoqda"da qoladi</td><td>Yo'q, lekin javobsiz foydalanuvchiga hech narsa ko'rsatilmaydi</td></tr>
</table>

<h3>Xavfsizlik eslatmasi: callback_data'ni ko'r-ko'rona ishonib bo'lmaydi</h3>
<p>callback_query.data &mdash; bu bot o'zi tugma yaratayotganda yozgan matn, lekin amalda uni
har doim <em>kim yubordi</em> bilan birga tekshiring: masalan admin panelidagi
<code>callback_data="admin:delete:42"</code> tugmasi faqat asl adminga ko'rsatilgan bo'lsa ham,
handler ichida yana bir bor <code>callback_query.from_user.id</code>ni tekshirib chiqish
kerak &mdash; chunki eski xabar forward qilinishi yoki ekran skrinshoti orqali boshqa kontekstga
tushib qolishi mumkin emas, lekin ehtiyotkorlik odat bo'lishi kerak.</p>""",
        "text_content_ru": """<h3>Callback query: что приходит при нажатии inline-кнопки</h3>
<p>Когда пользователь нажимает <code>InlineKeyboardButton(callback_data="...")</code>, боту
приходит <strong>отдельный тип update</strong> &mdash; <code>callback_query</code> (не обычное
message). Чтобы его поймать, нужен отдельный декоратор:</p>
<pre><code>from pyrogram import Client, filters

@app.on_callback_query(filters.regex("^menu_"))
async def on_menu_button(client, callback_query):
    action = callback_query.data  # например "menu_catalog"
    await callback_query.answer()  # ОБЯЗАТЕЛЬНО — убирает индикатор "загрузка"
    await callback_query.message.edit_text(f"Вы выбрали: {action}")</code></pre>
<p>Вызов <code>callback_query.answer()</code> <strong>обязателен</strong> &mdash; иначе кнопка
у пользователя бесконечно останется в состоянии «загрузка» (значок часиков), даже если
обработчик уже выполнил свою работу. Через <code>answer(text="...", show_alert=True)</code>
можно показать краткое сообщение или модальное окно &mdash; это в точности
<code>answerCallbackQuery</code> из Bot API.</p>

<h3>edit_text против отправки нового сообщения</h3>
<p>Внутри обработчика callback часто предпочтительнее не отправлять новое сообщение, а
<strong>отредактировать существующее</strong> &mdash; через
<code>callback_query.message.edit_text(...)</code> или <code>edit_reply_markup(...)</code>.
Это не засоряет чат лишними новыми сообщениями и создаёт у пользователя ощущение «меню
обновляется на месте».</p>

<h3>Ограничение в 64 байта для callback_data</h3>
<p>Важное техническое ограничение: поле <code>callback_data</code> не должно превышать
<strong>64 байт</strong>. Для сложного случая (например ID товара + тип действия) используют
не целый JSON-объект, а короткий закодированный формат: <code>f"prod:{action}:{product_id}"</code>,
затем внутри обработчика разбирают через <code>callback_query.data.split(":")</code>.</p>

<h3>Inline query: поиск в формате @bot слово</h3>
<p>Когда пользователь в любом чате пишет <code>@ваш_бот запрос</code>, бот получает update
<code>inline_query</code> &mdash; та же концепция, что и inline mode в Bot API. Бот возвращает
список результатов через <code>answer_inline_query()</code>:</p>
<pre><code>from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

@app.on_inline_query()
async def search_handler(client, inline_query):
    query_text = inline_query.query
    results = [
        InlineQueryResultArticle(
            title=f"Результат: {query_text}",
            input_message_content=InputTextMessageContent(f"Вы искали: {query_text}"),
        )
    ]
    await inline_query.answer(results, cache_time=1)</code></pre>
<p><code>cache_time</code> определяет, сколько секунд сервер Telegram будет кешировать
результаты; для быстро меняющихся данных (например, цена в реальном времени) его стоит
делать маленьким (0-1).</p>

<pre class="mermaid">
sequenceDiagram
  participant U as Пользователь
  participant T as Сервер Telegram
  participant B as Бот (Pyrogram)
  U->>T: Нажимает inline-кнопку
  T->>B: update callback_query
  B->>B: callback_query.answer()
  B->>T: message.edit_text(...)
  T->>U: Сообщение обновляется, "загрузка" исчезает
</pre>
<p>Диаграмма показывает полный жизненный цикл callback_query: от нажатия кнопки до вызова
<code>answer()</code> (обязателен для снятия индикатора загрузки), а затем редактирования
сообщения.</p>

<h3>Основное различие между ними</h3>
<table>
<tr><th></th><th>callback_query</th><th>inline_query</th></tr>
<tr><td>Когда приходит</td><td>При нажатии кнопки в сообщении бота</td><td>Когда в любом чате пишут @bot</td></tr>
<tr><td>Метод ответа</td><td>callback_query.answer()</td><td>inline_query.answer(results)</td></tr>
<tr><td>Обязателен ли</td><td>Да &mdash; иначе кнопка навсегда останется в "загрузке"</td><td>Нет, но без ответа пользователю ничего не покажется</td></tr>
</table>

<h3>Замечание по безопасности: нельзя слепо доверять callback_data</h3>
<p>callback_query.data &mdash; это текст, который сам бот записал при создании кнопки, но на
практике всегда проверяйте его вместе с тем, <em>кто отправил</em>: например, кнопка
<code>callback_data="admin:delete:42"</code> в админ-панели, даже если показана только
исходному админу, внутри обработчика всё равно стоит ещё раз проверить
<code>callback_query.from_user.id</code> &mdash; потому что старое сообщение может быть
переслано, а осторожность должна быть привычкой, а не исключением.</p>""",
        "code_content": """from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent,
)

app = Client("callback_inline_demo")

_PRODUCTS = {"1": "Kitob", "2": "Ruchka", "3": "Daftar"}


@app.on_message(filters.command("shop"))
async def shop(client, message):
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"prod:view:{pid}")]
        for pid, name in _PRODUCTS.items()
    ]
    await message.reply_text("Mahsulotlar:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex(r"^prod:view:"))
async def view_product(client, callback_query):
    _, _, product_id = callback_query.data.split(":")
    name = _PRODUCTS.get(product_id, "Noma'lum")
    await callback_query.answer()  # majburiy — "yuklanmoqda"ni olib tashlaydi
    buttons = [[InlineKeyboardButton("Xarid qilish", callback_data=f"prod:buy:{product_id}")]]
    await callback_query.message.edit_text(
        f"Siz tanladingiz: {name}", reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"^prod:buy:"))
async def buy_product(client, callback_query):
    await callback_query.answer("Buyurtma qabul qilindi!", show_alert=True)


@app.on_inline_query()
async def search_products(client, inline_query):
    q = inline_query.query.lower()
    results = [
        InlineQueryResultArticle(
            title=name,
            input_message_content=InputTextMessageContent(f"{name} — narxini so'rash uchun /shop"),
        )
        for pid, name in _PRODUCTS.items()
        if q in name.lower()
    ]
    await inline_query.answer(results, cache_time=1)


if __name__ == "__main__":
    app.run()
""",
        "code_content_ru": """from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent,
)

app = Client("callback_inline_demo")

_PRODUCTS = {"1": "Книга", "2": "Ручка", "3": "Тетрадь"}


@app.on_message(filters.command("shop"))
async def shop(client, message):
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"prod:view:{pid}")]
        for pid, name in _PRODUCTS.items()
    ]
    await message.reply_text("Товары:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex(r"^prod:view:"))
async def view_product(client, callback_query):
    _, _, product_id = callback_query.data.split(":")
    name = _PRODUCTS.get(product_id, "Неизвестно")
    await callback_query.answer()  # обязательно — убирает "загрузку"
    buttons = [[InlineKeyboardButton("Купить", callback_data=f"prod:buy:{product_id}")]]
    await callback_query.message.edit_text(
        f"Вы выбрали: {name}", reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"^prod:buy:"))
async def buy_product(client, callback_query):
    await callback_query.answer("Заказ принят!", show_alert=True)


@app.on_inline_query()
async def search_products(client, inline_query):
    q = inline_query.query.lower()
    results = [
        InlineQueryResultArticle(
            title=name,
            input_message_content=InputTextMessageContent(f"{name} — узнать цену: /shop"),
        )
        for pid, name in _PRODUCTS.items()
        if q in name.lower()
    ]
    await inline_query.answer(results, cache_time=1)


if __name__ == "__main__":
    app.run()
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: mini-do'kon callback zanjiri va inline qidiruv",
            "task_title_ru": "Практика: цепочка callback мини-магазина и inline-поиск",
            "task_description": (
                "3-5 mahsulotli lug'at yarating. /shop buyrug'i mahsulotlar ro'yxatini inline "
                "tugmalar bilan ko'rsatsin (callback_data 64 baytdan oshmasin, qisqa kodlangan "
                "format ishlating). Tugma bosilganda callback_query.answer() chaqirilib, xabar "
                "edit_text orqali yangilansin. Qo'shimcha /on_inline_query orqali mahsulot "
                "nomida qidiruv qiluvchi inline rejim yozing."
            ),
            "task_description_ru": (
                "Создайте словарь из 3-5 товаров. Команда /shop показывает список товаров с "
                "inline-кнопками (callback_data не более 64 байт, используйте короткий "
                "закодированный формат). При нажатии кнопки вызывается callback_query.answer(), "
                "сообщение обновляется через edit_text. Дополнительно напишите inline-режим "
                "через on_inline_query для поиска по названию товара."
            ),
            "task_requirements": (
                "callback_query.answer() har bir callback handlerda chaqirilishi kerak; "
                "callback_data qisqa kodlangan formatda bo'lishi kerak (64 bayt ichida); "
                "inline query natijalari InlineQueryResultArticle orqali qaytarilishi kerak."
            ),
            "task_requirements_ru": (
                "callback_query.answer() должен вызываться в каждом обработчике callback; "
                "callback_data должен быть в коротком закодированном формате (в пределах 64 "
                "байт); результаты inline query должны возвращаться через "
                "InlineQueryResultArticle."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: mini-do'kon callback zanjiri",
            "title_ru": "Пример: цепочка callback мини-магазина",
            "description": "callback_data kodlash, answer() va edit_text ishlatilgan to'liq ishlaydigan misol.",
            "description_ru": "Полностью рабочий пример с кодированием callback_data, answer() и edit_text.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "shop_callbacks.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("shop_demo")
PRODUCTS = {"1": "Kitob", "2": "Ruchka"}


@app.on_message(filters.command("shop"))
async def shop(client, message):
    buttons = [[InlineKeyboardButton(n, callback_data=f"p:{pid}")] for pid, n in PRODUCTS.items()]
    await message.reply_text("Tanlang:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_callback_query(filters.regex(r"^p:"))
async def on_pick(client, callback_query):
    _, pid = callback_query.data.split(":")
    await callback_query.answer(f"Tanlandi: {PRODUCTS[pid]}", show_alert=False)
    await callback_query.message.edit_text(f"Siz tanladingiz: {PRODUCTS[pid]}")


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Callback tugma bosilganda majburiy metod",
                "title_ru": "Обязательный метод при нажатии callback-кнопки",
                "description": "callback_query handlerida har doim chaqirilishi shart bo'lgan metod qaysi?",
                "description_ru": "Какой метод обязательно нужно вызвать внутри обработчика callback_query?",
                "exercise_type": "multiple_choice",
                "options": ["callback_query.reply()", "callback_query.answer()", "callback_query.send()", "callback_query.confirm()"],
                "options_ru": ["callback_query.reply()", "callback_query.answer()", "callback_query.send()", "callback_query.confirm()"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bu chaqiruv 'yuklanmoqda' soat belgisini olib tashlaydi.",
                "hint_ru": "Этот вызов убирает индикатор часиков «загрузка».",
                "explanation": "callback_query.answer() chaqirilmasa, foydalanuvchining tugmasi abadiy 'yuklanmoqda' holatida qolib ketadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "callback_data hajm chegarasi",
                "title_ru": "Ограничение размера callback_data",
                "description": "callback_data maydoni necha baytdan oshmasligi kerak: ___",
                "description_ru": "Поле callback_data не должно превышать сколько байт: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "64",
                "hint": "Kichik raqam, ko'p JSON obyektini sig'dirish uchun yetarli emas.",
                "hint_ru": "Небольшое число, недостаточное для большого JSON-объекта.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Inline query hayotiy siklini tartibga joylashtiring",
                "title_ru": "Расположите жизненный цикл inline query по порядку",
                "description": "Inline query'ning qadamlarini to'g'ri ketma-ketlikda joylashtiring",
                "description_ru": "Расположите шаги inline query в правильном порядке",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Foydalanuvchi @bot so'rov yozadi", "Bot inline_query update oladi", "Bot answer_inline_query() bilan natijalar qaytaradi", "Foydalanuvchi natijalardan birini tanlaydi"],
                "drag_items_ru": ["Пользователь пишет @bot запрос", "Бот получает update inline_query", "Бот возвращает результаты через answer_inline_query()", "Пользователь выбирает один из результатов"],
                "correct_order": ["Foydalanuvchi @bot so'rov yozadi", "Bot inline_query update oladi", "Bot answer_inline_query() bilan natijalar qaytaradi", "Foydalanuvchi natijalardan birini tanlaydi"],
                "hint": "Avval so'rov yoziladi, keyingina bot javob beradi.",
                "hint_ru": "Сначала пишется запрос, только потом бот отвечает.",
                "difficulty_level": "Medium",
                "points": 7,
            },
        ],
    },
    {
        "order": 7,
        "title": "8-Katta hajmdagi ma'lumotlar: chat tarixi va a'zolar bo'yicha async iteratsiya",
        "title_ru": "8-Работа с большими объёмами: асинхронная итерация по истории чата и участникам",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>Bot API'da yo'q, MTProto'da bor: chuqur tarix</h3>
<p>Bot API orqali botlar chatning eski xabarlarini "orqaga qarab" o'qiy olmaydi &mdash; faqat
kelayotgan update'larni ko'radi. Pyrogram MTProto darajasida ishlagani uchun bu cheklovga
ega emas: <code>get_chat_history()</code> orqali istalgan chatning butun (ruxsat etilgan)
tarixini <strong>orqaga qarab</strong> sahifalab o'qish mumkin &mdash; bu foydalanuvchi rejimida
ayniqsa kuchli (chunki foydalanuvchi hisobi allaqachon o'sha chatda "bo'lgan").</p>

<h3>async for &mdash; Pyrogram'ning sahifalashni yashiruvchi uslubi</h3>
<p>Katta ro'yxatlar (tarix, a'zolar, dialoglar) uchun Pyrogram alohida "keyingi sahifa" so'rovi
yozishga majburlamaydi &mdash; buning o'rniga <strong>async generator</strong> qaytaradi, va
siz oddiy <code>async for</code> bilan iteratsiya qilaverasiz, Pyrogram orqa fonda avtomatik
ravishda keyingi sahifalarni so'rab turadi:</p>
<pre><code>async for message in client.get_chat_history(chat_id, limit=1000):
    print(message.id, message.text)</code></pre>
<p><code>limit=0</code> (yoki umuman ko'rsatilmasa) &mdash; <strong>cheksiz</strong>, ya'ni
butun tarix oxirigacha o'qiladi. Katta kanallar uchun bu millionlab xabar bo'lishi mumkin,
shuning uchun har doim oqilona <code>limit</code> qo'yish yoki natijani real vaqtda qayta
ishlab, xotirada to'plamaslik kerak.</p>

<h3>Kanal/guruh a'zolarini ro'yxatlash</h3>
<pre><code>async for member in client.get_chat_members(chat_id):
    print(member.user.id, member.user.username, member.status)</code></pre>
<p>Katta ochiq kanallar (o'nlab minglab a'zo) uchun bu operatsiya sezilarli vaqt olishi va
Telegram'ning flood-limitlariga tegishi mumkin &mdash; ayniqsa userbot rejimida tez-tez
qo'llanilsa. <code>filter=</code> parametri orqali faqat ma'lum status (masalan
<code>ChatMembersFilter.ADMINISTRATORS</code>) bo'yicha cheklash tezlikni oshiradi.</p>

<h3>FloodWait: MTProto'ning tabiiy rate-limit signali</h3>
<p>Ko'p so'rov yuborilganda Telegram <code>FloodWait</code> xatosini qaytaradi &mdash; unda
qancha soniya kutish kerakligi ko'rsatiladi. To'g'ri yondashuv &mdash; buni <code>try/except</code>
bilan ushlab, ko'rsatilgan vaqt davomida <code>asyncio.sleep()</code> qilib, keyin qayta urinish:</p>
<pre><code>from pyrogram.errors import FloodWait
import asyncio

async def safe_iterate(client, chat_id):
    while True:
        try:
            async for msg in client.get_chat_history(chat_id, limit=5000):
                process(msg)
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)</code></pre>

<pre class="mermaid">
flowchart TB
  START["async for x in client.get_chat_history(...)"]
  START --> PAGE["Pyrogram bitta 'sahifa'ni
so'raydi (ichkarida)"]
  PAGE --> YIELD["Har bir elementni
navbat bilan qaytaradi"]
  YIELD --> MORE{"Yana sahifa bormi?"}
  MORE -->|"ha"| PAGE
  MORE -->|"yo'q"| DONE["Iteratsiya tugaydi"]
  PAGE -->|"FloodWait xatosi"| WAIT["asyncio.sleep(e.value)"]
  WAIT --> PAGE
</pre>
<p>Diagram <code>async for</code> ortida yashiringan sahifalash mexanizmini va FloodWait
uchrasa qayta urinish oqimini ko'rsatadi &mdash; kod darajasida siz bularning hech birini
qo'lda yozmaysiz, faqat oddiy for-loop ko'rasiz.</p>

<h3>Xotira bo'yicha eng ko'p uchraydigan xato</h3>
<p>Yangi boshlovchilar ko'pincha <code>results = [m async for m in get_chat_history(...)]</code>
kabi ro'yxat qurib, keyin uni qayta ishlaydi &mdash; bu katta kanallar uchun butun tarixni
xotiraga yuklashga urinishni anglatadi va xotira tugashiga olib kelishi mumkin. To'g'ri
yondashuv &mdash; har bir elementni <code>async for</code> ichida <strong>darhol</strong> qayta
ishlash (yozish, hisoblash, filtrlash), ro'yxatga yig'masdan.</p>

<h3>get_dialogs(): barcha suhbatlar ro'yxati (faqat foydalanuvchi rejimida)</h3>
<p>Yana bir Bot API'da mavjud bo'lmagan imkoniyat &mdash; <code>get_dialogs()</code> orqali
hisobingiz a'zo bo'lgan <strong>barcha</strong> shaxsiy chat, guruh va kanallar ro'yxatini
async iteratsiya qilish. Bu faqat foydalanuvchi (userbot) rejimida ma'noga ega &mdash; bot
faqat o'zi qo'shilgan chatlarni "biladi", lekin "barcha dialoglarim" degan tushunchaga ega
emas, chunki u hech qachon o'z xohishi bilan biror joyga qo'shilmagan:</p>
<pre><code>async for dialog in app.get_dialogs():
    print(dialog.chat.title or dialog.chat.first_name, dialog.unread_messages_count)</code></pre>
<p>Bu real hayotda, masalan, "500 tadan ortiq o'qilmagan xabarli barcha kanallarni arxivlash"
kabi avtomatlashtirish skriptlarida ishlatiladi.</p>""",
        "text_content_ru": """<h3>Чего нет в Bot API, но есть в MTProto: глубокая история</h3>
<p>Через Bot API боты не могут «прочитать назад» старые сообщения чата &mdash; они видят только
приходящие update. Так как Pyrogram работает на уровне MTProto, этого ограничения нет:
через <code>get_chat_history()</code> можно постранично прочитать <strong>всю (доступную)</strong>
историю любого чата <strong>назад во времени</strong> &mdash; это особенно мощно в режиме
пользователя (так как аккаунт уже «был» в этом чате).</p>

<h3>async for — стиль Pyrogram, скрывающий пагинацию</h3>
<p>Для больших списков (история, участники, диалоги) Pyrogram не заставляет вас писать отдельный
запрос «следующая страница» &mdash; вместо этого он возвращает <strong>асинхронный
генератор</strong>, и вы просто итерируетесь обычным <code>async for</code>, а Pyrogram в фоне
сам автоматически запрашивает следующие страницы:</p>
<pre><code>async for message in client.get_chat_history(chat_id, limit=1000):
    print(message.id, message.text)</code></pre>
<p><code>limit=0</code> (или вообще не указан) &mdash; означает <strong>без ограничения</strong>,
то есть вся история читается до конца. Для больших каналов это могут быть миллионы сообщений,
поэтому всегда ставьте разумный <code>limit</code> или обрабатывайте результат сразу «на лету»,
не накапливая в памяти.</p>

<h3>Перечисление участников канала/группы</h3>
<pre><code>async for member in client.get_chat_members(chat_id):
    print(member.user.id, member.user.username, member.status)</code></pre>
<p>Для больших открытых каналов (десятки тысяч участников) эта операция может занять
значительное время и упереться в flood-лимиты Telegram &mdash; особенно если часто применяется
в режиме юзербота. Параметр <code>filter=</code> позволяет ограничиться конкретным статусом
(например <code>ChatMembersFilter.ADMINISTRATORS</code>), что ускоряет работу.</p>

<h3>FloodWait: естественный сигнал rate-limit в MTProto</h3>
<p>При слишком большом числе запросов Telegram возвращает ошибку <code>FloodWait</code> &mdash;
в ней указано, сколько секунд нужно подождать. Правильный подход &mdash; поймать её через
<code>try/except</code>, подождать указанное время через <code>asyncio.sleep()</code>, а затем
повторить попытку:</p>
<pre><code>from pyrogram.errors import FloodWait
import asyncio

async def safe_iterate(client, chat_id):
    while True:
        try:
            async for msg in client.get_chat_history(chat_id, limit=5000):
                process(msg)
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)</code></pre>

<pre class="mermaid">
flowchart TB
  START["async for x in client.get_chat_history(...)"]
  START --> PAGE["Pyrogram запрашивает одну
'страницу' (внутри себя)"]
  PAGE --> YIELD["Возвращает каждый элемент
по очереди"]
  YIELD --> MORE{"Есть ещё страница?"}
  MORE -->|"да"| PAGE
  MORE -->|"нет"| DONE["Итерация завершается"]
  PAGE -->|"ошибка FloodWait"| WAIT["asyncio.sleep(e.value)"]
  WAIT --> PAGE
</pre>
<p>Диаграмма показывает скрытый за <code>async for</code> механизм пагинации и поток повторной
попытки при возникновении FloodWait &mdash; на уровне кода вы ничего из этого не пишете вручную,
видите только обычный for-loop.</p>

<h3>Самая частая ошибка с памятью</h3>
<p>Новички часто строят список вроде
<code>results = [m async for m in get_chat_history(...)]</code>, а затем обрабатывают его &mdash;
для больших каналов это означает попытку загрузить всю историю в память, что может привести к
исчерпанию памяти. Правильный подход &mdash; обрабатывать каждый элемент <strong>сразу</strong>
внутри <code>async for</code> (запись, подсчёт, фильтрация), не накапливая в списке.</p>

<h3>get_dialogs(): список всех диалогов (только в режиме пользователя)</h3>
<p>Ещё одна возможность, недоступная в Bot API &mdash; через <code>get_dialogs()</code>
асинхронно перебрать список <strong>всех</strong> личных чатов, групп и каналов, в которых
состоит ваш аккаунт. Это имеет смысл только в режиме пользователя (юзербота) &mdash; бот
«знает» только те чаты, в которые его добавили, но не имеет понятия «все мои диалоги», так как
он никогда сам никуда не вступал по собственному желанию:</p>
<pre><code>async for dialog in app.get_dialogs():
    print(dialog.chat.title or dialog.chat.first_name, dialog.unread_messages_count)</code></pre>
<p>Это используется на практике, например, в скриптах автоматизации вроде «архивировать все
каналы с более чем 500 непрочитанными сообщениями».</p>""",
        "code_content": """import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter

app = Client("history_demo")


async def count_messages_with_word(client: Client, chat_id: int, word: str, limit: int = 5000) -> int:
    \"\"\"Xotirada ro'yxat yig'masdan, har bir xabarni darhol tekshiradi.\"\"\"
    count = 0
    while True:
        try:
            async for message in client.get_chat_history(chat_id, limit=limit):
                if message.text and word.lower() in message.text.lower():
                    count += 1
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)
    return count


async def list_admins(client: Client, chat_id: int) -> list[str]:
    admins = []
    async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        admins.append(member.user.username or str(member.user.id))
    return admins


async def main():
    async with app:
        chat_id = -1001234567890
        total = await count_messages_with_word(app, chat_id, "pyrogram")
        print(f"'pyrogram' so'zi {total} marta uchradi")

        admins = await list_admins(app, chat_id)
        print("Adminlar:", admins)


if __name__ == "__main__":
    asyncio.run(main())
""",
        "code_content_ru": """import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter

app = Client("history_demo")


async def count_messages_with_word(client: Client, chat_id: int, word: str, limit: int = 5000) -> int:
    \"\"\"Не накапливает список в памяти, сразу проверяет каждое сообщение.\"\"\"
    count = 0
    while True:
        try:
            async for message in client.get_chat_history(chat_id, limit=limit):
                if message.text and word.lower() in message.text.lower():
                    count += 1
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)
    return count


async def list_admins(client: Client, chat_id: int) -> list[str]:
    admins = []
    async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        admins.append(member.user.username or str(member.user.id))
    return admins


async def main():
    async with app:
        chat_id = -1001234567890
        total = await count_messages_with_word(app, chat_id, "pyrogram")
        print(f"Слово 'pyrogram' встретилось {total} раз(а)")

        admins = await list_admins(app, chat_id)
        print("Админы:", admins)


if __name__ == "__main__":
    asyncio.run(main())
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: FloodWait'ga chidamli tarix skaneri",
            "task_title_ru": "Практика: сканер истории, устойчивый к FloodWait",
            "task_description": (
                "get_chat_history() orqali biror chatning oxirgi N (kamida 500) xabarini "
                "sahifalab o'qiydigan va ma'lum bir kalit so'z bo'yicha filtrlaydigan funksiya "
                "yozing. Natijani ro'yxatga yig'masdan, har bir xabarni darhol qayta ishlang. "
                "FloodWait xatosini try/except bilan ushlab, asyncio.sleep(e.value) orqali "
                "kutib, qayta urinish mantiqini qo'shing."
            ),
            "task_description_ru": (
                "Напишите функцию, которая через get_chat_history() постранично читает "
                "последние N (минимум 500) сообщений чата и фильтрует по ключевому слову. "
                "Обрабатывайте каждое сообщение сразу, не накапливая в списке. Добавьте логику "
                "повтора: поймайте FloodWait через try/except и подождите asyncio.sleep(e.value)."
            ),
            "task_requirements": (
                "async for ishlatilishi kerak; natija ro'yxatga to'liq yig'ilmasligi kerak "
                "(darhol qayta ishlanishi shart); FloodWait uchun try/except va sleep bo'lishi "
                "kerak."
            ),
            "task_requirements_ru": (
                "Должен использоваться async for; результат не должен полностью накапливаться "
                "в списке (обработка сразу); должны быть try/except и sleep для FloodWait."
            ),
            "task_technologies": "Pyrogram, asyncio",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: FloodWait'ga chidamli a'zolar sanagichi",
            "title_ru": "Пример: счётчик участников, устойчивый к FloodWait",
            "description": "get_chat_members() orqali a'zolarni sanaydigan, FloodWait'ni to'g'ri qayta ishlaydigan misol.",
            "description_ru": "Пример подсчёта участников через get_chat_members() с корректной обработкой FloodWait.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "member_counter.py",
                    "language": "python",
                    "code": """import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait

app = Client("member_counter_demo")


async def count_members(client: Client, chat_id: int) -> int:
    total = 0
    while True:
        try:
            async for _ in client.get_chat_members(chat_id):
                total += 1
            return total
        except FloodWait as e:
            print(f"FloodWait: {e.value} soniya kutilmoqda...")
            await asyncio.sleep(e.value)


async def main():
    async with app:
        total = await count_members(app, -1001234567890)
        print(f"Jami a'zolar: {total}")


asyncio.run(main())
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Bot API bilan asosiy farq",
                "title_ru": "Основное отличие от Bot API",
                "description": "Pyrogram get_chat_history() orqali qila oladigan, Bot API'da umuman mavjud bo'lmagan imkoniyat qaysi?",
                "description_ru": "Какая возможность доступна в Pyrogram через get_chat_history(), но отсутствует в Bot API вообще?",
                "exercise_type": "multiple_choice",
                "options": ["Yangi xabar yuborish", "Chatning eski tarixini orqaga qarab o'qish", "Foydalanuvchi profilini ko'rish", "Media fayl yuklab olish"],
                "options_ru": ["Отправка нового сообщения", "Чтение старой истории чата назад во времени", "Просмотр профиля пользователя", "Скачивание медиафайла"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Bot API faqat kelayotgan update'larni ko'radi, orqaga qaray olmaydi.",
                "hint_ru": "Bot API видит только входящие update, назад заглянуть не может.",
                "explanation": "Bot API botlar uchun faqat kelgusi update'larni taqdim etadi; MTProto orqali ishlaydigan Pyrogram esa ruxsat etilgan tarixni to'liq orqaga qarab o'qiy oladi.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Rate-limit signalini bildiruvchi xato",
                "title_ru": "Ошибка, сигнализирующая о rate-limit",
                "description": "Juda ko'p so'rov yuborilganda Telegram qaytaradigan, kutish vaqtini o'zida saqlagan xato klassi: ___",
                "description_ru": "Класс ошибки, который возвращает Telegram при слишком большом числе запросов, содержащий время ожидания: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "FloodWait",
                "hint": "Nomi 'suv toshqini kutish' ma'nosini bildiradi.",
                "hint_ru": "Название означает 'ожидание наводнения'.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Katta tarixni to'g'ri qayta ishlash tartibi",
                "title_ru": "Правильный порядок обработки большой истории",
                "description": "Katta chat tarixini xotira muammosiz qayta ishlash qadamlarini tartibga joylashtiring",
                "description_ru": "Расположите шаги правильной обработки большой истории чата без проблем с памятью",
                "exercise_type": "drag_and_drop",
                "drag_items": ["async for orqali bitta xabarni olish", "Xabarni darhol qayta ishlash (filtrlash/yozish)", "Ro'yxatga yig'masdan keyingi xabarga o'tish", "FloodWait kelsa kutib qayta urinish"],
                "drag_items_ru": ["Получение одного сообщения через async for", "Немедленная обработка сообщения (фильтрация/запись)", "Переход к следующему без накопления в списке", "При FloodWait — подождать и повторить"],
                "correct_order": ["async for orqali bitta xabarni olish", "Xabarni darhol qayta ishlash (filtrlash/yozish)", "Ro'yxatga yig'masdan keyingi xabarga o'tish", "FloodWait kelsa kutib qayta urinish"],
                "hint": "Har bir xabar kelgan zahoti qayta ishlanadi, ro'yxatga yig'ilmaydi.",
                "hint_ru": "Каждое сообщение обрабатывается сразу по получении, не накапливаясь в списке.",
                "difficulty_level": "Hard",
                "points": 8,
            },
        ],
    },
    {
        "order": 8,
        "title": "R1-Takrorlash: dual-mode Client, handlerlar, filters va sessiya xavfsizligi",
        "title_ru": "R1-Повторение: dual-mode Client, обработчики, фильтры и безопасность сессий",
        "points_reward": 18,
        "code_language": "python",
        "text_content": """<h3>Bu dars — sof takrorlash, yangi mavzu yo'q</h3>
<p>Bu qisqa takrorlash darsi ataylab yengil &mdash; yangi API yoki kontseptsiya kiritilmaydi,
faqat 1-8 darslarda o'rganilganlar amaliy loyihaga birlashtiriladi. Shuning uchun matn qisqa:
asosiy e'tibor pastdagi amaliy vazifada.</p>

<h3>Qisqacha xotira jadvali</h3>
<table>
<tr><th>Dars</th><th>Asosiy g'oya</th></tr>
<tr><td>1-2</td><td>Pyrogram MTProto ustida ishlaydi; bitta Client bot yoki userbot bo'lishi mumkin</td></tr>
<tr><td>3</td><td>@app.on_message dekoratorlari, group= va continue_propagation()</td></tr>
<tr><td>4</td><td>filters moduli, & / | / ~ bilan birlashtirish, filters.create()</td></tr>
<tr><td>5</td><td>Sessiya fayl = auth_key; workdir, in_memory, session_string xavfsizligi</td></tr>
<tr><td>6</td><td>InlineKeyboardMarkup, parse_mode, send_media_group</td></tr>
<tr><td>7</td><td>callback_query.answer() majburiy; inline_query.answer(results)</td></tr>
<tr><td>8</td><td>async for + get_chat_history/get_chat_members, FloodWait bilan ishlash</td></tr>
</table>
<p>Quyidagi amaliy vazifa aynan shu yettita bo'lakni bitta kichik, lekin to'liq ishlaydigan
botga birlashtirishni talab qiladi.</p>""",
        "text_content_ru": """<h3>Этот урок — чистое повторение, без новой темы</h3>
<p>Этот короткий урок повторения намеренно облегчён &mdash; не вводится ни новый API, ни новая
концепция, только то, что изучено в уроках 1-8, объединяется в практический проект. Поэтому
текст короткий: основное внимание в практическом задании ниже.</p>

<h3>Краткая таблица-памятка</h3>
<table>
<tr><th>Урок</th><th>Основная идея</th></tr>
<tr><td>1-2</td><td>Pyrogram работает на MTProto; один Client может быть ботом или юзерботом</td></tr>
<tr><td>3</td><td>Декораторы @app.on_message, group= и continue_propagation()</td></tr>
<tr><td>4</td><td>Модуль filters, объединение через & / | / ~, filters.create()</td></tr>
<tr><td>5</td><td>Файл сессии = auth_key; безопасность workdir, in_memory, session_string</td></tr>
<tr><td>6</td><td>InlineKeyboardMarkup, parse_mode, send_media_group</td></tr>
<tr><td>7</td><td>callback_query.answer() обязателен; inline_query.answer(results)</td></tr>
<tr><td>8</td><td>async for + get_chat_history/get_chat_members, работа с FloodWait</td></tr>
</table>
<p>Практическое задание ниже требует объединить именно эти семь частей в один небольшой, но
полностью рабочий бот.</p>""",
        "code_content": """# Takrorlash darsi — yangi kod yo'q. Amaliy vazifa (pastda) barcha
# o'rganilgan qismlarni (dual-mode, handlerlar, filters, klaviaturalar,
# callback, async iteratsiya) birlashtiradi.
""",
        "code_content_ru": """# Урок повторения — нового кода нет. Практическое задание (ниже)
# объединяет всё изученное (dual-mode, обработчики, фильтры, клавиатуры,
# callback, асинхронная итерация).
""",
        "video_url": None,
        "task": {
            "task_title": "Mini-capstone: guruh moderatori boti",
            "task_title_ru": "Мини-капстоун: бот-модератор группы",
            "task_description": (
                "1-8 darslarda o'rganilganlarni birlashtirib, kichik 'guruh moderatori' botini "
                "yozing: (1) dual-mode Client fabrikasi; (2) /stats buyrug'i "
                "get_chat_members() orqali guruhdagi jami a'zolar va adminlar sonini "
                "hisoblab, inline tugma bilan ('Batafsil') javob bersin; (3) tugma bosilganda "
                "callback_query orqali oxirgi 100 xabar ichidan eng faol 3 foydalanuvchini "
                "get_chat_history() bilan hisoblab ko'rsatsin; (4) is_admin custom filter bilan "
                "himoyalangan /warn buyrug'i (faqat adminlar uchun)."
            ),
            "task_description_ru": (
                "Объединив изученное в уроках 1-8, напишите небольшого бота-«модератора "
                "группы»: (1) фабрика dual-mode Client; (2) команда /stats через "
                "get_chat_members() считает общее число участников и админов, отвечает с "
                "inline-кнопкой («Подробнее»); (3) при нажатии кнопки через callback_query "
                "считает и показывает 3 самых активных пользователей за последние 100 "
                "сообщений через get_chat_history(); (4) команда /warn, защищённая "
                "custom-фильтром is_admin (только для админов)."
            ),
            "task_requirements": (
                "Barcha to'rtta qism ishlashi kerak; callback_query.answer() chaqirilishi shart; "
                "is_admin filters.create() orqali yozilgan bo'lishi kerak; async for "
                "ishlatilishi kerak (ro'yxatga to'liq yig'masdan)."
            ),
            "task_requirements_ru": (
                "Все четыре части должны работать; callback_query.answer() обязателен; "
                "is_admin должен быть написан через filters.create(); должен использоваться "
                "async for (без полного накопления в списке)."
            ),
            "task_technologies": "Pyrogram, asyncio",
            "task_deadline_days": 5,
        },
        "sample": {
            "title": "Namuna: mini guruh moderatori boti",
            "title_ru": "Пример: мини-бот модератор группы",
            "description": "1-8 darslardagi barcha g'oyalarni birlashtirgan qisqa, to'liq ishlaydigan bot.",
            "description_ru": "Короткий, полностью рабочий бот, объединяющий все идеи из уроков 1-8.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "moderator_bot.py",
                    "language": "python",
                    "code": """import os
from collections import Counter
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMembersFilter

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

app = Client(
    "moderator_bot" if BOT_TOKEN else "moderator_user",
    api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workdir="./sessions",
)


async def _is_admin(_, client, message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")


is_admin = filters.create(_is_admin)


@app.on_message(filters.command("stats") & filters.group)
async def stats(client, message):
    total = 0
    admins = 0
    async for member in client.get_chat_members(message.chat.id):
        total += 1
        if member.status in ("administrator", "creator"):
            admins += 1
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Batafsil", callback_data="stats:top")]])
    await message.reply_text(f"A'zolar: {total}, adminlar: {admins}", reply_markup=kb)


@app.on_callback_query(filters.regex(r"^stats:top$"))
async def top_users(client, callback_query):
    await callback_query.answer()
    counter = Counter()
    async for msg in client.get_chat_history(callback_query.message.chat.id, limit=100):
        if msg.from_user:
            counter[msg.from_user.username or str(msg.from_user.id)] += 1
    top3 = counter.most_common(3)
    text = "\\n".join(f"{name}: {count}" for name, count in top3) or "Ma'lumot yo'q"
    await callback_query.message.edit_text(f"Eng faol 3 foydalanuvchi:\\n{text}")


@app.on_message(filters.command("warn") & filters.group & is_admin)
async def warn(client, message):
    await message.reply_text("Ogohlantirish yuborildi (demo).")


app.run()
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "R1: dual-mode va filters bo'yicha bilim tekshiruvi",
                "title_ru": "R1: проверка знаний по dual-mode и filters",
                "description": "Client'ni bot rejimida ishga tushirish uchun qaysi parametr beriladi va admin-tekshiruvi uchun qaysi funksiya ishlatiladi? To'g'ri juftlikni tanlang.",
                "description_ru": "Какой параметр запускает Client в режиме бота и какая функция используется для проверки прав админа? Выберите правильную пару.",
                "exercise_type": "multiple_choice",
                "options": [
                    "bot_token va filters.create()",
                    "phone_number va filters.command()",
                    "session_string va filters.text",
                    "api_hash va filters.user()",
                ],
                "options_ru": [
                    "bot_token и filters.create()",
                    "phone_number и filters.command()",
                    "session_string и filters.text",
                    "api_hash и filters.user()",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "1-2 va 4-darslarni eslang.",
                "hint_ru": "Вспомните уроки 1-2 и 4.",
                "explanation": "bot_token bot rejimini yoqadi; filters.create() esa is_admin kabi maxsus tekshiruvlar yozish uchun ishlatiladi.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "R1: majburiy callback metodi",
                "title_ru": "R1: обязательный метод callback",
                "description": "Har qanday callback_query handlerida chaqirilishi shart bo'lgan metod: callback_query.___()",
                "description_ru": "Метод, обязательный к вызову в любом обработчике callback_query: callback_query.___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "answer",
                "hint": "7-darsni eslang.",
                "hint_ru": "Вспомните урок 7.",
                "difficulty_level": "Easy",
                "points": 5,
            },
        ],
    },
    {
        "order": 9,
        "title": "9-Plugins tizimi: katta botlarni modullarga bo'lib tashkil qilish",
        "title_ru": "9-Система plugins: организация крупных ботов через модули",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>Bitta faylning muammosi</h3>
<p>Bot kattalashgani sari <code>bot.py</code> ichida o'nlab, keyin yuzlab handler to'planadi
&mdash; fayl o'qib bo'lmas darajaga yetadi. aiogram'da bu muammo <code>Router</code>
obyektlarini alohida fayllarga bo'lib, keyin <code>dp.include_router()</code> orqali qo'lda
ulash bilan hal qilinadi. Pyrogram bu uchun <strong>built-in</strong> yechim taklif qiladi
&mdash; <code>plugins</code> parametri, u sizning qo'lingiz bilan hech qanday
<code>include</code> chaqirmasdan, papkani <em>avtomatik</em> skanerlaydi.</p>

<h3>plugins= parametri qanday ishlaydi</h3>
<pre><code>app = Client(
    "my_bot",
    api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)</code></pre>
<p><code>root="plugins"</code> &mdash; loyihangizda <code>plugins/</code> nomli papka bo'lishi
kerakligini bildiradi. <code>app.run()</code> chaqirilganda Pyrogram bu papka ichidagi
<strong>har bir</strong> <code>.py</code> faylni avtomatik import qiladi, va ular ichidagi
<code>@Client.on_message(...)</code> kabi dekoratorlangan funksiyalarni <em>o'zi</em> topib,
ishga tushirilgan <code>app</code> obyektiga bog'laydi &mdash; sizdan bironta qo'shimcha
ro'yxatga olish kodi talab qilinmaydi.</p>

<h3>Plagin fayli qanday ko'rinadi</h3>
<pre><code># plugins/greetings.py
from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def start(client: Client, message):
    await message.reply_text("Salom, bu greetings pluginidan!")</code></pre>
<pre><code># plugins/admin.py
from pyrogram import Client, filters

@Client.on_message(filters.command("ban") & filters.group)
async def ban(client: Client, message):
    await message.reply_text("Ban qilindi (admin pluginidan).")</code></pre>
<p>Muhim farq: bu yerda <code>@app.on_message</code> emas, <code>@Client.on_message</code>
(klassning o'zida, obyektida emas) ishlatiladi &mdash; chunki plugin fayli import qilinayotgan
paytda hali qaysi <code>app</code> nusxasiga bog'lanishi noma'lum, Pyrogram buni ichkarida
o'zi hal qiladi.</p>

<h3>Nega bu aiogram Router'idan ko'ra "aqlliroq" yuklash hisoblanadi</h3>
<p>aiogram'da har bir yangi Router fayli uchun asosiy faylga qo'lda import va
<code>include_router()</code> qatori qo'shish kerak &mdash; yangi fayl qo'shildi, lekin
ulanishni unutib qo'ydingiz, degan holat oson yuz beradi. Pyrogram'ning plugin tizimida esa
<code>plugins/</code> papkasiga yangi <code>.py</code> fayl qo'yishning o'zi kifoya &mdash;
keyingi ishga tushirishda u <em>avtomatik</em> topiladi va ulanadi, hech qanday markaziy
"registry" fayl yangilanishi shart emas.</p>

<h3>include/exclude bilan tanlab yuklash</h3>
<p>Ba'zida faqat ma'lum fayllarni yuklash kerak bo'ladi (masalan, test muhitida admin
plaginini o'chirib qo'yish) &mdash; <code>plugins=dict(root="plugins", exclude=["admin"])</code>
kabi yozib, ma'lum modullarni chetlab o'tish mumkin.</p>

<pre class="mermaid">
flowchart TB
  RUN["app.run()"]
  RUN --> SCAN["plugins/ papkasini skanerlaydi"]
  SCAN --> F1["plugins/greetings.py"]
  SCAN --> F2["plugins/admin.py"]
  SCAN --> F3["plugins/shop.py"]
  F1 --> H1["@Client.on_message ichidagi
funksiyalar topiladi"]
  F2 --> H2["@Client.on_message ichidagi
funksiyalar topiladi"]
  F3 --> H3["@Client.on_message ichidagi
funksiyalar topiladi"]
  H1 --> BOUND["Barchasi ishga tushirilgan
app obyektiga bog'lanadi"]
  H2 --> BOUND
  H3 --> BOUND
</pre>
<p>Diagram shuni ko'rsatadiki, <code>plugins/</code> papkasiga qancha fayl qo'shsangiz ham,
markaziy kodni o'zgartirmasdan, ular avtomatik topilib ishga tushiriladi.</p>

<h3>Ichki papkalar va o'lchov</h3>
<p><code>root</code> papkasi ichida yana ichki papkalar (masalan
<code>plugins/shop/catalog.py</code>, <code>plugins/shop/checkout.py</code>) bo'lishi
mumkin &mdash; Pyrogram rekursiv ravishda barcha ichki <code>.py</code> fayllarni ham topadi.
Bu katta loyihalarda plaginlarni o'z ichida yana mavzu bo'yicha (masalan "shop", "admin",
"analytics") papkalarga bo'lish imkonini beradi, aiogram'dagi ko'p darajali Router
ierarxiyasiga o'xshash natija beradi, lekin bironta ham qo'lda ulash kodisiz.</p>

<h3>Diqqat: nom to'qnashuvidan saqlaning</h3>
<p>Ikki xil plugin faylida bir xil nomli funksiya bo'lishi muammo emas (ular alohida modul
nom-maydonida yashaydi), lekin bitta update turiga (masalan ikkalasi ham
<code>filters.command("start")</code>) mos keladigan handlerlarni ikki xil faylga yozib
qo'yish &mdash; ikkalasi ham ishga tushishi mumkin, chunki ular odatiy holatda turli
"group"larda emas, bir xil standart guruhda ro'yxatga olinadi. Amaliy qoida: bitta buyruq
uchun bitta plugin faylida bitta handler &mdash; loyiha kattalashganda bu intizom o'zini
oqlaydi.</p>""",
        "text_content_ru": """<h3>Проблема одного файла</h3>
<p>По мере роста бота в <code>bot.py</code> накапливаются десятки, потом сотни обработчиков
&mdash; файл становится нечитаемым. В aiogram эта проблема решается разбиением объектов
<code>Router</code> по отдельным файлам, а затем ручным подключением через
<code>dp.include_router()</code>. Pyrogram предлагает для этого <strong>встроенное</strong>
решение &mdash; параметр <code>plugins</code>, который без единого вызова <code>include</code>
с вашей стороны <em>автоматически</em> сканирует папку.</p>

<h3>Как работает параметр plugins=</h3>
<pre><code>app = Client(
    "my_bot",
    api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)</code></pre>
<p><code>root="plugins"</code> означает, что в вашем проекте должна быть папка с именем
<code>plugins/</code>. При вызове <code>app.run()</code> Pyrogram автоматически импортирует
<strong>каждый</strong> <code>.py</code> файл внутри этой папки, и <em>сам</em> находит внутри
них функции, декорированные как <code>@Client.on_message(...)</code>, привязывая их к уже
запущенному объекту <code>app</code> &mdash; от вас не требуется никакого дополнительного кода
регистрации.</p>

<h3>Как выглядит файл плагина</h3>
<pre><code># plugins/greetings.py
from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def start(client: Client, message):
    await message.reply_text("Привет, это из плагина greetings!")</code></pre>
<pre><code># plugins/admin.py
from pyrogram import Client, filters

@Client.on_message(filters.command("ban") & filters.group)
async def ban(client: Client, message):
    await message.reply_text("Забанен (из плагина admin).")</code></pre>
<p>Важное отличие: здесь используется не <code>@app.on_message</code>, а
<code>@Client.on_message</code> (на самом классе, а не на объекте) &mdash; потому что в момент
импорта файла плагина ещё неизвестно, к какому именно экземпляру <code>app</code> он будет
привязан, Pyrogram решает это внутри себя.</p>

<h3>Почему это «умнее» подхода с Router из aiogram</h3>
<p>В aiogram для каждого нового файла Router нужно вручную добавлять импорт и строку
<code>include_router()</code> в основной файл &mdash; легко забыть подключить новый файл. В
системе плагинов Pyrogram достаточно просто положить новый <code>.py</code> файл в папку
<code>plugins/</code> &mdash; при следующем запуске он <em>автоматически</em> найдётся и
подключится, никакой центральный файл «реестра» обновлять не нужно.</p>

<h3>Выборочная загрузка через include/exclude</h3>
<p>Иногда нужно загружать только определённые файлы (например, отключить плагин admin в
тестовом окружении) &mdash; можно написать
<code>plugins=dict(root="plugins", exclude=["admin"])</code>, чтобы исключить конкретные
модули.</p>

<pre class="mermaid">
flowchart TB
  RUN["app.run()"]
  RUN --> SCAN["сканирует папку plugins/"]
  SCAN --> F1["plugins/greetings.py"]
  SCAN --> F2["plugins/admin.py"]
  SCAN --> F3["plugins/shop.py"]
  F1 --> H1["находятся функции внутри
@Client.on_message"]
  F2 --> H2["находятся функции внутри
@Client.on_message"]
  F3 --> H3["находятся функции внутри
@Client.on_message"]
  H1 --> BOUND["Все привязываются к
запущенному объекту app"]
  H2 --> BOUND
  H3 --> BOUND
</pre>
<p>Диаграмма показывает, что сколько бы файлов вы ни добавили в папку <code>plugins/</code>,
они автоматически находятся и подключаются без изменения центрального кода.</p>

<h3>Вложенные папки и масштаб</h3>
<p>Внутри папки <code>root</code> могут быть и вложенные папки (например
<code>plugins/shop/catalog.py</code>, <code>plugins/shop/checkout.py</code>) &mdash; Pyrogram
рекурсивно находит все вложенные <code>.py</code> файлы. Это позволяет в крупных проектах
разбивать плагины ещё и по тематическим папкам (например «shop», «admin», «analytics»),
давая результат, похожий на многоуровневую иерархию Router в aiogram, но вообще без кода
ручного подключения.</p>

<h3>Внимание: избегайте конфликта имён</h3>
<p>Одинаковое имя функции в двух разных файлах плагинов не проблема (они живут в разных
пространствах имён модулей), но написание обработчиков, соответствующих одному и тому же
update (например оба на <code>filters.command("start")</code>) в двух разных файлах &mdash;
могут сработать оба, так как по умолчанию они регистрируются не в разных «group», а в одной
и той же стандартной группе. Практическое правило: одна команда — один обработчик в одном
файле плагина &mdash; по мере роста проекта эта дисциплина себя окупает.</p>""",
        "code_content": """# Loyiha tuzilishi:
#
# my_bot/
#   bot.py
#   plugins/
#     __init__.py   (bo'sh bo'lishi mumkin)
#     greetings.py
#     admin.py
#     shop.py

# --- bot.py ---
import os
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

app = Client(
    "plugin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",
    plugins=dict(root="plugins"),  # plugins/ papkasi avtomatik skanerlanadi
)

if __name__ == "__main__":
    app.run()


# --- plugins/greetings.py ---
# from pyrogram import Client, filters
#
# @Client.on_message(filters.command("start"))
# async def start(client, message):
#     await message.reply_text("Salom, bu greetings pluginidan!")


# --- plugins/admin.py ---
# from pyrogram import Client, filters
#
# async def _is_admin(_, client, message):
#     member = await client.get_chat_member(message.chat.id, message.from_user.id)
#     return member.status in ("administrator", "creator")
#
# is_admin = filters.create(_is_admin)
#
# @Client.on_message(filters.command("ban") & filters.group & is_admin)
# async def ban(client, message):
#     await message.reply_text("Ban qilindi (admin pluginidan).")


# --- plugins/shop.py ---
# from pyrogram import Client, filters
#
# @Client.on_message(filters.command("shop"))
# async def shop(client, message):
#     await message.reply_text("Do'kon katalogi (shop pluginidan).")
""",
        "code_content_ru": """# Структура проекта:
#
# my_bot/
#   bot.py
#   plugins/
#     __init__.py   (может быть пустым)
#     greetings.py
#     admin.py
#     shop.py

# --- bot.py ---
import os
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

app = Client(
    "plugin_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="./sessions",
    plugins=dict(root="plugins"),  # папка plugins/ сканируется автоматически
)

if __name__ == "__main__":
    app.run()


# --- plugins/greetings.py ---
# from pyrogram import Client, filters
#
# @Client.on_message(filters.command("start"))
# async def start(client, message):
#     await message.reply_text("Привет, это из плагина greetings!")


# --- plugins/admin.py ---
# from pyrogram import Client, filters
#
# async def _is_admin(_, client, message):
#     member = await client.get_chat_member(message.chat.id, message.from_user.id)
#     return member.status in ("administrator", "creator")
#
# is_admin = filters.create(_is_admin)
#
# @Client.on_message(filters.command("ban") & filters.group & is_admin)
# async def ban(client, message):
#     await message.reply_text("Забанен (из плагина admin).")


# --- plugins/shop.py ---
# from pyrogram import Client, filters
#
# @Client.on_message(filters.command("shop"))
# async def shop(client, message):
#     await message.reply_text("Каталог магазина (из плагина shop).")
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: botni 3 ta pluginga bo'ling",
            "task_title_ru": "Практика: разбейте бота на 3 плагина",
            "task_description": (
                "Mavjud botingizni (yoki yangisini) plugins/ papkasiga ega qilib qayta "
                "tashkil qiling: greetings.py (/start, /help), admin.py (is_admin filter bilan "
                "himoyalangan /ban), shop.py (/shop mahsulotlar ro'yxati). bot.py faylida "
                "faqat Client(plugins=dict(root='plugins')) bo'lsin, hech qanday handler kodi "
                "bo'lmasin."
            ),
            "task_description_ru": (
                "Реорганизуйте существующего (или нового) бота, добавив папку plugins/: "
                "greetings.py (/start, /help), admin.py (/ban, защищённый фильтром is_admin), "
                "shop.py (/shop список товаров). В bot.py должен быть только "
                "Client(plugins=dict(root='plugins')), без кода обработчиков."
            ),
            "task_requirements": (
                "Kamida 3 ta alohida plugin fayli bo'lishi kerak; bot.py handler kodi "
                "saqlamasligi kerak; @Client.on_message (obyekt emas, klass) ishlatilishi "
                "kerak."
            ),
            "task_requirements_ru": (
                "Должно быть минимум 3 отдельных файла плагинов; bot.py не должен содержать "
                "код обработчиков; должен использоваться @Client.on_message (класс, а не "
                "объект)."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: plugins bilan tashkil qilingan bot skeleti",
            "title_ru": "Пример: скелет бота, организованного через plugins",
            "description": "bot.py + plugins/ papkasi bilan to'liq ishlaydigan minimal tuzilma.",
            "description_ru": "Полностью рабочая минимальная структура с bot.py + папкой plugins/.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "bot.py",
                    "language": "python",
                    "code": """import os
from pyrogram import Client

app = Client(
    "plugin_skeleton",
    api_id=int(os.environ["TG_API_ID"]),
    api_hash=os.environ["TG_API_HASH"],
    bot_token=os.environ["TG_BOT_TOKEN"],
    plugins=dict(root="plugins"),
)

app.run()
""",
                },
                {
                    "filename": "plugins/greetings.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters


@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Salom! Men plugins orqali tashkil qilinganman.")
""",
                },
            ],
        },
        "exercises": [
            {
                "title": "plugins= parametri qanday papkani skanerlaydi",
                "title_ru": "Какую папку сканирует параметр plugins=",
                "description": "Client(plugins=dict(root=\"plugins\")) berilganda, qaysi papka avtomatik skanerlanadi?",
                "description_ru": "Если задан Client(plugins=dict(root=\"plugins\")), какая папка сканируется автоматически?",
                "exercise_type": "multiple_choice",
                "options": ["sessions/", "root parametrida ko'rsatilgan papka", "handlers/", "Har doim /plugins (mutlaq yo'l)"],
                "options_ru": ["sessions/", "Папка, указанная в параметре root", "handlers/", "Всегда /plugins (абсолютный путь)"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "root= parametrining qiymatiga e'tibor bering.",
                "hint_ru": "Обратите внимание на значение параметра root=.",
                "explanation": "root parametri qaysi papka nomi skanerlanishini bildiradi (bu misolda 'plugins'), mutlaq yo'l emas, loyiha ichidagi nisbiy nom.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Plugin faylida ishlatiladigan dekorator",
                "title_ru": "Декоратор, используемый в файле плагина",
                "description": "Plugin fayli ichida (app obyekti mavjud bo'lmagani uchun) @app.on_message o'rniga @___.on_message ishlatiladi",
                "description_ru": "Внутри файла плагина (так как объекта app нет) вместо @app.on_message используется @___.on_message",
                "exercise_type": "fill_in_blank",
                "correct_answers": "Client",
                "hint": "Bu klassning o'zi, uning nusxasi (obyekti) emas.",
                "hint_ru": "Это сам класс, а не его экземпляр (объект).",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Plugin qo'shish jarayonini tartibga joylashtiring",
                "title_ru": "Расположите процесс добавления плагина по порядку",
                "description": "Yangi funksiyani mavjud botga plugins tizimi orqali qo'shish qadamlarini joylashtiring",
                "description_ru": "Расположите шаги добавления новой функции в существующего бота через систему plugins",
                "exercise_type": "drag_and_drop",
                "drag_items": ["plugins/ papkasiga yangi .py fayl yaratish", "Fayl ichida @Client.on_message bilan handler yozish", "app.run() qayta ishga tushirilganda avtomatik topiladi", "bot.py'da hech qanday qo'shimcha import kerak emas"],
                "drag_items_ru": ["Создать новый .py файл в папке plugins/", "Написать обработчик через @Client.on_message внутри файла", "При перезапуске app.run() автоматически находится", "В bot.py не нужен дополнительный импорт"],
                "correct_order": ["plugins/ papkasiga yangi .py fayl yaratish", "Fayl ichida @Client.on_message bilan handler yozish", "app.run() qayta ishga tushirilganda avtomatik topiladi", "bot.py'da hech qanday qo'shimcha import kerak emas"],
                "hint": "Fayl yaratiladi, ichiga handler yoziladi, keyin avtomatik topiladi.",
                "hint_ru": "Файл создаётся, внутри пишется обработчик, затем находится автоматически.",
                "difficulty_level": "Medium",
                "points": 7,
            },
        ],
    },
    {
        "order": 10,
        "title": "10-Xom MTProto chaqiruvlari: yuqori darajali API yetmasa invoke()",
        "title_ru": "10-Сырые вызовы MTProto: invoke(), когда высокоуровневого API не хватает",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>Yuqori darajali API — bu faqat qulaylik qatlami</h3>
<p>Kursimiz davomida ishlatgan <code>send_message()</code>, <code>get_chat_history()</code>,
<code>get_chat_members()</code> kabi metodlar &mdash; qulaylik uchun yozilgan "wrapper"lar.
Ularning har biri ichida haqiqatda MTProto'ning xom funksiyalaridan (masalan
<code>messages.SendMessage</code>, <code>messages.GetHistory</code>) foydalanadi. Pyrogram
bu xom funksiyalarning barchasini <code>pyrogram.raw.functions</code> ostida avtomatik
generatsiya qilingan Python klasslari sifatida taqdim etadi &mdash; va ularni
<code>client.invoke()</code> orqali to'g'ridan-to'g'ri chaqirish mumkin.</p>

<h3>Nega bu kerak bo'lishi mumkin</h3>
<p>Yuqori darajali API Telegram MTProto'sining <em>eng ko'p ishlatiladigan</em> qismini
qamrab oladi, lekin hammasini emas &mdash; ba'zi kam ishlatiladigan yoki yangi qo'shilgan
imkoniyatlar (masalan, kanal statistikasi, ba'zi maxsus admin huquqlari, eksperimental
funksiyalar) hali qulay wrapper'ga ega bo'lmasligi mumkin. Bunday holatlarda kutish o'rniga
xom funksiyani to'g'ridan-to'g'ri chaqirasiz.</p>

<h3>invoke() qanday ishlatiladi</h3>
<pre><code>from pyrogram.raw import functions, types

async def get_full_channel_info(client, channel_username: str):
    peer = await client.resolve_peer(channel_username)
    result = await client.invoke(
        functions.channels.GetFullChannel(channel=peer)
    )
    return result.full_chat</code></pre>
<p>Diqqat qiling: <code>chat_id</code> yoki <code>@username</code> emas, balki
<code>resolve_peer()</code> orqali olingan maxsus <code>InputPeer</code> obyekti kerak &mdash;
xom MTProto funksiyalari yuqori darajali API kabi "qulay" identifikatorlarni qabul qilmaydi,
faqat protokolning o'z ichki turlarini.</p>

<h3>pyrogram.raw ichida nima bor</h3>
<table>
<tr><th>Modul</th><th>Mazmuni</th></tr>
<tr><td><code>pyrogram.raw.functions</code></td><td>Serverga yuboriladigan barcha MTProto so'rovlari (RPC chaqiruvlari)</td></tr>
<tr><td><code>pyrogram.raw.types</code></td><td>So'rov/javoblarda ishlatiladigan barcha ma'lumot turlari</td></tr>
</table>
<p>Bu ikkalasi ham <strong>qo'lda yozilmagan</strong> &mdash; Telegram'ning rasmiy TL-schema
(Type Language) fayllaridan avtomatik generatsiya qilingan, shuning uchun har doim rasmiy
protokol bilan sinxron holatda.</p>

<pre class="mermaid">
flowchart TB
  H["Yuqori darajali API
(send_message, get_chat_history...)"]
  H --> W["Wrapper metodlar"]
  W --> R["client.invoke(functions.XYZ(...))"]
  R --> RAW["pyrogram.raw.functions
va pyrogram.raw.types"]
  RAW --> MT["MTProto tarmoq qatlami"]
  DIRECT["Sizning kodingiz
(wrapper yo'q bo'lsa)"] -.->|"to'g'ridan-to'g'ri invoke()"| R
</pre>
<p>Diagram shuni ko'rsatadiki, yuqori darajali metodlar ham, sizning to'g'ridan-to'g'ri
<code>invoke()</code> chaqiruvingiz ham, oxir-oqibat bir xil <code>pyrogram.raw</code>
qatlamiga tushadi &mdash; farq faqat qanchalik "qulay qadam"dan o'tishingizda.</p>

<h3>Ehtiyot choralari</h3>
<p>Xom funksiyalarni chaqirishda xatoni ushlash uchun ham <code>pyrogram.errors</code>
moduli ishlatiladi (masalan <code>ChannelPrivate</code>, <code>UsernameNotOccupied</code>).
Bu qatlam beqaror emas, lekin hujjatlari yuqori darajali API'ga qaraganda kamroq &mdash;
Telegram'ning rasmiy <code>core.telegram.org/methods</code> sahifasi va Pyrogram'ning
o'z <code>pyrogram.raw</code> API ma'lumotnomasi asosiy manba hisoblanadi.</p>

<h3>TL-schema "layer" versiyasi haqida</h3>
<p>MTProto protokoli vaqt o'tishi bilan yangilanadi &mdash; Telegram TL-schema'ga yangi
funksiya/tur qo'shadi yoki mavjudlarini o'zgartiradi, va bu o'zgarishlar "layer" raqami bilan
versiyalanadi. Pyrogram kutubxonasi ma'lum bir layer versiyasiga mos <code>pyrogram.raw</code>
kodini o'zida saqlaydi &mdash; shuning uchun kutubxonani yangilash ba'zan yangi xom
funksiyalarni ochadi yoki eskilarining imzosini o'zgartiradi. Bu <code>pyrogram.raw</code>
qatlamidan foydalanuvchi kod uchun amaliy xulosa: xom funksiyaga tayangan kodni versiya
yangilanishlarida qayta tekshirib turish kerak, aksincha yuqori darajali API (send_message va
h.k.) ancha barqaror interfeys taqdim etadi.</p>

<h3>Telethon bilan qiyoslash</h3>
<p>Telethon ham xuddi shunday xom qatlamga ega &mdash; u yerda <code>client(functions...)</code>
chaqiruvi Pyrogram'ning <code>client.invoke(functions...)</code>siga deyarli bevosita mos
keladi, chunki ikkalasi ham bir xil ochiq TL-schema'dan avtomatik generatsiya qilinadi.
Boshqacha aytganda, agar Telethon'da qandaydir xom funksiya nomini bilsangiz, xuddi shu nom
(faqat chaqiruv sintaksisi biroz farqli) Pyrogram'da ham mavjud bo'ladi &mdash; bu ikkala
kutubxona MTProto darajasida haqiqatda umumiy asosga ega ekanini yana bir bor tasdiqlaydi.</p>""",
        "text_content_ru": """<h3>Высокоуровневый API — это лишь слой удобства</h3>
<p>Методы вроде <code>send_message()</code>, <code>get_chat_history()</code>,
<code>get_chat_members()</code>, которые мы использовали на протяжении курса &mdash; это
удобные «обёртки». Каждая из них внутри на самом деле использует «сырые» функции MTProto
(например <code>messages.SendMessage</code>, <code>messages.GetHistory</code>). Pyrogram
предоставляет все эти сырые функции как автоматически сгенерированные Python-классы под
<code>pyrogram.raw.functions</code> &mdash; и их можно вызывать напрямую через
<code>client.invoke()</code>.</p>

<h3>Зачем это может понадобиться</h3>
<p>Высокоуровневый API покрывает <em>наиболее часто используемую</em> часть MTProto Telegram,
но не всё &mdash; некоторые редко используемые или недавно добавленные возможности
(например, статистика канала, некоторые особые права админа, экспериментальные функции) могут
ещё не иметь удобной обёртки. В таких случаях, вместо ожидания, вы вызываете сырую функцию
напрямую.</p>

<h3>Как используется invoke()</h3>
<pre><code>from pyrogram.raw import functions, types

async def get_full_channel_info(client, channel_username: str):
    peer = await client.resolve_peer(channel_username)
    result = await client.invoke(
        functions.channels.GetFullChannel(channel=peer)
    )
    return result.full_chat</code></pre>
<p>Обратите внимание: нужен не <code>chat_id</code> или <code>@username</code>, а специальный
объект <code>InputPeer</code>, полученный через <code>resolve_peer()</code> &mdash; сырые
функции MTProto не принимают «удобные» идентификаторы высокоуровневого API, только
собственные внутренние типы протокола.</p>

<h3>Что находится внутри pyrogram.raw</h3>
<table>
<tr><th>Модуль</th><th>Содержимое</th></tr>
<tr><td><code>pyrogram.raw.functions</code></td><td>Все MTProto-запросы (RPC-вызовы), отправляемые на сервер</td></tr>
<tr><td><code>pyrogram.raw.types</code></td><td>Все типы данных, используемые в запросах/ответах</td></tr>
</table>
<p>Оба они <strong>не написаны вручную</strong> &mdash; сгенерированы автоматически из
официальных TL-схема (Type Language) файлов Telegram, поэтому всегда синхронизированы с
официальным протоколом.</p>

<pre class="mermaid">
flowchart TB
  H["Высокоуровневый API
(send_message, get_chat_history...)"]
  H --> W["Методы-обёртки"]
  W --> R["client.invoke(functions.XYZ(...))"]
  R --> RAW["pyrogram.raw.functions
и pyrogram.raw.types"]
  RAW --> MT["Сетевой уровень MTProto"]
  DIRECT["Ваш код
(если обёртки нет)"] -.->|"прямой вызов invoke()"| R
</pre>
<p>Диаграмма показывает, что и высокоуровневые методы, и ваш прямой вызов
<code>invoke()</code> в итоге попадают в один и тот же слой <code>pyrogram.raw</code> &mdash;
разница лишь в том, через сколько «удобных ступеней» вы проходите.</p>

<h3>Меры предосторожности</h3>
<p>Для отлова ошибок при вызове сырых функций тоже используется модуль
<code>pyrogram.errors</code> (например <code>ChannelPrivate</code>,
<code>UsernameNotOccupied</code>). Этот слой не нестабилен, но документирован скромнее, чем
высокоуровневый API &mdash; основным источником служат официальная страница Telegram
<code>core.telegram.org/methods</code> и собственная справка Pyrogram по
<code>pyrogram.raw</code> API.</p>

<h3>О версии TL-схемы ("layer")</h3>
<p>Протокол MTProto со временем обновляется &mdash; Telegram добавляет в TL-схему новые
функции/типы или изменяет существующие, и эти изменения версионируются номером «layer».
Библиотека Pyrogram хранит у себя код <code>pyrogram.raw</code>, соответствующий
определённой версии layer &mdash; поэтому обновление библиотеки иногда открывает новые сырые
функции или меняет сигнатуру старых. Практический вывод для кода, использующего слой
<code>pyrogram.raw</code>: код, опирающийся на сырую функцию, стоит перепроверять при
обновлениях версий, тогда как высокоуровневый API (send_message и т.д.) предоставляет
значительно более стабильный интерфейс.</p>

<h3>Сравнение с Telethon</h3>
<p>У Telethon есть точно такой же сырой слой &mdash; там вызов <code>client(functions...)</code>
почти напрямую соответствует <code>client.invoke(functions...)</code> в Pyrogram, так как
оба генерируются автоматически из одной и той же открытой TL-схемы. Другими словами, если вы
знаете имя какой-то сырой функции в Telethon, то же самое имя (только синтаксис вызова слегка
отличается) будет и в Pyrogram &mdash; это лишний раз подтверждает, что обе библиотеки
реально имеют общую основу на уровне MTProto.</p>""",
        "code_content": """import asyncio
from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import RPCError, UsernameNotOccupied, ChannelPrivate

app = Client("raw_invoke_demo")


async def get_channel_full_stats(client: Client, channel_username: str) -> dict | None:
    \"\"\"Yuqori darajali API'da hali qulay wrapper bo'lmagan ma'lumotni
    to'g'ridan-to'g'ri xom MTProto funksiyasi orqali olish.\"\"\"
    try:
        peer = await client.resolve_peer(channel_username)
    except UsernameNotOccupied:
        print(f"@{channel_username} nomli kanal/foydalanuvchi topilmadi.")
        return None

    try:
        result = await client.invoke(functions.channels.GetFullChannel(channel=peer))
    except ChannelPrivate:
        print("Kanal yopiq — a'zo bo'lmagan hisob uchun ma'lumot mavjud emas.")
        return None
    except RPCError as e:
        print(f"Kutilmagan MTProto xatosi: {e}")
        return None

    full_chat = result.full_chat
    return {
        "participants_count": getattr(full_chat, "participants_count", None),
        "about": getattr(full_chat, "about", None),
        "linked_chat_id": getattr(full_chat, "linked_chat_id", None),
    }


async def get_history_raw(client: Client, channel_username: str, limit: int = 20):
    \"\"\"Xuddi shu narsani get_chat_history() bilan solishtirish uchun —
    yuqori darajali metod ichida chaqiradigan xom funksiyaning o'zi.\"\"\"
    peer = await client.resolve_peer(channel_username)
    return await client.invoke(
        functions.messages.GetHistory(
            peer=peer, offset_id=0, offset_date=0, add_offset=0,
            limit=limit, max_id=0, min_id=0, hash=0,
        )
    )


async def main():
    async with app:
        stats = await get_channel_full_stats(app, "durov")
        print("To'liq statistika:", stats)

        raw_history = await get_history_raw(app, "durov", limit=5)
        print("Xom tarix javobidagi xabarlar soni:", len(raw_history.messages))


if __name__ == "__main__":
    asyncio.run(main())
""",
        "code_content_ru": """import asyncio
from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import RPCError, UsernameNotOccupied, ChannelPrivate

app = Client("raw_invoke_demo")


async def get_channel_full_stats(client: Client, channel_username: str) -> dict | None:
    \"\"\"Получение данных, для которых ещё нет удобной обёртки в
    высокоуровневом API, напрямую через сырую функцию MTProto.\"\"\"
    try:
        peer = await client.resolve_peer(channel_username)
    except UsernameNotOccupied:
        print(f"Канал/пользователь @{channel_username} не найден.")
        return None

    try:
        result = await client.invoke(functions.channels.GetFullChannel(channel=peer))
    except ChannelPrivate:
        print("Канал закрыт — данные недоступны для аккаунта, не являющегося участником.")
        return None
    except RPCError as e:
        print(f"Неожиданная ошибка MTProto: {e}")
        return None

    full_chat = result.full_chat
    return {
        "participants_count": getattr(full_chat, "participants_count", None),
        "about": getattr(full_chat, "about", None),
        "linked_chat_id": getattr(full_chat, "linked_chat_id", None),
    }


async def get_history_raw(client: Client, channel_username: str, limit: int = 20):
    \"\"\"Для сравнения с get_chat_history() — сама сырая функция, которую
    вызывает высокоуровневый метод внутри себя.\"\"\"
    peer = await client.resolve_peer(channel_username)
    return await client.invoke(
        functions.messages.GetHistory(
            peer=peer, offset_id=0, offset_date=0, add_offset=0,
            limit=limit, max_id=0, min_id=0, hash=0,
        )
    )


async def main():
    async with app:
        stats = await get_channel_full_stats(app, "durov")
        print("Полная статистика:", stats)

        raw_history = await get_history_raw(app, "durov", limit=5)
        print("Число сообщений в сыром ответе истории:", len(raw_history.messages))


if __name__ == "__main__":
    asyncio.run(main())
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: invoke() orqali kanal ma'lumotini olish",
            "task_title_ru": "Практика: получение данных канала через invoke()",
            "task_description": (
                "resolve_peer() va client.invoke(functions.channels.GetFullChannel(...)) "
                "orqali biror ochiq kanalning to'liq ma'lumotini (a'zolar soni, tavsif) olib, "
                "konsolga chiqaring. Xatolarni pyrogram.errors orqali ushlab, foydalanuvchiga "
                "tushunarli xabar bering (masalan kanal topilmasa)."
            ),
            "task_description_ru": (
                "Через resolve_peer() и client.invoke(functions.channels.GetFullChannel(...)) "
                "получите полную информацию (число участников, описание) о каком-либо открытом "
                "канале и выведите в консоль. Обработайте ошибки через pyrogram.errors, дав "
                "понятное сообщение (например, если канал не найден)."
            ),
            "task_requirements": (
                "client.invoke() to'g'ridan-to'g'ri chaqirilishi kerak (wrapper metod emas); "
                "resolve_peer() ishlatilishi kerak; xatolar pyrogram.errors orqali ushlanishi "
                "kerak."
            ),
            "task_requirements_ru": (
                "Должен вызываться client.invoke() напрямую (не метод-обёртка); должен "
                "использоваться resolve_peer(); ошибки должны ловиться через pyrogram.errors."
            ),
            "task_technologies": "Pyrogram",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: invoke() bilan xom MTProto so'rovi",
            "title_ru": "Пример: сырой запрос MTProto через invoke()",
            "description": "resolve_peer() + client.invoke() orqali yuqori darajali API'da yo'q ma'lumotni olish namunasi.",
            "description_ru": "Пример получения данных, отсутствующих в высокоуровневом API, через resolve_peer() + client.invoke().",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "raw_channel_info.py",
                    "language": "python",
                    "code": """from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import RPCError

app = Client("raw_info_demo")


async def safe_full_channel(client: Client, username: str):
    try:
        peer = await client.resolve_peer(username)
        result = await client.invoke(functions.channels.GetFullChannel(channel=peer))
        return result.full_chat
    except RPCError as e:
        print(f"Xato: {e}")
        return None


async def main():
    async with app:
        info = await safe_full_channel(app, "durov")
        if info:
            print("A'zolar:", info.participants_count)


import asyncio
asyncio.run(main())
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "Xom MTProto funksiyalari qayerda joylashgan",
                "title_ru": "Где расположены сырые функции MTProto",
                "description": "Barcha xom MTProto RPC chaqiruvlari qaysi modul ostida joylashgan?",
                "description_ru": "Под каким модулем расположены все сырые RPC-вызовы MTProto?",
                "exercise_type": "multiple_choice",
                "options": ["pyrogram.types", "pyrogram.raw.functions", "pyrogram.filters", "pyrogram.enums"],
                "options_ru": ["pyrogram.types", "pyrogram.raw.functions", "pyrogram.filters", "pyrogram.enums"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Nomi to'g'ridan-to'g'ri 'xom' so'zini o'zida saqlaydi.",
                "hint_ru": "В названии прямо содержится слово 'сырой' (raw).",
                "explanation": "pyrogram.raw.functions ichida serverga yuboriladigan barcha xom MTProto so'rovlari, pyrogram.raw.types ichida esa ma'lumot turlari joylashgan.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Xom funksiyani chaqirish metodi",
                "title_ru": "Метод вызова сырой функции",
                "description": "pyrogram.raw.functions ichidagi biror funksiyani to'g'ridan-to'g'ri chaqirish uchun client.___() ishlatiladi",
                "description_ru": "Для прямого вызова функции из pyrogram.raw.functions используется client.___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "invoke",
                "hint": "Ingliz tilida 'chaqirish, ishga tushirish' ma'nosini bildiradi.",
                "hint_ru": "Английское слово, означающее 'вызвать'.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "invoke() chaqirishdan oldingi qadam",
                "title_ru": "Шаг перед вызовом invoke()",
                "description": "chat_id yoki @username o'rniga, xom funksiyaga uzatish uchun avval qanday obyekt olinishi kerak? O'z so'zlaringiz bilan tushuntiring va uni olish metodini ko'rsating.",
                "description_ru": "Вместо chat_id или @username, какой объект нужно сначала получить для передачи в сырую функцию? Объясните своими словами и укажите метод его получения.",
                "exercise_type": "text_input",
                "expected_answer": "InputPeer obyekti kerak, u client.resolve_peer(chat_id_yoki_username) metodi orqali olinadi — xom MTProto funksiyalari faqat shu maxsus turdagi identifikatorni qabul qiladi.",
                "hint": "Metod nomi 'resolve' so'zidan boshlanadi.",
                "hint_ru": "Название метода начинается со слова 'resolve'.",
                "difficulty_level": "Hard",
                "points": 8,
            },
        ],
    },
    {
        "order": 11,
        "title": "11-TgCrypto va unumdorlik: nima uchun tez ishlaydi va qanday o'lchash",
        "title_ru": "11-TgCrypto и производительность: почему быстро работает и как измерить",
        "points_reward": 15,
        "code_language": "python",
        "text_content": """<h3>MTProto nega shifrlashga muhtoj</h3>
<p>Bot API'da shifrlash HTTPS (TLS) qatlamiga yuklangan &mdash; kutubxonaning o'zi hech narsa
shifrlamaydi. Pyrogram esa MTProto protokolining o'zini amalga oshirgani uchun, har bir
so'rov/javobni <strong>AES-256-IGE</strong> algoritmi bilan o'zi shifrlashi va deshifrlashi
kerak &mdash; bu esa har bir update, har bir yuborilgan xabar uchun protsessorda amalga
oshiriladigan qo'shimcha ish.</p>

<h3>TgCrypto: sof Python'dan tezroq</h3>
<p>Standart holatda Pyrogram AES-256-IGE'ni sof Python (yoki mavjud bo'lsa
<code>pycryptodome</code>) orqali bajarishi mumkin, lekin buning uchun maxsus &mdash;
<strong>TgCrypto</strong> &mdash; kutubxonasi mavjud, u C tilida yozilgan va Python'ga
kengaytma (C extension) sifatida ulanadi:</p>
<pre><code>pip install tgcrypto</code></pre>
<p>O'rnatilgandan so'ng hech qanday qo'shimcha sozlash kerak emas &mdash; Pyrogram uni avtomatik
aniqlaydi va ishlatadi (agar mavjud bo'lmasa, sekinroq zaxira yo'lga o'tadi). Rasmiy
hujjatlarga ko'ra farq sezilarli: yuqori trafikli botlar (ko'p update, katta fayllar) uchun
TgCrypto shifrlash/deshifrlashni bir necha barobar tezlashtiradi, chunki C darajasidagi kod
Python bayt-kodidan ancha tez ishlaydi.</p>

<h3>Qachon bu ahamiyatli, qachon emas</h3>
<table>
<tr><th>Holat</th><th>TgCrypto ta'siri</th></tr>
<tr><td>Kam trafikli shaxsiy bot (kuniga bir necha o'nlab xabar)</td><td>Sezilarli farq yo'q</td></tr>
<tr><td>Ko'p update qabul qiluvchi katta guruh/kanal boti</td><td>Sezilarli tezlashuv</td></tr>
<tr><td>Katta fayllarni tez-tez yuklab olish/yuborish</td><td>Sezilarli tezlashuv (har bir chunk shifrlanadi)</td></tr>
<tr><td>Bir nechta bot-farm (10+ Client bir jarayonda)</td><td>Umumiy protsessor yukini kamaytiradi</td></tr>
</table>

<h3>Boshqa unumdorlik omillari: workers va parallelism</h3>
<p>TgCryptodan tashqari, <code>Client(..., workers=N)</code> parametri &mdash; handlerlar
ishlaydigan thread pool o'lchamini belgilaydi. Standart qiymat ko'p holatlar uchun yetarli,
lekin sinxron (bloklovchi) kod ko'p ishlatiladigan handlerlar bo'lsa, workers sonini oshirish
handlerlarning bir-birini "kutib turishi"ni kamaytiradi. Asosiy qoida esa &mdash; handlerlar
ichida <strong>hech qachon</strong> sinxron bloklovchi chaqiruv (masalan oddiy
<code>requests.get()</code>) ishlatmaslik, buning o'rniga <code>httpx.AsyncClient</code> kabi
async muqobilini ishlatish &mdash; aks holda bitta sekin handler butun event loop'ni
to'xtatib qo'yishi mumkin.</p>

<pre class="mermaid">
flowchart LR
  MSG["Kelgan/yuboriladigan
har bir MTProto paket"]
  MSG --> ENC{"TgCrypto o'rnatilganmi?"}
  ENC -->|"ha"| FAST["C-kengaytma orqali
tez AES-256-IGE"]
  ENC -->|"yo'q"| SLOW["Sof Python/pycryptodome
orqali sekinroq"]
  FAST --> NET["Tarmoq orqali yuboriladi"]
  SLOW --> NET
</pre>
<p>Diagram TgCrypto o'rnatilgan-o'rnatilmaganiga qarab bir xil shifrlash operatsiyasi ikki
mutlaqo boshqa tezlikda bajarilishini ko'rsatadi &mdash; kod darajasida hech qanday farq yo'q,
faqat <code>pip install tgcrypto</code> qilinganmi yoki yo'qmi.</p>

<h3>O'lchash: taxmin qilmang, o'lchang</h3>
<p>Har qanday "tezlashtirish" da'vosidan oldin haqiqiy botingizda o'lchang &mdash; masalan,
bir xil vazifani (1000 ta xabarni get_chat_history bilan o'qish) TgCrypto o'rnatilgan va
o'rnatilmagan holatda <code>time.perf_counter()</code> bilan solishtiring. Production
muhitida esa <code>logging</code> orqali har bir handler necha millisoniya ishlaganini
yozib borish &mdash; qaysi handler botning umumiy javob vaqtini "yeb qo'yayotganini" aniq
ko'rsatadi.</p>

<h3>Parallel yuklab olish/yuborish: max_concurrent_transmissions</h3>
<p>Katta fayllar bilan ishlaydigan botlar uchun yana bir sozlama muhim &mdash;
<code>Client(..., max_concurrent_transmissions=N)</code>. Bu parametr bir vaqtning o'zida
nechta fayl yuklab olish/yuborish operatsiyasi parallel bajarilishini belgilaydi. Standart
qiymat kichik botlar uchun yetarli, lekin ko'p foydalanuvchi bir vaqtda fayl yuklayotgan katta
botlarda uni oshirish umumiy o'tkazish qobiliyatini (throughput) yaxshilaydi &mdash; albatta,
serverning tarmoq va disk imkoniyatlari chegarasida.</p>

<h3>Xulosa: unumdorlik &mdash; o'lchash, keyin optimallashtirish</h3>
<p>TgCrypto, workers va max_concurrent_transmissions &mdash; barchasi "bepul" tezlashtirish
emas, balki resurslarni (protsessor, tarmoq, disk) qanday taqsimlashni belgilaydigan
parametrlar. Har birini o'zgartirishdan oldin joriy holatni o'lchang, keyin o'zgartiring, va
yana o'lchang &mdash; aks holda "optimallashtirish" aslida hech narsani yaxshilamagan, hatto
yomonlashtirgan bo'lishi mumkin.</p>""",
        "text_content_ru": """<h3>Почему MTProto нуждается в шифровании</h3>
<p>В Bot API шифрование возложено на слой HTTPS (TLS) &mdash; сама библиотека ничего не
шифрует. Pyrogram же, реализуя сам протокол MTProto, обязан сам шифровать и расшифровывать
каждый запрос/ответ алгоритмом <strong>AES-256-IGE</strong> &mdash; это дополнительная
работа для процессора на каждый update, каждое отправленное сообщение.</p>

<h3>TgCrypto: быстрее чистого Python</h3>
<p>По умолчанию Pyrogram может выполнять AES-256-IGE на чистом Python (или, если доступен,
через <code>pycryptodome</code>), но для этого есть специальная библиотека &mdash;
<strong>TgCrypto</strong> &mdash; написанная на C и подключаемая к Python как расширение
(C extension):</p>
<pre><code>pip install tgcrypto</code></pre>
<p>После установки никаких дополнительных настроек не требуется &mdash; Pyrogram определяет
её автоматически и использует (если её нет, переходит на более медленный резервный путь). По
официальной документации разница ощутима: для ботов с высоким трафиком (много update,
большие файлы) TgCrypto ускоряет шифрование/расшифровку в несколько раз, так как код на
уровне C работает намного быстрее байт-кода Python.</p>

<h3>Когда это важно, а когда нет</h3>
<table>
<tr><th>Ситуация</th><th>Эффект TgCrypto</th></tr>
<tr><td>Малотрафиковый личный бот (несколько десятков сообщений в день)</td><td>Заметной разницы нет</td></tr>
<tr><td>Бот большой группы/канала с большим числом update</td><td>Заметное ускорение</td></tr>
<tr><td>Частая загрузка/отправка больших файлов</td><td>Заметное ускорение (шифруется каждый chunk)</td></tr>
<tr><td>Несколько ботов-фермы (10+ Client в одном процессе)</td><td>Снижает общую нагрузку на процессор</td></tr>
</table>

<h3>Другие факторы производительности: workers и параллелизм</h3>
<p>Помимо TgCrypto, параметр <code>Client(..., workers=N)</code> определяет размер пула
потоков, в котором работают обработчики. Значение по умолчанию достаточно для большинства
случаев, но если часто используются синхронные (блокирующие) обработчики, увеличение числа
workers снижает «ожидание друг друга» между обработчиками. Основное правило &mdash;
<strong>никогда</strong> не использовать внутри обработчиков синхронные блокирующие вызовы
(например обычный <code>requests.get()</code>), а вместо этого использовать асинхронную
альтернативу вроде <code>httpx.AsyncClient</code> &mdash; иначе один медленный обработчик
может остановить весь event loop.</p>

<pre class="mermaid">
flowchart LR
  MSG["Каждый входящий/исходящий
пакет MTProto"]
  MSG --> ENC{"Установлен ли TgCrypto?"}
  ENC -->|"да"| FAST["Быстрый AES-256-IGE
через C-расширение"]
  ENC -->|"нет"| SLOW["Медленнее через
чистый Python/pycryptodome"]
  FAST --> NET["Отправляется по сети"]
  SLOW --> NET
</pre>
<p>Диаграмма показывает, что одна и та же операция шифрования выполняется с совершенно разной
скоростью в зависимости от наличия TgCrypto &mdash; на уровне кода разницы никакой, только
установлен ли <code>pip install tgcrypto</code>.</p>

<h3>Измерение: не гадайте, измеряйте</h3>
<p>Прежде чем верить любому заявлению об «ускорении», измерьте на своём реальном боте &mdash;
например, сравните одну и ту же задачу (чтение 1000 сообщений через get_chat_history) с
установленным и без установленного TgCrypto, используя <code>time.perf_counter()</code>. А в
продакшене через <code>logging</code> записывайте, сколько миллисекунд выполняется каждый
обработчик &mdash; это точно покажет, какой обработчик «съедает» общее время отклика бота.</p>

<h3>Параллельная загрузка/выгрузка: max_concurrent_transmissions</h3>
<p>Для ботов, работающих с большими файлами, важна ещё одна настройка &mdash;
<code>Client(..., max_concurrent_transmissions=N)</code>. Этот параметр определяет, сколько
операций загрузки/выгрузки файлов выполняется параллельно одновременно. Значение по
умолчанию достаточно для небольших ботов, но в крупных ботах, где много пользователей
одновременно загружают файлы, его увеличение улучшает общую пропускную способность
(throughput) &mdash; конечно, в пределах возможностей сети и диска сервера.</p>

<h3>Вывод: производительность — сначала измерение, потом оптимизация</h3>
<p>TgCrypto, workers и max_concurrent_transmissions &mdash; это не «бесплатное» ускорение, а
параметры, определяющие, как распределяются ресурсы (процессор, сеть, диск). Перед
изменением каждого из них измерьте текущее состояние, затем измените, и снова измерьте
&mdash; иначе «оптимизация» может на деле ничего не улучшить, а то и ухудшить ситуацию.</p>""",
        "code_content": """import time
import asyncio
from pyrogram import Client

app = Client("perf_demo")


async def benchmark_history_read(client: Client, chat_id: int, limit: int = 500) -> float:
    \"\"\"1000 xabarni o'qish uchun ketgan vaqtni o'lchaydi — TgCrypto
    o'rnatilgan/o'rnatilmaganini solishtirish uchun ishlatiladi.\"\"\"
    start = time.perf_counter()
    count = 0
    async for _ in client.get_chat_history(chat_id, limit=limit):
        count += 1
    elapsed = time.perf_counter() - start
    print(f"{count} ta xabar {elapsed:.2f} soniyada o'qildi")
    return elapsed


def is_tgcrypto_active() -> bool:
    \"\"\"TgCrypto o'rnatilganini tekshirish — sozlash kerak emas, Pyrogram
    o'zi avtomatik aniqlaydi, lekin diagnostika uchun foydali.\"\"\"
    try:
        import tgcrypto  # noqa: F401
        return True
    except ImportError:
        return False


async def main():
    print("TgCrypto faol:", is_tgcrypto_active())
    async with app:
        await benchmark_history_read(app, -1001234567890)


if __name__ == "__main__":
    asyncio.run(main())
""",
        "code_content_ru": """import time
import asyncio
from pyrogram import Client

app = Client("perf_demo")


async def benchmark_history_read(client: Client, chat_id: int, limit: int = 500) -> float:
    \"\"\"Измеряет время, затраченное на чтение сообщений — используется
    для сравнения с установленным/без установленного TgCrypto.\"\"\"
    start = time.perf_counter()
    count = 0
    async for _ in client.get_chat_history(chat_id, limit=limit):
        count += 1
    elapsed = time.perf_counter() - start
    print(f"{count} сообщений прочитано за {elapsed:.2f} секунд")
    return elapsed


def is_tgcrypto_active() -> bool:
    \"\"\"Проверка установлен ли TgCrypto — настраивать не нужно, Pyrogram
    сам определяет автоматически, но полезно для диагностики.\"\"\"
    try:
        import tgcrypto  # noqa: F401
        return True
    except ImportError:
        return False


async def main():
    print("TgCrypto активен:", is_tgcrypto_active())
    async with app:
        await benchmark_history_read(app, -1001234567890)


if __name__ == "__main__":
    asyncio.run(main())
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: TgCrypto ta'sirini o'lchang",
            "task_title_ru": "Практика: измерьте эффект TgCrypto",
            "task_description": (
                "is_tgcrypto_active() funksiyasini yozing. benchmark_history_read() orqali "
                "biror chatning kamida 300 xabarini o'qish vaqtini o'lchang. TgCrypto "
                "o'rnatilgan va (vaqtincha pip uninstall qilingan) o'rnatilmagan holatlarda "
                "natijalarni solishtirib, qisqa xulosa yozing."
            ),
            "task_description_ru": (
                "Напишите функцию is_tgcrypto_active(). Измерьте через "
                "benchmark_history_read() время чтения минимум 300 сообщений какого-либо "
                "чата. Сравните результаты с установленным и (временно удалённым через pip "
                "uninstall) TgCrypto, напишите краткий вывод."
            ),
            "task_requirements": (
                "time.perf_counter() ishlatilishi kerak; ikkala holat (bor/yo'q) uchun "
                "natijalar solishtirilgan bo'lishi kerak; xulosa yozma shaklda bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Должен использоваться time.perf_counter(); результаты для обоих случаев "
                "(есть/нет) должны быть сравнены; вывод должен быть в письменном виде."
            ),
            "task_technologies": "Pyrogram, TgCrypto",
            "task_deadline_days": 3,
        },
        "sample": {
            "title": "Namuna: TgCrypto tekshiruvi va benchmark",
            "title_ru": "Пример: проверка TgCrypto и бенчмарк",
            "description": "TgCrypto faolligini tekshirish va oddiy vaqt o'lchash namunasi.",
            "description_ru": "Пример проверки активности TgCrypto и простого измерения времени.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "perf_check.py",
                    "language": "python",
                    "code": """import time


def is_tgcrypto_active() -> bool:
    try:
        import tgcrypto  # noqa: F401
        return True
    except ImportError:
        return False


def fake_encrypt_benchmark(iterations: int = 100_000) -> float:
    \"\"\"Demo maqsadida oddiy vaqt o'lchash namunasi (haqiqiy shifrlash
    emas) — printsipni ko'rsatish uchun.\"\"\"
    start = time.perf_counter()
    total = sum(i * i for i in range(iterations))
    return time.perf_counter() - start


if __name__ == "__main__":
    print("TgCrypto:", is_tgcrypto_active())
    print("Vaqt:", fake_encrypt_benchmark())
""",
                }
            ],
        },
        "exercises": [
            {
                "title": "TgCrypto qanday texnologiya",
                "title_ru": "Какая технология лежит в основе TgCrypto",
                "description": "TgCrypto qaysi tilda yozilgan va Python'ga qanday ulanadi?",
                "description_ru": "На каком языке написан TgCrypto и как он подключается к Python?",
                "exercise_type": "multiple_choice",
                "options": ["Sof Python, hech qanday farq yo'q", "C tilida, C extension sifatida", "Rust, FFI orqali", "JavaScript, Node ko'prigi orqali"],
                "options_ru": ["Чистый Python, разницы нет", "На C, как C extension", "Rust, через FFI", "JavaScript, через мост Node"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Nomi 'tg' + 'crypto', lekin tezlik uchun past darajali til ishlatiladi.",
                "hint_ru": "Название 'tg' + 'crypto', но для скорости используется низкоуровневый язык.",
                "explanation": "TgCrypto C tilida yozilgan va Python'ga C extension sifatida ulanadi, shuning uchun sof Python'dan sezilarli tezroq ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "TgCrypto ishlatadigan shifrlash algoritmi",
                "title_ru": "Алгоритм шифрования, используемый TgCrypto",
                "description": "MTProto (va TgCrypto) ishlatadigan shifrlash algoritmi: AES-256-___",
                "description_ru": "Алгоритм шифрования, используемый MTProto (и TgCrypto): AES-256-___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "IGE",
                "hint": "Uch harfli qisqartma, 'Infinite Garble Extension' rejimi.",
                "hint_ru": "Трёхбуквенная аббревиатура, режим 'Infinite Garble Extension'.",
                "difficulty_level": "Hard",
                "points": 7,
            },
            {
                "title": "Handlerlarda taqiqlangan amaliyot",
                "title_ru": "Запрещённая практика в обработчиках",
                "description": "Handler ichida umuman ishlatilmasligi kerak bo'lgan narsalarni tartibga joylashtiring: avval eng xavfli (butun event loop'ni to'xtatuvchi), keyin nisbatan xavfsizroq",
                "description_ru": "Расположите по порядку то, чего следует избегать в обработчиках: сначала самое опасное (останавливающее весь event loop), затем менее опасное",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Sinxron requests.get() chaqirish (butun event loop bloklanadi)", "Juda katta workers= qiymatini o'ylamasdan oshirish"],
                "drag_items_ru": ["Синхронный вызов requests.get() (блокирует весь event loop)", "Бездумное увеличение слишком большого значения workers="],
                "correct_order": ["Sinxron requests.get() chaqirish (butun event loop bloklanadi)", "Juda katta workers= qiymatini o'ylamasdan oshirish"],
                "hint": "Butun event loop'ni to'xtatib qo'yadigan xato eng og'iri.",
                "hint_ru": "Самая тяжёлая ошибка — та, что останавливает весь event loop.",
                "difficulty_level": "Medium",
                "points": 6,
            },
        ],
    },
    {
        "order": 12,
        "title": "12-Pyrogram bot/userbot'ni xavfsiz deploy qilish",
        "title_ru": "12-Безопасный деплой Pyrogram-бота/юзербота",
        "points_reward": 16,
        "code_language": "python",
        "text_content": """<h3>48-kursdagi webhook deploydan farq</h3>
<p>48-kursda aiogram botini webhook orqali (Telegram bot API serverga xabar yuboradi) deploy
qilgansiz. Pyrogram esa doimiy TCP ulanish orqali ishlaydi (long-lived connection, MTProto
o'zi ichkarida "polling"ka o'xshash mexanizmni boshqaradi) &mdash; shuning uchun bu yerda
webhook konsepsiyasi umuman yo'q. Deploy qilish uchun kerak bo'lgani &mdash; jarayonning
uzluksiz ishlab turishini ta'minlaydigan process manager.</p>

<h3>Process manager: systemd yoki Docker + restart siyosati</h3>
<pre><code># /etc/systemd/system/pyrogram-bot.service
[Unit]
Description=Pyrogram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/pyrogram-bot
ExecStart=/opt/pyrogram-bot/venv/bin/python bot.py
Restart=on-failure
RestartSec=5
EnvironmentFile=/opt/pyrogram-bot/.env

[Install]
WantedBy=multi-user.target</code></pre>
<p><code>Restart=on-failure</code> &mdash; jarayon kutilmagan sabab bilan yiqilsa (masalan
tarmoq uzilishi), systemd uni avtomatik qayta ishga tushiradi. <code>EnvironmentFile</code>
orqali <code>api_id</code>/<code>api_hash</code>/<code>bot_token</code> muhit
o'zgaruvchilaridan o'qiladi, hech qachon kodga yozilmaydi.</p>

<h3>Session fayllarni deploy paytida saqlab qolish</h3>
<p>Har bir yangi deploy'da (masalan Docker konteynerini qayta qurishda) <code>workdir</code>
papkasi <strong>yo'qolib ketmasligi</strong> kerak &mdash; aks holda bot har safar qaytadan
avtorizatsiyadan o'tishga majbur bo'ladi (bot uchun kamroq muammo, foydalanuvchi rejimi uchun
esa har safar SMS kod kerak bo'ladi). Docker'da bu &mdash; named volume orqali
<code>workdir</code>ni konteynerdan tashqariga chiqarish:</p>
<pre><code># docker-compose.yml
services:
  bot:
    build: .
    volumes:
      - sessions_data:/app/sessions   # session fayllar konteyner qayta qurilganda ham qoladi
    env_file: .env
    restart: unless-stopped

volumes:
  sessions_data:</code></pre>

<h3>Graceful shutdown: xabar yozish o'rtasida to'xtamaslik</h3>
<p>Deploy paytida jarayon to'xtatilganda, hozir bajarilayotgan handler yarim yo'lda
kesilmasligi kerak. Pyrogram'ning <code>app.stop()</code> metodi &mdash; faol
so'rovlar tugashini kutib, keyin ulanishni yopadi. <code>SIGTERM</code> signalini to'g'ri
ushlab, <code>await app.stop()</code>ni chaqiruvchi yakuniy blok yozish &mdash; production
uchun zaruriy amaliyot.</p>

<pre class="mermaid">
flowchart TB
  DEPLOY["Yangi versiya deploy qilinadi"]
  DEPLOY --> SIGTERM["systemd/Docker SIGTERM yuboradi"]
  SIGTERM --> DRAIN["Joriy handlerlar tugashini kutish"]
  DRAIN --> STOP["await app.stop()"]
  STOP --> NEW["Yangi jarayon workdir'dagi
mavjud sessiyadan ishga tushadi"]
  NEW --> READY["Bot qayta login SO'RALMASDAN
ishlay boshlaydi"]
</pre>
<p>Diagram xavfsiz deployning to'liq zanjirini ko'rsatadi: signal &rarr; graceful to'xtash
&rarr; sessiya saqlanib qolgani tufayli qayta login talab qilinmasdan qayta ishga tushish.</p>

<h3>Monitoring: bot ishlab turganini qanday bilamiz</h3>
<p>Doimiy ulanish rejimida (webhook'dan farqli o'laroq, tashqi HTTP endpoint yo'q) bot
"tirik"ligini tekshirishning oddiy usuli &mdash; alohida yengil health-check jarayoni yoki
oddiy fayl-asosli signal: handler har muvaffaqiyatli update qayta ishlanganda
<code>/tmp/bot_heartbeat</code> faylining vaqt belgisini yangilaydi, va tashqi monitoring
(masalan systemd timer yoki cron) bu fayl necha daqiqadan beri yangilanmaganini tekshiradi.
Agar juda uzoq vaqt yangilanmasa &mdash; jarayon "osilib qolgan" (masalan tarmoq muammosi
tufayli) deb hisoblab, uni majburan qayta ishga tushirish mumkin.</p>

<h3>Log'larni tozalash: maxfiy ma'lumot chiqib ketmasligi</h3>
<p>Xato yuz berganda, ba'zi kutubxonalar butun so'rov/javob obyektini logga chiqarishi mumkin
&mdash; bu tasodifan <code>session_string</code> yoki <code>bot_token</code>ni log fayliga
yozib qo'yishi mumkin. Production'da xato loglashda har doim maxsus formatter yoki filtr
ishlatib, bunday maydonlarni <code>***REDACTED***</code> bilan almashtirish yaxshi amaliyot
hisoblanadi &mdash; log fayllari ko'pincha kod bazasidan ko'ra kamroq ehtiyotkorlik bilan
saqlanadi (masalan uchinchi tomon log-agregatorlariga yuboriladi).</p>

<h3>Deploy oldidan xavfsizlik nazorat ro'yxati</h3>
<ul>
<li>workdir/session fayllar persistent volume/diskda, .gitignore va Docker'da .dockerignore ichida</li>
<li>Barcha maxfiy qiymatlar (api_id/api_hash/bot_token/session_string) faqat muhit o'zgaruvchilarida</li>
<li>Restart siyosati (systemd yoki Docker restart) sozlangan</li>
<li>Log'larga hech qachon session_string yoki to'liq xatoning ichidagi maxfiy ma'lumot chiqmasligi tekshirilgan</li>
<li>Userbot rejimida &mdash; Telegram Settings &gt; Devices orqali faol seanslar davriy tekshiriladi</li>
<li>Heartbeat/health-check mexanizmi jarayon "osilib qolishi"ni aniqlash uchun sozlangan</li>
</ul>""",
        "text_content_ru": """<h3>Отличие от деплоя через webhook в курсе 48</h3>
<p>В курсе 48 вы деплоили бота aiogram через webhook (сервер Bot API Telegram сам отправляет
сообщение). Pyrogram же работает через постоянное TCP-соединение (long-lived connection,
сам MTProto внутри управляет механизмом, похожим на polling) &mdash; поэтому концепции
webhook здесь вообще нет. Для деплоя нужен процесс-менеджер, обеспечивающий непрерывную
работу процесса.</p>

<h3>Процесс-менеджер: systemd или Docker + политика перезапуска</h3>
<pre><code># /etc/systemd/system/pyrogram-bot.service
[Unit]
Description=Pyrogram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/pyrogram-bot
ExecStart=/opt/pyrogram-bot/venv/bin/python bot.py
Restart=on-failure
RestartSec=5
EnvironmentFile=/opt/pyrogram-bot/.env

[Install]
WantedBy=multi-user.target</code></pre>
<p><code>Restart=on-failure</code> &mdash; если процесс упадёт по неожиданной причине
(например обрыв сети), systemd автоматически перезапустит его. Через
<code>EnvironmentFile</code> <code>api_id</code>/<code>api_hash</code>/<code>bot_token</code>
читаются из переменных окружения, никогда не записываясь в код.</p>

<h3>Сохранение файлов сессии при деплое</h3>
<p>При каждом новом деплое (например, при пересборке Docker-контейнера) папка
<code>workdir</code> <strong>не должна теряться</strong> &mdash; иначе бот будет вынужден
каждый раз заново проходить авторизацию (для бота проблема меньше, а для режима пользователя
каждый раз нужен будет SMS-код). В Docker это достигается через именованный volume,
выносящий <code>workdir</code> за пределы контейнера:</p>
<pre><code># docker-compose.yml
services:
  bot:
    build: .
    volumes:
      - sessions_data:/app/sessions   # файлы сессий сохраняются и при пересборке контейнера
    env_file: .env
    restart: unless-stopped

volumes:
  sessions_data:</code></pre>

<h3>Graceful shutdown: не прерывать написание сообщения на середине</h3>
<p>При остановке процесса во время деплоя, выполняющийся в данный момент обработчик не должен
быть прерван на полпути. Метод <code>app.stop()</code> в Pyrogram &mdash; дожидается
завершения активных запросов, затем закрывает соединение. Правильная обработка сигнала
<code>SIGTERM</code> с финальным блоком, вызывающим <code>await app.stop()</code> &mdash;
необходимая практика для продакшена.</p>

<pre class="mermaid">
flowchart TB
  DEPLOY["Деплоится новая версия"]
  DEPLOY --> SIGTERM["systemd/Docker отправляет SIGTERM"]
  SIGTERM --> DRAIN["Ожидание завершения текущих обработчиков"]
  DRAIN --> STOP["await app.stop()"]
  STOP --> NEW["Новый процесс запускается из
существующей сессии в workdir"]
  NEW --> READY["Бот начинает работать
БЕЗ повторного входа"]
</pre>
<p>Диаграмма показывает полную цепочку безопасного деплоя: сигнал &rarr; graceful остановка
&rarr; повторный запуск без необходимости повторного входа благодаря сохранённой сессии.</p>

<h3>Мониторинг: как узнать, что бот работает</h3>
<p>В режиме постоянного соединения (в отличие от webhook, здесь нет внешнего HTTP-эндпоинта)
простой способ проверки «живости» бота &mdash; отдельный лёгкий health-check процесс или
простой файловый сигнал: обработчик при каждой успешной обработке update обновляет метку
времени файла <code>/tmp/bot_heartbeat</code>, а внешний мониторинг (например systemd timer
или cron) проверяет, сколько минут этот файл не обновлялся. Если слишком долго не обновлялся
&mdash; считаем процесс «зависшим» (например из-за сетевой проблемы) и принудительно
перезапускаем.</p>

<h3>Очистка логов: секретные данные не должны утекать</h3>
<p>При возникновении ошибки некоторые библиотеки могут вывести в лог весь объект
запроса/ответа целиком &mdash; это может случайно записать <code>session_string</code> или
<code>bot_token</code> в файл лога. В продакшене хорошей практикой считается всегда
использовать специальный форматтер или фильтр при логировании ошибок, заменяющий такие поля
на <code>***REDACTED***</code> &mdash; файлы логов часто хранятся с меньшей осторожностью, чем
кодовая база (например, отправляются во внешние лог-агрегаторы).</p>

<h3>Чек-лист безопасности перед деплоем</h3>
<ul>
<li>Файлы workdir/session на persistent volume/диске, в .gitignore и в .dockerignore для Docker</li>
<li>Все секретные значения (api_id/api_hash/bot_token/session_string) только в переменных окружения</li>
<li>Настроена политика перезапуска (systemd или Docker restart)</li>
<li>Проверено, что в логи никогда не попадают session_string или секретные данные внутри полной ошибки</li>
<li>В режиме юзербота — периодически проверяются активные сеансы через Telegram Settings &gt; Devices</li>
<li>Настроен механизм heartbeat/health-check для обнаружения «зависания» процесса</li>
</ul>""",
        "code_content": """import asyncio
import signal
import logging
import time
import re
from pathlib import Path
from pyrogram import Client

_SECRET_PATTERN = re.compile(r"(session_string|bot_token)=[^\\s,)]+", re.IGNORECASE)


class RedactSecretsFilter(logging.Filter):
    \"\"\"Log yozuvlaridan tasodifan tushib qolgan maxfiy qiymatlarni
    ***REDACTED*** bilan almashtiradi — production'da har doim yoqilishi
    kerak (deploy darsining log tozalash bo'limiga qarang).\"\"\"

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _SECRET_PATTERN.sub(r"\\1=***REDACTED***", str(record.msg))
        return True


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyrogram_bot")
logger.addFilter(RedactSecretsFilter())

app = Client(
    "prod_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="/app/sessions",  # persistent volume orqali saqlanadi
)

_shutdown_event = asyncio.Event()
_HEARTBEAT_PATH = Path("/tmp/bot_heartbeat")


def _handle_sigterm(*_args):
    logger.info("SIGTERM qabul qilindi — graceful shutdown boshlanmoqda")
    _shutdown_event.set()


async def _heartbeat_loop():
    \"\"\"Har 30 soniyada faylni yangilaydi — tashqi monitoring shu faylning
    yangilanish vaqtiga qarab jarayon 'tirik'ligini aniqlaydi.\"\"\"
    while not _shutdown_event.is_set():
        _HEARTBEAT_PATH.write_text(str(time.time()))
        await asyncio.sleep(30)


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _handle_sigterm)

    await app.start()
    logger.info("Bot ishga tushdi")
    heartbeat_task = asyncio.create_task(_heartbeat_loop())

    await _shutdown_event.wait()  # SIGTERM kelguncha kutadi

    logger.info("Faol so'rovlar tugashi kutilmoqda...")
    heartbeat_task.cancel()
    await app.stop()
    logger.info("Bot to'liq to'xtadi")


if __name__ == "__main__":
    asyncio.run(main())
""",
        "code_content_ru": """import asyncio
import signal
import logging
import time
import re
from pathlib import Path
from pyrogram import Client

_SECRET_PATTERN = re.compile(r"(session_string|bot_token)=[^\\s,)]+", re.IGNORECASE)


class RedactSecretsFilter(logging.Filter):
    \"\"\"Заменяет случайно попавшие в лог секретные значения на
    ***REDACTED*** — в продакшене должен быть включён всегда (см. раздел
    урока о деплое про очистку логов).\"\"\"

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _SECRET_PATTERN.sub(r"\\1=***REDACTED***", str(record.msg))
        return True


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyrogram_bot")
logger.addFilter(RedactSecretsFilter())

app = Client(
    "prod_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="/app/sessions",  # сохраняется через persistent volume
)

_shutdown_event = asyncio.Event()
_HEARTBEAT_PATH = Path("/tmp/bot_heartbeat")


def _handle_sigterm(*_args):
    logger.info("Получен SIGTERM — начинается graceful shutdown")
    _shutdown_event.set()


async def _heartbeat_loop():
    \"\"\"Обновляет файл каждые 30 секунд — внешний мониторинг по времени
    обновления этого файла определяет, что процесс 'жив'.\"\"\"
    while not _shutdown_event.is_set():
        _HEARTBEAT_PATH.write_text(str(time.time()))
        await asyncio.sleep(30)


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _handle_sigterm)

    await app.start()
    logger.info("Бот запущен")
    heartbeat_task = asyncio.create_task(_heartbeat_loop())

    await _shutdown_event.wait()  # ждёт SIGTERM

    logger.info("Ожидание завершения активных запросов...")
    heartbeat_task.cancel()
    await app.stop()
    logger.info("Бот полностью остановлен")


if __name__ == "__main__":
    asyncio.run(main())
""",
        "video_url": None,
        "task": {
            "task_title": "Amaliy: graceful shutdown va persistent session bilan deploy",
            "task_title_ru": "Практика: деплой с graceful shutdown и persistent-сессией",
            "task_description": (
                "Botingiz uchun systemd service fayli (yoki Dockerfile + docker-compose.yml, "
                "tanlovingizga ko'ra) yozing: Restart siyosati sozlangan, .env orqali maxfiy "
                "qiymatlar o'qiladigan, workdir persistent joyga (Docker'da named volume) "
                "yo'naltirilgan bo'lsin. Bot kodiga SIGTERM'ni ushlaydigan va app.stop()ni "
                "chaqiradigan graceful shutdown mantiqini qo'shing."
            ),
            "task_description_ru": (
                "Напишите файл systemd service для вашего бота (или Dockerfile + "
                "docker-compose.yml, на выбор): настроена политика перезапуска, секреты "
                "читаются через .env, workdir направлен в persistent-хранилище (в Docker — "
                "named volume). Добавьте в код бота логику graceful shutdown, ловящую SIGTERM "
                "и вызывающую app.stop()."
            ),
            "task_requirements": (
                "Restart siyosati (on-failure yoki unless-stopped) ko'rsatilgan bo'lishi "
                "kerak; workdir persistent bo'lishi kerak; SIGTERM handler va app.stop() "
                "chaqiruvi kod ichida bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Должна быть указана политика перезапуска (on-failure или unless-stopped); "
                "workdir должен быть persistent; обработчик SIGTERM и вызов app.stop() должны "
                "быть в коде."
            ),
            "task_technologies": "Pyrogram, systemd yoki Docker",
            "task_deadline_days": 4,
        },
        "sample": {
            "title": "Namuna: systemd service va graceful shutdown",
            "title_ru": "Пример: systemd service и graceful shutdown",
            "description": "Restart siyosati, persistent workdir va SIGTERM'ni to'g'ri ushlaydigan to'liq namuna.",
            "description_ru": "Полный пример с политикой перезапуска, persistent workdir и корректной обработкой SIGTERM.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "pyrogram-bot.service",
                    "language": "ini",
                    "code": """[Unit]
Description=Pyrogram Bot (production)
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/pyrogram-bot
ExecStart=/opt/pyrogram-bot/venv/bin/python bot.py
Restart=on-failure
RestartSec=5
EnvironmentFile=/opt/pyrogram-bot/.env

[Install]
WantedBy=multi-user.target
""",
                },
                {
                    "filename": "bot.py",
                    "language": "python",
                    "code": """import asyncio
import signal
from pyrogram import Client

app = Client("prod", workdir="/opt/pyrogram-bot/sessions")
_stop = asyncio.Event()


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _stop.set)
    await app.start()
    await _stop.wait()
    await app.stop()


asyncio.run(main())
""",
                },
            ],
        },
        "exercises": [
            {
                "title": "Pyrogram deploy uslubi Bot API'dan qanday farq qiladi",
                "title_ru": "Чем стиль деплоя Pyrogram отличается от Bot API",
                "description": "Pyrogram uchun webhook konsepsiyasi umuman qo'llanilmaydi, chunki u qanday ulanish turidan foydalanadi?",
                "description_ru": "Для Pyrogram концепция webhook вообще не применяется, потому что он использует какой тип соединения?",
                "exercise_type": "multiple_choice",
                "options": ["Qisqa muddatli HTTP so'rovlari", "Doimiy TCP ulanish (MTProto)", "WebSocket orqali push", "GraphQL subscription"],
                "options_ru": ["Кратковременные HTTP-запросы", "Постоянное TCP-соединение (MTProto)", "Push через WebSocket", "GraphQL subscription"],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "MTProto doimiy ulanish o'rnatadi, HTTP kabi so'rov-javob emas.",
                "hint_ru": "MTProto устанавливает постоянное соединение, а не запрос-ответ как HTTP.",
                "explanation": "Pyrogram doimiy TCP ulanish orqali ishlaydi, shuning uchun webhook (Telegram serveridan HTTP so'rov kutish) konsepsiyasi bu yerda umuman qo'llanilmaydi.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Faol so'rovlar tugashini kutib ulanishni yopuvchi metod",
                "title_ru": "Метод, закрывающий соединение после завершения активных запросов",
                "description": "Graceful shutdown uchun SIGTERM ushlangandan keyin chaqiriladigan metod: await app.___()",
                "description_ru": "Метод, вызываемый после перехвата SIGTERM для graceful shutdown: await app.___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "stop",
                "hint": "start()ning aksi.",
                "hint_ru": "Противоположность start().",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Xavfsiz deployning to'liq zanjirini tartibga joylashtiring",
                "title_ru": "Расположите полную цепочку безопасного деплоя по порядку",
                "description": "Deploy paytida sodir bo'ladigan qadamlarni to'g'ri ketma-ketlikda joylashtiring",
                "description_ru": "Расположите шаги, происходящие при деплое, в правильном порядке",
                "exercise_type": "drag_and_drop",
                "drag_items": ["systemd/Docker SIGTERM yuboradi", "Joriy handlerlar tugashi kutiladi", "await app.stop() chaqiriladi", "Yangi jarayon mavjud session fayldan ishga tushadi"],
                "drag_items_ru": ["systemd/Docker отправляет SIGTERM", "Ожидается завершение текущих обработчиков", "Вызывается await app.stop()", "Новый процесс запускается из существующего файла сессии"],
                "correct_order": ["systemd/Docker SIGTERM yuboradi", "Joriy handlerlar tugashi kutiladi", "await app.stop() chaqiriladi", "Yangi jarayon mavjud session fayldan ishga tushadi"],
                "hint": "Avval signal keladi, keyin kutish, keyin to'xtash, keyin qayta ishga tushish.",
                "hint_ru": "Сначала приходит сигнал, потом ожидание, потом остановка, потом перезапуск.",
                "difficulty_level": "Medium",
                "points": 7,
            },
        ],
    },
    {
        "order": 13,
        "title": "R2+CAPSTONE-Yakuniy loyiha: dual-mode bot va ixtiyoriy userbot rejimi",
        "title_ru": "R2+КАПСТОУН-Финальный проект: dual-mode бот и опциональный режим юзербота",
        "points_reward": 25,
        "code_language": "python",
        "text_content": """<h3>Kurs davomida o'rganilgan hammasi bitta loyihada</h3>
<p>Bu yakuniy capstone kursning markaziy g'oyasini &mdash; Pyrogram'ning dual-mode
imkoniyatini &mdash; to'liq amalda ko'rsatadi: bitta kod bazasi, ikkita ishga tushirish rejimi.
<strong>Asosiy bot</strong> (bot_token bilan) oddiy foydalanuvchilar uchun ochiq: buyruqlar,
inline menyu, callback tugmalar. <strong>Ixtiyoriy userbot rejimi</strong> (bir xil kod, faqat
boshqa Client konfiguratsiyasi bilan ishga tushiriladi) esa botga ochiq bo'lmagan qo'shimcha
imkoniyatlarni beradi: chuqur tarix skanerlash, kanal statistikasi (xom invoke() orqali).</p>

<h3>Arxitektura: bitta kodning ikki yuzi</h3>
<p>Loyiha 1-12 darslardagi barcha bo'laklarni birlashtiradi: plugins tizimi (9-dars) orqali
kod modullarga bo'linadi, filters (4-dars) va handlerlar (3-dars) buyruqlarni boshqaradi,
sessiya xavfsizligi (5-dars) ikkala Client uchun ham to'g'ri sozlanadi, callback/inline
(7-dars) foydalanuvchi interfeysini boyitadi, async iteratsiya (8-dars) katta ma'lumotlar bilan
ishlaydi, xom invoke() (10-dars) userbot rejimida qo'shimcha statistika oladi, TgCrypto
(11-dars) ikkala Client uchun ham ishlaydi, va nihoyat &mdash; 12-darsdagi deploy amaliyotlari
loyihani production darajasiga olib chiqadi.</p>

<pre class="mermaid">
flowchart TB
  ENV["Muhit o'zgaruvchilari:
TG_API_ID, TG_API_HASH,
TG_BOT_TOKEN, ENABLE_USERBOT"]
  ENV --> BOT["Asosiy Client
(bot_token bilan)
plugins/ orqali yuklanadi"]
  ENV -->|"ENABLE_USERBOT=1 bo'lsa"| USER["Ixtiyoriy Client
(session_string bilan,
faqat administrator uchun)"]
  BOT --> PUB["Ommaviy funksiyalar:
/start, /shop, inline menyu,
callback query'lar"]
  USER --> PRIV["Administrativ funksiyalar:
chuqur tarix tahlili,
invoke() bilan kanal statistikasi"]
  PUB --> DB[("Umumiy holat/keshlash
(ixtiyoriy, masalan Redis/DB)")]
  PRIV --> DB
</pre>
<p>Diagram shuni ko'rsatadiki, ikkala Client mustaqil ishga tushsa-da, ular bitta muhit
konfiguratsiyasidan (va xohlasa, umumiy holat qatlamidan) foydalanadi &mdash; bu Pyrogram'ning
dual-mode imkoniyatini haqiqiy production arxitekturaga aylantiradi.</p>

<h3>Nega userbot rejimi "ixtiyoriy" bo'lishi kerak</h3>
<p>5-darsda ko'rganingizdek, userbot sessiyasi butun shaxsiy hisobni nazorat qilish huquqini
beradi &mdash; shuning uchun uni yoqish qaror qabul qiluvchi tomonning ongli tanlovi bo'lishi
kerak (masalan <code>ENABLE_USERBOT</code> muhit bayrog'i orqali), hech qachon standart
holatda yoqilgan bo'lmasligi kerak. Bu shuningdek amaliy dizayn qoidasini ko'rsatadi: kuchli
imkoniyat = ongli ravishda yoqiladigan imkoniyat.</p>

<h3>Baholash mezonlari</h3>
<p>Ushbu capstone quyidagi mezonlar bo'yicha baholanadi: (1) dual-mode arxitekturasi to'g'ri
ishlashi (bot mustaqil, userbot ixtiyoriy); (2) kamida uchta plugin fayli orqali tashkil
etilgan kod; (3) sessiya xavfsizligi qoidalariga rioya qilingani (.gitignore, muhit
o'zgaruvchilari); (4) kamida bitta joyda xom invoke() ishlatilgani; (5) FloodWait to'g'ri
qayta ishlanishi; (6) graceful shutdown mavjudligi.</p>

<h3>Kengaytirish g'oyalari (loyihadan tashqari, ixtiyoriy)</h3>
<p>Capstone topshirilgandan keyin ham davom ettirish uchun tabiiy yo'nalishlar: statistika
natijalarini Redis yoki oddiy fayl keshida saqlab, har safar qaytadan hisoblamaslik; userbot
tomonidagi <code>/deep_stats</code> natijasini asosiy botga (masalan ichki queue yoki umumiy
DB orqali) uzatib, foydalanuvchilarga botning o'zi orqali ko'rsatish; yoki 6-darsdagi
send_media_group'ni ishlatib, statistikani grafik (masalan matplotlib bilan chizilgan rasm)
sifatida yuborish. Bularning hech biri baholash uchun shart emas &mdash; ular kursdan keyin
loyihani real mahsulotga aylantirish yo'nalishlarini ko'rsatish uchun keltirilgan.</p>

<h3>Kurs yakuni: nima o'zgardi</h3>
<p>Kurs boshida siz Pyrogram'ni aiogram va Telethon bilan taqqoslashdan boshladingiz. Endi
siz nafaqat farqlarni bilasiz, balki ularning har birini &mdash; dual-mode Client, dekorator
handlerlar, filters DSL, sessiya xavfsizligi, plugins arxitekturasi va xom MTProto darajasiga
tushish qobiliyatini &mdash; amalda qo'llay olasiz. Aynan shu amaliy tajriba, nazariy bilim
emas, Pyrogram'ni haqiqiy loyihada ishonch bilan ishlatish imkonini beradi.</p>

<p>Loyihangizni topshirishdan oldin o'zingiz uchun qisqa kod ko'rib chiqish (self-review)
o'tkazing: har bir maxfiy qiymat muhit o'zgaruvchisidanmi, har bir callback_query.answer()
chaqirilganmi, har bir katta iteratsiya FloodWait'ga chidamlimi &mdash; bu odat kursdan keyin
ham har qanday production Pyrogram loyihasida davom etadi.</p>""",
        "text_content_ru": """<h3>Всё изученное в курсе — в одном проекте</h3>
<p>Этот финальный капстоун полностью демонстрирует на практике центральную идею курса —
dual-mode возможности Pyrogram: одна кодовая база, два режима запуска.
<strong>Основной бот</strong> (с bot_token) открыт для обычных пользователей: команды,
inline-меню, callback-кнопки. <strong>Опциональный режим юзербота</strong> (тот же код,
запускаемый лишь с другой конфигурацией Client) даёт дополнительные возможности, недоступные
боту: глубокое сканирование истории, статистика канала (через сырой invoke()).</p>

<h3>Архитектура: две стороны одного кода</h3>
<p>Проект объединяет все части уроков 1-12: система plugins (урок 9) разбивает код на модули,
filters (урок 4) и обработчики (урок 3) управляют командами, безопасность сессий (урок 5)
правильно настроена для обоих Client, callback/inline (урок 7) обогащают пользовательский
интерфейс, асинхронная итерация (урок 8) работает с большими данными, сырой invoke() (урок 10)
получает дополнительную статистику в режиме юзербота, TgCrypto (урок 11) работает для обоих
Client, и наконец — практики деплоя из урока 12 доводят проект до продакшн-уровня.</p>

<pre class="mermaid">
flowchart TB
  ENV["Переменные окружения:
TG_API_ID, TG_API_HASH,
TG_BOT_TOKEN, ENABLE_USERBOT"]
  ENV --> BOT["Основной Client
(с bot_token)
загружается через plugins/"]
  ENV -->|"если ENABLE_USERBOT=1"| USER["Опциональный Client
(с session_string,
только для администратора)"]
  BOT --> PUB["Публичные функции:
/start, /shop, inline-меню,
callback query"]
  USER --> PRIV["Административные функции:
глубокий анализ истории,
статистика канала через invoke()"]
  PUB --> DB[("Общее состояние/кеш
(опционально, например Redis/БД)")]
  PRIV --> DB
</pre>
<p>Диаграмма показывает, что оба Client, хотя и запускаются независимо, используют одну и ту
же конфигурацию окружения (и, при желании, общий слой состояния) &mdash; это превращает
dual-mode возможность Pyrogram в реальную продакшн-архитектуру.</p>

<h3>Почему режим юзербота должен быть «опциональным»</h3>
<p>Как вы видели в уроке 5, сессия юзербота даёт право контроля над всем личным аккаунтом
&mdash; поэтому его включение должно быть осознанным выбором принимающей решение стороны
(например через флаг окружения <code>ENABLE_USERBOT</code>), и никогда не должно быть
включено по умолчанию. Это также показывает практическое правило дизайна: мощная возможность
= осознанно включаемая возможность.</p>

<h3>Критерии оценки</h3>
<p>Этот капстоун оценивается по следующим критериям: (1) правильная работа dual-mode
архитектуры (бот независим, юзербот опционален); (2) код организован минимум через три файла
плагинов; (3) соблюдены правила безопасности сессий (.gitignore, переменные окружения); (4)
сырой invoke() использован хотя бы в одном месте; (5) корректная обработка FloodWait; (6)
наличие graceful shutdown.</p>

<h3>Идеи для расширения (вне проекта, опционально)</h3>
<p>Естественные направления для продолжения после сдачи капстоуна: сохранять результаты
статистики в Redis или простом файловом кеше, чтобы не пересчитывать каждый раз; передавать
результат <code>/deep_stats</code> со стороны юзербота основному боту (например через
внутреннюю очередь или общую БД), чтобы показывать пользователям через сам бот; или
использовать send_media_group из урока 6, чтобы отправлять статистику в виде графика
(например, изображения, построенного через matplotlib). Ничего из этого не обязательно для
оценки &mdash; это приведено, чтобы показать направления превращения проекта в реальный
продукт после курса.</p>

<h3>Итог курса: что изменилось</h3>
<p>В начале курса вы начали со сравнения Pyrogram с aiogram и Telethon. Теперь вы не только
знаете различия, но и умеете применять каждое из них на практике &mdash; dual-mode Client,
декораторные обработчики, DSL фильтров, безопасность сессий, архитектуру plugins и умение
спускаться на уровень сырого MTProto. Именно этот практический опыт, а не теоретические
знания, даёт уверенность использовать Pyrogram в реальном проекте.</p>

<p>Перед сдачей проекта проведите короткий самостоятельный код-ревью: каждое ли секретное
значение берётся из переменной окружения, вызывается ли каждый callback_query.answer(),
устойчива ли каждая большая итерация к FloodWait &mdash; эта привычка продолжится и после
курса в любом продакшн-проекте на Pyrogram.</p>""",
        "code_content": """# Loyiha tuzilishi:
#
# capstone_bot/
#   bot.py
#   plugins/
#     public.py      (bot rejimi uchun: /start, /shop, callback)
#     admin_stats.py (faqat userbot mavjud bo'lsa ishlaydigan tahlil buyruqlari)
#   sessions/          (workdir — .gitignore ichida)

# --- bot.py ---
import os
import asyncio
import signal
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
ENABLE_USERBOT = os.environ.get("ENABLE_USERBOT") == "1"
USER_SESSION_STRING = os.environ.get("TG_USER_SESSION_STRING")

# Asosiy bot — ommaga ochiq, har doim ishga tushadi
bot_app = Client(
    "capstone_bot",
    api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
    workdir="./sessions",
    plugins=dict(root="plugins", include=["plugins.public"]),
)

# Ixtiyoriy userbot — faqat ongli ravishda yoqilganda ishga tushadi
user_app = None
if ENABLE_USERBOT and USER_SESSION_STRING:
    user_app = Client(
        "capstone_user",
        api_id=API_ID, api_hash=API_HASH,
        session_string=USER_SESSION_STRING,
        plugins=dict(root="plugins", include=["plugins.admin_stats"]),
    )


_stop = asyncio.Event()


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _stop.set)

    await bot_app.start()
    if user_app:
        await user_app.start()
        print("Userbot rejimi YOQILGAN — qo'shimcha admin funksiyalari faol.")
    else:
        print("Userbot rejimi o'chirilgan — faqat asosiy bot ishlaydi.")

    await _stop.wait()

    await bot_app.stop()
    if user_app:
        await user_app.stop()


if __name__ == "__main__":
    asyncio.run(main())
""",
        "code_content_ru": """# Структура проекта:
#
# capstone_bot/
#   bot.py
#   plugins/
#     public.py      (для режима бота: /start, /shop, callback)
#     admin_stats.py (команды аналитики, работающие только при наличии юзербота)
#   sessions/          (workdir — в .gitignore)

# --- bot.py ---
import os
import asyncio
import signal
from pyrogram import Client

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
ENABLE_USERBOT = os.environ.get("ENABLE_USERBOT") == "1"
USER_SESSION_STRING = os.environ.get("TG_USER_SESSION_STRING")

# Основной бот — публичный, запускается всегда
bot_app = Client(
    "capstone_bot",
    api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
    workdir="./sessions",
    plugins=dict(root="plugins", include=["plugins.public"]),
)

# Опциональный юзербот — запускается только при осознанном включении
user_app = None
if ENABLE_USERBOT and USER_SESSION_STRING:
    user_app = Client(
        "capstone_user",
        api_id=API_ID, api_hash=API_HASH,
        session_string=USER_SESSION_STRING,
        plugins=dict(root="plugins", include=["plugins.admin_stats"]),
    )


_stop = asyncio.Event()


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, _stop.set)

    await bot_app.start()
    if user_app:
        await user_app.start()
        print("Режим юзербота ВКЛЮЧЁН — дополнительные админ-функции активны.")
    else:
        print("Режим юзербота отключён — работает только основной бот.")

    await _stop.wait()

    await bot_app.stop()
    if user_app:
        await user_app.stop()


if __name__ == "__main__":
    asyncio.run(main())
""",
        "video_url": None,
        "task": {
            "task_title": "YAKUNIY CAPSTONE: dual-mode Pyrogram loyihasi",
            "task_title_ru": "ФИНАЛЬНЫЙ КАПСТОУН: dual-mode проект на Pyrogram",
            "task_description": (
                "To'liq dual-mode Pyrogram loyihasi yarating: (1) asosiy bot plugins/public.py "
                "orqali /start, /shop (inline menyu bilan) va tegishli callback handlerlarini "
                "taqdim etsin; (2) ENABLE_USERBOT=1 bo'lsa ishga tushuvchi ixtiyoriy userbot "
                "Client, plugins/admin_stats.py orqali /deep_stats buyrug'ini taqdim etsin — u "
                "get_chat_history() (async for, FloodWait qayta urinish bilan) va kamida bitta "
                "xom invoke() chaqiruvi (masalan GetFullChannel) orqali kanal haqida statistika "
                "chiqarsin; (3) ikkala Client ham sessiya xavfsizligi qoidalariga rioya qilib "
                "workdir/session_string orqali sozlansin; (4) graceful shutdown (SIGTERM + "
                "app.stop()) qo'shilsin."
            ),
            "task_description_ru": (
                "Создайте полноценный dual-mode проект на Pyrogram: (1) основной бот через "
                "plugins/public.py предоставляет /start, /shop (с inline-меню) и "
                "соответствующие обработчики callback; (2) опциональный Client юзербота, "
                "запускающийся при ENABLE_USERBOT=1, предоставляет через "
                "plugins/admin_stats.py команду /deep_stats — она выводит статистику канала "
                "через get_chat_history() (async for, с повтором при FloodWait) и минимум один "
                "сырой вызов invoke() (например GetFullChannel); (3) оба Client настроены с "
                "соблюдением правил безопасности сессий через workdir/session_string; (4) "
                "добавлен graceful shutdown (SIGTERM + app.stop())."
            ),
            "task_requirements": (
                "Dual-mode arxitektura ishlashi kerak (bot mustaqil, userbot ixtiyoriy); "
                "kamida 2 ta plugin fayli bo'lishi kerak; xom invoke() kamida bir marta "
                "ishlatilishi kerak; FloodWait qayta urinish mantiqi bo'lishi kerak; graceful "
                "shutdown ishlashi kerak; hech qanday maxfiy qiymat kodga hardcode qilinmagan "
                "bo'lishi kerak."
            ),
            "task_requirements_ru": (
                "Dual-mode архитектура должна работать (бот независим, юзербот опционален); "
                "минимум 2 файла плагинов; сырой invoke() использован хотя бы раз; должна быть "
                "логика повтора при FloodWait; graceful shutdown должен работать; ни одно "
                "секретное значение не должно быть захардкожено в коде."
            ),
            "task_technologies": "Pyrogram, TgCrypto, asyncio, plugins",
            "task_deadline_days": 7,
        },
        "sample": {
            "title": "Namuna: dual-mode capstone skeleti",
            "title_ru": "Пример: скелет dual-mode капстоуна",
            "description": "Asosiy bot + ixtiyoriy userbot pluginlari bilan to'liq ishlaydigan capstone skeleti.",
            "description_ru": "Полностью рабочий скелет капстоуна с основным ботом + опциональными плагинами юзербота.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "plugins/public.py",
                    "language": "python",
                    "code": """from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("start"))
async def start(client, message):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Katalog", callback_data="shop:open")]])
    await message.reply_text("Xush kelibsiz! Capstone bot ishlamoqda.", reply_markup=kb)


@Client.on_callback_query(filters.regex("^shop:open$"))
async def shop_open(client, callback_query):
    await callback_query.answer()
    await callback_query.message.edit_text("Katalog: Kitob, Ruchka, Daftar")
""",
                },
                {
                    "filename": "plugins/admin_stats.py",
                    "language": "python",
                    "code": """import asyncio
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.errors import FloodWait


@Client.on_message(filters.command("deep_stats") & filters.private)
async def deep_stats(client, message):
    chat_id = message.chat.id
    count = 0
    while True:
        try:
            async for _ in client.get_chat_history(chat_id, limit=1000):
                count += 1
            break
        except FloodWait as e:
            await asyncio.sleep(e.value)

    peer = await client.resolve_peer(chat_id)
    full = await client.invoke(functions.channels.GetFullChannel(channel=peer))

    await message.reply_text(
        f"Skanerlangan xabarlar: {count}\\n"
        f"A'zolar: {getattr(full.full_chat, 'participants_count', 'N/A')}"
    )
""",
                },
            ],
        },
        "exercises": [
            {
                "title": "Capstone arxitekturasining markaziy g'oyasi",
                "title_ru": "Центральная идея архитектуры капстоуна",
                "description": "Ushbu yakuniy capstone loyihasining markaziy arxitektura g'oyasi nima?",
                "description_ru": "Какова центральная архитектурная идея этого финального капстоун-проекта?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ikki xil dasturlash tilida yozilgan ikki alohida loyiha",
                    "Bitta kod bazasi, bot doim ishlaydi, userbot rejimi ongli ravishda ixtiyoriy",
                    "Faqat userbot rejimi, bot umuman ishlatilmaydi",
                    "Har xil kutubxonalar (Pyrogram va Telethon) bir loyihada",
                ],
                "options_ru": [
                    "Два отдельных проекта на разных языках программирования",
                    "Одна кодовая база, бот всегда работает, режим юзербота осознанно опционален",
                    "Только режим юзербота, бот вообще не используется",
                    "Разные библиотеки (Pyrogram и Telethon) в одном проекте",
                ],
                "correct_answers": "B",
                "is_multiple_select": False,
                "hint": "Kurs boshidan beri takrorlanayotgan dual-mode g'oyasini eslang.",
                "hint_ru": "Вспомните повторяющуюся с начала курса идею dual-mode.",
                "explanation": "Capstone Pyrogram'ning markaziy farqlovchi xususiyatini — bitta kod bazasida bot doimiy, userbot esa ongli ravishda yoqiladigan ixtiyoriy qo'shimcha rejim ekanini amalda ko'rsatadi.",
                "difficulty_level": "Medium",
                "points": 7,
            },
            {
                "title": "Userbot rejimini yoqish uchun tavsiya etilgan mexanizm",
                "title_ru": "Рекомендуемый механизм включения режима юзербота",
                "description": "Userbot rejimi standart holatda o'chirilgan bo'lishi va faqat ongli ravishda ___ orqali yoqilishi tavsiya etiladi",
                "description_ru": "Режим юзербота рекомендуется по умолчанию отключать и включать только осознанно через ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "muhit o'zgaruvchisi",
                "correct_answers_ru": "переменную окружения",
                "hint": "Bu 5-va 12-darslarda ko'rgan xavfsizlik amaliyoti bilan bog'liq.",
                "hint_ru": "Это связано с практикой безопасности из уроков 5 и 12.",
                "difficulty_level": "Medium",
                "points": 6,
            },
            {
                "title": "Capstone qismlarini kurs darslariga mos qo'ying",
                "title_ru": "Сопоставьте части капстоуна с уроками курса",
                "description": "Capstone loyihasining qismlarini ular asoslangan darslar bilan mos tartibda joylashtiring: avval plugins tashkiloti, keyin xom invoke(), keyin graceful shutdown",
                "description_ru": "Расположите части капстоуна в порядке уроков, на которых они основаны: сначала организация plugins, затем сырой invoke(), затем graceful shutdown",
                "exercise_type": "drag_and_drop",
                "drag_items": ["plugins/public.py va plugins/admin_stats.py tashkiloti", "GetFullChannel uchun client.invoke() chaqiruvi", "SIGTERM ushlab app.stop() chaqiruvchi yakuniy blok"],
                "drag_items_ru": ["Организация plugins/public.py и plugins/admin_stats.py", "Вызов client.invoke() для GetFullChannel", "Финальный блок, ловящий SIGTERM и вызывающий app.stop()"],
                "correct_order": ["plugins/public.py va plugins/admin_stats.py tashkiloti", "GetFullChannel uchun client.invoke() chaqiruvi", "SIGTERM ushlab app.stop() chaqiruvchi yakuniy blok"],
                "hint": "Bu 9, 10 va 12-darslarga mos keladi, shu tartibda.",
                "hint_ru": "Это соответствует урокам 9, 10 и 12 в этом порядке.",
                "difficulty_level": "Hard",
                "points": 9,
            },
            {
                "title": "Nega userbot funksiyasi alohida plugin faylida",
                "title_ru": "Почему функциональность юзербота в отдельном файле плагина",
                "description": "Capstone'da nima uchun userbot'ga xos buyruqlar (masalan /deep_stats) alohida plugins/admin_stats.py faylida, umumiy plugins/public.py bilan aralashtirilmasdan saqlanadi? Kamida ikkita sabab keltiring.",
                "description_ru": "Почему в капстоуне команды, специфичные для юзербота (например /deep_stats), хранятся в отдельном файле plugins/admin_stats.py, не смешиваясь с общим plugins/public.py? Приведите минимум две причины.",
                "exercise_type": "text_input",
                "expected_answer": "Birinchidan, aniq mas'uliyat ajratilishi — ommaviy va administrativ funksiyalarni bir faylda aralashtirmaslik kodni o'qishni osonlashtiradi. Ikkinchidan, xavfsizlik/ishga tushirish nazorati — include=[\"plugins.admin_stats\"] faqat userbot Client'iga yuklanadi, shuning uchun userbot o'chirilganda bu buyruqlar umuman mavjud bo'lmaydi, tasodifiy oshkor bo'lish xavfi kamayadi.",
                "hint": "Bitta sababi kod tashkilotchiligi, ikkinchisi xavfsizlik/nazorat bilan bog'liq.",
                "hint_ru": "Одна причина связана с организацией кода, другая — с безопасностью/контролем.",
                "difficulty_level": "Hard",
                "points": 9,
            },
        ],
    },
]
