"""Scratch GAMES course for children aged 7-12 (Uzbek-primary, Russian).

Sequel to course 144 (Scratch basics). Builds toward a real "catch the apple"
game: sprite control, a score variable, collisions, randomness, forever loops.
Scratch projects can't run or be AI-graded in the platform, so every `sample`
uses sample_type "code" showing the block script as readable Uzbek pseudocode,
and every `task` asks the child to build the game in Scratch and submit their
SHARE LINK (or a screenshot) for a teacher to review.

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "Scratch 2: O'yin yaratish (bolalar uchun)",
    "title_ru": "Scratch 2: Создаём игру (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun Scratch'da o'yin yaratish kursi. "
        "Personajni tugmalar bilan boshqarishni, ball sanashni, to'qnashuvni "
        "aniqlashni, tasodifiy harakat va sikllarni o'rganamiz hamda o'zimizning "
        "\"Olma tut\" o'yinimizni yaratamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: создаём игру в Scratch. Научимся управлять "
        "персонажем клавишами, считать очки, определять столкновения, "
        "использовать случайность и циклы, а также создадим свою игру "
        "\"Поймай яблоко\"."
    ),
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": 144,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "Personajni tugmalar bilan boshqarish",
        "title_ru": "Управляем персонажем клавишами",
        "points_reward": 15,
        "text_content": (
            "<h2>O'yin nima?</h2>"
            "<p>O'yinda biz personajni <b>boshqaramiz</b> — masalan tugmalar "
            "bilan uni chapga yoki o'ngga harakatlantiramiz. Scratch'da buni "
            "<b>Hodisa</b> (sariq) va <b>Harakat</b> (ko'k) bloklari bilan "
            "qilamiz.</p>"
            # Color key: same 8 categories used across every course-149 lesson's
            # `scratch-block` badges (see StudentLessonPage.css). Repeated once
            # per course intro so a student who lands here without doing course
            # 144 first still gets oriented.
            "<div class=\"scratch-legend\">"
            "<span class=\"scratch-block scratch-block--motion\">Harakat</span>"
            "<span class=\"scratch-block scratch-block--looks\">Ko'rinish</span>"
            "<span class=\"scratch-block scratch-block--sound\">Ovoz</span>"
            "<span class=\"scratch-block scratch-block--events\">Hodisa</span>"
            "<span class=\"scratch-block scratch-block--control\">Boshqarish</span>"
            "<span class=\"scratch-block scratch-block--sensing\">Sezish</span>"
            "<span class=\"scratch-block scratch-block--operators\">Amallar</span>"
            "<span class=\"scratch-block scratch-block--variables\">O'zgaruvchi</span>"
            "</div>"
            "<h2>Tugma bosilganda</h2>"
            "<p><span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span> "
            "bloki — bu tugma bosilishi bilan ishga tushadi. Uning ostiga harakat "
            "blokini qo'yamiz:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--motion\">x ni 10 ga o'zgartir</span> — personajni o'ngga 10 piksel "
            "suradi. Chapga surish uchun <code>-10</code> yozamiz.</p>"
            "<h3>Boshqaruv qanday ishlaydi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"o'ng tugma bosilganda\"] --> B[\"x ni 10 ga o'zgartir\"]\n"
            "  B --> C[\"personaj o'ngga suriladi\"]\n"
            "  style A fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style B fill:#4C97FF,stroke:#1a4d99,color:#fff\n"
            "  style C fill:#c9cbd6,stroke:#8a8d9e,color:#2a2c3a\n"
            "</pre>"
        ),
        "text_content_ru": (
            "<h2>Что такое игра?</h2>"
            "<p>В игре мы <b>управляем</b> персонажем — например, двигаем его "
            "влево или вправо клавишами. В Scratch это делается блоками "
            "<b>События</b> (жёлтые) и <b>Движение</b> (синие).</p>"
            "<div class=\"scratch-legend\">"
            "<span class=\"scratch-block scratch-block--motion\">Движение</span>"
            "<span class=\"scratch-block scratch-block--looks\">Внешность</span>"
            "<span class=\"scratch-block scratch-block--sound\">Звук</span>"
            "<span class=\"scratch-block scratch-block--events\">События</span>"
            "<span class=\"scratch-block scratch-block--control\">Управление</span>"
            "<span class=\"scratch-block scratch-block--sensing\">Сенсоры</span>"
            "<span class=\"scratch-block scratch-block--operators\">Операторы</span>"
            "<span class=\"scratch-block scratch-block--variables\">Переменные</span>"
            "</div>"
            "<h2>Когда нажата клавиша</h2>"
            "<p>Блок <span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span> "
            "запускается при нажатии этой клавиши. Под ним ставим блок движения:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--motion\">x ni 10 ga o'zgartir</span> — сдвигает персонажа вправо на "
            "10 пикселей. Чтобы двигать влево, пишем <code>-10</code>.</p>"
            "<h3>Как работает управление</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"o'ng tugma bosilganda\"] --> B[\"x ni 10 ga o'zgartir\"]\n"
            "  B --> C[\"personaj o'ngga suriladi\"]\n"
            "  style A fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style B fill:#4C97FF,stroke:#1a4d99,color:#fff\n"
            "  style C fill:#c9cbd6,stroke:#8a8d9e,color:#2a2c3a\n"
            "</pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: O'ng va chapga harakat",
            "description": "Personaj o'ng va chap strelka tugmalari bilan harakatlanadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "boshqaruv.txt",
                    "language": "text",
                    "code": (
                        "o'ng strelka tugmasi bosilganda\n"
                        "x ni 10 ga o'zgartir\n"
                        "\n"
                        "chap strelka tugmasi bosilganda\n"
                        "x ni -10 ga o'zgartir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Qaysi blok tugmani kutadi?",
                "title_ru": "Какой блок ждёт клавишу?",
                "description": "Tugma bosilishini qaysi blok kutadi?",
                "description_ru": "Какой блок ждёт нажатия клавиши?",
                "exercise_type": "multiple_choice",
                "options": [
                    "... tugmasi bosilganda",
                    "10 qadam yur",
                    "Salom deb ayt",
                    "ovozini chal",
                ],
                "options_ru": [
                    "... tugmasi bosilganda",
                    "10 qadam yur",
                    "Salom deb ayt",
                    "ovozini chal",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "U Hodisa (sariq) guruhiga tegishli.",
                "hint_ru": "Он относится к группе События (жёлтые).",
                "explanation": "'... tugmasi bosilganda' bloki tugma bosilishini kutadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "O'ngga surish",
                "title_ru": "Сдвинуть вправо",
                "description": "Personajni o'ngga surish uchun x ni qanday o'zgartiramiz?",
                "description_ru": "Как изменить x, чтобы сдвинуть персонажа вправо?",
                "exercise_type": "multiple_choice",
                "options": ["x ni 10 ga o'zgartir", "x ni -10 ga o'zgartir", "y ni 10 ga o'zgartir", "o'lchamni oshir"],
                "options_ru": ["x ni 10 ga o'zgartir", "x ni -10 ga o'zgartir", "y ni 10 ga o'zgartir", "o'lchamni oshir"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "O'ng tomon — musbat son.",
                "hint_ru": "Вправо — положительное число.",
                "explanation": "Musbat x personajni o'ngga, manfiy x chapga suradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Chapga surish",
                "title_ru": "Сдвинуть влево",
                "description": "Chapga surish uchun bo'sh joyni to'ldiring: 'x ni ___ ga o'zgartir'",
                "description_ru": "Заполни пропуск для сдвига влево: 'x ni ___ ga o'zgartir'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "-10",
                "correct_answers_ru": "-10",
                "hint": "Chap tomon — manfiy son.",
                "hint_ru": "Влево — отрицательное число.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Boshqaruv skriptini tuzing",
                "title_ru": "Собери скрипт управления",
                "description": "Bloklarni to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь блоки в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["o'ng strelka tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "drag_items_ru": ["o'ng strelka tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "correct_order": ["o'ng strelka tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "hint": "Avval hodisa (tugma), keyin harakat.",
                "hint_ru": "Сначала событие (клавиша), потом движение.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Boshqariladigan personaj",
            "task_title_ru": "Проект: управляемый персонаж",
            "task_description": (
                "Scratch'da (scratch.mit.edu) o'ng va chap strelka tugmalari bilan "
                "harakatlanadigan personaj yarating. Tayyor bo'lgach, Share "
                "(Ulashish) tugmasi bilan ulashib, HAVOLASINI yoki ekran rasmini "
                "topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Создайте в Scratch (scratch.mit.edu) персонажа, который движется "
                "клавишами вправо и влево. Когда закончите, поделитесь проектом "
                "кнопкой Share (Поделиться) и отправьте ССЫЛКУ или скриншот — "
                "учитель проверит."
            ),
            "task_requirements": (
                "• O'ng strelka bosilganda personaj o'ngga yursin\n"
                "• Chap strelka bosilganda personaj chapga yursin\n"
                "• x ni o'zgartir bloki ishlatilsin"
            ),
            "task_requirements_ru": (
                "• По правой стрелке персонаж идёт вправо\n"
                "• По левой стрелке персонаж идёт влево\n"
                "• Использован блок изменения x"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Ball sanash (o'zgaruvchi)",
        "title_ru": "Считаем очки (переменная)",
        "points_reward": 20,
        "text_content": (
            "<h2>O'zgaruvchi nima?</h2>"
            "<p>O'yinda <b>ball</b>ni saqlab turish kerak. Buning uchun "
            "<b>o'zgaruvchi</b> yaratamiz — bu qiymatni eslab qoladigan quti. "
            "Scratch'da <b>O'zgaruvchilar</b> (to'q sariq-qizil) bo'limidan "
            "\"O'zgaruvchi yasash\" ni bosib, unga "
            "<span class=\"scratch-block scratch-block--variables\">ball</span> deb nom "
            "beramiz.</p>"
            "<h2>Ballni oshirish</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bo'sh joy tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 1 ga oshir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--variables\">ball ni 1 ga oshir</span> — har safar ball 1 taga ko'payadi. "
            "O'yin boshida ballni nolga qaytaramiz:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 0 ga o'rnat</span>"
            "</div>"
        ),
        "text_content_ru": (
            "<h2>Что такое переменная?</h2>"
            "<p>В игре нужно хранить <b>очки</b>. Для этого создаём "
            "<b>переменную</b> — коробочку, которая запоминает значение. В "
            "Scratch в разделе <b>Переменные</b> (оранжево-красные) нажимаем "
            "«Создать переменную» и называем её "
            "<span class=\"scratch-block scratch-block--variables\">ball</span>.</p>"
            "<h2>Увеличиваем очки</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bo'sh joy tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 1 ga oshir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--variables\">ball ni 1 ga oshir</span> — каждый раз очки растут на 1. В "
            "начале игры сбрасываем очки в ноль:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 0 ga o'rnat</span>"
            "</div>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Ball hisoblagich",
            "description": "Bo'sh joy tugmasi bosilganda ball bittaga oshadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "ball.txt",
                    "language": "text",
                    "code": (
                        "yashil bayroq bosilganda\n"
                        "ball ni 0 ga o'rnat\n"
                        "\n"
                        "bo'sh joy tugmasi bosilganda\n"
                        "ball ni 1 ga oshir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Ballni nima saqlaydi?",
                "title_ru": "Что хранит очки?",
                "description": "O'yinda ballni saqlab turish uchun nima yaratamiz?",
                "description_ru": "Что мы создаём, чтобы хранить очки в игре?",
                "exercise_type": "multiple_choice",
                "options": ["O'zgaruvchi", "Personaj", "Fon", "Ovoz"],
                "options_ru": ["Переменную", "Персонажа", "Фон", "Звук"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Qiymatni eslab qoladigan quti.",
                "hint_ru": "Коробочка, которая запоминает значение.",
                "explanation": "O'zgaruvchi — ball kabi qiymatlarni saqlaydigan quti.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ballni oshirish",
                "title_ru": "Увеличить очки",
                "description": "Ballni bittaga ko'paytirish uchun qaysi blok kerak?",
                "description_ru": "Какой блок увеличивает очки на один?",
                "exercise_type": "multiple_choice",
                "options": ["ball ni 1 ga oshir", "ball ni 0 ga o'rnat", "10 qadam yur", "Salom deb ayt"],
                "options_ru": ["ball ni 1 ga oshir", "ball ni 0 ga o'rnat", "10 qadam yur", "Salom deb ayt"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"oshir\" — ko'paytirish.",
                "hint_ru": "\"oshir\" — увеличить.",
                "explanation": "'ball ni 1 ga oshir' bloki ballni bittaga ko'paytiradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Boshlanishda ball",
                "title_ru": "Очки в начале",
                "description": "O'yin boshida ballni nechiga o'rnatamiz? Bo'sh joyni to'ldiring: 'ball ni ___ ga o'rnat'",
                "description_ru": "На сколько ставим очки в начале игры? Заполни пропуск: 'ball ni ___ ga o'rnat'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "0",
                "correct_answers_ru": "0",
                "hint": "Hali hech kim ball to'plamagan.",
                "hint_ru": "Ещё никто не набрал очков.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Ball skriptini tuzing",
                "title_ru": "Собери скрипт очков",
                "description": "O'yin boshlanganda ball nolga tushsin. Bloklarni tartibga qo'ying.",
                "description_ru": "В начале игры очки обнуляются. Расставь блоки.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["yashil bayroq bosilganda", "ball ni 0 ga o'rnat"],
                "drag_items_ru": ["yashil bayroq bosilganda", "ball ni 0 ga o'rnat"],
                "correct_order": ["yashil bayroq bosilganda", "ball ni 0 ga o'rnat"],
                "hint": "Avval boshlanadi, keyin ball nolga tushadi.",
                "hint_ru": "Сначала старт, потом обнуление очков.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Ball hisoblagich",
            "task_title_ru": "Проект: счётчик очков",
            "task_description": (
                "Scratch'da 'ball' o'zgaruvchisini yarating. Bo'sh joy tugmasi "
                "bosilganda ball bittaga oshsin, yashil bayroqda esa nolga tushsin. "
                "Share havolasini yoki ekran rasmini topshiring."
            ),
            "task_description_ru": (
                "Создайте в Scratch переменную 'ball'. По пробелу очки растут на "
                "один, а по зелёному флажку обнуляются. Отправьте ссылку Share "
                "или скриншот."
            ),
            "task_requirements": (
                "• 'ball' o'zgaruvchisi yaratilgan bo'lsin\n"
                "• Bo'sh joy bosilganda ball 1 ga oshsin\n"
                "• Yashil bayroqda ball 0 ga o'rnatilsin"
            ),
            "task_requirements_ru": (
                "• Создана переменная 'ball'\n"
                "• По пробелу очки растут на 1\n"
                "• По зелёному флажку очки становятся 0"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "To'qnashuvni aniqlash",
        "title_ru": "Определяем столкновение",
        "points_reward": 20,
        "text_content": (
            "<h2>Ikki personaj tegdimi?</h2>"
            "<p>O'yinda ko'pincha bir personaj ikkinchisiga <b>tegishi</b>ni "
            "bilishimiz kerak (masalan, mushuk olmani tutdimi?). Buning uchun "
            "<b>Sezish</b> (och ko'k) bo'limidagi "
            "<span class=\"scratch-block scratch-block--sensing\">... ga tegayapti?</span> "
            "blokidan foydalanamiz.</p>"
            "<h2>Agar ... bo'lsa</h2>"
            "<p>Tekshirishni <span class=\"scratch-block scratch-block--control\">agar &lt;...&gt; bo'lsa</span> "
            "bloki bilan qilamiz — u <b>Boshqarish</b> (to'q sariq) guruhida:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">agar &lt;Olma ga tegayapti?&gt; bo'lsa</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 1 ga oshir</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Ushladim! deb ayt</span>"
            "</div>"
            "<p>Agar personaj Olmaga tegsa, ball oshadi va \"Ushladim!\" deb "
            "aytadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Коснулись ли два персонажа?</h2>"
            "<p>В игре часто нужно знать, <b>коснулся</b> ли один персонаж "
            "другого (например, кот поймал яблоко?). Для этого используем блок "
            "<span class=\"scratch-block scratch-block--sensing\">... ga tegayapti?</span> из раздела <b>Сенсоры</b> "
            "(голубые).</p>"
            "<h2>Если ...</h2>"
            "<p>Проверку делаем блоком <span class=\"scratch-block scratch-block--control\">agar &lt;...&gt; bo'lsa</span> "
            "— он в группе <b>Управление</b> (оранжевый):</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">agar &lt;Olma ga tegayapti?&gt; bo'lsa</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">ball ni 1 ga oshir</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Ushladim! deb ayt</span>"
            "</div>"
            "<p>Если персонаж коснулся Яблока, очки растут и он говорит "
            "«Ushladim!».</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Olmani tutish",
            "description": "Personaj Olmaga tegsa, ball oshadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "toqnashuv.txt",
                    "language": "text",
                    "code": (
                        "agar <Olma ga tegayapti?> bo'lsa\n"
                        "  ball ni 1 ga oshir\n"
                        "  Ushladim! deb ayt\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Tegishni qaysi blok biladi?",
                "title_ru": "Какой блок узнаёт касание?",
                "description": "Bir personaj ikkinchisiga tegishini qaysi blok tekshiradi?",
                "description_ru": "Какой блок проверяет, коснулся ли один персонаж другого?",
                "exercise_type": "multiple_choice",
                "options": ["... ga tegayapti?", "10 qadam yur", "ball ni 1 ga oshir", "keyingi kostyum"],
                "options_ru": ["... ga tegayapti?", "10 qadam yur", "ball ni 1 ga oshir", "keyingi kostyum"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "U Sezish (och ko'k) guruhida.",
                "hint_ru": "Он в группе Сенсоры (голубые).",
                "explanation": "'... ga tegayapti?' bloki to'qnashuvni aniqlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Shart bloki",
                "title_ru": "Блок условия",
                "description": "Biror shart bajarilsagina ish qilish uchun qaysi blok kerak?",
                "description_ru": "Какой блок выполняет действие только при условии?",
                "exercise_type": "multiple_choice",
                "options": ["agar <...> bo'lsa", "doim takrorla", "10 qadam yur", "Salom deb ayt"],
                "options_ru": ["agar <...> bo'lsa", "doim takrorla", "10 qadam yur", "Salom deb ayt"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"agar\" — shart degani.",
                "hint_ru": "\"agar\" — значит условие (если).",
                "explanation": "'agar <...> bo'lsa' bloki shart to'g'ri bo'lgandagina ichidagini bajaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tekshirish so'zi",
                "title_ru": "Слово проверки",
                "description": "Shartni boshlaydigan so'zni yozing: '___ <Olma ga tegayapti?> bo'lsa'",
                "description_ru": "Напиши слово, начинающее условие: '___ <Olma ga tegayapti?> bo'lsa'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "agar",
                "correct_answers_ru": "agar",
                "hint": "O'zbekcha \"if\" so'zi.",
                "hint_ru": "Узбекское слово \"если\".",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Tutish skriptini tuzing",
                "title_ru": "Собери скрипт ловли",
                "description": "Olmaga tegsa ball oshsin. Bloklarni tartibga qo'ying.",
                "description_ru": "При касании яблока очки растут. Расставь блоки.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["agar <Olma ga tegayapti?> bo'lsa", "ball ni 1 ga oshir"],
                "drag_items_ru": ["agar <Olma ga tegayapti?> bo'lsa", "ball ni 1 ga oshir"],
                "correct_order": ["agar <Olma ga tegayapti?> bo'lsa", "ball ni 1 ga oshir"],
                "hint": "Avval shart, keyin uning ichidagi ish.",
                "hint_ru": "Сначала условие, потом действие внутри него.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Tegsa ball oshadi",
            "task_title_ru": "Проект: касание добавляет очки",
            "task_description": (
                "Ikkita personaj qo'ying (masalan Mushuk va Olma). Mushuk Olmaga "
                "tegsa, ball 1 ga oshsin. Share havolasini yoki ekran rasmini "
                "topshiring."
            ),
            "task_description_ru": (
                "Добавьте двух персонажей (например Кот и Яблоко). Когда Кот "
                "касается Яблока, очки растут на 1. Отправьте ссылку Share или "
                "скриншот."
            ),
            "task_requirements": (
                "• Kamida ikkita personaj bo'lsin\n"
                "• '... ga tegayapti?' bloki ishlatilsin\n"
                "• Tegilganda ball 1 ga oshsin"
            ),
            "task_requirements_ru": (
                "• Хотя бы два персонажа\n"
                "• Использован блок '... ga tegayapti?'\n"
                "• При касании очки растут на 1"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Tasodifiy harakat",
        "title_ru": "Случайное движение",
        "points_reward": 20,
        "text_content": (
            "<h2>Har safar boshqa joyda</h2>"
            "<p>Qiziqarli o'yinda olma har safar <b>boshqa joyda</b> paydo "
            "bo'lishi kerak. Buning uchun <b>Amallar</b> (yashil) bo'limidagi "
            "<span class=\"scratch-block scratch-block--operators\">1 dan 10 gacha tasodifiy son</span> "
            "blokidan foydalanamiz — u har safar tasodifiy son beradi.</p>"
            "<h2>Tasodifiy joyga o'tish</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--motion\">x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't</span>"
            "</div>"
            "<p>Bu blok (ko'k — <b>Harakat</b>) personajni yuqorida, chapdan o'ngga "
            "tasodifiy joyga qo'yadi; ichidagi tasodifiy son esa yashil <b>Amallar</b> "
            "blokidan keladi. Shunday qilib olma har safar boshqa ustundan tushadi.</p>"
        ),
        "text_content_ru": (
            "<h2>Каждый раз в новом месте</h2>"
            "<p>В интересной игре яблоко должно появляться <b>каждый раз в "
            "новом месте</b>. Для этого используем блок "
            "<span class=\"scratch-block scratch-block--operators\">1 dan 10 gacha tasodifiy son</span> "
            "из раздела <b>Операторы</b> (зелёные) — он каждый раз даёт случайное число.</p>"
            "<h2>Прыжок в случайное место</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--motion\">x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't</span>"
            "</div>"
            "<p>Этот блок (синий — <b>Движение</b>) ставит персонажа вверху в случайное место слева "
            "направо; случайное число внутри берётся из зелёного блока <b>Операторы</b>. Так яблоко "
            "каждый раз падает из нового столбца.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Tasodifiy joyga sakrash",
            "description": "Personaj tasodifiy x joyga o'tadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "tasodif.txt",
                    "language": "text",
                    "code": (
                        "yashil bayroq bosilganda\n"
                        "x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Tasodifiy son bloki",
                "title_ru": "Блок случайного числа",
                "description": "Har safar boshqa son olish uchun qaysi blok kerak?",
                "description_ru": "Какой блок даёт каждый раз другое число?",
                "exercise_type": "multiple_choice",
                "options": ["1 dan 10 gacha tasodifiy son", "10 qadam yur", "ball ni 1 ga oshir", "Salom deb ayt"],
                "options_ru": ["1 dan 10 gacha tasodifiy son", "10 qadam yur", "ball ni 1 ga oshir", "Salom deb ayt"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"tasodifiy\" — har safar boshqacha.",
                "hint_ru": "\"tasodifiy\" — каждый раз по-разному.",
                "explanation": "'... tasodifiy son' bloki tasodifiy (random) son beradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Nega tasodif kerak?",
                "title_ru": "Зачем нужна случайность?",
                "description": "O'yinda tasodifiy son nima uchun ishlatiladi?",
                "description_ru": "Для чего в игре используется случайное число?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Olma har safar boshqa joyda paydo bo'lsin",
                    "Ovoz balandroq bo'lsin",
                    "Personaj kattaroq bo'lsin",
                    "Fon o'zgarsin",
                ],
                "options_ru": [
                    "Чтобы яблоко появлялось каждый раз в новом месте",
                    "Чтобы звук был громче",
                    "Чтобы персонаж был больше",
                    "Чтобы менялся фон",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "O'yin har safar bir xil bo'lmasligi uchun.",
                "hint_ru": "Чтобы игра не была каждый раз одинаковой.",
                "explanation": "Tasodif o'yinni har safar yangicha va qiziqarli qiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yuqoriga qo'yish",
                "title_ru": "Поставить наверх",
                "description": "Olma yuqorida turishi uchun y qanday bo'lishi kerak (musbatmi)? Bo'sh joyni to'ldiring: 'y: ___ ga o't' (masalan 150)",
                "description_ru": "Каким должен быть y, чтобы яблоко было наверху? Заполни пропуск: 'y: ___ ga o't' (например 150)",
                "exercise_type": "fill_in_blank",
                "correct_answers": "150",
                "correct_answers_ru": "150",
                "hint": "Yuqori — katta musbat y.",
                "hint_ru": "Верх — большое положительное y.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Tasodifiy joy skriptini tuzing",
                "title_ru": "Собери скрипт случайного места",
                "description": "Bloklarni tartibga qo'ying: o'yin boshida olma tasodifiy joyga o'tsin.",
                "description_ru": "Расставь блоки: в начале игры яблоко переходит в случайное место.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["yashil bayroq bosilganda", "x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't"],
                "drag_items_ru": ["yashil bayroq bosilganda", "x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't"],
                "correct_order": ["yashil bayroq bosilganda", "x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't"],
                "hint": "Avval boshlanadi, keyin tasodifiy joyga o'tadi.",
                "hint_ru": "Сначала старт, потом переход в случайное место.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Tasodifiy paydo bo'ladigan olma",
            "task_title_ru": "Проект: яблоко в случайном месте",
            "task_description": (
                "Olma personaji yashil bayroq bosilganda ekranning yuqorisida "
                "tasodifiy joyga o'tsin. Share havolasini yoki ekran rasmini "
                "topshiring."
            ),
            "task_description_ru": (
                "Персонаж Яблоко по зелёному флажку переходит в случайное место "
                "вверху экрана. Отправьте ссылку Share или скриншот."
            ),
            "task_requirements": (
                "• Tasodifiy son bloki ishlatilsin\n"
                "• Olma yuqorida (musbat y) paydo bo'lsin\n"
                "• Har safar x joyi boshqacha bo'lsin"
            ),
            "task_requirements_ru": (
                "• Использован блок случайного числа\n"
                "• Яблоко появляется наверху (положительный y)\n"
                "• Каждый раз позиция x другая"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Doimiy takrorlash (sikl)",
        "title_ru": "Бесконечное повторение (цикл)",
        "points_reward": 20,
        "text_content": (
            "<h2>Olma pastga tushadi</h2>"
            "<p>Olma to'xtovsiz pastga tushib turishi kerak. Buning uchun "
            "<b>Boshqarish</b> (to'q sariq) bo'limidagi "
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span> "
            "blokidan foydalanamiz — u ichidagi bloklarni cheksiz qayta-qayta "
            "bajaradi.</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--motion\">y ni -5 ga o'zgartir</span> — personajni biroz pastga "
            "suradi. <span class=\"scratch-block scratch-block--control\">doim takrorla</span> ichida bo'lgani uchun olma "
            "sekin-sekin pastga tushaveradi.</p>"
            "<h3>Sikl qanday ishlaydi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"doim takrorla\"] --> B[\"y ni -5 ga o'zgartir\"]\n"
            "  B --> A\n"
            "  style A fill:#E8820A,stroke:#7a3d02,color:#fff\n"
            "  style B fill:#4C97FF,stroke:#1a4d99,color:#fff\n"
            "</pre>"
        ),
        "text_content_ru": (
            "<h2>Яблоко падает вниз</h2>"
            "<p>Яблоко должно постоянно падать вниз. Для этого используем блок "
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span> из раздела <b>Управление</b> "
            "(оранжевые) — он повторяет блоки внутри себя бесконечно.</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "</div>"
            "<p><span class=\"scratch-block scratch-block--motion\">y ni -5 ga o'zgartir</span> — сдвигает персонажа чуть "
            "вниз. Так как это внутри <span class=\"scratch-block scratch-block--control\">doim takrorla</span>, яблоко "
            "медленно падает вниз.</p>"
            "<h3>Как работает цикл</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"doim takrorla\"] --> B[\"y ni -5 ga o'zgartir\"]\n"
            "  B --> A\n"
            "  style A fill:#E8820A,stroke:#7a3d02,color:#fff\n"
            "  style B fill:#4C97FF,stroke:#1a4d99,color:#fff\n"
            "</pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Pastga tushayotgan olma",
            "description": "Olma doimiy ravishda pastga tushadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "tushish.txt",
                    "language": "text",
                    "code": (
                        "yashil bayroq bosilganda\n"
                        "doim takrorla\n"
                        "  y ni -5 ga o'zgartir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Cheksiz takrorlash",
                "title_ru": "Бесконечное повторение",
                "description": "Bloklarni to'xtovsiz qayta-qayta bajarish uchun qaysi blok kerak?",
                "description_ru": "Какой блок повторяет блоки без остановки?",
                "exercise_type": "multiple_choice",
                "options": ["doim takrorla", "agar <...> bo'lsa", "10 qadam yur", "Salom deb ayt"],
                "options_ru": ["doim takrorla", "agar <...> bo'lsa", "10 qadam yur", "Salom deb ayt"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"doim\" — har doim, to'xtovsiz.",
                "hint_ru": "\"doim\" — всегда, без остановки.",
                "explanation": "'doim takrorla' bloki ichidagini cheksiz qayta bajaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Pastga tushirish",
                "title_ru": "Двигать вниз",
                "description": "Olmani pastga tushirish uchun y ni qanday o'zgartiramiz?",
                "description_ru": "Как изменить y, чтобы яблоко падало вниз?",
                "exercise_type": "multiple_choice",
                "options": ["y ni -5 ga o'zgartir", "y ni 5 ga o'zgartir", "x ni 5 ga o'zgartir", "o'lchamni oshir"],
                "options_ru": ["y ni -5 ga o'zgartir", "y ni 5 ga o'zgartir", "x ni 5 ga o'zgartir", "o'lchamni oshir"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Past tomon — manfiy y.",
                "hint_ru": "Вниз — отрицательный y.",
                "explanation": "Manfiy y personajni pastga, musbat y yuqoriga suradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Takrorlash so'zi",
                "title_ru": "Слово повторения",
                "description": "Cheksiz takrorlash blokini yozing: '___ takrorla'",
                "description_ru": "Напиши блок бесконечного повторения: '___ takrorla'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "doim",
                "correct_answers_ru": "doim",
                "hint": "\"har doim\" so'zining birinchi qismi.",
                "hint_ru": "Первая часть слова \"всегда\".",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Tushish skriptini tuzing",
                "title_ru": "Собери скрипт падения",
                "description": "Bloklarni tartibga qo'ying: olma doimiy pastga tushsin.",
                "description_ru": "Расставь блоки: яблоко постоянно падает вниз.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["yashil bayroq bosilganda", "doim takrorla", "y ni -5 ga o'zgartir"],
                "drag_items_ru": ["yashil bayroq bosilganda", "doim takrorla", "y ni -5 ga o'zgartir"],
                "correct_order": ["yashil bayroq bosilganda", "doim takrorla", "y ni -5 ga o'zgartir"],
                "hint": "Boshlanadi, keyin sikl, sikl ichida harakat.",
                "hint_ru": "Старт, потом цикл, внутри цикла движение.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Tushayotgan olma",
            "task_title_ru": "Проект: падающее яблоко",
            "task_description": (
                "Olma yashil bayroq bosilganda doimiy ravishda pastga tushsin "
                "(doim takrorla ichida y ni kamaytiring). Share havolasini yoki "
                "ekran rasmini topshiring."
            ),
            "task_description_ru": (
                "Яблоко по зелёному флажку постоянно падает вниз (внутри doim "
                "takrorla уменьшайте y). Отправьте ссылку Share или скриншот."
            ),
            "task_requirements": (
                "• 'doim takrorla' bloki ishlatilsin\n"
                "• Uning ichida y kamaytirilsin (manfiy)\n"
                "• Olma silliq pastga tushsin"
            ),
            "task_requirements_ru": (
                "• Использован блок 'doim takrorla'\n"
                "• Внутри уменьшается y (отрицательное)\n"
                "• Яблоко плавно падает вниз"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy o'yin: Olma tut",
        "title_ru": "Итоговая игра: Поймай яблоко",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi biz o'rgangan hamma narsani bitta o'yinga birlashtiramiz — "
            "<b>Olma tut</b>! Savat (yoki mushuk) tugmalar bilan harakatlanadi, "
            "olma yuqoridan tushadi. Savat olmani tutsa — ball oshadi va olma "
            "yana tasodifiy joydan tushadi.</p>"
            "<h3>O'yin qismlari</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Savatni tugmalar bilan boshqarish\"] --> B[\"Olma doim pastga tushadi\"]\n"
            "  B --> C[\"Agar savatga tegsa: ball +1\"]\n"
            "  C --> D[\"Olma tasodifiy joydan qayta tushadi\"]\n"
            "</pre>"
            "<h2>Savat skripti</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<h2>Olma skripti</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested\">agar &lt;Savat ga tegayapti?&gt; bo'lsa</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested2\">ball ni 1 ga oshir</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested2\">x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't</span>"
            "</div>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим всё выученное в одну игру — <b>Поймай "
            "яблоко</b>! Корзина (или кот) двигается клавишами, яблоко падает "
            "сверху. Если корзина поймала яблоко — очки растут, и яблоко снова "
            "падает из случайного места.</p>"
            "<h3>Части игры</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Savatni tugmalar bilan boshqarish\"] --> B[\"Olma doim pastga tushadi\"]\n"
            "  B --> C[\"Agar savatga tegsa: ball +1\"]\n"
            "  C --> D[\"Olma tasodifiy joydan qayta tushadi\"]\n"
            "</pre>"
            "<h2>Скрипт корзины</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<h2>Скрипт яблока</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">doim takrorla</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested\">agar &lt;Savat ga tegayapti?&gt; bo'lsa</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested2\">ball ni 1 ga oshir</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested2\">x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't</span>"
            "</div>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Olma tut o'yini",
            "description": "Savatni boshqaramiz, olma tushadi, tutsa ball oshadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "olma_tut.txt",
                    "language": "text",
                    "code": (
                        "# Savat personaji:\n"
                        "o'ng strelka tugmasi bosilganda\n"
                        "x ni 10 ga o'zgartir\n"
                        "chap strelka tugmasi bosilganda\n"
                        "x ni -10 ga o'zgartir\n"
                        "\n"
                        "# Olma personaji:\n"
                        "yashil bayroq bosilganda\n"
                        "ball ni 0 ga o'rnat\n"
                        "doim takrorla\n"
                        "  y ni -5 ga o'zgartir\n"
                        "  agar <Savat ga tegayapti?> bo'lsa\n"
                        "    ball ni 1 ga oshir\n"
                        "    x: (-200 dan 200 gacha tasodifiy son) y: 150 ga o't\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "O'yin qismlari",
                "title_ru": "Части игры",
                "description": "\"Olma tut\" o'yinida savat nima qiladi?",
                "description_ru": "Что делает корзина в игре \"Поймай яблоко\"?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Tugmalar bilan harakatlanib olmani tutadi",
                    "Yuqoridan pastga tushadi",
                    "Ovoz chiqaradi",
                    "Rangini o'zgartiradi",
                ],
                "options_ru": [
                    "Двигается клавишами и ловит яблоко",
                    "Падает сверху вниз",
                    "Издаёт звук",
                    "Меняет цвет",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Savatni o'yinchi boshqaradi.",
                "hint_ru": "Корзиной управляет игрок.",
                "explanation": "Savat tugmalar bilan harakatlanib, tushayotgan olmani tutadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tutgandan keyin",
                "title_ru": "После поимки",
                "description": "Savat olmani tutgach, olma nima qiladi?",
                "description_ru": "Что делает яблоко после того, как корзина его поймала?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Yana tasodifiy joydan tushadi",
                    "Butunlay yo'qoladi",
                    "Kattalashadi",
                    "To'xtaydi",
                ],
                "options_ru": [
                    "Снова падает из случайного места",
                    "Совсем исчезает",
                    "Увеличивается",
                    "Останавливается",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "O'yin davom etishi kerak.",
                "hint_ru": "Игра должна продолжаться.",
                "explanation": "Tutilgach olma tasodifiy joyga o'tib, qaytadan tushadi — o'yin davom etadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ball qachon oshadi?",
                "title_ru": "Когда растут очки?",
                "description": "Olma savatga ___ ball 1 ga oshadi. Bo'sh joyni to'ldiring (bir so'z).",
                "description_ru": "Яблоко ___ корзины — очки растут на 1. Заполни пропуск (одно слово).",
                "exercise_type": "fill_in_blank",
                "correct_answers": "tegsa",
                "correct_answers_ru": "tegsa",
                "hint": "To'qnashuv haqidagi darsni eslang: '... ga tegsa'.",
                "hint_ru": "Вспомни урок про столкновение: '... ga tegsa'.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "O'yin mantiqini tartibla",
                "title_ru": "Расставь логику игры",
                "description": "Olma skriptidagi bloklarni to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь блоки скрипта яблока в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": [
                    "doim takrorla",
                    "y ni -5 ga o'zgartir",
                    "agar <Savat ga tegayapti?> bo'lsa",
                    "ball ni 1 ga oshir",
                ],
                "drag_items_ru": [
                    "doim takrorla",
                    "y ni -5 ga o'zgartir",
                    "agar <Savat ga tegayapti?> bo'lsa",
                    "ball ni 1 ga oshir",
                ],
                "correct_order": [
                    "doim takrorla",
                    "y ni -5 ga o'zgartir",
                    "agar <Savat ga tegayapti?> bo'lsa",
                    "ball ni 1 ga oshir",
                ],
                "hint": "Sikl → tushish → shart → ball.",
                "hint_ru": "Цикл → падение → условие → очки.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: \"Olma tut\" o'yini",
            "task_title_ru": "Итоговый проект: игра \"Поймай яблоко\"",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtirib, to'liq \"Olma tut\" "
                "o'yinini yarating: savat tugmalar bilan harakatlansin, olma "
                "yuqoridan tushsin, savat tutsa ball oshsin va olma tasodifiy "
                "joydan qayta tushsin. Share havolasini yoki ekran rasmini "
                "topshiring — bu sizning eng katta o'yiningiz!"
            ),
            "task_description_ru": (
                "Объедини всё выученное в полную игру \"Поймай яблоко\": корзина "
                "движется клавишами, яблоко падает сверху, при поимке очки "
                "растут и яблоко снова падает из случайного места. Отправь ссылку "
                "Share или скриншот — это твоя самая большая игра!"
            ),
            "task_requirements": (
                "• Savat o'ng/chap tugmalar bilan harakatlansin\n"
                "• Olma 'doim takrorla' ichida pastga tushsin\n"
                "• Savatga tegsa 'ball ni 1 ga oshir' ishlasin\n"
                "• Tutilgach olma tasodifiy joyga o'tsin"
            ),
            "task_requirements_ru": (
                "• Корзина движется правой/левой клавишами\n"
                "• Яблоко падает внутри 'doim takrorla'\n"
                "• При касании корзины работает 'ball ni 1 ga oshir'\n"
                "• После поимки яблоко переходит в случайное место"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 5,
        },
    },
]
