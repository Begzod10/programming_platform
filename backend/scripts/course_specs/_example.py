"""EXAMPLE spec — documents the format by example, exercises every piece
of the pipeline (multiple_choice, drag_and_drop, fill_in_blank, a sample,
a submission task). NOT meant to be seeded for real — run this only with
--dry-run. Copy this file as a starting point for a real course spec;
prefix real spec files without the leading underscore.
"""

COURSE = {
    "title": "__EXAMPLE__ Course Builder Template",
    "description": "Template course exercising every field of the spec format. Do not publish.",
    "instructor_id": 2,
    "difficulty_level": "Beginner",
    "duration_weeks": 1,
    "max_points": 30,
    "category_id": None,
    "prerequisite_course_id": None,
    "display_order": 0,
    "is_active": True,
    "is_published": False,
}

LESSONS = [
    {
        "order": 0,
        "title": "1-Namuna dars",
        "title_ru": "1-Пример урока",
        "points_reward": 10,
        "text_content": "<h3>Bu namuna dars</h3><p>Matn mazmuni shu yerda.</p>",
        "text_content_ru": "<h3>Это пример урока</h3><p>Текстовое содержание здесь.</p>",
        "code_content": "print('salom')",
        "code_content_ru": "print('привет')",
        "code_language": "python",
        "video_url": None,
        "sample": {
            "title": "Namuna: Salom dunyo",
            "description": "Oddiy chiqish namunasi",
            "sample_type": "code",
            "code_files": [{"filename": "main.py", "language": "python", "code": "print('salom')"}],
        },
        "exercises": [
            {
                "title": "MCQ namunasi",
                "title_ru": "Пример MCQ",
                "description": "print('salom') nima qiladi?",
                "description_ru": "Что делает print('salom')?",
                "exercise_type": "multiple_choice",
                "options": ["Konsolga chiqaradi", "Faylga yozadi", "Xato beradi", "Hech narsa"],
                "options_ru": ["Выводит в консоль", "Записывает в файл", "Выдаёт ошибку", "Ничего"],
                "correct_answers": "A",
                "is_multiple_select": False,
                "hint": "print konsolga chiqarish uchun ishlatiladi.",
                "hint_ru": "print используется для вывода в консоль.",
                "explanation": "print() funksiyasi argumentini standart chiqishga (konsolga) yozadi.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Drag namunasi",
                "title_ru": "Пример drag",
                "description": "Qadamlarni to'g'ri tartibga joylashtiring",
                "description_ru": "Расположите шаги в правильном порядке",
                "exercise_type": "drag_and_drop",
                "drag_items": ["Kodni yozish", "Kodni ishga tushirish", "Natijani ko'rish"],
                "drag_items_ru": ["Написать код", "Запустить код", "Посмотреть результат"],
                "correct_order": ["Kodni yozish", "Kodni ishga tushirish", "Natijani ko'rish"],
                "hint": "Avval yozamiz, keyin ishga tushiramiz.",
                "hint_ru": "Сначала пишем, потом запускаем.",
                "difficulty_level": "Easy",
                "points": 5,
            },
            {
                "title": "Fill-in namunasi",
                "title_ru": "Пример fill-in",
                "description": "Konsolga chiqarish uchun funksiya nomi: ___()",
                "description_ru": "Функция для вывода в консоль: ___()",
                "exercise_type": "fill_in_blank",
                "correct_answers": "print",  # code token — no correct_answers_ru needed
                "hint": "",
                "difficulty_level": "Easy",
                "points": 5,
            },
        ],
    },
    {
        "order": 1,
        "title": "R1-Namuna takrorlash",
        "title_ru": "R1-Пример повторения",
        "points_reward": 15,
        "text_content": "<h3>Takrorlash darsi</h3><p>Bu yerda amaliy loyiha bo'ladi.</p>",
        "text_content_ru": "<h3>Урок повторения</h3><p>Здесь будет практический проект.</p>",
        "task": {
            "task_title": "Amaliy mashq: Salomlashish dasturi",
            "task_title_ru": "Практика: программа приветствия",
            "task_description": "Foydalanuvchi ismini so'rab, salomlashuvchi dastur yozing.",
            "task_description_ru": "Напишите программу, которая спрашивает имя пользователя и приветствует его.",
            "task_requirements": "input() va print() ishlatilishi kerak.",
            "task_requirements_ru": "Должны использоваться input() и print().",
            "task_technologies": "Python",
            "task_deadline_days": 3,
        },
        "exercises": [],
    },
]
