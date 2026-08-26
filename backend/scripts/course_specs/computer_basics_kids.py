""""How computers work" (unplugged CS concepts) course for children aged
7-12 (Uzbek-primary, Russian translations).

Not a coding course — the platform's second non-programming kids course
(alongside digital_safety_kids.py). Standalone (no prerequisite). Covers
what a computer actually is (input/process/output), binary numbers, what an
algorithm is (taught screen-free via a card-sorting example, in the
tradition of the well-known "CS Unplugged" curriculum), a simplified model
of how the internet moves a request from a device to a server and back, and
CPU vs RAM vs storage.

Same non-code task shape as digital_safety_kids.py — every task asks for a
WRITTEN or DRAWN deliverable, task_technologies is "Yozma javob" ("Written
response") instead of a programming language. Every `sample` shows a worked
example/analogy as sample_type "code" with language "text" (matching the
Scratch courses' convention for non-executable illustrative content).

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "Kompyuter qanday ishlaydi (bolalar uchun)",
    "title_ru": "Как работает компьютер (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun kompyuter va internet qanday "
        "ishlashini o'rgatuvchi kurs. Ikkilik sanoq tizimini, algoritm "
        "nimaligini, internet qanday ishlashini va kompyuterning asosiy "
        "qismlarini (protsessor, xotira) o'rganamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет о том, как устроены компьютер и интернет. "
        "Научимся понимать двоичную систему счисления, что такое алгоритм, "
        "как работает интернет и из чего состоит компьютер (процессор, "
        "память)."
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
        "title": "Kompyuter nima?",
        "title_ru": "Что такое компьютер?",
        "points_reward": 15,
        "text_content": (
            "<h2>Kompyuter — bu nima?</h2>"
            "<p><b>Kompyuter</b> — ma'lumotni qabul qiladigan, qayta "
            "ishlaydigan va natija chiqaradigan qurilma. Telefon, noutbuk, "
            "smart-soat, hatto o'yin konsoli ham — hammasi kompyuter!</p>"
            "<h2>Uch qadam: Kirish → Qayta ishlash → Chiqish</h2>"
            "<p>Har qanday kompyuter uchta ishni qiladi:</p><ul>"
            "<li><b>Kirish (Input)</b> — ma'lumot qabul qilish (klaviatura, "
            "sichqoncha, mikrofon)</li>"
            "<li><b>Qayta ishlash (Process)</b> — ma'lumotni tahlil qilish "
            "(protsessor)</li>"
            "<li><b>Chiqish (Output)</b> — natijani ko'rsatish (ekran, "
            "karnay)</li></ul>"
            "<h3>Misol: Siz sichqonchani bossangiz</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Kirish: sichqoncha bosiladi\"] --> B[\"Qayta ishlash: protsessor buyruqni tushunadi\"]\n"
            "  B --> C[\"Chiqish: ekranda tugma bosilgani ko'rinadi\"]\n"
            "</pre>"
        ),
        "text_content_ru": (
            "<h2>Что такое компьютер?</h2>"
            "<p><b>Компьютер</b> — устройство, которое принимает "
            "информацию, обрабатывает её и выдаёт результат. Телефон, "
            "ноутбук, смарт-часы, даже игровая приставка — всё это "
            "компьютеры!</p>"
            "<h2>Три шага: Ввод → Обработка → Вывод</h2>"
            "<p>Любой компьютер делает три вещи:</p><ul>"
            "<li><b>Ввод (Input)</b> — приём информации (клавиатура, мышь, "
            "микрофон)</li>"
            "<li><b>Обработка (Process)</b> — анализ информации "
            "(процессор)</li>"
            "<li><b>Вывод (Output)</b> — показ результата (экран, "
            "динамик)</li></ul>"
            "<h3>Пример: вы нажали мышью</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Kirish: sichqoncha bosiladi\"] --> B[\"Qayta ishlash: protsessor buyruqni tushunadi\"]\n"
            "  B --> C[\"Chiqish: ekranda tugma bosilgani ko'rinadi\"]\n"
            "</pre>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Kundalik kompyuterlar",
            "description": "Uy-ro'zg'or qurilmalarining kirish va chiqishi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "qurilmalar.txt",
                    "language": "text",
                    "code": (
                        "TELEFON:\n"
                        "  Kirish — ekranga tegish\n"
                        "  Chiqish — rasm/ovoz\n"
                        "\n"
                        "SMART SOAT:\n"
                        "  Kirish — tugma bosish\n"
                        "  Chiqish — vaqtni ko'rsatish\n"
                        "\n"
                        "MIKROTO'LQINLI PECH:\n"
                        "  Kirish — vaqt tugmalari bosiladi\n"
                        "  Chiqish — signal ovozi va isitilgan ovqat\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Uchta asosiy ish",
                "title_ru": "Три основных действия",
                "description": "Kompyuter uchta ishni qiladi. Ular qaysilar?",
                "description_ru": "Компьютер делает три вещи. Какие именно?",
                "exercise_type": "multiple_choice",
                "options": ["Kirish, qayta ishlash, chiqish", "Faqat o'ynash", "Faqat rasm chizish", "Faqat internetga kirish"],
                "options_ru": ["Ввод, обработка, вывод", "Только играть", "Только рисовать", "Только выходить в интернет"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsning eng muhim uchta so'zi.",
                "hint_ru": "Три главных слова урока.",
                "explanation": "Har qanday kompyuter kirish, qayta ishlash va chiqish bilan ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bu ham kompyuter",
                "title_ru": "Это тоже компьютер",
                "description": "Quyidagilardan qaysi biri ham kompyuter?",
                "description_ru": "Что из этого тоже компьютер?",
                "exercise_type": "multiple_choice",
                "options": ["Smart soat", "Qalam", "Kitob", "Stul"],
                "options_ru": ["Смарт-часы", "Карандаш", "Книга", "Стул"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ma'lumot qabul qilib, natija chiqaradigan narsa.",
                "hint_ru": "То, что принимает информацию и выдаёт результат.",
                "explanation": "Smart soat ham kirish, qayta ishlash va chiqishga ega — demak kompyuter.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Ma'lumot qabul qilish bosqichi",
                "title_ru": "Этап приёма информации",
                "description": "Ma'lumotni qabul qilish bosqichi qanday ataladi? Javob: ___",
                "description_ru": "Как называется этап приёма информации? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "kirish",
                "correct_answers_ru": "ввод",
                "hint": "Ingliz tilida \"input\".",
                "hint_ru": "По-английски «input».",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Uch qadamni tartibga soling",
                "title_ru": "Расставь три шага",
                "description": "Bloklarni to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь блоки в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Kirish", "Qayta ishlash", "Chiqish"],
                "drag_items_ru": ["Ввод", "Обработка", "Вывод"],
                "correct_order": ["Kirish", "Qayta ishlash", "Chiqish"],
                "hint": "Avval ma'lumot keladi, keyin ishlanadi, keyin natija chiqadi.",
                "hint_ru": "Сначала данные приходят, потом обрабатываются, потом выходит результат.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Uyimdagi kompyuterlar",
            "task_title_ru": "Проект: компьютеры в моём доме",
            "task_description": (
                "Uyingizda kompyuter hisoblanadigan 3 ta qurilmani toping "
                "(telefon, mikroto'lqinli pech, smart-teplevizor va h.k.) va "
                "har biri uchun kirish va chiqishini yozing. Matningizni "
                "topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Найди дома 3 устройства, которые являются компьютерами "
                "(телефон, микроволновка, смарт-телевизор и т.д.) и напиши "
                "для каждого его ввод и вывод. Отправь текст — учитель "
                "проверит."
            ),
            "task_requirements": (
                "• Kamida 3 ta qurilma tanlansin\n"
                "• Har biri uchun kirish (input) yozilsin\n"
                "• Har biri uchun chiqish (output) yozilsin"
            ),
            "task_requirements_ru": (
                "• Выбраны минимум 3 устройства\n"
                "• Для каждого написан ввод\n"
                "• Для каждого написан вывод"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Ikkilik sanoq tizimi (Binary)",
        "title_ru": "Двоичная система счисления (Binary)",
        "points_reward": 20,
        "text_content": (
            "<h2>Kompyuter faqat ikkita sonni biladi</h2>"
            "<p>Biz kundalik hayotda 0 dan 9 gacha sonlardan foydalanamiz. "
            "Lekin kompyuter ichida hamma narsa faqat <b>0</b> va <b>1</b> "
            "bilan yoziladi — bu <b>ikkilik (binary)</b> tizim.</p>"
            "<h2>Nega faqat 0 va 1?</h2>"
            "<p>Kompyuter ichida millionlab kichik <b>elektr kalitlari</b> "
            "bor — ular yo <b>yoniq (1)</b>, yo <b>o'chiq (0)</b>. Boshqa "
            "holat yo'q!</p>"
            "<h2>Kichik son qanday yoziladi</h2><ul>"
            "<li>0 = 0</li><li>1 = 1</li><li>2 = 10</li><li>3 = 11</li>"
            "<li>4 = 100</li><li>5 = 101</li></ul>"
            "<p>Har bir raqam joyi 2 ga karrali qiymatni bildiradi (1, 2, 4, "
            "8...).</p>"
        ),
        "text_content_ru": (
            "<h2>Компьютер знает только два числа</h2>"
            "<p>В обычной жизни мы используем числа от 0 до 9. Но внутри "
            "компьютера всё записывается только через <b>0</b> и <b>1</b> — "
            "это <b>двоичная (binary)</b> система.</p>"
            "<h2>Почему только 0 и 1?</h2>"
            "<p>Внутри компьютера миллионы маленьких <b>электрических "
            "переключателей</b> — они либо <b>включены (1)</b>, либо "
            "<b>выключены (0)</b>. Другого состояния нет!</p>"
            "<h2>Как пишутся маленькие числа</h2><ul>"
            "<li>0 = 0</li><li>1 = 1</li><li>2 = 10</li><li>3 = 11</li>"
            "<li>4 = 100</li><li>5 = 101</li></ul>"
            "<p>Каждая позиция цифры означает значение, кратное 2 (1, 2, 4, "
            "8...).</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Lampochkalar bilan son ko'rsatish",
            "description": "3 ta lampochka (o'chiq/yoniq) bilan sonlarni yozamiz.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "lampochkalar.txt",
                    "language": "text",
                    "code": (
                        "O'CHIQ O'CHIQ YONIQ = 001 = 1\n"
                        "O'CHIQ YONIQ O'CHIQ = 010 = 2\n"
                        "O'CHIQ YONIQ YONIQ  = 011 = 3\n"
                        "YONIQ O'CHIQ O'CHIQ = 100 = 4\n"
                        "YONIQ O'CHIQ YONIQ  = 101 = 5\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Ikkita raqam",
                "title_ru": "Две цифры",
                "description": "Kompyuter ichida sonlar qaysi ikkita raqam bilan yoziladi?",
                "description_ru": "Какими двумя цифрами записываются числа внутри компьютера?",
                "exercise_type": "multiple_choice",
                "options": ["0 va 1", "2 va 3", "5 va 10", "O'nlik sonlar"],
                "options_ru": ["0 и 1", "2 и 3", "5 и 10", "Десятичные числа"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Elektr kaliti yoki yoniq, yoki o'chiq.",
                "hint_ru": "Переключатель либо включён, либо выключен.",
                "explanation": "Ikkilik tizimda faqat 0 va 1 ishlatiladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "3 sonini yozish",
                "title_ru": "Запись числа 3",
                "description": "Ikkilik tizimda 3 soni qanday yoziladi?",
                "description_ru": "Как записывается число 3 в двоичной системе?",
                "exercise_type": "multiple_choice",
                "options": ["11", "3", "111", "10"],
                "options_ru": ["11", "3", "111", "10"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Darsdagi ro'yxatga qarang.",
                "hint_ru": "Посмотри на список из урока.",
                "explanation": "3 = 11 ikkilik tizimda (2 + 1).",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Elektr kaliti holatlari",
                "title_ru": "Состояния переключателя",
                "description": "Kompyuter ichidagi kichik elektr kaliti necha holatga ega bo'lishi mumkin? Javob: ___",
                "description_ru": "Сколько состояний может быть у маленького переключателя внутри компьютера? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "2",
                "hint": "Yoniq yoki o'chiq — jami nechta?",
                "hint_ru": "Включён или выключен — сколько всего?",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Ikkilik sanoqni tartibga soling",
                "title_ru": "Расставь двоичный счёт",
                "description": "0 dan 3 gachagi sonlarni ikkilik tizimda o'sish tartibida joylashtiring.",
                "description_ru": "Расставь числа от 0 до 3 в двоичной системе по возрастанию.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["0", "1", "10", "11"],
                "drag_items_ru": ["0", "1", "10", "11"],
                "correct_order": ["0", "1", "10", "11"],
                "hint": "0, 1, 2, 3 ning ikkilik ko'rinishlari.",
                "hint_ru": "Двоичные записи чисел 0, 1, 2, 3.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Sonlarni ikkilikka aylantiring",
            "task_title_ru": "Проект: переведи числа в двоичную систему",
            "task_description": (
                "0 dan 5 gacha bo'lgan sonlarni ikkilik tizimda yozing va "
                "kamida bitta songa (masalan 5 = 101) nega shunday "
                "yozilishini qisqacha tushuntiring. Matningizni topshiring "
                "— o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Запиши числа от 0 до 5 в двоичной системе и объясни для "
                "хотя бы одного числа (например 5 = 101), почему оно так "
                "записывается. Отправь текст — учитель проверит."
            ),
            "task_requirements": (
                "• 0 dan 5 gacha har bir sonning ikkilik ko'rinishi "
                "yozilsin\n"
                "• Kamida bitta songa qisqacha tushuntirish berilsin\n"
                "• Javob tushunarli yozilsin"
            ),
            "task_requirements_ru": (
                "• Записан двоичный вид чисел от 0 до 5\n"
                "• Дано краткое объяснение хотя бы для одного числа\n"
                "• Ответ написан понятно"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Algoritm nima?",
        "title_ru": "Что такое алгоритм?",
        "points_reward": 20,
        "text_content": (
            "<h2>Algoritm — qadam-baqadam retsept</h2>"
            "<p><b>Algoritm</b> — biror ishni bajarish uchun aniq, tartibli "
            "qadamlar ro'yxati. Choy tayyorlash ham, dasturlash ham — "
            "hammasi algoritm.</p>"
            "<h2>Kompyutersiz algoritm: Kartalarni saralash</h2>"
            "<p>4 ta raqamli kartani kichikdan kattaga saralaymiz deylik: 5, "
            "2, 8, 1. Bir usul — <b>qo'shni ikkitasini solishtirish</b>:</p>"
            "<ol>"
            "<li>5 va 2ni solishtir: 5&gt;2, joylarini almashtir → 2,5,8,1</li>"
            "<li>5 va 8ni solishtir: to'g'ri joyda, qoldir → 2,5,8,1</li>"
            "<li>8 va 1ni solishtir: 8&gt;1, joylarini almashtir → 2,5,1,8</li>"
            "<li>Hammasi tartibligacha takrorla → 2,1,5,8 → 1,2,5,8</li></ol>"
            "<p>Bu — <b>saralash algoritmi</b>, dasturchilar buni \"bubble "
            "sort\" (pufakchali saralash) deb ataydi.</p>"
        ),
        "text_content_ru": (
            "<h2>Алгоритм — пошаговый рецепт</h2>"
            "<p><b>Алгоритм</b> — точный, упорядоченный список шагов для "
            "выполнения задачи. Заваривание чая и программирование — оба "
            "являются алгоритмом.</p>"
            "<h2>Алгоритм без компьютера: сортировка карточек</h2>"
            "<p>Допустим, сортируем 4 карточки с числами от меньшего к "
            "большему: 5, 2, 8, 1. Один способ — <b>сравнивать соседние "
            "две</b>:</p>"
            "<ol>"
            "<li>Сравни 5 и 2: 5&gt;2, поменяй местами → 2,5,8,1</li>"
            "<li>Сравни 5 и 8: на своём месте, оставь → 2,5,8,1</li>"
            "<li>Сравни 8 и 1: 8&gt;1, поменяй местами → 2,5,1,8</li>"
            "<li>Повторяй, пока всё не отсортировано → 2,1,5,8 → 1,2,5,8</li></ol>"
            "<p>Это — <b>алгоритм сортировки</b>, программисты называют его "
            "«пузырьковая сортировка» (bubble sort).</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Saralash qadamlari",
            "description": "5, 2, 8, 1 kartalarini to'liq saralash jarayoni.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "saralash.txt",
                    "language": "text",
                    "code": (
                        "Boshlang'ich: 5, 2, 8, 1\n"
                        "\n"
                        "1-o'tish: 5 va 2 -> almashtir -> 2, 5, 8, 1\n"
                        "          5 va 8 -> qoldir    -> 2, 5, 8, 1\n"
                        "          8 va 1 -> almashtir -> 2, 5, 1, 8\n"
                        "\n"
                        "2-o'tish: 5 va 1 -> almashtir -> 2, 1, 5, 8\n"
                        "          2 va 1 -> almashtir -> 1, 2, 5, 8\n"
                        "\n"
                        "Natija: 1, 2, 5, 8 (tartiblangan!)\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Algoritm ta'rifi",
                "title_ru": "Определение алгоритма",
                "description": "Algoritm nima?",
                "description_ru": "Что такое алгоритм?",
                "exercise_type": "multiple_choice",
                "options": ["Qadam-baqadam ish tartibi", "Faqat kompyuter dasturi", "Rasm", "O'yin"],
                "options_ru": ["Пошаговый порядок действий", "Только компьютерная программа", "Картинка", "Игра"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Choy tayyorlash ham algoritm.",
                "hint_ru": "Заваривание чая — тоже алгоритм.",
                "explanation": "Algoritm — biror ishni bajarish uchun tartibli qadamlar ro'yxati.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kartalarni saralash usuli",
                "title_ru": "Способ сортировки карточек",
                "description": "Kartalarni saralashda nima qilinadi?",
                "description_ru": "Что делают при сортировке карточек?",
                "exercise_type": "multiple_choice",
                "options": ["Qo'shnilarni solishtirib, kerak bo'lsa almashtiriladi", "Kartalar tashlanadi", "Kartalar yashiriladi", "Hech narsa qilinmaydi"],
                "options_ru": ["Сравнивают соседей и меняют местами при нужде", "Карточки выбрасывают", "Карточки прячут", "Ничего не делают"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ikkitasini solishtirib, kattasi keyinga o'tadi.",
                "hint_ru": "Сравнивают две и большая переходит дальше.",
                "explanation": "Qo'shni ikkitasini solishtirib, kerak bo'lsa joylarini almashtirish — bubble sort mantig'i.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Kundalik algoritm",
                "title_ru": "Повседневный алгоритм",
                "description": "Choy tayyorlash ham bir turdagi ___.",
                "description_ru": "Заваривание чая — тоже вид ___.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "algoritm",
                "correct_answers_ru": "алгоритм",
                "hint": "Darsning bosh mavzusi.",
                "hint_ru": "Главная тема урока.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Saralash qadamlarini tartibga soling",
                "title_ru": "Расставь шаги сортировки",
                "description": "5, 2 kartalarini solishtirish qadamlarini tartibga qo'ying.",
                "description_ru": "Расставь шаги сравнения карточек 5 и 2.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["5 va 2ni solishtir", "5>2 ekanini ko'r", "Joylarini almashtir", "2, 5 natijasini ol"],
                "drag_items_ru": ["Сравни 5 и 2", "Увидь что 5>2", "Поменяй местами", "Получи результат 2, 5"],
                "correct_order": ["5 va 2ni solishtir", "5>2 ekanini ko'r", "Joylarini almashtir", "2, 5 natijasini ol"],
                "hint": "Avval solishtirish, keyin qaror, keyin harakat, keyin natija.",
                "hint_ru": "Сначала сравнение, потом решение, потом действие, потом результат.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: O'z algoritmingiz",
            "task_title_ru": "Проект: свой алгоритм",
            "task_description": (
                "Kundalik ishlaringizdan birini (masalan sendvich tayyorlash "
                "yoki tishlarni yuvish) qadam-baqadam algoritm sifatida "
                "yozing. Matningizni topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Опиши одно из своих повседневных дел (например "
                "приготовление бутерброда или чистка зубов) как пошаговый "
                "алгоритм. Отправь текст — учитель проверит."
            ),
            "task_requirements": (
                "• Kamida 5 ta qadam yozilsin\n"
                "• Qadamlar to'g'ri tartibda bo'lsin\n"
                "• Har bir qadam aniq va tushunarli bo'lsin"
            ),
            "task_requirements_ru": (
                "• Минимум 5 шагов\n"
                "• Шаги в правильном порядке\n"
                "• Каждый шаг чёткий и понятный"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Internet qanday ishlaydi",
        "title_ru": "Как работает интернет",
        "points_reward": 20,
        "text_content": (
            "<h2>Veb-sahifa qayerdan keladi?</h2>"
            "<p>Siz brauzerda bir sayt manzilini yozganingizda, "
            "kompyuteringiz uzoqdagi boshqa kompyuter — <b>server</b> — "
            "bilan gaplashadi.</p>"
            "<h3>So'rov safari</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Sizning kompyuteringiz\"] -->|\"so'rov yuboradi\"| B[\"Router (uy)\"]\n"
            "  B --> C[\"Internet provayder\"]\n"
            "  C --> D[\"Server (saytning uyi)\"]\n"
            "  D -->|\"sahifani qaytaradi\"| A\n"
            "</pre>"
            "<p>Bu safar ko'zga ko'rinmaydi va bir soniyaning bir qismida "
            "sodir bo'ladi — dunyoning narigi tomonidagi serverga borib "
            "qaytish!</p>"
            "<h2>Ma'lumot qanday yuboriladi?</h2>"
            "<p>Katta fayllar bittada emas, kichik <b>bo'lak (paket)</b>"
            "larga bo'linib yuboriladi — xuddi katta pochta jo'natmasi bir "
            "nechta kichik qutilarga bo'lib jo'natilgandek.</p>"
        ),
        "text_content_ru": (
            "<h2>Откуда берётся веб-страница?</h2>"
            "<p>Когда вы вводите адрес сайта в браузере, ваш компьютер "
            "«разговаривает» с другим, далёким компьютером — "
            "<b>сервером</b>.</p>"
            "<h3>Путешествие запроса</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart LR\n"
            "  A[\"Sizning kompyuteringiz\"] -->|\"отправляет запрос\"| B[\"Router (uy)\"]\n"
            "  B --> C[\"Internet provayder\"]\n"
            "  C --> D[\"Server (saytning uyi)\"]\n"
            "  D -->|\"возвращает страницу\"| A\n"
            "</pre>"
            "<p>Это путешествие невидимо и происходит за долю секунды — "
            "туда и обратно до сервера на другом конце света!</p>"
            "<h2>Как отправляется информация?</h2>"
            "<p>Большие файлы отправляются не целиком, а разбитыми на "
            "маленькие <b>части (пакеты)</b> — как большая посылка, "
            "разделённая на несколько маленьких коробок.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: So'rov safari qadamlari",
            "description": "Sayt manzilini yozgandan sahifa ko'rinishigacha.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "sorov_safari.txt",
                    "language": "text",
                    "code": (
                        "1. Siz brauzerda sayt manzilini yozasiz\n"
                        "2. Kompyuteringiz so'rovni Router orqali yuboradi\n"
                        "3. Router so'rovni Internet provayderga uzatadi\n"
                        "4. Provayder so'rovni to'g'ri Serverga topshiradi\n"
                        "5. Server sahifani tayyorlab, orqaga jo'natadi\n"
                        "6. Sahifa ekraningizda paydo bo'ladi\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Uzoqdagi kompyuter",
                "title_ru": "Далёкий компьютер",
                "description": "Veb-sahifani saqlab turadigan uzoqdagi kompyuter nima deb ataladi?",
                "description_ru": "Как называется далёкий компьютер, хранящий веб-страницу?",
                "exercise_type": "multiple_choice",
                "options": ["Server", "Router", "Klaviatura", "Karnay"],
                "options_ru": ["Сервер", "Роутер", "Клавиатура", "Динамик"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Xizmat qiluvchi\" degan ma'noni beradi.",
                "hint_ru": "Означает «обслуживающий».",
                "explanation": "Server — veb-sahifalarni saqlab, so'rov kelganda jo'natadigan kompyuter.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Katta fayllar",
                "title_ru": "Большие файлы",
                "description": "Katta fayllar internetda qanday yuboriladi?",
                "description_ru": "Как отправляются большие файлы в интернете?",
                "exercise_type": "multiple_choice",
                "options": ["Kichik bo'laklarga (paketlarga) bo'linib", "Bittada, to'liq", "Umuman yuborilmaydi", "Faqat rasm sifatida"],
                "options_ru": ["Разбитыми на маленькие части (пакеты)", "Целиком, одним куском", "Вообще не отправляются", "Только как картинка"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Katta pochta jo'natmasi kabi bo'lib yuboriladi.",
                "hint_ru": "Как большая посылка, разделённая на части.",
                "explanation": "Ma'lumot kichik paketlarga bo'linib yuboriladi va manzilda qayta yig'iladi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Uydagi qurilma",
                "title_ru": "Домашнее устройство",
                "description": "Sizning uydagi internetni tarqatuvchi qurilma qanday ataladi? Javob: ___",
                "description_ru": "Как называется домашнее устройство, раздающее интернет? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "router",
                "correct_answers_ru": "роутер",
                "hint": "Wi-Fi signalini beradigan qurilma.",
                "hint_ru": "Устройство, дающее сигнал Wi-Fi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "So'rov safarini tartibga soling",
                "title_ru": "Расставь путешествие запроса",
                "description": "So'rovning kompyuteringizdan serverga borish yo'lini tartibga qo'ying.",
                "description_ru": "Расставь путь запроса от твоего компьютера до сервера.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Sizning kompyuteringiz", "Router", "Internet provayder", "Server"],
                "drag_items_ru": ["Твой компьютер", "Роутер", "Интернет-провайдер", "Сервер"],
                "correct_order": ["Sizning kompyuteringiz", "Router", "Internet provayder", "Server"],
                "hint": "Uyingizdan boshlab, tashqariga qarab boring.",
                "hint_ru": "Начни из дома и двигайся наружу.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: So'rov safarini chizing",
            "task_title_ru": "Проект: нарисуй путешествие запроса",
            "task_description": (
                "So'rovning sizning qurilmangizdan serverga borib qaytish "
                "yo'lini chizing yoki yozing, har bir bosqichni "
                "belgilaganingizga ishonch hosil qiling. Suratini yoki "
                "matningizni topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Нарисуй или опиши путь запроса от твоего устройства до "
                "сервера и обратно, подписав каждый этап. Отправь фото или "
                "текст — учитель проверит."
            ),
            "task_requirements": (
                "• Kamida 4 ta bosqich belgilansin (qurilma, router, "
                "provayder, server)\n"
                "• Bosqichlar to'g'ri tartibda bo'lsin\n"
                "• Har bir bosqich qisqacha izohlansin"
            ),
            "task_requirements_ru": (
                "• Отмечены минимум 4 этапа (устройство, роутер, провайдер, "
                "сервер)\n"
                "• Этапы в правильном порядке\n"
                "• Каждый этап кратко подписан"
            ),
            "task_technologies": "Rasm/Matn",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "CPU va xotira",
        "title_ru": "Процессор и память",
        "points_reward": 20,
        "text_content": (
            "<h2>Kompyuterning miyasi — protsessor (CPU)</h2>"
            "<p><b>Protsessor (CPU)</b> — kompyuterning \"miyasi\". U barcha "
            "hisob-kitob va buyruqlarni bajaradi — nechta amal sekundiga "
            "bajarilishi CPU tezligiga bog'liq.</p>"
            "<h2>Ikki xil xotira</h2><ul>"
            "<li><b>RAM (tezkor xotira)</b> — hozir ishlayotgan narsalarni "
            "saqlaydi. O'chirilganda tozalanadi — xuddi qisqa muddatli "
            "xotirangiz kabi.</li>"
            "<li><b>Xotira (disk/SSD)</b> — fayllarni doimiy saqlaydi, "
            "o'chirilgandan keyin ham qoladi — xuddi uzoq muddatli "
            "xotirangiz kabi.</li></ul>"
            "<h2>Oddiy taqqoslash</h2>"
            "<p>CPU — oshpaz, RAM — oshxona stoli (hozir ishlatilayotgan "
            "narsalar), disk — omborxona (hamma narsa doimiy saqlanadigan "
            "joy).</p>"
        ),
        "text_content_ru": (
            "<h2>Мозг компьютера — процессор (CPU)</h2>"
            "<p><b>Процессор (CPU)</b> — «мозг» компьютера. Он выполняет "
            "все вычисления и команды — сколько операций в секунду он "
            "делает, зависит от скорости CPU.</p>"
            "<h2>Два вида памяти</h2><ul>"
            "<li><b>RAM (оперативная память)</b> — хранит то, что "
            "работает прямо сейчас. Очищается при выключении — как "
            "кратковременная память человека.</li>"
            "<li><b>Память (диск/SSD)</b> — хранит файлы постоянно, "
            "остаются и после выключения — как долговременная память "
            "человека.</li></ul>"
            "<h2>Простое сравнение</h2>"
            "<p>CPU — повар, RAM — кухонный стол (то, что используется "
            "прямо сейчас), диск — склад (место, где всё хранится "
            "постоянно).</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Oshxona taqqoslashi",
            "description": "CPU, RAM va diskni oshxona bilan solishtiramiz.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "oshxona.txt",
                    "language": "text",
                    "code": (
                        "CPU (protsessor)  = Oshpaz — ovqat pishiradi (hisoblaydi)\n"
                        "RAM (tezkor xotira) = Oshxona stoli — hozir ishlatilayotgan idish-taomlar\n"
                        "Disk (SSD)        = Omborxona — barcha oziq-ovqat doimiy saqlanadi\n"
                        "\n"
                        "Oshpaz ish tugagach, stol tozalanadi (RAM o'chadi),\n"
                        "lekin omborxona (disk) hamon to'la turadi.\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kompyuterning miyasi",
                "title_ru": "Мозг компьютера",
                "description": "Kompyuterning \"miyasi\" deb nima ataladi?",
                "description_ru": "Что называют «мозгом» компьютера?",
                "exercise_type": "multiple_choice",
                "options": ["Protsessor (CPU)", "Sichqoncha", "Ekran", "Karnay"],
                "options_ru": ["Процессор (CPU)", "Мышь", "Экран", "Динамик"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Barcha hisob-kitobni bajaradigan qism.",
                "hint_ru": "Часть, выполняющая все вычисления.",
                "explanation": "Protsessor (CPU) kompyuterning barcha hisob-kitoblarini bajaradi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "O'chirilganda tozalanadi",
                "title_ru": "Очищается при выключении",
                "description": "O'chirilganda tozalanadigan xotira qaysi?",
                "description_ru": "Какая память очищается при выключении?",
                "exercise_type": "multiple_choice",
                "options": ["RAM", "Disk (SSD)", "Ikkalasi ham", "Hech qaysisi"],
                "options_ru": ["RAM", "Диск (SSD)", "Обе", "Ни одна"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Qisqa muddatli xotiraga o'xshaydi.",
                "hint_ru": "Похожа на кратковременную память.",
                "explanation": "RAM o'chirilganda tozalanadi, disk esa doimiy saqlaydi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Doimiy saqlash",
                "title_ru": "Постоянное хранение",
                "description": "Fayllarni doimiy saqlaydigan xotira nima deb ataladi? Javob: ___",
                "description_ru": "Как называется память, постоянно хранящая файлы? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "disk",
                "correct_answers_ru": "диск",
                "hint": "SSD yoki qattiq disk.",
                "hint_ru": "SSD или жёсткий диск.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Taqqoslashni tartibga soling",
                "title_ru": "Расставь сравнение",
                "description": "Oshxona taqqoslashini to'g'ri juftlarga moslang.",
                "description_ru": "Сопоставь сравнение с кухней правильно.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["CPU — oshpaz", "RAM — oshxona stoli", "Disk — omborxona"],
                "drag_items_ru": ["CPU — повар", "RAM — кухонный стол", "Диск — склад"],
                "correct_order": ["CPU — oshpaz", "RAM — oshxona stoli", "Disk — omborxona"],
                "hint": "Darsda aytilgan tartibda.",
                "hint_ru": "В порядке, как в уроке.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mening qurilmam qismlari",
            "task_title_ru": "Проект: части моего устройства",
            "task_description": (
                "O'zingizning telefoningiz yoki kompyuteringizda CPU, RAM va "
                "diskning har biri nima uchun kerakligini o'z so'zlaringiz "
                "bilan tushuntiring. Matningizni topshiring — o'qituvchi "
                "tekshiradi."
            ),
            "task_description_ru": (
                "Объясни своими словами, зачем в твоём телефоне или "
                "компьютере нужны CPU, RAM и диск. Отправь текст — учитель "
                "проверит."
            ),
            "task_requirements": (
                "• CPU nima uchunligi tushuntirilsin\n"
                "• RAM nima uchunligi tushuntirilsin\n"
                "• Disk nima uchunligi tushuntirilsin"
            ),
            "task_requirements_ru": (
                "• Объяснено, зачем нужен CPU\n"
                "• Объяснено, зачем нужна RAM\n"
                "• Объяснено, зачем нужен диск"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy: Mening kompyuter bilimlarim",
        "title_ru": "Итог: мои знания о компьютере",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Ushbu kursda kompyuterning kirish-chiqishi, ikkilik "
            "sanoq tizimi, algoritm, internet va CPU-xotira haqida "
            "o'rgandik. Endi hammasini bitta rasmda ko'ramiz — siz "
            "klaviaturada tugma bosganingizdan, do'stingizning "
            "ekranida xabar ko'rinishigacha bo'lgan yo'l.</p>"
            "<h3>Xabar qanday yetib boradi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Kirish: tugma bosiladi\"] --> B[\"CPU xabarni ikkilik (0/1) kodga aylantiradi\"]\n"
            "  B --> C[\"Router va internet orqali yuboriladi\"]\n"
            "  C --> D[\"Server xabarni do'stingizga yo'naltiradi\"]\n"
            "  D --> E[\"Chiqish: do'stingiz ekranida xabar ko'rinadi\"]\n"
            "</pre>"
            "<p>Kirish-chiqish, ikkilik kod, algoritm (yo'naltirish "
            "qoidalari) va internet — hammasi birga ishlaganda, oddiy "
            "xabar bir necha soniyada dunyoning narigi tomoniga "
            "yetib boradi!</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>В этом курсе мы узнали про ввод-вывод компьютера, "
            "двоичную систему, алгоритм, интернет и CPU-память. Теперь "
            "посмотрим всё на одной схеме — путь от нажатия клавиши до "
            "появления сообщения на экране друга.</p>"
            "<h3>Как доходит сообщение</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Kirish: tugma bosiladi\"] --> B[\"CPU xabarni ikkilik (0/1) kodga aylantiradi\"]\n"
            "  B --> C[\"Router va internet orqali yuboriladi\"]\n"
            "  C --> D[\"Server xabarni do'stingizga yo'naltiradi\"]\n"
            "  D --> E[\"Chiqish: do'stingiz ekranida xabar ko'rinadi\"]\n"
            "</pre>"
            "<p>Ввод-вывод, двоичный код, алгоритм (правила маршрутизации) "
            "и интернет — когда всё работает вместе, простое сообщение за "
            "несколько секунд доходит на другой конец света!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Kurs xulosasi",
            "description": "5 ta mavzuning qisqacha yakuni.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "xulosa.txt",
                    "language": "text",
                    "code": (
                        "1. Kompyuter = Kirish + Qayta ishlash + Chiqish\n"
                        "2. Kompyuter ichida hammasi 0 va 1 (ikkilik) bilan yoziladi\n"
                        "3. Algoritm = qadam-baqadam ish tartibi\n"
                        "4. Internet = qurilma -> router -> provayder -> server -> orqaga\n"
                        "5. CPU hisoblaydi, RAM vaqtincha, disk doimiy saqlaydi\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kompyuterning uch qismi",
                "title_ru": "Три части компьютера",
                "description": "Har qanday kompyuter qaysi uchta ishni bajaradi?",
                "description_ru": "Какие три действия выполняет любой компьютер?",
                "exercise_type": "multiple_choice",
                "options": ["Kirish, qayta ishlash, chiqish", "O'ynash, kutish, o'chirish", "Yozish, o'qish, chizish", "Ochish, yopish, saqlash"],
                "options_ru": ["Ввод, обработка, вывод", "Игра, ожидание, выключение", "Письмо, чтение, рисование", "Открытие, закрытие, сохранение"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "1-darsni eslang.",
                "hint_ru": "Вспомни урок 1.",
                "explanation": "Har qanday kompyuter kirish, qayta ishlash va chiqish bilan ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kompyuterning tili",
                "title_ru": "Язык компьютера",
                "description": "Kompyuter ichida hamma narsa qaysi ikkita raqam bilan yoziladi?",
                "description_ru": "Какими двумя цифрами записывается всё внутри компьютера?",
                "exercise_type": "multiple_choice",
                "options": ["0 va 1", "1 va 10", "A va B", "2 va 4"],
                "options_ru": ["0 и 1", "1 и 10", "A и B", "2 и 4"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "2-darsni eslang.",
                "hint_ru": "Вспомни урок 2.",
                "explanation": "Kompyuter ichida hammasi ikkilik (0 va 1) kod bilan yoziladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Server vazifasi",
                "title_ru": "Роль сервера",
                "description": "Veb-sahifani saqlab, so'rov kelganda jo'natadigan uzoqdagi kompyuter nima deb ataladi? Javob: ___",
                "description_ru": "Как называется далёкий компьютер, хранящий страницу и отправляющий её по запросу? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "server",
                "correct_answers_ru": "сервер",
                "hint": "4-darsni eslang.",
                "hint_ru": "Вспомни урок 4.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Xabar safarini tartibga soling",
                "title_ru": "Расставь путь сообщения",
                "description": "Tugma bosishdan do'stingiz ekranigacha bo'lgan yo'lni tartibga qo'ying.",
                "description_ru": "Расставь путь от нажатия клавиши до экрана друга.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Tugma bosiladi", "CPU ikkilik kodga aylantiradi", "Internet orqali yuboriladi", "Do'stingiz ekranida ko'rinadi"],
                "drag_items_ru": ["Нажимается клавиша", "CPU превращает в двоичный код", "Отправляется через интернет", "Появляется на экране друга"],
                "correct_order": ["Tugma bosiladi", "CPU ikkilik kodga aylantiradi", "Internet orqali yuboriladi", "Do'stingiz ekranida ko'rinadi"],
                "hint": "Kirishdan chiqishgacha bo'lgan to'liq yo'l.",
                "hint_ru": "Полный путь от ввода до вывода.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Kompyuterni tushuntirib bering",
            "task_title_ru": "Итоговый проект: объясни компьютер",
            "task_description": (
                "Kursda o'rgangan kamida 4 ta tushunchani (kirish-chiqish, "
                "ikkilik sanoq, algoritm, internet, CPU-xotira) ishlatib, "
                "o'z so'zlaringiz bilan kompyuter va internet birgalikda "
                "qanday ishlashini tushuntiring. Chizma qo'shishingiz ham "
                "mumkin. Matningizni (yoki suratini) topshiring — bu "
                "sizning eng to'liq loyihangiz!"
            ),
            "task_description_ru": (
                "Используя минимум 4 понятия из курса (ввод-вывод, "
                "двоичная система, алгоритм, интернет, CPU-память), "
                "объясни своими словами, как вместе работают компьютер и "
                "интернет. Можешь добавить рисунок. Отправь текст (или "
                "фото) — это твой самый полный проект!"
            ),
            "task_requirements": (
                "• Kamida 4 ta kurs tushunchasi ishlatilsin\n"
                "• Tushuntirish o'z so'zlari bilan yozilsin\n"
                "• Javob mantiqiy va tushunarli bo'lsin"
            ),
            "task_requirements_ru": (
                "• Использованы минимум 4 понятия из курса\n"
                "• Объяснение написано своими словами\n"
                "• Ответ логичный и понятный"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 5,
        },
    },
]
