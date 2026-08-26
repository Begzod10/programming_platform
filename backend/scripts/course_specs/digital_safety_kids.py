"""Digital safety & online etiquette course for children aged 7-12
(Uzbek-primary, Russian translations).

Not a coding course — the platform's first non-programming kids course.
Standalone (no prerequisite): a child can take this before, after, or
alongside any Scratch/Python/Web course. Covers password hygiene, staying
safe around strangers online, recognizing scam/phishing messages, healthy
screen-time habits, and cyberbullying (recognizing it, responding to it, and
not doing it to others).

This content type doesn't fit the platform's usual "submit runnable code"
task shape, so every task here asks for a WRITTEN or DRAWN deliverable
(a short paragraph, a numbered list, a hand-made poster) submitted as text
or a photo — task_technologies is "Yozma javob" ("Written response") or
"Rasm/Matn" instead of a programming language, same idea as the Scratch
courses' "share a link or screenshot" pattern for content that can't run in
the platform. Every `sample` still exists for consistency with every other
kids course, but shows a worked example dialogue/scenario as sample_type
"code" with language "text" (matching the Scratch courses' own use of
sample_type "code" for non-executable illustrative content) rather than
runnable code.

Reviewed by a human before seeding; is_published stays False.
"""

COURSE = {
    "title": "Raqamli xavfsizlik va internet odobi (bolalar uchun)",
    "title_ru": "Цифровая безопасность и этикет в интернете (для детей)",
    "description": (
        "7-12 yoshdagi bolalar uchun internetda xavfsiz va odobli bo'lishni "
        "o'rgatuvchi kurs. Kuchli parol yaratishni, notanish odamlar bilan "
        "ehtiyot bo'lishni, yolg'on xabarlarni tanishni, ekran vaqtini "
        "boshqarishni va onlayn mehribon bo'lishni o'rganamiz hamda "
        "o'zimizning shaxsiy xavfsizlik qoidalarimizni tuzamiz."
    ),
    "description_ru": (
        "Курс для детей 7-12 лет: как быть в безопасности и вежливым в "
        "интернете. Научимся создавать надёжный пароль, быть осторожными с "
        "незнакомцами, распознавать поддельные сообщения, управлять "
        "экранным временем и быть добрыми онлайн, а также составим свои "
        "личные правила безопасности."
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
        "title": "Parol siri",
        "title_ru": "Секрет пароля",
        "points_reward": 15,
        "text_content": (
            "<h2>Parol nima uchun kerak?</h2>"
            "<p>Parol — bu sizning hisobingizni (masalan o'yin yoki elektron "
            "pochta) boshqalardan <b>himoya qiladigan</b> maxfiy so'z. Agar "
            "kimdir sizning parolingizni bilib olsa, u sizning nomingizdan "
            "yozishi yoki narsalaringizni o'g'irlashi mumkin.</p>"
            "<h2>Kuchli parol qanday bo'ladi?</h2><ul>"
            "<li>Kamida <b>8 ta belgi</b>dan iborat bo'lsin</li>"
            "<li>Harflar, raqamlar va belgilarni <b>aralashtiring</b> "
            "(masalan: Yulduz2026!)</li>"
            "<li>Ismingiz yoki tug'ilgan sanangizni ishlatmang — buni topish "
            "oson</li>"
            "<li>Har bir sayt uchun <b>boshqa</b> parol qo'ying</li></ul>"
            "<h2>Parolni kim bilishi mumkin?</h2>"
            "<p>Parolingizni <b>hech kimga</b> aytmang — hatto eng yaqin "
            "do'stingizga ham. Faqat ota-onangiz bilishi mumkin, chunki ular "
            "sizga yordam berishlari kerak bo'lishi mumkin.</p>"
        ),
        "text_content_ru": (
            "<h2>Зачем нужен пароль?</h2>"
            "<p>Пароль — это секретное слово, которое <b>защищает</b> ваш "
            "аккаунт (например, игру или почту) от других. Если кто-то "
            "узнает ваш пароль, он может писать от вашего имени или украсть "
            "ваши вещи.</p>"
            "<h2>Каким бывает надёжный пароль?</h2><ul>"
            "<li>Минимум <b>8 символов</b></li>"
            "<li><b>Смешивайте</b> буквы, цифры и знаки (например: "
            "Yulduz2026!)</li>"
            "<li>Не используйте своё имя или дату рождения — их легко "
            "угадать</li>"
            "<li>Для каждого сайта — <b>свой</b> пароль</li></ul>"
            "<h2>Кто может знать пароль?</h2>"
            "<p>Никогда не говорите пароль <b>никому</b> — даже лучшему "
            "другу. Знать его могут только родители, потому что им может "
            "понадобиться помочь вам.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Kuchli va zaif parol",
            "description": "Ikki xil parolni solishtiramiz.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "parol.txt",
                    "language": "text",
                    "code": (
                        "ZAIF PAROL: salom123\n"
                        "(ism yoki oddiy so'z + son — topish oson)\n"
                        "\n"
                        "KUCHLI PAROL: Y#7mReng!92\n"
                        "(harflar, sonlar, belgilar aralash — topish qiyin)\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kuchli parol tarkibi",
                "title_ru": "Состав надёжного пароля",
                "description": "Kuchli parolda nima bo'lishi kerak?",
                "description_ru": "Что должно быть в надёжном пароле?",
                "exercise_type": "multiple_choice",
                "options": ["Harf, son va belgilar aralash", "Faqat ismingiz", "Faqat sonlar", "Bo'sh joy"],
                "options_ru": ["Смешанные буквы, цифры и знаки", "Только ваше имя", "Только цифры", "Пробел"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Aralash bo'lsa, topish qiyinroq.",
                "hint_ru": "Чем более смешанный, тем труднее угадать.",
                "explanation": "Kuchli parolda harf, son va belgi aralash bo'ladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Parolni kimga aytish mumkin?",
                "title_ru": "Кому можно сказать пароль?",
                "description": "Parolingizni kimga aytish mumkin?",
                "description_ru": "Кому можно рассказать свой пароль?",
                "exercise_type": "multiple_choice",
                "options": ["Faqat ota-onangizga", "Eng yaqin do'stingizga", "Sinfdoshlaringizga", "Hammaga"],
                "options_ru": ["Только родителям", "Лучшему другу", "Одноклассникам", "Всем"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Faqat sizga yordam berishi kerak bo'lganlar.",
                "hint_ru": "Только тем, кому может понадобиться вам помочь.",
                "explanation": "Parolni faqat ota-onangiz bilishi kerak.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Minimal uzunlik",
                "title_ru": "Минимальная длина",
                "description": "Kuchli parol kamida nechta belgidan iborat bo'lishi kerak? Javob: ___",
                "description_ru": "Из скольки символов минимум должен состоять надёжный пароль? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "8",
                "hint": "Darsda aytilgan son.",
                "hint_ru": "Число из урока.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Kuchli parol qoidalarini tuzing",
                "title_ru": "Собери правила надёжного пароля",
                "description": "Bloklarni tartibga qo'ying: kuchli parol yaratish qadamlari.",
                "description_ru": "Расставь блоки: шаги создания надёжного пароля.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Harflar, sonlar va belgilarni aralashtir", "Ismingiz yoki tug'ilgan sanangizni ishlatma", "Har bir sayt uchun boshqa parol qo'y", "Hech kimga aytma"],
                "drag_items_ru": ["Смешай буквы, цифры и знаки", "Не используй имя или дату рождения", "Для каждого сайта свой пароль", "Никому не говори"],
                "correct_order": ["Harflar, sonlar va belgilarni aralashtir", "Ismingiz yoki tug'ilgan sanangizni ishlatma", "Har bir sayt uchun boshqa parol qo'y", "Hech kimga aytma"],
                "hint": "Barcha to'rt qoida ham teng muhim — mantiqiy tartibda joylashtiring.",
                "hint_ru": "Все четыре правила важны — расставь в логичном порядке.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mening parol qoidalarim",
            "task_title_ru": "Проект: мои правила пароля",
            "task_description": (
                "O'zingiz uchun 3 ta kuchli parol namunasi o'ylab toping "
                "(haqiqiy parolingizni EMAS!) va nima uchun ular kuchli "
                "ekanini tushuntirib yozing. Matningizni fayl qilib yoki "
                "qog'ozga yozib, suratga olib topshiring — o'qituvchi "
                "tekshiradi."
            ),
            "task_description_ru": (
                "Придумай 3 примера надёжного пароля (НЕ свой настоящий "
                "пароль!) и напиши, почему они надёжные. Отправь текст "
                "файлом или сфотографируй запись на бумаге — учитель "
                "проверит."
            ),
            "task_requirements": (
                "• Kamida 3 ta parol namunasi bo'lsin\n"
                "• Har birida harf, son va belgi aralash bo'lsin\n"
                "• Har biri uchun nega kuchli ekani tushuntirilsin"
            ),
            "task_requirements_ru": (
                "• Минимум 3 примера пароля\n"
                "• В каждом смешаны буквы, цифры и знаки\n"
                "• Для каждого объяснено, почему он надёжный"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 1
    {
        "order": 1,
        "title": "Notanish odamlar bilan onlayn muomala",
        "title_ru": "Общение с незнакомцами онлайн",
        "points_reward": 20,
        "text_content": (
            "<h2>Internet haqiqiy dunyoga o'xshaydi</h2>"
            "<p>Ko'chada notanish odam bilan gaplashib, unga uyingiz "
            "manzilini aytmaganingiz kabi, internetda ham notanish odamlarga "
            "shaxsiy ma'lumot bermaslik kerak.</p>"
            "<h2>Hech qachon aytmang</h2><ul>"
            "<li>To'liq ismingiz va familiyangiz</li>"
            "<li>Uy manzilingiz yoki maktabingiz nomi</li>"
            "<li>Telefon raqamingiz</li>"
            "<li>O'zingizning yoki oilangizning fotosuratlari</li></ul>"
            "<h2>Agar kimdir g'alati narsa so'rasa</h2><ol>"
            "<li>Javob bermang</li>"
            "<li>Suhbatni yoping yoki bloklang</li>"
            "<li>Darhol ota-onangizga yoki ishonchli kattaga ayting</li></ol>"
            "<p>Bu — sizning aybingiz emas, va yordam so'rash har doim "
            "to'g'ri!</p>"
        ),
        "text_content_ru": (
            "<h2>Интернет похож на настоящий мир</h2>"
            "<p>Как на улице вы не сообщаете незнакомцу домашний адрес, так "
            "и в интернете нельзя давать незнакомым людям личную "
            "информацию.</p>"
            "<h2>Никогда не говорите</h2><ul>"
            "<li>Полное имя и фамилию</li>"
            "<li>Домашний адрес или название школы</li>"
            "<li>Номер телефона</li>"
            "<li>Свои фото или фото семьи</li></ul>"
            "<h2>Если кто-то спрашивает странное</h2><ol>"
            "<li>Не отвечайте</li>"
            "<li>Закройте разговор или заблокируйте</li>"
            "<li>Сразу расскажите родителям или взрослому, которому "
            "доверяете</li></ol>"
            "<p>Это не ваша вина, и просить о помощи — всегда правильно!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Noto'g'ri va to'g'ri javob",
            "description": "Notanish odamning savoliga ikki xil javob.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "muomala.txt",
                    "language": "text",
                    "code": (
                        "NOTANISH ODAM: Salom! Uying qayerda, kim bilan yashaysan?\n"
                        "\n"
                        "NOTO'G'RI JAVOB: Men Toshkentda, Chilonzor tumanida, onam bilan yashayman...\n"
                        "(shaxsiy ma'lumot berilgan — xavfli!)\n"
                        "\n"
                        "TO'G'RI JAVOB: Kechirasiz, men bunday narsalarni notanishlarga aytmayman.\n"
                        "(suhbatni yopib, ota-onaga aytish kerak)\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Nimani aytmaslik kerak?",
                "title_ru": "Что нельзя говорить?",
                "description": "Notanish odamga nimani aytmaslik kerak?",
                "description_ru": "Что нельзя говорить незнакомцу?",
                "exercise_type": "multiple_choice",
                "options": ["Uy manzilingizni", "Sevimli rangingizni", "Sevimli o'yiningizni", "Sevimli hayvoningizni"],
                "options_ru": ["Домашний адрес", "Любимый цвет", "Любимую игру", "Любимое животное"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Bu sizni topib olishga yordam beradigan ma'lumot.",
                "hint_ru": "Это информация, которая поможет вас найти.",
                "explanation": "Uy manzili shaxsiy va xavfli ma'lumot hisoblanadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Birinchi qadam",
                "title_ru": "Первый шаг",
                "description": "Agar notanish kishi g'alati narsa so'rasa, birinchi qadam nima?",
                "description_ru": "Если незнакомец спрашивает странное, каков первый шаг?",
                "exercise_type": "multiple_choice",
                "options": ["Javob bermaslik", "Darhol manzilni aytish", "Uchrashuvga rozi bo'lish", "Rasm yuborish"],
                "options_ru": ["Не отвечать", "Сразу сказать адрес", "Согласиться на встречу", "Отправить фото"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Eng xavfsiz birinchi harakat.",
                "hint_ru": "Самое безопасное первое действие.",
                "explanation": "Shubhali savolga javob bermaslik eng xavfsiz birinchi qadam.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kimga aytish kerak",
                "title_ru": "Кому рассказать",
                "description": "Agar notanish kishidan xavotir sezsangiz, kimga aytishingiz kerak? Javob: ___",
                "description_ru": "Если незнакомец вас насторожил, кому нужно рассказать? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "ota-onaga",
                "correct_answers_ru": "родителям",
                "hint": "Sizga eng yaqin, ishonchli kattalar.",
                "hint_ru": "Самые близкие и надёжные взрослые.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "To'g'ri javob tartibini tuzing",
                "title_ru": "Собери порядок правильных действий",
                "description": "Bloklarni tartibga qo'ying: shubhali suhbatga to'g'ri javob.",
                "description_ru": "Расставь блоки: правильная реакция на подозрительный разговор.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Javob berma", "Suhbatni yop", "Ota-onangga ayt"],
                "drag_items_ru": ["Не отвечай", "Закрой разговор", "Расскажи родителям"],
                "correct_order": ["Javob berma", "Suhbatni yop", "Ota-onangga ayt"],
                "hint": "Avval to'xta, keyin yop, oxirida kattalarga ayt.",
                "hint_ru": "Сначала остановись, потом закрой, потом расскажи взрослым.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Xavfsizlik posteri",
            "task_title_ru": "Проект: постер безопасности",
            "task_description": (
                "Notanish odamlar bilan onlayn gaplashish uchun 3 ta "
                "qoidadan iborat kichik poster chizing yoki yozing. Postering "
                "yoki matningizni suratga olib topshiring — o'qituvchi "
                "tekshiradi."
            ),
            "task_description_ru": (
                "Нарисуй или напиши небольшой постер с 3 правилами общения с "
                "незнакомцами онлайн. Сфотографируй постер или текст и "
                "отправь — учитель проверит."
            ),
            "task_requirements": (
                "• Kamida 3 ta qoida yozilsin\n"
                "• Har biri aniq va tushunarli bo'lsin\n"
                "• Poster yoki matn suratga olib yuborilsin"
            ),
            "task_requirements_ru": (
                "• Минимум 3 правила\n"
                "• Каждое понятное и чёткое\n"
                "• Постер или текст отправлен фото"
            ),
            "task_technologies": "Rasm/Matn",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "order": 2,
        "title": "Yolg'on xabarlarni tanish",
        "title_ru": "Распознаём поддельные сообщения",
        "points_reward": 20,
        "text_content": (
            "<h2>\"Siz yutuq yutdingiz!\"</h2>"
            "<p>Ba'zan ekranda yoki xabarlarda \"Tabriklaymiz! Siz telefon "
            "yutdingiz, shu yerni bosing!\" kabi xabarlar chiqadi. Bular "
            "ko'pincha <b>yolg'on</b> — ular sizning ma'lumotlaringizni "
            "o'g'irlash yoki kompyuteringizga zararli dastur yuklash uchun "
            "yaratilgan.</p>"
            "<h2>Shubhali xabarning belgilari</h2><ul>"
            "<li>Juda <b>yaxshi</b> tuyuladi (bepul telefon, pul, o'yin)</li>"
            "<li><b>Shoshiling!</b> yoki <b>Hozir bosing!</b> deb turtki "
            "beradi</li>"
            "<li>Shaxsiy ma'lumot yoki parol so'raydi</li>"
            "<li>Notanish yoki g'alati havoladan (link) keladi</li></ul>"
            "<h2>Nima qilish kerak?</h2>"
            "<p>Shubhali havolani <b>bosmang</b>. Ekran rasmini olib, "
            "ota-onangizga yoki o'qituvchingizga ko'rsating.</p>"
        ),
        "text_content_ru": (
            "<h2>«Вы выиграли приз!»</h2>"
            "<p>Иногда на экране или в сообщениях появляется «Поздравляем! "
            "Вы выиграли телефон, нажмите сюда!». Такие сообщения часто "
            "<b>поддельные</b> — их создают, чтобы украсть вашу информацию "
            "или загрузить вредоносную программу на компьютер.</p>"
            "<h2>Признаки подозрительного сообщения</h2><ul>"
            "<li>Звучит слишком <b>хорошо</b> (бесплатный телефон, деньги, "
            "игра)</li>"
            "<li>Подгоняет: <b>Торопись!</b> или <b>Нажми сейчас!</b></li>"
            "<li>Просит личные данные или пароль</li>"
            "<li>Приходит по незнакомой или странной ссылке</li></ul>"
            "<h2>Что делать?</h2>"
            "<p><b>Не нажимайте</b> подозрительную ссылку. Сделайте "
            "скриншот и покажите родителям или учителю.</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Shubhali xabar",
            "description": "Yolg'on xabar va unga to'g'ri javob.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "shubhali_xabar.txt",
                    "language": "text",
                    "code": (
                        "NOTO'G'RI: 'Tabriklaymiz! Siz iPhone yutdingiz! Shu yerni bosing: bit.ly/sovga123'\n"
                        "(shubhali qisqa havola, juda yaxshi va'da, shoshiltiradi)\n"
                        "\n"
                        "TO'G'RI HARAKAT: Havolani bosmang. Skrinshot oling. Ota-onangizga ko'rsating.\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Yolg'on xabar belgisi",
                "title_ru": "Признак поддельного сообщения",
                "description": "Qaysi belgi xabarning yolg'on ekanini bildiradi?",
                "description_ru": "Какой признак указывает, что сообщение поддельное?",
                "exercise_type": "multiple_choice",
                "options": ["Juda yaxshi va'da beradi va shoshiltiradi", "Chiroyli rasm bor", "Uzun matn", "Kulgichlar bor"],
                "options_ru": ["Слишком хорошее обещание и спешка", "Есть красивая картинка", "Длинный текст", "Есть смайлики"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Juda yaxshi tuyulsa, ehtimol yolg'on.",
                "hint_ru": "Если звучит слишком хорошо — вероятно, обман.",
                "explanation": "Juda yaxshi va'da + shoshiltirish — yolg'on xabarning tipik belgisi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Shubhali havola ko'rsangiz",
                "title_ru": "Если видишь подозрительную ссылку",
                "description": "Shubhali havolani ko'rsangiz nima qilish kerak?",
                "description_ru": "Что делать, если видишь подозрительную ссылку?",
                "exercise_type": "multiple_choice",
                "options": ["Bosmaslik va kattalarga aytish", "Darhol bosish", "Do'stlaringizga yuborish", "Parolingizni kiritish"],
                "options_ru": ["Не нажимать и рассказать взрослым", "Сразу нажать", "Отправить друзьям", "Ввести пароль"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Bosmaslik eng xavfsiz.",
                "hint_ru": "Не нажимать — самое безопасное.",
                "explanation": "Shubhali havolani bosmang, kattalarga ko'rsating.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kimga ko'rsatish kerak",
                "title_ru": "Кому показать",
                "description": "Shubhali xabar ko'rganda uni kimga ko'rsatish kerak? Javob: ___",
                "description_ru": "Кому нужно показать подозрительное сообщение? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "ota-onaga",
                "correct_answers_ru": "родителям",
                "hint": "Eng ishonchli kattalar.",
                "hint_ru": "Самые надёжные взрослые.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "To'g'ri harakat tartibini tuzing",
                "title_ru": "Собери порядок правильных действий",
                "description": "Bloklarni tartibga qo'ying: shubhali xabar ko'rgandagi harakatlar.",
                "description_ru": "Расставь блоки: действия при подозрительном сообщении.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Shubhali xabarni ko'rasiz", "Havolani bosmaysiz", "Skrinshot olasiz", "Kattalarga ko'rsatasiz"],
                "drag_items_ru": ["Видишь подозрительное сообщение", "Не нажимаешь ссылку", "Делаешь скриншот", "Показываешь взрослым"],
                "correct_order": ["Shubhali xabarni ko'rasiz", "Havolani bosmaysiz", "Skrinshot olasiz", "Kattalarga ko'rsatasiz"],
                "hint": "Ko'rish, bosmaslik, dalil olish, kattalarga aytish.",
                "hint_ru": "Увидеть, не нажимать, сохранить доказательство, рассказать взрослым.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Yolg'on xabarni top",
            "task_title_ru": "Проект: найди поддельное сообщение",
            "task_description": (
                "O'zingiz shubhali xabar namunasini o'ylab toping (haqiqiy "
                "havola EMAS, faqat matn misoli). Nima uchun u shubhali "
                "ekanini kamida 2 ta sabab bilan tushuntiring va nima qilish "
                "kerakligini yozing. Matningizni topshiring — o'qituvchi "
                "tekshiradi."
            ),
            "task_description_ru": (
                "Придумай пример подозрительного сообщения (НЕ настоящую "
                "ссылку, просто текст-пример). Объясни минимум двумя "
                "причинами, почему оно подозрительное, и напиши, что нужно "
                "делать. Отправь текст — учитель проверит."
            ),
            "task_requirements": (
                "• Shubhali xabar namunasi yozilsin (o'zingiz o'ylab toping, "
                "haqiqiy havola emas)\n"
                "• Nega u shubhali ekani kamida 2 ta sabab bilan "
                "tushuntirilsin\n"
                "• Nima qilish kerakligi yozilsin"
            ),
            "task_requirements_ru": (
                "• Написан пример подозрительного сообщения (придуманный, "
                "не настоящая ссылка)\n"
                "• Объяснены минимум 2 причины подозрительности\n"
                "• Написано, что нужно делать"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "order": 3,
        "title": "Ekran vaqti va sog'lom foydalanish",
        "title_ru": "Экранное время и здоровое использование",
        "points_reward": 20,
        "text_content": (
            "<h2>Nega tanaffus kerak?</h2>"
            "<p>Kompyuter yoki telefonda uzoq vaqt o'tirish ko'zlaringizni "
            "charchatishi, uyqungizni buzishi va boshqa qiziqarli narsalar "
            "(sport, do'stlar, kitob) uchun vaqt qoldirmasligi mumkin.</p>"
            "<h2>20-20-20 qoidasi</h2>"
            "<p>Har <b>20 daqiqada</b>, <b>20 soniya</b> davomida <b>20 "
            "fut</b> (taxminan 6 metr) uzoqlikdagi narsaga qarang — bu "
            "ko'zlaringizni dam oldiradi.</p>"
            "<h2>Sog'lom odatlar</h2><ul>"
            "<li>Uxlashdan 1 soat oldin ekranni o'chiring</li>"
            "<li>Ovqatlanayotganda ekranga qaramang</li>"
            "<li>Har kuni tashqarida yoki sport bilan vaqt o'tkazing</li>"
            "<li>Ekran vaqtini ota-onangiz bilan birga rejalashtiring</li></ul>"
        ),
        "text_content_ru": (
            "<h2>Зачем нужны перерывы?</h2>"
            "<p>Долгое сидение за компьютером или телефоном утомляет глаза, "
            "мешает сну и не оставляет времени на другие интересные вещи "
            "(спорт, друзья, книги).</p>"
            "<h2>Правило 20-20-20</h2>"
            "<p>Каждые <b>20 минут</b> в течение <b>20 секунд</b> смотрите "
            "на предмет на расстоянии <b>20 футов</b> (примерно 6 метров) — "
            "это отдыхает глаза.</p>"
            "<h2>Здоровые привычки</h2><ul>"
            "<li>Выключайте экран за час до сна</li>"
            "<li>Не смотрите в экран во время еды</li>"
            "<li>Каждый день проводите время на улице или занимайтесь "
            "спортом</li>"
            "<li>Планируйте экранное время вместе с родителями</li></ul>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Balanslangan kunlik reja",
            "description": "Ekran vaqti va boshqa faoliyatlar orasidagi balans.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "kunlik_reja.txt",
                    "language": "text",
                    "code": (
                        "08:00 — Uyg'onish\n"
                        "09:00-10:00 — Dars/kodlash\n"
                        "10:00-10:05 — Tanaffus (ko'zni dam oldirish)\n"
                        "16:00-17:00 — Sport yoki tashqarida o'yin\n"
                        "20:00 — Ekranlarni o'chirish, kitob o'qish\n"
                        "21:00 — Uyqu\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "20-20-20 qoidasi",
                "title_ru": "Правило 20-20-20",
                "description": "20-20-20 qoidasi nima uchun ishlatiladi?",
                "description_ru": "Для чего используется правило 20-20-20?",
                "exercise_type": "multiple_choice",
                "options": ["Ko'zlarni dam oldirish uchun", "Tezroq o'ynash uchun", "Ovqatlanish uchun", "Uxlash uchun"],
                "options_ru": ["Чтобы отдохнули глаза", "Чтобы быстрее играть", "Чтобы поесть", "Чтобы поспать"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ekrandan uzoqqa qarash haqida.",
                "hint_ru": "Про взгляд вдаль от экрана.",
                "explanation": "20-20-20 qoidasi ko'z charchashining oldini oladi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Uxlashdan oldin",
                "title_ru": "Перед сном",
                "description": "Uxlashdan oldin nima qilish tavsiya etiladi?",
                "description_ru": "Что рекомендуется делать перед сном?",
                "exercise_type": "multiple_choice",
                "options": ["Ekranni o'chirish", "Ko'proq o'ynash", "Video ko'rish", "Xabar yozish"],
                "options_ru": ["Выключить экран", "Играть больше", "Смотреть видео", "Писать сообщения"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Yaxshi uyqu uchun ekransiz vaqt kerak.",
                "hint_ru": "Для хорошего сна нужно время без экрана.",
                "explanation": "Uxlashdan 1 soat oldin ekranni o'chirish uyqu sifatini yaxshilaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Tanaffus vaqti",
                "title_ru": "Время перерыва",
                "description": "20-20-20 qoidasida har necha daqiqada tanaffus qilinadi? Javob: ___",
                "description_ru": "Каждые сколько минут делается перерыв в правиле 20-20-20? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "20",
                "hint": "Qoida nomidagi birinchi son.",
                "hint_ru": "Первое число в названии правила.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Balanslangan kunni tuzing",
                "title_ru": "Собери сбалансированный день",
                "description": "Bloklarni tartibga qo'ying: sog'lom kun rejasi.",
                "description_ru": "Расставь блоки: план здорового дня.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Dars/kodlash", "Tanaffus", "Sport yoki o'yin", "Ekranlarni o'chirish"],
                "drag_items_ru": ["Учёба/кодинг", "Перерыв", "Спорт или игра", "Выключить экраны"],
                "correct_order": ["Dars/kodlash", "Tanaffus", "Sport yoki o'yin", "Ekranlarni o'chirish"],
                "hint": "Kun davomida ekran va harakatni almashtiring, kechqurun ekranni o'chiring.",
                "hint_ru": "Чередуй экран и движение днём, вечером выключи экран.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mening kunlik rejam",
            "task_title_ru": "Проект: мой распорядок дня",
            "task_description": (
                "O'zingiz uchun balanslangan kunlik reja yozing — dars/"
                "kodlash, tanaffus, sport va uyqu vaqtlarini kiriting. "
                "Matningizni topshiring — o'qituvchi tekshiradi."
            ),
            "task_description_ru": (
                "Напиши свой сбалансированный распорядок дня — включи время "
                "учёбы/кодинга, перерывов, спорта и сна. Отправь текст — "
                "учитель проверит."
            ),
            "task_requirements": (
                "• Kamida 4 ta faoliyat turi bo'lsin (dars, tanaffus, sport, "
                "uyqu)\n"
                "• Ekran vaqti va ekransiz vaqt balansda bo'lsin\n"
                "• Reja aniq vaqtlar bilan yozilsin"
            ),
            "task_requirements_ru": (
                "• Минимум 4 вида активности (учёба, перерыв, спорт, сон)\n"
                "• Баланс экранного и неэкранного времени\n"
                "• План с конкретным временем"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 3,
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "order": 4,
        "title": "Kiber-bulling (onlayn xafa qilish)",
        "title_ru": "Кибербуллинг",
        "points_reward": 20,
        "text_content": (
            "<h2>Onlayn xafa qilish nima?</h2>"
            "<p><b>Kiber-bulling</b> — bu birovni internet yoki telefon "
            "orqali doimiy ravishda xafa qilish, masxaralash yoki "
            "qo'rqitish. Bu chatda, o'yinlarda yoki ijtimoiy tarmoqlarda "
            "bo'lishi mumkin.</p>"
            "<h2>Agar sizni xafa qilishsa</h2><ol>"
            "<li>Javob <b>bermang</b> — bahslashish holatni yomonlashtirishi "
            "mumkin</li>"
            "<li>Suhbatni <b>bloklang</b></li>"
            "<li>Skrinshot oling (dalil sifatida)</li>"
            "<li>Ishonchli kattaga <b>ayting</b></li></ol>"
            "<h2>O'zingiz ham mehribon bo'ling</h2>"
            "<p>Boshqalarga internetda ham xuddi hayotdagidek <b>mehribon</b> "
            "bo'ling. Yozishdan oldin o'ylab ko'ring: \"Buni yuzma-yuz "
            "aytarmidim?\"</p>"
        ),
        "text_content_ru": (
            "<h2>Что такое онлайн-травля?</h2>"
            "<p><b>Кибербуллинг</b> — это постоянные обиды, насмешки или "
            "запугивание кого-то через интернет или телефон. Это может "
            "происходить в чате, играх или соцсетях.</p>"
            "<h2>Если вас обижают</h2><ol>"
            "<li><b>Не отвечайте</b> — спор может ухудшить ситуацию</li>"
            "<li><b>Заблокируйте</b> разговор</li>"
            "<li>Сделайте скриншот (как доказательство)</li>"
            "<li><b>Расскажите</b> взрослому, которому доверяете</li></ol>"
            "<h2>Будьте добры и сами</h2>"
            "<p>Будьте <b>добры</b> к другим в интернете так же, как в "
            "жизни. Прежде чем написать, подумайте: «Сказал бы я это лицом "
            "к лицу?»</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Xafa qiluvchi xabar",
            "description": "Xafa qiluvchi xabarga to'g'ri javob.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "kiberbulling.txt",
                    "language": "text",
                    "code": (
                        "XAFA QILUVCHI XABAR: 'Sen juda ahmoqsan, hech kim sen bilan o'ynamaydi!'\n"
                        "\n"
                        "TO'G'RI HARAKAT: Javob bermang. Skrinshot oling. Bloklang. Kattalarga ayting.\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kiber-bulling nima?",
                "title_ru": "Что такое кибербуллинг?",
                "description": "Kiber-bulling nima?",
                "description_ru": "Что такое кибербуллинг?",
                "exercise_type": "multiple_choice",
                "options": ["Internet orqali birovni doimiy xafa qilish", "Internet orqali o'ynash", "Video ko'rish", "Musiqa tinglash"],
                "options_ru": ["Постоянные обиды кого-то через интернет", "Игра через интернет", "Просмотр видео", "Прослушивание музыки"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Bu — internetdagi doimiy xafa qilish.",
                "hint_ru": "Это постоянная травля в интернете.",
                "explanation": "Kiber-bulling — internet orqali birovni doimiy xafa qilish yoki qo'rqitish.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Birinchi qilmasligingiz kerak",
                "title_ru": "Что не стоит делать первым",
                "description": "Sizni onlayn xafa qilishsa, birinchi nima qilmaslik kerak?",
                "description_ru": "Если вас обижают онлайн, чего не стоит делать первым?",
                "exercise_type": "multiple_choice",
                "options": ["Bahslashib javob berish", "Skrinshot olish", "Bloklash", "Kattalarga aytish"],
                "options_ru": ["Спорить в ответ", "Сделать скриншот", "Заблокировать", "Рассказать взрослым"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Bahslashish holatni yomonlashtirishi mumkin.",
                "hint_ru": "Спор может ухудшить ситуацию.",
                "explanation": "Bahslashib javob berish holatni yomonlashtirishi mumkin, shuning uchun bunday qilmaslik kerak.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Dalil sifatida",
                "title_ru": "В качестве доказательства",
                "description": "Xafa qiluvchi xabarlarni dalil sifatida saqlash uchun nima olish kerak? Javob: ___",
                "description_ru": "Что нужно сделать, чтобы сохранить обидное сообщение как доказательство? Ответ: ___",
                "exercise_type": "fill_in_blank",
                "correct_answers": "skrinshot",
                "correct_answers_ru": "скриншот",
                "hint": "Ekranning suratini olish.",
                "hint_ru": "Сфотографировать экран.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "To'g'ri harakat tartibini tuzing",
                "title_ru": "Собери порядок правильных действий",
                "description": "Bloklarni tartibga qo'ying: onlayn xafa qilishga to'g'ri javob.",
                "description_ru": "Расставь блоки: правильная реакция на онлайн-травлю.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Javob berma", "Skrinshot ol", "Blokla", "Kattalarga ayt"],
                "drag_items_ru": ["Не отвечай", "Сделай скриншот", "Заблокируй", "Расскажи взрослым"],
                "correct_order": ["Javob berma", "Skrinshot ol", "Blokla", "Kattalarga ayt"],
                "hint": "Javob bermaslikdan boshlanadi, kattalarga aytish bilan tugaydi.",
                "hint_ru": "Начинается с «не отвечай», заканчивается рассказом взрослым.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Loyiha: Mehribonlik qoidasi",
            "task_title_ru": "Проект: правило доброты",
            "task_description": (
                "Onlayn mehribon bo'lish uchun 3 ta qoida yozing, va agar "
                "sizni yoki do'stingizni onlayn xafa qilishsa nima qilish "
                "kerakligini yozing. Matningizni topshiring — o'qituvchi "
                "tekshiradi."
            ),
            "task_description_ru": (
                "Напиши 3 правила доброты онлайн, и что делать, если "
                "обижают тебя или друга. Отправь текст — учитель проверит."
            ),
            "task_requirements": (
                "• Onlayn mehribon bo'lish uchun 3 ta qoida yozilsin\n"
                "• Xafa qilishga duch kelganda nima qilish kerakligi "
                "yozilsin\n"
                "• Javob tushunarli va aniq bo'lsin"
            ),
            "task_requirements_ru": (
                "• Написаны 3 правила доброты онлайн\n"
                "• Написано, что делать при столкновении с травлей\n"
                "• Ответ понятный и чёткий"
            ),
            "task_technologies": "Yozma javob",
            "task_deadline_days": 4,
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "order": 5,
        "title": "Yakuniy: Mening xavfsizlik qoidalarim",
        "title_ru": "Итог: мои правила безопасности",
        "points_reward": 25,
        "text_content": (
            "<h2>Hammasini birlashtiramiz</h2>"
            "<p>Ushbu kursda parol, notanish odamlar, yolg'on xabarlar, "
            "ekran vaqti va onlayn mehribonlik haqida o'rgandik. Endi "
            "hammasini birlashtirib, o'zimizning <b>shaxsiy xavfsizlik "
            "qoidalarimiz</b>ni tuzamiz.</p>"
            "<h3>Xavfsiz internet foydalanuvchisi qoidalari</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Kuchli parol qo'yaman\"] --> B[\"Notanishlarga shaxsiy ma'lumot bermayman\"]\n"
            "  B --> C[\"Shubhali havolani bosmayman\"]\n"
            "  C --> D[\"Ekran vaqtimni boshqaraman\"]\n"
            "  D --> E[\"Onlayn mehribon bo'laman\"]\n"
            "  E --> F{\"Muammo bo'lsa?\"}\n"
            "  F -->|\"ha\"| G[\"Ishonchli kattaga aytaman\"]\n"
            "</pre>"
            "<p>Bu 5 qoida sizni internetda xavfsiz va baxtli qiladi!</p>"
        ),
        "text_content_ru": (
            "<h2>Собираем всё вместе</h2>"
            "<p>В этом курсе мы узнали про пароли, незнакомцев, поддельные "
            "сообщения, экранное время и доброту онлайн. Теперь объединим "
            "всё в свои <b>личные правила безопасности</b>.</p>"
            "<h3>Правила безопасного пользователя интернета</h3>"
            "<pre class=\"mermaid\">\n"
            "flowchart TB\n"
            "  A[\"Kuchli parol qo'yaman\"] --> B[\"Notanishlarga shaxsiy ma'lumot bermayman\"]\n"
            "  B --> C[\"Shubhali havolani bosmayman\"]\n"
            "  C --> D[\"Ekran vaqtimni boshqaraman\"]\n"
            "  D --> E[\"Onlayn mehribon bo'laman\"]\n"
            "  E --> F{\"Muammo bo'lsa?\"}\n"
            "  F -->|\"да\"| G[\"Ishonchli kattaga aytaman\"]\n"
            "</pre>"
            "<p>Эти 5 правил сделают тебя в безопасности и счастливым в "
            "интернете!</p>"
        ),
        "code_content": None,
        "code_language": None,
        "video_url": None,
        "sample": {
            "title": "Namuna: Xavfsizlik qoidalari ro'yxati",
            "description": "Yakuniy loyiha uchun ilhom sifatida bir kishining qoidalari.",
            "sample_type": "code",
            "code_files": [
                {
                    "filename": "qoidalar.txt",
                    "language": "text",
                    "code": (
                        "1. Parolimni hech kimga aytmayman.\n"
                        "2. Notanish odamlarga shaxsiy ma'lumot bermayman.\n"
                        "3. Shubhali havolani bosmayman, kattalarga aytaman.\n"
                        "4. Kuniga ekran vaqtimni rejalashtiraman.\n"
                        "5. Internetda ham hayotdagidek mehribon bo'laman.\n"
                    ),
                }
            ],
        },
        "exercises": [
            {
                "title": "Kuchsiz parol",
                "title_ru": "Слабый пароль",
                "description": "Qaysi biri KUCHSIZ parol?",
                "description_ru": "Какой из этих паролей СЛАБЫЙ?",
                "exercise_type": "multiple_choice",
                "options": ["ismim2015", "Y#7mReng!92", "Ko'k$8raQ!3", "T4v#uS!m9"],
                "options_ru": ["ismim2015", "Y#7mReng!92", "Ko'k$8raQ!3", "T4v#uS!m9"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Ism va oddiy sondan iborat parolni qidiring.",
                "hint_ru": "Ищи пароль из имени и простого числа.",
                "explanation": "Ism + son — oson topiladigan, kuchsiz parol.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Telefon raqami so'ralsa",
                "title_ru": "Если спрашивают номер телефона",
                "description": "Notanish odam telefon raqamingizni so'rasa nima qilish kerak?",
                "description_ru": "Что делать, если незнакомец спрашивает номер телефона?",
                "exercise_type": "multiple_choice",
                "options": ["Bermaslik va kattalarga aytish", "Darhol berish", "Do'stingizga aytish", "Ijtimoiy tarmoqqa yozish"],
                "options_ru": ["Не давать и рассказать взрослым", "Сразу дать", "Сказать другу", "Написать в соцсети"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "Telefon raqami ham shaxsiy ma'lumot.",
                "hint_ru": "Номер телефона тоже личная информация.",
                "explanation": "Telefon raqami shaxsiy ma'lumot, notanishlarga berilmaydi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Kursning yakuniy so'zi",
                "title_ru": "Итоговое слово курса",
                "description": "Internetda xavfsiz bo'lish uchun eng muhim narsa — muammo bo'lsa ___ ga aytish.",
                "description_ru": "Самое важное для безопасности в интернете — при проблеме рассказать ___.",
                "exercise_type": "fill_in_blank",
                "correct_answers": "ota-onaga",
                "correct_answers_ru": "родителям",
                "hint": "Butun kurs davomida takrorlangan javob.",
                "hint_ru": "Ответ, повторявшийся весь курс.",
                "difficulty_level": "Medium",
                "points": 5,
            },
            {
                "title": "Xavfsizlik qoidalarini tartibga soling",
                "title_ru": "Расставь правила безопасности",
                "description": "Kursda o'rgangan 5 qoidani mantiqiy tartibda joylashtiring.",
                "description_ru": "Расставь 5 правил из курса в логичном порядке.",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Kuchli parol qo'yaman", "Notanishlarga shaxsiy ma'lumot bermayman", "Shubhali havolani bosmayman", "Ekran vaqtimni boshqaraman", "Onlayn mehribon bo'laman"],
                "drag_items_ru": ["Ставлю надёжный пароль", "Не даю личные данные незнакомцам", "Не нажимаю подозрительные ссылки", "Управляю экранным временем", "Добр онлайн"],
                "correct_order": ["Kuchli parol qo'yaman", "Notanishlarga shaxsiy ma'lumot bermayman", "Shubhali havolani bosmayman", "Ekran vaqtimni boshqaraman", "Onlayn mehribon bo'laman"],
                "hint": "Kurs qanday tartibda o'tilgan bo'lsa, shu tartibda.",
                "hint_ru": "В том же порядке, в каком шёл курс.",
                "difficulty_level": "Medium",
                "points": 5,
            },
        ],
        "task": {
            "task_title": "Yakuniy loyiha: Mening xavfsizlik plakatim",
            "task_title_ru": "Итоговый проект: мой плакат безопасности",
            "task_description": (
                "Kursda o'rgangan hamma narsani birlashtiring: parol, "
                "notanish odamlar, yolg'on xabarlar, ekran vaqti va onlayn "
                "mehribonlik haqida kamida bittadan qoida bilan to'liq "
                "xavfsizlik plakati yasang. Plakatingizni suratga olib "
                "topshiring — bu sizning eng to'liq loyihangiz!"
            ),
            "task_description_ru": (
                "Объедини всё, что выучил: сделай полный плакат "
                "безопасности минимум с одним правилом по каждой теме "
                "(пароль, незнакомцы, поддельные сообщения, экранное время, "
                "доброта онлайн). Сфотографируй плакат и отправь — это твой "
                "самый полный проект!"
            ),
            "task_requirements": (
                "• Parol haqida kamida bitta qoida\n"
                "• Notanish odamlar haqida kamida bitta qoida\n"
                "• Yolg'on xabarlar haqida kamida bitta qoida\n"
                "• Ekran vaqti va onlayn mehribonlik haqida kamida bittadan "
                "qoida"
            ),
            "task_requirements_ru": (
                "• Минимум одно правило про пароль\n"
                "• Минимум одно правило про незнакомцев\n"
                "• Минимум одно правило про поддельные сообщения\n"
                "• Минимум по одному правилу про экранное время и доброту "
                "онлайн"
            ),
            "task_technologies": "Rasm/Matn",
            "task_deadline_days": 5,
        },
    },
]
