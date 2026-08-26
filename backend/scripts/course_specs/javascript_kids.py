"""JavaScript course for children aged 7-12 (Uzbek-primary, Russian translations).

Sequel to course 150 (CSS bilan sahifani bezash), completing the kids' web
track: HTML (148, skeleton) -> CSS (150, beauty) -> JavaScript (this course,
action). Teaches: onclick + alert(), finding/changing an element by id
(getElementById + innerText), controlling CSS from JS (.style), variables +
functions (a click counter), if/else, then a final project combining all of
it. Runs entirely in the browser, so every `sample` uses sample_type "web"
(html_code + css_code + js_code) so the child sees it actually work, and
every `task` asks the child to build a page and submit their index.html for
review.

Every code example deliberately avoids the Uzbek apostrophe letter (') inside
any single-quoted JS string literal (e.g. alert('...')) — that character
would prematurely close the JS string and break real code a child copies.
Apostrophes are fine anywhere in plain HTML text (headings, prose, button
labels) since those aren't JS string literals.

Published 2026-08-26 (user directive, after the review window).
"""

COURSE = {
    "title": "JavaScript bilan interaktivlik (bolalar uchun)",
    "title_ru": "Интерактивность с JavaScript (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun JavaScript bilan sahifani \"jonlantirish\" "
        "kursi. Tugma bosilganda xabar chiqarishni, matn va rangni "
        "o'zgartirishni, hisoblagich yasashni va shartlarni tekshirishni "
        "o'rganamiz hamda o'zimizning interaktiv sahifamizni yaratamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: «оживляем» страницу с помощью JavaScript. "
        "Научимся показывать сообщение по нажатию кнопки, менять текст и "
        "цвет, делать счётчик и проверять условия, а также создадим свою "
        "интерактивную страницу."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": 150,
    "display_order": 0,
    "is_active": True,
    "is_published": True,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "JavaScript nima? Tugma bosganda xabar",
        "title_ru": "Что такое JavaScript? Сообщение по клику",
        "points_reward": 15,
        "text_content": (
            "<h2>JavaScript nima?</h2>"
            "<p>HTML sahifani <b>yasaydi</b>, CSS uni <b>chiroyli</b> qiladi, "
            "<b>JavaScript</b> esa uni <b>jonlantiradi</b> — tugma bosilganda "
            "yoki sichqoncha yaqinlashganda nimadir sodir bo'lishini "
            "ta'minlaydi.</p>"
            "<h2>Bosilganda xabar chiqarish</h2>"
            "<p>Tugmaga <code>onclick</code> qo'shib, ichiga <code>alert(...)</code> "
            "yozsak, bosilganda ekranga xabar chiqadi:</p>"
            "<pre><code>&lt;button onclick=\"alert('Salom!')\"&gt;Bos meni&lt;/button&gt;</code></pre>"
            "<p><code>alert</code> — ingliz tilida \"ogohlantirish\". Qavs "
            "ichidagi matn (tirnoq orasida) ekranga chiqadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Что такое JavaScript?</h2>"
            "<p>HTML <b>создаёт</b> страницу, CSS делает её <b>красивой</b>, а "
            "<b>JavaScript</b> её <b>оживляет</b> — заставляет что-то "
            "происходить при нажатии кнопки или наведении мыши.</p>"
            "<h2>Показываем сообщение по клику</h2>"
            "<p>Добавив кнопке <code>onclick</code> и написав внутри "
            "<code>alert(...)</code>, при нажатии на экране появится "
            "сообщение:</p>"
            "<pre><code>&lt;button onclick=\"alert('Salom!')\"&gt;Bos meni&lt;/button&gt;</code></pre>"
            "<p><code>alert</code> — по-английски «предупреждение». Текст в "
            "кавычках внутри скобок появляется на экране.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Salomlashuvchi tugma",
            "description": "Bosilganda xabar chiqaradigan tugma.",
            "sample_type": "web",
            "html_code": (
                "<button onclick=\"alert('Salom!')\">Bos meni</button>\n"
                "<p>Tugmani bosib ko'ring!</p>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "JavaScript nima qiladi?",
                "title_ru": "Что делает JavaScript?",
                "description": "JavaScript sahifaga nima qo'shadi?",
                "description_ru": "Что JavaScript добавляет странице?",
                "exercise_type": "multiple_choice",
                "options": ["Harakat va jonlanish", "Faqat rang", "Faqat matn", "Faqat rasm"],
                "options_ru": ["Действие и оживление", "Только цвет", "Только текст", "Только картинку"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "U sahifani \"jonlantiradi\".",
                "hint_ru": "Он «оживляет» страницу.",
                "explanation": "JavaScript sahifani harakatchan va interaktiv qiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Xabar chiqarish",
                "title_ru": "Показать сообщение",
                "description": "Ekranga xabar chiqaradigan buyruq qaysi?",
                "description_ru": "Какая команда показывает сообщение на экране?",
                "exercise_type": "multiple_choice",
                "options": ["alert", "color", "border", "font-size"],
                "options_ru": ["alert", "color", "border", "font-size"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"alert\" — ogohlantirish, xabar.",
                "hint_ru": "\"alert\" — предупреждение, сообщение.",
                "explanation": "alert(...) qavs ichidagi matnni ekranga chiqaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bosish atributi",
                "title_ru": "Атрибут нажатия",
                "description": "Tugma bosilganda ishlaydigan atributni yozing: '<button ___=\"alert(...)\">'",
                "description_ru": "Напиши атрибут, который срабатывает при нажатии: '<button ___=\"alert(...)\">'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "onclick",
                "correct_answers_ru": "onclick",
                "hint": "\"on\" + \"click\" (bosish).",
                "hint_ru": "\"on\" + \"click\" (нажатие).",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Salomlashuvchi tugmani tuzing",
                "title_ru": "Собери приветственную кнопку",
                "description": "Bloklarni tartibga qo'ying: bosilganda \"Salom!\" deb xabar chiqaradigan tugma.",
                "description_ru": "Расставь блоки: кнопка, показывающая сообщение «Salom!» по нажатию.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["<button onclick=\"alert('Salom!')\">", "Bos meni", "</button>"],
                "drag_items_ru": ["<button onclick=\"alert('Salom!')\">", "Bos meni", "</button>"],
                "correct_order": ["<button onclick=\"alert('Salom!')\">", "Bos meni", "</button>"],
                "hint": "Ochuvchi teg (onclick bilan), matn, yopuvchi teg.",
                "hint_ru": "Открывающий тег (с onclick), текст, закрывающий тег.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Salomlashuvchi tugma",
            "task_title_ru": "Проект: приветственная кнопка",
            "task_description": (
                "Bosilganda ismingiz bilan salomlashuvchi tugma yasang. "
                "index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай кнопку, которая при нажатии здоровается с твоим "
                "именем. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Kamida bitta <button> bo'lsin\n"
                "• onclick bilan alert() chaqirilsin\n"
                "• Xabarda ismingiz yozilgan bo'lsin"
            ),
            "task_requirements_ru": (
                "• Хотя бы одна кнопка <button>\n"
                "• onclick вызывает alert()\n"
                "• В сообщении написано твоё имя"
            ),
            "task_technologies": "HTML, JavaScript",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Matnni o'zgartiramiz",
        "title_ru": "Меняем текст",
        "points_reward": 20,
        "text_content": (
            "<h2>Elementni topamiz</h2>"
            "<p>Sahifadagi biror narsani o'zgartirish uchun, avval unga "
            "<b>nom (id)</b> beramiz:</p>"
            "<pre><code>&lt;p id=\"salom\"&gt;Salom!&lt;/p&gt;</code></pre>"
            "<p>Keyin JavaScript'da <code>document.getElementById('salom')</code> "
            "orqali topamiz.</p>"
            "<h2>Matnni o'zgartirish</h2>"
            "<p><code>.innerText</code> — element ichidagi matn. Unga yangi "
            "qiymat bersak, matn o'zgaradi:</p>"
            "<pre><code>&lt;button onclick=\"document.getElementById('salom').innerText = 'Ajoyib!'\"&gt;Bos&lt;/button&gt;</code></pre>"
            "<p>Tugma bosilganda, id=\"salom\" li matn \"Ajoyib!\" ga aylanadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Находим элемент</h2>"
            "<p>Чтобы изменить что-то на странице, сначала даём ему <b>имя "
            "(id)</b>:</p>"
            "<pre><code>&lt;p id=\"salom\"&gt;Salom!&lt;/p&gt;</code></pre>"
            "<p>Затем находим его в JavaScript через "
            "<code>document.getElementById('salom')</code>.</p>"
            "<h2>Меняем текст</h2>"
            "<p><code>.innerText</code> — текст внутри элемента. Если задать "
            "новое значение, текст изменится:</p>"
            "<pre><code>&lt;button onclick=\"document.getElementById('salom').innerText = 'Ajoyib!'\"&gt;Bos&lt;/button&gt;</code></pre>"
            "<p>При нажатии кнопки текст с id=\"salom\" станет «Ajoyib!».</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: O'zgaruvchi matn",
            "description": "Bosilganda matni o'zgaradigan sahifa.",
            "sample_type": "web",
            "html_code": (
                "<p id=\"xabar\">Bu boshlang'ich matn.</p>\n"
                "<button onclick=\"document.getElementById('xabar').innerText = 'Ajoyib!'\">O'zgartir</button>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "Elementni topish",
                "title_ru": "Найти элемент",
                "description": "Elementni JavaScript orqali topish uchun unga nima kerak?",
                "description_ru": "Что нужно элементу, чтобы найти его через JavaScript?",
                "exercise_type": "multiple_choice",
                "options": ["id", "rang", "shrift", "rasm"],
                "options_ru": ["id", "цвет", "шрифт", "картинка"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "getElementById — \"id bo'yicha element topish\".",
                "hint_ru": "getElementById — «найти элемент по id».",
                "explanation": "Har bir element o'zining id nomi orqali topiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Matnni o'zgartirish",
                "title_ru": "Изменение текста",
                "description": "Element ichidagi matnni o'zgartiradigan buyruq qaysi?",
                "description_ru": "Какая команда меняет текст внутри элемента?",
                "exercise_type": "multiple_choice",
                "options": [".innerText", ".border", ".fontSize", ".alert"],
                "options_ru": [".innerText", ".border", ".fontSize", ".alert"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"inner\" — ichki, \"text\" — matn.",
                "hint_ru": "\"inner\" — внутренний, \"text\" — текст.",
                "explanation": ".innerText element ichidagi matnni o'qiydi va o'zgartiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Element topish buyrug'i",
                "title_ru": "Команда поиска элемента",
                "description": "Elementni topish uchun ishlatiladigan buyruqni to'ldiring: 'document.___(\"xabar\")'",
                "description_ru": "Заполни команду поиска элемента: 'document.___(\"xabar\")'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "getElementById",
                "correct_answers_ru": "getElementById",
                "hint": "\"get\" + \"Element\" + \"By\" + \"Id\".",
                "hint_ru": "\"get\" + \"Element\" + \"By\" + \"Id\".",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Matn o'zgartirish buyrug'ini tuzing",
                "title_ru": "Собери команду изменения текста",
                "description": "Bloklarni tartibga qo'ying: 'xabar' matnini \"Ajoyib!\" ga o'zgartiruvchi buyruq.",
                "description_ru": "Расставь блоки: команда, меняющая текст 'xabar' на «Ajoyib!».",
                "exercise_type": "drag_and_drop",
                "drag_items": ["document.getElementById('xabar')", ".innerText", " = 'Ajoyib!'"],
                "drag_items_ru": ["document.getElementById('xabar')", ".innerText", " = 'Ajoyib!'"],
                "correct_order": ["document.getElementById('xabar')", ".innerText", " = 'Ajoyib!'"],
                "hint": "Avval elementni topamiz, keyin matn xususiyatini, keyin yangi qiymatni.",
                "hint_ru": "Сначала находим элемент, потом свойство текста, потом новое значение.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: O'zgaruvchi salomlashuv",
            "task_title_ru": "Проект: меняющееся приветствие",
            "task_description": (
                "Bosilganda matni o'zgaradigan sahifa yasang — masalan, "
                "\"Bosing\" degan matn tugma bosilgach ismingizga aylansin. "
                "index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай страницу, где текст меняется по нажатию — например, "
                "текст «Bosing» после нажатия становится твоим именем. Отправь "
                "index.html в ZIP."
            ),
            "task_requirements": (
                "• Matnli elementga id berilgan bo'lsin\n"
                "• Tugmada onclick bilan getElementById va innerText ishlatilsin\n"
                "• Matn tugma bosilgach o'zgarsin"
            ),
            "task_requirements_ru": (
                "• Текстовому элементу задан id\n"
                "• В onclick кнопки используются getElementById и innerText\n"
                "• Текст меняется после нажатия"
            ),
            "task_technologies": "HTML, JavaScript",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Rangni o'zgartiramiz",
        "title_ru": "Меняем цвет",
        "points_reward": 20,
        "text_content": (
            "<h2>CSS'ni JavaScript bilan boshqarish</h2>"
            "<p>CSS kursida <code>style</code> orqali rang berishni o'rgangan "
            "edik. JavaScript orqali ham xuddi shu bezaklarni <b>o'zgartirish</b> "
            "mumkin — <code>.style</code> so'zi bilan.</p>"
            "<pre><code>&lt;p id=\"quti\" style=\"color: black\"&gt;Salom!&lt;/p&gt;\n"
            "&lt;button onclick=\"document.getElementById('quti').style.color = 'red'\"&gt;Qizil qil&lt;/button&gt;</code></pre>"
            "<h2>Fon rangi</h2>"
            "<p>Fon rangini o'zgartirish uchun <code>.style.backgroundColor</code> "
            "ishlatamiz:</p>"
            "<pre><code>document.getElementById('quti').style.backgroundColor = 'yellow';</code></pre>"
        ),
        "text_content_ru": (
            "<h2>Управляем CSS через JavaScript</h2>"
            "<p>В курсе CSS мы учились задавать цвет через <code>style</code>. "
            "Через JavaScript можно так же <b>менять</b> эти свойства — словом "
            "<code>.style</code>.</p>"
            "<pre><code>&lt;p id=\"quti\" style=\"color: black\"&gt;Salom!&lt;/p&gt;\n"
            "&lt;button onclick=\"document.getElementById('quti').style.color = 'red'\"&gt;Qizil qil&lt;/button&gt;</code></pre>"
            "<h2>Цвет фона</h2>"
            "<p>Чтобы изменить цвет фона, используем "
            "<code>.style.backgroundColor</code>:</p>"
            "<pre><code>document.getElementById('quti').style.backgroundColor = 'yellow';</code></pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Rang almashtiruvchi tugmalar",
            "description": "Har bir tugma matn rangini o'zgartiradi.",
            "sample_type": "web",
            "html_code": (
                "<p id=\"quti\" style=\"font-size: 24px\">Rangli matn</p>\n"
                "<button onclick=\"document.getElementById('quti').style.color = 'red'\">Qizil</button>\n"
                "<button onclick=\"document.getElementById('quti').style.color = 'blue'\">Ko'k</button>\n"
            ),
            "css_code": None,
            "js_code": None,
        },
        "exercises": [
            {
                "title": "CSS'ni boshqarish",
                "title_ru": "Управление CSS",
                "description": "JavaScript orqali CSS bezagini o'zgartirish uchun qaysi so'z ishlatiladi?",
                "description_ru": "Какое слово используют, чтобы менять CSS-свойство через JavaScript?",
                "exercise_type": "multiple_choice",
                "options": [".style", ".innerText", "alert", "getElementById"],
                "options_ru": [".style", ".innerText", "alert", "getElementById"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "CSSdagi \"style\" so'zi bilan bir xil.",
                "hint_ru": "То же слово \"style\", что и в CSS.",
                "explanation": ".style orqali elementning CSS bezaklariga JavaScript'dan kirish mumkin.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Fon rangi buyrug'i",
                "title_ru": "Команда цвета фона",
                "description": "Fon rangini o'zgartiradigan buyruq qaysi?",
                "description_ru": "Какая команда меняет цвет фона?",
                "exercise_type": "multiple_choice",
                "options": [".style.backgroundColor", ".style.color", ".innerText", ".fontSize"],
                "options_ru": [".style.backgroundColor", ".style.color", ".innerText", ".fontSize"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"background\" — fon, \"color\" — rang.",
                "hint_ru": "\"background\" — фон, \"color\" — цвет.",
                "explanation": ".style.backgroundColor fon rangini, .style.color matn rangini o'zgartiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Matn rangi",
                "title_ru": "Цвет текста",
                "description": "Matn rangini qizil qilish uchun to'ldiring: '.style.___ = \"red\"'",
                "description_ru": "Заполни, чтобы сделать текст красным: '.style.___ = \"red\"'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "color",
                "correct_answers_ru": "color",
                "hint": "CSSdagi bilan bir xil so'z.",
                "hint_ru": "То же слово, что и в CSS.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Rang o'zgartirish buyrug'ini tuzing",
                "title_ru": "Собери команду смены цвета",
                "description": "Bloklarni tartibga qo'ying: 'quti' rangini ko'k qiladigan buyruq.",
                "description_ru": "Расставь блоки: команда, делающая 'quti' синим.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["document.getElementById('quti')", ".style.color", " = 'blue'"],
                "drag_items_ru": ["document.getElementById('quti')", ".style.color", " = 'blue'"],
                "correct_order": ["document.getElementById('quti')", ".style.color", " = 'blue'"],
                "hint": "Avval element, keyin bezak nomi, keyin yangi rang.",
                "hint_ru": "Сначала элемент, потом свойство, потом новый цвет.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Rang tanlagich",
            "task_title_ru": "Проект: выбор цвета",
            "task_description": (
                "Bosilganda matn yoki fon rangi o'zgaradigan kamida ikkita "
                "tugma yasang. index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай минимум две кнопки, меняющие цвет текста или фона по "
                "нажатию. Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Kamida ikkita rang tugmasi bo'lsin\n"
                "• Har biri .style.color yoki .style.backgroundColor ni o'zgartirsin\n"
                "• Matn boshida ko'rinadigan bo'lsin"
            ),
            "task_requirements_ru": (
                "• Хотя бы две кнопки цвета\n"
                "• Каждая меняет .style.color или .style.backgroundColor\n"
                "• Текст изначально виден"
            ),
            "task_technologies": "HTML, CSS, JavaScript",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Hisoblagich yasaymiz (o'zgaruvchi va funksiya)",
        "title_ru": "Делаем счётчик (переменная и функция)",
        "points_reward": 20,
        "text_content": (
            "<h2>Skript bloki</h2>"
            "<p>Bir nechta buyruqni birga yozish uchun, sahifaga "
            "<code>&lt;script&gt;</code> blok qo'shamiz — bu CSSdagi "
            "<code>&lt;style&gt;</code> kabi, faqat JavaScript uchun.</p>"
            "<h2>O'zgaruvchi — son saqlaydigan quti</h2>"
            "<p><code>let hisob = 0;</code> — <b>hisob</b> nomli quti yaratib, "
            "unga 0 son beramiz.</p>"
            "<h2>Funksiya — takrorlanadigan amal</h2>"
            "<p><b>Funksiya</b> — nomi bilan chaqiriladigan buyruqlar "
            "to'plami:</p>"
            "<pre><code>&lt;script&gt;\n"
            "  let hisob = 0;\n"
            "  function ortir() {\n"
            "    hisob = hisob + 1;\n"
            "    document.getElementById('son').innerText = hisob;\n"
            "  }\n"
            "&lt;/script&gt;\n"
            "&lt;p id=\"son\"&gt;0&lt;/p&gt;\n"
            "&lt;button onclick=\"ortir()\"&gt;+1&lt;/button&gt;</code></pre>"
            "<p>Tugma bosilganda <code>ortir()</code> funksiyasi ishlaydi: "
            "hisobga 1 qo'shadi va ekranga chiqaradi.</p>"
        ),
        "text_content_ru": (
            "<h2>Блок скрипта</h2>"
            "<p>Чтобы написать несколько команд вместе, добавляем на страницу "
            "блок <code>&lt;script&gt;</code> — это как <code>&lt;style&gt;</code> "
            "в CSS, но для JavaScript.</p>"
            "<h2>Переменная — коробка для числа</h2>"
            "<p><code>let hisob = 0;</code> — создаём коробку по имени "
            "<b>hisob</b> и кладём в неё 0.</p>"
            "<h2>Функция — повторяемое действие</h2>"
            "<p><b>Функция</b> — набор команд, который вызывается по имени:</p>"
            "<pre><code>&lt;script&gt;\n"
            "  let hisob = 0;\n"
            "  function ortir() {\n"
            "    hisob = hisob + 1;\n"
            "    document.getElementById('son').innerText = hisob;\n"
            "  }\n"
            "&lt;/script&gt;\n"
            "&lt;p id=\"son\"&gt;0&lt;/p&gt;\n"
            "&lt;button onclick=\"ortir()\"&gt;+1&lt;/button&gt;</code></pre>"
            "<p>При нажатии кнопки запускается функция <code>ortir()</code>: "
            "прибавляет 1 к счётчику и показывает его на экране.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Bosish hisoblagichi",
            "description": "Har bosishda 1 taga oshadigan hisoblagich.",
            "sample_type": "web",
            "html_code": (
                "<p id=\"son\">0</p>\n"
                "<button onclick=\"ortir()\">+1</button>\n"
            ),
            "css_code": None,
            "js_code": (
                "let hisob = 0;\n"
                "function ortir() {\n"
                "  hisob = hisob + 1;\n"
                "  document.getElementById('son').innerText = hisob;\n"
                "}\n"
            ),
        },
        "exercises": [
            {
                "title": "Skript bloki",
                "title_ru": "Блок скрипта",
                "description": "Bir nechta JavaScript buyruqni yozish uchun qaysi blok ishlatiladi?",
                "description_ru": "Какой блок используют, чтобы написать несколько команд JavaScript?",
                "exercise_type": "multiple_choice",
                "options": ["<script>", "<style>", "<button>", "<alert>"],
                "options_ru": ["<script>", "<style>", "<button>", "<alert>"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"script\" — yozuv, dastur.",
                "hint_ru": "\"script\" — сценарий, программа.",
                "explanation": "<script> bloki ichida JavaScript kodini yozamiz.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "O'zgaruvchi yaratish",
                "title_ru": "Создание переменной",
                "description": "Son saqlaydigan qutini yaratadigan so'z qaysi?",
                "description_ru": "Какое слово создаёт коробку для хранения числа?",
                "exercise_type": "multiple_choice",
                "options": ["let", "function", "onclick", "style"],
                "options_ru": ["let", "function", "onclick", "style"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"let\" — \"bo'lsin\" (yangi qiymat yaratamiz).",
                "hint_ru": "\"let\" — «пусть будет» (создаём новое значение).",
                "explanation": "let hisob = 0; — hisob nomli o'zgaruvchi yaratib, 0 qiymat beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Funksiya yaratish",
                "title_ru": "Создание функции",
                "description": "Nomi bilan chaqiriladigan buyruqlar to'plamini yaratish uchun to'ldiring: '___ ortir() { ... }'",
                "description_ru": "Заполни, чтобы создать набор команд, вызываемый по имени: '___ ortir() { ... }'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "function",
                "correct_answers_ru": "function",
                "hint": "Ingliz tilida \"funksiya\".",
                "hint_ru": "По-английски «функция».",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Hisoblagich funksiyasini tuzing",
                "title_ru": "Собери функцию счётчика",
                "description": "Bloklarni tartibga qo'ying: hisobni 1 taga oshiruvchi va ekranga chiqaruvchi funksiya.",
                "description_ru": "Расставь блоки: функция, увеличивающая счётчик и показывающая его на экране.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "function ortir() {",
                    "hisob = hisob + 1;",
                    "document.getElementById('son').innerText = hisob;",
                    "}",
                ],
                "drag_items_ru": [
                    "function ortir() {",
                    "hisob = hisob + 1;",
                    "document.getElementById('son').innerText = hisob;",
                    "}",
                ],
                "correct_order": [
                    "function ortir() {",
                    "hisob = hisob + 1;",
                    "document.getElementById('son').innerText = hisob;",
                    "}",
                ],
                "hint": "Funksiya ochiladi, hisob oshadi, ekranga chiqadi, funksiya yopiladi.",
                "hint_ru": "Функция открывается, счётчик растёт, выводится на экран, функция закрывается.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mening hisoblagichim",
            "task_title_ru": "Проект: мой счётчик",
            "task_description": (
                "O'z hisoblagichingizni yasang — masalan, nechta olma "
                "yig'ganingiz yoki nechta yulduz topganingiz hisoblagichi. Har "
                "bosishda son oshsin. index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Сделай свой счётчик — например, сколько яблок собрал или "
                "сколько звёзд нашёл. Число должно расти с каждым нажатием. "
                "Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• <script> blokida let bilan o'zgaruvchi yaratilsin\n"
                "• function bilan hisoblovchi funksiya yozilsin\n"
                "• Tugma onclick bilan funksiyani chaqirsin va son ekranda ko'rinsin"
            ),
            "task_requirements_ru": (
                "• В блоке <script> создана переменная через let\n"
                "• Написана считающая функция через function\n"
                "• Кнопка вызывает функцию через onclick, число видно на экране"
            ),
            "task_technologies": "HTML, JavaScript",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Shart: agar-aks holda (if)",
        "title_ru": "Условие: если-иначе (if)",
        "points_reward": 20,
        "text_content": (
            "<h2>Shartni tekshirish</h2>"
            "<p><b>if</b> (\"agar\") biror shart <b>rost</b> bo'lsagina "
            "ichidagi buyruqlarni bajaradi:</p>"
            "<pre><code>if (hisob &gt;= 5) {\n"
            "  alert('Yutdingiz!');\n"
            "}</code></pre>"
            "<p>Bu yerda <code>&gt;=</code> — \"katta yoki teng\". Hisob 5 yoki "
            "undan katta bo'lsa, xabar chiqadi.</p>"
            "<h2>Aks holda — else</h2>"
            "<p><b>else</b> — shart <b>yolg'on</b> bo'lganda ishlaydigan "
            "qism:</p>"
            "<pre><code>if (hisob &gt;= 5) {\n"
            "  alert('Yutdingiz!');\n"
            "} else {\n"
            "  alert('Yana bosing!');\n"
            "}</code></pre>"
            "<p>Shart rost bo'lsa — birinchi qism, yolg'on bo'lsa — else "
            "ichidagi qism ishlaydi.</p>"
        ),
        "text_content_ru": (
            "<h2>Проверяем условие</h2>"
            "<p><b>if</b> («если») выполняет команды внутри только когда "
            "условие <b>истинно</b>:</p>"
            "<pre><code>if (hisob &gt;= 5) {\n"
            "  alert('Yutdingiz!');\n"
            "}</code></pre>"
            "<p>Здесь <code>&gt;=</code> — «больше или равно». Если hisob равен "
            "5 или больше, появится сообщение.</p>"
            "<h2>Иначе — else</h2>"
            "<p><b>else</b> — часть, которая выполняется, когда условие "
            "<b>ложно</b>:</p>"
            "<pre><code>if (hisob &gt;= 5) {\n"
            "  alert('Yutdingiz!');\n"
            "} else {\n"
            "  alert('Yana bosing!');\n"
            "}</code></pre>"
            "<p>Если условие истинно — выполняется первая часть, если ложно — "
            "часть внутри else.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: G'alaba hisoblagichi",
            "description": "5 taga yetganda tabriklovchi xabar chiqaradigan hisoblagich.",
            "sample_type": "web",
            "html_code": (
                "<p id=\"son\">0</p>\n"
                "<button onclick=\"ortir()\">+1</button>\n"
            ),
            "css_code": None,
            "js_code": (
                "let hisob = 0;\n"
                "function ortir() {\n"
                "  hisob = hisob + 1;\n"
                "  document.getElementById('son').innerText = hisob;\n"
                "  if (hisob >= 5) {\n"
                "    alert('Yutdingiz!');\n"
                "  }\n"
                "}\n"
            ),
        },
        "exercises": [
            {
                "title": "Shart so'zi",
                "title_ru": "Слово условия",
                "description": "Shartni tekshiradigan so'z qaysi?",
                "description_ru": "Какое слово проверяет условие?",
                "exercise_type": "multiple_choice",
                "options": ["if", "function", "let", "onclick"],
                "options_ru": ["if", "function", "let", "onclick"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ingliz tilida \"agar\".",
                "hint_ru": "По-английски «если».",
                "explanation": "if (shart) { ... } — shart rost bo'lsagina ichidagi kod ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Belgi ma'nosi",
                "title_ru": "Значение символа",
                "description": "'>=' belgisi nimani bildiradi?",
                "description_ru": "Что означает символ '>='?",
                "exercise_type": "multiple_choice",
                "options": ["Katta yoki teng", "Kichik", "Teng emas", "Ko'paytirish"],
                "options_ru": ["Больше или равно", "Меньше", "Не равно", "Умножение"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\">\" — katta, \"=\" — teng, ikkalasi birga.",
                "hint_ru": "\">\" — больше, \"=\" — равно, вместе.",
                "explanation": ">= — chap tomondagi son o'ng tomondagidan katta yoki teng bo'lsa rost.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Aks holda",
                "title_ru": "Иначе",
                "description": "Shart yolg'on bo'lganda ishlaydigan qismni to'ldiring: 'if (...) { ... } ___ { ... }'",
                "description_ru": "Заполни часть, которая выполняется при ложном условии: 'if (...) { ... } ___ { ... }'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "else",
                "correct_answers_ru": "else",
                "hint": "Ingliz tilida \"aks holda\".",
                "hint_ru": "По-английски «иначе».",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "G'alaba shartini tuzing",
                "title_ru": "Собери условие победы",
                "description": "Bloklarni tartibga qo'ying: hisob 5 dan katta yoki teng bo'lsa xabar chiqaradigan shart.",
                "description_ru": "Расставь блоки: условие, показывающее сообщение при hisob больше или равно 5.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["if (hisob >= 5) {", "alert('Yutdingiz!');", "}"],
                "drag_items_ru": ["if (hisob >= 5) {", "alert('Yutdingiz!');", "}"],
                "correct_order": ["if (hisob >= 5) {", "alert('Yutdingiz!');", "}"],
                "hint": "Shart ochiladi, ichidagi buyruq, shart yopiladi.",
                "hint_ru": "Условие открывается, команда внутри, условие закрывается.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: G'alaba sharti bilan hisoblagich",
            "task_title_ru": "Проект: счётчик с условием победы",
            "task_description": (
                "3-darsdagi hisoblagichingizga g'alaba sharti qo'shing — "
                "masalan, 10 taga yetganda tabriklovchi xabar chiqsin. "
                "index.html ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Добавь своему счётчику из 3-го урока условие победы — "
                "например, при достижении 10 показывается поздравление. "
                "Отправь index.html в ZIP."
            ),
            "task_requirements": (
                "• Hisoblagich ishlab tursin (let, function, onclick)\n"
                "• if bilan shart tekshirilsin (masalan >= 10)\n"
                "• Shart rost bo'lganda alert bilan tabriklovchi xabar chiqsin"
            ),
            "task_requirements_ru": (
                "• Счётчик работает (let, function, onclick)\n"
                "• Условие проверяется через if (например >= 10)\n"
                "• При истинном условии alert показывает поздравление"
            ),
            "task_technologies": "HTML, JavaScript",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy loyiha: Interaktiv sahifa",
        "title_ru": "Итоговый проект: интерактивная страница",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi HTML, CSS va JavaScript'da o'rgangan hamma narsani "
            "birlashtirib, o'zimizning <b>interaktiv sahifamizni</b> "
            "yaratamiz: matn va rangni o'zgartiruvchi tugmalar, ishlaydigan "
            "hisoblagich va g'alaba sharti.</p>"
            "<h3>Interaktiv sahifa qanday ishlaydi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Tugma bosiladi (onclick)\"] --> B[\"Funksiya ishga tushadi\"]\n"
            "  B --> C[\"O'zgaruvchi yangilanadi\"]\n"
            "  C --> D[\"Ekrandagi matn/rang o'zgaradi\"]\n"
            "  D --> E{\"Shart bajarildimi?\"}\n"
            "  E -->|\"ha\"| F[\"Tabriklovchi xabar (alert)\"]\n"
            "  E -->|\"yo'q\"| A\n"
            "</pre>"
            "<p>Shu tsikl — bosish, funksiya, o'zgarish, tekshirish — har "
            "qanday interaktiv o'yin va ilovaning yuragidir.</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим всё, что выучили в HTML, CSS и JavaScript, и "
            "создадим свою <b>интерактивную страницу</b>: кнопки, меняющие "
            "текст и цвет, работающий счётчик и условие победы.</p>"
            "<h3>Как работает интерактивная страница</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Tugma bosiladi (onclick)\"] --> B[\"Funksiya ishga tushadi\"]\n"
            "  B --> C[\"O'zgaruvchi yangilanadi\"]\n"
            "  C --> D[\"Ekrandagi matn/rang o'zgaradi\"]\n"
            "  D --> E{\"Shart bajarildimi?\"}\n"
            "  E -->|\"ha\"| F[\"Tabriklovchi xabar (alert)\"]\n"
            "  E -->|\"yo'q\"| A\n"
            "</pre>"
            "<p>Этот цикл — нажатие, функция, изменение, проверка — сердце "
            "любой интерактивной игры и приложения.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: To'liq interaktiv karta",
            "description": "Rang, matn va hisoblagichi bo'lgan to'liq sahifa.",
            "sample_type": "web",
            "html_code": (
                "<h1 id=\"sarlavha\">Mening sahifam</h1>\n"
                "<button onclick=\"document.getElementById('sarlavha').style.color = 'purple'\">Rangla</button>\n"
                "<p id=\"son\">0</p>\n"
                "<button onclick=\"ortir()\">+1</button>\n"
            ),
            "css_code": (
                "h1 { text-align: center; }\n"
                "#son { font-size: 30px; text-align: center; }\n"
            ),
            "js_code": (
                "let hisob = 0;\n"
                "function ortir() {\n"
                "  hisob = hisob + 1;\n"
                "  document.getElementById('son').innerText = hisob;\n"
                "  if (hisob >= 5) {\n"
                "    alert('Yutdingiz!');\n"
                "  }\n"
                "}\n"
            ),
        },
        "exercises": [
            {
                "title": "Interaktivlik tili",
                "title_ru": "Язык интерактивности",
                "description": "Sahifani interaktiv (harakatchan) qiladigan til qaysi?",
                "description_ru": "Какой язык делает страницу интерактивной?",
                "exercise_type": "multiple_choice",
                "options": ["JavaScript", "HTML", "CSS", "Word"],
                "options_ru": ["JavaScript", "HTML", "CSS", "Word"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Butun kurs shu haqida edi.",
                "hint_ru": "Весь курс был про это.",
                "explanation": "JavaScript sahifaga harakat va reaksiya qo'shadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Uchta qism",
                "title_ru": "Три части",
                "description": "Veb-sahifaning nechta asosiy qismi bor: skelet, bezak, harakat?",
                "description_ru": "Сколько основных частей у веб-страницы: скелет, оформление, действие?",
                "exercise_type": "multiple_choice",
                "options": ["3 ta: HTML, CSS, JavaScript", "2 ta: HTML, CSS", "1 ta: JavaScript", "4 ta"],
                "options_ru": ["3: HTML, CSS, JavaScript", "2: HTML, CSS", "1: JavaScript", "4"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Har biri boshqa kursda o'rganildi.",
                "hint_ru": "Каждой был посвящён отдельный курс.",
                "explanation": "HTML — skelet, CSS — bezak, JavaScript — harakat.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Funksiya chaqirish",
                "title_ru": "Вызов функции",
                "description": "Tugma bosilganda funksiyani chaqiradigan atributni yozing: '<button ___=\"ortir()\">'",
                "description_ru": "Напиши атрибут, вызывающий функцию по нажатию: '<button ___=\"ortir()\">'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "onclick",
                "correct_answers_ru": "onclick",
                "hint": "Kursning birinchi darsida o'rgangan atribut.",
                "hint_ru": "Атрибут из первого урока курса.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Interaktivlik tsiklini tartibga soling",
                "title_ru": "Расставь цикл интерактивности",
                "description": "Bosishdan natijagacha bo'lgan qadamlarni to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь шаги от нажатия до результата в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Tugma bosiladi", "Funksiya ishlaydi", "O'zgaruvchi yangilanadi", "Ekran o'zgaradi"],
                "drag_items_ru": ["Нажимается кнопка", "Работает функция", "Обновляется переменная", "Экран меняется"],
                "correct_order": ["Tugma bosiladi", "Funksiya ishlaydi", "O'zgaruvchi yangilanadi", "Ekran o'zgaradi"],
                "hint": "Sababdan natijaga qarab boring.",
                "hint_ru": "Иди от причины к результату.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Mening interaktiv sahifam",
            "task_title_ru": "Итоговый проект: моя интерактивная страница",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: o'zingiz "
                "haqingizdagi sahifaga kamida bitta rang/matn o'zgartiruvchi "
                "tugma va ishlaydigan hisoblagich (g'alaba sharti bilan) "
                "qo'shing. index.html ni ZIP qilib topshiring — bu sizning eng "
                "interaktiv loyihangiz!"
            ),
            "task_description_ru": (
                "Объедини всё, что выучил: добавь на страницу о себе хотя бы "
                "одну кнопку, меняющую цвет или текст, и работающий счётчик (с "
                "условием победы). Отправь index.html в ZIP — это твой самый "
                "интерактивный проект!"
            ),
            "task_requirements": (
                "• Kamida bitta tugma matn yoki rangni o'zgartirsin\n"
                "• Ishlaydigan hisoblagich bo'lsin (let, function, onclick)\n"
                "• if bilan g'alaba sharti tekshirilsin va alert bilan xabar chiqsin"
            ),
            "task_requirements_ru": (
                "• Хотя бы одна кнопка меняет текст или цвет\n"
                "• Работающий счётчик (let, function, onclick)\n"
                "• Условие победы проверяется через if, alert показывает сообщение"
            ),
            "task_technologies": "HTML, CSS, JavaScript",
            "task_deadline_days": 5,
        },
    },
]
