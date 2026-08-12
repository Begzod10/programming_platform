"""Telegram Bot Track, follow-up course: "Telegram Bot: Ilg'or Mavzular".

Pure-data course spec — see course_builder/__init__.py for the contract.
Advanced follow-up to course 48 (Telegram Bot aiogram). Assumes the student
already knows aiogram basics (handlers, keyboards, FSM basics, filters/
middleware basics, async SQLAlchemy, file handling, group admin, webhook
deploy) and covers genuinely new ground: Telegram Mini Apps + initData
security, the real Telegram Payments API, Redis-backed FSM for horizontal
scaling, testing bots with pytest, structured logging/observability,
production rate limiting, dispatcher/middleware internals, multi-bot
(bot-farm) architecture, i18n, graceful shutdown/zero-downtime deploy, and
a final capstone.

Build with:
    cd backend
    python scripts/build_course.py scripts/course_specs/telegram_bot_advanced.py --dry-run
    python scripts/build_course.py scripts/course_specs/telegram_bot_advanced.py
"""

COURSE = {'title': "Telegram Bot: Ilg'or Mavzular",
 'description': "Telegram Bot aiogram kursidan keyingi ilg'or bosqich: Telegram Mini Apps (WebApp) "
                'va initData xavfsizligi, real Telegram Payments API (invoice, pre_checkout_query, '
                "successful_payment, Stars), Redis'ga asoslangan FSM orqali gorizontal "
                'masshtablash, pytest bilan botlarni testlash, strukturaviy logging/observability, '
                'production darajasidagi rate limiting, aiogram dispatcher/middleware ichki '
                "tuzilishi, ko'p botli (bot-farm) arxitektura, ko'p tilli botlar uchun i18n, "
                'graceful shutdown va zero-downtime deploy. Yakuniy capstone — Mini App, real '
                "to'lovlar va Redis FSM'ni birlashtirgan to'liq bot.",
 'instructor_id': 2,
 'difficulty_level': 'Advanced',
 'duration_weeks': 5,
 'max_points': 600,
 'category_id': 12,
 'prerequisite_course_id': 48,
 'display_order': 701,
 'image_url': 'https://web.telegram.org/img/logo_share.png',
 'thumbnail_url': 'https://upload.wikimedia.org/wikipedia/commons/8/83/Telegram_2019_Logo.svg',
 'is_active': True,
 'is_published': False}


LESSONS = [{'order': 0,
  'title': '1-Telegram Mini Apps (WebApp): web_app tugmasi va Telegram.WebApp JS API',
  'title_ru': '1-Telegram Mini Apps (WebApp): кнопка web_app и JS API Telegram.WebApp',
  'points_reward': 16,
  'code_language': 'python',
  'text_content': '<h3>Oddiy bot doirasidan tashqariga chiqish</h3>\n'
                  '<p>48-kursda siz reply va inline klaviaturalar bilan ishladingiz &mdash; '
                  'foydalanuvchi tugmani bosadi, bot matn yoki callback_data oladi. Bu yetarli '
                  "bo'lgan holatlar ko'p, lekin forma to'ldirish, katalog ko'rish, xarita tanlash "
                  "kabi vazifalarda matn-asosli interfeys tezda noqulay bo'lib qoladi. Telegram "
                  'buning uchun <strong>Mini App</strong> (WebApp) deb ataladigan mexanizmni '
                  "taqdim etadi &mdash; bot ichida ochiladigan to'liq huquqli veb-sahifa, "
                  "HTML/CSS/JS bilan yozilgan, lekin Telegram'ning o'zi bilan "
                  'integratsiyalashgan.</p>\n'
                  '\n'
                  '<h3>web_app tugmasi: ikki xil joyda, ikki xil xulq-atvor</h3>\n'
                  "<p>Mini App'ni ochish uchun ikkita joy bor, va ular <em>bir xil emas</em>:</p>\n"
                  '<ul>\n'
                  '<li><code>KeyboardButton(text="...", web_app=WebAppInfo(url="..."))</code> '
                  '&mdash; reply klaviaturada, faqat <strong>shaxsiy chatda</strong> ishlaydi. '
                  'Sahifa <code>Telegram.WebApp.sendData(text)</code> chaqirsa, bot tomonga oddiy '
                  '<code>message</code> update keladi, unda <code>content_type == '
                  '"web_app_data"</code> va <code>message.web_app_data.data</code> ichida '
                  "yuborilgan matn bo'ladi.</li>\n"
                  '<li><code>InlineKeyboardButton(text="...", '
                  'web_app=WebAppInfo(url="..."))</code> &mdash; botning o\'z xabarida ishlaydi '
                  '(guruhda ham), lekin natijani qaytarish uchun boshqa mexanizm kerak &mdash; '
                  'inline rejimda <code>answerWebAppQuery</code> orqali.</li>\n'
                  '</ul>\n'
                  "<p>Amalda ko'p holatda kerak bo'ladigani &mdash; birinchisi: shaxsiy chatda "
                  '"Katalog ochish" tugmasi, foydalanuvchi tanlov qiladi, sahifa '
                  '<code>sendData</code> chaqiradi, bot javob beradi.</p>\n'
                  '\n'
                  '<h3>Telegram.WebApp JS API &mdash; sahifa ichida nima mavjud</h3>\n'
                  '<p>Mini App ochilganda, sahifangizga <code>&lt;script '
                  'src="https://telegram.org/js/telegram-web-app.js"&gt;&lt;/script&gt;</code> '
                  'ulanadi va global <code>window.Telegram.WebApp</code> obyekti paydo '
                  "bo'ladi:</p>\n"
                  '<table>\n'
                  '<tr><th>Metod / xususiyat</th><th>Vazifasi</th></tr>\n'
                  "<tr><td><code>WebApp.ready()</code></td><td>Sahifa tayyor ekanini Telegram'ga "
                  'bildiradi &mdash; splash screen yopiladi</td></tr>\n'
                  "<tr><td><code>WebApp.expand()</code></td><td>Sahifani to'liq balandlikka "
                  'kengaytiradi</td></tr>\n'
                  "<tr><td><code>WebApp.close()</code></td><td>Mini App'ni yopadi</td></tr>\n"
                  '<tr><td><code>WebApp.MainButton</code></td><td>Pastki katta tugma &mdash; '
                  '<code>setText()</code>, <code>show()</code>, <code>onClick()</code></td></tr>\n'
                  '<tr><td><code>WebApp.BackButton</code></td><td>Yuqori chap orqaga '
                  'tugmasi</td></tr>\n'
                  '<tr><td><code>WebApp.themeParams</code> / '
                  '<code>colorScheme</code></td><td>Foydalanuvchi Telegram mavzusiga (dark/light) '
                  'moslashtirish uchun ranglar</td></tr>\n'
                  '<tr><td><code>WebApp.initData</code> / '
                  "<code>initDataUnsafe</code></td><td>Foydalanuvchi haqida imzolangan ma'lumot "
                  '&mdash; keyingi darsda tekshiramiz</td></tr>\n'
                  "<tr><td><code>WebApp.sendData(data)</code></td><td>Ma'lumotni botga "
                  '<code>web_app_data</code> sifatida yuboradi va sahifani yopadi</td></tr>\n'
                  '<tr><td><code>WebApp.HapticFeedback</code></td><td>Qurilmada mayin tebranish '
                  '(vibratsiya) effektlari</td></tr>\n'
                  '</table>\n'
                  '\n'
                  '<h3>Nega initDataUnsafe nomida "Unsafe" so\'zi bor</h3>\n'
                  '<p>Bu ataylab shunday nomlangan &mdash; <code>initDataUnsafe</code> allaqachon '
                  'JavaScript obyektiga parslangan, lekin <strong>hali tasdiqlanmagan</strong> '
                  "ma'lumot. Har qanday foydalanuvchi brauzer konsolida shu obyektni o'zgartirishi "
                  "mumkin. Backend'ingiz unga ishonib, masalan, <code>user.id</code> asosida "
                  "ma'lumotlar bazasidan yozuv qaytarsa &mdash; boshqa birov o'zini xohlagan "
                  "foydalanuvchi qilib ko'rsatishi mumkin. Xom <code>initData</code> qatorini imzo "
                  '(hash) bilan tekshirish &mdash; bu keyingi darsning butun mavzusi.</p>\n'
                  '\n'
                  '<h3>Arxitektura: qayerda nima yashaydi</h3>\n'
                  '<p>Mini App uchun kamida ikkita qism kerak: HTTPS orqali xizmat qiladigan '
                  'statik sahifa (Telegram faqat <code>https://</code> manzillarni qabul qiladi, '
                  '<code>http://</code> yoki <code>localhost</code> ishlamaydi &mdash; test uchun '
                  "ngrok kabi tunnel kerak bo'ladi) va aiogram tomonidagi bot kodi, u tugmani "
                  "ro'yxatga oladi va qaytgan ma'lumotni qayta ishlaydi. Ikkalasi bitta serverda "
                  "ham, alohida serverlarda ham bo'lishi mumkin &mdash; muhimi, HTTPS.</p>\n"
                  '<pre class="mermaid">\n'
                  'flowchart TB\n'
                  '  A["Foydalanuvchi: \'Katalog\' tugmasini bosadi"] --> B["Telegram: WebView\'da '
                  'sahifani ochadi"]\n'
                  '  B --> C["Sahifa JS: WebApp.ready() + WebApp.expand()"]\n'
                  '  C --> D["Foydalanuvchi: mahsulot tanlaydi"]\n'
                  '  D --> E["Sahifa JS: WebApp.sendData(JSON)"]\n'
                  '  E --> F["Telegram: sahifani yopadi"]\n'
                  '  F --> G["Bot: message update, content_type=web_app_data"]\n'
                  '  G --> H["aiogram handler: message.web_app_data.data ni o\'qiydi"]\n'
                  '</pre>\n'
                  "<p>Diagramma shuni ko'rsatadi: <code>sendData</code> chaqirilgach, Telegram "
                  "avtomatik ravishda sahifani yopadi va botga oddiy xabar sifatida ma'lumot "
                  'yuboradi &mdash; alohida webhook yoki API chaqiruvi shart emas.</p>\n'
                  '\n'
                  "<h3>Fetch orqali muloqot &mdash; sendData'dan farqli yo'l</h3>\n"
                  '<p><code>sendData</code> faqat bitta marta, sahifa yopilishidan oldin ishlaydi. '
                  "Agar sahifa ochiq turgan holda backend bilan doimiy almashinuv kerak bo'lsa "
                  '(masalan, katalogni yuklash, buyurtma holatini kuzatish), oddiy '
                  "<code>fetch()</code> orqali o'z backend API'ingizga so'rov yuborilaveradi "
                  "&mdash; bu holatda foydalanuvchini aniqlash uchun <code>initData</code>'ni "
                  "so'rov sarlavhasida yuborish va uni backend'da tekshirish kerak bo'ladi "
                  '(keyingi darsning mavzusi).</p>',
  'text_content_ru': '<h3>Выход за рамки обычного бота</h3>\n'
                     '<p>В курсе 48 вы работали с reply- и inline-клавиатурами — пользователь '
                     'нажимает кнопку, бот получает текст или callback_data. Для многих задач '
                     'этого достаточно, но при заполнении форм, просмотре каталога, выборе на '
                     'карте текстовый интерфейс быстро становится неудобным. Telegram '
                     'предоставляет для этого механизм <strong>Mini App</strong> (WebApp) — '
                     'полноценную веб-страницу, открывающуюся внутри бота, написанную на '
                     'HTML/CSS/JS, но интегрированную с самим Telegram.</p>\n'
                     '\n'
                     '<h3>Кнопка web_app: два места, два разных поведения</h3>\n'
                     '<p>Открыть Mini App можно из двух мест, и они <em>не одинаковы</em>:</p>\n'
                     '<ul>\n'
                     '<li><code>KeyboardButton(text="...", web_app=WebAppInfo(url="..."))</code> — '
                     'в reply-клавиатуре, работает только в <strong>личном чате</strong>. Если '
                     'страница вызывает <code>Telegram.WebApp.sendData(text)</code>, боту приходит '
                     'обычное <code>message</code>-обновление, где <code>content_type == '
                     '"web_app_data"</code>, а отправленный текст лежит в '
                     '<code>message.web_app_data.data</code>.</li>\n'
                     '<li><code>InlineKeyboardButton(text="...", '
                     'web_app=WebAppInfo(url="..."))</code> — работает из собственного сообщения '
                     'бота (в том числе в группе), но для возврата результата нужен другой '
                     'механизм — в инлайн-режиме через <code>answerWebAppQuery</code>.</li>\n'
                     '</ul>\n'
                     '<p>На практике чаще всего нужен первый вариант: кнопка «Открыть каталог» в '
                     'личном чате, пользователь делает выбор, страница вызывает '
                     '<code>sendData</code>, бот отвечает.</p>\n'
                     '\n'
                     '<h3>Telegram.WebApp JS API — что доступно внутри страницы</h3>\n'
                     '<p>При открытии Mini App к вашей странице подключается <code>&lt;script '
                     'src="https://telegram.org/js/telegram-web-app.js"&gt;&lt;/script&gt;</code>, '
                     'и появляется глобальный объект <code>window.Telegram.WebApp</code>:</p>\n'
                     '<table>\n'
                     '<tr><th>Метод / свойство</th><th>Назначение</th></tr>\n'
                     '<tr><td><code>WebApp.ready()</code></td><td>Сообщает Telegram, что страница '
                     'готова — закрывается splash screen</td></tr>\n'
                     '<tr><td><code>WebApp.expand()</code></td><td>Разворачивает страницу на '
                     'полную высоту</td></tr>\n'
                     '<tr><td><code>WebApp.close()</code></td><td>Закрывает Mini App</td></tr>\n'
                     '<tr><td><code>WebApp.MainButton</code></td><td>Большая нижняя кнопка — '
                     '<code>setText()</code>, <code>show()</code>, '
                     '<code>onClick()</code></td></tr>\n'
                     '<tr><td><code>WebApp.BackButton</code></td><td>Кнопка «назад» вверху '
                     'слева</td></tr>\n'
                     '<tr><td><code>WebApp.themeParams</code> / '
                     '<code>colorScheme</code></td><td>Цвета для адаптации под тему Telegram '
                     '(dark/light)</td></tr>\n'
                     '<tr><td><code>WebApp.initData</code> / '
                     '<code>initDataUnsafe</code></td><td>Подписанные данные о пользователе — '
                     'разберём в следующем уроке</td></tr>\n'
                     '<tr><td><code>WebApp.sendData(data)</code></td><td>Отправляет данные боту '
                     'как <code>web_app_data</code> и закрывает страницу</td></tr>\n'
                     '<tr><td><code>WebApp.HapticFeedback</code></td><td>Лёгкая вибрация на '
                     'устройстве</td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Почему в названии initDataUnsafe есть слово "Unsafe"</h3>\n'
                     '<p>Это название дано намеренно — <code>initDataUnsafe</code> уже распарсен в '
                     'JS-объект, но ещё <strong>не проверен</strong>. Любой пользователь может '
                     'изменить этот объект в консоли браузера. Если ваш backend доверяет ему и, '
                     'например, возвращает запись из базы данных по <code>user.id</code> — кто '
                     'угодно может выдать себя за любого пользователя. Проверка подписи (hash) '
                     'исходной строки <code>initData</code> — тема следующего урока '
                     'полностью.</p>\n'
                     '\n'
                     '<h3>Архитектура: что где живёт</h3>\n'
                     '<p>Для Mini App нужны как минимум две части: статическая страница, '
                     'обслуживаемая по HTTPS (Telegram принимает только '
                     '<code>https://</code>-адреса, <code>http://</code> или '
                     '<code>localhost</code> не работают — для теста нужен туннель вроде ngrok), и '
                     'код бота на стороне aiogram, регистрирующий кнопку и обрабатывающий '
                     'вернувшиеся данные. Оба могут быть как на одном сервере, так и на разных — '
                     'важно только HTTPS.</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart TB\n'
                     '  A["Пользователь: нажимает кнопку \'Каталог\'"] --> B["Telegram: открывает '
                     'страницу в WebView"]\n'
                     '  B --> C["Страница JS: WebApp.ready() + WebApp.expand()"]\n'
                     '  C --> D["Пользователь: выбирает товар"]\n'
                     '  D --> E["Страница JS: WebApp.sendData(JSON)"]\n'
                     '  E --> F["Telegram: закрывает страницу"]\n'
                     '  F --> G["Бот: message-обновление, content_type=web_app_data"]\n'
                     '  G --> H["Обработчик aiogram: читает message.web_app_data.data"]\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает: после вызова <code>sendData</code> Telegram '
                     'автоматически закрывает страницу и отправляет боту данные обычным сообщением '
                     '— отдельный webhook или API-вызов не нужен.</p>\n'
                     '\n'
                     '<h3>Общение через fetch — путь, отличный от sendData</h3>\n'
                     '<p><code>sendData</code> работает только один раз, перед закрытием страницы. '
                     'Если страница должна оставаться открытой и постоянно обмениваться данными с '
                     'backend (например, загружать каталог, отслеживать статус заказа), '
                     'используется обычный <code>fetch()</code>-запрос к вашему собственному '
                     'backend API — в этом случае для определения пользователя '
                     '<code>initData</code> нужно передавать в заголовке запроса и проверять на '
                     'backend (тема следующего урока).</p>',
  'code_content': 'from aiogram import Router, F\n'
                  'from aiogram.filters import Command\n'
                  'from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, '
                  'WebAppInfo\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  'MINI_APP_URL = "https://mysite.example.com/catalog"  # HTTPS shart\n'
                  '\n'
                  '\n'
                  'def catalog_keyboard() -> ReplyKeyboardMarkup:\n'
                  '    return ReplyKeyboardMarkup(\n'
                  '        keyboard=[[KeyboardButton(text="Katalogni ochish", '
                  'web_app=WebAppInfo(url=MINI_APP_URL))]],\n'
                  '        resize_keyboard=True,\n'
                  '    )\n'
                  '\n'
                  '\n'
                  '@router.message(Command("shop"))\n'
                  'async def cmd_shop(message: Message):\n'
                  '    await message.answer(\n'
                  '        "Katalogni ko\'rish uchun quyidagi tugmani bosing:",\n'
                  '        reply_markup=catalog_keyboard(),\n'
                  '    )\n'
                  '\n'
                  '\n'
                  '@router.message(F.web_app_data)\n'
                  'async def handle_web_app_data(message: Message, db_session):\n'
                  '    import json\n'
                  '\n'
                  '    raw = message.web_app_data.data\n'
                  '    try:\n'
                  '        payload = json.loads(raw)\n'
                  '    except json.JSONDecodeError:\n'
                  '        await message.answer("Noto\'g\'ri ma\'lumot formati.")\n'
                  '        return\n'
                  '\n'
                  '    product_id = payload.get("product_id")\n'
                  '    quantity = payload.get("quantity", 1)\n'
                  '    await message.answer(\n'
                  '        f"Buyurtma qabul qilindi: mahsulot #{product_id}, {quantity} dona."\n'
                  '    )\n'
                  "    # bu yerda haqiqiy buyurtma yozuvini DB'ga saqlash kerak bo'ladi\n"
                  '\n'
                  '\n'
                  '# index.html / app.js (Mini App sahifasi) — to\'liq versiyasi "sample" '
                  "bo'limida.\n"
                  "# Sahifa tomonidagi asosiy chaqiruv shunday ko'rinadi:\n"
                  '#\n'
                  '#     Telegram.WebApp.sendData(JSON.stringify({"product_id": 42, "quantity": '
                  '2}));\n'
                  '#\n'
                  '# sendData chaqirilgach, Telegram sahifani avtomatik yopadi va\n'
                  '# yuqoridagi handle_web_app_data handleri ishga tushadi.',
  'code_content_ru': 'from aiogram import Router, F\n'
                     'from aiogram.filters import Command\n'
                     'from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, '
                     'WebAppInfo\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     'MINI_APP_URL = "https://mysite.example.com/catalog"  # обязательно HTTPS\n'
                     '\n'
                     '\n'
                     'def catalog_keyboard() -> ReplyKeyboardMarkup:\n'
                     '    return ReplyKeyboardMarkup(\n'
                     '        keyboard=[[KeyboardButton(text="Открыть каталог", '
                     'web_app=WebAppInfo(url=MINI_APP_URL))]],\n'
                     '        resize_keyboard=True,\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '@router.message(Command("shop"))\n'
                     'async def cmd_shop(message: Message):\n'
                     '    await message.answer(\n'
                     '        "Нажмите кнопку ниже, чтобы открыть каталог:",\n'
                     '        reply_markup=catalog_keyboard(),\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '@router.message(F.web_app_data)\n'
                     'async def handle_web_app_data(message: Message, db_session):\n'
                     '    import json\n'
                     '\n'
                     '    raw = message.web_app_data.data\n'
                     '    try:\n'
                     '        payload = json.loads(raw)\n'
                     '    except json.JSONDecodeError:\n'
                     '        await message.answer("Неверный формат данных.")\n'
                     '        return\n'
                     '\n'
                     '    product_id = payload.get("product_id")\n'
                     '    quantity = payload.get("quantity", 1)\n'
                     '    await message.answer(\n'
                     '        f"Заказ принят: товар #{product_id}, {quantity} шт."\n'
                     '    )\n'
                     '    # здесь нужно сохранить реальную запись заказа в БД\n'
                     '\n'
                     '\n'
                     '# index.html / app.js (страница Mini App) — полная версия в разделе '
                     '"sample".\n'
                     '# Основной вызов на стороне страницы выглядит так:\n'
                     '#\n'
                     '#     Telegram.WebApp.sendData(JSON.stringify({"product_id": 42, "quantity": '
                     '2}));\n'
                     '#\n'
                     '# После вызова sendData Telegram автоматически закрывает страницу,\n'
                     '# и запускается обработчик handle_web_app_data выше.',
  'task': {'task_title': 'Amaliy: mini Mini App katalogini ishga tushiring',
           'task_title_ru': 'Практика: запустите мини-каталог Mini App',
           'task_description': 'web_app tugmasi orqali ochiladigan oddiy Mini App sahifasi yasang: '
                               "kamida 3 ta mahsulot ko'rsating, MainButton orqali tanlovni "
                               'tasdiqlang va sendData orqali botga yuboring. Bot tomonida '
                               "web_app_data'ni qabul qilib, foydalanuvchiga tasdiqlovchi xabar "
                               'yuboring.',
           'task_description_ru': 'Создайте простую страницу Mini App, открываемую через кнопку '
                                  'web_app: покажите минимум 3 товара, подтвердите выбор через '
                                  'MainButton и отправьте его боту через sendData. На стороне бота '
                                  'примите web_app_data и отправьте пользователю подтверждающее '
                                  'сообщение.',
           'task_requirements': "HTTPS orqali xizmat qiluvchi sahifa (ngrok yoki shunga o'xshash "
                                "tunnel ruxsat etiladi); ready()/expand() chaqirilgan bo'lishi; "
                                "MainButton ishlatilgan bo'lishi; bot tomonida web_app_data "
                                "handler mavjud bo'lishi.",
           'task_requirements_ru': 'Страница, обслуживаемая по HTTPS (допустим туннель вроде '
                                   'ngrok); вызваны ready()/expand(); использован MainButton; на '
                                   'стороне бота реализован обработчик web_app_data.',
           'task_technologies': 'aiogram 3.x, Telegram.WebApp JS API, HTML/JS',
           'task_deadline_days': 3},
  'sample': {'title': 'Namuna: Mini App katalog sahifasi + aiogram handler',
             'description': 'Telegram.WebApp JS API ishlatilgan minimal Mini App sahifasi va uni '
                            "ro'yxatga oluvchi aiogram kodi",
             'sample_type': 'code',
             'code_files': [{'filename': 'index.html',
                             'language': 'html',
                             'code': '<!doctype html>\n'
                                     '<html lang="uz">\n'
                                     '<head>\n'
                                     '  <meta charset="utf-8" />\n'
                                     '  <title>Katalog</title>\n'
                                     '  <script '
                                     'src="https://telegram.org/js/telegram-web-app.js"></script>\n'
                                     '</head>\n'
                                     '<body>\n'
                                     '  <h2>Mahsulotlar</h2>\n'
                                     '  <ul id="products"></ul>\n'
                                     '  <script src="app.js"></script>\n'
                                     '</body>\n'
                                     '</html>'},
                            {'filename': 'app.js',
                             'language': 'javascript',
                             'code': 'const tg = window.Telegram.WebApp;\n'
                                     'tg.ready();\n'
                                     'tg.expand();\n'
                                     '\n'
                                     'const products = [\n'
                                     '  { id: 1, name: "Kitob", price: 45000 },\n'
                                     '  { id: 2, name: "Ruchka", price: 8000 },\n'
                                     '  { id: 3, name: "Daftar", price: 12000 },\n'
                                     '];\n'
                                     '\n'
                                     'const list = document.getElementById("products");\n'
                                     'products.forEach((p) => {\n'
                                     '  const li = document.createElement("li");\n'
                                     '  li.textContent = p.name + " — " + p.price + " so\'m";\n'
                                     '  li.onclick = () => selectProduct(p);\n'
                                     '  list.appendChild(li);\n'
                                     '});\n'
                                     '\n'
                                     'function selectProduct(product) {\n'
                                     '  tg.MainButton.setText("Xarid: " + product.name);\n'
                                     '  tg.MainButton.show();\n'
                                     '  tg.MainButton.onClick(() => {\n'
                                     '    tg.sendData(JSON.stringify({ product_id: product.id, '
                                     'quantity: 1 }));\n'
                                     '  });\n'
                                     '}\n'
                                     '\n'
                                     'tg.setHeaderColor(tg.themeParams.bg_color || "#ffffff");'},
                            {'filename': 'register_handlers.py',
                             'language': 'python',
                             'code': 'from aiogram import Dispatcher\n'
                                     'from mini_app_handlers import router as mini_app_router\n'
                                     '\n'
                                     '\n'
                                     'def setup_routers(dp: Dispatcher) -> None:\n'
                                     '    dp.include_router(mini_app_router)'}]},
  'exercises': [{'title': 'web_app tugmasi va chat turi',
                 'title_ru': 'Кнопка web_app и тип чата',
                 'description': 'Reply klaviaturadagi KeyboardButton(web_app=...) tugmasi qaysi '
                                'turdagi chatda ishlaydi?',
                 'description_ru': 'В каком типе чата работает кнопка KeyboardButton(web_app=...) '
                                   'в reply-клавиатуре?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Faqat shaxsiy chat',
                             'Faqat guruh',
                             'Guruh va kanal',
                             'Har qanday chat turi'],
                 'options_ru': ['Только личный чат',
                                'Только группа',
                                'Группа и канал',
                                'Любой тип чата'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "KeyboardButton bilan InlineKeyboardButton'dagi web_app farqini eslang.",
                 'hint_ru': 'Вспомните разницу между web_app в KeyboardButton и в '
                            'InlineKeyboardButton.',
                 'explanation': "KeyboardButton'dagi web_app faqat shaxsiy chatlarda ko'rinadi va "
                                'ishlaydi; guruh/kanal uchun bu ishlamaydi.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Splash screenni yopish metodi',
                 'title_ru': 'Метод закрытия splash screen',
                 'description': "Mini App sahifasi tayyor ekanini Telegram'ga bildirish uchun "
                                'chaqiriladigan metod: WebApp.___()',
                 'description_ru': 'Метод, который вызывают, чтобы сообщить Telegram о готовности '
                                   'страницы Mini App: WebApp.___()',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'ready',
                 'hint': 'Bu splash screen yopilishi uchun chaqiriladigan birinchi metod.',
                 'hint_ru': 'Это первый метод, который вызывают, чтобы закрылся splash screen.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Mini App lifecycle tartibi',
                 'title_ru': 'Порядок жизненного цикла Mini App',
                 'description': "Mini App hayotiy siklining qadamlarini to'g'ri tartibga "
                                'joylashtiring',
                 'description_ru': 'Расположите шаги жизненного цикла Mini App в правильном '
                                   'порядке',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Foydalanuvchi tugmani bosadi',
                                "Telegram sahifani WebView'da ochadi",
                                'Sahifa ready() va expand() chaqiradi',
                                'Foydalanuvchi tanlov qiladi',
                                'Sahifa sendData() chaqiradi',
                                "Bot web_app_data'ni oladi"],
                 'drag_items_ru': ['Пользователь нажимает кнопку',
                                   'Telegram открывает страницу в WebView',
                                   'Страница вызывает ready() и expand()',
                                   'Пользователь делает выбор',
                                   'Страница вызывает sendData()',
                                   'Бот получает web_app_data'],
                 'correct_order': ['Foydalanuvchi tugmani bosadi',
                                   "Telegram sahifani WebView'da ochadi",
                                   'Sahifa ready() va expand() chaqiradi',
                                   'Foydalanuvchi tanlov qiladi',
                                   'Sahifa sendData() chaqiradi',
                                   "Bot web_app_data'ni oladi"],
                 'hint': 'Voqealar ketma-ketligini sahifa ochilishidan boshlab kuzating.',
                 'hint_ru': 'Проследите последовательность событий начиная с открытия страницы.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': "sendData()ning yon ta'siri",
                 'title_ru': 'Побочный эффект sendData()',
                 'description': 'Mini App sahifasida WebApp.sendData() chaqirilgach nima sodir '
                                "bo'ladi?",
                 'description_ru': 'Что происходит после вызова WebApp.sendData() на странице Mini '
                                   'App?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Sahifa avtomatik yopiladi va bot xabar oladi',
                             'Hech narsa, sahifa ochiq qoladi',
                             'Bot darhol javob yozadi',
                             'Xatolik chiqadi'],
                 'options_ru': ['Страница автоматически закрывается, и бот получает сообщение',
                                'Ничего, страница остаётся открытой',
                                'Бот сразу отвечает',
                                'Возникает ошибка'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Bu — sendData'ning eng muhim yon ta'siri.",
                 'hint_ru': 'Это самый важный побочный эффект sendData.',
                 'explanation': 'sendData chaqirilgach Telegram sahifani avtomatik yopadi va botga '
                                'web_app_data sifatida xabar yuboradi.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 1,
  'title': "2-Mini App xavfsizligi: initData'ni HMAC-SHA256 bilan tekshirish",
  'title_ru': '2-Безопасность Mini App: проверка initData через HMAC-SHA256',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': '<h3>initData nima va nega uni "ishonch bilan" o\'qib bo\'lmaydi</h3>\n'
                  "<p><code>initData</code> &mdash; Telegram Mini App ochilganda WebView'ga "
                  "beriladigan, so'rov satri (query string) formatidagi ma'lumot: "
                  '<code>user</code> (JSON, foydalanuvchi id/ism/username), <code>auth_date</code> '
                  '(unix vaqt), <code>query_id</code>, va eng muhimi &mdash; <code>hash</code>. '
                  '<code>window.Telegram.WebApp.initDataUnsafe</code> shu qatorni sizga tayyor JS '
                  "obyekti sifatida beradi, lekin nomidan ko'rinib turganidek, u hali "
                  '<strong>tasdiqlanmagan</strong>: sahifa kodi mijoz brauzerida ishlaydi, demak '
                  "har qanday foydalanuvchi konsolda uni o'zgartirib, o'zini boshqa "
                  "<code>user.id</code> qilib ko'rsatishi mumkin. Agar backend'ingiz shunchaki "
                  "<code>initDataUnsafe.user.id</code>ga ishonib ma'lumotlar bazasidan yozuv "
                  "qaytarsa &mdash; bu to'g'ridan-to'g'ri autentifikatsiya aylanib o'tish (auth "
                  'bypass) zaifligi.</p>\n'
                  '\n'
                  '<h3>Tekshirish algoritmi &mdash; qadam-baqadam</h3>\n'
                  '<p>Telegram <code>hash</code>ni bot tokeningiz asosida hisoblaydi, shuning '
                  'uchun uni faqat siz qayta hisoblab, taqqoslay olasiz:</p>\n'
                  '<ol>\n'
                  "<li><code>initData</code> qatorini so'rov parametrlari sifatida parslang "
                  '(<code>urllib.parse.parse_qsl</code>).</li>\n'
                  "<li><code>hash</code> parametrini ro'yxatdan chiqarib oling &mdash; u "
                  'tekshiruvga kirmaydi.</li>\n'
                  "<li>Qolgan barcha <code>key=value</code> juftlarini <strong>kalit bo'yicha "
                  'alifbo tartibida</strong> saralang.</li>\n'
                  '<li>Ularni yangi qator (newline, <code>\\n</code>) belgisi bilan birlashtirib, '
                  '<code>data_check_string</code> hosil qiling.</li>\n'
                  '<li><code>secret_key = HMAC_SHA256(key=b"WebAppData", '
                  'msg=bot_token).digest()</code> &mdash; bu doimiy, <code>bot_token</code>ning '
                  "o'zi emas, undan hosil qilingan oraliq kalit.</li>\n"
                  '<li><code>computed_hash = HMAC_SHA256(key=secret_key, '
                  'msg=data_check_string).hexdigest()</code>.</li>\n'
                  '<li><code>computed_hash</code>ni <code>initData</code>dagi <code>hash</code> '
                  'bilan <code>hmac.compare_digest()</code> orqali solishtiring.</li>\n'
                  '</ol>\n'
                  '\n'
                  '<h3>Nega hmac.compare_digest(), oddiy == emas</h3>\n'
                  "<p>Oddiy Python <code>==</code> qatorlarni chapdan o'ngga solishtiradi va "
                  "<strong>birinchi mos kelmagan belgida darhol to'xtaydi</strong> &mdash; demak "
                  "solishtirish vaqti mos kelgan belgilar soniga bog'liq bo'ladi. Bu "
                  "millisekundlik farqni o'lchab, hash'ni belgi-baqadam topib olish mumkin bo'lgan "
                  '<em>timing attack</em> uchun eshik ochadi. <code>hmac.compare_digest()</code> '
                  "esa doimiy vaqtda ishlaydi &mdash; ikkala qatorning uzunligidan qat'iy nazar "
                  'bir xil vaqt sarflaydi, shuning uchun tashqi kuzatuvchi vaqt farqidan hech '
                  'narsa bilib ololmaydi. Har qanday maxfiy hash/tokenni solishtirishda shu '
                  'qoidaga rioya qiling.</p>\n'
                  '\n'
                  "<h3>auth_date &mdash; eskirgan initData'dan himoya</h3>\n"
                  "<p>Hash to'g'ri bo'lsa ham, <code>initData</code> vaqt o'tishi bilan "
                  '&ldquo;eskirmaydi&rdquo; &mdash; imzo abadiy amal qiladi. Agar kimdir eski, '
                  "allaqachon oshkor bo'lgan <code>initData</code> qatorini qayta ishlatsa "
                  "(replay), hash tekshiruvidan muvaffaqiyatli o'tadi. Shu sababli "
                  '<code>auth_date</code>ni joriy vaqt bilan solishtirib, masalan 24 soatdan '
                  "eskirgan bo'lsa rad etish shart &mdash; bu hash tekshiruvini "
                  "<strong>to'ldiradi</strong>, uni almashtirmaydi.</p>\n"
                  '\n'
                  '<h3>Amaliyotda: FastAPI dependency</h3>\n'
                  "<p>Mini App sahifasi har bir backend so'roviga <code>initData</code>ni "
                  '(masalan, <code>Authorization: tma &lt;initData&gt;</code> sarlavhasida) '
                  "qo'shib yuborishi, backend esa har bir so'rovda uni qayta tekshirishi kerak "
                  '&mdash; bir marta tekshirib, natijani "abadiy" ishonchli deb hisoblash '
                  "yaramaydi, chunki har xil so'rov turli foydalanuvchidan kelishi mumkin.</p>\n"
                  '<pre class="mermaid">\n'
                  'sequenceDiagram\n'
                  '  participant M as Mini App (JS)\n'
                  '  participant B as Backend (FastAPI)\n'
                  "  M->>B: so'rov + initData (Authorization sarlavhasida)\n"
                  "  B->>B: parse_qsl(initData), hash'ni ajratib olish\n"
                  "  B->>B: data_check_string yig'ish (saralangan key=value)\n"
                  '  B->>B: secret_key = HMAC_SHA256(b"WebAppData", bot_token)\n'
                  '  B->>B: computed_hash = HMAC_SHA256(secret_key, data_check_string)\n'
                  '  B->>B: compare_digest(computed_hash, hash) va auth_date tekshiruvi\n'
                  '  B-->>M: 200 OK (ishonchli user) yoki 401 Unauthorized\n'
                  '</pre>\n'
                  "<p>Diagramma shuni ta'kidlaydi: <code>hash</code> va <code>auth_date</code> "
                  "tekshiruvi &mdash; ikkalasi ham backend tomonda, HAR BIR so'rovda, mijozga "
                  'ishonmasdan bajariladi.</p>\n'
                  '\n'
                  "<h3>Umumiy xato: initData'ni faqat bir marta, kirishda tekshirish</h3>\n"
                  "<p>Ba'zi loyihalar <code>initData</code>ni faqat Mini App ochilganda bir marta "
                  "tekshirib, keyin session/cookie yaratadi va qolgan so'rovlarni shunga ishonadi "
                  "&mdash; bu ham to'g'ri yondashuv, lekin session yaratish logikasi ham xuddi shu "
                  "HMAC tekshiruvidan o'tishi shart. Xato &mdash; tekshiruvni umuman o'tkazib "
                  "yuborib, faqat <code>initDataUnsafe.user.id</code>ni frontend'dan qabul qilish, "
                  "go'yo u ishonchli manba ekan.</p>",
  'text_content_ru': '<h3>Что такое initData и почему ему нельзя "просто доверять"</h3>\n'
                     '<p><code>initData</code> — данные в формате query-строки, которые Telegram '
                     'передаёт в WebView при открытии Mini App: <code>user</code> (JSON с '
                     'id/именем/username пользователя), <code>auth_date</code> (unix-время), '
                     '<code>query_id</code> и, самое главное, — <code>hash</code>. '
                     '<code>window.Telegram.WebApp.initDataUnsafe</code> отдаёт эту строку уже '
                     'готовым JS-объектом, но, как следует из названия, она ещё <strong>не '
                     'проверена</strong>: код страницы выполняется в браузере клиента, а значит '
                     'любой пользователь может изменить его в консоли и выдать себя за другой '
                     '<code>user.id</code>. Если ваш backend просто доверяет '
                     '<code>initDataUnsafe.user.id</code> и возвращает данные из БД — это прямая '
                     'уязвимость обхода аутентификации.</p>\n'
                     '\n'
                     '<h3>Алгоритм проверки — шаг за шагом</h3>\n'
                     '<p>Telegram вычисляет <code>hash</code> на основе токена вашего бота, '
                     'поэтому только вы можете пересчитать и сравнить его:</p>\n'
                     '<ol>\n'
                     '<li>Распарсить строку <code>initData</code> как параметры запроса '
                     '(<code>urllib.parse.parse_qsl</code>).</li>\n'
                     '<li>Извлечь параметр <code>hash</code> — он не участвует в проверке.</li>\n'
                     '<li>Отсортировать оставшиеся пары <code>key=value</code> <strong>по ключу в '
                     'алфавитном порядке</strong>.</li>\n'
                     '<li>Объединить их через символ новой строки (<code>\\n</code>), получив '
                     '<code>data_check_string</code>.</li>\n'
                     '<li><code>secret_key = HMAC_SHA256(key=b"WebAppData", '
                     'msg=bot_token).digest()</code> — это промежуточный ключ, производный от '
                     'токена, а не сам токен.</li>\n'
                     '<li><code>computed_hash = HMAC_SHA256(key=secret_key, '
                     'msg=data_check_string).hexdigest()</code>.</li>\n'
                     '<li>Сравнить <code>computed_hash</code> с полем <code>hash</code> из '
                     '<code>initData</code> через <code>hmac.compare_digest()</code>.</li>\n'
                     '</ol>\n'
                     '\n'
                     '<h3>Почему hmac.compare_digest(), а не обычное ==</h3>\n'
                     '<p>Обычное сравнение строк <code>==</code> в Python идёт слева направо и '
                     '<strong>останавливается на первом несовпадении</strong> — значит время '
                     'сравнения зависит от числа совпавших символов. Это открывает возможность '
                     '<em>timing attack</em>: измеряя миллисекундные различия, можно подобрать '
                     'hash посимвольно. <code>hmac.compare_digest()</code> работает за постоянное '
                     'время — независимо от длины строк тратит одинаковое время, поэтому внешний '
                     'наблюдатель не может ничего узнать по разнице во времени. Придерживайтесь '
                     'этого правила при сравнении любых секретных hash/токенов.</p>\n'
                     '\n'
                     '<h3>auth_date — защита от устаревшего initData</h3>\n'
                     '<p>Даже если hash верен, <code>initData</code> со временем не "истекает" сам '
                     'по себе — подпись действительна вечно. Если кто-то повторно использует '
                     'старую, уже где-то раскрытую строку <code>initData</code> (replay-атака), '
                     'проверка hash пройдёт успешно. Поэтому нужно сравнивать '
                     '<code>auth_date</code> с текущим временем и отклонять данные старше, '
                     'например, 24 часов — это <strong>дополняет</strong> проверку hash, а не '
                     'заменяет её.</p>\n'
                     '\n'
                     '<h3>На практике: зависимость FastAPI</h3>\n'
                     '<p>Страница Mini App должна добавлять <code>initData</code> к каждому '
                     'запросу к backend (например, в заголовке <code>Authorization: tma '
                     '&lt;initData&gt;</code>), а backend обязан проверять его при каждом запросе '
                     '— проверить один раз и считать результат "вечно" доверенным нельзя, потому '
                     'что разные запросы могут приходить от разных пользователей.</p>\n'
                     '<pre class="mermaid">\n'
                     'sequenceDiagram\n'
                     '  participant M as Mini App (JS)\n'
                     '  participant B as Backend (FastAPI)\n'
                     '  M->>B: запрос + initData (в заголовке Authorization)\n'
                     '  B->>B: parse_qsl(initData), извлечение hash\n'
                     '  B->>B: сборка data_check_string (отсортированные key=value)\n'
                     '  B->>B: secret_key = HMAC_SHA256(b"WebAppData", bot_token)\n'
                     '  B->>B: computed_hash = HMAC_SHA256(secret_key, data_check_string)\n'
                     '  B->>B: compare_digest(computed_hash, hash) и проверка auth_date\n'
                     '  B-->>M: 200 OK (доверенный user) или 401 Unauthorized\n'
                     '</pre>\n'
                     '<p>Диаграмма подчёркивает: проверка <code>hash</code> и '
                     '<code>auth_date</code> — обе на стороне backend, при КАЖДОМ запросе, без '
                     'доверия клиенту.</p>\n'
                     '\n'
                     '<h3>Частая ошибка: проверять initData только один раз, при входе</h3>\n'
                     '<p>В некоторых проектах <code>initData</code> проверяют только один раз при '
                     'открытии Mini App, затем создают сессию/cookie и доверяют ей для остальных '
                     'запросов — это тоже допустимый подход, но логика создания сессии должна '
                     'проходить через ту же самую HMAC-проверку. Ошибка — вообще пропустить '
                     'проверку и просто принимать <code>initDataUnsafe.user.id</code> от frontend, '
                     'будто это надёжный источник.</p>',
  'code_content': 'import hashlib\n'
                  'import hmac\n'
                  'import time\n'
                  'from urllib.parse import parse_qsl\n'
                  '\n'
                  '\n'
                  'class InitDataError(Exception):\n'
                  '    """initData tekshiruvidan o\'tmadi."""\n'
                  '\n'
                  '\n'
                  'def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int = '
                  '86400) -> dict:\n'
                  '    """Telegram Mini App initData\'sini HMAC-SHA256 orqali tekshiradi.\n'
                  '\n'
                  "    Muvaffaqiyatli bo'lsa parslangan maydonlar lug'atini qaytaradi\n"
                  "    (shu jumladan 'user' -> dict). Muvaffaqiyatsiz bo'lsa InitDataError.\n"
                  '    """\n'
                  '    pairs = dict(parse_qsl(init_data, strict_parsing=True))\n'
                  '    received_hash = pairs.pop("hash", None)\n'
                  '    if not received_hash:\n'
                  '        raise InitDataError("initData ichida \'hash\' maydoni yo\'q")\n'
                  '\n'
                  '    data_check_string = "\\n".join(\n'
                  '        f"{key}={value}" for key, value in sorted(pairs.items())\n'
                  '    )\n'
                  '\n'
                  '    secret_key = hmac.new(\n'
                  '        key=b"WebAppData", msg=bot_token.encode(), digestmod=hashlib.sha256\n'
                  '    ).digest()\n'
                  '    computed_hash = hmac.new(\n'
                  '        key=secret_key, msg=data_check_string.encode(), '
                  'digestmod=hashlib.sha256\n'
                  '    ).hexdigest()\n'
                  '\n'
                  '    if not hmac.compare_digest(computed_hash, received_hash):\n'
                  '        raise InitDataError("hash mos kelmadi — initData soxta yoki buzilgan")\n'
                  '\n'
                  '    auth_date = int(pairs.get("auth_date", 0))\n'
                  '    if time.time() - auth_date > max_age_seconds:\n'
                  '        raise InitDataError(f"initData eskirgan (auth_date {max_age_seconds}s '
                  'dan katta)")\n'
                  '\n'
                  '    import json\n'
                  '    if "user" in pairs:\n'
                  '        pairs["user"] = json.loads(pairs["user"])\n'
                  '    return pairs\n'
                  '\n'
                  '\n'
                  "# --- FastAPI'da ishlatish ---\n"
                  'from fastapi import FastAPI, Header, HTTPException\n'
                  '\n'
                  'app = FastAPI()\n'
                  'BOT_TOKEN = "123456:ABC-DEF..."  # .env\'dan olinadi, hech qachon kodga '
                  'yozilmaydi\n'
                  '\n'
                  '\n'
                  '@app.get("/api/profile")\n'
                  'async def profile(authorization: str = Header(...)):\n'
                  '    if not authorization.startswith("tma "):\n'
                  '        raise HTTPException(401, "Noto\'g\'ri Authorization format")\n'
                  '    init_data = authorization.removeprefix("tma ")\n'
                  '    try:\n'
                  '        data = validate_init_data(init_data, BOT_TOKEN)\n'
                  '    except InitDataError as e:\n'
                  '        raise HTTPException(401, str(e))\n'
                  '    user = data["user"]\n'
                  '    return {"telegram_id": user["id"], "first_name": user.get("first_name")}\n'
                  '\n'
                  '\n'
                  'def _build_test_init_data(bot_token: str, user: dict, auth_date: int) -> str:\n'
                  '    """Faqat testlar uchun: haqiqiy initData\'ga o\'xshash, to\'g\'ri '
                  'imzolangan\n'
                  "    qatorni qo'lda yasab beradi — validate_init_data'ni Telegram'siz sinash "
                  'uchun."""\n'
                  '    import json\n'
                  '    from urllib.parse import urlencode\n'
                  '\n'
                  '    fields = {"auth_date": str(auth_date), "query_id": "AAH1234", "user": '
                  'json.dumps(user)}\n'
                  '    data_check_string = "\\n".join(f"{k}={v}" for k, v in '
                  'sorted(fields.items()))\n'
                  '    secret_key = hmac.new(b"WebAppData", bot_token.encode(), '
                  'hashlib.sha256).digest()\n'
                  '    fields["hash"] = hmac.new(secret_key, data_check_string.encode(), '
                  'hashlib.sha256).hexdigest()\n'
                  '    return urlencode(fields)\n'
                  '\n'
                  '\n'
                  'def test_validate_init_data_ok():\n'
                  '    token = "TEST:TOKEN"\n'
                  '    raw = _build_test_init_data(token, {"id": 1, "first_name": "Aziz"}, '
                  'int(time.time()))\n'
                  '    result = validate_init_data(raw, token)\n'
                  '    assert result["user"]["first_name"] == "Aziz"\n'
                  '\n'
                  '\n'
                  'def test_validate_init_data_tampered():\n'
                  '    token = "TEST:TOKEN"\n'
                  '    raw = _build_test_init_data(token, {"id": 1, "first_name": "Aziz"}, '
                  'int(time.time()))\n'
                  '    tampered = raw.replace("Aziz", "Hacker")\n'
                  '    try:\n'
                  '        validate_init_data(tampered, token)\n'
                  '        assert False, "bu yerga yetib kelmasligi kerak"\n'
                  '    except InitDataError:\n'
                  '        pass',
  'code_content_ru': 'import hashlib\n'
                     'import hmac\n'
                     'import time\n'
                     'from urllib.parse import parse_qsl\n'
                     '\n'
                     '\n'
                     'class InitDataError(Exception):\n'
                     '    """Проверка initData не пройдена."""\n'
                     '\n'
                     '\n'
                     'def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int '
                     '= 86400) -> dict:\n'
                     '    """Проверяет initData Telegram Mini App через HMAC-SHA256.\n'
                     '\n'
                     '    При успехе возвращает словарь распарсенных полей\n'
                     "    (включая 'user' -> dict). При неудаче выбрасывает InitDataError.\n"
                     '    """\n'
                     '    pairs = dict(parse_qsl(init_data, strict_parsing=True))\n'
                     '    received_hash = pairs.pop("hash", None)\n'
                     '    if not received_hash:\n'
                     '        raise InitDataError("В initData отсутствует поле \'hash\'")\n'
                     '\n'
                     '    data_check_string = "\\n".join(\n'
                     '        f"{key}={value}" for key, value in sorted(pairs.items())\n'
                     '    )\n'
                     '\n'
                     '    secret_key = hmac.new(\n'
                     '        key=b"WebAppData", msg=bot_token.encode(), digestmod=hashlib.sha256\n'
                     '    ).digest()\n'
                     '    computed_hash = hmac.new(\n'
                     '        key=secret_key, msg=data_check_string.encode(), '
                     'digestmod=hashlib.sha256\n'
                     '    ).hexdigest()\n'
                     '\n'
                     '    if not hmac.compare_digest(computed_hash, received_hash):\n'
                     '        raise InitDataError("hash не совпал — initData поддельный или '
                     'повреждён")\n'
                     '\n'
                     '    auth_date = int(pairs.get("auth_date", 0))\n'
                     '    if time.time() - auth_date > max_age_seconds:\n'
                     '        raise InitDataError(f"initData устарел (auth_date старше '
                     '{max_age_seconds}s)")\n'
                     '\n'
                     '    import json\n'
                     '    if "user" in pairs:\n'
                     '        pairs["user"] = json.loads(pairs["user"])\n'
                     '    return pairs\n'
                     '\n'
                     '\n'
                     '# --- Использование в FastAPI ---\n'
                     'from fastapi import FastAPI, Header, HTTPException\n'
                     '\n'
                     'app = FastAPI()\n'
                     'BOT_TOKEN = "123456:ABC-DEF..."  # берётся из .env, никогда не пишется в '
                     'код\n'
                     '\n'
                     '\n'
                     '@app.get("/api/profile")\n'
                     'async def profile(authorization: str = Header(...)):\n'
                     '    if not authorization.startswith("tma "):\n'
                     '        raise HTTPException(401, "Неверный формат Authorization")\n'
                     '    init_data = authorization.removeprefix("tma ")\n'
                     '    try:\n'
                     '        data = validate_init_data(init_data, BOT_TOKEN)\n'
                     '    except InitDataError as e:\n'
                     '        raise HTTPException(401, str(e))\n'
                     '    user = data["user"]\n'
                     '    return {"telegram_id": user["id"], "first_name": '
                     'user.get("first_name")}\n'
                     '\n'
                     '\n'
                     'def _build_test_init_data(bot_token: str, user: dict, auth_date: int) -> '
                     'str:\n'
                     '    """Только для тестов: вручную собирает корректно подписанную строку,\n'
                     '    похожую на настоящий initData — чтобы тестировать validate_init_data без '
                     'Telegram."""\n'
                     '    import json\n'
                     '    from urllib.parse import urlencode\n'
                     '\n'
                     '    fields = {"auth_date": str(auth_date), "query_id": "AAH1234", "user": '
                     'json.dumps(user)}\n'
                     '    data_check_string = "\\n".join(f"{k}={v}" for k, v in '
                     'sorted(fields.items()))\n'
                     '    secret_key = hmac.new(b"WebAppData", bot_token.encode(), '
                     'hashlib.sha256).digest()\n'
                     '    fields["hash"] = hmac.new(secret_key, data_check_string.encode(), '
                     'hashlib.sha256).hexdigest()\n'
                     '    return urlencode(fields)\n'
                     '\n'
                     '\n'
                     'def test_validate_init_data_ok():\n'
                     '    token = "TEST:TOKEN"\n'
                     '    raw = _build_test_init_data(token, {"id": 1, "first_name": "Aziz"}, '
                     'int(time.time()))\n'
                     '    result = validate_init_data(raw, token)\n'
                     '    assert result["user"]["first_name"] == "Aziz"\n'
                     '\n'
                     '\n'
                     'def test_validate_init_data_tampered():\n'
                     '    token = "TEST:TOKEN"\n'
                     '    raw = _build_test_init_data(token, {"id": 1, "first_name": "Aziz"}, '
                     'int(time.time()))\n'
                     '    tampered = raw.replace("Aziz", "Hacker")\n'
                     '    try:\n'
                     '        validate_init_data(tampered, token)\n'
                     '        assert False, "сюда не должны дойти"\n'
                     '    except InitDataError:\n'
                     '        pass',
  'task': {'task_title': "Amaliy: initData validatsiya funksiyasini yozing va sinab ko'ring",
           'task_title_ru': 'Практика: напишите и протестируйте функцию проверки initData',
           'task_description': "validate_init_data(init_data, bot_token) funksiyasini o'zingiz "
                               "yozing (yoki darsdagi namunani asos qiling), soxta/o'zgartirilgan "
                               'initData uchun InitDataError chiqishini va eskirgan auth_date '
                               'uchun rad etilishini pytest orqali tekshiring.',
           'task_description_ru': 'Напишите функцию validate_init_data(init_data, bot_token) '
                                  '(можно взять за основу пример из урока), проверьте через '
                                  'pytest, что для поддельного/изменённого initData выбрасывается '
                                  'InitDataError, а устаревший auth_date отклоняется.',
           'task_requirements': "hmac.compare_digest ishlatilgan bo'lishi shart; kamida 2 ta "
                                "pytest test: to'g'ri va soxta initData uchun; auth_date muddati "
                                'tekshiruvi mavjud.',
           'task_requirements_ru': 'Обязательно использование hmac.compare_digest; минимум 2 '
                                   'pytest-теста: для валидного и поддельного initData; '
                                   'реализована проверка срока auth_date.',
           'task_technologies': 'Python, hmac, hashlib, pytest, FastAPI',
           'task_deadline_days': 3},
  'sample': {'title': "Namuna: initData'ni HMAC-SHA256 bilan tekshirish",
             'description': "To'liq validate_init_data funksiyasi + soxta imzoni aniqlash testi",
             'sample_type': 'code',
             'code_files': [{'filename': 'init_data_validator.py',
                             'language': 'python',
                             'code': 'import hashlib\n'
                                     'import hmac\n'
                                     'from urllib.parse import parse_qsl\n'
                                     '\n'
                                     '\n'
                                     'def validate_init_data(init_data: str, bot_token: str) -> '
                                     'dict:\n'
                                     '    pairs = dict(parse_qsl(init_data, strict_parsing=True))\n'
                                     '    received_hash = pairs.pop("hash")\n'
                                     '    data_check_string = "\\n".join(f"{k}={v}" for k, v in '
                                     'sorted(pairs.items()))\n'
                                     '    secret_key = hmac.new(b"WebAppData", bot_token.encode(), '
                                     'hashlib.sha256).digest()\n'
                                     '    computed = hmac.new(secret_key, '
                                     'data_check_string.encode(), hashlib.sha256).hexdigest()\n'
                                     '    if not hmac.compare_digest(computed, received_hash):\n'
                                     '        raise ValueError("Imzo mos kelmadi")\n'
                                     '    return pairs'},
                            {'filename': 'test_init_data_validator.py',
                             'language': 'python',
                             'code': 'import pytest\n'
                                     'from init_data_validator import validate_init_data\n'
                                     '\n'
                                     '\n'
                                     'def test_tampered_hash_rejected():\n'
                                     '    fake = '
                                     '"user=%7B%22id%22%3A1%7D&auth_date=1700000000&hash=deadbeef"\n'
                                     '    with pytest.raises(ValueError):\n'
                                     '        validate_init_data(fake, "123:TEST")'}]},
  'exercises': [{'title': 'compare_digest sababi',
                 'title_ru': 'Причина использования compare_digest',
                 'description': 'Nega hash solishtirishda oddiy == emas, hmac.compare_digest() '
                                'ishlatiladi?',
                 'description_ru': 'Почему при сравнении hash используется hmac.compare_digest(), '
                                   'а не обычное ==?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Timing attack'dan himoyalanish uchun",
                             'Tezroq ishlashi uchun',
                             "Kod chiroyliroq ko'rinishi uchun",
                             "Python == operatorini qo'llab-quvvatlamaydi"],
                 'options_ru': ['Для защиты от timing attack',
                                'Для более быстрой работы',
                                'Чтобы код выглядел красивее',
                                'Python не поддерживает оператор =='],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "== chapdan o'ngga solishtiradi va birinchi mos kelmagan belgida "
                         "to'xtaydi.",
                 'hint_ru': '== сравнивает слева направо и останавливается на первом несовпадении.',
                 'explanation': "compare_digest doimiy vaqtda ishlaydi, shu bilan hash'ni "
                                "belgi-baqadam topishga asoslangan timing attack'ni oldini oladi.",
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'secret_key doimiy qatori',
                 'title_ru': 'Постоянная строка для secret_key',
                 'description': 'secret_key hosil qilishda HMAC kaliti sifatida ishlatiladigan '
                                "doimiy bayt qatori: b'___'",
                 'description_ru': 'Постоянная байтовая строка, используемая как ключ HMAC при '
                                   "вычислении secret_key: b'___'",
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'WebAppData',
                 'hint': "Bu Telegram spetsifikatsiyasida qat'iy belgilangan, o'zgarmas satr.",
                 'hint_ru': 'Эта строка жёстко задана в спецификации Telegram и не меняется.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Validatsiya algoritmi tartibi',
                 'title_ru': 'Порядок алгоритма проверки',
                 'description': "initData validatsiya algoritmining qadamlarini to'g'ri tartibga "
                                'joylashtiring',
                 'description_ru': 'Расположите шаги алгоритма проверки initData в правильном '
                                   'порядке',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ["initData'ni parse_qsl bilan ajratish",
                                'hash maydonini olib tashlash',
                                "qolgan juftlarni kalit bo'yicha saralash",
                                "data_check_string yig'ish",
                                'secret_key hisoblash',
                                'computed_hash hisoblash',
                                'compare_digest bilan solishtirish'],
                 'drag_items_ru': ['Разбор initData через parse_qsl',
                                   'Извлечение поля hash',
                                   'Сортировка оставшихся пар по ключу',
                                   'Сборка data_check_string',
                                   'Вычисление secret_key',
                                   'Вычисление computed_hash',
                                   'Сравнение через compare_digest'],
                 'correct_order': ["initData'ni parse_qsl bilan ajratish",
                                   'hash maydonini olib tashlash',
                                   "qolgan juftlarni kalit bo'yicha saralash",
                                   "data_check_string yig'ish",
                                   'secret_key hisoblash',
                                   'computed_hash hisoblash',
                                   'compare_digest bilan solishtirish'],
                 'hint': 'Har bir qadam oldingisining natijasiga tayanadi.',
                 'hint_ru': 'Каждый шаг опирается на результат предыдущего.',
                 'difficulty_level': 'Hard',
                 'points': 10},
                {'title': 'auth_date tekshiruvining maqsadi',
                 'title_ru': 'Назначение проверки auth_date',
                 'description': "hash to'g'ri bo'lsa ham, nega auth_date alohida tekshirilishi "
                                'kerak?',
                 'description_ru': 'Даже если hash верен, почему нужно отдельно проверять '
                                   'auth_date?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Replay (eski initData'ni qayta ishlatish) hujumidan himoya uchun",
                             "Hash'ni tezroq hisoblash uchun",
                             'Foydalanuvchi tilini aniqlash uchun',
                             'Bot tokenini shifrlash uchun'],
                 'options_ru': ['Для защиты от replay-атаки (повторного использования старого '
                                'initData)',
                                'Чтобы быстрее вычислить hash',
                                'Чтобы определить язык пользователя',
                                'Чтобы зашифровать токен бота'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Hash abadiy amal qiladi, lekin ma'lumot vaqt o'tishi bilan eskirishi "
                         'kerak.',
                 'hint_ru': 'Hash действителен вечно, но данные со временем должны считаться '
                            'устаревшими.',
                 'explanation': "auth_date tekshiruvi bo'lmasa, eski, oshkor bo'lgan initData "
                                "qatori hash tekshiruvidan muvaffaqiyatli o'tib, qayta "
                                'ishlatilishi mumkin.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 2,
  'title': '3-Telegram Payments: invoice yaratish va pre_checkout_query',
  'title_ru': '3-Telegram Payments: создание invoice и pre_checkout_query',
  'points_reward': 17,
  'code_language': 'python',
  'text_content': '<h3>48-kursdagi "to\'lov" bilan bu darsdagi farq</h3>\n'
                  '<p>48-kursning capstone loyihasida "to\'lov" administrator tomonidan qo\'lda '
                  'tasdiqlanadigan buyurtma edi &mdash; foydalanuvchi "to\'ladim" deb yozadi, '
                  'admin tekshirib tasdiqlaydi. Bu ishlaydi, lekin masshtablanmaydi va ishonchli '
                  "emas. Telegram Bot API'ning haqiqiy <strong>Payments</strong> mexanizmi esa "
                  "to'lovni to'g'ridan-to'g'ri Telegram interfeysi ichida, haqiqiy to'lov "
                  "provayderi orqali amalga oshiradi &mdash; karta ma'lumotlari botga umuman "
                  'tegmaydi.</p>\n'
                  '\n'
                  '<h3>Invoice yaratish: bot.send_invoice</h3>\n'
                  "<p>To'lov jarayoni <code>bot.send_invoice(...)</code> chaqiruvidan "
                  'boshlanadi:</p>\n'
                  '<ul>\n'
                  '<li><code>chat_id</code>, <code>title</code>, <code>description</code> &mdash; '
                  "foydalanuvchi ko'radigan matn.</li>\n"
                  '<li><code>payload</code> &mdash; foydalanuvchiga '
                  "<strong>ko'rinmaydigan</strong> ichki qator, sizning buyurtma "
                  'identifikatoringiz. Bu &mdash; keyingi bosqichlarda buyurtmani aniqlashning '
                  "yagona ishonchli yo'li.</li>\n"
                  "<li><code>provider_token</code> &mdash; @BotFather orqali ulangan to'lov "
                  'provayderidan olingan token (mahalliy provayder yoki test rejimidagi Stripe '
                  "kabi). Har bir provayder o'z valyutalari va talablariga ega.</li>\n"
                  '<li><code>currency</code> &mdash; ISO 4217 kodi, masalan '
                  '<code>"UZS"</code>.</li>\n'
                  '<li><code>prices</code> &mdash; <code>LabeledPrice(label=..., '
                  "amount=...)</code> ro'yxati.</li>\n"
                  '</ul>\n'
                  '\n'
                  "<h3>Eng ko'p uchraydigan xato: amount birligi</h3>\n"
                  '<p><code>LabeledPrice.amount</code> valyutaning <strong>eng kichik '
                  'birligida</strong> beriladi &mdash; masalan dollar uchun sentlarda. Bu '
                  'koeffitsient provayderdan provayderga farq qilishi mumkin, shuning uchun aniq '
                  'qiymatni ishlatilayotgan provayderning hujjatidan tekshiring va buni bitta '
                  'joyda &mdash; masalan <code>to_minor_units()</code> funksiyasida &mdash; '
                  "markazlashtiring, har bir handler'da qayta yozmang.</p>\n"
                  '\n'
                  "<h3>pre_checkout_query &mdash; pulni yechishdan oldingi so'nggi imkoniyat</h3>\n"
                  "<p>Foydalanuvchi to'lov shaklini to'ldirib tasdiqlagach, Telegram pulni "
                  'yechishdan <strong>oldin</strong> botga <code>pre_checkout_query</code> '
                  'yuboradi. Bot <code>answer_pre_checkout_query(pre_checkout_query.id, '
                  'ok=True)</code> yoki <code>ok=False, error_message=...</code> bilan javob '
                  'berishi <strong>shart</strong> &mdash; va buni <strong>10 soniya '
                  "ichida</strong> qilishi kerak. Javob bo'lmasa yoki kechiksa, Telegram to'lovni "
                  "bekor qiladi. Bu &mdash; zaxirani, narxni, foydalanuvchi huquqini so'nggi marta "
                  "serverda tekshirish uchun ideal joy: mahsulot tugab qolgan bo'lsa, aynan shu "
                  'yerda <code>ok=False</code> qaytariladi va pul umuman yechilmaydi.</p>\n'
                  '\n'
                  "<h3>To'liq oqim &mdash; besh qadam</h3>\n"
                  '<pre class="mermaid">\n'
                  'sequenceDiagram\n'
                  '  participant U as Foydalanuvchi\n'
                  '  participant T as Telegram\n'
                  '  participant B as Bot (aiogram)\n'
                  '  U->>B: /buy komandasi\n'
                  '  B->>T: bot.send_invoice(payload=..., prices=[...])\n'
                  "  T-->>U: to'lov shakli (karta ma'lumotlari kiritiladi)\n"
                  "  U->>T: to'lovni tasdiqlash\n"
                  '  T->>B: pre_checkout_query\n'
                  "  B->>B: zaxira/narxni DB'da tekshirish\n"
                  '  B->>T: answer_pre_checkout_query(ok=True) — 10s ichida\n'
                  '  T->>T: pulni yechish\n'
                  '  T->>B: message(successful_payment=...)\n'
                  '</pre>\n'
                  "<p>E'tibor bering: <code>pre_checkout_query</code>ga <code>ok=True</code> "
                  "deyilgandan keyingina haqiqiy pul yechiladi. Shu bosqichgacha bo'lgan hamma "
                  "narsa &mdash; faqat forma to'ldirish, hali pul harakati yo'q.</p>\n"
                  '\n'
                  "<h3>Nega DB tekshiruvi pre_checkout_query'da, invoice yaratishda emas</h3>\n"
                  "<p>Invoice yuborilgandan to foydalanuvchi tasdiqlashigacha vaqt o'tishi mumkin "
                  '&mdash; shu oraliqda boshqa foydalanuvchi oxirgi dona mahsulotni sotib olishi '
                  'mumkin. Shuning uchun zaxirani <code>send_invoice</code> chaqirilganda emas, '
                  "<code>pre_checkout_query</code> kelganda &mdash; ya'ni haqiqatan pul "
                  'yechilishidan bir necha soniya oldin &mdash; tekshirish kerak. Bu '
                  '"check-then-act" xatosining klassik namunasi: tekshiruv bilan harakat orasidagi '
                  "vaqt qanchalik qisqa bo'lsa, race condition xavfi shunchalik kam.</p>\n"
                  '\n'
                  '<h3>Test rejimida sinash</h3>\n'
                  "<p>Haqiqiy pul sarflamasdan sinash uchun @BotFather orqali ulangan ko'pchilik "
                  'provayderlar <strong>test rejimi</strong>ni taqdim etadi &mdash; bunda maxsus '
                  "test provider_token beriladi va karta ma'lumotlari o'rniga standart test karta "
                  'raqamlari ishlatiladi (masalan Stripe test rejimida <code>4242 4242 4242 '
                  "4242</code>). Ishlab chiqishda va CI'da har doim test provider_token "
                  "ishlatilishi, prodakshn provider_token esa faqat muhit o'zgaruvchisi "
                  '(environment variable) orqali, hech qachon kodga yozilmasdan saqlanishi '
                  'kerak.</p>\n'
                  '\n'
                  '<h3>currency va prices mosligini tekshirish</h3>\n'
                  "<p><code>send_invoice</code>ga noto'g'ri <code>currency</code> yoki bo'sh "
                  "<code>prices</code> ro'yxati yuborilsa, Telegram so'rovni rad etadi va aiogram "
                  "mos xatolik (masalan <code>TelegramBadRequest</code>) ko'taradi &mdash; bu "
                  "xatolikni bot darajasida ushlab, foydalanuvchiga tushunarli xabar ko'rsatish "
                  'kerak, aks holda foydalanuvchi hech qanday javob olmay qoladi.</p>',
  'text_content_ru': '<h3>Чем это отличается от "оплаты" в курсе 48</h3>\n'
                     '<p>В капстоун-проекте курса 48 "оплата" была заказом, который вручную '
                     'подтверждал администратор — пользователь писал "оплатил", админ проверял и '
                     'подтверждал. Это работает, но не масштабируется и не надёжно. Настоящий '
                     'механизм <strong>Payments</strong> Bot API проводит оплату прямо внутри '
                     'интерфейса Telegram, через реального платёжного провайдера — данные карты '
                     'вообще не попадают к боту.</p>\n'
                     '\n'
                     '<h3>Создание invoice: bot.send_invoice</h3>\n'
                     '<p>Процесс оплаты начинается с вызова '
                     '<code>bot.send_invoice(...)</code>:</p>\n'
                     '<ul>\n'
                     '<li><code>chat_id</code>, <code>title</code>, <code>description</code> — '
                     'текст, который видит пользователь.</li>\n'
                     '<li><code>payload</code> — <strong>невидимая</strong> пользователю '
                     'внутренняя строка, ваш идентификатор заказа. Это единственный надёжный '
                     'способ определить заказ на следующих шагах.</li>\n'
                     '<li><code>provider_token</code> — токен от платёжного провайдера, '
                     'подключённого через @BotFather (локальный провайдер или, например, тестовый '
                     'режим Stripe). У каждого провайдера свои валюты и требования.</li>\n'
                     '<li><code>currency</code> — код ISO 4217, например <code>"UZS"</code>.</li>\n'
                     '<li><code>prices</code> — список <code>LabeledPrice(label=..., '
                     'amount=...)</code>.</li>\n'
                     '</ul>\n'
                     '\n'
                     '<h3>Самая частая ошибка: единица amount</h3>\n'
                     '<p><code>LabeledPrice.amount</code> указывается в <strong>наименьшей '
                     'единице</strong> валюты — например в центах для доллара. Этот коэффициент '
                     'может отличаться от провайдера к провайдеру, поэтому точное значение '
                     'уточните в документации используемого провайдера и централизуйте его в одном '
                     'месте — например в функции <code>to_minor_units()</code> — не переписывайте '
                     'в каждом обработчике.</p>\n'
                     '\n'
                     '<h3>pre_checkout_query — последний шанс перед списанием денег</h3>\n'
                     '<p>После того как пользователь заполнил и подтвердил форму оплаты, Telegram '
                     '<strong>перед</strong> списанием денег отправляет боту '
                     '<code>pre_checkout_query</code>. Бот <strong>обязан</strong> ответить '
                     '<code>answer_pre_checkout_query(pre_checkout_query.id, ok=True)</code> либо '
                     '<code>ok=False, error_message=...</code> — и сделать это в течение '
                     '<strong>10 секунд</strong>. Если ответа нет или он опоздал, Telegram '
                     'отменяет оплату. Это идеальное место для последней проверки на сервере '
                     'остатка товара, цены, права пользователя: если товар закончился, именно '
                     'здесь возвращается <code>ok=False</code>, и деньги вообще не '
                     'списываются.</p>\n'
                     '\n'
                     '<h3>Полный поток — пять шагов</h3>\n'
                     '<pre class="mermaid">\n'
                     'sequenceDiagram\n'
                     '  participant U as Пользователь\n'
                     '  participant T as Telegram\n'
                     '  participant B as Бот (aiogram)\n'
                     '  U->>B: команда /buy\n'
                     '  B->>T: bot.send_invoice(payload=..., prices=[...])\n'
                     '  T-->>U: форма оплаты (ввод данных карты)\n'
                     '  U->>T: подтверждение оплаты\n'
                     '  T->>B: pre_checkout_query\n'
                     '  B->>B: проверка остатка/цены в БД\n'
                     '  B->>T: answer_pre_checkout_query(ok=True) — за 10с\n'
                     '  T->>T: списание денег\n'
                     '  T->>B: message(successful_payment=...)\n'
                     '</pre>\n'
                     '<p>Обратите внимание: реальное списание денег происходит только после ответа '
                     '<code>ok=True</code> на <code>pre_checkout_query</code>. Всё, что было до '
                     'этого шага, — лишь заполнение формы, движения денег ещё нет.</p>\n'
                     '\n'
                     '<h3>Почему проверка БД — в pre_checkout_query, а не при создании '
                     'invoice</h3>\n'
                     '<p>Между отправкой invoice и подтверждением пользователем может пройти время '
                     '— за это время другой пользователь может купить последнюю единицу товара. '
                     'Поэтому остаток нужно проверять не в момент вызова '
                     '<code>send_invoice</code>, а в момент прихода '
                     '<code>pre_checkout_query</code> — то есть за несколько секунд до реального '
                     'списания денег. Это классический пример проблемы "check-then-act": чем '
                     'короче промежуток между проверкой и действием, тем ниже риск race '
                     'condition.</p>\n'
                     '\n'
                     '<h3>Тестирование в тестовом режиме</h3>\n'
                     '<p>Чтобы протестировать без реальных денег, большинство провайдеров, '
                     'подключаемых через @BotFather, предоставляют <strong>тестовый режим</strong> '
                     '— выдаётся специальный тестовый provider_token, а вместо реальных данных '
                     'карты используются стандартные тестовые номера карт (например, в тестовом '
                     'режиме Stripe — <code>4242 4242 4242 4242</code>). В разработке и CI всегда '
                     'должен использоваться тестовый provider_token, а продакшн-токен должен '
                     'храниться только в переменных окружения, никогда не записываясь в код.</p>\n'
                     '\n'
                     '<h3>Проверка соответствия currency и prices</h3>\n'
                     '<p>Если в <code>send_invoice</code> передать неверный <code>currency</code> '
                     'или пустой список <code>prices</code>, Telegram отклонит запрос, а aiogram '
                     'выбросит соответствующую ошибку (например <code>TelegramBadRequest</code>) — '
                     'эту ошибку нужно перехватывать на уровне бота и показывать пользователю '
                     'понятное сообщение, иначе пользователь останется вообще без ответа.</p>',
  'code_content': 'from aiogram import Router\n'
                  'from aiogram.types import Message, PreCheckoutQuery, LabeledPrice\n'
                  'from aiogram.filters import Command\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  'PROVIDER_TOKEN = "381764678:TEST:12345"  # BotFather orqali olingan, .env\'da '
                  'saqlanadi\n'
                  'CURRENCY = "UZS"\n'
                  '\n'
                  '\n'
                  'def to_minor_units(sum_uzs: int) -> int:\n'
                  '    """Provayder talab qiladigan eng kichik birlikka o\'tkazadi.\n'
                  '    Aniq koeffitsientni ishlatilayotgan provayderning hujjatidan '
                  'tasdiqlang."""\n'
                  '    return sum_uzs * 100\n'
                  '\n'
                  '\n'
                  '@router.message(Command("buy"))\n'
                  'async def cmd_buy(message: Message, db_session):\n'
                  '    product = await get_product(db_session, sku="premium_1m")\n'
                  '    if product.stock <= 0:\n'
                  '        await message.answer("Kechirasiz, mahsulot tugagan.")\n'
                  '        return\n'
                  '\n'
                  '    await message.bot.send_invoice(\n'
                  '        chat_id=message.chat.id,\n'
                  '        title=product.title,\n'
                  '        description=product.description,\n'
                  '        payload=f"order:{product.id}:{message.from_user.id}",\n'
                  '        provider_token=PROVIDER_TOKEN,\n'
                  '        currency=CURRENCY,\n'
                  '        prices=[LabeledPrice(label=product.title, '
                  'amount=to_minor_units(product.price_uzs))],\n'
                  '    )\n'
                  '\n'
                  '\n'
                  '@router.pre_checkout_query()\n'
                  'async def handle_pre_checkout(pre_checkout_query: PreCheckoutQuery, '
                  'db_session):\n'
                  '    _, product_id, user_id = pre_checkout_query.invoice_payload.split(":")\n'
                  '    product = await get_product(db_session, id=int(product_id))\n'
                  '\n'
                  '    if product is None or product.stock <= 0:\n'
                  '        await pre_checkout_query.bot.answer_pre_checkout_query(\n'
                  '            pre_checkout_query.id, ok=False,\n'
                  '            error_message="Kechirasiz, mahsulot tugab qoldi. Pul yechilmadi.",\n'
                  '        )\n'
                  '        return\n'
                  '\n'
                  '    expected_amount = to_minor_units(product.price_uzs)\n'
                  '    if pre_checkout_query.total_amount != expected_amount:\n'
                  '        await pre_checkout_query.bot.answer_pre_checkout_query(\n'
                  '            pre_checkout_query.id, ok=False, error_message="Narx nomuvofiqligi '
                  'aniqlandi.",\n'
                  '        )\n'
                  '        return\n'
                  '\n'
                  '    await '
                  'pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, '
                  'ok=True)\n'
                  '\n'
                  '\n'
                  'async def get_product(db_session, **filters):\n'
                  "    ...  # repository qatlamidan haqiqiy so'rov",
  'code_content_ru': 'from aiogram import Router\n'
                     'from aiogram.types import Message, PreCheckoutQuery, LabeledPrice\n'
                     'from aiogram.filters import Command\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     'PROVIDER_TOKEN = "381764678:TEST:12345"  # получен через BotFather, хранится '
                     'в .env\n'
                     'CURRENCY = "UZS"\n'
                     '\n'
                     '\n'
                     'def to_minor_units(sum_uzs: int) -> int:\n'
                     '    """Переводит в наименьшую единицу, которую требует провайдер.\n'
                     '    Точный коэффициент нужно проверить в документации используемого '
                     'провайдера."""\n'
                     '    return sum_uzs * 100\n'
                     '\n'
                     '\n'
                     '@router.message(Command("buy"))\n'
                     'async def cmd_buy(message: Message, db_session):\n'
                     '    product = await get_product(db_session, sku="premium_1m")\n'
                     '    if product.stock <= 0:\n'
                     '        await message.answer("Извините, товар закончился.")\n'
                     '        return\n'
                     '\n'
                     '    await message.bot.send_invoice(\n'
                     '        chat_id=message.chat.id,\n'
                     '        title=product.title,\n'
                     '        description=product.description,\n'
                     '        payload=f"order:{product.id}:{message.from_user.id}",\n'
                     '        provider_token=PROVIDER_TOKEN,\n'
                     '        currency=CURRENCY,\n'
                     '        prices=[LabeledPrice(label=product.title, '
                     'amount=to_minor_units(product.price_uzs))],\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '@router.pre_checkout_query()\n'
                     'async def handle_pre_checkout(pre_checkout_query: PreCheckoutQuery, '
                     'db_session):\n'
                     '    _, product_id, user_id = pre_checkout_query.invoice_payload.split(":")\n'
                     '    product = await get_product(db_session, id=int(product_id))\n'
                     '\n'
                     '    if product is None or product.stock <= 0:\n'
                     '        await pre_checkout_query.bot.answer_pre_checkout_query(\n'
                     '            pre_checkout_query.id, ok=False,\n'
                     '            error_message="Извините, товар закончился. Деньги не списаны.",\n'
                     '        )\n'
                     '        return\n'
                     '\n'
                     '    expected_amount = to_minor_units(product.price_uzs)\n'
                     '    if pre_checkout_query.total_amount != expected_amount:\n'
                     '        await pre_checkout_query.bot.answer_pre_checkout_query(\n'
                     '            pre_checkout_query.id, ok=False, error_message="Обнаружено '
                     'несоответствие цены.",\n'
                     '        )\n'
                     '        return\n'
                     '\n'
                     '    await '
                     'pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, '
                     'ok=True)\n'
                     '\n'
                     '\n'
                     'async def get_product(db_session, **filters):\n'
                     '    ...  # реальный запрос через слой репозитория',
  'task': {'task_title': "Amaliy: to'liq invoice + pre_checkout_query oqimini yozing",
           'task_title_ru': 'Практика: реализуйте полный поток invoice + pre_checkout_query',
           'task_description': 'Bitta mahsulot uchun /buy komandasi orqali invoice yuboring, '
                               "pre_checkout_query handler'da DB'dan zaxira va narxni tekshiring, "
                               'mos kelmasa ok=False bilan rad eting.',
           'task_description_ru': 'Реализуйте отправку invoice через команду /buy для одного '
                                  'товара, в обработчике pre_checkout_query проверяйте остаток и '
                                  'цену из БД, при несоответствии отклоняйте с ok=False.',
           'task_requirements': 'amount to_minor_units() orqali hisoblanishi; invoice_payload '
                                "ichida buyurtma identifikatori bo'lishi; pre_checkout_query 10 "
                                'soniya ichida javob berilishi; narx nomuvofiqligi tekshirilishi.',
           'task_requirements_ru': 'amount должен вычисляться через to_minor_units(); '
                                   'invoice_payload должен содержать идентификатор заказа; ответ '
                                   'на pre_checkout_query — в течение 10 секунд; должно '
                                   'проверяться несовпадение цены.',
           'task_technologies': 'aiogram 3.x, Telegram Payments API, SQLAlchemy async',
           'task_deadline_days': 4},
  'sample': {'title': "Namuna: invoice yuborish va pre_checkout_query'ni tasdiqlash",
             'description': "Bitta mahsulot uchun to'liq /buy -> invoice -> pre_checkout_query "
                            'zanjiri',
             'sample_type': 'code',
             'code_files': [{'filename': 'payments_invoice.py',
                             'language': 'python',
                             'code': 'from aiogram import Router\n'
                                     'from aiogram.filters import Command\n'
                                     'from aiogram.types import Message, PreCheckoutQuery, '
                                     'LabeledPrice\n'
                                     '\n'
                                     'router = Router()\n'
                                     'PROVIDER_TOKEN = "381764678:TEST:12345"\n'
                                     '\n'
                                     '\n'
                                     '@router.message(Command("buy"))\n'
                                     'async def cmd_buy(message: Message):\n'
                                     '    await message.bot.send_invoice(\n'
                                     '        chat_id=message.chat.id,\n'
                                     '        title="Premium obuna",\n'
                                     '        description="1 oylik premium xizmat",\n'
                                     '        payload=f"order:premium:{message.from_user.id}",\n'
                                     '        provider_token=PROVIDER_TOKEN,\n'
                                     '        currency="UZS",\n'
                                     '        prices=[LabeledPrice(label="Premium 1 oy", '
                                     'amount=5000000)],\n'
                                     '    )\n'
                                     '\n'
                                     '\n'
                                     '@router.pre_checkout_query()\n'
                                     'async def handle_pre_checkout(pcq: PreCheckoutQuery):\n'
                                     '    await pcq.bot.answer_pre_checkout_query(pcq.id, '
                                     'ok=True)'}]},
  'exercises': [{'title': 'pre_checkout_query javob muddati',
                 'title_ru': 'Срок ответа на pre_checkout_query',
                 'description': "bot pre_checkout_query'ga necha soniya ichida javob berishi "
                                'shart?',
                 'description_ru': 'За сколько секунд бот обязан ответить на pre_checkout_query?',
                 'exercise_type': 'multiple_choice',
                 'options': ['10 soniya', '60 soniya', '5 daqiqa', "Muddat yo'q"],
                 'options_ru': ['10 секунд', '60 секунд', '5 минут', 'Срока нет'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Muddat juda qisqa — shuning uchun tekshiruv oldindan tez bo'lishi kerak.",
                 'hint_ru': 'Срок очень короткий — поэтому проверка должна быть быстрой.',
                 'explanation': "Telegram 10 soniya ichida javob kutadi; kechiksa to'lov avtomatik "
                                'bekor qilinadi.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': "pre_checkout_query'ga javob metodi",
                 'title_ru': 'Метод ответа на pre_checkout_query',
                 'description': "So'rovni tasdiqlash uchun ishlatiladigan to'liq metod nomi: "
                                'bot.answer_pre_checkout____',
                 'description_ru': 'Полное имя метода для подтверждения запроса: '
                                   'bot.answer_pre_checkout____',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'query',
                 'hint': "Metod nomi so'rovning o'zi nomi bilan tugaydi.",
                 'hint_ru': 'Имя метода заканчивается тем же словом, что и сам запрос.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': "To'lov oqimi tartibi",
                 'title_ru': 'Порядок потока оплаты',
                 'description': "To'lov oqimining qadamlarini to'g'ri tartibga joylashtiring",
                 'description_ru': 'Расположите шаги потока оплаты в правильном порядке',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Foydalanuvchi /buy yuboradi',
                                'Bot send_invoice chaqiradi',
                                "Foydalanuvchi to'lov shaklini tasdiqlaydi",
                                'Telegram pre_checkout_query yuboradi',
                                "Bot DB'da zaxirani tekshiradi",
                                'Bot answer_pre_checkout_query(ok=True) chaqiradi',
                                'Telegram pulni yechadi'],
                 'drag_items_ru': ['Пользователь отправляет /buy',
                                   'Бот вызывает send_invoice',
                                   'Пользователь подтверждает форму оплаты',
                                   'Telegram отправляет pre_checkout_query',
                                   'Бот проверяет остаток в БД',
                                   'Бот вызывает answer_pre_checkout_query(ok=True)',
                                   'Telegram списывает деньги'],
                 'correct_order': ['Foydalanuvchi /buy yuboradi',
                                   'Bot send_invoice chaqiradi',
                                   "Foydalanuvchi to'lov shaklini tasdiqlaydi",
                                   'Telegram pre_checkout_query yuboradi',
                                   "Bot DB'da zaxirani tekshiradi",
                                   'Bot answer_pre_checkout_query(ok=True) chaqiradi',
                                   'Telegram pulni yechadi'],
                 'hint': 'Pul faqat oxirgi qadamda yechiladi.',
                 'hint_ru': 'Деньги списываются только на последнем шаге.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Zaxira tekshiruvi qayerda bajarilishi kerak',
                 'title_ru': 'Где должна выполняться проверка остатка',
                 'description': "Nega mahsulot zaxirasini tekshirish send_invoice'da emas, aynan "
                                "pre_checkout_query'da bajarilishi kerak?",
                 'description_ru': 'Почему проверку остатка товара нужно делать именно в '
                                   'pre_checkout_query, а не в send_invoice?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Chunki invoice va tasdiqlash orasida boshqa foydalanuvchi mahsulotni '
                             'sotib olishi mumkin',
                             "Chunki send_invoice'da DB'ga ulanib bo'lmaydi",
                             'Chunki pre_checkout_query DB tekshiruvini talab qilmaydi',
                             "Farqi yo'q, ikkalasi ham bir xil"],
                 'options_ru': ['Потому что между invoice и подтверждением другой пользователь '
                                'может купить товар',
                                'Потому что в send_invoice нельзя подключиться к БД',
                                'Потому что pre_checkout_query не требует проверки БД',
                                'Разницы нет, оба варианта одинаковы'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Bu race condition / check-then-act muammosi bilan bog'liq.",
                 'hint_ru': 'Это связано с проблемой race condition / check-then-act.',
                 'explanation': 'Tekshiruv bilan pul yechish orasidagi vaqt qanchalik qisqa '
                                "bo'lsa, boshqa foydalanuvchi bilan to'qnashish (race condition) "
                                "xavfi shunchalik kam bo'ladi.",
                 'difficulty_level': 'Hard',
                 'points': 10}]},
 {'order': 3,
  'title': '4-successful_payment, pul qaytarish va Telegram Stars',
  'title_ru': '4-successful_payment, возврат средств и Telegram Stars',
  'points_reward': 17,
  'code_language': 'python',
  'text_content': '<h3>Pul yechilgach: successful_payment</h3>\n'
                  "<p><code>pre_checkout_query</code>ga <code>ok=True</code> javobidan so'ng, "
                  'Telegram haqiqatan pulni yechadi va botga oddiy <code>Message</code> yuboradi '
                  "&mdash; unda <code>message.successful_payment</code> maydoni to'ldirilgan "
                  "bo'ladi:</p>\n"
                  '<table>\n'
                  "<tr><th>Maydon</th><th>Ma'nosi</th></tr>\n"
                  '<tr><td><code>total_amount</code></td><td>Yechilgan summa (eng kichik '
                  'birlikda)</td></tr>\n'
                  '<tr><td><code>currency</code></td><td>Valyuta kodi</td></tr>\n'
                  '<tr><td><code>invoice_payload</code></td><td>Siz <code>send_invoice</code>da '
                  'yuborgan ichki payload &mdash; buyurtmani aynan shu orqali topasiz</td></tr>\n'
                  '<tr><td><code>telegram_payment_charge_id</code></td><td>Telegram tomonidagi '
                  "noyob to'lov identifikatori &mdash; qaytarish (refund) uchun kerak</td></tr>\n"
                  "<tr><td><code>provider_payment_charge_id</code></td><td>To'lov provayderi "
                  'tomonidagi identifikator</td></tr>\n'
                  '</table>\n'
                  '\n'
                  '<h3>Idempotentlik: nega bir xil to\'lovni ikki marta "bajarmaslik" kerak</h3>\n'
                  "<p>Telegram update'larni <strong>kamida bir marta</strong> yetkazishga kafolat "
                  "beradi, lekin ba'zan tarmoq muammosi tufayli bitta update ikki marta kelishi "
                  'mumkin (masalan webhook qayta urinishi). Agar <code>successful_payment</code> '
                  'handler\'ingiz mahsulotni "bir marta" berish o\'rniga har safar berib yuborsa '
                  '&mdash; foydalanuvchi bitta pul evaziga ikkita xizmat oladi. Yechim: '
                  '<code>telegram_payment_charge_id</code>ni (yoki <code>invoice_payload</code>ni) '
                  "ma'lumotlar bazasida <strong>UNIQUE</strong> ustun sifatida saqlang; qayta "
                  'kelgan xabar uchun yozuv allaqachon mavjudligini tekshirib, ikkinchi marta hech '
                  'narsa bajarmang.</p>\n'
                  '\n'
                  '<h3>Pul qaytarish (refund) &mdash; faqat Stars uchun Bot API orqali</h3>\n'
                  "<p>Bot API'da <code>refund_star_payment(user_id, "
                  'telegram_payment_charge_id)</code> metodi bor &mdash; lekin u <strong>faqat '
                  "Telegram Stars</strong> orqali to'langan xaridlar uchun ishlaydi. Haqiqiy fiat "
                  'pul (UZS, USD va h.k.) uchun Bot API\'da umumiy "qaytarish" metodi '
                  "<strong>yo'q</strong> &mdash; qaytarish ulangan to'lov provayderining o'z "
                  "boshqaruv paneli yoki API'si orqali amalga oshiriladi, chunki pul aslida "
                  "provayder hisobidan o'tadi, Telegram faqat vositachi.</p>\n"
                  '\n'
                  '<h3>Telegram Stars (XTR) &mdash; ichki raqamli valyuta</h3>\n'
                  "<p>Stars &mdash; Telegram'ning o'z ichki valyutasi, foydalanuvchilar uni ilova "
                  'ichidan sotib oladi va botlar/mini-ilovalarda raqamli tovar/xizmat uchun '
                  'sarflaydi. Stars bilan invoice yaratish sodda: <code>currency="XTR"</code>, '
                  '<code>provider_token=""</code> (bo\'sh qator &mdash; tashqi provayder shart '
                  "emas). Muhim cheklov: Telegram qoidalariga ko'ra Stars faqat <strong>raqamli "
                  'tovar/xizmat</strong> uchun ishlatilishi mumkin (masalan premium funksiya, '
                  "virtual buyum) &mdash; jismoniy tovarlarni Stars orqali sotib bo'lmaydi, ular "
                  'uchun haqiqiy fiat + provider_token kerak.</p>\n'
                  '\n'
                  '<h3>Ikkala oqimni solishtirish</h3>\n'
                  '<table>\n'
                  '<tr><th></th><th>Fiat (UZS/USD/...)</th><th>Telegram Stars (XTR)</th></tr>\n'
                  "<tr><td>provider_token</td><td>Tashqi provayderdan olingan</td><td>Bo'sh "
                  'qator</td></tr>\n'
                  '<tr><td>Kim uchun</td><td>Har qanday tovar/xizmat</td><td>Faqat raqamli '
                  'tovar/xizmat</td></tr>\n'
                  '<tr><td>Qaytarish</td><td>Provayder paneli/API '
                  'orqali</td><td><code>refund_star_payment</code> Bot API orqali</td></tr>\n'
                  '<tr><td>Sozlash murakkabligi</td><td>Yuqori (provayder shartnomasi '
                  "kerak)</td><td>Past (BotFather'da yoqiladi)</td></tr>\n"
                  '</table>\n'
                  '\n'
                  "<h3>Handler'ni yozish tartibi</h3>\n"
                  '<p>Amaliy qoida: <code>successful_payment</code> handler ichida birinchi '
                  'navbatda idempotentlik tekshiruvi, keyin yozuvni saqlash, faqat shundan keyin '
                  'foydalanuvchiga xizmatni "berish" (masalan, kanalga taklifnoma yuborish yoki '
                  "premium flag'ni yoqish) bajarilishi kerak &mdash; aks holda xatolik yozuvni "
                  "saqlashdan oldin yuz bersa, pul yechilgan bo'ladi-yu, xizmat berilmay "
                  'qoladi.</p>\n'
                  '\n'
                  "<h3>Audit: to'lov voqealarini xom holda saqlash</h3>\n"
                  '<p>Amaliy tavsiya: <code>successful_payment</code>ning barcha maydonlarini '
                  "(hatto keyinchalik kerak bo'lmasa ham) alohida audit jadvaliga xom (raw) holda "
                  "saqlab qo'ying. Kelajakda provayder bilan nizoli holat yoki hisobot kerak "
                  "bo'lganda, aynan shu audit yozuvi &mdash; Telegram tomonidan yuborilgan asl "
                  "ma'lumot &mdash; eng ishonchli manba bo'ladi.</p>\n"
                  '\n'
                  '<h3>"Muvaffaqiyatsiz to\'lov" degan alohida update yo\'q</h3>\n'
                  "<p>Ko'p dasturchi <code>failed_payment</code> degan update kutadi &mdash; lekin "
                  "bunday update Bot API'da <strong>mavjud emas</strong>. Agar foydalanuvchi "
                  "to'lov shaklini bekor qilsa yoki karta rad etilsa, bot umuman hech qanday xabar "
                  'olmaydi &mdash; shunchaki <code>successful_payment</code> kelmay qoladi. '
                  'Shuning uchun "kutilayotgan" buyurtmalarni vaqt bo\'yicha tozalash (masalan, 30 '
                  'daqiqadan keyin "bekor qilingan" deb belgilash) alohida fon vazifasi sifatida '
                  'amalga oshiriladi.</p>',
  'text_content_ru': '<h3>После списания денег: successful_payment</h3>\n'
                     '<p>После ответа <code>ok=True</code> на <code>pre_checkout_query</code> '
                     'Telegram реально списывает деньги и отправляет боту обычное '
                     '<code>Message</code> — в нём заполнено поле '
                     '<code>message.successful_payment</code>:</p>\n'
                     '<table>\n'
                     '<tr><th>Поле</th><th>Значение</th></tr>\n'
                     '<tr><td><code>total_amount</code></td><td>Списанная сумма (в наименьшей '
                     'единице)</td></tr>\n'
                     '<tr><td><code>currency</code></td><td>Код валюты</td></tr>\n'
                     '<tr><td><code>invoice_payload</code></td><td>Ваш внутренний payload из '
                     '<code>send_invoice</code> — именно по нему находится заказ</td></tr>\n'
                     '<tr><td><code>telegram_payment_charge_id</code></td><td>Уникальный '
                     'идентификатор платежа со стороны Telegram — нужен для возврата '
                     '(refund)</td></tr>\n'
                     '<tr><td><code>provider_payment_charge_id</code></td><td>Идентификатор со '
                     'стороны платёжного провайдера</td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Идемпотентность: почему нельзя "выполнять" один платёж дважды</h3>\n'
                     '<p>Telegram гарантирует доставку обновлений <strong>минимум один '
                     'раз</strong>, но иногда из-за сетевых проблем одно обновление может прийти '
                     'дважды (например, повторная отправка webhook). Если обработчик '
                     '<code>successful_payment</code> будет выдавать товар каждый раз, а не один '
                     'раз — пользователь получит услугу дважды за одну оплату. Решение: храните '
                     '<code>telegram_payment_charge_id</code> (или <code>invoice_payload</code>) в '
                     'базе данных как <strong>UNIQUE</strong>-колонку; для повторно пришедшего '
                     'сообщения проверяйте, что запись уже существует, и не выполняйте действие '
                     'повторно.</p>\n'
                     '\n'
                     '<h3>Возврат средств (refund) — только для Stars через Bot API</h3>\n'
                     '<p>В Bot API есть метод <code>refund_star_payment(user_id, '
                     'telegram_payment_charge_id)</code> — но он работает <strong>только для '
                     'покупок, оплаченных Telegram Stars</strong>. Для реальных фиатных денег '
                     '(UZS, USD и т.д.) в Bot API <strong>нет</strong> универсального метода '
                     'возврата — возврат делается через собственную панель управления или API '
                     'подключённого платёжного провайдера, поскольку деньги фактически проходят '
                     'через счёт провайдера, а Telegram выступает лишь посредником.</p>\n'
                     '\n'
                     '<h3>Telegram Stars (XTR) — внутренняя цифровая валюта</h3>\n'
                     '<p>Stars — собственная внутренняя валюта Telegram: пользователи покупают её '
                     'внутри приложения и тратят в ботах/мини-приложениях на цифровые '
                     'товары/услуги. Создать invoice со Stars просто: <code>currency="XTR"</code>, '
                     '<code>provider_token=""</code> (пустая строка — внешний провайдер не нужен). '
                     'Важное ограничение: по правилам Telegram Stars можно использовать только для '
                     '<strong>цифровых</strong> товаров/услуг (например, премиум-функция, '
                     'виртуальный предмет) — физические товары через Stars продавать нельзя, для '
                     'них нужна реальная фиатная оплата с provider_token.</p>\n'
                     '\n'
                     '<h3>Сравнение двух потоков</h3>\n'
                     '<table>\n'
                     '<tr><th></th><th>Фиат (UZS/USD/...)</th><th>Telegram Stars (XTR)</th></tr>\n'
                     '<tr><td>provider_token</td><td>Получен от внешнего провайдера</td><td>Пустая '
                     'строка</td></tr>\n'
                     '<tr><td>Для чего</td><td>Любой товар/услуга</td><td>Только цифровые '
                     'товары/услуги</td></tr>\n'
                     '<tr><td>Возврат</td><td>Через панель/API '
                     'провайдера</td><td><code>refund_star_payment</code> через Bot API</td></tr>\n'
                     '<tr><td>Сложность настройки</td><td>Высокая (нужен договор с '
                     'провайдером)</td><td>Низкая (включается в BotFather)</td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Порядок написания обработчика</h3>\n'
                     '<p>Практическое правило: внутри обработчика <code>successful_payment</code> '
                     'сначала должна идти проверка идемпотентности, затем сохранение записи, и '
                     'только потом — фактическая "выдача" услуги пользователю (например, отправка '
                     'приглашения в канал или включение премиум-флага) — иначе если ошибка '
                     'произойдёт до сохранения записи, деньги окажутся списаны, а услуга не будет '
                     'предоставлена.</p>\n'
                     '\n'
                     '<h3>Аудит: сохранение сырых данных о платеже</h3>\n'
                     '<p>Практическая рекомендация: сохраняйте все поля '
                     '<code>successful_payment</code> (даже если они пока не нужны) в отдельную '
                     'таблицу аудита в сыром виде. Если в будущем возникнет спор с провайдером или '
                     'понадобится отчётность, именно эта запись — исходные данные, присланные '
                     'Telegram, — будет самым надёжным источником.</p>\n'
                     '\n'
                     '<h3>Отдельного обновления "неудачный платёж" не существует</h3>\n'
                     '<p>Многие разработчики ожидают обновление вида <code>failed_payment</code> — '
                     'но такого обновления в Bot API <strong>не существует</strong>. Если '
                     'пользователь отменил форму оплаты или карта была отклонена, бот вообще не '
                     'получает никакого сообщения — просто <code>successful_payment</code> не '
                     'приходит. Поэтому очистку "ожидающих" заказов по времени (например, пометка '
                     'как "отменён" через 30 минут) нужно реализовывать отдельной фоновой '
                     'задачей.</p>',
  'code_content': 'from aiogram import Router, F\n'
                  'from aiogram.filters import Command\n'
                  'from aiogram.types import Message, LabeledPrice\n'
                  'from sqlalchemy.exc import IntegrityError\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  '\n'
                  '@router.message(F.successful_payment)\n'
                  'async def handle_successful_payment(message: Message, db_session):\n'
                  '    payment = message.successful_payment\n'
                  '\n'
                  '    try:\n'
                  '        await save_payment_record(\n'
                  '            db_session,\n'
                  '            charge_id=payment.telegram_payment_charge_id,\n'
                  '            invoice_payload=payment.invoice_payload,\n'
                  '            amount=payment.total_amount,\n'
                  '            currency=payment.currency,\n'
                  '        )\n'
                  '    except IntegrityError:\n'
                  "        # charge_id UNIQUE ustunga to'qnashdi — bu update allaqachon qayta "
                  'ishlangan,\n'
                  "        # xizmatni ikkinchi marta bermaslik uchun shu yerda to'xtaymiz\n"
                  '        await db_session.rollback()\n'
                  '        return\n'
                  '\n'
                  '    _, product_id, user_id = payment.invoice_payload.split(":")\n'
                  '    await grant_access(db_session, user_id=int(user_id), '
                  'product_id=int(product_id))\n'
                  '    await message.answer("To\'lovingiz uchun rahmat! Xizmat faollashtirildi.")\n'
                  '\n'
                  '\n'
                  'async def save_payment_record(db_session, *, charge_id: str, invoice_payload: '
                  'str, amount: int, currency: str):\n'
                  "    ...  # INSERT ... charge_id UNIQUE bo'lgan jadvalga\n"
                  '\n'
                  '\n'
                  'async def grant_access(db_session, *, user_id: int, product_id: int):\n'
                  '    ...  # foydalanuvchiga xizmatni yoqish\n'
                  '\n'
                  '\n'
                  '# --- Telegram Stars orqali invoice (raqamli tovar uchun) ---\n'
                  '@router.message(Command("buy_stars"))\n'
                  'async def cmd_buy_with_stars(message: Message):\n'
                  '    await message.bot.send_invoice(\n'
                  '        chat_id=message.chat.id,\n'
                  '        title="Premium obuna (1 oy)",\n'
                  '        description="Reklamasiz, cheksiz so\'rovlar",\n'
                  '        payload=f"stars_order:premium_1m:{message.from_user.id}",\n'
                  '        provider_token="",       # Stars uchun bo\'sh\n'
                  '        currency="XTR",\n'
                  '        prices=[LabeledPrice(label="Premium 1 oy", amount=100)],  # 100 Stars\n'
                  '    )\n'
                  '\n'
                  '\n'
                  "# --- Stars to'lovini qaytarish ---\n"
                  'async def refund_stars_payment(bot, user_id: int, charge_id: str) -> bool:\n'
                  '    """Faqat XTR (Stars) to\'lovlar uchun ishlaydi — fiat uchun provayder\n'
                  '    paneli/API orqali qaytariladi, bu metod orqali emas."""\n'
                  '    return await bot.refund_star_payment(user_id=user_id, '
                  'telegram_payment_charge_id=charge_id)',
  'code_content_ru': 'from aiogram import Router, F\n'
                     'from aiogram.filters import Command\n'
                     'from aiogram.types import Message, LabeledPrice\n'
                     'from sqlalchemy.exc import IntegrityError\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     '\n'
                     '@router.message(F.successful_payment)\n'
                     'async def handle_successful_payment(message: Message, db_session):\n'
                     '    payment = message.successful_payment\n'
                     '\n'
                     '    try:\n'
                     '        await save_payment_record(\n'
                     '            db_session,\n'
                     '            charge_id=payment.telegram_payment_charge_id,\n'
                     '            invoice_payload=payment.invoice_payload,\n'
                     '            amount=payment.total_amount,\n'
                     '            currency=payment.currency,\n'
                     '        )\n'
                     '    except IntegrityError:\n'
                     '        # charge_id столкнулся с UNIQUE-колонкой — это обновление уже '
                     'обработано,\n'
                     '        # чтобы не выдать услугу повторно, останавливаемся здесь\n'
                     '        await db_session.rollback()\n'
                     '        return\n'
                     '\n'
                     '    _, product_id, user_id = payment.invoice_payload.split(":")\n'
                     '    await grant_access(db_session, user_id=int(user_id), '
                     'product_id=int(product_id))\n'
                     '    await message.answer("Спасибо за оплату! Услуга активирована.")\n'
                     '\n'
                     '\n'
                     'async def save_payment_record(db_session, *, charge_id: str, '
                     'invoice_payload: str, amount: int, currency: str):\n'
                     '    ...  # INSERT в таблицу, где charge_id является UNIQUE\n'
                     '\n'
                     '\n'
                     'async def grant_access(db_session, *, user_id: int, product_id: int):\n'
                     '    ...  # включение услуги пользователю\n'
                     '\n'
                     '\n'
                     '# --- Invoice через Telegram Stars (для цифрового товара) ---\n'
                     '@router.message(Command("buy_stars"))\n'
                     'async def cmd_buy_with_stars(message: Message):\n'
                     '    await message.bot.send_invoice(\n'
                     '        chat_id=message.chat.id,\n'
                     '        title="Премиум-подписка (1 месяц)",\n'
                     '        description="Без рекламы, безлимитные запросы",\n'
                     '        payload=f"stars_order:premium_1m:{message.from_user.id}",\n'
                     '        provider_token="",       # для Stars — пусто\n'
                     '        currency="XTR",\n'
                     '        prices=[LabeledPrice(label="Премиум 1 месяц", amount=100)],  # 100 '
                     'Stars\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '# --- Возврат оплаты Stars ---\n'
                     'async def refund_stars_payment(bot, user_id: int, charge_id: str) -> bool:\n'
                     '    """Работает только для платежей XTR (Stars) — для фиата возврат '
                     'делается\n'
                     '    через панель/API провайдера, не через этот метод."""\n'
                     '    return await bot.refund_star_payment(user_id=user_id, '
                     'telegram_payment_charge_id=charge_id)',
  'task': {'task_title': "Amaliy: successful_payment'ni idempotent saqlang",
           'task_title_ru': 'Практика: сохраните successful_payment идемпотентно',
           'task_description': "successful_payment handler yozing: to'lov yozuvini "
                               "telegram_payment_charge_id bo'yicha UNIQUE ustunga saqlang, "
                               'takroriy update kelganda xizmatni ikkinchi marta bermang. Telegram '
                               "Stars orqali ham bitta oddiy invoice qo'shing.",
           'task_description_ru': 'Напишите обработчик successful_payment: сохраняйте запись '
                                  'платежа с UNIQUE-колонкой по telegram_payment_charge_id, при '
                                  'повторном обновлении не выдавайте услугу повторно. Добавьте '
                                  'также один простой invoice через Telegram Stars.',
           'task_requirements': "DB jadvalida charge_id UNIQUE bo'lishi; IntegrityError orqali "
                                'takrorlanishni aniqlash; kamida bitta XTR invoice namunasi.',
           'task_requirements_ru': 'В таблице БД charge_id должен быть UNIQUE; повтор должен '
                                   'определяться через IntegrityError; минимум один пример invoice '
                                   'с XTR.',
           'task_technologies': 'aiogram 3.x, SQLAlchemy async, Telegram Stars (XTR)',
           'task_deadline_days': 4},
  'sample': {'title': 'Namuna: idempotent successful_payment handler + Stars invoice',
             'description': "UNIQUE charge_id orqali takroriy to'lovni oldini oluvchi handler va "
                            'Stars bilan invoice',
             'sample_type': 'code',
             'code_files': [{'filename': 'successful_payment_handler.py',
                             'language': 'python',
                             'code': 'from aiogram import Router, F\n'
                                     'from aiogram.types import Message\n'
                                     'from sqlalchemy.exc import IntegrityError\n'
                                     '\n'
                                     'router = Router()\n'
                                     '\n'
                                     '\n'
                                     '@router.message(F.successful_payment)\n'
                                     'async def handle_successful_payment(message: Message, '
                                     'db_session):\n'
                                     '    payment = message.successful_payment\n'
                                     '    try:\n'
                                     '        await save_payment_record(db_session, '
                                     'payment.telegram_payment_charge_id)\n'
                                     '    except IntegrityError:\n'
                                     '        return\n'
                                     '    await message.answer("To\'lov muvaffaqiyatli qabul '
                                     'qilindi!")\n'
                                     '\n'
                                     '\n'
                                     'async def save_payment_record(db_session, charge_id: str):\n'
                                     '    ...  # charge_id UNIQUE ustunga INSERT'}]},
  'exercises': [{'title': 'refund_star_payment qamrovi',
                 'title_ru': 'Область действия refund_star_payment',
                 'description': "refund_star_payment metodi qaysi to'lovlar uchun ishlaydi?",
                 'description_ru': 'Для каких платежей работает метод refund_star_payment?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Faqat Telegram Stars (XTR) orqali to'langan xaridlar",
                             "Har qanday valyutadagi to'lovlar",
                             "Faqat UZS to'lovlari",
                             'Hech qanday, bunday metod mavjud emas'],
                 'options_ru': ['Только покупки, оплаченные Telegram Stars (XTR)',
                                'Платежи в любой валюте',
                                'Только платежи в UZS',
                                'Ни для каких, такого метода не существует'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Bu metod faqat Telegram'ning o'z ichki valyutasiga tegishli.",
                 'hint_ru': 'Этот метод относится только к собственной внутренней валюте Telegram.',
                 'explanation': "refund_star_payment faqat XTR (Stars) to'lovlarini qaytaradi; "
                                'fiat pul uchun provayder paneli kerak.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': "To'lovni noyob aniqlash maydoni",
                 'title_ru': 'Поле для уникальной идентификации платежа',
                 'description': "To'lovni Telegram tomonidan noyob aniqlash uchun ishlatiladigan "
                                'maydon: message.successful_payment.telegram_payment_charge____',
                 'description_ru': 'Поле для уникальной идентификации платежа со стороны Telegram: '
                                   'message.successful_payment.telegram_payment_charge____',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'id',
                 'hint': "So'z bu maydon nomining oxirida keladi.",
                 'hint_ru': 'Это слово стоит в конце названия поля.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Fiat pulni qaytarish qayerda amalga oshiriladi',
                 'title_ru': 'Где выполняется возврат фиатных денег',
                 'description': "Haqiqiy fiat (masalan UZS) to'lovini qaytarish odatda qayerda "
                                'amalga oshiriladi?',
                 'description_ru': 'Где обычно выполняется возврат реального фиатного (например, '
                                   'UZS) платежа?',
                 'exercise_type': 'multiple_choice',
                 'options': ["To'lov provayderining boshqaruv paneli yoki API'si orqali",
                             "Bot API'ning umumiy refund metodi orqali",
                             "Telegram administratori orqali qo'lda",
                             'Bu imkonsiz, fiat pul hech qachon qaytarilmaydi'],
                 'options_ru': ['Через панель управления или API платёжного провайдера',
                                'Через универсальный метод refund в Bot API',
                                'Вручную через администратора Telegram',
                                'Это невозможно, фиатные деньги никогда не возвращаются'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Pul aslida qaysi tomon hisobidan o'tganini eslang.",
                 'hint_ru': 'Вспомните, через чей счёт фактически проходят деньги.',
                 'explanation': "Bot API'da fiat uchun umumiy refund metodi yo'q — bu "
                                "provayderning o'z vositalari orqali bajariladi.",
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Idempotentlik nega muhim',
                 'title_ru': 'Почему важна идемпотентность',
                 'description': "successful_payment handler'da idempotentlik tekshiruvi nega "
                                'muhim? Qisqacha tushuntiring.',
                 'description_ru': 'Почему в обработчике successful_payment важна проверка '
                                   'идемпотентности? Кратко объясните.',
                 'exercise_type': 'text_input',
                 'expected_answer': "Telegram bir xil update'ni ba'zan qayta yuborishi mumkin "
                                    '(masalan tarmoq xatosi tufayli); agar handler tekshiruvsiz '
                                    "har safar xizmatni bersa, foydalanuvchi bitta to'lov evaziga "
                                    'bir necha marta xizmat olib qoladi — shuning uchun '
                                    'charge_id/invoice_payload UNIQUE sifatida saqlanib, takror '
                                    "kelgan update'da hech narsa qilinmasligi kerak.",
                 'hint': "Telegram update'larni qanday kafolat bilan yetkazishini eslang.",
                 'hint_ru': 'Вспомните, с какой гарантией Telegram доставляет обновления.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 4,
  'title': '5-Redis bilan FSM: gorizontal masshtablash',
  'title_ru': '5-FSM на Redis: горизонтальное масштабирование',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': '<h3>MemoryStorage nega gorizontal masshtablanmaydi</h3>\n'
                  '<p>48-kursda FSM bilan tanishganingizda, '
                  "<code>Dispatcher(storage=MemoryStorage())</code> yozib qo'yib, bu haqda ko'p "
                  "o'ylamagan bo'lishingiz mumkin — va bu to'g'ri, chunki bitta bot jarayoni uchun "
                  'u mukammal ishlaydi. Muammo boshqa yerda: <code>MemoryStorage</code> har bir '
                  "foydalanuvchining holatini (<code>state</code>) va vaqtinchalik ma'lumotini "
                  "(<code>data</code>) oddiy Python <code>dict</code>'da, aynan shu jarayonning "
                  'operativ xotirasida saqlaydi.</p>\n'
                  "<p>Bitta worker bilan bu sezilmaydi. Lekin botingiz o'sib, bitta webhook worker "
                  "yetarli bo'lmay qolganda — masalan, zero-downtime deploy uchun ikkita nusxa "
                  "parallel ishlashi kerak bo'lganda (13-darsda ko'ramiz), yoki shunchaki yukni "
                  "taqsimlash uchun — rasm boshqacha bo'ladi: foydalanuvchining birinchi xabari "
                  '1-workerga, ikkinchi xabari esa load balancer orqali 2-workerga tushishi '
                  'mumkin. 2-worker esa bu foydalanuvchi haqida <em>hech narsa bilmaydi</em> — '
                  'uning xotirasida bunday <code>chat_id</code> mavjud emas. Natija: FSM holati '
                  '"yo\'qoladi", foydalanuvchi to\'ldirayotgan anketa yoki buyurtma jarayoni '
                  "birinchi qadamga qaytadi yoki xatolik bilan to'xtaydi.</p>\n"
                  '\n'
                  '<h3>Yechim: umumiy tashqi xotira</h3>\n'
                  '<p>Yechim printsipial jihatdan oddiy — FSM holatini worker jarayonining ichida '
                  "emas, barcha workerlar ko'ra oladigan <strong>tashqi</strong> joyda saqlash "
                  'kerak. aiogram buning uchun <code>aiogram.fsm.storage.redis.RedisStorage</code> '
                  'klassini taqdim etadi. Eng muhim tafsilot: <code>FSMContext</code> orqali '
                  "ishlaydigan handler kodi <strong>butunlay o'zgarmaydi</strong> — "
                  '<code>state.set_state(...)</code>, <code>state.update_data(...)</code>, '
                  "<code>state.get_data()</code> xuddi avvalgidek chaqiriladi. O'zgaradigan narsa "
                  'faqat bitta qator: <code>Dispatcher</code> yaratilganda qaysi '
                  '<code>storage</code> uzatilishi.</p>\n'
                  '<pre class="mermaid">\n'
                  'flowchart LR\n'
                  '  U["Foydalanuvchi\n'
                  'chat_id=123"] -- "1-xabar: /order" --> W1["Worker #1\n'
                  '(webhook)"]\n'
                  '  W1 -- "state yozish\n'
                  'fsm:bot42:123:123" --> R[("Redis\n'
                  'umumiy FSM xotirasi")]\n'
                  '  U -- "2-xabar: mahsulot nomi" --> W2["Worker #2\n'
                  '(webhook)"]\n'
                  '  W2 -- "state o\'qish\n'
                  'fsm:bot42:123:123" --> R\n'
                  '  R -- "joriy holat: waiting_quantity" --> W2\n'
                  '  style R fill:#ffe9b3,stroke:#d09000\n'
                  '</pre>\n'
                  "<p>Diagramma aynan shu holatni ko'rsatadi: bitta foydalanuvchining ikkita "
                  'ketma-ket xabari ikkita xil workerga tushsa ham, ikkalasi bir xil Redis '
                  'kalitiga murojaat qilgani uchun FSM holati uzilmaydi.</p>\n'
                  '\n'
                  '<h3>Kalitlar qanday quriladi</h3>\n'
                  '<p><code>RedisStorage</code> har bir foydalanuvchi/chat juftligi uchun alohida '
                  'Redis kaliti yasaydi, odatda <code>fsm:{bot_id}:{chat_id}:{user_id}</code> '
                  "ko'rinishida. Kalitning aniq shakli <code>key_builder</code> parametri orqali "
                  'sozlanadi — masalan, <code>DefaultKeyBuilder(with_destiny=True)</code> holat '
                  "(<code>state</code>) va ma'lumotni (<code>data</code>) bitta kalitda "
                  "birlashtiradi, aks holda ular ikkita alohida kalitga bo'linadi. Qiymat ichida "
                  'JSON ko\'rinishida <code>{"state": "OrderForm:waiting_quantity", "data": '
                  '{"product": "noutbuk"}}</code> kabi tuzilma saqlanadi — shuning uchun '
                  "<code>redis-cli</code> orqali <code>GET fsm:...</code> buyrug'i bilan joriy "
                  "holatni jonli tekshirish mumkin, bu debugging paytida juda qo'l keladi.</p>\n"
                  '\n'
                  '<h3>TTL — holat abadiy saqlanmasligi kerak</h3>\n'
                  '<p>Foydalanuvchi anketani boshlab, yarmida tashlab ketishi mumkin. Agar holat '
                  'abadiy Redis\'da qolaversa, oy oxirida minglab "chala qolgan" kalit to\'planadi '
                  'va ular hech qachon tozalanmaydi. Shu sababli <code>RedisStorage</code> '
                  'konstruktoriga <code>state_ttl</code> va <code>data_ttl</code> (odatda '
                  '<code>timedelta</code> sifatida) berish tavsiya etiladi — belgilangan vaqtdan '
                  "so'ng Redis kalitni avtomatik o'chiradi, xuddi sessiya cookie muddati "
                  'kabi.</p>\n'
                  '\n'
                  '<h3>Operatsion xavf: Redis endi yagona nuqta</h3>\n'
                  "<p>MemoryStorage'dan RedisStorage'ga o'tish bitta muammoni yechib, boshqa "
                  'masalani ochadi: endi Redis ishdan chiqsa, <strong>barcha</strong> '
                  "workerlardagi FSM holati bir vaqtda yo'qoladi — bu avvalgidan ham kattaroq "
                  "nosozlik radiusi. Productionda buning uchun kamida: Redis'ning persistence "
                  'rejimini (RDB yoki AOF) yoqish, yoki boshqarilgan Redis xizmatidan (masalan, '
                  "bulutli provayder Redis'i) foydalanish tavsiya etiladi. Rate-limiting uchun "
                  "Redis'dan 8-darsda ham foydalanamiz — demak, bitta Redis instansi bir nechta "
                  "subsistema uchun umumiy infratuzilma bo'lib qoladi, uni monitoring qilish "
                  'shart.</p>\n'
                  '\n'
                  '<h3>Docker Compose bilan mahalliy sinov muhiti</h3>\n'
                  "<p>Rivojlantirish paytida Redis'ni alohida o'rnatishning hojati yo'q — "
                  "<code>docker-compose.yml</code>ga bitta <code>redis</code> xizmatini qo'shish "
                  "kifoya (namunada ko'rasiz). Bot konteyneri <code>redis://redis:6379/0</code> "
                  "manzili orqali unga ulanadi, chunki Docker tarmog'ida xizmat nomi "
                  '(<code>redis</code>) DNS sifatida ishlaydi.</p>',
  'text_content_ru': '<h3>Почему MemoryStorage не масштабируется горизонтально</h3>\n'
                     '<p>Когда вы знакомились с FSM в 48-м курсе, вы, возможно, просто писали '
                     '<code>Dispatcher(storage=MemoryStorage())</code> и не задумывались об этом '
                     'дальше — и это правильно, для одного процесса бота это работает отлично. '
                     'Проблема в другом: <code>MemoryStorage</code> хранит состояние '
                     '(<code>state</code>) и временные данные (<code>data</code>) каждого '
                     'пользователя в обычном Python <code>dict</code>, прямо в оперативной памяти '
                     'этого самого процесса.</p>\n'
                     '<p>С одним воркером это незаметно. Но когда ваш бот вырастает и одного '
                     'webhook-воркера становится мало — например, для zero-downtime деплоя нужно '
                     'параллельно держать две копии (разберём в 13-м уроке), или просто чтобы '
                     'распределить нагрузку — картина меняется: первое сообщение пользователя '
                     'может прийти на воркер №1, а второе через балансировщик нагрузки — на воркер '
                     '№2. Воркер №2 же <em>ничего не знает</em> об этом пользователе — в его '
                     'памяти нет такого <code>chat_id</code>. Итог: состояние FSM «теряется», '
                     'заполняемая пользователем анкета или процесс заказа откатывается к первому '
                     'шагу или падает с ошибкой.</p>\n'
                     '\n'
                     '<h3>Решение: общая внешняя память</h3>\n'
                     '<p>Решение принципиально простое — хранить состояние FSM не внутри процесса '
                     'воркера, а во <strong>внешнем</strong> месте, которое видят все воркеры. Для '
                     'этого aiogram предоставляет класс '
                     '<code>aiogram.fsm.storage.redis.RedisStorage</code>. Важная деталь: код '
                     'хендлеров, работающий через <code>FSMContext</code>, остаётся '
                     '<strong>полностью без изменений</strong> — '
                     '<code>state.set_state(...)</code>, <code>state.update_data(...)</code>, '
                     '<code>state.get_data()</code> вызываются точно так же, как раньше. Меняется '
                     'только одна строка: какой <code>storage</code> передаётся при создании '
                     '<code>Dispatcher</code>.</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart LR\n'
                     '  U["Пользователь\n'
                     'chat_id=123"] -- "1-е сообщение: /order" --> W1["Воркер №1\n'
                     '(webhook)"]\n'
                     '  W1 -- "запись state\n'
                     'fsm:bot42:123:123" --> R[("Redis\n'
                     'общая память FSM")]\n'
                     '  U -- "2-е сообщение: название товара" --> W2["Воркер №2\n'
                     '(webhook)"]\n'
                     '  W2 -- "чтение state\n'
                     'fsm:bot42:123:123" --> R\n'
                     '  R -- "текущее состояние: waiting_quantity" --> W2\n'
                     '  style R fill:#ffe9b3,stroke:#d09000\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает именно эту ситуацию: даже если два подряд идущих '
                     'сообщения одного пользователя попадают на разные воркеры, оба обращаются к '
                     'одному и тому же ключу Redis, поэтому состояние FSM не прерывается.</p>\n'
                     '\n'
                     '<h3>Как строятся ключи</h3>\n'
                     '<p><code>RedisStorage</code> создаёт отдельный ключ Redis для каждой пары '
                     'пользователь/чат, обычно в виде '
                     '<code>fsm:{bot_id}:{chat_id}:{user_id}</code>. Точный формат ключа '
                     'настраивается через параметр <code>key_builder</code> — например, '
                     '<code>DefaultKeyBuilder(with_destiny=True)</code> объединяет состояние '
                     '(<code>state</code>) и данные (<code>data</code>) в один ключ, иначе они '
                     'разделяются на два отдельных ключа. Внутри значения хранится структура в '
                     'формате JSON вида <code>{"state": "OrderForm:waiting_quantity", "data": '
                     '{"product": "noutbuk"}}</code> — поэтому текущее состояние можно живьём '
                     'посмотреть командой <code>GET fsm:...</code> через <code>redis-cli</code>, '
                     'что очень удобно при отладке.</p>\n'
                     '\n'
                     '<h3>TTL — состояние не должно храниться вечно</h3>\n'
                     '<p>Пользователь может начать заполнять анкету и бросить на середине. Если '
                     'состояние остаётся в Redis навсегда, к концу месяца накопятся тысячи '
                     '«недозаполненных» ключей, которые никогда не очистятся. Поэтому в '
                     'конструктор <code>RedisStorage</code> рекомендуется передавать '
                     '<code>state_ttl</code> и <code>data_ttl</code> (обычно как '
                     '<code>timedelta</code>) — по истечении заданного времени Redis автоматически '
                     'удаляет ключ, подобно сроку действия сессионной cookie.</p>\n'
                     '\n'
                     '<h3>Операционный риск: Redis теперь единая точка отказа</h3>\n'
                     '<p>Переход с MemoryStorage на RedisStorage решает одну проблему и открывает '
                     'другую: теперь при падении Redis состояние FSM пропадает сразу у '
                     '<strong>всех</strong> воркеров — это ещё больший радиус поражения, чем '
                     'раньше. В продакшене для этого как минимум рекомендуется: включить режим '
                     'персистентности Redis (RDB или AOF), либо использовать управляемый '
                     'Redis-сервис (например, Redis от облачного провайдера). Redis мы также '
                     'используем для rate-limiting в 8-м уроке — то есть один экземпляр Redis '
                     'становится общей инфраструктурой для нескольких подсистем, и его обязательно '
                     'нужно мониторить.</p>\n'
                     '\n'
                     '<h3>Локальная тестовая среда через Docker Compose</h3>\n'
                     '<p>Для разработки необязательно устанавливать Redis отдельно — достаточно '
                     'добавить один сервис <code>redis</code> в <code>docker-compose.yml</code> '
                     '(см. пример). Контейнер бота подключается к нему по адресу '
                     '<code>redis://redis:6379/0</code>, поскольку в сети Docker имя сервиса '
                     '(<code>redis</code>) работает как DNS.</p>',
  'code_content': "# storage.py -- MemoryStorage'dan RedisStorage'ga bitta o'zgarish bilan o'tish\n"
                  'from datetime import timedelta\n'
                  '\n'
                  'from aiogram import Bot, Dispatcher, F, Router\n'
                  'from aiogram.filters import StateFilter\n'
                  'from aiogram.fsm.context import FSMContext\n'
                  'from aiogram.fsm.state import State, StatesGroup\n'
                  'from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage\n'
                  'from aiogram.types import Message\n'
                  'from redis.asyncio import Redis\n'
                  '\n'
                  "# 1) Redis ulanishi -- bitta Redis, nechta bot worker bo'lishidan qat'i nazar\n"
                  'redis_client = Redis(host="redis", port=6379, db=0, decode_responses=True)\n'
                  '\n'
                  '# 2) with_destiny=True -- har bir foydalanuvchi uchun "state" va "data"\n'
                  '#    bitta Redis kalitida saqlanadi (fsm:{bot_id}:{chat_id}:{user_id}),\n'
                  "#    aks holda ular ikkita alohida kalitga bo'linadi.\n"
                  'key_builder = DefaultKeyBuilder(with_destiny=True)\n'
                  '\n'
                  'storage = RedisStorage(\n'
                  '    redis=redis_client,\n'
                  '    key_builder=key_builder,\n'
                  '    state_ttl=timedelta(hours=6),\n'
                  '    data_ttl=timedelta(hours=6),\n'
                  ')\n'
                  '\n'
                  "# 3) Dispatcher'ga faqat storage beriladi -- handler kodi BUTUNLAY o'zgarmaydi\n"
                  'dp = Dispatcher(storage=storage)\n'
                  'router = Router()\n'
                  'dp.include_router(router)\n'
                  '\n'
                  '\n'
                  'class OrderForm(StatesGroup):\n'
                  '    waiting_product = State()\n'
                  '    waiting_quantity = State()\n'
                  '\n'
                  '\n'
                  '@router.message(F.text == "/order")\n'
                  'async def start_order(message: Message, state: FSMContext) -> None:\n'
                  '    await state.set_state(OrderForm.waiting_product)\n'
                  '    await message.answer("Qaysi mahsulotni buyurtma qilmoqchisiz?")\n'
                  '\n'
                  '\n'
                  '@router.message(StateFilter(OrderForm.waiting_product))\n'
                  'async def product_chosen(message: Message, state: FSMContext) -> None:\n'
                  "    # Bu yozuv endi Redis'ga tushadi -- keyingi xabarni qaysi worker\n"
                  "    # qabul qilishidan qat'i nazar, holat bir xil ko'rinadi.\n"
                  '    await state.update_data(product=message.text)\n'
                  '    await state.set_state(OrderForm.waiting_quantity)\n'
                  '    await message.answer("Nechta dona kerak?")\n'
                  '\n'
                  '\n'
                  '@router.message(StateFilter(OrderForm.waiting_quantity))\n'
                  'async def quantity_chosen(message: Message, state: FSMContext) -> None:\n'
                  '    data = await state.get_data()\n'
                  '    await message.answer(\n'
                  '        f"Buyurtma qabul qilindi: {data[\'product\']} -- {message.text} dona"\n'
                  '    )\n'
                  '    await state.clear()\n'
                  '\n'
                  '\n'
                  'async def main() -> None:\n'
                  '    bot = Bot(token="BOT_TOKEN")\n'
                  '    await dp.start_polling(bot)\n'
                  '\n'
                  '\n'
                  '# --- Debugging: redis-cli orqali joriy holatni tekshirish ---\n'
                  '#   $ redis-cli\n'
                  '#   > KEYS fsm:*\n'
                  '#   1) "fsm:123456:123:123"\n'
                  '#   > GET fsm:123456:123:123\n'
                  '#   \'{"state": "OrderForm:waiting_quantity", "data": {"product": '
                  '"noutbuk"}}\'\n'
                  '#   > TTL fsm:123456:123:123\n'
                  '#   (integer) 21432   -- soniyalarda qolgan TTL\n',
  'code_content_ru': '# storage.py -- переход с MemoryStorage на RedisStorage одним изменением\n'
                     'from datetime import timedelta\n'
                     '\n'
                     'from aiogram import Bot, Dispatcher, F, Router\n'
                     'from aiogram.filters import StateFilter\n'
                     'from aiogram.fsm.context import FSMContext\n'
                     'from aiogram.fsm.state import State, StatesGroup\n'
                     'from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage\n'
                     'from aiogram.types import Message\n'
                     'from redis.asyncio import Redis\n'
                     '\n'
                     '# 1) Подключение к Redis -- один Redis, сколько бы воркеров бота ни было\n'
                     'redis_client = Redis(host="redis", port=6379, db=0, decode_responses=True)\n'
                     '\n'
                     '# 2) with_destiny=True -- для каждого пользователя "state" и "data"\n'
                     '#    хранятся в одном ключе Redis (fsm:{bot_id}:{chat_id}:{user_id}),\n'
                     '#    иначе они разделяются на два отдельных ключа.\n'
                     'key_builder = DefaultKeyBuilder(with_destiny=True)\n'
                     '\n'
                     'storage = RedisStorage(\n'
                     '    redis=redis_client,\n'
                     '    key_builder=key_builder,\n'
                     '    state_ttl=timedelta(hours=6),\n'
                     '    data_ttl=timedelta(hours=6),\n'
                     ')\n'
                     '\n'
                     '# 3) Dispatcher получает только storage -- код хендлеров НЕ меняется\n'
                     'dp = Dispatcher(storage=storage)\n'
                     'router = Router()\n'
                     'dp.include_router(router)\n'
                     '\n'
                     '\n'
                     'class OrderForm(StatesGroup):\n'
                     '    waiting_product = State()\n'
                     '    waiting_quantity = State()\n'
                     '\n'
                     '\n'
                     '@router.message(F.text == "/order")\n'
                     'async def start_order(message: Message, state: FSMContext) -> None:\n'
                     '    await state.set_state(OrderForm.waiting_product)\n'
                     '    await message.answer("Qaysi mahsulotni buyurtma qilmoqchisiz?")\n'
                     '\n'
                     '\n'
                     '@router.message(StateFilter(OrderForm.waiting_product))\n'
                     'async def product_chosen(message: Message, state: FSMContext) -> None:\n'
                     '    # Эта запись теперь попадает в Redis -- какой бы воркер ни принял\n'
                     '    # следующее сообщение, состояние будет видно одинаково.\n'
                     '    await state.update_data(product=message.text)\n'
                     '    await state.set_state(OrderForm.waiting_quantity)\n'
                     '    await message.answer("Nechta dona kerak?")\n'
                     '\n'
                     '\n'
                     '@router.message(StateFilter(OrderForm.waiting_quantity))\n'
                     'async def quantity_chosen(message: Message, state: FSMContext) -> None:\n'
                     '    data = await state.get_data()\n'
                     '    await message.answer(\n'
                     '        f"Buyurtma qabul qilindi: {data[\'product\']} -- {message.text} '
                     'dona"\n'
                     '    )\n'
                     '    await state.clear()\n'
                     '\n'
                     '\n'
                     'async def main() -> None:\n'
                     '    bot = Bot(token="BOT_TOKEN")\n'
                     '    await dp.start_polling(bot)\n'
                     '\n'
                     '\n'
                     '# --- Отладка: проверка текущего состояния через redis-cli ---\n'
                     '#   $ redis-cli\n'
                     '#   > KEYS fsm:*\n'
                     '#   1) "fsm:123456:123:123"\n'
                     '#   > GET fsm:123456:123:123\n'
                     '#   \'{"state": "OrderForm:waiting_quantity", "data": {"product": '
                     '"noutbuk"}}\'\n'
                     '#   > TTL fsm:123456:123:123\n'
                     '#   (integer) 21432   -- оставшийся TTL в секундах\n',
  'sample': {'title': "Namuna: Dispatcher'ni RedisStorage bilan sozlash + docker-compose",
             'description': 'Bitta bot konteyneri va bitta redis konteyneridan iborat mahalliy '
                            'sinov muhiti.',
             'sample_type': 'code',
             'code_files': [{'filename': 'docker-compose.yml',
                             'language': 'yaml',
                             'code': 'version: "3.9"\n'
                                     '\n'
                                     'services:\n'
                                     '  bot:\n'
                                     '    build: .\n'
                                     '    environment:\n'
                                     '      - BOT_TOKEN=${BOT_TOKEN}\n'
                                     '      - REDIS_URL=redis://redis:6379/0\n'
                                     '    depends_on:\n'
                                     '      - redis\n'
                                     '    restart: unless-stopped\n'
                                     '\n'
                                     '  redis:\n'
                                     '    image: redis:7-alpine\n'
                                     '    command: ["redis-server", "--appendonly", "yes"]\n'
                                     '    volumes:\n'
                                     '      - redis_data:/data\n'
                                     '    restart: unless-stopped\n'
                                     '\n'
                                     'volumes:\n'
                                     '  redis_data:\n'},
                            {'filename': 'bot_main.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'import os\n'
                                     '\n'
                                     'from aiogram import Bot, Dispatcher\n'
                                     'from aiogram.fsm.storage.redis import DefaultKeyBuilder, '
                                     'RedisStorage\n'
                                     'from redis.asyncio import Redis\n'
                                     '\n'
                                     'from handlers import router\n'
                                     '\n'
                                     '\n'
                                     'async def main() -> None:\n'
                                     '    redis_client = Redis.from_url(os.environ["REDIS_URL"], '
                                     'decode_responses=True)\n'
                                     '    storage = RedisStorage(redis=redis_client, '
                                     'key_builder=DefaultKeyBuilder(with_destiny=True))\n'
                                     '\n'
                                     '    bot = Bot(token=os.environ["BOT_TOKEN"])\n'
                                     '    dp = Dispatcher(storage=storage)\n'
                                     '    dp.include_router(router)\n'
                                     '\n'
                                     '    await dp.start_polling(bot)\n'
                                     '\n'
                                     '\n'
                                     'if __name__ == "__main__":\n'
                                     '    asyncio.run(main())\n'}]},
  'task': {'task_title': "Amaliy mashq: mavjud botni RedisStorage'ga o'tkazish",
           'task_title_ru': 'Практика: перевести существующего бота на RedisStorage',
           'task_description': '48-kurs capstone botingizdagi (yoki istalgan boshqa FSM '
                               "ishlatuvchi botingizdagi) MemoryStorage'ni RedisStorage'ga "
                               "almashtiring. Docker Compose orqali Redis'ni ishga tushiring, "
                               'state_ttl/data_ttl belgilang va redis-cli orqali FSM holatining '
                               "haqiqatan ham Redis'da saqlanayotganini tekshiring.",
           'task_description_ru': 'Замените MemoryStorage на RedisStorage в вашем боте-капстоуне '
                                  'из 48-го курса (или в любом другом боте с FSM). Запустите Redis '
                                  'через Docker Compose, задайте state_ttl/data_ttl и через '
                                  'redis-cli убедитесь, что состояние FSM действительно хранится в '
                                  'Redis.',
           'task_requirements': "RedisStorage.from_url yoki to'g'ridan-to'g'ri Redis klienti bilan "
                                "ulanish, state_ttl/data_ttl belgilangan bo'lishi, handler kodi "
                                "o'zgarmasligi, redis-cli orqali kamida bitta faol FSM kalitini "
                                "ko'rsatish.",
           'task_requirements_ru': 'Подключение через RedisStorage.from_url либо напрямую через '
                                   'клиент Redis, обязательно заданные state_ttl/data_ttl, код '
                                   'хендлеров не должен измениться, показать через redis-cli хотя '
                                   'бы один активный ключ FSM.',
           'task_technologies': 'aiogram 3.x, Redis, redis-py (redis.asyncio), Docker Compose',
           'task_deadline_days': 4},
  'exercises': [{'title': 'MemoryStorage muammosi',
                 'title_ru': 'Проблема MemoryStorage',
                 'description': 'Bir nechta bot worker ishlatilganda MemoryStorage nega muammo '
                                "tug'diradi?",
                 'description_ru': 'Почему MemoryStorage создаёт проблему при использовании '
                                   'нескольких воркеров бота?',
                 'exercise_type': 'multiple_choice',
                 'options': ["U holatni faqat o'zi ishlayotgan jarayon xotirasida saqlaydi, boshqa "
                             "workerlar uni ko'ra olmaydi",
                             "U juda sekin ishlaydi va so'rovlarni kechiktiradi",
                             'U faqat inline keyboard bilan ishlay oladi',
                             "U bitta vaqtning o'zida faqat bitta foydalanuvchi bilan ishlay "
                             'oladi'],
                 'options_ru': ['Она хранит состояние только в памяти своего процесса, другие '
                                'воркеры его не видят',
                                'Она работает слишком медленно и задерживает запросы',
                                'Она умеет работать только с inline-клавиатурой',
                                'Она может обслуживать только одного пользователя одновременно'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Muammo tezlikda emas, ma'lumot qayerda saqlanishida.",
                 'hint_ru': 'Проблема не в скорости, а в том, где хранятся данные.',
                 'explanation': "MemoryStorage holatni jarayonning RAM'ida saqlaydi; boshqa worker "
                                'jarayoni bu xotiraga kira olmaydi, shuning uchun foydalanuvchi '
                                "holati 'yo'qoladi'.",
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Redis storage klassi',
                 'title_ru': 'Класс хранилища Redis',
                 'description': "Bir nechta worker orasida FSM holatini almashish uchun aiogram'da "
                                '___ klassidan foydalaniladi (aiogram.fsm.storage.redis modulida).',
                 'description_ru': 'Для обмена состоянием FSM между несколькими воркерами в '
                                   'aiogram используется класс ___ (в модуле '
                                   'aiogram.fsm.storage.redis).',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'RedisStorage',
                 'hint': 'Modul nomi allaqachon javobga ishora qiladi.',
                 'hint_ru': 'Название модуля уже подсказывает ответ.',
                 'explanation': "aiogram.fsm.storage.redis.RedisStorage FSM holatini Redis'da "
                                'saqlaydi, shu bilan barcha worker jarayonlar uni umumiy manba '
                                "sifatida ko'radi.",
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Migratsiya qadamlari',
                 'title_ru': 'Шаги миграции',
                 'description': "MemoryStorage'dan RedisStorage'ga o'tish qadamlarini to'g'ri "
                                'tartibda joylashtiring.',
                 'description_ru': 'Расположите шаги перехода с MemoryStorage на RedisStorage в '
                                   'правильном порядке.',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Redis serverini ishga tushirish (masalan, docker-compose orqali)',
                                'RedisStorage obyektini yaratish (Redis ulanishi bilan)',
                                'Dispatcher(storage=...) ga uni uzatish',
                                "Handler kodini FSMContext orqali o'zgarishsiz qoldirish"],
                 'drag_items_ru': ['Запустить сервер Redis (например, через docker-compose)',
                                   'Создать объект RedisStorage (с подключением к Redis)',
                                   'Передать его в Dispatcher(storage=...)',
                                   'Оставить код хендлеров через FSMContext без изменений'],
                 'correct_order': ['Redis serverini ishga tushirish (masalan, docker-compose '
                                   'orqali)',
                                   'RedisStorage obyektini yaratish (Redis ulanishi bilan)',
                                   'Dispatcher(storage=...) ga uni uzatish',
                                   "Handler kodini FSMContext orqali o'zgarishsiz qoldirish"],
                 'hint': 'Avval infratuzilma, keyin ulanish, keyin ulash, oxirida — hech narsani '
                         'buzmaslik.',
                 'hint_ru': 'Сначала инфраструктура, потом подключение, потом связывание, и в '
                            'конце — ничего не ломать.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'state_ttl vazifasi',
                 'title_ru': 'Назначение state_ttl',
                 'description': "RedisStorage'da state_ttl parametrining vazifasi nima?",
                 'description_ru': 'Какова роль параметра state_ttl в RedisStorage?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Redis serveriga ulanish tezligini belgilaydi',
                             'Foydalanuvchi FSM holati necha vaqtdan keyin avtomatik '
                             "o'chirilishini belgilaydi",
                             'Bot tokenining amal qilish muddatini belgilaydi',
                             "Webhook so'rovi uchun timeout vaqtini belgilaydi"],
                 'options_ru': ['Определяет скорость подключения к серверу Redis',
                                'Определяет, через сколько времени состояние FSM пользователя '
                                'удалится автоматически',
                                'Определяет срок действия токена бота',
                                'Определяет таймаут для webhook-запроса'],
                 'correct_answers': 'B',
                 'is_multiple_select': False,
                 'hint': "TTL — 'time to live', ya'ni ma'lumot qancha vaqt yashashi.",
                 'hint_ru': 'TTL — «time to live», то есть сколько живут данные.',
                 'explanation': "state_ttl (va data_ttl) belgilangan vaqtdan so'ng Redis mos "
                                "kalitni avtomatik o'chiradi, shu bilan 'chala qolgan' FSM "
                                'holatlari abadiy saqlanib qolmaydi.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 5,
  'title': '6-Botlarni testlash: pytest bilan Update va Message mocklash',
  'title_ru': '6-Тестирование ботов: мокаем Update и Message с помощью pytest',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': "<h3>Nega handler'ni to'g'ridan-to'g'ri testlash noqulay</h3>\n"
                  "<p>aiogram handler'i odatda uchta narsaga bog'liq: haqiqiy <code>Bot</code> "
                  "obyekti (tarmoq so'rovi yuboradi), Telegram'dan kelgan "
                  "<code>Message</code>/<code>CallbackQuery</code> obyektlari va ba'zan tashqi "
                  "xizmatlar (baza, Redis). Agar testni to'g'ridan-to'g'ri shu handler ustida "
                  "yozsangiz, testingiz ham tarmoqqa, ham bazaga bog'liq bo'lib qoladi — bu sekin, "
                  'beqaror va CI\'da tez-tez "nosabab" muvaffaqiyatsiz bo\'ladigan testlarga olib '
                  'keladi.</p>\n'
                  "<p>Amaliy yechim — handler'larni <em>yupqa</em> qilib qoldirish: handler faqat "
                  "kiruvchi ma'lumotni o'qiydi, sof (aiogram'dan mustaqil) funksiyani chaqiradi va "
                  'natijani foydalanuvchiga qaytaradi. Aynan shu sof funksiyalar odatiy pytest '
                  "bilan, hech qanday aiogram/Telegram bog'liqligisiz test qilinadi. Handler'ning "
                  'o\'zi esa faqat "elim" qatlami sifatida qoladi va uni kamroq, lekin '
                  'integratsion darajadagi testlar bilan tekshiramiz.</p>\n'
                  '\n'
                  '<h3>Fake Message/User/Chat qurish</h3>\n'
                  "<p>aiogram 3.x'da barcha turlar (<code>Message</code>, <code>User</code>, "
                  '<code>Chat</code>, <code>Update</code> va h.k.) — bu pydantic modellari. Bu '
                  "degani, ularni testda haqiqiy Telegram serveridan kutmasdan, to'g'ridan-to'g'ri "
                  "qo'lda qurish mumkin — barcha majburiy maydonlarni berib, konstruktor "
                  "chaqiriladi (yoki validatsiyani chetlab o'tish kerak bo'lsa, "
                  '<code>Message.model_construct(...)</code>). Bu — testingizning "Arrange" '
                  '(tayyorlash) bosqichi: haqiqiy foydalanuvchi xabar yozganda aiogram nimani '
                  "qursa, xuddi shuni qo'lda yasaysiz.</p>\n"
                  '\n'
                  "<h3>Bot'ni AsyncMock bilan almashtirish</h3>\n"
                  "<p>Test paytida haqiqiy <code>Bot</code> orqali Telegram API'ga so'rov ketishi "
                  "shart emas — aksincha, bu xato: sekin, tarmoqqa bog'liq va haqiqiy chatlarga "
                  "xabar yuborib yuborishi mumkin. Buning o'rniga "
                  '<code>unittest.mock.AsyncMock(spec=Bot)</code> ishlatiladi: '
                  "<code>spec=Bot</code> mock'ni haqiqiy <code>Bot</code> klassi metodlari bilan "
                  "cheklaydi (mavjud bo'lmagan metodni chaqirsangiz, test darhol xato beradi), "
                  '<code>AsyncMock</code> esa <code>await bot.send_message(...)</code> kabi async '
                  "chaqiruvlarni to'g'ri qo'llab-quvvatlaydi. Test oxirida "
                  '<code>bot.send_message.assert_called_once_with(chat_id=123, text="...")</code> '
                  "orqali handler nima yuborganini tekshirasiz — haqiqiy tarmoq bo'lmasa ham.</p>\n"
                  '\n'
                  '<h3>Update\'ni Dispatcher orqali "oqizish"</h3>\n'
                  "<p>Faqat sof funksiyani emas, handler'ning o'zini ham (filtrlar, middleware'lar "
                  "ishlaganini) tekshirmoqchi bo'lsangiz, integratsion test kerak: qo'lda qurilgan "
                  '<code>Update</code> obyektini <code>await dp.feed_update(bot, update)</code> '
                  "orqali xuddi haqiqiy yangilanish kabi Dispatcher'ga uzatasiz. Dispatcher barcha "
                  "ro'yxatdan o'tgan filtr/middleware/handler zanjirini xuddi productionda "
                  "ishlaganidek bajaradi — farqi faqat <code>bot</code> o'rnida mock turgani.</p>\n"
                  '<pre class="mermaid">\n'
                  'flowchart LR\n'
                  '  A["Qo\'lda qurilgan\n'
                  'Update/Message"] --> B["dp.feed_update(bot, update)"]\n'
                  '  B --> C["Middleware zanjiri"]\n'
                  '  C --> D["Filtr mos keladigan\n'
                  'handler"]\n'
                  '  D --> E["bot.send_message(...)\n'
                  '(AsyncMock)"]\n'
                  '  E --> F["assert_called_once_with(...)"]\n'
                  '</pre>\n'
                  '<p>Bu diagramma test paytida qaysi qism <em>haqiqiy</em> (Dispatcher, '
                  'middleware, filtr, handler mantiqi) va qaysi qism <em>mock</em>langan (faqat '
                  "<code>Bot</code>) ekanini ko'rsatadi — aynan shu chegara testni ham ishonchli, "
                  'ham tez qiladi.</p>\n'
                  '\n'
                  "<h3>pytest-asyncio fixture'lari</h3>\n"
                  "<p>Har bir testda Dispatcher va mock Bot'ni qaytadan yozmaslik uchun ularni "
                  '<code>@pytest.fixture</code> qilib chiqarish tabiiy: bitta fixture toza '
                  '<code>Dispatcher</code> qaytaradi, boshqasi <code>AsyncMock(spec=Bot)</code> '
                  'qaytaradi. <code>pytest-asyncio</code> paketi <code>async def test_...()</code> '
                  "funksiyalarini to'g'ridan-to'g'ri ishga tushirish imkonini beradi "
                  '(<code>@pytest.mark.asyncio</code> yoki <code>asyncio_mode = "auto"</code> '
                  "sozlamasi bilan) — aiogram'ning o'zi ham to'liq asinxron bo'lgani uchun bu "
                  'tabiiy tanlov.</p>\n'
                  '\n'
                  "<h3>Middleware va filtr ta'sirini ham unutmang</h3>\n"
                  '<p><code>dp.feed_update</code> orqali test yozganda, real productiondagi kabi '
                  "ro'yxatdan o'tgan barcha middleware'lar (masalan, 6-darsda ko'rgan auth yoki "
                  "rate-limit middleware'lar) ham ishga tushadi. Bu ba'zan kutilmagan natijaga "
                  'olib keladi — masalan, test foydalanuvchisi rate-limit middleware tomonidan '
                  "bloklanib qolishi mumkin. Shu sababli testlarda ko'pincha sinov uchun alohida, "
                  '"yengil" middleware zanjiri yoki middleware\'larni vaqtincha o\'chirib '
                  'turadigan fixture ishlatiladi, aks holda testlar production konfiguratsiyasiga '
                  "bog'liq bo'lib, sabab-oqibat aloqasi tushunarsiz bo'lib qoladi.</p>\n"
                  '\n'
                  "<h3>Nima uchun bu barchasi CI'da muhim</h3>\n"
                  "<p>Bu testlar oddiy <code>pytest</code> buyrug'i bilan hech qanday Telegram "
                  'serveriga ulanmasdan, hech qanday haqiqiy botga xabar yubormasdan ishlaydi — '
                  "shuning uchun ularni GitHub Actions kabi CI quvurida har bir commit'da "
                  'avtomatik ishga tushirish xavfsiz va tez. Aynan shu xususiyat ularni haqiqiy '
                  "botga qarshi qo'lda tekshirishdan tubdan farqlaydi: qo'lda tekshirish sekin, "
                  'takrorlanmaydigan va unutilib qoladigan jarayon, avtomatik test esa har doim '
                  'bir xil natija beradigan, doimiy himoya qatlami.</p>',
  'text_content_ru': '<h3>Почему тестировать хендлер напрямую неудобно</h3>\n'
                     '<p>Хендлер aiogram обычно зависит от трёх вещей: реального объекта '
                     '<code>Bot</code> (отправляет сетевые запросы), объектов '
                     '<code>Message</code>/<code>CallbackQuery</code>, пришедших от Telegram, и '
                     'иногда внешних сервисов (БД, Redis). Если писать тест прямо поверх такого '
                     'хендлера, тест окажется завязан и на сеть, и на базу данных — это медленно, '
                     'нестабильно и приводит к тестам, которые в CI периодически падают «без '
                     'причины».</p>\n'
                     '<p>Практическое решение — держать хендлеры <em>тонкими</em>: хендлер только '
                     'читает входные данные, вызывает чистую (не зависящую от aiogram) функцию и '
                     'возвращает результат пользователю. Именно эти чистые функции тестируются '
                     'обычным pytest, без какой-либо зависимости от aiogram/Telegram. Сам хендлер '
                     'остаётся лишь «клеевым» слоем, и его проверяют реже, но зато интеграционными '
                     'тестами.</p>\n'
                     '\n'
                     '<h3>Строим фейковые Message/User/Chat</h3>\n'
                     '<p>В aiogram 3.x все типы (<code>Message</code>, <code>User</code>, '
                     '<code>Chat</code>, <code>Update</code> и т.д.) — это pydantic-модели. '
                     'Значит, их можно строить в тесте вручную, не дожидаясь настоящего сервера '
                     'Telegram — просто передав все обязательные поля в конструктор (либо, если '
                     'нужно обойти валидацию, через <code>Message.model_construct(...)</code>). '
                     'Это — этап «Arrange» (подготовка) вашего теста: вы вручную собираете ровно '
                     'то, что aiogram собрал бы сам, когда реальный пользователь пишет '
                     'сообщение.</p>\n'
                     '\n'
                     '<h3>Заменяем Bot на AsyncMock</h3>\n'
                     '<p>Во время теста реальный запрос к Telegram API через настоящий '
                     '<code>Bot</code> не нужен — более того, это ошибка: медленно, зависит от '
                     'сети и может реально отправить сообщение в чат. Вместо этого используется '
                     '<code>unittest.mock.AsyncMock(spec=Bot)</code>: <code>spec=Bot</code> '
                     'ограничивает мок методами настоящего класса <code>Bot</code> (вызов '
                     'несуществующего метода сразу даст ошибку теста), а <code>AsyncMock</code> '
                     'корректно поддерживает асинхронные вызовы вроде <code>await '
                     'bot.send_message(...)</code>. В конце теста через '
                     '<code>bot.send_message.assert_called_once_with(chat_id=123, '
                     'text="...")</code> вы проверяете, что именно отправил хендлер — без реальной '
                     'сети.</p>\n'
                     '\n'
                     '<h3>«Прогоняем» Update через Dispatcher</h3>\n'
                     '<p>Если нужно проверить не только чистую функцию, но и сам хендлер '
                     '(сработали ли фильтры, миддлвари), нужен интеграционный тест: вручную '
                     'собранный объект <code>Update</code> передаётся в Dispatcher через '
                     '<code>await dp.feed_update(bot, update)</code>, как будто это настоящее '
                     'обновление. Dispatcher выполняет всю зарегистрированную цепочку '
                     'фильтров/миддлварей/хендлеров точно так же, как в продакшене — разница лишь '
                     'в том, что вместо <code>bot</code> стоит мок.</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart LR\n'
                     '  A["Вручную собранный\n'
                     'Update/Message"] --> B["dp.feed_update(bot, update)"]\n'
                     '  B --> C["Цепочка миддлварей"]\n'
                     '  C --> D["Подходящий по фильтру\n'
                     'хендлер"]\n'
                     '  D --> E["bot.send_message(...)\n'
                     '(AsyncMock)"]\n'
                     '  E --> F["assert_called_once_with(...)"]\n'
                     '</pre>\n'
                     '<p>Эта диаграмма показывает, какая часть во время теста <em>настоящая</em> '
                     '(Dispatcher, миддлвари, фильтры, логика хендлера), а какая — '
                     '<em>замокана</em> (только <code>Bot</code>) — именно эта граница делает тест '
                     'одновременно надёжным и быстрым.</p>\n'
                     '\n'
                     '<h3>Фикстуры pytest-asyncio</h3>\n'
                     '<p>Чтобы не переписывать Dispatcher и мок Bot в каждом тесте заново, их '
                     'естественно вынести в <code>@pytest.fixture</code>: одна фикстура возвращает '
                     'чистый <code>Dispatcher</code>, другая — <code>AsyncMock(spec=Bot)</code>. '
                     'Пакет <code>pytest-asyncio</code> позволяет запускать функции <code>async '
                     'def test_...()</code> напрямую (через <code>@pytest.mark.asyncio</code> или '
                     'настройку <code>asyncio_mode = "auto"</code>) — поскольку сам aiogram '
                     'полностью асинхронный, это естественный выбор.</p>\n'
                     '\n'
                     '<h3>Не забывайте про влияние middleware и фильтров</h3>\n'
                     '<p>При тесте через <code>dp.feed_update</code> отрабатывают все '
                     'зарегистрированные middleware, точно как в продакшене (например, миддлвари '
                     'auth или rate-limit из 6-го урока курса 48). Иногда это приводит к '
                     'неожиданному результату — например, тестовый пользователь может оказаться '
                     'заблокирован middleware ограничения частоты запросов. Поэтому в тестах часто '
                     'используют отдельную, «облегчённую» цепочку middleware либо фикстуру, '
                     'временно отключающую middleware — иначе тесты окажутся завязаны на '
                     'продакшен-конфигурацию, и причинно-следственная связь перестанет быть '
                     'понятной.</p>\n'
                     '\n'
                     '<h3>Почему всё это важно для CI</h3>\n'
                     '<p>Эти тесты выполняются обычной командой <code>pytest</code>, не '
                     'подключаясь ни к какому серверу Telegram и не отправляя сообщений в реальный '
                     'чат — поэтому их безопасно и быстро запускать автоматически при каждом '
                     'коммите в пайплайне вроде GitHub Actions. Именно это принципиально отличает '
                     'их от ручной проверки на живом боте: ручная проверка — медленный, '
                     'неповторяемый и легко забываемый процесс, а автоматический тест — это всегда '
                     'одинаковый результат и постоянный слой защиты.</p>',
  'code_content': '# test_handlers.py -- hendlerlarni yupqa qilib, biznes-mantiqni alohida '
                  'testlash\n'
                  'from datetime import datetime\n'
                  'from unittest.mock import AsyncMock\n'
                  '\n'
                  'import pytest\n'
                  'from aiogram import Bot, Dispatcher, F, Router\n'
                  'from aiogram.types import Chat, Message, Update, User\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  '\n'
                  "# ---- 1) Sof biznes-mantiq -- aiogram'ga bog'liq emas, oddiy funksiya ----\n"
                  'def format_greeting(first_name: str) -> str:\n'
                  '    return f"Salom, {first_name}! Botga xush kelibsiz."\n'
                  '\n'
                  '\n'
                  "# ---- 2) Yupqa handler -- faqat o'qiydi, chaqiradi, javob beradi ----\n"
                  '@router.message(F.text == "/start")\n'
                  'async def start_handler(message: Message) -> None:\n'
                  '    text = format_greeting(message.from_user.first_name)\n'
                  '    await message.answer(text)\n'
                  '\n'
                  '\n'
                  "# ---- 3) pytest fixture'lari ----\n"
                  '@pytest.fixture\n'
                  'def dp() -> Dispatcher:\n'
                  '    d = Dispatcher()\n'
                  '    d.include_router(router)\n'
                  '    return d\n'
                  '\n'
                  '\n'
                  '@pytest.fixture\n'
                  'def bot() -> AsyncMock:\n'
                  '    return AsyncMock(spec=Bot)\n'
                  '\n'
                  '\n'
                  'def _make_update(text: str) -> Update:\n'
                  '    chat = Chat(id=123, type="private")\n'
                  '    user = User(id=42, is_bot=False, first_name="Aziz")\n'
                  '    message = Message(message_id=1, date=datetime.now(), chat=chat, '
                  'from_user=user, text=text)\n'
                  '    return Update(update_id=1, message=message)\n'
                  '\n'
                  '\n'
                  '# ---- 4a) Sof funksiyani testlash -- aiogram umuman ishtirok etmaydi ----\n'
                  'def test_format_greeting() -> None:\n'
                  '    assert format_greeting("Aziz") == "Salom, Aziz! Botga xush kelibsiz."\n'
                  '\n'
                  '\n'
                  "# ---- 4b) Integratsion test -- Dispatcher orqali to'liq zanjirni tekshirish "
                  '----\n'
                  '@pytest.mark.asyncio\n'
                  'async def test_start_handler_replies(dp: Dispatcher, bot: AsyncMock) -> None:\n'
                  '    update = _make_update("/start")\n'
                  '\n'
                  '    await dp.feed_update(bot, update)\n'
                  '\n'
                  '    bot.send_message.assert_called_once_with(\n'
                  '        chat_id=123, text="Salom, Aziz! Botga xush kelibsiz."\n'
                  '    )\n'
                  '\n'
                  '\n'
                  '# ---- 5) pytest.ini / pyproject.toml sozlamasi (izoh sifatida) ----\n'
                  '# [tool.pytest.ini_options]\n'
                  '# asyncio_mode = "auto"\n'
                  '# testpaths = ["tests"]\n'
                  '#\n'
                  "# Shu sozlama bilan @pytest.mark.asyncio har bir testga qo'lda yozilmaydi --\n"
                  '# pytest-asyncio barcha "async def test_..." funksiyalarni avtomatik taniydi.\n',
  'code_content_ru': '# test_handlers.py -- тонкие хендлеры, бизнес-логика тестируется отдельно\n'
                     'from datetime import datetime\n'
                     'from unittest.mock import AsyncMock\n'
                     '\n'
                     'import pytest\n'
                     'from aiogram import Bot, Dispatcher, F, Router\n'
                     'from aiogram.types import Chat, Message, Update, User\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     '\n'
                     '# ---- 1) Чистая бизнес-логика -- не зависит от aiogram, обычная функция '
                     '----\n'
                     'def format_greeting(first_name: str) -> str:\n'
                     '    return f"Salom, {first_name}! Botga xush kelibsiz."\n'
                     '\n'
                     '\n'
                     '# ---- 2) Тонкий хендлер -- только читает, вызывает, отвечает ----\n'
                     '@router.message(F.text == "/start")\n'
                     'async def start_handler(message: Message) -> None:\n'
                     '    text = format_greeting(message.from_user.first_name)\n'
                     '    await message.answer(text)\n'
                     '\n'
                     '\n'
                     '# ---- 3) Фикстуры pytest ----\n'
                     '@pytest.fixture\n'
                     'def dp() -> Dispatcher:\n'
                     '    d = Dispatcher()\n'
                     '    d.include_router(router)\n'
                     '    return d\n'
                     '\n'
                     '\n'
                     '@pytest.fixture\n'
                     'def bot() -> AsyncMock:\n'
                     '    return AsyncMock(spec=Bot)\n'
                     '\n'
                     '\n'
                     'def _make_update(text: str) -> Update:\n'
                     '    chat = Chat(id=123, type="private")\n'
                     '    user = User(id=42, is_bot=False, first_name="Aziz")\n'
                     '    message = Message(message_id=1, date=datetime.now(), chat=chat, '
                     'from_user=user, text=text)\n'
                     '    return Update(update_id=1, message=message)\n'
                     '\n'
                     '\n'
                     '# ---- 4a) Тест чистой функции -- aiogram вообще не участвует ----\n'
                     'def test_format_greeting() -> None:\n'
                     '    assert format_greeting("Aziz") == "Salom, Aziz! Botga xush kelibsiz."\n'
                     '\n'
                     '\n'
                     '# ---- 4b) Интеграционный тест -- проверка всей цепочки через Dispatcher '
                     '----\n'
                     '@pytest.mark.asyncio\n'
                     'async def test_start_handler_replies(dp: Dispatcher, bot: AsyncMock) -> '
                     'None:\n'
                     '    update = _make_update("/start")\n'
                     '\n'
                     '    await dp.feed_update(bot, update)\n'
                     '\n'
                     '    bot.send_message.assert_called_once_with(\n'
                     '        chat_id=123, text="Salom, Aziz! Botga xush kelibsiz."\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '# ---- 5) настройка pytest.ini / pyproject.toml (в виде комментария) ----\n'
                     '# [tool.pytest.ini_options]\n'
                     '# asyncio_mode = "auto"\n'
                     '# testpaths = ["tests"]\n'
                     '#\n'
                     '# С этой настройкой @pytest.mark.asyncio не нужно писать вручную для\n'
                     '# каждого теста -- pytest-asyncio сам распознаёт все "async def test_...".\n',
  'sample': {'title': 'Namuna: CallbackQuery uchun integratsion test',
             'description': "Inline tugma bosilganda ishlaydigan handler'ni feed_update orqali "
                            'testlash.',
             'sample_type': 'code',
             'code_files': [{'filename': 'test_callback_handler.py',
                             'language': 'python',
                             'code': '# test_callback_handler.py -- CallbackQuery uchun namuna '
                                     'test\n'
                                     'from datetime import datetime\n'
                                     'from unittest.mock import AsyncMock\n'
                                     '\n'
                                     'import pytest\n'
                                     'from aiogram import Bot, Dispatcher, F, Router\n'
                                     'from aiogram.types import CallbackQuery, Chat, Message, '
                                     'Update, User\n'
                                     '\n'
                                     'router = Router()\n'
                                     '\n'
                                     '\n'
                                     '@router.callback_query(F.data == "confirm_order")\n'
                                     'async def confirm_order_handler(callback: CallbackQuery) -> '
                                     'None:\n'
                                     '    await callback.answer("Buyurtma tasdiqlandi!")\n'
                                     '    await callback.message.edit_text("Holat: tasdiqlandi")\n'
                                     '\n'
                                     '\n'
                                     '@pytest.fixture\n'
                                     'def dp() -> Dispatcher:\n'
                                     '    d = Dispatcher()\n'
                                     '    d.include_router(router)\n'
                                     '    return d\n'
                                     '\n'
                                     '\n'
                                     '@pytest.fixture\n'
                                     'def bot() -> AsyncMock:\n'
                                     '    return AsyncMock(spec=Bot)\n'
                                     '\n'
                                     '\n'
                                     'def _make_callback_update() -> Update:\n'
                                     '    chat = Chat(id=123, type="private")\n'
                                     '    user = User(id=42, is_bot=False, first_name="Aziz")\n'
                                     '    message = Message(\n'
                                     '        message_id=5, date=datetime.now(), chat=chat, '
                                     'from_user=user, text="Buyurtma: 2 dona"\n'
                                     '    )\n'
                                     '    callback = CallbackQuery(\n'
                                     '        id="cb1", from_user=user, chat_instance="x", '
                                     'data="confirm_order", message=message\n'
                                     '    )\n'
                                     '    return Update(update_id=2, callback_query=callback)\n'
                                     '\n'
                                     '\n'
                                     '@pytest.mark.asyncio\n'
                                     'async def test_confirm_order_answers_and_edits(dp: '
                                     'Dispatcher, bot: AsyncMock) -> None:\n'
                                     '    update = _make_callback_update()\n'
                                     '\n'
                                     '    await dp.feed_update(bot, update)\n'
                                     '\n'
                                     '    bot.answer_callback_query.assert_called_once()\n'
                                     '    bot.edit_message_text.assert_called_once()\n'}]},
  'task': {'task_title': "Amaliy mashq: handler'larni yupqa qilib qayta yozish va test qo'shish",
           'task_title_ru': 'Практика: сделать хендлеры тонкими и добавить тесты',
           'task_description': "O'zingizning avvalgi botingizdan (yoki 48-kurs capstone botidan) "
                               'kamida ikkita handler tanlang. Ularni yupqa qilib qayta yozing — '
                               "biznes-mantiqni alohida sof funksiyalarga chiqaring, so'ngra shu "
                               "funksiyalar uchun pytest unit testlar, handler'lar uchun esa "
                               'dp.feed_update orqali integratsion testlar yozing.',
           'task_description_ru': 'Выберите как минимум два хендлера из своего предыдущего бота '
                                  '(или капстоуна 48-го курса). Перепишите их так, чтобы они стали '
                                  'тонкими — вынесите бизнес-логику в отдельные чистые функции, '
                                  'затем напишите для этих функций unit-тесты на pytest, а для '
                                  'хендлеров — интеграционные тесты через dp.feed_update.',
           'task_requirements': 'Kamida 2 ta sof funksiya uchun unit test, kamida 2 ta handler '
                                'uchun AsyncMock(spec=Bot) va dp.feed_update orqali integratsion '
                                'test, pytest-asyncio ishlatilishi kerak.',
           'task_requirements_ru': 'Минимум 2 unit-теста для чистых функций, минимум 2 '
                                   'интеграционных теста для хендлеров через AsyncMock(spec=Bot) и '
                                   'dp.feed_update, обязательно использовать pytest-asyncio.',
           'task_technologies': 'aiogram 3.x, pytest, pytest-asyncio, unittest.mock.AsyncMock',
           'task_deadline_days': 4},
  'exercises': [{'title': 'Yupqa handler sababi',
                 'title_ru': 'Причина тонких хендлеров',
                 'description': "Nega handler'larni 'yupqa' qilib yozish tavsiya etiladi?",
                 'description_ru': 'Почему рекомендуется делать хендлеры «тонкими»?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Chunki shunda biznes-mantiqni aiogram'siz, oddiy pytest bilan tez va "
                             'barqaror test qilish mumkin',
                             'Chunki Telegram Bot API buni majburiy talab qiladi',
                             'Chunki yupqa handler tarmoq orqali tezroq javob beradi',
                             'Chunki shunda kod fayli kamroq joy egallaydi'],
                 'options_ru': ['Потому что так бизнес-логику можно быстро и стабильно тестировать '
                                'обычным pytest, без aiogram',
                                'Потому что этого обязательно требует Telegram Bot API',
                                'Потому что тонкий хендлер быстрее отвечает по сети',
                                'Потому что так файл кода занимает меньше места'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Javobni test yozish qulayligi nuqtai nazaridan o'ylab ko'ring.",
                 'hint_ru': 'Подумайте с точки зрения удобства написания тестов.',
                 'explanation': 'Yupqa handler biznes-mantiqni sof funksiyalarga ajratadi, shu '
                                "funksiyalar esa hech qanday aiogram/tarmoq bog'liqligisiz oddiy "
                                'pytest bilan tez testlanadi.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Bot mocklash',
                 'title_ru': 'Мокирование Bot',
                 'description': 'Bot obyektini haqiqiy tarmoqqa murojaat qilmasdan testlash uchun '
                                "unittest.mock'dan ___(spec=Bot) ishlatiladi.",
                 'description_ru': 'Для тестирования объекта Bot без реального сетевого запроса из '
                                   'unittest.mock используется ___(spec=Bot).',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'AsyncMock',
                 'hint': "Bot metodlari async bo'lgani uchun oddiy Mock yetarli emas.",
                 'hint_ru': 'Методы Bot асинхронные, поэтому обычного Mock недостаточно.',
                 'explanation': 'AsyncMock(spec=Bot) — Bot klassining metodlariga mos, await bilan '
                                'chaqiriladigan mock obyekt yaratadi.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Integratsion test qadamlari',
                 'title_ru': 'Шаги интеграционного теста',
                 'description': "Handler'ni Dispatcher orqali testlash qadamlarini to'g'ri "
                                'tartibda joylashtiring.',
                 'description_ru': 'Расположите шаги тестирования хендлера через Dispatcher в '
                                   'правильном порядке.',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ["Update/Message obyektini qo'lda qurish",
                                'AsyncMock(spec=Bot) yaratish',
                                'dp.feed_update(bot, update) orqali yuborish',
                                'bot.send_message.assert_called_once_with(...) bilan tekshirish'],
                 'drag_items_ru': ['Вручную собрать объект Update/Message',
                                   'Создать AsyncMock(spec=Bot)',
                                   'Отправить через dp.feed_update(bot, update)',
                                   'Проверить через bot.send_message.assert_called_once_with(...)'],
                 'correct_order': ["Update/Message obyektini qo'lda qurish",
                                   'AsyncMock(spec=Bot) yaratish',
                                   'dp.feed_update(bot, update) orqali yuborish',
                                   'bot.send_message.assert_called_once_with(...) bilan '
                                   'tekshirish'],
                 'hint': "Klassik Arrange - Act - Assert tartibini eslang, faqat 'Arrange' ikkita "
                         "qadamga bo'lingan.",
                 'hint_ru': 'Вспомните классический порядок Arrange - Act - Assert, только '
                            '«Arrange» разбит на два шага.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 6,
  'title': "R1-Takrorlash: Mini App, xavfsizlik va real to'lovlar",
  'title_ru': 'R1-Повторение: Mini App, безопасность и реальные платежи',
  'points_reward': 13,
  'code_language': 'python',
  'text_content': '<h3>Bu — takrorlash darsi</h3>\n'
                  "<p>Bu darsda yangi mavzu yo'q — 1—5-darslarda (Mini App, uning xavfsizligi va "
                  "real to'lovlar) o'rganilganlarni bitta amaliy zanjirga bog'laymiz. 6-dars "
                  "(botlarni testlash) bu sintezga kirmaydi — u alohida yo'nalish bo'lib, undan "
                  'keyingi darslarda ham foydalanasiz.</p>\n'
                  "<p>Uch qismning bir-biriga qanday ulanishini eslab o'tamiz: foydalanuvchi bot "
                  'xabaridagi <code>web_app</code> tugmasini bosadi, Mini App ochiladi, u '
                  "Telegram'dan olgan <code>initData</code>ni sizning backend'ingizga yuboradi. "
                  "Backend uni HMAC-SHA256 orqali tekshiradi — imzo mos kelmasa, so'rov rad "
                  "etiladi. Imzo to'g'ri bo'lsa, endi siz ushbu foydalanuvchi haqiqatan ham "
                  'Telegram orqali kirganiga ishonch bilan buyurtma yaratasiz va '
                  "<code>send_invoice</code> chaqirasiz. Foydalanuvchi to'lovni tasdiqlaganda, "
                  'Telegram avval <code>pre_checkout_query</code> yuboradi — bot uni 10 soniya '
                  "ichida tasdiqlaydi — so'ng <code>successful_payment</code> keladi, va "
                  'shundagina siz buyurtmani "to\'langan" deb belgilaysiz.</p>\n'
                  '\n'
                  '<h3>Nega tartib muhim</h3>\n'
                  "<p>Bu zanjirda ikkita qoida buzilsa, xavfsizlik teshigi paydo bo'ladi: "
                  "birinchisi — <code>initData</code>ni tekshirmasdan foydalanuvchi ID'siga "
                  "ishonish, bu orqali istalgan kishi o'zini boshqa foydalanuvchi qilib "
                  "ko'rsatishi mumkin; ikkinchisi — <code>pre_checkout_query</code>ni "
                  'tasdiqlashdan oldin narx/mahsulot mavjudligini serverda qayta tekshirmaslik. '
                  "Mijoz tomonidan yuborilgan narxga hech qachon ishonmang, faqat backend'dagi "
                  'haqiqiy narxni ishlating.</p>\n'
                  '\n'
                  "<h3>Xatolar qayerda ko'proq uchraydi</h3>\n"
                  '<table>\n'
                  "<tr><th>Qadam</th><th>Odatiy xato</th><th>To'g'ri yondashuv</th></tr>\n"
                  "<tr><td>initData tekshiruvi</td><td>Faqat frontendda tekshirish (JS'ni "
                  "o'zgartirish oson)</td><td>Backend'da HMAC-SHA256 bilan majburiy "
                  'tekshirish</td></tr>\n'
                  "<tr><td>Invoice yaratish</td><td>Narxni mijozdan (Mini App'dan) qabul "
                  'qilish</td><td>Narxni faqat serverdagi mahsulot bazasidan olish</td></tr>\n'
                  '<tr><td>pre_checkout_query</td><td>10 soniyadan kech javob berish yoki umuman '
                  'javob bermaslik</td><td>Darhol tekshirib, ok=True/False bilan javob '
                  'qaytarish</td></tr>\n'
                  '</table>\n'
                  '\n'
                  '<h3>Amaliy loyihada nima kutilmoqda</h3>\n'
                  '<p>Quyidagi vazifada uchala qismni birlashtirgan kichik xususiyat yasaysiz: '
                  "Mini App orqali mahsulot tanlash, initData'ni backend'da tasdiqlash, so'ng shu "
                  'tasdiqlangan foydalanuvchi nomidan real invoys yuborish. Bu — 13-darsdagi katta '
                  "capstone'ning kichik prototipi, shuning uchun uni endi puxta qilib bajarish "
                  'keyingi ishni ancha osonlashtiradi.</p>\n'
                  "<p>E'tibor bering: bu yerda hali Redis FSM (5-dars) ishlatilishi shart emas — "
                  "kichik prototip uchun oddiy in-memory FSM ham yetarli. Redis'ga o'tish faqat "
                  "bot bir nechta worker'da ishlay boshlaganda haqiqiy zarurat bo'ladi, bu esa "
                  "13-dars capstone'ida to'liq talab qilinadi.</p>",
  'text_content_ru': '<h3>Это — урок повторения</h3>\n'
                     '<p>В этом уроке нет новой темы — мы связываем в одну практическую цепочку '
                     'то, что изучили в уроках 1—5 (Mini App, его безопасность и реальные '
                     'платежи). Урок 6 (тестирование ботов) в этот синтез не входит — это '
                     'отдельное направление, которое вы будете использовать и дальше.</p>\n'
                     '<p>Вспомним, как три части связаны друг с другом: пользователь нажимает '
                     'кнопку <code>web_app</code> в сообщении бота, открывается Mini App, который '
                     'отправляет полученный от Telegram <code>initData</code> на ваш бэкенд. '
                     'Бэкенд проверяет его через HMAC-SHA256 — если подпись не совпадает, запрос '
                     'отклоняется. Если подпись верна, теперь вы с уверенностью создаёте заказ от '
                     'имени этого пользователя, который действительно вошёл через Telegram, и '
                     'вызываете <code>send_invoice</code>. Когда пользователь подтверждает оплату, '
                     'Telegram сначала отправляет <code>pre_checkout_query</code> — бот '
                     'подтверждает его в течение 10 секунд — затем приходит '
                     '<code>successful_payment</code>, и только тогда вы помечаете заказ как '
                     '«оплачен».</p>\n'
                     '\n'
                     '<h3>Почему порядок важен</h3>\n'
                     '<p>Если в этой цепочке нарушить два правила, появится дыра в безопасности: '
                     'первое — доверять ID пользователя без проверки <code>initData</code>, из-за '
                     'чего кто угодно может выдать себя за другого пользователя; второе — не '
                     'перепроверять на сервере цену/наличие товара перед подтверждением '
                     '<code>pre_checkout_query</code>. Никогда не доверяйте цене, присланной '
                     'клиентом, используйте только реальную цену из бэкенда.</p>\n'
                     '\n'
                     '<h3>Где чаще всего встречаются ошибки</h3>\n'
                     '<table>\n'
                     '<tr><th>Шаг</th><th>Типичная ошибка</th><th>Правильный подход</th></tr>\n'
                     '<tr><td>Проверка initData</td><td>Проверка только на фронтенде (JS легко '
                     'изменить)</td><td>Обязательная проверка на бэкенде через '
                     'HMAC-SHA256</td></tr>\n'
                     '<tr><td>Создание invoice</td><td>Принимать цену от клиента (из Mini '
                     'App)</td><td>Брать цену только из серверной базы товаров</td></tr>\n'
                     '<tr><td>pre_checkout_query</td><td>Отвечать позже 10 секунд или вообще не '
                     'отвечать</td><td>Сразу проверить и ответить через ok=True/False</td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Что ожидается в практическом проекте</h3>\n'
                     '<p>В задании ниже вы соберёте небольшую функцию, объединяющую все три части: '
                     'выбор товара через Mini App, проверку initData на бэкенде и отправку '
                     'реального инвойса от имени подтверждённого пользователя. Это — маленький '
                     'прототип большого капстоуна из 13-го урока, поэтому, сделав это сейчас '
                     'качественно, вы сильно облегчите себе дальнейшую работу.</p>\n'
                     '<p>Обратите внимание: здесь ещё не обязательно использовать Redis FSM (урок '
                     '5) — для маленького прототипа достаточно и обычного FSM в памяти. Переход на '
                     'Redis становится реально необходим только тогда, когда бот начинает работать '
                     'в нескольких воркерах, а это уже полноценное требование капстоуна 13-го '
                     'урока.</p>',
  'code_content': '# review_flow.py -- Mini App + initData + Payments -- bitta qisqa zanjir\n'
                  'from aiogram import Bot, F, Router\n'
                  'from aiogram.types import Message\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  "# To'liq HMAC-SHA256 validatsiya kodi 2-darsda berilgan edi -- bu yerda\n"
                  "# faqat uning oqim ichidagi o'rni ko'rsatilgan.\n"
                  'from security import verify_init_data  # 2-darsdagi funksiya\n'
                  '\n'
                  '\n'
                  'async def handle_mini_app_order(bot: Bot, chat_id: int, init_data: str, '
                  'product_id: str) -> None:\n'
                  '    user = verify_init_data(init_data, bot_token=bot.token)\n'
                  '    if user is None:\n'
                  '        raise PermissionError("initData yaroqsiz -- so\'rov rad etildi")\n'
                  '\n'
                  '    price = get_real_price(product_id)  # faqat serverdagi narx, mijozdan emas\n'
                  '    await bot.send_invoice(\n'
                  '        chat_id=chat_id,\n'
                  '        title="Buyurtma",\n'
                  '        description=f"Mahsulot #{product_id}",\n'
                  '        payload=f"order:{user[\'id\']}:{product_id}",\n'
                  '        provider_token="PROVIDER_TOKEN",\n'
                  '        currency="UZS",\n'
                  '        prices=[{"label": "Narx", "amount": price}],\n'
                  '    )\n'
                  '\n'
                  '\n'
                  '@router.pre_checkout_query()\n'
                  'async def confirm_pre_checkout(pre_checkout_query) -> None:\n'
                  '    await pre_checkout_query.answer(ok=True)\n'
                  '\n'
                  '\n'
                  '@router.message(F.successful_payment)\n'
                  'async def mark_order_paid(message: Message) -> None:\n'
                  '    payload = message.successful_payment.invoice_payload\n'
                  '    mark_paid_in_db(payload, '
                  'charge_id=message.successful_payment.telegram_payment_charge_id)\n',
  'code_content_ru': '# review_flow.py -- Mini App + initData + Payments -- одна короткая цепочка\n'
                     'from aiogram import Bot, F, Router\n'
                     'from aiogram.types import Message\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     '# Полный код валидации HMAC-SHA256 был дан во 2-м уроке -- здесь\n'
                     '# показано только его место внутри всей цепочки.\n'
                     'from security import verify_init_data  # функция из 2-го урока\n'
                     '\n'
                     '\n'
                     'async def handle_mini_app_order(bot: Bot, chat_id: int, init_data: str, '
                     'product_id: str) -> None:\n'
                     '    user = verify_init_data(init_data, bot_token=bot.token)\n'
                     '    if user is None:\n'
                     '        raise PermissionError("initData недействителен -- запрос отклонён")\n'
                     '\n'
                     '    price = get_real_price(product_id)  # только серверная цена, не от '
                     'клиента\n'
                     '    await bot.send_invoice(\n'
                     '        chat_id=chat_id,\n'
                     '        title="Buyurtma",\n'
                     '        description=f"Mahsulot #{product_id}",\n'
                     '        payload=f"order:{user[\'id\']}:{product_id}",\n'
                     '        provider_token="PROVIDER_TOKEN",\n'
                     '        currency="UZS",\n'
                     '        prices=[{"label": "Narx", "amount": price}],\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '@router.pre_checkout_query()\n'
                     'async def confirm_pre_checkout(pre_checkout_query) -> None:\n'
                     '    await pre_checkout_query.answer(ok=True)\n'
                     '\n'
                     '\n'
                     '@router.message(F.successful_payment)\n'
                     'async def mark_order_paid(message: Message) -> None:\n'
                     '    payload = message.successful_payment.invoice_payload\n'
                     '    mark_paid_in_db(payload, '
                     'charge_id=message.successful_payment.telegram_payment_charge_id)\n',
  'sample': {'title': 'Namuna: Mini App + initData + Payments birlashtirilgan oqim',
             'description': "Uchala mavzuni bitta ish jarayonida ko'rsatuvchi qisqa, sintez "
                            'namunasi.',
             'sample_type': 'code',
             'code_files': [{'filename': 'webapp_checkout.html',
                             'language': 'html',
                             'code': '<!DOCTYPE html>\n'
                                     '<html>\n'
                                     '<head><meta name="viewport" content="width=device-width, '
                                     'initial-scale=1"></head>\n'
                                     '<body>\n'
                                     '  <button id="buy">Buyurtma berish</button>\n'
                                     '  <script '
                                     'src="https://telegram.org/js/telegram-web-app.js"></script>\n'
                                     '  <script>\n'
                                     '    const tg = window.Telegram.WebApp;\n'
                                     '    tg.ready();\n'
                                     '    document.getElementById("buy").addEventListener("click", '
                                     'async () => {\n'
                                     '      await fetch("/api/checkout", {\n'
                                     '        method: "POST",\n'
                                     '        headers: { "Content-Type": "application/json" },\n'
                                     '        body: JSON.stringify({ init_data: tg.initData, '
                                     'product_id: "sku_1" }),\n'
                                     '      });\n'
                                     '      tg.close();\n'
                                     '    });\n'
                                     '  </script>\n'
                                     '</body>\n'
                                     '</html>\n'},
                            {'filename': 'api_checkout.py',
                             'language': 'python',
                             'code': 'from fastapi import APIRouter, HTTPException\n'
                                     '\n'
                                     'from security import verify_init_data\n'
                                     'from bot_instance import bot, handle_mini_app_order\n'
                                     '\n'
                                     'router = APIRouter()\n'
                                     '\n'
                                     '\n'
                                     '@router.post("/api/checkout")\n'
                                     'async def checkout(init_data: str, product_id: str):\n'
                                     '    user = verify_init_data(init_data, bot_token=bot.token)\n'
                                     '    if user is None:\n'
                                     '        raise HTTPException(status_code=401, '
                                     'detail="initData yaroqsiz")\n'
                                     '\n'
                                     '    await handle_mini_app_order(bot, chat_id=user["id"], '
                                     'init_data=init_data, product_id=product_id)\n'
                                     '    return {"status": "invoice_sent"}\n'}]},
  'task': {'task_title': "Mini-loyiha: Mini App orqali tasdiqlangan foydalanuvchidan real to'lov "
                         'olish',
           'task_title_ru': 'Мини-проект: реальная оплата от подтверждённого через Mini App '
                            'пользователя',
           'task_description': 'Mini App sahifasi yasang (yoki mavjud shablondan foydalaning) — '
                               "unda foydalanuvchi mahsulot tanlaydi va 'Buyurtma berish' "
                               "tugmasini bosadi. Bu bosilganda sahifa Telegram'dan olingan "
                               "initData'ni sizning FastAPI backend'ingizga yuboradi. Backend "
                               "initData'ni HMAC-SHA256 orqali tasdiqlaydi, so'ng aiogram bot "
                               'orqali shu foydalanuvchiga tanlangan mahsulot uchun send_invoice '
                               "chaqiradi. pre_checkout_query'ni tasdiqlang va successful_payment "
                               "kelganda buyurtmani 'to'langan' deb belgilang.",
           'task_description_ru': 'Создайте страницу Mini App (или используйте готовый шаблон) — '
                                  'пользователь выбирает товар и нажимает «Оформить заказ». По '
                                  'нажатию страница отправляет полученный от Telegram initData на '
                                  'ваш FastAPI-бэкенд. Бэкенд проверяет initData через '
                                  'HMAC-SHA256, затем через aiogram-бота вызывает send_invoice для '
                                  'выбранного товара от имени этого пользователя. Подтвердите '
                                  'pre_checkout_query и при получении successful_payment пометьте '
                                  'заказ как «оплачен».',
           'task_requirements': 'initData HMAC-SHA256 orqali serverda tasdiqlanishi shart, invoice '
                                "narxi faqat serverdagi mahsulot ro'yxatidan olinishi kerak, "
                                'pre_checkout_query 10 soniya ichida javob berilishi, '
                                'successful_payment handler orqali buyurtma holati yangilanishi '
                                'kerak.',
           'task_requirements_ru': 'initData обязательно должен проверяться на сервере через '
                                   'HMAC-SHA256, цена инвойса должна браться только из серверного '
                                   'списка товаров, на pre_checkout_query нужно ответить в течение '
                                   '10 секунд, статус заказа должен обновляться в хендлере '
                                   'successful_payment.',
           'task_technologies': 'aiogram 3.x, FastAPI, Telegram WebApp JS API, Telegram Payments '
                                'API',
           'task_deadline_days': 4},
  'exercises': [{'title': 'initData tekshiruvi',
                 'title_ru': 'Проверка initData',
                 'description': "initData'ni backend'da tekshirishning asosiy sababi nima?",
                 'description_ru': 'В чём основная причина проверки initData на бэкенде?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Frontend JS kodi o'zgartirilishi mumkin, shuning uchun mijoz "
                             "yuborgan foydalanuvchi ma'lumotiga ishonib bo'lmaydi",
                             'Bu Telegram serverlarining tezligini oshiradi',
                             "Bu faqat kod chiroyliroq ko'rinishi uchun kerak",
                             "Bu Mini App'ning ochilish tezligini oshiradi"],
                 'options_ru': ['Код фронтенда на JS можно изменить, поэтому нельзя доверять '
                                'данным пользователя, присланным клиентом',
                                'Это повышает скорость серверов Telegram',
                                'Это нужно только для того, чтобы код выглядел красивее',
                                'Это ускоряет открытие Mini App'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "2-darsni eslang: kim tomonidan yuborilgan ma'lumotga ishonib bo'lmaydi?",
                 'hint_ru': 'Вспомните урок 2: данным от кого нельзя доверять напрямую?',
                 'explanation': "Mijoz tomonidagi JS kodini istalgan kishi o'zgartirishi mumkin, "
                                'shuning uchun foydalanuvchi shaxsini faqat server tomonidagi '
                                'HMAC-SHA256 tekshiruvi orqali tasdiqlash mumkin.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'pre_checkout_query metodi',
                 'title_ru': 'Метод pre_checkout_query',
                 'description': "pre_checkout_query'ga javob berish uchun ___ metodi chaqiriladi.",
                 'description_ru': 'Для ответа на pre_checkout_query вызывается метод ___.',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'answer_pre_checkout_query',
                 'hint': "aiogram'da pre_checkout_query obyektining o'zida ham shunga mos qisqa "
                         'metod bor.',
                 'hint_ru': 'В aiogram у самого объекта pre_checkout_query тоже есть '
                            'соответствующий короткий метод.',
                 'explanation': 'Bot.answer_pre_checkout_query(ok=True/False) (yoki '
                                'pre_checkout_query.answer(ok=...)) — Telegram bu javobni 10 '
                                "soniya ichida kutadi, aks holda to'lov bekor qilinadi.",
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': "To'liq oqim tartibi",
                 'title_ru': 'Порядок полного потока',
                 'description': "Mini App'dan real to'lovgacha bo'lgan to'liq oqimni to'g'ri "
                                'tartibga joylashtiring.',
                 'description_ru': 'Расположите полный поток от Mini App до реальной оплаты в '
                                   'правильном порядке.',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Foydalanuvchi web_app tugmasini bosadi',
                                "Mini App initData'ni backend'ga yuboradi",
                                'Backend HMAC-SHA256 bilan tasdiqlaydi',
                                'Bot send_invoice chaqiradi',
                                "Foydalanuvchi to'lovni tasdiqlaydi (pre_checkout_query)",
                                'successful_payment keladi va buyurtma yangilanadi'],
                 'drag_items_ru': ['Пользователь нажимает кнопку web_app',
                                   'Mini App отправляет initData на бэкенд',
                                   'Бэкенд проверяет через HMAC-SHA256',
                                   'Бот вызывает send_invoice',
                                   'Пользователь подтверждает оплату (pre_checkout_query)',
                                   'Приходит successful_payment и заказ обновляется'],
                 'correct_order': ['Foydalanuvchi web_app tugmasini bosadi',
                                   "Mini App initData'ni backend'ga yuboradi",
                                   'Backend HMAC-SHA256 bilan tasdiqlaydi',
                                   'Bot send_invoice chaqiradi',
                                   "Foydalanuvchi to'lovni tasdiqlaydi (pre_checkout_query)",
                                   'successful_payment keladi va buyurtma yangilanadi'],
                 'hint': 'Bu 1-5-darslarning butun zanjiri — boshidan oxirigacha ketma-ket eslang.',
                 'hint_ru': 'Это вся цепочка уроков 1-5 — вспомните по порядку от начала до конца.',
                 'difficulty_level': 'Hard',
                 'points': 10}]},
 {'order': 7,
  'title': '8-Strukturaviy logging va observability: xatoliklarni kuzatish',
  'title_ru': '8-Структурированное логирование и observability: отслеживание ошибок',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': '<h3>Nega oddiy print() yetarli emas</h3>\n'
                  "<p>Kurs 48'da botingiz ishlayotganini konsolga <code>print()</code> yoki oddiy "
                  "<code>logging.info()</code> orqali ko'rib yurgansiz. Bitta foydalanuvchi, bitta "
                  "noutbuk uchun bu yetarli. Lekin bot production'da 500 ta foydalanuvchini bir "
                  "vaqtda xizmat qilayotganda, log fayl daqiqada minglab qatorga to'ladi, va siz "
                  '"nega Aziz ismli foydalanuvchining to\'lovi ishlamadi" degan savolga javob '
                  "qidirganingizda, erkin matn ichidan qidirish deyarli imkonsiz bo'lib "
                  'qoladi.</p>\n'
                  '<p>Muammo aniq: erkin matn (<em>"User 123 sent /start"</em>) mashina uchun '
                  'emas, inson uchun yozilgan. Uni dastur bilan filtrlash, agregatlash yoki '
                  'grafikka chizish qiyin. Yechim &mdash; <strong>strukturaviy logging</strong>: '
                  'har bir log yozuvi erkin gap emas, balki kalit-qiymat juftlari (yoki '
                  "to'g'ridan-to'g'ri JSON) bo'lishi kerak.</p>\n"
                  '\n'
                  '<h3>structlog: kalit-qiymat va JSON formatida logging</h3>\n'
                  "<p><code>structlog</code> kutubxonasi Python'ning standart <code>logging</code> "
                  'tizimi ustiga qurilgan, lekin har bir chaqiruvga strukturaviy maydonlar '
                  "qo'shish imkonini beradi:</p>\n"
                  '<pre><code>log.info("payment_received", user_id=123, amount=50000, '
                  'currency="UZS")</code></pre>\n'
                  "<p>Bu qator konsolda o'qilishi qulay matn sifatida, production'da esa bitta "
                  'JSON obyekti sifatida chiqadi &mdash; <code>{"event": "payment_received", '
                  '"user_id": 123, "amount": 50000, "currency": "UZS", "timestamp": "..."}</code>. '
                  'Endi Elasticsearch, Loki yoki oddiy <code>jq</code> bilan '
                  "<code>user_id=123</code> bo'yicha barcha loglarni bir zumda topish mumkin.</p>\n"
                  '\n'
                  "<h3>Context binding &mdash; har bir yangilanishga o'z izini yopishtirish</h3>\n"
                  "<p>Eng katta amaliy foyda &mdash; bitta update'ni qayta ishlash davomida "
                  'chaqirilgan <em>barcha</em> log qatorlariga avtomatik ravishda '
                  '<code>user_id</code>, <code>chat_id</code>, <code>update_id</code> va '
                  "generatsiya qilingan <code>trace_id</code> ni qo'shib qo'yish. Buni qo'lda har "
                  "bir <code>log.info(...)</code> chaqiruviga yozish o'rniga, bitta <strong>outer "
                  'middleware</strong> ichida '
                  "<code>structlog.contextvars.bind_contextvars(...)</code> chaqirilsa, o'sha "
                  'handler ichida chaqirilgan har qanday keyingi log avtomatik shu maydonlarni '
                  'oladi &mdash; hatto uch qatlam pastdagi yordamchi funksiyada chaqirilgan log '
                  'ham.</p>\n'
                  '<p>Bu ayniqsa xatoni qidirishda hal qiluvchi: bitta <code>trace_id</code> '
                  "bo'yicha filtrlab, o'sha bitta update qayta ishlanayotganda nima bo'lganini "
                  "&mdash; boshidan oxirigacha &mdash; bitta chiziq sifatida ko'rasiz, minglab "
                  'boshqa foydalanuvchi loglari orasida adashmasdan.</p>\n'
                  '\n'
                  '<h3>Sentry &mdash; kutilmagan xatoliklarni ushlash</h3>\n'
                  '<p>Handler ichida kutilmagan istisno (exception) chiqsa va uni hech kim '
                  'ushlamasa, aiogram uni faqat konsolga yozadi &mdash; ekranga qaramasangiz, hech '
                  'qachon bilmaysiz. <code>sentry_sdk.init(dsn=...)</code> chaqirilgach, '
                  "dispetcherga bitta xatolik handler ro'yxatdan o'tkaziladi "
                  '(<code>dp.errors.register(...)</code> yoki <code>dp.error()</code> dekoratori '
                  "orqali) &mdash; endi har qanday ushlanmagan istisno avtomatik Sentry'ga to'liq "
                  'stack trace, foydalanuvchi konteksti va oxirgi log qatorlari bilan '
                  'yuboriladi.</p>\n'
                  "<p>Muhim nozik joy: Sentry'ga <em>hamma narsani</em> yubormang &mdash; "
                  "<code>before_send</code> hook orqali maxfiy ma'lumotlarni (parol, to'lov "
                  "tokeni) filtrlab tashlang, aks holda xatolikni kuzatish tizimi o'zi maxfiylik "
                  'muammosiga aylanadi.</p>\n'
                  '\n'
                  '<h3>Metrikalar: Prometheus bilan sonlarni kuzatish</h3>\n'
                  '<p>Loglar "nima bo\'ldi" degan savolga javob beradi, metrikalar esa "qancha va '
                  'qanday tezlikda" degan savolga. <code>prometheus_client</code> kutubxonasi '
                  'ikkita asosiy vositani beradi: <code>Counter</code> &mdash; faqat oshib '
                  'boradigan sanoqchi (masalan, qayta ishlangan xabarlar soni, buyruq nomi '
                  "bo'yicha teglangan) va <code>Histogram</code> &mdash; qiymatlar taqsimotini "
                  "o'lchash uchun (masalan, har bir handler necha millisekundda bajarilgani).</p>\n"
                  '<table>\n'
                  '<tr><th>Vosita</th><th>Savolga javob beradi</th><th>Misol</th></tr>\n'
                  '<tr><td>Counter</td><td>Nechta marta sodir '
                  'bo\'ldi?</td><td><code>messages_total{command="start"}</code></td></tr>\n'
                  '<tr><td>Histogram</td><td>Qancha vaqt ketdi, taqsimoti '
                  'qanday?</td><td><code>handler_duration_seconds</code></td></tr>\n'
                  '</table>\n'
                  "<p>Bu metrikalar webhook rejimida ishlayotgan aiohttp serverida qo'shimcha "
                  '<code>/metrics</code> endpoint sifatida ochiladi &mdash; Prometheus serveri uni '
                  'davriy ravishda "scrape" qilib, Grafana\'da grafik chizadi. Shu tarzda '
                  '"so\'nggi 5 daqiqada xatolik darajasi keskin oshdi" degan holatni log '
                  "qatorlarini o'qimasdan, bitta grafikdan darrov ko'rasiz.</p>\n"
                  '\n'
                  '<h3>Uch qatlam birga: logging + xatolik + metrika</h3>\n'
                  '<p>Amalda bu uchtasi bitta outer middleware ichida birlashadi: update kelganda '
                  "&mdash; context bog'lanadi, handler chaqiriladi, muvaffaqiyatli tugasa &mdash; "
                  "Counter oshadi va Histogram vaqtni yozadi, istisno chiqsa &mdash; Sentry'ga "
                  'yuboriladi va xatolik strukturaviy log sifatida yoziladi. Quyidagi diagramma '
                  "shu yagona oqimni ko'rsatadi.</p>\n"
                  '<pre class="mermaid">\n'
                  'flowchart TB\n'
                  '  A["Update keladi"] --> B["Outer middleware:\n'
                  'bind_contextvars(user_id, chat_id, trace_id)"]\n'
                  '  B --> C["Handler chaqiriladi"]\n'
                  '  C -->|"muvaffaqiyatli"| D["Counter++ va\n'
                  'Histogram vaqtni yozadi"]\n'
                  '  C -->|"istisno chiqdi"| E["Sentry capture_exception\n'
                  '+ structlog xatolik log"]\n'
                  '  D --> F["/metrics orqali\n'
                  'Prometheus scrape qiladi"]\n'
                  '  E --> G["Sentry dashboard\'da\n'
                  'alert va stack trace"]\n'
                  '  style E fill:#ffd6d6,stroke:#c00000\n'
                  '  style D fill:#d6ffd9,stroke:#0a8a2e\n'
                  '</pre>\n'
                  "<p>Diagramma shuni ko'rsatadi: bitta middleware uchta vazifani bajaradi, lekin "
                  "har biri mustaqil tizimga (log agregator, Sentry, Prometheus) yo'naltiriladi "
                  '&mdash; biri ishlamay qolsa, qolgan ikkitasi baribir ishlayveradi.</p>',
  'text_content_ru': '<h3>Почему обычного print() недостаточно</h3>\n'
                     '<p>На курсе 48 вы наблюдали за работой бота через <code>print()</code> или '
                     'простой <code>logging.info()</code> в консоли. Для одного пользователя на '
                     'одном ноутбуке этого достаточно. Но когда бот в продакшене обслуживает 500 '
                     'пользователей одновременно, лог-файл заполняется тысячами строк в минуту, и '
                     'когда вы ищете ответ на вопрос «почему платёж пользователя Aziz не '
                     'сработал», искать в свободном тексте практически невозможно.</p>\n'
                     '<p>Проблема очевидна: свободный текст (<em>«User 123 sent /start»</em>) '
                     'написан для человека, а не для машины. Его сложно фильтровать, агрегировать '
                     'или строить по нему графики. Решение — <strong>структурированное '
                     'логирование</strong>: каждая запись лога — это не предложение, а пары '
                     'ключ-значение (или сразу JSON).</p>\n'
                     '\n'
                     '<h3>structlog: логирование в формате ключ-значение и JSON</h3>\n'
                     '<p>Библиотека <code>structlog</code> построена поверх стандартной системы '
                     '<code>logging</code> Python, но позволяет добавлять структурированные поля к '
                     'каждому вызову:</p>\n'
                     '<pre><code>log.info("payment_received", user_id=123, amount=50000, '
                     'currency="UZS")</code></pre>\n'
                     '<p>Эта строка выводится в консоли как удобочитаемый текст, а в продакшене — '
                     'как один JSON-объект: <code>{"event": "payment_received", "user_id": 123, '
                     '"amount": 50000, "currency": "UZS", "timestamp": "..."}</code>. Теперь можно '
                     'мгновенно найти все логи по <code>user_id=123</code> через Elasticsearch, '
                     'Loki или простой <code>jq</code>.</p>\n'
                     '\n'
                     '<h3>Context binding — привязка своего следа к каждому апдейту</h3>\n'
                     '<p>Самая большая практическая польза — автоматически добавлять '
                     '<code>user_id</code>, <code>chat_id</code>, <code>update_id</code> и '
                     'сгенерированный <code>trace_id</code> ко <em>всем</em> логам, вызванным во '
                     'время обработки одного апдейта. Вместо того чтобы вручную писать это в '
                     'каждый вызов <code>log.info(...)</code>, достаточно один раз в <strong>outer '
                     'middleware</strong> вызвать '
                     '<code>structlog.contextvars.bind_contextvars(...)</code> — и любой лог, '
                     'вызванный внутри этого хендлера, автоматически получит эти поля, даже если '
                     'он вызван тремя слоями глубже во вспомогательной функции.</p>\n'
                     '<p>Это особенно важно при поиске багов: фильтруя по одному '
                     '<code>trace_id</code>, вы видите весь путь обработки одного апдейта от '
                     'начала до конца одной линией, не путаясь среди логов тысяч других '
                     'пользователей.</p>\n'
                     '\n'
                     '<h3>Sentry — отлов неожиданных ошибок</h3>\n'
                     '<p>Если внутри хендлера возникает неожиданное исключение и его никто не '
                     'перехватывает, aiogram просто пишет его в консоль — если вы не смотрите на '
                     'экран, вы никогда об этом не узнаете. После вызова '
                     '<code>sentry_sdk.init(dsn=...)</code> у диспетчера регистрируется один '
                     'обработчик ошибок (через <code>dp.errors.register(...)</code> или декоратор '
                     '<code>dp.error()</code>) — теперь любое неперехваченное исключение '
                     'автоматически отправляется в Sentry с полным stack trace, контекстом '
                     'пользователя и последними строками логов.</p>\n'
                     '<p>Важный нюанс: не отправляйте в Sentry <em>всё подряд</em> — через хук '
                     '<code>before_send</code> отфильтруйте чувствительные данные (пароль, '
                     'платёжный токен), иначе система отслеживания ошибок сама станет проблемой '
                     'конфиденциальности.</p>\n'
                     '\n'
                     '<h3>Метрики: отслеживание чисел через Prometheus</h3>\n'
                     '<p>Логи отвечают на вопрос «что произошло», а метрики — на вопрос «сколько и '
                     'с какой скоростью». Библиотека <code>prometheus_client</code> даёт два '
                     'основных инструмента: <code>Counter</code> — счётчик, который только растёт '
                     '(например, количество обработанных сообщений с меткой по названию команды), '
                     'и <code>Histogram</code> — измерение распределения значений (например, за '
                     'сколько миллисекунд отрабатывает каждый хендлер).</p>\n'
                     '<table>\n'
                     '<tr><th>Инструмент</th><th>Отвечает на вопрос</th><th>Пример</th></tr>\n'
                     '<tr><td>Counter</td><td>Сколько раз '
                     'произошло?</td><td><code>messages_total{command="start"}</code></td></tr>\n'
                     '<tr><td>Histogram</td><td>Сколько времени заняло, каково '
                     'распределение?</td><td><code>handler_duration_seconds</code></td></tr>\n'
                     '</table>\n'
                     '<p>Эти метрики открываются как дополнительный endpoint <code>/metrics</code> '
                     'на aiohttp-сервере, работающем в режиме webhook — сервер Prometheus '
                     'периодически их «scrape»-ит, а Grafana строит график. Так вы мгновенно '
                     'видите на одном графике, что «за последние 5 минут уровень ошибок резко '
                     'вырос», не читая строки логов.</p>\n'
                     '\n'
                     '<h3>Три слоя вместе: логирование + ошибки + метрики</h3>\n'
                     '<p>На практике эти три вещи объединяются в одном outer middleware: при '
                     'получении апдейта — привязывается контекст, вызывается хендлер, при успехе — '
                     'растёт Counter и Histogram записывает время, при исключении — отправляется в '
                     'Sentry и пишется структурированный лог ошибки. Диаграмма ниже показывает '
                     'именно этот единый поток.</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart TB\n'
                     '  A["Update keladi"] --> B["Outer middleware:\n'
                     'bind_contextvars(user_id, chat_id, trace_id)"]\n'
                     '  B --> C["Handler chaqiriladi"]\n'
                     '  C -->|"muvaffaqiyatli"| D["Counter++ va\n'
                     'Histogram vaqtni yozadi"]\n'
                     '  C -->|"istisno chiqdi"| E["Sentry capture_exception\n'
                     '+ structlog xatolik log"]\n'
                     '  D --> F["/metrics orqali\n'
                     'Prometheus scrape qiladi"]\n'
                     '  E --> G["Sentry dashboard\'da\n'
                     'alert va stack trace"]\n'
                     '  style E fill:#ffd6d6,stroke:#c00000\n'
                     '  style D fill:#d6ffd9,stroke:#0a8a2e\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает: один middleware выполняет три задачи, но каждая '
                     'направляется в свою независимую систему (лог-агрегатор, Sentry, Prometheus) '
                     '— если одна из них падает, две другие всё равно продолжают работать.</p>',
  'code_content': '# ═══════════════════════════════════════════════════════════════════════\n'
                  '# Strukturaviy logging + Sentry + Prometheus: bitta outer middleware\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'import time\n'
                  'import uuid\n'
                  'from typing import Any, Awaitable, Callable, Dict\n'
                  '\n'
                  'import structlog\n'
                  'import sentry_sdk\n'
                  'from aiogram import BaseMiddleware\n'
                  'from aiogram.types import TelegramObject, Update\n'
                  'from prometheus_client import Counter, Histogram, start_http_server\n'
                  '\n'
                  "# --- structlog konfiguratsiyasi: production'da JSON, dev'da o'qish qulay ---\n"
                  'structlog.configure(\n'
                  '    processors=[\n'
                  '        structlog.contextvars.merge_contextvars,\n'
                  '        structlog.processors.add_log_level,\n'
                  '        structlog.processors.TimeStamper(fmt="iso"),\n'
                  '        structlog.processors.JSONRenderer(),  # dev uchun ConsoleRenderer() ga '
                  'almashtiring\n'
                  '    ],\n'
                  ')\n'
                  'log = structlog.get_logger()\n'
                  '\n'
                  "# --- Sentry: faqat production'da yoqamiz ---\n"
                  'sentry_sdk.init(\n'
                  '    dsn="https://ornak-dsn@sentry.io/000000",\n'
                  '    traces_sample_rate=0.1,\n'
                  '    before_send=lambda event, hint: _strip_sensitive(event),\n'
                  ')\n'
                  '\n'
                  '\n'
                  'def _strip_sensitive(event: dict) -> dict:\n'
                  '    extra = event.get("extra", {})\n'
                  '    for key in ("password", "payment_token", "init_data"):\n'
                  '        extra.pop(key, None)\n'
                  '    return event\n'
                  '\n'
                  '\n'
                  '# --- Prometheus metrikalar ---\n'
                  'MESSAGES_TOTAL = Counter(\n'
                  '    "bot_messages_total", "Qayta ishlangan xabarlar soni", ["handler"]\n'
                  ')\n'
                  'HANDLER_DURATION = Histogram(\n'
                  '    "bot_handler_duration_seconds", "Handler bajarilish vaqti", ["handler"]\n'
                  ')\n'
                  '\n'
                  '\n'
                  'class ObservabilityMiddleware(BaseMiddleware):\n'
                  '    # Outer middleware — HAR BIR update uchun ishga tushadi, handler\n'
                  "    # topilgan-topilmaganidan qat'i nazar. Context bog'lash, metrika va\n"
                  '    # Sentry xatolik ushlash shu yerda birlashtiriladi.\n'
                  '\n'
                  '    async def __call__(\n'
                  '        self,\n'
                  '        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],\n'
                  '        event: Update,\n'
                  '        data: Dict[str, Any],\n'
                  '    ) -> Any:\n'
                  '        trace_id = str(uuid.uuid4())\n'
                  '        user = data.get("event_from_user")\n'
                  '        chat = data.get("event_chat")\n'
                  '\n'
                  '        structlog.contextvars.clear_contextvars()\n'
                  '        structlog.contextvars.bind_contextvars(\n'
                  '            trace_id=trace_id,\n'
                  '            update_id=event.update_id,\n'
                  '            user_id=user.id if user else None,\n'
                  '            chat_id=chat.id if chat else None,\n'
                  '        )\n'
                  '\n'
                  '        handler_name = data.get("handler", {}).__class__.__name__ if '
                  'data.get("handler") else "unknown"\n'
                  '        started = time.perf_counter()\n'
                  '        log.info("update_received")\n'
                  '\n'
                  '        try:\n'
                  '            result = await handler(event, data)\n'
                  '        except Exception as exc:  # noqa: BLE001 — qasddan: har qanday '
                  'xatolikni ushlaymiz\n'
                  '            log.error("handler_failed", error=str(exc), exc_info=True)\n'
                  '            sentry_sdk.capture_exception(exc)\n'
                  '            raise\n'
                  '        else:\n'
                  '            elapsed = time.perf_counter() - started\n'
                  '            MESSAGES_TOTAL.labels(handler=handler_name).inc()\n'
                  '            HANDLER_DURATION.labels(handler=handler_name).observe(elapsed)\n'
                  '            log.info("update_processed", duration_ms=round(elapsed * 1000, 2))\n'
                  '            return result\n'
                  '\n'
                  '\n'
                  'def setup_observability(dp) -> None:\n'
                  '    dp.update.outer_middleware(ObservabilityMiddleware())\n'
                  '    start_http_server(9090)  # /metrics — http://localhost:9090/metrics\n',
  'code_content_ru': '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# Структурированное логирование + Sentry + Prometheus: один outer '
                     'middleware\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'import time\n'
                     'import uuid\n'
                     'from typing import Any, Awaitable, Callable, Dict\n'
                     '\n'
                     'import structlog\n'
                     'import sentry_sdk\n'
                     'from aiogram import BaseMiddleware\n'
                     'from aiogram.types import TelegramObject, Update\n'
                     'from prometheus_client import Counter, Histogram, start_http_server\n'
                     '\n'
                     '# --- конфигурация structlog: в продакшене JSON, в разработке — читаемо ---\n'
                     'structlog.configure(\n'
                     '    processors=[\n'
                     '        structlog.contextvars.merge_contextvars,\n'
                     '        structlog.processors.add_log_level,\n'
                     '        structlog.processors.TimeStamper(fmt="iso"),\n'
                     '        structlog.processors.JSONRenderer(),  # для dev замените на '
                     'ConsoleRenderer()\n'
                     '    ],\n'
                     ')\n'
                     'log = structlog.get_logger()\n'
                     '\n'
                     '# --- Sentry: включаем только в продакшене ---\n'
                     'sentry_sdk.init(\n'
                     '    dsn="https://example-dsn@sentry.io/000000",\n'
                     '    traces_sample_rate=0.1,\n'
                     '    before_send=lambda event, hint: _strip_sensitive(event),\n'
                     ')\n'
                     '\n'
                     '\n'
                     'def _strip_sensitive(event: dict) -> dict:\n'
                     '    extra = event.get("extra", {})\n'
                     '    for key in ("password", "payment_token", "init_data"):\n'
                     '        extra.pop(key, None)\n'
                     '    return event\n'
                     '\n'
                     '\n'
                     '# --- метрики Prometheus ---\n'
                     'MESSAGES_TOTAL = Counter(\n'
                     '    "bot_messages_total", "Количество обработанных сообщений", ["handler"]\n'
                     ')\n'
                     'HANDLER_DURATION = Histogram(\n'
                     '    "bot_handler_duration_seconds", "Время выполнения хендлера", '
                     '["handler"]\n'
                     ')\n'
                     '\n'
                     '\n'
                     'class ObservabilityMiddleware(BaseMiddleware):\n'
                     '    # Outer middleware — запускается для КАЖДОГО апдейта, независимо от\n'
                     '    # того, найден хендлер или нет. Здесь объединены привязка контекста,\n'
                     '    # метрики и перехват ошибок Sentry.\n'
                     '\n'
                     '    async def __call__(\n'
                     '        self,\n'
                     '        handler: Callable[[TelegramObject, Dict[str, Any]], '
                     'Awaitable[Any]],\n'
                     '        event: Update,\n'
                     '        data: Dict[str, Any],\n'
                     '    ) -> Any:\n'
                     '        trace_id = str(uuid.uuid4())\n'
                     '        user = data.get("event_from_user")\n'
                     '        chat = data.get("event_chat")\n'
                     '\n'
                     '        structlog.contextvars.clear_contextvars()\n'
                     '        structlog.contextvars.bind_contextvars(\n'
                     '            trace_id=trace_id,\n'
                     '            update_id=event.update_id,\n'
                     '            user_id=user.id if user else None,\n'
                     '            chat_id=chat.id if chat else None,\n'
                     '        )\n'
                     '\n'
                     '        handler_name = data.get("handler", {}).__class__.__name__ if '
                     'data.get("handler") else "unknown"\n'
                     '        started = time.perf_counter()\n'
                     '        log.info("update_received")\n'
                     '\n'
                     '        try:\n'
                     '            result = await handler(event, data)\n'
                     '        except Exception as exc:  # noqa: BLE001 — намеренно: перехватываем '
                     'любую ошибку\n'
                     '            log.error("handler_failed", error=str(exc), exc_info=True)\n'
                     '            sentry_sdk.capture_exception(exc)\n'
                     '            raise\n'
                     '        else:\n'
                     '            elapsed = time.perf_counter() - started\n'
                     '            MESSAGES_TOTAL.labels(handler=handler_name).inc()\n'
                     '            HANDLER_DURATION.labels(handler=handler_name).observe(elapsed)\n'
                     '            log.info("update_processed", duration_ms=round(elapsed * 1000, '
                     '2))\n'
                     '            return result\n'
                     '\n'
                     '\n'
                     'def setup_observability(dp) -> None:\n'
                     '    dp.update.outer_middleware(ObservabilityMiddleware())\n'
                     '    start_http_server(9090)  # /metrics — http://localhost:9090/metrics\n',
  'sample': {'title': "Namuna: to'liq observability paketi (logging + Sentry + Prometheus)",
             'title_ru': 'Пример: полный пакет observability (логирование + Sentry + Prometheus)',
             'description': 'structlog konfiguratsiyasi, ObservabilityMiddleware va uni botga '
                            'ulash — bitta ishlaydigan misol.',
             'description_ru': 'Конфигурация structlog, ObservabilityMiddleware и его подключение '
                               'к боту — один рабочий пример.',
             'sample_type': 'code',
             'code_files': [{'filename': 'observability.py',
                             'language': 'python',
                             'code': 'import structlog\n'
                                     'import sentry_sdk\n'
                                     'from prometheus_client import Counter, Histogram, '
                                     'start_http_server\n'
                                     '\n'
                                     'structlog.configure(\n'
                                     '    processors=[\n'
                                     '        structlog.contextvars.merge_contextvars,\n'
                                     '        structlog.processors.add_log_level,\n'
                                     '        structlog.processors.TimeStamper(fmt="iso"),\n'
                                     '        structlog.processors.JSONRenderer(),\n'
                                     '    ],\n'
                                     ')\n'
                                     'log = structlog.get_logger()\n'
                                     '\n'
                                     'sentry_sdk.init(dsn="https://example-dsn@sentry.io/000000", '
                                     'traces_sample_rate=0.1)\n'
                                     '\n'
                                     'MESSAGES_TOTAL = Counter("bot_messages_total", "Qayta '
                                     'ishlangan xabarlar", ["handler"])\n'
                                     'HANDLER_DURATION = Histogram("bot_handler_duration_seconds", '
                                     '"Handler vaqti", ["handler"])\n'
                                     '\n'
                                     'def start_metrics_server(port: int = 9090) -> None:\n'
                                     '    start_http_server(port)\n'
                                     '    log.info("metrics_server_started", port=port)\n'},
                            {'filename': 'bot.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'from aiogram import Bot, Dispatcher\n'
                                     'from aiogram.filters import CommandStart\n'
                                     'from aiogram.types import Message\n'
                                     '\n'
                                     'from observability import log, start_metrics_server\n'
                                     'from middlewares import ObservabilityMiddleware\n'
                                     '\n'
                                     'bot = Bot(token="123456:BOT-TOKEN")\n'
                                     'dp = Dispatcher()\n'
                                     'dp.update.outer_middleware(ObservabilityMiddleware())\n'
                                     '\n'
                                     '\n'
                                     '@dp.message(CommandStart())\n'
                                     'async def cmd_start(message: Message) -> None:\n'
                                     '    log.info("start_command_handled")  # trace_id/user_id '
                                     "avtomatik qo'shiladi\n"
                                     '    await message.answer("Salom! Bot observability bilan '
                                     'ishlayapti.")\n'
                                     '\n'
                                     '\n'
                                     'async def main() -> None:\n'
                                     '    start_metrics_server(9090)\n'
                                     '    await dp.start_polling(bot)\n'
                                     '\n'
                                     '\n'
                                     'if __name__ == "__main__":\n'
                                     '    asyncio.run(main())\n'}]},
  'task': {'task_title': "Amaliy mashq: botingizga to'liq observability qo'shing",
           'task_title_ru': 'Практика: добавьте полный observability в своего бота',
           'task_description': "Kurs 48'dagi (yoki o'zingizning) botga structlog asosidagi "
                               'strukturaviy logging, Sentry xatolik ushlash va Prometheus '
                               "metrikalarini qo'shuvchi bitta ObservabilityMiddleware yozing.",
           'task_description_ru': 'Напишите для бота из курса 48 (или своего) один '
                                  'ObservabilityMiddleware, добавляющий структурированное '
                                  'логирование на structlog, перехват ошибок через Sentry и '
                                  'метрики Prometheus.',
           'task_requirements': "Har bir update uchun trace_id/user_id/chat_id context'ga "
                                "bog'lanishi kerak; kamida bitta Counter va bitta Histogram "
                                "bo'lishi kerak; /metrics endpoint ishga tushishi kerak; kamida "
                                "bitta handler ichida qasddan xatolik chiqarib, Sentry'ga "
                                'borishini log orqali tekshiring.',
           'task_requirements_ru': 'Для каждого апдейта должен привязываться context с '
                                   'trace_id/user_id/chat_id; должен быть минимум один Counter и '
                                   'один Histogram; должен работать endpoint /metrics; проверьте '
                                   'через лог, что намеренно вызванная в одном хендлере ошибка '
                                   'доходит до Sentry.',
           'task_technologies': 'aiogram 3.x, structlog, sentry-sdk, prometheus_client',
           'task_deadline_days': 4},
  'exercises': [{'title': 'Strukturaviy vs erkin matn logging',
                 'title_ru': 'Структурированное vs свободное текстовое логирование',
                 'description': "Production botida nima uchun erkin matnli log ('User 123 sent "
                                "/start') o'rniga strukturaviy (kalit-qiymat/JSON) logging afzal?",
                 'description_ru': 'Почему в продакшен-боте структурированное (ключ-значение/JSON) '
                                   "логирование предпочтительнее свободного текста ('User 123 sent "
                                   "/start')?",
                 'exercise_type': 'multiple_choice',
                 'options': ['Chunki u dastur/agregator tomonidan avtomatik filtrlanadi va '
                             "qidiriladi, erkin matn esa faqat inson o'qishi uchun mos",
                             'Chunki strukturaviy log fayl hajmini kichraytiradi',
                             'Chunki aiogram faqat strukturaviy logni qabul qiladi',
                             "Farqi yo'q, ikkalasi ham bir xil ishlaydi"],
                 'options_ru': ['Потому что его можно автоматически фильтровать и агрегировать '
                                'программой, тогда как свободный текст рассчитан только на чтение '
                                'человеком',
                                'Потому что структурированный лог уменьшает размер файла',
                                'Потому что aiogram принимает только структурированные логи',
                                'Разницы нет, оба работают одинаково'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "O'ylab ko'ring: minglab qatordan bitta user_id bo'yicha qidirish qanday "
                         "osonroq bo'ladi.",
                 'hint_ru': 'Подумайте: как проще искать по одному user_id среди тысяч строк.',
                 'explanation': 'Strukturaviy log (JSON/kalit-qiymat) Elasticsearch, Loki kabi '
                                "vositalar tomonidan to'g'ridan-to'g'ri filtrlanadi va "
                                'agregatlanadi — erkin matnda bu faqat regex bilan, ishonchsiz '
                                'tarzda qilinadi.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': "Context bog'lash funksiyasi",
                 'title_ru': 'Функция привязки контекста',
                 'description': "structlog'da bitta update davomida chaqirilgan barcha loglarga "
                                "user_id/chat_id/trace_id ni avtomatik qo'shish uchun "
                                'ishlatiladigan funksiya: structlog.contextvars.___()',
                 'description_ru': 'Функция structlog, используемая для автоматического добавления '
                                   'user_id/chat_id/trace_id ко всем логам одного апдейта: '
                                   'structlog.contextvars.___()',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'bind_contextvars',
                 'hint': "Bu funksiya 'bog'lash' ma'nosini beradi va contextvars submodulida "
                         'joylashgan.',
                 'hint_ru': 'Эта функция означает «привязку» и находится в подмодуле contextvars.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Observability oqimini tartiblang',
                 'title_ru': 'Расположите поток observability по порядку',
                 'description': "ObservabilityMiddleware ichida sodir bo'ladigan qadamlarni "
                                "to'g'ri ketma-ketlikka joylashtiring (muvaffaqiyatli holat uchun)",
                 'description_ru': 'Расположите шаги, происходящие внутри ObservabilityMiddleware, '
                                   'в правильном порядке (для успешного случая)',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['trace_id generatsiya qilinadi va bind_contextvars chaqiriladi',
                                'handler(event, data) chaqiriladi',
                                'Counter.labels(...).inc() bajariladi',
                                'Histogram.labels(...).observe(elapsed) bajariladi'],
                 'drag_items_ru': ['генерируется trace_id и вызывается bind_contextvars',
                                   'вызывается handler(event, data)',
                                   'выполняется Counter.labels(...).inc()',
                                   'выполняется Histogram.labels(...).observe(elapsed)'],
                 'correct_order': ['trace_id generatsiya qilinadi va bind_contextvars chaqiriladi',
                                   'handler(event, data) chaqiriladi',
                                   'Counter.labels(...).inc() bajariladi',
                                   'Histogram.labels(...).observe(elapsed) bajariladi'],
                 'hint': "Avval kontekst tayyorlanadi, keyin haqiqiy ish bajariladi, so'ng natija "
                         "o'lchanadi.",
                 'hint_ru': 'Сначала готовится контекст, затем выполняется реальная работа, потом '
                            'измеряется результат.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Sentry filtrlash',
                 'title_ru': 'Фильтрация в Sentry',
                 'description': 'sentry_sdk.init(___=...) ga qaysi parametr orqali xatolik '
                                'yuborilishidan oldin uni tozalash (masalan, parol/tokenlarni olib '
                                'tashlash) mumkin?',
                 'description_ru': 'Через какой параметр sentry_sdk.init(___=...) можно очистить '
                                   'событие ошибки перед отправкой (например, убрать '
                                   'пароли/токены)?',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'before_send',
                 'hint': "Ingliz tilida 'yuborishdan oldin' degan ma'noni beruvchi ikki so'zli "
                         'parametr nomi.',
                 'hint_ru': 'Название параметра из двух английских слов, означающее «перед '
                            'отправкой».',
                 'difficulty_level': 'Medium',
                 'points': 7}]},
 {'order': 8,
  'title': "9-Rate limiting va suiiste'moldan himoya: production darajasida",
  'title_ru': '9-Rate limiting и защита от злоупотреблений: на уровне продакшена',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': "<h3>Kurs 48'dagi throttling nega ko'p workerda ishlamaydi</h3>\n"
                  "<p>Kurs 48'da siz oddiy in-memory throttling middleware yozgan edingiz &mdash; "
                  "har bir foydalanuvchi uchun oxirgi so'rov vaqtini Python <code>dict</code>'da "
                  'saqlab, juda tez-tez yozayotganlarni bloklagan edingiz. Bitta process uchun bu '
                  "ishlaydi. Lekin botingizni gorizontal masshtablab, ikki yoki uch worker'da "
                  '(yoki bir nechta server instansiyasida) ishga tushirsangiz, har bir worker '
                  "o'zining alohida <code>dict</code>'iga ega bo'ladi.</p>\n"
                  "<p>Natija &mdash; foydalanuvchi haqiqiy limitni chetlab o'tishi mumkin: agar "
                  "load balancer uning so'rovlarini worker A va worker B orasida almashtirib "
                  'yuborsa, har ikkala worker "bu foydalanuvchi hali limitga yetmadi" deb '
                  "o'ylaydi, chunki ular bir-birining hisoblagichini bilmaydi. Bundan tashqari, "
                  'worker qayta ishga tushsa (deploy, crash), butun hisoblagich nolga tushadi '
                  "&mdash; cheklov vaqtincha yo'qoladi.</p>\n"
                  '\n'
                  '<h3>Yechim: Redis &mdash; barcha workerlar uchun umumiy hisoblagich</h3>\n'
                  '<p>Yechim oddiy: hisoblagichni har bir worker xotirasida emas, balki '
                  "<strong>barcha workerlar ulanadigan bitta Redis'da</strong> saqlash. Eng sodda "
                  "usul &mdash; <code>INCR</code> + <code>EXPIRE</code>: foydalanuvchi so'rov "
                  "yuborganda kalitni oshiramiz, agar kalit yangi bo'lsa unga TTL (masalan, 10 "
                  "soniya) qo'yamiz, va agar qiymat limitdan oshsa &mdash; rad etamiz.</p>\n"
                  '<p>Bu usulning nozik kamchiligi bor: <strong>fixed window</strong> chegara '
                  'muammosi. Agar limit "10 soniyada 5 ta so\'rov" bo\'lsa-yu, foydalanuvchi '
                  '9-soniyada 5 ta va yangi oyna boshlangan 11-soniyada яна 5 ta yuborsa &mdash; u '
                  "haqiqatda 2 soniya ichida 10 ta so'rov yuborgan bo'ladi, lekin ikkala oyna "
                  'alohida hisoblanganidan limitni "rasman" buzmagan bo\'lib chiqadi.</p>\n'
                  '\n'
                  '<h3>Token bucket va Lua skript &mdash; atomiklik muammosi</h3>\n'
                  '<p>Chegaraviy portlash (boundary burst) muammosini hal qilish uchun '
                  '<strong>token bucket</strong> algoritmi ishlatiladi: har bir foydalanuvchi '
                  'uchun "chelak" bor, unga belgilangan tezlikda token to\'ldiriladi (masalan, '
                  "soniyasiga 1 ta), chelakning maksimal sig'imi bor (burst capacity, masalan 5 "
                  "ta), va har bir so'rov 1 ta tokenni sarflaydi. Token yetarli bo'lmasa &mdash; "
                  "so'rov rad etiladi.</p>\n"
                  '<p>Redis\'da bu algoritmni to\'g\'ri amalga oshirish uchun "tokenni tekshirish '
                  '+ kamaytirish" ikki amali <strong>atomik</strong> bo\'lishi shart &mdash; aks '
                  'holda ikkita parallel so\'rov bir vaqtda "hali token bor" deb o\'qib, ikkalasi '
                  "ham o'tib ketishi mumkin (race condition). Yechim &mdash; <code>EVAL</code> "
                  "orqali bitta Lua skriptini yuborish: Redis Lua skriptni to'liq atomik bajaradi, "
                  "ya'ni skript ichida boshqa hech qanday buyruq oralab kirmaydi.</p>\n"
                  '<pre><code>-- token_bucket.lua (soddalashtirilgan)\n'
                  'local key = KEYS[1]\n'
                  'local capacity = tonumber(ARGV[1])\n'
                  'local refill_rate = tonumber(ARGV[2])\n'
                  'local now = tonumber(ARGV[3])\n'
                  '\n'
                  'local bucket = redis.call("HMGET", key, "tokens", "ts")\n'
                  'local tokens = tonumber(bucket[1]) or capacity\n'
                  'local last_ts = tonumber(bucket[2]) or now\n'
                  '\n'
                  'local elapsed = now - last_ts\n'
                  'tokens = math.min(capacity, tokens + elapsed * refill_rate)\n'
                  '\n'
                  'if tokens &lt; 1 then\n'
                  '  return 0\n'
                  'end\n'
                  '\n'
                  'tokens = tokens - 1\n'
                  'redis.call("HMSET", key, "tokens", tokens, "ts", now)\n'
                  'redis.call("EXPIRE", key, 3600)\n'
                  'return 1</code></pre>\n'
                  '\n'
                  '<h3>Bosqichma-bosqich javob: ogohlantirish, vaqtinchalik bloklash, uzoq '
                  'bloklash</h3>\n'
                  '<p>Limitni buzgan foydalanuvchini birinchi marta darhol butunlay bloklash yomon '
                  "UX &mdash; tarmoq kechikishi yoki qo'l tegib ketishi ham shu holatga olib "
                  'kelishi mumkin. Amaliyotda <strong>bosqichma-bosqich (graduated) javob</strong> '
                  'qo\'llaniladi: birinchi buzilishda &mdash; ogohlantiruvchi xabar ("iltimos, '
                  'sekinroq"), qayta-qayta buzsa &mdash; Redis\'da TTL\'li vaqtinchalik ban kaliti '
                  '(masalan, 5 daqiqaga), va agar bu ham davom etsa &mdash; uzoqroq muddatli '
                  '(masalan, 24 soatlik) bloklash.</p>\n'
                  "<p>Bu ban kaliti ham Redis'da: <code>SET ban:{user_id} 1 EX 300</code> &mdash; "
                  'oddiy, tez va barcha workerlar uchun umumiy. Middleware har bir update kelganda '
                  'avval shu ban kalitini tekshiradi, keyingina token bucket tekshiruviga '
                  "o'tadi.</p>\n"
                  '\n'
                  '<h3>Qayerga ulash: outer middleware sifatida</h3>\n'
                  "<p>Bu tekshiruv <strong>outer middleware</strong> sifatida ro'yxatdan "
                  "o'tkazilishi kerak &mdash; ya'ni hech qanday filtr mos kelmagan update uchun "
                  'ham ishlashi kerak. Sababi: agar tekshiruvni faqat muayyan handler ichida '
                  '(inner middleware) qilsangiz, foydalanuvchi hech qaysi buyruqqa mos kelmaydigan '
                  "spam xabarlar yuborib, baribir serverni band qilib qo'yishi mumkin &mdash; ban "
                  "tekshiruvi handlerdan oldinroq, eng tashqi qatlamda bo'lishi shart.</p>\n"
                  '<pre class="mermaid">\n'
                  'flowchart TB\n'
                  '  A["Update keladi"] --> B{"Redis: ban:{user_id}\n'
                  'mavjudmi?"}\n'
                  '  B -->|"ha"| C["Rad etiladi (jim yoki\n'
                  '\'siz vaqtincha bloklangansiz\')"]\n'
                  '  B -->|"yo\'q"| D["Lua skript: token bucket\n'
                  'atomik tekshiruvi"]\n'
                  '  D -->|"token yetarli"| E["Handlerga o\'tkaziladi"]\n'
                  '  D -->|"token yetmadi"| F["Ogohlantirish yuboriladi +\n'
                  'buzilish hisoblagichi oshadi"]\n'
                  '  F --> G{"buzilish soni\n'
                  'chegaradan oshdimi?"}\n'
                  '  G -->|"ha"| H["SET ban:{user_id} EX 300"]\n'
                  '  G -->|"yo\'q"| C2["Hozircha faqat ogohlantirish"]\n'
                  '  style C fill:#ffd6d6,stroke:#c00000\n'
                  '  style E fill:#d6ffd9,stroke:#0a8a2e\n'
                  '</pre>\n'
                  "<p>Diagramma shuni ko'rsatadi: ban tekshiruvi eng tez va arzon amal sifatida "
                  "birinchi bo'lib boradi, faqat undan keyin qimmatroq token bucket hisoblashi "
                  "ishga tushadi &mdash; bu tartib botni haqiqiy DDoS-ga o'xshash hujumdan ham "
                  'himoya qiladi, chunki bloklangan foydalanuvchi uchun Lua skript hatto '
                  'chaqirilmaydi.</p>',
  'text_content_ru': '<h3>Почему throttling из курса 48 не работает с несколькими workers</h3>\n'
                     '<p>На курсе 48 вы написали простой in-memory throttling middleware — хранили '
                     'время последнего запроса каждого пользователя в Python <code>dict</code> и '
                     'блокировали тех, кто пишет слишком часто. Для одного процесса это работает. '
                     'Но если вы горизонтально масштабируете бота и запускаете его на двух-трёх '
                     'workers (или нескольких серверных инстансах), у каждого worker будет свой '
                     'отдельный <code>dict</code>.</p>\n'
                     '<p>Результат — пользователь может обойти реальный лимит: если балансировщик '
                     'нагрузки чередует его запросы между worker A и worker B, оба worker думают '
                     '«этот пользователь ещё не достиг лимита», потому что они не знают о счётчике '
                     'друг друга. Более того, при перезапуске worker (деплой, падение) весь '
                     'счётчик обнуляется — ограничение временно исчезает.</p>\n'
                     '\n'
                     '<h3>Решение: Redis — общий счётчик для всех workers</h3>\n'
                     '<p>Решение простое: хранить счётчик не в памяти каждого worker, а в '
                     '<strong>одном Redis, к которому подключаются все workers</strong>. Самый '
                     'простой способ — <code>INCR</code> + <code>EXPIRE</code>: при запросе '
                     'пользователя увеличиваем ключ, если ключ новый — ставим ему TTL (например, '
                     '10 секунд), и если значение превышает лимит — отклоняем.</p>\n'
                     '<p>У этого способа есть тонкий недостаток: проблема границы '
                     '<strong>фиксированного окна</strong> (fixed window). Если лимит «5 запросов '
                     'за 10 секунд», а пользователь отправит 5 запросов на 9-й секунде и ещё 5 в '
                     'начавшемся новом окне на 11-й секунде — фактически он отправил 10 запросов '
                     'за 2 секунды, но формально не нарушил лимит, так как оба окна считаются '
                     'раздельно.</p>\n'
                     '\n'
                     '<h3>Token bucket и Lua-скрипт — проблема атомарности</h3>\n'
                     '<p>Для решения проблемы граничного всплеска (boundary burst) используется '
                     'алгоритм <strong>token bucket</strong>: у каждого пользователя есть «ведро», '
                     'которое пополняется токенами с заданной скоростью (например, 1 в секунду), у '
                     'ведра есть максимальная ёмкость (burst capacity, например 5), и каждый '
                     'запрос тратит 1 токен. Если токенов не хватает — запрос отклоняется.</p>\n'
                     '<p>Чтобы правильно реализовать этот алгоритм в Redis, операция «проверить '
                     'токен + уменьшить» должна быть <strong>атомарной</strong> — иначе два '
                     'параллельных запроса могут одновременно прочитать «токен ещё есть» и оба '
                     'пройдут (race condition). Решение — отправить один Lua-скрипт через '
                     '<code>EVAL</code>: Redis выполняет Lua-скрипт полностью атомарно, то есть '
                     'внутри скрипта не может вклиниться никакая другая команда.</p>\n'
                     '<pre><code>-- token_bucket.lua (упрощённо)\n'
                     'local key = KEYS[1]\n'
                     'local capacity = tonumber(ARGV[1])\n'
                     'local refill_rate = tonumber(ARGV[2])\n'
                     'local now = tonumber(ARGV[3])\n'
                     '\n'
                     'local bucket = redis.call("HMGET", key, "tokens", "ts")\n'
                     'local tokens = tonumber(bucket[1]) or capacity\n'
                     'local last_ts = tonumber(bucket[2]) or now\n'
                     '\n'
                     'local elapsed = now - last_ts\n'
                     'tokens = math.min(capacity, tokens + elapsed * refill_rate)\n'
                     '\n'
                     'if tokens &lt; 1 then\n'
                     '  return 0\n'
                     'end\n'
                     '\n'
                     'tokens = tokens - 1\n'
                     'redis.call("HMSET", key, "tokens", tokens, "ts", now)\n'
                     'redis.call("EXPIRE", key, 3600)\n'
                     'return 1</code></pre>\n'
                     '\n'
                     '<h3>Поэтапный ответ: предупреждение, временная блокировка, длительная '
                     'блокировка</h3>\n'
                     '<p>Полностью блокировать пользователя при первом же нарушении лимита — '
                     'плохой UX: причиной может быть сетевая задержка или случайное нажатие. На '
                     'практике применяется <strong>поэтапный (graduated) ответ</strong>: при '
                     'первом нарушении — предупреждающее сообщение («пожалуйста, помедленнее»), '
                     'при повторных нарушениях — ключ временного бана с TTL в Redis (например, на '
                     '5 минут), а если это продолжается — более долгая блокировка (например, на 24 '
                     'часа).</p>\n'
                     '<p>Этот ключ бана тоже хранится в Redis: <code>SET ban:{user_id} 1 EX '
                     '300</code> — просто, быстро и общее для всех workers. Middleware при каждом '
                     'входящем апдейте сначала проверяет этот ключ бана, и только потом переходит '
                     'к проверке token bucket.</p>\n'
                     '\n'
                     '<h3>Куда подключать: как outer middleware</h3>\n'
                     '<p>Эта проверка должна регистрироваться как <strong>outer '
                     'middleware</strong> — то есть должна работать даже для апдейта, не '
                     'подошедшего ни под один фильтр. Причина: если проверять только внутри '
                     'конкретного хендлера (inner middleware), пользователь может слать '
                     'спам-сообщения, не подходящие ни под одну команду, и всё равно нагружать '
                     'сервер — проверка бана должна быть раньше хендлера, на самом внешнем '
                     'уровне.</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart TB\n'
                     '  A["Update keladi"] --> B{"Redis: ban:{user_id}\n'
                     'mavjudmi?"}\n'
                     '  B -->|"ha"| C["Rad etiladi (jim yoki\n'
                     '\'siz vaqtincha bloklangansiz\')"]\n'
                     '  B -->|"yo\'q"| D["Lua skript: token bucket\n'
                     'atomik tekshiruvi"]\n'
                     '  D -->|"token yetarli"| E["Handlerga o\'tkaziladi"]\n'
                     '  D -->|"token yetmadi"| F["Ogohlantirish yuboriladi +\n'
                     'buzilish hisoblagichi oshadi"]\n'
                     '  F --> G{"buzilish soni\n'
                     'chegaradan oshdimi?"}\n'
                     '  G -->|"ha"| H["SET ban:{user_id} EX 300"]\n'
                     '  G -->|"yo\'q"| C2["Hozircha faqat ogohlantirish"]\n'
                     '  style C fill:#ffd6d6,stroke:#c00000\n'
                     '  style E fill:#d6ffd9,stroke:#0a8a2e\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает: проверка бана идёт первой как самая быстрая и '
                     'дешёвая операция, и только после неё запускается более дорогой расчёт token '
                     'bucket — такой порядок защищает бота даже от атаки, похожей на настоящий '
                     'DDoS, потому что для заблокированного пользователя Lua-скрипт вообще не '
                     'вызывается.</p>',
  'code_content': '# ═══════════════════════════════════════════════════════════════════════\n'
                  '# Redis-based token bucket throttling + graduated ban (aiogram outer '
                  'middleware)\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'import time\n'
                  'from typing import Any, Awaitable, Callable, Dict\n'
                  '\n'
                  'from aiogram import BaseMiddleware\n'
                  'from aiogram.types import TelegramObject, Update\n'
                  'from redis.asyncio import Redis\n'
                  '\n'
                  '_TOKEN_BUCKET_LUA = """\n'
                  'local key = KEYS[1]\n'
                  'local capacity = tonumber(ARGV[1])\n'
                  'local refill_rate = tonumber(ARGV[2])\n'
                  'local now = tonumber(ARGV[3])\n'
                  '\n'
                  'local bucket = redis.call("HMGET", key, "tokens", "ts")\n'
                  'local tokens = tonumber(bucket[1]) or capacity\n'
                  'local last_ts = tonumber(bucket[2]) or now\n'
                  '\n'
                  'local elapsed = now - last_ts\n'
                  'tokens = math.min(capacity, tokens + elapsed * refill_rate)\n'
                  '\n'
                  'if tokens < 1 then\n'
                  '  return 0\n'
                  'end\n'
                  '\n'
                  'tokens = tokens - 1\n'
                  'redis.call("HMSET", key, "tokens", tokens, "ts", now)\n'
                  'redis.call("EXPIRE", key, 3600)\n'
                  'return 1\n'
                  '"""\n'
                  '\n'
                  '\n'
                  'class RedisThrottlingMiddleware(BaseMiddleware):\n'
                  '    # Outer middleware — barcha workerlar uchun umumiy Redis orqali\n'
                  '    # token-bucket throttling + bosqichma-bosqich vaqtinchalik ban.\n'
                  '\n'
                  '    def __init__(self, redis: Redis, capacity: int = 5, refill_rate: float = '
                  '1.0):\n'
                  '        self.redis = redis\n'
                  '        self.capacity = capacity\n'
                  '        self.refill_rate = refill_rate\n'
                  '        self._script = redis.register_script(_TOKEN_BUCKET_LUA)\n'
                  '\n'
                  '    async def __call__(\n'
                  '        self,\n'
                  '        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],\n'
                  '        event: Update,\n'
                  '        data: Dict[str, Any],\n'
                  '    ) -> Any:\n'
                  '        user = data.get("event_from_user")\n'
                  '        if not user:\n'
                  '            return await handler(event, data)\n'
                  '\n'
                  '        ban_key = f"ban:{user.id}"\n'
                  '        if await self.redis.exists(ban_key):\n'
                  '            return None  # jim rad etiladi — bloklangan foydalanuvchiga javob '
                  "yo'q\n"
                  '\n'
                  '        bucket_key = f"bucket:{user.id}"\n'
                  '        allowed = await self._script(\n'
                  '            keys=[bucket_key],\n'
                  '            args=[self.capacity, self.refill_rate, time.time()],\n'
                  '        )\n'
                  '\n'
                  '        if not allowed:\n'
                  '            violations_key = f"violations:{user.id}"\n'
                  '            violations = await self.redis.incr(violations_key)\n'
                  '            await self.redis.expire(violations_key, 60)\n'
                  '            if violations >= 3:\n'
                  '                await self.redis.set(ban_key, 1, ex=300)  # 5 daqiqalik ban\n'
                  '            bot = data["bot"]\n'
                  '            chat = data.get("event_chat")\n'
                  '            if chat:\n'
                  '                await bot.send_message(chat.id, "Iltimos, biroz sekinroq '
                  'yozing.")\n'
                  '            return None\n'
                  '\n'
                  '        return await handler(event, data)\n'
                  '\n'
                  '\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  "# Botga ulash: ikki alohida worker process bir xil Redis'ga ulanadi\n"
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'import asyncio\n'
                  'import os\n'
                  '\n'
                  'from aiogram import Bot, Dispatcher\n'
                  'from aiogram.filters import CommandStart\n'
                  'from aiogram.types import Message\n'
                  '\n'
                  '\n'
                  'async def create_dispatcher() -> Dispatcher:\n'
                  '    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=False)\n'
                  '    dp = Dispatcher()\n'
                  '    dp.update.outer_middleware(\n'
                  '        RedisThrottlingMiddleware(redis, capacity=5, refill_rate=1.0)\n'
                  '    )\n'
                  '\n'
                  '    @dp.message(CommandStart())\n'
                  '    async def cmd_start(message: Message) -> None:\n'
                  '        await message.answer("Salom! Bu botning barcha workerlari bitta Redis '
                  'limitini bo\'lishadi.")\n'
                  '\n'
                  '    return dp\n'
                  '\n'
                  '\n'
                  'async def main() -> None:\n'
                  "    # WORKER_NAME faqat log/diagnostika uchun — throttling holati Redis'da,\n"
                  '    # shuning uchun WORKER_NAME=worker-1 yoki worker-2 bilan ishga tushirilgan\n'
                  "    # ikki jarayon HAM bitta umumiy limitni ko'radi.\n"
                  '    worker_name = os.environ.get("WORKER_NAME", "worker-1")\n'
                  '    bot = Bot(token=os.environ["BOT_TOKEN"])\n'
                  '    dp = await create_dispatcher()\n'
                  '    print(f"{worker_name} ishga tushdi, Redis orqali umumiy throttling faol")\n'
                  '    await dp.start_polling(bot)\n'
                  '\n'
                  '\n'
                  'if __name__ == "__main__":\n'
                  '    asyncio.run(main())\n'
                  '\n'
                  '\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  '# pytest: token bucket atomikligini tekshirish (fakeredis bilan)\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'import pytest\n'
                  '\n'
                  '\n'
                  '@pytest.mark.asyncio\n'
                  'async def test_token_bucket_blocks_after_capacity_exhausted():\n'
                  '    import fakeredis.aioredis\n'
                  '    redis = fakeredis.aioredis.FakeRedis()\n'
                  '    middleware = RedisThrottlingMiddleware(redis, capacity=2, refill_rate=0.0)\n'
                  '\n'
                  '    calls = []\n'
                  '\n'
                  '    async def fake_handler(event, data):\n'
                  '        calls.append(1)\n'
                  '        return "ok"\n'
                  '\n'
                  '    class _User:\n'
                  '        id = 555\n'
                  '\n'
                  '    class _Chat:\n'
                  '        id = 555\n'
                  '\n'
                  '    data = {"event_from_user": _User(), "event_chat": _Chat(), "bot": None}\n'
                  '\n'
                  "    # refill_rate=0.0 bo'lgani uchun to'ldirilmaydi: birinchi ikkita so'rov\n"
                  "    # o'tadi (capacity=2), uchinchisi token yo'qligi sababli rad etiladi\n"
                  '    for _ in range(3):\n'
                  '        await middleware(fake_handler, event=None, data=data)\n'
                  '    assert len(calls) == 2\n',
  'code_content_ru': '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# Redis-based token bucket throttling + поэтапный бан (aiogram outer '
                     'middleware)\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'import time\n'
                     'from typing import Any, Awaitable, Callable, Dict\n'
                     '\n'
                     'from aiogram import BaseMiddleware\n'
                     'from aiogram.types import TelegramObject, Update\n'
                     'from redis.asyncio import Redis\n'
                     '\n'
                     '_TOKEN_BUCKET_LUA = """\n'
                     'local key = KEYS[1]\n'
                     'local capacity = tonumber(ARGV[1])\n'
                     'local refill_rate = tonumber(ARGV[2])\n'
                     'local now = tonumber(ARGV[3])\n'
                     '\n'
                     'local bucket = redis.call("HMGET", key, "tokens", "ts")\n'
                     'local tokens = tonumber(bucket[1]) or capacity\n'
                     'local last_ts = tonumber(bucket[2]) or now\n'
                     '\n'
                     'local elapsed = now - last_ts\n'
                     'tokens = math.min(capacity, tokens + elapsed * refill_rate)\n'
                     '\n'
                     'if tokens < 1 then\n'
                     '  return 0\n'
                     'end\n'
                     '\n'
                     'tokens = tokens - 1\n'
                     'redis.call("HMSET", key, "tokens", tokens, "ts", now)\n'
                     'redis.call("EXPIRE", key, 3600)\n'
                     'return 1\n'
                     '"""\n'
                     '\n'
                     '\n'
                     'class RedisThrottlingMiddleware(BaseMiddleware):\n'
                     '    # Outer middleware — throttling по token-bucket через общий для всех\n'
                     '    # workers Redis + поэтапный временный бан.\n'
                     '\n'
                     '    def __init__(self, redis: Redis, capacity: int = 5, refill_rate: float = '
                     '1.0):\n'
                     '        self.redis = redis\n'
                     '        self.capacity = capacity\n'
                     '        self.refill_rate = refill_rate\n'
                     '        self._script = redis.register_script(_TOKEN_BUCKET_LUA)\n'
                     '\n'
                     '    async def __call__(\n'
                     '        self,\n'
                     '        handler: Callable[[TelegramObject, Dict[str, Any]], '
                     'Awaitable[Any]],\n'
                     '        event: Update,\n'
                     '        data: Dict[str, Any],\n'
                     '    ) -> Any:\n'
                     '        user = data.get("event_from_user")\n'
                     '        if not user:\n'
                     '            return await handler(event, data)\n'
                     '\n'
                     '        ban_key = f"ban:{user.id}"\n'
                     '        if await self.redis.exists(ban_key):\n'
                     '            return None  # молча отклоняем — заблокированному пользователю '
                     'без ответа\n'
                     '\n'
                     '        bucket_key = f"bucket:{user.id}"\n'
                     '        allowed = await self._script(\n'
                     '            keys=[bucket_key],\n'
                     '            args=[self.capacity, self.refill_rate, time.time()],\n'
                     '        )\n'
                     '\n'
                     '        if not allowed:\n'
                     '            violations_key = f"violations:{user.id}"\n'
                     '            violations = await self.redis.incr(violations_key)\n'
                     '            await self.redis.expire(violations_key, 60)\n'
                     '            if violations >= 3:\n'
                     '                await self.redis.set(ban_key, 1, ex=300)  # бан на 5 минут\n'
                     '            bot = data["bot"]\n'
                     '            chat = data.get("event_chat")\n'
                     '            if chat:\n'
                     '                await bot.send_message(chat.id, "Пожалуйста, пишите немного '
                     'медленнее.")\n'
                     '            return None\n'
                     '\n'
                     '        return await handler(event, data)\n'
                     '\n'
                     '\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# Подключение к боту: два отдельных worker-процесса используют один Redis\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'import asyncio\n'
                     'import os\n'
                     '\n'
                     'from aiogram import Bot, Dispatcher\n'
                     'from aiogram.filters import CommandStart\n'
                     'from aiogram.types import Message\n'
                     '\n'
                     '\n'
                     'async def create_dispatcher() -> Dispatcher:\n'
                     '    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=False)\n'
                     '    dp = Dispatcher()\n'
                     '    dp.update.outer_middleware(\n'
                     '        RedisThrottlingMiddleware(redis, capacity=5, refill_rate=1.0)\n'
                     '    )\n'
                     '\n'
                     '    @dp.message(CommandStart())\n'
                     '    async def cmd_start(message: Message) -> None:\n'
                     '        await message.answer("Привет! Все workers этого бота используют один '
                     'общий лимит Redis.")\n'
                     '\n'
                     '    return dp\n'
                     '\n'
                     '\n'
                     'async def main() -> None:\n'
                     '    # WORKER_NAME нужен только для логов/диагностики — состояние throttling\n'
                     '    # хранится в Redis, поэтому два процесса, запущенных с '
                     'WORKER_NAME=worker-1\n'
                     '    # и WORKER_NAME=worker-2, ВИДЯТ один и тот же общий лимит.\n'
                     '    worker_name = os.environ.get("WORKER_NAME", "worker-1")\n'
                     '    bot = Bot(token=os.environ["BOT_TOKEN"])\n'
                     '    dp = await create_dispatcher()\n'
                     '    print(f"{worker_name} запущен, общий throttling через Redis активен")\n'
                     '    await dp.start_polling(bot)\n'
                     '\n'
                     '\n'
                     'if __name__ == "__main__":\n'
                     '    asyncio.run(main())\n'
                     '\n'
                     '\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# pytest: проверка атомарности token bucket (с fakeredis)\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'import pytest\n'
                     '\n'
                     '\n'
                     '@pytest.mark.asyncio\n'
                     'async def test_token_bucket_blocks_after_capacity_exhausted():\n'
                     '    import fakeredis.aioredis\n'
                     '    redis = fakeredis.aioredis.FakeRedis()\n'
                     '    middleware = RedisThrottlingMiddleware(redis, capacity=2, '
                     'refill_rate=0.0)\n'
                     '\n'
                     '    calls = []\n'
                     '\n'
                     '    async def fake_handler(event, data):\n'
                     '        calls.append(1)\n'
                     '        return "ok"\n'
                     '\n'
                     '    class _User:\n'
                     '        id = 555\n'
                     '\n'
                     '    class _Chat:\n'
                     '        id = 555\n'
                     '\n'
                     '    data = {"event_from_user": _User(), "event_chat": _Chat(), "bot": None}\n'
                     '\n'
                     '    # refill_rate=0.0, поэтому пополнения не будет: первые два запроса\n'
                     '    # проходят (capacity=2), третий отклоняется из-за нехватки токена\n'
                     '    for _ in range(3):\n'
                     '        await middleware(fake_handler, event=None, data=data)\n'
                     '    assert len(calls) == 2\n',
  'sample': {'title': 'Namuna: token bucket + vaqtinchalik ban middleware',
             'title_ru': 'Пример: middleware token bucket + временный бан',
             'description': 'Redis Lua skripti bilan atomik token-bucket tekshiruvi va uch marta '
                            'buzilgach vaqtinchalik ban.',
             'description_ru': 'Атомарная проверка token-bucket через Lua-скрипт Redis и временный '
                               'бан после трёх нарушений.',
             'sample_type': 'code',
             'code_files': [{'filename': 'throttling.py',
                             'language': 'python',
                             'code': 'import time\n'
                                     'from redis.asyncio import Redis\n'
                                     '\n'
                                     'TOKEN_BUCKET_LUA = """\n'
                                     'local key = KEYS[1]\n'
                                     'local capacity = tonumber(ARGV[1])\n'
                                     'local refill_rate = tonumber(ARGV[2])\n'
                                     'local now = tonumber(ARGV[3])\n'
                                     'local bucket = redis.call("HMGET", key, "tokens", "ts")\n'
                                     'local tokens = tonumber(bucket[1]) or capacity\n'
                                     'local last_ts = tonumber(bucket[2]) or now\n'
                                     'tokens = math.min(capacity, tokens + (now - last_ts) * '
                                     'refill_rate)\n'
                                     'if tokens < 1 then return 0 end\n'
                                     'tokens = tokens - 1\n'
                                     'redis.call("HMSET", key, "tokens", tokens, "ts", now)\n'
                                     'redis.call("EXPIRE", key, 3600)\n'
                                     'return 1\n'
                                     '"""\n'
                                     '\n'
                                     'async def check_allowed(redis: Redis, user_id: int, '
                                     'capacity: int = 5, refill_rate: float = 1.0) -> bool:\n'
                                     '    script = redis.register_script(TOKEN_BUCKET_LUA)\n'
                                     '    result = await script(keys=[f"bucket:{user_id}"], '
                                     'args=[capacity, refill_rate, time.time()])\n'
                                     '    return bool(result)\n'},
                            {'filename': 'test_throttling.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'from redis.asyncio import Redis\n'
                                     'from throttling import check_allowed\n'
                                     '\n'
                                     'async def main():\n'
                                     '    redis = Redis.from_url("redis://localhost:6379/0")\n'
                                     '    for i in range(7):\n'
                                     '        allowed = await check_allowed(redis, user_id=1, '
                                     'capacity=5, refill_rate=1.0)\n'
                                     '        print(f"so\'rov {i + 1}: {\'ruxsat\' if allowed else '
                                     '\'rad etildi\'}")\n'
                                     '\n'
                                     'asyncio.run(main())\n'}]},
  'task': {'task_title': 'Amaliy mashq: distributed rate limiter yozing',
           'task_title_ru': 'Практика: напишите распределённый rate limiter',
           'task_description': 'Redis va Lua skripti asosida token-bucket throttling middleware '
                               "yozing va uni ikki xil aiogram worker process'ida ishga tushirib, "
                               'limit umumiy ekanini isbotlang.',
           'task_description_ru': 'Напишите throttling middleware на основе token-bucket с '
                                  'Lua-скриптом в Redis и запустите его в двух разных aiogram '
                                  'worker-процессах, доказав, что лимит общий.',
           'task_requirements': "Lua skripti orqali atomik tekshiruv bo'lishi shart; uch marta "
                                "buzilgach TTL'li vaqtinchalik ban ishga tushishi kerak; ikkita "
                                'alohida process bir xil Redis kalitidan foydalanib, limitni '
                                "birgalikda hisoblashini ko'rsating.",
           'task_requirements_ru': 'Обязательна атомарная проверка через Lua-скрипт; после трёх '
                                   'нарушений должен срабатывать временный бан с TTL; покажите, '
                                   'что два отдельных процесса используют один и тот же ключ Redis '
                                   'и совместно учитывают лимит.',
           'task_technologies': 'aiogram 3.x, redis.asyncio, Lua (EVAL)',
           'task_deadline_days': 4},
  'exercises': [{'title': "Nega in-memory throttling ko'p workerda buziladi",
                 'title_ru': 'Почему in-memory throttling ломается при нескольких workers',
                 'description': "Botni ikki worker'da ishga tushirganda, in-memory (Python dict) "
                                "throttling nega haqiqiy limitni ta'minlay olmaydi?",
                 'description_ru': 'Почему при запуске бота на двух workers in-memory throttling '
                                   '(Python dict) не может обеспечить реальный лимит?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Har bir worker o'z alohida dict'iga ega va ular bir-birining "
                             'hisoblagichini bilmaydi',
                             "Python dict Redis'dan sekinroq ishlaydi",
                             "aiogram ko'p workerni umuman qo'llab-quvvatlamaydi",
                             'dict faqat bitta foydalanuvchini saqlay oladi'],
                 'options_ru': ['Каждый worker имеет свой отдельный dict, и они не знают о '
                                'счётчике друг друга',
                                'Python dict работает медленнее, чем Redis',
                                'aiogram вообще не поддерживает несколько workers',
                                'dict может хранить только одного пользователя'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Har bir process o'zining alohida xotirasiga ega ekanini eslang.",
                 'hint_ru': 'Вспомните, что у каждого процесса своя отдельная память.',
                 'explanation': "Process'lar xotirani bo'lishmaydi — shuning uchun umumiy holat "
                                "(shared state) uchun tashqi do'kon (Redis) kerak.",
                 'difficulty_level': 'Medium',
                 'points': 7},
                {'title': "Atomiklik uchun Redis buyrug'i",
                 'title_ru': 'Команда Redis для атомарности',
                 'description': "Token bucket tekshiruvini bir nechta parallel so'rovda ham "
                                "xavfsiz (race condition'siz) atomik bajarish uchun Redis'da ___ "
                                'orqali yuborilgan skript ishlatiladi.',
                 'description_ru': 'Для безопасного (без race condition) атомарного выполнения '
                                   'проверки token bucket даже при нескольких параллельных '
                                   'запросах в Redis используется скрипт, отправленный через ___.',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'EVAL',
                 'hint': "Redis'da Lua skriptini ishga tushiruvchi buyruq nomi — bosh harflar "
                         'bilan.',
                 'hint_ru': 'Название команды Redis для запуска Lua-скрипта — заглавными буквами.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Bosqichma-bosqich javobni tartiblang',
                 'title_ru': 'Расположите поэтапный ответ по порядку',
                 'description': "Foydalanuvchi limitni takror-takror buzganda qo'llaniladigan "
                                "bosqichlarni to'g'ri tartibga joylashtiring",
                 'description_ru': 'Расположите в правильном порядке шаги, применяемые при '
                                   'повторных нарушениях лимита пользователем',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Birinchi buzilishda ogohlantiruvchi xabar yuboriladi',
                                "Buzilishlar soni Redis'da hisoblanadi",
                                "Chegaradan oshgach qisqa (masalan, 5 daqiqalik) ban qo'yiladi",
                                'Ban davomida davom etsa, uzoqroq (masalan, 24 soatlik) ban '
                                "qo'yiladi"],
                 'drag_items_ru': ['При первом нарушении отправляется предупреждающее сообщение',
                                   'Количество нарушений считается в Redis',
                                   'После превышения порога ставится короткий (например, '
                                   '5-минутный) бан',
                                   'Если нарушения продолжаются, ставится более долгий (например, '
                                   '24-часовой) бан'],
                 'correct_order': ['Birinchi buzilishda ogohlantiruvchi xabar yuboriladi',
                                   "Buzilishlar soni Redis'da hisoblanadi",
                                   "Chegaradan oshgach qisqa (masalan, 5 daqiqalik) ban qo'yiladi",
                                   'Ban davomida davom etsa, uzoqroq (masalan, 24 soatlik) ban '
                                   "qo'yiladi"],
                 'hint': 'Eng yengil javobdan eng qattiq javobga qarab boring.',
                 'hint_ru': 'Идите от самого мягкого ответа к самому строгому.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 9,
  'title': '10-Dispatcher ichki tuzilishi va middleware zanjiri tartibi',
  'title_ru': '10-Внутреннее устройство Dispatcher и порядок цепочки middleware',
  'points_reward': 20,
  'code_language': 'python',
  'text_content': "<h3>Router'lar ichma-ich joylashadi, Update pastga oqadi</h3>\n"
                  "<p>Kurs 48'da <code>Dispatcher</code>'ni bitta markaz sifatida ishlatgan "
                  "bo'lishingiz mumkin. Katta botlarda esa kod bir nechta <code>Router</code>'ga "
                  "bo'linadi (masalan, <code>admin_router</code>, <code>payments_router</code>, "
                  '<code>user_router</code>) va ular <code>dp.include_router(...)</code> orqali '
                  "asosiy dispetcherga bog'lanadi. Har bir kelgan <code>Update</code> aynan shu "
                  "daraxt bo'ylab &mdash; tashqi dispetcherdan boshlab, ichki routerlargacha "
                  '&mdash; navbat bilan tekshirib chiqiladi, toki mos filtrga ega birinchi handler '
                  'topilmaguncha.</p>\n'
                  "<p>Bu arxitekturaning eng muhim, ko'pincha noto'g'ri tushuniladigan qismi "
                  "&mdash; <strong>middleware</strong>'ning ikki turi va ularning ishlash vaqti "
                  'butunlay farq qiladi.</p>\n'
                  '\n'
                  '<h3>Outer middleware &mdash; har doim ishlaydi, filtrdan oldin</h3>\n'
                  '<p><code>router.outer_middleware</code> (yoki '
                  "<code>dp.update.outer_middleware</code>) orqali ro'yxatdan o'tkazilgan "
                  'middleware <strong>har bir</strong> kelgan update uchun ishga tushadi &mdash; '
                  'hatto hech qanday handler mos kelmasa ham. Bu aynan shu sababdan auth '
                  'tekshiruvi, logging, rate-limiting kabi "har doim bajarilishi shart" bo\'lgan '
                  "mantiq uchun to'g'ri joy: agar siz buni inner middleware qilib qo'ysangiz, "
                  "filtrga mos kelmagan (masalan, noma'lum buyruq yozgan) foydalanuvchi bu "
                  "tekshiruvni butunlay chetlab o'tadi.</p>\n"
                  '\n'
                  '<h3>Inner middleware &mdash; faqat handler topilgandan keyin</h3>\n'
                  '<p><code>router.message.middleware</code> kabi <code>.middleware(...)</code> '
                  "orqali ro'yxatdan o'tkazilgan middleware esa faqat filtrlar allaqachon mos "
                  "kelgan, ya'ni <strong>aynan shu handler chaqirilishi aniqlangandan "
                  "keyin</strong> ishga tushadi. Bu handler kontekstiga bog'liq narsalar uchun "
                  'to\'g\'ri joy &mdash; masalan, faqat "buyurtma qilish" handleridan oldin '
                  "savatni bazadan yuklab, uni <code>data</code> ichiga qo'shib berish (dependency "
                  "injection'ga o'xshash naqsh).</p>\n"
                  '<table>\n'
                  '<tr><th>Xususiyat</th><th>Outer middleware</th><th>Inner middleware</th></tr>\n'
                  '<tr><td>Qachon ishlaydi</td><td>Har bir update uchun, filtrdan '
                  'OLDIN</td><td>Faqat handler mos kelgandan KEYIN</td></tr>\n'
                  "<tr><td>Tipik ishlatilishi</td><td>Auth, logging, rate-limit</td><td>Ma'lumot "
                  'yuklash, handlerga xos context</td></tr>\n'
                  "<tr><td>Ro'yxatdan "
                  "o'tkazish</td><td><code>.outer_middleware(...)</code></td><td><code>.middleware(...)</code></td></tr>\n"
                  '</table>\n'
                  '\n'
                  '<h3>"Piyoz" (onion) naqshi: call_next()</h3>\n'
                  '<p>Har bir middleware ikki argument oladi &mdash; <code>handler</code> (keyingi '
                  "qatlam yoki asl handler) va <code>data</code> (kontekst lug'ati). Middleware "
                  "ichida <code>await handler(event, data)</code> chaqirilgan joygacha bo'lgan kod "
                  '&mdash; "ichkariga kirishdan oldin" bajariladi, chaqiruvdan <em>keyingi</em> '
                  'kod esa &mdash; "tashqariga chiqishda" bajariladi. Shu sababli middleware '
                  "nafaqat oldindan tekshirish, balki natijani keyin o'zgartirish yoki vaqtni "
                  "o'lchash uchun ham ishlatilishi mumkin (masalan, 8-darsdagi Histogram vaqtni "
                  "aynan shu tarzda o'lchagan edi).</p>\n"
                  "<p>Middleware'lar ro'yxatdan o'tkazilgan tartibda ichma-ich joylashadi: "
                  "birinchi ro'yxatdan o'tkazilgan middleware &mdash; eng tashqi qatlam, oxirgisi "
                  '&mdash; handlerga eng yaqin qatlam. Xuddi piyoz pardalari kabi: har bir keyingi '
                  'middleware avvalgisining ichida ishlaydi.</p>\n'
                  '\n'
                  "<h3>Ikki qatlamning to'liq oqimi &mdash; diagramma</h3>\n"
                  '<pre class="mermaid">\n'
                  'sequenceDiagram\n'
                  '  participant U as Update\n'
                  '  participant O1 as Outer MW 1 (logging)\n'
                  '  participant O2 as Outer MW 2 (auth)\n'
                  '  participant R as Router filtri\n'
                  '  participant I1 as Inner MW 1 (savat yuklash)\n'
                  "  participant I2 as Inner MW 2 (o'lchash)\n"
                  '  participant H as Handler\n'
                  '\n'
                  '  U->>O1: call_next(event, data)\n'
                  '  O1->>O2: call_next(event, data)\n'
                  '  O2->>R: filtr tekshiradi\n'
                  '  R->>I1: mos keldi -> call_next(event, data)\n'
                  '  I1->>I2: call_next(event, data)\n'
                  '  I2->>H: call_next(event, data)\n'
                  '  H-->>I2: natija qaytadi\n'
                  "  I2-->>I1: vaqt o'lchandi\n"
                  '  I1-->>O2: natija\n'
                  '  O2-->>O1: natija\n'
                  '  O1-->>U: yakuniy natija\n'
                  '</pre>\n'
                  "<p>Diagramma shuni ko'rsatadi: chaqiruv birinchi navbatda ikkita outer "
                  "middleware'dan o'tadi (bular HAR safar ishlaydi), keyingina router filtri "
                  'handlerni topadi, shundan keyingina ikkita inner middleware ishga tushadi '
                  "&mdash; va natija xuddi shu yo'lni teskari tartibda bosib qaytadi. Agar filtr "
                  'hech qanday handlerga mos kelmasa, diagrammaning "R" qadamidan keyingi qismi '
                  'umuman ishga tushmaydi &mdash; lekin ikkita outer middleware baribir '
                  "chaqirilgan bo'ladi.</p>\n"
                  '\n'
                  "<h3>Amaliy xato: ro'yxatdan o'tkazish tartibini chalkashtirib yuborish</h3>\n"
                  "<p>Eng ko'p uchraydigan xato &mdash; auth middleware'ni logging middleware'dan "
                  "<em>keyin</em> ro'yxatdan o'tkazish. Natijada, bloklangan foydalanuvchining "
                  "so'rovi ham logga tushib ulguradi (bu ba'zan kerak bo'lishi mumkin, lekin "
                  'ataylab qilinmasa &mdash; chalkashlik), yoki aksincha, auth middleware xato '
                  "bilan avval ro'yxatdan o'tsa, keyingi loggerlar ishlab ulgurmasdan javob "
                  'qaytarilishi mumkin. Middleware tartibini rejalashtirishda har doim "bu HAR '
                  'doim ishlashi kerakmi (outer) yoki faqat mos handler uchunmi (inner)" va "qaysi '
                  'middleware boshqasiga bog\'liq ma\'lumot tayyorlaydi" degan ikki savolga javob '
                  'bering.</p>',
  'text_content_ru': '<h3>Routers вложены друг в друга, Update течёт вниз</h3>\n'
                     '<p>На курсе 48 вы, возможно, использовали <code>Dispatcher</code> как единый '
                     'центр. В крупных ботах код делится на несколько <code>Router</code> '
                     '(например, <code>admin_router</code>, <code>payments_router</code>, '
                     '<code>user_router</code>), которые подключаются к основному диспетчеру через '
                     '<code>dp.include_router(...)</code>. Каждый пришедший <code>Update</code> '
                     'проверяется именно по этому дереву — начиная с внешнего диспетчера и до '
                     'внутренних routers — по очереди, пока не найдётся первый хендлер с '
                     'подходящим фильтром.</p>\n'
                     '<p>Самая важная и часто неправильно понимаемая часть этой архитектуры — два '
                     'вида <strong>middleware</strong>, время работы которых принципиально '
                     'отличается.</p>\n'
                     '\n'
                     '<h3>Outer middleware — работает всегда, до фильтра</h3>\n'
                     '<p>Middleware, зарегистрированный через <code>router.outer_middleware</code> '
                     '(или <code>dp.update.outer_middleware</code>), запускается для '
                     '<strong>каждого</strong> пришедшего апдейта — даже если ни один хендлер не '
                     'подошёл. Именно поэтому это правильное место для логики, которая «обязана '
                     'выполняться всегда» — проверка авторизации, логирование, rate-limiting: если '
                     'сделать это inner middleware, пользователь, не подходящий под фильтр '
                     '(например, написавший неизвестную команду), полностью обойдёт эту '
                     'проверку.</p>\n'
                     '\n'
                     '<h3>Inner middleware — только после того, как хендлер найден</h3>\n'
                     '<p>Middleware, зарегистрированный через <code>.middleware(...)</code> '
                     '(например, <code>router.message.middleware</code>), запускается только после '
                     'того, как фильтры уже совпали, то есть <strong>после того, как определено, '
                     'что будет вызван именно этот хендлер</strong>. Это правильное место для '
                     'вещей, зависящих от контекста хендлера — например, загрузить корзину из базы '
                     'только перед хендлером «оформить заказ» и добавить её в <code>data</code> '
                     '(паттерн, похожий на dependency injection).</p>\n'
                     '<table>\n'
                     '<tr><th>Свойство</th><th>Outer middleware</th><th>Inner '
                     'middleware</th></tr>\n'
                     '<tr><td>Когда работает</td><td>Для каждого апдейта, ДО '
                     'фильтра</td><td>Только ПОСЛЕ совпадения хендлера</td></tr>\n'
                     '<tr><td>Типичное применение</td><td>Auth, логирование, '
                     'rate-limit</td><td>Загрузка данных, контекст конкретного хендлера</td></tr>\n'
                     '<tr><td>Регистрация</td><td><code>.outer_middleware(...)</code></td><td><code>.middleware(...)</code></td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Паттерн «луковицы» (onion): call_next()</h3>\n'
                     '<p>Каждый middleware принимает два аргумента — <code>handler</code> '
                     '(следующий слой или сам хендлер) и <code>data</code> (словарь контекста). '
                     'Код до вызова <code>await handler(event, data)</code> внутри middleware '
                     'выполняется «на входе внутрь», а код <em>после</em> этого вызова — «на '
                     'выходе наружу». Поэтому middleware можно использовать не только для '
                     'предварительной проверки, но и для изменения результата после или для '
                     'измерения времени (например, Histogram в уроке 8 измерял время именно '
                     'так).</p>\n'
                     '<p>Middleware вкладываются друг в друга в порядке регистрации: первый '
                     'зарегистрированный middleware — самый внешний слой, последний — ближайший к '
                     'хендлеру. Как слои луковицы: каждый следующий middleware работает внутри '
                     'предыдущего.</p>\n'
                     '\n'
                     '<h3>Полный поток двух слоёв — диаграмма</h3>\n'
                     '<pre class="mermaid">\n'
                     'sequenceDiagram\n'
                     '  participant U as Update\n'
                     '  participant O1 as Outer MW 1 (logging)\n'
                     '  participant O2 as Outer MW 2 (auth)\n'
                     '  participant R as Router filtri\n'
                     '  participant I1 as Inner MW 1 (savat yuklash)\n'
                     "  participant I2 as Inner MW 2 (o'lchash)\n"
                     '  participant H as Handler\n'
                     '\n'
                     '  U->>O1: call_next(event, data)\n'
                     '  O1->>O2: call_next(event, data)\n'
                     '  O2->>R: filtr tekshiradi\n'
                     '  R->>I1: mos keldi -> call_next(event, data)\n'
                     '  I1->>I2: call_next(event, data)\n'
                     '  I2->>H: call_next(event, data)\n'
                     '  H-->>I2: natija qaytadi\n'
                     "  I2-->>I1: vaqt o'lchandi\n"
                     '  I1-->>O2: natija\n'
                     '  O2-->>O1: natija\n'
                     '  O1-->>U: yakuniy natija\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает: вызов сначала проходит через два outer middleware '
                     '(они срабатывают КАЖДЫЙ раз), затем фильтр Router находит хендлер, и только '
                     'тогда запускаются два inner middleware — а результат проходит тот же путь в '
                     'обратном порядке. Если фильтр не подошёл ни под один хендлер, часть '
                     'диаграммы после шага «R» вообще не выполняется — но оба outer middleware всё '
                     'равно были вызваны.</p>\n'
                     '\n'
                     '<h3>Практическая ошибка: перепутать порядок регистрации</h3>\n'
                     '<p>Самая частая ошибка — зарегистрировать auth middleware <em>после</em> '
                     'logging middleware. В результате запрос заблокированного пользователя всё '
                     'равно попадёт в лог (это иногда нужно, но если сделано не намеренно — '
                     'путаница), или наоборот, если auth middleware ошибочно зарегистрирован '
                     'первым, логгеры могут не успеть отработать до возврата ответа. При '
                     'планировании порядка middleware всегда отвечайте на два вопроса: «это ДОЛЖНО '
                     'работать всегда (outer) или только для подходящего хендлера (inner)?» и '
                     '«какой middleware готовит данные, от которых зависит другой?».</p>',
  'code_content': '# ═══════════════════════════════════════════════════════════════════════\n'
                  '# Outer va Inner middleware zanjiri: ishga tushirish tartibini isbotlash\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'from typing import Any, Awaitable, Callable, Dict\n'
                  '\n'
                  'from aiogram import BaseMiddleware, Router\n'
                  'from aiogram.types import Message, TelegramObject\n'
                  '\n'
                  '\n'
                  'class OuterLoggingMiddleware(BaseMiddleware):\n'
                  '    # Outer #1 — HAR bir update uchun ishlaydi.\n'
                  '\n'
                  '    async def __call__(self, handler, event: TelegramObject, data: Dict[str, '
                  'Any]) -> Any:\n'
                  '        print("-> OUTER logging: kirish")\n'
                  '        result = await handler(event, data)\n'
                  '        print("<- OUTER logging: chiqish")\n'
                  '        return result\n'
                  '\n'
                  '\n'
                  'class OuterAuthMiddleware(BaseMiddleware):\n'
                  '    # Outer #2 — HAR bir update uchun ishlaydi, logging ICHIDA.\n'
                  '\n'
                  '    async def __call__(self, handler, event: TelegramObject, data: Dict[str, '
                  'Any]) -> Any:\n'
                  '        print("-> OUTER auth: tekshirilmoqda")\n'
                  '        result = await handler(event, data)\n'
                  '        print("<- OUTER auth: tugadi")\n'
                  '        return result\n'
                  '\n'
                  '\n'
                  'class InnerLoadCartMiddleware(BaseMiddleware):\n'
                  '    # Inner #1 — FAQAT filtr mos kelgan handler uchun ishlaydi.\n'
                  '\n'
                  '    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> '
                  'Any:\n'
                  '        print("-> INNER savat yuklash")\n'
                  '        data["cart"] = {"items": []}  # odatda bazadan yuklanadi\n'
                  '        result = await handler(event, data)\n'
                  '        print("<- INNER savat: tozalash")\n'
                  '        return result\n'
                  '\n'
                  '\n'
                  'class InnerTimingMiddleware(BaseMiddleware):\n'
                  '    # Inner #2 — handlerga eng yaqin qatlam.\n'
                  '\n'
                  '    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> '
                  'Any:\n'
                  '        print("-> INNER timing: boshlandi")\n'
                  '        result = await handler(event, data)\n'
                  '        print("<- INNER timing: tugadi")\n'
                  '        return result\n'
                  '\n'
                  '\n'
                  'def register_middlewares(router: Router) -> None:\n'
                  "    # Ro'yxatdan o'tkazish tartibi = ichma-ich joylashish tartibi\n"
                  '    router.update.outer_middleware(OuterLoggingMiddleware())   # eng tashqi\n'
                  '    router.update.outer_middleware(OuterAuthMiddleware())\n'
                  '    router.message.middleware(InnerLoadCartMiddleware())\n'
                  '    router.message.middleware(InnerTimingMiddleware())          # handlerga eng '
                  'yaqin\n'
                  '\n'
                  '\n'
                  '# Kutilgan konsol chiqishi mos handler topilganda:\n'
                  '# -> OUTER logging: kirish\n'
                  '# -> OUTER auth: tekshirilmoqda\n'
                  '# -> INNER savat yuklash\n'
                  '# -> INNER timing: boshlandi\n'
                  '#   (handler ishlaydi)\n'
                  '# <- INNER timing: tugadi\n'
                  '# <- INNER savat: tozalash\n'
                  '# <- OUTER auth: tugadi\n'
                  '# <- OUTER logging: chiqish\n'
                  '\n'
                  '\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  "# Nested router'lar: admin_router va user_router asosiy dispetcherga ulanadi\n"
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'from aiogram import Dispatcher\n'
                  'from aiogram.filters import Command\n'
                  'from aiogram.types import Message\n'
                  '\n'
                  'admin_router = Router(name="admin")\n'
                  'user_router = Router(name="user")\n'
                  '\n'
                  '\n'
                  '@admin_router.message(Command("stats"))\n'
                  'async def cmd_stats(message: Message) -> None:\n'
                  '    await message.answer("Statistika: faol foydalanuvchilar soni ...")\n'
                  '\n'
                  '\n'
                  '@user_router.message(Command("help"))\n'
                  'async def cmd_help(message: Message) -> None:\n'
                  '    await message.answer("Yordam: /start, /help buyruqlari mavjud.")\n'
                  '\n'
                  '\n'
                  'def build_dispatcher() -> Dispatcher:\n'
                  '    dp = Dispatcher()\n'
                  "    # Outer middleware'lar ASOSIY dispetcherga qo'yiladi — shu tufayli\n"
                  "    # admin_router HAM, user_router HAM ular orqali o'tadi, chunki\n"
                  "    # include_router qilingan router'lar ota dispetcherning outer\n"
                  "    # middleware'laridan chetlanib qololmaydi.\n"
                  '    dp.update.outer_middleware(OuterLoggingMiddleware())\n'
                  '    dp.update.outer_middleware(OuterAuthMiddleware())\n'
                  '\n'
                  '    user_router.message.middleware(InnerLoadCartMiddleware())\n'
                  '    user_router.message.middleware(InnerTimingMiddleware())\n'
                  '\n'
                  '    dp.include_router(admin_router)\n'
                  '    dp.include_router(user_router)\n'
                  '    return dp\n'
                  '\n'
                  '\n'
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  "# pytest: ishga tushirish tartibini ro'yxat orqali isbotlash\n"
                  '# ═══════════════════════════════════════════════════════════════════════\n'
                  'import pytest\n'
                  '\n'
                  '\n'
                  'class RecordingMiddleware(BaseMiddleware):\n'
                  "    # Sinov uchun: har bir bosqichni umumiy ro'yxatga yozib boradi.\n"
                  '\n'
                  '    def __init__(self, name: str, trace: list):\n'
                  '        self.name = name\n'
                  '        self.trace = trace\n'
                  '\n'
                  '    async def __call__(self, handler, event, data):\n'
                  '        self.trace.append(f"-> {self.name}")\n'
                  '        result = await handler(event, data)\n'
                  '        self.trace.append(f"<- {self.name}")\n'
                  '        return result\n'
                  '\n'
                  '\n'
                  '@pytest.mark.asyncio\n'
                  'async def test_middleware_order_is_onion_shaped():\n'
                  '    trace: list[str] = []\n'
                  '    router = Router(name="test")\n'
                  '    router.update.outer_middleware(RecordingMiddleware("OUTER-1", trace))\n'
                  '    router.update.outer_middleware(RecordingMiddleware("OUTER-2", trace))\n'
                  '    router.message.middleware(RecordingMiddleware("INNER-1", trace))\n'
                  '    router.message.middleware(RecordingMiddleware("INNER-2", trace))\n'
                  '\n'
                  '    @router.message(Command("ping"))\n'
                  '    async def handler(message: Message) -> None:\n'
                  '        trace.append("HANDLER")\n'
                  '\n'
                  '    dp = Dispatcher()\n'
                  '    dp.include_router(router)\n'
                  '\n'
                  '    # _build_fake_command_update — 6-darsda ("Botlarni testlash") yozilgan\n'
                  "    # yordamchi funksiya: minimal Update/Message obyektini qo'lda quradi.\n"
                  '    fake_update = _build_fake_command_update("/ping")\n'
                  '    await dp.feed_update(bot=None, update=fake_update)\n'
                  '\n'
                  '    assert trace == [\n'
                  '        "-> OUTER-1", "-> OUTER-2", "-> INNER-1", "-> INNER-2",\n'
                  '        "HANDLER",\n'
                  '        "<- INNER-2", "<- INNER-1", "<- OUTER-2", "<- OUTER-1",\n'
                  '    ]\n',
  'code_content_ru': '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# Цепочка Outer и Inner middleware: доказываем порядок выполнения\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'from typing import Any, Awaitable, Callable, Dict\n'
                     '\n'
                     'from aiogram import BaseMiddleware, Router\n'
                     'from aiogram.types import Message, TelegramObject\n'
                     '\n'
                     '\n'
                     'class OuterLoggingMiddleware(BaseMiddleware):\n'
                     '    # Outer #1 — работает для КАЖДОГО апдейта.\n'
                     '\n'
                     '    async def __call__(self, handler, event: TelegramObject, data: Dict[str, '
                     'Any]) -> Any:\n'
                     '        print("-> OUTER logging: вход")\n'
                     '        result = await handler(event, data)\n'
                     '        print("<- OUTER logging: выход")\n'
                     '        return result\n'
                     '\n'
                     '\n'
                     'class OuterAuthMiddleware(BaseMiddleware):\n'
                     '    # Outer #2 — работает для КАЖДОГО апдейта, ВНУТРИ logging.\n'
                     '\n'
                     '    async def __call__(self, handler, event: TelegramObject, data: Dict[str, '
                     'Any]) -> Any:\n'
                     '        print("-> OUTER auth: проверка")\n'
                     '        result = await handler(event, data)\n'
                     '        print("<- OUTER auth: завершено")\n'
                     '        return result\n'
                     '\n'
                     '\n'
                     'class InnerLoadCartMiddleware(BaseMiddleware):\n'
                     '    # Inner #1 — работает ТОЛЬКО если фильтр совпал с хендлером.\n'
                     '\n'
                     '    async def __call__(self, handler, event: Message, data: Dict[str, Any]) '
                     '-> Any:\n'
                     '        print("-> INNER загрузка корзины")\n'
                     '        data["cart"] = {"items": []}  # обычно загружается из базы\n'
                     '        result = await handler(event, data)\n'
                     '        print("<- INNER корзина: очистка")\n'
                     '        return result\n'
                     '\n'
                     '\n'
                     'class InnerTimingMiddleware(BaseMiddleware):\n'
                     '    # Inner #2 — слой, ближайший к хендлеру.\n'
                     '\n'
                     '    async def __call__(self, handler, event: Message, data: Dict[str, Any]) '
                     '-> Any:\n'
                     '        print("-> INNER timing: начало")\n'
                     '        result = await handler(event, data)\n'
                     '        print("<- INNER timing: конец")\n'
                     '        return result\n'
                     '\n'
                     '\n'
                     'def register_middlewares(router: Router) -> None:\n'
                     '    # Порядок регистрации = порядок вложенности\n'
                     '    router.update.outer_middleware(OuterLoggingMiddleware())   # самый '
                     'внешний\n'
                     '    router.update.outer_middleware(OuterAuthMiddleware())\n'
                     '    router.message.middleware(InnerLoadCartMiddleware())\n'
                     '    router.message.middleware(InnerTimingMiddleware())          # ближе '
                     'всего к хендлеру\n'
                     '\n'
                     '\n'
                     '# Ожидаемый вывод в консоли, когда хендлер найден:\n'
                     '# -> OUTER logging: вход\n'
                     '# -> OUTER auth: проверка\n'
                     '# -> INNER загрузка корзины\n'
                     '# -> INNER timing: начало\n'
                     '#   (хендлер работает)\n'
                     '# <- INNER timing: конец\n'
                     '# <- INNER корзина: очистка\n'
                     '# <- OUTER auth: завершено\n'
                     '# <- OUTER logging: выход\n'
                     '\n'
                     '\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# Вложенные routers: admin_router и user_router подключаются к основному '
                     'диспетчеру\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'from aiogram import Dispatcher\n'
                     'from aiogram.filters import Command\n'
                     'from aiogram.types import Message\n'
                     '\n'
                     'admin_router = Router(name="admin")\n'
                     'user_router = Router(name="user")\n'
                     '\n'
                     '\n'
                     '@admin_router.message(Command("stats"))\n'
                     'async def cmd_stats(message: Message) -> None:\n'
                     '    await message.answer("Статистика: количество активных пользователей '
                     '...")\n'
                     '\n'
                     '\n'
                     '@user_router.message(Command("help"))\n'
                     'async def cmd_help(message: Message) -> None:\n'
                     '    await message.answer("Помощь: доступны команды /start, /help.")\n'
                     '\n'
                     '\n'
                     'def build_dispatcher() -> Dispatcher:\n'
                     '    dp = Dispatcher()\n'
                     '    # Outer middleware регистрируются на ОСНОВНОМ диспетчере — поэтому\n'
                     '    # и admin_router, И user_router проходят через них: router, '
                     'подключённый\n'
                     '    # через include_router, не может уклониться от outer middleware\n'
                     '    # родительского диспетчера.\n'
                     '    dp.update.outer_middleware(OuterLoggingMiddleware())\n'
                     '    dp.update.outer_middleware(OuterAuthMiddleware())\n'
                     '\n'
                     '    user_router.message.middleware(InnerLoadCartMiddleware())\n'
                     '    user_router.message.middleware(InnerTimingMiddleware())\n'
                     '\n'
                     '    dp.include_router(admin_router)\n'
                     '    dp.include_router(user_router)\n'
                     '    return dp\n'
                     '\n'
                     '\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     '# pytest: доказываем порядок выполнения через список записей\n'
                     '# ═══════════════════════════════════════════════════════════════════════\n'
                     'import pytest\n'
                     '\n'
                     '\n'
                     'class RecordingMiddleware(BaseMiddleware):\n'
                     '    # Для теста: записывает каждый шаг в общий список.\n'
                     '\n'
                     '    def __init__(self, name: str, trace: list):\n'
                     '        self.name = name\n'
                     '        self.trace = trace\n'
                     '\n'
                     '    async def __call__(self, handler, event, data):\n'
                     '        self.trace.append(f"-> {self.name}")\n'
                     '        result = await handler(event, data)\n'
                     '        self.trace.append(f"<- {self.name}")\n'
                     '        return result\n'
                     '\n'
                     '\n'
                     '@pytest.mark.asyncio\n'
                     'async def test_middleware_order_is_onion_shaped():\n'
                     '    trace: list[str] = []\n'
                     '    router = Router(name="test")\n'
                     '    router.update.outer_middleware(RecordingMiddleware("OUTER-1", trace))\n'
                     '    router.update.outer_middleware(RecordingMiddleware("OUTER-2", trace))\n'
                     '    router.message.middleware(RecordingMiddleware("INNER-1", trace))\n'
                     '    router.message.middleware(RecordingMiddleware("INNER-2", trace))\n'
                     '\n'
                     '    @router.message(Command("ping"))\n'
                     '    async def handler(message: Message) -> None:\n'
                     '        trace.append("HANDLER")\n'
                     '\n'
                     '    dp = Dispatcher()\n'
                     '    dp.include_router(router)\n'
                     '\n'
                     '    # _build_fake_command_update — вспомогательная функция из урока 6\n'
                     '    # («Тестирование ботов»): вручную строит минимальный объект '
                     'Update/Message.\n'
                     '    fake_update = _build_fake_command_update("/ping")\n'
                     '    await dp.feed_update(bot=None, update=fake_update)\n'
                     '\n'
                     '    assert trace == [\n'
                     '        "-> OUTER-1", "-> OUTER-2", "-> INNER-1", "-> INNER-2",\n'
                     '        "HANDLER",\n'
                     '        "<- INNER-2", "<- INNER-1", "<- OUTER-2", "<- OUTER-1",\n'
                     '    ]\n',
  'sample': {'title': "Namuna: to'rt qatlamli middleware zanjiri va uning konsol chiqishi",
             'title_ru': 'Пример: цепочка из четырёх middleware и её консольный вывод',
             'description': "Ikkita outer va ikkita inner middleware'ni ro'yxatdan o'tkazib, ishga "
                            "tushirish tartibini konsolda ko'rsatuvchi to'liq misol.",
             'description_ru': 'Полный пример регистрации двух outer и двух inner middleware, '
                               'показывающий порядок выполнения в консоли.',
             'sample_type': 'code',
             'code_files': [{'filename': 'middlewares.py',
                             'language': 'python',
                             'code': 'from aiogram import BaseMiddleware\n'
                                     '\n'
                                     'class OuterLoggingMiddleware(BaseMiddleware):\n'
                                     '    async def __call__(self, handler, event, data):\n'
                                     '        print("-> OUTER logging")\n'
                                     '        result = await handler(event, data)\n'
                                     '        print("<- OUTER logging")\n'
                                     '        return result\n'
                                     '\n'
                                     'class InnerTimingMiddleware(BaseMiddleware):\n'
                                     '    async def __call__(self, handler, event, data):\n'
                                     '        print("-> INNER timing")\n'
                                     '        result = await handler(event, data)\n'
                                     '        print("<- INNER timing")\n'
                                     '        return result\n'},
                            {'filename': 'bot.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'from aiogram import Bot, Dispatcher\n'
                                     'from aiogram.filters import CommandStart\n'
                                     'from aiogram.types import Message\n'
                                     '\n'
                                     'from middlewares import OuterLoggingMiddleware, '
                                     'InnerTimingMiddleware\n'
                                     '\n'
                                     'bot = Bot(token="123456:BOT-TOKEN")\n'
                                     'dp = Dispatcher()\n'
                                     '\n'
                                     'dp.update.outer_middleware(OuterLoggingMiddleware())\n'
                                     'dp.message.middleware(InnerTimingMiddleware())\n'
                                     '\n'
                                     '\n'
                                     '@dp.message(CommandStart())\n'
                                     'async def cmd_start(message: Message) -> None:\n'
                                     '    print("   (handler ishlamoqda)")\n'
                                     '    await message.answer("Salom!")\n'
                                     '\n'
                                     '\n'
                                     'async def main() -> None:\n'
                                     '    await dp.start_polling(bot)\n'
                                     '\n'
                                     'if __name__ == "__main__":\n'
                                     '    asyncio.run(main())\n'}]},
  'task': {'task_title': 'Amaliy mashq: middleware zanjirini qurib, tartibni isbotlang',
           'task_title_ru': 'Практика: постройте цепочку middleware и докажите порядок',
           'task_description': 'Ikkita outer va ikkita inner middleware yozing, ularni bir botga '
                               'ulang va konsol logidan ishga tushirish tartibi kutilganidek '
                               'ekanini isbotlang (skrinshot yoki log faylini ilova qiling).',
           'task_description_ru': 'Напишите два outer и два inner middleware, подключите их к боту '
                                  'и докажите по консольному логу, что порядок выполнения '
                                  'соответствует ожидаемому (приложите скриншот или лог-файл).',
           'task_requirements': 'Kamida bitta outer middleware filtrga mos kelmagan xabar uchun '
                                "ham ishga tushishini alohida ko'rsating (masalan, noma'lum matn "
                                'yuborib); inner middleware esa faqat mos handler uchun ishga '
                                'tushishini isbotlang.',
           'task_requirements_ru': 'Отдельно покажите, что хотя бы один outer middleware '
                                   'срабатывает даже для сообщения, не подошедшего ни под один '
                                   'фильтр (например, отправив произвольный текст); докажите, что '
                                   'inner middleware срабатывает только для подходящего хендлера.',
           'task_technologies': 'aiogram 3.x, BaseMiddleware, Router',
           'task_deadline_days': 5},
  'exercises': [{'title': 'Outer vs Inner middleware',
                 'title_ru': 'Outer vs Inner middleware',
                 'description': 'Qaysi middleware turi HAR bir kelgan update uchun ishlaydi, hatto '
                                'hech qanday handler mos kelmasa ham?',
                 'description_ru': 'Какой тип middleware работает для КАЖДОГО пришедшего апдейта, '
                                   'даже если ни один хендлер не подошёл?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Outer middleware',
                             'Inner middleware',
                             'Ikkalasi ham bir xil ishlaydi',
                             'Hech qaysi biri — handler har doim kerak'],
                 'options_ru': ['Outer middleware',
                                'Inner middleware',
                                'Оба работают одинаково',
                                'Ни один — хендлер всегда обязателен'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': 'Qaysi middleware filtrdan OLDIN ishga tushishini eslang.',
                 'hint_ru': 'Вспомните, какой middleware запускается ДО фильтра.',
                 'explanation': "Outer middleware .outer_middleware() orqali ro'yxatdan "
                                "o'tkaziladi va filtr natijasidan qat'i nazar har doim ishlaydi.",
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': "Ichkariga o'tish funksiyasi",
                 'title_ru': 'Функция перехода внутрь',
                 'description': 'Middleware ichida keyingi qatlamga (yoki asl handlerga) nazoratni '
                                'topshirish uchun chaqiriladigan funksiya: await ___(event, data)',
                 'description_ru': 'Функция, вызываемая внутри middleware для передачи управления '
                                   'следующему слою (или самому хендлеру): await ___(event, data)',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'handler',
                 'hint': 'Middleware __call__ metodining birinchi argumenti sifatida qabul '
                         'qilinadigan nom.',
                 'hint_ru': 'Имя, принимаемое как первый аргумент метода __call__ у middleware.',
                 'difficulty_level': 'Medium',
                 'points': 7},
                {'title': 'Konsol chiqish tartibini tartiblang',
                 'title_ru': 'Расположите порядок консольного вывода',
                 'description': "code_content'dagi namunaviy chiqishga asosan, mos handler "
                                "topilganda konsolga chiqadigan qatorlarni to'g'ri ketma-ketlikka "
                                'joylashtiring',
                 'description_ru': 'На основе примера вывода из code_content расположите строки, '
                                   'выводимые в консоль при найденном хендлере, в правильном '
                                   'порядке',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['-> OUTER logging: kirish',
                                '-> OUTER auth: tekshirilmoqda',
                                '-> INNER savat yuklash',
                                '<- INNER timing: tugadi'],
                 'drag_items_ru': ['-> OUTER logging: вход',
                                   '-> OUTER auth: проверка',
                                   '-> INNER загрузка корзины',
                                   '<- INNER timing: конец'],
                 'correct_order': ['-> OUTER logging: kirish',
                                   '-> OUTER auth: tekshirilmoqda',
                                   '-> INNER savat yuklash',
                                   '<- INNER timing: tugadi'],
                 'hint': 'Eng tashqi qatlam birinchi kiradi, eng ichki qatlam birinchi chiqadi — '
                         'piyoz naqshini eslang.',
                 'hint_ru': 'Самый внешний слой входит первым, самый внутренний выходит первым — '
                            'вспомните паттерн луковицы.',
                 'difficulty_level': 'Hard',
                 'points': 10},
                {'title': "Ro'yxatdan o'tkazish tartibi",
                 'title_ru': 'Порядок регистрации',
                 'description': "Ikkita outer middleware ro'yxatdan o'tkazilganda, birinchi "
                                "ro'yxatdan o'tkazilgani qaysi qatlamda joylashadi?",
                 'description_ru': 'Когда регистрируются два outer middleware, на каком слое '
                                   'оказывается первый зарегистрированный?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Eng tashqi qatlamda',
                             'Eng ichki qatlamda',
                             'Handlerga eng yaqin qatlamda',
                             'Tartib ahamiyatsiz, tasodifiy joylashadi'],
                 'options_ru': ['На самом внешнем слое',
                                'На самом внутреннем слое',
                                'На слое, ближайшем к хендлеру',
                                'Порядок не важен, размещается случайно'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "code_content namunasidagi izohni qayta o'qing: 'Ro'yxatdan o'tkazish "
                         "tartibi = ichma-ich joylashish tartibi'.",
                 'hint_ru': 'Перечитайте комментарий в примере code_content: «порядок регистрации '
                            '= порядок вложенности».',
                 'explanation': "Birinchi ro'yxatdan o'tkazilgan middleware eng tashqi qatlam "
                                "bo'ladi, chunki keyingi middleware'lar uning ICHIDA ro'yxatdan "
                                "o'tadi.",
                 'difficulty_level': 'Medium',
                 'points': 7}]},
 {'order': 10,
  'title': "11-Ko'p botli arxitektura (bot-farm): bitta koddan ko'p tokenlarni boshqarish",
  'title_ru': '11-Мультиботовая архитектура (bot-farm): управление множеством токенов из одного '
              'кода',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': "<h3>Bitta bot ko'p chat bilan emas — ko'p bot bitta kod bilan</h3>\n"
                  '<p>48-kursda siz bitta bot tokeni bilan minglab foydalanuvchi va guruhga xizmat '
                  'qiladigan botni qurdingiz &mdash; bu odatiy holat. Endi butunlay boshqa '
                  "masalani ko'ramiz: <strong>SaaS mahsulot</strong> qurayotganingizni tasavvur "
                  "qiling &mdash; masalan, do'kon egalari uchun &ldquo;o'z Telegram botingizni "
                  "oling&rdquo; xizmati. Har bir mijoz @BotFather'dan <em>o'zining</em> tokenini "
                  "oladi, lekin siz ularning barchasiga bitta kod bazasi, bitta handler to'plami "
                  "bilan xizmat ko'rsatasiz. Bu &ldquo;bot-farm&rdquo; yoki <strong>multi-tenant "
                  'bot arxitektura</strong> deb ataladi.</p>\n'
                  "<p>Farqni aniq ajratib olish muhim: bitta Bot obyekti ko'p chat_id bilan "
                  "gaplashishi &mdash; bu oddiy ko'p foydalanuvchili bot. Bizga kerak bo'lgani esa "
                  "&mdash; <em>ko'p Bot obyekti</em>, har biri o'z tokeni, o'z Telegram "
                  "identifikatori bilan, lekin bitta Dispatcher/handler mantig'ini bo'lishadigan "
                  'tuzilma.</p>\n'
                  '\n'
                  '<h3>Polling rejimi: bitta Dispatcher, N ta Bot obyekti</h3>\n'
                  "<p>aiogram 3.x'da <code>Dispatcher</code> handlerlarni saqlaydi, "
                  '<code>Bot</code> esa faqat Telegram API bilan gaplashish uchun HTTP mijozi. '
                  "Bitta Dispatcher'ni bir nechta Bot bilan bir vaqtda ishga tushirish mumkin "
                  "&mdash; har biri o'zining <code>get_updates</code> long-polling tsiklini "
                  "yuritadi, lekin barchasi bitta handler grafigidan o'tadi:</p>\n"
                  '<pre><code>bots = [Bot(token=t) for t in tokens_from_db]\n'
                  'await asyncio.gather(*(dp.start_polling(bot) for bot in bots))</code></pre>\n'
                  '<p>Bu yerda muhim narsa &mdash; har bir <code>start_polling</code> chaqiruvi '
                  'mustaqil asyncio task sifatida ishlaydi. Bitta tokenning tarmoq xatosi '
                  "(masalan, noto'g'ri token yoki bloklangan bot) boshqalarini to'xtatmasligi "
                  "uchun har bir taskni <code>try/except</code> bilan o'rab, xatoni logga yozib, "
                  "faqat o'sha bitta botni qayta ishga tushirish siyosatini yozish tavsiya "
                  'etiladi.</p>\n'
                  '\n'
                  "<h3>Webhook rejimi: bot_id URL yo'lida</h3>\n"
                  '<p>Polling N ta doimiy ochiq ulanish talab qiladi &mdash; bir necha yuzlab '
                  "mijozda bu resurs isrofgarchiligi. Ishlab chiqarishda ko'pincha "
                  '<strong>webhook</strong> afzal: bitta HTTP endpoint barcha botlar uchun umumiy '
                  "bo'ladi, lekin URL yo'lining bir qismi qaysi botga tegishli ekanini "
                  'bildiradi:</p>\n'
                  '<pre><code>POST /webhook/{bot_id}</code></pre>\n'
                  "<p>Endpoint <code>bot_id</code>ni URL'dan o'qiydi, xotiradagi (yoki Redis'dagi) "
                  '<code>{bot_id: Bot}</code> reestridan mos Bot obyektini topadi va '
                  "<code>Update</code>ni o'sha Bot bilan bog'liq Dispatcher chaqiruviga uzatadi: "
                  '<code>await dp.feed_update(bot=bots[bot_id], update=update)</code>. Bitta '
                  "reverse-proxy (nginx yoki bulut provayderi) barcha so'rovlarni shu bitta "
                  "endpointga yo'naltiradi &mdash; har bir mijoz uchun alohida domen yoki "
                  'sertifikat kerak emas.</p>\n'
                  '\n'
                  '<table>\n'
                  '<tr><th>Jihat</th><th>Polling (N ta Bot)</th><th>Webhook (1 ta '
                  'endpoint)</th></tr>\n'
                  '<tr><td>Ochiq ulanishlar</td><td>Har bot uchun alohida uzun '
                  "so'rov</td><td>Faqat kiruvchi HTTP so'rovlar, doimiy ulanish yo'q</td></tr>\n"
                  '<tr><td>Masshtab</td><td>Yuzlab botda protsessor/tarmoq yukini '
                  'oshiradi</td><td>Bitta jarayon minglab botga xizmat qila oladi</td></tr>\n'
                  '<tr><td>Sozlash murakkabligi</td><td>Oddiy, HTTPS/domen shart '
                  'emas</td><td>HTTPS sertifikat va ochiq domen kerak</td></tr>\n'
                  "<tr><td>Yangi mijoz qo'shish</td><td>Yangi Bot obyekti yaratib gather "
                  "ro'yxatiga qo'shish</td><td>Reestrga yozuv qo'shish, kod o'zgarmaydi</td></tr>\n"
                  '</table>\n'
                  '\n'
                  '<h3>Tenant izolyatsiyasi: bot_id &mdash; har bir kalitning old qismi</h3>\n'
                  '<p>Eng xavfli xato &mdash; barcha mijozlarning FSM holati yoki buyurtma '
                  'yozuvlari bitta umumiy jadval/kalit fazosida saqlanishi, faqat '
                  "<code>chat_id</code> bo'yicha ajratilgan holda. Muammo shundaki, ikkita "
                  '<em>turli</em> botning ikkita <em>turli</em> mijozida bir xil '
                  '<code>chat_id</code> qiymati chiqishi mumkin (Telegram chat_id botga emas, '
                  "foydalanuvchi/guruhga bog'liq, lekin turli botlarda bir xil foydalanuvchi bir "
                  'xil chat_id bilan yozishadi). Shu sababli har bir DB qatori va har bir Redis '
                  'kaliti albatta <code>bot_id</code> (yoki <code>tenant_id</code>) bilan '
                  'boshlanishi shart:</p>\n'
                  '<pre><code>fsm:{bot_id}:{chat_id}:{user_id}:state\n'
                  'buyurtmalar WHERE bot_id = :bot_id AND chat_id = :chat_id</code></pre>\n'
                  "<p>Bu bitta qatorli o'zgarish &mdash; lekin uni loyihaning boshida "
                  "qo'ymasangiz, keyinchalik minglab yozuvni migratsiya qilishga to'g'ri "
                  'keladi.</p>\n'
                  '\n'
                  '<pre class="mermaid">\n'
                  'flowchart TB\n'
                  '  DB[("bot_registry\n'
                  'jadvali (DB)")] --> R["Markaziy reestr\n'
                  'bot_id -> token"]\n'
                  '  R --> B1["Bot #1\n'
                  'tenant A tokeni"]\n'
                  '  R --> B2["Bot #2\n'
                  'tenant B tokeni"]\n'
                  '  R --> B3["Bot #N\n'
                  'tenant N tokeni"]\n'
                  '  B1 --> DP["Bitta Dispatcher\n'
                  'umumiy handlerlar"]\n'
                  '  B2 --> DP\n'
                  '  B3 --> DP\n'
                  '  DP --> SVC[("Umumiy DB / Redis\n'
                  'har yozuv bot_id bilan")]\n'
                  '  WH["Webhook proxy\n'
                  '/webhook/{bot_id}"] -->|"bot_id bo\'yicha yo\'naltiradi"| B1\n'
                  '  WH --> B2\n'
                  '  WH --> B3\n'
                  '</pre>\n'
                  "<p>Diagramma ko'rsatadiki: reestr yangi tenant qo'shilganda faqat DB'ga yozuv "
                  "qo'shadi, Dispatcher va handlerlar kod darajasida umumiy qoladi, faqat DB/Redis "
                  'yozuvlari bot_id bilan ajratiladi.</p>\n'
                  '\n'
                  "<h3>Markaziy reestr: redeploy'siz yangi mijoz qo'shish</h3>\n"
                  '<p>Reestr &mdash; oddiy jadval: <code>id, bot_id, token, tenant_name, '
                  "is_active</code>. Ishga tushishda barcha faol yozuvlar o'qiladi, har biriga Bot "
                  "obyekti yaratiladi. Yangi mijoz qo'shish &mdash; shunchaki yangi qator qo'shish "
                  "va (agar polling bo'lsa) jarayonni qayta ishga tushirish yoki (webhook bo'lsa) "
                  'reestrni davriy yangilab turish &mdash; ikkala holatda ham kodga tegmasdan. Bu '
                  'ayni SaaS mahsulotning asosiy afzalligi: bitta kod bazasi, cheksiz mijoz.</p>',
  'text_content_ru': '<h3>Не один бот с множеством чатов — а множество ботов на одном коде</h3>\n'
                     '<p>На курсе 48 вы строили бота с одним токеном, обслуживающим тысячи '
                     'пользователей и групп &mdash; это обычный случай. Теперь рассмотрим '
                     'совершенно другую задачу: представьте, что вы строите '
                     '<strong>SaaS-продукт</strong> &mdash; например, сервис &laquo;получи своего '
                     'Telegram-бота&raquo; для владельцев магазинов. Каждый клиент получает у '
                     '@BotFather <em>свой</em> токен, но вы обслуживаете их всех одной кодовой '
                     'базой, одним набором хендлеров. Это называется &laquo;bot-farm&raquo; или '
                     '<strong>мультитенантная архитектура ботов</strong>.</p>\n'
                     '<p>Важно чётко разделить: один объект Bot, разговаривающий со множеством '
                     'chat_id &mdash; это обычный многопользовательский бот. Нам же нужна '
                     '<em>структура с множеством объектов Bot</em>, каждый со своим токеном и '
                     'своим Telegram-идентификатором, но разделяющих одну логику '
                     'Dispatcher/хендлеров.</p>\n'
                     '\n'
                     '<h3>Режим polling: один Dispatcher, N объектов Bot</h3>\n'
                     '<p>В aiogram 3.x <code>Dispatcher</code> хранит хендлеры, а <code>Bot</code> '
                     '&mdash; лишь HTTP-клиент для общения с Telegram API. Один Dispatcher можно '
                     'запустить одновременно с несколькими объектами Bot &mdash; каждый ведёт свой '
                     'цикл long-polling через <code>get_updates</code>, но все проходят через один '
                     'и тот же граф хендлеров:</p>\n'
                     '<pre><code>bots = [Bot(token=t) for t in tokens_from_db]\n'
                     'await asyncio.gather(*(dp.start_polling(bot) for bot in bots))</code></pre>\n'
                     '<p>Важный момент &mdash; каждый вызов <code>start_polling</code> работает '
                     'как независимая asyncio-задача. Чтобы сетевая ошибка одного токена '
                     '(например, неверный токен или заблокированный бот) не останавливала '
                     'остальные, рекомендуется обернуть каждую задачу в <code>try/except</code>, '
                     'записывать ошибку в лог и применять политику перезапуска только для этого '
                     'одного бота.</p>\n'
                     '\n'
                     '<h3>Режим webhook: bot_id в пути URL</h3>\n'
                     '<p>Polling требует N постоянно открытых соединений &mdash; при нескольких '
                     'сотнях клиентов это расточительно по ресурсам. В продакшене чаще '
                     'предпочитают <strong>webhook</strong>: один HTTP-эндпоинт общий для всех '
                     'ботов, но часть URL-пути указывает, какому боту принадлежит запрос:</p>\n'
                     '<pre><code>POST /webhook/{bot_id}</code></pre>\n'
                     '<p>Эндпоинт читает <code>bot_id</code> из URL, находит соответствующий '
                     'объект Bot в реестре в памяти (или в Redis) вида <code>{bot_id: Bot}</code> '
                     'и передаёт <code>Update</code> в вызов Dispatcher, связанный именно с этим '
                     'Bot: <code>await dp.feed_update(bot=bots[bot_id], update=update)</code>. '
                     'Один reverse-proxy (nginx или облачный провайдер) направляет все запросы на '
                     'этот единственный эндпоинт &mdash; отдельный домен или сертификат для '
                     'каждого клиента не нужен.</p>\n'
                     '\n'
                     '<table>\n'
                     '<tr><th>Аспект</th><th>Polling (N ботов)</th><th>Webhook (1 '
                     'эндпоинт)</th></tr>\n'
                     '<tr><td>Открытые соединения</td><td>Отдельный долгий запрос на каждого '
                     'бота</td><td>Только входящие HTTP-запросы, без постоянного '
                     'соединения</td></tr>\n'
                     '<tr><td>Масштаб</td><td>Сотни ботов увеличивают нагрузку на '
                     'процессор/сеть</td><td>Один процесс обслуживает тысячи ботов</td></tr>\n'
                     '<tr><td>Сложность настройки</td><td>Просто, HTTPS/домен не '
                     'обязателен</td><td>Нужен HTTPS-сертификат и открытый домен</td></tr>\n'
                     '<tr><td>Добавление клиента</td><td>Создать новый объект Bot и добавить в '
                     'список gather</td><td>Добавить запись в реестр, код не меняется</td></tr>\n'
                     '</table>\n'
                     '\n'
                     '<h3>Изоляция тенантов: bot_id &mdash; префикс каждого ключа</h3>\n'
                     '<p>Самая опасная ошибка &mdash; хранить состояние FSM или записи заказов '
                     'всех клиентов в одной общей таблице/пространстве ключей, разделяя их только '
                     'по <code>chat_id</code>. Проблема в том, что у двух <em>разных</em> ботов у '
                     'двух <em>разных</em> клиентов может встретиться одинаковое значение '
                     '<code>chat_id</code> (chat_id в Telegram привязан к пользователю/группе, а '
                     'не к боту, поэтому один и тот же пользователь пишет разным ботам с одним и '
                     'тем же chat_id). Поэтому каждая строка БД и каждый ключ Redis обязательно '
                     'должны начинаться с <code>bot_id</code> (или <code>tenant_id</code>):</p>\n'
                     '<pre><code>fsm:{bot_id}:{chat_id}:{user_id}:state\n'
                     'buyurtmalar WHERE bot_id = :bot_id AND chat_id = :chat_id</code></pre>\n'
                     '<p>Это изменение в одну строчку &mdash; но если не заложить его с самого '
                     'начала проекта, позже придётся мигрировать тысячи записей.</p>\n'
                     '\n'
                     '<pre class="mermaid">\n'
                     'flowchart TB\n'
                     '  DB[("Таблица\n'
                     'bot_registry (БД)")] --> R["Центральный реестр\n'
                     'bot_id -> token"]\n'
                     '  R --> B1["Bot #1\n'
                     'токен тенанта A"]\n'
                     '  R --> B2["Bot #2\n'
                     'токен тенанта B"]\n'
                     '  R --> B3["Bot #N\n'
                     'токен тенанта N"]\n'
                     '  B1 --> DP["Один Dispatcher\n'
                     'общие хендлеры"]\n'
                     '  B2 --> DP\n'
                     '  B3 --> DP\n'
                     '  DP --> SVC[("Общая БД / Redis\n'
                     'каждая запись с bot_id")]\n'
                     '  WH["Webhook proxy\n'
                     '/webhook/{bot_id}"] -->|"направляет по bot_id"| B1\n'
                     '  WH --> B2\n'
                     '  WH --> B3\n'
                     '</pre>\n'
                     '<p>Диаграмма показывает: при добавлении нового тенанта реестр получает лишь '
                     'новую запись в БД, Dispatcher и хендлеры остаются общими на уровне кода, а '
                     'записи БД/Redis разделяются только через bot_id.</p>\n'
                     '\n'
                     '<h3>Центральный реестр: новый клиент без redeploy</h3>\n'
                     '<p>Реестр &mdash; обычная таблица: <code>id, bot_id, token, tenant_name, '
                     'is_active</code>. При запуске считываются все активные записи, для каждой '
                     'создаётся объект Bot. Добавление нового клиента &mdash; это просто '
                     'добавление новой строки и (при polling) перезапуск процесса, либо (при '
                     'webhook) периодическое обновление реестра &mdash; в обоих случаях без '
                     'изменения кода. Это и есть главное преимущество SaaS-продукта: одна кодовая '
                     'база, неограниченное число клиентов.</p>',
  'code_content': '"""Multi-bot (bot-farm) polling launcher.\n'
                  '\n'
                  'Bitta kod bazasi, N ta mustaqil Bot obyekti, bitta umumiy Dispatcher.\n'
                  "Har bir tenant bot_registry jadvalidan o'qiladi; kodni o'zgartirmasdan\n"
                  "yangi qator qo'shish orqali yangi mijoz ulanadi.\n"
                  '"""\n'
                  'import asyncio\n'
                  'import logging\n'
                  'from dataclasses import dataclass\n'
                  '\n'
                  'from aiogram import Bot, Dispatcher, Router\n'
                  'from aiogram.filters import CommandStart\n'
                  'from aiogram.types import Message\n'
                  'from aiogram.client.default import DefaultBotProperties\n'
                  'from aiogram.enums import ParseMode\n'
                  '\n'
                  'logger = logging.getLogger("bot_farm")\n'
                  '\n'
                  '\n'
                  '@dataclass(frozen=True)\n'
                  'class TenantConfig:\n'
                  '    bot_id: int\n'
                  '    token: str\n'
                  '    tenant_name: str\n'
                  '\n'
                  '\n'
                  'async def load_active_tenants(db) -> list[TenantConfig]:\n'
                  '    """bot_registry jadvalidan faol tenantlarni o\'qiydi."""\n'
                  '    rows = await db.fetch_all(\n'
                  '        "SELECT bot_id, token, tenant_name FROM bot_registry WHERE is_active = '
                  'true"\n'
                  '    )\n'
                  '    return [TenantConfig(r["bot_id"], r["token"], r["tenant_name"]) for r in '
                  'rows]\n'
                  '\n'
                  '\n'
                  'router = Router(name="shared-handlers")\n'
                  '\n'
                  '\n'
                  '@router.message(CommandStart())\n'
                  'async def cmd_start(message: Message, bot: Bot) -> None:\n'
                  "    # bot.id — aiogram avtomatik to'ldiradi (get_me orqali), shu yerdan\n"
                  "    # qaysi tenant ekanini bilib olamiz, keyingi so'rovlarda bot_id\n"
                  '    # sifatida ishlatamiz.\n'
                  '    me = await bot.get_me()\n'
                  '    await message.answer(\n'
                  '        f"Salom! Siz @{me.username} boti bilan gaplashyapsiz "\n'
                  '        f"(bot_id={bot.id})."\n'
                  '    )\n'
                  '\n'
                  '\n'
                  'async def run_one_bot(dp: Dispatcher, bot: Bot, tenant: TenantConfig) -> None:\n'
                  '    """Bitta tenant uchun polling tsikli — xato boshqalarni to\'xtatmaydi."""\n'
                  '    try:\n'
                  '        logger.info("tenant %s (bot_id=%s) polling boshlandi", '
                  'tenant.tenant_name, tenant.bot_id)\n'
                  '        await dp.start_polling(bot, handle_signals=False)\n'
                  '    except Exception:\n'
                  '        logger.exception("tenant %s (bot_id=%s) polling\'da xato", '
                  'tenant.tenant_name, tenant.bot_id)\n'
                  '    finally:\n'
                  '        await bot.session.close()\n'
                  '\n'
                  '\n'
                  'async def main(db) -> None:\n'
                  '    dp = Dispatcher()\n'
                  '    dp.include_router(router)\n'
                  '\n'
                  '    tenants = await load_active_tenants(db)\n'
                  '    if not tenants:\n'
                  '        logger.warning("faol tenant topilmadi")\n'
                  '        return\n'
                  '\n'
                  '    bots = {\n'
                  '        t.bot_id: Bot(\n'
                  '            token=t.token,\n'
                  '            default=DefaultBotProperties(parse_mode=ParseMode.HTML),\n'
                  '        )\n'
                  '        for t in tenants\n'
                  '    }\n'
                  '\n'
                  '    await asyncio.gather(\n'
                  '        *(run_one_bot(dp, bots[t.bot_id], t) for t in tenants)\n'
                  '    )\n'
                  '\n'
                  '\n'
                  "# ── Webhook rejimi uchun yo'naltiruvchi (aiohttp misolida) ──────────────\n"
                  'from aiohttp import web\n'
                  'from aiogram.types import Update\n'
                  '\n'
                  "BOTS_REGISTRY: dict[int, Bot] = {}   # ishga tushishda load_active_tenants'dan "
                  "to'ldiriladi\n"
                  'DISPATCHER: Dispatcher | None = None\n'
                  '\n'
                  '\n'
                  'async def webhook_handler(request: web.Request) -> web.Response:\n'
                  '    bot_id = int(request.match_info["bot_id"])\n'
                  '    bot = BOTS_REGISTRY.get(bot_id)\n'
                  '    if bot is None:\n'
                  "        # Mavjud bo'lmagan yoki o'chirilgan tenant — 404, xato jim yutilmaydi.\n"
                  '        return web.Response(status=404, text="unknown bot_id")\n'
                  '\n'
                  '    data = await request.json()\n'
                  '    update = Update.model_validate(data)\n'
                  '    assert DISPATCHER is not None\n'
                  '    await DISPATCHER.feed_update(bot=bot, update=update)\n'
                  '    return web.Response(status=200)\n'
                  '\n'
                  '\n'
                  'def build_webhook_app() -> web.Application:\n'
                  '    app = web.Application()\n'
                  '    app.router.add_post("/webhook/{bot_id}", webhook_handler)\n'
                  '    return app\n'
                  '\n'
                  '\n'
                  'if __name__ == "__main__":\n'
                  '    # db — loyihangizning haqiqiy DB ulanish obyekti bilan almashtiriladi\n'
                  '    asyncio.run(main(db=None))',
  'code_content_ru': '"""Мультиботовый (bot-farm) polling-лаунчер.\n'
                     '\n'
                     'Одна кодовая база, N независимых объектов Bot, один общий Dispatcher.\n'
                     'Каждый тенант читается из таблицы bot_registry; новый клиент\n'
                     'подключается добавлением строки, без изменения кода.\n'
                     '"""\n'
                     'import asyncio\n'
                     'import logging\n'
                     'from dataclasses import dataclass\n'
                     '\n'
                     'from aiogram import Bot, Dispatcher, Router\n'
                     'from aiogram.filters import CommandStart\n'
                     'from aiogram.types import Message\n'
                     'from aiogram.client.default import DefaultBotProperties\n'
                     'from aiogram.enums import ParseMode\n'
                     '\n'
                     'logger = logging.getLogger("bot_farm")\n'
                     '\n'
                     '\n'
                     '@dataclass(frozen=True)\n'
                     'class TenantConfig:\n'
                     '    bot_id: int\n'
                     '    token: str\n'
                     '    tenant_name: str\n'
                     '\n'
                     '\n'
                     'async def load_active_tenants(db) -> list[TenantConfig]:\n'
                     '    """Считывает активных тенантов из таблицы bot_registry."""\n'
                     '    rows = await db.fetch_all(\n'
                     '        "SELECT bot_id, token, tenant_name FROM bot_registry WHERE is_active '
                     '= true"\n'
                     '    )\n'
                     '    return [TenantConfig(r["bot_id"], r["token"], r["tenant_name"]) for r in '
                     'rows]\n'
                     '\n'
                     '\n'
                     'router = Router(name="shared-handlers")\n'
                     '\n'
                     '\n'
                     '@router.message(CommandStart())\n'
                     'async def cmd_start(message: Message, bot: Bot) -> None:\n'
                     '    # bot.id — aiogram заполняет автоматически (через get_me), отсюда\n'
                     '    # узнаём, какой это тенант, и используем как bot_id в дальнейших '
                     'запросах.\n'
                     '    me = await bot.get_me()\n'
                     '    await message.answer(\n'
                     '        f"Привет! Вы общаетесь с ботом @{me.username} "\n'
                     '        f"(bot_id={bot.id})."\n'
                     '    )\n'
                     '\n'
                     '\n'
                     'async def run_one_bot(dp: Dispatcher, bot: Bot, tenant: TenantConfig) -> '
                     'None:\n'
                     '    """Цикл polling для одного тенанта — ошибка не останавливает '
                     'остальных."""\n'
                     '    try:\n'
                     '        logger.info("tenant %s (bot_id=%s) polling запущен", '
                     'tenant.tenant_name, tenant.bot_id)\n'
                     '        await dp.start_polling(bot, handle_signals=False)\n'
                     '    except Exception:\n'
                     '        logger.exception("tenant %s (bot_id=%s) ошибка в polling", '
                     'tenant.tenant_name, tenant.bot_id)\n'
                     '    finally:\n'
                     '        await bot.session.close()\n'
                     '\n'
                     '\n'
                     'async def main(db) -> None:\n'
                     '    dp = Dispatcher()\n'
                     '    dp.include_router(router)\n'
                     '\n'
                     '    tenants = await load_active_tenants(db)\n'
                     '    if not tenants:\n'
                     '        logger.warning("активные тенанты не найдены")\n'
                     '        return\n'
                     '\n'
                     '    bots = {\n'
                     '        t.bot_id: Bot(\n'
                     '            token=t.token,\n'
                     '            default=DefaultBotProperties(parse_mode=ParseMode.HTML),\n'
                     '        )\n'
                     '        for t in tenants\n'
                     '    }\n'
                     '\n'
                     '    await asyncio.gather(\n'
                     '        *(run_one_bot(dp, bots[t.bot_id], t) for t in tenants)\n'
                     '    )\n'
                     '\n'
                     '\n'
                     '# ── Режим webhook: маршрутизатор (на примере aiohttp) ───────────────────\n'
                     'from aiohttp import web\n'
                     'from aiogram.types import Update\n'
                     '\n'
                     'BOTS_REGISTRY: dict[int, Bot] = {}   # заполняется при старте из '
                     'load_active_tenants\n'
                     'DISPATCHER: Dispatcher | None = None\n'
                     '\n'
                     '\n'
                     'async def webhook_handler(request: web.Request) -> web.Response:\n'
                     '    bot_id = int(request.match_info["bot_id"])\n'
                     '    bot = BOTS_REGISTRY.get(bot_id)\n'
                     '    if bot is None:\n'
                     '        # Несуществующий или отключённый тенант — 404, ошибка не молчит.\n'
                     '        return web.Response(status=404, text="unknown bot_id")\n'
                     '\n'
                     '    data = await request.json()\n'
                     '    update = Update.model_validate(data)\n'
                     '    assert DISPATCHER is not None\n'
                     '    await DISPATCHER.feed_update(bot=bot, update=update)\n'
                     '    return web.Response(status=200)\n'
                     '\n'
                     '\n'
                     'def build_webhook_app() -> web.Application:\n'
                     '    app = web.Application()\n'
                     '    app.router.add_post("/webhook/{bot_id}", webhook_handler)\n'
                     '    return app\n'
                     '\n'
                     '\n'
                     'if __name__ == "__main__":\n'
                     '    # db — заменяется на реальный объект подключения к БД вашего проекта\n'
                     '    asyncio.run(main(db=None))',
  'sample': {'title': "Namuna: ko'p botli tizim uchun polling launcher va webhook yo'naltiruvchi",
             'description': 'Bitta koddan N ta tenant botni ishga tushirish (polling) va bot_id '
                            "bo'yicha yo'naltirish (webhook)",
             'sample_type': 'code',
             'code_files': [{'filename': 'bot_farm_launcher.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'from aiogram import Bot, Dispatcher, Router\n'
                                     'from aiogram.filters import CommandStart\n'
                                     'from aiogram.types import Message\n'
                                     '\n'
                                     'router = Router()\n'
                                     '\n'
                                     '\n'
                                     '@router.message(CommandStart())\n'
                                     'async def start(message: Message, bot: Bot) -> None:\n'
                                     '    me = await bot.get_me()\n'
                                     '    await message.answer(f"Bot_id={bot.id}, '
                                     'username=@{me.username}")\n'
                                     '\n'
                                     '\n'
                                     'async def main(tokens: list[str]) -> None:\n'
                                     '    dp = Dispatcher()\n'
                                     '    dp.include_router(router)\n'
                                     '    bots = [Bot(token=t) for t in tokens]\n'
                                     '    await asyncio.gather(*(dp.start_polling(b) for b in '
                                     'bots))\n'
                                     '\n'
                                     '\n'
                                     'if __name__ == "__main__":\n'
                                     '    asyncio.run(main(tokens=["TOKEN_A", "TOKEN_B", '
                                     '"TOKEN_C"]))'},
                            {'filename': 'webhook_router.py',
                             'language': 'python',
                             'code': 'from aiohttp import web\n'
                                     'from aiogram import Bot, Dispatcher\n'
                                     'from aiogram.types import Update\n'
                                     '\n'
                                     'bots_by_id: dict[int, Bot] = {}\n'
                                     'dp = Dispatcher()\n'
                                     '\n'
                                     '\n'
                                     'async def handle(request: web.Request) -> web.Response:\n'
                                     '    bot_id = int(request.match_info["bot_id"])\n'
                                     '    bot = bots_by_id.get(bot_id)\n'
                                     '    if bot is None:\n'
                                     '        return web.Response(status=404, text="unknown '
                                     'bot_id")\n'
                                     '    update = Update.model_validate(await request.json())\n'
                                     '    await dp.feed_update(bot=bot, update=update)\n'
                                     '    return web.Response()\n'
                                     '\n'
                                     '\n'
                                     'app = web.Application()\n'
                                     'app.router.add_post("/webhook/{bot_id}", handle)'}]},
  'task': {'task_title': 'Amaliy loyiha: ikki tenantli bot-farm prototipi',
           'task_title_ru': 'Практический проект: прототип bot-farm с двумя тенантами',
           'task_description': "Bitta umumiy Dispatcher va handler to'plamiga ega, lekin ikkita "
                               'mustaqil bot tokeni bilan bir vaqtda ishlaydigan polling-launcher '
                               'yozing. Har bir tenant uchun bot_id, token va tenant_name '
                               'saqlaydigan oddiy jadval (yoki JSON fayl) reestr sifatida '
                               'ishlating.',
           'task_description_ru': 'Напишите polling-лаунчер с одним общим Dispatcher и набором '
                                  'хендлеров, который одновременно обслуживает два независимых '
                                  'токена бота. Используйте простую таблицу (или JSON-файл) с '
                                  'bot_id, token и tenant_name как реестр.',
           'task_requirements': "1) Reestrdan kamida 2 ta tenant o'qilishi kerak. 2) /start "
                                "buyrug'i javobida aynan qaysi bot_id orqali yozilganini "
                                "ko'rsating. 3) Bitta tokenning xatosi ikkinchisini "
                                "to'xtatmasligini try/except bilan ta'minlang. 4) Har bir FSM/DB "
                                "yozuvi bot_id bilan boshlanishi kerak (hech bo'lmasa log "
                                "darajasida ko'rsating).",
           'task_requirements_ru': '1) Из реестра должно читаться минимум 2 тенанта. 2) В ответе '
                                   'на /start показывать, через какой именно bot_id пришло '
                                   'сообщение. 3) Ошибка одного токена не должна останавливать '
                                   'другой — обеспечить через try/except. 4) Каждая запись FSM/БД '
                                   'должна начинаться с bot_id (показать хотя бы в логах).',
           'task_technologies': 'aiogram 3.x, asyncio.gather, Dispatcher, multi-tenant',
           'task_deadline_days': 4},
  'exercises': [{'title': 'Nega har bir kalit bot_id bilan boshlanishi kerak?',
                 'title_ru': 'Почему каждый ключ должен начинаться с bot_id?',
                 'description': "Ko'p botli tizimda FSM kaliti nima uchun albatta bot_id bilan "
                                'boshlanishi kerak?',
                 'description_ru': 'Почему в мультиботовой системе ключ FSM обязательно должен '
                                   'начинаться с bot_id?',
                 'exercise_type': 'multiple_choice',
                 'options': ['Chunki turli botlarda bir xil chat_id qiymati takrorlanishi mumkin, '
                             "aks holda tenantlar ma'lumoti aralashib ketadi",
                             'Chunki Redis kalitlari faqat raqamlardan boshlanishi kerak',
                             'Chunki aiogram buni majburiy talab qiladi va boshqacha ishlamaydi',
                             "Chunki bot_id har doim chat_id'dan katta bo'lishi kerak"],
                 'options_ru': ['Потому что в разных ботах может повториться одинаковое значение '
                                'chat_id, иначе данные тенантов перемешаются',
                                'Потому что ключи Redis обязательно должны начинаться с цифр',
                                'Потому что aiogram требует этого в обязательном порядке и иначе '
                                'не работает',
                                'Потому что bot_id всегда должен быть больше chat_id'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "chat_id foydalanuvchi/guruhga bog'liq, botga emas — shu sababli turli "
                         'botlarda takrorlanishi mumkin.',
                 'hint_ru': 'chat_id привязан к пользователю/группе, а не к боту — поэтому может '
                            'повторяться в разных ботах.',
                 'explanation': "chat_id Telegram foydalanuvchisiga bog'liq bo'lgani uchun ikkita "
                                'turli botda bir xil qiymat chiqishi mumkin; bot_id shu '
                                'qiymatlarni ajratib turadi.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': "Ko'p bot polling'ni bitta vaqtda ishga tushirish",
                 'title_ru': 'Запуск нескольких ботов polling одновременно',
                 'description': 'N ta Bot obyektini bitta Dispatcher bilan bir vaqtda ishga '
                                "tushirish uchun asyncio'ning qaysi funksiyasi ishlatiladi: "
                                'asyncio.___(*(dp.start_polling(b) for b in bots))',
                 'description_ru': 'Какая функция asyncio используется для одновременного запуска '
                                   'N объектов Bot с одним Dispatcher: '
                                   'asyncio.___(*(dp.start_polling(b) for b in bots))',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'gather',
                 'hint': "Bir nechta coroutine'ni parallel kutish uchun ishlatiladigan standart "
                         'asyncio funksiyasi.',
                 'hint_ru': 'Стандартная функция asyncio для параллельного ожидания нескольких '
                            'корутин.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': "Yangi tenant qo'shish qadamlari",
                 'title_ru': 'Шаги добавления нового тенанта',
                 'description': "Kodni o'zgartirmasdan yangi mijoz botini ulash qadamlarini "
                                "to'g'ri tartibga joylashtiring",
                 'description_ru': 'Расположите в правильном порядке шаги подключения бота нового '
                                   'клиента без изменения кода',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ["@BotFather'dan yangi token olish",
                                "bot_registry jadvaliga yangi qator qo'shish (bot_id, token, "
                                'tenant_name)',
                                'Jarayonni qayta ishga tushirish yoki webhook reestrini yangilash',
                                "Yangi bot Telegram'da ishlay boshlaydi"],
                 'drag_items_ru': ['Получить новый токен у @BotFather',
                                   'Добавить новую строку в таблицу bot_registry (bot_id, token, '
                                   'tenant_name)',
                                   'Перезапустить процесс или обновить реестр webhook',
                                   'Новый бот начинает работать в Telegram'],
                 'correct_order': ["@BotFather'dan yangi token olish",
                                   "bot_registry jadvaliga yangi qator qo'shish (bot_id, token, "
                                   'tenant_name)',
                                   'Jarayonni qayta ishga tushirish yoki webhook reestrini '
                                   'yangilash',
                                   "Yangi bot Telegram'da ishlay boshlaydi"],
                 'hint': "Avval token olinadi, keyin reestrga yoziladi, keyin tizim uni o'qishi "
                         'kerak.',
                 'hint_ru': 'Сначала получаем токен, затем записываем в реестр, затем система '
                            'должна его прочитать.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 11,
  'title': "12-Ko'p tilli botlar uchun i18n",
  'title_ru': '12-Интернационализация (i18n) для многоязычных ботов',
  'points_reward': 17,
  'code_language': 'python',
  'text_content': "<h3>Nega hardcode qilingan matn ko'p tillilikka ishlamaydi</h3>\n"
                  '<p>48-kursdagi botda har bir <code>message.answer("Salom!")</code> qatorida '
                  "matn to'g'ridan-to'g'ri kodga yozilgan edi. Bitta til uchun bu yetarli, lekin "
                  "O'zbekiston, Rossiya va boshqa mintaqalardagi foydalanuvchilarga xizmat "
                  'qiladigan bot uchun har bir matnni uchta joyda &mdash; kodda, keyin har bir '
                  "tilga tarjima qilinganda &mdash; qayta yozish imkonsiz bo'lib qoladi. Yechim "
                  '&mdash; matnni koddan <strong>ajratish</strong>: kodda faqat '
                  '&ldquo;kalit&rdquo; qoladi, haqiqiy matn tashqi tarjima fayllarida '
                  'saqlanadi.</p>\n'
                  '\n'
                  '<h3>gettext ekotizimi: .pot &rarr; .po &rarr; .mo</h3>\n'
                  '<p>Python dunyosida bu standart <code>gettext</code> mexanizmi orqali qilinadi. '
                  "Ish jarayoni to'rt bosqichdan iborat:</p>\n"
                  '<ol>\n'
                  '<li>Kodda tarjima qilinadigan har bir matnni <code>_("Salom!")</code> '
                  "ko'rinishida belgilaysiz (funksiya nomi shartli &mdash; odatda pastki "
                  'chiziqcha).</li>\n'
                  '<li><code>pybabel extract</code> (yoki <code>xgettext</code>) butun kodni '
                  'skanerlab, barcha <code>_("...")</code> chaqiruvlarini yig\'ib, '
                  "<strong>.pot</strong> shablon faylini yaratadi &mdash; bu asl matnlar ro'yxati, "
                  'hali tarjimasiz.</li>\n'
                  '<li>Har bir til uchun .pot asosida <strong>.po</strong> fayl yaratiladi '
                  '(masalan <code>ru/LC_MESSAGES/messages.po</code>), tarjimon shu yerga rus '
                  'tilidagi variantni yozadi.</li>\n'
                  '<li><code>pybabel compile</code> .po faylni ikkilik <strong>.mo</strong> '
                  "formatga o'giradi &mdash; runtime aynan shu faylni tez o'qiydi, matn qidirish "
                  'uchun matnli faylni har safar parse qilmaydi.</li>\n'
                  '</ol>\n'
                  '<pre class="mermaid">\n'
                  'flowchart LR\n'
                  '  A["Kod: _(\'Salom!\')"] --> B["pybabel extract"]\n'
                  '  B --> C[".pot shablon"]\n'
                  '  C --> D1["uz/messages.po"]\n'
                  '  C --> D2["ru/messages.po"]\n'
                  '  D1 --> E1["pybabel compile"]\n'
                  '  D2 --> E2["pybabel compile"]\n'
                  '  E1 --> F1[".mo (uz)"]\n'
                  '  E2 --> F2[".mo (ru)"]\n'
                  '  F1 --> G["Runtime: locale bo\'yicha tanlash"]\n'
                  '  F2 --> G\n'
                  '</pre>\n'
                  '<p>Diagrammadagi eng muhim joy &mdash; oxirgi qadam: runtime hech qachon .po '
                  "yoki .pot faylni o'qimaydi, faqat oldindan compile qilingan .mo'ni. Shuning "
                  'uchun tarjimani yangilagach <code>pybabel compile</code>ni qayta ishga '
                  'tushirishni unutmang &mdash; aks holda eski tarjima serverda qolib ketadi.</p>\n'
                  '\n'
                  '<h3>Foydalanuvchi tilini aniqlash: middleware orqali</h3>\n'
                  '<p>Har bir Telegram <code>User</code> obyektida <code>language_code</code> '
                  'maydoni bor &mdash; bu foydalanuvchining Telegram ilovasidagi til sozlamasi, '
                  "<em>botni qanday tilda ishlatmoqchi ekanidan</em> farqli bo'lishi mumkin "
                  "(masalan, ilova ingliz tilida, lekin foydalanuvchi botdan o'zbekcha javob "
                  "kutishi mumkin). Shu sababli ko'plab botlar birinchi ishga tushirishda tilni "
                  "so'raydi va tanlovni bazaga saqlaydi, keyin har safar shu saqlangan qiymatdan "
                  "foydalanadi, faqat hali tanlanmagan bo'lsa <code>language_code</code>ga "
                  'tayanadi.</p>\n'
                  '<p>Bu mantiq &mdash; <strong>outer middleware</strong>da joylashtiriladi '
                  "(9-darsda ko'rgan zanjir tartibini eslang): har bir update kelganda "
                  "foydalanuvchi tilini DB'dan (yoki keshdan) o'qib, uni joriy update kontekstiga "
                  '(masalan, <code>aiogram-i18n</code>ning <code>I18nMiddleware</code>i yoki oddiy '
                  "<code>ContextVar</code>) o'rnatadi. Shu tufayli handler ichidagi har bir "
                  '<code>_("...")</code> chaqiruvi &mdash; hech qanday qo\'shimcha parametrsiz '
                  "&mdash; to'g'ri tilni topadi.</p>\n"
                  '\n'
                  "<h3>Ko'plik shakllari: ngettext</h3>\n"
                  "<p>Ingliz tilida ko'plik oddiy: &ldquo;1 item&rdquo; / &ldquo;2 items&rdquo;. "
                  "Lekin rus va o'zbek tillarida qoidalar boshqacha &mdash; rus tilida uchta shakl "
                  "bor (1, 2-4, 5+ uchun alohida), o'zbek tilida esa son ko'pincha o'zgarmaydi "
                  "(&ldquo;5 ta kitob&rdquo;, &ldquo;1 ta kitob&rdquo; &mdash; so'z shakli bir "
                  'xil). <code>ngettext(singular, plural, n)</code> funksiyasi aynan shu '
                  "til-bo'yicha qoidani .po faylidagi <code>Plural-Forms</code> sarlavhasidan "
                  "o'qib, to'g'ri variantni tanlaydi &mdash; dasturchi o'zi <code>if n == 1</code> "
                  "yozib o'tirmaydi.</p>\n"
                  '\n'
                  "<h3>Tarjima yo'qolganda: fallback</h3>\n"
                  "<p>Agar yangi matn qo'shilgan-u, lekin hali rus tiliga tarjima qilinmagan "
                  "bo'lsa, <code>gettext</code> standart xatti-harakati &mdash; kalitning o'zini "
                  "(odatda manba til matnini) qaytarish, xato tashlamaslik yoki bo'sh qator "
                  "ko'rsatmaslik. Bu muhim: foydalanuvchi hech bo'lmasa manba tildagi tushunarli "
                  "matnni ko'radi, dastur qulamaydi va &ldquo;MISSING_KEY&rdquo; kabi texnik xabar "
                  'chiqmaydi.</p>',
  'text_content_ru': '<h3>Почему захардкоженный текст не масштабируется на многоязычность</h3>\n'
                     '<p>В боте курса 48 каждая строка вида <code>message.answer("Salom!")</code> '
                     'содержала текст прямо в коде. Для одного языка этого достаточно, но для '
                     'бота, обслуживающего пользователей из Узбекистана, России и других регионов, '
                     'переписывать каждый текст в трёх местах &mdash; в коде, а затем при переводе '
                     'на каждый язык &mdash; становится невозможным. Решение &mdash; '
                     '<strong>отделить</strong> текст от кода: в коде остаётся только '
                     '&laquo;ключ&raquo;, а сам текст хранится во внешних файлах перевода.</p>\n'
                     '\n'
                     '<h3>Экосистема gettext: .pot &rarr; .po &rarr; .mo</h3>\n'
                     '<p>В мире Python это делается через стандартный механизм '
                     '<code>gettext</code>. Рабочий процесс состоит из четырёх шагов:</p>\n'
                     '<ol>\n'
                     '<li>В коде вы помечаете каждый переводимый текст как '
                     '<code>_("Salom!")</code> (имя функции условно &mdash; обычно нижнее '
                     'подчёркивание).</li>\n'
                     '<li><code>pybabel extract</code> (или <code>xgettext</code>) сканирует весь '
                     'код, собирает все вызовы <code>_("...")</code> и создаёт файл-шаблон '
                     '<strong>.pot</strong> &mdash; список исходных текстов, ещё без '
                     'перевода.</li>\n'
                     '<li>Для каждого языка на основе .pot создаётся файл <strong>.po</strong> '
                     '(например <code>ru/LC_MESSAGES/messages.po</code>), куда переводчик '
                     'вписывает вариант на русском языке.</li>\n'
                     '<li><code>pybabel compile</code> превращает .po файл в бинарный формат '
                     '<strong>.mo</strong> &mdash; именно его быстро читает runtime, не разбирая '
                     'текстовый файл заново при каждом поиске.</li>\n'
                     '</ol>\n'
                     '<pre class="mermaid">\n'
                     'flowchart LR\n'
                     '  A["Код: _(\'Salom!\')"] --> B["pybabel extract"]\n'
                     '  B --> C[".pot шаблон"]\n'
                     '  C --> D1["uz/messages.po"]\n'
                     '  C --> D2["ru/messages.po"]\n'
                     '  D1 --> E1["pybabel compile"]\n'
                     '  D2 --> E2["pybabel compile"]\n'
                     '  E1 --> F1[".mo (uz)"]\n'
                     '  E2 --> F2[".mo (ru)"]\n'
                     '  F1 --> G["Runtime: выбор по locale"]\n'
                     '  F2 --> G\n'
                     '</pre>\n'
                     '<p>Самое важное место на диаграмме &mdash; последний шаг: runtime никогда не '
                     'читает .po или .pot файл, только заранее скомпилированный .mo. Поэтому после '
                     'обновления перевода не забывайте заново запускать <code>pybabel '
                     'compile</code> &mdash; иначе на сервере останется старый перевод.</p>\n'
                     '\n'
                     '<h3>Определение языка пользователя: через middleware</h3>\n'
                     '<p>У каждого Telegram-объекта <code>User</code> есть поле '
                     '<code>language_code</code> &mdash; это настройка языка в приложении Telegram '
                     'у пользователя, которая может отличаться от того, <em>на каком языке он '
                     'хочет использовать бота</em> (например, приложение на английском, но '
                     'пользователь ожидает от бота ответы на узбекском). Поэтому многие боты при '
                     'первом запуске спрашивают язык и сохраняют выбор в базе, а затем каждый раз '
                     'используют это сохранённое значение, полагаясь на <code>language_code</code> '
                     'только если выбор ещё не сделан.</p>\n'
                     '<p>Эта логика размещается в <strong>outer middleware</strong> (вспомните '
                     'порядок цепочки из 9-го урока): при каждом входящем update читается язык '
                     'пользователя из БД (или кеша) и устанавливается в контекст текущего update '
                     '(например, через <code>I18nMiddleware</code> пакета '
                     '<code>aiogram-i18n</code> или через обычный <code>ContextVar</code>). '
                     'Благодаря этому каждый вызов <code>_("...")</code> внутри хендлера &mdash; '
                     'без каких-либо дополнительных параметров &mdash; находит нужный язык.</p>\n'
                     '\n'
                     '<h3>Формы множественного числа: ngettext</h3>\n'
                     '<p>В английском языке множественное число простое: &laquo;1 item&raquo; / '
                     '&laquo;2 items&raquo;. Но в русском и узбекском правила другие &mdash; в '
                     'русском есть три формы (отдельно для 1, для 2-4, для 5+), в узбекском же '
                     'слово чаще не меняется вовсе (&laquo;5 ta kitob&raquo;, &laquo;1 ta '
                     'kitob&raquo; &mdash; форма слова одна и та же). Функция '
                     '<code>ngettext(singular, plural, n)</code> считывает именно это языковое '
                     'правило из заголовка <code>Plural-Forms</code> в .po файле и сама выбирает '
                     'нужный вариант &mdash; разработчику не нужно писать <code>if n == 1</code> '
                     'вручную.</p>\n'
                     '\n'
                     '<h3>Когда перевод отсутствует: fallback</h3>\n'
                     '<p>Если добавлен новый текст, но он ещё не переведён на русский, стандартное '
                     'поведение <code>gettext</code> &mdash; вернуть сам ключ (обычно это и есть '
                     'текст на исходном языке), не выбрасывая ошибку и не показывая пустую строку. '
                     'Это важно: пользователь хотя бы увидит понятный текст на исходном языке, '
                     'приложение не упадёт, и не появится техническое сообщение вида '
                     '&laquo;MISSING_KEY&raquo;.</p>',
  'code_content': '"""i18n middleware: foydalanuvchi tilini aniqlash va handlerlarga uzatish.\n'
                  '\n'
                  "Haqiqiy loyihada tarjima .mo fayllaridan gettext orqali o'qiladi;\n"
                  "bu yerda tushunarli bo'lishi uchun kichik in-memory lug'at ishlatilgan,\n"
                  'lekin _()/ngettext() interfeysi haqiqiy gettext bilan bir xil.\n'
                  '"""\n'
                  'from __future__ import annotations\n'
                  '\n'
                  'import gettext\n'
                  'from pathlib import Path\n'
                  'from typing import Any, Awaitable, Callable\n'
                  '\n'
                  'from aiogram import BaseMiddleware\n'
                  'from aiogram.types import TelegramObject, User\n'
                  '\n'
                  'LOCALES_DIR = Path(__file__).parent / "locales"\n'
                  'DEFAULT_LOCALE = "uz"\n'
                  'SUPPORTED_LOCALES = ("uz", "ru")\n'
                  '\n'
                  '# Har bir til uchun oldindan compile qilingan .mo asosida GNUTranslations\n'
                  "# obyektini keshda saqlaymiz — har update uchun diskdan qayta o'qimaslik "
                  'uchun.\n'
                  '_translations: dict[str, gettext.NullTranslations] = {}\n'
                  'for lang in SUPPORTED_LOCALES:\n'
                  '    try:\n'
                  '        _translations[lang] = gettext.translation(\n'
                  '            "messages", localedir=LOCALES_DIR, languages=[lang]\n'
                  '        )\n'
                  '    except FileNotFoundError:\n'
                  '        _translations[lang] = gettext.NullTranslations()\n'
                  '\n'
                  '\n'
                  'async def get_saved_locale(user_id: int, db) -> str | None:\n'
                  '    """Foydalanuvchi oldin tanlagan tilni DB\'dan o\'qiydi (mavjud '
                  'bo\'lsa)."""\n'
                  '    row = await db.fetch_one(\n'
                  '        "SELECT locale FROM user_preferences WHERE user_id = :uid", {"uid": '
                  'user_id}\n'
                  '    )\n'
                  '    return row["locale"] if row else None\n'
                  '\n'
                  '\n'
                  'class I18nMiddleware(BaseMiddleware):\n'
                  '    """Outer middleware — har bir update uchun locale\'ni aniqlab, handlerga\n'
                  '    tarjima funksiyasini (\'_\' va \'ngettext\') data orqali uzatadi."""\n'
                  '\n'
                  '    def __init__(self, db) -> None:\n'
                  '        self.db = db\n'
                  '\n'
                  '    async def __call__(\n'
                  '        self,\n'
                  '        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],\n'
                  '        event: TelegramObject,\n'
                  '        data: dict[str, Any],\n'
                  '    ) -> Any:\n'
                  '        user: User | None = data.get("event_from_user")\n'
                  '        locale = DEFAULT_LOCALE\n'
                  '        if user is not None:\n'
                  '            saved = await get_saved_locale(user.id, self.db)\n'
                  '            if saved in SUPPORTED_LOCALES:\n'
                  '                locale = saved\n'
                  '            elif user.language_code in SUPPORTED_LOCALES:\n'
                  '                locale = user.language_code\n'
                  '\n'
                  '        translation = _translations.get(locale, _translations[DEFAULT_LOCALE])\n'
                  '        data["locale"] = locale\n'
                  '        data["_"] = translation.gettext\n'
                  '        data["ngettext"] = translation.ngettext\n'
                  '        return await handler(event, data)\n'
                  '\n'
                  '\n'
                  "# ── Handler misoli: middleware kiritgan '_' va 'ngettext'dan foydalanish ──\n"
                  'from aiogram import Router\n'
                  'from aiogram.filters import Command\n'
                  'from aiogram.types import Message\n'
                  '\n'
                  'router = Router()\n'
                  '\n'
                  '\n'
                  '@router.message(Command("kurslar"))\n'
                  'async def show_courses_count(message: Message, _: Callable[[str], str],\n'
                  '                              ngettext: Callable[[str, str, int], str]) -> '
                  'None:\n'
                  '    count = await get_active_courses_count()\n'
                  "    # ngettext o'zi son bo'yicha to'g'ri shaklni tanlaydi — dasturchi\n"
                  '    # if count == 1 deb yozmaydi.\n'
                  '    text = ngettext(\n'
                  '        "Sizda {n} ta faol kurs bor.",\n'
                  '        "Sizda {n} ta faol kurs bor.",\n'
                  '        count,\n'
                  '    ).format(n=count)\n'
                  '    await message.answer(_( "Ma\'lumot: " ) + text)\n'
                  '\n'
                  '\n'
                  'async def get_active_courses_count() -> int:\n'
                  '    return 3',
  'code_content_ru': '"""i18n middleware: определение языка пользователя и передача в хендлеры.\n'
                     '\n'
                     'В реальном проекте перевод читается из .mo файлов через gettext;\n'
                     'здесь для наглядности используется небольшой in-memory словарь,\n'
                     'но интерфейс _()/ngettext() совпадает с настоящим gettext.\n'
                     '"""\n'
                     'from __future__ import annotations\n'
                     '\n'
                     'import gettext\n'
                     'from pathlib import Path\n'
                     'from typing import Any, Awaitable, Callable\n'
                     '\n'
                     'from aiogram import BaseMiddleware\n'
                     'from aiogram.types import TelegramObject, User\n'
                     '\n'
                     'LOCALES_DIR = Path(__file__).parent / "locales"\n'
                     'DEFAULT_LOCALE = "uz"\n'
                     'SUPPORTED_LOCALES = ("uz", "ru")\n'
                     '\n'
                     '# Кешируем объект GNUTranslations для каждого языка на основе заранее\n'
                     '# скомпилированных .mo — чтобы не читать с диска заново на каждый update.\n'
                     '_translations: dict[str, gettext.NullTranslations] = {}\n'
                     'for lang in SUPPORTED_LOCALES:\n'
                     '    try:\n'
                     '        _translations[lang] = gettext.translation(\n'
                     '            "messages", localedir=LOCALES_DIR, languages=[lang]\n'
                     '        )\n'
                     '    except FileNotFoundError:\n'
                     '        _translations[lang] = gettext.NullTranslations()\n'
                     '\n'
                     '\n'
                     'async def get_saved_locale(user_id: int, db) -> str | None:\n'
                     '    """Читает ранее выбранный пользователем язык из БД (если есть)."""\n'
                     '    row = await db.fetch_one(\n'
                     '        "SELECT locale FROM user_preferences WHERE user_id = :uid", {"uid": '
                     'user_id}\n'
                     '    )\n'
                     '    return row["locale"] if row else None\n'
                     '\n'
                     '\n'
                     'class I18nMiddleware(BaseMiddleware):\n'
                     '    """Outer middleware — определяет locale для каждого update и передаёт\n'
                     '    функции перевода (\'_\' и \'ngettext\') хендлеру через data."""\n'
                     '\n'
                     '    def __init__(self, db) -> None:\n'
                     '        self.db = db\n'
                     '\n'
                     '    async def __call__(\n'
                     '        self,\n'
                     '        handler: Callable[[TelegramObject, dict[str, Any]], '
                     'Awaitable[Any]],\n'
                     '        event: TelegramObject,\n'
                     '        data: dict[str, Any],\n'
                     '    ) -> Any:\n'
                     '        user: User | None = data.get("event_from_user")\n'
                     '        locale = DEFAULT_LOCALE\n'
                     '        if user is not None:\n'
                     '            saved = await get_saved_locale(user.id, self.db)\n'
                     '            if saved in SUPPORTED_LOCALES:\n'
                     '                locale = saved\n'
                     '            elif user.language_code in SUPPORTED_LOCALES:\n'
                     '                locale = user.language_code\n'
                     '\n'
                     '        translation = _translations.get(locale, '
                     '_translations[DEFAULT_LOCALE])\n'
                     '        data["locale"] = locale\n'
                     '        data["_"] = translation.gettext\n'
                     '        data["ngettext"] = translation.ngettext\n'
                     '        return await handler(event, data)\n'
                     '\n'
                     '\n'
                     "# ── Пример хендлера: использование '_' и 'ngettext', добавленных middleware "
                     '──\n'
                     'from aiogram import Router\n'
                     'from aiogram.filters import Command\n'
                     'from aiogram.types import Message\n'
                     '\n'
                     'router = Router()\n'
                     '\n'
                     '\n'
                     '@router.message(Command("kurslar"))\n'
                     'async def show_courses_count(message: Message, _: Callable[[str], str],\n'
                     '                              ngettext: Callable[[str, str, int], str]) -> '
                     'None:\n'
                     '    count = await get_active_courses_count()\n'
                     '    # ngettext сам выбирает правильную форму по числу — разработчику\n'
                     '    # не нужно писать if count == 1.\n'
                     '    text = ngettext(\n'
                     '        "У вас {n} активный курс.",\n'
                     '        "У вас {n} активных курсов.",\n'
                     '        count,\n'
                     '    ).format(n=count)\n'
                     '    await message.answer(_( "Информация: " ) + text)\n'
                     '\n'
                     '\n'
                     'async def get_active_courses_count() -> int:\n'
                     '    return 3',
  'sample': {'title': 'Namuna: uch tildagi tarjima kalitlari (.po formatida) va locale middleware',
             'description': "gettext .po fayl formatidagi namuna yozuvlar va ularni o'qiydigan "
                            'middleware',
             'sample_type': 'code',
             'code_files': [{'filename': 'locales/ru/LC_MESSAGES/messages.po',
                             'language': 'text',
                             'code': 'msgid "Salom!"\n'
                                     'msgstr "Привет!"\n'
                                     '\n'
                                     'msgid "Sizda {n} ta faol kurs bor."\n'
                                     'msgid_plural "Sizda {n} ta faol kurs bor."\n'
                                     'msgstr[0] "У вас {n} активный курс."\n'
                                     'msgstr[1] "У вас {n} активных курса."\n'
                                     'msgstr[2] "У вас {n} активных курсов."\n'
                                     '\n'
                                     'msgid "Ma\'lumot: "\n'
                                     'msgstr "Информация: " '},
                            {'filename': 'i18n_middleware.py',
                             'language': 'python',
                             'code': 'import gettext\n'
                                     'from aiogram import BaseMiddleware\n'
                                     '\n'
                                     'translations = {\n'
                                     '    "uz": gettext.NullTranslations(),\n'
                                     '    "ru": gettext.translation("messages", "locales", '
                                     'languages=["ru"]),\n'
                                     '}\n'
                                     '\n'
                                     '\n'
                                     'class I18nMiddleware(BaseMiddleware):\n'
                                     '    async def __call__(self, handler, event, data):\n'
                                     '        user = data.get("event_from_user")\n'
                                     '        locale = (user.language_code if user else "uz")\n'
                                     '        locale = locale if locale in translations else "uz"\n'
                                     '        t = translations[locale]\n'
                                     '        data["_"] = t.gettext\n'
                                     '        data["ngettext"] = t.ngettext\n'
                                     '        return await handler(event, data)'}]},
  'task': {'task_title': 'Amaliy loyiha: botni ikkinchi tilga tarjima qilish',
           'task_title_ru': 'Практический проект: перевод бота на второй язык',
           'task_description': 'aiogram botingizning kamida 3 ta handler javobini _() kaliti bilan '
                               'belgilang, .po fayl yarating va rus tiliga tarjima qiling, keyin '
                               "locale'ni user.language_code asosida tanlaydigan middleware "
                               'yozing.',
           'task_description_ru': 'Пометьте минимум 3 ответа хендлеров вашего aiogram-бота ключом '
                                  '_(), создайте .po файл и переведите на русский, затем напишите '
                                  'middleware, выбирающий locale на основе user.language_code.',
           'task_requirements': "1) Kamida 3 ta matn kaliti bo'lishi kerak. 2) uz va ru uchun "
                                "alohida .po (yoki ekvivalent lug'at) bo'lishi kerak. 3) "
                                "Middleware DB'da saqlangan tanlovni language_code'dan ustun "
                                "qo'yishi kerak. 4) Kamida bitta ngettext (ko'plik) misoli.",
           'task_requirements_ru': '1) Минимум 3 текстовых ключа. 2) Отдельные .po (или '
                                   'эквивалентный словарь) для uz и ru. 3) Middleware должен '
                                   'отдавать приоритет сохранённому в БД выбору перед '
                                   'language_code. 4) Минимум один пример ngettext (множественное '
                                   'число).',
           'task_technologies': 'aiogram 3.x, gettext, pybabel, BaseMiddleware',
           'task_deadline_days': 4},
  'exercises': [{'title': "language_code'ga ishonch",
                 'title_ru': 'Доверие к language_code',
                 'description': "Nega faqat User.language_code'ga tayanish yetarli emas?",
                 'description_ru': 'Почему полагаться только на User.language_code недостаточно?',
                 'exercise_type': 'multiple_choice',
                 'options': ['U Telegram ilovasining til sozlamasi, foydalanuvchi botdan qaysi '
                             'tilni xohlashidan farq qilishi mumkin',
                             "U har doim noto'g'ri qiymat qaytaradi",
                             "aiogram bu maydonni umuman qo'llab-quvvatlamaydi",
                             "U faqat guruh chatlarida mavjud bo'ladi"],
                 'options_ru': ['Это настройка языка приложения Telegram, которая может отличаться '
                                'от желаемого языка бота',
                                'Оно всегда возвращает неверное значение',
                                'aiogram вообще не поддерживает это поле',
                                'Оно доступно только в групповых чатах'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': 'Bu ilova interfeysi tili, botga xos tanlov emas.',
                 'hint_ru': 'Это язык интерфейса приложения, а не выбор, специфичный для бота.',
                 'explanation': 'language_code Telegram ilovasi tilini bildiradi; foydalanuvchi '
                                'botdan boshqa tilni xohlashi mumkin, shuning uchun saqlangan '
                                'tanlov ustun turishi kerak.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Tarjima faylini kompilyatsiya qilish',
                 'title_ru': 'Компиляция файла перевода',
                 'description': ".po faylni runtime o'qiy oladigan ikkilik .mo formatga "
                                "o'giradigan buyruq: pybabel ___",
                 'description_ru': 'Команда, преобразующая .po файл в бинарный формат .mo, '
                                   'читаемый в runtime: pybabel ___',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'compile',
                 'hint': 'extract shablon yaratadi, bu buyruq esa yakuniy binary faylni yaratadi.',
                 'hint_ru': 'extract создаёт шаблон, а эта команда создаёт итоговый бинарный файл.',
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Tarjima quvur liniyasi',
                 'title_ru': 'Конвейер перевода',
                 'description': "gettext ish jarayonining to'g'ri tartibini joylashtiring",
                 'description_ru': 'Расположите в правильном порядке этапы рабочего процесса '
                                   'gettext',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['Kodda _("matn") bilan belgilash',
                                'pybabel extract orqali .pot yaratish',
                                'Har til uchun .po faylga tarjima yozish',
                                'pybabel compile orqali .mo yaratish'],
                 'drag_items_ru': ['Пометить в коде через _("текст")',
                                   'Создать .pot через pybabel extract',
                                   'Записать перевод в .po файл для каждого языка',
                                   'Создать .mo через pybabel compile'],
                 'correct_order': ['Kodda _("matn") bilan belgilash',
                                   'pybabel extract orqali .pot yaratish',
                                   'Har til uchun .po faylga tarjima yozish',
                                   'pybabel compile orqali .mo yaratish'],
                 'hint': 'Avval belgilash, keyin ajratib olish, keyin tarjima, oxirida '
                         'kompilyatsiya.',
                 'hint_ru': 'Сначала пометка, затем извлечение, затем перевод, в конце компиляция.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 12,
  'title': '13-Graceful shutdown va uzilishsiz (zero-downtime) deploy',
  'title_ru': '13-Graceful shutdown и деплой без простоя (zero-downtime)',
  'points_reward': 18,
  'code_language': 'python',
  'text_content': '<h3>Nega qattiq kill xavfli</h3>\n'
                  "<p>Har bir deploy jarayon o'chirilishini talab qiladi. Agar buni oddiy "
                  "<code>kill -9</code> yoki konteynerni to'xtatish orqali qilsangiz, o'sha "
                  "zumdagi vaziyat aniq emas: bitta handler bazaga yozayotgan bo'lishi mumkin "
                  "(yarim yozilgan tranzaksiya), foydalanuvchiga xabar yuborilayotgan bo'lishi "
                  'mumkin (yarim yuborilgan xabar &mdash; foydalanuvchi hech narsa olmaydi), yoki '
                  'webhook rejimida hozirgina kelgan update hali handler navbatiga tushmagan '
                  "bo'lishi mumkin (bu update butunlay yo'qoladi, Telegram uni qayta yubormaydi, "
                  'chunki sizning serveringiz 200 qaytargan edi).</p>\n'
                  "<p><strong>Graceful shutdown</strong> &mdash; jarayonni to'satdan emas, balki "
                  "tartibli ravishda to'xtatish: avval yangi ishni qabul qilishni to'xtatish, "
                  'keyin joriy ishlarni tugatishga vaqt berish, faqat shundan keyin chiqish.</p>\n'
                  '\n'
                  "<h3>Signal handling: SIGTERM'ni tutib olish</h3>\n"
                  "<p>Docker/systemd/Kubernetes jarayonni to'xtatganda avval <code>SIGTERM</code> "
                  'signalini yuboradi (va faqat belgilangan &ldquo;grace period&rdquo;dan keyin, '
                  'agar jarayon hali ishlab tursa, majburiy <code>SIGKILL</code>). Sizning '
                  'vazifangiz &mdash; <code>SIGTERM</code>ni tutib, uchta qadamni bajarish:</p>\n'
                  '<ol>\n'
                  "<li><strong>Yangi ishni qabul qilishni to'xtatish</strong> &mdash; polling "
                  "rejimida <code>get_updates</code> chaqirishni to'xtatish, webhook rejimida esa "
                  "load balancer/reverse-proxy'ga &ldquo;bu instansga yangi so'rov "
                  'yubormang&rdquo; deb signal berish (yoki health-check endpointini &ldquo;not '
                  "ready&rdquo; qilib qo'yish, orkestrator o'zi trafikni ko'chiradi).</li>\n"
                  '<li><strong>Joriy vazifalarni tugatish uchun cheklangan vaqt berish</strong> '
                  '&mdash; <code>asyncio.wait(tasks, timeout=30)</code> kabi chegaralangan kutish; '
                  'agar 30 soniyada tugallanmasa, qolganini majburan bekor qilish siyosatini '
                  'oldindan hal qiling (log yozib qoldirish kamida).</li>\n'
                  '<li><strong>Resurslarni yopish</strong> &mdash; '
                  "<code>bot.session.close()</code>, DB pool'ini yopish, Redis ulanishini yopish "
                  '&mdash; aks holda &ldquo;connection leaked&rdquo; ogohlantirishlari keyingi '
                  "deploy'da ko'payib boradi.</li>\n"
                  '</ol>\n'
                  '<pre><code>import asyncio\n'
                  'import signal\n'
                  '\n'
                  'stop_event = asyncio.Event()\n'
                  '\n'
                  'def _on_sigterm() -> None:\n'
                  '    stop_event.set()\n'
                  '\n'
                  'loop = asyncio.get_running_loop()\n'
                  'loop.add_signal_handler(signal.SIGTERM, _on_sigterm)\n'
                  'await stop_event.wait()          # 1-qadam: signal kelguncha kutish\n'
                  'await asyncio.wait_for(drain_in_flight_tasks(), timeout=30)  # 2-qadam\n'
                  'await bot.session.close()        # 3-qadam</code></pre>\n'
                  '\n'
                  '<h3>Polling va webhook uzishi bir xil emas</h3>\n'
                  "<p>Polling rejimida &ldquo;yangi ishni to'xtatish&rdquo; oddiy &mdash; "
                  'shunchaki <code>get_updates</code>ning navbatdagi chaqiruvini qilmaslik kifoya, '
                  "chunki so'rovni <em>siz</em> boshlaysiz. Webhook rejimida esa aksincha &mdash; "
                  "Telegram sizga <em>o'zi</em> so'rov yuboradi, va agar reverse-proxy hamon "
                  "eskirgan instansga yo'naltirsa, sizning &ldquo;tayyor emasman&rdquo; degan "
                  "ichki holatingiz hech kimga ko'rinmaydi. Shu sababli webhook uchun "
                  'orkestratorning <strong>readiness probe</strong>si (&ldquo;men hozir yangi '
                  'trafikni qabul qilishga tayyormanmi&rdquo;) va <strong>liveness '
                  'probe</strong>si (&ldquo;men umuman ishlayapmanmi, hali osilib '
                  "qolmaganmanmi&rdquo;) alohida bo'lishi kerak &mdash; shutdown boshlanganda "
                  "readiness darhol &ldquo;yo'q&rdquo;ga o'tadi, liveness esa joriy so'rovlar "
                  'tugaguncha &ldquo;ha&rdquo; qoladi.</p>\n'
                  '\n'
                  '<h3>Blue-green: eski instans va yangisi bir vaqtda</h3>\n'
                  '<p>Eng ishonchli uzilishsiz deploy strategiyasi &mdash; '
                  '<strong>blue-green</strong>: yangi versiya (&ldquo;green&rdquo;) eskisi '
                  '(&ldquo;blue&rdquo;) bilan bir vaqtda, alohida ishga tushiriladi. Load balancer '
                  "hamon &ldquo;blue&rdquo;ga trafik yuboradi. Green tayyor bo'lgach (health-check "
                  "o'tgach), trafik green'ga ko'chiriladi, faqat shundan keyin blue'ni graceful "
                  "shutdown qilib o'chiriladi. Agar green'da muammo chiqsa, trafikni darhol "
                  "blue'ga qaytarish mumkin &mdash; hech narsa buzilmagan holda.</p>\n"
                  '<pre class="mermaid">\n'
                  'sequenceDiagram\n'
                  '    participant LB as Load Balancer\n'
                  '    participant Blue as Eski instans (blue)\n'
                  '    participant Green as Yangi instans (green)\n'
                  '    LB->>Blue: Trafik (hozirgi)\n'
                  '    Note over Green: Green ishga tushadi\n'
                  '    Green->>Green: Health-check tayyor\n'
                  "    LB->>Green: Trafik ko'chiriladi\n"
                  '    Note over Blue: SIGTERM yuboriladi\n'
                  "    Blue->>Blue: Joriy so'rovlarni tugatadi (graceful)\n"
                  '    Blue->>Blue: Resurslarni yopadi, chiqadi\n'
                  '</pre>\n'
                  "<p>Diagrammada ko'rinib turibdiki, ikkala instans bir muddat <em>parallel</em> "
                  "ishlaydi &mdash; aynan shu qоплаш (overlap) uzilishsizlikni ta'minlaydi. "
                  'Rolling restart (bitta-bittalab almashtirish) ham xuddi shu tamoyilga tayanadi, '
                  "faqat ko'proq instans bo'lganda.</p>",
  'text_content_ru': '<h3>Почему жёсткий kill опасен</h3>\n'
                     '<p>Каждый деплой требует остановки процесса. Если делать это простым '
                     '<code>kill -9</code> или остановкой контейнера, момент остановки '
                     'непредсказуем: один хендлер может как раз писать в базу (наполовину '
                     'выполненная транзакция), пользователю может отправляться сообщение '
                     '(наполовину отправленное &mdash; пользователь ничего не получит), либо в '
                     'режиме webhook только что пришедший update ещё не попал в очередь хендлеров '
                     '(этот update будет полностью потерян, Telegram не отправит его повторно, так '
                     'как ваш сервер уже вернул 200).</p>\n'
                     '<p><strong>Graceful shutdown</strong> &mdash; это остановка процесса не '
                     'резко, а упорядоченно: сначала прекратить принимать новую работу, затем дать '
                     'время завершить текущую, и только потом выходить.</p>\n'
                     '\n'
                     '<h3>Обработка сигналов: перехват SIGTERM</h3>\n'
                     '<p>Docker/systemd/Kubernetes при остановке процесса сначала посылает сигнал '
                     '<code>SIGTERM</code> (и только после установленного &laquo;grace '
                     'period&raquo;, если процесс всё ещё работает, принудительный '
                     '<code>SIGKILL</code>). Ваша задача &mdash; перехватить <code>SIGTERM</code> '
                     'и выполнить три шага:</p>\n'
                     '<ol>\n'
                     '<li><strong>Прекратить принимать новую работу</strong> &mdash; в режиме '
                     'polling прекратить вызывать <code>get_updates</code>, в режиме webhook '
                     '&mdash; сигнализировать балансировщику/reverse-proxy &laquo;не отправляйте '
                     'новые запросы на этот инстанс&raquo; (либо перевести health-check эндпоинт в '
                     'состояние &laquo;not ready&raquo;, оркестратор сам перенаправит '
                     'трафик).</li>\n'
                     '<li><strong>Дать ограниченное время на завершение текущих задач</strong> '
                     '&mdash; ограниченное ожидание вида <code>asyncio.wait(tasks, '
                     'timeout=30)</code>; если за 30 секунд не завершилось, заранее решите '
                     'политику принудительной отмены оставшегося (как минимум записать в '
                     'лог).</li>\n'
                     '<li><strong>Закрыть ресурсы</strong> &mdash; '
                     '<code>bot.session.close()</code>, закрыть пул соединений БД, закрыть '
                     'подключение к Redis &mdash; иначе предупреждения &laquo;connection '
                     'leaked&raquo; будут накапливаться с каждым следующим деплоем.</li>\n'
                     '</ol>\n'
                     '<pre><code>import asyncio\n'
                     'import signal\n'
                     '\n'
                     'stop_event = asyncio.Event()\n'
                     '\n'
                     'def _on_sigterm() -> None:\n'
                     '    stop_event.set()\n'
                     '\n'
                     'loop = asyncio.get_running_loop()\n'
                     'loop.add_signal_handler(signal.SIGTERM, _on_sigterm)\n'
                     'await stop_event.wait()          # шаг 1: ожидание сигнала\n'
                     'await asyncio.wait_for(drain_in_flight_tasks(), timeout=30)  # шаг 2\n'
                     'await bot.session.close()        # шаг 3</code></pre>\n'
                     '\n'
                     '<h3>Дренаж polling и webhook — не одно и то же</h3>\n'
                     '<p>В режиме polling &laquo;прекратить принимать новую работу&raquo; просто '
                     '&mdash; достаточно не делать следующий вызов <code>get_updates</code>, так '
                     'как запрос инициируете <em>вы сами</em>. В режиме webhook, наоборот &mdash; '
                     'Telegram отправляет запрос <em>сам</em>, и если reverse-proxy всё ещё '
                     'направляет трафик на устаревший инстанс, ваше внутреннее состояние &laquo;я '
                     'не готов&raquo; никому не видно. Поэтому для webhook <strong>readiness '
                     'probe</strong> оркестратора (&laquo;готов ли я сейчас принимать новый '
                     'трафик&raquo;) и <strong>liveness probe</strong> (&laquo;работаю ли я '
                     'вообще, не завис ли&raquo;) должны быть раздельными &mdash; при начале '
                     'shutdown readiness сразу переходит в &laquo;нет&raquo;, а liveness остаётся '
                     '&laquo;да&raquo; пока не завершатся текущие запросы.</p>\n'
                     '\n'
                     '<h3>Blue-green: старый и новый инстанс одновременно</h3>\n'
                     '<p>Самая надёжная стратегия деплоя без простоя &mdash; '
                     '<strong>blue-green</strong>: новая версия (&laquo;green&raquo;) запускается '
                     'отдельно, одновременно со старой (&laquo;blue&raquo;). Балансировщик всё ещё '
                     'направляет трафик на &laquo;blue&raquo;. Когда green готов (прошёл '
                     'health-check), трафик переключается на green, и только после этого blue '
                     'останавливается через graceful shutdown. Если в green обнаружится проблема, '
                     'трафик можно немедленно вернуть на blue &mdash; ничего не сломав.</p>\n'
                     '<pre class="mermaid">\n'
                     'sequenceDiagram\n'
                     '    participant LB as Load Balancer\n'
                     '    participant Blue as Старый инстанс (blue)\n'
                     '    participant Green as Новый инстанс (green)\n'
                     '    LB->>Blue: Трафик (текущий)\n'
                     '    Note over Green: Green запускается\n'
                     '    Green->>Green: Health-check пройден\n'
                     '    LB->>Green: Трафик переключается\n'
                     '    Note over Blue: Отправляется SIGTERM\n'
                     '    Blue->>Blue: Завершает текущие запросы (graceful)\n'
                     '    Blue->>Blue: Закрывает ресурсы, выходит\n'
                     '</pre>\n'
                     '<p>На диаграмме видно, что оба инстанса некоторое время работают '
                     '<em>параллельно</em> &mdash; именно это перекрытие (overlap) обеспечивает '
                     'отсутствие простоя. Rolling restart (замена по одному инстансу) опирается на '
                     'тот же принцип, просто при большем числе инстансов.</p>',
  'code_content': '"""Graceful shutdown: SIGTERM\'ni tutish, joriy vazifalarni tugatish,\n'
                  'resurslarni tozalab yopish. aiohttp-webhook misolida health-check bilan.\n'
                  '"""\n'
                  'from __future__ import annotations\n'
                  '\n'
                  'import asyncio\n'
                  'import logging\n'
                  'import signal\n'
                  '\n'
                  'from aiohttp import web\n'
                  'from aiogram import Bot, Dispatcher\n'
                  '\n'
                  'logger = logging.getLogger("shutdown")\n'
                  '\n'
                  'DRAIN_TIMEOUT_SECONDS = 30\n'
                  '_in_flight: set[asyncio.Task] = set()\n'
                  '_ready = True   # readiness probe holati\n'
                  '\n'
                  '\n'
                  'def track(coro) -> asyncio.Task:\n'
                  '    """Har bir handler task\'ini ro\'yxatga oladi — shutdown paytida\n'
                  '    qaysilari hali tugallanmaganini bilish uchun."""\n'
                  '    task = asyncio.create_task(coro)\n'
                  '    _in_flight.add(task)\n'
                  '    task.add_done_callback(_in_flight.discard)\n'
                  '    return task\n'
                  '\n'
                  '\n'
                  'async def readiness_probe(request: web.Request) -> web.Response:\n'
                  '    # Orkestrator shutdown boshlanganda buni "not ready" deb o\'qib,\n'
                  "    # yangi trafikni boshqa instansga yo'naltiradi.\n"
                  '    if _ready:\n'
                  '        return web.Response(status=200, text="ready")\n'
                  '    return web.Response(status=503, text="draining")\n'
                  '\n'
                  '\n'
                  'async def liveness_probe(request: web.Request) -> web.Response:\n'
                  '    # Joriy so\'rovlar tugagunga qadar "ha" qaytadi — jarayon hali\n'
                  '    # osilib qolmagan, faqat yangi ish qabul qilmayapti.\n'
                  '    return web.Response(status=200, text="alive")\n'
                  '\n'
                  '\n'
                  'async def graceful_shutdown(bot: Bot) -> None:\n'
                  '    global _ready\n'
                  '    logger.info("SIGTERM qabul qilindi — yangi so\'rovlarni to\'xtatish")\n'
                  "    _ready = False   # 1-qadam: yangi ishni qabul qilishni to'xtatish\n"
                  '\n'
                  '    if _in_flight:\n'
                  '        logger.info("joriy %d ta vazifa tugashi kutilmoqda (timeout=%ss)",\n'
                  '                     len(_in_flight), DRAIN_TIMEOUT_SECONDS)\n'
                  '        done, pending = await asyncio.wait(\n'
                  '            _in_flight, timeout=DRAIN_TIMEOUT_SECONDS\n'
                  '        )\n'
                  '        for task in pending:\n'
                  '            logger.warning("vazifa %s belgilangan vaqtda tugamadi — bekor '
                  'qilinmoqda", task)\n'
                  '            task.cancel()\n'
                  '\n'
                  '    await bot.session.close()   # 3-qadam: resurslarni yopish\n'
                  '    logger.info("bot sessiyasi yopildi, jarayon chiqadi")\n'
                  '\n'
                  '\n'
                  'def install_signal_handlers(bot: Bot) -> None:\n'
                  '    loop = asyncio.get_running_loop()\n'
                  '    stop_event = asyncio.Event()\n'
                  '\n'
                  '    def _handle_signal() -> None:\n'
                  '        stop_event.set()\n'
                  '\n'
                  '    for sig in (signal.SIGTERM, signal.SIGINT):\n'
                  '        loop.add_signal_handler(sig, _handle_signal)\n'
                  '\n'
                  '    async def _waiter() -> None:\n'
                  '        await stop_event.wait()\n'
                  '        await graceful_shutdown(bot)\n'
                  '\n'
                  '    loop.create_task(_waiter())\n'
                  '\n'
                  '\n'
                  'async def main() -> None:\n'
                  '    bot = Bot(token="BOT_TOKEN")\n'
                  '    dp = Dispatcher()\n'
                  '    install_signal_handlers(bot)\n'
                  '\n'
                  '    app = web.Application()\n'
                  '    app.router.add_get("/health/ready", readiness_probe)\n'
                  '    app.router.add_get("/health/live", liveness_probe)\n'
                  '\n'
                  '    runner = web.AppRunner(app)\n'
                  '    await runner.setup()\n'
                  '    site = web.TCPSite(runner, "0.0.0.0", 8080)\n'
                  '    await site.start()\n'
                  '\n'
                  "    await dp.start_polling(bot, handle_signals=False)  # o'z signal "
                  "handler'imiz bor\n"
                  '\n'
                  '\n'
                  'if __name__ == "__main__":\n'
                  '    asyncio.run(main())',
  'code_content_ru': '"""Graceful shutdown: перехват SIGTERM, завершение текущих задач,\n'
                     'аккуратное закрытие ресурсов. На примере aiohttp-webhook с health-check.\n'
                     '"""\n'
                     'from __future__ import annotations\n'
                     '\n'
                     'import asyncio\n'
                     'import logging\n'
                     'import signal\n'
                     '\n'
                     'from aiohttp import web\n'
                     'from aiogram import Bot, Dispatcher\n'
                     '\n'
                     'logger = logging.getLogger("shutdown")\n'
                     '\n'
                     'DRAIN_TIMEOUT_SECONDS = 30\n'
                     '_in_flight: set[asyncio.Task] = set()\n'
                     '_ready = True   # состояние readiness probe\n'
                     '\n'
                     '\n'
                     'def track(coro) -> asyncio.Task:\n'
                     '    """Регистрирует каждую задачу-хендлер — чтобы при shutdown знать,\n'
                     '    какие ещё не завершились."""\n'
                     '    task = asyncio.create_task(coro)\n'
                     '    _in_flight.add(task)\n'
                     '    task.add_done_callback(_in_flight.discard)\n'
                     '    return task\n'
                     '\n'
                     '\n'
                     'async def readiness_probe(request: web.Request) -> web.Response:\n'
                     '    # Оркестратор при начале shutdown читает это как "not ready" и\n'
                     '    # направляет новый трафик на другой инстанс.\n'
                     '    if _ready:\n'
                     '        return web.Response(status=200, text="ready")\n'
                     '    return web.Response(status=503, text="draining")\n'
                     '\n'
                     '\n'
                     'async def liveness_probe(request: web.Request) -> web.Response:\n'
                     '    # Возвращает "да" пока не завершатся текущие запросы — процесс ещё\n'
                     '    # не завис, просто не принимает новую работу.\n'
                     '    return web.Response(status=200, text="alive")\n'
                     '\n'
                     '\n'
                     'async def graceful_shutdown(bot: Bot) -> None:\n'
                     '    global _ready\n'
                     '    logger.info("получен SIGTERM — прекращаем приём новых запросов")\n'
                     '    _ready = False   # шаг 1: прекратить принимать новую работу\n'
                     '\n'
                     '    if _in_flight:\n'
                     '        logger.info("ожидание завершения %d текущих задач (timeout=%sс)",\n'
                     '                     len(_in_flight), DRAIN_TIMEOUT_SECONDS)\n'
                     '        done, pending = await asyncio.wait(\n'
                     '            _in_flight, timeout=DRAIN_TIMEOUT_SECONDS\n'
                     '        )\n'
                     '        for task in pending:\n'
                     '            logger.warning("задача %s не завершилась вовремя — отменяется", '
                     'task)\n'
                     '            task.cancel()\n'
                     '\n'
                     '    await bot.session.close()   # шаг 3: закрытие ресурсов\n'
                     '    logger.info("сессия бота закрыта, процесс завершается")\n'
                     '\n'
                     '\n'
                     'def install_signal_handlers(bot: Bot) -> None:\n'
                     '    loop = asyncio.get_running_loop()\n'
                     '    stop_event = asyncio.Event()\n'
                     '\n'
                     '    def _handle_signal() -> None:\n'
                     '        stop_event.set()\n'
                     '\n'
                     '    for sig in (signal.SIGTERM, signal.SIGINT):\n'
                     '        loop.add_signal_handler(sig, _handle_signal)\n'
                     '\n'
                     '    async def _waiter() -> None:\n'
                     '        await stop_event.wait()\n'
                     '        await graceful_shutdown(bot)\n'
                     '\n'
                     '    loop.create_task(_waiter())\n'
                     '\n'
                     '\n'
                     'async def main() -> None:\n'
                     '    bot = Bot(token="BOT_TOKEN")\n'
                     '    dp = Dispatcher()\n'
                     '    install_signal_handlers(bot)\n'
                     '\n'
                     '    app = web.Application()\n'
                     '    app.router.add_get("/health/ready", readiness_probe)\n'
                     '    app.router.add_get("/health/live", liveness_probe)\n'
                     '\n'
                     '    runner = web.AppRunner(app)\n'
                     '    await runner.setup()\n'
                     '    site = web.TCPSite(runner, "0.0.0.0", 8080)\n'
                     '    await site.start()\n'
                     '\n'
                     '    await dp.start_polling(bot, handle_signals=False)  # у нас свой '
                     'обработчик сигналов\n'
                     '\n'
                     '\n'
                     'if __name__ == "__main__":\n'
                     '    asyncio.run(main())',
  'sample': {'title': 'Namuna: SIGTERM handler va readiness/liveness endpoint',
             'description': 'Signal asosida graceful shutdown va orkestrator uchun health-check',
             'sample_type': 'code',
             'code_files': [{'filename': 'graceful_shutdown.py',
                             'language': 'python',
                             'code': 'import asyncio\n'
                                     'import signal\n'
                                     '\n'
                                     '_ready = True\n'
                                     '\n'
                                     '\n'
                                     'async def on_sigterm(bot, in_flight_tasks):\n'
                                     '    global _ready\n'
                                     '    _ready = False\n'
                                     '    if in_flight_tasks:\n'
                                     '        await asyncio.wait(in_flight_tasks, timeout=30)\n'
                                     '    await bot.session.close()\n'
                                     '\n'
                                     '\n'
                                     'def install(loop, bot, in_flight_tasks):\n'
                                     '    stop = asyncio.Event()\n'
                                     '    loop.add_signal_handler(signal.SIGTERM, stop.set)\n'
                                     '\n'
                                     '    async def waiter():\n'
                                     '        await stop.wait()\n'
                                     '        await on_sigterm(bot, in_flight_tasks)\n'
                                     '\n'
                                     '    loop.create_task(waiter())'},
                            {'filename': 'health.py',
                             'language': 'python',
                             'code': 'from aiohttp import web\n'
                                     'import graceful_shutdown as gs\n'
                                     '\n'
                                     '\n'
                                     'async def ready(request):\n'
                                     '    return web.Response(status=200 if gs._ready else 503)\n'
                                     '\n'
                                     '\n'
                                     'async def alive(request):\n'
                                     '    return web.Response(status=200)'}]},
  'task': {'task_title': "Amaliy loyiha: botga graceful shutdown qo'shish",
           'task_title_ru': 'Практический проект: добавить graceful shutdown в бота',
           'task_description': "Mavjud (yoki yangi) aiogram botingizga SIGTERM'ni tutadigan, joriy "
                               'handler vazifalarini belgilangan vaqt ichida tugatishga imkon '
                               "beradigan, so'ng bot sessiyasini tartibli yopadigan shutdown "
                               "mexanizmini qo'shing. Readiness endpointi ham qo'shing.",
           'task_description_ru': 'Добавьте в существующего (или нового) aiogram-бота механизм '
                                  'shutdown, перехватывающий SIGTERM, дающий текущим '
                                  'задачам-хендлерам ограниченное время на завершение, а затем '
                                  'аккуратно закрывающий сессию бота. Добавьте также '
                                  'readiness-эндпоинт.',
           'task_requirements': "1) SIGTERM signal handler ro'yxatga olinishi kerak. 2) Kamida "
                                "bitta 'joriy vazifa'ni sun'iy kechikish bilan simulyatsiya qilib, "
                                'shutdown uni kutishini isbotlang. 3) Timeout tugagach majburiy '
                                "bekor qilish logikasi bo'lsin. 4) /health/ready endpointi "
                                'shutdown boshlanganda 503 qaytarishi kerak.',
           'task_requirements_ru': '1) Должен быть зарегистрирован обработчик сигнала SIGTERM. 2) '
                                   "Симулируйте минимум одну 'текущую задачу' с искусственной "
                                   'задержкой и покажите, что shutdown её дожидается. 3) После '
                                   'истечения timeout должна сработать логика принудительной '
                                   'отмены. 4) Эндпоинт /health/ready должен возвращать 503 при '
                                   'начале shutdown.',
           'task_technologies': 'aiogram 3.x, asyncio, signal, aiohttp health-check',
           'task_deadline_days': 5},
  'exercises': [{'title': 'Nega qattiq kill xavfli',
                 'title_ru': 'Почему опасен жёсткий kill',
                 'description': "Deploy paytida jarayonni kill -9 bilan to'xtatishning asosiy "
                                'xavfi nimada?',
                 'description_ru': 'В чём главная опасность остановки процесса через kill -9 во '
                                   'время деплоя?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Joriy bajarilayotgan yozuv/xabar yarim holatda to'xtab, ma'lumot "
                             "yo'qolishi yoki nomuvofiqlik yuzaga kelishi mumkin",
                             "Bu har doim serverni butunlay o'chirib qo'yadi",
                             "Bu faqat Windows'da muammo tug'diradi",
                             "aiogram bunga avtomatik himoyalangan, hech qanday xavf yo'q"],
                 'options_ru': ['Текущая выполняемая запись/сообщение может остановиться в '
                                'половинчатом состоянии, вызвав потерю данных или рассогласование',
                                'Это всегда полностью выключает сервер',
                                'Это проблема только под Windows',
                                'aiogram автоматически защищён от этого, риска нет'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "Yarim bajarilgan operatsiyalarni o'ylab ko'ring — DB yozuvi yoki xabar "
                         'yuborish.',
                 'hint_ru': 'Подумайте о наполовину выполненных операциях — записи в БД или '
                            'отправке сообщения.',
                 'explanation': "Kutilmagan to'xtash joriy I/O operatsiyasini yarim holatda "
                                'qoldirishi mumkin — bu graceful shutdown yechadigan asosiy '
                                'muammo.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Signal nomi',
                 'title_ru': 'Название сигнала',
                 'description': "Orkestrator jarayonni tartibli to'xtatish uchun avval qaysi "
                                "signalni yuboradi (majburiy SIGKILL'dan oldin): SIG___",
                 'description_ru': 'Какой сигнал оркестратор отправляет первым для упорядоченной '
                                   'остановки процесса (перед принудительным SIGKILL): SIG___',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'TERM',
                 'hint': "SIG bilan boshlanadi, uch harfli qisqartma, 'terminate' so'zidan.",
                 'hint_ru': "Начинается с SIG, трёхбуквенное сокращение от слова 'terminate'.",
                 'difficulty_level': 'Easy',
                 'points': 5},
                {'title': 'Graceful shutdown qadamlari',
                 'title_ru': 'Шаги graceful shutdown',
                 'description': "Tartibli to'xtatish qadamlarini to'g'ri ketma-ketlikka "
                                'joylashtiring',
                 'description_ru': 'Расположите шаги упорядоченной остановки в правильном порядке',
                 'exercise_type': 'drag_and_drop',
                 'drag_items': ['SIGTERM signalini qabul qilish',
                                "Yangi so'rovlarni qabul qilishni to'xtatish (readiness=false)",
                                'Joriy vazifalarni belgilangan vaqt ichida kutish',
                                'Bot sessiyasi va boshqa resurslarni yopish'],
                 'drag_items_ru': ['Получить сигнал SIGTERM',
                                   'Прекратить приём новых запросов (readiness=false)',
                                   'Дождаться текущих задач в течение ограниченного времени',
                                   'Закрыть сессию бота и другие ресурсы'],
                 'correct_order': ['SIGTERM signalini qabul qilish',
                                   "Yangi so'rovlarni qabul qilishni to'xtatish (readiness=false)",
                                   'Joriy vazifalarni belgilangan vaqt ichida kutish',
                                   'Bot sessiyasi va boshqa resurslarni yopish'],
                 'hint': "Avval signal keladi, keyin qabul to'xtaydi, keyin kutish, oxirida "
                         'yopish.',
                 'hint_ru': 'Сначала приходит сигнал, затем прекращается приём, затем ожидание, в '
                            'конце закрытие.',
                 'difficulty_level': 'Medium',
                 'points': 8}]},
 {'order': 13,
  'title': "R2+CAPSTONE-Ilg'or Telegram bot: Mini App, real to'lovlar va Redis FSM",
  'title_ru': 'R2+КАПСТОУН-Продвинутый Telegram-бот: Mini App, реальные платежи и Redis FSM',
  'points_reward': 25,
  'code_language': 'python',
  'text_content': '<h3>Qisqacha takrorlash: 7-12-darslar</h3>\n'
                  '<p>Bu dars &mdash; ikkinchi takrorlash va ayni paytda kursning yakuniy capstone '
                  "loyihasi. Avval 7-12-darslarda o'rgangan production-daraja mavzularini bir "
                  'joyga jamlaymiz:</p>\n'
                  '<ul>\n'
                  '<li><strong>7-dars</strong> &mdash; strukturaviy logging (structlog, har update '
                  'uchun contextvars orqali chat_id/user_id biriktirish), Sentry orqali xatolarni '
                  'kuzatish, Prometheus metrikalari.</li>\n'
                  '<li><strong>8-dars</strong> &mdash; Redis asosidagi taqsimlangan rate-limiting: '
                  'token bucket, foydalanuvchi va global chegaralar, vaqtinchalik ban.</li>\n'
                  '<li><strong>9-dars</strong> &mdash; Dispatcher/Router ichki tuzilishi: outer '
                  'middleware har doim, inner middleware faqat filter mos kelganda ishlaydi, '
                  "ro'yxatga olish tartibi zanjir tartibini belgilaydi.</li>\n"
                  "<li><strong>10-dars</strong> &mdash; bot-farm: bitta kod, ko'p bot tokeni, "
                  'bot_id bilan tenant izolyatsiyasi.</li>\n'
                  '<li><strong>11-dars</strong> &mdash; i18n: gettext .pot/.po/.mo quvur liniyasi, '
                  'middleware orqali locale aniqlash.</li>\n'
                  '<li><strong>12-dars</strong> &mdash; graceful shutdown: SIGTERM, cheklangan '
                  'drain, blue-green deploy.</li>\n'
                  '</ul>\n'
                  "<p>Bu daslarning barchasi &mdash; kursning boshida (0-6-darslar) o'rgangan Mini "
                  'App, initData xavfsizligi, real Telegram Payments va Redis-backed FSM bilan '
                  'birga &mdash; endi bitta ishlaydigan tizimga jamlanadi.</p>\n'
                  '\n'
                  '<h3>Capstone arxitekturasi: barcha qismlar bir joyda</h3>\n'
                  '<p>Yakuniy loyiha &mdash; masalan, &ldquo;kurslarga premium obuna '
                  "sotadigan&rdquo; bot &mdash; quyidagi qatlamlardan iborat bo'lishi kerak: "
                  "foydalanuvchi Mini App orqali mahsulotni ko'radi (0-dars), Mini App backend'ga "
                  '<code>initData</code>ni yuboradi va backend uni HMAC orqali tasdiqlaydi '
                  "(1-dars), foydalanuvchi haqiqiy Telegram Payments orqali to'lov qiladi &mdash; "
                  'invoice, pre_checkout_query, successful_payment (2-3-darslar), bot bir nechta '
                  "worker sifatida ishlaydi va FSM holatini Redis'da saqlaydi (4-dars), barcha "
                  "so'rovlar strukturaviy log yozadi va rate-limit qatoridan o'tadi (7-8-darslar), "
                  'va deploy paytida graceful shutdown ishlaydi (12-dars).</p>\n'
                  '<pre class="mermaid">\n'
                  'flowchart TB\n'
                  '  subgraph Frontend\n'
                  '    MA["Mini App\n'
                  '(Telegram.WebApp JS)"]\n'
                  '  end\n'
                  '  subgraph Backend\n'
                  '    V["initData validatsiyasi\n'
                  '(HMAC-SHA256)"]\n'
                  '    API["FastAPI/aiohttp\n'
                  'backend"]\n'
                  '  end\n'
                  '  subgraph BotLayer["Bot qatlami (N worker)"]\n'
                  '    W1["Worker #1"]\n'
                  '    W2["Worker #2"]\n'
                  '  end\n'
                  '  subgraph Shared["Umumiy infratuzilma"]\n'
                  '    R[("Redis\n'
                  'FSM + rate-limit")]\n'
                  '    DB[("PostgreSQL")]\n'
                  '    LOG["Structured logs\n'
                  '+ Sentry + Prometheus"]\n'
                  '  end\n'
                  '  MA -->|"initData"| V\n'
                  '  V --> API\n'
                  '  API --> W1\n'
                  '  API --> W2\n'
                  '  W1 --> R\n'
                  '  W2 --> R\n'
                  '  W1 --> DB\n'
                  '  W2 --> DB\n'
                  '  W1 -.->|"successful_payment"| DB\n'
                  '  W1 --> LOG\n'
                  '  W2 --> LOG\n'
                  '</pre>\n'
                  '<p>Diagramma &mdash; aynan shu kursning xulosasi: har bir quti alohida darsda '
                  "chuqur o'rganilgan, endi ular birgalikda bitta ishlaydigan tizimni tashkil "
                  'etadi.</p>\n'
                  '\n'
                  '<h3>Nima uchun aynan shu tartibda qurish kerak</h3>\n'
                  "<p>Capstone'ni noldan yozishda tavsiya etilgan tartib: avval Redis FSM va "
                  "logging'ni ulang (bularsiz keyingi qadamlarni debug qilish qiyin bo'ladi), "
                  "keyin Mini App + initData validatsiyasini qo'shing, so'ng Payments oqimini "
                  "ulang (bu eng ko'p tashqi bog'liqlikka ega qism &mdash; oxiriga qoldirilsa, "
                  "boshqa qismlar allaqachon ishlab turgan bo'ladi), va nihoyat rate-limiting "
                  "hamda graceful shutdown bilan &ldquo;production'ga tayyor&rdquo; holatga "
                  'keltiring.</p>\n'
                  '\n'
                  '<h3>Baholash mezonlari</h3>\n'
                  "<p>Ushbu capstone quyidagi mezonlar bo'yicha baholanadi: (1) Mini App orqali "
                  'initData xavfsiz tasdiqlanishi, (2) kamida bitta real Payments oqimi (invoice '
                  "&rarr; pre_checkout_query &rarr; successful_payment) to'liq ishlashi, (3) FSM "
                  "holati Redis'da saqlanishi va kamida ikkita worker orasida umumiy bo'lishi, (4) "
                  'har bir muhim amal strukturaviy log qoldirishi, (5) SIGTERM kelganda joriy '
                  "so'rovlar tugatib, so'ng chiqish.</p>\n"
                  '\n'
                  '<h3>Testlash va topshirish</h3>\n'
                  "<p>5-darsda o'rgangan pytest+AsyncMock naqshidan foydalanib, kamida ikkita test "
                  'yozing: biri <code>build_dispatcher</code> ikkala routerni (Mini App va '
                  "Payments) haqiqatan ham qo'shganini tekshirsin, ikkinchisi "
                  '<code>graceful_shutdown</code> chaqirilganda bot sessiyasi yopilishini '
                  "tasdiqlasin. Testlar &mdash; capstone'ning &ldquo;ishlaydi&rdquo; degan "
                  "da'vosini so'z bilan emas, kod bilan isbotlaydi, aynan shu sabab har bir "
                  'production-daraja loyihada talab qilinadi.</p>',
  'text_content_ru': '<h3>Краткое повторение: уроки 7-12</h3>\n'
                     '<p>Этот урок &mdash; второе повторение и одновременно финальный '
                     'capstone-проект курса. Сначала соберём воедино темы уровня production, '
                     'изученные в уроках 7-12:</p>\n'
                     '<ul>\n'
                     '<li><strong>Урок 7</strong> &mdash; структурное логирование (structlog, '
                     'привязка chat_id/user_id через contextvars к каждому update), отслеживание '
                     'ошибок через Sentry, метрики Prometheus.</li>\n'
                     '<li><strong>Урок 8</strong> &mdash; распределённый rate-limiting на Redis: '
                     'token bucket, лимиты на пользователя и глобальные, временный бан.</li>\n'
                     '<li><strong>Урок 9</strong> &mdash; внутреннее устройство Dispatcher/Router: '
                     'outer middleware работает всегда, inner middleware &mdash; только при '
                     'совпадении фильтра, порядок регистрации определяет порядок цепочки.</li>\n'
                     '<li><strong>Урок 10</strong> &mdash; bot-farm: один код, много токенов '
                     'ботов, изоляция тенантов через bot_id.</li>\n'
                     '<li><strong>Урок 11</strong> &mdash; i18n: конвейер gettext .pot/.po/.mo, '
                     'определение locale через middleware.</li>\n'
                     '<li><strong>Урок 12</strong> &mdash; graceful shutdown: SIGTERM, '
                     'ограниченный drain, blue-green деплой.</li>\n'
                     '</ul>\n'
                     '<p>Все эти темы &mdash; вместе с изученными в начале курса (уроки 0-6) Mini '
                     'App, безопасностью initData, реальными Telegram Payments и Redis-backed FSM '
                     '&mdash; теперь объединяются в одну работающую систему.</p>\n'
                     '\n'
                     '<h3>Архитектура capstone: все части вместе</h3>\n'
                     '<p>Финальный проект &mdash; например, бот, &laquo;продающий премиум-подписку '
                     'на курсы&raquo; &mdash; должен состоять из следующих слоёв: пользователь '
                     'видит продукт через Mini App (урок 0), Mini App отправляет '
                     '<code>initData</code> на backend, а backend подтверждает его через HMAC '
                     '(урок 1), пользователь оплачивает через настоящие Telegram Payments &mdash; '
                     'invoice, pre_checkout_query, successful_payment (уроки 2-3), бот работает '
                     'как несколько воркеров и хранит состояние FSM в Redis (урок 4), каждый '
                     'запрос пишет структурный лог и проходит через rate-limit (уроки 7-8), а при '
                     'деплое срабатывает graceful shutdown (урок 12).</p>\n'
                     '<pre class="mermaid">\n'
                     'flowchart TB\n'
                     '  subgraph Frontend\n'
                     '    MA["Mini App\n'
                     '(Telegram.WebApp JS)"]\n'
                     '  end\n'
                     '  subgraph Backend\n'
                     '    V["Валидация initData\n'
                     '(HMAC-SHA256)"]\n'
                     '    API["FastAPI/aiohttp\n'
                     'backend"]\n'
                     '  end\n'
                     '  subgraph BotLayer["Слой бота (N воркеров)"]\n'
                     '    W1["Воркер #1"]\n'
                     '    W2["Воркер #2"]\n'
                     '  end\n'
                     '  subgraph Shared["Общая инфраструктура"]\n'
                     '    R[("Redis\n'
                     'FSM + rate-limit")]\n'
                     '    DB[("PostgreSQL")]\n'
                     '    LOG["Structured logs\n'
                     '+ Sentry + Prometheus"]\n'
                     '  end\n'
                     '  MA -->|"initData"| V\n'
                     '  V --> API\n'
                     '  API --> W1\n'
                     '  API --> W2\n'
                     '  W1 --> R\n'
                     '  W2 --> R\n'
                     '  W1 --> DB\n'
                     '  W2 --> DB\n'
                     '  W1 -.->|"successful_payment"| DB\n'
                     '  W1 --> LOG\n'
                     '  W2 --> LOG\n'
                     '</pre>\n'
                     '<p>Диаграмма &mdash; и есть итог курса: каждый блок был глубоко изучен в '
                     'отдельном уроке, теперь вместе они образуют одну работающую систему.</p>\n'
                     '\n'
                     '<h3>Почему строить именно в таком порядке</h3>\n'
                     '<p>Рекомендуемый порядок при написании capstone с нуля: сначала подключите '
                     'Redis FSM и логирование (без них последующие шаги трудно отлаживать), затем '
                     'добавьте Mini App + валидацию initData, потом подключите поток Payments (это '
                     'часть с наибольшим количеством внешних зависимостей &mdash; если оставить её '
                     'напоследок, остальные части уже будут работать), и наконец доведите до '
                     '&laquo;готовности к production&raquo; через rate-limiting и graceful '
                     'shutdown.</p>\n'
                     '\n'
                     '<h3>Критерии оценки</h3>\n'
                     '<p>Этот capstone оценивается по следующим критериям: (1) initData безопасно '
                     'подтверждается через Mini App, (2) минимум один настоящий поток Payments '
                     '(invoice &rarr; pre_checkout_query &rarr; successful_payment) полностью '
                     'работает, (3) состояние FSM хранится в Redis и является общим минимум между '
                     'двумя воркерами, (4) каждое важное действие оставляет структурный лог, (5) '
                     'при получении SIGTERM текущие запросы завершаются, и только потом происходит '
                     'выход.</p>\n'
                     '\n'
                     '<h3>Тестирование и сдача</h3>\n'
                     '<p>Используя паттерн pytest+AsyncMock из урока 5, напишите минимум два '
                     'теста: один должен проверять, что <code>build_dispatcher</code> '
                     'действительно подключает оба роутера (Mini App и Payments), второй &mdash; '
                     'что при вызове <code>graceful_shutdown</code> сессия бота закрывается. Тесты '
                     'доказывают утверждение capstone &laquo;это работает&raquo; не словами, а '
                     'кодом — именно поэтому они обязательны в любом проекте '
                     'production-уровня.</p>',
  'code_content': '"""Capstone loyiha skeleti: barcha qismlarni bog\'lovchi entrypoint.\n'
                  '\n'
                  "bot.py — RedisStorage, Payments handlerlari, i18n/logging middleware'lari\n"
                  "va graceful shutdown'ni bitta joyda ulaydi. Har bir qism avvalgi\n"
                  "darslarda alohida chuqur o'rganilgan — bu yerda faqat ULASH ko'rsatilgan.\n"
                  '"""\n'
                  'from __future__ import annotations\n'
                  '\n'
                  'import asyncio\n'
                  'import logging\n'
                  'import signal\n'
                  '\n'
                  'import structlog\n'
                  'from aiogram import Bot, Dispatcher, Router\n'
                  'from aiogram.fsm.storage.redis import RedisStorage\n'
                  'from aiogram.client.default import DefaultBotProperties\n'
                  'from aiogram.enums import ParseMode\n'
                  '\n'
                  '# --- 4-dars: Redis FSM storage --------------------------------------------\n'
                  'storage = RedisStorage.from_url("redis://localhost:6379/0")\n'
                  '\n'
                  '# --- 7-dars: strukturaviy logging -----------------------------------------\n'
                  'logger = structlog.get_logger("capstone_bot")\n'
                  '\n'
                  '# --- 8-dars: rate limiting va 9-dars: middleware zanjiri -------------------\n'
                  'from rate_limit_middleware import RedisRateLimitMiddleware   # 8-darsdan\n'
                  'from logging_middleware import RequestContextMiddleware      # 7-darsdan\n'
                  'from i18n_middleware import I18nMiddleware                   # 11-darsdan\n'
                  '\n'
                  '# --- 0-1-darslar: Mini App + initData validatsiyasi ------------------------\n'
                  'from mini_app_routes import mini_app_router                  # 0-1-darslardan\n'
                  '\n'
                  '# --- 2-3-darslar: real Payments ---------------------------------------------\n'
                  'from payments_router import payments_router                  # 2-3-darslardan\n'
                  '\n'
                  '# --- 12-dars: graceful shutdown ---------------------------------------------\n'
                  'from graceful_shutdown import install_signal_handlers\n'
                  '\n'
                  '\n'
                  'def build_dispatcher(db, redis_client) -> Dispatcher:\n'
                  '    dp = Dispatcher(storage=storage)\n'
                  '\n'
                  '    # Outer middleware — HAR bir update uchun, tartib muhim (9-dars):\n'
                  '    # avval kontekst/log, keyin locale, keyin rate-limit.\n'
                  '    dp.update.outer_middleware(RequestContextMiddleware())\n'
                  '    dp.update.outer_middleware(I18nMiddleware(db=db))\n'
                  '    dp.update.outer_middleware(RedisRateLimitMiddleware(redis=redis_client))\n'
                  '\n'
                  '    dp.include_router(mini_app_router)\n'
                  '    dp.include_router(payments_router)\n'
                  '    return dp\n'
                  '\n'
                  '\n'
                  'async def main() -> None:\n'
                  '    bot = Bot(\n'
                  '        token="BOT_TOKEN",\n'
                  '        default=DefaultBotProperties(parse_mode=ParseMode.HTML),\n'
                  '    )\n'
                  '\n'
                  '    import redis.asyncio as redis\n'
                  '    redis_client = redis.from_url("redis://localhost:6379/1")\n'
                  '    db = None  # loyihaning haqiqiy DB ulanish obyekti\n'
                  '\n'
                  '    dp = build_dispatcher(db, redis_client)\n'
                  '    install_signal_handlers(bot)   # 12-dars: SIGTERM -> drain -> yopish\n'
                  '\n'
                  '    logger.info("capstone_bot_started")\n'
                  '    await dp.start_polling(bot, handle_signals=False)\n'
                  '\n'
                  '\n'
                  'if __name__ == "__main__":\n'
                  '    asyncio.run(main())\n'
                  '\n'
                  '\n'
                  '# --- 5-dars: capstone uchun minimal test misoli ----------------------------\n'
                  "# To'liq testlash 5-darsda o'rgangan pytest+AsyncMock naqshiga tayanadi;\n"
                  "# bu yerda faqat ulash to'g'riligini tekshiruvchi bitta misol keltirilgan.\n"
                  'import pytest\n'
                  'from unittest.mock import AsyncMock\n'
                  '\n'
                  '\n'
                  '@pytest.mark.asyncio\n'
                  'async def test_build_dispatcher_includes_both_routers() -> None:\n'
                  '    fake_redis = AsyncMock()\n'
                  '    dp = build_dispatcher(db=None, redis_client=fake_redis)\n'
                  '\n'
                  '    included_routers = {r.name for r in dp.sub_routers}\n'
                  '    assert "mini_app" in included_routers\n'
                  '    assert "payments" in included_routers\n'
                  '\n'
                  '\n'
                  '@pytest.mark.asyncio\n'
                  'async def test_graceful_shutdown_closes_bot_session() -> None:\n'
                  '    fake_bot = AsyncMock()\n'
                  '    from graceful_shutdown import graceful_shutdown\n'
                  '\n'
                  '    await graceful_shutdown(fake_bot)\n'
                  '\n'
                  '    fake_bot.session.close.assert_awaited_once()',
  'code_content_ru': '"""Скелет capstone-проекта: entrypoint, связывающий все части.\n'
                     '\n'
                     'bot.py — соединяет в одном месте RedisStorage, хендлеры Payments,\n'
                     'middleware для i18n/логирования и graceful shutdown. Каждая часть\n'
                     'подробно изучена в отдельном уроке — здесь показана только СВЯЗКА.\n'
                     '"""\n'
                     'from __future__ import annotations\n'
                     '\n'
                     'import asyncio\n'
                     'import logging\n'
                     'import signal\n'
                     '\n'
                     'import structlog\n'
                     'from aiogram import Bot, Dispatcher, Router\n'
                     'from aiogram.fsm.storage.redis import RedisStorage\n'
                     'from aiogram.client.default import DefaultBotProperties\n'
                     'from aiogram.enums import ParseMode\n'
                     '\n'
                     '# --- Урок 4: Redis FSM storage '
                     '--------------------------------------------\n'
                     'storage = RedisStorage.from_url("redis://localhost:6379/0")\n'
                     '\n'
                     '# --- Урок 7: структурное логирование '
                     '--------------------------------------\n'
                     'logger = structlog.get_logger("capstone_bot")\n'
                     '\n'
                     '# --- Урок 8: rate limiting и урок 9: цепочка middleware '
                     '--------------------\n'
                     'from rate_limit_middleware import RedisRateLimitMiddleware   # из урока 8\n'
                     'from logging_middleware import RequestContextMiddleware      # из урока 7\n'
                     'from i18n_middleware import I18nMiddleware                   # из урока 11\n'
                     '\n'
                     '# --- Уроки 0-1: Mini App + валидация initData '
                     '------------------------------\n'
                     'from mini_app_routes import mini_app_router                  # из уроков '
                     '0-1\n'
                     '\n'
                     '# --- Уроки 2-3: настоящие Payments '
                     '------------------------------------------\n'
                     'from payments_router import payments_router                  # из уроков '
                     '2-3\n'
                     '\n'
                     '# --- Урок 12: graceful shutdown '
                     '---------------------------------------------\n'
                     'from graceful_shutdown import install_signal_handlers\n'
                     '\n'
                     '\n'
                     'def build_dispatcher(db, redis_client) -> Dispatcher:\n'
                     '    dp = Dispatcher(storage=storage)\n'
                     '\n'
                     '    # Outer middleware — для КАЖДОГО update, порядок важен (урок 9):\n'
                     '    # сначала контекст/лог, затем locale, затем rate-limit.\n'
                     '    dp.update.outer_middleware(RequestContextMiddleware())\n'
                     '    dp.update.outer_middleware(I18nMiddleware(db=db))\n'
                     '    '
                     'dp.update.outer_middleware(RedisRateLimitMiddleware(redis=redis_client))\n'
                     '\n'
                     '    dp.include_router(mini_app_router)\n'
                     '    dp.include_router(payments_router)\n'
                     '    return dp\n'
                     '\n'
                     '\n'
                     'async def main() -> None:\n'
                     '    bot = Bot(\n'
                     '        token="BOT_TOKEN",\n'
                     '        default=DefaultBotProperties(parse_mode=ParseMode.HTML),\n'
                     '    )\n'
                     '\n'
                     '    import redis.asyncio as redis\n'
                     '    redis_client = redis.from_url("redis://localhost:6379/1")\n'
                     '    db = None  # реальный объект подключения к БД вашего проекта\n'
                     '\n'
                     '    dp = build_dispatcher(db, redis_client)\n'
                     '    install_signal_handlers(bot)   # урок 12: SIGTERM -> drain -> закрытие\n'
                     '\n'
                     '    logger.info("capstone_bot_started")\n'
                     '    await dp.start_polling(bot, handle_signals=False)\n'
                     '\n'
                     '\n'
                     'if __name__ == "__main__":\n'
                     '    asyncio.run(main())\n'
                     '\n'
                     '\n'
                     '# --- Урок 5: минимальный пример теста для capstone '
                     '--------------------------\n'
                     '# Полноценное тестирование опирается на паттерн pytest+AsyncMock из урока '
                     '5;\n'
                     '# здесь приведён только пример проверки корректности связки.\n'
                     'import pytest\n'
                     'from unittest.mock import AsyncMock\n'
                     '\n'
                     '\n'
                     '@pytest.mark.asyncio\n'
                     'async def test_build_dispatcher_includes_both_routers() -> None:\n'
                     '    fake_redis = AsyncMock()\n'
                     '    dp = build_dispatcher(db=None, redis_client=fake_redis)\n'
                     '\n'
                     '    included_routers = {r.name for r in dp.sub_routers}\n'
                     '    assert "mini_app" in included_routers\n'
                     '    assert "payments" in included_routers\n'
                     '\n'
                     '\n'
                     '@pytest.mark.asyncio\n'
                     'async def test_graceful_shutdown_closes_bot_session() -> None:\n'
                     '    fake_bot = AsyncMock()\n'
                     '    from graceful_shutdown import graceful_shutdown\n'
                     '\n'
                     '    await graceful_shutdown(fake_bot)\n'
                     '\n'
                     '    fake_bot.session.close.assert_awaited_once()',
  'sample': {'title': "Namuna: to'liq capstone loyihaning fayl tuzilishi va bog'lovchi kod",
             'description': "Barcha darslarda o'rganilgan qismlarni birlashtiruvchi loyiha skeleti",
             'sample_type': 'code',
             'code_files': [{'filename': 'project_structure.txt',
                             'language': 'text',
                             'code': 'capstone_bot/\n'
                                     '├── bot.py                      # entrypoint — '
                                     'build_dispatcher(), main()\n'
                                     '├── mini_app_routes.py          # 0-1-dars: web_app tugmasi '
                                     '+ initData validatsiyasi\n'
                                     '├── payments_router.py          # 2-3-dars: invoice, '
                                     'pre_checkout, successful_payment\n'
                                     '├── fsm_storage.py              # 4-dars: RedisStorage '
                                     'sozlamalari\n'
                                     '├── logging_middleware.py       # 7-dars: structlog + '
                                     'contextvars\n'
                                     '├── rate_limit_middleware.py    # 8-dars: Redis token '
                                     'bucket\n'
                                     '├── i18n_middleware.py          # 11-dars: locale aniqlash\n'
                                     '├── graceful_shutdown.py        # 12-dars: SIGTERM, drain, '
                                     'health-check\n'
                                     '└── tests/\n'
                                     '    └── test_handlers.py        # 5-dars: pytest + '
                                     'AsyncMock'},
                            {'filename': 'bot.py',
                             'language': 'python',
                             'code': 'from aiogram import Bot, Dispatcher\n'
                                     'from aiogram.fsm.storage.redis import RedisStorage\n'
                                     '\n'
                                     'from mini_app_routes import mini_app_router\n'
                                     'from payments_router import payments_router\n'
                                     'from logging_middleware import RequestContextMiddleware\n'
                                     'from rate_limit_middleware import RedisRateLimitMiddleware\n'
                                     'from graceful_shutdown import install_signal_handlers\n'
                                     '\n'
                                     '\n'
                                     'def build_dispatcher(redis_client) -> Dispatcher:\n'
                                     '    dp = '
                                     'Dispatcher(storage=RedisStorage.from_url("redis://localhost:6379/0"))\n'
                                     '    dp.update.outer_middleware(RequestContextMiddleware())\n'
                                     '    '
                                     'dp.update.outer_middleware(RedisRateLimitMiddleware(redis=redis_client))\n'
                                     '    dp.include_router(mini_app_router)\n'
                                     '    dp.include_router(payments_router)\n'
                                     '    return dp'}]},
  'task': {'task_title': "CAPSTONE: Mini App + real to'lovlar + Redis FSM'li ilg'or Telegram bot",
           'task_title_ru': 'КАПСТОУН: продвинутый Telegram-бот с Mini App + реальными платежами + '
                            'Redis FSM',
           'task_description': "Kurs davomida o'rgangan mavzularning kamida to'rttasini "
                               "birlashtiruvchi to'liq ishlaydigan Telegram bot qiling: (1) Mini "
                               "App orqali mahsulot ko'rsatish va backend'da initData'ni HMAC "
                               'bilan tasdiqlash, (2) real Telegram Payments oqimi (invoice, '
                               'pre_checkout_query, successful_payment), (3) RedisStorage orqali '
                               "FSM, kamida ikkita worker jarayoni bilan sinab ko'ring, (4) "
                               "strukturaviy logging yoki Redis rate-limiting'dan kamida bittasi, "
                               '(5) SIGTERM bilan graceful shutdown.',
           'task_description_ru': 'Постройте полностью работающего Telegram-бота, объединяющего '
                                  'минимум четыре темы курса: (1) показ товара через Mini App и '
                                  'подтверждение initData через HMAC на backend, (2) настоящий '
                                  'поток Telegram Payments (invoice, pre_checkout_query, '
                                  'successful_payment), (3) FSM через RedisStorage, проверенный '
                                  'минимум с двумя воркер-процессами, (4) минимум одно из — '
                                  'структурное логирование или Redis rate-limiting, (5) graceful '
                                  'shutdown по SIGTERM.',
           'task_requirements': '1) Mini App sahifasi kamida bitta interaktiv element (masalan '
                                "MainButton) bilan ishlashi va initData backend'da HMAC-SHA256 "
                                "orqali tasdiqlanishi shart. 2) Payments oqimi to'liq: invoice "
                                'yuborilishi, pre_checkout_query 10 soniya ichida javob berilishi, '
                                "successful_payment DB'ga yozilishi. 3) FSM holati ikkinchi worker "
                                "jarayonida ham ko'rinishi kerak (Redis orqali). 4) Kamida bitta "
                                'production-daraja komponent (logging yoki rate-limit) ishlab '
                                "turishi. 5) SIGTERM kelganda joriy so'rov tugab, keyin process "
                                'chiqishi kerak.',
           'task_requirements_ru': '1) Страница Mini App должна работать минимум с одним '
                                   'интерактивным элементом (например, MainButton), а initData '
                                   'должен подтверждаться на backend через HMAC-SHA256. 2) Поток '
                                   'Payments должен быть полным: отправка invoice, ответ на '
                                   'pre_checkout_query в течение 10 секунд, запись '
                                   'successful_payment в БД. 3) Состояние FSM должно быть видно и '
                                   'во втором воркер-процессе (через Redis). 4) Минимум один '
                                   'production-компонент (логирование или rate-limit) должен '
                                   'работать. 5) При получении SIGTERM текущий запрос должен '
                                   'завершиться, и только потом процесс должен выйти.',
           'task_technologies': 'aiogram 3.x, Telegram.WebApp JS API, HMAC-SHA256, Telegram '
                                'Payments API, RedisStorage, structlog, asyncio signal handling',
           'task_deadline_days': 12},
  'exercises': [{'title': 'Capstone qurish tartibi',
                 'title_ru': 'Порядок построения capstone',
                 'description': "Capstone'ni noldan qurishda tavsiya etilgan birinchi qadam qaysi?",
                 'description_ru': 'Какой рекомендуемый первый шаг при построении capstone с нуля?',
                 'exercise_type': 'multiple_choice',
                 'options': ["Redis FSM va logging'ni ulash — bularsiz keyingi qadamlarni debug "
                             'qilish qiyin',
                             'Darhol Payments oqimini ulash, chunki u eng muhim qism',
                             'Avval frontend Mini App dizaynini pikselgacha tugatish',
                             "Rate-limiting'ni birinchi qo'shish, qolganini keyin"],
                 'options_ru': ['Подключить Redis FSM и логирование — без них сложно отлаживать '
                                'следующие шаги',
                                'Сразу подключить поток Payments, так как это самая важная часть',
                                'Сначала довести дизайн Mini App до пикселя',
                                'Сначала добавить rate-limiting, остальное потом'],
                 'correct_answers': 'A',
                 'is_multiple_select': False,
                 'hint': "O'ylab ko'ring: keyingi barcha qadamlarni kuzatish/debug qilish uchun "
                         'nima kerak?',
                 'hint_ru': 'Подумайте: что нужно, чтобы отслеживать/отлаживать все последующие '
                            'шаги?',
                 'explanation': "Logging va Redis FSM infratuzilma darajasidagi asos bo'lgani "
                                "uchun ular birinchi bo'lib ulanadi — shundan keyingi qadamlarni "
                                'kuzatish osonlashadi.',
                 'difficulty_level': 'Medium',
                 'points': 8},
                {'title': 'Xavfsizlik talabi',
                 'title_ru': 'Требование безопасности',
                 'description': "Capstone'da Mini App'dan kelgan ma'lumotni backend har doim nima "
                                'orqali tasdiqlashi shart: ___-SHA256',
                 'description_ru': 'Через что backend обязательно должен подтверждать данные, '
                                   'пришедшие от Mini App в capstone: ___-SHA256',
                 'exercise_type': 'fill_in_blank',
                 'correct_answers': 'HMAC',
                 'hint': "1-darsda o'rgangan initData validatsiya algoritmining nomi.",
                 'hint_ru': 'Название алгоритма валидации initData, изученного в уроке 1.',
                 'difficulty_level': 'Easy',
                 'points': 5}]}]
