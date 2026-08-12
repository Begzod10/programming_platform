"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=9 (L10, CAPSTONE, final lesson)."""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from write_ru_translations import translate_lesson, translate_exercises  # noqa: E402

LESSON_ID = 664

TITLE_RU = "10-Capstone: Практика алгоритмов"

TEXT_RU = """\
<h3>Capstone: Итог курса и практический проект</h3>
<p>Поздравляем! Вы изучили все основные темы курса "Python: Алгоритмы и структуры данных" &mdash; нотацию Big O, LinkedList, Stack/Queue, Binary Search, алгоритмы сортировки, HashMap, BST и Graph. В этом заключительном уроке вы объединяете все свои знания, закрепляя их решением реальной задачи.</p>
<h3>Почему эти знания важны</h3>
<p>Глубокое понимание структур данных и алгоритмов помогает вам не только добиться успеха на технических собеседованиях, но и делать код в реальных проектах быстрее и эффективнее, <em>выбирая правильную структуру</em>. Например, выбор HashMap (dict) вместо обычного списка для задачи, часто требующей поиска, может ускорить программу в сотни раз.</p>
<h3>Обобщающая таблица всех тем</h3>
<table>
<tr><th>Структура/Алгоритм</th><th>Основная сложность</th><th>Когда используется</th></tr>
<tr><td>List</td><td>Доступ O(1), Поиск O(n)</td><td>Последовательные данные</td></tr>
<tr><td>LinkedList</td><td>Добавление O(1), Поиск O(n)</td><td>Частое добавление/удаление</td></tr>
<tr><td>Stack/Queue</td><td>O(1) все основные операции</td><td>Задачи с логикой LIFO/FIFO</td></tr>
<tr><td>Binary Search</td><td>O(log n)</td><td>Поиск в отсортированных данных</td></tr>
<tr><td>Merge/Quick Sort</td><td>O(n log n)</td><td>Сортировка больших объёмов</td></tr>
<tr><td>HashMap (dict)</td><td>O(1) в среднем</td><td>Быстрый поиск, кеш</td></tr>
<tr><td>BST</td><td>O(log n) в среднем</td><td>Отсортированные динамические данные</td></tr>
<tr><td>Graph (BFS/DFS)</td><td>O(V + E)</td><td>Сети, маршруты, связи</td></tr>
</table>
<p>Следующая диаграмма показывает путь знаний, изученных за курс:</p>
<pre class="mermaid">
flowchart LR
  A["Big O"] --> B["LinkedList"] --> C["Stack/Queue"] --> D["Binary Search"]
  D --> E["Сортировка I & II"] --> F["HashMap"] --> G["BST"] --> H["Graph"] --> I["Capstone-проект"]
</pre>
<p>Теперь вы умеете не только писать алгоритмы, но и оценивать их эффективность. Следующий шаг &mdash; применять эти знания в реальных проектах, практиковаться на платформах вроде LeetCode и знакомиться с более сложными темами (Dynamic Programming, жадные алгоритмы, Trie).</p>
"""

CODE_RU = """\
# Capstone: практический пример, объединяющий все знания
# Задача: реализовать быстрый поиск, сортировку и поиск по диапазону
# в списке студентов

students = [
    {"id": 101, "name": "Ali", "score": 87},
    {"id": 102, "name": "Vali", "score": 65},
    {"id": 103, "name": "Guli", "score": 92},
    {"id": 104, "name": "Sami", "score": 78},
    {"id": 105, "name": "Dilnoza", "score": 55},
]


# 1) Быстрый поиск по ID через HashMap (dict) - O(1)
def build_student_index(students):
    index = {}
    for student in students:
        index[student["id"]] = student
    return index


student_index = build_student_index(students)
print("ID=103 talaba:", student_index.get(103))


# 2) Сортировка по баллам через Merge Sort - O(n log n)
def merge_sort_by_score(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_by_score(arr[:mid])
    right = merge_sort_by_score(arr[mid:])
    return merge_by_score(left, right)


def merge_by_score(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i]["score"] <= right[j]["score"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


sorted_by_score = merge_sort_by_score(students)
print(
    "Ballar bo'yicha tartiblangan:",
    [f"{s['name']}:{s['score']}" for s in sorted_by_score],
)


# 3) Нахождение первого студента выше определённого балла через Binary Search
def find_first_above_score(sorted_students, min_score):
    left = 0
    right = len(sorted_students) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if sorted_students[mid]["score"] >= min_score:
            result = mid
            right = mid - 1
        else:
            left = mid + 1
    return sorted_students[result] if result != -1 else None


print("70 balldan yuqori birinchi talaba:", find_first_above_score(sorted_by_score, 70))

# Вывод: HashMap (dict) — для быстрого поиска, Merge Sort — для эффективной сортировки,
# Binary Search — для быстрого поиска в отсортированных данных, все использованы вместе.
"""

EX = {
    3928: {
        "title": "Структура для быстрого поиска",
        "description": "Какая структура данных наиболее подходит, когда нужен быстрый (O(1)) поиск по ID?",
        "hint": "Эта структура даёт в среднем O(1) поиск.",
        "explanation": "HashMap (в Python — dict) обеспечивает поиск по ключу в среднем за O(1), поэтому наиболее подходит для быстрого поиска по ID.",
    },
    3929: {
        "title": "Сортировка 1 миллиона чисел",
        "description": "Какой лучший выбор для сортировки 1,000,000 случайных чисел?",
        "hint": "O(n^2) слишком медленно для больших объёмов данных.",
        "explanation": "Для больших объёмов данных Merge/Quick Sort со сложностью O(n log n) намного эффективнее.",
    },
    3930: {
        "title": "Структуры, изученные в курсе",
        "description": "Какие из перечисленных структур/алгоритмов изучались в этом курсе?",
        "hint": "Один из вариантов вообще не относится к этому курсу.",
        "explanation": "LinkedList, Binary Search Tree и Graph — темы, изученные в курсе. Neural Network не входит в рамки этого курса.",
    },
    3931: {
        "title": "Структура телефонной книги",
        "description": "Какая комбинация наиболее подходит для приложения телефонной книги, требующего O(1) поиска по имени и вывода всех имён в алфавитном порядке? (например: 'HashMap va BST')",
        "hint": "",
        "expected_answer": "HashMap va BST",
    },
    3932: {
        "title": "Сравнение всех структур",
        "description": "Вспомните общее название 8 основных структур/алгоритмов, изученных в курсе, и запишите их общую категорию сложности (например: 'линейная и логарифмическая').",
        "hint": "",
        "expected_answer": "chiziqli va logarifmik",
    },
    3933: {
        "title": "Шаги выбора правильной структуры",
        "description": "Расположите шаги процесса анализа задачи и выбора правильной структуры данных в правильном порядке.",
        "hint": "",
    },
    3934: {
        "title": "Порядок тем курса",
        "description": "Расположите темы, изученные в течение курса, в том порядке, в котором они преподавались.",
        "hint": "",
    },
}


async def _run():
    async with AsyncSessionLocal() as db:
        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        ex_rows = (
            await db.execute(select(Exercise).where(Exercise.id.in_(EX.keys())))
        ).scalars().all()

        section_map = {"Текст": "Текст", "Код": "Код", "Упражнения": "Упражнения"}
        section_map[lesson.text_content] = TEXT_RU
        section_map[lesson.code_content] = CODE_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={"title": TITLE_RU, "text_content": TEXT_RU},
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
