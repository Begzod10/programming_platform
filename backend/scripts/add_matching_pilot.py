"""Pilot: add one hand-authored `matching` exercise per lesson to course_id=30
("Python Asoslari", 14 lessons), content drawn from each lesson's own
sections_json (see py_asoslari_summary.txt). Additive — does not touch any
existing exercise. Also writes RU translations via translation_cache so
Russian-language students see a translated version, per the mandatory
REQUIRED WORKFLOW in write_ru_translations.py.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select, func  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from scripts.write_ru_translations import translate_exercises, _write  # noqa: E402

# lesson_id -> content
LESSONS = {
    218: dict(
        topic="Python bilan tanishish",
        topic_ru="Знакомство с Python",
        terms=["print()", "REPL", ".py fayl", "#", "interpreter"],
        terms_ru=["print()", "REPL", "файл .py", "#", "интерпретатор"],
        defs=[
            "ekranga matn chiqaradi",
            "interaktiv (qatordan-qator) rejim",
            "Python dastur fayli kengaytmasi",
            "izoh (comment) belgisi",
            "kodni bajaruvchi dastur",
        ],
        defs_ru=[
            "выводит текст на экран",
            "интерактивный (построчный) режим",
            "расширение файла программы Python",
            "символ комментария",
            "программа, исполняющая код",
        ],
    ),
    219: dict(
        topic="O'zgaruvchilar va ma'lumot turlari",
        topic_ru="Переменные и типы данных",
        terms=["int", "str", "float", "bool", "type()"],
        terms_ru=["int", "str", "float", "bool", "type()"],
        defs=[
            "butun son turi",
            "matn (satr) turi",
            "kasr son turi",
            "True/False turi",
            "o'zgaruvchi turini aniqlaydi",
        ],
        defs_ru=[
            "тип целых чисел",
            "строковый тип (текст)",
            "тип дробных чисел",
            "тип True/False",
            "определяет тип переменной",
        ],
    ),
    220: dict(
        topic="Stringlar bilan ishlash",
        topic_ru="Работа со строками",
        terms=["upper()", "lower()", "len()", "split()", "f-string"],
        terms_ru=["upper()", "lower()", "len()", "split()", "f-строка"],
        defs=[
            "katta harflarga o'giradi",
            "kichik harflarga o'giradi",
            "uzunlikni qaytaradi",
            "stringni listga bo'ladi",
            "o'zgaruvchini matn ichiga joylaydi",
        ],
        defs_ru=[
            "переводит в верхний регистр",
            "переводит в нижний регистр",
            "возвращает длину",
            "разбивает строку на список",
            "вставляет переменную в текст",
        ],
    ),
    221: dict(
        topic="Takrorlash: Modul 1 (kalkulyator)",
        topic_ru="Повторение: Модуль 1 (калькулятор)",
        terms=["input()", "float()", 'f"{a:.2f}"', "ZeroDivisionError"],
        terms_ru=["input()", "float()", 'f"{a:.2f}"', "ZeroDivisionError"],
        defs=[
            "foydalanuvchidan matn oladi",
            "matnni kasr songa aylantiradi",
            "2 xonali formatlash",
            "nolga bo'lishda chiqadigan xato",
        ],
        defs_ru=[
            "получает текст от пользователя",
            "преобразует текст в дробное число",
            "форматирование с 2 знаками после запятой",
            "ошибка при делении на ноль",
        ],
    ),
    222: dict(
        topic="Shartli ifodalar",
        topic_ru="Условные конструкции",
        terms=["if", "elif", "else", "and", "Falsy"],
        terms_ru=["if", "elif", "else", "and", "Falsy"],
        defs=[
            "shart tekshiradi",
            "qo'shimcha shart",
            "aks holda bajariladi",
            "ikkala shart ham True bo'lishi kerak",
            "False deb hisoblanadigan qiymat (masalan 0, \"\")",
        ],
        defs_ru=[
            "проверяет условие",
            "дополнительное условие",
            "выполняется иначе",
            "оба условия должны быть True",
            "значение, считающееся False (например 0, \"\")",
        ],
    ),
    223: dict(
        topic="Sikllar — for va while",
        topic_ru="Циклы — for и while",
        terms=["for", "while", "break", "continue", "range()"],
        terms_ru=["for", "while", "break", "continue", "range()"],
        defs=[
            "ketma-ketlik bo'yicha aylanadi",
            "shart True bo'lguncha aylanadi",
            "siklni to'xtatadi",
            "keyingi iteratsiyaga o'tadi",
            "sonlar ketma-ketligini yaratadi",
        ],
        defs_ru=[
            "проходит по последовательности",
            "выполняется пока условие True",
            "останавливает цикл",
            "переходит к следующей итерации",
            "создаёт последовательность чисел",
        ],
    ),
    224: dict(
        topic="Ro'yxatlar (list) va kortejlar (tuple)",
        topic_ru="Списки (list) и кортежи (tuple)",
        terms=["list", "tuple", "append()", "pop()", "slice [a:b]"],
        terms_ru=["list", "tuple", "append()", "pop()", "срез [a:b]"],
        defs=[
            "o'zgaruvchan ro'yxat",
            "o'zgarmas ketma-ketlik",
            "oxiriga element qo'shadi",
            "elementni o'chirib qaytaradi",
            "qism-ro'yxat oladi",
        ],
        defs_ru=[
            "изменяемый список",
            "неизменяемая последовательность",
            "добавляет элемент в конец",
            "удаляет и возвращает элемент",
            "получает часть списка",
        ],
    ),
    225: dict(
        topic="Takrorlash: Modul 2 (tovarlar ro'yxati)",
        topic_ru="Повторение: Модуль 2 (список товаров)",
        terms=["while True", "append()", "remove()", "break"],
        terms_ru=["while True", "append()", "remove()", "break"],
        defs=[
            "menyu siklini yaratadi",
            "ro'yxatga tovar qo'shadi",
            "ro'yxatdan tovar o'chiradi",
            "menyudan chiqadi",
        ],
        defs_ru=[
            "создаёт цикл меню",
            "добавляет товар в список",
            "удаляет товар из списка",
            "выходит из меню",
        ],
    ),
    226: dict(
        topic="Funksiyalar — def, return, parametrlar",
        topic_ru="Функции — def, return, параметры",
        terms=["def", "return", "parametr", "default qiymat", "scope"],
        terms_ru=["def", "return", "параметр", "значение по умолчанию", "область видимости"],
        defs=[
            "funksiya e'lon qiladi",
            "natijani qaytaradi",
            "funksiyaga uzatiladigan qiymat",
            "argument berilmasa ishlatiladigan qiymat",
            "o'zgaruvchining ko'rinish doirasi",
        ],
        defs_ru=[
            "объявляет функцию",
            "возвращает результат",
            "значение, передаваемое в функцию",
            "значение, используемое если аргумент не передан",
            "область видимости переменной",
        ],
    ),
    227: dict(
        topic="Lug'atlar (dict) va to'plamlar (set)",
        topic_ru="Словари (dict) и множества (set)",
        terms=["dict", "set", ".get()", ".items()", ".keys()"],
        terms_ru=["dict", "set", ".get()", ".items()", ".keys()"],
        defs=[
            "kalit-qiymat juftliklari",
            "takrorlanmas elementlar to'plami",
            "kalitni xavfsiz oladi",
            "kalit va qiymat juftlarini qaytaradi",
            "barcha kalitlarni qaytaradi",
        ],
        defs_ru=[
            "пары ключ-значение",
            "набор уникальных элементов",
            "безопасно получает значение по ключу",
            "возвращает пары ключ-значение",
            "возвращает все ключи",
        ],
    ),
    228: dict(
        topic="Modullar va paketlar — import",
        topic_ru="Модули и пакеты — import",
        terms=["import", "math", "random", "pip install", "as"],
        terms_ru=["import", "math", "random", "pip install", "as"],
        defs=[
            "modulni kodga qo'shadi",
            "matematik funksiyalar moduli",
            "tasodifiy son moduli",
            "tashqi paket o'rnatadi",
            "modulga taxallus beradi",
        ],
        defs_ru=[
            "добавляет модуль в код",
            "модуль математических функций",
            "модуль случайных чисел",
            "устанавливает внешний пакет",
            "даёт модулю псевдоним",
        ],
    ),
    229: dict(
        topic="Takrorlash: Modul 3 (so'zlik + JSON)",
        topic_ru="Повторение: Модуль 3 (словарь + JSON)",
        terms=["json.dump()", "json.load()", "try/except", "FileNotFoundError"],
        terms_ru=["json.dump()", "json.load()", "try/except", "FileNotFoundError"],
        defs=[
            "ma'lumotni faylga yozadi",
            "fayldan ma'lumotni o'qiydi",
            "xatoni ushlaydi",
            "fayl topilmasa chiqadigan xato",
        ],
        defs_ru=[
            "записывает данные в файл",
            "читает данные из файла",
            "перехватывает ошибку",
            "ошибка, если файл не найден",
        ],
    ),
    230: dict(
        topic="Klasslar va obyektlar (OOP)",
        topic_ru="Классы и объекты (ООП)",
        terms=["class", "__init__", "self", "meros (inheritance)", "__str__"],
        terms_ru=["class", "__init__", "self", "наследование", "__str__"],
        defs=[
            "obyekt namunasini belgilaydi",
            "obyekt yaratilganda ishga tushadi",
            "obyektning o'ziga ishora",
            "classdan xususiyat olish",
            "obyektni matn ko'rinishida chiqaradi",
        ],
        defs_ru=[
            "определяет шаблон объекта",
            "запускается при создании объекта",
            "ссылка на сам объект",
            "получение свойств от класса",
            "выводит объект в виде текста",
        ],
    ),
    231: dict(
        topic="Fayllar va xatolar bilan ishlash",
        topic_ru="Работа с файлами и ошибками",
        terms=["open()", "with", "try", "except", "finally"],
        terms_ru=["open()", "with", "try", "except", "finally"],
        defs=[
            "faylni ochadi",
            "faylni avtomatik yopadi",
            "xatarli kodni sinaydi",
            "xatoni ushlaydi",
            "har doim bajariladi",
        ],
        defs_ru=[
            "открывает файл",
            "автоматически закрывает файл",
            "пробует выполнить рискованный код",
            "перехватывает ошибку",
            "выполняется всегда",
        ],
    ),
}


async def main():
    async with AsyncSessionLocal() as db:
        created_ids = []
        for lesson_id, c in LESSONS.items():
            max_order = (
                await db.execute(
                    select(func.max(Exercise.order)).where(Exercise.lesson_id == lesson_id)
                )
            ).scalar()
            next_order = (max_order or 0) + 1

            title = f"🔗 Juftlikni top: {c['topic']}"
            description = "Chap tarafdagi atamalarni o'ng tarafdagi ta'riflari bilan moslashtiring."
            hint = "Har bir so'zni dars matnida qanday ishlatilganini eslang."

            ex = Exercise(
                lesson_id=lesson_id,
                title=title,
                description=description,
                exercise_type="matching",
                drag_items=json.dumps(c["terms"], ensure_ascii=False),
                options=json.dumps(c["defs"], ensure_ascii=False),
                hint=hint,
                difficulty_level="Medium",
                points=4,
                order=next_order,
            )
            db.add(ex)
            await db.flush()
            created_ids.append((lesson_id, ex.id))

            title_ru = f"🔗 Найди пару: {c['topic_ru']}"
            description_ru = "Сопоставьте термины слева с их определениями справа."
            hint_ru = "Вспомните, как каждое слово использовалось в тексте урока."
            drag_items_ru = json.dumps(c["terms_ru"], ensure_ascii=False)
            options_ru = json.dumps(c["defs_ru"], ensure_ascii=False)

            await _write(db, "exercise", ex.id, "title", title, title_ru)
            await _write(db, "exercise", ex.id, "description", description, description_ru)
            await _write(db, "exercise", ex.id, "hint", hint, hint_ru)
            await _write(db, "exercise", ex.id, "drag_items", ex.drag_items, drag_items_ru)
            await _write(db, "exercise", ex.id, "options", ex.options, options_ru)

        await db.commit()
        for lesson_id, ex_id in created_ids:
            print(f"lesson {lesson_id}: created exercise id={ex_id}")


if __name__ == "__main__":
    asyncio.run(main())
