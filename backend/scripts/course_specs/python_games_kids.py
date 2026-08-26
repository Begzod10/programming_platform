"""Python text-games course for children aged 7-12 (Uzbek-primary, Russian).

Sequel to course 146 (Python turtle / first text code). Moves from drawing to
game LOGIC with simple text games: talking to the player (print/input),
randomness, if/else, while loops, a guess-the-number game, and a
rock-paper-scissors capstone. Python runs and is AI-gradable, so every `sample`
uses sample_type "code" with real runnable Python, and every `task` asks the
child to write a small .py program and submit it (ZIP) for review.

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "Python bilan o'yinlar (bolalar uchun)",
    "title_ru": "Игры на Python (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun Python'da oddiy o'yinlar yozish kursi. "
        "O'yinchi bilan gaplashishni (print, input), tasodifni, shart va "
        "sikllarni o'rganamiz hamda \"Sonni top\" va \"Tosh-qaychi-qog'oz\" "
        "o'yinlarini yozamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: пишем простые игры на Python. Научимся "
        "общаться с игроком (print, input), использовать случайность, условия "
        "и циклы, а также напишем игры \"Угадай число\" и "
        "\"Камень-ножницы-бумага\"."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": 146,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "O'yinchi bilan gaplashamiz",
        "title_ru": "Разговариваем с игроком",
        "points_reward": 15,
        "text_content": (
            "<h2>Ekranga yozish — print</h2>"
            "<p>Python'da ekranga yozish uchun <code>print()</code> ishlatamiz. "
            "So'zlar qo'shtirnoq ichida yoziladi:</p>"
            "<pre><code>print(\"Salom, o'yin boshlandi!\")</code></pre>"
            "<h2>O'yinchidan so'rash — input</h2>"
            "<p><code>input()</code> o'yinchidan javob so'raydi va uni saqlaydi:</p>"
            "<pre><code>ism = input(\"Isming nima? \")\n"
            "print(\"Salom, \" + ism + \"!\")</code></pre>"
            "<p>O'yinchi ismini yozadi, dastur esa uni <code>ism</code> "
            "o'zgaruvchisiga saqlab, salom aytadi.</p>"
            "<h3>Dastur qanday gaplashadi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"input — o'yinchidan so'raydi\"] --> B[\"javob saqlanadi\"]\n"
            "  B --> C[\"print — javob bilan gapiradi\"]\n"
            "</pre>"
        ),
        "text_content_ru": (
            "<h2>Пишем на экран — print</h2>"
            "<p>В Python для вывода на экран используем <code>print()</code>. "
            "Слова пишутся в кавычках:</p>"
            "<pre><code>print(\"Salom, o'yin boshlandi!\")</code></pre>"
            "<h2>Спрашиваем игрока — input</h2>"
            "<p><code>input()</code> спрашивает игрока и сохраняет ответ:</p>"
            "<pre><code>ism = input(\"Isming nima? \")\n"
            "print(\"Salom, \" + ism + \"!\")</code></pre>"
            "<p>Игрок пишет своё имя, программа сохраняет его в переменную "
            "<code>ism</code> и здоровается.</p>"
            "<h3>Как программа разговаривает</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"input — o'yinchidan so'raydi\"] --> B[\"javob saqlanadi\"]\n"
            "  B --> C[\"print — javob bilan gapiradi\"]\n"
            "</pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Salomlashuvchi dastur",
            "description": "Dastur ismni so'raydi va salom aytadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "salom.py",
                    "language": "python",
                    "code": (
                        "ism = input(\"Isming nima? \")\n"
                        "print(\"Salom, \" + ism + \"!\")\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Ekranga yozish",
                "title_ru": "Вывод на экран",
                "description": "Ekranga so'z yozish uchun qaysi buyruq ishlatiladi?",
                "description_ru": "Какая команда выводит слово на экран?",
                "exercise_type": "multiple_choice",
                "options": ["print()", "input()", "random()", "if"],
                "options_ru": ["print()", "input()", "random()", "if"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"print\" — chop etish, yozish.",
                "hint_ru": "\"print\" — печатать, выводить.",
                "explanation": "print() so'zlarni ekranga yozadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "O'yinchidan so'rash",
                "title_ru": "Спросить игрока",
                "description": "O'yinchidan javob so'raydigan buyruq qaysi?",
                "description_ru": "Какая команда спрашивает ответ у игрока?",
                "exercise_type": "multiple_choice",
                "options": ["input()", "print()", "while", "import"],
                "options_ru": ["input()", "print()", "while", "import"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"input\" — kiritish, kiritma.",
                "hint_ru": "\"input\" — ввод.",
                "explanation": "input() o'yinchidan javob so'rab, uni qaytaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "So'rash buyrug'i",
                "title_ru": "Команда запроса",
                "description": "O'yinchidan ism so'rash uchun to'ldiring: 'ism = ___(\"Isming? \")'",
                "description_ru": "Заполни, чтобы спросить имя: 'ism = ___(\"Isming? \")'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "input",
                "correct_answers_ru": "input",
                "hint": "Kiritish buyrug'i.",
                "hint_ru": "Команда ввода.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Salom dasturini tuzing",
                "title_ru": "Собери программу приветствия",
                "description": "Kod qatorlarini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь строки кода в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["ism = input(\"Isming nima? \")", "print(\"Salom, \" + ism)"],
                "drag_items_ru": ["ism = input(\"Isming nima? \")", "print(\"Salom, \" + ism)"],
                "correct_order": ["ism = input(\"Isming nima? \")", "print(\"Salom, \" + ism)"],
                "hint": "Avval so'raymiz, keyin salom aytamiz.",
                "hint_ru": "Сначала спрашиваем, потом здороваемся.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Salomlashuvchi dastur",
            "task_title_ru": "Проект: программа-приветствие",
            "task_description": (
                "O'yinchidan ismini so'rab, unga chiroyli salom aytadigan Python "
                "dasturi yozing. Faylni salom.py deb nomlab, ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши программу на Python, которая спрашивает имя игрока и "
                "красиво здоровается. Назови файл salom.py, заархивируй в ZIP и "
                "отправь."
            ),
            "task_requirements": (
                "• input() bilan ism so'ralsin\n"
                "• Ism o'zgaruvchiga saqlansin\n"
                "• print() bilan ism qo'shib salom aytilsin"
            ),
            "task_requirements_ru": (
                "• Имя спрашивается через input()\n"
                "• Имя сохраняется в переменную\n"
                "• print() здоровается, добавляя имя"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Sonlar va tasodif",
        "title_ru": "Числа и случайность",
        "points_reward": 20,
        "text_content": (
            "<h2>Tasodifiy son</h2>"
            "<p>O'yinda tasodif kerak — masalan zar tashlash. Buning uchun avval "
            "<code>random</code> kutubxonasini chaqiramiz:</p>"
            "<pre><code>import random\n"
            "son = random.randint(1, 6)\n"
            "print(\"Zar:\", son)</code></pre>"
            "<p><code>random.randint(1, 6)</code> — 1 dan 6 gacha tasodifiy son "
            "beradi (zar kabi).</p>"
            "<h2>Matnni songa aylantirish</h2>"
            "<p><code>input()</code> har doim <b>matn</b> qaytaradi. Uni son "
            "qilish uchun <code>int()</code> ishlatamiz:</p>"
            "<pre><code>yosh = int(input(\"Yoshing? \"))</code></pre>"
        ),
        "text_content_ru": (
            "<h2>Случайное число</h2>"
            "<p>В игре нужна случайность — например бросок кубика. Для этого "
            "сначала подключаем библиотеку <code>random</code>:</p>"
            "<pre><code>import random\n"
            "son = random.randint(1, 6)\n"
            "print(\"Zar:\", son)</code></pre>"
            "<p><code>random.randint(1, 6)</code> — даёт случайное число от 1 до "
            "6 (как кубик).</p>"
            "<h2>Превращаем текст в число</h2>"
            "<p><code>input()</code> всегда возвращает <b>текст</b>. Чтобы "
            "сделать из него число, используем <code>int()</code>:</p>"
            "<pre><code>yosh = int(input(\"Yoshing? \"))</code></pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Zar tashlash",
            "description": "1 dan 6 gacha tasodifiy son chiqaradi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "zar.py",
                    "language": "python",
                    "code": (
                        "import random\n"
                        "son = random.randint(1, 6)\n"
                        "print(\"Zar tushdi:\", son)\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kutubxonani chaqirish",
                "title_ru": "Подключить библиотеку",
                "description": "Tasodif uchun qaysi kutubxonani chaqiramiz?",
                "description_ru": "Какую библиотеку подключаем для случайности?",
                "exercise_type": "multiple_choice",
                "options": ["random", "turtle", "print", "input"],
                "options_ru": ["random", "turtle", "print", "input"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"random\" — tasodifiy.",
                "hint_ru": "\"random\" — случайный.",
                "explanation": "import random tasodifiy sonlar kutubxonasini chaqiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tasodifiy son",
                "title_ru": "Случайное число",
                "description": "1 dan 6 gacha tasodifiy son beradigan buyruq qaysi?",
                "description_ru": "Какая команда даёт случайное число от 1 до 6?",
                "exercise_type": "multiple_choice",
                "options": ["random.randint(1, 6)", "print(1, 6)", "input(1, 6)", "int(1, 6)"],
                "options_ru": ["random.randint(1, 6)", "print(1, 6)", "input(1, 6)", "int(1, 6)"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"randint\" — random + integer (butun son).",
                "hint_ru": "\"randint\" — random + integer (целое).",
                "explanation": "random.randint(1, 6) 1 dan 6 gacha tasodifiy butun son beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Matnni songa aylantirish",
                "title_ru": "Текст в число",
                "description": "input javobini songa aylantirish uchun to'ldiring: 'yosh = ___(input(\"Yosh? \"))'",
                "description_ru": "Заполни, чтобы превратить ответ input в число: 'yosh = ___(input(\"Yosh? \"))'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "int",
                "correct_answers_ru": "int",
                "hint": "\"integer\" — butun son.",
                "hint_ru": "\"integer\" — целое число.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Zar dasturini tuzing",
                "title_ru": "Собери программу кубика",
                "description": "Kod qatorlarini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь строки кода в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["import random", "son = random.randint(1, 6)", "print(son)"],
                "drag_items_ru": ["import random", "son = random.randint(1, 6)", "print(son)"],
                "correct_order": ["import random", "son = random.randint(1, 6)", "print(son)"],
                "hint": "Avval kutubxona, keyin son, oxirida chop etish.",
                "hint_ru": "Сначала библиотека, потом число, в конце вывод.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Zar tashlagich",
            "task_title_ru": "Проект: бросок кубика",
            "task_description": (
                "1 dan 6 gacha tasodifiy son chiqaradigan (zar tashlaydigan) "
                "Python dasturi yozing. zar.py ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши программу на Python, которая выдаёт случайное число от 1 "
                "до 6 (бросает кубик). Отправь zar.py в ZIP."
            ),
            "task_requirements": (
                "• import random ishlatilsin\n"
                "• random.randint bilan 1-6 son olinsin\n"
                "• Natija print() bilan ko'rsatilsin"
            ),
            "task_requirements_ru": (
                "• Использован import random\n"
                "• Число 1-6 получено через random.randint\n"
                "• Результат показан через print()"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Shart (if / else)",
        "title_ru": "Условие (if / else)",
        "points_reward": 20,
        "text_content": (
            "<h2>Agar ... bo'lsa</h2>"
            "<p>O'yin qaror qabul qilishi kerak. Buni <code>if</code> (agar) "
            "bilan qilamiz:</p>"
            "<pre><code>yosh = int(input(\"Yoshing? \"))\n"
            "if yosh >= 7:\n"
            "    print(\"Sen katta bola ekansan!\")\n"
            "else:\n"
            "    print(\"Sen kichkinasan.\")</code></pre>"
            "<p><code>if</code> sharti to'g'ri bo'lsa, birinchi qatorni yozadi; "
            "aks holda <code>else</code> qatorini. <b>Muhim:</b> if ostidagi "
            "qatorlar <b>ichkariga surilib</b> (bo'sh joy bilan) yoziladi.</p>"
            "<p>Taqqoslash belgilari: <code>&gt;</code> katta, <code>&lt;</code> "
            "kichik, <code>==</code> teng.</p>"
        ),
        "text_content_ru": (
            "<h2>Если ...</h2>"
            "<p>Игра должна принимать решения. Это делаем с помощью "
            "<code>if</code> (если):</p>"
            "<pre><code>yosh = int(input(\"Yoshing? \"))\n"
            "if yosh >= 7:\n"
            "    print(\"Sen katta bola ekansan!\")\n"
            "else:\n"
            "    print(\"Sen kichkinasan.\")</code></pre>"
            "<p>Если условие <code>if</code> верно — печатается первая строка, "
            "иначе — строка <code>else</code>. <b>Важно:</b> строки под if "
            "пишутся <b>с отступом</b> (пробелами).</p>"
            "<p>Знаки сравнения: <code>&gt;</code> больше, <code>&lt;</code> "
            "меньше, <code>==</code> равно.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Katta yoki kichik",
            "description": "Yoshga qarab boshqacha javob beradi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "yosh.py",
                    "language": "python",
                    "code": (
                        "yosh = int(input(\"Yoshing nechida? \"))\n"
                        "if yosh >= 7:\n"
                        "    print(\"Sen katta bola ekansan!\")\n"
                        "else:\n"
                        "    print(\"Sen kichkinasan.\")\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Shart so'zi",
                "title_ru": "Слово условия",
                "description": "Qaror qabul qilish (agar) uchun qaysi so'z ishlatiladi?",
                "description_ru": "Какое слово используется для условия (если)?",
                "exercise_type": "multiple_choice",
                "options": ["if", "print", "input", "import"],
                "options_ru": ["if", "print", "input", "import"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"if\" — agar.",
                "hint_ru": "\"if\" — если.",
                "explanation": "if — shart to'g'ri bo'lgandagina ichidagini bajaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Aks holda",
                "title_ru": "Иначе",
                "description": "Shart noto'g'ri bo'lganda ishlaydigan so'z qaysi?",
                "description_ru": "Какое слово срабатывает, если условие неверно?",
                "exercise_type": "multiple_choice",
                "options": ["else", "if", "while", "print"],
                "options_ru": ["else", "if", "while", "print"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"else\" — aks holda.",
                "hint_ru": "\"else\" — иначе.",
                "explanation": "else — if sharti noto'g'ri bo'lganda ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tenglik belgisi",
                "title_ru": "Знак равенства",
                "description": "Ikki qiymat teng ekanini tekshirish belgisini yozing: 'if a ___ b:'",
                "description_ru": "Напиши знак проверки равенства: 'if a ___ b:'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "==",
                "correct_answers_ru": "==",
                "hint": "Ikkita teng belgisi.",
                "hint_ru": "Два знака равно.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Shartni tuzing",
                "title_ru": "Собери условие",
                "description": "Kod qatorlarini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь строки кода в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["if yosh >= 7:", "    print(\"Katta\")", "else:", "    print(\"Kichik\")"],
                "drag_items_ru": ["if yosh >= 7:", "    print(\"Katta\")", "else:", "    print(\"Kichik\")"],
                "correct_order": ["if yosh >= 7:", "    print(\"Katta\")", "else:", "    print(\"Kichik\")"],
                "hint": "Avval if, uning ishi, keyin else, uning ishi.",
                "hint_ru": "Сначала if и его действие, потом else и его действие.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Katta yoki kichik",
            "task_title_ru": "Проект: большой или маленький",
            "task_description": (
                "O'yinchidan son so'rab, agar u 10 dan katta bo'lsa \"Katta son!\", "
                "aks holda \"Kichik son.\" deb yozadigan dastur yozing. son.py ni "
                "ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши программу, которая спрашивает число и печатает \"Katta "
                "son!\", если оно больше 10, иначе \"Kichik son.\". Отправь son.py "
                "в ZIP."
            ),
            "task_requirements": (
                "• int(input()) bilan son so'ralsin\n"
                "• if bilan 10 dan katta ekani tekshirilsin\n"
                "• else bilan boshqa javob berilsin"
            ),
            "task_requirements_ru": (
                "• Число спрашивается через int(input())\n"
                "• if проверяет, больше ли оно 10\n"
                "• else даёт другой ответ"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Takrorlash (while sikli)",
        "title_ru": "Повторение (цикл while)",
        "points_reward": 20,
        "text_content": (
            "<h2>Bir ishni qayta-qayta</h2>"
            "<p>O'yinda ko'pincha bir ishni qayta-qayta qilamiz. "
            "<code>while</code> (toki) sikli shart to'g'ri turgan ekan, "
            "ichidagini takrorlaydi:</p>"
            "<pre><code>son = 1\n"
            "while son <= 5:\n"
            "    print(son)\n"
            "    son = son + 1</code></pre>"
            "<p>Bu 1, 2, 3, 4, 5 sonlarini yozadi. Har aylanishda "
            "<code>son</code> bittaga oshadi; u 5 dan oshsa, sikl to'xtaydi.</p>"
            "<p><b>Diqqat:</b> ichidagi <code>son = son + 1</code> bo'lmasa, sikl "
            "hech qachon to'xtamaydi (cheksiz sikl)!</p>"
        ),
        "text_content_ru": (
            "<h2>Одно действие много раз</h2>"
            "<p>В игре часто повторяем одно действие. Цикл <code>while</code> "
            "(пока) повторяет то, что внутри, пока условие верно:</p>"
            "<pre><code>son = 1\n"
            "while son <= 5:\n"
            "    print(son)\n"
            "    son = son + 1</code></pre>"
            "<p>Это печатает 1, 2, 3, 4, 5. На каждом круге <code>son</code> "
            "растёт на 1; когда станет больше 5, цикл остановится.</p>"
            "<p><b>Внимание:</b> без <code>son = son + 1</code> внутри цикл "
            "никогда не остановится (бесконечный цикл)!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: 1 dan 5 gacha sanash",
            "description": "while sikli bilan sonlarni sanaydi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "sanoq.py",
                    "language": "python",
                    "code": (
                        "son = 1\n"
                        "while son <= 5:\n"
                        "    print(son)\n"
                        "    son = son + 1\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Takrorlash so'zi",
                "title_ru": "Слово повторения",
                "description": "Shart turgan ekan takrorlaydigan so'z qaysi?",
                "description_ru": "Какое слово повторяет, пока верно условие?",
                "exercise_type": "multiple_choice",
                "options": ["while", "if", "print", "import"],
                "options_ru": ["while", "if", "print", "import"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"while\" — toki, ...gacha.",
                "hint_ru": "\"while\" — пока.",
                "explanation": "while sharti to'g'ri turgan ekan ichidagini takrorlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Cheksiz sikl xavfi",
                "title_ru": "Опасность бесконечного цикла",
                "description": "Sikl to'xtashi uchun ichida nima bo'lishi kerak?",
                "description_ru": "Что должно быть внутри, чтобы цикл остановился?",
                "exercise_type": "multiple_choice",
                "options": [
                    "son o'zgarib borishi (masalan son = son + 1)",
                    "yana bitta print",
                    "import random",
                    "hech narsa",
                ],
                "options_ru": [
                    "изменение son (например son = son + 1)",
                    "ещё один print",
                    "import random",
                    "ничего",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Shart bir kun yolg'on bo'lishi kerak.",
                "hint_ru": "Условие когда-то должно стать ложным.",
                "explanation": "Sonni o'zgartirmasak, shart doim to'g'ri qolib, sikl cheksiz aylanadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Sikl so'zini yozing",
                "title_ru": "Напиши слово цикла",
                "description": "Takrorlash siklini yozing: '___ son <= 5:'",
                "description_ru": "Напиши цикл повторения: '___ son <= 5:'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "while",
                "correct_answers_ru": "while",
                "hint": "Toki ma'nosidagi so'z.",
                "hint_ru": "Слово в значении \"пока\".",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Sanoq siklini tuzing",
                "title_ru": "Собери цикл счёта",
                "description": "Kod qatorlarini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь строки кода в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["son = 1", "while son <= 5:", "    print(son)", "    son = son + 1"],
                "drag_items_ru": ["son = 1", "while son <= 5:", "    print(son)", "    son = son + 1"],
                "correct_order": ["son = 1", "while son <= 5:", "    print(son)", "    son = son + 1"],
                "hint": "Avval boshlang'ich son, keyin sikl, ichida chop etish va oshirish.",
                "hint_ru": "Сначала начальное число, потом цикл, внутри вывод и увеличение.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: 1 dan 10 gacha sanash",
            "task_title_ru": "Проект: счёт от 1 до 10",
            "task_description": (
                "while sikli bilan 1 dan 10 gacha sonlarni ekranga yozadigan "
                "dastur yozing. sanoq.py ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши программу, которая циклом while печатает числа от 1 до "
                "10. Отправь sanoq.py в ZIP."
            ),
            "task_requirements": (
                "• while sikli ishlatilsin\n"
                "• 1 dan 10 gacha sonlar chiqsin\n"
                "• Sikl ichida son oshirilib borsin"
            ),
            "task_requirements_ru": (
                "• Использован цикл while\n"
                "• Выводятся числа от 1 до 10\n"
                "• Внутри цикла число увеличивается"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "\"Sonni top\" o'yini",
        "title_ru": "Игра \"Угадай число\"",
        "points_reward": 20,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi tasodif, sikl va shartni birlashtirib, birinchi haqiqiy "
            "o'yinni yozamiz — <b>Sonni top</b>! Kompyuter maxfiy son o'ylaydi, "
            "o'yinchi esa uni topguncha taxmin qiladi.</p>"
            "<pre><code>import random\n"
            "maxfiy = random.randint(1, 10)\n"
            "taxmin = 0\n"
            "while taxmin != maxfiy:\n"
            "    taxmin = int(input(\"1-10 orasida son ayt: \"))\n"
            "    if taxmin < maxfiy:\n"
            "        print(\"Kattaroq!\")\n"
            "    elif taxmin > maxfiy:\n"
            "        print(\"Kichikroq!\")\n"
            "print(\"Topding! Barakalla!\")</code></pre>"
            "<p><code>!=</code> — teng emas. Sikl taxmin maxfiyga teng bo'lmaguncha "
            "davom etadi. <code>elif</code> — \"aks holda agar\".</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим случайность, цикл и условие и напишем первую "
            "настоящую игру — <b>Угадай число</b>! Компьютер загадывает "
            "секретное число, а игрок угадывает, пока не найдёт.</p>"
            "<pre><code>import random\n"
            "maxfiy = random.randint(1, 10)\n"
            "taxmin = 0\n"
            "while taxmin != maxfiy:\n"
            "    taxmin = int(input(\"1-10 orasida son ayt: \"))\n"
            "    if taxmin < maxfiy:\n"
            "        print(\"Kattaroq!\")\n"
            "    elif taxmin > maxfiy:\n"
            "        print(\"Kichikroq!\")\n"
            "print(\"Topding! Barakalla!\")</code></pre>"
            "<p><code>!=</code> — не равно. Цикл идёт, пока догадка не равна "
            "секрету. <code>elif</code> — «иначе если».</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Sonni top o'yini",
            "description": "Kompyuter son o'ylaydi, o'yinchi topguncha taxmin qiladi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "sonni_top.py",
                    "language": "python",
                    "code": (
                        "import random\n"
                        "maxfiy = random.randint(1, 10)\n"
                        "taxmin = 0\n"
                        "while taxmin != maxfiy:\n"
                        "    taxmin = int(input(\"1-10 orasida son ayt: \"))\n"
                        "    if taxmin < maxfiy:\n"
                        "        print(\"Kattaroq!\")\n"
                        "    elif taxmin > maxfiy:\n"
                        "        print(\"Kichikroq!\")\n"
                        "print(\"Topding! Barakalla!\")\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Teng emas belgisi",
                "title_ru": "Знак «не равно»",
                "description": "\"Teng emas\" ni qaysi belgi bildiradi?",
                "description_ru": "Какой знак означает «не равно»?",
                "exercise_type": "multiple_choice",
                "options": ["!=", "==", ">=", "<="],
                "options_ru": ["!=", "==", ">=", "<="],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Undov belgisi va teng belgisi.",
                "hint_ru": "Восклицательный знак и знак равно.",
                "explanation": "!= teng emasligini bildiradi; sikl topilguncha davom etadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Aks holda agar",
                "title_ru": "Иначе если",
                "description": "\"Aks holda agar\" ni bildiruvchi so'z qaysi?",
                "description_ru": "Какое слово означает «иначе если»?",
                "exercise_type": "multiple_choice",
                "options": ["elif", "else", "while", "if"],
                "options_ru": ["elif", "else", "while", "if"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "else + if = elif.",
                "hint_ru": "else + if = elif.",
                "explanation": "elif — oldingi shart noto'g'ri bo'lsa, yangi shartni tekshiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Maxfiy son",
                "title_ru": "Секретное число",
                "description": "Kompyuter 1-10 orasida maxfiy son o'ylashi uchun to'ldiring: 'maxfiy = random.___(1, 10)'",
                "description_ru": "Заполни, чтобы компьютер загадал число 1-10: 'maxfiy = random.___(1, 10)'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "randint",
                "correct_answers_ru": "randint",
                "hint": "random + integer.",
                "hint_ru": "random + integer.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "O'yin mantiqini tuzing",
                "title_ru": "Собери логику игры",
                "description": "Sonni top o'yinining boshini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь начало игры «Угадай число» по порядку.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["import random", "maxfiy = random.randint(1, 10)", "while taxmin != maxfiy:", "    taxmin = int(input(\"Son: \"))"],
                "drag_items_ru": ["import random", "maxfiy = random.randint(1, 10)", "while taxmin != maxfiy:", "    taxmin = int(input(\"Son: \"))"],
                "correct_order": ["import random", "maxfiy = random.randint(1, 10)", "while taxmin != maxfiy:", "    taxmin = int(input(\"Son: \"))"],
                "hint": "Kutubxona, maxfiy son, sikl, taxmin so'rash.",
                "hint_ru": "Библиотека, секретное число, цикл, запрос догадки.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Sonni top o'yini",
            "task_title_ru": "Проект: игра \"Угадай число\"",
            "task_description": (
                "Kompyuter 1-10 orasida maxfiy son o'ylaydigan va o'yinchi uni "
                "topguncha \"Kattaroq/Kichikroq\" deb yordam beradigan o'yin "
                "yozing. sonni_top.py ni ZIP qilib topshiring."
            ),
            "task_description_ru": (
                "Напиши игру, где компьютер загадывает число 1-10, а игрок "
                "угадывает с подсказками \"Kattaroq/Kichikroq\". Отправь "
                "sonni_top.py в ZIP."
            ),
            "task_requirements": (
                "• random.randint bilan maxfiy son o'ylansin\n"
                "• while sikli topilguncha davom etsin\n"
                "• if/elif bilan \"Kattaroq/Kichikroq\" yordam berilsin\n"
                "• Topilganda tabrik yozilsin"
            ),
            "task_requirements_ru": (
                "• Секретное число через random.randint\n"
                "• Цикл while идёт до угадывания\n"
                "• if/elif дают подсказки \"Kattaroq/Kichikroq\"\n"
                "• При угадывании выводится поздравление"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy o'yin: Tosh-qaychi-qog'oz",
        "title_ru": "Итоговая игра: Камень-ножницы-бумага",
        "points_reward": 25,
        "text_content": (
            "<h2>Kompyuterga qarshi o'ynaymiz</h2>"
            "<p>Yakuniy o'yin — <b>Tosh-qaychi-qog'oz</b>! Kompyuter tasodifiy "
            "tanlaydi, o'yinchi ham tanlaydi, keyin dastur kim yutganini "
            "aytadi.</p>"
            "<h2>Kim kimni yutadi?</h2>"
            "<p>Uchta qoida bor:</p>"
            "<ul>"
            "<li><b>Tosh</b> qaychini yutadi (qaychini sindiradi)</li>"
            "<li><b>Qaychi</b> qog'ozni yutadi (qog'ozni kesadi)</li>"
            "<li><b>Qog'oz</b> toshni yutadi (toshni o'raydi)</li>"
            "</ul>"
            "<p>Har bir qoidani alohida <code>elif</code> bilan tekshiramiz:</p>"
            "<pre><code>if sen == kompyuter:\n"
            "    print(\"Durrang!\")\n"
            "elif sen == \"tosh\" and kompyuter == \"qaychi\":\n"
            "    print(\"Sen yutding!\")\n"
            "elif sen == \"qaychi\" and kompyuter == \"qog'oz\":\n"
            "    print(\"Sen yutding!\")\n"
            "elif sen == \"qog'oz\" and kompyuter == \"tosh\":\n"
            "    print(\"Sen yutding!\")\n"
            "else:\n"
            "    print(\"Kompyuter yutdi!\")</code></pre>"
            "<p><code>and</code> — \"va\" degani: ikkala shart ham rost "
            "bo'lsagina, elif ishga tushadi. Yuqoridagi uchta elif — o'yinchi "
            "yutadigan uchta holat. Boshqa hamma holatda (durrang bo'lmasa-yu, "
            "o'yinchi yutgan holatlardan birortasiga to'g'ri kelmasa) — "
            "<code>else</code> ishlaydi, ya'ni kompyuter yutgan bo'ladi.</p>"
        ),
        "text_content_ru": (
            "<h2>Играем против компьютера</h2>"
            "<p>Итоговая игра — <b>Камень-ножницы-бумага</b>! Компьютер "
            "выбирает случайно, игрок тоже выбирает, потом программа говорит, "
            "кто выиграл.</p>"
            "<h2>Кто кого побеждает?</h2>"
            "<p>Есть три правила:</p>"
            "<ul>"
            "<li><b>Камень</b> побеждает ножницы (ломает их)</li>"
            "<li><b>Ножницы</b> побеждают бумагу (режут её)</li>"
            "<li><b>Бумага</b> побеждает камень (заворачивает его)</li>"
            "</ul>"
            "<p>Каждое правило проверяем отдельным <code>elif</code>:</p>"
            "<pre><code>if sen == kompyuter:\n"
            "    print(\"Durrang!\")\n"
            "elif sen == \"tosh\" and kompyuter == \"qaychi\":\n"
            "    print(\"Sen yutding!\")\n"
            "elif sen == \"qaychi\" and kompyuter == \"qog'oz\":\n"
            "    print(\"Sen yutding!\")\n"
            "elif sen == \"qog'oz\" and kompyuter == \"tosh\":\n"
            "    print(\"Sen yutding!\")\n"
            "else:\n"
            "    print(\"Kompyuter yutdi!\")</code></pre>"
            "<p><code>and</code> — значит «и»: elif срабатывает только если "
            "оба условия верны. Три elif выше — три случая, когда выигрывает "
            "игрок. Во всех остальных случаях (не ничья и не победа игрока) "
            "срабатывает <code>else</code> — значит, выиграл компьютер.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Tosh-qaychi-qog'oz",
            "description": "Kompyuter tasodifiy tanlaydi, o'yinchi bilan solishtiradi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "tqq.py",
                    "language": "python",
                    "code": (
                        "import random\n"
                        "variantlar = [\"tosh\", \"qaychi\", \"qog'oz\"]\n"
                        "kompyuter = random.choice(variantlar)\n"
                        "sen = input(\"tosh, qaychi yoki qog'oz? \")\n"
                        "print(\"Kompyuter tanladi:\", kompyuter)\n"
                        "\n"
                        "if sen == kompyuter:\n"
                        "    print(\"Durrang!\")\n"
                        "elif sen == \"tosh\" and kompyuter == \"qaychi\":\n"
                        "    print(\"Sen yutding! Tosh qaychini sindiradi.\")\n"
                        "elif sen == \"qaychi\" and kompyuter == \"qog'oz\":\n"
                        "    print(\"Sen yutding! Qaychi qog'ozni kesadi.\")\n"
                        "elif sen == \"qog'oz\" and kompyuter == \"tosh\":\n"
                        "    print(\"Sen yutding! Qog'oz toshni o'raydi.\")\n"
                        "else:\n"
                        "    print(\"Kompyuter yutdi!\")\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Ro'yxatdan tanlash",
                "title_ru": "Выбор из списка",
                "description": "Ro'yxatdan tasodifiy bittasini tanlaydigan buyruq qaysi?",
                "description_ru": "Какая команда выбирает случайный элемент из списка?",
                "exercise_type": "multiple_choice",
                "options": ["random.choice(variantlar)", "random.randint(variantlar)", "print(variantlar)", "input(variantlar)"],
                "options_ru": ["random.choice(variantlar)", "random.randint(variantlar)", "print(variantlar)", "input(variantlar)"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"choice\" — tanlov.",
                "hint_ru": "\"choice\" — выбор.",
                "explanation": "random.choice() ro'yxatdan tasodifiy bitta elementni tanlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Durrang qachon?",
                "title_ru": "Когда ничья?",
                "description": "Qachon \"Durrang\" bo'ladi?",
                "description_ru": "Когда будет «Ничья»?",
                "exercise_type": "multiple_choice",
                "options": [
                    "O'yinchi va kompyuter bir xil tanlaganda",
                    "Kompyuter yutganda",
                    "O'yinchi yutganda",
                    "Har doim",
                ],
                "options_ru": [
                    "Когда игрок и компьютер выбрали одинаково",
                    "Когда выиграл компьютер",
                    "Когда выиграл игрок",
                    "Всегда",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "sen == kompyuter bo'lsa.",
                "hint_ru": "Если sen == kompyuter.",
                "explanation": "Ikkalasi bir xil tanlasa (sen == kompyuter), durrang bo'ladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ro'yxat yasash",
                "title_ru": "Создать список",
                "description": "Variantlar ro'yxati qaysi qavslar ichida yoziladi? To'ldiring: 'variantlar = ___\"tosh\", \"qaychi\"]'",
                "description_ru": "В какие скобки пишется список? Заполни: 'variantlar = ___\"tosh\", \"qaychi\"]'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "[",
                "correct_answers_ru": "[",
                "hint": "Kvadrat qavs ochiladi.",
                "hint_ru": "Открывается квадратная скобка.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "O'yin boshini tuzing",
                "title_ru": "Собери начало игры",
                "description": "Tosh-qaychi-qog'oz o'yinining boshini tartibga qo'ying.",
                "description_ru": "Расставь начало игры по порядку.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["import random", "variantlar = [\"tosh\", \"qaychi\", \"qog'oz\"]", "kompyuter = random.choice(variantlar)", "sen = input(\"tanla: \")"],
                "drag_items_ru": ["import random", "variantlar = [\"tosh\", \"qaychi\", \"qog'oz\"]", "kompyuter = random.choice(variantlar)", "sen = input(\"tanla: \")"],
                "correct_order": ["import random", "variantlar = [\"tosh\", \"qaychi\", \"qog'oz\"]", "kompyuter = random.choice(variantlar)", "sen = input(\"tanla: \")"],
                "hint": "Kutubxona, ro'yxat, kompyuter tanlovi, o'yinchi tanlovi.",
                "hint_ru": "Библиотека, список, выбор компьютера, выбор игрока.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Kim kimni yutadi?",
                "title_ru": "Кто кого побеждает?",
                "description": "Tosh kimni yutadi?",
                "description_ru": "Кого побеждает камень?",
                "exercise_type": "multiple_choice",
                "options": ["Qaychini", "Qog'ozni", "O'zini", "Hech kimni"],
                "options_ru": ["Ножницы", "Бумагу", "Себя", "Никого"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Tosh qattiq, u qaychini sindiradi.",
                "hint_ru": "Камень твёрдый, он ломает ножницы.",
                "explanation": "Tosh qaychini yutadi, qaychi qog'ozni yutadi, qog'oz toshni yutadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Tosh-qaychi-qog'oz o'yini",
            "task_title_ru": "Итоговый проект: игра Камень-ножницы-бумага",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: kompyuter "
                "tasodifiy tanlaydigan, o'yinchi bilan solishtirib UCHALA "
                "holatni ham (durrang, o'yinchi yutdi, kompyuter yutdi) to'g'ri "
                "aniqlaydigan Tosh-qaychi-qog'oz o'yinini yozing. tqq.py ni ZIP "
                "qilib topshiring — bu sizning eng katta o'yiningiz!"
            ),
            "task_description_ru": (
                "Объедини всё выученное: напиши игру Камень-ножницы-бумага, где "
                "компьютер выбирает случайно, а программа правильно определяет "
                "ВСЕ ТРИ исхода (ничья, победил игрок, победил компьютер). "
                "Отправь tqq.py в ZIP — это твоя самая большая игра!"
            ),
            "task_requirements": (
                "• import random va variantlar ro'yxati bo'lsin\n"
                "• random.choice bilan kompyuter tanlasin\n"
                "• input bilan o'yinchi tanlasin\n"
                "• Barcha uchta g'alaba holati (tosh-qaychi, qaychi-qog'oz, "
                "qog'oz-tosh) elif bilan tekshirilsin\n"
                "• Durrang va kompyuter g'alabasi ham to'g'ri aniqlansin"
            ),
            "task_requirements_ru": (
                "• Есть import random и список вариантов\n"
                "• Компьютер выбирает через random.choice\n"
                "• Игрок выбирает через input\n"
                "• Все три исхода победы игрока (камень-ножницы, "
                "ножницы-бумага, бумага-камень) проверяются через elif\n"
                "• Ничья и победа компьютера тоже определяются верно"
            ),
            "task_technologies": "Python",
            "task_deadline_days": 5,
        },
    },
]
