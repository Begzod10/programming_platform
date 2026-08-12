"""Telegram Bot Track, follow-up course: "Telethon: Telegram Userbot va MTProto".

Pure-data course spec — see course_builder/__init__.py for the contract.
Follow-up to course 48 (Telegram Bot aiogram, Bot API). Assumes the student
already knows Bot API concepts (handlers, keyboards, FSM, middleware, async
SQLAlchemy, file handling, group admin, webhook deploy) from course 48, and
teaches a fundamentally different technology: Telethon, a pure-Python
library implementing Telegram's raw MTProto protocol, which can log in as a
real user account ("userbot") instead of only as a bot. This unlocks things
the Bot API can never do — reading full chat/channel history without being
an admin, joining groups without an invite link, acting as "you" — and this
course's job is to teach what is different about MTProto/user-account
automation, not to re-teach Bot API concepts or generic aiogram material.

A parallel course on Pyrogram (another MTProto library) is being built
separately; some MTProto-fundamentals overlap between the two is expected
and fine (same as how the JS and Python tracks each have their own testing
course) — this course stays focused on Telethon's own API and idioms.

Build with:
    cd backend
    python scripts/build_course.py scripts/course_specs/telethon_userbot_mtproto.py --dry-run
    python scripts/build_course.py scripts/course_specs/telethon_userbot_mtproto.py
"""

COURSE = {
    "title": "Telethon: Telegram Userbot va MTProto",
    "description": (
        "Telegram Bot aiogram kursidan keyingi ilg'or yo'nalish: Telethon kutubxonasi orqali "
        "Telegram'ning xom MTProto protokoli bilan ishlash va oddiy bot emas, balki haqiqiy "
        "foydalanuvchi hisobi nomidan ishlaydigan \"userbot\" yaratish. Kursda api_id/api_hash "
        "olish va birinchi TelegramClient ulanishi, session string/session fayl xavfsizligi "
        "(bu mavzuga alohida chuqur e'tibor beriladi — chunki oqib ketgan session butun hisobni "
        "to'liq qo'lga olishga teng), voqea-asosli event handlerlar (events.NewMessage va "
        "boshqalar), tarixni ommaviy o'qish va sahifalash, kanal/guruhlarga dasturiy qo'shilish "
        "va Telegram ToS/ban xavfi haqida halol muhokama, mediani ommaviy yuklab olish, "
        "dialog/kontakt/entity'lar bilan ishlash, userbot va haqiqiy botni bitta gibrid tizimda "
        "birlashtirish, xavfsiz deploy (session sirlarini boshqarish, systemd) va yakuniy "
        "capstone loyihasi qamrab olinadi."
    ),
    "instructor_id": 2,
    "difficulty_level": "Advanced",
    "duration_weeks": 4,
    "max_points": 571,  # sum(lesson.points_reward) + sum(exercise.points) across all 13 lessons
    "category_id": 12,
    "prerequisite_course_id": 48,
    "display_order": 702,
    "image_url": "https://raw.githubusercontent.com/LonamiWebs/Telethon/master/logo.svg",
    "thumbnail_url": "https://raw.githubusercontent.com/LonamiWebs/Telethon/master/logo.svg",
    "is_active": True,
    "is_published": False,
}

# Natural Russian course title, written to translation_cache (entity_type="course")
# by a small one-off step after the build — see bottom of this file / README note
# in the build report. NOT part of the standard COURSE dict contract (Course model
# has no title_ru column), but the platform DOES serve course.title/description
# translations from translation_store at request time (see
# app/api/v1/endpoints/courses.py::_translate_course_dto), so this is provided
# here for that separate write step.
COURSE_TITLE_RU = "Telethon: Telegram-юзербот и MTProto"
COURSE_DESCRIPTION_RU = (
    "Продвинутое направление после курса Telegram Bot aiogram: работа с сырым протоколом "
    "Telegram — MTProto — через библиотеку Telethon, и создание не обычного бота, а "
    "\"юзербота\", работающего от имени реального аккаунта пользователя. В курсе разбираются "
    "получение api_id/api_hash и первое подключение TelegramClient, безопасность "
    "session-строки/файла сессии (этой теме уделяется отдельное глубокое внимание — "
    "утёкшая сессия равносильна полному захвату аккаунта), событийные обработчики "
    "(events.NewMessage и другие), массовое чтение истории и постраничная загрузка, "
    "программное вступление в каналы/группы и честное обсуждение риска бана по ToS Telegram, "
    "массовая загрузка медиа, работа с диалогами/контактами/entity, объединение юзербота и "
    "настоящего бота в одну гибридную систему, безопасный деплой (управление секретами сессии, "
    "systemd) и итоговый capstone-проект."
)


LESSONS = [
{
"order": 0,
"title": """1-MTProto va Bot API: userbot nima va u nimalarga qodir""",
"title_ru": """1-MTProto и Bot API: что такое юзербот и на что он способен""",
"points_reward": 16,
"code_language": "python",
"text_content": """<h3>Ikki mutlaqo boshqa yo'l: Bot API va MTProto</h3>
<p>48-kursda siz aiogram orqali <strong>Bot API</strong> bilan ishladingiz. Bot API &mdash; Telegram serverlari ustiga qurilgan qulay HTTPS qatlam: siz botga buyruq berasiz (masalan, <code>sendMessage</code>), Telegram esa buni ichkarida haqiqiy protokolga &mdash; <strong>MTProto</strong>ga &mdash; o'zi tarjima qiladi. Siz hech qachon MTProto bilan to'g'ridan-to'g'ri gaplashmaysiz, va bu ataylab shunday qilingan: Bot API xavfsizlik va soddalik uchun ancha tor, nazorat qilinadigan imkoniyatlar to'plamini beradi.</p>
<p>Telethon esa boshqa qatlamda ishlaydi &mdash; u MTProtoning o'zini, xom holida, to'g'ridan-to'g'ri gapiradi. Bu <em>arxitektura darajasidagi</em> farq, shunchaki "boshqa kutubxona" emas: aiogram bot Telegram serveriga "men botman, mendan sendMessage so'ralganda shuni bajar" deb ro'yxatdan o'tgan cheklangan hisob nomidan gapiradi; Telethon esa sizning haqiqiy telefon raqamingiz bilan ro'yxatdan o'tgan <strong>haqiqiy foydalanuvchi hisobi</strong> nomidan &mdash; xuddi rasmiy Telegram ilovasi qanday ishlasa, xuddi shunday &mdash; gapiradi. Shu sababli bunday dasturlarni <strong>"userbot"</strong> deb atashadi: u texnik jihatdan bot emas, balki avtomatlashtirilgan foydalanuvchi hisobi.</p>
<h3>Userbot nimalarga qodir &mdash; oddiy bot esa qodir emas</h3>
<ul>
<li><strong>To'liq tarixni o'qish</strong> &mdash; kanalda administrator bo'lmasangiz ham, agar hisobingiz shu kanalga a'zo bo'lsa, barcha eski xabarlarni o'qiy olasiz. Oddiy bot esa faqat o'ziga yuborilgan yoki u qo'shilgandan keyingi xabarlarni (va faqat guruh admin sozlamalariga ko'ra) ko'radi.</li>
<li><strong>Username orqali istalgan ochiq guruh/kanalga qo'shilish</strong> &mdash; taklif havolasi shart emas, oddiy <code>@kanal_nomi</code> yetarli. Bot esa hech qachon o'zini guruhga "qo'sha olmaydi" &mdash; uni faqat inson qo'shishi mumkin.</li>
<li><strong>Dialoglar, kontaktlar va arxiv ro'yxatiga to'liq kirish</strong> &mdash; hisobingizdagi barcha suhbatlar, kontaktlar, arxivlangan chatlar ro'yxati.</li>
<li><strong>"Inson kabi" ko'rinish</strong> &mdash; xabar "Bot" belgisisiz, oddiy foydalanuvchidan kelayotgandek ko'rinadi.</li>
</ul>
<p>Bu imkoniyatlar kuchli, lekin ular bilan katta mas'uliyat keladi &mdash; buni 7-darsda ochiq muhokama qilamiz: Telegram bunday avtomatlashtirishni kuzatib boradi va suiiste'mol qilingan hisoblarni cheklaydi yoki butunlay bloklaydi. Bu kursda userbot texnikasi shaxsiy avtomatlashtirish va tadqiqot uchun o'rgatiladi, ommaviy spam yoki hisob-fermalari uchun emas.</p>
<h3>Ikkalasi ham bitta protokolga tayanadi</h3>
<p>Muhim nuqta: Bot API HAM, Telethon HAM, oxir-oqibatda bir xil MTProto protokoli ustida ishlaydi &mdash; farq shunda, KIM MTProto bilan bevosita gaplashadi. Bot API holatida &mdash; Telegramning o'zi (sizning nomingizdan HTTPS orqali vositachilik qiladi). Telethon holatida &mdash; sizning kodingiz, to'g'ridan-to'g'ri, hech qanday vositachisiz.</p>
<pre class="mermaid">
flowchart TB
  subgraph BotAPI["Bot API yoli (48-kurs)"]
    A1["Sizning aiogram kodingiz"] -->|"HTTPS so'rov"| A2["api.telegram.org (Bot API server)"]
    A2 -->|"MTProto"| A3["Telegram core datacenter"]
  end
  subgraph Userbot["Userbot yoli (bu kurs)"]
    B1["Sizning Telethon kodingiz"] -->|"MTProto to'gridan-to'gri"| B3["Telegram core datacenter"]
  end
</pre>
<p>Diagramma shuni ko'rsatadi: Bot API yo'lida orada qo'shimcha vositachi qatlam bor va u sizning nomingizdan faqat cheklangan amallarni bajaradi; Telethon yo'lida esa vositachi yo'q &mdash; sizning kodingiz bevosita, to'liq foydalanuvchi huquqi bilan gaplashadi. Shu farq keyingi darslarning butun mazmunini belgilaydi.</p>
<h3>api_id / api_hash &mdash; bu bot tokeni emas</h3>
<p>aiogram'da bot yaratish uchun @BotFather'dan bitta <code>token</code> olingan edi &mdash; u bot hisobini butunlay aniqlaydi. Telethon'da esa ikkita mutlaqo boshqa narsa kerak bo'ladi: <code>api_id</code>/<code>api_hash</code> juftligi (keyingi darsda my.telegram.org'dan olinadi) va <strong>hisobingizning o'zi</strong> (telefon raqami orqali login). <code>api_id</code>/<code>api_hash</code> &mdash; bu sizning <em>ilovangizni</em> aniqlaydi (xuddi rasmiy Telegram ilovasi ham o'zining api_id'siga ega bo'lgani kabi), lekin u orqali HECH KIM avtomatik ravishda sizning hisobingizga kira olmaydi &mdash; kirish uchun alohida, to'liq login jarayoni (telefon + kod + ehtimol 2FA) kerak bo'ladi. Bu farqni tushunish keyingi darsning butun asosi.</p>
<h3>Kod shakli qanday o'zgaradi</h3>
<p>Yuzaki qaraganda ikkala kutubxona ham o'xshash &mdash; ikkalasida ham <code>async def</code> handlerlar, xabar yuborish metodlari bor. Lekin ostidagi model boshqa: aiogram'da <code>Dispatcher</code> va <code>Router</code> orqali filtrlangan update oqimi bilan ishlaysiz; Telethon'da <code>TelegramClient</code>ning o'zi ham client, ham event-dispatcher vazifasini bajaradi &mdash; alohida Dispatcher obyekti yo'q. Quyidagi kod ikkalasini yonma-yon solishtiradi &mdash; hozircha faqat umumiy shaklga e'tibor bering, ichki farqlarni 4-darsda chuqur ko'ramiz.</p>""",
"text_content_ru": """<h3>Два совершенно разных пути: Bot API и MTProto</h3>
<p>В курсе 48 вы работали с <strong>Bot API</strong> через aiogram. Bot API &mdash; это удобный HTTPS-слой поверх серверов Telegram: вы вызываете метод бота (например, <code>sendMessage</code>), а Telegram сам внутри переводит это в настоящий протокол &mdash; <strong>MTProto</strong>. Вы никогда не общаетесь с MTProto напрямую, и это сделано намеренно: Bot API даёт узкий, контролируемый набор возможностей ради безопасности и простоты.</p>
<p>Telethon работает на другом уровне &mdash; он говорит с самим MTProto, в сыром виде, напрямую. Это различие <em>на уровне архитектуры</em>, а не просто "другая библиотека": бот на aiogram говорит с сервером Telegram от имени ограниченного аккаунта, зарегистрированного как "я бот, выполняй sendMessage по запросу"; Telethon же говорит от имени <strong>настоящего аккаунта пользователя</strong>, зарегистрированного по вашему реальному номеру телефона &mdash; точно так же, как работает официальное приложение Telegram. Поэтому такие программы называют <strong>"юзербот"</strong> (userbot): технически это не бот, а автоматизированный пользовательский аккаунт.</p>
<h3>На что способен юзербот &mdash; а обычный бот нет</h3>
<ul>
<li><strong>Чтение полной истории</strong> &mdash; даже не будучи администратором канала, если ваш аккаунт состоит в нём участником, вы можете прочитать все старые сообщения. Обычный бот видит только сообщения, отправленные ему, или после момента его добавления (и то в зависимости от настроек группы).</li>
<li><strong>Вступление в любую открытую группу/канал по username</strong> &mdash; ссылка-приглашение не нужна, достаточно обычного <code>@username_канала</code>. Бот же никогда не может "сам себя добавить" &mdash; его добавляет только человек.</li>
<li><strong>Полный доступ к диалогам, контактам и архиву</strong> &mdash; список всех переписок, контактов, архивных чатов вашего аккаунта.</li>
<li><strong>Вид "как у человека"</strong> &mdash; сообщение выглядит как от обычного пользователя, без пометки "Bot".</li>
</ul>
<p>Эти возможности мощные, но с ними приходит большая ответственность &mdash; это честно обсудим в 7-м уроке: Telegram отслеживает такую автоматизацию и ограничивает или полностью блокирует аккаунты за злоупотребление. В этом курсе техника юзербота преподаётся для личной автоматизации и исследований, а не для массового спама или фермы аккаунтов.</p>
<h3>Оба пути опираются на один и тот же протокол</h3>
<p>Важный момент: и Bot API, и Telethon в итоге работают поверх одного и того же MTProto &mdash; разница в том, КТО говорит с MTProto напрямую. В случае Bot API &mdash; сам Telegram (посредничает от вашего имени через HTTPS). В случае Telethon &mdash; ваш код, напрямую, без какого-либо посредника.</p>
<pre class="mermaid">
flowchart TB
  subgraph BotAPI["Путь Bot API (курс 48)"]
    A1["Ваш код на aiogram"] -->|"HTTPS-запрос"| A2["api.telegram.org (сервер Bot API)"]
    A2 -->|"MTProto"| A3["核心-дата-центр Telegram"]
  end
  subgraph Userbot["Путь юзербота (этот курс)"]
    B1["Ваш код на Telethon"] -->|"MTProto напрямую"| B3["核心-дата-центр Telegram"]
  end
</pre>
<p>Диаграмма показывает: в пути Bot API между вами и ядром есть дополнительный посреднический слой, который выполняет от вашего имени только ограниченный набор действий; в пути Telethon посредника нет &mdash; ваш код говорит напрямую, с полными правами пользователя. Именно это различие определяет содержание всех следующих уроков.</p>
<h3>api_id / api_hash &mdash; это не токен бота</h3>
<p>В aiogram для создания бота у @BotFather получали один <code>token</code> &mdash; он полностью идентифицирует аккаунт бота. В Telethon же нужны две совершенно разные вещи: пара <code>api_id</code>/<code>api_hash</code> (её получим в следующем уроке на my.telegram.org) и <strong>сам аккаунт</strong> (вход по номеру телефона). <code>api_id</code>/<code>api_hash</code> идентифицирует ваше <em>приложение</em> (так же как у официального приложения Telegram есть свой api_id), но через них НИКТО не может автоматически войти в ваш аккаунт &mdash; для входа нужен отдельный, полноценный процесс логина (телефон + код + возможно 2FA). Понимание этого различия &mdash; основа следующего урока.</p>
<h3>Как меняется форма кода</h3>
<p>На первый взгляд обе библиотеки похожи &mdash; в обеих есть <code>async def</code>-обработчики, методы отправки сообщений. Но модель под капотом другая: в aiogram вы работаете через <code>Dispatcher</code> и <code>Router</code> с отфильтрованным потоком апдейтов; в Telethon сам <code>TelegramClient</code> выполняет роль и клиента, и диспетчера событий &mdash; отдельного объекта Dispatcher нет. Код ниже сравнивает их бок о бок &mdash; пока обращайте внимание только на общую форму, во внутренние различия углубимся в 4-м уроке.</p>""",
"code_content": """# ============================================================
# Bot API (aiogram) vs MTProto (Telethon) -- bir vazifa, ikki yondashuv
# ============================================================

# --- 1) aiogram (Bot API) -- 48-kursdan tanish shakl -----------------
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

bot = Bot(token="123456:BOT_TOKEN")          # bot HISOBINI aniqlaydi
dp = Dispatcher()
router = Router()


@router.message(Command("ping"))
async def aiogram_ping(message: Message) -> None:
    # Bu handler faqat botga yuborilgan /ping buyrug'iga javob beradi.
    # Bot faqat: (a) unga yuborilgan, (b) u qo'shilgan guruhdagi
    # xabarlarni ko'radi -- guruhning eski tarixini o'qiy olmaydi.
    await message.answer("pong (Bot API orqali)")


dp.include_router(router)
# asyncio.run(dp.start_polling(bot))


# --- 2) Telethon (MTProto) -- shu kursning shakli --------------------
from telethon import TelegramClient, events

api_id = 123456          # my.telegram.org'dan -- ILOVANI aniqlaydi
api_hash = "abcdef0123456789abcdef0123456789"

# "session_name" -- diskdagi session fayl nomi (2-darsda batafsil).
# Birinchi ishga tushirishda telefon raqami + kod so'raladi -- shundan
# keyin bu HAQIQIY FOYDALANUVCHI HISOBI nomidan ishlaydigan client.
client = TelegramClient("session_name", api_id, api_hash)


@client.on(events.NewMessage(pattern="/ping"))
async def telethon_ping(event: events.NewMessage.Event) -> None:
    # Bu handler HAR QANDAY chatda ishlaydi -- shaxsiy, guruh, kanal --
    # chunki bu endi "botga kelgan update" emas, balki "hisobim
    # ishtirok etayotgan har qanday suhbatdagi yangi xabar" hodisasi.
    await event.reply("pong (Telethon/MTProto orqali)")


# with client:
#     client.run_until_disconnected()


# --- 3) Imkoniyatlar solishtiruvi -- shu darsning asosiy xulosasi ----
BOT_API_CAPABILITIES = {
    "faqat o'ziga tegishli xabarlarni ko'radi": True,
    "guruhning eski tarixini o'qiydi (admin bo'lmasa)": False,
    "username orqali kanalga o'zi qo'shiladi": False,
    "kontaktlar/dialoglar ro'yxatiga kiradi": False,
    "odam sifatida ko'rinadi (Bot belgisisiz)": False,
}

USERBOT_CAPABILITIES = {
    "faqat o'ziga tegishli xabarlarni ko'radi": False,  # barchasini ko'radi
    "guruhning eski tarixini o'qiydi (admin bo'lmasa)": True,
    "username orqali kanalga o'zi qo'shiladi": True,
    "kontaktlar/dialoglar ro'yxatiga kiradi": True,
    "odam sifatida ko'rinadi (Bot belgisisiz)": True,
}


def print_comparison() -> None:
    print(f"{'Imkoniyat':<55}{'Bot API':>10}{'Userbot':>10}")
    for key in BOT_API_CAPABILITIES:
        print(f"{key:<55}{str(BOT_API_CAPABILITIES[key]):>10}{str(USERBOT_CAPABILITIES[key]):>10}")


if __name__ == "__main__":
    print_comparison()
""",
"code_content_ru": """# ============================================================
# Bot API (aiogram) vs MTProto (Telethon) -- одна задача, два подхода
# ============================================================

# --- 1) aiogram (Bot API) -- знакомая форма из курса 48 --------------
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

bot = Bot(token="123456:BOT_TOKEN")          # идентифицирует АККАУНТ БОТА
dp = Dispatcher()
router = Router()


@router.message(Command("ping"))
async def aiogram_ping(message: Message) -> None:
    # Этот обработчик отвечает только на /ping, отправленный боту.
    # Бот видит только: (а) сообщения, адресованные ему, (б) сообщения
    # в группе после его добавления -- прочитать старую историю группы
    # он не может.
    await message.answer("pong (через Bot API)")


dp.include_router(router)
# asyncio.run(dp.start_polling(bot))


# --- 2) Telethon (MTProto) -- форма этого курса ----------------------
from telethon import TelegramClient, events

api_id = 123456          # с my.telegram.org -- идентифицирует ПРИЛОЖЕНИЕ
api_hash = "abcdef0123456789abcdef0123456789"

# "session_name" -- имя файла сессии на диске (подробно в уроке 2).
# При первом запуске запросит номер телефона + код -- после этого
# это клиент, работающий от имени НАСТОЯЩЕГО АККАУНТА ПОЛЬЗОВАТЕЛЯ.
client = TelegramClient("session_name", api_id, api_hash)


@client.on(events.NewMessage(pattern="/ping"))
async def telethon_ping(event: events.NewMessage.Event) -> None:
    # Этот обработчик срабатывает в ЛЮБОМ чате -- личном, группе,
    # канале -- потому что это уже не "апдейт, пришедший боту", а
    # событие "новое сообщение в любом диалоге, где участвует мой аккаунт".
    await event.reply("pong (через Telethon/MTProto)")


# with client:
#     client.run_until_disconnected()


# --- 3) Сравнение возможностей -- главный вывод этого урока ----------
BOT_API_CAPABILITIES = {
    "видит только адресованные ему сообщения": True,
    "читает старую историю группы (без прав админа)": False,
    "сам вступает в канал по username": False,
    "имеет доступ к списку контактов/диалогов": False,
    "выглядит как человек (без пометки Bot)": False,
}

USERBOT_CAPABILITIES = {
    "видит только адресованные ему сообщения": False,  # видит всё
    "читает старую историю группы (без прав админа)": True,
    "сам вступает в канал по username": True,
    "имеет доступ к списку контактов/диалогов": True,
    "выглядит как человек (без пометки Bot)": True,
}


def print_comparison() -> None:
    print(f"{'Возможность':<55}{'Bot API':>10}{'Userbot':>10}")
    for key in BOT_API_CAPABILITIES:
        print(f"{key:<55}{str(BOT_API_CAPABILITIES[key]):>10}{str(USERBOT_CAPABILITIES[key]):>10}")


if __name__ == "__main__":
    print_comparison()
""",
"task": {
"task_title": """Amaliy: Bot API va Userbot imkoniyatlar jadvalini kengaytiring""",
"task_title_ru": """Практика: расширьте таблицу возможностей Bot API и юзербота""",
"task_description": """1-darsdagi BOT_API_CAPABILITIES / USERBOT_CAPABILITIES lug'atlariga kamida 4 ta yangi qator qo'shing (masalan: "guruh a'zolari ro'yxatini to'liq ko'radi", "media faylni progress bilan yuklab oladi", "bir vaqtda bir nechta hisobni boshqaradi" va h.k.) va print_comparison() funksiyasini ikkala lug'at bo'yicha to'g'ri chiqishini tekshiring.""",
"task_description_ru": """Добавьте в словари BOT_API_CAPABILITIES / USERBOT_CAPABILITIES из урока 1 минимум 4 новые строки (например: "видит полный список участников группы", "скачивает медиафайл с прогрессом", "управляет несколькими аккаунтами одновременно" и т.д.) и проверьте, что print_comparison() корректно выводит обе таблицы.""",
"task_requirements": """Kamida 4 ta yangi imkoniyat qo'shilgan bo'lishi; ikkala lug'atda bir xil kalitlar bo'lishi shart; print_comparison() xatosiz ishlashi kerak.""",
"task_requirements_ru": """Добавлено минимум 4 новые возможности; в обоих словарях должны быть одинаковые ключи; print_comparison() должен работать без ошибок.""",
"task_technologies": "Python 3.11+, Telethon (kontseptual)",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: Bot API vs Userbot imkoniyatlar solishtiruv skripti""",
"description": """To'liq ishga tushiriladigan Python skripti -- login talab qilmaydi, faqat ikkala yondashuv imkoniyatlarini jadval qilib chiqaradi""",
"sample_type": "code",
"code_files": [
{"filename": "capability_matrix.py", "language": "python", "code": """\"\"\"Bot API vs Telethon userbot -- imkoniyatlar solishtiruvi.
Login talab qilmaydi -- faqat kontseptual jadval chiqaradi.
Ishga tushirish: python capability_matrix.py
\"\"\"

CAPABILITIES = [
    ("Faqat o'ziga tegishli xabarlarni ko'rish", True, False),
    ("Guruhning eski tarixini o'qish (admin bo'lmasa)", False, True),
    ("Username orqali kanalga o'zi qo'shilish", False, True),
    ("Kontaktlar/dialoglar ro'yxatiga to'liq kirish", False, True),
    ("Odam sifatida ko'rinish (Bot belgisisiz)", False, True),
    ("BotFather orqali ro'yxatdan o'tish", True, False),
    ("Telefon raqami orqali login", False, True),
    ("Inline rejim va shu kabi bot-maxsus API'lar", True, False),
]


def render_table() -> str:
    header = f"{'Imkoniyat':<50} | {'Bot API':^8} | {'Userbot':^8}"
    lines = [header, "-" * len(header)]
    for label, bot_ok, userbot_ok in CAPABILITIES:
        lines.append(f"{label:<50} | {str(bot_ok):^8} | {str(userbot_ok):^8}")
    return "\\n".join(lines)


if __name__ == "__main__":
    print(render_table())
    total_userbot_only = sum(1 for _, b, u in CAPABILITIES if u and not b)
    print(f"\\nFaqat userbotga xos imkoniyatlar soni: {total_userbot_only}")
"""},
],
},
"exercises": [
{
"title": """Bot API va MTProto: kim bilan kim gaplashadi""",
"title_ru": """Bot API и MTProto: кто с кем говорит""",
"description": """aiogram bot ishlatganda, sizning kodingiz MTProto bilan to'g'ridan-to'g'ri gaplashadimi?""",
"description_ru": """Когда вы используете бота на aiogram, ваш код говорит с MTProto напрямую?""",
"exercise_type": "multiple_choice",
"options": ["Ha, har doim to'g'ridan-to'g'ri", "Yo'q, Bot API server (Telegram) vositachilik qiladi", "Yo'q, chunki aiogram MTProto'ni umuman ishlatmaydi", "Ha, lekin faqat webhook rejimida"],
"options_ru": ["Да, всегда напрямую", "Нет, посредничает сервер Bot API (сам Telegram)", "Нет, потому что aiogram вообще не использует MTProto", "Да, но только в режиме webhook"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bot API — bu MTProto ustiga qurilgan HTTPS qatlam.""",
"hint_ru": """Bot API — это HTTPS-слой поверх MTProto.""",
"explanation": """Bot API serveri (api.telegram.org) sizning HTTPS so'rovingizni qabul qilib, uni ichkarida MTProto'ga o'zi tarjima qiladi. Sizning kodingiz MTProto bilan hech qachon bevosita gaplashmaydi.""",
"difficulty_level": "Easy",
"points": 8,
},
{
"title": """Userbot nima uchun kerak bo'lishi mumkin""",
"title_ru": """Зачем может понадобиться юзербот""",
"description": """Quyidagilardan qaysi biri FAQAT userbot (Telethon) orqali mumkin, oddiy bot orqali EMAS?""",
"description_ru": """Что из перечисленного возможно ТОЛЬКО через юзербота (Telethon), но НЕ через обычного бота?""",
"exercise_type": "multiple_choice",
"options": ["/start buyrug'iga javob berish", "Inline klaviatura ko'rsatish", "Administrator bo'lmasdan kanalning eski tarixini o'qish", "Webhook orqali update qabul qilish"],
"options_ru": ["Ответ на команду /start", "Показ inline-клавиатуры", "Чтение старой истории канала без прав администратора", "Приём апдейтов через webhook"],
"correct_answers": "C",
"is_multiple_select": False,
"hint": """Bot faqat o'ziga tegishli yoki qo'shilgandan keyingi xabarlarni ko'radi.""",
"hint_ru": """Бот видит только адресованные ему или отправленные после его добавления сообщения.""",
"explanation": """Oddiy bot guruh/kanalning o'zi qo'shilishidan oldingi tarixini hech qachon o'qiy olmaydi, hatto admin bo'lsa ham (Bot API bunga umuman API bermaydi). Userbot esa, agar hisob shu chatga a'zo bo'lsa, to'liq tarixni o'qiy oladi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Arxitektura qatlamlarini tartiblang: Bot API yo'li""",
"title_ru": """Расположите по порядку слои архитектуры: путь Bot API""",
"description": """aiogram bot xabar yuborganda, so'rov qanday tartibda o'tadi? To'g'ri ketma-ketlikni tuzing.""",
"description_ru": """Когда бот на aiogram отправляет сообщение, в каком порядке проходит запрос? Составьте правильную последовательность.""",
"exercise_type": "drag_and_drop",
"drag_items": ["Sizning aiogram kodingiz", "HTTPS so'rov (Bot API metodi)", "api.telegram.org (Bot API server)", "MTProto (ichki tarjima)", "Telegram core datacenter"],
"drag_items_ru": ["Ваш код на aiogram", "HTTPS-запрос (метод Bot API)", "api.telegram.org (сервер Bot API)", "MTProto (внутренний перевод)", "Дата-центр ядра Telegram"],
"correct_order": ["Sizning aiogram kodingiz", "HTTPS so'rov (Bot API metodi)", "api.telegram.org (Bot API server)", "MTProto (ichki tarjima)", "Telegram core datacenter"],
"hint": """Kod avval HTTPS orqali Bot API serverga, keyin u ichkarida MTProto'ga murojaat qiladi.""",
"hint_ru": """Код сначала обращается по HTTPS к серверу Bot API, а тот уже внутри — к MTProto.""",
"difficulty_level": "Easy",
"points": 7,
},
{
"title": """Protokol nomi""",
"title_ru": """Название протокола""",
"description": """Telethon va Telegram'ning rasmiy ilovalari ishlatadigan xom protokol nomi: ___""",
"description_ru": """Название сырого протокола, который используют Telethon и официальные приложения Telegram: ___""",
"exercise_type": "fill_in_blank",
"correct_answers": "MTProto",
"hint": """Bot API shu protokol ustiga qurilgan qatlam.""",
"hint_ru": """Bot API — это слой, построенный поверх этого протокола.""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 1,
"title": """2-api_id/api_hash olish va birinchi TelegramClient login""",
"title_ru": """2-Получение api_id/api_hash и первый вход через TelegramClient""",
"points_reward": 17,
"code_language": "python",
"text_content": """<h3>my.telegram.org: ilovangizni ro'yxatdan o'tkazish</h3>
<p>Telethon ishlashi uchun avvalo <strong>ilovangizga</strong> shaxsiy raqam kerak &mdash; xuddi har qanday rasmiy Telegram klienti (mobil, desktop) o'zining <code>api_id</code>/<code>api_hash</code> juftligiga ega bo'lgani kabi. Buni olish jarayoni:</p>
<ol>
<li><a href="https://my.telegram.org">my.telegram.org</a> saytiga o'z telefon raqamingiz bilan kiring (SMS/ilova orqali tasdiqlash kodi keladi).</li>
<li>"API development tools" bo'limiga o'ting.</li>
<li>"Create new application" formasini to'ldiring: <code>App title</code> va <code>Short name</code> &mdash; bular ixtiyoriy, faqat sizga ko'rinadi, boshqa foydalanuvchilarga ko'rsatilmaydi. <code>Platform</code> maydonida "Desktop" yoki "Other" tanlash odatiy.</li>
<li>Yuborilgach, sizga ikkita qiymat beriladi: <code>api_id</code> (butun son, masalan <code>2040</code> kabi ko'rinishda) va <code>api_hash</code> (32 belgili hex qator).</li>
</ol>
<p>Bu juftlik <strong>hisobingiz emas, ilovangizni</strong> aniqlaydi. Bitta Telegram hisobi bir nechta ilova (api_id) yaratishi mumkin, va bitta api_id/api_hash orqali istalgan hisob login qila oladi &mdash; ya'ni ular login qilinayotgan HISOBni belgilamaydi, faqat "qaysi ilova nomidan ulanilyapti"ni bildiradi. Shunga qaramay, ularni ochiq repositoryga commit qilmang: Telegram noodatiy trafik ko'rgan taqdirda butun api_id'ni cheklashi mumkin, va bu sizning barcha loyihalaringizga ta'sir qiladi.</p>
<h3>O'rnatish va birinchi client</h3>
<p><code>pip install telethon</code> &mdash; boshqa tashqi bog'liqlik shart emas (Telethon MTProto'ni sof Python'da amalga oshiradi, hech qanday C kengaytmasiga muhtoj emas). Asosiy obyekt &mdash; <code>TelegramClient</code>:</p>
<pre class="mermaid">
flowchart TB
  A["TelegramClient('nomi', api_id, api_hash) yaratiladi"] --> B{"'nomi.session' fayli\nmavjudmi?"}
  B -- "Yo'q (birinchi marta)" --> C["Telefon raqami so'raladi"]
  C --> D["Telegram SMS/ilova orqali kod yuboradi"]
  D --> E["Kod kiritiladi"]
  E --> F{"2FA (bulutli parol)\nyoqilganmi?"}
  F -- "Ha" --> G["Parol so'raladi"]
  F -- "Yo'q" --> H["Login tugadi"]
  G --> H
  B -- "Ha (keyingi ishga tushirishlarda)" --> H
  H --> I["'nomi.session' faylga auth_key yoziladi/o'qiladi"]
</pre>
<p>Diagramma shuni ko'rsatadi: to'liq login jarayoni (telefon + kod + 2FA) faqat <strong>birinchi marta</strong> sodir bo'ladi. Muvaffaqiyatli logindan so'ng, natija (auth_key va boshqa metama'lumot) diskdagi <code>nomi.session</code> fayliga yoziladi &mdash; keyingi ishga tushirishlarda Telethon shu faylni o'qiydi va hech narsa qayta so'ramaydi. Bu faylning nima ekanligi va nega u parol darajasida xavfiy ekanligi &mdash; keyingi darsning butun mavzusi.</p>
<h3>Interaktiv vs skript rejimida login</h3>
<p><code>client.start()</code> &mdash; eng qulay yo'l: agar session hali bo'lmasa, u konsolda telefon, kod va (kerak bo'lsa) parolni <em>o'zi so'raydi</em>. Bu qo'lda ishga tushiriladigan skriptlar uchun ajoyib, lekin serverda avtomatik (masalan systemd orqali) ishga tushadigan kodda konsol input yo'q &mdash; shu sababli <code>phone=</code>, <code>code_callback=</code>, <code>password=</code> parametrlarini funksiya sifatida berish mumkin, yoki quyi darajadagi <code>send_code_request()</code> / <code>sign_in()</code> metodlaridan alohida foydalanish mumkin (masalan, kodni Telegram orqali emas, boshqa kanal &mdash; email yoki admin panel &mdash; orqali kiritish kerak bo'lsa).</p>
<h3>Xatoliklar bilan ishlash</h3>
<p>Login jarayonida bir nechta muhim istisno turlari bor: <code>PhoneNumberInvalidError</code> (raqam formati noto'g'ri), <code>PhoneCodeInvalidError</code> (kod noto'g'ri kiritildi), <code>SessionPasswordNeededError</code> (2FA yoqilgan &mdash; parol kerak) va <code>FloodWaitError</code> (juda ko'p urinish &mdash; belgilangan soniyagacha kutish kerak). Bularni to'g'ri ushlamaslik &mdash; ishlab chiqarish kodida eng ko'p uchraydigan xato: skript oddiy <code>except Exception</code> bilan hammasini yutib yuborsa, nima uchun login muvaffaqiyatsiz bo'lganini hech qachon bilmaysiz.</p>
<h3>Ilova versiyasi va qurilma ma'lumotlari</h3>
<p><code>TelegramClient</code> konstruktorida ixtiyoriy <code>device_model</code>, <code>system_version</code>, <code>app_version</code> parametrlari ham bor &mdash; ular Telegram'ning "Active Sessions" ro'yxatida qaysi qurilma sifatida ko'rinishingizni belgilaydi. Standart holatda Telethon o'z versiyasini ko'rsatadi; ko'plab o'quv loyihalarida buni o'zgartirishning hojati yo'q, lekin ishlab chiqarishda tushunarli nom qo'yish (masalan <code>"MonitorBot v1"</code>) keyinchalik "Active Sessions"da qaysi skript qaysi ekanini ajratishga yordam beradi.</p>""",
"text_content_ru": """<h3>my.telegram.org: регистрация вашего приложения</h3>
<p>Для работы Telethon сначала нужен персональный номер для <strong>вашего приложения</strong> &mdash; точно так же, как у любого официального клиента Telegram (мобильного, десктопного) есть своя пара <code>api_id</code>/<code>api_hash</code>. Процесс получения:</p>
<ol>
<li>Войдите на <a href="https://my.telegram.org">my.telegram.org</a> по своему номеру телефона (придёт код подтверждения по SMS/приложению).</li>
<li>Перейдите в раздел "API development tools".</li>
<li>Заполните форму "Create new application": <code>App title</code> и <code>Short name</code> &mdash; произвольные, видны только вам, другим пользователям не показываются. В поле <code>Platform</code> обычно выбирают "Desktop" или "Other".</li>
<li>После отправки вы получите два значения: <code>api_id</code> (целое число, например в виде <code>2040</code>) и <code>api_hash</code> (hex-строка из 32 символов).</li>
</ol>
<p>Эта пара идентифицирует <strong>не аккаунт, а приложение</strong>. Один аккаунт Telegram может создать несколько приложений (api_id), и через одну пару api_id/api_hash может войти любой аккаунт &mdash; то есть они не определяют, КАКОЙ аккаунт входит, а только "от имени какого приложения происходит подключение". Тем не менее не коммитьте их в открытый репозиторий: при подозрительном трафике Telegram может ограничить весь api_id, что затронет все ваши проекты.</p>
<h3>Установка и первый клиент</h3>
<p><code>pip install telethon</code> &mdash; других внешних зависимостей не нужно (Telethon реализует MTProto на чистом Python, без C-расширений). Основной объект &mdash; <code>TelegramClient</code>:</p>
<pre class="mermaid">
flowchart TB
  A["Создаётся TelegramClient('имя', api_id, api_hash)"] --> B{"Файл 'имя.session'\nсуществует?"}
  B -- "Нет (первый запуск)" --> C["Запрашивается номер телефона"]
  C --> D["Telegram отправляет код по SMS/приложению"]
  D --> E["Код вводится"]
  E --> F{"Включена 2FA\n(облачный пароль)?"}
  F -- "Да" --> G["Запрашивается пароль"]
  F -- "Нет" --> H["Логин завершён"]
  G --> H
  B -- "Да (при следующих запусках)" --> H
  H --> I["auth_key записывается/читается из файла 'имя.session'"]
</pre>
<p>Диаграмма показывает: полный процесс логина (телефон + код + 2FA) происходит только <strong>один раз, при первом запуске</strong>. После успешного входа результат (auth_key и другие метаданные) записывается в файл <code>имя.session</code> на диске &mdash; при следующих запусках Telethon просто читает этот файл и ничего заново не спрашивает. Что это за файл и почему он опасен на уровне пароля &mdash; тема следующего урока полностью.</p>
<h3>Интерактивный вход vs вход в скрипте</h3>
<p><code>client.start()</code> &mdash; самый удобный способ: если сессии ещё нет, он <em>сам</em> спросит в консоли телефон, код и (если нужно) пароль. Это отлично для скриптов, запускаемых вручную, но в коде, автоматически запускаемом на сервере (например, через systemd), консольного ввода нет &mdash; поэтому можно передать параметры <code>phone=</code>, <code>code_callback=</code>, <code>password=</code> как функции, либо использовать методы более низкого уровня <code>send_code_request()</code> / <code>sign_in()</code> отдельно (например, если код нужно вводить не из Telegram, а через другой канал &mdash; почту или админ-панель).</p>
<h3>Обработка ошибок</h3>
<p>В процессе логина есть несколько важных типов исключений: <code>PhoneNumberInvalidError</code> (неверный формат номера), <code>PhoneCodeInvalidError</code> (код введён неверно), <code>SessionPasswordNeededError</code> (включена 2FA &mdash; нужен пароль) и <code>FloodWaitError</code> (слишком много попыток &mdash; нужно подождать указанное число секунд). Неправильная обработка этого &mdash; самая частая ошибка в продакшен-коде: если скрипт ловит всё простым <code>except Exception</code>, вы никогда не узнаете, почему логин не удался.</p>
<h3>Версия приложения и данные устройства</h3>
<p>В конструкторе <code>TelegramClient</code> есть также необязательные параметры <code>device_model</code>, <code>system_version</code>, <code>app_version</code> &mdash; они определяют, как ваш клиент будет выглядеть в списке "Active Sessions" Telegram. По умолчанию Telethon показывает свою версию; во многих учебных проектах менять это не обязательно, но в продакшене понятное имя (например <code>"MonitorBot v1"</code>) поможет позже отличить, какой скрипт есть какой в "Active Sessions".</p>""",
"code_content": """\"\"\"Birinchi Telethon client -- interaktiv login (qo'lda ishga tushiriladigan skript).
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
)

load_dotenv()  # .env faylidan API_ID / API_HASH / PHONE ni o'qiydi

API_ID = int(os.environ["API_ID"])          # .env: API_ID=2040...
API_HASH = os.environ["API_HASH"]           # .env: API_HASH=abcdef...
PHONE = os.environ.get("PHONE")             # ixtiyoriy -- berilmasa so'raydi

# device_model/app_version -- ixtiyoriy, "Active Sessions"da ko'rinadigan nom
client = TelegramClient(
    "session_name",
    API_ID,
    API_HASH,
    device_model="Telethon Kurs Namunasi",
    app_version="1.0",
)


async def interactive_login() -> None:
    \"\"\"client.start() -- eng oddiy yo'l: kerak bo'lsa o'zi so'raydi.\"\"\"
    await client.start(phone=PHONE)
    me = await client.get_me()
    print(f"Muvaffaqiyatli login: {me.first_name} (id={me.id}, @{me.username})")


async def manual_login_flow() -> None:
    \"\"\"Quyi darajadagi, qadam-baqadam login -- serverda avtomatik
    ishga tushiriladigan skriptlar uchun (masalan, kod boshqa kanaldan
    kelganda, yoki xatolarni alohida ushlash kerak bo'lganda) foydali.\"\"\"
    await client.connect()

    if await client.is_user_authorized():
        print("Session allaqachon mavjud -- login shart emas.")
        return

    phone = PHONE or input("Telefon raqamini kiriting (+998...): ")
    try:
        sent = await client.send_code_request(phone)
    except PhoneNumberInvalidError:
        print("Telefon raqami formati noto'g'ri.")
        return
    except FloodWaitError as e:
        print(f"Juda ko'p urinish -- {e.seconds} soniya kutish kerak.")
        return

    code = input("Telegram yuborgan kodni kiriting: ")
    try:
        await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
    except PhoneCodeInvalidError:
        print("Kod noto'g'ri kiritildi.")
        return
    except SessionPasswordNeededError:
        password = input("2FA (bulutli) parolni kiriting: ")
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"Qo'lda login muvaffaqiyatli: {me.first_name} (id={me.id})")


async def main() -> None:
    await manual_login_flow()
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Первый клиент Telethon -- интерактивный вход (запускаемый вручную скрипт).
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
)

load_dotenv()  # читает API_ID / API_HASH / PHONE из файла .env

API_ID = int(os.environ["API_ID"])          # .env: API_ID=2040...
API_HASH = os.environ["API_HASH"]           # .env: API_HASH=abcdef...
PHONE = os.environ.get("PHONE")             # необязательно -- если нет, спросит сам

# device_model/app_version -- необязательно, имя видно в "Active Sessions"
client = TelegramClient(
    "session_name",
    API_ID,
    API_HASH,
    device_model="Пример курса Telethon",
    app_version="1.0",
)


async def interactive_login() -> None:
    \"\"\"client.start() -- самый простой способ: спросит сам, если нужно.\"\"\"
    await client.start(phone=PHONE)
    me = await client.get_me()
    print(f"Успешный вход: {me.first_name} (id={me.id}, @{me.username})")


async def manual_login_flow() -> None:
    \"\"\"Пошаговый вход низкого уровня -- полезен для скриптов, автоматически
    запускаемых на сервере (например, если код приходит по другому каналу,
    или нужно отдельно обрабатывать ошибки).\"\"\"
    await client.connect()

    if await client.is_user_authorized():
        print("Сессия уже существует -- вход не нужен.")
        return

    phone = PHONE or input("Введите номер телефона (+998...): ")
    try:
        sent = await client.send_code_request(phone)
    except PhoneNumberInvalidError:
        print("Неверный формат номера телефона.")
        return
    except FloodWaitError as e:
        print(f"Слишком много попыток -- нужно подождать {e.seconds} секунд.")
        return

    code = input("Введите код, присланный Telegram: ")
    try:
        await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
    except PhoneCodeInvalidError:
        print("Код введён неверно.")
        return
    except SessionPasswordNeededError:
        password = input("Введите пароль 2FA (облачный): ")
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"Ручной вход выполнен успешно: {me.first_name} (id={me.id})")


async def main() -> None:
    await manual_login_flow()
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: to'liq xatolik-boshqaruvli login skripti""",
"task_title_ru": """Практика: скрипт входа с полной обработкой ошибок""",
"task_description": """manual_login_flow() funksiyasini asos qilib, o'zingizning api_id/api_hash bilan (my.telegram.org'dan olingan) haqiqiy login skriptini yozing. Skript PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError va FloodWaitError holatlarini alohida ushlab, foydalanuvchiga tushunarli xabar chiqarishi kerak.""",
"task_description_ru": """На основе функции manual_login_flow() напишите реальный скрипт входа со своими api_id/api_hash (полученными на my.telegram.org). Скрипт должен отдельно обрабатывать PhoneNumberInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError и FloodWaitError, выводя понятное пользователю сообщение.""",
"task_requirements": """api_id/api_hash .env fayldan o'qilishi kerak (koddа hardcoded bo'lmasin); kamida 4 xil istisno alohida ushlangan bo'lishi; muvaffaqiyatli logindan keyin client.get_me() natijasi chiqarilishi kerak.""",
"task_requirements_ru": """api_id/api_hash должны читаться из .env файла (не hardcoded в коде); минимум 4 разных исключения должны обрабатываться отдельно; после успешного входа должен выводиться результат client.get_me().""",
"task_technologies": "Python 3.11+, Telethon, python-dotenv",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: .env asosidagi xavfsiz login skripti""",
"description": """api_id/api_hash'ni muhit o'zgaruvchilaridan o'qiydigan, to'liq xatolik-boshqaruvli login skripti""",
"sample_type": "code",
"code_files": [
{"filename": ".env.example", "language": "bash", "code": """API_ID=2040
API_HASH=abcdef0123456789abcdef0123456789
PHONE=+998901234567
"""},
{"filename": "login.py", "language": "python", "code": """import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
)

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

client = TelegramClient("namuna_session", API_ID, API_HASH)


async def main() -> None:
    await client.connect()
    if not await client.is_user_authorized():
        phone = os.environ.get("PHONE") or input("Telefon: ")
        try:
            sent = await client.send_code_request(phone)
            code = input("Kod: ")
            await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
        except SessionPasswordNeededError:
            await client.sign_in(password=input("2FA parol: "))
        except (PhoneNumberInvalidError, PhoneCodeInvalidError) as e:
            print(f"Login xatosi: {e}")
            return
        except FloodWaitError as e:
            print(f"{e.seconds} soniya kutish kerak.")
            return

    me = await client.get_me()
    print(f"Salom, {me.first_name}! (id={me.id})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
"""},
],
},
"exercises": [
{
"title": """api_id/api_hash nimani aniqlaydi""",
"title_ru": """Что идентифицируют api_id/api_hash""",
"description": """api_id va api_hash juftligi asosan nimani aniqlaydi?""",
"description_ru": """Что в первую очередь идентифицирует пара api_id и api_hash?""",
"exercise_type": "multiple_choice",
"options": ["Aniq Telegram hisobini (foydalanuvchini)", "Ilovani (qaysi dastur nomidan ulanilayotganini)", "Foydalanuvchining 2FA parolini", "Session faylning joylashuvini"],
"options_ru": ["Конкретный аккаунт Telegram (пользователя)", "Приложение (от имени какой программы идёт подключение)", "Пароль 2FA пользователя", "Расположение файла сессии"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bitta api_id orqali istalgan hisob login qila oladi.""",
"hint_ru": """Через один api_id может войти любой аккаунт.""",
"explanation": """api_id/api_hash ilovani aniqlaydi, hisobni emas — login qilish uchun alohida telefon+kod (va ehtimol 2FA) jarayoni kerak.""",
"difficulty_level": "Easy",
"points": 8,
},
{
"title": """Session fayl mavjud bo'lganda""",
"title_ru": """Когда файл сессии уже существует""",
"description": """Agar 'nomi.session' fayli allaqachon mavjud bo'lsa, client.start() qayta ishga tushirilganda nima sodir bo'ladi?""",
"description_ru": """Если файл 'имя.session' уже существует, что произойдёт при повторном запуске client.start()?""",
"exercise_type": "multiple_choice",
"options": ["Telefon va kod qayta so'raladi", "Hech narsa so'ralmaydi -- mavjud session ishlatiladi", "Xatolik chiqadi, session o'chirilishi kerak", "Yangi api_id talab qilinadi"],
"options_ru": ["Телефон и код запрашиваются заново", "Ничего не спрашивается -- используется существующая сессия", "Возникает ошибка, сессию нужно удалить", "Требуется новый api_id"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Session fayl auth_key'ni saqlaydi -- shuning uchun keyingi safar qayta login shart emas.""",
"hint_ru": """Файл сессии хранит auth_key -- поэтому повторный вход не нужен.""",
"explanation": """.session fayl mavjud bo'lsa va u haqiqiy bo'lsa, Telethon uni o'qib, avtorizatsiyani tiklaydi -- telefon/kod faqat birinchi marta so'raladi.""",
"difficulty_level": "Easy",
"points": 5,
},
{
"title": """Login jarayonini tartiblang""",
"title_ru": """Расположите процесс входа по порядку""",
"description": """Birinchi marta ishga tushirilayotgan skriptda to'liq login jarayonining to'g'ri ketma-ketligini tuzing.""",
"description_ru": """Составьте правильную последовательность полного процесса входа при первом запуске скрипта.""",
"exercise_type": "drag_and_drop",
"drag_items": ["my.telegram.org'dan api_id/api_hash olish", "TelegramClient obyektini yaratish", "send_code_request() bilan telefon raqamini yuborish", "Telegram yuborgan kodni sign_in() bilan kiritish", "(agar 2FA yoqilgan bo'lsa) parolni kiritish"],
"drag_items_ru": ["Получить api_id/api_hash на my.telegram.org", "Создать объект TelegramClient", "Отправить номер телефона через send_code_request()", "Ввести код от Telegram через sign_in()", "(если включена 2FA) ввести пароль"],
"correct_order": ["my.telegram.org'dan api_id/api_hash olish", "TelegramClient obyektini yaratish", "send_code_request() bilan telefon raqamini yuborish", "Telegram yuborgan kodni sign_in() bilan kiritish", "(agar 2FA yoqilgan bo'lsa) parolni kiritish"],
"hint": """Avval ilova ma'lumotlari, keyin client, keyin telefon, keyin kod, oxirida (agar kerak bo'lsa) 2FA.""",
"hint_ru": """Сначала данные приложения, потом клиент, потом телефон, потом код, в конце (если нужно) 2FA.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """2FA xatoligi klassi""",
"title_ru": """Класс исключения для 2FA""",
"description": """Hisobda 2FA (bulutli parol) yoqilgan bo'lsa, kod to'g'ri kiritilgandan keyin Telethon qaysi istisno klassini ko'taradi: ___""",
"description_ru": """Если в аккаунте включена 2FA (облачный пароль), какое исключение выбрасывает Telethon после правильно введённого кода: ___""",
"exercise_type": "fill_in_blank",
"correct_answers": "SessionPasswordNeededError",
"hint": """Nomi to'g'ridan-to'g'ri "parol kerak" degan ma'noni bildiradi.""",
"hint_ru": """Название буквально означает "нужен пароль".""",
"difficulty_level": "Medium",
"points": 8,
},
],
},
{
"order": 2,
"title": """3-Session string va session fayl: nega oqib ketgan session -- hisobni to'liq qo'lga olish demakdir""",
"title_ru": """3-Session-строка и файл сессии: почему их утечка равносильна полному захвату аккаунта""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>Session nima -- texnik jihatdan</h3>
<p>2-darsda login muvaffaqiyatli o'tgach, Telethon <code>auth_key</code> deb ataladigan qiymatni oladi &mdash; bu Diffie-Hellman kalit almashinuvi natijasida hosil bo'lgan, sizning clientingiz bilan Telegram'ning muayyan datacentri (DC) orasidagi <strong>umumiy maxfiy kalit</strong>. Shu kalit mavjud bo'lsa, qo'shimcha parol, SMS yoki 2FA'siz, o'sha hisob nomidan MTProto so'rovlarini yuborish mumkin &mdash; chunki server nuqtai nazaridan bu allaqachon "tasdiqlangan" ulanish. Standart <code>TelegramClient("nomi", ...)</code> bu kalitni <code>nomi.session</code> nomli SQLite faylida saqlaydi (DC raqami, port va boshqa metama'lumotlar bilan birga).</p>
<h3>StringSession -- bir qatorli, portativ shakl</h3>
<p>Ba'zan fayl tizimiga yozish noqulay (serverless muhitlar, konteynerlar, CI) yoki session'ni bitta muhit o'zgaruvchisi sifatida saqlash qulayroq. <code>StringSession</code> xuddi shu <code>auth_key</code> va metama'lumotlarni SQLite fayl o'rniga bitta base64-ga o'xshash matn qatoriga seriyalashtiradi:</p>
<pre class="mermaid">
flowchart LR
  A["Muvaffaqiyatli login"] --> B["auth_key + DC ma'lumoti"]
  B --> C["Fayl: nomi.session (SQLite)"]
  B --> D["Yoki: StringSession -- bitta matn qatori"]
  C --> E["Diskda saqlanadi"]
  D --> F["Muhit o'zgaruvchisi / secrets manager'da saqlanadi"]
</pre>
<p>Ikkalasi ham &mdash; fayl ham, satr ham &mdash; MAZMUNAN bir xil narsa: to'liq, tayyor autentifikatsiya. Ular orasidagi farq faqat saqlash formatida, xavfsizlik darajasida emas.</p>
<h3>Nega bu parol darajasida (undan ham xavfliroq) xavfli</h3>
<p>Parol oqib ketsa, hujumchi baribir login jarayonidan o'tishi kerak &mdash; agar 2FA yoqilgan bo'lsa, u ham kerak bo'ladi. Session string/fayl oqib ketsa esa, hujumchi <strong>login jarayonini butunlay chetlab o'tadi</strong>: u shunchaki <code>TelegramClient(StringSession(oqib_ketgan_qator), api_id, api_hash)</code> yaratadi va darhol, hech qanday parol yoki kod so'ralmasdan, sizning hisobingiz nomidan xabar o'qiy oladi, yubora oladi, hatto <strong>2FA parolni o'zgartirib, sizni hisobingizdan chiqarib qo'yishi</strong> ham mumkin. Bu &mdash; nega bu kursda session xavfsizligiga alohida bob ajratilganining sababi: bu 123-kursda o'rgatilgan Mini App initData xavfsizligiga parallel, lekin oqibati ancha og'irroq muammo.</p>
<pre class="mermaid">
flowchart TB
  A["Session string tasodifan commit qilinadi\n(masalan .env fayl git'ga qo'shiladi)"] --> B["Hujumchi GitHub tarixidan uni topadi"]
  B --> C["TelegramClient(StringSession(topilgan_qator), ...)"]
  C --> D["Darhol to'liq kirish -- parol/2FA/kod SHART EMAS"]
  D --> E["Xabarlarni o'qish, yuborish, kontaktlarga spam"]
  D --> F["2FA parolni o'zgartirib, egasini bloklash"]
</pre>
<h3>Amaliy qoidalar</h3>
<ul>
<li><strong>Hech qachon</strong> <code>*.session</code> faylni yoki session string qiymatini git'ga commit qilmang &mdash; <code>.gitignore</code>ga <code>*.session</code> qo'shing.</li>
<li>Session string'ni faqat muhit o'zgaruvchisi yoki secrets manager (masalan, serverning maxfiy o'zgaruvchilar bo'limi) orqali uzating &mdash; hech qachon chatga, log fayliga, xatolik xabariga yozmang.</li>
<li>Agar session oqib ketgan deb gumon qilsangiz &mdash; darhol Telegram ilovasida <strong>Sozlamalar &rarr; Qurilmalar (Active Sessions)</strong> bo'limiga kirib, gumonli seansni tugating. Bu bitta amal, kodni o'zgartirish shart emas.</li>
<li>Dasturiy ravishda ham buni qilish mumkin &mdash; xom API orqali <code>account.getAuthorizations</code> faol seanslar ro'yxatini, <code>account.resetAuthorization</code> esa muayyan seansni tugatish imkonini beradi (Telethon'da <code>functions.account</code> ostida mavjud).</li>
<li>Rivojlantirish (dev) va ishlab chiqarish (prod) uchun <strong>alohida</strong> session'lardan foydalaning &mdash; bitta session faylni ikkita jarayon bir vaqtda ishlatsa, SQLite "database is locked" xatosi chiqadi (11-darsda batafsil).</li>
</ul>
<h3>Session bilan parolni tenglashtiring, boshqacha emas</h3>
<p>Eng muhim xulosa: session string yoki faylni xuddi ochiq matndagi parol kabi ko'ring &mdash; balki undan ham ehtiyotkorroq, chunki uni qayta ishlatish uchun hech qanday qo'shimcha tasdiqlash kerak emas. Kod bazasida uni ko'rish mumkin bo'lgan har qanday joy (kod sharhi, xato xabari, debug log) &mdash; potentsial xavfsizlik teshigidir.</p>""",
"text_content_ru": """<h3>Что такое сессия -- технически</h3>
<p>После успешного входа в уроке 2 Telethon получает значение <code>auth_key</code> &mdash; это <strong>общий секретный ключ</strong>, полученный в результате обмена ключами Диффи-Хеллмана между вашим клиентом и конкретным дата-центром (DC) Telegram. Пока этот ключ существует, можно отправлять MTProto-запросы от имени этого аккаунта без пароля, SMS или 2FA &mdash; потому что с точки зрения сервера это уже "подтверждённое" соединение. Стандартный <code>TelegramClient("имя", ...)</code> хранит этот ключ в SQLite-файле <code>имя.session</code> (вместе с номером DC, портом и другими метаданными).</p>
<h3>StringSession -- портативная форма в одну строку</h3>
<p>Иногда писать в файловую систему неудобно (serverless-среды, контейнеры, CI) или удобнее хранить сессию как одну переменную окружения. <code>StringSession</code> сериализует тот же <code>auth_key</code> и метаданные не в SQLite-файл, а в одну base64-подобную текстовую строку:</p>
<pre class="mermaid">
flowchart LR
  A["Успешный вход"] --> B["auth_key + данные DC"]
  B --> C["Файл: имя.session (SQLite)"]
  B --> D["Или: StringSession -- одна текстовая строка"]
  C --> E["Хранится на диске"]
  D --> F["Хранится в переменной окружения / secrets manager"]
</pre>
<p>И файл, и строка &mdash; ПО СУТИ одно и то же: полная, готовая аутентификация. Разница между ними только в формате хранения, а не в уровне безопасности.</p>
<h3>Почему это опасно на уровне пароля (и даже опаснее)</h3>
<p>Если утекает пароль, злоумышленнику всё равно нужно пройти процесс входа &mdash; если включена 2FA, понадобится и она. Если утекает session-строка/файл, злоумышленник <strong>полностью обходит процесс входа</strong>: он просто создаёт <code>TelegramClient(StringSession(утёкшая_строка), api_id, api_hash)</code> и сразу же, без пароля или кода, может читать сообщения, отправлять их от вашего имени, и даже <strong>сменить пароль 2FA, заблокировав вас в собственном аккаунте</strong>. Именно поэтому в этом курсе безопасности сессий посвящена отдельная глава: это параллель к безопасности initData из курса 123, но с гораздо более тяжёлыми последствиями.</p>
<pre class="mermaid">
flowchart TB
  A["Session-строка случайно закоммичена\n(например, .env добавлен в git)"] --> B["Злоумышленник находит её в истории GitHub"]
  B --> C["TelegramClient(StringSession(найденная_строка), ...)"]
  C --> D["Немедленный полный доступ -- пароль/2FA/код НЕ НУЖНЫ"]
  D --> E["Читает сообщения, рассылает спам по контактам"]
  D --> F["Меняет пароль 2FA, блокируя владельца"]
</pre>
<h3>Практические правила</h3>
<ul>
<li><strong>Никогда</strong> не коммитьте файл <code>*.session</code> или значение session-строки в git &mdash; добавьте <code>*.session</code> в <code>.gitignore</code>.</li>
<li>Передавайте session-строку только через переменную окружения или secrets manager (например, раздел секретов на сервере) &mdash; никогда не пишите её в чат, лог-файл или сообщение об ошибке.</li>
<li>Если подозреваете утечку сессии &mdash; немедленно зайдите в приложении Telegram в <strong>Настройки &rarr; Устройства (Active Sessions)</strong> и завершите подозрительный сеанс. Это одно действие, менять код не нужно.</li>
<li>Это же можно сделать программно &mdash; через сырой API <code>account.getAuthorizations</code> получить список активных сеансов, а <code>account.resetAuthorization</code> завершить конкретный (в Telethon доступны под <code>functions.account</code>).</li>
<li>Используйте <strong>отдельные</strong> сессии для разработки (dev) и продакшена (prod) &mdash; если один файл сессии одновременно используют два процесса, возникнет ошибка SQLite "database is locked" (подробно в уроке 11).</li>
</ul>
<h3>Приравнивайте сессию к паролю, а не наоборот</h3>
<p>Главный вывод: относитесь к session-строке или файлу как к паролю в открытом виде &mdash; возможно, даже осторожнее, потому что для повторного использования не требуется никакого дополнительного подтверждения. Любое место в кодовой базе, где её можно увидеть (комментарий в коде, сообщение об ошибке, debug-лог) &mdash; потенциальная дыра в безопасности.</p>""",
"code_content": """\"\"\"Session'lar bilan xavfsiz ishlash: StringSession yaratish, saqlash, yuklash.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]


async def create_string_session() -> str:
    \"\"\"Bir martalik: yangi StringSession yaratib, uni chop etadi.
    Natijani DARHOL muhit o'zgaruvchisiga (masalan, .env yoki secrets
    manager'ga) ko'chiring va konsol tarixidan/log fayllaridan tozalang --
    hech qachon repo'ga yoki chatga yuborilmasin.\"\"\"
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        me = await client.get_me()
        session_str = client.session.save()
        print(f"Login: {me.first_name}")
        print("SESSION_STRING (buni faqat xavfsiz joyga ko'chiring!):")
        print(session_str)
        return session_str


async def use_saved_string_session() -> None:
    \"\"\"Keyingi ishga tushirishlarda -- muhit o'zgaruvchisidan o'qiladi,
    hech qanday login jarayoni qayta bo'lmaydi.\"\"\"
    session_str = os.environ["TELETHON_SESSION_STRING"]
    async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"Saqlangan session orqali kirish: {me.first_name} (id={me.id})")


async def list_active_sessions_and_revoke_suspicious() -> None:
    \"\"\"Faol seanslarni ko'rish va gumonli bo'lganini tugatish -- session
    oqib ketganidan shubha bo'lsa, birinchi qadam shu.\"\"\"
    session_str = os.environ["TELETHON_SESSION_STRING"]
    async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as client:
        result = await client(GetAuthorizationsRequest())
        for auth in result.authorizations:
            flag = " <-- BU SIZ EMASMI?" if auth.current is False else " (joriy seans)"
            print(f"  {auth.device_model} / {auth.platform} -- {auth.country}{flag}")
            print(f"    hash={auth.hash}, so'nggi faollik={auth.date_active}")

        # Misol uchun: gumonli deb topilgan seansni tugatish
        # (haqiqiy hash qiymatini yuqoridagi ro'yxatdan oling):
        # await client(ResetAuthorizationRequest(hash=SUSPICIOUS_HASH))


if __name__ == "__main__":
    # Faqat BIR martalik ishga tushirish uchun (yangi session yaratish):
    # asyncio.run(create_string_session())
    asyncio.run(use_saved_string_session())
""",
"code_content_ru": """\"\"\"Безопасная работа с сессиями: создание, хранение, загрузка StringSession.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest, ResetAuthorizationRequest

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]


async def create_string_session() -> str:
    \"\"\"Разовое действие: создаёт новую StringSession и выводит её.
    Результат НЕМЕДЛЕННО перенесите в переменную окружения (например,
    .env или secrets manager) и удалите из истории консоли/логов --
    никогда не отправляйте в репозиторий или чат.\"\"\"
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        me = await client.get_me()
        session_str = client.session.save()
        print(f"Вход: {me.first_name}")
        print("SESSION_STRING (перенесите только в безопасное место!):")
        print(session_str)
        return session_str


async def use_saved_string_session() -> None:
    \"\"\"При следующих запусках -- читается из переменной окружения,
    процесс входа заново не происходит.\"\"\"
    session_str = os.environ["TELETHON_SESSION_STRING"]
    async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"Вход через сохранённую сессию: {me.first_name} (id={me.id})")


async def list_active_sessions_and_revoke_suspicious() -> None:
    \"\"\"Просмотр активных сеансов и завершение подозрительного -- если
    есть подозрение на утечку сессии, это первый шаг.\"\"\"
    session_str = os.environ["TELETHON_SESSION_STRING"]
    async with TelegramClient(StringSession(session_str), API_ID, API_HASH) as client:
        result = await client(GetAuthorizationsRequest())
        for auth in result.authorizations:
            flag = " <-- ЭТО ТОЧНО ВЫ?" if auth.current is False else " (текущий сеанс)"
            print(f"  {auth.device_model} / {auth.platform} -- {auth.country}{flag}")
            print(f"    hash={auth.hash}, последняя активность={auth.date_active}")

        # Пример: завершение подозрительного сеанса
        # (реальный hash возьмите из списка выше):
        # await client(ResetAuthorizationRequest(hash=SUSPICIOUS_HASH))


if __name__ == "__main__":
    # Только для ОДНОРАЗОВОГО запуска (создание новой сессии):
    # asyncio.run(create_string_session())
    asyncio.run(use_saved_string_session())
""",
"task": {
"task_title": """Amaliy: session xavfsizligi tekshiruvi va faol seanslar auditi""",
"task_title_ru": """Практика: проверка безопасности сессии и аудит активных сеансов""",
"task_description": """list_active_sessions_and_revoke_suspicious() funksiyasini asos qilib, o'z hisobingizdagi barcha faol seanslarni chiqaring va har biri uchun qurilma, joylashuv va oxirgi faollik vaqtini ko'rsating. Shundan so'ng, loyihangizga .gitignore fayl qo'shing (agar hali yo'q bo'lsa) va unda *.session hamda .env qatorlari borligini tekshiring.""",
"task_description_ru": """На основе функции list_active_sessions_and_revoke_suspicious() выведите все активные сеансы своего аккаунта с указанием устройства, местоположения и времени последней активности для каждого. Затем добавьте в проект файл .gitignore (если его ещё нет) и убедитесь, что в нём есть строки *.session и .env.""",
"task_requirements": """Faol seanslar ro'yxati chiqarilgan bo'lishi; .gitignore faylida *.session va .env qatorlari bo'lishi; session string kodda hardcoded holda bo'lmasligi kerak.""",
"task_requirements_ru": """Должен быть выведен список активных сеансов; в .gitignore должны быть строки *.session и .env; session-строка не должна быть hardcoded в коде.""",
"task_technologies": "Python 3.11+, Telethon, python-dotenv, git",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: session yaratish + faol seanslarni auditlash skripti""",
"description": """StringSession yaratuvchi va faol seanslarni ro'yxatga oluvchi to'liq skript, xavfsiz .gitignore namunasi bilan""",
"sample_type": "code",
"code_files": [
{"filename": ".gitignore", "language": "text", "code": """*.session
*.session-journal
.env
__pycache__/
"""},
{"filename": "session_audit.py", "language": "python", "code": """import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["TELETHON_SESSION_STRING"]


async def audit() -> None:
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        result = await client(GetAuthorizationsRequest())
        print(f"Jami faol seanslar: {len(result.authorizations)}\\n")
        for auth in result.authorizations:
            marker = "JORIY" if auth.current else "boshqa qurilma"
            print(f"[{marker}] {auth.device_model} ({auth.platform}) -- {auth.country}")
            print(f"        so'nggi faollik: {auth.date_active}, hash={auth.hash}")


if __name__ == "__main__":
    asyncio.run(audit())
"""},
],
},
"exercises": [
{
"title": """Session oqib ketishining oqibati""",
"title_ru": """Последствие утечки сессии""",
"description": """Session string oqib ketsa, hujumchi hisobga kirish uchun yana nima kerak bo'ladi?""",
"description_ru": """Если утекает session-строка, что ещё нужно злоумышленнику для входа в аккаунт?""",
"exercise_type": "multiple_choice",
"options": ["Hech narsa -- darhol to'liq kirish mumkin", "Faqat SMS kodi", "Faqat 2FA paroli", "SMS kodi va 2FA paroli ikkalasi ham"],
"options_ru": ["Ничего -- сразу возможен полный доступ", "Только SMS-код", "Только пароль 2FA", "И SMS-код, и пароль 2FA"],
"correct_answers": "A",
"is_multiple_select": False,
"hint": """Session string allaqachon tugallangan autentifikatsiyani ifodalaydi.""",
"hint_ru": """Session-строка уже представляет собой завершённую аутентификацию.""",
"explanation": """auth_key allaqachon Telegram tomonidan tasdiqlangan -- shuning uchun uni ishlatish uchun qo'shimcha parol, kod yoki 2FA shart emas, bu esa uni parolga qaraganda ham xavfliroq qiladi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Session string qayerda saqlanishi kerak""",
"title_ru": """Где должна храниться session-строка""",
"description": """Production muhitda session string'ni saqlash uchun eng to'g'ri joy qaysi?""",
"description_ru": """Какое место правильнее всего для хранения session-строки в production?""",
"exercise_type": "multiple_choice",
"options": ["Python kodida o'zgaruvchi sifatida, to'g'ridan-to'g'ri yozilgan", "Git repozitoriyasidagi konfiguratsiya faylida", "Muhit o'zgaruvchisi yoki secrets manager'da", "Loyihaning README faylida, hujjatlashtirish uchun"],
"options_ru": ["Как переменная прямо в коде Python", "В конфигурационном файле в git-репозитории", "В переменной окружения или secrets manager", "В файле README проекта, для документации"],
"correct_answers": "C",
"is_multiple_select": False,
"hint": """Kod bazasida ko'rinadigan har qanday joy -- xavfsizlik teshigi.""",
"hint_ru": """Любое место, видимое в кодовой базе, -- дыра в безопасности.""",
"explanation": """Session string parol darajasidagi maxfiy ma'lumot -- u faqat muhit o'zgaruvchisi yoki maxsus secrets manager orqali uzatilishi kerak, hech qachon kod yoki repozitoriyada emas.""",
"difficulty_level": "Easy",
"points": 5,
},
{
"title": """Session oqib ketganda javob choralarini tartiblang""",
"title_ru": """Расположите по порядку меры реагирования на утечку сессии""",
"description": """Session oqib ketgani aniqlangandan so'ng qanday tartibda harakat qilish kerak?""",
"description_ru": """В каком порядке нужно действовать после обнаружения утечки сессии?""",
"exercise_type": "drag_and_drop",
"drag_items": ["Active Sessions'da gumonli seansni darhol tugatish", "Barcha faol seanslarni ko'rib chiqib, notanish qurilmalarni topish", "2FA (bulutli) parolni yangilash", "Yangi, toza session yaratib qayta autentifikatsiyadan o'tish"],
"drag_items_ru": ["Немедленно завершить подозрительный сеанс в Active Sessions", "Просмотреть все активные сеансы и найти незнакомые устройства", "Обновить пароль 2FA (облачный)", "Создать новую, чистую сессию и заново пройти аутентификацию"],
"correct_order": ["Active Sessions'da gumonli seansni darhol tugatish", "Barcha faol seanslarni ko'rib chiqib, notanish qurilmalarni topish", "2FA (bulutli) parolni yangilash", "Yangi, toza session yaratib qayta autentifikatsiyadan o'tish"],
"hint": """Avval xavfni to'xtatish (tugatish), keyin tekshirish, keyin mustahkamlash, oxirida qayta boshlash.""",
"hint_ru": """Сначала остановить угрозу (завершить), потом проверить, потом усилить защиту, в конце начать заново.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Portativ session klassi""",
"title_ru": """Класс портативной сессии""",
"description": """auth_key va metama'lumotlarni SQLite fayl o'rniga bitta matn qatoriga seriyalashtiruvchi Telethon klassi: ___""",
"description_ru": """Класс Telethon, сериализующий auth_key и метаданные не в SQLite-файл, а в одну текстовую строку: ___""",
"exercise_type": "fill_in_blank",
"correct_answers": "StringSession",
"hint": """telethon.sessions modulidan import qilinadi.""",
"hint_ru": """Импортируется из модуля telethon.sessions.""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 3,
"title": """4-Xabar yuborish va o'qish: haqiqiy hisob nomidan ishlash""",
"title_ru": """4-Отправка и чтение сообщений: работа от имени настоящего аккаунта""",
"points_reward": 17,
"code_language": "python",
"text_content": """<h3>send_message va get_messages -- tanish, lekin boshqacha</h3>
<p>Metodlar nomi aiogram'dagiga o'xshab tuyulishi mumkin, lekin ma'no boshqa: <code>client.send_message(entity, text)</code> chaqirilganda, xabar bot nomidan emas, balki <strong>sizning haqiqiy hisobingiz</strong> nomidan yuboriladi &mdash; qabul qiluvchi buni oddiy foydalanuvchi xabari sifatida ko'radi, "Bot" belgisi yo'q. <code>client.get_messages(entity, limit=N)</code> esa &mdash; standart holatda eng yangi xabarlardan boshlab, teskari xronologik tartibda &mdash; oxirgi N ta xabarni qaytaradi (bu 6-darsda ko'radigan <code>iter_messages</code>'dan farqli, u katta hajmdagi tarixni sahifalab o'qish uchun).</p>
<h3>"entity" nima -- va nega bu tushuncha muhim</h3>
<p>Telethon'da deyarli har bir metod "entity" kutadi &mdash; bu foydalanuvchi, guruh yoki kanalni bildiruvchi mavhum tushuncha. Entity sifatida quyidagilarni berish mumkin:</p>
<ul>
<li>Username qatori: <code>"@someuser"</code> yoki <code>"someuser"</code> (ikkalasi ham ishlaydi).</li>
<li>Butun son ID: <code>777000</code> (Telegram xizmat hisobi kabi).</li>
<li>Maxsus qator <code>"me"</code> &mdash; bu sizning o'z hisobingiz (Saved Messages'ga yuborish uchun juda qulay: <code>client.send_message("me", "eslatma")</code>).</li>
<li>Oldindan olingan <code>User</code>/<code>Chat</code>/<code>Channel</code> obyekti (masalan, <code>get_dialogs()</code>dan qaytgan).</li>
</ul>
<p>Ostida esa Telegram serveri har doim <code>PeerUser</code>/<code>PeerChat</code>/<code>PeerChannel</code> (ID) VA <code>access_hash</code> (o'sha entity uchun bir martalik ruxsat kaliti) juftligini talab qiladi. Telethon buni sizdan yashiradi &mdash; u ichki <strong>entity cache</strong>'da username/ID'larni access_hash'larga moslashtirib boradi. Shu sababli ba'zan <code>ValueError: Could not find the input entity</code> xatosi chiqadi: agar hisobingiz hali hech qachon o'sha foydalanuvchi/kanal bilan "uchrashmagan" bo'lsa (masalan, umumiy guruhda bo'lmagan notanish foydalanuvchi ID'si), Telethon uning access_hash'ini qayerdan olishni bilmaydi.</p>
<pre class="mermaid">
flowchart TB
  A["client.send_message(entity, text)"] --> B{"entity turi?"}
  B -- "username / 'me' / ID" --> C["Entity cache'dan qidiriladi"]
  C -- "Topildi" --> D["access_hash bilan PeerUser/PeerChannel tuziladi"]
  C -- "Topilmadi" --> E["ValueError: Could not find the input entity"]
  B -- "User/Chat/Channel obyekti" --> D
  D --> F["Xom MTProto so'rovi (messages.sendMessage)"]
</pre>
<p>Diagramma shuni ko'rsatadi: entity resolution &mdash; bu Bot API'da umuman yo'q qo'shimcha qatlam, chunki Bot API sizning nomingizdan har doim to'g'ridan-to'g'ri ID orqali ishlaydi va access_hash muammosi Telegram tomonida hal qilinadi.</p>
<h3>O'qish, tahrirlash, o'chirish -- foydalanuvchiga xos amallar</h3>
<p>Haqiqiy hisob sifatida sizda bot hech qachon qila olmaydigan amallar bor: <code>client.send_read_acknowledge(entity)</code> &mdash; xabarlarni "o'qilgan" deb belgilash (bot buni hech qachon boshqara olmaydi, chunki botning "o'qish holati" tushunchasi yo'q); <code>client.action(entity, "typing")</code> &mdash; "yozmoqda..." holatini ko'rsatish; <code>client.edit_message(entity, message, new_text)</code> &mdash; avval yuborilgan xabarni tahrirlash; <code>client.delete_messages(entity, message_ids)</code> &mdash; xabarlarni o'chirish. Bu metodlarning barchasi Bot API'da ham mavjud, lekin faqat botning O'Z xabarlari uchun ishlaydi; userbot esa (agar guruh sozlamalari ruxsat bersa) boshqa a'zolarning xabarlarini ham o'chira oladi, agar admin bo'lsa.</p>
<h3>Tezlik cheklovlari -- bu yerda ham amal qiladi</h3>
<p>Xabar yuborish tezligi cheksiz emas &mdash; ayniqsa yangi yoki ko'p kontaktga ega bo'lmagan hisoblar uchun Telegram <code>FloodWaitError</code> qaytarishi mumkin. Bir nechta xabarni ketma-ket, halqada (loop) yuborishdan saqlaning &mdash; bu 7-darsda batafsil ko'rib chiqiladigan "ommaviy avtomatlashtirish xavfi"ning eng oddiy shakli.</p>
<h3>Qo'shimcha yuborish parametrlari</h3>
<p><code>send_message</code> yana bir nechta foydali parametrni qabul qiladi, ular Bot API'da ham mavjud, lekin userbot kontekstida boshqacha ma'no kasb etadi: <code>silent=True</code> &mdash; qabul qiluvchiga ovozli bildirishnomasiz yetkazish; <code>schedule=datetime(...)</code> &mdash; xabarni kelajakdagi aniq vaqtga rejalashtirish (Telegram serverining o'zi saqlaydi, sizning dasturingiz ishlab turishi shart emas); <code>link_preview=False</code> &mdash; havola oldindan ko'rinishini o'chirish; <code>reply_to=message_id</code> &mdash; muayyan xabarga javob sifatida yuborish. Bulardan tashqari, foydalanuvchi hisobiga xos yana bir imkoniyat &mdash; <strong>qoralamalar (drafts)</strong>: <code>client.get_drafts()</code> orqali barcha chatlardagi hali yuborilmagan qoralama matnlarni olish mumkin, bu bot hisobida umuman mavjud bo'lmagan tushuncha, chunki qoralama &mdash; klient ilovasining shaxsiy holati, bot esa bunday "ilova holati"ga ega emas.</p>""",
"text_content_ru": """<h3>send_message и get_messages -- знакомо, но иначе</h3>
<p>Названия методов могут показаться похожими на aiogram, но смысл другой: когда вызывается <code>client.send_message(entity, text)</code>, сообщение отправляется не от имени бота, а от имени <strong>вашего настоящего аккаунта</strong> &mdash; получатель видит его как обычное сообщение пользователя, без пометки "Bot". <code>client.get_messages(entity, limit=N)</code> по умолчанию возвращает последние N сообщений, начиная с самых новых, в обратном хронологическом порядке (это отличается от <code>iter_messages</code> из урока 6, предназначенного для постраничного чтения большой истории).</p>
<h3>Что такое "entity" -- и почему это понятие важно</h3>
<p>В Telethon почти каждый метод ожидает "entity" &mdash; абстрактное понятие, обозначающее пользователя, группу или канал. В качестве entity можно передать:</p>
<ul>
<li>Строку с username: <code>"@someuser"</code> или <code>"someuser"</code> (работают оба варианта).</li>
<li>Целое число ID: <code>777000</code> (например, служебный аккаунт Telegram).</li>
<li>Специальную строку <code>"me"</code> &mdash; это ваш собственный аккаунт (очень удобно для отправки в Saved Messages: <code>client.send_message("me", "заметка")</code>).</li>
<li>Уже полученный объект <code>User</code>/<code>Chat</code>/<code>Channel</code> (например, из <code>get_dialogs()</code>).</li>
</ul>
<p>Под капотом же сервер Telegram всегда требует пару <code>PeerUser</code>/<code>PeerChat</code>/<code>PeerChannel</code> (ID) И <code>access_hash</code> (одноразовый ключ доступа для этого entity). Telethon скрывает это от вас &mdash; он ведёт внутренний <strong>кэш entity</strong>, сопоставляя username/ID с access_hash. Поэтому иногда возникает ошибка <code>ValueError: Could not find the input entity</code>: если ваш аккаунт ещё никогда не "встречал" этого пользователя/канал (например, ID незнакомого пользователя не из общей группы), Telethon не знает, откуда взять его access_hash.</p>
<pre class="mermaid">
flowchart TB
  A["client.send_message(entity, text)"] --> B{"Тип entity?"}
  B -- "username / 'me' / ID" --> C["Поиск в кэше entity"]
  C -- "Найдено" --> D["Строится PeerUser/PeerChannel с access_hash"]
  C -- "Не найдено" --> E["ValueError: Could not find the input entity"]
  B -- "Объект User/Chat/Channel" --> D
  D --> F["Сырой MTProto-запрос (messages.sendMessage)"]
</pre>
<p>Диаграмма показывает: разрешение entity &mdash; это дополнительный слой, которого вообще нет в Bot API, потому что Bot API всегда работает от вашего имени напрямую по ID, а проблему access_hash решает сторона Telegram.</p>
<h3>Чтение, редактирование, удаление -- действия, свойственные пользователю</h3>
<p>Как настоящий аккаунт, у вас есть действия, которые бот никогда не может выполнить: <code>client.send_read_acknowledge(entity)</code> &mdash; пометить сообщения как "прочитанные" (бот никогда не может этим управлять, потому что у бота нет понятия "статус прочтения"); <code>client.action(entity, "typing")</code> &mdash; показать статус "печатает..."; <code>client.edit_message(entity, message, new_text)</code> &mdash; отредактировать ранее отправленное сообщение; <code>client.delete_messages(entity, message_ids)</code> &mdash; удалить сообщения. Все эти методы есть и в Bot API, но работают только для СВОИХ сообщений бота; юзербот же (если позволяют настройки группы) может удалить сообщения и других участников, если является администратором.</p>
<h3>Ограничения скорости -- действуют и здесь</h3>
<p>Скорость отправки сообщений не безгранична &mdash; особенно для новых аккаунтов или аккаунтов с небольшим числом контактов Telegram может вернуть <code>FloodWaitError</code>. Избегайте отправки нескольких сообщений подряд в цикле &mdash; это простейшая форма "риска массовой автоматизации", подробно разобранного в уроке 7.</p>
<h3>Дополнительные параметры отправки</h3>
<p><code>send_message</code> принимает ещё несколько полезных параметров, которые есть и в Bot API, но в контексте юзербота приобретают другой смысл: <code>silent=True</code> &mdash; доставка получателю без звукового уведомления; <code>schedule=datetime(...)</code> &mdash; запланировать сообщение на конкретное время в будущем (хранит сам сервер Telegram, ваша программа не обязана всё это время работать); <code>link_preview=False</code> &mdash; отключить превью ссылки; <code>reply_to=message_id</code> &mdash; отправить как ответ на конкретное сообщение. Помимо этого, ещё одна возможность, свойственная именно пользовательскому аккаунту &mdash; <strong>черновики (drafts)</strong>: через <code>client.get_drafts()</code> можно получить ещё не отправленные черновики текста во всех чатах; это понятие вообще отсутствует у аккаунта бота, потому что черновик &mdash; это личное состояние клиентского приложения, а у бота такого "состояния приложения" нет.</p>""",
"code_content": """\"\"\"Xabar yuborish, o'qish, tahrirlash va entity resolution namunalari.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["TELETHON_SESSION_STRING"]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


async def send_and_receive_basics() -> None:
    async with client:
        # 1) O'zingizga eslatma yuborish (Saved Messages)
        note = await client.send_message("me", "Telethon darsligi: 4-dars yakunlandi.")
        print(f"Yuborildi, id={note.id}")

        # 2) Xabarni tahrirlash
        await client.edit_message("me", note.id, "Telethon darsligi: 4-dars -- tahrirlangan.")

        # 3) Oxirgi 5 ta xabarni o'qish (eng yangisidan boshlab)
        async for msg in client.iter_messages("me", limit=5):
            sender = await msg.get_sender()
            name = getattr(sender, "first_name", "Noma'lum")
            print(f"[{msg.date}] {name}: {msg.text!r}")

        # 4) "Yozmoqda..." holatini ko'rsatish (foydalanuvchiga xos amal)
        async with client.action("me", "typing"):
            await asyncio.sleep(1)

        # 5) Xabarni o'qilgan deb belgilash
        await client.send_read_acknowledge("me")


async def resolve_entity_safely(username: str) -> None:
    \"\"\"Entity topilmasa ValueError chiqishi mumkin -- buni to'g'ri ushlash.\"\"\"
    async with client:
        try:
            entity = await client.get_entity(username)
            print(f"Topildi: {entity.first_name if hasattr(entity, 'first_name') else entity.title}")
        except ValueError:
            print(
                f"'{username}' entity'sini topib bo'lmadi -- hisobingiz hali "
                f"bu foydalanuvchi/kanal bilan hech qachon 'uchrashmagan' bo'lishi mumkin."
            )


async def send_with_flood_guard(entity: str, text: str) -> None:
    \"\"\"Ommaviy yuborishda albatta FloodWaitError'ni ushlash kerak --
    aks holda dastur kutilmaganda to'xtab qoladi.\"\"\"
    async with client:
        try:
            await client.send_message(entity, text)
        except FloodWaitError as e:
            print(f"Flood limit -- {e.seconds} soniya kutish kerak, keyin qayta urinamiz.")
            await asyncio.sleep(e.seconds)
            await client.send_message(entity, text)


if __name__ == "__main__":
    asyncio.run(send_and_receive_basics())
""",
"code_content_ru": """\"\"\"Примеры отправки, чтения, редактирования сообщений и разрешения entity.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["TELETHON_SESSION_STRING"]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


async def send_and_receive_basics() -> None:
    async with client:
        # 1) Отправка заметки себе (Saved Messages)
        note = await client.send_message("me", "Учебник по Telethon: урок 4 завершён.")
        print(f"Отправлено, id={note.id}")

        # 2) Редактирование сообщения
        await client.edit_message("me", note.id, "Учебник по Telethon: урок 4 -- отредактировано.")

        # 3) Чтение последних 5 сообщений (начиная с самого нового)
        async for msg in client.iter_messages("me", limit=5):
            sender = await msg.get_sender()
            name = getattr(sender, "first_name", "Неизвестно")
            print(f"[{msg.date}] {name}: {msg.text!r}")

        # 4) Показ статуса "печатает..." (действие, свойственное пользователю)
        async with client.action("me", "typing"):
            await asyncio.sleep(1)

        # 5) Пометка сообщений как прочитанных
        await client.send_read_acknowledge("me")


async def resolve_entity_safely(username: str) -> None:
    \"\"\"Если entity не найден, может возникнуть ValueError -- обработаем это правильно.\"\"\"
    async with client:
        try:
            entity = await client.get_entity(username)
            print(f"Найдено: {entity.first_name if hasattr(entity, 'first_name') else entity.title}")
        except ValueError:
            print(
                f"Не удалось найти entity '{username}' -- возможно, ваш аккаунт "
                f"никогда не 'встречал' этого пользователя/канал."
            )


async def send_with_flood_guard(entity: str, text: str) -> None:
    \"\"\"При массовой отправке обязательно нужно ловить FloodWaitError --
    иначе программа неожиданно упадёт.\"\"\"
    async with client:
        try:
            await client.send_message(entity, text)
        except FloodWaitError as e:
            print(f"Флуд-лимит -- нужно подождать {e.seconds} секунд, затем повторим попытку.")
            await asyncio.sleep(e.seconds)
            await client.send_message(entity, text)


if __name__ == "__main__":
    asyncio.run(send_and_receive_basics())
""",
"task": {
"task_title": """Amaliy: xabar yuborish, tahrirlash va entity xatoligini boshqarish""",
"task_title_ru": """Практика: отправка, редактирование сообщений и обработка ошибки entity""",
"task_description": """send_and_receive_basics() funksiyasidan foydalanib, o'zingizga (Saved Messages) kamida 3 ta xabar yuboring, ulardan birini tahriring va oxirgi 5 ta xabarni jadval ko'rinishida chiqaring. Shundan so'ng resolve_entity_safely() funksiyasini mavjud bo'lmagan (o'ylab topilgan) username bilan chaqirib, ValueError to'g'ri ushlanishini tekshiring.""",
"task_description_ru": """Используя функцию send_and_receive_basics(), отправьте себе (в Saved Messages) минимум 3 сообщения, отредактируйте одно из них и выведите последние 5 сообщений в виде списка. Затем вызовите resolve_entity_safely() с несуществующим (выдуманным) username и убедитесь, что ValueError корректно обрабатывается.""",
"task_requirements": """Kamida 3 xabar yuborilgan; kamida 1 xabar tahrirlangan; ValueError to'g'ri ushlangan holat namoyish etilgan bo'lishi kerak.""",
"task_requirements_ru": """Отправлено минимум 3 сообщения; минимум 1 сообщение отредактировано; должен быть продемонстрирован случай корректной обработки ValueError.""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: Saved Messages jurnal skripti""",
"description": """O'zingizga eslatmalar yozadigan va oxirgi yozuvlarni jadval qilib chiqaruvchi kichik "jurnal" skripti""",
"sample_type": "code",
"code_files": [
{"filename": "journal.py", "language": "python", "code": """import asyncio
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def add_entry(text: str) -> None:
    async with client:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        await client.send_message("me", f"[{timestamp}] {text}")
        print("Yozuv qo'shildi.")


async def show_recent(limit: int = 10) -> None:
    async with client:
        print(f"So'nggi {limit} ta yozuv:")
        async for msg in client.iter_messages("me", limit=limit):
            print(f"  #{msg.id}: {msg.text}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        asyncio.run(add_entry(" ".join(sys.argv[2:])))
    else:
        asyncio.run(show_recent())
"""},
],
},
"exercises": [
{
"title": """get_messages standart tartibi""",
"title_ru": """Порядок по умолчанию в get_messages""",
"description": """client.get_messages(entity, limit=10) standart holatda xabarlarni qaysi tartibda qaytaradi?""",
"description_ru": """В каком порядке client.get_messages(entity, limit=10) возвращает сообщения по умолчанию?""",
"exercise_type": "multiple_choice",
"options": ["Eng eskisidan eng yangisiga", "Eng yangisidan eng eskisiga", "Alifbo tartibida", "Tasodifiy tartibda"],
"options_ru": ["От самого старого к самому новому", "От самого нового к самому старому", "В алфавитном порядке", "В случайном порядке"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu "so'nggi N ta xabar"ni olishga mo'ljallangan.""",
"hint_ru": """Это предназначено для получения "последних N сообщений".""",
"explanation": """get_messages standart holatda eng yangi xabardan boshlab teskari tartibda qaytaradi -- katta tarixni sahifalab, xronologik tartibda o'qish uchun esa iter_messages (6-dars) ishlatiladi.""",
"difficulty_level": "Easy",
"points": 5,
},
{
"title": """'me' entity nimani anglatadi""",
"title_ru": """Что означает entity 'me'""",
"description": """client.send_message('me', text) chaqirilganda xabar qayerga yuboriladi?""",
"description_ru": """Куда отправляется сообщение при вызове client.send_message('me', text)?""",
"exercise_type": "multiple_choice",
"options": ["Botning o'ziga", "Saved Messages'ga (o'zingizga)", "Barcha kontaktlarga", "Telegram administratsiyasiga"],
"options_ru": ["Самому боту", "В Saved Messages (самому себе)", "Всем контактам", "Администрации Telegram"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """'me' -- bu maxsus qisqartma, hisobingizning o'ziga ishora qiladi.""",
"hint_ru": """'me' -- это специальное сокращение, указывающее на ваш собственный аккаунт.""",
"explanation": """'me' shaxsiy Saved Messages chatiga ishora qiladi -- eslatmalar, jurnal yozuvlari va shunga o'xshash narsalar uchun juda qulay.""",
"difficulty_level": "Easy",
"points": 5,
},
{
"title": """Entity resolution jarayonini tartiblang""",
"title_ru": """Расположите процесс разрешения entity по порядку""",
"description": """client.send_message(username, text) chaqirilganda, entity qanday tartibda MTProto so'roviga aylanadi?""",
"description_ru": """При вызове client.send_message(username, text), в каком порядке entity превращается в MTProto-запрос?""",
"exercise_type": "drag_and_drop",
"drag_items": ["Berilgan username/ID entity cache'dan qidiriladi", "Agar topilsa, access_hash bilan PeerUser/PeerChannel tuziladi", "Tuzilgan Peer bilan xom MTProto so'rovi (messages.sendMessage) yuboriladi", "Agar topilmasa, ValueError ko'tariladi"],
"drag_items_ru": ["Данный username/ID ищется в кэше entity", "Если найден, строится PeerUser/PeerChannel с access_hash", "С построенным Peer отправляется сырой MTProto-запрос (messages.sendMessage)", "Если не найден, выбрасывается ValueError"],
"correct_order": ["Berilgan username/ID entity cache'dan qidiriladi", "Agar topilsa, access_hash bilan PeerUser/PeerChannel tuziladi", "Tuzilgan Peer bilan xom MTProto so'rovi (messages.sendMessage) yuboriladi", "Agar topilmasa, ValueError ko'tariladi"],
"hint": """Avval qidiruv, keyin muvaffaqiyat/muvaffaqiyatsizlik shoxobchasi.""",
"hint_ru": """Сначала поиск, потом ветвление успех/неудача.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Avval yuborilgan xabarni tahrirlash metodi""",
"title_ru": """Метод редактирования ранее отправленного сообщения""",
"description": """Avval yuborilgan xabar matnini o'zgartirish uchun ishlatiladigan client metodi: client.___()""",
"description_ru": """Метод client, используемый для изменения текста ранее отправленного сообщения: client.___()""",
"exercise_type": "fill_in_blank",
"correct_answers": "edit_message",
"hint": """Nomi to'g'ridan-to'g'ri "tahrirlash" ma'nosini bildiradi.""",
"hint_ru": """Название буквально означает "редактировать".""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 4,
"title": """5-Voqea-asosli handlerlar: events.NewMessage va aiogram router modelidan farqi""",
"title_ru": """5-Обработчики событий: events.NewMessage и отличие от модели router aiogram""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>Ikki mutlaqo boshqa dispetcherlash modeli</h3>
<p>aiogram'da siz <code>Router</code> obyektlarini yaratib, ularni <code>Dispatcher</code>ga <code>include_router()</code> orqali ulaysiz; filtrlash <code>Command(...)</code>, <code>F.text</code>, maxsus filter klasslari orqali, ko'pincha bir nechta routerga bo'lingan holda amalga oshiriladi. Telethon'da esa alohida Dispatcher obyekti <strong>yo'q</strong> &mdash; <code>TelegramClient</code>ning o'zi handlerlarni ro'yxatga oladi va yangi update kelganda ularni chaqiradi. Ro'yxatga olishning ikki yo'li bor:</p>
<ul>
<li>Dekorator: <code>@client.on(events.NewMessage(pattern="/start"))</code></li>
<li>To'g'ridan-to'g'ri: <code>client.add_event_handler(callback, events.NewMessage(pattern="/start"))</code> &mdash; dinamik ravishda (masalan, runtime'da) handler qo'shish kerak bo'lsa foydali.</li>
</ul>
<p>Filtrlar routerlar yoki alohida filter klasslari orqali emas, balki har bir <code>events.*</code> klassining <strong>konstruktor argumentlari</strong> orqali beriladi &mdash; masalan <code>events.NewMessage(incoming=True, chats=[-100123], from_users=[42])</code>.</p>
<h3>Asosiy event turlari</h3>
<table>
<tr><th>Event klassi</th><th>Qachon ishga tushadi</th></tr>
<tr><td><code>events.NewMessage</code></td><td>Yangi xabar kelganda (shaxsiy, guruh, kanal)</td></tr>
<tr><td><code>events.MessageEdited</code></td><td>Mavjud xabar tahrirlanganda</td></tr>
<tr><td><code>events.MessageDeleted</code></td><td>Xabar o'chirilganda (faqat ID beriladi, matn EMAS &mdash; Telegram o'chirilgan xabar mazmunini saqlamaydi)</td></tr>
<tr><td><code>events.ChatAction</code></td><td>Foydalanuvchi qo'shildi/chiqdi, sarlavha o'zgardi, rasm o'zgardi, xabar pin qilindi</td></tr>
<tr><td><code>events.UserUpdate</code></td><td>Foydalanuvchi holati (online/offline, "yozmoqda...") o'zgarganda</td></tr>
<tr><td><code>events.CallbackQuery</code></td><td>Inline tugma bosilganda (asosan bot hisoblari uchun, lekin userbot ham botlar bilan ishlaganda kuzatishi mumkin)</td></tr>
</table>
<h3>NewMessage'ning muhim filtrlari</h3>
<p><code>pattern</code> &mdash; regex yoki oddiy matn (aiogram'dagi <code>Command</code>ga o'xshaydi, lekin bu yerda to'g'ridan-to'g'ri regex); <code>incoming</code>/<code>outgoing</code> &mdash; faqat kiruvchi yoki faqat o'zingiz yuborgan xabarlar (userbot o'z xabarlarini ham "ko'radi", chunki bu sizning hisobingiz oqimi &mdash; bot hech qachon o'zining chiquvchi xabarlarini event sifatida qaytadan olmaydi); <code>chats</code> &mdash; faqat berilgan chat ID/username'lardan; <code>from_users</code> &mdash; faqat berilgan yuboruvchilardan; <code>func</code> &mdash; ixtiyoriy qo'shimcha shart (lambda funksiya).</p>
<pre class="mermaid">
flowchart TB
  A["Yangi Update Telegram serveridan keladi"] --> B["TelegramClient ichki dispatch tsikli"]
  B --> C{"Ro'yxatga olingan har bir\nevent builder filtriga mos keladimi?"}
  C -- "Mos keldi" --> D["Handler chaqiriladi (ro'yxatga olingan tartibda)"]
  D --> E{"Handler ichida\nraise events.StopPropagation?"}
  E -- "Ha" --> F["Qolgan handlerlar chaqirilmaydi"]
  E -- "Yo'q" --> G["Navbatdagi mos handler chaqiriladi"]
  C -- "Mos kelmadi" --> H["Handler chaqirilmaydi, keyingisiga o'tiladi"]
</pre>
<p>Diagramma shuni ko'rsatadi: aiogram'dagi middleware zanjiri va router ierarxiyasi o'rniga, Telethon'da oddiy, tekis ro'yxat bor &mdash; har bir mos keluvchi handler ro'yxatga olingan tartibda ishga tushadi, va <code>events.StopPropagation</code> ko'tarilmaguncha davom etadi.</p>
<h3>event obyekti ichida nima bor</h3>
<p><code>events.NewMessage.Event</code> obyektida <code>event.text</code>, <code>event.sender_id</code>, <code>event.chat_id</code>, <code>event.is_private</code>/<code>is_group</code>/<code>is_channel</code>, va eng muhimi &mdash; <code>event.reply()</code> (suhbatga javob, reply sifatida) hamda <code>event.respond()</code> (oddiy xabar, reply emas) metodlari bor. Bular aiogram'dagi <code>message.answer()</code>/<code>message.reply()</code>ga juda o'xshash &mdash; bu yerda ikkala kutubxona ham deyarli bir xil qulaylikni taqdim etadi, farq faqat dispetcherlash modelida.</p>
<h3>Handlerni olib tashlash va bitta funksiyaga bir nechta filtr ulash</h3>
<p><code>client.remove_event_handler(callback)</code> &mdash; runtime'da handlerni to'xtatish kerak bo'lganda ishlatiladi (masalan, vaqtinchalik "texnik ishlar" rejimi uchun). Shuningdek, bitta funksiyaga bir nechta dekorator qo'yish orqali uni bir nechta turli event/filtrga ro'yxatga olish mumkin &mdash; masalan, xuddi shu <code>on_ping</code> funksiyasini ham <code>events.NewMessage(pattern="/ping")</code>ga, ham alohida <code>events.NewMessage(pattern="/salom")</code>ga ulash mumkin, ikkalasi ham bir xil kodni ishga tushiradi. Bu aiogram'dagi bitta handlerga bir nechta filtr birlashtirish (<code>F.text | Command(...)</code>) imkoniyatiga o'xshash natijaga olib keladi, faqat sintaksis boshqacha &mdash; bir nechta alohida <code>@client.on(...)</code> qatlami sifatida.</p>""",
"text_content_ru": """<h3>Две совершенно разные модели диспетчеризации</h3>
<p>В aiogram вы создаёте объекты <code>Router</code> и подключаете их к <code>Dispatcher</code> через <code>include_router()</code>; фильтрация делается через <code>Command(...)</code>, <code>F.text</code>, специальные классы фильтров, часто разделённые на несколько routers. В Telethon же отдельного объекта Dispatcher <strong>нет</strong> &mdash; сам <code>TelegramClient</code> регистрирует обработчики и вызывает их при получении нового апдейта. Есть два способа регистрации:</p>
<ul>
<li>Декоратор: <code>@client.on(events.NewMessage(pattern="/start"))</code></li>
<li>Напрямую: <code>client.add_event_handler(callback, events.NewMessage(pattern="/start"))</code> &mdash; полезно, если обработчик нужно добавить динамически (например, во время выполнения).</li>
</ul>
<p>Фильтры задаются не через routers или отдельные классы фильтров, а через <strong>аргументы конструктора</strong> каждого класса <code>events.*</code> &mdash; например <code>events.NewMessage(incoming=True, chats=[-100123], from_users=[42])</code>.</p>
<h3>Основные типы событий</h3>
<table>
<tr><th>Класс события</th><th>Когда срабатывает</th></tr>
<tr><td><code>events.NewMessage</code></td><td>При новом сообщении (личном, в группе, в канале)</td></tr>
<tr><td><code>events.MessageEdited</code></td><td>При редактировании существующего сообщения</td></tr>
<tr><td><code>events.MessageDeleted</code></td><td>При удалении сообщения (передаётся только ID, а НЕ текст &mdash; Telegram не хранит содержимое удалённого сообщения)</td></tr>
<tr><td><code>events.ChatAction</code></td><td>Пользователь добавлен/вышел, изменён заголовок, изменена фотография, сообщение закреплено</td></tr>
<tr><td><code>events.UserUpdate</code></td><td>При изменении статуса пользователя (онлайн/офлайн, "печатает...")</td></tr>
<tr><td><code>events.CallbackQuery</code></td><td>При нажатии inline-кнопки (в основном для аккаунтов ботов, но юзербот тоже может отслеживать это при взаимодействии с ботами)</td></tr>
</table>
<h3>Важные фильтры NewMessage</h3>
<p><code>pattern</code> &mdash; regex или обычный текст (похоже на <code>Command</code> в aiogram, но здесь это напрямую regex); <code>incoming</code>/<code>outgoing</code> &mdash; только входящие или только отправленные вами сообщения (юзербот "видит" и свои исходящие сообщения, потому что это поток вашего аккаунта &mdash; бот никогда не получает свои исходящие сообщения как событие заново); <code>chats</code> &mdash; только из указанных ID/username чатов; <code>from_users</code> &mdash; только от указанных отправителей; <code>func</code> &mdash; дополнительное произвольное условие (lambda-функция).</p>
<pre class="mermaid">
flowchart TB
  A["Новый Update приходит с сервера Telegram"] --> B["Внутренний цикл диспетчеризации TelegramClient"]
  B --> C{"Соответствует ли фильтру\nкаждого зарегистрированного event builder?"}
  C -- "Совпало" --> D["Вызывается обработчик (в порядке регистрации)"]
  D --> E{"Внутри обработчика\nraise events.StopPropagation?"}
  E -- "Да" --> F["Остальные обработчики не вызываются"]
  E -- "Нет" --> G["Вызывается следующий подходящий обработчик"]
  C -- "Не совпало" --> H["Обработчик не вызывается, переход к следующему"]
</pre>
<p>Диаграмма показывает: вместо цепочки middleware и иерархии routers из aiogram, в Telethon есть простой, плоский список &mdash; каждый подходящий обработчик срабатывает в порядке регистрации, и это продолжается, пока не будет выброшено <code>events.StopPropagation</code>.</p>
<h3>Что внутри объекта event</h3>
<p>В объекте <code>events.NewMessage.Event</code> есть <code>event.text</code>, <code>event.sender_id</code>, <code>event.chat_id</code>, <code>event.is_private</code>/<code>is_group</code>/<code>is_channel</code>, и самое главное &mdash; методы <code>event.reply()</code> (ответ в чат, как reply) и <code>event.respond()</code> (обычное сообщение, не reply). Они очень похожи на <code>message.answer()</code>/<code>message.reply()</code> из aiogram &mdash; здесь обе библиотеки предлагают почти одинаковое удобство, разница только в модели диспетчеризации.</p>
<h3>Удаление обработчика и несколько фильтров на одну функцию</h3>
<p><code>client.remove_event_handler(callback)</code> &mdash; используется, когда обработчик нужно отключить во время выполнения (например, для временного режима "технических работ"). Также можно повесить на одну функцию несколько декораторов, зарегистрировав её сразу для нескольких разных событий/фильтров &mdash; например, ту же функцию <code>on_ping</code> можно подключить и к <code>events.NewMessage(pattern="/ping")</code>, и отдельно к <code>events.NewMessage(pattern="/hello")</code>, оба будут запускать один и тот же код. Это даёт результат, похожий на объединение нескольких фильтров в одном обработчике aiogram (<code>F.text | Command(...)</code>), только синтаксис другой &mdash; в виде нескольких отдельных слоёв <code>@client.on(...)</code>.</p>""",
"code_content": """\"\"\"Turli xil events.* handlerlari namunasi.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


# 1) Oddiy buyruq -- faqat kiruvchi shaxsiy xabarlarda
@client.on(events.NewMessage(pattern=r"(?i)^/ping$", incoming=True))
async def on_ping(event: events.NewMessage.Event) -> None:
    if event.is_private:
        await event.reply("pong")


# 2) Regex bilan naqsh -- masalan, "eslatma: <matn>" ko'rinishidagi xabarlar
@client.on(events.NewMessage(pattern=re.compile(r"^eslatma:\\s*(.+)$", re.IGNORECASE)))
async def on_reminder(event: events.NewMessage.Event) -> None:
    reminder_text = event.pattern_match.group(1)
    await event.respond(f"Eslatma saqlandi: {reminder_text!r}")
    raise events.StopPropagation  # boshqa handlerlar bu xabar uchun ishga tushmasin


# 3) Faqat belgilangan kanal/guruhlardagi xabarlarni kuzatish
MONITORED_CHATS = [-1001234567890]  # kanal/guruh ID'lari


@client.on(events.NewMessage(chats=MONITORED_CHATS))
async def on_monitored_message(event: events.NewMessage.Event) -> None:
    print(f"[Kuzatilayotgan chat] {event.chat_id}: {event.text[:80]!r}")


# 4) Guruhga a'zo qo'shilganda/chiqqanda
@client.on(events.ChatAction())
async def on_chat_action(event: events.ChatAction.Event) -> None:
    if event.user_joined or event.user_added:
        user = await event.get_user()
        print(f"Yangi a'zo: {user.first_name}")
    elif event.user_left or event.user_kicked:
        print("Bir a'zo chiqib ketdi/chiqarildi.")


# 5) Xabar tahrirlanganda kuzatish
@client.on(events.MessageEdited())
async def on_message_edited(event: events.MessageEdited.Event) -> None:
    print(f"Xabar tahrirlandi (id={event.id}): {event.text[:80]!r}")


# 6) Dinamik ravishda handler qo'shish (dekoratorsiz)
async def dynamic_handler(event: events.NewMessage.Event) -> None:
    await event.reply("Dinamik ro'yxatga olingan handler ishladi.")


def register_dynamic_handler() -> None:
    client.add_event_handler(dynamic_handler, events.NewMessage(pattern="/dinamik"))


async def main() -> None:
    register_dynamic_handler()
    async with client:
        print("Handlerlar tayyor, tinglanmoqda...")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Пример обработчиков разных events.*.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


# 1) Простая команда -- только во входящих личных сообщениях
@client.on(events.NewMessage(pattern=r"(?i)^/ping$", incoming=True))
async def on_ping(event: events.NewMessage.Event) -> None:
    if event.is_private:
        await event.reply("pong")


# 2) Шаблон с regex -- например, сообщения вида "напоминание: <текст>"
@client.on(events.NewMessage(pattern=re.compile(r"^напоминание:\\s*(.+)$", re.IGNORECASE)))
async def on_reminder(event: events.NewMessage.Event) -> None:
    reminder_text = event.pattern_match.group(1)
    await event.respond(f"Напоминание сохранено: {reminder_text!r}")
    raise events.StopPropagation  # остальные обработчики для этого сообщения не сработают


# 3) Отслеживание сообщений только из указанных каналов/групп
MONITORED_CHATS = [-1001234567890]  # ID каналов/групп


@client.on(events.NewMessage(chats=MONITORED_CHATS))
async def on_monitored_message(event: events.NewMessage.Event) -> None:
    print(f"[Отслеживаемый чат] {event.chat_id}: {event.text[:80]!r}")


# 4) Когда участник добавлен/вышел из группы
@client.on(events.ChatAction())
async def on_chat_action(event: events.ChatAction.Event) -> None:
    if event.user_joined or event.user_added:
        user = await event.get_user()
        print(f"Новый участник: {user.first_name}")
    elif event.user_left or event.user_kicked:
        print("Участник вышел/был удалён.")


# 5) Отслеживание редактирования сообщений
@client.on(events.MessageEdited())
async def on_message_edited(event: events.MessageEdited.Event) -> None:
    print(f"Сообщение отредактировано (id={event.id}): {event.text[:80]!r}")


# 6) Динамическое добавление обработчика (без декоратора)
async def dynamic_handler(event: events.NewMessage.Event) -> None:
    await event.reply("Сработал динамически зарегистрированный обработчик.")


def register_dynamic_handler() -> None:
    client.add_event_handler(dynamic_handler, events.NewMessage(pattern="/dinamik"))


async def main() -> None:
    register_dynamic_handler()
    async with client:
        print("Обработчики готовы, ожидание событий...")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: 3 xil event handler yozing""",
"task_title_ru": """Практика: напишите 3 разных обработчика событий""",
"task_description": """Kamida uchta turli event handler yozing: (1) NewMessage orqali /holat buyrug'iga javob beruvchi, (2) ChatAction orqali guruhga yangi a'zo qo'shilganda salomlashuvchi, (3) MessageEdited orqali xabar tahrirlanganini konsolga chiqaruvchi. Kamida bittasida chats yoki from_users filtri ishlatilgan bo'lsin.""",
"task_description_ru": """Напишите минимум три разных обработчика событий: (1) через NewMessage отвечающий на команду /status, (2) через ChatAction приветствующий нового участника группы, (3) через MessageEdited выводящий в консоль факт редактирования сообщения. Минимум в одном должен использоваться фильтр chats или from_users.""",
"task_requirements": """Kamida 3 ta event handler; kamida bitta filtr (chats/from_users/pattern) ishlatilgan; barcha handlerlar async def bo'lishi shart.""",
"task_requirements_ru": """Минимум 3 обработчика событий; минимум один фильтр (chats/from_users/pattern) использован; все обработчики должны быть async def.""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 4,
},
"sample": {
"title": """Namuna: oddiy buyruq-asosli userbot skeleti""",
"description": """Bir nechta events.NewMessage handlerlariga ega, ishga tushirishga tayyor userbot skeleti""",
"sample_type": "code",
"code_files": [
{"filename": "userbot_skeleton.py", "language": "python", "code": """import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

COMMANDS = {}


def command(name):
    def decorator(func):
        COMMANDS[name] = func
        return func
    return decorator


@command("/holat")
async def cmd_status(event):
    await event.reply("Userbot ishlamoqda va tayyor.")


@command("/vaqt")
async def cmd_time(event):
    from datetime import datetime
    await event.reply(f"Joriy vaqt: {datetime.now().strftime('%H:%M:%S')}")


@client.on(events.NewMessage(outgoing=True, pattern=r"^/\\w+$"))
async def dispatch_command(event):
    handler = COMMANDS.get(event.text)
    if handler:
        await handler(event)


if __name__ == "__main__":
    with client:
        print("Userbot ishga tushdi. Buyruqlar:", list(COMMANDS.keys()))
        client.run_until_disconnected()
"""},
],
},
"exercises": [
{
"title": """Telethon'da handlerlarni ro'yxatga olish""",
"title_ru": """Регистрация обработчиков в Telethon""",
"description": """aiogram'dan farqli o'laroq, Telethon'da handlerlarni ro'yxatga olish uchun alohida qanday obyekt kerak?""",
"description_ru": """В отличие от aiogram, какой отдельный объект нужен в Telethon для регистрации обработчиков?""",
"exercise_type": "multiple_choice",
"options": ["Alohida Dispatcher obyekti shart", "Alohida Router obyekti shart", "Hech qanday alohida obyekt shart emas -- TelegramClient o'zi bajaradi", "Alohida Middleware zanjiri shart"],
"options_ru": ["Обязателен отдельный объект Dispatcher", "Обязателен отдельный объект Router", "Отдельный объект не нужен -- TelegramClient делает это сам", "Обязательна отдельная цепочка Middleware"],
"correct_answers": "C",
"is_multiple_select": False,
"hint": """TelegramClient ham client, ham dispetcher vazifasini bajaradi.""",
"hint_ru": """TelegramClient выполняет роль и клиента, и диспетчера.""",
"explanation": """aiogram'dagi Dispatcher/Router modelidan farqli, Telethon'da TelegramClient.on() yoki add_event_handler() orqali handlerlar to'g'ridan-to'g'ri clientning o'ziga ro'yxatga olinadi.""",
"difficulty_level": "Easy",
"points": 8,
},
{
"title": """MessageDeleted eventida nima yo'q""",
"title_ru": """Чего нет в событии MessageDeleted""",
"description": """events.MessageDeleted hodisasi ishga tushganda, handler ichida odatda NIMA mavjud EMAS?""",
"description_ru": """Когда срабатывает событие events.MessageDeleted, чего обычно НЕТ внутри обработчика?""",
"exercise_type": "multiple_choice",
"options": ["O'chirilgan xabarning ID raqami", "O'chirilgan xabar joylashgan chat ID", "O'chirilgan xabarning matni", "Hodisa ro'y bergan vaqt"],
"options_ru": ["ID-номер удалённого сообщения", "ID чата, где было сообщение", "Текст удалённого сообщения", "Время события"],
"correct_answers": "C",
"is_multiple_select": False,
"hint": """Telegram o'chirilgan xabar mazmunini saqlab qolmaydi.""",
"hint_ru": """Telegram не сохраняет содержимое удалённого сообщения.""",
"explanation": """Telegram serveri o'chirilgan xabarning matnini hech qayerda saqlamaydi, shuning uchun MessageDeleted faqat ID(lar)ni beradi -- asl matnni olish uchun uni oldindan (masalan, NewMessage orqali) o'zingiz saqlab qo'ygan bo'lishingiz kerak.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Event dispatch oqimini tartiblang""",
"title_ru": """Расположите поток диспетчеризации событий по порядку""",
"description": """Yangi update kelganidan handler ishlashigacha bo'lgan ketma-ketlikni tuzing.""",
"description_ru": """Составьте последовательность от получения нового апдейта до срабатывания обработчика.""",
"exercise_type": "drag_and_drop",
"drag_items": ["Yangi Update Telegram serveridan keladi", "TelegramClient ichki dispatch tsikli uni qabul qiladi", "Ro'yxatga olingan har bir event builder filtriga tekshiriladi", "Mos keluvchi handler(lar) ro'yxatga olingan tartibda chaqiriladi", "StopPropagation ko'tarilmaguncha keyingi mos handler ham ishlaydi"],
"drag_items_ru": ["Новый Update приходит с сервера Telegram", "Внутренний цикл диспетчеризации TelegramClient принимает его", "Проверяется соответствие фильтру каждого зарегистрированного event builder", "Вызываются подходящие обработчики в порядке регистрации", "Пока не выброшен StopPropagation, срабатывает и следующий подходящий обработчик"],
"correct_order": ["Yangi Update Telegram serveridan keladi", "TelegramClient ichki dispatch tsikli uni qabul qiladi", "Ro'yxatga olingan har bir event builder filtriga tekshiriladi", "Mos keluvchi handler(lar) ro'yxatga olingan tartibda chaqiriladi", "StopPropagation ko'tarilmaguncha keyingi mos handler ham ishlaydi"],
"hint": """Server -> ichki tsikl -> filtr tekshiruvi -> chaqiruv -> davomiylik.""",
"hint_ru": """Сервер -> внутренний цикл -> проверка фильтра -> вызов -> продолжение.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Boshqa handlerlarni to'xtatish""",
"title_ru": """Остановка остальных обработчиков""",
"description": """Bir handler ishlagandan keyin qolgan mos handlerlar ishga tushmasligi uchun qanday istisno ko'tariladi: events.___""",
"description_ru": """Какое исключение выбрасывается, чтобы после срабатывания одного обработчика остальные подходящие не вызывались: events.___""",
"exercise_type": "fill_in_blank",
"correct_answers": "StopPropagation",
"hint": """Nomi "tarqalishni to'xtatish" ma'nosini bildiradi.""",
"hint_ru": """Название означает "остановить распространение".""",
"difficulty_level": "Medium",
"points": 8,
},
],
},
{
"order": 5,
"title": """6-Tarixni ommaviy o'qish: iter_messages, sahifalash va tezlik cheklovlari""",
"title_ru": """6-Массовое чтение истории: iter_messages, пагинация и ограничения скорости""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>get_messages emas, iter_messages -- katta hajm uchun</h3>
<p>4-darsda ko'rgan <code>get_messages(limit=N)</code> qulay, lekin u BARCHA N ta xabarni bir vaqtning o'zida xotiraga yuklaydi &mdash; agar N o'nlab minglab bo'lsa, bu muammoli. <code>client.iter_messages(entity, limit=None, ...)</code> esa <strong>async generator</strong>: u xabarlarni kichik partiyalarda (odatda 100 tadan) so'rab, ularni birma-bir <code>async for</code> orqali beradi. Xotira sarfi doim bir xil, hajm N=100 bo'ladimi yoki N=100000 &mdash; farqi yo'q.</p>
<h3>Sahifalash parametrlari</h3>
<table>
<tr><th>Parametr</th><th>Vazifasi</th></tr>
<tr><td><code>limit</code></td><td>Jami nechta xabar kerak (<code>None</code> &mdash; cheksiz, to'liq tarix)</td></tr>
<tr><td><code>offset_date</code></td><td>Faqat shu sanadan oldingi/keyingi xabarlar (<code>reverse</code>ga bog'liq)</td></tr>
<tr><td><code>offset_id</code></td><td>Shu ID'dan boshlab (masalan, oldingi to'xtagan joyni davom ettirish uchun)</td></tr>
<tr><td><code>min_id</code> / <code>max_id</code></td><td>Faqat shu ID oralig'idagi xabarlar</td></tr>
<tr><td><code>reverse</code></td><td><code>True</code> bo'lsa &mdash; eng eskisidan eng yangisiga (xronologik tartib); <code>False</code> (standart) &mdash; teskari</td></tr>
<tr><td><code>search</code></td><td>Matn bo'yicha qidiruv (server tomonda amalga oshadi, tezroq)</td></tr>
<tr><td><code>from_user</code></td><td>Faqat muayyan yuboruvchidan</td></tr>
</table>
<p>Katta arxivni oxirgi to'xtagan joydan davom ettirish uchun eng ishonchli yondashuv &mdash; oxirgi qayta ishlangan xabar ID'sini biror joyga (fayl, DB) saqlab, keyingi ishga tushirishda <code>offset_id=last_saved_id, reverse=True</code> bilan davom ettirish.</p>
<h3>FloodWaitError -- bu yerda muqarrar, hazil emas</h3>
<p>Telegram serverlari ma'lum vaqt oralig'ida qancha so'rov qabul qilishga cheklov qo'yadi. Katta tarixni tez-tez so'rasangiz, <code>FloodWaitError</code> qaytadi &mdash; <code>e.seconds</code> xususiyati aynan qancha kutish kerakligini bildiradi. Telethon buni QISMAN o'zi boshqaradi (ba'zi ichki so'rovlarni avtomatik qayta urinadi), lekin <code>iter_messages</code> siklidagi o'zingiz yozgan kod (masalan, har bir xabar uchun DB yozuvi) bu himoyadan tashqarida &mdash; shu qismni o'zingiz himoya qilishingiz kerak.</p>
<pre class="mermaid">
flowchart TB
  A["iter_messages(entity, limit=None) chaqiriladi"] --> B["Telethon 100 talik partiyalarni so'raydi"]
  B --> C{"Server FloodWaitError\nqaytardimi?"}
  C -- "Ha" --> D["e.seconds soniya kutiladi"]
  D --> B
  C -- "Yo'q" --> E["Partiya xabarlari birma-bir 'yield' qilinadi"]
  E --> F["async for tsiklida sizning kodingiz ishlaydi (masalan DB'ga yozish)"]
  F --> G{"Yana xabar bormi?"}
  G -- "Ha" --> B
  G -- "Yo'q" --> H["Iteratsiya tugadi"]
</pre>
<p>Diagramma shuni ko'rsatadi: Telethon o'zi partiyalash va qayta urinishni boshqaradi, lekin sizning <code>async for</code> ichidagi kodingiz sekin bo'lsa (masalan, har bir xabar uchun tashqi API'ga so'rov yuborsangiz), bu butun jarayonni sekinlashtiradi &mdash; shuning uchun og'ir ishlarni partiyalab (masalan, 50 tadan) bajarish tavsiya etiladi.</p>
<h3>wait_time parametri</h3>
<p><code>iter_messages(..., wait_time=N)</code> &mdash; har bir so'rov orasida kamida N soniya kutishni majburlaydi, hatto FloodWaitError kelmasa ham. Bu "ehtiyotkorlik uchun sekinlashtirish" &mdash; ayniqsa yangi yoki kam faol hisoblar bilan katta tarixni skanerlashda foydali, chunki tezlik cheklovi chegarasiga yaqinlashishning o'zi ba'zan hisobni "shubhali" deb belgilashga sabab bo'ladi (7-darsda batafsil).</p>
<h3>Server tomonidagi filtrlar -- barcha xabarni yuklamasdan</h3>
<p><code>iter_messages</code> yana <code>filter</code> parametrini qabul qiladi &mdash; bu <code>telethon.tl.types</code> ichidagi <code>InputMessagesFilterPhotos</code>, <code>InputMessagesFilterDocument</code>, <code>InputMessagesFilterVideo</code> kabi maxsus klasslar bo'lib, faqat mos turdagi xabarlarni <strong>server tomonida</strong> filtrlaydi &mdash; ya'ni butun tarixni o'zingiz yuklab, keyin Python'da filtrlashdan ko'ra ancha tejamli. Masalan, <code>client.iter_messages(chat, filter=InputMessagesFilterPhotos)</code> faqat rasmli xabarlarni qaytaradi &mdash; bu 8-darsda ko'radigan ommaviy media yuklab olish bilan bevosita bog'liq: avval kerakli xabarlarni server tomonida ajratib olish, keyin faqat ularni yuklab olish ancha samarali.</p>""",
"text_content_ru": """<h3>Не get_messages, а iter_messages -- для больших объёмов</h3>
<p><code>get_messages(limit=N)</code> из урока 4 удобен, но он загружает ВСЕ N сообщений в память одновременно &mdash; если N составляет десятки тысяч, это проблематично. <code>client.iter_messages(entity, limit=None, ...)</code> &mdash; это <strong>асинхронный генератор</strong>: он запрашивает сообщения небольшими партиями (обычно по 100), выдавая их по одному через <code>async for</code>. Расход памяти всегда одинаков, независимо от того, N=100 или N=100000.</p>
<h3>Параметры пагинации</h3>
<table>
<tr><th>Параметр</th><th>Назначение</th></tr>
<tr><td><code>limit</code></td><td>Сколько всего сообщений нужно (<code>None</code> &mdash; без ограничения, вся история)</td></tr>
<tr><td><code>offset_date</code></td><td>Только сообщения до/после этой даты (зависит от <code>reverse</code>)</td></tr>
<tr><td><code>offset_id</code></td><td>Начиная с этого ID (например, чтобы продолжить с места остановки)</td></tr>
<tr><td><code>min_id</code> / <code>max_id</code></td><td>Только сообщения в этом диапазоне ID</td></tr>
<tr><td><code>reverse</code></td><td><code>True</code> &mdash; от самого старого к самому новому (хронологический порядок); <code>False</code> (по умолчанию) &mdash; обратный</td></tr>
<tr><td><code>search</code></td><td>Поиск по тексту (выполняется на стороне сервера, быстрее)</td></tr>
<tr><td><code>from_user</code></td><td>Только от конкретного отправителя</td></tr>
</table>
<p>Самый надёжный способ продолжить обработку большого архива с места остановки &mdash; сохранить ID последнего обработанного сообщения куда-нибудь (файл, БД) и при следующем запуске продолжить с <code>offset_id=last_saved_id, reverse=True</code>.</p>
<h3>FloodWaitError -- здесь неизбежен, и это не шутка</h3>
<p>Серверы Telegram ограничивают количество запросов за определённый промежуток времени. Если слишком часто запрашивать большую историю, вернётся <code>FloodWaitError</code> &mdash; свойство <code>e.seconds</code> указывает, сколько именно секунд нужно подождать. Telethon ЧАСТИЧНО управляет этим сам (некоторые внутренние запросы повторяет автоматически), но код, написанный вами внутри цикла <code>iter_messages</code> (например, запись в БД для каждого сообщения), находится вне этой защиты &mdash; эту часть нужно защищать самостоятельно.</p>
<pre class="mermaid">
flowchart TB
  A["Вызывается iter_messages(entity, limit=None)"] --> B["Telethon запрашивает партии по 100"]
  B --> C{"Сервер вернул\nFloodWaitError?"}
  C -- "Да" --> D["Ожидание e.seconds секунд"]
  D --> B
  C -- "Нет" --> E["Сообщения партии выдаются ('yield') по одному"]
  E --> F["В цикле async for выполняется ваш код (например, запись в БД)"]
  F --> G{"Есть ещё сообщения?"}
  G -- "Да" --> B
  G -- "Нет" --> H["Итерация завершена"]
</pre>
<p>Диаграмма показывает: Telethon сам управляет разбиением на партии и повторными попытками, но если код внутри вашего <code>async for</code> медленный (например, вы делаете запрос к внешнему API для каждого сообщения), это замедляет весь процесс &mdash; поэтому тяжёлую работу рекомендуется выполнять партиями (например, по 50).</p>
<h3>Параметр wait_time</h3>
<p><code>iter_messages(..., wait_time=N)</code> &mdash; принудительно ждёт минимум N секунд между запросами, даже если FloodWaitError не приходит. Это "подстраховочное замедление" &mdash; особенно полезно при сканировании большой истории новыми или малоактивными аккаунтами, потому что само приближение к границе лимита скорости иногда приводит к тому, что аккаунт помечается как "подозрительный" (подробно в уроке 7).</p>
<h3>Фильтры на стороне сервера -- без загрузки всех сообщений</h3>
<p><code>iter_messages</code> также принимает параметр <code>filter</code> &mdash; это специальные классы из <code>telethon.tl.types</code>, такие как <code>InputMessagesFilterPhotos</code>, <code>InputMessagesFilterDocument</code>, <code>InputMessagesFilterVideo</code>, фильтрующие только сообщения нужного типа <strong>на стороне сервера</strong> &mdash; то есть гораздо экономнее, чем загрузить всю историю самому и потом фильтровать в Python. Например, <code>client.iter_messages(chat, filter=InputMessagesFilterPhotos)</code> вернёт только сообщения с фото &mdash; это напрямую связано с массовой загрузкой медиа из урока 8: сначала отобрать нужные сообщения на стороне сервера, а уже потом загружать только их — гораздо эффективнее.</p>""",
"code_content": """\"\"\"iter_messages orqali katta tarixni sahifalab, davom ettirib o'qish.
pip install telethon python-dotenv
\"\"\"
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

PROGRESS_FILE = Path("scan_progress.json")


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def save_progress(chat_key: str, last_id: int) -> None:
    progress = load_progress()
    progress[chat_key] = last_id
    PROGRESS_FILE.write_text(json.dumps(progress))


async def scan_full_history(chat: str, batch_size: int = 50) -> None:
    \"\"\"Chatning to'liq tarixini xronologik tartibda, oldingi to'xtagan
    joydan davom ettirib skanerlaydi.\"\"\"
    progress = load_progress()
    last_id = progress.get(chat, 0)
    processed = 0
    batch: list[str] = []

    async def flush_batch() -> None:
        if not batch:
            return
        # Bu yerda haqiqiy loyihada DB'ga bulk insert bo'lardi.
        print(f"  -- {len(batch)} ta xabar saqlandi (batch)")
        batch.clear()

    try:
        async for message in client.iter_messages(
            chat, reverse=True, offset_id=last_id, wait_time=1
        ):
            if message.text:
                batch.append(message.text)
            if len(batch) >= batch_size:
                await flush_batch()
            processed += 1
            last_id = message.id

            if processed % 500 == 0:
                save_progress(chat, last_id)
                print(f"Progress saqlandi: {processed} ta xabar, oxirgi id={last_id}")
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds} soniya kutamiz va progressni saqlaymiz.")
        save_progress(chat, last_id)
        await asyncio.sleep(e.seconds)
        await scan_full_history(chat, batch_size)  # davom ettirish
        return

    await flush_batch()
    save_progress(chat, last_id)
    print(f"Skanerlash tugadi: jami {processed} ta xabar qayta ishlandi.")


async def main() -> None:
    async with client:
        await scan_full_history("@ochiq_kanal_namunasi")


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Массовое чтение большой истории с пагинацией и продолжением через iter_messages.
pip install telethon python-dotenv
\"\"\"
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

PROGRESS_FILE = Path("scan_progress.json")


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def save_progress(chat_key: str, last_id: int) -> None:
    progress = load_progress()
    progress[chat_key] = last_id
    PROGRESS_FILE.write_text(json.dumps(progress))


async def scan_full_history(chat: str, batch_size: int = 50) -> None:
    \"\"\"Сканирует полную историю чата в хронологическом порядке,
    продолжая с места предыдущей остановки.\"\"\"
    progress = load_progress()
    last_id = progress.get(chat, 0)
    processed = 0
    batch: list[str] = []

    async def flush_batch() -> None:
        if not batch:
            return
        # В реальном проекте здесь был бы bulk insert в БД.
        print(f"  -- сохранено {len(batch)} сообщений (партия)")
        batch.clear()

    try:
        async for message in client.iter_messages(
            chat, reverse=True, offset_id=last_id, wait_time=1
        ):
            if message.text:
                batch.append(message.text)
            if len(batch) >= batch_size:
                await flush_batch()
            processed += 1
            last_id = message.id

            if processed % 500 == 0:
                save_progress(chat, last_id)
                print(f"Прогресс сохранён: {processed} сообщений, последний id={last_id}")
    except FloodWaitError as e:
        print(f"FloodWait: ждём {e.seconds} секунд и сохраняем прогресс.")
        save_progress(chat, last_id)
        await asyncio.sleep(e.seconds)
        await scan_full_history(chat, batch_size)  # продолжение
        return

    await flush_batch()
    save_progress(chat, last_id)
    print(f"Сканирование завершено: всего обработано {processed} сообщений.")


async def main() -> None:
    async with client:
        await scan_full_history("@пример_открытого_канала")


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: davom ettiriladigan tarix skaneri""",
"task_title_ru": """Практика: сканер истории с возможностью продолжения""",
"task_description": """scan_full_history() funksiyasidan foydalanib, o'zingiz a'zo bo'lgan biror ochiq kanal yoki guruhning tarixini skanerlang. Skriptni ishga tushiring, uni to'xtating (Ctrl+C), keyin qayta ishga tushirib, u oldingi to'xtagan joydan davom etishini tekshiring.""",
"task_description_ru": """Используя функцию scan_full_history(), просканируйте историю какого-нибудь открытого канала или группы, участником которых вы являетесь. Запустите скрипт, остановите его (Ctrl+C), затем запустите заново и убедитесь, что он продолжает с места предыдущей остановки.""",
"task_requirements": """scan_progress.json fayli orqali progress saqlanishi va o'qilishi kerak; FloodWaitError to'g'ri ushlangan bo'lishi; qayta ishga tushirishda takroriy xabarlar qayta ishlanmasligi kerak.""",
"task_requirements_ru": """Прогресс должен сохраняться и читаться через файл scan_progress.json; FloodWaitError должен корректно обрабатываться; при повторном запуске одни и те же сообщения не должны обрабатываться повторно.""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 4,
},
"sample": {
"title": """Namuna: kanal statistikasi yig'uvchi skript""",
"description": """iter_messages orqali kanal xabarlarini skanerlab, eng faol soatlar va o'rtacha xabar uzunligini hisoblovchi skript""",
"sample_type": "code",
"code_files": [
{"filename": "channel_stats.py", "language": "python", "code": """import asyncio
import os
from collections import Counter

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def collect_stats(chat: str, limit: int = 2000) -> None:
    hour_counter: Counter = Counter()
    total_len = 0
    total_count = 0

    async with client:
        async for message in client.iter_messages(chat, limit=limit, wait_time=0.5):
            if not message.text:
                continue
            hour_counter[message.date.hour] += 1
            total_len += len(message.text)
            total_count += 1

    print(f"Tahlil qilingan xabarlar: {total_count}")
    if total_count:
        print(f"O'rtacha uzunlik: {total_len / total_count:.1f} belgi")
    print("Eng faol soatlar (UTC):")
    for hour, count in hour_counter.most_common(5):
        print(f"  {hour:02d}:00 -- {count} ta xabar")


if __name__ == "__main__":
    asyncio.run(collect_stats("@ochiq_kanal_namunasi"))
"""},
],
},
"exercises": [
{
"title": """get_messages va iter_messages orasidagi asosiy farq""",
"title_ru": """Главное отличие get_messages от iter_messages""",
"description": """iter_messages'ni katta hajmdagi tarixni o'qish uchun get_messages(limit=N)dan afzal qiladigan narsa nima?""",
"description_ru": """Что делает iter_messages предпочтительнее get_messages(limit=N) для чтения большого объёма истории?""",
"exercise_type": "multiple_choice",
"options": ["U tezroq ishlaydi, chunki boshqa protokol ishlatadi", "U xabarlarni kichik partiyalarda oladi, xotirani bir xilda ushlab turadi", "U faqat matnli xabarlarni qaytaradi", "U FloodWaitError'ni umuman chiqarmaydi"],
"options_ru": ["Работает быстрее, потому что использует другой протокол", "Получает сообщения небольшими партиями, расход памяти постоянен", "Возвращает только текстовые сообщения", "Вообще не выбрасывает FloodWaitError"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu async generator -- barcha natijani bir vaqtda xotiraga yuklamaydi.""",
"hint_ru": """Это асинхронный генератор -- не загружает весь результат в память сразу.""",
"explanation": """iter_messages xabarlarni ~100 talik partiyalarda so'rab, ularni birma-bir beradi -- shuning uchun N=100 yoki N=100000 bo'lishidan qat'iy nazar xotira sarfi bir xil bo'lib qoladi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Xronologik tartibda o'qish""",
"title_ru": """Чтение в хронологическом порядке""",
"description": """iter_messages'da xabarlarni eng eskisidan eng yangisiga (xronologik) tartibda olish uchun qaysi parametr True qilib beriladi?""",
"description_ru": """Какой параметр в iter_messages нужно установить в True, чтобы получать сообщения от самого старого к самому новому (хронологически)?""",
"exercise_type": "multiple_choice",
"options": ["ascending", "reverse", "chronological", "oldest_first"],
"options_ru": ["ascending", "reverse", "chronological", "oldest_first"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Standart tartib teskari (yangidan eskiga) bo'lgani uchun bu parametr uni "aylantiradi".""",
"hint_ru": """Порядок по умолчанию обратный (от нового к старому), этот параметр его "переворачивает".""",
"explanation": """reverse=True xronologik (eskidan yangiga) tartibni beradi -- bu ayniqsa progress'ni offset_id bilan davom ettirishda muhim, chunki oldinga siljish faqat shu tartibda mantiqiy.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Katta skanerlash oqimini tartiblang""",
"title_ru": """Расположите поток большого сканирования по порядку""",
"description": """Davom ettiriladigan katta tarix skaneri qanday tartibda ishlaydi?""",
"description_ru": """В каком порядке работает сканер большой истории с возможностью продолжения?""",
"exercise_type": "drag_and_drop",
"drag_items": ["Saqlangan progressdan oxirgi ID o'qiladi", "iter_messages offset_id va reverse=True bilan chaqiriladi", "Har bir xabar partiyaga qo'shiladi va davriy ravishda saqlanadi", "FloodWaitError kelsa, kutib, keyin xuddi shu ID'dan davom etiladi", "Iteratsiya tugagach, yakuniy progress saqlanadi"],
"drag_items_ru": ["Читается последний ID из сохранённого прогресса", "Вызывается iter_messages с offset_id и reverse=True", "Каждое сообщение добавляется в партию и периодически сохраняется", "При FloodWaitError -- ожидание, затем продолжение с того же ID", "После завершения итерации сохраняется финальный прогресс"],
"correct_order": ["Saqlangan progressdan oxirgi ID o'qiladi", "iter_messages offset_id va reverse=True bilan chaqiriladi", "Har bir xabar partiyaga qo'shiladi va davriy ravishda saqlanadi", "FloodWaitError kelsa, kutib, keyin xuddi shu ID'dan davom etiladi", "Iteratsiya tugagach, yakuniy progress saqlanadi"],
"hint": """Avval o'qish, keyin so'rov, keyin ishlov, keyin xatolik holati, oxirida saqlash.""",
"hint_ru": """Сначала чтение, потом запрос, потом обработка, потом случай ошибки, в конце сохранение.""",
"difficulty_level": "Hard",
"points": 8,
},
{
"title": """FloodWaitError'ning kutish vaqti""",
"title_ru": """Время ожидания в FloodWaitError""",
"description": """FloodWaitError obyektida necha soniya kutish kerakligini bildiruvchi xususiyat nomi: e.___""",
"description_ru": """Название свойства объекта FloodWaitError, указывающего, сколько секунд нужно подождать: e.___""",
"exercise_type": "fill_in_blank",
"correct_answers": "seconds",
"hint": """Ingliz tilida "soniyalar" so'zi.""",
"hint_ru": """Английское слово "секунды".""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 6,
"title": """7-Kanal/guruhga dasturiy qo'shilish va Telegram ToS/ban xavfi -- halol suhbat""",
"title_ru": """7-Программное вступление в канал/группу и риск бана по ToS Telegram -- честный разговор""",
"points_reward": 13,
"code_language": "python",
"text_content": """<h3>Username orqali qo'shilish -- bir amal, ikkita funksiya</h3>
<p>1-darsda aytilganidek, userbot ochiq kanal/guruhga taklif havolasisiz, faqat username orqali qo'shilishi mumkin. Buning uchun xom API funksiyalari ishlatiladi: ochiq (public) kanal/guruh uchun <code>JoinChannelRequest(channel)</code> (<code>telethon.tl.functions.channels</code>dan), yopiq (faqat taklif havolasi bilan) guruh uchun esa <code>ImportChatInviteRequest(invite_hash)</code> (<code>telethon.tl.functions.messages</code>dan, havoladagi <code>t.me/joinchat/HASH</code> yoki <code>t.me/+HASH</code>dagi HASH qismi bilan). Chiqish uchun &mdash; <code>LeaveChannelRequest(channel)</code>.</p>
<h3>Nega bu "shunchaki bitta API chaqiruvi" emas</h3>
<p>Bot API'da bunday metod umuman yo'q &mdash; chunki Telegram botlarni <em>faqat inson qo'shishi mumkin bo'lgan</em> tarzda ataylab loyihalagan. Userbot esa buni o'zi qila oladi, va aynan shu sabab uni suiiste'mol qilish xavfi kuchli: hisob qisqa vaqt ichida ko'plab guruhga ketma-ket qo'shilsa, bu spam-hisoblarning odatiy xatti-harakati bilan bir xil ko'rinadi.</p>
<h3>Telegram'ning rasmiy pozitsiyasi -- bu gipotetik emas</h3>
<p>Telegram'ning Foydalanish shartlari (Terms of Service) va API foydalanish siyosati aniq belgilaydi: hisoblarni avtomatlashtirish o'zi taqiqlanmagan (aks holda Telethon/Pyrogram kabi kutubxonalar mavjud bo'lmasdi), lekin <strong>ommaviy, so'ralmagan xabar yuborish (spam)</strong>, <strong>hisob-fermalari (bir vaqtda ko'plab soxta/avtomatlashtirilgan hisob yuritish)</strong> va <strong>tezkor, ommaviy guruhlarga qo'shilish/chiqish</strong> singari xatti-harakatlar aniq ta'qiqlangan va kuzatiladi. Telegram'ning o'zi rasmiy repozitoriyasida ham buni ochiq yozadi: uchinchi tomon kutubxonalari (Telethon shu jumladan) orqali ToS'ni buzish hisobni <strong>vaqtincha cheklash</strong> (masalan, ma'lum amallarni bloklash) yoki <strong>butunlay o'chirishga</strong> olib kelishi mumkin. Bu haqiqiy, hujjatlashtirilgan xavf &mdash; nazariy emas.</p>
<pre class="mermaid">
flowchart TB
  A["Userbot qisqa vaqtda ko'plab guruhga qo'shiladi"] --> B{"Telegram bu xatti-harakatni\nspam-signaturaga o'xshatdimi?"}
  B -- "Ha" --> C["PeerFloodError -- vaqtincha ba'zi amallar bloklanadi"]
  C --> D["Davom etsa -- hisob to'liq cheklanishi/bloklanishi mumkin"]
  B -- "Yo'q (sekin, tabiiy tezlikda)" --> E["Odatiy foydalanuvchi xatti-harakati sifatida qabul qilinadi"]
</pre>
<p>Diagramma shuni ko'rsatadi: xavf harakatning O'ZIDA emas (guruhga qo'shilishning o'zi qonuniy), balki uning <strong>tezligi va ko'lamida</strong>. Bir kunda 2-3 ta guruhga qo'shilish odatiy foydalanuvchi xatti-harakati; bir daqiqada 50 tasiga qo'shilish &mdash; bot-signatura.</p>
<h3>Amaliy, mas'uliyatli qo'llanma</h3>
<ul>
<li>Guruhlarga qo'shilish orasida sezilarli tanaffus qo'ying (masalan, bir necha daqiqadan bir necha soatgacha, tasodifiy oraliqda) &mdash; robot ritmidan qoching.</li>
<li><code>PeerFloodError</code>ni albatta ushlang &mdash; bu "juda ko'p ijtimoiy amal (qo'shilish, kontakt qo'shish va h.k.) qilyapsiz" degan aniq signal, darhol to'xtash va kutish kerak.</li>
<li>Faqat <strong>o'zingiz nazorat qiladigan yoki shaxsiy ehtiyoj uchun kerak bo'lgan</strong> kanal/guruhlarga qo'shiling &mdash; ommaviy, tasodifiy ro'yxat bo'yicha "hamma joyga qo'shilish" skriptlari yozmang.</li>
<li>Bitta hisobdan bir nechta avtomatlashtirilgan skript bir vaqtda ishlamasin (session konflikti bilan bir qatorda, bu ham shubhali faoliyat hisoblanadi).</li>
<li>Agar loyihangizga chinakam ko'plab guruhni kuzatish kerak bo'lsa &mdash; buni ilova api_id'siga emas, balki (agar imkon bo'lsa) rasmiy Bot API + guruh admin ruxsati orqali yechishni ko'rib chiqing; userbot faqat Bot API yetarli bo'lmagan holatlar uchun.</li>
</ul>
<h3>Bu kursning pozitsiyasi</h3>
<p>Bu kursda userbot texnikasi <strong>shaxsiy avtomatlashtirish, tadqiqot va o'z kanallaringizni kuzatish</strong> uchun o'rgatiladi &mdash; masalan, o'zingiz admin bo'lgan kanalning statistikasini yig'ish, shaxsiy arxivlash, yoki kichik miqyosdagi monitoring vositalari. Ommaviy spam, kontakt yig'ish yoki hisob-fermalari yaratish &mdash; bu kurs doirasidan tashqarida va ochiq ravishda tavsiya etilmaydi.</p>""",
"text_content_ru": """<h3>Вступление по username -- одно действие, две функции</h3>
<p>Как уже говорилось в уроке 1, юзербот может вступить в открытый канал/группу по username, без ссылки-приглашения. Для этого используются функции сырого API: для открытого (публичного) канала/группы &mdash; <code>JoinChannelRequest(channel)</code> (из <code>telethon.tl.functions.channels</code>), для закрытой группы (только по ссылке-приглашению) &mdash; <code>ImportChatInviteRequest(invite_hash)</code> (из <code>telethon.tl.functions.messages</code>, с частью HASH из ссылки <code>t.me/joinchat/HASH</code> или <code>t.me/+HASH</code>). Для выхода &mdash; <code>LeaveChannelRequest(channel)</code>.</p>
<h3>Почему это не "просто ещё один вызов API"</h3>
<p>В Bot API такого метода вообще нет &mdash; потому что Telegram намеренно спроектировал ботов так, что их <em>может добавить только человек</em>. Юзербот же может делать это сам, и именно поэтому риск злоупотребления высок: если аккаунт за короткое время вступает подряд во множество групп, это выглядит точно так же, как типичное поведение спам-аккаунтов.</p>
<h3>Официальная позиция Telegram -- это не гипотеза</h3>
<p>Условия использования (ToS) и политика использования API Telegram чётко определяют: сама по себе автоматизация аккаунтов не запрещена (иначе не существовало бы таких библиотек, как Telethon/Pyrogram), но <strong>массовая рассылка нежелательных сообщений (спам)</strong>, <strong>фермы аккаунтов (одновременное ведение множества фейковых/автоматизированных аккаунтов)</strong> и <strong>быстрое массовое вступление/выход из групп</strong> прямо запрещены и отслеживаются. Сам Telegram в своём официальном репозитории открыто пишет: нарушение ToS через сторонние библиотеки (включая Telethon) может привести к <strong>временному ограничению</strong> аккаунта (блокировке определённых действий) или к его <strong>полной блокировке</strong>. Это реальный, задокументированный риск, а не теория.</p>
<pre class="mermaid">
flowchart TB
  A["Юзербот за короткое время вступает во множество групп"] --> B{"Telegram распознал поведение\nкак спам-сигнатуру?"}
  B -- "Да" --> C["PeerFloodError -- некоторые действия временно блокируются"]
  C --> D["При продолжении -- аккаунт может быть полностью ограничен/заблокирован"]
  B -- "Нет (медленно, в естественном темпе)" --> E["Воспринимается как обычное поведение пользователя"]
</pre>
<p>Диаграмма показывает: риск не в самом действии (вступление в группу само по себе законно), а в его <strong>скорости и масштабе</strong>. Вступление в 2-3 группы за день &mdash; обычное поведение пользователя; вступление в 50 групп за минуту &mdash; сигнатура бота.</p>
<h3>Практическое, ответственное руководство</h3>
<ul>
<li>Делайте заметные паузы между вступлениями в группы (например, от нескольких минут до нескольких часов, в случайном интервале) &mdash; избегайте роботического ритма.</li>
<li>Обязательно ловите <code>PeerFloodError</code> &mdash; это чёткий сигнал "вы совершаете слишком много социальных действий (вступление, добавление контактов и т.д.)", нужно немедленно остановиться и подождать.</li>
<li>Вступайте только в те каналы/группы, которые вы <strong>сами контролируете или которые действительно нужны для личных целей</strong> &mdash; не пишите скрипты "вступить везде" по массовому случайному списку.</li>
<li>Не запускайте одновременно несколько автоматизированных скриптов с одного аккаунта (помимо конфликта сессии, это тоже расценивается как подозрительная активность).</li>
<li>Если вашему проекту действительно нужно отслеживать множество групп &mdash; рассмотрите решение через официальный Bot API + права администратора группы (если возможно); юзербот нужен только там, где Bot API объективно недостаточно.</li>
</ul>
<h3>Позиция этого курса</h3>
<p>В этом курсе техника юзербота преподаётся для <strong>личной автоматизации, исследований и отслеживания собственных каналов</strong> &mdash; например, сбор статистики канала, где вы сами администратор, личное архивирование, или небольшие инструменты мониторинга. Массовый спам, сбор контактов или создание ферм аккаунтов &mdash; вне рамок этого курса и прямо не рекомендуются.</p>""",
"code_content": """\"\"\"Kanal/guruhga xavfsiz, tezlikni cheklab qo'shilish namunasi.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import random

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PeerFloodError,
    FloodWaitError,
    UserAlreadyParticipantError,
    InviteHashExpiredError,
)
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def join_public_channel_safely(username: str) -> bool:
    \"\"\"Ochiq kanalga qo'shilish -- xatoliklarni to'g'ri ushlab.\"\"\"
    try:
        await client(JoinChannelRequest(username))
        print(f"Muvaffaqiyatli qo'shildi: {username}")
        return True
    except UserAlreadyParticipantError:
        print(f"Allaqachon a'zo: {username}")
        return True
    except PeerFloodError:
        print(
            "PeerFloodError -- juda ko'p ijtimoiy amal bajarilyapti. "
            "DARHOL to'xtash va bir necha soat kutish kerak."
        )
        return False
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds} soniya kutish kerak.")
        return False


async def join_private_group_by_invite(invite_hash: str) -> bool:
    \"\"\"Yopiq guruhga taklif havolasi orqali qo'shilish.\"\"\"
    try:
        await client(ImportChatInviteRequest(invite_hash))
        print("Yopiq guruhga muvaffaqiyatli qo'shildi.")
        return True
    except InviteHashExpiredError:
        print("Taklif havolasi muddati o'tgan yoki bekor qilingan.")
        return False
    except PeerFloodError:
        print("PeerFloodError -- to'xtash kerak.")
        return False


async def join_many_with_responsible_pacing(usernames: list[str]) -> None:
    \"\"\"MAS'ULIYATLI namuna: guruhga qo'shilishlar orasida tasodifiy,
    sezilarli tanaffus bilan. Ommaviy, tez qo'shilish HECH QACHON
    tavsiya etilmaydi -- bu shunchaki xavfni kamaytiruvchi namuna,
    ommaviy avtomatlashtirishni rag'batlantirish emas.\"\"\"
    for username in usernames:
        ok = await join_public_channel_safely(username)
        if not ok:
            print("Xavfsizlik uchun jarayon to'xtatildi.")
            break
        pause = random.uniform(120, 600)  # 2-10 daqiqa
        print(f"Keyingi qo'shilishgacha {pause / 60:.1f} daqiqa kutamiz...")
        await asyncio.sleep(pause)


async def main() -> None:
    async with client:
        # Faqat DEMO uchun -- haqiqiy ro'yxat juda kichik bo'lishi kerak
        await join_many_with_responsible_pacing(["@ochiq_kanal_namunasi"])


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Пример безопасного вступления в канал/группу с ограничением скорости.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import random

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PeerFloodError,
    FloodWaitError,
    UserAlreadyParticipantError,
    InviteHashExpiredError,
)
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def join_public_channel_safely(username: str) -> bool:
    \"\"\"Вступление в открытый канал -- с корректной обработкой ошибок.\"\"\"
    try:
        await client(JoinChannelRequest(username))
        print(f"Успешно вступили: {username}")
        return True
    except UserAlreadyParticipantError:
        print(f"Уже участник: {username}")
        return True
    except PeerFloodError:
        print(
            "PeerFloodError -- выполняется слишком много социальных действий. "
            "НЕМЕДЛЕННО остановиться и подождать несколько часов."
        )
        return False
    except FloodWaitError as e:
        print(f"FloodWait: нужно подождать {e.seconds} секунд.")
        return False


async def join_private_group_by_invite(invite_hash: str) -> bool:
    \"\"\"Вступление в закрытую группу по ссылке-приглашению.\"\"\"
    try:
        await client(ImportChatInviteRequest(invite_hash))
        print("Успешно вступили в закрытую группу.")
        return True
    except InviteHashExpiredError:
        print("Срок действия ссылки-приглашения истёк или она отозвана.")
        return False
    except PeerFloodError:
        print("PeerFloodError -- нужно остановиться.")
        return False


async def join_many_with_responsible_pacing(usernames: list[str]) -> None:
    \"\"\"ОТВЕТСТВЕННЫЙ пример: с заметной случайной паузой между
    вступлениями в группы. Массовое, быстрое вступление НИКОГДА не
    рекомендуется -- это просто пример снижения риска, а не поощрение
    массовой автоматизации.\"\"\"
    for username in usernames:
        ok = await join_public_channel_safely(username)
        if not ok:
            print("Процесс остановлен из соображений безопасности.")
            break
        pause = random.uniform(120, 600)  # 2-10 минут
        print(f"Ждём {pause / 60:.1f} минут до следующего вступления...")
        await asyncio.sleep(pause)


async def main() -> None:
    async with client:
        # Только для ДЕМОНСТРАЦИИ -- реальный список должен быть очень коротким
        await join_many_with_responsible_pacing(["@пример_открытого_канала"])


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: xavfsiz qo'shilish skriptini xatoliklar bilan sinang""",
"task_title_ru": """Практика: протестируйте безопасный скрипт вступления с обработкой ошибок""",
"task_description": """join_public_channel_safely() funksiyasidan foydalanib, o'zingiz allaqachon a'zo bo'lgan bitta kanalga "qayta qo'shilishga" urinib ko'ring (UserAlreadyParticipantError qanday ushlanishini kuzating), so'ngra mavjud bo'lmagan/noto'g'ri username bilan sinab ko'ring. Ikkala holat uchun ham tushunarli konsol xabari chiqishi kerak.""",
"task_description_ru": """Используя функцию join_public_channel_safely(), попробуйте "повторно вступить" в канал, где вы уже состоите (понаблюдайте, как обрабатывается UserAlreadyParticipantError), затем попробуйте с несуществующим/неверным username. Для обоих случаев должно выводиться понятное сообщение в консоли.""",
"task_requirements": """Kamida 3 xil istisno holati (muvaffaqiyat, allaqachon a'zo, xatolik) alohida ko'rsatilgan bo'lishi; qo'shilishlar orasida tasodifiy tanaffus mavjud bo'lishi kerak.""",
"task_requirements_ru": """Минимум 3 разных случая (успех, уже участник, ошибка) должны быть показаны отдельно; между вступлениями должна быть случайная пауза.""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: mas'uliyatli qo'shilish jadvalchisi""",
"description": """Kanal ro'yxatini faylda saqlab, ular orasiga tasodifiy tanaffus qo'yib, xatolarni to'liq ushlaydigan qo'shilish skripti""",
"sample_type": "code",
"code_files": [
{"filename": "channels.txt", "language": "text", "code": """@ochiq_kanal_namunasi
@ikkinchi_kanal_namunasi
"""},
{"filename": "responsible_joiner.py", "language": "python", "code": """import asyncio
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import PeerFloodError, FloodWaitError, UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def run() -> None:
    channels = [
        line.strip() for line in Path("channels.txt").read_text().splitlines() if line.strip()
    ]
    async with client:
        for ch in channels:
            try:
                await client(JoinChannelRequest(ch))
                print(f"OK: {ch}")
            except UserAlreadyParticipantError:
                print(f"Allaqachon a'zo: {ch}")
            except PeerFloodError:
                print("PeerFloodError -- to'xtatilmoqda.")
                break
            except FloodWaitError as e:
                print(f"Kutish: {e.seconds}s")
                await asyncio.sleep(e.seconds)
            await asyncio.sleep(random.uniform(180, 420))


if __name__ == "__main__":
    asyncio.run(run())
"""},
],
},
"exercises": [
{
"title": """Bot API'da yo'q, lekin userbot'da bor""",
"title_ru": """Чего нет в Bot API, но есть у юзербота""",
"description": """Ochiq kanalga username orqali dasturiy ravishda qo'shilish nima uchun Bot API'da mavjud emas?""",
"description_ru": """Почему программное вступление в открытый канал по username отсутствует в Bot API?""",
"exercise_type": "multiple_choice",
"options": ["Texnik jihatdan imkonsiz", "Telegram botlarni faqat inson qo'sha oladigan qilib ataylab loyihalagan", "Bu funksiya hali chiqarilmagan, kelajakda qo'shiladi", "Buning uchun alohida to'lov kerak"],
"options_ru": ["Технически невозможно", "Telegram намеренно спроектировал ботов так, что их может добавить только человек", "Эта функция ещё не выпущена, появится в будущем", "Для этого нужна отдельная оплата"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu dizayn qarori, texnik cheklov emas.""",
"hint_ru": """Это дизайнерское решение, а не техническое ограничение.""",
"explanation": """Telegram bot hisoblarini ataylab shunday loyihalagan -- bot faqat inson tomonidan qo'shilishi mumkin, o'zini hech qachon "qo'sha olmaydi". Userbot esa haqiqiy hisob bo'lgani uchun bu cheklov unga tegishli emas.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """PeerFloodError nimani anglatadi""",
"title_ru": """Что означает PeerFloodError""",
"description": """PeerFloodError xatoligi ko'tarilganda, eng to'g'ri javob nima bo'lishi kerak?""",
"description_ru": """Когда возникает ошибка PeerFloodError, каким должен быть правильный ответ?""",
"exercise_type": "multiple_choice",
"options": ["Darhol qayta urinish", "Bir necha soniyadan keyin qayta urinish", "To'xtash va bir necha soat kutish, ijtimoiy amallarni kamaytirish", "Yangi hisob yaratib davom etish"],
"options_ru": ["Немедленно повторить попытку", "Повторить попытку через несколько секунд", "Остановиться и подождать несколько часов, снизить количество социальных действий", "Создать новый аккаунт и продолжить"],
"correct_answers": "C",
"is_multiple_select": False,
"hint": """Bu FloodWaitError'dan farqli -- aniq kutish vaqti berilmaydi, chunki bu xatti-harakat cheklovi.""",
"hint_ru": """Это отличается от FloodWaitError -- точное время ожидания не указывается, потому что это ограничение поведения.""",
"explanation": """PeerFloodError -- "juda ko'p ijtimoiy amal" haqidagi signal, aniq soniya berilmaydi. To'g'ri javob -- faoliyatni sezilarli darajada kamaytirish va uzoq kutish, "yangi hisob yaratish" esa aynan taqiqlangan hisob-fermasi xatti-harakati.""",
"difficulty_level": "Hard",
"points": 8,
},
{
"title": """Xavfni kamaytirish choralarini tartiblang""",
"title_ru": """Расположите меры снижения риска по порядку""",
"description": """Ko'plab guruhga qo'shilish kerak bo'lgan (kamdan-kam, shaxsiy ehtiyoj) vaziyatda mas'uliyatli yondashuv tartibini tuzing.""",
"description_ru": """Составьте порядок ответственного подхода в ситуации, когда нужно вступить во множество групп (редкая, личная необходимость).""",
"exercise_type": "drag_and_drop",
"drag_items": ["Faqat haqiqatan kerak bo'lgan, oz sonli kanal ro'yxatini tuzish", "Qo'shilishlar orasiga tasodifiy, sezilarli tanaffus qo'yish", "PeerFloodError/FloodWaitError'ni albatta ushlash", "Xatolik kelsa -- darhol to'xtash, keyinroq davom ettirish"],
"drag_items_ru": ["Составить список только действительно нужных, немногочисленных каналов", "Добавить случайную, заметную паузу между вступлениями", "Обязательно перехватывать PeerFloodError/FloodWaitError", "При ошибке -- немедленно остановиться, продолжить позже"],
"correct_order": ["Faqat haqiqatan kerak bo'lgan, oz sonli kanal ro'yxatini tuzish", "Qo'shilishlar orasiga tasodifiy, sezilarli tanaffus qo'yish", "PeerFloodError/FloodWaitError'ni albatta ushlash", "Xatolik kelsa -- darhol to'xtash, keyinroq davom ettirish"],
"hint": """Avval ro'yxat, keyin sekinlashtirish, keyin himoya, oxirida javob.""",
"hint_ru": """Сначала список, потом замедление, потом защита, в конце реакция.""",
"difficulty_level": "Medium",
"points": 7,
},
],
},
{
"order": 7,
"title": """8-Mediani ommaviy yuklab olish: download_media, iter_download va progress""",
"title_ru": """8-Массовая загрузка медиа: download_media, iter_download и прогресс""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>download_media -- eng oddiy yo'l</h3>
<p><code>client.download_media(message, file=path)</code> &mdash; xabardagi media (rasm, hujjat, video, ovozli xabar) qanday turda bo'lishidan qat'iy nazar, uni to'liq yuklab, berilgan yo'lga saqlaydi. <code>message.file</code> xususiyati esa media turidan qat'i nazar umumiy metama'lumot beradi: <code>message.file.name</code>, <code>message.file.size</code>, <code>message.file.mime_type</code> &mdash; bu orqali yuklashdan OLDIN faylning hajmi va turi haqida bilib olish mumkin (masalan, juda katta fayllarni o'tkazib yuborish uchun).</p>
<h3>progress_callback -- katta fayllar uchun muhim</h3>
<p>Katta video yoki hujjat yuklanayotganda, foydalanuvchiga (yoki log fayliga) jarayon haqida xabar berish uchun <code>progress_callback</code> parametri beriladi &mdash; u <code>(received_bytes, total_bytes)</code> ikkita argument bilan chaqiriladigan funksiya. Bu ayniqsa uzoq davom etadigan (bir necha daqiqalik) yuklab olishlarda foydali &mdash; aks holda dastur "osilib qolgandek" ko'rinadi.</p>
<h3>iter_download -- qism-qism, quyi darajadagi nazorat</h3>
<p>Ba'zan butun faylni yuklashning hojati yo'q &mdash; masalan, faqat faylning bir qismini o'qish (video thumbnaili uchun boshlang'ich baytlar) yoki yuklab olishni pauza/davom ettirish kerak bo'lganda. <code>client.iter_download(file, offset=N, limit=M, request_size=...)</code> &mdash; xom baytlarni kichik qismlarda beruvchi quyi darajadagi async generator. U <code>download_media</code>ning ostida ham ishlatiladi, lekin to'g'ridan-to'g'ri chaqirilganda sizga to'liq nazorat beradi &mdash; masalan, diskka emas, to'g'ridan-to'g'ri xotiradagi buffer yoki tarmoq oqimiga yozish.</p>
<pre class="mermaid">
flowchart TB
  A["Xabarda media bormi? (message.file)"] --> B{"Butun faylni diskka\nyuklash kifoyami?"}
  B -- "Ha (odatiy holat)" --> C["client.download_media(message, file=yo'l, progress_callback=cb)"]
  B -- "Yo'q (qisman o'qish, streaming, pauza/davom)" --> D["client.iter_download(file, offset=..., limit=...)"]
  C --> E["Fayl diskka to'liq yozildi"]
  D --> F["Baytlar kichik bo'laklarda 'yield' qilinadi -- o'zingiz nazorat qilasiz"]
</pre>
<p>Diagramma shuni ko'rsatadi: ko'pchilik holatlarda <code>download_media</code> yetarli va sodda; <code>iter_download</code> esa faqat maxsus, quyi darajadagi ehtiyoj bo'lganda kerak &mdash; ikkalasini bir xil vaziyatda ishlatishning hojati yo'q.</p>
<h3>Ommaviy yuklab olish -- 6-darsdagi bilim bilan birlashtirish</h3>
<p>Ko'p sonli mediani yuklab olish odatda <code>iter_messages(..., filter=InputMessagesFilterPhotos)</code> (6-darsda ko'rilgan server-tomon filtri) bilan boshlanadi, so'ng har bir mos xabar uchun <code>download_media</code> chaqiriladi. Bu yerda ikkita xavf bor: (1) tezlik cheklovi &mdash; ko'p sonli yuklab olish so'rovi ham <code>FloodWaitError</code>ga olib kelishi mumkin, (2) diskdan joy tugashi &mdash; katta kanal tarixini "hammasini yukla" qilishdan oldin taxminiy umumiy hajmni hisoblab ko'rish tavsiya etiladi. Bir vaqtning o'zida juda ko'p yuklab olishni cheklash uchun <code>asyncio.Semaphore</code> ishlatish keng tarqalgan yechim.</p>
<h3>Fayl nomlash strategiyasi</h3>
<p>Standart <code>download_media(message)</code> (yo'lsiz chaqirilsa) Telegram taklif qilgan original nomdan foydalanadi, lekin bir nechta xabar bir xil nomga ega bo'lishi mumkin (masalan, hammasi <code>photo.jpg</code>). Ommaviy yuklashda har doim <code>message.id</code> yoki <code>message.date</code>ni fayl nomiga qo'shib, ustma-ust yozilib ketishning oldini oling &mdash; masalan <code>f"{chat_id}_{message.id}_{message.file.name}"</code>.</p>
<h3>Faqat thumbnail kerak bo'lsa</h3>
<p>Ba'zida to'liq faylning o'zi emas, faqat kichik oldindan ko'rish (thumbnail) kerak bo'ladi &mdash; masalan, katalog yasashda yoki tezkor ko'rib chiqishda. <code>download_media(message, thumb=-1)</code> &mdash; eng kichik mavjud thumbnailni yuklaydi, bu to'liq video/rasmni yuklashdan o'nlab-yuzlab marta tezroq va tejamliroq. <code>message.voice</code> va <code>message.audio</code> ham xuddi shu <code>download_media</code> orqali ishlaydi &mdash; ovozli xabarlar va audio fayllar ham "media" tushunchasiga kiradi, alohida metod talab qilinmaydi.</p>""",
"text_content_ru": """<h3>download_media -- самый простой способ</h3>
<p><code>client.download_media(message, file=path)</code> &mdash; независимо от типа медиа в сообщении (фото, документ, видео, голосовое сообщение), полностью загружает его и сохраняет по указанному пути. Свойство <code>message.file</code> даёт общие метаданные независимо от типа медиа: <code>message.file.name</code>, <code>message.file.size</code>, <code>message.file.mime_type</code> &mdash; это позволяет узнать размер и тип файла ДО загрузки (например, чтобы пропустить слишком большие файлы).</p>
<h3>progress_callback -- важен для больших файлов</h3>
<p>При загрузке большого видео или документа, чтобы сообщать пользователю (или в лог-файл) о ходе процесса, передаётся параметр <code>progress_callback</code> &mdash; функция, вызываемая с двумя аргументами <code>(received_bytes, total_bytes)</code>. Это особенно полезно при долгих (многоминутных) загрузках &mdash; иначе программа выглядит "зависшей".</p>
<h3>iter_download -- частями, контроль низкого уровня</h3>
<p>Иногда нет необходимости загружать весь файл целиком &mdash; например, нужно прочитать только часть файла (первые байты для превью видео) или требуется возможность паузы/продолжения загрузки. <code>client.iter_download(file, offset=N, limit=M, request_size=...)</code> &mdash; асинхронный генератор низкого уровня, выдающий сырые байты небольшими частями. Он используется и внутри <code>download_media</code>, но при прямом вызове даёт полный контроль &mdash; например, запись не на диск, а прямо в буфер в памяти или в сетевой поток.</p>
<pre class="mermaid">
flowchart TB
  A["Есть ли медиа в сообщении? (message.file)"] --> B{"Достаточно ли загрузить\nвесь файл на диск?"}
  B -- "Да (обычный случай)" --> C["client.download_media(message, file=путь, progress_callback=cb)"]
  B -- "Нет (частичное чтение, стриминг, пауза/продолжение)" --> D["client.iter_download(file, offset=..., limit=...)"]
  C --> E["Файл полностью записан на диск"]
  D --> F["Байты выдаются небольшими частями ('yield') -- контроль у вас"]
</pre>
<p>Диаграмма показывает: в большинстве случаев <code>download_media</code> достаточно и прост; <code>iter_download</code> нужен только для специальных потребностей низкого уровня &mdash; использовать оба в одной ситуации не нужно.</p>
<h3>Массовая загрузка -- объединение со знаниями урока 6</h3>
<p>Загрузка большого количества медиа обычно начинается с <code>iter_messages(..., filter=InputMessagesFilterPhotos)</code> (серверный фильтр из урока 6), затем для каждого подходящего сообщения вызывается <code>download_media</code>. Здесь есть два риска: (1) ограничение скорости &mdash; много запросов на загрузку тоже может привести к <code>FloodWaitError</code>, (2) нехватка места на диске &mdash; перед "скачать всё" из большой истории канала рекомендуется прикинуть примерный общий объём. Для ограничения числа одновременных загрузок распространённое решение &mdash; <code>asyncio.Semaphore</code>.</p>
<h3>Стратегия именования файлов</h3>
<p>Стандартный вызов <code>download_media(message)</code> (без пути) использует оригинальное имя, предложенное Telegram, но несколько сообщений могут иметь одинаковое имя (например, все называются <code>photo.jpg</code>). При массовой загрузке всегда добавляйте <code>message.id</code> или <code>message.date</code> в имя файла, чтобы избежать перезаписи &mdash; например <code>f"{chat_id}_{message.id}_{message.file.name}"</code>.</p>
<h3>Если нужен только thumbnail</h3>
<p>Иногда нужен не весь файл, а только маленькое превью (thumbnail) &mdash; например, при построении каталога или быстром просмотре. <code>download_media(message, thumb=-1)</code> &mdash; загружает наименьший доступный thumbnail, что в десятки-сотни раз быстрее и экономнее, чем загрузка полного видео/фото. <code>message.voice</code> и <code>message.audio</code> тоже работают через тот же <code>download_media</code> &mdash; голосовые сообщения и аудиофайлы тоже относятся к понятию "медиа", отдельный метод не требуется.</p>""",
"code_content": """\"\"\"Mediani ommaviy yuklab olish: progress, semaphore bilan tezlik nazorati.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterPhotos

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
MAX_CONCURRENT_DOWNLOADS = 3  # bir vaqtda ko'pi bilan shuncha yuklab olish


def make_progress_callback(label: str):
    def callback(received: int, total: int) -> None:
        pct = (received / total * 100) if total else 0
        print(f"\\r{label}: {pct:5.1f}% ({received}/{total} bayt)", end="")
    return callback


async def download_one(message, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        if not message.file:
            return
        filename = f"{message.chat_id}_{message.id}_{message.file.name or 'media'}"
        target = DOWNLOAD_DIR / filename
        if target.exists():
            print(f"O'tkazib yuborildi (mavjud): {filename}")
            return
        try:
            await client.download_media(
                message, file=str(target), progress_callback=make_progress_callback(filename)
            )
            print()  # progress qatoridan keyin yangi qator
        except FloodWaitError as e:
            print(f"\\nFloodWait media yuklashda: {e.seconds}s kutamiz.")
            await asyncio.sleep(e.seconds)
            await download_one(message, semaphore)


async def bulk_download_photos(chat: str, limit: int = 100) -> None:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    tasks = []
    async with client:
        async for message in client.iter_messages(
            chat, limit=limit, filter=InputMessagesFilterPhotos
        ):
            tasks.append(asyncio.create_task(download_one(message, semaphore)))
        await asyncio.gather(*tasks)
    print(f"\\nJami {len(tasks)} ta media uchun yuklab olish yakunlandi.")


if __name__ == "__main__":
    asyncio.run(bulk_download_photos("@ochiq_kanal_namunasi", limit=50))
""",
"code_content_ru": """\"\"\"Массовая загрузка медиа: прогресс, контроль скорости через semaphore.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterPhotos

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
MAX_CONCURRENT_DOWNLOADS = 3  # максимум столько одновременных загрузок


def make_progress_callback(label: str):
    def callback(received: int, total: int) -> None:
        pct = (received / total * 100) if total else 0
        print(f"\\r{label}: {pct:5.1f}% ({received}/{total} байт)", end="")
    return callback


async def download_one(message, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        if not message.file:
            return
        filename = f"{message.chat_id}_{message.id}_{message.file.name or 'media'}"
        target = DOWNLOAD_DIR / filename
        if target.exists():
            print(f"Пропущено (уже существует): {filename}")
            return
        try:
            await client.download_media(
                message, file=str(target), progress_callback=make_progress_callback(filename)
            )
            print()  # новая строка после прогресса
        except FloodWaitError as e:
            print(f"\\nFloodWait при загрузке медиа: ждём {e.seconds}с.")
            await asyncio.sleep(e.seconds)
            await download_one(message, semaphore)


async def bulk_download_photos(chat: str, limit: int = 100) -> None:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    tasks = []
    async with client:
        async for message in client.iter_messages(
            chat, limit=limit, filter=InputMessagesFilterPhotos
        ):
            tasks.append(asyncio.create_task(download_one(message, semaphore)))
        await asyncio.gather(*tasks)
    print(f"\\nЗагрузка {len(tasks)} медиафайлов завершена.")


if __name__ == "__main__":
    asyncio.run(bulk_download_photos("@пример_открытого_канала", limit=50))
""",
"task": {
"task_title": """Amaliy: progress-bar bilan ommaviy media yuklovchi""",
"task_title_ru": """Практика: массовый загрузчик медиа с индикатором прогресса""",
"task_description": """bulk_download_photos() funksiyasini kengaytirib, u nafaqat rasmlarni, balki hujjatlarni ham (InputMessagesFilterDocument) yuklab olishini ta'minlang. Har bir fayl uchun progress foizini konsolga chiqaring va yuklab olingan fayllar hajmini umumlashtirib chiqaring.""",
"task_description_ru": """Расширьте функцию bulk_download_photos() так, чтобы она загружала не только фото, но и документы (InputMessagesFilterDocument). Для каждого файла выводите процент прогресса в консоль и в конце выведите общий размер загруженных файлов.""",
"task_requirements": """Kamida ikkita media turi (rasm va hujjat) qo'llab-quvvatlanishi; progress_callback ishlatilgan bo'lishi; MAX_CONCURRENT_DOWNLOADS orqali parallel yuklashlar cheklangan bo'lishi kerak.""",
"task_requirements_ru": """Должны поддерживаться минимум два типа медиа (фото и документ); должен использоваться progress_callback; параллельные загрузки должны быть ограничены через MAX_CONCURRENT_DOWNLOADS.""",
"task_technologies": "Python 3.11+, Telethon, asyncio",
"task_deadline_days": 4,
},
"sample": {
"title": """Namuna: fayl hajmini oldindan hisoblovchi yuklovchi""",
"description": """Yuklashdan oldin umumiy hajmni hisoblab, foydalanuvchidan tasdiq so'raydigan xavfsizroq yuklab olish skripti""",
"sample_type": "code",
"code_files": [
{"filename": "safe_bulk_download.py", "language": "python", "code": """import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterDocument

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def estimate_and_download(chat: str, limit: int = 200) -> None:
    async with client:
        candidates = []
        total_bytes = 0
        async for message in client.iter_messages(
            chat, limit=limit, filter=InputMessagesFilterDocument
        ):
            if message.file:
                candidates.append(message)
                total_bytes += message.file.size or 0

        print(f"Topildi: {len(candidates)} ta fayl, jami ~{total_bytes / 1024 / 1024:.1f} MB")
        confirm = input("Yuklab olishni davom ettirasizmi? (ha/yo'q): ")
        if confirm.lower() not in ("ha", "yes", "y"):
            print("Bekor qilindi.")
            return

        for msg in candidates:
            path = f"downloads/{msg.id}_{msg.file.name or 'file'}"
            await client.download_media(msg, file=path)
            print(f"Yuklandi: {path}")


if __name__ == "__main__":
    asyncio.run(estimate_and_download("@ochiq_kanal_namunasi"))
"""},
],
},
"exercises": [
{
"title": """progress_callback nima uchun kerak""",
"title_ru": """Зачем нужен progress_callback""",
"description": """download_media()dagi progress_callback parametrining vazifasi nima?""",
"description_ru": """Какова функция параметра progress_callback в download_media()?""",
"exercise_type": "multiple_choice",
"options": ["Yuklab olish tezligini oshiradi", "Yuklanish jarayoni haqida (received_bytes, total_bytes) xabar beradi", "Faylni avtomatik siqadi", "Yuklab olishni fon jarayoniga o'tkazadi"],
"options_ru": ["Увеличивает скорость загрузки", "Сообщает о ходе загрузки (received_bytes, total_bytes)", "Автоматически сжимает файл", "Переводит загрузку в фоновый процесс"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu funksiya har safar yangi qism yuklanganda chaqiriladi.""",
"hint_ru": """Эта функция вызывается каждый раз при получении новой части.""",
"explanation": """progress_callback yuklanish davomida bir necha marta chaqiriladi va hozirgacha nechta hamda jami nechta bayt borligini beradi -- bu uzoq yuklab olishlarda foydalanuvchiga jarayon holatini ko'rsatish uchun ishlatiladi.""",
"difficulty_level": "Easy",
"points": 5,
},
{
"title": """Qism-qism, quyi darajadagi yuklash""",
"title_ru": """Частичная загрузка низкого уровня""",
"description": """Faylning faqat bir qismini o'qish yoki yuklashni o'zingiz to'liq nazorat qilish kerak bo'lsa, qaysi metod ishlatiladi?""",
"description_ru": """Какой метод используется, если нужно прочитать только часть файла или полностью самостоятельно контролировать загрузку?""",
"exercise_type": "multiple_choice",
"options": ["client.download_media()", "client.iter_download()", "client.get_messages()", "client.send_file()"],
"options_ru": ["client.download_media()", "client.iter_download()", "client.get_messages()", "client.send_file()"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu -- baytlarni kichik bo'laklarda beruvchi async generator.""",
"hint_ru": """Это -- асинхронный генератор, выдающий байты небольшими частями.""",
"explanation": """iter_download offset/limit orqali faylning istalgan qismini o'qish imkonini beradi -- download_media esa har doim to'liq faylni yuklaydi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Ommaviy yuklashda xavfsizlik tartibini tuzing""",
"title_ru": """Составьте порядок безопасной массовой загрузки""",
"description": """Katta kanal tarixidagi barcha rasmlarni yuklashdan oldin qanday tartibda harakat qilish maqsadga muvofiq?""",
"description_ru": """В каком порядке целесообразно действовать перед загрузкой всех фото из большой истории канала?""",
"exercise_type": "drag_and_drop",
"drag_items": ["iter_messages orqali server-tomon filtr bilan nomzod xabarlarni yig'ish", "Umumiy taxminiy hajmni hisoblash", "Semaphore orqali bir vaqtdagi yuklashlar sonini cheklash", "Har bir faylni progress_callback bilan yuklab olish"],
"drag_items_ru": ["Собрать сообщения-кандидаты через iter_messages с серверным фильтром", "Подсчитать примерный общий объём", "Ограничить число одновременных загрузок через Semaphore", "Загрузить каждый файл с progress_callback"],
"correct_order": ["iter_messages orqali server-tomon filtr bilan nomzod xabarlarni yig'ish", "Umumiy taxminiy hajmni hisoblash", "Semaphore orqali bir vaqtdagi yuklashlar sonini cheklash", "Har bir faylni progress_callback bilan yuklab olish"],
"hint": """Avval yig'ish, keyin baholash, keyin cheklash, keyin bajarish.""",
"hint_ru": """Сначала сбор, потом оценка, потом ограничение, потом выполнение.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Media faylni yuklab oluvchi metod""",
"title_ru": """Метод для загрузки медиафайла""",
"description": """Xabardagi mediani (rasm, hujjat, video) diskka to'liq yuklab oluvchi asosiy client metodi: client.___()""",
"description_ru": """Основной метод client для полной загрузки медиа из сообщения (фото, документ, видео) на диск: client.___()""",
"exercise_type": "fill_in_blank",
"correct_answers": "download_media",
"hint": """Nomi to'g'ridan-to'g'ri "media yuklab olish" degan ma'noni bildiradi.""",
"hint_ru": """Название буквально означает "загрузить медиа".""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 8,
"title": """9-Dialoglar, kontaktlar va entity'lar bilan chuqurroq ishlash""",
"title_ru": """9-Углублённая работа с диалогами, контактами и entity""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>get_dialogs -- hisobingizning "bosh sahifasi"</h3>
<p><code>client.get_dialogs(limit=N)</code> &mdash; Telegram ilovasi ochilganda ko'radigan suhbatlar ro'yxatini xuddi shunday qaytaradi: har bir <code>Dialog</code> obyekti tegishli entity (User/Chat/Channel), oxirgi xabar va <code>unread_count</code>ni o'z ichiga oladi. Bu &mdash; bot API'da UMUMAN yo'q tushuncha, chunki botning "suhbatlar ro'yxati" degan narsasi yo'q &mdash; u faqat unga xabar yozgan chatlarni "eslaydi", ammo ularni ro'yxat sifatida so'ray olmaydi. <code>client.iter_dialogs()</code> esa xuddi <code>iter_messages</code> kabi, katta ro'yxatni sahifalab beruvchi async generator.</p>
<h3>Kontaktlar</h3>
<p><code>client.get_contacts()</code> (qulay wrapper) yoki xom <code>functions.contacts.GetContactsRequest(hash=0)</code> &mdash; hisobingizdagi barcha saqlangan kontaktlar ro'yxatini qaytaradi. Yangi kontakt qo'shish uchun <code>functions.contacts.ImportContactsRequest</code> ishlatiladi &mdash; lekin buni ham 7-darsdagi ehtiyotkorlik tamoyillari bilan, ommaviy emas, ehtiyotkorlik bilan qo'llash kerak.</p>
<h3>get_entity vs get_input_entity</h3>
<p><code>client.get_entity(x)</code> &mdash; TO'LIQ entity obyektini qaytaradi (ism, foto, bio va h.k. bilan), buning uchun ba'zan qo'shimcha so'rov kerak bo'ladi. <code>client.get_input_entity(x)</code> esa faqat MTProto so'rovi uchun zarur bo'lgan minimal <code>InputPeer*</code> obyektini qaytaradi (ID + access_hash) &mdash; agar sizga faqat <code>send_message</code> kabi metodga entity berish kerak bo'lsa (ular ichkarida <code>get_input_entity</code>ni o'zi chaqiradi), to'liq ma'lumot ortiqcha va sekinroq. Katta hajmdagi ishlov berishda (masalan, minglab xabarga javob yozish) <code>get_input_entity</code>ni oldindan keshlashning o'zi sezilarli tezlashtirish beradi.</p>
<pre class="mermaid">
flowchart TB
  A["client.get_dialogs()"] --> B["Har bir Dialog: entity + oxirgi xabar + unread_count"]
  A --> C["client.get_contacts()"]
  C --> D["Saqlangan kontaktlar ro'yxati (User obyektlari)"]
  B --> E["client.get_entity(dialog.entity) -- to'liq ma'lumot"]
  B --> F["client.get_input_entity(dialog.entity) -- faqat so'rov uchun minimal"]
</pre>
<p>Diagramma shuni ko'rsatadi: dialoglar, kontaktlar va entity'lar &mdash; uchta bog'liq, lekin alohida tushuncha; ularning har biri o'zining API chaqiruviga ega, va get_entity/get_input_entity orasidagi tanlov ko'pincha unutiladigan, lekin unumdorlikka sezilarli ta'sir qiluvchi detal.</p>
<h3>Katta kanal a'zolari ro'yxati -- iter_participants</h3>
<p><code>client.iter_participants(entity, limit=None, aggressive=True)</code> &mdash; kanal/guruh a'zolarini sahifalab beradi. Juda katta kanallarda (o'n minglab a'zo) Telegram API bitta so'rashda cheklangan sonini qaytaradi; <code>aggressive=True</code> rejimi bir nechta qidiruv so'rovini (masalan, har xil harflar bo'yicha) birlashtirib, imkon qadar to'liqroq ro'yxat yig'ishga harakat qiladi. Bu ham &mdash; 7-darsdagi mas'uliyat tamoyillari doirasida qo'llanilishi kerak bo'lgan imkoniyat: butun a'zolar ro'yxatini tez-tez, ko'plab kanal uchun yig'ish ham "shubhali ommaviy faoliyat" sifatida ko'rinishi mumkin.</p>
<h3>Telefon raqami orqali entity topish</h3>
<p>Agar foydalanuvchi sizning kontaktlaringizda bo'lsa (yoki muayyan sozlamalar ruxsat bersa), <code>client.get_entity(phone_number)</code> orqali telefon raqami bo'yicha ham entity topish mumkin. Bu &mdash; yana bir Bot API'da yo'q imkoniyat, va aynan shu sabab u ko'pincha noto'g'ri niyat bilan (raqamlar bazasini "tekshirish" uchun) suiiste'mol qilinadi &mdash; bu kursda faqat o'zingizning haqiqiy kontaktlaringiz bilan ishlash uchun qo'llanilishi kerak.</p>
<h3>Arxivlangan dialoglar</h3>
<p><code>get_dialogs(folder=1)</code> &mdash; standart <code>folder=0</code> (asosiy ro'yxat) o'rniga, arxivlangan chatlarni qaytaradi. Bu ham foydalanuvchi hisobiga xos tushuncha: arxiv &mdash; sizning shaxsiy interfeys holatingiz, bot esa hech qachon "o'z chatlarini arxivlamaydi". Monitoring vazifalarida ko'pincha ikkalasini ham (asosiy va arxiv) alohida so'rab, natijalarni birlashtirish kerak bo'ladi, chunki standart chaqiruv faqat asosiy ro'yxatni qaytaradi. Katta hisoblarda arxiv ko'pincha yuzlab eski, kam faol suhbatni o'zida saqlaydi &mdash; monitoring skriptlari buni e'tiborsiz qoldirib, muhim signalni yo'qotib qo'yishi mumkin.</p>""",
"text_content_ru": """<h3>get_dialogs -- "главная страница" вашего аккаунта</h3>
<p><code>client.get_dialogs(limit=N)</code> возвращает точно такой же список бесед, какой вы видите при открытии приложения Telegram: каждый объект <code>Dialog</code> содержит соответствующий entity (User/Chat/Channel), последнее сообщение и <code>unread_count</code>. Это понятие ВООБЩЕ отсутствует в Bot API, потому что у бота нет "списка бесед" &mdash; он только "помнит" чаты, которые ему писали, но не может запросить их как список. <code>client.iter_dialogs()</code> &mdash; так же, как <code>iter_messages</code>, асинхронный генератор, постранично выдающий большой список.</p>
<h3>Контакты</h3>
<p><code>client.get_contacts()</code> (удобная обёртка) или сырой <code>functions.contacts.GetContactsRequest(hash=0)</code> &mdash; возвращает список всех сохранённых контактов вашего аккаунта. Для добавления нового контакта используется <code>functions.contacts.ImportContactsRequest</code> &mdash; но и это следует применять с теми же принципами осторожности из урока 7, не массово, а аккуратно.</p>
<h3>get_entity vs get_input_entity</h3>
<p><code>client.get_entity(x)</code> возвращает ПОЛНЫЙ объект entity (имя, фото, био и т.д.), для чего иногда нужен дополнительный запрос. <code>client.get_input_entity(x)</code> же возвращает только минимальный объект <code>InputPeer*</code>, необходимый для MTProto-запроса (ID + access_hash) &mdash; если вам нужен entity только чтобы передать его методу вроде <code>send_message</code> (они сами внутри вызывают <code>get_input_entity</code>), полная информация избыточна и медленнее. При обработке больших объёмов (например, ответ на тысячи сообщений) предварительное кэширование <code>get_input_entity</code> само по себе даёт заметное ускорение.</p>
<pre class="mermaid">
flowchart TB
  A["client.get_dialogs()"] --> B["Каждый Dialog: entity + последнее сообщение + unread_count"]
  A --> C["client.get_contacts()"]
  C --> D["Список сохранённых контактов (объекты User)"]
  B --> E["client.get_entity(dialog.entity) -- полная информация"]
  B --> F["client.get_input_entity(dialog.entity) -- минимум для запроса"]
</pre>
<p>Диаграмма показывает: диалоги, контакты и entity &mdash; три связанных, но отдельных понятия; у каждого свой вызов API, а выбор между get_entity/get_input_entity &mdash; часто забываемая, но заметно влияющая на производительность деталь.</p>
<h3>Список участников большого канала -- iter_participants</h3>
<p><code>client.iter_participants(entity, limit=None, aggressive=True)</code> постранично выдаёт участников канала/группы. В очень крупных каналах (десятки тысяч участников) API Telegram возвращает ограниченное количество за один запрос; режим <code>aggressive=True</code> объединяет несколько поисковых запросов (например, по разным буквам), пытаясь собрать максимально полный список. Это тоже возможность, которую следует применять в рамках принципов ответственности из урока 7: частый сбор полного списка участников множества каналов тоже может выглядеть как "подозрительная массовая активность".</p>
<h3>Поиск entity по номеру телефона</h3>
<p>Если пользователь есть в ваших контактах (или это разрешают определённые настройки), можно найти entity и по номеру телефона через <code>client.get_entity(phone_number)</code>. Это ещё одна возможность, отсутствующая в Bot API, и именно поэтому её часто злоупотребляют недобросовестно (для "проверки" баз номеров) &mdash; в этом курсе она должна применяться только для работы с вашими настоящими контактами.</p>
<h3>Архивированные диалоги</h3>
<p><code>get_dialogs(folder=1)</code> &mdash; вместо стандартного <code>folder=0</code> (основной список) возвращает архивированные чаты. Это тоже понятие, свойственное только пользовательскому аккаунту: архив &mdash; это состояние вашего личного интерфейса, а бот никогда "не архивирует свои чаты". В задачах мониторинга часто нужно запрашивать оба списка (основной и архив) отдельно и объединять результаты, потому что стандартный вызов возвращает только основной список.</p>""",
"code_content": """\"\"\"Dialoglar, kontaktlar va entity keshlash namunalari.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import GetContactsRequest

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def list_dialogs_summary(limit: int = 20) -> None:
    async with client:
        async for dialog in client.iter_dialogs(limit=limit):
            kind = "kanal" if dialog.is_channel else ("guruh" if dialog.is_group else "shaxsiy")
            print(
                f"[{kind}] {dialog.name!r} -- o'qilmagan: {dialog.unread_count}, "
                f"oxirgi xabar: {dialog.message.date if dialog.message else '-'}"
            )


async def list_contacts() -> None:
    async with client:
        result = await client(GetContactsRequest(hash=0))
        for user in result.users:
            print(f"{user.first_name} {user.last_name or ''} (@{user.username})")


async def cache_input_entities_for_bulk_reply(chat: str, limit: int = 200) -> dict:
    \"\"\"Ommaviy javob yozishda har safar to'liq get_entity chaqirish
    o'rniga, oldindan yengil InputPeer'larni keshlash tezroq ishlaydi.\"\"\"
    cache: dict[int, object] = {}
    async with client:
        async for message in client.iter_messages(chat, limit=limit):
            sender_id = message.sender_id
            if sender_id and sender_id not in cache:
                cache[sender_id] = await client.get_input_entity(message.sender_id)
        print(f"{len(cache)} ta yuboruvchi uchun input entity keshlandi.")
    return cache


async def list_channel_participants(channel: str, limit: int = 500) -> None:
    \"\"\"Katta kanal a'zolarini imkon qadar to'liqroq yig'ish.
    E'TIBOR: bu amalni tez-tez, ko'plab kanal uchun bajarish 7-darsdagi
    "shubhali ommaviy faoliyat" tavsifiga to'g'ri keladi -- ehtiyot bo'ling.\"\"\"
    async with client:
        count = 0
        async for user in client.iter_participants(channel, limit=limit, aggressive=True):
            count += 1
        print(f"Jami topilgan a'zolar: {count}")


if __name__ == "__main__":
    asyncio.run(list_dialogs_summary())
""",
"code_content_ru": """\"\"\"Примеры работы с диалогами, контактами и кэшированием entity.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import GetContactsRequest

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def list_dialogs_summary(limit: int = 20) -> None:
    async with client:
        async for dialog in client.iter_dialogs(limit=limit):
            kind = "канал" if dialog.is_channel else ("группа" if dialog.is_group else "личный")
            print(
                f"[{kind}] {dialog.name!r} -- непрочитано: {dialog.unread_count}, "
                f"последнее сообщение: {dialog.message.date if dialog.message else '-'}"
            )


async def list_contacts() -> None:
    async with client:
        result = await client(GetContactsRequest(hash=0))
        for user in result.users:
            print(f"{user.first_name} {user.last_name or ''} (@{user.username})")


async def cache_input_entities_for_bulk_reply(chat: str, limit: int = 200) -> dict:
    \"\"\"При массовой рассылке ответов кэширование лёгких InputPeer заранее
    работает быстрее, чем каждый раз вызывать полный get_entity.\"\"\"
    cache: dict[int, object] = {}
    async with client:
        async for message in client.iter_messages(chat, limit=limit):
            sender_id = message.sender_id
            if sender_id and sender_id not in cache:
                cache[sender_id] = await client.get_input_entity(message.sender_id)
        print(f"Закэшировано input entity для {len(cache)} отправителей.")
    return cache


async def list_channel_participants(channel: str, limit: int = 500) -> None:
    \"\"\"Сбор максимально полного списка участников крупного канала.
    ВНИМАНИЕ: частое выполнение этого действия для множества каналов
    соответствует описанию "подозрительной массовой активности" из
    урока 7 -- будьте осторожны.\"\"\"
    async with client:
        count = 0
        async for user in client.iter_participants(channel, limit=limit, aggressive=True):
            count += 1
        print(f"Всего найдено участников: {count}")


if __name__ == "__main__":
    asyncio.run(list_dialogs_summary())
""",
"task": {
"task_title": """Amaliy: dialoglar hisobotini tuzing""",
"task_title_ru": """Практика: составьте отчёт по диалогам""",
"task_description": """list_dialogs_summary() funksiyasini kengaytirib, u kanal/guruh/shaxsiy suhbatlar sonini alohida hisoblab, yakunda umumiy statistikani (masalan, "12 shaxsiy, 3 guruh, 5 kanal, jami 8 ta o'qilmagan xabar") chiqarsin.""",
"task_description_ru": """Расширьте функцию list_dialogs_summary() так, чтобы она отдельно подсчитывала количество каналов/групп/личных бесед и в конце выводила общую статистику (например, "12 личных, 3 группы, 5 каналов, всего 8 непрочитанных сообщений").""",
"task_requirements": """Uchala dialog turi (shaxsiy, guruh, kanal) alohida hisoblanishi; yakuniy statistika chiqarilishi; iter_dialogs() dan foydalanilgan bo'lishi kerak.""",
"task_requirements_ru": """Все три типа диалогов (личный, группа, канал) должны учитываться отдельно; должна выводиться итоговая статистика; должен использоваться iter_dialogs().""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 3,
},
"sample": {
"title": """Namuna: kontaktlar va dialoglar eksporti""",
"description": """Barcha kontaktlar va dialoglarni JSON faylga eksport qiluvchi kichik skript""",
"sample_type": "code",
"code_files": [
{"filename": "export_dialogs.py", "language": "python", "code": """import asyncio
import json
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


async def export() -> None:
    dialogs_data = []
    async with client:
        async for dialog in client.iter_dialogs():
            dialogs_data.append({
                "id": dialog.id,
                "name": dialog.name,
                "is_channel": dialog.is_channel,
                "is_group": dialog.is_group,
                "unread_count": dialog.unread_count,
            })

    with open("dialogs_export.json", "w", encoding="utf-8") as f:
        json.dump(dialogs_data, f, ensure_ascii=False, indent=2)
    print(f"{len(dialogs_data)} ta dialog eksport qilindi -> dialogs_export.json")


if __name__ == "__main__":
    asyncio.run(export())
"""},
],
},
"exercises": [
{
"title": """get_dialogs Bot API'da yo'qligining sababi""",
"title_ru": """Почему get_dialogs отсутствует в Bot API""",
"description": """Nima uchun Bot API'da "barcha suhbatlar ro'yxatini olish" metodi umuman yo'q?""",
"description_ru": """Почему в Bot API вообще нет метода "получить список всех бесед"?""",
"exercise_type": "multiple_choice",
"options": ["Texnik cheklov -- server buni hisoblay olmaydi", "Bot faqat unga yozilgan chatlarni biladi, umumiy ro'yxat tushunchasi yo'q", "Bu funksiya to'lovli, botlar uchun yopilgan", "Bot API buni qo'llab-quvvatlaydi, lekin boshqa nom bilan"],
"options_ru": ["Техническое ограничение -- сервер не может это подсчитать", "Бот знает только чаты, которые ему писали, понятия общего списка нет", "Эта функция платная, закрыта для ботов", "Bot API поддерживает это, но под другим названием"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bot hisobi bilan foydalanuvchi hisobi tuzilishi tubdan boshqacha.""",
"hint_ru": """Структура аккаунта бота принципиально отличается от аккаунта пользователя.""",
"explanation": """Bot API bot hisobiga "suhbatlar ro'yxati" tushunchasini umuman bermaydi -- bot faqat o'ziga kelgan xabarlar orqali chatlarni biladi. Userbot esa haqiqiy hisob bo'lgani uchun to'liq dialog ro'yxatiga ega.""",
"difficulty_level": "Medium",
"points": 7,
},
{
"title": """get_entity va get_input_entity farqi""",
"title_ru": """Разница между get_entity и get_input_entity""",
"description": """Faqat send_message kabi metodga entity berish kerak bo'lganda, qaysi metod ko'proq tezkor?""",
"description_ru": """Когда entity нужен только для передачи в метод вроде send_message, какой метод быстрее?""",
"exercise_type": "multiple_choice",
"options": ["get_entity -- chunki u to'liq ma'lumot beradi", "get_input_entity -- chunki u faqat so'rov uchun minimal ma'lumot qaytaradi", "Ikkalasi ham bir xil tezlikda ishlaydi", "get_dialogs -- chunki u hammasini oldindan yuklaydi"],
"options_ru": ["get_entity -- потому что даёт полную информацию", "get_input_entity -- потому что возвращает минимум, нужный только для запроса", "Оба работают с одинаковой скоростью", "get_dialogs -- потому что загружает всё заранее"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """To'liq ma'lumot (ism, foto va h.k.) MTProto so'rovi uchun shart emas.""",
"hint_ru": """Полная информация (имя, фото и т.д.) не нужна для самого MTProto-запроса.""",
"explanation": """get_input_entity faqat ID+access_hash kabi minimal InputPeer qaytaradi -- bu ko'p sonli so'rov yuborishda sezilarli tezlik farqini beradi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Katta kanal a'zolarini yig'ish tartibini tuzing""",
"title_ru": """Составьте порядок сбора участников большого канала""",
"description": """iter_participants orqali kanal a'zolarini mas'uliyat bilan yig'ish uchun to'g'ri tartibni tuzing.""",
"description_ru": """Составьте правильный порядок ответственного сбора участников канала через iter_participants.""",
"exercise_type": "drag_and_drop",
"drag_items": ["Bu amal qanchalik zarur ekanini baholash (7-dars tamoyillari)", "iter_participants(entity, aggressive=True) chaqirish", "Natijalarni asta-sekin, tezlik cheklovlarini kuzatib qayta ishlash", "Yig'ilgan ro'yxatni xavfsiz saqlash (masalan shifrlangan yoki cheklangan kirish bilan)"],
"drag_items_ru": ["Оценить, насколько это действие необходимо (принципы урока 7)", "Вызвать iter_participants(entity, aggressive=True)", "Постепенно обрабатывать результаты, следя за ограничениями скорости", "Безопасно сохранить собранный список (например, с шифрованием или ограниченным доступом)"],
"correct_order": ["Bu amal qanchalik zarur ekanini baholash (7-dars tamoyillari)", "iter_participants(entity, aggressive=True) chaqirish", "Natijalarni asta-sekin, tezlik cheklovlarini kuzatib qayta ishlash", "Yig'ilgan ro'yxatni xavfsiz saqlash (masalan shifrlangan yoki cheklangan kirish bilan)"],
"hint": """Avval zaruratni baholash, keyin bajarish, keyin ehtiyotkorlik, oxirida xavfsiz saqlash.""",
"hint_ru": """Сначала оценка необходимости, потом выполнение, потом осторожность, в конце безопасное хранение.""",
"difficulty_level": "Hard",
"points": 8,
},
],
},
{
"order": 9,
"title": """10-Takrorlash: 1-9-darslar bo'yicha xulosa va mini-loyiha""",
"title_ru": """10-Повторение: итоги уроков 1-9 и мини-проект""",
"points_reward": 20,
"code_language": "python",
"text_content": """<h3>Bu -- takrorlash darsi</h3>
<p>Bu darsda yangi mavzu yo'q &mdash; shuning uchun matn boshqa darslarga qaraganda ataylab qisqaroq. 1-9-darslarda o'rganilgan asosiy g'oyalarni bitta zanjirga bog'laymiz: MTProto asosi, xavfsiz login va session boshqaruvi, xabar/hodisa ishlash, va tarix/media/entity bilan ommaviy ishlash.</p>
<h3>Butun zanjir bitta ko'zqarashda</h3>
<p>Userbot ishga tushishi uchun: (1) my.telegram.org'dan olingan <code>api_id</code>/<code>api_hash</code> ilovani aniqlaydi; (2) birinchi login &mdash; telefon + kod + (ehtimol) 2FA &mdash; orqali <code>auth_key</code> yaratiladi va u <code>.session</code> fayl yoki <code>StringSession</code> qatorida saqlanadi (BU &mdash; parol darajasidagi maxfiy ma'lumot, hech qachon kod/repo/chatda ko'rinmasin); (3) shundan keyin <code>client.on(events.NewMessage(...))</code> kabi handlerlar orqali hodisalarga reaktsiya bildiriladi; (4) katta hajmdagi ishlarda &mdash; tarixni <code>iter_messages</code>, mediani <code>download_media</code>/<code>iter_download</code>, a'zolarni <code>iter_participants</code> orqali sahifalab, <code>FloodWaitError</code>/<code>PeerFloodError</code>ni har doim ushlab, ishni davomli progress bilan bajarish kerak.</p>
<h3>Eng ko'p uchraydigan xatolar qayerda</h3>
<table>
<tr><th>Bosqich</th><th>Odatiy xato</th><th>To'g'ri yondashuv</th></tr>
<tr><td>Session saqlash</td><td>StringSession'ni kodga yozib, git'ga commit qilish</td><td>Muhit o'zgaruvchisi/secrets manager, .gitignore'da *.session</td></tr>
<tr><td>Entity resolution</td><td>ValueError'ni ushlab olmaslik</td><td>get_entity/send_message atrofida try/except ValueError</td></tr>
<tr><td>Ommaviy tarix o'qish</td><td>Butun tarixni get_messages(limit=100000) bilan bir yo'la olish</td><td>iter_messages + offset_id bilan progressni saqlab davom ettirish</td></tr>
<tr><td>Kanallarga qo'shilish</td><td>Ketma-ket, tanaffusiz ko'plab guruhga qo'shilish</td><td>Tasodifiy tanaffus + PeerFloodError'ni ushlash</td></tr>
<tr><td>Media yuklash</td><td>Progress'siz, ketma-ket (bir vaqtda bittadan) yuklash</td><td>progress_callback + Semaphore bilan cheklangan parallellik</td></tr>
</table>
<h3>Nega tartib muhim</h3>
<p>Bu zanjirda ikkita qoida buzilsa, jiddiy oqibat yuzaga keladi: birinchisi &mdash; session xavfsizligini e'tiborsiz qoldirish (3-dars) &mdash; bu butun hisobni yo'qotishga olib kelishi mumkin; ikkinchisi &mdash; tezlik/ToS cheklovlarini e'tiborsiz qoldirish (7-dars) &mdash; bu hisobni cheklash yoki bloklanishga olib kelishi mumkin. Qolgan barcha texnik bilim (event handlerlar, iter_messages, media) shu ikki qoida hurmat qilingandagina xavfsiz ishlaydi.</p>""",
"text_content_ru": """<h3>Это -- урок повторения</h3>
<p>В этом уроке нет новой темы &mdash; поэтому текст намеренно короче, чем в других уроках. Свяжем в одну цепочку основные идеи из уроков 1-9: основы MTProto, безопасный вход и управление сессией, работа с сообщениями/событиями, и массовая работа с историей/медиа/entity.</p>
<h3>Вся цепочка одним взглядом</h3>
<p>Для запуска юзербота нужно: (1) <code>api_id</code>/<code>api_hash</code> с my.telegram.org идентифицируют приложение; (2) первый вход &mdash; телефон + код + (возможно) 2FA &mdash; создаёт <code>auth_key</code>, который хранится в файле <code>.session</code> или строке <code>StringSession</code> (ЭТО &mdash; секретные данные уровня пароля, никогда не должны быть видны в коде/репозитории/чате); (3) далее через обработчики вроде <code>client.on(events.NewMessage(...))</code> реагируем на события; (4) при больших объёмах работы &mdash; история через <code>iter_messages</code>, медиа через <code>download_media</code>/<code>iter_download</code>, участники через <code>iter_participants</code>, постранично, всегда перехватывая <code>FloodWaitError</code>/<code>PeerFloodError</code>, с сохранением прогресса.</p>
<h3>Где чаще всего встречаются ошибки</h3>
<table>
<tr><th>Этап</th><th>Типичная ошибка</th><th>Правильный подход</th></tr>
<tr><td>Хранение сессии</td><td>Запись StringSession в код и коммит в git</td><td>Переменная окружения/secrets manager, *.session в .gitignore</td></tr>
<tr><td>Разрешение entity</td><td>Не перехватывать ValueError</td><td>try/except ValueError вокруг get_entity/send_message</td></tr>
<tr><td>Массовое чтение истории</td><td>Получить всю историю разом через get_messages(limit=100000)</td><td>iter_messages + продолжение через offset_id с сохранением прогресса</td></tr>
<tr><td>Вступление в каналы</td><td>Вступление подряд, без пауз, во множество групп</td><td>Случайная пауза + перехват PeerFloodError</td></tr>
<tr><td>Загрузка медиа</td><td>Загрузка без прогресса, строго последовательно (по одному)</td><td>progress_callback + ограниченный параллелизм через Semaphore</td></tr>
</table>
<h3>Почему порядок важен</h3>
<p>Если в этой цепочке нарушены два правила, наступают серьёзные последствия: первое &mdash; пренебрежение безопасностью сессии (урок 3) &mdash; может привести к полной потере аккаунта; второе &mdash; пренебрежение ограничениями скорости/ToS (урок 7) &mdash; может привести к ограничению или блокировке аккаунта. Все остальные технические знания (обработчики событий, iter_messages, медиа) работают безопасно только при соблюдении этих двух правил.</p>""",
"code_content": """# review_flow.py -- 1-9-darslar bilimini bitta qisqa zanjirga bog'lash
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PeerFloodError

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),  # 2-3-darslar: xavfsiz session
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


@client.on(events.NewMessage(pattern="/holat", outgoing=True))  # 5-dars: event handler
async def on_status(event: events.NewMessage.Event) -> None:
    me = await client.get_me()
    dialogs_count = 0
    async for _ in client.iter_dialogs(limit=50):  # 9-dars: dialoglar
        dialogs_count += 1
    await event.reply(f"Salom, {me.first_name}! Faol dialoglar: {dialogs_count}+")


async def safe_bulk_operation() -> None:
    \"\"\"6, 7, 8-darslar bilimini birlashtirgan xavfsiz ommaviy amal namunasi.\"\"\"
    try:
        async for message in client.iter_messages("@ochiq_kanal_namunasi", limit=100, wait_time=1):
            if message.file:
                await client.download_media(message, file=f"downloads/{message.id}")
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds}s kutamiz.")
        await asyncio.sleep(e.seconds)
    except PeerFloodError:
        print("PeerFloodError -- ommaviy amal to'xtatildi, keyinroq davom etamiz.")


async def main() -> None:
    async with client:
        print("Review userbot ishga tushdi.")
        await safe_bulk_operation()
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """# review_flow.py -- связываем знания уроков 1-9 в одну короткую цепочку
import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PeerFloodError

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),  # уроки 2-3: безопасная сессия
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


@client.on(events.NewMessage(pattern="/holat", outgoing=True))  # урок 5: обработчик событий
async def on_status(event: events.NewMessage.Event) -> None:
    me = await client.get_me()
    dialogs_count = 0
    async for _ in client.iter_dialogs(limit=50):  # урок 9: диалоги
        dialogs_count += 1
    await event.reply(f"Привет, {me.first_name}! Активных диалогов: {dialogs_count}+")


async def safe_bulk_operation() -> None:
    \"\"\"Пример безопасной массовой операции, объединяющей знания уроков 6, 7, 8.\"\"\"
    try:
        async for message in client.iter_messages("@пример_открытого_канала", limit=100, wait_time=1):
            if message.file:
                await client.download_media(message, file=f"downloads/{message.id}")
    except FloodWaitError as e:
        print(f"FloodWait: ждём {e.seconds}с.")
        await asyncio.sleep(e.seconds)
    except PeerFloodError:
        print("PeerFloodError -- массовая операция остановлена, продолжим позже.")


async def main() -> None:
    async with client:
        print("Обзорный юзербот запущен.")
        await safe_bulk_operation()
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: 1-9-darslar bilimini bitta mini-userbotga birlashtiring""",
"task_title_ru": """Практика: объедините знания уроков 1-9 в один мини-юзербот""",
"task_description": """StringSession asosida ishlaydigan, kamida bitta event handler (masalan /holat buyrug'i), kamida bitta xavfsiz ommaviy amal (iter_messages yoki media yuklash, FloodWaitError ushlangan holda) va dialoglar hisobotini birlashtirgan mini-userbot yozing.""",
"task_description_ru": """Напишите мини-юзербот на основе StringSession, объединяющий минимум один обработчик событий (например, команда /holat), минимум одну безопасную массовую операцию (iter_messages или загрузка медиа с перехватом FloodWaitError) и отчёт по диалогам.""",
"task_requirements": """Session StringSession orqali muhit o'zgaruvchisidan o'qilishi; kamida 1 event handler; FloodWaitError/PeerFloodError to'g'ri ushlangan bo'lishi kerak.""",
"task_requirements_ru": """Сессия должна читаться через StringSession из переменной окружения; минимум 1 обработчик событий; FloodWaitError/PeerFloodError должны корректно обрабатываться.""",
"task_technologies": "Python 3.11+, Telethon",
"task_deadline_days": 4,
},
"sample": {
"title": """Namuna: 1-9-darslar review skeleti""",
"description": """Session, event handler va xavfsiz ommaviy amalni birlashtirgan qisqa review skripti""",
"sample_type": "code",
"code_files": [
{"filename": "review_bot.py", "language": "python", "code": """import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)


@client.on(events.NewMessage(pattern="/hisobot", outgoing=True))
async def report(event):
    dialogs = [d async for d in client.iter_dialogs(limit=20)]
    unread = sum(d.unread_count for d in dialogs)
    await event.reply(f"So'nggi 20 dialog: {unread} ta o'qilmagan xabar.")


if __name__ == "__main__":
    with client:
        client.run_until_disconnected()
"""},
],
},
"exercises": [
{
"title": """Zanjirdagi eng xavfli ikki nuqta""",
"title_ru": """Две самые опасные точки в цепочке""",
"description": """1-9-darslar bo'yicha, e'tiborsiz qoldirilsa eng og'ir oqibatga olib keladigan ikkita narsa qaysi?""",
"description_ru": """По урокам 1-9, какие две вещи при пренебрежении приводят к самым тяжёлым последствиям?""",
"exercise_type": "multiple_choice",
"options": ["Kod formatlash uslubi va o'zgaruvchi nomlari", "Session xavfsizligi va tezlik/ToS cheklovlari", "Docstring yozish va type hint qo'shish", "Fayl nomlash konventsiyasi"],
"options_ru": ["Стиль форматирования кода и имена переменных", "Безопасность сессии и ограничения скорости/ToS", "Написание docstring и добавление type hints", "Конвенция именования файлов"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bittasi hisobni yo'qotishga, ikkinchisi bloklanishga olib keladi.""",
"hint_ru": """Одно ведёт к потере аккаунта, другое -- к блокировке.""",
"explanation": """Session oqib ketishi hisobni to'liq qo'lga olishga, tezlik/ToS cheklovlarini e'tiborsiz qoldirish esa hisobni cheklash yoki blokka olib kelishi mumkin -- boshqa barcha texnik bilim shu ikkitasi ustiga quriladi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """To'g'ri ommaviy o'qish yondashuvi""",
"title_ru": """Правильный подход к массовому чтению""",
"description": """Katta hajmdagi tarixni o'qishning to'g'ri yondashuvi qaysi?""",
"description_ru": """Какой подход правильный для чтения большого объёма истории?""",
"exercise_type": "multiple_choice",
"options": ["get_messages(limit=100000) bitta chaqiruvda", "iter_messages + offset_id bilan progressni saqlab davom ettirish", "Barcha xabarlarni qo'lda, bittalab so'rash", "Faqat get_dialogs ishlatish"],
"options_ru": ["get_messages(limit=100000) одним вызовом", "iter_messages + продолжение через offset_id с сохранением прогресса", "Запрашивать все сообщения вручную, по одному", "Использовать только get_dialogs"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Xotira sarfi va davom ettirish imkoniyati muhim.""",
"hint_ru": """Важны расход памяти и возможность продолжения.""",
"explanation": """iter_messages xotirani bir xilda ushlab turadi va offset_id bilan oldingi to'xtagan joydan davom ettirish imkonini beradi -- katta hajm uchun bu yagona amaliy yondashuv.""",
"difficulty_level": "Medium",
"points": 8,
},
],
},
{
"order": 10,
"title": """11-Gibrid arxitektura: userbot va aiogram botni bitta tizimda birlashtirish""",
"title_ru": """11-Гибридная архитектура: объединение юзербота и бота на aiogram в одной системе""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>Nega ikkalasi birga kerak bo'lishi mumkin</h3>
<p>48-kursdagi aiogram bot va bu kursdagi Telethon userbot &mdash; ikkalasi ham kuchli, lekin har biri boshqa narsada. Bot: xavfsiz, oldindan tanish sintaksisga ega, foydalanuvchilar bilan ochiq muloqot uchun mo'ljallangan (buyruqlar, inline klaviatura, to'lovlar) va Telegram tomonidan "ishonchli" hisoblanadi. Userbot: kanal/guruh tarixini to'liq o'qiy oladi, admin bo'lmasdan ham kuzatuv olib boradi, lekin foydalanuvchilar bilan ochiq, ommaviy muloqot uchun mo'ljallanmagan (7-darsdagi ToS xavfini eslang). <strong>Gibrid arxitektura</strong> &mdash; ikkalasini o'z kuchli tomoniga ko'ra ishlatish: userbot orqa fonda kuzatadi/yig'adi, bot esa foydalanuvchi bilan xavfsiz muloqot qiladi.</p>
<h3>Amaliy misol: kanal monitoring + bildirishnoma</h3>
<p>Tasavvur qiling: sizga tegishli bo'lmagan (faqat a'zo bo'lgan) bir nechta ochiq kanalda muayyan kalit so'z paydo bo'lganda, foydalanuvchilaringizga bot orqali bildirishnoma yuborish kerak. Userbot buni <code>events.NewMessage(chats=[...])</code> orqali kuzatadi (kanal admini bo'lish shart emas &mdash; shunchaki a'zo bo'lish yetarli); topilgan moslikni ichki navbat (queue) orqali botga uzatadi; bot esa <code>bot.send_message(subscriber_id, ...)</code> orqali obunachilarga yetkazadi. Bu &mdash; aiogram-only kurslarda hech qachon ko'rilmaydigan, chunki bot API o'zi hech qachon kanal tarixini kuzata olmaydi.</p>
<h3>Bitta jarayon ichida yoki alohida jarayonlarda</h3>
<p>Ikkala client ham <code>asyncio</code>-asosli bo'lgani uchun, texnik jihatdan ularni bitta Python jarayonida <code>asyncio.gather(bot_task, userbot_task)</code> orqali birga ishga tushirish mumkin. Lekin production'da <strong>alohida jarayonlar</strong> (masalan, ikkita systemd xizmati) tavsiya etiladi: (1) biri qulasa, ikkinchisi ishlashda davom etadi; (2) har birini mustaqil qayta ishga tushirish/masshtablash mumkin; (3) userbot'ning tezlik cheklovlari botning tezlik cheklovlariga aralashmaydi. Aloqa uchun Redis pub/sub, oddiy DB jadvali (navbat sifatida) yoki xabar navbati (masalan RabbitMQ) ishlatiladi.</p>
<pre class="mermaid">
flowchart LR
  A["Telethon userbot\n(kanallarni kuzatadi, a'zo sifatida)"] -->|"Kalit so'z topildi"| B["Navbat: Redis / DB jadvali"]
  B --> C["aiogram bot\n(obunachilarga xabar yetkazadi)"]
  C --> D["Foydalanuvchi 1"]
  C --> E["Foydalanuvchi 2"]
  C --> F["Foydalanuvchi N"]
</pre>
<p>Diagramma shuni ko'rsatadi: userbot va bot bir-biri bilan TO'G'RIDAN-TO'G'RI gaplashmaydi &mdash; ular orasida navbat qatlami bor. Bu ataylab shunday: agar userbot vaqtincha ishlamay qolsa (masalan, FloodWait tufayli), bot baribir mavjud navbat asosida ishlashda davom etadi, va aksincha.</p>
<h3>Xavfsizlik chegarasi -- ikkalasini aralashtirmang</h3>
<p>Muhim qoida: bot tomonidagi foydalanuvchi kiritgan ma'lumot (masalan, <code>/kuzat @kanal</code> buyrug'i) hech qachon TO'G'RIDAN-TO'G'RI, tekshirilmasdan userbotga "shu kanalga qo'shil" buyrug'iga aylanmasin. Aks holda, istalgan foydalanuvchi sizning userbotingizni o'zining shaxsiy maqsadi uchun (masalan, ko'plab kanalga ommaviy qo'shilish) ishlatib, hisobingizni 7-darsda tasvirlangan xavf ostiga qo'yishi mumkin. Har doim ro'yxatni, tezlikni va qaysi kanallar kuzatilishini o'zingiz (administrator sifatida) nazorat qiling, foydalanuvchi so'roviga avtomatik ishonmang.</p>
<h3>Ikki turdagi maxfiy ma'lumot -- alohida saqlanadi</h3>
<p>Gibrid tizimda ikkita mutlaqo boshqa maxfiy ma'lumot bor: bot tokeni (@BotFather'dan, agar oqib ketsa &mdash; faqat bot hisobi xavf ostida, uni bekor qilish oson) va userbot session (2-3-darslar, agar oqib ketsa &mdash; butun shaxsiy hisob xavf ostida). Ularni HECH QACHON bir xil muhit o'zgaruvchisi guruhida, bir xil log faylida yoki bir xil xatolik xabarida aralashtirmang &mdash; ikkalasi uchun alohida <code>.env</code> qatorlari, va agar imkon bo'lsa, alohida secrets manager yozuvlari ishlatilishi tavsiya etiladi.</p>
<h3>Kengaytirish: bir nechta kanal, bir nechta obunachi</h3>
<p>Loyiha o'sib, kuzatiladigan kanallar yoki obunachilar soni ko'paysa, navbat mexanizmi (Redis) tabiiy ravishda masshtablanadi &mdash; userbot tomonida yozuvchi (producer) bitta bo'lib qoladi, bot tomonida esa bir nechta "worker" jarayoni navbatni parallel o'qishi mumkin. Bu arxitektura shuningdek testlashga ham qulay: 123-kursda ko'rgan pytest+mock yondashuvini bu yerda ham qo'llash mumkin &mdash; userbot qismini haqiqiy Telegram ulanishisiz, faqat navbatga yozuvchi funksiya sifatida sinab ko'rish mumkin.</p>""",
"text_content_ru": """<h3>Зачем могут понадобиться оба вместе</h3>
<p>Бот на aiogram из курса 48 и юзербот на Telethon из этого курса &mdash; оба мощные, но каждый силён в своём. Бот: безопасен, имеет знакомый синтаксис, предназначен для открытого общения с пользователями (команды, inline-клавиатуры, платежи) и считается Telegram "доверенным". Юзербот: может полностью читать историю канала/группы, вести наблюдение без прав администратора, но не предназначен для открытого, массового общения с пользователями (вспомните риск ToS из урока 7). <strong>Гибридная архитектура</strong> &mdash; это использование каждого по его сильной стороне: юзербот наблюдает/собирает в фоне, бот безопасно общается с пользователем.</p>
<h3>Практический пример: мониторинг канала + уведомление</h3>
<p>Представьте: вам нужно отправлять пользователям уведомление через бота, когда в нескольких открытых каналах (в которых вы только участник, не владелец) появляется определённое ключевое слово. Юзербот отслеживает это через <code>events.NewMessage(chats=[...])</code> (быть админом канала не нужно &mdash; достаточно быть участником); найденное совпадение передаётся через внутреннюю очередь боту; бот же через <code>bot.send_message(subscriber_id, ...)</code> доставляет его подписчикам. Это архитектура, которую никогда не увидишь в курсах только про aiogram, потому что Bot API сам по себе никогда не может отслеживать историю канала.</p>
<h3>В одном процессе или в отдельных процессах</h3>
<p>Поскольку оба клиента основаны на <code>asyncio</code>, технически их можно запустить вместе в одном процессе Python через <code>asyncio.gather(bot_task, userbot_task)</code>. Но в продакшене рекомендуются <strong>отдельные процессы</strong> (например, две службы systemd): (1) если один падает, второй продолжает работать; (2) каждый можно независимо перезапускать/масштабировать; (3) ограничения скорости юзербота не смешиваются с ограничениями скорости бота. Для связи используется Redis pub/sub, простая таблица в БД (в роли очереди) или очередь сообщений (например RabbitMQ).</p>
<pre class="mermaid">
flowchart LR
  A["Юзербот Telethon\n(следит за каналами как участник)"] -->|"Найдено ключевое слово"| B["Очередь: Redis / таблица БД"]
  B --> C["Бот на aiogram\n(доставляет уведомление подписчикам)"]
  C --> D["Пользователь 1"]
  C --> E["Пользователь 2"]
  C --> F["Пользователь N"]
</pre>
<p>Диаграмма показывает: юзербот и бот НЕ общаются друг с другом напрямую &mdash; между ними есть слой очереди. Это сделано намеренно: если юзербот временно не работает (например, из-за FloodWait), бот всё равно продолжает работать на основе существующей очереди, и наоборот.</p>
<h3>Граница безопасности -- не смешивайте их</h3>
<p>Важное правило: данные, введённые пользователем на стороне бота (например, команда <code>/следить @канал</code>), никогда не должны НАПРЯМУЮ, без проверки, превращаться в команду юзерботу "вступи в этот канал". Иначе любой пользователь сможет использовать вашего юзербота в своих личных целях (например, для массового вступления во множество каналов), подвергая ваш аккаунт риску, описанному в уроке 7. Всегда сами (как администратор) контролируйте список, скорость и то, какие каналы отслеживаются, не доверяйте автоматически пользовательскому запросу.</p>
<h3>Два типа секретов -- хранятся отдельно</h3>
<p>В гибридной системе есть два совершенно разных секрета: токен бота (от @BotFather, при утечке &mdash; под угрозой только аккаунт бота, его легко отозвать) и сессия юзербота (уроки 2-3, при утечке &mdash; под угрозой весь личный аккаунт). НИКОГДА не смешивайте их в одной группе переменных окружения, в одном лог-файле или в одном сообщении об ошибке &mdash; рекомендуется использовать отдельные строки <code>.env</code> для каждого, а по возможности &mdash; отдельные записи в secrets manager.</p>
<h3>Масштабирование: несколько каналов, несколько подписчиков</h3>
<p>Если проект растёт и увеличивается число отслеживаемых каналов или подписчиков, механизм очереди (Redis) естественно масштабируется &mdash; на стороне юзербота остаётся один producer, а на стороне бота несколько процессов-"воркеров" могут параллельно читать очередь. Такая архитектура также удобна для тестирования: подход pytest+mock из курса 123 применим и здесь &mdash; часть с юзерботом можно тестировать без реального подключения к Telegram, просто как функцию записи в очередь.</p>""",
"code_content": """\"\"\"Gibrid arxitektura: Telethon userbot + aiogram bot, Redis navbat orqali.
pip install telethon aiogram redis python-dotenv
\"\"\"
import asyncio
import json
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher

load_dotenv()

QUEUE_KEY = "userbot:alerts"
redis_client = aioredis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

# --- Userbot qismi -----------------------------------------------------
userbot = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)
KEYWORDS = ["chegirma", "aksiya"]
MONITORED_CHANNELS = ["@ochiq_kanal_1", "@ochiq_kanal_2"]  # ADMIN nazorat qiladi, foydalanuvchi emas!


@userbot.on(events.NewMessage(chats=MONITORED_CHANNELS))
async def on_channel_message(event: events.NewMessage.Event) -> None:
    text = (event.text or "").lower()
    if any(kw in text for kw in KEYWORDS):
        payload = {
            "chat_id": event.chat_id,
            "message_id": event.id,
            "text": event.text[:200],
        }
        await redis_client.rpush(QUEUE_KEY, json.dumps(payload))
        print(f"Navbatga qo'shildi: {payload['text'][:40]!r}")


# --- Bot qismi ----------------------------------------------------------
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()
SUBSCRIBERS = [111111, 222222]  # obunachi student_id'lar (haqiqiy loyihada DB'dan)


async def notify_subscribers_loop() -> None:
    \"\"\"Navbatni doimiy tekshirib, topilgan moslikni obunachilarga yetkazadi.\"\"\"
    while True:
        raw = await redis_client.blpop(QUEUE_KEY, timeout=5)
        if raw is None:
            continue
        _, payload_json = raw
        payload = json.loads(payload_json)
        for subscriber_id in SUBSCRIBERS:
            await bot.send_message(
                subscriber_id, f"Yangi moslik topildi:\\n{payload['text']}"
            )


async def main() -> None:
    async with userbot:
        await asyncio.gather(
            userbot.run_until_disconnected(),
            notify_subscribers_loop(),
        )


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Гибридная архитектура: юзербот Telethon + бот aiogram, через очередь Redis.
pip install telethon aiogram redis python-dotenv
\"\"\"
import asyncio
import json
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher

load_dotenv()

QUEUE_KEY = "userbot:alerts"
redis_client = aioredis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

# --- Часть юзербота ------------------------------------------------------
userbot = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)
KEYWORDS = ["скидка", "акция"]
MONITORED_CHANNELS = ["@открытый_канал_1", "@открытый_канал_2"]  # контролирует АДМИН, не пользователь!


@userbot.on(events.NewMessage(chats=MONITORED_CHANNELS))
async def on_channel_message(event: events.NewMessage.Event) -> None:
    text = (event.text or "").lower()
    if any(kw in text for kw in KEYWORDS):
        payload = {
            "chat_id": event.chat_id,
            "message_id": event.id,
            "text": event.text[:200],
        }
        await redis_client.rpush(QUEUE_KEY, json.dumps(payload))
        print(f"Добавлено в очередь: {payload['text'][:40]!r}")


# --- Часть бота -----------------------------------------------------------
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()
SUBSCRIBERS = [111111, 222222]  # id подписчиков (в реальном проекте -- из БД)


async def notify_subscribers_loop() -> None:
    \"\"\"Постоянно проверяет очередь и доставляет найденные совпадения подписчикам.\"\"\"
    while True:
        raw = await redis_client.blpop(QUEUE_KEY, timeout=5)
        if raw is None:
            continue
        _, payload_json = raw
        payload = json.loads(payload_json)
        for subscriber_id in SUBSCRIBERS:
            await bot.send_message(
                subscriber_id, f"Найдено новое совпадение:\\n{payload['text']}"
            )


async def main() -> None:
    async with userbot:
        await asyncio.gather(
            userbot.run_until_disconnected(),
            notify_subscribers_loop(),
        )


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: kichik gibrid monitoring tizimi""",
"task_title_ru": """Практика: небольшая гибридная система мониторинга""",
"task_description": """Yuqoridagi namunani asos qilib, o'zingiz a'zo bo'lgan 1-2 ta ochiq kanalni kuzatuvchi userbot va topilgan xabarlarni sizga (Saved Messages orqali, aiogram bot shart emas) yetkazuvchi tizim yozing. Redis o'rniga oddiy JSON fayl-navbatdan foydalansangiz ham bo'ladi.""",
"task_description_ru": """На основе примера выше напишите юзербота, отслеживающего 1-2 открытых канала, где вы участник, и систему, доставляющую найденные сообщения вам (через Saved Messages, aiogram бот не обязателен). Вместо Redis можно использовать простую JSON-очередь в файле.""",
"task_requirements": """Kamida 1 kalit so'z bo'yicha kuzatuv; navbat mexanizmi (Redis yoki fayl) ishlatilgan bo'lishi; kuzatiladigan kanallar ro'yxati kodda administrator tomonidan qat'iy belgilangan (foydalanuvchi kiritmasin).""",
"task_requirements_ru": """Отслеживание минимум по 1 ключевому слову; должен использоваться механизм очереди (Redis или файл); список отслеживаемых каналов должен быть жёстко задан в коде администратором (не вводиться пользователем).""",
"task_technologies": "Python 3.11+, Telethon, aiogram (ixtiyoriy), Redis (ixtiyoriy)",
"task_deadline_days": 5,
},
"sample": {
"title": """Namuna: fayl-navbatli oddiy gibrid monitor""",
"description": """Redis'siz, oddiy JSON fayl orqali ishlaydigan minimal gibrid monitoring namunasi""",
"sample_type": "code",
"code_files": [
{"filename": "simple_hybrid_monitor.py", "language": "python", "code": """import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
QUEUE_FILE = Path("alerts_queue.json")
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)
KEYWORDS = ["muhim", "eslatma"]
MONITORED = ["@ochiq_kanal_namunasi"]


def push_alert(text: str) -> None:
    queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else []
    queue.append(text)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False))


@client.on(events.NewMessage(chats=MONITORED))
async def watcher(event):
    if any(k in (event.text or "").lower() for k in KEYWORDS):
        push_alert(event.text[:200])
        await client.send_message("me", f"[MONITOR] {event.text[:200]}")


if __name__ == "__main__":
    with client:
        print("Monitoring boshlandi...")
        client.run_until_disconnected()
"""},
],
},
"exercises": [
{
"title": """Nega alohida jarayonlar tavsiya etiladi""",
"title_ru": """Почему рекомендуются отдельные процессы""",
"description": """Production'da userbot va botni alohida jarayonlarda ishga tushirishning asosiy sababi nima?""",
"description_ru": """Какова основная причина запуска юзербота и бота в отдельных процессах в production?""",
"exercise_type": "multiple_choice",
"options": ["Bitta jarayonda ishlash texnik jihatdan imkonsiz", "Xato izolyatsiyasi -- biri qulasa, ikkinchisi ishlashda davom etadi", "Bu Telegram tomonidan majburiy talab", "Bitta jarayon ko'proq xotira sarflaydi"],
"options_ru": ["Работа в одном процессе технически невозможна", "Изоляция сбоев -- если один падает, второй продолжает работать", "Это обязательное требование Telegram", "Один процесс потребляет больше памяти"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Ikkalasi ham asyncio-asosli, texnik jihatdan bitta jarayonda ham ishlaydi.""",
"hint_ru": """Оба основаны на asyncio, технически могут работать и в одном процессе.""",
"explanation": """Asosiy sabab -- fault isolation: alohida jarayonlar bir-biridan mustaqil ishlaydi, qulash yoki qayta ishga tushirish boshqasiga ta'sir qilmaydi, va tezlik cheklovlari aralashmaydi.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Xavfsizlik chegarasi qoidasi""",
"title_ru": """Правило границы безопасности""",
"description": """Gibrid tizimda bot tomonidagi foydalanuvchi buyrug'i nima qilishi MUTLAQO mumkin emas?""",
"description_ru": """Что АБСОЛЮТНО недопустимо в гибридной системе для команды пользователя со стороны бота?""",
"exercise_type": "multiple_choice",
"options": ["Foydalanuvchiga xabar yuborish", "Userbotga tekshirilmasdan to'g'ridan-to'g'ri 'kanalga qo'shil' buyrug'i berish", "Bazadan ma'lumot o'qish", "Inline klaviatura ko'rsatish"],
"options_ru": ["Отправить пользователю сообщение", "Напрямую, без проверки, дать юзерботу команду 'вступить в канал'", "Прочитать данные из базы", "Показать inline-клавиатуру"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu userbot hisobini boshqa birovning maqsadi uchun ishlatishga imkon beradi.""",
"hint_ru": """Это позволяет использовать аккаунт юзербота в чужих целях.""",
"explanation": """Foydalanuvchi kiritgan buyruq to'g'ridan-to'g'ri, tekshirilmasdan userbot amaliga aylansa, istalgan kishi sizning hisobingizni ommaviy avtomatlashtirish uchun ishlatishi mumkin -- bu 7-darsdagi ToS xavfini keltirib chiqaradi.""",
"difficulty_level": "Hard",
"points": 8,
},
{
"title": """Gibrid arxitektura oqimini tartiblang""",
"title_ru": """Расположите поток гибридной архитектуры по порядку""",
"description": """Kanaldagi kalit so'zdan foydalanuvchiga bildirishnoma yetishigacha bo'lgan yo'lni tuzing.""",
"description_ru": """Составьте путь от ключевого слова в канале до уведомления пользователя.""",
"exercise_type": "drag_and_drop",
"drag_items": ["Userbot kuzatilayotgan kanalda kalit so'zni topadi", "Topilgan ma'lumot navbatga (Redis/fayl) yoziladi", "Bot navbatni doimiy tekshiradi", "Bot obunachilarga xabar yuboradi"],
"drag_items_ru": ["Юзербот находит ключевое слово в отслеживаемом канале", "Найденные данные записываются в очередь (Redis/файл)", "Бот постоянно проверяет очередь", "Бот отправляет сообщение подписчикам"],
"correct_order": ["Userbot kuzatilayotgan kanalda kalit so'zni topadi", "Topilgan ma'lumot navbatga (Redis/fayl) yoziladi", "Bot navbatni doimiy tekshiradi", "Bot obunachilarga xabar yuboradi"],
"hint": """Avval topish, keyin yozish, keyin tekshirish, oxirida yetkazish.""",
"hint_ru": """Сначала обнаружение, потом запись, потом проверка, в конце доставка.""",
"difficulty_level": "Medium",
"points": 7,
},
],
},
{
"order": 11,
"title": """12-Userbotni xavfsiz deploy qilish: sirlarni boshqarish va systemd""",
"title_ru": """12-Безопасный деплой юзербота: управление секретами и systemd""",
"points_reward": 18,
"code_language": "python",
"text_content": """<h3>Nima farq qiladi -- oddiy botga nisbatan</h3>
<p>aiogram botni deploy qilish (48-kurs) va Telethon userbotni deploy qilish o'xshash bosqichlarga ega (server, process manager, log), lekin bitta hal qiluvchi farq bilan: <strong>session</strong>. Bot tokenini almashtirish oson (BotFather orqali <code>/revoke</code>) va faqat bot hisobiga ta'sir qiladi; session'ni "almashtirish" esa qayta to'liq login talab qiladi va butun shaxsiy hisobga tegishli. Shu sababli userbot deploy qilishda sirlarni boshqarish alohida e'tibor talab qiladi.</p>
<h3>Session'ni serverga qanday yetkazish kerak</h3>
<p>Eng xavfsiz yo'l: <code>.session</code> faylni serverga qo'lda (masalan <code>scp</code> orqali, shifrlangan kanal orqali) bir marta ko'chirish, yoki <code>StringSession</code>ni server muhitidagi maxfiy o'zgaruvchi (masalan, systemd'ning <code>EnvironmentFile</code>, Docker secrets, yoki bulut provayderining secrets manager xizmati) sifatida saqlash. <strong>Hech qachon</strong> session'ni CI/CD log chiqishida, deploy skriptining konsol chiqishida yoki git commit xabarida ko'rsatmang &mdash; bular ko'pincha uzoq vaqt saqlanadigan, qidiriladigan joylar.</p>
<h3>systemd orqali uzluksiz ishlash</h3>
<p>Userbot skriptini doimiy ishlab turish uchun <code>systemd</code> xizmati sifatida sozlash tavsiya etiladi &mdash; bu avtomatik qayta ishga tushirish (server qayta yuklansa yoki jarayon qulasa), log'larni <code>journalctl</code> orqali markazlashtirilgan ko'rish, va <code>Restart=on-failure</code> orqali barqarorlikni beradi. Muhim: <code>EnvironmentFile</code> orqali berilgan <code>.env</code> faylning ruxsatlari <code>600</code> (faqat egasi o'qiy oladi) qilib qo'yilishi kerak.</p>
<pre class="mermaid">
flowchart TB
  A["Session StringSession sifatida yaratiladi (dev muhitda, bir marta)"] --> B["Serverning secrets manager/EnvironmentFile'ga yoziladi"]
  B --> C["systemd xizmati ishga tushiriladi"]
  C --> D{"Jarayon qulab tushdimi?"}
  D -- "Ha" --> E["Restart=on-failure avtomatik qayta ishga tushiradi"]
  E --> C
  D -- "Yo'q" --> F["Userbot barqaror ishlaydi, journalctl orqali log kuzatiladi"]
</pre>
<p>Diagramma shuni ko'rsatadi: session yaratish (xavfli, bir martalik qadam) va uni doimiy ishlatish (systemd tomonidan avtomatlashtirilgan) &mdash; ikkita alohida bosqich, va ular orasidagi ko'chirish eng ehtiyotkorlik talab qiladigan lahza.</p>
<h3>Bitta session -- bitta faol jarayon</h3>
<p>SQLite'ga asoslangan <code>.session</code> fayl bir vaqtning o'zida faqat bitta jarayon tomonidan ochilishi mumkin &mdash; ikkinchi jarayon uni ochishga urinsa, <code>database is locked</code> xatosi chiqadi. Bu ayniqsa deploy paytida muammo tug'diradi: eski jarayon hali to'liq to'xtamasdan turib yangisini ishga tushirish (masalan, "rolling deploy") session konfliktiga olib keladi. Xavfsiz deploy uchun: avval eskisini to'liq to'xtatish (<code>systemctl stop</code>), keyingina yangisini ishga tushirish (<code>systemctl start</code>) &mdash; <code>StringSession</code> ishlatilganda bu muammo yo'q, chunki fayl tizimiga yozish umuman kerak emas.</p>
<h3>Graceful shutdown</h3>
<p>Jarayon to'xtatilganda (masalan, <code>systemctl stop</code> yoki server qayta yuklanganda), <code>SIGTERM</code> signalini to'g'ri ushlab, <code>await client.disconnect()</code>ni chaqirish tavsiya etiladi &mdash; bu joriy so'rovlarni yakunlash va ulanishni toza yopish imkonini beradi, ma'lumot yo'qotish yoki keyingi ishga tushirishda g'alati holatlarning oldini oladi.</p>
<h3>Konteyner ichida deploy qilish</h3>
<p>systemd o'rniga Docker konteyneri orqali deploy qilish ham keng tarqalgan &mdash; bu holatda <code>StringSession</code> shubhasiz afzal, chunki konteynerlar odatda o'zgarmas (immutable) hisoblanadi va diskka doimiy yozish qulay emas. Session'ni konteynerga environment variable sifatida <code>docker run -e TELETHON_SESSION_STRING=...</code> yoki <code>docker-compose.yml</code>dagi <code>env_file</code> orqali uzatish mumkin &mdash; lekin <code>env_file</code> ishlatilgan taqdirda ham, o'sha faylning o'zi <code>.gitignore</code>da bo'lishi shart, xuddi oddiy <code>.env</code> kabi. Konteyner qulasa, orkestrator (masalan Docker Compose'ning <code>restart: unless-stopped</code>) uni systemd'ning <code>Restart=on-failure</code>siga o'xshash tarzda avtomatik qayta ishga tushiradi.</p>
<h3>Monitoring va ogohlantirish</h3>
<p>Userbot ishlab chiqarishda "jim" ishlab qolishi mumkin &mdash; masalan, session muddati o'tib ketsa yoki hisob cheklansa (7-dars), jarayon xato bermasdan shunchaki hech narsa qilmay qolishi mumkin. Shu sababli oddiy "process ishlayaptimi" tekshiruvidan tashqari, funksional tekshiruv ham qo'shish tavsiya etiladi &mdash; masalan, har necha soatda bir marta <code>client.get_me()</code> chaqirib, muvaffaqiyatsiz bo'lsa (yoki ma'lum vaqt ichida hech qanday yangi hodisa kelmasa) administratorlarga alohida kanalga xabar yuborish.</p>""",
"text_content_ru": """<h3>Что отличается от обычного бота</h3>
<p>Деплой бота на aiogram (курс 48) и деплой юзербота на Telethon имеют похожие этапы (сервер, process manager, логи), но с одним решающим отличием: <strong>сессия</strong>. Токен бота легко заменить (через <code>/revoke</code> у BotFather), и это затрагивает только аккаунт бота; "заменить" же сессию означает заново пройти полный вход, и это касается всего личного аккаунта. Поэтому при деплое юзербота управлению секретами уделяется особое внимание.</p>
<h3>Как передать сессию на сервер</h3>
<p>Самый безопасный способ: перенести файл <code>.session</code> на сервер вручную один раз (например, через <code>scp</code>, по зашифрованному каналу), либо хранить <code>StringSession</code> как секретную переменную окружения на сервере (например, <code>EnvironmentFile</code> systemd, Docker secrets, или сервис secrets manager облачного провайдера). <strong>Никогда</strong> не показывайте сессию в выводе логов CI/CD, в консольном выводе деплой-скрипта или в сообщении git-коммита &mdash; это часто долгоживущие, индексируемые места.</p>
<h3>Непрерывная работа через systemd</h3>
<p>Для постоянной работы скрипта юзербота рекомендуется настроить его как службу <code>systemd</code> &mdash; это даёт автоматический перезапуск (при перезагрузке сервера или падении процесса), централизованный просмотр логов через <code>journalctl</code>, и устойчивость через <code>Restart=on-failure</code>. Важно: права доступа к файлу <code>.env</code>, передаваемому через <code>EnvironmentFile</code>, должны быть <code>600</code> (читает только владелец).</p>
<pre class="mermaid">
flowchart TB
  A["Сессия создаётся как StringSession (в dev-среде, один раз)"] --> B["Записывается в secrets manager/EnvironmentFile сервера"]
  B --> C["Запускается служба systemd"]
  C --> D{"Процесс упал?"}
  D -- "Да" --> E["Restart=on-failure автоматически перезапускает"]
  E --> C
  D -- "Нет" --> F["Юзербот стабильно работает, логи через journalctl"]
</pre>
<p>Диаграмма показывает: создание сессии (опасный, разовый шаг) и её постоянное использование (автоматизировано systemd) &mdash; два отдельных этапа, и перенос между ними требует наибольшей осторожности.</p>
<h3>Одна сессия -- один активный процесс</h3>
<p>Файл <code>.session</code> на основе SQLite может быть открыт только одним процессом одновременно &mdash; если второй процесс попытается открыть его, возникнет ошибка <code>database is locked</code>. Это особенно проблематично во время деплоя: запуск нового процесса до полной остановки старого (например, "rolling deploy") приводит к конфликту сессии. Для безопасного деплоя: сначала полностью остановить старый (<code>systemctl stop</code>), и только потом запускать новый (<code>systemctl start</code>) &mdash; при использовании <code>StringSession</code> этой проблемы нет, так как запись в файловую систему вообще не требуется.</p>
<h3>Graceful shutdown</h3>
<p>При остановке процесса (например, <code>systemctl stop</code> или перезагрузке сервера) рекомендуется корректно перехватывать сигнал <code>SIGTERM</code> и вызывать <code>await client.disconnect()</code> &mdash; это позволяет завершить текущие запросы и чисто закрыть соединение, предотвращая потерю данных или странное поведение при следующем запуске.</p>
<h3>Деплой внутри контейнера</h3>
<p>Деплой через контейнер Docker вместо systemd тоже широко распространён &mdash; в этом случае <code>StringSession</code> безусловно предпочтительнее, потому что контейнеры обычно считаются неизменяемыми (immutable), и постоянная запись на диск неудобна. Сессию можно передать в контейнер как переменную окружения через <code>docker run -e TELETHON_SESSION_STRING=...</code> или через <code>env_file</code> в <code>docker-compose.yml</code> &mdash; но даже при использовании <code>env_file</code> сам этот файл обязательно должен быть в <code>.gitignore</code>, как и обычный <code>.env</code>. Если контейнер падает, оркестратор (например, <code>restart: unless-stopped</code> в Docker Compose) автоматически перезапускает его, аналогично <code>Restart=on-failure</code> у systemd.</p>
<h3>Мониторинг и оповещения</h3>
<p>Юзербот в продакшене может "тихо" перестать работать &mdash; например, если истёк срок сессии или аккаунт был ограничен (урок 7), процесс может просто ничего не делать, не выдавая ошибки. Поэтому, помимо обычной проверки "работает ли процесс", рекомендуется добавить и функциональную проверку &mdash; например, раз в несколько часов вызывать <code>client.get_me()</code>, и при неудаче (или если долгое время не приходит ни одного нового события) отправлять отдельное уведомление администраторам в специальный канал.</p>""",
"code_content": """\"\"\"Xavfsiz deploy: graceful shutdown va systemd bilan ishlash namunasi.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import signal

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

_shutdown_event = asyncio.Event()


def _handle_sigterm() -> None:
    print("SIGTERM qabul qilindi -- graceful shutdown boshlandi...")
    _shutdown_event.set()


async def heartbeat_monitor(interval_seconds: int = 3600) -> None:
    \"\"\"Funksional monitoring: userbot 'jim' ishlab qolganini aniqlash uchun
    davriy ravishda o'zini tekshiradi va administratorga xabar beradi.\"\"\"
    admin_chat = os.environ.get("ADMIN_ALERT_CHAT", "me")
    while True:
        try:
            me = await client.get_me()
            print(f"[heartbeat] OK -- {me.first_name} faol, {interval_seconds}s dan keyin qayta.")
        except Exception as exc:  # noqa: BLE001 -- monitoring uchun ataylab keng ushlanadi
            await client.send_message(
                admin_chat, f"[OGOHLANTIRISH] Userbot heartbeat muvaffaqiyatsiz: {exc!r}"
            )
        await asyncio.sleep(interval_seconds)


async def main() -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_sigterm)

    async with client:
        print("Userbot ishga tushdi (systemd tomonidan boshqariladi).")
        wait_task = asyncio.create_task(_shutdown_event.wait())
        disconnected_task = asyncio.create_task(client.run_until_disconnected())
        heartbeat_task = asyncio.create_task(heartbeat_monitor())

        done, pending = await asyncio.wait(
            {wait_task, disconnected_task}, return_when=asyncio.FIRST_COMPLETED
        )
        heartbeat_task.cancel()
        for task in pending:
            task.cancel()

    print("Ulanish toza yopildi. Chiqilmoqda.")


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"Пример безопасного деплоя: graceful shutdown и работа с systemd.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
import signal

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

_shutdown_event = asyncio.Event()


def _handle_sigterm() -> None:
    print("Получен SIGTERM -- начинается graceful shutdown...")
    _shutdown_event.set()


async def heartbeat_monitor(interval_seconds: int = 3600) -> None:
    \"\"\"Функциональный мониторинг: периодически проверяет себя, чтобы
    обнаружить, что юзербот "тихо" перестал работать, и уведомляет админа.\"\"\"
    admin_chat = os.environ.get("ADMIN_ALERT_CHAT", "me")
    while True:
        try:
            me = await client.get_me()
            print(f"[heartbeat] OK -- {me.first_name} активен, повтор через {interval_seconds}с.")
        except Exception as exc:  # noqa: BLE001 -- для мониторинга ловим широко намеренно
            await client.send_message(
                admin_chat, f"[ПРЕДУПРЕЖДЕНИЕ] Heartbeat юзербота не удался: {exc!r}"
            )
        await asyncio.sleep(interval_seconds)


async def main() -> None:
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_sigterm)

    async with client:
        print("Юзербот запущен (управляется через systemd).")
        wait_task = asyncio.create_task(_shutdown_event.wait())
        disconnected_task = asyncio.create_task(client.run_until_disconnected())
        heartbeat_task = asyncio.create_task(heartbeat_monitor())

        done, pending = await asyncio.wait(
            {wait_task, disconnected_task}, return_when=asyncio.FIRST_COMPLETED
        )
        heartbeat_task.cancel()
        for task in pending:
            task.cancel()

    print("Соединение чисто закрыто. Завершение работы.")


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Amaliy: systemd xizmat fayli va graceful shutdown""",
"task_title_ru": """Практика: файл службы systemd и graceful shutdown""",
"task_description": """Yuqoridagi graceful shutdown namunasi asosida userbot skriptingizni yozing va unga mos systemd .service faylini tayyorlang (EnvironmentFile, Restart=on-failure, ruxsatlari 600 bo'lgan .env bilan). Serverga (yoki virtual mashinaga) deploy qilishni simulyatsiya qiling.""",
"task_description_ru": """На основе примера graceful shutdown выше напишите скрипт юзербота и подготовьте соответствующий .service файл systemd (EnvironmentFile, Restart=on-failure, .env с правами 600). Смоделируйте деплой на сервер (или виртуальную машину).""",
"task_requirements": """.service faylida Restart=on-failure bo'lishi; .env fayl ruxsatlari 600 qilib ko'rsatilgan bo'lishi; SIGTERM to'g'ri ushlangan bo'lishi kerak.""",
"task_requirements_ru": """В .service файле должен быть Restart=on-failure; права .env файла должны быть указаны как 600; SIGTERM должен корректно перехватываться.""",
"task_technologies": "Python 3.11+, Telethon, systemd, Linux",
"task_deadline_days": 4,
},
"sample": {
"title": """Namuna: to'liq systemd xizmat konfiguratsiyasi""",
"description": """Userbot uchun tayyor systemd .service fayli va uni ishga tushirish bo'yicha qo'llanma""",
"sample_type": "code",
"code_files": [
{"filename": "telethon-userbot.service", "language": "text", "code": """[Unit]
Description=Telethon Userbot Monitoring Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=userbot
WorkingDirectory=/opt/telethon-userbot
EnvironmentFile=/opt/telethon-userbot/.env
ExecStart=/opt/telethon-userbot/venv/bin/python main.py
Restart=on-failure
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
"""},
{"filename": "deploy_notes.txt", "language": "text", "code": """1. .env fayl yaratish va ruxsatlarini cheklash:
   chmod 600 /opt/telethon-userbot/.env
   chown userbot:userbot /opt/telethon-userbot/.env

2. Xizmatni yoqish va ishga tushirish:
   sudo systemctl daemon-reload
   sudo systemctl enable telethon-userbot.service
   sudo systemctl start telethon-userbot.service

3. Log'larni kuzatish:
   journalctl -u telethon-userbot.service -f

4. Xavfsiz qayta deploy (eski jarayon TO'LIQ to'xtagandan keyin yangisi ishga tushadi):
   sudo systemctl stop telethon-userbot.service
   # yangi kodni joylashtirish
   sudo systemctl start telethon-userbot.service
"""},
],
},
"exercises": [
{
"title": """Bot tokeni va session orasidagi asosiy farq (deploy nuqtai nazaridan)""",
"title_ru": """Главное отличие токена бота от сессии (с точки зрения деплоя)""",
"description": """Deploy nuqtai nazaridan, session bot tokeniga qaraganda nima uchun ancha ehtiyotkorlik talab qiladi?""",
"description_ru": """С точки зрения деплоя, почему сессия требует гораздо большей осторожности, чем токен бота?""",
"exercise_type": "multiple_choice",
"options": ["Session kattaroq fayl hajmiga ega", "Bot tokenini oson bekor qilish mumkin, session esa butun shaxsiy hisobga tegishli", "Session faqat Linux serverlarda ishlaydi", "Bot tokeni shifrlangan, session esa emas"],
"options_ru": ["Сессия имеет больший размер файла", "Токен бота легко отозвать, а сессия относится ко всему личному аккаунту", "Сессия работает только на серверах Linux", "Токен бота зашифрован, а сессия нет"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """BotFather orqali /revoke qilish oson, lekin session'ni "bekor qilish" qayta login talab qiladi.""",
"hint_ru": """Отозвать через /revoke у BotFather легко, а "отменить" сессию требует повторного входа.""",
"explanation": """Bot tokeni oqib ketsa, uni BotFather orqali bir zumda bekor qilish mumkin -- faqat bot ishlamay qoladi. Session oqib ketsa, butun shaxsiy hisob xavf ostida, va tiklash ancha murakkabroq.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """database is locked xatoligi""",
"title_ru": """Ошибка database is locked""",
"description": """.session fayl asosidagi userbotni "rolling deploy" (eski to'xtamasdan yangisini ishga tushirish) qilishga urinilsa, odatda qanday xatolik chiqadi?""",
"description_ru": """При попытке "rolling deploy" (запуск нового процесса до остановки старого) юзербота на основе .session файла, какая ошибка обычно возникает?""",
"exercise_type": "multiple_choice",
"options": ["ConnectionError", "database is locked (SQLite konflikti)", "PhoneCodeInvalidError", "ModuleNotFoundError"],
"options_ru": ["ConnectionError", "database is locked (конфликт SQLite)", "PhoneCodeInvalidError", "ModuleNotFoundError"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """.session fayl SQLite formatida saqlanadi.""",
"hint_ru": """Файл .session хранится в формате SQLite.""",
"explanation": """SQLite fayl bir vaqtning o'zida faqat bitta jarayon tomonidan ochilishi mumkin -- ikkinchi jarayon urinsa, database is locked xatoligi chiqadi. Buning oldini olish uchun avval eskisini to'xtatib, keyin yangisini ishga tushirish kerak.""",
"difficulty_level": "Hard",
"points": 8,
},
{
"title": """Xavfsiz deploy tartibini tuzing""",
"title_ru": """Составьте порядок безопасного деплоя""",
"description": """.session fayl asosidagi userbotni yangilash uchun to'g'ri, xavfsiz tartibni tuzing.""",
"description_ru": """Составьте правильный, безопасный порядок обновления юзербота на основе .session файла.""",
"exercise_type": "drag_and_drop",
"drag_items": ["systemctl stop -- eski jarayonni to'liq to'xtatish", "Yangi kodni serverga joylashtirish", "systemctl start -- yangi jarayonni ishga tushirish", "journalctl orqali log'larni tekshirib, muvaffaqiyatli ishga tushganini tasdiqlash"],
"drag_items_ru": ["systemctl stop -- полностью остановить старый процесс", "Разместить новый код на сервере", "systemctl start -- запустить новый процесс", "Проверить логи через journalctl, подтвердить успешный запуск"],
"correct_order": ["systemctl stop -- eski jarayonni to'liq to'xtatish", "Yangi kodni serverga joylashtirish", "systemctl start -- yangi jarayonni ishga tushirish", "journalctl orqali log'larni tekshirib, muvaffaqiyatli ishga tushganini tasdiqlash"],
"hint": """Avval to'xtatish, keyin yangilash, keyin ishga tushirish, oxirida tekshirish.""",
"hint_ru": """Сначала остановка, потом обновление, потом запуск, в конце проверка.""",
"difficulty_level": "Medium",
"points": 7,
},
{
"title": """Toza uzilish uchun metod""",
"title_ru": """Метод для корректного отключения""",
"description": """SIGTERM qabul qilinganda, ulanishni toza yopish uchun chaqiriladigan client metodi: await client.___()""",
"description_ru": """Метод client, вызываемый при получении SIGTERM для чистого закрытия соединения: await client.___()""",
"exercise_type": "fill_in_blank",
"correct_answers": "disconnect",
"hint": """Nomi to'g'ridan-to'g'ri "ulanishni uzish" degan ma'noni bildiradi.""",
"hint_ru": """Название буквально означает "отключиться".""",
"difficulty_level": "Easy",
"points": 5,
},
],
},
{
"order": 12,
"title": """13-Yakuniy capstone: kanal-monitoring va ogohlantirish userboti""",
"title_ru": """13-Финальный capstone: юзербот для мониторинга каналов и оповещений""",
"points_reward": 25,
"code_language": "python",
"text_content": """<h3>Capstone nima uchun mo'ljallangan</h3>
<p>Bu yakuniy loyiha 2-12-darslarda o'rganilgan barcha bilimni bitta kichik, real ishlaydigan vositaga birlashtiradi: xavfsiz session boshqaruvi, event handlerlar, tarixni skanerlash, mediani yuklab olish, dialoglar bilan ishlash, mas'uliyatli tezlik nazorati va xavfsiz deploy. Maqsad &mdash; "kanal-monitoring va ogohlantirish userboti": siz a'zo bo'lgan bir nechta ochiq kanalni kuzatib, muayyan shartlar (kalit so'z, media turi, muayyan yuboruvchi) bajarilganda sizga (yoki belgilangan Saved Messages/kanalga) tuzilgan ogohlantirish yuboradigan vosita.</p>
<h3>Capstone talablari</h3>
<ul>
<li><strong>Xavfsiz autentifikatsiya</strong> (2-3-darslar): <code>StringSession</code> muhit o'zgaruvchisidan o'qilishi, hech qanday maxfiy ma'lumot kodda yoki repozitoriyada bo'lmasligi kerak.</li>
<li><strong>Kamida ikkita event handler turi</strong> (5-dars): masalan, <code>events.NewMessage</code> kalit so'z uchun va <code>events.ChatAction</code> muhim o'zgarish (masalan, kanal sarlavhasi o'zgarishi) uchun.</li>
<li><strong>Tarixiy kontekst</strong> (6-dars): ishga tushganda, <code>iter_messages</code> orqali oxirgi N ta xabarni tekshirib, "boshlang'ich holat" hisobotini tuzish.</li>
<li><strong>Media bilan ishlash</strong> (8-dars): agar ogohlantirish media bilan bog'liq bo'lsa (masalan, rasm), uni <code>download_media</code> orqali saqlash va progress ko'rsatish.</li>
<li><strong>Mas'uliyatli tezlik nazorati</strong> (7-dars): barcha ommaviy amallar <code>FloodWaitError</code>/<code>PeerFloodError</code>ni ushlashi, va kuzatiladigan kanallar ro'yxati faqat administrator (siz) tomonidan kodda belgilanishi kerak.</li>
<li><strong>Xavfsiz konfiguratsiya</strong> (12-dars): barcha sirlar <code>.env</code> orqali, <code>.gitignore</code>da <code>*.session</code> va <code>.env</code> bo'lishi shart.</li>
</ul>
<h3>Arxitektura -- barcha darslarni birlashtiruvchi ko'rinish</h3>
<pre class="mermaid">
flowchart TB
  A["Ishga tushirishda: iter_messages orqali\noxirgi holatni tekshirish"] --> B["events.NewMessage / events.ChatAction\nhandlerlari ro'yxatga olinadi"]
  B --> C{"Shart bajarildimi?\n(kalit so'z / media / yuboruvchi)"}
  C -- "Ha" --> D{"Media bormi?"}
  D -- "Ha" --> E["download_media orqali saqlash"]
  D -- "Yo'q" --> F["To'g'ridan-to'g'ri ogohlantirish tuzish"]
  E --> G["send_message('me', tuzilgan_ogohlantirish)"]
  F --> G
  C -- "Yo'q" --> H["Hech narsa qilinmaydi, kuzatuv davom etadi"]
  G --> I["FloodWaitError/PeerFloodError\nnazorati doimiy ishlaydi"]
</pre>
<p>Diagramma &mdash; bu kursning butun mazmunini bitta rasmda ifodalaydi: xavfsiz kirish (ko'rsatilmagan, lekin oldindan bajarilgan), real vaqtli kuzatuv, tarixiy kontekst, media, va doimiy tezlik/xavfsizlik nazorati bir vositada birlashadi.</p>
<h3>Baholash mezonlari</h3>
<p>Loyiha quyidagi mezonlar bo'yicha baholanadi: (1) xavfsizlik &mdash; session/sirlar kodda yoki repozitoriyada yo'qligi; (2) to'g'rilik &mdash; barcha talab qilingan funksiyalar ishlashi; (3) barqarorlik &mdash; xatoliklar (FloodWait, ValueError, tarmoq xatosi) to'g'ri ushlanishi; (4) mas'uliyat &mdash; kuzatiladigan kanallar ro'yxati qattiq belgilangan, foydalanuvchi kiritmagan bo'lishi. Bu &mdash; kursning yakuniy, eng yuqori ballli vazifasi, shuning uchun barcha oldingi darslardagi amaliy mashqlaringizni qayta ko'rib chiqish tavsiya etiladi.</p>
<h3>Kengaytirish g'oyalari (ixtiyoriy)</h3>
<p>Asosiy talablar bajarilgandan so'ng, loyihani quyidagi yo'nalishlarda kengaytirish mumkin: (a) 10-darsdagi gibrid arxitekturani qo'llab, ogohlantirishlarni Saved Messages o'rniga alohida aiogram bot orqali bir nechta obunachiga yetkazish; (b) 9-darsdagi <code>iter_participants</code> orqali kanal a'zolari sonining vaqt o'tishi bilan o'zgarishini kuzatish (ehtiyotkorlik bilan, kamdan-kam); (c) yig'ilgan ogohlantirishlarni oddiy SQLite jadvaliga yozib, keyinchalik qidirish/filtrlash imkonini qo'shish. Bular ixtiyoriy &mdash; asosiy baholash faqat yuqoridagi olti talabga asoslanadi, lekin bu kengaytmalar Telethon'ni haqiqiy loyihada qo'llash tajribasini chuqurlashtiradi.</p>
<h3>Kurs yakunida</h3>
<p>Ushbu 13 darsda siz aiogram Bot API'dan tubdan farq qiluvchi qatlamni &mdash; xom MTProto'ni Telethon orqali &mdash; o'rgandingiz: haqiqiy hisob sifatida login qilish, uning eng og'ir xavfsizlik oqibatlarini (session xavfsizligi) tushunish, hodisalarga real vaqtda reaktsiya bildirish, katta hajmdagi ma'lumot bilan mas'uliyat bilan ishlash, va buni ishlab chiqarishga xavfsiz yetkazish. Bu bilim endi sizga Bot API yetarli bo'lmagan har qanday real muammoni &mdash; shaxsiy arxivlash vositasidan tortib kichik monitoring xizmatigacha &mdash; hal qilish imkonini beradi.</p>""",
"text_content_ru": """<h3>Для чего предназначен capstone</h3>
<p>Этот итоговый проект объединяет все знания из уроков 2-12 в один маленький, реально работающий инструмент: безопасное управление сессией, обработчики событий, сканирование истории, загрузка медиа, работа с диалогами, ответственный контроль скорости и безопасный деплой. Цель &mdash; "юзербот для мониторинга каналов и оповещений": инструмент, который отслеживает несколько открытых каналов, где вы участник, и при выполнении определённых условий (ключевое слово, тип медиа, конкретный отправитель) отправляет вам (или в указанный Saved Messages/канал) структурированное оповещение.</p>
<h3>Требования к capstone</h3>
<ul>
<li><strong>Безопасная аутентификация</strong> (уроки 2-3): <code>StringSession</code> должна читаться из переменной окружения, никаких секретов в коде или репозитории.</li>
<li><strong>Минимум два типа обработчиков событий</strong> (урок 5): например, <code>events.NewMessage</code> для ключевого слова и <code>events.ChatAction</code> для важного изменения (например, смены заголовка канала).</li>
<li><strong>Исторический контекст</strong> (урок 6): при запуске проверить последние N сообщений через <code>iter_messages</code> и составить отчёт о "начальном состоянии".</li>
<li><strong>Работа с медиа</strong> (урок 8): если оповещение связано с медиа (например, фото), сохранить его через <code>download_media</code> с индикацией прогресса.</li>
<li><strong>Ответственный контроль скорости</strong> (урок 7): все массовые операции должны перехватывать <code>FloodWaitError</code>/<code>PeerFloodError</code>, а список отслеживаемых каналов должен быть задан в коде только администратором (вами).</li>
<li><strong>Безопасная конфигурация</strong> (урок 12): все секреты через <code>.env</code>, в <code>.gitignore</code> обязательно должны быть <code>*.session</code> и <code>.env</code>.</li>
</ul>
<h3>Архитектура -- объединяющий все уроки взгляд</h3>
<pre class="mermaid">
flowchart TB
  A["При запуске: проверка последнего состояния\nчерез iter_messages"] --> B["Регистрируются обработчики\nevents.NewMessage / events.ChatAction"]
  B --> C{"Условие выполнено?\n(ключевое слово / медиа / отправитель)"}
  C -- "Да" --> D{"Есть медиа?"}
  D -- "Да" --> E["Сохранение через download_media"]
  D -- "Нет" --> F["Формирование оповещения напрямую"]
  E --> G["send_message('me', сформированное_оповещение)"]
  F --> G
  C -- "Нет" --> H["Ничего не делается, наблюдение продолжается"]
  G --> I["Контроль FloodWaitError/PeerFloodError\nработает постоянно"]
</pre>
<p>Диаграмма отражает всё содержание этого курса на одной схеме: безопасный вход (не показан, но выполнен заранее), наблюдение в реальном времени, исторический контекст, медиа и постоянный контроль скорости/безопасности объединяются в одном инструменте.</p>
<h3>Критерии оценки</h3>
<p>Проект оценивается по следующим критериям: (1) безопасность &mdash; отсутствие сессии/секретов в коде или репозитории; (2) корректность &mdash; работа всех требуемых функций; (3) устойчивость &mdash; корректная обработка ошибок (FloodWait, ValueError, сетевая ошибка); (4) ответственность &mdash; список отслеживаемых каналов жёстко задан, не вводится пользователем. Это финальное, самое ценное по баллам задание курса, поэтому рекомендуется пересмотреть все предыдущие практические задания.</p>
<h3>Идеи для расширения (необязательно)</h3>
<p>После выполнения основных требований проект можно расширить в следующих направлениях: (а) применив гибридную архитектуру из урока 10, доставлять оповещения нескольким подписчикам через отдельного бота на aiogram вместо Saved Messages; (б) отслеживать изменение числа участников канала со временем через <code>iter_participants</code> из урока 9 (осторожно, редко); (в) записывать собранные оповещения в простую таблицу SQLite, добавив возможность поиска/фильтрации позже. Это необязательно &mdash; основная оценка опирается только на шесть требований выше, но эти расширения углубляют опыт применения Telethon в реальном проекте.</p>
<h3>По завершении курса</h3>
<p>За эти 13 уроков вы изучили слой, принципиально отличающийся от Bot API aiogram &mdash; сырой MTProto через Telethon: вход как настоящий аккаунт, понимание самых тяжёлых последствий безопасности (безопасность сессии), реакцию на события в реальном времени, ответственную работу с большими объёмами данных и безопасную доставку этого в продакшен. Эти знания теперь позволяют вам решать любую реальную задачу, для которой Bot API недостаточно &mdash; от инструмента личного архивирования до небольшого сервиса мониторинга.</p>""",
"code_content": """\"\"\"CAPSTONE: kanal-monitoring va ogohlantirish userboti.
Barcha kurs bilimini birlashtiradi -- to'liq ishlaydigan skelet.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PeerFloodError

load_dotenv()

client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

# ADMINISTRATOR tomonidan qat'iy belgilangan -- foydalanuvchi kiritmaydi (7, 11-darslar)
MONITORED_CHATS = ["@ochiq_kanal_1", "@ochiq_kanal_2"]
KEYWORDS = ["chegirma", "e'lon", "muhim"]
ALERT_DESTINATION = "me"  # Saved Messages


async def startup_report() -> None:
    \"\"\"6-dars: ishga tushganda so'nggi 24 soatlik tarixiy kontekstni tekshirish.\"\"\"
    since = datetime.now() - timedelta(hours=24)
    total_checked = 0
    matches = 0
    for chat in MONITORED_CHATS:
        async for message in client.iter_messages(chat, offset_date=since, reverse=True):
            total_checked += 1
            if message.text and any(kw in message.text.lower() for kw in KEYWORDS):
                matches += 1
    await client.send_message(
        ALERT_DESTINATION,
        f"[Boshlang'ich hisobot] {total_checked} ta xabar tekshirildi, "
        f"{matches} ta moslik topildi (so'nggi 24 soat).",
    )


async def send_alert(text: str, media=None) -> None:
    \"\"\"7-dars: FloodWait/PeerFlood himoyasi bilan ogohlantirish yuborish.\"\"\"
    try:
        if media:
            path = f"downloads/alert_{datetime.now().timestamp():.0f}"
            await client.download_media(media, file=path)  # 8-dars
            await client.send_file(ALERT_DESTINATION, path, caption=text)
        else:
            await client.send_message(ALERT_DESTINATION, text)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        await send_alert(text, media)
    except PeerFloodError:
        print("PeerFloodError -- ogohlantirish vaqtincha to'xtatildi.")


@client.on(events.NewMessage(chats=MONITORED_CHATS))  # 5-dars
async def on_keyword_match(event: events.NewMessage.Event) -> None:
    text = (event.text or "").lower()
    if any(kw in text for kw in KEYWORDS):
        alert_text = f"[Kalit so'z topildi] {event.chat_id}: {event.text[:200]}"
        await send_alert(alert_text, media=event.message if event.message.media else None)


@client.on(events.ChatAction(chats=MONITORED_CHATS))  # 5-dars
async def on_channel_change(event: events.ChatAction.Event) -> None:
    if event.new_title:
        await send_alert(f"[Kanal o'zgarishi] Yangi sarlavha: {event.new_title}")


async def main() -> None:
    async with client:
        print("Capstone userbot ishga tushdi.")
        await startup_report()
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"code_content_ru": """\"\"\"CAPSTONE: юзербот для мониторинга каналов и оповещений.
Объединяет все знания курса -- полностью рабочий скелет.
pip install telethon python-dotenv
\"\"\"
import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PeerFloodError

load_dotenv()

client = TelegramClient(
    StringSession(os.environ["TELETHON_SESSION_STRING"]),
    int(os.environ["API_ID"]),
    os.environ["API_HASH"],
)

# Жёстко задано АДМИНИСТРАТОРОМ -- пользователь не вводит (уроки 7, 11)
MONITORED_CHATS = ["@открытый_канал_1", "@открытый_канал_2"]
KEYWORDS = ["скидка", "объявление", "важно"]
ALERT_DESTINATION = "me"  # Saved Messages


async def startup_report() -> None:
    \"\"\"Урок 6: при запуске проверяем исторический контекст за последние 24 часа.\"\"\"
    since = datetime.now() - timedelta(hours=24)
    total_checked = 0
    matches = 0
    for chat in MONITORED_CHATS:
        async for message in client.iter_messages(chat, offset_date=since, reverse=True):
            total_checked += 1
            if message.text and any(kw in message.text.lower() for kw in KEYWORDS):
                matches += 1
    await client.send_message(
        ALERT_DESTINATION,
        f"[Начальный отчёт] проверено {total_checked} сообщений, "
        f"найдено {matches} совпадений (последние 24 часа).",
    )


async def send_alert(text: str, media=None) -> None:
    \"\"\"Урок 7: отправка оповещения с защитой от FloodWait/PeerFlood.\"\"\"
    try:
        if media:
            path = f"downloads/alert_{datetime.now().timestamp():.0f}"
            await client.download_media(media, file=path)  # урок 8
            await client.send_file(ALERT_DESTINATION, path, caption=text)
        else:
            await client.send_message(ALERT_DESTINATION, text)
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        await send_alert(text, media)
    except PeerFloodError:
        print("PeerFloodError -- оповещения временно приостановлены.")


@client.on(events.NewMessage(chats=MONITORED_CHATS))  # урок 5
async def on_keyword_match(event: events.NewMessage.Event) -> None:
    text = (event.text or "").lower()
    if any(kw in text for kw in KEYWORDS):
        alert_text = f"[Найдено ключевое слово] {event.chat_id}: {event.text[:200]}"
        await send_alert(alert_text, media=event.message if event.message.media else None)


@client.on(events.ChatAction(chats=MONITORED_CHATS))  # урок 5
async def on_channel_change(event: events.ChatAction.Event) -> None:
    if event.new_title:
        await send_alert(f"[Изменение канала] Новый заголовок: {event.new_title}")


async def main() -> None:
    async with client:
        print("Capstone юзербот запущен.")
        await startup_report()
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
""",
"task": {
"task_title": """Yakuniy capstone: kanal-monitoring va ogohlantirish userboti""",
"task_title_ru": """Финальный capstone: юзербот для мониторинга каналов и оповещений""",
"task_description": """Yuqoridagi skelet asosida, kamida 2 ta ochiq kanalni kuzatuvchi, tarixiy kontekst hisobotini beruvchi, media bilan ishlaydigan, FloodWait/PeerFlood himoyasiga ega, xavfsiz konfiguratsiyali (session .env orqali, .gitignore to'g'ri sozlangan) to'liq userbot yozing va uni qisqacha README bilan hujjatlashtiring (o'rnatish, ishga tushirish, xavfsizlik eslatmalari).""",
"task_description_ru": """На основе скелета выше напишите полноценного юзербота, отслеживающего минимум 2 открытых канала, выдающего отчёт по историческому контексту, работающего с медиа, с защитой от FloodWait/PeerFlood, с безопасной конфигурацией (сессия через .env, правильно настроенный .gitignore), и задокументируйте его кратким README (установка, запуск, заметки по безопасности).""",
"task_requirements": """Barcha 6 talab (xavfsiz autentifikatsiya, 2+ event handler, tarixiy kontekst, media ishlov, tezlik nazorati, xavfsiz konfiguratsiya) bajarilgan bo'lishi; README fayli mavjud bo'lishi; kod ishga tushirilganda xatosiz ishlashi kerak.""",
"task_requirements_ru": """Должны быть выполнены все 6 требований (безопасная аутентификация, 2+ обработчика событий, исторический контекст, обработка медиа, контроль скорости, безопасная конфигурация); должен быть файл README; код должен запускаться без ошибок.""",
"task_technologies": "Python 3.11+, Telethon, python-dotenv, systemd (ixtiyoriy)",
"task_deadline_days": 7,
},
"sample": {
"title": """Namuna: to'liq capstone loyiha tuzilishi""",
"description": """Capstone loyihaning tavsiya etilgan fayl tuzilishi va konfiguratsiya namunalari""",
"sample_type": "code",
"code_files": [
{"filename": "README.md", "language": "markdown", "code": """# Kanal-Monitoring Userbot

## O'rnatish
1. `pip install -r requirements.txt`
2. `.env.example`ni `.env`ga nusxalab, API_ID/API_HASH/TELETHON_SESSION_STRING'ni to'ldiring
3. `python create_session.py` (bir martalik -- StringSession yaratish uchun)

## Ishga tushirish
```
python main.py
```

## Xavfsizlik eslatmalari
- `.session` va `.env` fayllari HECH QACHON commit qilinmasin (.gitignore tekshiring)
- MONITORED_CHATS ro'yxati faqat administrator tomonidan o'zgartiriladi
- Session oqib ketgan deb gumon qilsangiz -- Active Sessions'da darhol tugating
"""},
{"filename": "requirements.txt", "language": "text", "code": """telethon>=1.34
python-dotenv>=1.0
"""},
{"filename": ".gitignore", "language": "text", "code": """*.session
*.session-journal
.env
downloads/
__pycache__/
"""},
],
},
"exercises": [
{
"title": """Capstone'da eng yuqori ustuvorlikdagi talab""",
"title_ru": """Требование с наивысшим приоритетом в capstone""",
"description": """Baholash mezonlari orasida, agar session yoki sirlar kodda ochiq ko'rinsa, bu qanday baholanadi?""",
"description_ru": """Среди критериев оценки, как будет оценен проект, если сессия или секреты видны в открытом коде?""",
"exercise_type": "multiple_choice",
"options": ["Kichik kamchilik, ozgina ball ayiriladi", "Jiddiy xavfsizlik nuqsoni -- 3-darsdagi asosiy qoidani buzadi", "Bunga umuman e'tibor berilmaydi", "Faqat kod uslubi masalasi"],
"options_ru": ["Незначительный недостаток, снимается немного баллов", "Серьёзный дефект безопасности -- нарушает основное правило урока 3", "На это вообще не обращают внимания", "Это только вопрос стиля кода"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu kurs boshidan beri ta'kidlab kelingan eng muhim xavfsizlik qoidasi.""",
"hint_ru": """Это самое важное правило безопасности, подчёркиваемое с начала курса.""",
"explanation": """Session/sirlarning kodda yoki repozitoriyada ko'rinishi -- 3-darsda batafsil o'rganilgan, hisobni to'liq qo'lga olishga olib keladigan jiddiy xavfsizlik nuqsoni, shuning uchun baholashda eng yuqori ustuvorlikka ega.""",
"difficulty_level": "Medium",
"points": 8,
},
{
"title": """Capstone arxitekturasidagi tarixiy kontekstning o'rni""",
"title_ru": """Роль исторического контекста в архитектуре capstone""",
"description": """startup_report() funksiyasi capstone loyihada qaysi darsning bilimiga asoslanadi?""",
"description_ru": """На знаниях какого урока основана функция startup_report() в capstone-проекте?""",
"exercise_type": "multiple_choice",
"options": ["5-dars (event handlerlar)", "6-dars (tarixni ommaviy o'qish, iter_messages)", "8-dars (media yuklash)", "12-dars (deploy)"],
"options_ru": ["Урок 5 (обработчики событий)", "Урок 6 (массовое чтение истории, iter_messages)", "Урок 8 (загрузка медиа)", "Урок 12 (деплой)"],
"correct_answers": "B",
"is_multiple_select": False,
"hint": """Bu funksiya oxirgi 24 soatlik xabarlarni tekshiradi.""",
"hint_ru": """Эта функция проверяет сообщения за последние 24 часа.""",
"explanation": """startup_report() offset_date va reverse parametrlari bilan iter_messages'ni ishlatadi -- bu to'g'ridan-to'g'ri 6-darsda o'rganilgan tarixni ommaviy o'qish texnikasi.""",
"difficulty_level": "Medium",
"points": 7,
},
{
"title": """Capstone arxitekturasi oqimini tartiblang""",
"title_ru": """Расположите поток архитектуры capstone по порядку""",
"description": """Capstone userbot ishga tushishidan ogohlantirish yuborilishigacha bo'lgan asosiy oqimni tuzing.""",
"description_ru": """Составьте основной поток от запуска capstone-юзербота до отправки оповещения.""",
"exercise_type": "drag_and_drop",
"drag_items": ["StringSession orqali xavfsiz login", "iter_messages orqali so'nggi 24 soatlik tarixiy hisobot", "Event handlerlar (NewMessage, ChatAction) ro'yxatga olinadi", "Shart bajarilganda send_alert() FloodWait himoyasi bilan chaqiriladi"],
"drag_items_ru": ["Безопасный вход через StringSession", "Исторический отчёт за последние 24 часа через iter_messages", "Регистрируются обработчики событий (NewMessage, ChatAction)", "При выполнении условия вызывается send_alert() с защитой от FloodWait"],
"correct_order": ["StringSession orqali xavfsiz login", "iter_messages orqali so'nggi 24 soatlik tarixiy hisobot", "Event handlerlar (NewMessage, ChatAction) ro'yxatga olinadi", "Shart bajarilganda send_alert() FloodWait himoyasi bilan chaqiriladi"],
"hint": """Avval kirish, keyin tarixiy kontekst, keyin ro'yxatga olish, oxirida real vaqtli reaktsiya.""",
"hint_ru": """Сначала вход, потом исторический контекст, потом регистрация, в конце реакция в реальном времени.""",
"difficulty_level": "Hard",
"points": 8,
},
{
"title": """Ommaviy amallarda majburiy ushlanadigan xatolik""",
"title_ru": """Обязательно перехватываемая ошибка в массовых операциях""",
"description": """Ijtimoiy amallar (qo'shilish, ko'p xabar yuborish) juda tez bajarilganda ko'tariladigan, darhol to'xtashni talab qiluvchi xatolik klassi: ___""",
"description_ru": """Класс исключения, выбрасываемый при слишком быстром выполнении социальных действий (вступление, множество сообщений), требующий немедленной остановки: ___""",
"exercise_type": "fill_in_blank",
"correct_answers": "PeerFloodError",
"hint": """7-darsda batafsil o'rganilgan.""",
"hint_ru": """Подробно разобрано в уроке 7.""",
"difficulty_level": "Medium",
"points": 8,
},
],
},
# LESSONS_END
]
