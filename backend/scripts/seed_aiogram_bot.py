"""Seed the "Telegram Bot aiogram" course (14 lessons: 11 main + 3 revisions).

Usage:
    cd backend
    python scripts/seed_aiogram_bot.py
    # add --dry-run to preview without writing

Idempotent: skips creation if a course with the same title already exists.

Target audience: Python: Keyingi Bosqich graduates. aiogram 3.x — modern
async-first Telegram bot framework. From BotFather setup to fully deployed
shop/delivery bot capstone with payments. Language: Uzbek + Russian
section labels. WIN-FIRST pedagogy.
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
    "title": "Telegram Bot aiogram",
    "description": (
        "Python: Keyingi Bosqich kursini tugatgan dasturchilar uchun: aiogram "
        "3.x bilan zamonaviy async Telegram botlari. BotFather'dan tortib "
        "FSM, inline tugmalar, database, file handling, deploy va to'liq "
        "delivery/shop bot capstone'iga qadar. Real local market uchun mos."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 5,
    "max_points": 280,
    "is_active": True,
    "is_published": True,
}


# ═════════════════════════════════════════════════════════════════════════════
# Lesson content placeholders
# ═════════════════════════════════════════════════════════════════════════════
L1_TEXT = """\
<h2>BotFather, token va birinchi "Salom" bot</h2>

<pre class="mermaid">
flowchart LR
    BF["BotFather\n@BotFather"] -->|/newbot| TOKEN["TOKEN"]
    TOKEN --> PY["Python bot.py"]
    PY -->|aiogram| API["Telegram API"]
    API --> USER["Foydalanuvchi"]
</pre>

<p>Telegram bot — bu sizning Python kodingiz Telegram orqali foydalanuvchi bilan gaplashishi. Buyurtma qabul qilish, eslatmalar, FAQ, mini-shop — har narsa. <strong>aiogram 3.x</strong> — bu Python'da bot yozish uchun eng zamonaviy framework. Async-first, type-safe, jamiyat eng katta (Russian/Uzbek tilida).</p>

<p>Bu darsda — 15 daqiqada ishlovchi bot.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — BotFather bilan tanishing</h4>

<p>1. Telegram'da <a href="https://t.me/BotFather">@BotFather</a> ni toping va <code>/start</code> bosing.</p>
<p>2. <code>/newbot</code> yuboring. BotFather sizdan 2 narsa so'raydi:</p>
<ul>
<li><strong>Bot nomi</strong> (ko'rinadi) — "Mening Birinchi Botim"</li>
<li><strong>Username</strong> (oxiri <code>_bot</code>) — <code>olim_birinchi_bot</code></li>
</ul>

<p>3. Token oldingiz! Misol:</p>
<pre><code>7234567890:AAH1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234</code></pre>

<p>⚠️ <strong>Token — sirli kalit</strong>. Hech kim bilan baham ko'rmang, GitHub'ga commit qilmang.</p>

<h4>BLOKA 2 — Loyiha sozlash</h4>

<pre><code># Terminal
mkdir mening-bot && cd mening-bot

# Virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\\Scripts\\activate

# aiogram va env'lar uchun
pip install aiogram python-dotenv

# requirements saqlash
pip freeze &gt; requirements.txt

# .env yaratish (TOKEN bu yerda)
cat &gt; .env &lt;&lt;EOF
BOT_TOKEN=7234567890:AAH1aBcDeFgHiJkL...
EOF

# .gitignore — token tushib ketmasin
cat &gt; .gitignore &lt;&lt;EOF
venv/
__pycache__/
*.pyc
.env
EOF</code></pre>

<h4>BLOKA 3 — Birinchi bot</h4>

<pre><code># bot.py
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}! 👋\\n"
        f"Men aiogram'da yozilgan bot'man."
    )

@dp.message()
async def echo(message: Message):
    await message.answer(f"Siz dedingiz: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())</code></pre>

<p>Ishga tushirish:</p>
<pre><code>python bot.py</code></pre>

<p>Telegram'da botni qidiring (username bilan) → <code>/start</code> → 🎉 Salom!</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>bot = Bot(token="7234567890:AAH1aBcDeFgHiJkLmNoP...")</code></pre>

<p><strong>Natija:</strong> Bot ishlaydi, lekin <strong>token kodda ko'rinadi</strong>. GitHub'ga push qilsangiz — bot o'g'irlanishi mumkin (botlar avtomatik token qidiradi). Token'ni o'g'rilangach BotFather'da <code>/revoke</code> qilish kerak.</p>

<p>To'g'risi — har doim <code>.env</code> + <code>os.getenv()</code>. Va <code>.env</code> ni <code>.gitignore</code>'ga.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. aiogram 3.x asosiy ob'ektlari</h4>

<table>
<tr><th>Ob'ekt</th><th>Vazifa</th></tr>
<tr><td><code>Bot</code></td><td>Telegram API ga so'rov yuboruvchi (send_message, va h.k.)</td></tr>
<tr><td><code>Dispatcher</code></td><td>Kelayotgan update'larni handler'larga taqsimlaydi</td></tr>
<tr><td><code>Message</code></td><td>Foydalanuvchi yuborgan xabar (text, from_user, chat, photo, ...)</td></tr>
<tr><td><code>CallbackQuery</code></td><td>Inline tugma bosilganda</td></tr>
<tr><td><code>Router</code></td><td>Handler'larni guruhlash (kattaroq loyihada)</td></tr>
</table>

<h4>2. Handler decorator'lari</h4>

<pre><code>@dp.message()              # har xabar
@dp.message(CommandStart())          # /start
@dp.message(Command("help"))         # /help
@dp.message(Command("settings"))     # /settings
@dp.callback_query()                  # inline tugma
@dp.edited_message()                  # tahrirlangan xabar</code></pre>

<h4>3. Message ichida nima bor?</h4>

<pre><code>async def handler(message: Message):
    message.text              # matn
    message.from_user.id      # user ID
    message.from_user.first_name  # ism
    message.from_user.username    # @username
    message.chat.id           # chat ID (DM = user ID)
    message.chat.type         # 'private', 'group', ...
    message.message_id        # xabar ID
    message.date              # vaqt
    message.photo             # rasm (agar bor)
    message.voice             # voice (agar bor)
    message.reply_to_message   # javob qilingan xabar
    message.entities          # mention, hashtag, link...
</code></pre>

<h4>4. Bot'ning asosiy metodlari</h4>

<pre><code># Message uslubida (tavsiya)
await message.answer("matn")              # shu chat'ga
await message.reply("matn")               # reply qilib
await message.answer_photo(rasm, caption="...")
await message.answer_video(video)
await message.delete()                    # xabarni o'chirish

# Bot uslubida (har joydan)
await bot.send_message(chat_id, "matn")
await bot.send_photo(chat_id, photo)
await bot.delete_message(chat_id, message_id)</code></pre>

<h4>5. Polling vs Webhook</h4>

<table>
<tr><th></th><th>Polling</th><th>Webhook</th></tr>
<tr><td>Qachon</td><td>Development, lokal</td><td>Production, server</td></tr>
<tr><td>Sozlash</td><td>Oson (<code>start_polling</code>)</td><td>HTTPS server kerak</td></tr>
<tr><td>Resurs</td><td>Bot doim Telegram'ga so'rov</td><td>Telegram bot'ga push qiladi</td></tr>
</table>

<p>Bu kursda — birinchi 9 dars polling. 10-darsda webhook va deploy.</p>

<h4>6. async/await — eslatma</h4>

<p>Python: Keyingi Bosqich kursida o'rgangansiz. aiogram async-first:</p>
<ul>
<li>Har handler — <code>async def</code></li>
<li>Bot metodlari — <code>await</code> bilan chaqiriladi</li>
<li><code>asyncio.run(main())</code> — entry point</li>
</ul>

<h4>7. Format'lash — Markdown va HTML</h4>

<pre><code>from aiogram.enums import ParseMode

# Bot yaratganda default parse_mode
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Endi har answer'da:
await message.answer("&lt;b&gt;Qalin&lt;/b&gt;, &lt;i&gt;qiyshiq&lt;/i&gt;, &lt;code&gt;kod&lt;/code&gt;")
await message.answer("&lt;a href='https://uz'&gt;link&lt;/a&gt;")</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ BotFather'da bot yaratish va token olish</li>
<li>✅ Token'ni <code>.env</code>'da xavfsiz saqlash</li>
<li>✅ aiogram 3.x — <code>Bot</code>, <code>Dispatcher</code>, <code>Message</code></li>
<li>✅ <code>@dp.message()</code>, <code>CommandStart()</code> decorator'lari</li>
<li>✅ <code>await message.answer(...)</code></li>
<li>✅ <code>asyncio.run(main())</code> + <code>start_polling</code></li>
<li>✅ HTML format'lash</li>
<li>✅ Polling vs Webhook tushuncha</li>
</ul>
"""

L1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 1: BotFather + birinchi aiogram bot
# ════════════════════════════════════════════════════════════════════
#
# Tayyorgarlik:
#   1) Telegram'da @BotFather'ga /newbot
#   2) Bot nomi + username (oxiri _bot)
#   3) Token oling
#
#   mkdir mening-bot && cd mening-bot
#   python -m venv venv
#   source venv/bin/activate
#   pip install aiogram python-dotenv
#
#   .env faylda:
#   BOT_TOKEN=7234567890:AAH1aBcDeFgHi...
# ════════════════════════════════════════════════════════════════════

# bot.py
import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


# ─────────────────────────────────────────────────────────────────────
# Sozlash
# ─────────────────────────────────────────────────────────────────────

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylda yo'q!")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# Handler'lar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: Message):
    ism = message.from_user.first_name or "Foydalanuvchi"
    await message.answer(
        f"Salom, <b>{ism}</b>! 👋\\n\\n"
        f"Men sizning birinchi aiogram bot'ingizman.\\n"
        f"Buyruqlar:\\n"
        f"/help — yordam\\n"
        f"/info — bot haqida"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Yordam</b>\\n\\n"
        "Menga istalgan matn yuboring — men uni qaytaraman (echo).\\n\\n"
        "Maxsus buyruqlar:\\n"
        "• /start — qaytadan boshlash\\n"
        "• /help — bu xabar\\n"
        "• /info — bot haqida\\n"
        "• /id — sizning Telegram ID"
    )


@dp.message(Command("info"))
async def cmd_info(message: Message):
    me = await bot.get_me()
    await message.answer(
        f"🤖 Bot: <b>{me.full_name}</b>\\n"
        f"Username: @{me.username}\\n"
        f"ID: <code>{me.id}</code>\\n\\n"
        f"Yaratuvchi: aiogram kursi talabasi"
    )


@dp.message(Command("id"))
async def cmd_id(message: Message):
    user = message.from_user
    await message.answer(
        f"Sizning ma'lumotlaringiz:\\n"
        f"ID: <code>{user.id}</code>\\n"
        f"Ism: {user.first_name}\\n"
        f"Familiya: {user.last_name or '—'}\\n"
        f"Username: @{user.username or '—'}\\n"
        f"Til: {user.language_code or '—'}"
    )


@dp.message()
async def echo(message: Message):
    if message.text:
        await message.answer(f"📝 Siz dedingiz: <i>{message.text}</i>")
    else:
        await message.answer("❓ Faqat matn yuboring (hozircha).")


# ─────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────

async def main():
    logging.info("Bot ishga tushdi...")
    # Eskirgan update'larni o'tkazib yuborish (bot ishlamagan paytdagilar)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nBot to'xtatildi (Ctrl+C)")


# ─────────────────────────────────────────────────────────────────────
# Sinash:
#   python bot.py
#
# Telegram'da bot'ni qidiring (username bilan):
#   /start
#   /help
#   /info
#   /id
#   "Salom" — echo qaytaradi
# ─────────────────────────────────────────────────────────────────────
"""
L2_TEXT = """\
<h2>Message handler'lar — turli xil filter'lar</h2>

<pre class="mermaid">
flowchart LR
    M["Update kelyapti"] --> F{"Filter zanjiri"}
    F -->|CommandStart| H1["start handler"]
    F -->|Command("help")| H2["help handler"]
    F -->|F.text == "Salom"| H3["text handler"]
    F -->|F.text.regexp(r"...")| H4["regex handler"]
    F -->|hech qaysi mos kelmasa| H5["catch-all"]
</pre>

<p>aiogram'ning eng kuchli xususiyati — <strong>filter zanjiri</strong>. Har handler decorator'iga filter qo'yasiz, va Telegram'dan kelayotgan har update <em>birinchi mos kelgan handler</em>'ga yo'naltiriladi. Tartib muhim!</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Asosiy filter'lar</h4>

<pre><code>from aiogram import F
from aiogram.filters import Command, CommandStart

# /start
@dp.message(CommandStart())
async def start(m: Message): ...

# /help yoki /info
@dp.message(Command("help", "info"))
async def help_cmd(m: Message): ...

# Aniq matn (case-sensitive)
@dp.message(F.text == "Salom")
async def salom(m: Message): ...

# Matnda mavjud (case-insensitive)
@dp.message(F.text.lower().contains("rahmat"))
async def rahmat(m: Message): ...

# Regex
@dp.message(F.text.regexp(r"^\\d+$"))   # faqat sonlar
async def son(m: Message): ...

# Faqat sticker yuborilsa
@dp.message(F.sticker)
async def sticker(m: Message): ...

# Photo
@dp.message(F.photo)
async def photo(m: Message): ...

# Catch-all (eng oxirda!)
@dp.message()
async def all_other(m: Message): ...</code></pre>

<h4>BLOKA 2 — Magic F bilan murakkab</h4>

<pre><code># Bir necha shart birga
@dp.message(F.text & F.from_user.id == 123)
async def admin_only(m: Message): ...

# Yoki
@dp.message(F.text.in_({"ha", "ok", "tasdiq"}))
async def tasdiq(m: Message): ...

# Negate
@dp.message(~F.text.startswith("/"))    # / bilan boshlanmagan
async def matn(m: Message): ...</code></pre>

<h4>BLOKA 3 — Argumentli buyruq</h4>

<pre><code>from aiogram.filters import Command, CommandObject

# /ban olim
@dp.message(Command("ban"))
async def ban(m: Message, command: CommandObject):
    if not command.args:
        await m.answer("Foydalanuvchini ko'rsating: /ban olim")
        return
    await m.answer(f"Ban: {command.args}")

# Bir nechta arg
# /weather Toshkent 7
@dp.message(Command("weather"))
async def weather(m: Message, command: CommandObject):
    args = command.args.split() if command.args else []
    if len(args) &lt; 2:
        await m.answer("Foydalanish: /weather &lt;shahar&gt; &lt;kun&gt;")
        return
    shahar, kun = args[0], args[1]
    await m.answer(f"{shahar} — {kun} kun")</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>@dp.message()          # ❌ Birinchi
async def hammasi(m): ...

@dp.message(Command("start"))   # bu hech qachon ishga tushmaydi!
async def start(m): ...</code></pre>

<p><strong>Sabab:</strong> aiogram handler'larni <strong>tartibda</strong> tekshiradi. Birinchi mos kelgan ishlaydi. Catch-all <code>@dp.message()</code> tepada bo'lsa — har xabar shu yerda to'xtaydi, qolganlari hech qachon ishga tushmaydi.</p>

<p><strong>Qoidasi:</strong> aniqroq filter'lar tepada, umumiy (catch-all) — eng oxirda.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Filter turlari to'liq</h4>

<table>
<tr><th>Filter</th><th>Misol</th></tr>
<tr><td><code>CommandStart()</code></td><td>/start (deeplink ham)</td></tr>
<tr><td><code>Command("X")</code></td><td>/X</td></tr>
<tr><td><code>Command("X", "Y")</code></td><td>/X yoki /Y</td></tr>
<tr><td><code>F.text == "salom"</code></td><td>aniq matn</td></tr>
<tr><td><code>F.text.lower() == "salom"</code></td><td>case-insensitive</td></tr>
<tr><td><code>F.text.contains("X")</code></td><td>ichida "X"</td></tr>
<tr><td><code>F.text.startswith("/")</code></td><td>/ bilan boshlangan</td></tr>
<tr><td><code>F.text.regexp(r"...")</code></td><td>regex</td></tr>
<tr><td><code>F.text.in_({...})</code></td><td>to'plamdan biri</td></tr>
<tr><td><code>F.photo</code></td><td>rasm yuborilgan</td></tr>
<tr><td><code>F.voice</code></td><td>voice xabar</td></tr>
<tr><td><code>F.sticker</code></td><td>sticker</td></tr>
<tr><td><code>F.document</code></td><td>hujjat</td></tr>
<tr><td><code>F.location</code></td><td>joylashuv</td></tr>
<tr><td><code>F.contact</code></td><td>kontakt</td></tr>
<tr><td><code>F.chat.type == "private"</code></td><td>shaxsiy DM</td></tr>
</table>

<h4>2. Magic Filter — F</h4>

<p><code>F</code> — aiogram'ning "magic filter" tizimi. Atribut, operator va metodlarni zanjir qilib filter yaratasiz.</p>

<pre><code>F.text                      # text bor
F.text.lower()              # kichik harf
F.text.startswith("hi")
F.from_user.id == 123
F.chat.type.in_({"group", "supergroup"})

# Boolean
&  # AND
|  # OR
~  # NOT</code></pre>

<h4>3. CommandObject — arg'lar bilan ishlash</h4>

<pre><code>from aiogram.filters import CommandObject

@dp.message(Command("echo"))
async def echo(m: Message, command: CommandObject):
    command.command   # "echo"
    command.prefix    # "/"
    command.mention   # bot mention (agar group'da)
    command.args      # /echo salom dunyo  → "salom dunyo"</code></pre>

<h4>4. Router — modullarga ajratish</h4>

<p>Katta loyihada — Router bilan handler'larni alohida fayllarga:</p>

<pre><code># handlers/start.py
from aiogram import Router
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start(m: Message): ...

# bot.py
from handlers import start, profile, admin

dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(admin.router)</code></pre>

<h4>5. Handler'da bir nechta filter (AND)</h4>

<pre><code>@dp.message(Command("admin"), F.from_user.id.in_({111, 222}))
async def admin_panel(m: Message):
    # Faqat /admin VA user ID 111 yoki 222
    await m.answer("Welcome admin")</code></pre>

<h4>6. Deeplink — /start parametr bilan</h4>

<pre><code># Link: t.me/your_bot?start=ref_olim
@dp.message(CommandStart(deep_link=True))
async def deeplink(m: Message, command: CommandObject):
    # command.args = "ref_olim"
    await m.answer(f"Siz keldingiz: {command.args}")</code></pre>

<h4>7. Error handling</h4>

<pre><code>from aiogram.types import ErrorEvent

@dp.error()
async def error_handler(event: ErrorEvent):
    logging.error(f"Update: {event.update}\\nException: {event.exception}")
    return True   # xato qayta ishlandi</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <code>Command</code>, <code>CommandStart</code>, <code>F</code> filter'lar</li>
<li>✅ Filter tartibi muhim — aniqdan umumiyga</li>
<li>✅ <code>F.text</code>, <code>F.photo</code>, <code>F.voice</code> — turli content tur</li>
<li>✅ <code>CommandObject</code> bilan arg'lar olish</li>
<li>✅ <code>Router</code> bilan handler'larni modullarga</li>
<li>✅ <code>&amp;</code>, <code>|</code>, <code>~</code> — filter kombinatsiyalari</li>
<li>✅ Deeplink (<code>?start=ref</code>) bilan ishlash</li>
</ul>
"""

L2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 2: Message handler'lar
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
import re
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

# Admin user ID'lar
ADMINS = {111111111, 222222222}   # haqiqiy ID'lar bilan almashtiring


# ─────────────────────────────────────────────────────────────────────
# 1) Buyruqlar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"Buyruqlar:\\n"
        f"/help — yordam\\n"
        f"/echo &lt;matn&gt; — echo\\n"
        f"/calc &lt;ifoda&gt; — kalkulyator\\n"
        f"/ban &lt;user&gt; — admin only"
    )


# Bitta handler — bir nechta buyruq uchun
@dp.message(Command("help", "yordam", "info"))
async def cmd_help(m: Message):
    await m.answer(
        "<b>Yordam</b>\\n\\n"
        "Quyidagi xabarlarni ham yuborib ko'ring:\\n"
        "• Salom — javob keladi\\n"
        "• Rahmat — yana javob\\n"
        "• Matn ichida 'pizza' — alohida\\n"
        "• Sonni yuboring — kvadrat hisoblanadi"
    )


# Arg'lar bilan
@dp.message(Command("echo"))
async def cmd_echo(m: Message, command: CommandObject):
    if not command.args:
        await m.answer("Foydalanish: /echo &lt;matn&gt;")
        return
    await m.answer(f"📣 <b>{command.args}</b>")


# Kalkulyator
@dp.message(Command("calc"))
async def cmd_calc(m: Message, command: CommandObject):
    if not command.args:
        await m.answer("Misol: /calc 2 + 2")
        return
    try:
        # XAVFLI — production'da bunday eval qilmang!
        # Bu faqat demo. Production: ast.literal_eval yoki sympy
        result = eval(command.args, {"__builtins__": {}}, {})
        await m.answer(f"= <code>{result}</code>")
    except Exception as e:
        await m.answer(f"Xato: {e}")


# Admin only
@dp.message(Command("ban"), F.from_user.id.in_(ADMINS))
async def cmd_ban(m: Message, command: CommandObject):
    if not command.args:
        await m.answer("Foydalanish: /ban &lt;user&gt;")
        return
    await m.answer(f"🔨 Ban: {command.args}")


# ─────────────────────────────────────────────────────────────────────
# 2) Matn bilan ishlash — F filter
# ─────────────────────────────────────────────────────────────────────

# Aniq matn
@dp.message(F.text == "Salom")
async def salom_yuborildi(m: Message):
    await m.answer(f"Va alaykum salom, {m.from_user.first_name}! 👋")


# Case-insensitive (lower bilan)
@dp.message(F.text.lower() == "rahmat")
async def rahmat(m: Message):
    await m.answer("Arzimaydi! 🤗")


# Ichida bo'lsa
@dp.message(F.text.lower().contains("pizza"))
async def pizza(m: Message):
    await m.answer("🍕 Pizza haqida gapiryapsizmi?")


# To'plamdan biri
@dp.message(F.text.in_({"ha", "ok", "tasdiqlayman"}))
async def tasdiq(m: Message):
    await m.answer("✅ Tasdiqlandi")


# Boshlangan
@dp.message(F.text.startswith("salom"))
async def salom_boshlangan(m: Message):
    await m.answer("Salom bilan boshlangan xabar 👋")


# ─────────────────────────────────────────────────────────────────────
# 3) Regex
# ─────────────────────────────────────────────────────────────────────

# Faqat son
@dp.message(F.text.regexp(r"^-?\\d+$"))
async def son(m: Message):
    n = int(m.text)
    await m.answer(f"Son: {n}\\nKvadrat: {n*n}\\nKub: {n*n*n}")


# Telefon raqami
@dp.message(F.text.regexp(r"^\\+998\\d{9}$"))
async def telefon(m: Message):
    await m.answer(f"📞 O'zbekiston telefoni: {m.text}")


# Email
@dp.message(F.text.regexp(r"^[\\w._-]+@[\\w.-]+\\.\\w+$"))
async def email(m: Message):
    await m.answer(f"📧 Email: {m.text}")


# ─────────────────────────────────────────────────────────────────────
# 4) Content turlar
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.sticker)
async def sticker(m: Message):
    await m.answer(f"😄 Sticker oldim! ID: <code>{m.sticker.file_id}</code>")


@dp.message(F.photo)
async def photo(m: Message):
    # m.photo — har xil o'lchamdagi versiyalar (eng katta — oxiri)
    photo = m.photo[-1]
    await m.answer(
        f"📷 Rasm oldim!\\n"
        f"Eni × bo'yi: {photo.width} × {photo.height}\\n"
        f"Hajmi: {photo.file_size} bayt"
    )


@dp.message(F.voice)
async def voice(m: Message):
    await m.answer(f"🎤 Voice: {m.voice.duration} soniya")


@dp.message(F.document)
async def document(m: Message):
    doc = m.document
    await m.answer(
        f"📄 Hujjat: <b>{doc.file_name}</b>\\n"
        f"Hajmi: {doc.file_size:,} bayt\\n"
        f"Tur: {doc.mime_type}"
    )


@dp.message(F.location)
async def location(m: Message):
    loc = m.location
    await m.answer(
        f"📍 Joylashuv:\\n"
        f"Latitude: <code>{loc.latitude}</code>\\n"
        f"Longitude: <code>{loc.longitude}</code>"
    )


@dp.message(F.contact)
async def contact(m: Message):
    c = m.contact
    await m.answer(
        f"📞 Kontakt:\\n"
        f"Ism: {c.first_name}\\n"
        f"Tel: {c.phone_number}"
    )


# ─────────────────────────────────────────────────────────────────────
# 5) Catch-all — ENG OXIRDA
# ─────────────────────────────────────────────────────────────────────

@dp.message()
async def catch_all(m: Message):
    await m.answer(
        f"🤔 Bunaqa xabarni qanday qaytarishni bilmayman.\\n"
        f"<i>/help</i> bosing yoki matn yozing."
    )


# ─────────────────────────────────────────────────────────────────────
# 6) Error handler
# ─────────────────────────────────────────────────────────────────────

@dp.error()
async def error_handler(event):
    logging.error(f"Exception: {event.exception}", exc_info=True)
    return True


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L3_TEXT = """\
<h2>Reply keyboard — tugmalar bilan menyu</h2>

<pre class="mermaid">
flowchart LR
    B["Bot xabari"] --> KB["Reply Keyboard"]
    KB -->|tugma matni| MSG["Oddiy Message kabi"]
    MSG --> H["Handler F.text == 'tugma'"]
</pre>

<p>Foydalanuvchi matn yozish o'rniga — <strong>tugma bosadi</strong>. Tugma — bu shunchaki matn jo'natadi (oddiy xabar kabi). Lekin chiroyli, oson va xatosiz.</p>

<p>Telegram'da 2 xil keyboard:</p>
<ul>
<li><strong>Reply keyboard</strong> — pastida (input o'rnida). Tugma bosish = matn yuborish.</li>
<li><strong>Inline keyboard</strong> — xabar ostida. Tugma bosish = callback (4-darsda).</li>
</ul>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi reply keyboard</h4>

<pre><code>from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

# Klaviatura yaratish
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="📦 Buyurtmalar")],
        [KeyboardButton(text="ℹ️ Yordam")],
    ],
    resize_keyboard=True,    # ekran bo'ylab moslashadi
)

@dp.message(CommandStart())
async def start(m: Message):
    await m.answer("Bosh menyu:", reply_markup=kb)


# Tugma bosilganda — oddiy matn handler
@dp.message(F.text == "👤 Profil")
async def profil(m: Message):
    await m.answer("Sizning profilingiz...")</code></pre>

<h4>BLOKA 2 — Builder (zamonaviy)</h4>

<pre><code>from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb = ReplyKeyboardBuilder()
kb.button(text="👤 Profil")
kb.button(text="📦 Buyurtmalar")
kb.button(text="ℹ️ Yordam")
kb.adjust(2, 1)    # birinchi qatorda 2, ikkinchida 1

await m.answer("Menyu:", reply_markup=kb.as_markup(resize_keyboard=True))</code></pre>

<h4>BLOKA 3 — Maxsus tugmalar</h4>

<pre><code># Kontakt so'rash
kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(
        text="📞 Telefon yuborish",
        request_contact=True
    )]],
    resize_keyboard=True,
    one_time_keyboard=True,    # bosgandan keyin yashirish
)

@dp.message(F.contact)
async def contact(m: Message):
    await m.answer(f"Rahmat! Tel: {m.contact.phone_number}")


# Joylashuv so'rash
kb_loc = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(
        text="📍 Joylashuv yuborish",
        request_location=True
    )]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

@dp.message(F.location)
async def location(m: Message):
    await m.answer(f"{m.location.latitude}, {m.location.longitude}")</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Tugma matnida emoji
KeyboardButton(text="👤 Profil")

# Lekin handler'da
@dp.message(F.text == "Profil")   # ❌ emoji yo'q
async def profil(m): ...</code></pre>

<p><strong>Natija:</strong> Tugma bosildi → bot "Profil" emas, balki "👤 Profil" yuboradi. Handler bilan mos kelmaydi → catch-all'ga ketadi.</p>

<p>To'g'risi: handler ham aniq matn bilan: <code>F.text == "👤 Profil"</code>. Yoki konstanta sifatida:</p>

<pre><code>BTN_PROFIL = "👤 Profil"
BTN_ORDERS = "📦 Buyurtmalar"

kb = ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton(text=BTN_PROFIL),
    KeyboardButton(text=BTN_ORDERS),
]])

@dp.message(F.text == BTN_PROFIL)
async def profil(m): ...</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. ReplyKeyboardMarkup parametrlari</h4>

<table>
<tr><th>Parametr</th><th>Vazifa</th></tr>
<tr><td><code>keyboard</code></td><td>2D ro'yxat: [[btn, btn], [btn]]</td></tr>
<tr><td><code>resize_keyboard</code></td><td>Ekran o'lchamiga moslash (har doim True)</td></tr>
<tr><td><code>one_time_keyboard</code></td><td>Bosgandan keyin yashirish</td></tr>
<tr><td><code>input_field_placeholder</code></td><td>Input maydonida ko'rinadigan matn</td></tr>
<tr><td><code>selective</code></td><td>Faqat ba'zi foydalanuvchilarga ko'rsatish</td></tr>
</table>

<h4>2. KeyboardButton turlar</h4>

<table>
<tr><th>Tur</th><th>Misol</th></tr>
<tr><td>Oddiy matn</td><td><code>KeyboardButton(text="Salom")</code></td></tr>
<tr><td>Kontakt so'rash</td><td><code>KeyboardButton(text="Tel", request_contact=True)</code></td></tr>
<tr><td>Joylashuv so'rash</td><td><code>KeyboardButton(text="Loc", request_location=True)</code></td></tr>
<tr><td>WebApp ochish</td><td><code>KeyboardButton(text="App", web_app=WebAppInfo(url="..."))</code></td></tr>
<tr><td>Bot tanlash</td><td><code>KeyboardButton(text="Bot", request_users=...)</code></td></tr>
</table>

<h4>3. ReplyKeyboardBuilder — zamonaviy</h4>

<pre><code>kb = ReplyKeyboardBuilder()

# Tugma qo'shish
kb.button(text="A")
kb.button(text="B")
kb.button(text="C")
kb.button(text="D")

# Qatorda nechtadan
kb.adjust(2, 2)   # 2 qator, har birida 2

# Yoki dinamik
kb.adjust(*[2] * 3)   # 6 tugma — 2 qatorda 2 ta

# Konvertatsiya
markup = kb.as_markup(
    resize_keyboard=True,
    input_field_placeholder="Tanlang...",
)</code></pre>

<h4>4. Keyboard'ni olib tashlash</h4>

<pre><code>from aiogram.types import ReplyKeyboardRemove

await m.answer(
    "Menyu yashirildi",
    reply_markup=ReplyKeyboardRemove()
)</code></pre>

<h4>5. Tipik patterns</h4>

<pre><code># Yes/No
kb = ReplyKeyboardBuilder()
kb.button(text="✅ Ha")
kb.button(text="❌ Yo'q")
kb.adjust(2)

# Asosiy menyu
kb = ReplyKeyboardBuilder()
kb.button(text="🛒 Buyurtma berish")
kb.button(text="📦 Mening buyurtmalarim")
kb.button(text="📞 Bog'lanish")
kb.button(text="ℹ️ Yordam")
kb.adjust(1)   # har biri alohida qatorda

# Bekor qilish + boshqalar
kb = ReplyKeyboardBuilder()
kb.button(text="✏️ Tahrirlash")
kb.button(text="🗑 O'chirish")
kb.button(text="❌ Bekor qilish")
kb.adjust(2, 1)</code></pre>

<h4>6. Konstantalar bilan tartib</h4>

<pre><code># constants/buttons.py
class MenuButtons:
    PROFIL = "👤 Profil"
    ORDERS = "📦 Buyurtmalar"
    HELP = "ℹ️ Yordam"

# handlers/menu.py
from constants.buttons import MenuButtons as MB

@dp.message(F.text == MB.PROFIL)
async def profil(m: Message): ...

@dp.message(F.text == MB.ORDERS)
async def orders(m: Message): ...</code></pre>

<p>Bu — production'da tavsiya. Tugma matnini bir joydan o'zgartirsangiz — barcha handler'lar avtomatik ishlaydi.</p>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Reply keyboard — pastdagi tugmalar</li>
<li>✅ <code>ReplyKeyboardMarkup</code> + <code>KeyboardButton</code></li>
<li>✅ <code>ReplyKeyboardBuilder</code> (zamonaviy)</li>
<li>✅ <code>adjust()</code> — qatorlarni belgilash</li>
<li>✅ Maxsus tugmalar: kontakt, joylashuv, WebApp</li>
<li>✅ <code>ReplyKeyboardRemove</code> — yashirish</li>
<li>✅ Tugma matni va handler filter aniq mos kelishi shart</li>
<li>✅ Konstantalar bilan tartib</li>
</ul>
"""

L3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 3: Reply keyboard'lar
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# Tugma konstantalari (kelajakda bir joydan o'zgartirish uchun)
# ─────────────────────────────────────────────────────────────────────

class BTN:
    PROFIL = "👤 Profil"
    ORDERS = "📦 Buyurtmalar"
    HELP = "ℹ️ Yordam"
    CONTACT = "📞 Telefon yuborish"
    LOCATION = "📍 Joylashuv yuborish"
    YES = "✅ Ha"
    NO = "❌ Yo'q"
    BACK = "⬅️ Orqaga"
    CANCEL = "❌ Bekor qilish"


# ─────────────────────────────────────────────────────────────────────
# Klaviatura yaratuvchi funksiyalar
# ─────────────────────────────────────────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    # Bosh menyu — eski uslub (oddiy ReplyKeyboardMarkup).
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN.PROFIL), KeyboardButton(text=BTN.ORDERS)],
            [KeyboardButton(text=BTN.HELP)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang...",
    )


def yes_no_kb() -> ReplyKeyboardMarkup:
    # Builder bilan.
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.YES)
    kb.button(text=BTN.NO)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def contact_kb() -> ReplyKeyboardMarkup:
    # Telefon raqamini so'rovchi.
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.CONTACT, request_contact=True)
    kb.button(text=BTN.CANCEL)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def location_kb() -> ReplyKeyboardMarkup:
    # Joylashuv so'rash.
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.LOCATION, request_location=True)
    kb.button(text=BTN.CANCEL)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def dynamic_grid(items: list[str], cols: int = 2) -> ReplyKeyboardMarkup:
    # Dinamik — N ustunli grid.
    kb = ReplyKeyboardBuilder()
    for it in items:
        kb.button(text=it)
    kb.adjust(cols)
    return kb.as_markup(resize_keyboard=True)


# ─────────────────────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>! 👋\\n"
        f"Bosh menyudan tanlang.",
        reply_markup=main_menu(),
    )


# ─────────────────────────────────────────────────────────────────────
# Menyu handler'lari (aniq matn)
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.text == BTN.PROFIL)
async def profil(m: Message):
    await m.answer(
        f"👤 <b>Sizning profilingiz</b>\\n\\n"
        f"Ism: {m.from_user.first_name}\\n"
        f"Username: @{m.from_user.username or '—'}\\n"
        f"ID: <code>{m.from_user.id}</code>\\n\\n"
        f"Telefon raqamingizni yuborasizmi?",
        reply_markup=contact_kb(),
    )


@dp.message(F.text == BTN.ORDERS)
async def orders(m: Message):
    # Demo — dinamik tugmalar
    mahsulotlar = ["🍕 Pizza", "🍔 Burger", "🌮 Taco", "🍜 Lag'mon", "🥗 Salat"]
    await m.answer(
        "📦 Sizning buyurtmalaringiz:\\n(hozirgi misol)",
        reply_markup=dynamic_grid(mahsulotlar, cols=2),
    )


@dp.message(F.text == BTN.HELP)
async def help_btn(m: Message):
    await m.answer(
        "ℹ️ <b>Yordam</b>\\n\\n"
        "• 👤 Profil — sizning ma'lumotlaringiz\\n"
        "• 📦 Buyurtmalar — xarid tarixi\\n"
        "• ℹ️ Yordam — bu xabar\\n\\n"
        "Bekor qilish uchun: /cancel",
    )


# ─────────────────────────────────────────────────────────────────────
# Kontakt va joylashuv
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.contact)
async def get_contact(m: Message):
    c = m.contact
    await m.answer(
        f"✅ Rahmat!\\n"
        f"Telefon: <b>{c.phone_number}</b>\\n"
        f"Saqlandi.",
        reply_markup=main_menu(),
    )


@dp.message(F.location)
async def get_location(m: Message):
    loc = m.location
    await m.answer(
        f"📍 Joylashuv qabul qilindi:\\n"
        f"Lat: <code>{loc.latitude}</code>\\n"
        f"Lon: <code>{loc.longitude}</code>",
        reply_markup=main_menu(),
    )


# ─────────────────────────────────────────────────────────────────────
# Bekor qilish — har joydan
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.text.in_({BTN.CANCEL, BTN.BACK}) | Command("cancel"))
async def cancel(m: Message):
    await m.answer(
        "🔙 Bosh menyuga qaytdingiz",
        reply_markup=main_menu(),
    )


@dp.message(Command("hide"))
async def hide(m: Message):
    await m.answer(
        "Klaviatura yashirildi",
        reply_markup=ReplyKeyboardRemove(),
    )


# ─────────────────────────────────────────────────────────────────────
# Catch-all
# ─────────────────────────────────────────────────────────────────────

@dp.message()
async def catch_all(m: Message):
    await m.answer(
        "🤔 Menyudan tanlang yoki /help bosing.",
        reply_markup=main_menu(),
    )


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
R1_TEXT = """\
<h2>R1 — Modul 1 takrorlash: Echo bot + 3-darajali menyu</h2>

<p>Modul 1 ning hamma narsasi birga: setup + handlers + filter'lar + reply keyboard'lar. Real bot tuzilmasi — kategoriyalar, sub-menyular, orqaga qaytish, kontent.</p>

<h3>Loyihaning maqsadi</h3>

<p>3 darajali menyuga ega bot:</p>

<pre><code>Bosh menyu
├── 🍕 Taomlar
│   ├── 🍕 Pizza
│   ├── 🍔 Burger
│   ├── 🌮 Taco
│   └── ⬅️ Orqaga
├── 🥤 Ichimliklar
│   ├── ☕ Choy
│   ├── 🥃 Kofe
│   ├── 🧃 Sok
│   └── ⬅️ Orqaga
├── 📞 Bog'lanish
└── ℹ️ Bot haqida</code></pre>

<p>Plus — echo handler (catch-all), state-siz simulyatsiya (4-darsda real state).</p>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — Loyiha sozlash</h4>
<ul>
<li>Yangi virtual env + aiogram + dotenv</li>
<li>BotFather'da bot (yangi yoki avvalgi)</li>
<li>.env + .gitignore</li>
<li>bot.py + handlers/ papkasi (Router bilan)</li>
</ul>

<h4>Vazifa 2 — Bosh menyu</h4>
<ul>
<li><code>main_menu()</code> klaviaturasi: 4 ta tugma</li>
<li><code>/start</code> da ko'rsatish</li>
<li>Welcome xabari user nomi bilan</li>
</ul>

<h4>Vazifa 3 — 2-daraja menyular</h4>
<ul>
<li><code>food_menu()</code> — Pizza, Burger, Taco + ⬅️ Orqaga</li>
<li><code>drink_menu()</code> — Choy, Kofe, Sok + ⬅️ Orqaga</li>
<li>"🍕 Taomlar" → food_menu chiqsin</li>
<li>"🥤 Ichimliklar" → drink_menu</li>
</ul>

<h4>Vazifa 4 — 3-daraja (kontent)</h4>
<ul>
<li>Har taom/ichimlik nomi bosilganda — batafsil ma'lumot (rasm, narx, tavsif)</li>
<li>Avval rasm bilan jo'natish (<code>answer_photo</code>)</li>
<li>Orqaga tugmasi food_menu yoki drink_menu'ga qaytarsin</li>
</ul>

<h4>Vazifa 5 — Bog'lanish va Bot haqida</h4>
<ul>
<li>"📞 Bog'lanish" → telefon raqami + manzil + ish vaqti</li>
<li>"ℹ️ Bot haqida" → bot versiyasi, kim yaratganini</li>
</ul>

<h4>Vazifa 6 — Catch-all</h4>
<ul>
<li>Tugma bilan bog'lanmagan xabarlarni echo qilish</li>
<li>"📝 Echo: matn" ko'rinishida</li>
</ul>

<h4>Vazifa 7 — UX</h4>
<ul>
<li>Har xabar — HTML format'da chiroyli (b, i, code, emoji)</li>
<li>Har menyuga emoji</li>
<li>Welcome xabar uzun, lekin chiroyli</li>
</ul>

<h3>🐛 Ataylab qiyin: state-siz menyu</h3>

<p>Hozircha foydalanuvchi qaerda turganini bilmaymiz (FSM — 5-darsda). Lekin oddiy yo'l: <strong>har submenyu o'z tugmalari bilan farqlanadi</strong>, va orqaga tugmasi bosh menyuga qaytaradi. Ko'p loyihalar shu pattern bilan ishlaydi.</p>

<h3>Yechim sketch</h3>

<details>
<summary>To'liq yechim — avval o'zingiz urinib ko'ring!</summary>
<pre><code># keyboards.py
from aiogram.utils.keyboard import ReplyKeyboardBuilder

class BTN:
    # Bosh menyu
    FOOD = "🍕 Taomlar"
    DRINK = "🥤 Ichimliklar"
    CONTACT = "📞 Bog'lanish"
    ABOUT = "ℹ️ Bot haqida"
    # Orqaga
    BACK = "⬅️ Orqaga"
    # Taomlar
    PIZZA = "🍕 Pizza"
    BURGER = "🍔 Burger"
    TACO = "🌮 Taco"
    # Ichimliklar
    TEA = "☕ Choy"
    COFFEE = "🥃 Kofe"
    JUICE = "🧃 Sok"

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.FOOD)
    kb.button(text=BTN.DRINK)
    kb.button(text=BTN.CONTACT)
    kb.button(text=BTN.ABOUT)
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)

def food_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.PIZZA)
    kb.button(text=BTN.BURGER)
    kb.button(text=BTN.TACO)
    kb.button(text=BTN.BACK)
    kb.adjust(3, 1)
    return kb.as_markup(resize_keyboard=True)

# handlers.py
@dp.message(F.text == BTN.FOOD)
async def food(m: Message):
    await m.answer("🍕 Taom tanlang:", reply_markup=food_menu())

@dp.message(F.text == BTN.PIZZA)
async def pizza(m: Message):
    await m.answer(
        "🍕 <b>Pizza Margherita</b>\\n\\n"
        "Italyan klassikasi: pomidor, mozzarella, basilik.\\n"
        "Narx: <b>45,000 so'm</b>",
        reply_markup=food_menu(),
    )

@dp.message(F.text == BTN.BACK)
async def back(m: Message):
    await m.answer("🏠 Bosh menyu:", reply_markup=main_menu())</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 1 ning hammasi birga real loyihada</li>
<li>✅ Multi-level menyu (3 daraja)</li>
<li>✅ Klaviatura uchun konstantalar pattern</li>
<li>✅ Orqaga qaytish UX</li>
<li>✅ HTML format'lash bilan chiroyli content</li>
<li>✅ Router'lar bilan kod organizatsiyasi (ixtiyoriy)</li>
</ul>
"""

R1_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 1: Echo bot + 3-darajali menyu
# Modul 1: setup + handlers + filter + reply keyboards
# ════════════════════════════════════════════════════════════════════

# bot.py
import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    URLInputFile,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# Konstantalar
# ─────────────────────────────────────────────────────────────────────

class BTN:
    # Bosh menyu
    FOOD = "🍕 Taomlar"
    DRINK = "🥤 Ichimliklar"
    CONTACT = "📞 Bog'lanish"
    ABOUT = "ℹ️ Bot haqida"
    # Orqaga
    BACK = "⬅️ Orqaga"
    # Taomlar
    PIZZA = "🍕 Pizza"
    BURGER = "🍔 Burger"
    TACO = "🌮 Taco"
    LAGMON = "🍜 Lag'mon"
    # Ichimliklar
    TEA = "☕ Choy"
    COFFEE = "🥃 Kofe"
    JUICE = "🧃 Sok"


# ─────────────────────────────────────────────────────────────────────
# Klaviaturalar
# ─────────────────────────────────────────────────────────────────────

def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.FOOD)
    kb.button(text=BTN.DRINK)
    kb.button(text=BTN.CONTACT)
    kb.button(text=BTN.ABOUT)
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Menyudan tanlang...")


def food_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.PIZZA)
    kb.button(text=BTN.BURGER)
    kb.button(text=BTN.TACO)
    kb.button(text=BTN.LAGMON)
    kb.button(text=BTN.BACK)
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def drink_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN.TEA)
    kb.button(text=BTN.COFFEE)
    kb.button(text=BTN.JUICE)
    kb.button(text=BTN.BACK)
    kb.adjust(3, 1)
    return kb.as_markup(resize_keyboard=True)


# ─────────────────────────────────────────────────────────────────────
# Mahsulot ma'lumotlari
# ─────────────────────────────────────────────────────────────────────

PRODUCTS = {
    BTN.PIZZA: {
        "narx": 45000,
        "tavsif": "Italyan klassikasi: pomidor, mozzarella, basilik",
        "photo": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600",
    },
    BTN.BURGER: {
        "narx": 35000,
        "tavsif": "Mol go'shti, salat, pomidor, maxsus sous",
        "photo": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600",
    },
    BTN.TACO: {
        "narx": 25000,
        "tavsif": "Meksika ovqati: tortilla + go'sht + salat",
        "photo": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=600",
    },
    BTN.LAGMON: {
        "narx": 28000,
        "tavsif": "Markaziy Osiyo klassikasi: ko'k makaron, go'sht, sabzi",
        "photo": "https://images.unsplash.com/photo-1543353071-873f17a7a088?w=600",
    },
    BTN.TEA: {
        "narx": 5000,
        "tavsif": "Yashil yoki qora choy. O'zbek dasturxoni qadrigi",
    },
    BTN.COFFEE: {
        "narx": 18000,
        "tavsif": "Espresso, Americano, Latte yoki Cappuccino",
    },
    BTN.JUICE: {
        "narx": 12000,
        "tavsif": "Yangi siqilgan: olma, apelsin yoki anor",
    },
}


# ─────────────────────────────────────────────────────────────────────
# Handler'lar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"🎉 Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"<b>Restoran Botiga xush kelibsiz!</b>\\n\\n"
        f"Bizning menyumiz orqali tanishishingiz, "
        f"narxlarni ko'rishingiz va bog'lanishingiz mumkin.\\n\\n"
        f"👇 Menyudan tanlang:",
        reply_markup=main_menu(),
    )


# ─────────── Bosh menyu kirishlari ───────────

@dp.message(F.text == BTN.FOOD)
async def food_category(m: Message):
    await m.answer("🍕 <b>Taomlar</b>\\n\\nNimani tatib ko'rmoqchisiz?", reply_markup=food_menu())


@dp.message(F.text == BTN.DRINK)
async def drink_category(m: Message):
    await m.answer("🥤 <b>Ichimliklar</b>\\n\\nQaysi birini xohlaysiz?", reply_markup=drink_menu())


@dp.message(F.text == BTN.CONTACT)
async def contact(m: Message):
    await m.answer(
        "📞 <b>Bog'lanish</b>\\n\\n"
        "Telefon: <code>+998 71 200 00 00</code>\\n"
        "Manzil: Toshkent, Amir Temur ko'chasi 1\\n"
        "Ish vaqti: <b>10:00 — 23:00</b>, dam olish kunisiz\\n\\n"
        "🚗 Yetkazib berish: bepul (Toshkent ichida)\\n"
        "💳 To'lov: naqd, Click, Payme",
        reply_markup=main_menu(),
    )


@dp.message(F.text == BTN.ABOUT)
async def about(m: Message):
    await m.answer(
        "ℹ️ <b>Bot haqida</b>\\n\\n"
        "Bu — aiogram kursi talabasi tomonidan ishlab chiqilgan demo bot.\\n\\n"
        "Texnologiyalar:\\n"
        "• Python 3.12\\n"
        "• aiogram 3.x\\n"
        "• ⚡ async/await\\n\\n"
        "GitHub: github.com/olim/restoran-bot",
        reply_markup=main_menu(),
    )


# ─────────── Mahsulot tafsiloti (3-daraja) ───────────

@dp.message(F.text.in_({BTN.PIZZA, BTN.BURGER, BTN.TACO, BTN.LAGMON}))
async def show_food(m: Message):
    product = PRODUCTS.get(m.text)
    if not product:
        return

    caption = (
        f"{m.text}\\n\\n"
        f"{product['tavsif']}\\n\\n"
        f"💰 Narx: <b>{product['narx']:,} so'm</b>"
    )

    if photo := product.get("photo"):
        await m.answer_photo(
            URLInputFile(photo),
            caption=caption,
            reply_markup=food_menu(),
        )
    else:
        await m.answer(caption, reply_markup=food_menu())


@dp.message(F.text.in_({BTN.TEA, BTN.COFFEE, BTN.JUICE}))
async def show_drink(m: Message):
    product = PRODUCTS.get(m.text)
    if not product:
        return
    await m.answer(
        f"{m.text}\\n\\n"
        f"{product['tavsif']}\\n\\n"
        f"💰 Narx: <b>{product['narx']:,} so'm</b>",
        reply_markup=drink_menu(),
    )


# ─────────── Orqaga ───────────

@dp.message(F.text == BTN.BACK)
async def back_to_main(m: Message):
    await m.answer("🏠 Bosh menyu", reply_markup=main_menu())


# ─────────── Echo (catch-all) ───────────

@dp.message()
async def echo(m: Message):
    if m.text:
        await m.answer(
            f"📝 <b>Echo:</b> <i>{m.text}</i>\\n\\n"
            f"<i>Menyudan tanlang yoki /start bosing.</i>",
            reply_markup=main_menu(),
        )
    else:
        await m.answer(
            "❓ Faqat matn yoki menyu tugmalari.",
            reply_markup=main_menu(),
        )


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L4_TEXT = """\
<h2>Inline keyboard va callback_data</h2>

<pre class="mermaid">
flowchart LR
    B["Bot xabari + inline tugmalar"] --> U["Foydalanuvchi tugma bosadi"]
    U -->|callback_data| H["@dp.callback_query handler"]
    H -->|edit_text yoki answer| B2["Xabar yangilanadi"]
</pre>

<p>Reply keyboard'lar — pastda, oddiy matn yuboradi. <strong>Inline keyboard</strong> — xabar ostida, va tugma bosilganda <em>maxsus</em> callback yuboradi. Bu juda kuchli — siz xabarni o'zgartirishingiz mumkin (chap'siz va e'tibordan tashqari), tasdiqlovchi popup ko'rsatasiz, navigatsiya qilasiz.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — birinchi inline keyboard</h4>

<pre><code>from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="👍 Yaxshi", callback_data="like"),
        InlineKeyboardButton(text="👎 Yomon", callback_data="dislike"),
    ],
])

@dp.message(Command("rate"))
async def rate(m: Message):
    await m.answer("Bot qanday?", reply_markup=kb)


@dp.callback_query(F.data == "like")
async def like(call: CallbackQuery):
    await call.answer("Rahmat! 😊", show_alert=False)
    await call.message.edit_text("✅ Sizga yoqdi")


@dp.callback_query(F.data == "dislike")
async def dislike(call: CallbackQuery):
    await call.answer("Afsuski 😢", show_alert=True)
    await call.message.edit_text("👎 Yaxshilaymiz")</code></pre>

<h4>BLOKA 2 — InlineKeyboardBuilder</h4>

<pre><code>from aiogram.utils.keyboard import InlineKeyboardBuilder

kb = InlineKeyboardBuilder()
kb.button(text="🟢 1", callback_data="num:1")
kb.button(text="🟢 2", callback_data="num:2")
kb.button(text="🟢 3", callback_data="num:3")
kb.button(text="🟢 4", callback_data="num:4")
kb.button(text="🟢 5", callback_data="num:5")
kb.adjust(5)   # 5 ta bir qatorda

await m.answer("Baho bering:", reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("num:"))
async def rate_num(call: CallbackQuery):
    num = call.data.split(":")[1]
    await call.answer(f"Sizning bahoyingiz: {num}/5")
    await call.message.edit_text(f"✅ Baho: {'⭐' * int(num)}")</code></pre>

<h4>BLOKA 3 — CallbackData (zamonaviy)</h4>

<pre><code>from aiogram.filters.callback_data import CallbackData

class OrderCb(CallbackData, prefix="order"):
    action: str       # "view", "delete", "confirm"
    order_id: int

# Tugma yaratish
kb = InlineKeyboardBuilder()
kb.button(text="👁 Ko'rish", callback_data=OrderCb(action="view", order_id=42).pack())
kb.button(text="🗑 O'chirish", callback_data=OrderCb(action="delete", order_id=42).pack())

# Handler
@dp.callback_query(OrderCb.filter(F.action == "view"))
async def view_order(call: CallbackQuery, callback_data: OrderCb):
    await call.answer(f"Buyurtma #{callback_data.order_id}")
    # ... ma'lumotni ko'rsatish</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>@dp.callback_query(F.data == "like")
async def like(call: CallbackQuery):
    await call.message.edit_text("Rahmat!")
    # call.answer() unutilgan!</code></pre>

<p><strong>Natija:</strong> Telegram'da tugma "loading" holatda qoladi 30 soniya. Bot ishlamayotgandek tuyuladi.</p>

<p><strong>Sabab:</strong> Har callback uchun <code>call.answer()</code> chaqirish shart — Telegram'ga "qabul qildim" deb javob beradi. Aks holda — bot xato deb hisoblanadi.</p>

<pre><code>@dp.callback_query(F.data == "like")
async def like(call: CallbackQuery):
    await call.answer("Rahmat!")    # ✅ avval bu
    await call.message.edit_text("✅ Yaxshi")</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Reply vs Inline — to'liq taqqoslash</h4>

<table>
<tr><th></th><th>Reply</th><th>Inline</th></tr>
<tr><td>Joy</td><td>Input maydonida</td><td>Xabar ostida</td></tr>
<tr><td>Bosish natijasi</td><td>Matn yuboriladi</td><td>callback_data yuboriladi</td></tr>
<tr><td>Xabar tarixiga</td><td>Qoladi (qaytarilgan matn)</td><td>Bilinmaydi</td></tr>
<tr><td>URL/Web App</td><td>Faqat WebApp</td><td>URL, Web App, Switch, Pay</td></tr>
<tr><td>Xabar tahriri</td><td>Yo'q</td><td>Ha (edit_text/edit_markup)</td></tr>
<tr><td>Qachon</td><td>Asosiy menyu</td><td>Tasdiqlash, navigatsiya, like/dislike</td></tr>
</table>

<h4>2. InlineKeyboardButton turlar</h4>

<table>
<tr><th>Turi</th><th>Misol</th></tr>
<tr><td>callback_data</td><td><code>callback_data="like"</code> — bot qabul qiladi</td></tr>
<tr><td>url</td><td><code>url="https://google.com"</code> — link ochadi</td></tr>
<tr><td>web_app</td><td><code>web_app=WebAppInfo(url=...)</code> — Mini App</td></tr>
<tr><td>switch_inline_query</td><td>Boshqa chat'ga inline mode bilan o'tish</td></tr>
<tr><td>pay</td><td>To'lov tugmasi (BotFather'da yoqilgan bo'lishi kerak)</td></tr>
</table>

<h4>3. callback_data cheklovlari</h4>

<ul>
<li>Maksimum <strong>64 bayt</strong>!</li>
<li>Faqat string</li>
<li>Tuzilmali ma'lumot uchun ":" ajratuvchi yoki <code>CallbackData</code> klassi</li>
</ul>

<h4>4. CallbackData klassi (production)</h4>

<pre><code>from aiogram.filters.callback_data import CallbackData

class PaginateCb(CallbackData, prefix="page"):
    page: int
    category: str

# Tugma
btn = InlineKeyboardButton(
    text="➡️ Keyingi",
    callback_data=PaginateCb(page=2, category="food").pack(),
)
# Pack: "page:2:food"

# Handler
@dp.callback_query(PaginateCb.filter())
async def paginate(call: CallbackQuery, callback_data: PaginateCb):
    await call.answer()
    page = callback_data.page
    cat = callback_data.category
    # ...</code></pre>

<h4>5. Xabar va markup tahrirlash</h4>

<pre><code># Faqat matn
await call.message.edit_text("Yangi matn")

# Faqat tugmalar
await call.message.edit_reply_markup(reply_markup=yangi_kb)

# Caption (rasm bilan)
await call.message.edit_caption(caption="Yangi caption")

# Hammasini olib tashlash
await call.message.edit_reply_markup(reply_markup=None)

# Xabarni o'chirish
await call.message.delete()</code></pre>

<h4>6. answer turlari</h4>

<pre><code># Oddiy — toast (yuqorida 1-2 soniya)
await call.answer("Saqlandi")

# Alert — modal, foydalanuvchi OK bosishi kerak
await call.answer("Diqqat! Bu amal qaytarilmaydi.", show_alert=True)

# Bo'sh (faqat loading'ni to'xtatish)
await call.answer()

# URL bilan
await call.answer(url="https://example.com")
</code></pre>

<h4>7. Pagination misoli</h4>

<pre><code>def build_pagination(page: int, total_pages: int) -&gt; InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if page &gt; 1:
        kb.button(text="⬅️", callback_data=f"page:{page-1}")
    kb.button(text=f"{page}/{total_pages}", callback_data="noop")
    if page &lt; total_pages:
        kb.button(text="➡️", callback_data=f"page:{page+1}")
    return kb.as_markup()


@dp.callback_query(F.data.startswith("page:"))
async def paginate(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    text = f"Sahifa {page}\\n\\n..."
    await call.message.edit_text(text, reply_markup=build_pagination(page, 10))
    await call.answer()

@dp.callback_query(F.data == "noop")
async def noop(call: CallbackQuery):
    await call.answer()</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Inline keyboard — xabar ostida, callback yuboradi</li>
<li>✅ <code>@dp.callback_query</code> + <code>F.data == "..."</code></li>
<li>✅ <strong>Doim <code>call.answer()</code> qiling</strong></li>
<li>✅ <code>edit_text</code>, <code>edit_reply_markup</code></li>
<li>✅ <code>CallbackData</code> klassi — strukturali</li>
<li>✅ Pagination pattern</li>
<li>✅ 64 bayt cheklov — uzun data uchun klassik yoki DB ID</li>
</ul>
"""

L4_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 4: Inline keyboard va callback_data
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# 1) Eng oddiy — like/dislike
# ─────────────────────────────────────────────────────────────────────

def like_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👍 Yaxshi", callback_data="rate:like")
    kb.button(text="👎 Yomon", callback_data="rate:dislike")
    kb.adjust(2)
    return kb.as_markup()


@dp.message(Command("rate"))
async def cmd_rate(m: Message):
    await m.answer("Bot qanday?", reply_markup=like_kb())


@dp.callback_query(F.data == "rate:like")
async def cb_like(call: CallbackQuery):
    await call.answer("Rahmat! 😊")
    await call.message.edit_text("✅ Sizga yoqdi! Bizga juda muhim.")


@dp.callback_query(F.data == "rate:dislike")
async def cb_dislike(call: CallbackQuery):
    await call.answer("Afsuski 😢", show_alert=True)
    await call.message.edit_text("👎 Sabablarini izoh qilib yozsangiz, yaxshilaymiz.")


# ─────────────────────────────────────────────────────────────────────
# 2) 5 baholi — pattern data
# ─────────────────────────────────────────────────────────────────────

def stars_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in range(1, 6):
        kb.button(text=f"{i} ⭐", callback_data=f"star:{i}")
    kb.adjust(5)
    return kb.as_markup()


@dp.message(Command("stars"))
async def cmd_stars(m: Message):
    await m.answer("Bahoni tanlang:", reply_markup=stars_kb())


@dp.callback_query(F.data.startswith("star:"))
async def cb_stars(call: CallbackQuery):
    n = int(call.data.split(":")[1])
    await call.answer(f"Tanlandi: {n}/5", show_alert=False)
    await call.message.edit_text(
        f"✅ Sizning bahoyingiz: {'⭐' * n}{'☆' * (5-n)} ({n}/5)",
    )


# ─────────────────────────────────────────────────────────────────────
# 3) CallbackData klassi — production approach
# ─────────────────────────────────────────────────────────────────────

class OrderCb(CallbackData, prefix="order"):
    action: str       # "view", "delete", "confirm"
    order_id: int


def order_actions_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="👁 Ko'rish",
        callback_data=OrderCb(action="view", order_id=order_id).pack(),
    )
    kb.button(
        text="✏️ Tahrir",
        callback_data=OrderCb(action="edit", order_id=order_id).pack(),
    )
    kb.button(
        text="🗑 O'chirish",
        callback_data=OrderCb(action="delete", order_id=order_id).pack(),
    )
    kb.adjust(3)
    return kb.as_markup()


@dp.message(Command("orders"))
async def cmd_orders(m: Message):
    # Demo — 3 ta buyurtma
    for order_id in [42, 43, 44]:
        await m.answer(
            f"🧾 Buyurtma #<b>{order_id}</b>\\n"
            f"Status: <i>tasdiqlangan</i>\\n"
            f"Summa: 150,000 so'm",
            reply_markup=order_actions_kb(order_id),
        )


@dp.callback_query(OrderCb.filter(F.action == "view"))
async def cb_view_order(call: CallbackQuery, callback_data: OrderCb):
    await call.answer()
    await call.message.edit_text(
        f"👁 <b>Buyurtma #{callback_data.order_id}</b>\\n\\n"
        f"Mahsulotlar:\\n"
        f"• Pizza Margherita — 1 dona\\n"
        f"• Cola — 2 dona\\n\\n"
        f"Jami: <b>150,000 so'm</b>",
    )


@dp.callback_query(OrderCb.filter(F.action == "delete"))
async def cb_delete_order(call: CallbackQuery, callback_data: OrderCb):
    # Tasdiqlovchi tugmalar
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ Ha, o'chir",
        callback_data=f"confirm_del:{callback_data.order_id}",
    )
    kb.button(
        text="❌ Bekor",
        callback_data=f"cancel_del:{callback_data.order_id}",
    )
    kb.adjust(2)
    await call.message.edit_text(
        f"⚠️ Buyurtma #{callback_data.order_id} ni o'chirasizmi?",
        reply_markup=kb.as_markup(),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("confirm_del:"))
async def cb_confirm_del(call: CallbackQuery):
    order_id = call.data.split(":")[1]
    await call.answer("O'chirildi", show_alert=True)
    await call.message.edit_text(f"🗑 Buyurtma #{order_id} o'chirildi.")


@dp.callback_query(F.data.startswith("cancel_del:"))
async def cb_cancel_del(call: CallbackQuery):
    await call.answer("Bekor qilindi")
    order_id = int(call.data.split(":")[1])
    await call.message.edit_text(
        f"🧾 Buyurtma #<b>{order_id}</b>\\n"
        f"Status: <i>tasdiqlangan</i>",
        reply_markup=order_actions_kb(order_id),
    )


# ─────────────────────────────────────────────────────────────────────
# 4) Pagination
# ─────────────────────────────────────────────────────────────────────

ITEMS = [f"Item #{i}" for i in range(1, 51)]   # 50 ta
PER_PAGE = 5


def page_kb(page: int) -> InlineKeyboardMarkup:
    total = (len(ITEMS) + PER_PAGE - 1) // PER_PAGE
    kb = InlineKeyboardBuilder()
    if page > 1:
        kb.button(text="⬅️", callback_data=f"pg:{page-1}")
    kb.button(text=f"{page}/{total}", callback_data="noop")
    if page < total:
        kb.button(text="➡️", callback_data=f"pg:{page+1}")
    return kb.as_markup()


def page_text(page: int) -> str:
    start = (page - 1) * PER_PAGE
    items = ITEMS[start:start + PER_PAGE]
    lines = "\\n".join(f"• {it}" for it in items)
    return f"📋 <b>Sahifa {page}</b>\\n\\n{lines}"


@dp.message(Command("list"))
async def cmd_list(m: Message):
    await m.answer(page_text(1), reply_markup=page_kb(1))


@dp.callback_query(F.data.startswith("pg:"))
async def cb_page(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    await call.message.edit_text(page_text(page), reply_markup=page_kb(page))
    await call.answer()


@dp.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


# ─────────────────────────────────────────────────────────────────────
# 5) URL tugmasi
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("link"))
async def cmd_link(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Bizning sayt", url="https://example.uz")],
        [InlineKeyboardButton(text="📺 YouTube", url="https://youtube.com")],
        [InlineKeyboardButton(text="🐦 Twitter", url="https://twitter.com")],
    ])
    await m.answer("Bizning ijtimoiy tarmoqlar:", reply_markup=kb)


# ─────────────────────────────────────────────────────────────────────
# 6) Ataylab xato — answer'siz handler
# ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "broken")
async def cb_broken(call: CallbackQuery):
    # ❌ call.answer() YO'Q — tugma loading'da qotadi
    await call.message.edit_text("Bu xatolik...")


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L5_TEXT = """\
<h2>FSM — Finite State Machine: multi-step formalar</h2>

<pre class="mermaid">
flowchart LR
    START["/register"] -->|set_state| S1["waiting_for_ism"]
    S1 -->|matn keldi| S2["waiting_for_yosh"]
    S2 -->|matn keldi| S3["waiting_for_telefon"]
    S3 -->|kontakt keldi| DONE["✅ saqlash + clear()"]
</pre>

<p>Ko'p real bot vazifalari — <strong>bir nechta bosqichli</strong>: ro'yxatdan o'tish (ism → email → parol), buyurtma berish (mahsulot → manzil → to'lov), feedback (mavzu → matn → fayl). Har bosqich uchun alohida handler kerak, va bot foydalanuvchining qaerda turganini <em>eslab qolishi</em> kerak.</p>

<p>Bu — <strong>FSM (Finite State Machine)</strong>. aiogram'da built-in.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — State'lar e'lon qilish</h4>

<pre><code>from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class RegisterStates(StatesGroup):
    ism = State()
    yosh = State()
    telefon = State()</code></pre>

<h4>BLOKA 2 — Bosqichli registratsiya</h4>

<pre><code># Bosqich 1: /register → ism so'rash
@dp.message(Command("register"))
async def register_start(m: Message, state: FSMContext):
    await m.answer("Ismingizni kiriting:")
    await state.set_state(RegisterStates.ism)


# Bosqich 2: ism qabul → yosh so'rash
@dp.message(RegisterStates.ism)
async def get_ism(m: Message, state: FSMContext):
    await state.update_data(ism=m.text)
    await m.answer("Yoshingizni kiriting:")
    await state.set_state(RegisterStates.yosh)


# Bosqich 3: yosh qabul → telefon so'rash
@dp.message(RegisterStates.yosh)
async def get_yosh(m: Message, state: FSMContext):
    if not m.text.isdigit():
        await m.answer("Yosh — son bo'lishi kerak. Qaytadan:")
        return
    await state.update_data(yosh=int(m.text))
    await m.answer("Telefonni kiriting:")
    await state.set_state(RegisterStates.telefon)


# Bosqich 4: telefon qabul → saqlash + clear
@dp.message(RegisterStates.telefon)
async def get_telefon(m: Message, state: FSMContext):
    data = await state.get_data()
    data["telefon"] = m.text

    # ... DB'ga saqlash ...

    await m.answer(
        f"✅ Saqlandi!\\n"
        f"Ism: {data['ism']}\\n"
        f"Yosh: {data['yosh']}\\n"
        f"Tel: {data['telefon']}"
    )
    await state.clear()</code></pre>

<h4>BLOKA 3 — Bekor qilish har bosqichda</h4>

<pre><code>@dp.message(Command("cancel"), StateFilter("*"))
async def cancel(m: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await m.answer("Hech narsa bekor qilinmaydi.")
        return
    await state.clear()
    await m.answer("❌ Bekor qilindi.")</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Storage e'lon qilinmagan
dp = Dispatcher()

# State ishlatamiz
@dp.message(RegisterStates.ism)
async def get_ism(m: Message, state: FSMContext):
    ...</code></pre>

<p><strong>Sabab:</strong> Default'da aiogram <code>MemoryStorage</code> ishlatadi (process'da). Bot restart bo'lsa — har bir foydalanuvchining state'i yo'qoladi. Production'da — Redis ishlatish kerak.</p>

<pre><code>from aiogram.fsm.storage.redis import RedisStorage

storage = RedisStorage.from_url("redis://localhost:6379/0")
dp = Dispatcher(storage=storage)</code></pre>

<p>Development uchun MemoryStorage yetadi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. FSM Storage turlari</h4>

<table>
<tr><th>Storage</th><th>Qachon</th></tr>
<tr><td>MemoryStorage</td><td>Dev — restart bo'lsa state'lar yo'qoladi</td></tr>
<tr><td>RedisStorage</td><td>Production — tez, ko'p bot uchun</td></tr>
<tr><td>MongoStorage</td><td>Production — boshqa storage'lar uchun</td></tr>
</table>

<pre><code># Memory (default — Dispatcher() yetadi)
from aiogram.fsm.storage.memory import MemoryStorage
dp = Dispatcher(storage=MemoryStorage())

# Redis
from aiogram.fsm.storage.redis import RedisStorage
storage = RedisStorage.from_url("redis://localhost:6379/0")
dp = Dispatcher(storage=storage)</code></pre>

<h4>2. StatesGroup tuzilishi</h4>

<pre><code>class OrderStates(StatesGroup):
    choose_product = State()
    choose_quantity = State()
    enter_address = State()
    confirm = State()

# Ishlatilishi
await state.set_state(OrderStates.choose_product)
await state.set_state(OrderStates.confirm)</code></pre>

<h4>3. State'da ma'lumot saqlash</h4>

<pre><code># Yangi qiymat qo'shish (eski'lar saqlanadi)
await state.update_data(ism="Olim", yosh=25)

# Olish
data = await state.get_data()
print(data["ism"])

# To'liq tozalash (state ham, data ham)
await state.clear()

# Faqat data — state qoladi
await state.set_data({})</code></pre>

<h4>4. State filter'lari</h4>

<pre><code># Aniq state
@dp.message(RegisterStates.ism)
async def ...

# Har qanday state
from aiogram.filters import StateFilter
@dp.message(StateFilter("*"))
async def ...

# Bir nechta state
@dp.message(StateFilter(RegisterStates.ism, RegisterStates.yosh))
async def ...

# State yo'q
@dp.message(StateFilter(None))
async def no_state(m): ...</code></pre>

<h4>5. Validatsiya — agar xato bo'lsa qaytarish</h4>

<pre><code>@dp.message(RegisterStates.yosh)
async def get_yosh(m: Message, state: FSMContext):
    # Validatsiya
    if not m.text or not m.text.isdigit():
        await m.answer("❌ Yosh — son bo'lishi kerak. Qaytadan kiriting:")
        return    # state o'zgarmaydi, foydalanuvchi qaytadan urinadi

    yosh = int(m.text)
    if yosh &lt; 14 or yosh &gt; 120:
        await m.answer("❌ Yosh 14-120 oraliqda bo'lishi kerak.")
        return

    # OK — saqlab keyingi bosqichga
    await state.update_data(yosh=yosh)
    await state.set_state(RegisterStates.telefon)
    await m.answer("Telefonni kiriting:")</code></pre>

<h4>6. State + Inline keyboard birga</h4>

<pre><code>class OrderStates(StatesGroup):
    choose_size = State()
    choose_topping = State()
    confirm = State()


@dp.message(Command("order"))
async def order_start(m: Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Kichik", callback_data="size:small")
    kb.button(text="O'rta", callback_data="size:medium")
    kb.button(text="Katta", callback_data="size:large")
    kb.adjust(3)
    await m.answer("Pizza o'lchamini tanlang:", reply_markup=kb.as_markup())
    await state.set_state(OrderStates.choose_size)


@dp.callback_query(F.data.startswith("size:"), OrderStates.choose_size)
async def choose_size(call: CallbackQuery, state: FSMContext):
    size = call.data.split(":")[1]
    await state.update_data(size=size)
    # Keyingi bosqichga...
    await state.set_state(OrderStates.choose_topping)
    await call.message.edit_text("Topping tanlang...", reply_markup=...)
    await call.answer()</code></pre>

<h4>7. Step-back — orqaga qaytish</h4>

<pre><code>from aiogram.fsm.state import State

@dp.message(Command("back"), StateFilter("*"))
async def step_back(m: Message, state: FSMContext):
    current = await state.get_state()

    if current == RegisterStates.yosh.state:
        await state.set_state(RegisterStates.ism)
        await m.answer("Ismni qaytadan kiriting:")
    elif current == RegisterStates.telefon.state:
        await state.set_state(RegisterStates.yosh)
        await m.answer("Yoshni qaytadan kiriting:")</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ FSM = bot foydalanuvchi qaerda turganini eslaydi</li>
<li>✅ <code>StatesGroup</code> + <code>State()</code> e'lon</li>
<li>✅ <code>state.set_state()</code>, <code>get_state()</code>, <code>clear()</code></li>
<li>✅ <code>state.update_data()</code>, <code>get_data()</code></li>
<li>✅ <code>@dp.message(MyStates.X)</code> filter</li>
<li>✅ Validatsiya — return bilan state o'zgarmaydi</li>
<li>✅ Storage: Memory (dev) vs Redis (prod)</li>
<li>✅ <code>/cancel</code> har bosqichda</li>
</ul>
"""

L5_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 5: FSM — multi-step formalar
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())


# ─────────────────────────────────────────────────────────────────────
# State'lar
# ─────────────────────────────────────────────────────────────────────

class RegisterStates(StatesGroup):
    ism = State()
    yosh = State()
    jins = State()
    telefon = State()


# Klaviaturalar
def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )

def jins_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Erkak")
    kb.button(text="👩 Ayol")
    kb.button(text="❌ Bekor qilish")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

def contact_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


# ─────────────────────────────────────────────────────────────────────
# Boshlash
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"Ro'yxatdan o'tish uchun: /register\\n"
        f"Bekor qilish: /cancel"
    )


# ─────────────────────────────────────────────────────────────────────
# /cancel — har bosqichda
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("cancel"), StateFilter("*"))
@dp.message(F.text == "❌ Bekor qilish", StateFilter("*"))
async def cancel(m: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await m.answer("Hech narsa bekor qilinmaydi.")
        return
    await state.clear()
    await m.answer(
        "❌ Ro'yxatdan o'tish bekor qilindi.",
        reply_markup=ReplyKeyboardRemove(),
    )


# ─────────────────────────────────────────────────────────────────────
# Bosqich 1: /register → ism so'rash
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("register"))
async def register_start(m: Message, state: FSMContext):
    await state.set_state(RegisterStates.ism)
    await m.answer(
        "📝 <b>Ro'yxatdan o'tish</b>\\n\\n"
        "1/4: Ismingizni kiriting:",
        reply_markup=cancel_kb(),
    )


# ─────────────────────────────────────────────────────────────────────
# Bosqich 2: ism qabul → yosh so'rash
# ─────────────────────────────────────────────────────────────────────

@dp.message(RegisterStates.ism, F.text)
async def get_ism(m: Message, state: FSMContext):
    ism = m.text.strip()
    if len(ism) < 2:
        await m.answer("❌ Ism kamida 2 belgi bo'lsin. Qaytadan:")
        return
    if len(ism) > 50:
        await m.answer("❌ Ism juda uzun. 50 belgidan kam bo'lsin:")
        return

    await state.update_data(ism=ism)
    await state.set_state(RegisterStates.yosh)
    await m.answer(
        f"✅ Ism: <b>{ism}</b>\\n\\n"
        f"2/4: Yoshingizni kiriting (14-120):",
        reply_markup=cancel_kb(),
    )


# ─────────────────────────────────────────────────────────────────────
# Bosqich 3: yosh qabul → jins so'rash
# ─────────────────────────────────────────────────────────────────────

@dp.message(RegisterStates.yosh, F.text)
async def get_yosh(m: Message, state: FSMContext):
    if not m.text.isdigit():
        await m.answer("❌ Yosh faqat son bo'lishi kerak:")
        return

    yosh = int(m.text)
    if yosh < 14 or yosh > 120:
        await m.answer("❌ Yosh 14-120 oraliqda bo'lsin:")
        return

    await state.update_data(yosh=yosh)
    await state.set_state(RegisterStates.jins)
    await m.answer(
        f"✅ Yosh: <b>{yosh}</b>\\n\\n"
        f"3/4: Jinsingizni tanlang:",
        reply_markup=jins_kb(),
    )


# ─────────────────────────────────────────────────────────────────────
# Bosqich 4: jins qabul → telefon so'rash
# ─────────────────────────────────────────────────────────────────────

@dp.message(RegisterStates.jins, F.text.in_({"👨 Erkak", "👩 Ayol"}))
async def get_jins(m: Message, state: FSMContext):
    jins = "Erkak" if "Erkak" in m.text else "Ayol"
    await state.update_data(jins=jins)
    await state.set_state(RegisterStates.telefon)
    await m.answer(
        f"✅ Jins: <b>{jins}</b>\\n\\n"
        f"4/4: Telefon raqamingizni yuboring:",
        reply_markup=contact_kb(),
    )


@dp.message(RegisterStates.jins)
async def jins_xato(m: Message):
    await m.answer("❌ Iltimos, tugma orqali tanlang.", reply_markup=jins_kb())


# ─────────────────────────────────────────────────────────────────────
# Bosqich 5: telefon qabul → saqlash va clear()
# ─────────────────────────────────────────────────────────────────────

@dp.message(RegisterStates.telefon, F.contact)
async def get_telefon_contact(m: Message, state: FSMContext):
    await save_user(m, state, m.contact.phone_number)


@dp.message(RegisterStates.telefon, F.text)
async def get_telefon_text(m: Message, state: FSMContext):
    # Telefon validatsiyasi
    import re
    if not re.match(r"^\\+?998\\d{9}$", m.text.replace(" ", "")):
        await m.answer(
            "❌ Telefon noto'g'ri formatda.\\n"
            "Misol: +998901234567\\n"
            "Yoki tugmadan foydalaning:",
            reply_markup=contact_kb(),
        )
        return
    await save_user(m, state, m.text)


async def save_user(m: Message, state: FSMContext, telefon: str):
    # Yakuniy saqlash.
    data = await state.get_data()
    data["telefon"] = telefon
    data["user_id"] = m.from_user.id

    # ... DB'ga saqlash (7-darsda real) ...
    logging.info(f"Saved user: {data}")

    await state.clear()
    await m.answer(
        f"✅ <b>Ro'yxatdan o'tdingiz!</b>\\n\\n"
        f"Ism: <b>{data['ism']}</b>\\n"
        f"Yosh: <b>{data['yosh']}</b>\\n"
        f"Jins: <b>{data['jins']}</b>\\n"
        f"Tel: <code>{data['telefon']}</code>\\n\\n"
        f"Rahmat 🙏",
        reply_markup=ReplyKeyboardRemove(),
    )


# ─────────────────────────────────────────────────────────────────────
# State'lar tashqarisida — boshlash uchun yo'l ko'rsatish
# ─────────────────────────────────────────────────────────────────────

@dp.message(StateFilter(None))
async def no_state(m: Message):
    await m.answer(
        "Boshlash uchun: /register\\n"
        "Yordam: /start",
    )


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L6_TEXT = """\
<h2>Custom filter'lar va middleware</h2>

<pre class="mermaid">
flowchart LR
    U["Update"] --> MW1["Outer Middleware\n(logging, rate-limit)"]
    MW1 --> F["Filter zanjiri"]
    F --> MW2["Inner Middleware\n(DB session, i18n)"]
    MW2 --> H["Handler"]
</pre>

<p>aiogram'da har xabar handler'ga yetib borishidan oldin <strong>filter'lar</strong> tekshiriladi va <strong>middleware</strong>'lar bajariladi. Bu juda kuchli — sizning kod loyik bo'ladi, takrorlanmaydi.</p>

<ul>
<li><strong>Filter</strong> — true/false qaytaradi (handler ishlasinmi?)</li>
<li><strong>Middleware</strong> — har handler'dan oldin/keyin code (logging, DB session, auth, rate-limit)</li>
</ul>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Custom filter</h4>

<pre><code>from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: set[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -&gt; bool:
        return message.from_user.id in self.admin_ids


# Ishlatish
ADMINS = {111, 222}

@dp.message(Command("admin"), IsAdmin(ADMINS))
async def admin_panel(m: Message):
    await m.answer("Admin paneli")</code></pre>

<h4>BLOKA 2 — Logging middleware</h4>

<pre><code>from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
import logging

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -&gt; Any:
        user_id = event.from_user.id if event.from_user else "?"
        text = event.text[:50] if event.text else "[non-text]"
        logging.info(f"[{user_id}] {text}")

        return await handler(event, data)


dp.message.middleware(LoggingMiddleware())</code></pre>

<h4>BLOKA 3 — Rate-limit middleware</h4>

<pre><code>from time import time

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 1.0):
        self.rate = rate    # min vaqt ikki xabar orasida
        self.users: dict[int, float] = {}

    async def __call__(self, handler, event, data):
        if not event.from_user:
            return await handler(event, data)
        user_id = event.from_user.id
        now = time()

        last = self.users.get(user_id, 0)
        if now - last &lt; self.rate:
            await event.answer("⏳ Sekinroq! Bir necha soniya kuting.")
            return    # handler ishga tushmaydi

        self.users[user_id] = now
        return await handler(event, data)


dp.message.middleware(RateLimitMiddleware(rate=1.0))</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>class XatoMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        logging.info("Pre")
        # await handler(event, data)   ❌ UNUTILGAN!
        logging.info("Post")</code></pre>

<p><strong>Natija:</strong> Middleware o'tib ketadi, lekin <strong>handler hech qachon chaqirilmaydi</strong>. Bot foydalanuvchini e'tibordan tashqari qoldiradi.</p>

<p><strong>Qoidasi:</strong> Middleware <code>return await handler(event, data)</code> bilan tugashi shart (block qilmasangiz).</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Filter'lar — 3 ta yaratish usuli</h4>

<p><strong>1) Lambda / F (oddiy):</strong></p>
<pre><code>@dp.message(F.text.startswith("/"))
async def slash(m): ...</code></pre>

<p><strong>2) Function:</strong></p>
<pre><code>async def is_admin(message: Message) -&gt; bool:
    return message.from_user.id in {111, 222}

@dp.message(Command("admin"), is_admin)
async def admin(m): ...</code></pre>

<p><strong>3) Class (BaseFilter) — parametr bilan:</strong></p>
<pre><code>class IsAdmin(BaseFilter):
    def __init__(self, admin_ids):
        self.admin_ids = admin_ids
    async def __call__(self, m: Message):
        return m.from_user.id in self.admin_ids

@dp.message(IsAdmin({111, 222}))
async def admin(m): ...</code></pre>

<h4>2. Middleware turlari</h4>

<table>
<tr><th>Tur</th><th>Qachon ishga tushadi</th></tr>
<tr><td>Outer middleware</td><td>Update qabul qilingach, filter'lardan oldin</td></tr>
<tr><td>Inner middleware</td><td>Filter o'tgach, handler'dan oldin</td></tr>
</table>

<pre><code># Outer (har update uchun, hatto filter o'tmasa ham)
dp.update.outer_middleware(LoggingMiddleware())

# Inner — handler'ga yaqinroq
dp.message.middleware(DBSessionMiddleware())

# Faqat callback uchun
dp.callback_query.middleware(MyMiddleware())</code></pre>

<h4>3. Middleware'dan data uzatish</h4>

<pre><code>class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(self, handler, event, data):
        async with self.session_maker() as session:
            data["db"] = session   # handler'ga uzatamiz
            return await handler(event, data)


# Handler shu data'ni argumentda oladi:
@dp.message(Command("profile"))
async def profile(m: Message, db: AsyncSession):
    user = await db.get(User, m.from_user.id)
    await m.answer(f"Ism: {user.ism}")</code></pre>

<h4>4. Real misol — admin va auth middleware</h4>

<pre><code>class AuthMiddleware(BaseMiddleware):
    # Foydalanuvchini DB'dan oladi yoki yaratadi.

    async def __call__(self, handler, event, data):
        if not event.from_user:
            return await handler(event, data)

        db: AsyncSession = data.get("db")
        if not db:
            return await handler(event, data)

        user = await db.get(User, event.from_user.id)
        if not user:
            user = User(
                id=event.from_user.id,
                ism=event.from_user.first_name,
            )
            db.add(user)
            await db.commit()

        data["user"] = user
        return await handler(event, data)


# Endi har handler'da user avtomatik
@dp.message(Command("profile"))
async def profile(m: Message, user: User):
    await m.answer(f"Ism: {user.ism}\\nBan: {user.banned}")</code></pre>

<h4>5. Rate-limit pro versiyasi</h4>

<pre><code>from collections import defaultdict
from cachetools import TTLCache

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate: int = 5, per: int = 10):
        # 5 ta so'rov 10 soniyada
        self.rate = rate
        self.per = per
        self.cache: dict[int, list[float]] = defaultdict(list)

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        now = time()

        # Eski timestamps'ni tozalash
        self.cache[user_id] = [t for t in self.cache[user_id] if now - t &lt; self.per]

        if len(self.cache[user_id]) &gt;= self.rate:
            await event.answer(f"⏳ {self.per} soniyada {self.rate} ta xabar — limit!")
            return

        self.cache[user_id].append(now)
        return await handler(event, data)</code></pre>

<h4>6. Ban filter</h4>

<pre><code>class NotBanned(BaseFilter):
    async def __call__(self, m: Message, user: User = None) -&gt; bool:
        if user and user.banned:
            await m.answer("🚫 Siz ban qilingansiz.")
            return False
        return True


# Hammadan oldin
dp.message.filter(NotBanned())</code></pre>

<h4>7. ChatTypeFilter — guruh/DM ajratish</h4>

<pre><code># Faqat shaxsiy
@dp.message(F.chat.type == "private")
async def private_only(m): ...

# Faqat guruh
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def group_only(m): ...</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Custom filter — function yoki BaseFilter klass</li>
<li>✅ Middleware — har handler oldin/keyin code</li>
<li>✅ Outer vs Inner middleware</li>
<li>✅ Middleware'dan handler'ga <code>data['x'] = ...</code></li>
<li>✅ <strong>Doim <code>return await handler(event, data)</code></strong></li>
<li>✅ Tipik: logging, rate-limit, auth, DB session, ban</li>
<li>✅ Filter'lar va middleware'lar — DRY kod uchun</li>
</ul>
"""

L6_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 6: Custom filter'lar va middleware
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from collections import defaultdict
from time import time
from typing import Any, Awaitable, Callable, Dict
from dotenv import load_dotenv

from aiogram import Bot, BaseMiddleware, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter, Command, CommandStart
from aiogram.types import Message, TelegramObject

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# 1) Custom filter — admin tekshirish
# ─────────────────────────────────────────────────────────────────────

ADMIN_IDS = {111111111, 222222222}    # haqiqiy ID'lar bilan


class IsAdmin(BaseFilter):
    # Foydalanuvchi admin ekanini tekshiradi.

    def __init__(self, admin_ids: set[int] | None = None):
        self.admin_ids = admin_ids or ADMIN_IDS

    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user) and message.from_user.id in self.admin_ids


# ─────────────────────────────────────────────────────────────────────
# 2) Logging middleware — har xabarni log qiladi
# ─────────────────────────────────────────────────────────────────────

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        text = event.text[:50] if event.text else f"[{event.content_type}]"
        username = f"@{user.username}" if user.username else f"id={user.id}"
        logging.info(f"📥 {username}: {text}")

        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            logging.error(f"❌ Handler xato: {e}")
            await event.answer("⚠️ Texnik xato. Keyinroq qayta urinib ko'ring.")
            raise


# ─────────────────────────────────────────────────────────────────────
# 3) Rate-limit middleware — spam'dan saqlash
# ─────────────────────────────────────────────────────────────────────

class RateLimitMiddleware(BaseMiddleware):
    # N ta xabar M soniyada.

    def __init__(self, rate: int = 5, per: int = 10):
        self.rate = rate
        self.per = per
        self.cache: dict[int, list[float]] = defaultdict(list)

    async def __call__(self, handler, event: Message, data):
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time()

        # Eski timestamp'larni o'chirish (per sekund oldindan)
        self.cache[user_id] = [t for t in self.cache[user_id] if now - t < self.per]

        if len(self.cache[user_id]) >= self.rate:
            wait = self.per - (now - self.cache[user_id][0])
            await event.answer(
                f"⏳ Sekinroq! {self.per}s da {self.rate} xabar limit.\\n"
                f"{wait:.1f}s kuting."
            )
            return    # handler ishga tushmaydi

        self.cache[user_id].append(now)
        return await handler(event, data)


# ─────────────────────────────────────────────────────────────────────
# 4) User context middleware (auth simulyatsiyasi)
# ─────────────────────────────────────────────────────────────────────

# Demo "DB" — production'da SQLAlchemy
USERS_DB: dict[int, dict] = {}


class UserContextMiddleware(BaseMiddleware):
    # Foydalanuvchini DB'dan oladi yoki yaratadi, data['user']'ga qo'shadi.

    async def __call__(self, handler, event: Message, data):
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        user = USERS_DB.get(user_id)
        if not user:
            user = {
                "id": user_id,
                "ism": event.from_user.first_name,
                "username": event.from_user.username,
                "banned": False,
                "messages_count": 0,
            }
            USERS_DB[user_id] = user

        user["messages_count"] += 1
        data["user"] = user

        return await handler(event, data)


# ─────────────────────────────────────────────────────────────────────
# 5) Ban filter (middleware'dan kelgan user bilan)
# ─────────────────────────────────────────────────────────────────────

class NotBanned(BaseFilter):
    async def __call__(self, message: Message, user: dict | None = None) -> bool:
        if user and user.get("banned"):
            await message.answer("🚫 Siz bloklangansiz. Adminga murojaat qiling.")
            return False
        return True


# ─────────────────────────────────────────────────────────────────────
# Middleware'larni dispatcher'ga ulash
# ─────────────────────────────────────────────────────────────────────

dp.message.middleware(LoggingMiddleware())
dp.message.middleware(UserContextMiddleware())
dp.message.middleware(RateLimitMiddleware(rate=5, per=10))


# ─────────────────────────────────────────────────────────────────────
# Handler'lar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message, user: dict):
    await m.answer(
        f"Salom, <b>{user['ism']}</b>!\\n"
        f"Siz {user['messages_count']} ta xabar yubordingiz.\\n\\n"
        f"Buyruqlar:\\n"
        f"/profile — sizning profilingiz\\n"
        f"/admin — admin paneli (faqat admin)\\n"
        f"/ban &lt;id&gt; — foydalanuvchini ban (admin)\\n"
        f"/users — barcha foydalanuvchilar (admin)"
    )


@dp.message(Command("profile"), NotBanned())
async def profile(m: Message, user: dict):
    await m.answer(
        f"👤 <b>Sizning profilingiz</b>\\n\\n"
        f"ID: <code>{user['id']}</code>\\n"
        f"Ism: {user['ism']}\\n"
        f"Username: @{user['username'] or '—'}\\n"
        f"Yuborgan xabar: {user['messages_count']}\\n"
        f"Holat: {'🚫 ban' if user['banned'] else '✅ faol'}"
    )


# Admin only
@dp.message(Command("admin"), IsAdmin())
async def admin_panel(m: Message):
    await m.answer(
        "🛠 <b>Admin paneli</b>\\n\\n"
        "/users — ro'yxat\\n"
        "/ban &lt;id&gt; — ban\\n"
        "/unban &lt;id&gt; — unban\\n"
        "/stats — statistika"
    )


@dp.message(Command("users"), IsAdmin())
async def list_users(m: Message):
    if not USERS_DB:
        await m.answer("Foydalanuvchilar yo'q")
        return
    lines = []
    for u in USERS_DB.values():
        mark = "🚫" if u["banned"] else "✅"
        lines.append(f"{mark} <code>{u['id']}</code> — {u['ism']} ({u['messages_count']})")
    await m.answer("👥 <b>Foydalanuvchilar:</b>\\n\\n" + "\\n".join(lines))


@dp.message(Command("ban"), IsAdmin())
async def ban_user(m: Message):
    parts = m.text.split()
    if len(parts) < 2:
        await m.answer("Foydalanish: /ban &lt;user_id&gt;")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await m.answer("ID raqam bo'lishi kerak")
        return

    target = USERS_DB.get(target_id)
    if not target:
        await m.answer("Bunday foydalanuvchi yo'q")
        return

    target["banned"] = True
    await m.answer(f"🚫 {target['ism']} ban qilindi")


@dp.message(Command("unban"), IsAdmin())
async def unban_user(m: Message):
    parts = m.text.split()
    if len(parts) < 2:
        await m.answer("Foydalanish: /unban &lt;user_id&gt;")
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await m.answer("ID raqam bo'lishi kerak")
        return

    target = USERS_DB.get(target_id)
    if not target:
        await m.answer("Bunday foydalanuvchi yo'q")
        return

    target["banned"] = False
    await m.answer(f"✅ {target['ism']} unban qilindi")


@dp.message(Command("stats"), IsAdmin())
async def stats(m: Message):
    total = len(USERS_DB)
    banned = sum(1 for u in USERS_DB.values() if u["banned"])
    msgs = sum(u["messages_count"] for u in USERS_DB.values())
    await m.answer(
        f"📊 <b>Statistika</b>\\n\\n"
        f"Jami: {total}\\n"
        f"Ban: {banned}\\n"
        f"Faol: {total - banned}\\n"
        f"Jami xabar: {msgs}"
    )


# Catch-all (ban filtri bilan)
@dp.message(NotBanned())
async def echo(m: Message, user: dict):
    if m.text:
        await m.answer(f"📝 Echo: {m.text}")
    else:
        await m.answer("Faqat matn yuboring")


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
R2_TEXT = """\
<h2>R2 — Modul 2 takrorlash: Anketa to'ldiruvchi bot</h2>

<p>Modul 2 ning hammasi birga — <strong>FSM + Inline keyboards + Filter + Middleware</strong>. Yagona amaliy bot: foydalanuvchi anketa to'ldiradi, ma'lumotlar saqlanadi, admin ko'rishi mumkin.</p>

<h3>Loyihaning maqsadi</h3>

<p>"O'quvchi anketasi" bot — kurs ro'yxatga olish uchun. 7 bosqich:</p>
<ol>
<li>Ism (matn)</li>
<li>Familiya (matn)</li>
<li>Yosh (raqam)</li>
<li>Jins (inline tugma: Erkak/Ayol)</li>
<li>Shahar (inline tugma: Toshkent/Samarqand/...)</li>
<li>Telefon (contact)</li>
<li>Tasdiq (inline tugma: Tasdiqlayman/Tahrirlash)</li>
</ol>

<p>Admin (BotFather'da yoki .env'da belgilangan ID'lar) — <code>/applications</code> bilan barcha anketalarni ko'radi.</p>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — FSM states</h4>
<ul>
<li>7 ta state (ism, familiya, yosh, jins, shahar, telefon, confirm)</li>
<li>StorageMemory ishlatish</li>
</ul>

<h4>Vazifa 2 — Bosqichlar</h4>
<ul>
<li>Har bosqich: avvalgi natijani ko'rsatish + yangisini so'rash</li>
<li>Progress: "3/7", "4/7"...</li>
<li>Validatsiya: yosh — son va 14-100 oraliq, ism/familiya — 2-50 belgi</li>
<li>Jins va shahar — inline keyboard</li>
</ul>

<h4>Vazifa 3 — Tasdiqlash sahifasi</h4>
<ul>
<li>Hamma ma'lumotlar chiroyli ko'rsatiladi</li>
<li>2 ta tugma: ✅ Tasdiqlayman / ✏️ Tahrirlash</li>
<li>Tahrirlash — boshidan boshlash (yoki bosqich tanlash)</li>
</ul>

<h4>Vazifa 4 — Saqlash</h4>
<ul>
<li>Hozircha: in-memory dictionary <code>APPLICATIONS</code></li>
<li>(7-darsda DB bilan to'g'rilaymiz)</li>
<li>Admin uchun ko'rinishga tayyor</li>
</ul>

<h4>Vazifa 5 — Admin paneli</h4>
<ul>
<li><code>/applications</code> — barcha anketalar (inline pagination, 5/sahifa)</li>
<li>Har anketa — inline tugma: 👁 Ko'rish</li>
<li>Ko'rish — to'liq ma'lumot + 🗑 O'chirish, ⬅️ Ro'yxatga</li>
</ul>

<h4>Vazifa 6 — Rate-limit va logging</h4>
<ul>
<li>5 ta xabar 10 soniyada limit</li>
<li>Har xabar — log fayl yoki console</li>
</ul>

<h4>Vazifa 7 — /cancel</h4>
<ul>
<li>Har bosqichda <code>/cancel</code> ishlasin</li>
<li>State clear + xabar</li>
</ul>

<h3>🐛 Ataylab qiyin: tahrirlash</h3>

<p>"✏️ Tahrirlash" tugmasi qaerga olib boradi? Variantlar:</p>
<ol>
<li>Boshidan (eng oson — barcha bosqichlarni qaytadan)</li>
<li>Bosqich tanlash inline keyboard (qiyinroq — har bosqich uchun "Yana 1 marta" tugma)</li>
<li>Yagona maydon tanlash (eng qiyin — "Faqat ismni" — selektiv update)</li>
</ol>

<p>Bazaviy — variant 1. Bonus — variant 2 yoki 3.</p>

<h3>Yechim sketch</h3>

<details>
<summary>FSM struktura — avval o'zingiz urinib ko'ring!</summary>
<pre><code>class AnketaStates(StatesGroup):
    ism = State()
    familiya = State()
    yosh = State()
    jins = State()
    shahar = State()
    telefon = State()
    confirm = State()


@dp.message(Command("anketa"))
async def start(m: Message, state: FSMContext):
    await state.set_state(AnketaStates.ism)
    await m.answer("1/7 Ismingiz?", reply_markup=cancel_kb())


@dp.message(AnketaStates.ism, F.text)
async def get_ism(m: Message, state: FSMContext):
    if len(m.text) &lt; 2:
        return await m.answer("Qisqa")
    await state.update_data(ism=m.text)
    await state.set_state(AnketaStates.familiya)
    await m.answer("2/7 Familiyangiz?")


# ... va h.k.


@dp.callback_query(F.data.startswith("jins:"), AnketaStates.jins)
async def get_jins(call: CallbackQuery, state: FSMContext):
    jins = call.data.split(":")[1]
    await state.update_data(jins=jins)
    await state.set_state(AnketaStates.shahar)
    # ...


# Tasdiqlash
@dp.callback_query(F.data == "confirm:yes", AnketaStates.confirm)
async def confirmed(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    APPLICATIONS[call.from_user.id] = data
    await state.clear()
    await call.message.edit_text("✅ Anketa qabul qilindi!")</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 2 ning hammasi birga: FSM + inline + filter + middleware</li>
<li>✅ Multi-step form yaratish</li>
<li>✅ Inline tugma + FSM state birga</li>
<li>✅ Tasdiqlash sahifasi pattern</li>
<li>✅ Admin paneli — pagination bilan</li>
<li>✅ Validatsiya + UX (progress 3/7)</li>
</ul>
"""

R2_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 2: Anketa to'ldiruvchi bot
# Modul 2: FSM + inline keyboards + filter + middleware
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
import re
from typing import Any, Callable, Dict, Awaitable
from dotenv import load_dotenv

from aiogram import Bot, BaseMiddleware, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter, Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

ADMINS = {int(x) for x in os.getenv("ADMIN_IDS", "111").split(",") if x.strip()}

# In-memory "DB"
APPLICATIONS: dict[int, dict] = {}


# ─────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────

class LoggingMW(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        text = (event.text or f"[{event.__class__.__name__}]")[:50]
        logging.info(f"[{user.id} @{user.username}] {text}")
        return await handler(event, data)


dp.message.middleware(LoggingMW())
dp.callback_query.middleware(LoggingMW())


# ─────────────────────────────────────────────────────────────────────
# Filter — IsAdmin
# ─────────────────────────────────────────────────────────────────────

class IsAdmin(BaseFilter):
    async def __call__(self, event) -> bool:
        return event.from_user.id in ADMINS


# ─────────────────────────────────────────────────────────────────────
# FSM
# ─────────────────────────────────────────────────────────────────────

class AnketaStates(StatesGroup):
    ism = State()
    familiya = State()
    yosh = State()
    jins = State()
    shahar = State()
    telefon = State()
    confirm = State()


# ─────────────────────────────────────────────────────────────────────
# Klaviaturalar
# ─────────────────────────────────────────────────────────────────────

def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def jins_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="👨 Erkak", callback_data="jins:Erkak")
    kb.button(text="👩 Ayol", callback_data="jins:Ayol")
    kb.adjust(2)
    return kb.as_markup()


SHAHARLAR = ["Toshkent", "Samarqand", "Buxoro", "Andijon",
             "Farg'ona", "Namangan", "Qarshi", "Nukus"]


def shahar_kb():
    kb = InlineKeyboardBuilder()
    for s in SHAHARLAR:
        kb.button(text=s, callback_data=f"shahar:{s}")
    kb.adjust(2)
    return kb.as_markup()


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
    )


def confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlayman", callback_data="confirm:yes")
    kb.button(text="✏️ Tahrirlash", callback_data="confirm:edit")
    kb.adjust(2)
    return kb.as_markup()


# ─────────────────────────────────────────────────────────────────────
# Boshlash va bekor qilish
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"Anketa to'ldirish: /anketa\\n"
        f"Bekor qilish: /cancel"
    )


@dp.message(Command("cancel"), StateFilter("*"))
@dp.message(F.text == "❌ Bekor qilish", StateFilter("*"))
async def cancel(m: Message, state: FSMContext):
    if await state.get_state() is None:
        await m.answer("Anketa to'ldirilmayapti.")
        return
    await state.clear()
    await m.answer("❌ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())


# ─────────────────────────────────────────────────────────────────────
# Anketa bosqichlari
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("anketa"))
async def anketa_start(m: Message, state: FSMContext):
    await state.set_state(AnketaStates.ism)
    await m.answer("📝 1/7 — Ismingizni kiriting:", reply_markup=cancel_kb())


@dp.message(AnketaStates.ism, F.text)
async def get_ism(m: Message, state: FSMContext):
    ism = m.text.strip()
    if not 2 <= len(ism) <= 50:
        return await m.answer("❌ Ism 2-50 belgi bo'lsin.")
    await state.update_data(ism=ism)
    await state.set_state(AnketaStates.familiya)
    await m.answer(f"✅ Ism: <b>{ism}</b>\\n\\n📝 2/7 — Familiyangiz?")


@dp.message(AnketaStates.familiya, F.text)
async def get_familiya(m: Message, state: FSMContext):
    fam = m.text.strip()
    if not 2 <= len(fam) <= 50:
        return await m.answer("❌ Familiya 2-50 belgi bo'lsin.")
    await state.update_data(familiya=fam)
    await state.set_state(AnketaStates.yosh)
    await m.answer(f"✅ Familiya: <b>{fam}</b>\\n\\n📝 3/7 — Yoshingiz? (14-100)")


@dp.message(AnketaStates.yosh, F.text)
async def get_yosh(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer("❌ Faqat son.")
    yosh = int(m.text)
    if not 14 <= yosh <= 100:
        return await m.answer("❌ 14-100 oraliqda.")
    await state.update_data(yosh=yosh)
    await state.set_state(AnketaStates.jins)
    await m.answer(
        f"✅ Yosh: <b>{yosh}</b>\\n\\n📝 4/7 — Jinsingiz?",
        reply_markup=jins_kb(),
    )


@dp.callback_query(F.data.startswith("jins:"), AnketaStates.jins)
async def get_jins(call: CallbackQuery, state: FSMContext):
    jins = call.data.split(":")[1]
    await state.update_data(jins=jins)
    await state.set_state(AnketaStates.shahar)
    await call.answer()
    await call.message.edit_text(
        f"✅ Jins: <b>{jins}</b>\\n\\n📝 5/7 — Shaharingiz?",
        reply_markup=shahar_kb(),
    )


@dp.callback_query(F.data.startswith("shahar:"), AnketaStates.shahar)
async def get_shahar(call: CallbackQuery, state: FSMContext):
    shahar = call.data.split(":")[1]
    await state.update_data(shahar=shahar)
    await state.set_state(AnketaStates.telefon)
    await call.answer()
    await call.message.edit_text(f"✅ Shahar: <b>{shahar}</b>")
    await call.message.answer("📝 6/7 — Telefon raqam?", reply_markup=contact_kb())


@dp.message(AnketaStates.telefon, F.contact)
async def get_telefon_contact(m: Message, state: FSMContext):
    await save_phone(m, state, m.contact.phone_number)


@dp.message(AnketaStates.telefon, F.text)
async def get_telefon_text(m: Message, state: FSMContext):
    phone = m.text.strip()
    if not re.match(r"^\\+?998\\d{9}$", phone.replace(" ", "")):
        return await m.answer("❌ Misol: +998901234567 yoki tugma bosing.")
    await save_phone(m, state, phone)


async def save_phone(m: Message, state: FSMContext, phone: str):
    await state.update_data(telefon=phone)
    await state.set_state(AnketaStates.confirm)
    data = await state.get_data()

    summary = (
        f"📋 <b>Anketa to'ldirildi:</b>\\n\\n"
        f"Ism: <b>{data['ism']}</b>\\n"
        f"Familiya: <b>{data['familiya']}</b>\\n"
        f"Yosh: <b>{data['yosh']}</b>\\n"
        f"Jins: <b>{data['jins']}</b>\\n"
        f"Shahar: <b>{data['shahar']}</b>\\n"
        f"Telefon: <code>{data['telefon']}</code>\\n\\n"
        f"📝 7/7 — Tasdiqlaysizmi?"
    )
    await m.answer(summary, reply_markup=confirm_kb())


# ─────────────────────────────────────────────────────────────────────
# Tasdiq yoki tahrirlash
# ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "confirm:yes", AnketaStates.confirm)
async def confirmed(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    APPLICATIONS[call.from_user.id] = {
        **data,
        "user_id": call.from_user.id,
        "username": call.from_user.username,
    }
    await state.clear()
    await call.answer("Saqlandi!", show_alert=True)
    await call.message.edit_text(
        "✅ <b>Anketa qabul qilindi!</b>\\n\\n"
        "Tez orada siz bilan bog'lanamiz. Rahmat 🙏"
    )
    # Adminga xabar
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 Yangi anketa: <b>{data['ism']} {data['familiya']}</b>\\n"
                f"Yosh: {data['yosh']}, Shahar: {data['shahar']}\\n"
                f"Tel: {data['telefon']}",
            )
        except Exception as e:
            logging.error(f"Admin xabar yuborilmadi: {e}")


@dp.callback_query(F.data == "confirm:edit", AnketaStates.confirm)
async def edit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await call.message.edit_text("✏️ Anketa qaytadan boshlanadi.")
    await call.message.answer("📝 1/7 — Ismingizni kiriting:", reply_markup=cancel_kb())
    await state.set_state(AnketaStates.ism)


# ─────────────────────────────────────────────────────────────────────
# Admin paneli
# ─────────────────────────────────────────────────────────────────────

PER_PAGE = 5


@dp.message(Command("applications"), IsAdmin())
async def admin_apps(m: Message):
    await show_apps_page(m, page=1)


async def show_apps_page(m_or_call, page: int):
    apps = list(APPLICATIONS.values())
    if not apps:
        text = "Hech qanday anketa yo'q."
        kb = None
    else:
        total = (len(apps) + PER_PAGE - 1) // PER_PAGE
        page = max(1, min(page, total))
        start = (page - 1) * PER_PAGE
        page_apps = apps[start:start + PER_PAGE]

        lines = [f"📋 <b>Anketalar ({page}/{total}):</b>\\n"]
        for a in page_apps:
            lines.append(
                f"• <b>{a['ism']} {a['familiya']}</b> ({a['shahar']}, {a['yosh']})"
            )
        text = "\\n".join(lines)

        kb = InlineKeyboardBuilder()
        for a in page_apps:
            kb.button(
                text=f"👁 {a['ism']} {a['familiya']}",
                callback_data=f"view:{a['user_id']}",
            )
        # Navigation
        nav = []
        if page > 1:
            nav.append(("⬅️", f"apps_pg:{page-1}"))
        nav.append((f"{page}/{total}", "noop"))
        if page < total:
            nav.append(("➡️", f"apps_pg:{page+1}"))
        for txt, cb_data in nav:
            kb.button(text=txt, callback_data=cb_data)
        kb.adjust(1, 1, 1, 1, 1, 3)
        kb = kb.as_markup()

    if isinstance(m_or_call, CallbackQuery):
        await m_or_call.message.edit_text(text, reply_markup=kb)
        await m_or_call.answer()
    else:
        await m_or_call.answer(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("apps_pg:"), IsAdmin())
async def cb_apps_page(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    await show_apps_page(call, page)


@dp.callback_query(F.data.startswith("view:"), IsAdmin())
async def cb_view_app(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    a = APPLICATIONS.get(user_id)
    if not a:
        await call.answer("Topilmadi", show_alert=True)
        return

    text = (
        f"👤 <b>{a['ism']} {a['familiya']}</b>\\n\\n"
        f"Yosh: {a['yosh']}\\n"
        f"Jins: {a['jins']}\\n"
        f"Shahar: {a['shahar']}\\n"
        f"Telefon: <code>{a['telefon']}</code>\\n"
        f"Username: @{a['username'] or '—'}\\n"
        f"User ID: <code>{a['user_id']}</code>"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 O'chirish", callback_data=f"delete:{a['user_id']}")
    kb.button(text="⬅️ Ro'yxat", callback_data="apps_pg:1")
    kb.adjust(2)

    await call.message.edit_text(text, reply_markup=kb.as_markup())
    await call.answer()


@dp.callback_query(F.data.startswith("delete:"), IsAdmin())
async def cb_delete(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    APPLICATIONS.pop(user_id, None)
    await call.answer("O'chirildi", show_alert=True)
    await show_apps_page(call, page=1)


@dp.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L7_TEXT = """\
<h2>SQLAlchemy async bilan database</h2>

<pre class="mermaid">
flowchart LR
    M["Message"] -->|middleware| S["AsyncSession"]
    S --> H["Handler"]
    H -->|await session.execute| DB[("PostgreSQL")]
    H -->|await session.commit| DB
</pre>

<p>Hozirgacha ma'lumotni in-memory dictionary'da saqladik. Bot restart bo'lsa — yo'qoladi. Production'da — <strong>database</strong>. aiogram async-first, shuning uchun SQLAlchemy ham async ishlatamiz. Bu darsda — to'liq pattern.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — O'rnatish</h4>

<pre><code>pip install sqlalchemy[asyncio] asyncpg aiosqlite alembic
# asyncpg — PostgreSQL uchun
# aiosqlite — SQLite uchun (dev)
# alembic — migration uchun</code></pre>

<h4>BLOKA 2 — Model va engine</h4>

<pre><code># db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


# db/models.py
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ism: Mapped[str] = mapped_column(String(50))
    username: Mapped[str | None] = mapped_column(String(50))
    yaratilgan: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    mahsulot: Mapped[str] = mapped_column(String(100))
    summa: Mapped[float] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="orders")


# db/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DB_URL = "postgresql+asyncpg://user:pass@localhost/botdb"
# Dev: DB_URL = "sqlite+aiosqlite:///bot.db"

engine = create_async_engine(DB_URL, echo=True)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)</code></pre>

<h4>BLOKA 3 — DB session middleware</h4>

<pre><code>class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(self, handler, event, data):
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)


dp.update.middleware(DBSessionMiddleware(SessionMaker))


# Handler'da
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@dp.message(Command("profile"))
async def profile(m: Message, session: AsyncSession):
    user = await session.get(User, m.from_user.id)
    if not user:
        user = User(id=m.from_user.id, ism=m.from_user.first_name)
        session.add(user)
        await session.commit()
    await m.answer(f"Ism: {user.ism}\\nYaratilgan: {user.yaratilgan}")</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Sync SQLAlchemy ishlatish
from sqlalchemy.orm import Session

session = Session(engine)   # ❌ sync session
user = session.query(User).get(user_id)   # ❌ sync query</code></pre>

<p><strong>Sabab:</strong> aiogram async event loop'da ishlaydi. Sync DB chaqiriqlari butun bot'ni bloklаydi (boshqa foydalanuvchilar javob ololmaydi). To'g'ri yo'l — <code>AsyncSession</code> + <code>await</code>.</p>

<pre><code># ✅
from sqlalchemy.ext.asyncio import AsyncSession

async with SessionMaker() as session:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Async SQLAlchemy 2.x — asosiy operatsiyalar</h4>

<pre><code># GET by ID
user = await session.get(User, user_id)

# SELECT
from sqlalchemy import select
stmt = select(User).where(User.ism.startswith("Olim"))
result = await session.execute(stmt)
users = result.scalars().all()
# Bittasi:
user = result.scalar_one()      # exact 1 — bo'lmasa Exception
user = result.scalar_one_or_none()   # 0 yoki 1

# INSERT
user = User(id=123, ism="Olim")
session.add(user)
await session.commit()

# UPDATE
user.ism = "Yangi"
await session.commit()

# DELETE
await session.delete(user)
await session.commit()

# Bulk
from sqlalchemy import update, delete
await session.execute(update(User).where(User.id == 1).values(ism="X"))
await session.execute(delete(User).where(User.banned == True))
await session.commit()</code></pre>

<h4>2. Boshlang'ich migration (alembic'siz, oddiy)</h4>

<pre><code>async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_db()    # birinchi marta
    await dp.start_polling(bot)</code></pre>

<h4>3. Production'da Alembic</h4>

<pre><code>alembic init alembic
# alembic.ini'da:
# sqlalchemy.url = postgresql+asyncpg://...

# env.py — async config (alembic templates'da)

# Migration yaratish
alembic revision --autogenerate -m "init"

# Ishlatish
alembic upgrade head</code></pre>

<h4>4. Relationship — JOIN bilan</h4>

<pre><code>from sqlalchemy.orm import selectinload

# User'ni orders bilan birga olish (N+1 oldini olish)
stmt = (
    select(User)
    .where(User.id == user_id)
    .options(selectinload(User.orders))
)
result = await session.execute(stmt)
user = result.scalar_one_or_none()

for order in user.orders:    # qo'shimcha so'rovsiz
    print(order.mahsulot)</code></pre>

<h4>5. Repository pattern (toza kod)</h4>

<pre><code># services/user_service.py
class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int, ism: str) -&gt; User:
        user = await self.session.get(User, user_id)
        if not user:
            user = User(id=user_id, ism=ism)
            self.session.add(user)
            await self.session.commit()
        return user

    async def list_all(self, limit: int = 10) -&gt; list[User]:
        result = await self.session.execute(
            select(User).limit(limit)
        )
        return list(result.scalars())


# Handler'da
@dp.message(Command("users"))
async def users_list(m: Message, session: AsyncSession):
    service = UserService(session)
    users = await service.list_all(50)
    text = "\\n".join(f"• {u.ism}" for u in users)
    await m.answer(text)</code></pre>

<h4>6. Transactions</h4>

<pre><code># Avtomatik commit/rollback
async with session.begin():
    user1.balans -= 100
    user2.balans += 100
    # Exception bo'lsa — rollback
    # Tugagach — commit</code></pre>

<h4>7. FSM bilan birga — yakuniy saqlash</h4>

<pre><code># L5/R2 dagi anketani DB'ga saqlash
@dp.callback_query(F.data == "confirm:yes", AnketaStates.confirm)
async def save_to_db(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    user = User(
        id=call.from_user.id,
        ism=data["ism"],
        # ...
    )
    session.add(user)
    await session.commit()
    await state.clear()</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ <strong>async</strong> SQLAlchemy — <code>AsyncSession</code></li>
<li>✅ Engine + SessionMaker pattern</li>
<li>✅ DBSessionMiddleware — har handler'ga session</li>
<li>✅ get, select, insert, update, delete</li>
<li>✅ Relationship + selectinload (N+1 oldini olish)</li>
<li>✅ Repository pattern — service layer</li>
<li>✅ FSM bilan birga — anketa DB'ga</li>
</ul>
"""

L7_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 7: SQLAlchemy async bilan database
# ════════════════════════════════════════════════════════════════════
#
# O'rnatish:
#   pip install sqlalchemy[asyncio] asyncpg aiosqlite
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict
from dotenv import load_dotenv

from aiogram import Bot, BaseMiddleware, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, TelegramObject

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Float, select, func, delete
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, selectinload,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)


# ─────────────────────────────────────────────────────────────────────
# Database — engine va session
# ─────────────────────────────────────────────────────────────────────

# Dev: SQLite. Production: PostgreSQL.
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///bot.db")
# DB_URL = "postgresql+asyncpg://user:pass@localhost/botdb"

engine = create_async_engine(DB_URL, echo=False)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────────────
# Modellar
# ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ism: Mapped[str] = mapped_column(String(50))
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    yaratilgan: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.id} {self.ism}>"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    mahsulot: Mapped[str] = mapped_column(String(100))
    summa: Mapped[float] = mapped_column(Float)
    sana: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="orders")


async def init_db():
    # Birinchi marta — jadvallar yaratish.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ─────────────────────────────────────────────────────────────────────
# Repository / Service layer
# ─────────────────────────────────────────────────────────────────────

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: int, ism: str, username: str | None = None) -> User:
        user = await self.session.get(User, user_id)
        if user:
            return user

        user = User(id=user_id, ism=ism, username=username)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_with_orders(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.orders))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def list_all(self, limit: int = 50) -> list[User]:
        result = await self.session.execute(
            select(User).order_by(User.yaratilgan.desc()).limit(limit)
        )
        return list(result.scalars())


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, mahsulot: str, summa: float) -> Order:
        order = Order(user_id=user_id, mahsulot=mahsulot, summa=summa)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def list_user_orders(self, user_id: int) -> list[Order]:
        result = await self.session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.sana.desc())
        )
        return list(result.scalars())

    async def total_revenue(self) -> float:
        result = await self.session.execute(select(func.sum(Order.summa)))
        return result.scalar() or 0.0


# ─────────────────────────────────────────────────────────────────────
# DBSessionMiddleware
# ─────────────────────────────────────────────────────────────────────

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]):
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)


# UserContextMiddleware — har handler'da user mavjud
class UserContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not event.from_user:
            return await handler(event, data)

        session: AsyncSession = data["session"]
        service = UserService(session)
        user = await service.get_or_create(
            user_id=event.from_user.id,
            ism=event.from_user.first_name,
            username=event.from_user.username,
        )
        data["user"] = user
        return await handler(event, data)


# ─────────────────────────────────────────────────────────────────────
# Bot va Dispatcher
# ─────────────────────────────────────────────────────────────────────

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

dp.update.middleware(DBSessionMiddleware(SessionMaker))
dp.update.middleware(UserContextMiddleware())


# ─────────────────────────────────────────────────────────────────────
# Handler'lar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message, user: User):
    await m.answer(
        f"Salom, <b>{user.ism}</b>!\\n"
        f"Sizning ID: <code>{user.id}</code>\\n"
        f"Ro'yxatdan o'tgan: {user.yaratilgan:%Y-%m-%d}\\n\\n"
        f"Buyruqlar:\\n"
        f"/buy &lt;mahsulot&gt; &lt;summa&gt; — buyurtma\\n"
        f"/orders — sizning buyurtmalaringiz\\n"
        f"/stats — umumiy statistika"
    )


@dp.message(Command("buy"))
async def cmd_buy(m: Message, user: User, session: AsyncSession):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        await m.answer("Foydalanish: /buy &lt;mahsulot&gt; &lt;summa&gt;\\nMisol: /buy Pizza 45000")
        return

    mahsulot = parts[1]
    try:
        summa = float(parts[2])
    except ValueError:
        await m.answer("Summa son bo'lishi kerak")
        return

    service = OrderService(session)
    order = await service.create(user.id, mahsulot, summa)

    await m.answer(
        f"✅ Buyurtma qabul qilindi!\\n\\n"
        f"ID: <code>#{order.id}</code>\\n"
        f"Mahsulot: <b>{order.mahsulot}</b>\\n"
        f"Summa: <b>{order.summa:,.0f}</b> so'm\\n"
        f"Sana: {order.sana:%Y-%m-%d %H:%M}"
    )


@dp.message(Command("orders"))
async def cmd_orders(m: Message, user: User, session: AsyncSession):
    service = OrderService(session)
    orders = await service.list_user_orders(user.id)

    if not orders:
        await m.answer("Sizda buyurtmalar yo'q. /buy bilan boshlang.")
        return

    lines = [f"📦 <b>Sizning buyurtmalaringiz:</b>\\n"]
    jami = 0.0
    for o in orders:
        lines.append(f"• #{o.id} — {o.mahsulot}: {o.summa:,.0f} so'm")
        jami += o.summa
    lines.append(f"\\n💰 Jami: <b>{jami:,.0f}</b> so'm")

    await m.answer("\\n".join(lines))


@dp.message(Command("stats"))
async def cmd_stats(m: Message, session: AsyncSession):
    user_service = UserService(session)
    order_service = OrderService(session)

    user_count = await user_service.count_all()
    revenue = await order_service.total_revenue()

    await m.answer(
        f"📊 <b>Bot statistikasi</b>\\n\\n"
        f"Foydalanuvchilar: <b>{user_count}</b>\\n"
        f"Umumiy daromad: <b>{revenue:,.0f}</b> so'm"
    )


@dp.message(Command("profile"))
async def cmd_profile(m: Message, session: AsyncSession):
    service = UserService(session)
    user = await service.get_with_orders(m.from_user.id)
    if not user:
        await m.answer("Avval /start bosing")
        return

    orders_count = len(user.orders)
    total_spent = sum(o.summa for o in user.orders)

    await m.answer(
        f"👤 <b>Sizning profil</b>\\n\\n"
        f"Ism: <b>{user.ism}</b>\\n"
        f"Username: @{user.username or '—'}\\n"
        f"Ro'yxatdan o'tgan: {user.yaratilgan:%Y-%m-%d}\\n\\n"
        f"📦 Buyurtmalar: <b>{orders_count}</b>\\n"
        f"💰 Sarflagan: <b>{total_spent:,.0f}</b> so'm"
    )


# ─────────────────────────────────────────────────────────────────────
async def main():
    await init_db()    # birinchi marta
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L8_TEXT = """\
<h2>Fayllar bilan ishlash (rasm, hujjat, voice)</h2>

<pre class="mermaid">
flowchart LR
    U["User yuborgan fayl"] -->|file_id| H["Handler"]
    H -->|bot.download| LOCAL["Lokal fayl"]
    H2["Bot"] -->|FSInputFile yoki URLInputFile| SEND["User'ga yuborish"]
</pre>

<p>Telegram fayllarini ishlash — har real bot'ning zarur qismi: shop botida mahsulot rasmlari, support bot'da screenshot'lar, education bot'da PDF'lar. aiogram bilan oson, lekin nuanse'lar bor.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — fayl yuborish (4 ta yo'l)</h4>

<pre><code>from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile

# 1) Lokal fayl
await m.answer_photo(FSInputFile("photos/cat.jpg"))
await m.answer_document(FSInputFile("docs/report.pdf"))

# 2) URL'dan
await m.answer_photo(URLInputFile("https://example.com/cat.jpg"))

# 3) Buffer (Python ob'ekt)
import io
buf = io.BytesIO(some_bytes)
await m.answer_document(
    BufferedInputFile(buf.getvalue(), filename="hisobot.pdf")
)

# 4) file_id (avval Telegram'dan kelgan — eng tez)
await m.answer_photo("AgACAgIAAxkBAAIBcGZ...")</code></pre>

<h4>BLOKA 2 — fayl qabul qilish</h4>

<pre><code>@dp.message(F.photo)
async def get_photo(m: Message):
    # m.photo — har xil o'lcham (oxiri — eng katta)
    photo = m.photo[-1]

    file_id = photo.file_id        # qayta yuborish uchun
    width = photo.width
    height = photo.height
    file_size = photo.file_size

    # Lokal'ga saqlash
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, f"downloads/{file_id}.jpg")

    await m.answer(f"📷 Saqlandi: {width}x{height}, {file_size} bayt")


@dp.message(F.document)
async def get_doc(m: Message):
    doc = m.document
    # doc.file_name, doc.mime_type, doc.file_size

    if doc.file_size &gt; 10 * 1024 * 1024:    # 10 MB
        await m.answer("Fayl juda katta (max 10 MB)")
        return

    file = await bot.get_file(doc.file_id)
    await bot.download_file(file.file_path, f"downloads/{doc.file_name}")
    await m.answer(f"📄 Saqlandi: {doc.file_name}")</code></pre>

<h4>BLOKA 3 — Bir nechta rasm (album)</h4>

<pre><code>from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import InputMediaPhoto

builder = MediaGroupBuilder(caption="📸 3 ta rasm")
builder.add_photo(FSInputFile("1.jpg"))
builder.add_photo(FSInputFile("2.jpg"))
builder.add_photo(FSInputFile("3.jpg"))

await bot.send_media_group(m.chat.id, builder.build())</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code># Har gal lokal fayldan qayta yuklash
@dp.message(Command("logo"))
async def logo(m: Message):
    await m.answer_photo(FSInputFile("static/logo.jpg"))   # ❌ har safar upload</code></pre>

<p><strong>Sabab:</strong> Har <code>FSInputFile</code> chaqiriqida Telegram'ga upload bo'ladi (sekin, traffic). To'g'risi — birinchi marta upload, <code>file_id</code> ni saqlash, keyingi safarlar — <code>file_id</code> bilan.</p>

<pre><code># Birinchi marta
msg = await bot.send_photo(chat_id, FSInputFile("logo.jpg"))
LOGO_FILE_ID = msg.photo[-1].file_id    # saqlang (config, DB)

# Keyingi safarlar — TEZ
await m.answer_photo(LOGO_FILE_ID)</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. InputFile turlari</h4>

<table>
<tr><th>Tur</th><th>Manba</th><th>Tezlik</th></tr>
<tr><td><code>FSInputFile("path")</code></td><td>Lokal fayl</td><td>Sekin (upload)</td></tr>
<tr><td><code>URLInputFile("url")</code></td><td>Internet</td><td>O'rta</td></tr>
<tr><td><code>BufferedInputFile(bytes, "name")</code></td><td>Python bytes</td><td>Sekin</td></tr>
<tr><td><code>"file_id"</code> (string)</td><td>Avval Telegram'da bo'lgan</td><td>Eng tez (instant)</td></tr>
</table>

<h4>2. Send metodlari</h4>

<pre><code>await m.answer_photo(photo, caption="...")
await m.answer_video(video, caption="...")
await m.answer_audio(audio, title="...", performer="...")
await m.answer_voice(voice)
await m.answer_document(doc, caption="...")
await m.answer_animation(gif)
await m.answer_sticker(sticker)
await m.answer_video_note(circle_video)
await m.answer_location(latitude=41.31, longitude=69.24)
await m.answer_contact(phone_number="+998...", first_name="Olim")</code></pre>

<h4>3. Content tur filter'lari</h4>

<pre><code>@dp.message(F.photo)      # rasm
@dp.message(F.video)       # video
@dp.message(F.voice)       # voice xabar
@dp.message(F.audio)       # audio fayl
@dp.message(F.document)    # hujjat (har xil tur)
@dp.message(F.sticker)
@dp.message(F.animation)   # gif

# MIME bilan
@dp.message(F.document.mime_type == "application/pdf")
async def pdf(m): ...

# Hajm bilan
@dp.message(F.document.file_size &gt; 10 * 1024 * 1024)
async def big_file(m: Message):
    await m.answer("Fayl 10 MB dan katta")</code></pre>

<h4>4. Fayl download — to'liq</h4>

<pre><code>@dp.message(F.photo)
async def save_photo(m: Message, session: AsyncSession):
    photo = m.photo[-1]

    # Telegram'dan file_path
    file = await bot.get_file(photo.file_id)

    # Local'ga
    local_path = f"uploads/{m.from_user.id}_{photo.file_unique_id}.jpg"
    await bot.download_file(file.file_path, local_path)

    # DB'ga path saqlash
    image = Image(
        user_id=m.from_user.id,
        path=local_path,
        file_id=photo.file_id,
    )
    session.add(image)
    await session.commit()

    await m.answer("✅ Rasm saqlandi")</code></pre>

<h4>5. Caption + reply_markup</h4>

<pre><code>await m.answer_photo(
    FSInputFile("pizza.jpg"),
    caption=(
        "🍕 <b>Pizza Margherita</b>\\n\\n"
        "Pomidor, mozzarella, basilik\\n"
        "Narx: <b>45,000 so'm</b>"
    ),
    reply_markup=order_kb,
)

# Caption tahrirlash
await call.message.edit_caption(
    caption="Yangi caption",
    reply_markup=new_kb,
)</code></pre>

<h4>6. Media group (album)</h4>

<pre><code>from aiogram.utils.media_group import MediaGroupBuilder

builder = MediaGroupBuilder(caption="📸 Loyiha screenshot'lari")
builder.add_photo(FSInputFile("ss1.jpg"))
builder.add_photo(FSInputFile("ss2.jpg"))
builder.add_video(FSInputFile("demo.mp4"))

await bot.send_media_group(m.chat.id, builder.build())</code></pre>

<p>Cheklov: max 10 ta media bir album'da. Caption — faqat birinchi media'ga.</p>

<h4>7. Voice → matn (bonus)</h4>

<pre><code># OpenAI Whisper bilan
@dp.message(F.voice)
async def voice_to_text(m: Message):
    file = await bot.get_file(m.voice.file_id)
    await bot.download_file(file.file_path, "voice.ogg")

    # Whisper API yoki openai-whisper local
    # text = whisper.transcribe("voice.ogg")

    await m.answer(f"📝 Yozdim: {text}")</code></pre>

<h4>8. Fayl yuborish tezligi — file_id pattern</h4>

<pre><code># config.py
class Files:
    LOGO = "AgACAgIAAxkBAA..."   # birinchi marta upload qilingach
    BANNER_NEW = "AgACAgIAAx..."
    MENU_PIZZA = "AgACAgIAAx..."

# birinchi marta yuborib file_id ni saqlash:
# msg = await bot.send_photo(YOUR_ID, FSInputFile("logo.jpg"))
# print(msg.photo[-1].file_id)
# va shu ID'ni config'ga</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ 4 ta InputFile turi (FS, URL, Buffered, file_id)</li>
<li>✅ <code>file_id</code> — eng tez (saqlang!)</li>
<li>✅ <code>answer_photo</code>, <code>_video</code>, <code>_document</code>, <code>_voice</code>, ...</li>
<li>✅ <code>F.photo</code>, <code>F.document.mime_type == "..."</code></li>
<li>✅ <code>bot.get_file</code> + <code>bot.download_file</code></li>
<li>✅ Media group (album) — 10 ta gacha</li>
<li>✅ Caption + reply_markup + edit_caption</li>
</ul>
"""

L8_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 8: Fayllar bilan ishlash
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    FSInputFile, URLInputFile, BufferedInputFile,
    InputMediaPhoto,
)
from aiogram.utils.media_group import MediaGroupBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# file_id cache (production'da DB)
SAVED_FILE_IDS: dict[str, str] = {}


# ─────────────────────────────────────────────────────────────────────
# 1) Boshlash
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"Fayllar bilan ishlash bo'lim:\\n"
        f"/photo — rasm yuborish\\n"
        f"/doc — PDF yuborish\\n"
        f"/album — 4 ta rasm albom\\n"
        f"/voice — voice xabar\\n\\n"
        f"Yoki menga rasm/voice/hujjat yuboring — saqlayman."
    )


# ─────────────────────────────────────────────────────────────────────
# 2) Yuborish — 4 ta variant
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("photo"))
async def cmd_photo(m: Message):
    # 1) Lokal fayl (sekin — har safar upload)
    # await m.answer_photo(FSInputFile("static/cat.jpg"))

    # 2) URL'dan
    await m.answer_photo(
        URLInputFile("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600"),
        caption="🐱 Mushuk (Unsplash'dan)",
    )


@dp.message(Command("doc"))
async def cmd_doc(m: Message):
    # Buffer'dan (yangi yaratilgan)
    import io
    text = "Bu — bot tomonidan yaratilgan PDF mazmuni.\\n\\n"
    text += "Production'da reportlab yoki weasyprint bilan."
    buf = io.BytesIO(text.encode())

    await m.answer_document(
        BufferedInputFile(buf.getvalue(), filename="hisobot.txt"),
        caption="📄 Hisobot tayyor",
    )


@dp.message(Command("album"))
async def cmd_album(m: Message):
    urls = [
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600",
        "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=600",
        "https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=600",
        "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=600",
    ]
    builder = MediaGroupBuilder(caption="📸 Mushuklar albomi")
    for i, url in enumerate(urls):
        builder.add_photo(URLInputFile(url))
    await bot.send_media_group(m.chat.id, builder.build())


@dp.message(Command("voice"))
async def cmd_voice(m: Message):
    # Demo — agar voice fayl bo'lsa
    voice_path = Path("static/voice.ogg")
    if voice_path.exists():
        await m.answer_voice(FSInputFile(voice_path))
    else:
        await m.answer("voice.ogg topilmadi. Faqat demo.")


# ─────────────────────────────────────────────────────────────────────
# 3) Qabul qilish — rasm
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.photo)
async def get_photo(m: Message):
    photo = m.photo[-1]    # eng katta versiyasi

    # Telegram'dan file_path
    file = await bot.get_file(photo.file_id)

    # Local'ga saqlash
    local_path = UPLOAD_DIR / f"{m.from_user.id}_{photo.file_unique_id}.jpg"
    await bot.download_file(file.file_path, str(local_path))

    # file_id ni saqlash (qayta yuborish uchun)
    SAVED_FILE_IDS[f"user_{m.from_user.id}_last_photo"] = photo.file_id

    await m.answer(
        f"📷 Rasm saqlandi!\\n"
        f"Eni × bo'yi: {photo.width} × {photo.height}\\n"
        f"Hajmi: {photo.file_size:,} bayt\\n"
        f"Yo'li: <code>{local_path}</code>\\n"
        f"file_id: <code>{photo.file_id[:30]}...</code>"
    )


# ─────────────────────────────────────────────────────────────────────
# 4) Qabul qilish — hujjat
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.document)
async def get_doc(m: Message):
    doc = m.document

    # Hajm tekshirish
    MAX_MB = 10
    if doc.file_size > MAX_MB * 1024 * 1024:
        await m.answer(f"❌ Fayl juda katta (max {MAX_MB} MB)")
        return

    # Mime tekshirish
    ALLOWED = {"application/pdf", "image/png", "image/jpeg", "text/plain"}
    if doc.mime_type not in ALLOWED:
        await m.answer(f"❌ Bu turdagi fayl qabul qilinmaydi: {doc.mime_type}")
        return

    file = await bot.get_file(doc.file_id)
    local_path = UPLOAD_DIR / f"{m.from_user.id}_{doc.file_name}"
    await bot.download_file(file.file_path, str(local_path))

    await m.answer(
        f"📄 Hujjat saqlandi!\\n"
        f"Nomi: <b>{doc.file_name}</b>\\n"
        f"Tur: {doc.mime_type}\\n"
        f"Hajmi: {doc.file_size:,} bayt"
    )


# ─────────────────────────────────────────────────────────────────────
# 5) Qabul qilish — voice
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.voice)
async def get_voice(m: Message):
    voice = m.voice
    if voice.duration > 60:
        await m.answer("❌ Voice 60 sekunddan ko'p — qisqaroq yuboring")
        return

    file = await bot.get_file(voice.file_id)
    local_path = UPLOAD_DIR / f"{m.from_user.id}_voice.ogg"
    await bot.download_file(file.file_path, str(local_path))

    await m.answer(
        f"🎤 Voice saqlandi!\\n"
        f"Davomiyligi: {voice.duration}s\\n"
        f"Hajmi: {voice.file_size:,} bayt\\n\\n"
        f"<i>Whisper bilan matn'ga aylantirish mumkin (bonus).</i>"
    )

    # Bonus: voice'ni qaytarib yuborish
    await m.answer_voice(FSInputFile(local_path), caption="🔄 Sizning voice'ingiz")


# ─────────────────────────────────────────────────────────────────────
# 6) PDF/PNG specific
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.document.mime_type == "application/pdf")
async def get_pdf(m: Message):
    # PDF — alohida handler
    doc = m.document
    await m.answer(f"📕 PDF qabul qilindi: {doc.file_name}")
    # Davom — yuqoridagi F.document handler ham ishlamaydi (filter aniqroq)


# ─────────────────────────────────────────────────────────────────────
# 7) Sticker
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.sticker)
async def get_sticker(m: Message):
    s = m.sticker
    await m.answer(
        f"😄 Sticker!\\n"
        f"Emoji: {s.emoji}\\n"
        f"Set: {s.set_name or '—'}\\n"
        f"Animatsiya: {'ha' if s.is_animated else 'yo\\'q'}\\n"
        f"Video: {'ha' if s.is_video else 'yo\\'q'}\\n"
        f"file_id: <code>{s.file_id[:30]}...</code>"
    )
    # Sticker'ni qaytarish
    await m.answer_sticker(s.file_id)


# ─────────────────────────────────────────────────────────────────────
# 8) Location
# ─────────────────────────────────────────────────────────────────────

@dp.message(F.location)
async def get_location(m: Message):
    loc = m.location
    await m.answer(
        f"📍 Joylashuv:\\n"
        f"Lat: <code>{loc.latitude}</code>\\n"
        f"Lon: <code>{loc.longitude}</code>\\n\\n"
        f"Google Maps: https://maps.google.com/?q={loc.latitude},{loc.longitude}"
    )

    # Bot ham joylashuv yuboradi (Toshkent markazi)
    await m.answer_location(latitude=41.3111, longitude=69.2797)


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L9_TEXT = """\
<h2>Guruh va kanal admin xususiyatlari</h2>

<pre class="mermaid">
flowchart LR
    BOT["Bot (admin)"] --> G["Guruh / Kanal"]
    G -->|new_chat_members| H1["Salomlashish"]
    G -->|left_chat_member| H2["Xayrlashish"]
    G -->|admin commands| H3["ban, mute, delete"]
    G -->|filter| H4["Anti-spam"]
</pre>

<p>Bu darsda — guruh va kanallarda bot'ning admin ishlari: salomlashish, kick/ban/mute, antispam, e'lonlar. Bularsiz Uzbek bot ekosistemasi yo'q (har telegram guruhda 1-2 ta admin bot).</p>

<p>Eslatma: bu funksiyalar bot guruh'da <strong>admin</strong> bo'lganida ishlaydi. Guruh sozlamalari → Admins → Add bot.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — yangi a'zoga salomlashish</h4>

<pre><code>from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER

@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER &gt;&gt; IS_MEMBER))
async def new_member(event: ChatMemberUpdated):
    user = event.new_chat_member.user
    await event.bot.send_message(
        event.chat.id,
        f"👋 <b>{user.full_name}</b>, xush kelibsiz!\\n"
        f"Guruh qoidalari uchun /rules"
    )</code></pre>

<h4>BLOKA 2 — ban / kick / mute</h4>

<pre><code>from datetime import timedelta
from aiogram.types import ChatPermissions

@dp.message(Command("ban"), F.chat.type.in_({"group", "supergroup"}))
async def ban(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling kerakli user xabariga, keyin /ban")

    target = m.reply_to_message.from_user
    await m.chat.ban(target.id)
    await m.answer(f"🔨 {target.full_name} ban qilindi")


@dp.message(Command("kick"))
async def kick(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    target = m.reply_to_message.from_user
    # Ban + darhol unban = kick
    await m.chat.ban(target.id)
    await m.chat.unban(target.id)
    await m.answer(f"👢 {target.full_name} kick qilindi")


@dp.message(Command("mute"))
async def mute(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    target = m.reply_to_message.from_user

    # 1 soat mute
    await m.chat.restrict(
        target.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=datetime.now() + timedelta(hours=1),
    )
    await m.answer(f"🔇 {target.full_name} 1 soatga mute qilindi")</code></pre>

<h4>BLOKA 3 — Anti-spam (link/forward'larni o'chirish)</h4>

<pre><code>SPAM_DOMAINS = {"t.me/spam_channel", "bad-site.com"}

@dp.message(F.text)
async def antispam(m: Message):
    if m.chat.type not in {"group", "supergroup"}:
        return

    text = m.text.lower()
    for domain in SPAM_DOMAINS:
        if domain in text:
            await m.delete()
            await m.answer(
                f"❌ {m.from_user.full_name}, link tashlash taqiqlangan!"
            )
            break


# Forward'larni cheklash
@dp.message(F.forward_from | F.forward_from_chat)
async def no_forward(m: Message):
    if m.chat.type in {"group", "supergroup"}:
        await m.delete()
        await m.answer("❌ Forward taqiqlangan")</code></pre>

<h3>🐛 Ataylab xato</h3>
<pre><code>@dp.message(Command("ban"))
async def ban(m: Message):
    target_id = int(m.text.split()[1])
    await m.chat.ban(target_id)</code></pre>

<p><strong>Sabab:</strong> Bot user_id ni bilmaydi (har user_id 9 raqamli — qiyin). Tipik telegram pattern — <strong>reply</strong> bilan. Yoki: <code>@username</code> bilan, lekin Telegram username'larni har gal API'dan olishi kerak.</p>

<pre><code># To'g'risi
@dp.message(Command("ban"))
async def ban(m: Message):
    if not m.reply_to_message:
        await m.answer("Avval kerakli user xabariga reply qiling, keyin /ban")
        return
    target = m.reply_to_message.from_user
    await m.chat.ban(target.id)</code></pre>

<h3>Endi tushuntiramiz</h3>

<h4>1. Chat turlari</h4>

<table>
<tr><th>Tur</th><th>Tavsif</th></tr>
<tr><td>private</td><td>DM bilan bot</td></tr>
<tr><td>group</td><td>Oddiy guruh (200 a'zo)</td></tr>
<tr><td>supergroup</td><td>Katta guruh (200,000 a'zo)</td></tr>
<tr><td>channel</td><td>Kanal (cheksiz a'zo, faqat admin yozadi)</td></tr>
</table>

<h4>2. Bot'ning guruh huquqlari</h4>

<p>BotFather'da: <code>/setprivacy</code> → DISABLE — bot guruhda har xabarni ko'radi (group commands uchun zarur).</p>

<p>Guruhda admin qilish: <strong>Group Settings → Administrators → Add admin → bot</strong>. Huquqlar tanlang:</p>

<ul>
<li>Delete messages</li>
<li>Ban users</li>
<li>Restrict users</li>
<li>Invite users via link</li>
<li>Manage topics (supergroup)</li>
</ul>

<h4>3. Asosiy admin metodlar</h4>

<pre><code># Ban
await m.chat.ban(user_id)
await m.chat.ban(user_id, until_date=...)   # vaqtinchalik

# Unban
await m.chat.unban(user_id)

# Restrict (mute)
await m.chat.restrict(
    user_id,
    permissions=ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
    ),
    until_date=datetime.now() + timedelta(hours=1),
)

# Promote — admin qilish
await m.chat.promote(
    user_id,
    can_delete_messages=True,
    can_restrict_members=True,
)

# Pin
await m.chat.pin(message_id)
await m.chat.unpin(message_id)

# Delete
await m.delete()
await bot.delete_message(chat_id, message_id)

# Set title/description
await m.chat.set_title("Yangi nom")
await m.chat.set_description("Tavsif...")</code></pre>

<h4>4. Member status events</h4>

<pre><code>from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, IS_ADMIN

@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER &gt;&gt; IS_MEMBER))
async def member_joined(event: ChatMemberUpdated): ...

@dp.chat_member(ChatMemberUpdatedFilter(IS_MEMBER &gt;&gt; IS_NOT_MEMBER))
async def member_left(event: ChatMemberUpdated): ...

@dp.chat_member(ChatMemberUpdatedFilter(IS_MEMBER &gt;&gt; IS_ADMIN))
async def became_admin(event: ChatMemberUpdated): ...</code></pre>

<p>Eslatma: <code>my_chat_member</code> — bot statusi o'zgargandagi event (admin qilingach, kick qilingach).</p>

<h4>5. Kanal'da post yuborish</h4>

<pre><code>CHANNEL_ID = -1001234567890   # @username dan ham mumkin

@dp.message(Command("post"), IsAdmin())
async def post_to_channel(m: Message, command: CommandObject):
    if not command.args:
        return await m.answer("/post matn")

    await bot.send_message(CHANNEL_ID, command.args)
    await m.answer("✅ Kanalga yuborildi")</code></pre>

<h4>6. CAPTCHA — yangi a'zoni tekshirish</h4>

<pre><code># Yangi a'zo — mute, matematik savol, javob bersa unmute
@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER &gt;&gt; IS_MEMBER))
async def captcha(event: ChatMemberUpdated):
    user = event.new_chat_member.user

    # Mute
    await event.chat.restrict(user.id, permissions=ChatPermissions(...))

    # Inline keyboard: "Men robot emasman" tugmasi
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ Men robot emasman",
        callback_data=f"captcha:{user.id}",
    )
    await event.bot.send_message(
        event.chat.id,
        f"👋 {user.full_name}, robot emasligingizni tasdiqlang:",
        reply_markup=kb.as_markup(),
    )


@dp.callback_query(F.data.startswith("captcha:"))
async def cb_captcha(call: CallbackQuery):
    target_id = int(call.data.split(":")[1])
    if call.from_user.id != target_id:
        return await call.answer("Bu sizning emas", show_alert=True)

    # Unmute
    await call.message.chat.restrict(
        target_id,
        permissions=ChatPermissions(can_send_messages=True, ...),
    )
    await call.message.delete()
    await call.answer("✅ Tasdiqlandi!")</code></pre>

<h4>7. Ko'p tilli antispam</h4>

<pre><code>import re

URL_PATTERN = re.compile(r"https?://\\S+|t\\.me/\\S+")
PHONE_PATTERN = re.compile(r"\\+?\\d{10,15}")

@dp.message(F.text)
async def filter_spam(m: Message):
    if m.chat.type not in {"group", "supergroup"}:
        return

    # Link
    if URL_PATTERN.search(m.text):
        if m.from_user.id not in ALLOWED_USERS:
            await m.delete()
            return

    # Telefon
    if PHONE_PATTERN.search(m.text):
        await m.delete()
        return</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Bot guruhda admin bo'lish — privacy DISABLE</li>
<li>✅ <code>m.chat.ban/unban/restrict/promote</code></li>
<li>✅ Reply pattern (admin commands)</li>
<li>✅ ChatMemberUpdated event — yangi a'zo, chiqib ketgan</li>
<li>✅ CAPTCHA pattern — robot tekshirish</li>
<li>✅ Anti-spam: link, forward, telefon</li>
<li>✅ Kanal'ga bot orqali post</li>
</ul>
"""

L9_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 9: Guruh va kanal admin
# ════════════════════════════════════════════════════════════════════
#
# Sozlash:
#   1) BotFather'da /setprivacy → DISABLE
#   2) Bot'ni guruhga admin qilish (Delete messages, Ban, Restrict)
# ════════════════════════════════════════════════════════════════════

import asyncio
import os
import logging
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import (
    Command, CommandStart, BaseFilter,
    ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER, IS_ADMIN,
)
from aiogram.types import (
    Message, CallbackQuery, ChatMemberUpdated, ChatPermissions,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ─────────────────────────────────────────────────────────────────────
# Filter — faqat guruh'larda
# ─────────────────────────────────────────────────────────────────────

class IsGroup(BaseFilter):
    async def __call__(self, event) -> bool:
        chat = getattr(event, "chat", None) or event.message.chat
        return chat.type in {"group", "supergroup"}


class IsGroupAdmin(BaseFilter):
    # User guruh'da admin bo'lsa.
    async def __call__(self, m: Message) -> bool:
        if m.chat.type not in {"group", "supergroup"}:
            return False
        member = await bot.get_chat_member(m.chat.id, m.from_user.id)
        return member.status in {"creator", "administrator"}


# ─────────────────────────────────────────────────────────────────────
# Yangi a'zo (welcome + CAPTCHA)
# ─────────────────────────────────────────────────────────────────────

@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def member_joined(event: ChatMemberUpdated):
    user = event.new_chat_member.user

    if user.is_bot:
        return

    # Mute (CAPTCHA o'tguncha)
    try:
        await event.chat.restrict(
            user.id,
            permissions=ChatPermissions(can_send_messages=False),
        )
    except Exception as e:
        logging.warning(f"Restrict xato: {e}")
        return

    # CAPTCHA inline
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Men robot emasman", callback_data=f"captcha:{user.id}")
    await event.bot.send_message(
        event.chat.id,
        f"👋 <b>{user.full_name}</b>, xush kelibsiz!\\n\\n"
        f"Robot emasligingizni tasdiqlang (5 daqiqa ichida):",
        reply_markup=kb.as_markup(),
    )


@dp.callback_query(F.data.startswith("captcha:"))
async def cb_captcha(call: CallbackQuery):
    target_id = int(call.data.split(":")[1])

    if call.from_user.id != target_id:
        return await call.answer("Bu sizga emas 🤖", show_alert=True)

    # Unmute
    await bot.restrict_chat_member(
        call.message.chat.id,
        target_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_other_messages=True,
        ),
    )
    await call.message.delete()
    await call.message.answer(
        f"✅ <b>{call.from_user.full_name}</b>, xush kelibsiz!"
    )
    await call.answer()


# ─────────────────────────────────────────────────────────────────────
# Chiqib ketganlar
# ─────────────────────────────────────────────────────────────────────

@dp.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def member_left(event: ChatMemberUpdated):
    user = event.old_chat_member.user
    if user.is_bot:
        return
    await event.bot.send_message(
        event.chat.id,
        f"👋 <b>{user.full_name}</b> guruhdan chiqdi"
    )


# ─────────────────────────────────────────────────────────────────────
# Admin buyruqlari
# ─────────────────────────────────────────────────────────────────────

@dp.message(Command("ban"), IsGroupAdmin())
async def cmd_ban(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling kerakli xabariga, keyin /ban")

    target = m.reply_to_message.from_user
    try:
        await m.chat.ban(target.id)
        await m.answer(f"🔨 <b>{target.full_name}</b> ban qilindi")
    except Exception as e:
        await m.answer(f"❌ Xato: {e}")


@dp.message(Command("unban"), IsGroupAdmin())
async def cmd_unban(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    target = m.reply_to_message.from_user
    await m.chat.unban(target.id)
    await m.answer(f"✅ <b>{target.full_name}</b> unban qilindi")


@dp.message(Command("kick"), IsGroupAdmin())
async def cmd_kick(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    target = m.reply_to_message.from_user
    await m.chat.ban(target.id)
    await m.chat.unban(target.id)   # ban + unban = kick
    await m.answer(f"👢 <b>{target.full_name}</b> kick qilindi")


@dp.message(Command("mute"), IsGroupAdmin())
async def cmd_mute(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")

    parts = m.text.split()
    minutes = 60   # default
    if len(parts) > 1 and parts[1].isdigit():
        minutes = int(parts[1])

    target = m.reply_to_message.from_user
    await m.chat.restrict(
        target.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=datetime.now() + timedelta(minutes=minutes),
    )
    await m.answer(f"🔇 <b>{target.full_name}</b> {minutes} daqiqaga mute")


@dp.message(Command("unmute"), IsGroupAdmin())
async def cmd_unmute(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    target = m.reply_to_message.from_user
    await m.chat.restrict(
        target.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
        ),
    )
    await m.answer(f"🔊 <b>{target.full_name}</b> unmute")


@dp.message(Command("pin"), IsGroupAdmin())
async def cmd_pin(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    await m.reply_to_message.pin()
    await m.answer("📌 Pinlandi")


@dp.message(Command("del"), IsGroupAdmin())
async def cmd_del(m: Message):
    if not m.reply_to_message:
        return await m.answer("Reply qiling")
    await m.reply_to_message.delete()
    await m.delete()    # /del buyrug'ining o'zini ham


# ─────────────────────────────────────────────────────────────────────
# Anti-spam
# ─────────────────────────────────────────────────────────────────────

URL_PATTERN = re.compile(r"https?://\\S+|t\\.me/\\S+|telegram\\.me/\\S+", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\\+?\\d{9,15}")
SPAM_WORDS = {"casino", "loan", "обмен", "арбитраж"}

# Adminlar uchun ruxsat
ALLOWED_USERS: set[int] = set()


@dp.message(F.text, IsGroup())
async def antispam(m: Message):
    if m.from_user.id in ALLOWED_USERS:
        return

    # Admin'ni e'tibordan tashqari
    member = await bot.get_chat_member(m.chat.id, m.from_user.id)
    if member.status in {"creator", "administrator"}:
        return

    text = m.text.lower()
    reasons = []

    if URL_PATTERN.search(m.text):
        reasons.append("link")
    if PHONE_PATTERN.search(m.text):
        reasons.append("telefon")
    if any(w in text for w in SPAM_WORDS):
        reasons.append("taqiqlangan so'z")

    if reasons:
        await m.delete()
        warn = await m.chat.send_message(
            f"⚠️ <b>{m.from_user.full_name}</b>, xabaringiz o'chirildi: "
            f"{', '.join(reasons)}"
        )
        # Warning'ni 10 sekunddan keyin o'chirish
        await asyncio.sleep(10)
        try:
            await warn.delete()
        except Exception:
            pass


# Forward'larni cheklash (faqat oddiy user'lar)
@dp.message(F.forward_from | F.forward_from_chat, IsGroup())
async def no_forward(m: Message):
    member = await bot.get_chat_member(m.chat.id, m.from_user.id)
    if member.status in {"creator", "administrator"}:
        return
    await m.delete()


# ─────────────────────────────────────────────────────────────────────
# Yordamchi
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    if m.chat.type == "private":
        await m.answer(
            "Bu — guruh boshqaruvchi bot.\\n\\n"
            "Meni guruhga qo'shing va admin qiling:\\n"
            "• Delete messages\\n"
            "• Ban users\\n"
            "• Restrict users"
        )
    else:
        await m.answer(
            "🛠 <b>Buyruqlar (admin):</b>\\n\\n"
            "/ban — reply bilan ban\\n"
            "/kick — reply bilan kick\\n"
            "/mute &lt;daqiqa&gt; — reply bilan mute\\n"
            "/unmute — reply bilan unmute\\n"
            "/pin — reply bilan pin\\n"
            "/del — reply bilan o'chirish\\n\\n"
            "Anti-spam: link, telefon, taqiqlangan so'zlar — avtomatik o'chirish"
        )


@dp.message(Command("rules"))
async def cmd_rules(m: Message):
    await m.answer(
        "📜 <b>Guruh qoidalari</b>\\n\\n"
        "1. Hurmat — har user'ga\\n"
        "2. Spam, reklama, link taqiqlangan\\n"
        "3. Forward taqiqlangan\\n"
        "4. Off-topic — alohida guruhga\\n"
        "5. NSFW — taqiqlangan\\n\\n"
        "Buzilganda — mute → kick → ban"
    )


# ─────────────────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    # chat_member updates olish uchun:
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":
    asyncio.run(main())
"""
R3_TEXT = """\
<h2>R3 — Modul 3 takrorlash: Mini-shop bot</h2>

<p>Modul 3 ning hammasi birga — <strong>DB + Files + Admin features</strong>. To'liq mini e-commerce bot: mahsulot katalog, savatcha, buyurtma, admin paneli.</p>

<h3>Loyihaning maqsadi</h3>

<p>Restoran/dukon uchun bot. Foydalanuvchi:</p>
<ul>
<li>Katalog ko'radi (kategoriya bo'yicha)</li>
<li>Mahsulot rasmlari va tafsilotlari</li>
<li>Savatchaga qo'shadi</li>
<li>Buyurtma beradi (telefon + manzil)</li>
</ul>

<p>Admin:</p>
<ul>
<li>Yangi mahsulot qo'shadi (rasm, narx, tavsif)</li>
<li>Mahsulotlarni o'chiradi/tahrirlaydi</li>
<li>Yangi buyurtmalarni real-time qabul qiladi</li>
<li>Statistika ko'radi</li>
</ul>

<h3>Sxema</h3>

<table>
<tr><th>Jadval</th><th>Maydonlar</th></tr>
<tr><td><code>categories</code></td><td>id, nomi</td></tr>
<tr><td><code>products</code></td><td>id, category_id (FK), nomi, narx, tavsif, photo_id, mavjud</td></tr>
<tr><td><code>users</code></td><td>id, ism, telefon, manzil</td></tr>
<tr><td><code>cart_items</code></td><td>id, user_id, product_id, miqdor</td></tr>
<tr><td><code>orders</code></td><td>id, user_id, summa, holat, sana</td></tr>
<tr><td><code>order_items</code></td><td>id, order_id, product_id, miqdor, narx_birlik</td></tr>
</table>

<h3>Topshiriqlar</h3>

<h4>Vazifa 1 — DB + models</h4>
<ul>
<li>SQLAlchemy async + 6 ta model</li>
<li>Relationship'lar (Category.products, Order.items)</li>
<li>init_db() — birinchi marta jadvallar</li>
<li>Seed data — 2 ta kategoriya, 4-6 mahsulot</li>
</ul>

<h4>Vazifa 2 — Katalog (user uchun)</h4>
<ul>
<li>/menu — kategoriyalar (inline)</li>
<li>Kategoriya tanlangach — mahsulotlar (har biri inline tugma)</li>
<li>Mahsulot tanlangach — rasm + narx + tavsif + "Savatga qo'shish"</li>
</ul>

<h4>Vazifa 3 — Savatcha</h4>
<ul>
<li>"➕ Savatga" tugma — DB'ga qo'shish (miqdor +1)</li>
<li>/cart — savat ko'rinishi (mahsulot ro'yxati + jami summa)</li>
<li>Har mahsulot uchun [➖ -1] [➕ +1] [🗑] tugmalari</li>
<li>"✅ Buyurtma berish" tugma</li>
</ul>

<h4>Vazifa 4 — Buyurtma berish (FSM)</h4>
<ul>
<li>Telefon (contact tugma)</li>
<li>Manzil (matn yoki location)</li>
<li>Izoh (ixtiyoriy)</li>
<li>Tasdiqlash — summa + ma'lumotlar</li>
<li>Saqlash → orders + order_items, savat tozalanadi</li>
</ul>

<h4>Vazifa 5 — Admin paneli</h4>
<ul>
<li><code>/add</code> — yangi mahsulot (FSM: kategoriya → nom → narx → tavsif → rasm)</li>
<li><code>/products</code> — barcha mahsulotlar (pagination, [🗑] tugma)</li>
<li><code>/orders</code> — yangi buyurtmalar (inline: [✅ Qabul][❌ Bekor])</li>
<li>Real-time xabar adminga yangi buyurtma kelganda</li>
</ul>

<h4>Vazifa 6 — UX</h4>
<ul>
<li>file_id cache — rasm bir marta upload</li>
<li>Chiroyli format'lash (HTML, emoji)</li>
<li>3 ta holat: yo'q mahsulot, bo'sh savat, xato</li>
</ul>

<h3>🐛 Ataylab qiyin: 2 ta foydalanuvchi bir vaqtda</h3>

<p>2 ta user oxirgi pizza'ni bir vaqtda buyurtma qildi (stock = 1). Race condition. Yechim — DB transaction bilan stock'ni tekshirib kamaytirish (atomic update).</p>

<h3>Yechim sketch</h3>

<details>
<summary>Asosiy strukturasi — avval o'zingiz urinib ko'ring!</summary>
<pre><code>class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    nomi: Mapped[str] = mapped_column(String(50))
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    nomi: Mapped[str] = mapped_column(String(100))
    narx: Mapped[float] = mapped_column()
    tavsif: Mapped[str] = mapped_column(String(500))
    photo_id: Mapped[str | None] = mapped_column(String(200))   # file_id
    mavjud: Mapped[bool] = mapped_column(default=True)

    category: Mapped["Category"] = relationship(back_populates="products")


# Inline keyboard'lar
def categories_kb(cats):
    kb = InlineKeyboardBuilder()
    for c in cats:
        kb.button(text=c.nomi, callback_data=f"cat:{c.id}")
    kb.adjust(2)
    return kb.as_markup()

def products_kb(products):
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(
            text=f"{p.nomi} — {p.narx:,.0f}",
            callback_data=f"prod:{p.id}",
        )
    kb.button(text="⬅️ Kategoriyalar", callback_data="cats")
    kb.adjust(1)
    return kb.as_markup()

# ... handler'lar</code></pre>
</details>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Modul 3 ning hammasi: DB + Files + Admin birga</li>
<li>✅ E-commerce sxema (6 ta jadval)</li>
<li>✅ Savatcha state DB'da</li>
<li>✅ FSM bilan checkout</li>
<li>✅ Admin uchun real-time notification</li>
<li>✅ file_id caching pattern</li>
<li>✅ Race condition haqida tushuncha</li>
</ul>
"""

R3_CODE = """\
# ════════════════════════════════════════════════════════════════════
# REVISION 3: Mini-shop bot
# Modul 3: DB + Files + Admin birga
# ════════════════════════════════════════════════════════════════════
#
# Bu fayl — to'liq strukturani ko'rsatadi.
# Production'da modullarga ajrating: handlers/, services/, db/, keyboards/

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, BaseMiddleware, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InputMediaPhoto,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from sqlalchemy import BigInteger, String, ForeignKey, Float, Integer, Boolean, DateTime, select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

load_dotenv()
logging.basicConfig(level=logging.INFO)

ADMINS = {int(x) for x in os.getenv("ADMIN_IDS", "111").split(",") if x.strip()}

# ─────────────────────────────────────────────────────────────────────
# DB
# ─────────────────────────────────────────────────────────────────────

engine = create_async_engine("sqlite+aiosqlite:///shop.db", echo=False)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    nomi: Mapped[str] = mapped_column(String(50))
    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    nomi: Mapped[str] = mapped_column(String(100))
    narx: Mapped[float] = mapped_column(Float)
    tavsif: Mapped[str] = mapped_column(String(500), default="")
    photo_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mavjud: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["Category"] = relationship(back_populates="products")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ism: Mapped[str] = mapped_column(String(50))
    telefon: Mapped[str | None] = mapped_column(String(20), nullable=True)
    manzil: Mapped[str | None] = mapped_column(String(200), nullable=True)


class CartItem(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    miqdor: Mapped[int] = mapped_column(Integer, default=1)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    summa: Mapped[float] = mapped_column(Float)
    holat: Mapped[str] = mapped_column(String(20), default="kutmoqda")
    telefon: Mapped[str] = mapped_column(String(20))
    manzil: Mapped[str] = mapped_column(String(200))
    izoh: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sana: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    miqdor: Mapped[int] = mapped_column(Integer)
    narx_birlik: Mapped[float] = mapped_column(Float)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed
    async with SessionMaker() as s:
        if await s.scalar(select(func.count(Category.id))) == 0:
            cat1 = Category(nomi="🍕 Pizza")
            cat2 = Category(nomi="🥤 Ichimliklar")
            s.add_all([
                cat1, cat2,
                Product(category=cat1, nomi="Margherita", narx=45000, tavsif="Klassik"),
                Product(category=cat1, nomi="Pepperoni", narx=55000, tavsif="O'tkir"),
                Product(category=cat2, nomi="Coca-Cola 1L", narx=10000, tavsif="Sovuq"),
                Product(category=cat2, nomi="Suv 1L", narx=5000, tavsif="Toza"),
            ])
            await s.commit()


# ─────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with SessionMaker() as session:
            data["session"] = session
            return await handler(event, data)


class UserCtxMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not event.from_user:
            return await handler(event, data)
        session: AsyncSession = data["session"]
        user = await session.get(User, event.from_user.id)
        if not user:
            user = User(id=event.from_user.id, ism=event.from_user.first_name)
            session.add(user)
            await session.commit()
        data["user"] = user
        return await handler(event, data)


# ─────────────────────────────────────────────────────────────────────
# Bot / Dispatcher
# ─────────────────────────────────────────────────────────────────────

bot = Bot(token=os.getenv("BOT_TOKEN"),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.update.middleware(DBMiddleware())
dp.update.middleware(UserCtxMiddleware())


# ─────────────────────────────────────────────────────────────────────
# FSM
# ─────────────────────────────────────────────────────────────────────

class CheckoutStates(StatesGroup):
    telefon = State()
    manzil = State()
    izoh = State()
    confirm = State()


class AddProductStates(StatesGroup):
    category = State()
    nomi = State()
    narx = State()
    tavsif = State()
    photo = State()


# ─────────────────────────────────────────────────────────────────────
# Klaviaturalar
# ─────────────────────────────────────────────────────────────────────

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🍕 Menyu")
    kb.button(text="🛒 Savatcha")
    kb.button(text="📞 Bog'lanish")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def categories_kb(cats: list[Category]):
    kb = InlineKeyboardBuilder()
    for c in cats:
        kb.button(text=c.nomi, callback_data=f"cat:{c.id}")
    kb.adjust(1)
    return kb.as_markup()


def products_kb(products: list[Product], category_id: int):
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(
            text=f"{p.nomi} — {p.narx:,.0f}",
            callback_data=f"prod:{p.id}",
        )
    kb.button(text="⬅️ Kategoriyalar", callback_data="back_cats")
    kb.adjust(1)
    return kb.as_markup()


def product_card_kb(product_id: int, category_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Savatga qo'shish", callback_data=f"add:{product_id}")
    kb.button(text="⬅️ Orqaga", callback_data=f"cat:{category_id}")
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items_with_products):
    kb = InlineKeyboardBuilder()
    for ci, prod in items_with_products:
        kb.button(text=f"➖ {prod.nomi}", callback_data=f"dec:{ci.id}")
        kb.button(text=f"{ci.miqdor}", callback_data="noop")
        kb.button(text="➕", callback_data=f"inc:{ci.id}")
        kb.button(text="🗑", callback_data=f"del:{ci.id}")
    kb.adjust(4)
    kb.button(text="✅ Buyurtma berish", callback_data="checkout")
    kb.button(text="🗑 Savatni tozalash", callback_data="clear_cart")
    kb.adjust(*([4] * len(items_with_products)), 1, 1)
    return kb.as_markup()


# ─────────────────────────────────────────────────────────────────────
# Boshlash
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message, user: User):
    await m.answer(
        f"Salom, <b>{user.ism}</b>!\\n"
        f"Bizning restoranga xush kelibsiz 🍽\\n\\n"
        f"Menyudan tanlang:",
        reply_markup=main_menu(),
    )


@dp.message(F.text == "🍕 Menyu")
async def show_categories(m: Message, session: AsyncSession):
    result = await session.execute(select(Category))
    cats = list(result.scalars())
    if not cats:
        return await m.answer("Hozircha menyu yo'q")
    await m.answer("Kategoriya tanlang:", reply_markup=categories_kb(cats))


@dp.callback_query(F.data.startswith("cat:"))
async def show_products(call: CallbackQuery, session: AsyncSession):
    cat_id = int(call.data.split(":")[1])
    result = await session.execute(
        select(Product).where(Product.category_id == cat_id, Product.mavjud == True)
    )
    products = list(result.scalars())
    if not products:
        await call.answer("Bo'sh", show_alert=True)
        return
    cat = await session.get(Category, cat_id)
    await call.message.edit_text(
        f"<b>{cat.nomi}</b>\\n\\nMahsulot tanlang:",
        reply_markup=products_kb(products, cat_id),
    )
    await call.answer()


@dp.callback_query(F.data == "back_cats")
async def back_cats(call: CallbackQuery, session: AsyncSession):
    result = await session.execute(select(Category))
    cats = list(result.scalars())
    await call.message.edit_text("Kategoriya tanlang:", reply_markup=categories_kb(cats))
    await call.answer()


@dp.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery, session: AsyncSession):
    prod_id = int(call.data.split(":")[1])
    prod = await session.get(Product, prod_id)
    if not prod:
        return await call.answer("Topilmadi", show_alert=True)

    caption = (
        f"<b>{prod.nomi}</b>\\n\\n"
        f"{prod.tavsif}\\n\\n"
        f"💰 Narx: <b>{prod.narx:,.0f}</b> so'm"
    )

    if prod.photo_id:
        await call.message.delete()
        await call.message.answer_photo(
            prod.photo_id,
            caption=caption,
            reply_markup=product_card_kb(prod.id, prod.category_id),
        )
    else:
        await call.message.edit_text(
            caption,
            reply_markup=product_card_kb(prod.id, prod.category_id),
        )
    await call.answer()


# ─────────────────────────────────────────────────────────────────────
# Savatcha
# ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("add:"))
async def add_to_cart(call: CallbackQuery, user: User, session: AsyncSession):
    prod_id = int(call.data.split(":")[1])

    # Mavjudmi tekshirish
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == prod_id)
    )
    item = result.scalar_one_or_none()
    if item:
        item.miqdor += 1
    else:
        session.add(CartItem(user_id=user.id, product_id=prod_id, miqdor=1))
    await session.commit()
    await call.answer("✅ Savatga qo'shildi", show_alert=False)


@dp.message(F.text == "🛒 Savatcha")
async def show_cart(m: Message, user: User, session: AsyncSession):
    result = await session.execute(
        select(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .where(CartItem.user_id == user.id)
    )
    items = list(result.all())
    if not items:
        return await m.answer("🛒 Savat bo'sh", reply_markup=main_menu())

    lines = ["🛒 <b>Savatcha:</b>\\n"]
    jami = 0.0
    for ci, prod in items:
        sub = prod.narx * ci.miqdor
        jami += sub
        lines.append(f"• {prod.nomi} × {ci.miqdor} = {sub:,.0f}")
    lines.append(f"\\n💰 Jami: <b>{jami:,.0f}</b> so'm")

    await m.answer("\\n".join(lines), reply_markup=cart_kb(items))


@dp.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery, user: User, session: AsyncSession):
    await session.execute(
        CartItem.__table__.delete().where(CartItem.user_id == user.id)
    )
    await session.commit()
    await call.message.delete()
    await call.answer("✅ Savat tozalandi")


# ─────────────────────────────────────────────────────────────────────
# Checkout (FSM)
# ─────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "checkout")
async def checkout_start(call: CallbackQuery, user: User, state: FSMContext):
    await state.set_state(CheckoutStates.telefon)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True,
    )
    await call.message.answer(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=kb,
    )
    await call.answer()


@dp.message(CheckoutStates.telefon, F.contact | F.text)
async def get_telefon(m: Message, state: FSMContext):
    phone = m.contact.phone_number if m.contact else m.text.strip()
    await state.update_data(telefon=phone)
    await state.set_state(CheckoutStates.manzil)
    await m.answer("📍 Manzilni yozing:", reply_markup=ReplyKeyboardRemove())


@dp.message(CheckoutStates.manzil, F.text)
async def get_manzil(m: Message, state: FSMContext):
    await state.update_data(manzil=m.text.strip())
    await state.set_state(CheckoutStates.izoh)
    await m.answer("💬 Izoh (yoki /skip):")


@dp.message(CheckoutStates.izoh, F.text)
async def get_izoh(m: Message, state: FSMContext, user: User, session: AsyncSession):
    izoh = None if m.text == "/skip" else m.text
    data = await state.get_data()

    # Cart -> Order
    result = await session.execute(
        select(CartItem, Product)
        .join(Product)
        .where(CartItem.user_id == user.id)
    )
    items = list(result.all())
    if not items:
        await state.clear()
        return await m.answer("Savat bo'sh", reply_markup=main_menu())

    summa = sum(p.narx * ci.miqdor for ci, p in items)
    order = Order(
        user_id=user.id, summa=summa, telefon=data["telefon"],
        manzil=data["manzil"], izoh=izoh,
    )
    session.add(order)
    await session.flush()

    for ci, prod in items:
        session.add(OrderItem(
            order_id=order.id, product_id=prod.id,
            miqdor=ci.miqdor, narx_birlik=prod.narx,
        ))

    # Clear cart
    await session.execute(
        CartItem.__table__.delete().where(CartItem.user_id == user.id)
    )
    await session.commit()
    await state.clear()

    await m.answer(
        f"✅ <b>Buyurtma #{order.id} qabul qilindi!</b>\\n\\n"
        f"Jami: <b>{summa:,.0f}</b> so'm\\n"
        f"Tez orada bog'lanamiz 📞",
        reply_markup=main_menu(),
    )

    # Adminlarga
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 Yangi buyurtma #{order.id}\\n"
                f"User: {user.ism}\\n"
                f"Tel: {data['telefon']}\\n"
                f"Manzil: {data['manzil']}\\n"
                f"Summa: {summa:,.0f}",
            )
        except Exception as e:
            logging.error(f"Admin xabar: {e}")


# ─────────────────────────────────────────────────────────────────────
# Admin paneli (qisqartirilgan — to'liq versiya capstone'da)
# ─────────────────────────────────────────────────────────────────────

class IsAdmin(BaseFilter):
    async def __call__(self, event) -> bool:
        return event.from_user.id in ADMINS


@dp.message(Command("orders"), IsAdmin())
async def admin_orders(m: Message, session: AsyncSession):
    result = await session.execute(
        select(Order).where(Order.holat == "kutmoqda").order_by(Order.sana.desc()).limit(10)
    )
    orders = list(result.scalars())
    if not orders:
        return await m.answer("Yangi buyurtma yo'q")

    for o in orders:
        await m.answer(
            f"🧾 #{o.id} — {o.summa:,.0f} so'm\\n"
            f"📞 {o.telefon}\\n"
            f"📍 {o.manzil}\\n"
            f"⏰ {o.sana:%Y-%m-%d %H:%M}"
        )


async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
"""
L10_TEXT = """\
<h2>Webhook va deploy</h2>

<pre class="mermaid">
flowchart LR
    DEV["Lokal: polling\nDevelopment"]
    PROD["Production: webhook\nRailway / VPS"]
    DEV -.->|deploy| PROD
    TG["Telegram"] -->|POST update| PROD
    PROD -->|reply| TG
</pre>

<p>9 darsda hammasi polling bilan edi — bot doim Telegram'dan so'rab turardi "yangi update bormi?". Production'da bu sekin va resurs ko'p sarflaydi. <strong>Webhook</strong> — bot HTTPS server, Telegram update bo'lganda bot'ga to'g'ridan-to'g'ri push qiladi.</p>

<p>Plus — botni qaerda hostlashni o'rganamiz: <strong>Railway</strong> (eng oson), VPS, yoki Docker.</p>

<h3>🏆 5 daqiqada g'alaba</h3>

<h4>BLOKA 1 — Webhook variant (oddiy)</h4>

<pre><code># bot.py
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler, setup_application,
)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")    # https://your-app.up.railway.app/webhook
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "any-random-string")
WEBHOOK_PATH = "/webhook"


async def on_startup(bot: Bot):
    await bot.set_webhook(
        url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True,
    )

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    main()</code></pre>

<h4>BLOKA 2 — env va requirements</h4>

<pre><code># .env (PRODUCTION'da Railway/Render — environment variables tab'da)
BOT_TOKEN=7234567890:AAH...
WEBHOOK_URL=https://your-bot.up.railway.app
WEBHOOK_SECRET=random-32-char-string
DB_URL=postgresql+asyncpg://user:pass@host:5432/dbname
ADMIN_IDS=111,222,333


# requirements.txt
aiogram&gt;=3.0
aiohttp
python-dotenv
sqlalchemy[asyncio]
asyncpg


# Procfile (Railway uchun)
web: python bot.py</code></pre>

<h4>BLOKA 3 — Railway'da deploy (5 daqiqa)</h4>

<ol>
<li><a href="https://railway.app">railway.app</a> ga GitHub bilan kirish</li>
<li>"New Project" → "Deploy from GitHub repo"</li>
<li>Repo tanlash</li>
<li>Variables tab'da: BOT_TOKEN, WEBHOOK_SECRET</li>
<li>"Settings" → "Generate Domain" → public URL paydo bo'ladi</li>
<li>WEBHOOK_URL'ni ham qo'shing (Generate qilingan URL)</li>
<li>Deploy avtomatik boshlandi</li>
</ol>

<p>Logs tab'da loglar ko'rinadi. Bot'ga /start yuborib tekshiring.</p>

<h3>🐛 Ataylab xato</h3>
<pre><code>BOT_TOKEN = "7234567890:AAH..."     # ❌ kodda
# yoki
WEBHOOK_URL = "http://example.com"  # ❌ HTTPS emas</code></pre>

<p><strong>Sabablar:</strong></p>
<ol>
<li><strong>Kodda token</strong> — GitHub'ga push bo'lsa, botlar topadi va o'g'irlaydi.</li>
<li><strong>HTTP webhook</strong> — Telegram faqat HTTPS qabul qiladi.</li>
</ol>

<p>Yechim — har doim <strong>env variables</strong> va Railway/Render avtomatik HTTPS beradi.</p>

<h3>Endi tushuntiramiz</h3>

<h4>1. Polling vs Webhook — to'liq taqqoslash</h4>

<table>
<tr><th></th><th>Polling</th><th>Webhook</th></tr>
<tr><td>Dev'da</td><td>✅ oson</td><td>Murakkab (ngrok kerak)</td></tr>
<tr><td>Production'da</td><td>Sekin, resurs ko'p</td><td>✅ tez, kam resurs</td></tr>
<tr><td>HTTPS kerakmi</td><td>Yo'q</td><td>Ha (majburiy)</td></tr>
<tr><td>Latency</td><td>1-2s</td><td>&lt; 200ms</td></tr>
<tr><td>Server uptime</td><td>Bot mumkin uxlab qolish</td><td>24/7 kerak</td></tr>
</table>

<h4>2. Hosting variantlari</h4>

<table>
<tr><th>Platform</th><th>Bepul tier</th><th>Sozlash</th></tr>
<tr><td><strong>Railway</strong></td><td>$5 credit/oy</td><td>Eng oson (tavsiya)</td></tr>
<tr><td><strong>Render</strong></td><td>750 soat/oy</td><td>Oson, sleep mode bor</td></tr>
<tr><td><strong>Fly.io</strong></td><td>Hobby tier</td><td>Docker bilan</td></tr>
<tr><td><strong>VPS</strong> (Hetzner, DO)</td><td>$5/oy dan</td><td>Qiyin, lekin to'liq nazorat</td></tr>
<tr><td><strong>Heroku</strong></td><td>Bepul tier yo'q endi</td><td>—</td></tr>
</table>

<h4>3. Webhook URL — security</h4>

<pre><code># 1) WEBHOOK_SECRET — random string
# Telegram har request'ga shu token yuboradi (X-Telegram-Bot-Api-Secret-Token header)
# aiogram avtomatik tekshiradi.

# 2) Webhook path — random
WEBHOOK_PATH = "/abc-secret-123-xyz/webhook"
# Yoki:
WEBHOOK_PATH = f"/{os.getenv('BOT_TOKEN').split(':')[1]}"

# Adminlardan tashqari hech kim webhook URL'ni bilmasligi kerak</code></pre>

<h4>4. Logging — production'da to'g'ri</h4>

<pre><code>import logging
import sys

# Tovush, fayl, va xato darajalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),    # Railway/Docker logs uchun
        # logging.FileHandler("bot.log"),     # VPS'da fayl
    ],
)

# Sentry — production xatolarini track qilish
# import sentry_sdk
# sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))</code></pre>

<h4>5. Health check endpoint</h4>

<pre><code>async def healthcheck(request):
    return web.Response(text="OK")


app.router.add_get("/health", healthcheck)

# Railway/Render avtomatik tekshiradi /health</code></pre>

<h4>6. Database migration deploy paytida</h4>

<pre><code># on_startup'da migration
async def on_startup(bot: Bot):
    # Alembic auto-migrate
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    await bot.set_webhook(...)</code></pre>

<h4>7. Multi-instance va Redis</h4>

<p>Bir nechta bot instance (load balancing) ishlatish — FSM state'ni Memory'da emas, Redis'da saqlash kerak:</p>

<pre><code>from aiogram.fsm.storage.redis import RedisStorage

storage = RedisStorage.from_url(os.getenv("REDIS_URL"))
dp = Dispatcher(storage=storage)</code></pre>

<h4>8. Docker bilan (bonus)</h4>

<pre><code># Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]


# docker-compose.yml
version: "3.9"
services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret

  redis:
    image: redis:7</code></pre>

<h4>9. Polling'dan webhook'ga o'tish — universal pattern</h4>

<pre><code>if os.getenv("USE_WEBHOOK") == "1":
    # Webhook variant
    web.run_app(app, ...)
else:
    # Polling (dev)
    asyncio.run(dp.start_polling(bot))</code></pre>

<h3>📌 Bu darsdan keyin siz bilasizki</h3>
<ul>
<li>✅ Polling vs Webhook — qachon qaysini</li>
<li>✅ <code>SimpleRequestHandler</code> + aiohttp setup</li>
<li>✅ HTTPS majburiy — Railway/Render avto-beradi</li>
<li>✅ Env variables — kodda token yo'q</li>
<li>✅ Webhook secret + maxfiy URL pattern</li>
<li>✅ Logging (stdout) + Sentry</li>
<li>✅ Health check endpoint</li>
<li>✅ Redis storage — multi-instance uchun</li>
<li>✅ Docker bilan paketlash (bonus)</li>
</ul>
"""

L10_CODE = """\
# ════════════════════════════════════════════════════════════════════
# DARS 10: Webhook va deploy
# ════════════════════════════════════════════════════════════════════
#
# Dev: USE_WEBHOOK=0 (polling)
# Prod: USE_WEBHOOK=1 (webhook + aiohttp)
# ════════════════════════════════════════════════════════════════════

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler, setup_application,
)

load_dotenv()


# ─────────────────────────────────────────────────────────────────────
# Sozlash
# ─────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env'da yo'q")

USE_WEBHOOK = os.getenv("USE_WEBHOOK", "0") == "1"
PORT = int(os.getenv("PORT", "8000"))

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "very-secret-random-string")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[1][:16]}"


# ─────────────────────────────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────────────────────────────

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# Production'da Redis ishlatish
# from aiogram.fsm.storage.redis import RedisStorage
# storage = RedisStorage.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
# dp = Dispatcher(storage=storage)

dp = Dispatcher(storage=MemoryStorage())


# ─────────────────────────────────────────────────────────────────────
# Handler'lar
# ─────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Salom, <b>{m.from_user.first_name}</b>!\\n\\n"
        f"Bu — production'ga deploy qilingan bot.\\n"
        f"Mode: <b>{'webhook' if USE_WEBHOOK else 'polling'}</b>"
    )


@dp.message(Command("info"))
async def cmd_info(m: Message):
    me = await bot.get_me()
    await m.answer(
        f"🤖 Bot: <b>{me.full_name}</b>\\n"
        f"Username: @{me.username}\\n"
        f"Mode: <b>{'webhook' if USE_WEBHOOK else 'polling'}</b>\\n"
        f"Hosting: {os.getenv('HOSTING', 'lokal')}\\n"
        f"Python: {sys.version.split()[0]}\\n"
        f"PID: {os.getpid()}"
    )


@dp.message()
async def echo(m: Message):
    if m.text:
        await m.answer(f"Echo: {m.text}")


# ─────────────────────────────────────────────────────────────────────
# Webhook lifecycle
# ─────────────────────────────────────────────────────────────────────

async def on_startup(bot: Bot):
    if USE_WEBHOOK:
        url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
        )
        logging.info(f"Webhook set: {url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Polling mode")


async def on_shutdown(bot: Bot):
    if USE_WEBHOOK:
        await bot.delete_webhook()


# ─────────────────────────────────────────────────────────────────────
# Health check (Railway/Render uchun)
# ─────────────────────────────────────────────────────────────────────

async def healthcheck(request):
    return web.Response(text="OK", status=200)


# ─────────────────────────────────────────────────────────────────────
# Webhook server
# ─────────────────────────────────────────────────────────────────────

def main_webhook():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    # Webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    # Health check
    app.router.add_get("/health", healthcheck)
    app.router.add_get("/", healthcheck)

    setup_application(app, dp, bot=bot)

    logging.info(f"Server starting on 0.0.0.0:{PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)


# ─────────────────────────────────────────────────────────────────────
# Polling (dev)
# ─────────────────────────────────────────────────────────────────────

async def main_polling():
    await on_startup(bot)
    await dp.start_polling(bot)


# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if USE_WEBHOOK:
        main_webhook()
    else:
        try:
            asyncio.run(main_polling())
        except KeyboardInterrupt:
            print("\\nBot to'xtatildi")


# ════════════════════════════════════════════════════════════════════
# Deploy fayllari (har birini alohida faylga ko'chirib oling):
# ════════════════════════════════════════════════════════════════════
#
# ── .env (lokal — gitignore'da) ──────────────────────────────────────
# BOT_TOKEN=7234567890:AAH...
# USE_WEBHOOK=0
#
# Production'da Railway/Render variables tab'da:
# BOT_TOKEN
# WEBHOOK_URL (Generate Domain'dan)
# WEBHOOK_SECRET (random string)
# USE_WEBHOOK=1
# DB_URL=postgresql+asyncpg://...
# REDIS_URL=redis://...
# HOSTING=railway
#
# ── requirements.txt ─────────────────────────────────────────────────
# aiogram>=3.7
# aiohttp>=3.9
# python-dotenv
# sqlalchemy[asyncio]
# asyncpg
# redis
#
# ── Procfile (Railway) ───────────────────────────────────────────────
# web: python bot.py
#
# ── Dockerfile (bonus) ───────────────────────────────────────────────
# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD ["python", "bot.py"]
#
# ── docker-compose.yml (lokal'da test) ───────────────────────────────
# version: "3.9"
# services:
#   bot:
#     build: .
#     env_file: .env
#     ports:
#       - "8000:8000"
#     environment:
#       - DB_URL=postgresql+asyncpg://postgres:secret@db:5432/botdb
#       - REDIS_URL=redis://redis:6379/0
#     depends_on:
#       - db
#       - redis
#   db:
#     image: postgres:16
#     environment:
#       POSTGRES_DB: botdb
#       POSTGRES_PASSWORD: secret
#     volumes:
#       - pgdata:/var/lib/postgresql/data
#   redis:
#     image: redis:7-alpine
# volumes:
#   pgdata:
"""
L11_TEXT = """\
<h2>🚀 CAPSTONE: To'liq delivery bot</h2>

<pre class="mermaid">
flowchart TB
    USER["Mijoz"] -->|katalog| BOT["Bot"]
    BOT -->|inline + FSM| ORDER["Buyurtma"]
    ORDER -->|notify| ADMIN["Admin paneli"]
    ADMIN -->|status update| KURYER["Kuryer bot"]
    KURYER -->|location| USER
    BOT <--> DB[("PostgreSQL")]
    BOT <--> REDIS[("Redis FSM")]
    BOT --> RAILWAY["Railway prod"]
</pre>

<p>Kursning yakuniy loyihasi — <strong>haqiqiy ish uchun mos</strong> delivery bot. R3 dagi shop botni kengaytirib, professional darajaga olib chiqamiz: real payment, kuryer tracking, statistika, deploy.</p>

<p>Bu loyiha — Tashkent bozori uchun real biznes idea: kichik restoran, kafe, pizzeria — har qaysi shu botni ishlatishi mumkin (sizning kichik biznesingiz!).</p>

<h3>Loyiha mahsuloti</h3>

<p>Uch tomonlama bot tizimi:</p>
<ul>
<li>👤 <strong>Mijoz bot</strong> — katalog, buyurtma, tracking</li>
<li>🧑‍💼 <strong>Admin paneli</strong> — buyurtmalarni qabul/rad, statistika</li>
<li>🛵 <strong>Kuryer bot</strong> — yangi buyurtma qabul, status update, location</li>
</ul>

<p>(Yoki bitta bot — admin/kuryer aliada interface'lar bilan)</p>

<h3>Texnik talablar</h3>

<h4>1. Repository va project structure</h4>

<pre><code>delivery-bot/
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── user/
│   │   │   ├── menu.py
│   │   │   ├── cart.py
│   │   │   ├── checkout.py
│   │   │   └── tracking.py
│   │   ├── admin/
│   │   │   ├── orders.py
│   │   │   ├── products.py
│   │   │   └── stats.py
│   │   └── courier/
│   │       └── pickup.py
│   ├── keyboards/
│   ├── filters/
│   ├── middlewares/
│   ├── states/
│   └── utils/
├── db/
│   ├── models.py
│   ├── repositories.py
│   └── engine.py
├── alembic/
│   └── versions/
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Procfile
└── README.md</code></pre>

<h4>2. Database (PostgreSQL)</h4>

<table>
<tr><th>Jadval</th><th>Maydonlar</th></tr>
<tr><td>users</td><td>id, ism, telefon, manzil, lang, yaratilgan</td></tr>
<tr><td>categories</td><td>id, nomi, tartib, faol</td></tr>
<tr><td>products</td><td>id, category_id, nomi, narx, tavsif, photo_id, stock, faol</td></tr>
<tr><td>cart_items</td><td>id, user_id, product_id, miqdor</td></tr>
<tr><td>orders</td><td>id, user_id, courier_id, status, summa, manzil, lokatsiya, izoh, sana</td></tr>
<tr><td>order_items</td><td>id, order_id, product_id, miqdor, narx_birlik</td></tr>
<tr><td>couriers</td><td>id, ism, telefon, faol, hozirgi_buyurtma_id</td></tr>
<tr><td>broadcasts</td><td>id, matn, photo_id, yuborilgan, vaqt</td></tr>
</table>

<h4>3. User funksiyalar</h4>

<ul>
<li>✅ /start — welcome + ro'yxatdan o'tish (FSM)</li>
<li>✅ Multi-til (uz/ru) — i18n middleware</li>
<li>✅ Menyu (kategoriya → mahsulot → tafsilot)</li>
<li>✅ Savatcha (+/-/o'chirish)</li>
<li>✅ Checkout (manzil — text yoki location)</li>
<li>✅ To'lov — naqd / Click / Payme</li>
<li>✅ Buyurtma trackingi — "Tayyorlanmoqda → Yetkazilmoqda → Yetkazildi"</li>
<li>✅ Tarix (oldingi buyurtmalar)</li>
<li>✅ Reyting va izoh</li>
<li>✅ Yordam, FAQ, bog'lanish</li>
</ul>

<h4>4. Admin funksiyalar</h4>

<ul>
<li>✅ Real-time notification yangi buyurtma kelganda</li>
<li>✅ Buyurtma qabul / bekor qilish (kuryer'ga yo'naltirish)</li>
<li>✅ Mahsulot CRUD (FSM bilan add/edit)</li>
<li>✅ Kategoriya CRUD</li>
<li>✅ Statistika: kun/hafta/oy daromad, top mahsulot, top mijoz</li>
<li>✅ Broadcast — barcha foydalanuvchilarga xabar (rasm bilan)</li>
<li>✅ Kuryer boshqaruvi (qo'shish, faollashtirish)</li>
<li>✅ Export — buyurtmalar Excel'ga (openpyxl)</li>
</ul>

<h4>5. Kuryer funksiyalar</h4>

<ul>
<li>✅ Yangi buyurtma kelganda push (admin tomonidan yo'naltirilgach)</li>
<li>✅ "✅ Qabul qilaman" / "❌ Mumkin emas"</li>
<li>✅ Mijoz manzili (link bilan Yandex Maps)</li>
<li>✅ Mijozga telefon raqami (clickable)</li>
<li>✅ Status update: "Olib ketdim" → "Yo'lda" → "Yetkazdim"</li>
<li>✅ Live location yuborish (mijozga tracking)</li>
</ul>

<h4>6. Production sozlash</h4>

<ul>
<li>✅ PostgreSQL (Railway/Supabase)</li>
<li>✅ Redis (Upstash bepul) — FSM storage</li>
<li>✅ Webhook + aiohttp</li>
<li>✅ Railway/Render deploy</li>
<li>✅ Alembic migrations</li>
<li>✅ Logging (Sentry yoki Logtail)</li>
<li>✅ Health check endpoint</li>
<li>✅ .env.example bilan toza dokument</li>
<li>✅ README.md (setup, deploy, screenshot)</li>
</ul>

<h4>7. Test va sifat</h4>

<ul>
<li>✅ pytest bilan handler'lar uchun test (kamida 5 ta)</li>
<li>✅ Type hints har joyda</li>
<li>✅ Ruff / Black linter</li>
<li>✅ Pre-commit hook</li>
<li>✅ GitHub Actions: lint + test har PR'da</li>
</ul>

<h3>Bonus (ixtiyoriy, lekin CV uchun zo'r)</h3>

<ul>
<li>💳 <strong>Telegram Payments</strong> (Stripe orqali) — real to'lov</li>
<li>🌍 <strong>Click va Payme integratsiya</strong> (real O'zbekistan to'lov)</li>
<li>📊 <strong>Grafana dashboard</strong> — buyurtma metrikalar</li>
<li>🔔 <strong>Notification</strong> — Telegram Stars yoki email</li>
<li>🌐 <strong>Web admin paneli</strong> — Flask/FastAPI bilan</li>
<li>🤖 <strong>AI suggestions</strong> — OpenAI bilan menyu tavsif yaratish</li>
<li>📱 <strong>Mini App</strong> (Telegram WebApp) — chiroyli UI</li>
<li>🎁 <strong>Loyalty programma</strong> — har 10-buyurtma bepul</li>
<li>📈 <strong>A/B test</strong> — turli welcome xabarlar</li>
<li>🌍 <strong>3 til</strong> (uz/ru/en) — gettext bilan</li>
</ul>

<h3>Bosqichlar (3 hafta)</h3>

<h4>Hafta 1 — Foundation</h4>
<ol>
<li>Project structure, .env, .gitignore</li>
<li>Database models + Alembic init</li>
<li>Asosiy User funksiyalar (start, menu)</li>
<li>Savatcha + checkout</li>
<li>Local'da to'liq ishlashi</li>
</ol>

<h4>Hafta 2 — Admin va Kuryer</h4>
<ol>
<li>Admin paneli (buyurtmalar, mahsulotlar CRUD)</li>
<li>Real-time notification</li>
<li>Statistika</li>
<li>Broadcast</li>
<li>Kuryer bot tarmog'i</li>
</ol>

<h4>Hafta 3 — Polish va deploy</h4>
<ol>
<li>i18n (2 til)</li>
<li>Tests + lint</li>
<li>Webhook setup</li>
<li>Railway deploy</li>
<li>Bonus features (1-2 ta)</li>
<li>Demo video + README</li>
</ol>

<h3>🎯 Yakuniy g'olib bayonoti</h3>

<p>Bu loyihani tugatgan dasturchi:</p>

<ul>
<li>✅ <strong>Real ishga tayyor</strong> — kichik restoran shu botni $200-500/oy uchun ijaraga oladi</li>
<li>✅ <strong>CV uchun klassik proyekt</strong> — har Telegram bot vakansiyasiga mos</li>
<li>✅ <strong>Freelance imkoniyat</strong> — har dukon bot xohlaydi</li>
<li>✅ <strong>O'z biznesi</strong> — shu kodni boshqa restoranlarga sotish (white-label)</li>
<li>✅ <strong>Senior darajadagi Python ko'nikmasi</strong> — async, ORM, deploy, testing, design patterns</li>
</ul>

<p>Keyingi qadamlar (kurs tugagandan keyin):</p>
<ul>
<li>📚 <strong>FastAPI</strong> — REST API qo'shish (mobile app uchun)</li>
<li>🌐 <strong>Web admin</strong> — Flask/React</li>
<li>📱 <strong>Telegram Mini App</strong> — chiroyli React UI bot ichida</li>
<li>🤖 <strong>OpenAI integratsiya</strong> — AI assistant</li>
<li>🐳 <strong>Kubernetes</strong> — scale uchun</li>
</ul>

<p>Tabriklayman! Siz endi <strong>Telegram bot engineer</strong>siz. Real bozorda 5-15 mln so'm/oy ish topish mumkin. Omad! 🚀</p>
"""

L11_CODE = """\
# ════════════════════════════════════════════════════════════════════
# 🚀 CAPSTONE: To'liq delivery bot — strukturasi
# ════════════════════════════════════════════════════════════════════
#
# Bu fayl — to'liq emas. Faqat arxitektura ko'rsatadi.
# Siz 3 hafta ichida modullarni alohida fayllarga yozasiz.
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# Loyiha struktura
# ─────────────────────────────────────────────────────────────────────

delivery-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point — webhook yoki polling
│   ├── config.py            # Env variables
│   ├── handlers/
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── start.py     # /start, ro'yxatdan o'tish
│   │   │   ├── menu.py      # Katalog ko'rinishi
│   │   │   ├── cart.py      # Savatcha
│   │   │   ├── checkout.py  # Buyurtma berish (FSM)
│   │   │   ├── tracking.py  # Buyurtma kuzatish
│   │   │   └── history.py   # Tarix
│   │   ├── admin/
│   │   │   ├── orders.py    # Buyurtmalar (real-time)
│   │   │   ├── products.py  # Mahsulot CRUD (FSM)
│   │   │   ├── stats.py     # Statistika
│   │   │   └── broadcast.py # Hammaga xabar
│   │   └── courier/
│   │       └── pickup.py    # Kuryer interface
│   ├── keyboards/
│   │   ├── user.py
│   │   ├── admin.py
│   │   └── courier.py
│   ├── filters/
│   │   ├── is_admin.py
│   │   ├── is_courier.py
│   │   └── is_group.py
│   ├── middlewares/
│   │   ├── db.py
│   │   ├── user_ctx.py
│   │   ├── i18n.py
│   │   └── throttling.py
│   ├── states/
│   │   ├── checkout.py
│   │   ├── add_product.py
│   │   └── broadcast.py
│   └── utils/
│       ├── format.py        # Money, datetime
│       └── notify.py        # Multi-recipient xabar
├── db/
│   ├── models.py            # SQLAlchemy
│   ├── repositories.py      # Service layer
│   └── engine.py
├── alembic/
│   ├── env.py
│   └── versions/
├── locales/
│   ├── uz.po
│   └── ru.po
├── tests/
│   ├── conftest.py
│   ├── test_cart.py
│   └── test_checkout.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Procfile
├── alembic.ini
└── README.md



# ─────────────────────────────────────────────────────────────────────
# bot/main.py — Entry point
# ─────────────────────────────────────────────────────────────────────

import asyncio
import logging
import sys
from aiohttp import web

from bot.config import settings
from bot.handlers.user import start, menu, cart, checkout, tracking
from bot.handlers.admin import orders, products, stats, broadcast
from bot.handlers.courier import pickup
from bot.middlewares import db, user_ctx, i18n, throttling
from db.engine import init_db, SessionMaker

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def create_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)

    # Middlewares
    dp.update.middleware(db.DBSessionMiddleware(SessionMaker))
    dp.update.middleware(user_ctx.UserContextMiddleware())
    dp.update.middleware(i18n.I18nMiddleware())
    dp.message.middleware(throttling.ThrottlingMiddleware(rate=5, per=10))

    # Routers
    for router in (
        start.router, menu.router, cart.router, checkout.router, tracking.router,
        orders.router, products.router, stats.router, broadcast.router,
        pickup.router,
    ):
        dp.include_router(router)

    return bot, dp


async def main_polling():
    bot, dp = await create_bot()
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Polling started")
    await dp.start_polling(bot)


def main_webhook():
    bot, dp = asyncio.get_event_loop().run_until_complete(create_bot())

    async def on_startup(bot: Bot):
        await init_db()
        await bot.set_webhook(
            url=f"{settings.webhook_url}{settings.webhook_path}",
            secret_token=settings.webhook_secret,
        )

    dp.startup.register(on_startup)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot,
        secret_token=settings.webhook_secret,
    ).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=settings.port)


if __name__ == "__main__":
    if settings.use_webhook:
        main_webhook()
    else:
        asyncio.run(main_polling())



# ─────────────────────────────────────────────────────────────────────
# db/models.py — Asosiy modellar
# ─────────────────────────────────────────────────────────────────────

from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Float, Integer, Boolean, DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ism: Mapped[str] = mapped_column(String(50))
    telefon: Mapped[str | None] = mapped_column(String(20))
    manzil: Mapped[str | None] = mapped_column(String(200))
    lang: Mapped[str] = mapped_column(String(2), default="uz")
    yaratilgan: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    nomi_uz: Mapped[str] = mapped_column(String(50))
    nomi_ru: Mapped[str] = mapped_column(String(50))
    tartib: Mapped[int] = mapped_column(Integer, default=0)
    faol: Mapped[bool] = mapped_column(Boolean, default=True)
    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    nomi_uz: Mapped[str] = mapped_column(String(100))
    nomi_ru: Mapped[str] = mapped_column(String(100))
    narx: Mapped[float] = mapped_column(Float)
    tavsif_uz: Mapped[str] = mapped_column(Text)
    tavsif_ru: Mapped[str] = mapped_column(Text)
    photo_id: Mapped[str | None] = mapped_column(String(200))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    faol: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped["Category"] = relationship(back_populates="products")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    courier_id: Mapped[int | None] = mapped_column(ForeignKey("couriers.id"))
    status: Mapped[str] = mapped_column(String(20), default="kutmoqda")
    # kutmoqda → tasdiqlangan → tayyor → yetkazilmoqda → yetkazildi → bekor
    summa: Mapped[float] = mapped_column(Float)
    manzil: Mapped[str] = mapped_column(String(300))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    izoh: Mapped[str | None] = mapped_column(Text)
    sana: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    items: Mapped[list["OrderItem"]] = relationship(cascade="all, delete-orphan")


class Courier(Base):
    __tablename__ = "couriers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ism: Mapped[str] = mapped_column(String(50))
    telefon: Mapped[str] = mapped_column(String(20))
    faol: Mapped[bool] = mapped_column(Boolean, default=True)
    hozirgi_buyurtma_id: Mapped[int | None] = mapped_column()



# ─────────────────────────────────────────────────────────────────────
# bot/middlewares/i18n.py — Multi-til
# ─────────────────────────────────────────────────────────────────────

from aiogram import BaseMiddleware

TRANSLATIONS = {
    "uz": {
        "welcome": "Salom, {name}!",
        "menu": "🍕 Menyu",
        "cart": "🛒 Savatcha",
        "empty_cart": "Savat bo'sh",
        # ...
    },
    "ru": {
        "welcome": "Здравствуйте, {name}!",
        "menu": "🍕 Меню",
        "cart": "🛒 Корзина",
        "empty_cart": "Корзина пуста",
        # ...
    },
}


class I18nMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("user")
        lang = user.lang if user else "uz"

        def _(key: str, **kwargs) -> str:
            t = TRANSLATIONS.get(lang, TRANSLATIONS["uz"])
            text = t.get(key, key)
            return text.format(**kwargs) if kwargs else text

        data["_"] = _
        return await handler(event, data)


# Handler'da:
# @router.message(F.text == "🍕 Menyu")
# async def menu(m: Message, _):
#     await m.answer(_("menu_intro"))



# ─────────────────────────────────────────────────────────────────────
# tests/test_cart.py — Pytest misol
# ─────────────────────────────────────────────────────────────────────

import pytest
from db.models import User, Product, CartItem


@pytest.mark.asyncio
async def test_add_to_cart(session, sample_user, sample_product):
    item = CartItem(
        user_id=sample_user.id,
        product_id=sample_product.id,
        miqdor=2,
    )
    session.add(item)
    await session.commit()

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == sample_user.id)
    )
    items = list(result.scalars())
    assert len(items) == 1
    assert items[0].miqdor == 2



# ─────────────────────────────────────────────────────────────────────
# Dockerfile
# ─────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY . .

# Migration
RUN alembic upgrade head

EXPOSE 8000
CMD ["python", "-m", "bot.main"]



# ════════════════════════════════════════════════════════════════════
# Yakuniy yetkazib berish:
#
# 1. GitHub repo URL — https://github.com/sizning-user/delivery-bot
# 2. Live bot — t.me/sizning_delivery_bot
# 3. Demo video (5-10 daqiqa) — YouTube
# 4. README.md (setup, deploy, screenshot'lar)
# 5. Hisobot:
#    - Texnologiyalar tanlovi
#    - Eng qiyin qism
#    - Bonus features
#    - Production stats (foydalanuvchilar soni, buyurtmalar)
#
# 🏆 SIZ ENDI BOT ENGINEER!
# ════════════════════════════════════════════════════════════════════
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
    mc("Telegram'da yangi bot yaratish uchun qaysi bot'ga murojaat qilamiz?",
       ["@BotFather",
        "@TelegramSupport",
        "@CreateBot",
        "@AdminBot"],
       "A", diff="Easy", pts=2),
    mc("Bot token'ni qaerga saqlash xavfsiz?",
       ["Kodda bevosita string sifatida",
        ".env faylda + os.getenv(), va .env ni .gitignore'ga",
        "GitHub repo'da public",
        "README'da"],
       "B", explanation="Token sirli kalit. Ko'rinsa botni o'g'rilashlari mumkin.",
       diff="Medium", pts=3),
    mc("aiogram 3.x'da handler — bu:",
       ["Sinkron oddiy funksiya",
        "Async funksiya (`async def`) — @dp.message va h.k. bilan belgilangan",
        "Class metod",
        "Lambda"],
       "B", explanation="aiogram async-first — barcha handler'lar async.",
       diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari TO'G'RI aiogram 3.x sintaksisi?",
       ["@dp.message(CommandStart())",
        "@dp.message(Command('help'))",
        "@bot.handler('start')",
        "@dp.message()",
        "await message.answer('matn')"],
       "A,B,D,E", multi=True,
       hint="@bot.handler — bu eskirgan/bo'lmagan sintaksis.",
       diff="Medium", pts=3),
    mc("`message.from_user.id` nima qaytaradi?",
       ["Bot ID",
        "Xabar yuborgan foydalanuvchining Telegram ID'si (raqam)",
        "Chat ID",
        "Message text"],
       "B", diff="Easy", pts=2),
    dd("Birinchi bot uchun handler yozish bosqichlari",
       ["import asyncio",
        "from aiogram import Bot, Dispatcher",
        "from aiogram.filters import CommandStart",
        "from aiogram.types import Message",
        "bot = Bot(token='TOKEN')",
        "dp = Dispatcher()",
        "@dp.message(CommandStart())",
        "async def start(message: Message):",
        "    await message.answer('Salom!')",
        "asyncio.run(dp.start_polling(bot))"],
       diff="Medium", pts=3),
    ti("Polling va Webhook orasidagi farq nima va qaysi vaziyatda qaysini ishlatamiz?",
       "Polling: bot Telegram'ga DOIM so'rov yuboradi 'yangi xabar bormi?'. Oson, lokal/dev uchun. "
       "Resurs ko'p ishlatadi va kechikish (1-2s) bor. start_polling() bilan. "
       "Webhook: TELEGRAM bot'ga push qiladi yangi update bo'lganda. Tezroq, kam resurs, lekin "
       "HTTPS sertifikatli server kerak. Production'da afzal. set_webhook() bilan. "
       "Tavsiya: dev — polling, production — webhook. 10-darsda webhook va deploy chuqurroq.",
       hint="Resurs va sozlash murakkabligi.",
       diff="Hard", pts=4),
]
L2_EX: list = [
    mc("`Command('help', 'info')` filter nimani qabul qiladi?",
       ["Faqat /help",
        "/help yoki /info — 2 ta buyruq, bitta handler",
        "/help info",
        "Hech narsa"],
       "B", diff="Easy", pts=2),
    mc("aiogram'da `F` nima?",
       ["Boolean qiymat",
        "Magic Filter — atribut va metodlarni zanjir qilib filter yaratish",
        "Function decorator",
        "Filter klassi"],
       "B", diff="Medium", pts=3),
    mc("Quyidagi kod nima xato bera oladi?\n```python\n@dp.message()\nasync def all(m): ...\n@dp.message(Command('start'))\nasync def start(m): ...\n```",
       ["Hech qanday",
        "Tartib noto'g'ri — catch-all tepada, /start hech qachon ishlamaydi",
        "Sintaktik xato",
        "Import yo'q"],
       "B", explanation="Aniqroq filter'lar tepada, catch-all eng oxirda.",
       diff="Hard", pts=4),
    mc("`F.text.lower() == 'salom'` qaysi vaziyatda TRUE?",
       ["Faqat 'salom'",
        "'salom', 'Salom', 'SALOM', 'sAlOm' — har xil case",
        "Faqat 'SALOM'",
        "Hech qachon"],
       "B", explanation="lower() — kichik harfga aylantiradi, keyin solishtiriladi.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari MAVJUD F filter'lari?",
       ["F.photo",
        "F.voice",
        "F.sticker",
        "F.location",
        "F.email",
        "F.text.regexp(r'...')"],
       "A,B,C,D,F", multi=True,
       hint="F.email — yo'q. Email tekshirish — regex bilan.",
       diff="Medium", pts=3),
    dd("Admin only /ban buyrug'i handler bosqichlari",
       ["from aiogram.filters import Command, CommandObject",
        "ADMINS = {111111111}",
        "@dp.message(Command('ban'), F.from_user.id.in_(ADMINS))",
        "async def cmd_ban(m: Message, command: CommandObject):",
        "    if not command.args:",
        "        await m.answer('Foydalanish: /ban <user>')",
        "        return",
        "    await m.answer(f'Banned: {command.args}')"],
       diff="Hard", pts=4),
    ti("Filter'larda `&`, `|`, `~` operatorlari nima qiladi?",
       "& = AND (ikkala shart). Misol: F.text & F.from_user.id == 123. "
       "| = OR (kamida bittasi). Misol: F.text == 'ha' | F.text == 'ok'. "
       "~ = NOT (inkor). Misol: ~F.text.startswith('/') — slesh bilan boshlanmagan. "
       "Bu — Python'ning oddiy boolean operatorlaridan farqli (and/or/not). "
       "Magic Filter ichida — operator overload qilingan. "
       "Plus: bir handler'da bir nechta filter berish (vergul bilan) ham AND demakdir.",
       hint="Boolean operatorlar overload.",
       diff="Hard", pts=4),
]
L3_EX: list = [
    mc("Reply keyboard tugmasi bosilganda nima yuboriladi?",
       ["Maxsus callback",
        "Tugmadagi matn — oddiy Message kabi",
        "Tugma ID raqami",
        "Hech narsa"],
       "B", explanation="Shuning uchun handler F.text == 'tugma matni' bilan.",
       diff="Easy", pts=2),
    mc("`resize_keyboard=True` nima qiladi?",
       ["Tugmalarni o'chiradi",
        "Klaviaturani ekran o'lchamiga moslab kichraytiradi (har doim True qo'yish tavsiya)",
        "Faqat 1 marta ko'rsatadi",
        "Performance"],
       "B", diff="Easy", pts=2),
    mc("Quyidagi kod nima xato qiladi?\n```python\nKeyboardButton(text=\"👤 Profil\")\n# va handler:\n@dp.message(F.text == \"Profil\")\n```",
       ["Hech qanday",
        "Tugma '👤 Profil' yuboradi, handler faqat 'Profil' kutadi — mos kelmaydi",
        "Sintaktik xato",
        "Emoji ishlamaydi"],
       "B", explanation="Yechim: handler ham aniq matn — F.text == '👤 Profil', yoki konstanta.",
       diff="Medium", pts=3),
    mc("Telefon raqamini so'rashning to'g'ri yo'li:",
       ["KeyboardButton(text='Telefon yuboring')",
        "KeyboardButton(text='Telefon', request_contact=True)",
        "Inline button",
        "Faqat matn"],
       "B", explanation="request_contact=True — Telegram avtomatik telefon dialogini ochadi.",
       diff="Medium", pts=3),
    mc("`ReplyKeyboardBuilder` bilan adjust(2, 1) nima qiladi?",
       ["2 ta tugma",
        "Birinchi qatorda 2 ta tugma, ikkinchisida 1 ta",
        "2 qator, har birida 1 ta",
        "Hech narsa"],
       "B", explanation="adjust(*sizes) — har qatorda nechta tugma.",
       diff="Hard", pts=4),
    dd("Yes/No klaviatura yaratish bosqichlari",
       ["from aiogram.utils.keyboard import ReplyKeyboardBuilder",
        "def yes_no_kb():",
        "    kb = ReplyKeyboardBuilder()",
        "    kb.button(text='✅ Ha')",
        "    kb.button(text='❌ Yo\\'q')",
        "    kb.adjust(2)",
        "    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)"],
       diff="Medium", pts=3),
    ti("Production'da tugma matnlarini konstantalarda saqlash nima uchun yaxshi?",
       "Sabablari: 1) Bir joyda o'zgartirish — masalan, '👤 Profil' ni '👤 Hisobim' ga o'zgartirsangiz, "
       "10 ta handler'da qo'l bilan o'zgartirish kerak emas — konstantani o'zgartirsangiz, "
       "har joyda avtomatik. 2) Typo'dan saqlash — IDE autocomplete ko'rsatadi. "
       "3) i18n (ko'p tilli) tayyorlik — tugmalarni dictionary'dan olish oson. "
       "4) Reviewerlar uchun aniq — hammasi bir joyda ko'rinadi. "
       "5) Magic string anti-pattern oldini olish. "
       "Misol: class BTN: PROFIL = '👤 Profil' yoki dictionary bilan.",
       hint="Maintenance va typo.",
       diff="Hard", pts=4),
]
R1_EX: list = [
    mc("3-darajali menyu nima?",
       ["3 ta tugma",
        "Bosh menyu → kategoriyalar → kontent — 3 ta darajada navigatsiya",
        "3 ta bot",
        "Faqat sintaksis"],
       "B", diff="Easy", pts=2),
    mc("State-siz menyu navigatsiyasini qanday qilamiz?",
       ["FSM bilan",
        "Har submenyu o'z tugmalariga ega, orqaga tugmasi bosh menyuga qaytaradi",
        "Database bilan",
        "Mumkin emas"],
       "B", explanation="Oddiy va ko'p hollarda yetarli. FSM (5-darsda) — multi-step forms uchun.",
       diff="Medium", pts=3),
    mc("Mahsulot rasmini caption bilan jo'natish:",
       ["m.answer + m.answer_photo alohida",
        "m.answer_photo(photo, caption='matn', reply_markup=kb)",
        "URL'ni text sifatida",
        "Mumkin emas"],
       "B", explanation="answer_photo — caption va reply_markup parametrlarini qabul qiladi.",
       diff="Medium", pts=3),
    mc("`URLInputFile('https://...')` qachon foydali?",
       ["Hech qachon",
        "Internet'dan rasm yuborish (Telegram'ga upload qilmaslik)",
        "Faqat file_id bilan",
        "Faqat local fayllar"],
       "B", explanation="Tezroq + serverda fayl saqlash shart emas.",
       diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari bu loyihada TO'G'RI pattern?",
       ["Tugma matnlarini BTN konstantlarda saqlash",
        "Har submenyu uchun alohida klaviatura funksiya",
        "Catch-all eng oxirda",
        "Har handler'da tugma matnini hardcode qilish",
        "Mahsulot ma'lumotlarini PRODUCTS dict'da",
        "Har mahsulot uchun alohida handler"],
       "A,B,C,E", multi=True,
       hint="Hardcode + 1000 handler — yomon. DRY pattern.",
       diff="Hard", pts=4),
    dd("Submenyudan bosh menyuga qaytish (BACK)",
       ["@dp.message(F.text == BTN.BACK)",
        "async def back_to_main(m: Message):",
        "    await m.answer(",
        "        '🏠 Bosh menyu',",
        "        reply_markup=main_menu()",
        "    )"],
       diff="Easy", pts=2),
    ti("Hozircha state-siz menyu ishlashda nima cheklov bor va FSM (keyingi modulda) nimani yechadi?",
       "Cheklov: bot foydalanuvchi qaerda turganligini ESLAB QOLMAYDI. "
       "Misol: ro'yxatdan o'tish 3 bosqich (ism → email → parol). State-siz — har xabar uchun "
       "alohida handler kerak va qaerda turganligini bilish qiyin. "
       "FSM (Finite State Machine) bunda yordam beradi: har foydalanuvchining hozirgi 'state'i "
       "saqlanadi (Redis yoki memory). Handler: agar state == 'waiting_for_email' bo'lsa, "
       "kelgan matn email deb qabul qilinadi. Multi-step form'lar uchun shart. "
       "5-darsda FSM amaliyot qilamiz.",
       hint="State eslab qolish va multi-step.",
       diff="Hard", pts=4),
]
L4_EX: list = [
    mc("Inline keyboard tugmasi bosilganda nima sodir bo'ladi?",
       ["Matn yuboriladi",
        "Bot'ga `callback_data` qiymatini olib `@dp.callback_query` handler ishga tushadi",
        "Hech narsa",
        "Botga so'rov yuboriladi"],
       "B", diff="Easy", pts=2),
    mc("`call.answer()` ni chaqirish nima uchun shart?",
       ["Performance uchun",
        "Telegram'ga 'qabul qildim' deb javob — aks holda tugma 30s loading'da qoladi",
        "Mantiqiy emas",
        "Faqat tasdiqlash"],
       "B", explanation="Har callback handler boshida call.answer() — qoidasi.",
       diff="Medium", pts=3),
    mc("`callback_data` uchun maksimal hajm:",
       ["Cheksiz",
        "64 bayt",
        "256 bayt",
        "1 KB"],
       "B", explanation="Uzun ma'lumot uchun: DB ID + CallbackData klassi.",
       diff="Medium", pts=3),
    mc("Xabarning faqat tugmalarini o'zgartirish (matnga tegmasdan):",
       ["edit_text",
        "edit_reply_markup",
        "delete + send_message",
        "Mumkin emas"],
       "B", explanation="edit_reply_markup(reply_markup=yangi_kb) yoki None bilan o'chirish.",
       diff="Medium", pts=3),
    mc("CallbackData klassi'ning afzalligi:",
       ["Tezroq",
        "Tip xavfsiz, strukturali ma'lumot",
        "Filter aniqroq",
        "Auto-validate"],
       "B,C,D", multi=True,
       hint="Tezlik — emas. Asosiy — clean code va xavfsizlik.",
       diff="Hard", pts=4),
    dd("CallbackData klassi yaratish va ishlatish",
       ["from aiogram.filters.callback_data import CallbackData",
        "class OrderCb(CallbackData, prefix='order'):",
        "    action: str",
        "    order_id: int",
        "# Tugma:",
        "kb.button(text='View', callback_data=OrderCb(action='view', order_id=42).pack())",
        "# Handler:",
        "@dp.callback_query(OrderCb.filter(F.action == 'view'))",
        "async def view(call: CallbackQuery, callback_data: OrderCb):",
        "    await call.answer()",
        "    await call.message.edit_text(f'Order {callback_data.order_id}')"],
       diff="Hard", pts=4),
    ti("`call.answer()` da `show_alert=True` qachon ishlatamiz?",
       "show_alert=False (default) — toast (yuqori chap burchakda 1-2 sek). Oddiy bildirgi uchun. "
       "show_alert=True — modal popup, foydalanuvchi OK bosishi kerak. "
       "Qachon True: 1) Muhim ogohlantirishlar ('Buyurtma bekor qilindi!'); "
       "2) Tasdiqlovchi xabarlar (delete qilingach); "
       "3) Xato xabarlari ('Mahsulot tugagan'); "
       "4) Foydalanuvchi e'tibor bermasligi mumkin bo'lgan muhim ma'lumot. "
       "Qachon False (default): oddiy feedback, loading to'xtatish. "
       "Tavsiya: ko'p hollarda False; alert — kam, lekin muhim.",
       hint="Toast vs modal popup.",
       diff="Hard", pts=4),
]
L5_EX: list = [
    mc("FSM (Finite State Machine) nima va qachon kerak?",
       ["Performance optimizatsiya",
        "Bot foydalanuvchining qaerda turganini eslab qolish — multi-step formalar uchun",
        "Faqat admin uchun",
        "Database alternativi"],
       "B", diff="Easy", pts=2),
    mc("aiogram'da state'larni qanday e'lon qilamiz?",
       ["Oddiy o'zgaruvchi",
        "class MyStates(StatesGroup): step1 = State()",
        "Dictionary",
        "Database"],
       "B", diff="Easy", pts=2),
    mc("`MemoryStorage` va `RedisStorage` farqi?",
       ["Hech qanday",
        "Memory: process'da, restart bo'lsa yo'qoladi (dev). Redis: production — bot crash bo'lsa state saqlanadi",
        "Redis tezroq",
        "Memory faqat 100 user"],
       "B", diff="Medium", pts=3),
    mc("State'da ma'lumot saqlash uchun:",
       ["state.save(x)",
        "state.update_data(ism='Olim', yosh=25)",
        "state.set(x)",
        "state.write(x)"],
       "B", explanation="update_data — eski'larni saqlab yangilarini qo'shadi.",
       diff="Medium", pts=3),
    mc("Yoshni qabul qilgan handler'da validatsiya xato bo'lsa nima qilamiz?",
       ["state.clear()",
        "return (xabar yuborib state'ni o'zgartirmasdan — foydalanuvchi qaytadan urinadi)",
        "Bekor qilish",
        "Boshqa state'ga o'tish"],
       "B", explanation="State o'zgarmaydi → foydalanuvchi shu yerda qoladi → qaytadan kiritadi.",
       diff="Hard", pts=4),
    dd("Ro'yxatdan o'tish — ism bosqichi handler",
       ["@dp.message(Command('register'))",
        "async def register_start(m: Message, state: FSMContext):",
        "    await state.set_state(RegisterStates.ism)",
        "    await m.answer('Ismingizni kiriting:')",
        "",
        "@dp.message(RegisterStates.ism, F.text)",
        "async def get_ism(m: Message, state: FSMContext):",
        "    if len(m.text) < 2:",
        "        await m.answer('Ism qisqa')",
        "        return",
        "    await state.update_data(ism=m.text)",
        "    await state.set_state(RegisterStates.yosh)",
        "    await m.answer('Yoshingiz?')"],
       diff="Hard", pts=4),
    ti("Ro'yxatdan o'tish tugagach `state.clear()` chaqirish nima uchun muhim?",
       "1) State'ni tozalaydi — keyingi /register qaytadan boshlanadi (ism so'rashdan); "
       "2) Data ham tozalanadi — eski ma'lumotlar (ism, yosh) RAM/Redis'da qolib ketmaydi; "
       "3) Boshqa handler'lar (StateFilter(None) bilan filterlangan) ishlashga ruxsat oladi — masalan oddiy menyu; "
       "4) Memory leak oldini olish — Redis'da minglab foydalanuvchining yarim-finished state'lari saqlanmaydi. "
       "Tavsiya: har form tugashi yoki bekor qilinishida — clear(). "
       "Tipik yo'l: muvaffaqiyatda — clear() + success msg, /cancel da — clear() + cancel msg.",
       hint="Memory leak va clean state.",
       diff="Hard", pts=4),
]
L6_EX: list = [
    mc("Filter va middleware orasidagi farq?",
       ["Hech qanday",
        "Filter — true/false qaytaradi (handler ishlasinmi). Middleware — har handler oldin/keyin code",
        "Faqat sintaktik",
        "Filter tezroq"],
       "B", diff="Medium", pts=3),
    mc("Custom filter klass yaratish uchun:",
       ["class X(Filter)",
        "class X(BaseFilter): async def __call__(self, m): ...",
        "@filter decorator",
        "def filter_x()"],
       "B", explanation="BaseFilter.__call__ async va boolean qaytaradi.",
       diff="Easy", pts=2),
    mc("Middleware'ning eng katta xatosi qaysi?",
       ["import yo'q",
        "`return await handler(event, data)` ni unutib qoldirish — handler hech qachon ishga tushmaydi",
        "Sintaksis",
        "Logging"],
       "B", diff="Hard", pts=4),
    mc("Outer va inner middleware farqi?",
       ["Hech qanday",
        "Outer — har update uchun (filter'lardan oldin). Inner — filter o'tgach (handler'ga yaqinroq)",
        "Tezlik",
        "Faqat sintaktik"],
       "B", diff="Hard", pts=4),
    mc("Middleware'dan handler'ga ma'lumot uzatish:",
       ["return qiymat",
        "data['key'] = qiymat, keyin handler argument: `async def h(m: Message, key: str)`",
        "Global o'zgaruvchi",
        "Mumkin emas"],
       "B", explanation="data dictionary aiogram tomonidan handler argumentlariga 'inject' qilinadi.",
       diff="Hard", pts=4),
    dd("Rate-limit middleware bosqichlari",
       ["from collections import defaultdict",
        "from time import time",
        "class RateLimitMiddleware(BaseMiddleware):",
        "    def __init__(self, rate=5, per=10):",
        "        self.rate = rate",
        "        self.per = per",
        "        self.cache = defaultdict(list)",
        "    async def __call__(self, handler, event, data):",
        "        user_id = event.from_user.id",
        "        now = time()",
        "        self.cache[user_id] = [t for t in self.cache[user_id] if now - t < self.per]",
        "        if len(self.cache[user_id]) >= self.rate:",
        "            await event.answer('Sekinroq!')",
        "            return",
        "        self.cache[user_id].append(now)",
        "        return await handler(event, data)"],
       diff="Hard", pts=4),
    ti("Production'da auth + rate-limit + DB session uchun necha ta middleware kerak va tartibi qanday?",
       "Kamida 3 ta: 1) LoggingMiddleware (outer — har update'ni log); "
       "2) DBSessionMiddleware (inner — session ochish, handler'ga uzatish, finally yopish); "
       "3) AuthMiddleware (inner — DB'dan user olish, data['user']'ga); "
       "4) RateLimitMiddleware (inner — spam'dan saqlash); "
       "5) BanFilter (filter — banned user'larni filterlash). "
       "Tartib: outer middleware'lar avval, keyin filter'lar, keyin inner middleware'lar, keyin handler. "
       "Tipik tartib: Logging → RateLimit → DB → Auth → Filter(NotBanned) → Handler. "
       "Har middleware bir narsani qiladi (Single Responsibility) — kod toza va testlash oson.",
       hint="Single Responsibility per middleware.",
       diff="Hard", pts=4),
]
R2_EX: list = [
    mc("FSM + inline keyboard birga ishlatganda nima diqqat?",
       ["Inline tugma faqat oddiy handler",
        "Callback_query handler'da ham state filter qo'shish: @dp.callback_query(F.data == 'X', AnketaStates.Y)",
        "Mumkin emas",
        "Faqat database"],
       "B", explanation="State filter shart — boshqa state'da inline xato ishlamasligi uchun.",
       diff="Hard", pts=4),
    mc("Tasdiqlash sahifasida nima ko'rsatish kerak?",
       ["Faqat 'Saqlandimi?'",
        "Hamma to'ldirilgan ma'lumotlarni chiroyli + 2 ta tugma (Tasdiq/Tahrir)",
        "Faqat ism",
        "Hech narsa"],
       "B", diff="Easy", pts=2),
    mc("Anketa muvaffaqiyatli saqlangach adminlarga xabar yuborish:",
       ["Mumkin emas",
        "for admin_id in ADMINS: await bot.send_message(admin_id, '...')",
        "Faqat email",
        "Faqat callback"],
       "B", explanation="Bot.send_message har joydan ishlatish mumkin (handler ichidan ham).",
       diff="Medium", pts=3),
    mc("Pagination ko'p ma'lumotlar uchun nima uchun kerak?",
       ["Estetika",
        "Telegram xabar maksimum 4096 belgi. Plus UX — 100 ta ro'yxat bir vaqtda — yomon",
        "Performance",
        "Mumkin emas"],
       "B", diff="Medium", pts=3),
    mc("Quyidagilardan qaysilari TO'G'RI anketa bot uchun?",
       ["Har bosqichda progress 'N/7'",
        "Validatsiya har bosqichda",
        "Tugmalar oldida emoji",
        "Cancel har bosqichda",
        "Adminga xabar saqlangach",
        "Pagination kattaroq ro'yxatda"],
       "A,B,C,D,E,F", multi=True, diff="Medium", pts=3),
    dd("Tasdiq tugmasi handler'i",
       ["@dp.callback_query(F.data == 'confirm:yes', AnketaStates.confirm)",
        "async def confirmed(call: CallbackQuery, state: FSMContext):",
        "    data = await state.get_data()",
        "    APPLICATIONS[call.from_user.id] = data",
        "    await state.clear()",
        "    await call.answer('Saqlandi!', show_alert=True)",
        "    await call.message.edit_text('✅ Qabul qilindi!')",
        "    for admin_id in ADMINS:",
        "        await bot.send_message(admin_id, f'Yangi: {data}')"],
       diff="Hard", pts=4),
    ti("Anketa to'liq UX uchun nimani qo'shish mumkin (loyihada bo'lmagan, lekin yaxshi)?",
       "1) Avvalgi javobni o'zgartirish (har step keyin '✏️ Tahrirlash' inline tugmasi); "
       "2) 'Yarim to'ldirilgan' anketani saqlash (Redis bilan) — user keyin /resume bilan davom etishi mumkin; "
       "3) Inline'da pagination shaharlar (8 emas, 20+ shahar bo'lsa); "
       "4) PDF tayyorlash (reportlab) anketa tugagach va foydalanuvchiga yuborish; "
       "5) Admin uchun: anketa Excel'ga export, statistika (Toshkent vs Samarqand soni); "
       "6) Ko'p tilli (uz/ru/en — i18n middleware bilan); "
       "7) Recaptcha-style spam himoya (matematik javob); "
       "8) Webhook notification — yangi anketa kelganda Slack/Discord'ga.",
       hint="UX, persistence, admin tools.",
       diff="Hard", pts=4),
]
L7_EX: list = [
    mc("aiogram bilan nima uchun ASYNC SQLAlchemy?",
       ["Tezroq",
        "aiogram async event loop'da. Sync DB chaqiriq butun bot'ni bloklab qo'yadi (boshqa user'lar javob ololmaydi)",
        "Faqat zamonaviy",
        "Async ham sync ham bir xil"],
       "B", diff="Medium", pts=3),
    mc("`async_sessionmaker` nima qaytaradi?",
       ["Session ob'ekt",
        "Session yaratuvchi factory — har chaqiriq yangi session",
        "Bot",
        "Engine"],
       "B", explanation="async with SessionMaker() as session — har handler uchun yangi.",
       diff="Medium", pts=3),
    mc("`AsyncSession` da SELECT qanday yoziladi?",
       ["session.query(User).get(id)",
        "await session.execute(select(User).where(User.id == id))",
        "session.get(User, id)",
        "Ikkalasi (B va C)"],
       "D", explanation="get — primary key bilan oddiy. execute(select) — murakkab so'rovlar uchun.",
       diff="Hard", pts=4),
    mc("`selectinload` nima qiladi?",
       ["Faqat select",
        "Relationship'larni bitta qo'shimcha query'da yuklaydi (N+1 oldini olish)",
        "Performance buzadi",
        "Faqat ko'p tabledan"],
       "B", explanation="N+1 problem — har user uchun alohida orders query. selectinload — bitta IN query.",
       diff="Hard", pts=4),
    mc("Production'da schema o'zgartirish uchun:",
       ["Bevosita SQL",
        "Alembic migration",
        "Base.metadata.create_all har ishga tushganda",
        "Dump + restore"],
       "B", explanation="create_all — faqat dev. Production — versiyalangan migration.",
       diff="Medium", pts=3),
    dd("DB session middleware",
       ["class DBSessionMiddleware(BaseMiddleware):",
        "    def __init__(self, session_maker):",
        "        self.session_maker = session_maker",
        "    async def __call__(self, handler, event, data):",
        "        async with self.session_maker() as session:",
        "            data['session'] = session",
        "            return await handler(event, data)",
        "dp.update.middleware(DBSessionMiddleware(SessionMaker))"],
       diff="Hard", pts=4),
    ti("`expire_on_commit=False` parametr nima uchun aiogram'da MUHIM?",
       "Default'da SQLAlchemy commit keyin ob'ektlarni 'expire' qiladi — keyingi atribut o'qish "
       "uchun yangi DB so'rovi kerak. async kontextida bu xato beradi (lazy load yo'q async'da). "
       "Misol: order = await create_order(); await message.answer(f'ID: {order.id}') — "
       "expire bo'lsa, order.id ga kirish yangi sync query → xato. "
       "expire_on_commit=False bilan — commit keyin ob'ekt yashash davom etadi, atributlar "
       "ishlay beradi. Bu — async + SQLAlchemy uchun standart practice. "
       "Async pattern: commit, keyin manually session.refresh(obj) agar yangi data kerak bo'lsa.",
       hint="Lazy load async'da ishlamaydi.",
       diff="Hard", pts=4),
]
L8_EX: list = [
    mc("Eng tez fayl yuborish usuli qaysi?",
       ["FSInputFile (lokal)",
        "file_id (string — avval Telegram'da bo'lgan)",
        "URLInputFile",
        "BufferedInputFile"],
       "B", explanation="file_id — Telegram serverlarida saqlanadigan referans. Instant.",
       diff="Medium", pts=3),
    mc("`m.photo` nima qaytaradi?",
       ["Bitta rasm ob'ekti",
        "Har xil o'lchamdagi versiyalar ro'yxati (oxiri — eng katta)",
        "URL string",
        "file_id string"],
       "B", explanation="m.photo[-1] — eng katta versiyasi.",
       diff="Medium", pts=3),
    mc("Lokal fayl yuborish:",
       ["m.answer_photo('path/to/file.jpg')",
        "m.answer_photo(FSInputFile('path/to/file.jpg'))",
        "m.send_photo('file.jpg')",
        "Faqat file_id"],
       "B", diff="Easy", pts=2),
    mc("Quyidagilardan qaysilari MAVJUD content filter'lar?",
       ["F.photo",
        "F.video",
        "F.document",
        "F.voice",
        "F.sticker",
        "F.email"],
       "A,B,C,D,E", multi=True,
       hint="F.email — yo'q (regex bilan).",
       diff="Easy", pts=2),
    mc("Album (media group) yuborish uchun:",
       ["bot.send_photo bir nechta marta",
        "MediaGroupBuilder + bot.send_media_group",
        "Inline keyboard",
        "Faqat URLInputFile"],
       "B", explanation="Max 10 ta media, caption faqat birinchisida.",
       diff="Medium", pts=3),
    dd("Foydalanuvchidan rasm qabul qilib saqlash",
       ["@dp.message(F.photo)",
        "async def get_photo(m: Message):",
        "    photo = m.photo[-1]",
        "    file = await bot.get_file(photo.file_id)",
        "    local = f'uploads/{m.from_user.id}_{photo.file_unique_id}.jpg'",
        "    await bot.download_file(file.file_path, local)",
        "    await m.answer(f'Saqlandi: {local}')"],
       diff="Hard", pts=4),
    ti("Production'da har gal `FSInputFile` ishlatish nima uchun yomon va `file_id` saqlash patterni qanday?",
       "Sabab: FSInputFile har chaqirilganda fayl Telegram'ga UPLOAD bo'ladi. "
       "Sekin (katta fayl 5-30s), traffic ko'p, server I/O. 100 user uchun logo yuborish — 100 marta upload. "
       "Yechim — file_id pattern: 1) Birinchi marta admin (yoki bot ishga tushganda) faylni yuboradi, "
       "msg.photo[-1].file_id ni log/DB'ga saqlaydi; "
       "2) Keyingi safar — m.answer_photo(LOGO_FILE_ID) — bevosita ID bilan, INSTANT. "
       "config.py'da: FILES = {'logo': 'AgACAg...', 'banner': 'AgAC...'}. "
       "Production: DB jadval 'media_cache' (key → file_id). Birinchi yuborganda saqlash, keyingi safar olish.",
       hint="Upload narxi va caching.",
       diff="Hard", pts=4),
]
L9_EX: list = [
    mc("Bot guruhda xabarlarni ko'rishi uchun BotFather'da:",
       ["/setname",
        "/setprivacy → DISABLE",
        "/newbot",
        "Hech narsa"],
       "B", explanation="Privacy mode'da bot faqat /commands va mention ko'radi.",
       diff="Medium", pts=3),
    mc("Reply pattern (admin commands uchun) qanday ishlaydi?",
       ["Username yozish",
        "Admin kerakli user xabariga reply qiladi, keyin /ban — m.reply_to_message.from_user.id'dan target oladi",
        "Telefon raqami",
        "Inline keyboard"],
       "B", explanation="Standard Telegram pattern. user_id ni qo'l bilan yozish chiroyli emas.",
       diff="Medium", pts=3),
    mc("Kick = ban + ___",
       ["mute",
        "unban (darhol)",
        "delete",
        "restart"],
       "B", explanation="Ban → user chiqib ketadi. Darhol unban — qaytib qo'shilishi mumkin.",
       diff="Medium", pts=3),
    mc("CAPTCHA pattern guruh'da nima uchun foydali?",
       ["Estetika",
        "Yangi a'zo'ni mute → tugma bosgach unmute — botlardan saqlanish",
        "Spam himoya emas",
        "Faqat statistika"],
       "B", explanation="Spam botlar avtomatik join + reklama. CAPTCHA — to'siq.",
       diff="Hard", pts=4),
    mc("Quyidagilardan qaysilari MAVJUD anti-spam:",
       ["Link o'chirish (URL pattern)",
        "Telefon o'chirish (\\d{10,})",
        "Forward o'chirish (F.forward_from)",
        "Taqiqlangan so'zlar",
        "Pe vaktdan ko'p xabar"],
       "A,B,C,D,E", multi=True, diff="Medium", pts=3),
    dd("Mute komandasi (1 soatga)",
       ["from datetime import datetime, timedelta",
        "from aiogram.types import ChatPermissions",
        "@dp.message(Command('mute'), IsGroupAdmin())",
        "async def cmd_mute(m: Message):",
        "    if not m.reply_to_message: return",
        "    target = m.reply_to_message.from_user",
        "    await m.chat.restrict(",
        "        target.id,",
        "        permissions=ChatPermissions(can_send_messages=False),",
        "        until_date=datetime.now() + timedelta(hours=1),",
        "    )",
        "    await m.answer(f'{target.full_name} mute qilindi')"],
       diff="Hard", pts=4),
    ti("`ChatMemberUpdated` event va `new_chat_members` field orasidagi farq nima?",
       "ChatMemberUpdated — har user status o'zgarganda (member→admin, member→banned, kicked). "
       "Yangi event tizimi (2021 dan keyin). Bot allowed_updates'da chat_member yoqilgan bo'lishi shart. "
       "new_chat_members — eski Message ichida ('user qo'shildi' xabari ko'rinishida). "
       "Hozir tavsiya — ChatMemberUpdated, chunki: 1) Aniqroq event'lar (admin status ham); "
       "2) Service xabar (Message) yaratilmaydi (chiroyli); 3) Privacy mode bilan ham ishlaydi. "
       "Yagona kamchilik: chat_member faqat bot admin bo'lganda keladi. Privacy DISABLE shart emas, "
       "lekin bot allowed_updates ro'yxatida bo'lishi va dp.start_polling(allowed_updates=...) bilan.",
       hint="Eski (Message) vs yangi (Event).",
       diff="Hard", pts=4),
]
R3_EX: list = [
    mc("Shop bot uchun savatcha (cart) qaerda saqlanadi?",
       ["FSM state'da",
        "DB jadval (cart_items: user_id, product_id, miqdor) — bot restart bo'lsa ham saqlanadi",
        "Faqat memory'da",
        "URL'da"],
       "B", explanation="State — checkout uchun. Cart — DB (uzoq muddat).",
       diff="Medium", pts=3),
    mc("Rasmni har gal yuborish o'rniga:",
       ["Lokal saqlash",
        "Birinchi marta upload, photo_id ni DB'da saqlash, keyingi safar photo_id bilan",
        "URL bilan har gal",
        "Mumkin emas"],
       "B", explanation="photo_id pattern — performance + UX.",
       diff="Medium", pts=3),
    mc("Yangi buyurtma kelganda adminlarni xabardor qilish:",
       ["Email yuborish",
        "for admin_id in ADMINS: await bot.send_message(admin_id, '...')",
        "Faqat ko'rinmasa",
        "Mumkin emas"],
       "B", diff="Easy", pts=2),
    mc("2 ta user oxirgi mahsulotni bir vaqtda buyurtma qildi. Bu nima?",
       ["Bug emas",
        "Race condition — DB transaction bilan stock'ni atomic kamaytirish kerak",
        "Hech qachon bo'lmaydi",
        "Faqat sintaktik"],
       "B", explanation="Production: SELECT ... FOR UPDATE yoki UPDATE ... WHERE stock > 0.",
       diff="Hard", pts=4),
    mc("Bu loyiha uchun KAMINA qanday komponentlar kerak?",
       ["6 ta DB jadval (Category, Product, User, CartItem, Order, OrderItem)",
        "DBSessionMiddleware",
        "UserCtxMiddleware",
        "Checkout FSM",
        "Admin paneli",
        "Hech narsa"],
       "A,B,C,D,E", multi=True, diff="Medium", pts=3),
    dd("Cart item miqdorini oshirish",
       ["@dp.callback_query(F.data.startswith('inc:'))",
        "async def inc(call: CallbackQuery, session: AsyncSession):",
        "    item_id = int(call.data.split(':')[1])",
        "    item = await session.get(CartItem, item_id)",
        "    item.miqdor += 1",
        "    await session.commit()",
        "    await call.answer('✅')",
        "    # qayta render cart"],
       diff="Hard", pts=4),
    ti("Hozircha sxemada nima yo'q (production'da kerak bo'lardi)?",
       "1) Stock (mahsulot mavjudligi raqami) — mahsulot tugagan bo'lsa ogohlantirish; "
       "2) Buyurtma holati (yangi → tasdiqlangan → tayyor → yetkazilgan → bekor) state machine; "
       "3) Yetkazib berish vaqti va kuryer; "
       "4) Promo code / chegirma; "
       "5) Reyting va izoh (foydalanuvchi mahsulotga baho beradi); "
       "6) Hisobot — kategoriya bo'yicha sotuv, top mahsulot, kun bo'yicha trend; "
       "7) Multi-tilli (uz/ru/en); "
       "8) Real-time order tracking (kuryer joylashuvi); "
       "9) Payment integration (Click, Payme, Telegram Stars/Payments); "
       "10) Push notification (broadcast — yangi mahsulot, chegirma). "
       "Capstone'da shu sxemani kengaytirish.",
       hint="E-commerce real funksiyalar.",
       diff="Hard", pts=4),
]
L10_EX: list = [
    mc("Polling va Webhook orasidagi farq?",
       ["Hech qanday",
        "Polling: bot Telegram'dan so'rab turadi (dev). Webhook: Telegram bot'ga push qiladi (prod, tezroq)",
        "Polling tezroq",
        "Webhook faqat Python'da"],
       "B", diff="Easy", pts=2),
    mc("Webhook uchun nima MAJBURIY?",
       ["VPS",
        "HTTPS server",
        "Custom domain",
        "Docker"],
       "B", explanation="Telegram faqat HTTPS qabul qiladi. Self-signed sertifikat ham mumkin, lekin Railway/Render avto-beradi.",
       diff="Medium", pts=3),
    mc("Bot token'ni kodda yozish nima xato?",
       ["Performance",
        "GitHub'ga push bo'lsa, botlar topadi va o'g'irlaydi — token bilan bot'ni boshqaradi",
        "Sintaksis",
        "Hech qanday"],
       "B", explanation="Doim .env + os.getenv() + .gitignore.",
       diff="Medium", pts=3),
    mc("Bepul tier'da Telegram bot uchun qaysi platform tavsiya?",
       ["AWS",
        "Railway ($5 credit) yoki Render (750 soat/oy)",
        "Heroku (bepul yo'q endi)",
        "Faqat VPS"],
       "B", explanation="Railway eng oson, GitHub bilan auto-deploy.",
       diff="Easy", pts=2),
    mc("WEBHOOK_SECRET nima uchun kerak?",
       ["Performance",
        "Webhook'ga kelgan request'lar haqiqatan Telegram'dan ekanini tasdiqlash (X-Telegram-Bot-Api-Secret-Token header)",
        "Faqat estetika",
        "Auth"],
       "B", explanation="Aks holda har kim webhook URL'ga sasi sasi update yuborishi mumkin.",
       diff="Hard", pts=4),
    dd("Railway'da bot deploy qadamlari",
       ["1. railway.app'ga GitHub bilan kirish",
        "2. New Project → Deploy from GitHub repo",
        "3. Repo tanlash",
        "4. Variables tab: BOT_TOKEN, WEBHOOK_SECRET, USE_WEBHOOK=1",
        "5. Settings → Generate Domain → URL olamiz",
        "6. WEBHOOK_URL = generated URL",
        "7. Deploy avtomatik boshlanadi",
        "8. Logs tab'da loglar, Bot'ga /start"],
       diff="Medium", pts=3),
    ti("Multi-instance bot (3 ta replica) ishlatish uchun FSM storage qanday bo'lishi kerak va nima uchun?",
       "Memory storage — yaramaydi. Har instance o'z RAM'iga ega, foydalanuvchi 1-instance'da ism kiritsa, "
       "2-instance'da yosh — state yo'q (boshqa RAM). "
       "Yechim: RedisStorage. Bir Redis — barcha instance'lar ulanadi, state shared. "
       "Misol: instance A user.set_state(yosh) — Redis'ga yozadi. Instance B keladi — Redis'dan o'qiydi. "
       "Plus: bot restart bo'lsa, state yo'qolmaydi. "
       "RedisStorage.from_url('redis://...') + dp = Dispatcher(storage=storage). "
       "Production sozlash: managed Redis (Railway/Upstash/Render) — 256 MB bepul. "
       "Yagona kamchilik: Redis ulanish — latency qo'shadi (1-5ms), lekin scale uchun zarur.",
       hint="Distributed state.",
       diff="Hard", pts=4),
]
L11_EX: list = [
    mc("Yakuniy capstone'da nechta interface bor?",
       ["1 (faqat user)",
        "3 ta: User (mijoz), Admin, Kuryer — yagona bot ichida yoki alohida botlar",
        "5+",
        "Faqat admin"],
       "B", explanation="Real delivery sistema — 3 ta role.",
       diff="Easy", pts=2),
    mc("Bu loyiha uchun MAJBURIY texnologiyalar:",
       ["aiogram 3.x",
        "PostgreSQL + SQLAlchemy async",
        "Redis (FSM storage)",
        "Webhook deployment (Railway/Render)",
        "PHP",
        "Alembic migrations"],
       "A,B,C,D,F", multi=True, hint="PHP — yo'q.", diff="Medium", pts=3),
    mc("Multi-til (uz/ru) qanday qo'shamiz?",
       ["Har handler'da if/else",
        "I18nMiddleware — data['_'] = translator funksiya; handler argument _ qabul qiladi",
        "Faqat database",
        "Mumkin emas"],
       "B", explanation="Gettext yoki oddiy dict — middleware bilan inject.",
       diff="Hard", pts=4),
    mc("Real-time admin notification yangi buyurtma kelganda:",
       ["Email",
        "for admin_id in ADMINS: await bot.send_message(admin_id, ...)",
        "Faqat polling",
        "Webhook"],
       "B", explanation="Same as R3, lekin admin paneli + accept/reject tugmalari.",
       diff="Easy", pts=2),
    mc("Bonus uchun qaysilari real biznes uchun foydali?",
       ["Click va Payme integratsiya (O'zbekiston to'lov)",
        "Mini App (chiroyli UI)",
        "Loyalty programma",
        "Yandex Maps tracking",
        "OpenAI menyu generation",
        "AI image generation har xabarga"],
       "A,B,C,D", multi=True,
       hint="OpenAI menyu — foydali, lekin har xabarga AI image — qimmat va keraksiz.",
       diff="Hard", pts=4),
    dd("Yakuniy deploy bosqichlari",
       ["1. GitHub'ga code push",
        "2. Railway: New Project from GitHub",
        "3. Variables: BOT_TOKEN, DB_URL, REDIS_URL, WEBHOOK_SECRET, WEBHOOK_URL",
        "4. Settings → Generate Domain",
        "5. PostgreSQL addon (Railway/Supabase)",
        "6. Redis addon (Railway/Upstash)",
        "7. Alembic migrations (Procfile: web: alembic upgrade head && python -m bot.main)",
        "8. Logs'da tekshirish",
        "9. Bot'ga /start"],
       diff="Hard", pts=4),
    ti("Bu loyihani CV'da qanday yozasiz va u sizga qanday foyda beradi?",
       "CV'da: 'Telegram Delivery Bot — fullstack delivery system (aiogram 3.x + PostgreSQL + Redis + Railway). "
       "3 ta role: user/admin/courier. Multi-til (uz/ru), real-time orders, payment integratsiya. "
       "GitHub: link. Live: @username_bot. Texnologiyalar: aiogram 3, SQLAlchemy async, Alembic, Docker, GitHub Actions.' "
       "Foyda: 1) Real ish (Tashkent'da Telegram dev — 5-15 mln/oy); "
       "2) Freelance (har dukon shu narsani xohlaydi); "
       "3) O'z biznesi (kichik restoran'ga white-label sotish — $200-500/oy); "
       "4) Interview uchun klassik tema (async, ORM, deploy, FSM, middleware); "
       "5) Senior Python ko'nikmasi — bu darajada loyiha kam dev'larda; "
       "6) Portfolio yulduzlari — GitHub Stars, live demo. "
       "Bu — 1 ta loyiha 5 ta foyda.",
       hint="CV, ish, biznes, portfolio.",
       diff="Easy", pts=2),
]


LESSON_TASKS: dict = {
    0: {
        "title": "Birinchi aiogram bot",
        "description": "BotFather'da bot, aiogram 3.x setup, birinchi handler'lar.",
        "requirements": (
            "• @BotFather'da yangi bot (screenshot)\n"
            "• Virtual env + aiogram + python-dotenv\n"
            "• .env'da BOT_TOKEN, .gitignore'da .env\n"
            "• /start, /help, /info, /id handler'lari\n"
            "• Echo handler\n"
            "• HTML format'lash (bold, italic, code)\n"
            "• `default=DefaultBotProperties(parse_mode=ParseMode.HTML)`\n"
            "• Bot.get_me() bilan info ko'rsatish\n"
            "• Screenshot: bot bilan chat"
        ),
        "technologies": "aiogram 3.x, BotFather, python-dotenv, asyncio",
        "deadline_days": 3,
    },
    1: {
        "title": "Filter'lar bilan ko'p turli handler'lar",
        "description": "Magic F filter'lar va Command filter'lar bilan rang-barang bot.",
        "requirements": (
            "• Kamida 10 ta handler turli filter bilan\n"
            "• /start, /help, /echo &lt;matn&gt;, /calc, /weather (mock)\n"
            "• F.text aniq matn (kamida 3 ta)\n"
            "• F.text.lower().contains() — case-insensitive\n"
            "• F.text.regexp() — kamida 2 ta pattern (telefon, email)\n"
            "• F.photo, F.voice, F.sticker, F.location handler'lari\n"
            "• Admin only handler (F.from_user.id.in_)\n"
            "• CommandObject bilan arg'lar\n"
            "• Catch-all eng oxirda\n"
            "• Filter tartibi xato qilib ko'rsatib tuzatish"
        ),
        "technologies": "aiogram, Magic F, Command, CommandObject, content filters",
        "deadline_days": 3,
    },
    2: {
        "title": "Reply keyboard bilan menyu",
        "description": "Tugmalar bilan asosiy menyu va kontakt/joylashuv so'rash.",
        "requirements": (
            "• `BTN` konstantalar klassi\n"
            "• 4-5 ta tugma asosiy menyu\n"
            "• ReplyKeyboardBuilder bilan adjust(...)\n"
            "• Kontakt so'rash (request_contact=True)\n"
            "• Joylashuv so'rash (request_location=True)\n"
            "• one_time_keyboard misoli\n"
            "• input_field_placeholder\n"
            "• ReplyKeyboardRemove — yashirish\n"
            "• Dinamik grid (cols=2)\n"
            "• Har tugma uchun aniq handler"
        ),
        "technologies": "aiogram, ReplyKeyboardMarkup, ReplyKeyboardBuilder, KeyboardButton",
        "deadline_days": 3,
    },
    3: {  # R1
        "title": "🔁 R1: Echo bot + 3-darajali menyu",
        "description": (
            "Modul 1 ning hammasi birga: restoran/dukon menyu boti — "
            "kategoriyalar, mahsulotlar, kontent."
        ),
        "requirements": (
            "• 4 ta bosh menyu tugma (Taomlar, Ichimliklar, Bog'lanish, Bot haqida)\n"
            "• 2-daraja submenyu (Taomlar → Pizza/Burger/Taco/Lag'mon)\n"
            "• 2-daraja submenyu (Ichimliklar → Choy/Kofe/Sok)\n"
            "• 3-daraja kontent (rasm + narx + tavsif + Orqaga)\n"
            "• Rasm — URLInputFile bilan (Unsplash)\n"
            "• PRODUCTS dict bilan kontent\n"
            "• Echo (catch-all) eng oxirda\n"
            "• HTML format'lash, emoji\n"
            "• Screenshot: 3 darajali navigatsiya"
        ),
        "technologies": "aiogram, ReplyKeyboard, URLInputFile, multi-level menu",
        "deadline_days": 4,
    },
    4: {
        "title": "Inline keyboard va callback bilan rating bot",
        "description": "Inline tugmalar bilan baholash, pagination va kanal links.",
        "requirements": (
            "• /rate — Like/Dislike\n"
            "• /stars — 1-5 yulduz, callback bilan edit_text\n"
            "• Doim call.answer() (loading to'xtatish)\n"
            "• CallbackData klassi (kamida 2 ta misol)\n"
            "• /orders — fake buyurtmalar + actions (view/edit/delete)\n"
            "• Tasdiqlovchi tugma (delete uchun)\n"
            "• /list — 50 ta item, pagination (5/sahifa)\n"
            "• /link — URL tugmalar (3+ social media)\n"
            "• show_alert=True misoli\n"
            "• Ataylab answer'siz handler — sabab tushuntirish"
        ),
        "technologies": "aiogram, InlineKeyboard, CallbackData, pagination, edit_text",
        "deadline_days": 4,
    },
    5: {
        "title": "FSM bilan ro'yxatdan o'tish",
        "description": "Multi-step form: ism → familiya → yosh → jins → shahar → telefon.",
        "requirements": (
            "• MemoryStorage o'rnatish\n"
            "• StatesGroup — 5-7 ta state\n"
            "• Har bosqichda progress (3/7)\n"
            "• Validatsiya har bosqichda (yosh 14-100, ism 2-50 belgi)\n"
            "• Inline keyboard FSM bilan (jins, shahar)\n"
            "• Reply keyboard kontakt so'rash\n"
            "• Tasdiqlash sahifasi (ma'lumotlar + 2 tugma)\n"
            "• Yakuniy save_user() + state.clear()\n"
            "• /cancel har bosqichda ishlatish\n"
            "• MemoryStorage vs RedisStorage haqida hisobot"
        ),
        "technologies": "aiogram, FSM, StatesGroup, FSMContext, MemoryStorage, validation",
        "deadline_days": 4,
    },
    6: {
        "title": "Filter'lar, middleware'lar bilan auth bot",
        "description": "Custom filter (IsAdmin, NotBanned) va 4 ta middleware.",
        "requirements": (
            "• LoggingMiddleware — har xabarni log\n"
            "• UserContextMiddleware — user'ni avto-yaratish, data['user']'ga\n"
            "• RateLimitMiddleware (5 xabar 10s)\n"
            "• IsAdmin filter klass\n"
            "• NotBanned filter klass (data['user'] bilan)\n"
            "• /profile, /admin, /users, /ban, /unban, /stats handler'lar\n"
            "• Admin orasidagi farq UI'da ko'rinishi\n"
            "• Try/except middleware'da\n"
            "• Multi-language welcome (bonus)\n"
            "• Hisobot: middleware tartibi (logging → throttling → DB → auth)"
        ),
        "technologies": "aiogram, BaseFilter, BaseMiddleware, custom auth, rate-limit",
        "deadline_days": 5,
    },
    7: {  # R2
        "title": "🔁 R2: Anketa to'ldiruvchi bot",
        "description": (
            "Modul 2 takrorlash: FSM + inline + filter + middleware birga. "
            "Real anketa bot admin paneli bilan."
        ),
        "requirements": (
            "• 7 bosqichli FSM (ism, familiya, yosh, jins, shahar, telefon, tasdiq)\n"
            "• Inline jins va shahar tanlash\n"
            "• Progress 'N/7' har bosqichda\n"
            "• Validatsiya + xato xabarlari\n"
            "• Tasdiqlash sahifa (ma'lumotlar + 2 tugma)\n"
            "• Tahrirlash → boshidan (bonus: bosqich tanlash)\n"
            "• Save → APPLICATIONS dict + admin xabar\n"
            "• /applications — admin only paginated ro'yxat\n"
            "• Har anketa uchun view/delete inline\n"
            "• LoggingMiddleware\n"
            "• /cancel har bosqichda"
        ),
        "technologies": "aiogram, FSM, inline, filter, middleware, pagination",
        "deadline_days": 6,
    },
    8: {
        "title": "SQLAlchemy async bilan production bot",
        "description": "Anketa bot'ni real DB bilan (PostgreSQL yoki SQLite).",
        "requirements": (
            "• sqlalchemy[asyncio] + asyncpg yoki aiosqlite\n"
            "• User, Order models (Mapped pattern)\n"
            "• Relationship + selectinload\n"
            "• DBSessionMiddleware\n"
            "• UserContextMiddleware (get_or_create)\n"
            "• /buy, /orders, /stats, /profile handler'lari\n"
            "• Service/Repository pattern (UserService, OrderService)\n"
            "• init_db() — birinchi marta\n"
            "• Transactions misoli (session.begin())\n"
            "• N+1 problem misoli va selectinload yechimi"
        ),
        "technologies": "aiogram, SQLAlchemy async, AsyncSession, Mapped, repository pattern",
        "deadline_days": 5,
    },
    9: {
        "title": "Fayllar bilan ishlovchi shop bot",
        "description": "Rasm, hujjat, voice qabul va yuborish, file_id caching.",
        "requirements": (
            "• /photo, /doc, /album, /voice — yuborish\n"
            "• FSInputFile, URLInputFile, BufferedInputFile, file_id — 4 variant\n"
            "• F.photo handler — bot.get_file + download_file\n"
            "• Local'ga saqlash (uploads/)\n"
            "• F.document — hajm va MIME filter\n"
            "• F.voice — duration limit\n"
            "• F.sticker — qaytarish\n"
            "• F.location — Google Maps link\n"
            "• MediaGroupBuilder bilan album (4+ rasm)\n"
            "• file_id cache pattern + tushuntirish\n"
            "• answer_photo caption + reply_markup"
        ),
        "technologies": "aiogram, FSInputFile, URLInputFile, file handling, MediaGroup",
        "deadline_days": 4,
    },
    10: {
        "title": "Guruh admin bot",
        "description": "Guruh boshqaruv: ban/mute/kick + CAPTCHA + anti-spam.",
        "requirements": (
            "• BotFather: /setprivacy → DISABLE\n"
            "• Bot'ni guruhga admin qilish (screenshot)\n"
            "• IsGroup, IsGroupAdmin filter'lar\n"
            "• /ban, /kick, /mute &lt;daqiqa&gt;, /unmute, /pin, /del (reply pattern)\n"
            "• ChatMemberUpdated bilan welcome\n"
            "• CAPTCHA — yangi a'zo mute + inline tugma\n"
            "• Tugma boshqalarni e'tibordan tashqari qoldirish\n"
            "• Anti-spam: URL, telefon, taqiqlangan so'zlar\n"
            "• Forward block (faqat oddiy user)\n"
            "• /rules buyrug'i\n"
            "• allowed_updates=dp.resolve_used_update_types()"
        ),
        "technologies": "aiogram, ChatMemberUpdated, ChatPermissions, anti-spam, CAPTCHA",
        "deadline_days": 5,
    },
    11: {  # R3
        "title": "🔁 R3: Mini-shop bot",
        "description": (
            "Modul 3 takrorlash: to'liq e-commerce bot. DB + Files + Admin birga."
        ),
        "requirements": (
            "• 6 ta DB jadval (Category, Product, User, CartItem, Order, OrderItem)\n"
            "• Seed data — 2 kategoriya, 4-6 mahsulot\n"
            "• Menyu navigatsiya (categories → products → product card)\n"
            "• Mahsulot rasmi photo_id bilan\n"
            "• Savatcha (+/-/o'chirish) — DB'da saqlanadi\n"
            "• Checkout FSM (telefon, manzil, izoh, tasdiq)\n"
            "• Yakuniy saqlash (orders + order_items) + cart tozalash\n"
            "• Admin paneli (/orders) — real-time notification\n"
            "• Mahsulot CRUD admin uchun (bonus)\n"
            "• file_id caching"
        ),
        "technologies": "aiogram, SQLAlchemy async, FSM, inline, file_id, e-commerce",
        "deadline_days": 7,
    },
    12: {
        "title": "Production'ga deploy",
        "description": "Webhook bilan Railway/Render'ga deploy.",
        "requirements": (
            "• USE_WEBHOOK flag bilan polling/webhook tanlash\n"
            "• SimpleRequestHandler + aiohttp\n"
            "• WEBHOOK_SECRET tekshirish\n"
            "• .env va .env.example\n"
            "• requirements.txt + Procfile\n"
            "• Railway'da deploy + Generate Domain\n"
            "• Variables sozlash (BOT_TOKEN, WEBHOOK_URL, ...)\n"
            "• Live URL bilan ishlovchi bot (screenshot)\n"
            "• Health check endpoint (/health)\n"
            "• Logging stdout'ga\n"
            "• RedisStorage (Upstash bepul)\n"
            "• Dockerfile + docker-compose (bonus)"
        ),
        "technologies": "aiogram, webhook, aiohttp, Railway, Docker, Redis, deploy",
        "deadline_days": 5,
    },
    13: {  # L11 — CAPSTONE
        "title": "🚀 CAPSTONE: To'liq delivery bot",
        "description": (
            "Kursning yakuniy loyihasi: 3 hafta professional delivery bot. "
            "User + Admin + Kuryer interface, production deploy, real biznes uchun mos."
        ),
        "requirements": (
            "Foundation:\n"
            "• Toza project structure (handlers/user/, admin/, courier/)\n"
            "• 8+ ta DB jadval (User, Category, Product, Order, OrderItem, Courier, ...)\n"
            "• Alembic migrations\n"
            "• Service/Repository pattern\n"
            "\n"
            "User funksiyalar:\n"
            "• Multi-til (uz/ru) — i18n middleware\n"
            "• Katalog (kategoriya → product → tafsilot)\n"
            "• Savatcha DB'da\n"
            "• Checkout FSM (telefon, manzil/location, izoh, tasdiq)\n"
            "• Buyurtma tracking (kutmoqda → tasdiqlangan → yetkazilmoqda → yetkazildi)\n"
            "• Tarix\n"
            "• Reyting va izoh\n"
            "\n"
            "Admin paneli:\n"
            "• Real-time notification yangi buyurtma\n"
            "• Buyurtma qabul/rad + kuryer yo'naltirish\n"
            "• Mahsulot CRUD FSM bilan\n"
            "• Kategoriya CRUD\n"
            "• Statistika (daromad, top mahsulot)\n"
            "• Broadcast — barcha userlarga xabar (rasm bilan)\n"
            "• Kuryer boshqaruvi\n"
            "• Excel export (bonus)\n"
            "\n"
            "Kuryer:\n"
            "• Yangi buyurtma push notification\n"
            "• Qabul/rad qilish\n"
            "• Mijoz manzili + Yandex Maps link\n"
            "• Status update (Olib ketdim → Yo'lda → Yetkazdim)\n"
            "• Live location yuborish\n"
            "\n"
            "Production:\n"
            "• PostgreSQL (Railway/Supabase)\n"
            "• Redis FSM storage\n"
            "• Webhook deployment\n"
            "• .env.example + README\n"
            "• Logging (stdout) + Sentry/Logtail\n"
            "• Health check endpoint\n"
            "• Docker compose\n"
            "\n"
            "Sifat:\n"
            "• Pytest bilan testlar (kamida 5)\n"
            "• Type hints\n"
            "• Ruff/Black\n"
            "• Pre-commit hooks\n"
            "• GitHub Actions CI\n"
            "\n"
            "Yakuniy yetkazib berish:\n"
            "• GitHub repo URL (chiroyli README)\n"
            "• Live bot URL\n"
            "• Demo video 5-10 daqiqa\n"
            "• Hisobot (texnologiyalar, qiyin qism, bonus, statistika)\n"
            "\n"
            "Bonus (CV uchun zo'r):\n"
            "• Click/Payme integratsiya\n"
            "• Telegram Mini App\n"
            "• Loyalty programma\n"
            "• Web admin paneli (FastAPI/Flask)\n"
            "• AI menyu suggestions"
        ),
        "technologies": (
            "aiogram 3.x, PostgreSQL, SQLAlchemy async, Alembic, Redis, "
            "webhook, aiohttp, Railway, Docker, pytest, i18n, multi-role"
        ),
        "deadline_days": 21,
    },
}


LESSONS = [
    {"order": 0,  "title": "1-BotFather, token va birinchi 'Salom' bot",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/Z6m4HtgKxRk", "exercises": L1_EX, "_ref": "L1"},
    {"order": 1,  "title": "2-Message handler'lar (/start, /help, text, regex)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/p4xS0xL5RyA", "exercises": L2_EX, "_ref": "L2"},
    {"order": 2,  "title": "3-Reply keyboard'lar va tugma boshqaruvi",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/3p9NnyukH5g", "exercises": L3_EX, "_ref": "L3"},
    {"order": 3,  "title": "R1-Echo bot + 3 darajali menyu (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/EUH-NkO_NvE", "exercises": R1_EX, "_ref": "R1"},
    {"order": 4,  "title": "4-Inline keyboard va callback_data",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/oXAJEKhrkqQ", "exercises": L4_EX, "_ref": "L4"},
    {"order": 5,  "title": "5-FSM — multi-step formalar",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/8YkmEvbJDFc", "exercises": L5_EX, "_ref": "L5"},
    {"order": 6,  "title": "6-Filter'lar va middleware (auth, rate-limit)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/0aEtR9G9TQg", "exercises": L6_EX, "_ref": "L6"},
    {"order": 7,  "title": "R2-Anketa to'ldiruvchi bot (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/Cv2zmqEZyBA", "exercises": R2_EX, "_ref": "R2"},
    {"order": 8,  "title": "7-SQLAlchemy async bilan database",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/u_dQAo2k4Nk", "exercises": L7_EX, "_ref": "L7"},
    {"order": 9,  "title": "8-Fayllar bilan ishlash (rasm, hujjat, voice)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/PHV28U2VWLA", "exercises": L8_EX, "_ref": "L8"},
    {"order": 10, "title": "9-Guruh va kanal admin xususiyatlari",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/JjFidM5ywMg", "exercises": L9_EX, "_ref": "L9"},
    {"order": 11, "title": "R3-Mini-shop bot (takrorlash)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/I6ifo46wIBE", "exercises": R3_EX, "_ref": "R3"},
    {"order": 12, "title": "10-Webhook va deploy (Railway, env, logging)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/Acwj7gfMfRk", "exercises": L10_EX, "_ref": "L10"},
    {"order": 13, "title": "11-CAPSTONE: To'liq delivery bot (admin + payment)",
     "text": None, "code": None, "lang": "python",
     "video": "https://youtu.be/vd5HTcrk7TI", "exercises": L11_EX, "_ref": "L11"},
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
