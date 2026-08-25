"""HTML course for children aged 7-12 (Uzbek-primary, Russian translations).

Beginner, first web page. Warm, simple language for kids. HTML renders in a
real browser, so every `sample` uses sample_type "web" (html_code + css) so the
child sees the actual colourful page, and every `task` asks the child to build
a small page and submit their index.html file for review.

Bridges kids toward the main HTML/CSS track. Reviewed by a human before
seeding; is_published stays False (flipped on after review).
"""

COURSE = {
    "title": "HTML bilan birinchi vebsahifa (bolalar uchun)",
    "title_ru": "Первая веб-страница на HTML (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun HTML asosida birinchi vebsahifa yasash "
        "kursi. Sarlavha va matn yozishni, rang berishni, rasm qo'yishni, "
        "ro'yxat va havola yaratishni o'rganamiz hamda o'zimiz haqimizdagi "
        "chiroyli sahifani birga yasaymiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: делаем первую веб-страницу на HTML. Научимся "
        "писать заголовки и текст, раскрашивать страницу, добавлять картинки, "
        "списки и ссылки, а также вместе создадим красивую страницу о себе."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": None,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "Vebsahifa va birinchi teglar",
        "title_ru": "Веб-страница и первые теги",
        "points_reward": 15,
        "text_content": (
            "<h2>Vebsahifa nima?</h2>"
            "<p>Internetdagi har bir sahifa — masalan multfilm sayti yoki o'yin "
            "sahifasi — <b>HTML</b> yordamida yasalgan. HTML — bu brauzerga "
            "(Chrome, Firefox) sahifada nima ko'rsatishni aytadigan til.</p>"
            "<h2>Teg nima?</h2>"
            "<p>HTMLda biz <b>teg</b>lar yozamiz. Teg — bu burchak qavslar "
            "<code>&lt; &gt;</code> ichidagi buyruq. Ko'p teglar juft bo'ladi: "
            "<b>ochuvchi</b> va <b>yopuvchi</b>.</p>"
            "<pre><code>&lt;h1&gt;Salom!&lt;/h1&gt;</code></pre>"
            "<p>Bu yerda <code>&lt;h1&gt;</code> — ochuvchi teg (katta sarlavha "
            "boshlanadi), <code>&lt;/h1&gt;</code> — yopuvchi teg (sarlavha "
            "tugaydi). Ular orasidagi <b>Salom!</b> — ekranda ko'rinadigan matn.</p>"
            "<h2>Ikkita muhim teg</h2>"
            "<ul>"
            "<li><code>&lt;h1&gt;...&lt;/h1&gt;</code> — eng katta <b>sarlavha</b>.</li>"
            "<li><code>&lt;p&gt;...&lt;/p&gt;</code> — oddiy <b>matn</b> (paragraf).</li>"
            "</ul>"
            "<h3>Brauzer HTMLni qanday ko'rsatadi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Biz HTML yozamiz\"] --> B[\"Brauzer o'qiydi\"]\n"
            "  B --> C[\"Chiroyli sahifa ko'rinadi\"]\n"
            "</pre>"
            "<p>Biz teglarni yozamiz, brauzer ularni o'qib, chiroyli sahifaga "
            "aylantiradi.</p>"
        ),
        "text_content_ru": (
            "<h2>Что такое веб-страница?</h2>"
            "<p>Каждая страница в интернете — например сайт мультфильмов или "
            "страница игры — сделана с помощью <b>HTML</b>. HTML — это язык, "
            "который говорит браузеру (Chrome, Firefox), что показать на "
            "странице.</p>"
            "<h2>Что такое тег?</h2>"
            "<p>В HTML мы пишем <b>теги</b>. Тег — это команда в угловых скобках "
            "<code>&lt; &gt;</code>. Многие теги парные: <b>открывающий</b> и "
            "<b>закрывающий</b>.</p>"
            "<pre><code>&lt;h1&gt;Salom!&lt;/h1&gt;</code></pre>"
            "<p>Здесь <code>&lt;h1&gt;</code> — открывающий тег (начинается "
            "большой заголовок), <code>&lt;/h1&gt;</code> — закрывающий тег "
            "(заголовок заканчивается). Между ними <b>Salom!</b> — текст, "
            "который виден на экране.</p>"
            "<h2>Два важных тега</h2>"
            "<ul>"
            "<li><code>&lt;h1&gt;...&lt;/h1&gt;</code> — самый большой "
            "<b>заголовок</b>.</li>"
            "<li><code>&lt;p&gt;...&lt;/p&gt;</code> — обычный <b>текст</b> "
            "(абзац).</li>"
            "</ul>"
            "<h3>Как браузер показывает HTML</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Biz HTML yozamiz\"] --> B[\"Brauzer o'qiydi\"]\n"
            "  B --> C[\"Chiroyli sahifa ko'rinadi\"]\n"
            "</pre>"
            "<p>Мы пишем теги, браузер читает их и превращает в красивую "
            "страницу.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Birinchi sahifa",
            "description": (
                "Katta sarlavha va bitta matndan iborat eng oddiy sahifa. "
                "O'ngdagi oynada natijani ko'rasiz."
            ),
            "sample_type": "web",
            "html_code": (
                "<h1>Salom!</h1>\n"
                "<p>Bu mening birinchi vebsahifam.</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "HTML nima uchun kerak?",
                "title_ru": "Для чего нужен HTML?",
                "description": "HTML yordamida biz nima yasaymiz?",
                "description_ru": "Что мы создаём с помощью HTML?",
                "exercise_type": "multiple_choice",
                "options": ["Vebsahifalar", "Muzqaymoq", "Qo'shiq", "Rasm chizadigan qalam"],
                "options_ru": ["Веб-страницы", "Мороженое", "Песню", "Карандаш для рисования"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Internetdagi sahifalar shu til bilan yasaladi.",
                "hint_ru": "Страницы в интернете делаются на этом языке.",
                "explanation": "HTML — vebsahifalarni yasash uchun ishlatiladigan til.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Teg qanday belgilar ichida yoziladi?",
                "title_ru": "В каких символах пишется тег?",
                "description": "Teg qaysi belgilar ichiga yoziladi?",
                "description_ru": "В какие символы заключается тег?",
                "exercise_type": "multiple_choice",
                "options": ["< va > (burchak qavslar)", "( va )", "[ va ]", "{ va }"],
                "options_ru": ["< и > (угловые скобки)", "( и )", "[ и ]", "{ и }"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ular burchakka o'xshaydi.",
                "hint_ru": "Они похожи на уголки.",
                "explanation": "Teglar burchak qavslar < > ichida yoziladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sarlavha tegi",
                "title_ru": "Тег заголовка",
                "description": "Eng katta sarlavhani yozish uchun bo'sh joyni to'ldiring: '<___>Salom</h1>'",
                "description_ru": "Заполни пропуск, чтобы написать самый большой заголовок: '<___>Salom</h1>'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "h1",
                "correct_answers_ru": "h1",
                "hint": "Yopuvchi tegga qarang: </h1>.",
                "hint_ru": "Посмотри на закрывающий тег: </h1>.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sarlavhani tuzing",
                "title_ru": "Собери заголовок",
                "description": "Bloklarni to'g'ri tartibga qo'yib, sarlavha yasang.",
                "description_ru": "Расставь блоки по порядку, чтобы получился заголовок.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<h1>", "Salom", "</h1>"],
                "drag_items_ru": ["<h1>", "Salom", "</h1>"],
                "correct_order": ["<h1>", "Salom", "</h1>"],
                "hint": "Avval ochuvchi teg, keyin matn, oxirida yopuvchi teg.",
                "hint_ru": "Сначала открывающий тег, потом текст, в конце закрывающий тег.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mening birinchi sahifam",
            "task_title_ru": "Проект: моя первая страница",
            "task_description": (
                "Bitta katta sarlavha (ismingiz) va bitta matndan iborat sahifa "
                "yasang. Faylni index.html deb nomlab, ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу с одним большим заголовком (твоё имя) и одним "
                "абзацем текста. Назови файл index.html, заархивируй в ZIP и "
                "отправь."
            ),
            "task_requirements": (
                "• Bitta <h1> sarlavha bo'lsin (ismingiz)\n"
                "• Bitta <p> matn bo'lsin (o'zingiz haqingizda bir gap)\n"
                "• Har bir teg to'g'ri yopilsin"
            ),
            "task_requirements_ru": (
                "• Один заголовок <h1> (твоё имя)\n"
                "• Один абзац <p> (одно предложение о себе)\n"
                "• Каждый тег правильно закрыт"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Sarlavhalar va matn",
        "title_ru": "Заголовки и текст",
        "points_reward": 20,
        "text_content": (
            "<h2>Turli o'lchamdagi sarlavhalar</h2>"
            "<p>HTMLda 6 xil sarlavha bor: <code>&lt;h1&gt;</code> eng katta, "
            "<code>&lt;h6&gt;</code> eng kichik.</p>"
            "<pre><code>&lt;h1&gt;Katta&lt;/h1&gt;\n"
            "&lt;h2&gt;O'rta&lt;/h2&gt;\n"
            "&lt;h3&gt;Kichik&lt;/h3&gt;</code></pre>"
            "<h2>Matnni bezash</h2>"
            "<ul>"
            "<li><code>&lt;p&gt;...&lt;/p&gt;</code> — oddiy paragraf.</li>"
            "<li><code>&lt;b&gt;...&lt;/b&gt;</code> — <b>qalin</b> (qora) harflar.</li>"
            "<li><code>&lt;br&gt;</code> — yangi qatorga o'tadi (yopuvchi tegi yo'q).</li>"
            "</ul>"
            "<p>Masalan: <code>&lt;p&gt;Men &lt;b&gt;futbol&lt;/b&gt; yaxshi "
            "ko'raman&lt;/p&gt;</code> — bu yerda \"futbol\" so'zi qalin bo'ladi.</p>"
        ),
        "text_content_ru": (
            "<h2>Заголовки разного размера</h2>"
            "<p>В HTML есть 6 видов заголовков: <code>&lt;h1&gt;</code> самый "
            "большой, <code>&lt;h6&gt;</code> самый маленький.</p>"
            "<pre><code>&lt;h1&gt;Katta&lt;/h1&gt;\n"
            "&lt;h2&gt;O'rta&lt;/h2&gt;\n"
            "&lt;h3&gt;Kichik&lt;/h3&gt;</code></pre>"
            "<h2>Оформление текста</h2>"
            "<ul>"
            "<li><code>&lt;p&gt;...&lt;/p&gt;</code> — обычный абзац.</li>"
            "<li><code>&lt;b&gt;...&lt;/b&gt;</code> — <b>жирные</b> буквы.</li>"
            "<li><code>&lt;br&gt;</code> — переход на новую строку (без закрывающего тега).</li>"
            "</ul>"
            "<p>Например: <code>&lt;p&gt;Men &lt;b&gt;futbol&lt;/b&gt; yaxshi "
            "ko'raman&lt;/p&gt;</code> — здесь слово \"futbol\" станет жирным.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Men haqimda",
            "description": "Ikki sarlavha, matn va bitta qalin so'zdan iborat kichik sahifa.",
            "sample_type": "web",
            "html_code": (
                "<h1>Ali</h1>\n"
                "<h2>Men haqimda</h2>\n"
                "<p>Menga <b>rasm chizish</b> juda yoqadi.</p>\n"
                "<p>Sinfim: 3-A</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Eng katta sarlavha",
                "title_ru": "Самый большой заголовок",
                "description": "Qaysi teg eng katta sarlavhani yasaydi?",
                "description_ru": "Какой тег делает самый большой заголовок?",
                "exercise_type": "multiple_choice",
                "options": ["<h1>", "<h6>", "<p>", "<b>"],
                "options_ru": ["<h1>", "<h6>", "<p>", "<b>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Raqam qancha kichik bo'lsa, sarlavha shuncha katta.",
                "hint_ru": "Чем меньше число, тем больше заголовок.",
                "explanation": "<h1> eng katta, <h6> eng kichik sarlavha.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Qalin harflar",
                "title_ru": "Жирные буквы",
                "description": "So'zni qalin (qora) qilish uchun qaysi teg ishlatiladi?",
                "description_ru": "Какой тег делает слово жирным?",
                "exercise_type": "multiple_choice",
                "options": ["<b>", "<p>", "<br>", "<h1>"],
                "options_ru": ["<b>", "<p>", "<br>", "<h1>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"bold\" — qalin degani.",
                "hint_ru": "\"bold\" — значит жирный.",
                "explanation": "<b> tegi ichidagi matn qalin ko'rinadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yangi qator",
                "title_ru": "Новая строка",
                "description": "Yangi qatorga o'tish uchun bo'sh joyni to'ldiring: '<___>' (yopuvchisi yo'q teg)",
                "description_ru": "Заполни пропуск для перехода на новую строку: '<___>' (тег без закрывающего)",
                "exercise_type": "fill_in_blank",
                "correct_answers": "br",
                "correct_answers_ru": "br",
                "hint": "\"break\" so'zining qisqasi.",
                "hint_ru": "Сокращение от слова \"break\".",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Paragrafni tuzing",
                "title_ru": "Собери абзац",
                "description": "Bloklarni tartibga qo'yib, matn (paragraf) yasang.",
                "description_ru": "Расставь блоки, чтобы получился абзац.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<p>", "Men futbol o'ynayman", "</p>"],
                "drag_items_ru": ["<p>", "Men futbol o'ynayman", "</p>"],
                "correct_order": ["<p>", "Men futbol o'ynayman", "</p>"],
                "hint": "Ochuvchi teg, matn, yopuvchi teg.",
                "hint_ru": "Открывающий тег, текст, закрывающий тег.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Men haqimda sahifa",
            "task_title_ru": "Проект: страница обо мне",
            "task_description": (
                "O'zingiz haqingizda sahifa yasang: ismingiz sarlavha bo'lsin, "
                "keyin sevimli mashg'ulotingiz haqida matn bo'lsin. index.html "
                "faylini ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу о себе: твоё имя как заголовок, потом текст о "
                "любимом занятии. Отправь файл index.html в ZIP."
            ),
            "task_requirements": (
                "• Kamida bitta <h1> va bitta <h2> sarlavha\n"
                "• Kamida ikkita <p> matn\n"
                "• Bitta so'z <b> bilan qalin qilingan bo'lsin"
            ),
            "task_requirements_ru": (
                "• Хотя бы один <h1> и один <h2> заголовок\n"
                "• Хотя бы два абзаца <p>\n"
                "• Одно слово выделено жирным с помощью <b>"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Ranglar berish",
        "title_ru": "Раскрашиваем страницу",
        "points_reward": 20,
        "text_content": (
            "<h2>Matn va fon rangi</h2>"
            "<p>Sahifamizni rangli qilsak, chiroyliroq bo'ladi. Buning uchun "
            "tegga <code>style</code> qo'shamiz.</p>"
            "<pre><code>&lt;h1 style=\"color: red\"&gt;Salom&lt;/h1&gt;</code></pre>"
            "<p>Bu sarlavhani <b>qizil</b> qiladi. <code>color</code> — matn rangi.</p>"
            "<pre><code>&lt;p style=\"background-color: yellow\"&gt;Matn&lt;/p&gt;</code></pre>"
            "<p><code>background-color</code> — orqa fon rangi (sariq).</p>"
            "<h2>Rang nomlari</h2>"
            "<p>Inglizcha oddiy rang nomlari: <code>red</code> (qizil), "
            "<code>blue</code> (ko'k), <code>green</code> (yashil), "
            "<code>orange</code> (to'q sariq), <code>pink</code> (pushti).</p>"
        ),
        "text_content_ru": (
            "<h2>Цвет текста и фона</h2>"
            "<p>Раскрашенная страница выглядит красивее. Для этого мы добавляем "
            "к тегу <code>style</code>.</p>"
            "<pre><code>&lt;h1 style=\"color: red\"&gt;Salom&lt;/h1&gt;</code></pre>"
            "<p>Это делает заголовок <b>красным</b>. <code>color</code> — цвет "
            "текста.</p>"
            "<pre><code>&lt;p style=\"background-color: yellow\"&gt;Matn&lt;/p&gt;</code></pre>"
            "<p><code>background-color</code> — цвет фона (жёлтый).</p>"
            "<h2>Названия цветов</h2>"
            "<p>Простые английские названия: <code>red</code> (красный), "
            "<code>blue</code> (синий), <code>green</code> (зелёный), "
            "<code>orange</code> (оранжевый), <code>pink</code> (розовый).</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Rangli sahifa",
            "description": "Qizil sarlavha va sariq fonli matn.",
            "sample_type": "web",
            "html_code": (
                "<h1 style=\"color: red\">Mening rangli sahifam</h1>\n"
                "<p style=\"background-color: yellow\">Bu matnning foni sariq.</p>\n"
                "<p style=\"color: blue\">Bu matn esa ko'k rangda.</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Matn rangi",
                "title_ru": "Цвет текста",
                "description": "Matnning rangini o'zgartirish uchun qaysi so'z ishlatiladi?",
                "description_ru": "Какое слово меняет цвет текста?",
                "exercise_type": "multiple_choice",
                "options": ["color", "background-color", "size", "font"],
                "options_ru": ["color", "background-color", "size", "font"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"color\" — rang degani.",
                "hint_ru": "\"color\" — значит цвет.",
                "explanation": "color — matn rangini, background-color — fon rangini belgilaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ko'k rang",
                "title_ru": "Синий цвет",
                "description": "Ko'k rang inglizcha qanday yoziladi?",
                "description_ru": "Как по-английски пишется синий цвет?",
                "exercise_type": "multiple_choice",
                "options": ["blue", "green", "red", "pink"],
                "options_ru": ["blue", "green", "red", "pink"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Osmon rangi.",
                "hint_ru": "Цвет неба.",
                "explanation": "blue — ko'k, green — yashil, red — qizil.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Fon rangi",
                "title_ru": "Цвет фона",
                "description": "Fon rangini berish uchun bo'sh joyni to'ldiring: 'style=\"___: yellow\"'",
                "description_ru": "Заполни пропуск для цвета фона: 'style=\"___: yellow\"'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "background-color",
                "correct_answers_ru": "background-color",
                "hint": "\"background\" — orqa fon.",
                "hint_ru": "\"background\" — фон.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Rangli sarlavhani tuzing",
                "title_ru": "Собери цветной заголовок",
                "description": "Bloklarni tartibga qo'yib, yashil sarlavha yasang.",
                "description_ru": "Расставь блоки, чтобы получился зелёный заголовок.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<h1 style=\"color: green\">", "Salom", "</h1>"],
                "drag_items_ru": ["<h1 style=\"color: green\">", "Salom", "</h1>"],
                "correct_order": ["<h1 style=\"color: green\">", "Salom", "</h1>"],
                "hint": "Rang ochuvchi teg ichida yoziladi.",
                "hint_ru": "Цвет пишется внутри открывающего тега.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Rangli sahifa",
            "task_title_ru": "Проект: цветная страница",
            "task_description": (
                "1-darsdagi sahifangizga rang qo'shing: sarlavha bir rangda, "
                "matnlardan biri boshqa rangda bo'lsin. index.html ni ZIP qilib "
                "topshiring."
            ),
            "task_description_ru": (
                "Добавь цвета на свою страницу из урока 1: заголовок одного "
                "цвета, один из абзацев другого цвета. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Sarlavhaga color bilan rang berilgan bo'lsin\n"
                "• Kamida bitta matnga rang yoki fon rangi berilsin\n"
                "• Kamida ikki xil rang ishlatilsin"
            ),
            "task_requirements_ru": (
                "• Заголовку задан цвет через color\n"
                "• Хотя бы одному абзацу задан цвет или цвет фона\n"
                "• Использованы хотя бы два разных цвета"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Rasm qo'yish",
        "title_ru": "Добавляем картинку",
        "points_reward": 20,
        "text_content": (
            "<h2>Rasm tegi</h2>"
            "<p>Sahifaga rasm qo'yish uchun <code>&lt;img&gt;</code> tegidan "
            "foydalanamiz. Bu tegning yopuvchisi yo'q.</p>"
            "<pre><code>&lt;img src=\"mushuk.jpg\" alt=\"mushuk\"&gt;</code></pre>"
            "<ul>"
            "<li><code>src</code> — rasm manzili (qaysi rasm).</li>"
            "<li><code>alt</code> — rasm ko'rinmasa chiqadigan matn (rasm nomi).</li>"
            "</ul>"
            "<h2>Rasm o'lchamini o'zgartirish</h2>"
            "<p><code>width</code> bilan rasm kengligini beramiz:</p>"
            "<pre><code>&lt;img src=\"mushuk.jpg\" alt=\"mushuk\" width=\"200\"&gt;</code></pre>"
            "<p>Bu rasmni 200 piksel kenglikda ko'rsatadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Тег картинки</h2>"
            "<p>Чтобы добавить картинку, используем тег "
            "<code>&lt;img&gt;</code>. У него нет закрывающего тега.</p>"
            "<pre><code>&lt;img src=\"mushuk.jpg\" alt=\"mushuk\"&gt;</code></pre>"
            "<ul>"
            "<li><code>src</code> — адрес картинки (какая картинка).</li>"
            "<li><code>alt</code> — текст, который появится, если картинка не "
            "видна (название картинки).</li>"
            "</ul>"
            "<h2>Меняем размер картинки</h2>"
            "<p>С помощью <code>width</code> задаём ширину картинки:</p>"
            "<pre><code>&lt;img src=\"mushuk.jpg\" alt=\"mushuk\" width=\"200\"&gt;</code></pre>"
            "<p>Это покажет картинку шириной 200 пикселей.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Rasmli sahifa",
            "description": "Sarlavha va uning ostida bitta rasm.",
            "sample_type": "web",
            "html_code": (
                "<h1>Mening sevimli hayvonim</h1>\n"
                "<img src=\"https://picsum.photos/seed/cat/240/160\" alt=\"hayvon\" width=\"240\">\n"
                "<p>Bu juda chiroyli rasm.</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Rasm tegi",
                "title_ru": "Тег картинки",
                "description": "Sahifaga rasm qo'yadigan teg qaysi?",
                "description_ru": "Какой тег добавляет картинку на страницу?",
                "exercise_type": "multiple_choice",
                "options": ["<img>", "<p>", "<h1>", "<pic>"],
                "options_ru": ["<img>", "<p>", "<h1>", "<pic>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"image\" so'zining qisqasi.",
                "hint_ru": "Сокращение от слова \"image\".",
                "explanation": "<img> tegi rasm qo'yadi; src rasm manzilini beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Rasm manzili",
                "title_ru": "Адрес картинки",
                "description": "Qaysi rasmni ko'rsatishni qaysi so'z belgilaydi?",
                "description_ru": "Какое слово указывает, какую картинку показать?",
                "exercise_type": "multiple_choice",
                "options": ["src", "alt", "width", "color"],
                "options_ru": ["src", "alt", "width", "color"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"source\" — manba degani.",
                "hint_ru": "\"source\" — значит источник.",
                "explanation": "src — rasm manzili, alt — rasm ko'rinmaganda chiqadigan nom.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Rasm kengligi",
                "title_ru": "Ширина картинки",
                "description": "Rasm kengligini berish uchun bo'sh joyni to'ldiring: 'src=\"...\" ___=\"200\"'",
                "description_ru": "Заполни пропуск для ширины картинки: 'src=\"...\" ___=\"200\"'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "width",
                "correct_answers_ru": "width",
                "hint": "\"width\" — kenglik degani.",
                "hint_ru": "\"width\" — значит ширина.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Rasm tegini tuzing",
                "title_ru": "Собери тег картинки",
                "description": "Bloklarni tartibga qo'ying: rasm tegi to'g'ri yozilsin.",
                "description_ru": "Расставь блоки: тег картинки должен быть написан правильно.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<img", "src=\"mushuk.jpg\"", "alt=\"mushuk\">"],
                "drag_items_ru": ["<img", "src=\"mushuk.jpg\"", "alt=\"mushuk\">"],
                "correct_order": ["<img", "src=\"mushuk.jpg\"", "alt=\"mushuk\">"],
                "hint": "Avval teg nomi, keyin src, keyin alt.",
                "hint_ru": "Сначала имя тега, потом src, потом alt.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Sevimli rasmim",
            "task_title_ru": "Проект: моя любимая картинка",
            "task_description": (
                "Sarlavha, bitta rasm va rasm haqida bir gap matndan iborat "
                "sahifa yasang. index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу с заголовком, одной картинкой и одним "
                "предложением о картинке. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Bitta <h1> sarlavha bo'lsin\n"
                "• Bitta <img> rasm bo'lsin (src va alt bilan)\n"
                "• Rasm haqida bitta <p> matn bo'lsin"
            ),
            "task_requirements_ru": (
                "• Один заголовок <h1>\n"
                "• Одна картинка <img> (с src и alt)\n"
                "• Один абзац <p> о картинке"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Ro'yxatlar va havolalar",
        "title_ru": "Списки и ссылки",
        "points_reward": 20,
        "text_content": (
            "<h2>Ro'yxat yasash</h2>"
            "<p>Sevimli narsalarimizni ro'yxat qilib yozishimiz mumkin. Buning "
            "uchun <code>&lt;ul&gt;</code> (ro'yxat) va <code>&lt;li&gt;</code> "
            "(har bir band) teglaridan foydalanamiz.</p>"
            "<pre><code>&lt;ul&gt;\n"
            "  &lt;li&gt;Olma&lt;/li&gt;\n"
            "  &lt;li&gt;Banan&lt;/li&gt;\n"
            "&lt;/ul&gt;</code></pre>"
            "<p>Bu ikkita nuqtali band chiqaradi: Olma va Banan.</p>"
            "<h2>Havola (link)</h2>"
            "<p>Boshqa sahifaga o'tadigan havola <code>&lt;a&gt;</code> tegi "
            "bilan yasaladi:</p>"
            "<pre><code>&lt;a href=\"https://scratch.mit.edu\"&gt;Scratch&lt;/a&gt;</code></pre>"
            "<p><code>href</code> — qayerga o'tishni ko'rsatadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Делаем список</h2>"
            "<p>Мы можем записать любимые вещи списком. Для этого используем "
            "<code>&lt;ul&gt;</code> (список) и <code>&lt;li&gt;</code> (каждый "
            "пункт).</p>"
            "<pre><code>&lt;ul&gt;\n"
            "  &lt;li&gt;Olma&lt;/li&gt;\n"
            "  &lt;li&gt;Banan&lt;/li&gt;\n"
            "&lt;/ul&gt;</code></pre>"
            "<p>Это выведет два пункта с точками: Olma и Banan.</p>"
            "<h2>Ссылка (link)</h2>"
            "<p>Ссылка на другую страницу делается тегом "
            "<code>&lt;a&gt;</code>:</p>"
            "<pre><code>&lt;a href=\"https://scratch.mit.edu\"&gt;Scratch&lt;/a&gt;</code></pre>"
            "<p><code>href</code> — указывает, куда перейти.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Sevimlilar ro'yxati",
            "description": "Nuqtali ro'yxat va bitta havola.",
            "sample_type": "web",
            "html_code": (
                "<h1>Mening sevimli mevalarim</h1>\n"
                "<ul>\n"
                "  <li>Olma</li>\n"
                "  <li>Banan</li>\n"
                "  <li>Uzum</li>\n"
                "</ul>\n"
                "<a href=\"https://scratch.mit.edu\">Scratch saytiga o'tish</a>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Ro'yxat bandi",
                "title_ru": "Пункт списка",
                "description": "Ro'yxatdagi har bir band qaysi teg bilan yoziladi?",
                "description_ru": "Каким тегом пишется каждый пункт списка?",
                "exercise_type": "multiple_choice",
                "options": ["<li>", "<ul>", "<a>", "<p>"],
                "options_ru": ["<li>", "<ul>", "<a>", "<p>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"list item\" — ro'yxat bandi.",
                "hint_ru": "\"list item\" — пункт списка.",
                "explanation": "<ul> butun ro'yxat, <li> esa uning har bir bandi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Havola tegi",
                "title_ru": "Тег ссылки",
                "description": "Boshqa saytga o'tadigan havola qaysi teg bilan yasaladi?",
                "description_ru": "Каким тегом делается ссылка на другой сайт?",
                "exercise_type": "multiple_choice",
                "options": ["<a>", "<li>", "<img>", "<h1>"],
                "options_ru": ["<a>", "<li>", "<img>", "<h1>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Juda qisqa teg — bitta harf.",
                "hint_ru": "Очень короткий тег — одна буква.",
                "explanation": "<a> tegi havola yasaydi; href qayerga o'tishni beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Havola manzili",
                "title_ru": "Адрес ссылки",
                "description": "Havola qayerga o'tishini bo'sh joyni to'ldirib ko'rsating: '<a ___=\"...\">'",
                "description_ru": "Заполни пропуск, куда ведёт ссылка: '<a ___=\"...\">'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "href",
                "correct_answers_ru": "href",
                "hint": "Havola manzilini beradigan so'z.",
                "hint_ru": "Слово, задающее адрес ссылки.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Ro'yxatni tuzing",
                "title_ru": "Собери список",
                "description": "Bloklarni tartibga qo'yib, bitta bandli ro'yxat yasang.",
                "description_ru": "Расставь блоки, чтобы получился список с одним пунктом.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<ul>", "<li>Olma</li>", "</ul>"],
                "drag_items_ru": ["<ul>", "<li>Olma</li>", "</ul>"],
                "correct_order": ["<ul>", "<li>Olma</li>", "</ul>"],
                "hint": "Ro'yxat ochiladi, band yoziladi, ro'yxat yopiladi.",
                "hint_ru": "Список открывается, пишется пункт, список закрывается.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Sevimli narsalarim ro'yxati",
            "task_title_ru": "Проект: список моих любимых вещей",
            "task_description": (
                "Sevimli narsalaringiz (o'yin, ovqat, mult) ro'yxati bo'lgan "
                "sahifa yasang va oxiriga bitta havola qo'shing. index.html ni "
                "ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу со списком любимых вещей (игра, еда, мультик) и "
                "добавь в конце одну ссылку. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Bitta <h1> sarlavha bo'lsin\n"
                "• Kamida uchta <li> bandli <ul> ro'yxat bo'lsin\n"
                "• Bitta <a> havola bo'lsin (href bilan)"
            ),
            "task_requirements_ru": (
                "• Один заголовок <h1>\n"
                "• Список <ul> хотя бы с тремя пунктами <li>\n"
                "• Одна ссылка <a> (с href)"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Tugma va yakuniy loyiha",
        "title_ru": "Кнопка и итоговый проект",
        "points_reward": 25,
        "text_content": (
            "<h2>Tugma</h2>"
            "<p>Sahifaga tugma qo'yish uchun <code>&lt;button&gt;</code> "
            "tegidan foydalanamiz:</p>"
            "<pre><code>&lt;button&gt;Bosing!&lt;/button&gt;</code></pre>"
            "<p>Tugmaga ham rang berish mumkin:</p>"
            "<pre><code>&lt;button style=\"background-color: pink\"&gt;Bosing!&lt;/button&gt;</code></pre>"
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi biz o'rgangan hamma narsani bitta sahifada birlashtiramiz: "
            "<b>sarlavha</b>, rangli <b>matn</b>, <b>rasm</b>, <b>ro'yxat</b>, "
            "<b>havola</b> va <b>tugma</b>. Bu sizning eng chiroyli sahifangiz "
            "bo'ladi!</p>"
            "<h3>Sahifa qismlari</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Sarlavha (h1)\"] --> B[\"Rasm (img)\"]\n"
            "  B --> C[\"Ro'yxat (ul, li)\"]\n"
            "  C --> D[\"Tugma (button)\"]\n"
            "</pre>"
        ),
        "text_content_ru": (
            "<h2>Кнопка</h2>"
            "<p>Чтобы добавить кнопку, используем тег "
            "<code>&lt;button&gt;</code>:</p>"
            "<pre><code>&lt;button&gt;Bosing!&lt;/button&gt;</code></pre>"
            "<p>Кнопке тоже можно задать цвет:</p>"
            "<pre><code>&lt;button style=\"background-color: pink\"&gt;Bosing!&lt;/button&gt;</code></pre>"
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим на одной странице всё, что выучили: "
            "<b>заголовок</b>, цветной <b>текст</b>, <b>картинку</b>, "
            "<b>список</b>, <b>ссылку</b> и <b>кнопку</b>. Это будет твоя самая "
            "красивая страница!</p>"
            "<h3>Части страницы</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Sarlavha (h1)\"] --> B[\"Rasm (img)\"]\n"
            "  B --> C[\"Ro'yxat (ul, li)\"]\n"
            "  C --> D[\"Tugma (button)\"]\n"
            "</pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: To'liq sahifa",
            "description": "Sarlavha, rasm, ro'yxat, havola va rangli tugmadan iborat to'liq sahifa.",
            "sample_type": "web",
            "html_code": (
                "<h1 style=\"color: purple\">Men haqimda</h1>\n"
                "<img src=\"https://picsum.photos/seed/me/220/150\" alt=\"rasm\" width=\"220\">\n"
                "<p>Menga quyidagilar yoqadi:</p>\n"
                "<ul>\n"
                "  <li>Rasm chizish</li>\n"
                "  <li>Futbol</li>\n"
                "</ul>\n"
                "<a href=\"https://scratch.mit.edu\">Sevimli saytim</a>\n"
                "<br>\n"
                "<button style=\"background-color: pink\">Salom bering!</button>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Tugma tegi",
                "title_ru": "Тег кнопки",
                "description": "Sahifaga tugma qo'yadigan teg qaysi?",
                "description_ru": "Какой тег добавляет кнопку?",
                "exercise_type": "multiple_choice",
                "options": ["<button>", "<a>", "<li>", "<img>"],
                "options_ru": ["<button>", "<a>", "<li>", "<img>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Nomi inglizcha \"tugma\" so'zi.",
                "hint_ru": "Название — английское слово \"кнопка\".",
                "explanation": "<button> tegi bosiladigan tugma yasaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tugmaga rang",
                "title_ru": "Цвет кнопки",
                "description": "Tugma foniga rang berish uchun qaysi so'z ishlatiladi?",
                "description_ru": "Каким словом задать цвет фона кнопки?",
                "exercise_type": "multiple_choice",
                "options": ["background-color", "href", "src", "alt"],
                "options_ru": ["background-color", "href", "src", "alt"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Fon rangi haqidagi darsni eslang.",
                "hint_ru": "Вспомни урок о цвете фона.",
                "explanation": "style=\"background-color: ...\" tugma foniga rang beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bo'sh joyni to'ldiring",
                "title_ru": "Заполни пропуск",
                "description": "Tugma yasash uchun to'ldiring: '<___>Bosing</button>'",
                "description_ru": "Заполни пропуск для кнопки: '<___>Bosing</button>'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "button",
                "correct_answers_ru": "button",
                "hint": "Yopuvchi tegga qarang: </button>.",
                "hint_ru": "Посмотри на закрывающий тег: </button>.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sahifa qismlarini tartibla",
                "title_ru": "Расставь части страницы",
                "description": "Chiroyli sahifada qismlar odatda qanday tartibda keladi?",
                "description_ru": "В каком порядке обычно идут части красивой страницы?",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<h1>Sarlavha</h1>", "<img src=\"rasm.jpg\" alt=\"rasm\">", "<button>Bosing</button>"],
                "drag_items_ru": ["<h1>Sarlavha</h1>", "<img src=\"rasm.jpg\" alt=\"rasm\">", "<button>Bosing</button>"],
                "correct_order": ["<h1>Sarlavha</h1>", "<img src=\"rasm.jpg\" alt=\"rasm\">", "<button>Bosing</button>"],
                "hint": "Avval sarlavha, keyin rasm, oxirida tugma.",
                "hint_ru": "Сначала заголовок, потом картинка, в конце кнопка.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Men haqimda to'liq sahifa",
            "task_title_ru": "Итоговый проект: полная страница обо мне",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: o'zingiz haqingizda "
                "to'liq va chiroyli sahifa yasang. index.html faylini ZIP qilib "
                "topshiring — bu sizning eng katta loyihangiz!"
            ),
            "task_description_ru": (
                "Объедини всё, что выучил в курсе: сделай полную и красивую "
                "страницу о себе. Отправь файл index.html в ZIP — это твой самый "
                "большой проект!"
            ),
            "task_requirements": (
                "• Rangli <h1> sarlavha bo'lsin\n"
                "• Bitta <img> rasm bo'lsin\n"
                "• Kamida uch bandli <ul> ro'yxat bo'lsin\n"
                "• Bitta <a> havola va bitta <button> tugma bo'lsin"
            ),
            "task_requirements_ru": (
                "• Цветной заголовок <h1>\n"
                "• Одна картинка <img>\n"
                "• Список <ul> хотя бы с тремя пунктами\n"
                "• Одна ссылка <a> и одна кнопка <button>"
            ),
            "task_technologies": "HTML",
            "task_deadline_days": 5,
        },
    },
]
