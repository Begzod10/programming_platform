"""Advanced Scratch course for children aged 7-12 (Uzbek-primary, Russian).

Third and final step of the kids' Scratch track: 144 (Scratch bilan
tanishish, basics) -> 149 (Scratch 2: O'yin yaratish, a single-sprite game)
-> this course (multi-sprite coordination). Everything here assumes a
single-sprite game already works (course 149's "Olma tut") and teaches what
it takes to make TWO sprites cooperate: independent per-sprite scripts,
broadcasting a signal between them, a variable shared across all sprites
(vs one private to a single sprite), two-player controls, and cloning a
sprite to spawn many copies of it. The capstone is a simple two-player race.

Scratch projects can't run or be AI-graded in the platform, so every
`sample` uses sample_type "code" showing the block script as readable
Uzbek pseudocode (matching course 149's convention), and every `task` asks
the child to build the game in Scratch and submit their SHARE LINK (or a
screenshot) for a teacher to review.

Block names use the site's `scratch-block` color-coded span convention
(see StudentLessonPage.css) rather than plain `<code>` — matches the fix
already applied to courses 144 and 149.

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "Scratch 3: Ilg'or Scratch (bolalar uchun)",
    "title_ru": "Scratch 3: Продвинутый Scratch (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun Scratch'da bir nechta personaj bilan "
        "ishlashni o'rgatuvchi kurs. Personajlar orasida signal yuborishni, "
        "barcha personajlar uchun umumiy o'zgaruvchini, ikki o'yinchili "
        "boshqaruvni va klonlashni o'rganamiz hamda ikki o'yinchili poyga "
        "o'yinini yaratamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: работа с несколькими персонажами в "
        "Scratch. Научимся отправлять сигналы между персонажами, "
        "использовать переменную, общую для всех персонажей, управление "
        "для двух игроков и клонирование, а также создадим гонку на двоих "
        "игроков."
    ),
    "instructor_id": 2,
    "difficulty_level": "Intermediate",
    "duration_weeks": 6,
    "max_points": 120,
    "category_id": None,
    "prerequisite_course_id": 149,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    # ------------------------------------------------------------------ 0
    {
        "order": 0,
        "title": "Bir nechta personaj bilan ishlash",
        "title_ru": "Работаем с несколькими персонажами",
        "points_reward": 15,
        "text_content": (
            "<h2>Har bir personaj — o'z skripti</h2>"
            "<p>Hozirgacha bitta personaj bilan ishladik. Lekin o'yinda "
            "ko'pincha bir nechta personaj kerak bo'ladi — masalan ikkita "
            "o'yinchi yoki bir nechta dushman. Ekranning pastki qismidagi "
            "<b>personajlar ro'yxati</b>da qaysi personajni bossangiz, "
            "o'sha personajning <b>o'z</b> skriptlari ko'rinadi.</p>"
            "<p><b>Muhim:</b> har bir personajning skriptlari faqat o'shaning "
            "o'zi uchun ishlaydi. 1-personajga qo'shgan blok 2-personajga "
            "ta'sir qilmaydi — ular butunlay mustaqil.</p>"
            "<h2>Ikkala skript bir vaqtda ishlaydi</h2>"
            "<p>Agar ikkala personajda ham "
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span> "
            "bloki bo'lsa, bayroq bosilganda ikkalasi <b>bir vaqtning "
            "o'zida</b> ishga tushadi:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Men birinchi personajman! deb ayt</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Men ikkinchiman! deb ayt</span>"
            "</div>"
            "<p>Yangi personaj qo'shish uchun personajlar ro'yxati ostidagi "
            "<b>\"Yangi personaj\"</b> tugmasini bosamiz.</p>"
        ),
        "text_content_ru": (
            "<h2>У каждого персонажа — свой скрипт</h2>"
            "<p>До сих пор мы работали с одним персонажем. Но в играх часто "
            "нужно несколько — например два игрока или несколько врагов. В "
            "<b>списке персонажей</b> внизу экрана: на какого персонажа "
            "нажмёшь, того скрипты и видны.</p>"
            "<p><b>Важно:</b> скрипты каждого персонажа работают только для "
            "него самого. Блок, добавленный персонажу 1, не влияет на "
            "персонажа 2 — они полностью независимы.</p>"
            "<h2>Оба скрипта работают одновременно</h2>"
            "<p>Если у обоих персонажей есть блок "
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>, "
            "при нажатии флага оба запустятся <b>одновременно</b>:</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Men birinchi personajman! deb ayt</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Men ikkinchiman! deb ayt</span>"
            "</div>"
            "<p>Чтобы добавить нового персонажа, нажимаем кнопку <b>«Новый "
            "персонаж»</b> под списком персонажей.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Ikki personaj, ikki mustaqil skript",
            "description": "Bayroq bosilganda ikkala personaj bir vaqtda o'z gapini aytadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "ikki_personaj.txt",
                    "language": "text",
                    "code": (
                        "[1-PERSONAJ]\n"
                        "yashil bayroq bosilganda\n"
                        "Men birinchi personajman! deb ayt\n"
                        "\n"
                        "[2-PERSONAJ]\n"
                        "yashil bayroq bosilganda\n"
                        "Men ikkinchiman! deb ayt\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Skriptlar kimga tegishli?",
                "title_ru": "Кому принадлежат скрипты?",
                "description": "1-personajga qo'shilgan blok 2-personajga ta'sir qiladimi?",
                "description_ru": "Влияет ли блок, добавленный персонажу 1, на персонажа 2?",
                "exercise_type": "multiple_choice",
                "options": ["Yo'q, har biri mustaqil", "Ha, hammaga ta'sir qiladi", "Faqat rangga ta'sir qiladi", "Faqat ovozga ta'sir qiladi"],
                "options_ru": ["Нет, каждый независим", "Да, влияет на всех", "Влияет только на цвет", "Влияет только на звук"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Har bir personajning o'z skriptlari bor.",
                "hint_ru": "У каждого персонажа свои скрипты.",
                "explanation": "Har bir personajning skriptlari faqat o'shaning o'zi uchun ishlaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yangi personaj",
                "title_ru": "Новый персонаж",
                "description": "Yangi personaj qo'shish tugmasi qayerda joylashgan?",
                "description_ru": "Где находится кнопка добавления нового персонажа?",
                "exercise_type": "multiple_choice",
                "options": ["Personajlar ro'yxati ostida", "Sahna ichida", "Bloklar palitrasida", "Skriptlar maydonida"],
                "options_ru": ["Под списком персонажей", "Внутри сцены", "В палитре блоков", "В области скриптов"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ekranning pastki qismiga qarang.",
                "hint_ru": "Посмотри в нижнюю часть экрана.",
                "explanation": "\"Yangi personaj\" tugmasi personajlar ro'yxati ostida joylashgan.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Bir vaqtda ishga tushish",
                "title_ru": "Запуск одновременно",
                "description": "Ikkala personajda ham 'yashil bayroq bosilganda' bo'lsa, bayroq bosilganda ular qachon ishga tushadi? To'ldiring: '___ vaqtning o'zida'",
                "description_ru": "Если у обоих персонажей есть 'yashil bayroq bosilganda', когда они запускаются? Заполни: 'в один и тот же ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "bir",
                "correct_answers_ru": "момент",
                "hint": "Ikkalasi bir zumda, birga.",
                "hint_ru": "Оба сразу, вместе.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Ikki skriptli sahnani tuzing",
                "title_ru": "Собери сцену с двумя скриптами",
                "description": "Bloklarni tartibga qo'ying: har ikkala personaj bayroq bosilganda gapiradi.",
                "description_ru": "Расставь блоки: оба персонажа говорят по нажатию флага.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["1-personaj: yashil bayroq bosilganda", "1-personaj: Salom! deb ayt", "2-personaj: yashil bayroq bosilganda", "2-personaj: Salom! deb ayt"],
                "drag_items_ru": ["1-personaj: yashil bayroq bosilganda", "1-personaj: Salom! deb ayt", "2-personaj: yashil bayroq bosilganda", "2-personaj: Salom! deb ayt"],
                "correct_order": ["1-personaj: yashil bayroq bosilganda", "1-personaj: Salom! deb ayt", "2-personaj: yashil bayroq bosilganda", "2-personaj: Salom! deb ayt"],
                "hint": "Har bir personaj uchun avval hodisa, keyin uning ishi.",
                "hint_ru": "Для каждого персонажа сначала событие, потом его действие.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Ikki personajli sahna",
            "task_title_ru": "Проект: сцена с двумя персонажами",
            "task_description": (
                "Scratchda (scratch.mit.edu) ikkita personaj qo'shing. Har "
                "birida yashil bayroq bosilganda ishga tushadigan, bir-biridan "
                "farqli o'z skripti bo'lsin (masalan, har biri boshqa gap "
                "aytsin yoki boshqa tomonga yursin). Tayyor bo'lgach, Share "
                "tugmasi bilan ulashib, HAVOLASINI yoki ekran rasmini "
                "topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Добавь в Scratch (scratch.mit.edu) двух персонажей. У каждого "
                "должен быть свой скрипт, запускающийся по зелёному флагу и "
                "отличающийся от другого (например, каждый говорит своё или "
                "идёт в свою сторону). Когда будет готово, поделись через "
                "кнопку Share и отправь ССЫЛКУ или скриншот — учитель "
                "проверит."
            ),
            "task_requirements": (
                "• Kamida ikkita personaj bo'lsin\n"
                "• Har birida yashil bayroq bosilganda blokidan foydalanilsin\n"
                "• Ikkala personajning skripti bir-biridan farq qilsin"
            ),
            "task_requirements_ru": (
                "• Минимум два персонажа\n"
                "• У каждого использован блок «когда нажат зелёный флаг»\n"
                "• Скрипты персонажей отличаются друг от друга"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Signal yuborish (broadcast)",
        "title_ru": "Отправка сигнала (broadcast)",
        "points_reward": 20,
        "text_content": (
            "<h2>Personajlar bir-biriga qanday gapiradi?</h2>"
            "<p>Bitta personaj boshqasiga \"boshla!\" deb aytishi kerak "
            "bo'lsa, buni <b>signal (broadcast)</b> bilan qilamiz. Signal — "
            "bu barcha personajlar eshitadigan xabar.</p>"
            "<h2>Signal yuborish va qabul qilish</h2>"
            "<p>Signal yuboradigan blok — <span class=\"scratch-block scratch-block--events\">xabar1 ni yubor</span>. "
            "Uni eshitadigan blok — <span class=\"scratch-block scratch-block--events\">xabar1 ni qabul qilganda</span>. "
            "Ular ikkalasi ham <b>Hodisalar</b> guruhida (sariq).</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bu personaj bosilganda</span>"
            "<span class=\"scratch-block scratch-block--events scratch-block--nested\">xabar1 ni yubor</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">xabar1 ni qabul qilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Signal keldi! deb ayt</span>"
            "</div>"
            "<p>1-skript bir personajda, 2-skript boshqasida bo'lishi mumkin "
            "— <b>xabar1 ni yubor</b> ishlaganda, <b>xabar1 ni qabul "
            "qilganda</b> bloki bor <b>hamma</b> personaj ishga tushadi.</p>"
            "<h3>Signal qanday ishlaydi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"1-personaj: bu personaj bosilganda\"] --> B[\"xabar1 ni yubor\"]\n"
            "  B -->|\"signal eshitildi\"| C[\"2-personaj: xabar1 ni qabul qilganda\"]\n"
            "  C --> D[\"Signal keldi! deb ayt\"]\n"
            "  style A fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style B fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style C fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style D fill:#9966FF,stroke:#5c2ea6,color:#fff\n"
            "</pre>"
            "<p>1-personaj signalni yuboradi, 2-personaj uni eshitib, o'z "
            "ishini boshlaydi — ular bir-biriga to'g'ridan-to'g'ri "
            "ulanmagan, faqat signal orqali \"gaplashadi\".</p>"
        ),
        "text_content_ru": (
            "<h2>Как персонажи разговаривают друг с другом?</h2>"
            "<p>Если одному персонажу нужно сказать другому «начинай!», это "
            "делается через <b>сигнал (broadcast)</b>. Сигнал — это "
            "сообщение, которое слышат все персонажи.</p>"
            "<h2>Отправка и получение сигнала</h2>"
            "<p>Блок отправки сигнала — <span class=\"scratch-block scratch-block--events\">xabar1 ni yubor</span>. "
            "Блок, который его слышит — <span class=\"scratch-block scratch-block--events\">xabar1 ni qabul qilganda</span>. "
            "Оба они в группе <b>События</b> (жёлтые).</p>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bu personaj bosilganda</span>"
            "<span class=\"scratch-block scratch-block--events scratch-block--nested\">xabar1 ni yubor</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">xabar1 ni qabul qilganda</span>"
            "<span class=\"scratch-block scratch-block--looks scratch-block--nested\">Signal keldi! deb ayt</span>"
            "</div>"
            "<p>Скрипт 1 может быть у одного персонажа, скрипт 2 — у "
            "другого. Когда срабатывает <b>xabar1 ni yubor</b>, запускается "
            "<b>каждый</b> персонаж с блоком <b>xabar1 ni qabul qilganda</b>.</p>"
            "<h3>Как работает сигнал</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"1-personaj: bu personaj bosilganda\"] --> B[\"xabar1 ni yubor\"]\n"
            "  B -->|\"сигнал услышан\"| C[\"2-personaj: xabar1 ni qabul qilganda\"]\n"
            "  C --> D[\"Signal keldi! deb ayt\"]\n"
            "  style A fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style B fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style C fill:#D9A600,stroke:#3d2e00,color:#fff\n"
            "  style D fill:#9966FF,stroke:#5c2ea6,color:#fff\n"
            "</pre>"
            "<p>Персонаж 1 отправляет сигнал, персонаж 2 его слышит и "
            "начинает своё действие — они не связаны напрямую, а "
            "«разговаривают» только через сигнал.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Signal bilan boshlash",
            "description": "1-personaj bosilganda signal yuboradi, 2-personaj signalni eshitib javob beradi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "signal.txt",
                    "language": "text",
                    "code": (
                        "[1-PERSONAJ]\n"
                        "bu personaj bosilganda\n"
                        "xabar1 ni yubor\n"
                        "\n"
                        "[2-PERSONAJ]\n"
                        "xabar1 ni qabul qilganda\n"
                        "Signal keldi! deb ayt\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Signal nima uchun kerak?",
                "title_ru": "Зачем нужен сигнал?",
                "description": "Signal (broadcast) nima uchun ishlatiladi?",
                "description_ru": "Для чего используется сигнал (broadcast)?",
                "exercise_type": "multiple_choice",
                "options": ["Bir personaj boshqasiga xabar berish uchun", "Rang o'zgartirish uchun", "Ovoz balandligini o'zgartirish uchun", "Fayl saqlash uchun"],
                "options_ru": ["Чтобы один персонаж сообщил другому", "Чтобы изменить цвет", "Чтобы изменить громкость", "Чтобы сохранить файл"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Bu personajlar orasidagi \"gaplashish\" usuli.",
                "hint_ru": "Это способ персонажей «разговаривать» друг с другом.",
                "explanation": "Signal bitta personajdan boshqalariga xabar yetkazadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Signalni kim eshitadi?",
                "title_ru": "Кто слышит сигнал?",
                "description": "'xabar1 ni yubor' ishlaganda qaysi personajlar ishga tushadi?",
                "description_ru": "Какие персонажи запускаются, когда срабатывает 'xabar1 ni yubor'?",
                "exercise_type": "multiple_choice",
                "options": [
                    "xabar1 ni qabul qilganda blokiga ega barcha personajlar",
                    "Faqat signal yuborgan personaj",
                    "Faqat birinchi personaj",
                    "Hech kim",
                ],
                "options_ru": [
                    "Все персонажи с блоком xabar1 ni qabul qilganda",
                    "Только тот, кто отправил сигнал",
                    "Только первый персонаж",
                    "Никто",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Signal barchaga eshitiladi, lekin faqat kutayotganlar javob beradi.",
                "hint_ru": "Сигнал слышат все, но реагируют только те, кто его ждёт.",
                "explanation": "'xabar1 ni qabul qilganda' bloki bor har bir personaj ishga tushadi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Signal yuborish bloki",
                "title_ru": "Блок отправки сигнала",
                "description": "Signal yuboradigan blokni to'ldiring: 'xabar1 ni ___'",
                "description_ru": "Заполни блок отправки сигнала: 'xabar1 ni ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "yubor",
                "correct_answers_ru": "yubor",
                "hint": "\"Yuborish\" fe'li.",
                "hint_ru": "Глагол «отправить».",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Signal skriptini tuzing",
                "title_ru": "Собери скрипт сигнала",
                "description": "Bloklarni tartibga qo'ying: personaj bosilganda signal yuboriladi.",
                "description_ru": "Расставь блоки: сигнал отправляется по клику на персонажа.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["bu personaj bosilganda", "xabar1 ni yubor"],
                "drag_items_ru": ["bu personaj bosilganda", "xabar1 ni yubor"],
                "correct_order": ["bu personaj bosilganda", "xabar1 ni yubor"],
                "hint": "Avval hodisa, keyin signal yuborish.",
                "hint_ru": "Сначала событие, потом отправка сигнала.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Signal bilan gaplashuvchi personajlar",
            "task_title_ru": "Проект: персонажи, общающиеся сигналом",
            "task_description": (
                "Scratchda (scratch.mit.edu) bitta personaj signal "
                "yuboradigan, ikkinchisi esa shu signalni qabul qilib javob "
                "beradigan skript yozing. Tayyor bo'lgach, Share tugmasi "
                "bilan ulashib, HAVOLASINI yoki ekran rasmini topshiring — "
                "o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Напиши в Scratch (scratch.mit.edu) скрипт, где один "
                "персонаж отправляет сигнал, а второй его получает и "
                "отвечает. Когда будет готово, поделись через кнопку Share и "
                "отправь ССЫЛКУ или скриншот — учитель проверит."
            ),
            "task_requirements": (
                "• Bitta personajda 'xabar ni yubor' blokidan foydalanilsin\n"
                "• Boshqa personajda 'xabar ni qabul qilganda' blokidan "
                "foydalanilsin\n"
                "• Signal kelganda ikkinchi personaj biror ish qilsin "
                "(gapirsin, yursin va h.k.)"
            ),
            "task_requirements_ru": (
                "• У одного персонажа использован блок «отправить сигнал»\n"
                "• У другого использован блок «когда получен сигнал»\n"
                "• При получении сигнала второй персонаж что-то делает "
                "(говорит, двигается и т.д.)"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Umumiy o'zgaruvchilar",
        "title_ru": "Переменные для всех персонажей",
        "points_reward": 20,
        "text_content": (
            "<h2>Faqat men uchunmi, hammaga birgami?</h2>"
            "<p>O'zgaruvchi yaratganda Scratch ikkita variant beradi:</p>"
            "<ul>"
            "<li><b>Barcha personajlar uchun</b> — o'zgaruvchi <b>umumiy</b>: "
            "har qanday personaj uni o'qishi va o'zgartirishi mumkin, va "
            "qiymati hammasi uchun bir xil.</li>"
            "<li><b>Faqat shu personaj uchun</b> — o'zgaruvchi <b>xususiy</b>: "
            "har bir personajning o'z alohida nusxasi bo'ladi.</li>"
            "</ul>"
            "<p>Ikki o'yinchili o'yinda umumiy hisob kerak bo'lsa (masalan, "
            "ikkalasi ham bitta hisobga qo'shadi), <b>Barcha personajlar "
            "uchun</b> ni tanlaymiz.</p>"
            "<h2>Ikki personaj bitta hisobga qo'shadi</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bo'shliq tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">hisob ni 1 ga oshir</span>"
            "</div>"
            "<p>Bu skript qaysi personajga qo'yilmasin, <b>hisob</b> umumiy "
            "bo'lgani uchun, oshgan qiymatni sahnadagi <b>hamma</b> "
            "ko'radi.</p>"
        ),
        "text_content_ru": (
            "<h2>Только для меня или для всех вместе?</h2>"
            "<p>При создании переменной Scratch предлагает два варианта:</p>"
            "<ul>"
            "<li><b>Для всех персонажей</b> — переменная <b>общая</b>: "
            "любой персонаж может её читать и менять, и значение у всех "
            "одинаковое.</li>"
            "<li><b>Только для этого персонажа</b> — переменная <b>личная</b>: "
            "у каждого персонажа своя отдельная копия.</li>"
            "</ul>"
            "<p>Если в игре на двоих нужен общий счёт (например, оба "
            "добавляют в один счёт), выбираем <b>«Для всех персонажей»</b>.</p>"
            "<h2>Два персонажа добавляют в один счёт</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">bo'shliq tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--variables scratch-block--nested\">hisob ni 1 ga oshir</span>"
            "</div>"
            "<p>Этот скрипт, у какого бы персонажа ни стоял, поскольку "
            "<b>hisob</b> общая, увеличенное значение видят <b>все</b> на "
            "сцене.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Umumiy hisob",
            "description": "Ikkala personaj ham bosh joy tugmasi bilan bitta umumiy hisobga qo'shadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "umumiy_hisob.txt",
                    "language": "text",
                    "code": (
                        "[O'ZGARUVCHI]\n"
                        "hisob — Barcha personajlar uchun\n"
                        "\n"
                        "[1-PERSONAJ]\n"
                        "bo'shliq tugmasi bosilganda\n"
                        "hisob ni 1 ga oshir\n"
                        "\n"
                        "[2-PERSONAJ]\n"
                        "bo'shliq tugmasi bosilganda\n"
                        "hisob ni 1 ga oshir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Umumiy o'zgaruvchi",
                "title_ru": "Общая переменная",
                "description": "Barcha personajlar o'qiy va o'zgartira oladigan o'zgaruvchi qaysi variantda yaratiladi?",
                "description_ru": "В каком варианте создаётся переменная, которую могут читать и менять все персонажи?",
                "exercise_type": "multiple_choice",
                "options": ["Barcha personajlar uchun", "Faqat shu personaj uchun", "Faqat sahna uchun", "Hech qaysi biri emas"],
                "options_ru": ["Для всех персонажей", "Только для этого персонажа", "Только для сцены", "Ни один из вариантов"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Nomi to'g'ridan-to'g'ri javobni bildiradi.",
                "hint_ru": "Название прямо подсказывает ответ.",
                "explanation": "\"Barcha personajlar uchun\" tanlansa, o'zgaruvchi umumiy bo'ladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Xususiy o'zgaruvchi",
                "title_ru": "Личная переменная",
                "description": "\"Faqat shu personaj uchun\" o'zgaruvchi haqida nima to'g'ri?",
                "description_ru": "Что верно про переменную «только для этого персонажа»?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Har bir personajning o'z alohida nusxasi bor",
                    "Hamma personajda bir xil qiymat bo'ladi",
                    "U hech qachon o'zgarmaydi",
                    "Faqat sahnada ko'rinadi",
                ],
                "options_ru": [
                    "У каждого персонажа своя отдельная копия",
                    "У всех персонажей одинаковое значение",
                    "Она никогда не меняется",
                    "Видна только на сцене",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "\"Faqat shu personaj uchun\" — xususiy, mustaqil nusxa.",
                "hint_ru": "«Только для этого персонажа» — личная, отдельная копия.",
                "explanation": "Xususiy o'zgaruvchida har bir personaj o'zining alohida nusxasiga ega.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Qaysi variantni tanlaymiz?",
                "title_ru": "Какой вариант выбрать?",
                "description": "Ikki o'yinchi bitta umumiy hisobga qo'shishi kerak bo'lsa, qaysi variantni tanlaymiz? To'ldiring: 'Barcha ___ uchun'",
                "description_ru": "Если два игрока должны добавлять в один общий счёт, какой вариант выбрать? Заполни: 'Для всех ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "personajlar",
                "correct_answers_ru": "персонажей",
                "hint": "Savoldagi so'zga qarang.",
                "hint_ru": "Посмотри на слово в вопросе.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Umumiy hisob skriptini tuzing",
                "title_ru": "Собери скрипт общего счёта",
                "description": "Bloklarni tartibga qo'ying: bo'sh joy bosilganda hisob oshadi.",
                "description_ru": "Расставь блоки: счёт растёт по нажатию пробела.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["bo'shliq tugmasi bosilganda", "hisob ni 1 ga oshir"],
                "drag_items_ru": ["bo'shliq tugmasi bosilganda", "hisob ni 1 ga oshir"],
                "correct_order": ["bo'shliq tugmasi bosilganda", "hisob ni 1 ga oshir"],
                "hint": "Avval hodisa, keyin o'zgaruvchini oshirish.",
                "hint_ru": "Сначала событие, потом увеличение переменной.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Umumiy hisob",
            "task_title_ru": "Проект: общий счёт",
            "task_description": (
                "Scratchda (scratch.mit.edu) \"Barcha personajlar uchun\" "
                "umumiy o'zgaruvchi yarating. Ikkita personajning har biri "
                "o'z tugmasi bosilganda shu umumiy hisobga qo'shsin. Tayyor "
                "bo'lgach, Share tugmasi bilan ulashib, HAVOLASINI yoki "
                "ekran rasmini topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Создай в Scratch (scratch.mit.edu) общую переменную «для "
                "всех персонажей». У обоих персонажей по нажатию своей "
                "клавиши должно добавляться в этот общий счёт. Когда будет "
                "готово, поделись через кнопку Share и отправь ССЫЛКУ или "
                "скриншот — учитель проверит."
            ),
            "task_requirements": (
                "• Umumiy o'zgaruvchi (\"Barcha personajlar uchun\") "
                "yaratilsin\n"
                "• Ikkala personaj ham shu o'zgaruvchiga qo'shsin\n"
                "• Har bir personaj o'zining tugmasi bilan ishlasin"
            ),
            "task_requirements_ru": (
                "• Создана общая переменная («для всех персонажей»)\n"
                "• Оба персонажа добавляют в эту переменную\n"
                "• У каждого персонажа своя клавиша"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Ikki o'yinchili boshqaruv",
        "title_ru": "Управление для двух игроков",
        "points_reward": 20,
        "text_content": (
            "<h2>Bitta klaviaturada ikki o'yinchi</h2>"
            "<p>2-darsda o'rgangan strelka tugmalari bilan boshqarishni "
            "eslaymizmi? Ikki o'yinchi bitta klaviaturada birga o'ynashi "
            "uchun, ularga <b>turli tugmalar</b> beramiz — 1-o'yinchiga "
            "strelkalar, 2-o'yinchiga <b>W, A, S, D</b> harflari.</p>"
            "<h2>1-o'yinchi skripti (strelkalar)</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<h2>2-o'yinchi skripti (D harfi)</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">d tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<p>Ikkala skript ham bir xil ishni qiladi — faqat boshqa "
            "personajda va boshqa tugma bilan. Har bir yo'nalish uchun "
            "(yuqori-past-chap-o'ng) shunga o'xshash skript yozamiz.</p>"
        ),
        "text_content_ru": (
            "<h2>Два игрока на одной клавиатуре</h2>"
            "<p>Помнишь управление стрелками из урока 2? Чтобы два игрока "
            "играли вместе на одной клавиатуре, даём им <b>разные "
            "клавиши</b> — игроку 1 стрелки, игроку 2 буквы <b>W, A, S, "
            "D</b>.</p>"
            "<h2>Скрипт игрока 1 (стрелки)</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">o'ng strelka tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<h2>Скрипт игрока 2 (буква D)</h2>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">d tugmasi bosilganda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">x ni 10 ga o'zgartir</span>"
            "</div>"
            "<p>Оба скрипта делают одно и то же — только у разных "
            "персонажей и с разной клавишей. Для каждого направления "
            "(вверх-вниз-влево-вправо) пишем похожий скрипт.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Ikki o'yinchi harakati",
            "description": "1-o'yinchi strelkalar bilan, 2-o'yinchi WASD bilan yuradi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "ikki_oyinchi.txt",
                    "language": "text",
                    "code": (
                        "[1-O'YINCHI]\n"
                        "o'ng strelka tugmasi bosilganda\n"
                        "x ni 10 ga o'zgartir\n"
                        "chap strelka tugmasi bosilganda\n"
                        "x ni -10 ga o'zgartir\n"
                        "\n"
                        "[2-O'YINCHI]\n"
                        "d tugmasi bosilganda\n"
                        "x ni 10 ga o'zgartir\n"
                        "a tugmasi bosilganda\n"
                        "x ni -10 ga o'zgartir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Ikkinchi o'yinchi tugmalari",
                "title_ru": "Клавиши второго игрока",
                "description": "Ikki o'yinchi bitta klaviaturada o'ynasa, 2-o'yinchi odatda qaysi tugmalarni ishlatadi?",
                "description_ru": "Если два игрока играют на одной клавиатуре, какие клавиши обычно у игрока 2?",
                "exercise_type": "multiple_choice",
                "options": ["W, A, S, D", "Strelkalar", "Faqat probel", "Sonlar"],
                "options_ru": ["W, A, S, D", "Стрелки", "Только пробел", "Цифры"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Strelkalar 1-o'yinchida band.",
                "hint_ru": "Стрелки заняты игроком 1.",
                "explanation": "1-o'yinchi strelkalar, 2-o'yinchi odatda WASD ishlatadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Nima uchun turli tugmalar?",
                "title_ru": "Зачем разные клавиши?",
                "description": "Ikki o'yinchiga turli tugmalar berilishining sababi nima?",
                "description_ru": "Почему двум игрокам дают разные клавиши?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Bitta tugma ikkalasini bir vaqtda boshqara olmaydi",
                    "Rang chiroyli bo'lishi uchun",
                    "Ovoz balandroq chiqishi uchun",
                    "Sabab yo'q, shunchaki odat",
                ],
                "options_ru": [
                    "Одна клавиша не может управлять обоими сразу",
                    "Чтобы было красивее",
                    "Чтобы звук был громче",
                    "Причины нет, просто традиция",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Har bir tugma faqat bitta personajga bog'lanadi.",
                "hint_ru": "Каждая клавиша привязана только к одному персонажу.",
                "explanation": "Har bir o'yinchi o'z tugmalari bilan faqat o'z personajini boshqaradi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "2-o'yinchi tugmasi",
                "title_ru": "Клавиша игрока 2",
                "description": "2-o'yinchining o'ngga yurish tugmasini yozing: '___ tugmasi bosilganda'",
                "description_ru": "Напиши клавишу движения вправо у игрока 2: 'когда нажата клавиша ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "d",
                "correct_answers_ru": "d",
                "hint": "WASD'dagi o'ngga mos harf.",
                "hint_ru": "Буква из WASD, соответствующая движению вправо.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "2-o'yinchi skriptini tuzing",
                "title_ru": "Собери скрипт игрока 2",
                "description": "Bloklarni tartibga qo'ying: D tugmasi bosilganda personaj o'ngga suriladi.",
                "description_ru": "Расставь блоки: персонаж двигается вправо по нажатию D.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["d tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "drag_items_ru": ["d tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "correct_order": ["d tugmasi bosilganda", "x ni 10 ga o'zgartir"],
                "hint": "Avval tugma hodisasi, keyin harakat.",
                "hint_ru": "Сначала событие клавиши, потом движение.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Ikki o'yinchi boshqaruvi",
            "task_title_ru": "Проект: управление на двух игроков",
            "task_description": (
                "Scratchda (scratch.mit.edu) ikkita personaj yarating: "
                "1-o'yinchi strelka tugmalari bilan, 2-o'yinchi WASD "
                "tugmalari bilan yursin. Tayyor bo'lgach, Share tugmasi "
                "bilan ulashib, HAVOLASINI yoki ekran rasmini topshiring — "
                "o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Создай в Scratch (scratch.mit.edu) двух персонажей: игрок 1 "
                "двигается стрелками, игрок 2 — клавишами WASD. Когда будет "
                "готово, поделись через кнопку Share и отправь ССЫЛКУ или "
                "скриншот — учитель проверит."
            ),
            "task_requirements": (
                "• 1-o'yinchi kamida ikkita strelka tugmasi bilan yursin\n"
                "• 2-o'yinchi kamida ikkita WASD tugmasi bilan yursin\n"
                "• Ikkalasi bir vaqtda mustaqil boshqarilsin"
            ),
            "task_requirements_ru": (
                "• Игрок 1 двигается минимум двумя стрелками\n"
                "• Игрок 2 двигается минимум двумя клавишами WASD\n"
                "• Оба управляются независимо и одновременно"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Klonlash (Clone)",
        "title_ru": "Клонирование (Clone)",
        "points_reward": 20,
        "text_content": (
            "<h2>Bitta personajdan ko'plab nusxa</h2>"
            "<p>Ba'zan bitta personajdan bir nechta nusxa kerak bo'ladi — "
            "masalan osmondan tushayotgan ko'plab yulduzchalar. Har birini "
            "qo'lda chizish o'rniga, <b>klonlash</b>dan foydalanamiz — bu "
            "<b>Boshqarish</b> guruhida (to'q sariq).</p>"
            "<h2>Uchta muhim blok</h2>"
            "<ul>"
            "<li><span class=\"scratch-block scratch-block--control\">o'zimning nusxamni yasa</span> — "
            "yangi nusxa (klon) yaratadi.</li>"
            "<li><span class=\"scratch-block scratch-block--control\">nusxa sifatida boshlaganimda</span> — "
            "har bir yangi klon shu bloqdan boshlaydi (asl personaj emas).</li>"
            "<li><span class=\"scratch-block scratch-block--control\">bu nusxani o'chir</span> — "
            "klonni yo'q qiladi (ekrandan chiqib ketganda, xotira "
            "to'lib qolmasin).</li>"
            "</ul>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested\">doim</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested2\">1 soniya kut</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested2\">o'zimning nusxamni yasa</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">nusxa sifatida boshlaganimda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "</div>"
            "<p>Birinchi skript har soniyada yangi nusxa yasayveradi. "
            "Ikkinchi skript esa <b>har bir</b> yangi nusxaga alohida "
            "\"pastga tush\" buyrug'ini beradi — go'yo bir nechta yulduzcha "
            "birga tushayotgandek.</p>"
        ),
        "text_content_ru": (
            "<h2>Много копий одного персонажа</h2>"
            "<p>Иногда нужно несколько копий одного персонажа — например "
            "много звёздочек, падающих с неба. Вместо того чтобы рисовать "
            "каждую вручную, используем <b>клонирование</b> — оно в группе "
            "<b>Управление</b> (оранжевые).</p>"
            "<h2>Три важных блока</h2>"
            "<ul>"
            "<li><span class=\"scratch-block scratch-block--control\">o'zimning nusxamni yasa</span> — "
            "создаёт новую копию (клон).</li>"
            "<li><span class=\"scratch-block scratch-block--control\">nusxa sifatida boshlaganimda</span> — "
            "каждый новый клон начинает именно с этого блока (не "
            "с самого персонажа).</li>"
            "<li><span class=\"scratch-block scratch-block--control\">bu nusxani o'chir</span> — "
            "удаляет клон (когда он ушёл с экрана, чтобы не "
            "переполнить память).</li>"
            "</ul>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--events\">yashil bayroq bosilganda</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested\">doim</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested2\">1 soniya kut</span>"
            "<span class=\"scratch-block scratch-block--control scratch-block--nested2\">o'zimning nusxamni yasa</span>"
            "</div>"
            "<div class=\"scratch-script\">"
            "<span class=\"scratch-block scratch-block--control\">nusxa sifatida boshlaganimda</span>"
            "<span class=\"scratch-block scratch-block--motion scratch-block--nested\">y ni -5 ga o'zgartir</span>"
            "</div>"
            "<p>Первый скрипт каждую секунду создаёт новую копию. Второй "
            "скрипт даёт <b>каждой</b> новой копии отдельную команду "
            "«падать вниз» — будто несколько звёздочек падают вместе.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Tushayotgan yulduzchalar",
            "description": "Har soniyada yangi yulduzcha nusxasi paydo bo'lib, pastga tushadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "yulduzchalar.txt",
                    "language": "text",
                    "code": (
                        "yashil bayroq bosilganda\n"
                        "doim\n"
                        "  1 soniya kut\n"
                        "  o'zimning nusxamni yasa\n"
                        "\n"
                        "nusxa sifatida boshlaganimda\n"
                        "doim\n"
                        "  y ni -5 ga o'zgartir\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Klonlash nima uchun kerak?",
                "title_ru": "Зачем нужно клонирование?",
                "description": "Klonlash odatda qachon ishlatiladi?",
                "description_ru": "Когда обычно используют клонирование?",
                "exercise_type": "multiple_choice",
                "options": ["Bitta personajdan ko'plab nusxa kerak bo'lganda", "Rangni o'zgartirganda", "Ovoz yozganda", "Sahnani o'zgartirganda"],
                "options_ru": ["Когда нужно много копий одного персонажа", "Когда меняют цвет", "Когда записывают звук", "Когда меняют сцену"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Masalan, bir nechta yulduzcha bir vaqtda tushishi.",
                "hint_ru": "Например, несколько звёздочек падают одновременно.",
                "explanation": "Klonlash bitta personajdan ko'plab mustaqil nusxa yaratadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Yangi klon qayerdan boshlaydi?",
                "title_ru": "С чего начинает новый клон?",
                "description": "Har bir yangi klon qaysi blokdan ishga tushadi?",
                "description_ru": "С какого блока запускается каждый новый клон?",
                "exercise_type": "multiple_choice",
                "options": ["nusxa sifatida boshlaganimda", "yashil bayroq bosilganda", "bu personaj bosilganda", "hech qaysi biri emas"],
                "options_ru": ["nusxa sifatida boshlaganimda", "yashil bayroq bosilganda", "bu personaj bosilganda", "Ни один из них"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Nomi \"nusxa\" so'zini o'z ichiga oladi.",
                "hint_ru": "В названии есть слово «копия».",
                "explanation": "Har bir klon aynan shu bloqdan o'z ishini boshlaydi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Nusxa yaratish bloki",
                "title_ru": "Блок создания копии",
                "description": "Yangi klon yaratadigan blokni to'ldiring: 'o'zimning ___ni yasa'",
                "description_ru": "Заполни блок создания клона: 'o'zimning ___ni yasa'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "nusxa",
                "correct_answers_ru": "копию",
                "hint": "Klon — bu personajning bir nusxasi.",
                "hint_ru": "Клон — это одна копия персонажа.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Klon yaratish tsiklini tuzing",
                "title_ru": "Собери цикл создания клонов",
                "description": "Bloklarni tartibga qo'ying: har soniyada yangi nusxa yasaladi.",
                "description_ru": "Расставь блоки: каждую секунду создаётся новая копия.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["yashil bayroq bosilganda", "doim", "1 soniya kut", "o'zimning nusxamni yasa"],
                "drag_items_ru": ["yashil bayroq bosilganda", "doim", "1 soniya kut", "o'zimning nusxamni yasa"],
                "correct_order": ["yashil bayroq bosilganda", "doim", "1 soniya kut", "o'zimning nusxamni yasa"],
                "hint": "Boshlanish, cheksiz sikl, kutish, nusxa yasash.",
                "hint_ru": "Начало, бесконечный цикл, ожидание, создание копии.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Tushayotgan nusxalar",
            "task_title_ru": "Проект: падающие копии",
            "task_description": (
                "Scratchda (scratch.mit.edu) bitta personajdan har necha "
                "soniyada yangi nusxa yaratiladigan va har bir nusxa pastga "
                "tushadigan skript yozing. Tayyor bo'lgach, Share tugmasi "
                "bilan ulashib, HAVOLASINI yoki ekran rasmini topshiring — "
                "o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Напиши в Scratch (scratch.mit.edu) скрипт, где новая копия "
                "персонажа создаётся каждые несколько секунд, и каждая "
                "падает вниз. Когда будет готово, поделись через кнопку "
                "Share и отправь ССЫЛКУ или скриншот — учитель проверит."
            ),
            "task_requirements": (
                "• 'o'zimning nusxamni yasa' bloki takroriy chaqirilsin "
                "(masalan doim + kut ichida)\n"
                "• 'nusxa sifatida boshlaganimda' blokidan har bir nusxa "
                "uchun harakat yozilsin\n"
                "• Kamida bir necha nusxa bir vaqtda ekranda ko'rinsin"
            ),
            "task_requirements_ru": (
                "• Блок «создать копию себя» вызывается повторно (например "
                "внутри doim + kut)\n"
                "• Через «когда я начинаю как копия» задано действие для "
                "каждой копии\n"
                "• Несколько копий одновременно видны на экране"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy loyiha: Ikki o'yinchili poyga",
        "title_ru": "Итоговый проект: гонка на двух игроков",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Endi ushbu kursda o'rgangan hamma narsani birlashtirib, "
            "haqiqiy <b>ikki o'yinchili poyga</b> yaratamiz: ikkita "
            "mustaqil personaj (2-dars), signal orqali \"start!\" e'lon "
            "qilish (2-dars), ikkalasi ham o'z tugmalari bilan yurishi "
            "(4-dars), va kim finishga birinchi yetsa, umumiy o'zgaruvchi "
            "orqali g'alaba e'lon qilinadi (3-dars).</p>"
            "<h3>Poyga qanday ishlaydi</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Bayroq bosiladi\"] --> B[\"'start!' signali yuboriladi\"]\n"
            "  B --> C[\"1-o'yinchi: strelkalar bilan yuradi\"]\n"
            "  B --> D[\"2-o'yinchi: WASD bilan yuradi\"]\n"
            "  C --> E{\"Finishga yetdimi?\"}\n"
            "  D --> E\n"
            "  E -->|\"ha\"| F[\"g'olib nomi umumiy o'zgaruvchiga yoziladi\"]\n"
            "</pre>"
            "<p>Ixtiyoriy: yo'l bo'ylab tushayotgan to'siqlarni klonlash "
            "bilan qo'shsangiz (5-dars), poyga yanada qiziqarli bo'ladi!</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>Теперь объединим всё, что выучили в этом курсе, и создадим "
            "настоящую <b>гонку на двух игроков</b>: два независимых "
            "персонажа (урок 2), объявление «старт!» через сигнал (урок "
            "2), оба двигаются своими клавишами (урок 4), и когда кто-то "
            "первым доходит до финиша, победа объявляется через общую "
            "переменную (урок 3).</p>"
            "<h3>Как работает гонка</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Bayroq bosiladi\"] --> B[\"'start!' signali yuboriladi\"]\n"
            "  B --> C[\"1-o'yinchi: strelkalar bilan yuradi\"]\n"
            "  B --> D[\"2-o'yinchi: WASD bilan yuradi\"]\n"
            "  C --> E{\"Finishga yetdimi?\"}\n"
            "  D --> E\n"
            "  E -->|\"да\"| F[\"g'olib nomi umumiy o'zgaruvchiga yoziladi\"]\n"
            "</pre>"
            "<p>Необязательно: если добавишь падающие препятствия через "
            "клонирование (урок 5), гонка станет ещё интереснее!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Ikki o'yinchili poyga",
            "description": "Ikkala o'yinchi ham o'z tugmalari bilan finishga intiladi, g'olib e'lon qilinadi.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "poyga.txt",
                    "language": "text",
                    "code": (
                        "[O'ZGARUVCHI]\n"
                        "g'olib — Barcha personajlar uchun\n"
                        "\n"
                        "[1-O'YINCHI]\n"
                        "yashil bayroq bosilganda\n"
                        "doim\n"
                        "  o'ng strelka tugmasi bosilganda\n"
                        "    x ni 10 ga o'zgartir\n"
                        "  agar <x: 200 ga tegayapti?> bo'lsa\n"
                        "    g'olib ni [1-o'yinchi] ga o'rnat\n"
                        "\n"
                        "[2-O'YINCHI]\n"
                        "yashil bayroq bosilganda\n"
                        "doim\n"
                        "  d tugmasi bosilganda\n"
                        "    x ni 10 ga o'zgartir\n"
                        "  agar <x: 200 ga tegayapti?> bo'lsa\n"
                        "    g'olib ni [2-o'yinchi] ga o'rnat\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Poyga qismlari",
                "title_ru": "Части гонки",
                "description": "Ikki o'yinchili poyga uchun qaysi to'rtta narsa kerak?",
                "description_ru": "Что из четырёх нужно для гонки на двух игроков?",
                "exercise_type": "multiple_choice",
                "options": [
                    "Ikki personaj, ikki xil tugma, finish sharti, g'olib o'zgaruvchisi",
                    "Faqat bitta personaj",
                    "Faqat rang o'zgartirish",
                    "Faqat ovoz",
                ],
                "options_ru": [
                    "Два персонажа, разные клавиши, условие финиша, переменная победителя",
                    "Только один персонаж",
                    "Только смена цвета",
                    "Только звук",
                ],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Kursda o'rgangan hamma mavzuni eslang.",
                "hint_ru": "Вспомни все темы курса.",
                "explanation": "Poyga ikki mustaqil personaj, ularning o'z tugmalari, finish tekshiruvi va umumiy g'olib o'zgaruvchisidan iborat.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "G'olibni qayerda saqlaymiz?",
                "title_ru": "Где хранится победитель?",
                "description": "G'olib nomini ikkala personaj ham yoza olishi uchun o'zgaruvchi qanday bo'lishi kerak?",
                "description_ru": "Какой должна быть переменная, чтобы оба персонажа могли в неё писать?",
                "exercise_type": "multiple_choice",
                "options": ["Barcha personajlar uchun (umumiy)", "Faqat 1-o'yinchi uchun", "Faqat 2-o'yinchi uchun", "Hech qanaqa o'zgaruvchi kerak emas"],
                "options_ru": ["Для всех персонажей (общая)", "Только для игрока 1", "Только для игрока 2", "Переменная не нужна"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "2-darsni eslang.",
                "hint_ru": "Вспомни урок 2.",
                "explanation": "Faqat umumiy o'zgaruvchiga ikkala personaj ham yoza oladi.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Boshlanish signali",
                "title_ru": "Сигнал старта",
                "description": "Poyga boshlanishini hammaga e'lon qilish uchun qaysi mexanizmdan foydalanamiz? To'ldiring: 'xabar1 ni ___'",
                "description_ru": "Какой механизм используем, чтобы объявить старт всем? Заполни: 'xabar1 ni ___'",
                "exercise_type": "fill_in_blank",
                "correct_answers": "yubor",
                "correct_answers_ru": "yubor",
                "hint": "1-darsda o'rgangan blok.",
                "hint_ru": "Блок из урока 1.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Poyga mantiqini tartibga soling",
                "title_ru": "Расставь логику гонки",
                "description": "Poyganing asosiy bosqichlarini to'g'ri tartibga qo'ying.",
                "description_ru": "Расставь основные шаги гонки в правильном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Bayroq bosiladi", "Signal yuboriladi", "O'yinchilar tugmalar bilan yuradi", "Finishga yetgan g'olib bo'ladi"],
                "drag_items_ru": ["Нажимается флаг", "Отправляется сигнал", "Игроки двигаются клавишами", "Достигший финиша побеждает"],
                "correct_order": ["Bayroq bosiladi", "Signal yuboriladi", "O'yinchilar tugmalar bilan yuradi", "Finishga yetgan g'olib bo'ladi"],
                "hint": "Boshlanishdan g'alabagacha ketma-ketlikda o'ylang.",
                "hint_ru": "Думай по порядку от начала до победы.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Mening ikki o'yinchili poygam",
            "task_title_ru": "Итоговый проект: моя гонка на двоих",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: ikkita "
                "mustaqil personaj, har biri o'z tugmalari bilan yursin, "
                "signal orqali o'yin boshlansin, va kim birinchi finishga "
                "yetsa, uning nomi umumiy \"g'olib\" o'zgaruvchisiga "
                "yozilsin. Tayyor bo'lgach, Share tugmasi bilan ulashib, "
                "HAVOLASINI yoki ekran rasmini topshiring — bu sizning eng "
                "katta Scratch loyihangiz!"
            ),
            "task_description_ru": (
                "Объедини всё, что выучил в курсе: два независимых "
                "персонажа, каждый двигается своими клавишами, игра "
                "начинается по сигналу, а имя того, кто первым дошёл до "
                "финиша, записывается в общую переменную «g'olib». Когда "
                "будет готово, поделись через кнопку Share и отправь "
                "ССЫЛКУ или скриншот — это твой самый большой проект в "
                "Scratch!"
            ),
            "task_requirements": (
                "• Ikkita mustaqil personaj bo'lsin (1-dars)\n"
                "• O'yin signal orqali boshlansin (2-dars)\n"
                "• Har bir o'yinchi o'zining tugmalari bilan yursin (4-dars)\n"
                "• Finishga yetgan o'yinchining nomi umumiy o'zgaruvchiga "
                "yozilsin (3-dars)"
            ),
            "task_requirements_ru": (
                "• Два независимых персонажа (урок 1)\n"
                "• Игра начинается по сигналу (урок 2)\n"
                "• Каждый игрок двигается своими клавишами (урок 4)\n"
                "• Имя дошедшего до финиша записывается в общую переменную "
                "(урок 3)"
            ),
            "task_technologies": "Scratch",
            "task_deadline_days": 5,
        },
    },
]
