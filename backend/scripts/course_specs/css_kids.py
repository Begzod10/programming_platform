"""CSS course for children aged 7-12 (Uzbek-primary, Russian translations).

Sequel to course 148 (first HTML page). Teaches styling: colours, text size &
alignment, borders, padding & rounded corners, and finally a <style> block with
a class. HTML+CSS renders in a real browser, so every `sample` uses sample_type
"web" (html_code + css_code) so the child sees the actual styled page, and every
`task` asks the child to style a page and submit their index.html for review.

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "CSS bilan sahifani bezash (bolalar uchun)",
    "title_ru": "Оформляем страницу с CSS (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun HTML sahifasini CSS bilan chiroyli qilish "
        "kursi. Rang berishni, matn o'lchami va joylashuvini, chegara, ichki "
        "bo'shliq va yumaloq burchaklarni o'rganamiz hamda o'zimiz haqimizdagi "
        "sahifani go'zal bezaymiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: делаем HTML-страницу красивой с помощью CSS. "
        "Научимся задавать цвета, размер и выравнивание текста, рамки, отступы "
        "и скруглённые углы, а также красиво оформим свою страницу о себе."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": 148,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "CSS nima? Rang berish",
        "title_ru": "Что такое CSS? Задаём цвета",
        "points_reward": 15,
        "text_content": (
            "<h2>CSS nima?</h2>"
            "<p>HTML sahifamizni yasaydi, <b>CSS</b> esa uni <b>chiroyli</b> "
            "qiladi — rang, o'lcham, bo'shliqlar beradi. Eng oson yo'l — tegga "
            "<code>style</code> qo'shish.</p>"
            "<pre><code>&lt;h1 style=\"color: red\"&gt;Salom&lt;/h1&gt;</code></pre>"
            "<ul>"
            "<li><code>color</code> — matn rangi.</li>"
            "<li><code>background-color</code> — orqa fon rangi.</li>"
            "</ul>"
            "<p>Bir vaqtning o'zida ikkita bezakni <b>nuqta-vergul</b> "
            "(<code>;</code>) bilan ajratamiz:</p>"
            "<pre><code>&lt;h1 style=\"color: white; background-color: blue\"&gt;Salom&lt;/h1&gt;</code></pre>"
        ),
        "text_content_ru": (
            "<h2>Что такое CSS?</h2>"
            "<p>HTML создаёт нашу страницу, а <b>CSS</b> делает её "
            "<b>красивой</b> — задаёт цвет, размер, отступы. Самый простой "
            "способ — добавить к тегу <code>style</code>.</p>"
            "<pre><code>&lt;h1 style=\"color: red\"&gt;Salom&lt;/h1&gt;</code></pre>"
            "<ul>"
            "<li><code>color</code> — цвет текста.</li>"
            "<li><code>background-color</code> — цвет фона.</li>"
            "</ul>"
            "<p>Два оформления сразу разделяем <b>точкой с запятой</b> "
            "(<code>;</code>):</p>"
            "<pre><code>&lt;h1 style=\"color: white; background-color: blue\"&gt;Salom&lt;/h1&gt;</code></pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Rangli sarlavha",
            "description": "Oq matn, ko'k fonli sarlavha.",
            "sample_type": "web",
            "html_code": (
                "<h1 style=\"color: white; background-color: blue\">Mening sahifam</h1>\n"
                "<p style=\"color: green\">Bu matn yashil rangda.</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "CSS nima qiladi?",
                "title_ru": "Что делает CSS?",
                "description": "CSS sahifaga nima beradi?",
                "description_ru": "Что CSS добавляет странице?",
                "exercise_type": "multiple_choice",
                "options": ["Rang va bezak", "Yangi kompyuter", "Ovoz", "Internet"],
                "options_ru": ["Цвет и оформление", "Новый компьютер", "Звук", "Интернет"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "U sahifani chiroyli qiladi.",
                "hint_ru": "Он делает страницу красивой.",
                "explanation": "CSS sahifaga rang, o'lcham va bezak beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Matn rangi",
                "title_ru": "Цвет текста",
                "description": "Matn rangini o'zgartiradigan so'z qaysi?",
                "description_ru": "Какое слово меняет цвет текста?",
                "exercise_type": "multiple_choice",
                "options": ["color", "background-color", "size", "border"],
                "options_ru": ["color", "background-color", "size", "border"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"color\" — rang.",
                "hint_ru": "\"color\" — цвет.",
                "explanation": "color — matn rangi, background-color — fon rangi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ikki bezakni ajratish",
                "title_ru": "Разделить два свойства",
                "description": "Ikki bezakni ajratish uchun qaysi belgi ishlatiladi? Bo'sh joyni to'ldiring: 'color: red___ background-color: blue'",
                "description_ru": "Каким символом разделяют два свойства? Заполни пропуск: 'color: red___ background-color: blue'",
                "exercise_type": "fill_in_blank",
                "correct_answers": ";",
                "correct_answers_ru": ";",
                "hint": "Nuqta-vergul belgisi.",
                "hint_ru": "Точка с запятой.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Rangli sarlavhani tuzing",
                "title_ru": "Собери цветной заголовок",
                "description": "Bloklarni tartibga qo'yib, qizil sarlavha yasang.",
                "description_ru": "Расставь блоки, чтобы получился красный заголовок.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<h1 style=\"color: red\">", "Salom", "</h1>"],
                "drag_items_ru": ["<h1 style=\"color: red\">", "Salom", "</h1>"],
                "correct_order": ["<h1 style=\"color: red\">", "Salom", "</h1>"],
                "hint": "Ochuvchi teg (style bilan), matn, yopuvchi teg.",
                "hint_ru": "Открывающий тег (со style), текст, закрывающий тег.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Rangli sahifa",
            "task_title_ru": "Проект: цветная страница",
            "task_description": (
                "Sarlavha va ikkita matndan iborat sahifa yasang. Har biriga "
                "boshqa rang bering (color yoki background-color bilan). "
                "index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу с заголовком и двумя абзацами. Задай каждому "
                "свой цвет (через color или background-color). Отправь index.html "
                "в ZIP."
            ),
            "task_requirements": (
                "• Sarlavhaga rang berilgan bo'lsin\n"
                "• Kamida bitta matnga fon rangi (background-color) berilsin\n"
                "• Kamida uch xil rang ishlatilsin"
            ),
            "task_requirements_ru": (
                "• Заголовку задан цвет\n"
                "• Хотя бы одному абзацу задан фон (background-color)\n"
                "• Использованы хотя бы три разных цвета"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Matn o'lchami va joylashuvi",
        "title_ru": "Размер и выравнивание текста",
        "points_reward": 20,
        "text_content": (
            "<h2>Matnni kattalashtirish</h2>"
            "<p><code>font-size</code> matn o'lchamini beradi (piksel bilan):</p>"
            "<pre><code>&lt;p style=\"font-size: 30px\"&gt;Katta matn&lt;/p&gt;</code></pre>"
            "<p>Son qancha katta bo'lsa, harflar shuncha katta.</p>"
            "<h2>Matnni markazga qo'yish</h2>"
            "<p><code>text-align: center</code> matnni o'rtaga qo'yadi:</p>"
            "<pre><code>&lt;h1 style=\"text-align: center\"&gt;O'rtada&lt;/h1&gt;</code></pre>"
            "<p><code>left</code> — chapga, <code>right</code> — o'ngga, "
            "<code>center</code> — o'rtaga.</p>"
        ),
        "text_content_ru": (
            "<h2>Увеличиваем текст</h2>"
            "<p><code>font-size</code> задаёт размер текста (в пикселях):</p>"
            "<pre><code>&lt;p style=\"font-size: 30px\"&gt;Katta matn&lt;/p&gt;</code></pre>"
            "<p>Чем больше число, тем больше буквы.</p>"
            "<h2>Ставим текст по центру</h2>"
            "<p><code>text-align: center</code> ставит текст по центру:</p>"
            "<pre><code>&lt;h1 style=\"text-align: center\"&gt;O'rtada&lt;/h1&gt;</code></pre>"
            "<p><code>left</code> — влево, <code>right</code> — вправо, "
            "<code>center</code> — по центру.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Katta markazlashgan sarlavha",
            "description": "Katta o'lchamli, o'rtaga qo'yilgan sarlavha.",
            "sample_type": "web",
            "html_code": (
                "<h1 style=\"font-size: 40px; text-align: center; color: purple\">Salom!</h1>\n"
                "<p style=\"text-align: center\">Bu matn o'rtada turibdi.</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Matn o'lchami",
                "title_ru": "Размер текста",
                "description": "Matn o'lchamini o'zgartiradigan so'z qaysi?",
                "description_ru": "Какое слово меняет размер текста?",
                "exercise_type": "multiple_choice",
                "options": ["font-size", "color", "border", "text-align"],
                "options_ru": ["font-size", "color", "border", "text-align"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"font\" — shrift, \"size\" — o'lcham.",
                "hint_ru": "\"font\" — шрифт, \"size\" — размер.",
                "explanation": "font-size matnning o'lchamini piksel bilan beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "O'rtaga qo'yish",
                "title_ru": "Поставить по центру",
                "description": "Matnni o'rtaga qo'yish uchun qaysi qiymat kerak?",
                "description_ru": "Какое значение ставит текст по центру?",
                "exercise_type": "multiple_choice",
                "options": ["text-align: center", "text-align: left", "color: center", "font-size: center"],
                "options_ru": ["text-align: center", "text-align: left", "color: center", "font-size: center"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"center\" — markaz.",
                "hint_ru": "\"center\" — центр.",
                "explanation": "text-align: center matnni o'rtaga joylashtiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Katta harflar",
                "title_ru": "Большие буквы",
                "description": "Matnni 30 piksel qilish uchun to'ldiring: 'font-size: ___'",
                "description_ru": "Заполни, чтобы текст был 30 пикселей: 'font-size: ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "30px",
                "correct_answers_ru": "30px",
                "hint": "Son va \"px\" (piksel).",
                "hint_ru": "Число и \"px\" (пиксели).",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Bezakli matnni tuzing",
                "title_ru": "Собери оформленный текст",
                "description": "Bloklarni tartibga qo'ying: katta va o'rtaga qo'yilgan sarlavha.",
                "description_ru": "Расставь блоки: большой и центрированный заголовок.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<h1 style=\"font-size: 40px; text-align: center\">", "Salom", "</h1>"],
                "drag_items_ru": ["<h1 style=\"font-size: 40px; text-align: center\">", "Salom", "</h1>"],
                "correct_order": ["<h1 style=\"font-size: 40px; text-align: center\">", "Salom", "</h1>"],
                "hint": "Bezaklar ochuvchi teg ichida, nuqta-vergul bilan.",
                "hint_ru": "Свойства внутри открывающего тега, через точку с запятой.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Katta chiroyli sarlavha",
            "task_title_ru": "Проект: большой красивый заголовок",
            "task_description": (
                "Ismingizni katta (font-size) va o'rtaga qo'yilgan (text-align) "
                "sarlavha qilib yozing, ostiga bitta matn qo'shing. index.html ni "
                "ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши своё имя большим (font-size) и центрированным "
                "(text-align) заголовком, добавь ниже один абзац. Отправь "
                "index.html в ZIP."
            ),
            "task_requirements": (
                "• Sarlavhaga font-size berilgan bo'lsin (kamida 30px)\n"
                "• Sarlavha text-align: center bilan o'rtada bo'lsin\n"
                "• Ostida bitta <p> matn bo'lsin"
            ),
            "task_requirements_ru": (
                "• Заголовку задан font-size (хотя бы 30px)\n"
                "• Заголовок по центру через text-align: center\n"
                "• Ниже один абзац <p>"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Chegara (border)",
        "title_ru": "Рамка (border)",
        "points_reward": 20,
        "text_content": (
            "<h2>Atrofga chegara chizamiz</h2>"
            "<p><code>border</code> element atrofiga chiziq (ramka) chizadi. "
            "Uch narsani beramiz: qalinlik, turi va rangi.</p>"
            "<pre><code>&lt;p style=\"border: 3px solid red\"&gt;Ramkali matn&lt;/p&gt;</code></pre>"
            "<ul>"
            "<li><code>3px</code> — chiziq qalinligi.</li>"
            "<li><code>solid</code> — to'liq chiziq (uzluksiz).</li>"
            "<li><code>red</code> — chiziq rangi.</li>"
            "</ul>"
            "<p>Shunday qilib matn atrofida chiroyli qizil ramka paydo bo'ladi.</p>"
        ),
        "text_content_ru": (
            "<h2>Рисуем рамку вокруг</h2>"
            "<p><code>border</code> рисует линию (рамку) вокруг элемента. "
            "Задаём три вещи: толщину, тип и цвет.</p>"
            "<pre><code>&lt;p style=\"border: 3px solid red\"&gt;Ramkali matn&lt;/p&gt;</code></pre>"
            "<ul>"
            "<li><code>3px</code> — толщина линии.</li>"
            "<li><code>solid</code> — сплошная линия.</li>"
            "<li><code>red</code> — цвет линии.</li>"
            "</ul>"
            "<p>Так вокруг текста появляется красивая красная рамка.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Ramkali quti",
            "description": "Ko'k chegarali va sariq fonli matn qutisi.",
            "sample_type": "web",
            "html_code": (
                "<p style=\"border: 4px solid blue; background-color: yellow\">Men ramka ichidaman!</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Chegara so'zi",
                "title_ru": "Слово рамки",
                "description": "Element atrofiga chiziq chizadigan so'z qaysi?",
                "description_ru": "Какое слово рисует линию вокруг элемента?",
                "exercise_type": "multiple_choice",
                "options": ["border", "color", "font-size", "text-align"],
                "options_ru": ["border", "color", "font-size", "text-align"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"border\" — chegara, ramka.",
                "hint_ru": "\"border\" — граница, рамка.",
                "explanation": "border element atrofiga ramka chizadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "To'liq chiziq",
                "title_ru": "Сплошная линия",
                "description": "Uzluksiz to'liq chiziq turi qanday yoziladi?",
                "description_ru": "Как пишется тип сплошной линии?",
                "exercise_type": "multiple_choice",
                "options": ["solid", "center", "red", "px"],
                "options_ru": ["solid", "center", "red", "px"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"solid\" — qattiq, to'liq.",
                "hint_ru": "\"solid\" — сплошной.",
                "explanation": "solid — uzluksiz to'liq chiziq turi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Chegara qalinligi",
                "title_ru": "Толщина рамки",
                "description": "Chegarani belgilaydigan so'zni yozing: '___: 3px solid red'",
                "description_ru": "Напиши слово, задающее рамку: '___: 3px solid red'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "border",
                "correct_answers_ru": "border",
                "hint": "Atrofdagi chiziq nomi.",
                "hint_ru": "Название линии вокруг.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Ramkali qutini tuzing",
                "title_ru": "Собери рамочный блок",
                "description": "Bloklarni tartibga qo'ying: qizil ramkali matn.",
                "description_ru": "Расставь блоки: текст с красной рамкой.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<p style=\"border: 3px solid red\">", "Salom", "</p>"],
                "drag_items_ru": ["<p style=\"border: 3px solid red\">", "Salom", "</p>"],
                "correct_order": ["<p style=\"border: 3px solid red\">", "Salom", "</p>"],
                "hint": "Bezak ochuvchi teg ichida.",
                "hint_ru": "Свойство внутри открывающего тега.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Ramkali quti",
            "task_title_ru": "Проект: блок с рамкой",
            "task_description": (
                "Bitta matnni chegara (border) va fon rangi bilan chiroyli qutiga "
                "aylantiring. index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Преврати один абзац в красивый блок с рамкой (border) и цветом "
                "фона. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Matnga border berilgan bo'lsin (qalinlik, solid, rang)\n"
                "• Qutiga background-color berilsin\n"
                "• Chegara rangi ko'rinib tursin"
            ),
            "task_requirements_ru": (
                "• Абзацу задан border (толщина, solid, цвет)\n"
                "• Блоку задан background-color\n"
                "• Цвет рамки хорошо виден"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Bo'shliq va yumaloq burchak",
        "title_ru": "Отступы и скруглённые углы",
        "points_reward": 20,
        "text_content": (
            "<h2>Ichki bo'shliq (padding)</h2>"
            "<p>Ba'zan matn chegaraga juda yopishib qoladi. <code>padding</code> "
            "chegara bilan matn orasiga <b>ichki bo'shliq</b> qo'shadi:</p>"
            "<pre><code>&lt;p style=\"border: 2px solid black; padding: 20px\"&gt;Matn&lt;/p&gt;</code></pre>"
            "<h2>Yumaloq burchaklar</h2>"
            "<p><code>border-radius</code> qutining burchaklarini <b>yumaloq</b> "
            "qiladi:</p>"
            "<pre><code>&lt;p style=\"border: 2px solid black; border-radius: 15px\"&gt;Yumaloq quti&lt;/p&gt;</code></pre>"
            "<p>Son qancha katta bo'lsa, burchaklar shuncha yumaloq bo'ladi.</p>"
        ),
        "text_content_ru": (
            "<h2>Внутренний отступ (padding)</h2>"
            "<p>Иногда текст сильно прижат к рамке. <code>padding</code> "
            "добавляет <b>внутренний отступ</b> между рамкой и текстом:</p>"
            "<pre><code>&lt;p style=\"border: 2px solid black; padding: 20px\"&gt;Matn&lt;/p&gt;</code></pre>"
            "<h2>Скруглённые углы</h2>"
            "<p><code>border-radius</code> делает углы блока <b>круглыми</b>:</p>"
            "<pre><code>&lt;p style=\"border: 2px solid black; border-radius: 15px\"&gt;Yumaloq quti&lt;/p&gt;</code></pre>"
            "<p>Чем больше число, тем круглее углы.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Yumshoq quti",
            "description": "Ichki bo'shliqli va yumaloq burchakli chiroyli quti.",
            "sample_type": "web",
            "html_code": (
                "<p style=\"border: 2px solid green; padding: 20px; border-radius: 15px; background-color: #eaffea\">Men chiroyli qutidaman!</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Ichki bo'shliq",
                "title_ru": "Внутренний отступ",
                "description": "Chegara bilan matn orasiga bo'shliq qo'shadigan so'z qaysi?",
                "description_ru": "Какое слово добавляет отступ между рамкой и текстом?",
                "exercise_type": "multiple_choice",
                "options": ["padding", "color", "border", "font-size"],
                "options_ru": ["padding", "color", "border", "font-size"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"padding\" — ichki yumshoq bo'shliq.",
                "hint_ru": "\"padding\" — внутренний отступ.",
                "explanation": "padding chegara bilan matn orasiga ichki bo'shliq qo'shadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yumaloq burchak",
                "title_ru": "Круглый угол",
                "description": "Qutining burchaklarini yumaloq qiladigan so'z qaysi?",
                "description_ru": "Какое слово делает углы блока круглыми?",
                "exercise_type": "multiple_choice",
                "options": ["border-radius", "text-align", "font-size", "color"],
                "options_ru": ["border-radius", "text-align", "font-size", "color"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"radius\" — aylana radiusi.",
                "hint_ru": "\"radius\" — радиус окружности.",
                "explanation": "border-radius burchaklarni yumaloq qiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bo'shliq qo'shish",
                "title_ru": "Добавить отступ",
                "description": "Ichki bo'shliq beradigan so'zni yozing: '___: 20px'",
                "description_ru": "Напиши слово внутреннего отступа: '___: 20px'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "padding",
                "correct_answers_ru": "padding",
                "hint": "Ichki yumshoq bo'shliq nomi.",
                "hint_ru": "Название внутреннего отступа.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Yumshoq qutini tuzing",
                "title_ru": "Собери мягкий блок",
                "description": "Bloklarni tartibga qo'ying: bo'shliqli, yumaloq burchakli quti.",
                "description_ru": "Расставь блоки: блок с отступом и круглыми углами.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<p style=\"padding: 20px; border-radius: 15px\">", "Salom", "</p>"],
                "drag_items_ru": ["<p style=\"padding: 20px; border-radius: 15px\">", "Salom", "</p>"],
                "correct_order": ["<p style=\"padding: 20px; border-radius: 15px\">", "Salom", "</p>"],
                "hint": "Bezaklar ochuvchi teg ichida.",
                "hint_ru": "Свойства внутри открывающего тега.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Chiroyli yumshoq quti",
            "task_title_ru": "Проект: красивый мягкий блок",
            "task_description": (
                "O'zingiz haqingizdagi matnni chegara, ichki bo'shliq (padding) "
                "va yumaloq burchakli (border-radius) chiroyli qutiga aylantiring. "
                "index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Преврати абзац о себе в красивый блок с рамкой, внутренним "
                "отступом (padding) и круглыми углами (border-radius). Отправь "
                "index.html в ZIP."
            ),
            "task_requirements": (
                "• Qutiga border berilgan bo'lsin\n"
                "• padding bilan ichki bo'shliq berilsin\n"
                "• border-radius bilan burchaklar yumaloq bo'lsin"
            ),
            "task_requirements_ru": (
                "• Блоку задан border\n"
                "• Задан внутренний отступ через padding\n"
                "• Углы скруглены через border-radius"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Style bloki va klass",
        "title_ru": "Блок <style> и класс",
        "points_reward": 20,
        "text_content": (
            "<h2>Bezakni alohida yozamiz</h2>"
            "<p>Har bir tegga <code>style</code> yozish uzun bo'ladi. Buning "
            "o'rniga sahifaning yuqorisida <code>&lt;style&gt;</code> bloki "
            "yasab, hamma bezakni bir joyda yozamiz.</p>"
            "<pre><code>&lt;style&gt;\n"
            "  p { color: blue; font-size: 20px; }\n"
            "&lt;/style&gt;</code></pre>"
            "<p>Bu <b>barcha</b> <code>&lt;p&gt;</code> larni ko'k va 20px "
            "qiladi! <code>p</code> — bu <b>selektor</b> (kimni bezashni "
            "ko'rsatadi), <code>{ }</code> ichida esa bezaklar.</p>"
            "<h2>Klass — o'zimizning nom</h2>"
            "<p>Faqat ba'zi elementlarni bezash uchun ularga <b>klass</b> nom "
            "beramiz:</p>"
            "<pre><code>&lt;style&gt;\n"
            "  .quti { border: 2px solid red; padding: 10px; }\n"
            "&lt;/style&gt;\n"
            "&lt;p class=\"quti\"&gt;Men klassdaman&lt;/p&gt;</code></pre>"
            "<p>CSSda klass oldiga <b>nuqta</b> (<code>.</code>) qo'yiladi.</p>"
        ),
        "text_content_ru": (
            "<h2>Пишем оформление отдельно</h2>"
            "<p>Писать <code>style</code> у каждого тега — долго. Вместо этого "
            "вверху страницы создаём блок <code>&lt;style&gt;</code> и пишем всё "
            "оформление в одном месте.</p>"
            "<pre><code>&lt;style&gt;\n"
            "  p { color: blue; font-size: 20px; }\n"
            "&lt;/style&gt;</code></pre>"
            "<p>Это делает <b>все</b> <code>&lt;p&gt;</code> синими и 20px! "
            "<code>p</code> — это <b>селектор</b> (кого оформляем), а внутри "
            "<code>{ }</code> — свойства.</p>"
            "<h2>Класс — наше имя</h2>"
            "<p>Чтобы оформить только некоторые элементы, даём им <b>класс</b>:</p>"
            "<pre><code>&lt;style&gt;\n"
            "  .quti { border: 2px solid red; padding: 10px; }\n"
            "&lt;/style&gt;\n"
            "&lt;p class=\"quti\"&gt;Men klassdaman&lt;/p&gt;</code></pre>"
            "<p>В CSS перед классом ставится <b>точка</b> (<code>.</code>).</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Style bloki bilan bezash",
            "description": "Barcha sarlavhalar bir xil bezaladi, klass bilan quti yasaladi.",
            "sample_type": "web",
            "html_code": (
                "<h1>Birinchi sarlavha</h1>\n"
                "<p class=\"quti\">Men chiroyli qutidaman.</p>\n"
                "<p>Oddiy matn.</p>\n"
            ),
            "css_code": (
                "h1 { color: purple; text-align: center; }\n"
                ".quti { border: 3px solid orange; padding: 15px; border-radius: 12px; }\n"
            ),
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Bezakni bir joyda",
                "title_ru": "Оформление в одном месте",
                "description": "Barcha bezakni bir joyda yozish uchun qaysi teg ishlatiladi?",
                "description_ru": "Каким тегом пишут всё оформление в одном месте?",
                "exercise_type": "multiple_choice",
                "options": ["<style>", "<border>", "<color>", "<h1>"],
                "options_ru": ["<style>", "<border>", "<color>", "<h1>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"style\" — bezak.",
                "hint_ru": "\"style\" — стиль, оформление.",
                "explanation": "<style> bloki ichida barcha CSS bezaklarini yozamiz.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Klass belgisi",
                "title_ru": "Символ класса",
                "description": "CSSda klass nomi oldiga qaysi belgi qo'yiladi?",
                "description_ru": "Какой символ ставится перед именем класса в CSS?",
                "exercise_type": "multiple_choice",
                "options": [". (nuqta)", "# (panjara)", "@ (kuchukcha)", "* (yulduzcha)"],
                "options_ru": [". (точка)", "# (решётка)", "@ (собачка)", "* (звёздочка)"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Kichkina nuqta.",
                "hint_ru": "Маленькая точка.",
                "explanation": "CSSda klass oldiga nuqta (.) qo'yiladi: .quti { ... }.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bezaklar qayerda?",
                "title_ru": "Где свойства?",
                "description": "Selektordan keyin bezaklar qaysi qavslar ichiga yoziladi? Bo'sh joyni to'ldiring: 'p ___ color: blue }'",
                "description_ru": "В какие скобки пишут свойства после селектора? Заполни пропуск: 'p ___ color: blue }'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "{",
                "correct_answers_ru": "{",
                "hint": "Jingalak (figurali) qavs ochiladi.",
                "hint_ru": "Открывается фигурная скобка.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "CSS qoidasini tuzing",
                "title_ru": "Собери правило CSS",
                "description": "Bloklarni tartibga qo'ying: barcha p larni ko'k qiladigan qoida.",
                "description_ru": "Расставь блоки: правило, делающее все p синими.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["p", "{", "color: blue;", "}"],
                "drag_items_ru": ["p", "{", "color: blue;", "}"],
                "correct_order": ["p", "{", "color: blue;", "}"],
                "hint": "Selektor, ochuvchi qavs, bezak, yopuvchi qavs.",
                "hint_ru": "Селектор, открывающая скобка, свойство, закрывающая скобка.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Style bloki bilan sahifa",
            "task_title_ru": "Проект: страница с блоком <style>",
            "task_description": (
                "Sahifa yuqorisiga <style> bloki qo'ying va u orqali barcha "
                "sarlavhalarni bir xil rangga bo'yang. Bitta matnga klass berib, "
                "uni qutiga aylantiring. index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Добавь вверху страницы блок <style> и через него покрась все "
                "заголовки в один цвет. Дай одному абзацу класс и преврати его в "
                "блок. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• <style> bloki ishlatilsin\n"
                "• Selektor bilan sarlavha(lar) bezalsin\n"
                "• Kamida bitta klass (.nom) yaratilib, elementga qo'llanilsin"
            ),
            "task_requirements_ru": (
                "• Использован блок <style>\n"
                "• Заголовок(и) оформлены через селектор\n"
                "• Создан хотя бы один класс (.имя) и применён к элементу"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy loyiha: Chiroyli sahifa",
        "title_ru": "Итоговый проект: красивая страница",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi CSSda o'rgangan hamma narsani birlashtirib, o'zimiz "
            "haqimizdagi <b>eng chiroyli sahifa</b>ni yasaymiz: ranglar, katta "
            "markazlashgan sarlavha, ramkali va yumaloq burchakli qutilar, "
            "ichki bo'shliqlar.</p>"
            "<h3>Chiroyli sahifa qismlari</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Rangli, markazlashgan sarlavha\"] --> B[\"Ramkali quti (border)\"]\n"
            "  B --> C[\"Ichki bo'shliq (padding)\"]\n"
            "  C --> D[\"Yumaloq burchaklar (border-radius)\"]\n"
            "</pre>"
            "<p>Har bir bezak sahifangizni yanada go'zal qiladi. O'z rangingiz va "
            "o'lchamlaringizni tanlang — bu sizning sahifangiz!</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим всё, что выучили в CSS, и сделаем <b>самую "
            "красивую страницу</b> о себе: цвета, большой центрированный "
            "заголовок, блоки с рамкой и круглыми углами, внутренние отступы.</p>"
            "<h3>Части красивой страницы</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Rangli, markazlashgan sarlavha\"] --> B[\"Ramkali quti (border)\"]\n"
            "  B --> C[\"Ichki bo'shliq (padding)\"]\n"
            "  C --> D[\"Yumaloq burchaklar (border-radius)\"]\n"
            "</pre>"
            "<p>Каждое свойство делает твою страницу красивее. Выбери свои цвета "
            "и размеры — это твоя страница!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: To'liq bezatilgan sahifa",
            "description": "Rang, o'lcham, chegara, bo'shliq va yumaloq burchak — hammasi birga.",
            "sample_type": "web",
            "html_code": (
                "<h1>Men haqimda</h1>\n"
                "<p class=\"karta\">Menga rasm chizish va futbol yoqadi.</p>\n"
                "<p class=\"karta\">Sinfim: 3-A</p>\n"
            ),
            "css_code": (
                "h1 { color: white; background-color: #6C63FF; text-align: center; padding: 15px; border-radius: 10px; }\n"
                ".karta { border: 2px solid #6C63FF; padding: 15px; border-radius: 12px; font-size: 18px; }\n"
            ),
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Sahifani chiroyli qiladi",
                "title_ru": "Делает страницу красивой",
                "description": "Sahifani bezash uchun qaysi tilni ishlatamiz?",
                "description_ru": "Какой язык мы используем для оформления страницы?",
                "exercise_type": "multiple_choice",
                "options": ["CSS", "Scratch", "Python", "Word"],
                "options_ru": ["CSS", "Scratch", "Python", "Word"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Butun kurs shu haqida edi.",
                "hint_ru": "Весь курс был про это.",
                "explanation": "CSS — HTML sahifasini bezaydigan til.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yumaloq quti retsepti",
                "title_ru": "Рецепт мягкого блока",
                "description": "Chiroyli yumshoq quti uchun odatda qaysi uchta bezak birga ishlatiladi?",
                "description_ru": "Какие три свойства обычно используют вместе для красивого блока?",
                "exercise_type": "multiple_choice",
                "options": [
                    "border, padding, border-radius",
                    "color, Scratch, blok",
                    "font-size, ovoz, rasm",
                    "src, href, alt",
                ],
                "options_ru": [
                    "border, padding, border-radius",
                    "color, Scratch, блок",
                    "font-size, звук, картинка",
                    "src, href, alt",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Chegara, ichki bo'shliq, yumaloq burchak.",
                "hint_ru": "Рамка, внутренний отступ, круглые углы.",
                "explanation": "border + padding + border-radius chiroyli yumshoq quti yasaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sarlavhani markazga",
                "title_ru": "Заголовок по центру",
                "description": "Sarlavhani o'rtaga qo'yish uchun to'ldiring: 'text-align: ___'",
                "description_ru": "Заполни, чтобы поставить заголовок по центру: 'text-align: ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "center",
                "correct_answers_ru": "center",
                "hint": "Markaz — inglizcha \"center\".",
                "hint_ru": "Центр — по-английски \"center\".",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Chiroyli karta qoidasini tuzing",
                "title_ru": "Собери правило красивой карточки",
                "description": "Bloklarni tartibga qo'ying: .karta klassi uchun CSS qoidasi.",
                "description_ru": "Расставь блоки: правило CSS для класса .karta.",
                "exercise_type": "drag_and_drop",
                "drag_items": [".karta", "{", "border: 2px solid blue; padding: 15px;", "}"],
                "drag_items_ru": [".karta", "{", "border: 2px solid blue; padding: 15px;", "}"],
                "correct_order": [".karta", "{", "border: 2px solid blue; padding: 15px;", "}"],
                "hint": "Klass (nuqta bilan), qavs ochiladi, bezaklar, qavs yopiladi.",
                "hint_ru": "Класс (с точкой), скобка открывается, свойства, скобка закрывается.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Chiroyli \"Men haqimda\" sahifa",
            "task_title_ru": "Итоговый проект: красивая страница \"Обо мне\"",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: o'zingiz haqingizda "
                "to'liq bezatilgan chiroyli sahifa yasang — ranglar, katta "
                "markazlashgan sarlavha, ramkali va yumaloq burchakli qutilar. "
                "index.html ni ZIP qilib topshiring — bu sizning eng chiroyli "
                "loyihangiz!"
            ),
            "task_description_ru": (
                "Объедини всё, что выучил: сделай полностью оформленную красивую "
                "страницу о себе — цвета, большой центрированный заголовок, блоки "
                "с рамкой и круглыми углами. Отправь index.html в ZIP — это твой "
                "самый красивый проект!"
            ),
            "task_requirements": (
                "• Rangli va markazlashgan (text-align: center) sarlavha\n"
                "• Kamida bitta ramkali (border) quti\n"
                "• padding va border-radius ishlatilsin\n"
                "• Kamida ikki xil rang ishlatilsin"
            ),
            "task_requirements_ru": (
                "• Цветной и центрированный (text-align: center) заголовок\n"
                "• Хотя бы один блок с рамкой (border)\n"
                "• Использованы padding и border-radius\n"
                "• Использованы хотя бы два разных цвета"
            ),
            "task_technologies": "HTML, CSS",
            "task_deadline_days": 5,
        },
    },
]
