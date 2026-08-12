"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=3 (L4)."""
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

LESSON_ID = 652

TITLE_RU = "4-Бинарный поиск (Binary Search)"

TEXT_RU = """\
<h3>Что такое Binary Search (бинарный поиск)?</h3>
<p>Binary Search &mdash; эффективный алгоритм поиска, используемый для очень быстрого нахождения элемента в <strong>отсортированном</strong> списке. Он основан на принципе <em>"разделяй и властвуй" (divide and conquer)</em>: на каждом шаге область поиска сокращается вдвое.</p>
<p>Важное условие: список должен быть <strong>заранее отсортирован</strong>. В противном случае алгоритм может дать неверный результат.</p>
<h3>Как работает алгоритм</h3>
<ul>
<li>Выбираем средний элемент списка (<code>mid</code>).</li>
<li>Если <code>mid</code> равен искомому значению &mdash; найдено.</li>
<li>Если искомое значение меньше <code>mid</code> &mdash; продолжаем в левой половине.</li>
<li>Если искомое значение больше <code>mid</code> &mdash; продолжаем в правой половине.</li>
<li>Повторяем, пока область поиска не станет пустой или элемент не будет найден.</li>
</ul>
<h3>Сравнение с Linear Search</h3>
<table>
<tr><th>Свойство</th><th>Linear Search</th><th>Binary Search</th></tr>
<tr><td>Требование</td><td>Может быть неотсортирован</td><td>Должен быть отсортирован</td></tr>
<tr><td>Временная сложность</td><td>O(n)</td><td>O(log n)</td></tr>
<tr><td>Примерное число шагов при 1,000,000 элементах</td><td>1,000,000</td><td>~20</td></tr>
<tr><td>Реализация</td><td>Простой цикл</td><td>Два указателя (left/right)</td></tr>
</table>
<p>Следующая диаграмма показывает процесс binary search пошагово (поиск в отсортированном списке для target=7):</p>
<pre class="mermaid">
flowchart TB
  A["left=0, right=6, mid=3"] --> B{"arr[mid] == 7?"}
  B -->|"Да"| C["Найдено!"]
  B -->|"arr[mid] &lt; 7"| D["left = mid+1, отбросить левую часть, продолжить справа"]
  B -->|"arr[mid] &gt; 7"| E["right = mid-1, отбросить правую часть, продолжить слева"]
</pre>
<p>Binary Search &mdash; один из самых часто задаваемых алгоритмов на технических собеседованиях. Он может быть написан рекурсивно или итеративно. Кроме того, в отличие от простого линейного поиска, на больших отсортированных наборах данных (например, индексированные записи в базе данных) алгоритм binary search работает значительно быстрее. Модуль Python <code>bisect</code> предоставляет готовую, оптимизированную версию именно этого алгоритма.</p>
"""

CODE_RU = """\
# Binary Search - итеративный вариант
def binary_search_iterative(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if sorted_arr[mid] == target:
            return mid  # Найдено
        elif sorted_arr[mid] < target:
            left = mid + 1  # Продолжить в правой половине
        else:
            right = mid - 1  # Продолжить в левой половине

    return -1  # Не найдено


# Binary Search - рекурсивный вариант
def binary_search_recursive(sorted_arr, target, left=0, right=None):
    if right is None:
        right = len(sorted_arr) - 1

    if left > right:
        return -1  # Базовый случай: область поиска закончилась

    mid = (left + right) // 2

    if sorted_arr[mid] == target:
        return mid
    elif sorted_arr[mid] < target:
        return binary_search_recursive(sorted_arr, target, mid + 1, right)
    else:
        return binary_search_recursive(sorted_arr, target, left, mid - 1)


# Практический пример: нахождение индекса первого вхождения элемента (lower bound)
def find_first_occurrence(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            result = mid
            right = mid - 1  # Продолжаем влево, ищем первое вхождение
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result


# Практика
numbers = [1, 3, 5, 7, 9, 11, 13, 15]
print("Iterativ qidiruv (7):", binary_search_iterative(numbers, 7))
print("Rekursiv qidiruv (13):", binary_search_recursive(numbers, 13))
print("Topilmagan qiymat (4):", binary_search_iterative(numbers, 4))

with_duplicates = [1, 2, 2, 2, 3, 4, 5]
print("Birinchi uchrash (2):", find_first_occurrence(with_duplicates, 2))
"""

EX = {
    3844: {
        "title": "Условие Binary Search",
        "description": "Каким должен быть список, чтобы алгоритм Binary Search работал?",
        "hint": "Алгоритм работает, разделяя на левую/правую части.",
        "explanation": "Binary Search правильно работает только на отсортированном списке, потому что он сравнивает значения и сокращает область поиска вдвое.",
    },
    3845: {
        "title": "Сложность Binary Search",
        "description": "Какова временная сложность алгоритма Binary Search?",
        "hint": "На каждом шаге область поиска сокращается вдвое.",
        "explanation": "Binary Search на каждом шаге сокращает область поиска вдвое, поэтому его сложность O(log n).",
    },
    3846: {
        "title": "Свойства Binary Search",
        "description": "Какие из перечисленных утверждений о Binary Search верны?",
        "hint": "Второй вариант противоречит основному требованию алгоритма.",
        "explanation": "Binary Search основан на принципе divide and conquer, может быть написан рекурсивно или итеративно, и на каждом шаге сокращает область поиска вдвое. Но он работает только на ОТСОРТИРОВАННОМ списке.",
    },
    3847: {
        "title": "Формула среднего индекса",
        "description": "Запишите формулу вычисления индекса mid с помощью указателей left и right (в синтаксисе Python, например: (left + right) // 2).",
        "hint": "В Python используется оператор целочисленного деления //.",
        "expected_answer": "(left + right) // 2",
    },
    3848: {
        "title": "Шаги при 1,000,000 элементах",
        "description": "Примерно за сколько шагов выполняется поиск методом Binary Search в отсортированном списке из 1,000,000 элементов? (ответьте числом)",
        "hint": "Вычислите log2(1,000,000).",
        "expected_answer": "20",
    },
    3849: {
        "title": "Порядок шагов Binary Search",
        "description": "Расположите шаги выполнения алгоритма Binary Search в правильном порядке.",
        "hint": "",
    },
    3850: {
        "title": "Скорость Linear vs Binary",
        "description": "Расположите методы поиска от медленного к быстрому по мере роста размера списка.",
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
