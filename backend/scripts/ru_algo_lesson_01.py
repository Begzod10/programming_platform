"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=0 (L1)."""
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

LESSON_ID = 646

TITLE_RU = "1-Нотация Big O"

TEXT_RU = """\
<h3>Что такое нотация Big O?</h3>
<p>Нотация Big O &mdash; это математический способ записи, описывающий, как <strong>временная сложность</strong> (time complexity) и <strong>сложность по памяти</strong> (space complexity) алгоритма изменяются с ростом объёма данных. Она позволяет оценить скорость работы алгоритма в худшем случае (worst case), что крайне важно для сравнения разных алгоритмов между собой.</p>
<p>Как разработчик, вы должны обеспечивать не только правильную работу кода, но и его эффективность при больших объёмах данных. Например, функция, работающая со списком из 10 элементов, должна за приемлемое время работать и со списком из 10 миллионов элементов.</p>
<h3>Основные типы сложности</h3>
<ul>
<li><strong>O(1)</strong> &mdash; Константное время (constant time). Обращение к одному элементу списка по индексу.</li>
<li><strong>O(log n)</strong> &mdash; Логарифмическое время. Алгоритмы вроде Binary Search.</li>
<li><strong>O(n)</strong> &mdash; Линейное время. Один проход по списку (loop).</li>
<li><strong>O(n log n)</strong> &mdash; Эффективные алгоритмы сортировки вроде Merge Sort, Quick Sort.</li>
<li><strong>O(n^2)</strong> &mdash; Квадратичное время. Два вложенных цикла (например, Bubble Sort).</li>
<li><strong>O(2^n)</strong> &mdash; Экспоненциальное время. Неэффективные алгоритмы вроде рекурсивного Фибоначчи.</li>
</ul>
<h3>Таблица сравнения сложности</h3>
<table>
<tr><th>Нотация</th><th>Название</th><th>n=10</th><th>n=1000</th></tr>
<tr><td>O(1)</td><td>Константная</td><td>1</td><td>1</td></tr>
<tr><td>O(log n)</td><td>Логарифмическая</td><td>~3</td><td>~10</td></tr>
<tr><td>O(n)</td><td>Линейная</td><td>10</td><td>1000</td></tr>
<tr><td>O(n log n)</td><td>Лог-линейная</td><td>~33</td><td>~10000</td></tr>
<tr><td>O(n^2)</td><td>Квадратичная</td><td>100</td><td>1000000</td></tr>
</table>
<p>Следующая диаграмма показывает типы сложности от самого быстрого к самому медленному по скорости роста:</p>
<pre class="mermaid">
flowchart TB
  A["O(1) - Константная"] --> B["O(log n) - Логарифмическая"]
  B --> C["O(n) - Линейная"]
  C --> D["O(n log n) - Лог-линейная"]
  D --> E["O(n^2) - Квадратичная"]
  E --> F["O(2^n) - Экспоненциальная"]
</pre>
<p>Правильное понимание Big O даёт вам способность оптимизировать код, выбирать алгоритмы и эффективно отвечать на технических собеседованиях. Всегда учитывайте худший случай (worst case) и игнорируйте постоянные коэффициенты (constants) и малые слагаемые — например, O(2n) записывается просто как O(n).</p>
"""

CODE_RU = """\
# Нотация Big O - практические примеры

# O(1) - Константное время: обращение к элементу списка по индексу
def get_first_element(arr):
    # Всегда одна операция, независимо от размера списка
    return arr[0]


# O(n) - Линейное время: один проход по списку
def find_max(arr):
    max_val = arr[0]
    for i in range(1, len(arr)):
        # Каждый элемент проверяем один раз
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val


# O(n^2) - Квадратичное время: два вложенных цикла
def has_duplicates(arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            # Сравниваем каждую пару - примерно n * n операций
            if arr[i] == arr[j]:
                return True
    return False


# O(log n) - Логарифмическое время: бинарный поиск
def binary_search(sorted_arr, target):
    left = 0
    right = len(sorted_arr) - 1

    while left <= right:
        # Каждый раз сокращаем область поиска вдвое
        mid = (left + right) // 2

        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# O(n log n) - встроенная функция sorted() для эффективной сортировки
def sort_numbers(arr):
    # Python использует алгоритм Timsort - в среднем O(n log n)
    return sorted(arr)


# Тест для практики
numbers = [5, 3, 8, 1, 9, 2, 7]
print("Max element (O(n)):", find_max(numbers))
print("Duplicates bormi (O(n^2)):", has_duplicates(numbers))

sorted_numbers = sort_numbers(numbers)
print("Tartiblangan (O(n log n)):", sorted_numbers)
print("Binary search natijasi (O(log n)):", binary_search(sorted_numbers, 8))

# Для каждой функции важно уметь объяснить сложность,
# так как это позволяет заранее выявлять проблемы
# производительности в реальных проектах.
"""

EX = {
    3802: {
        "title": "Сложность константного времени",
        "description": "Какой сложностью обладает обращение к одному элементу списка по индексу?",
        "hint": "Обращение по индексу не зависит от размера списка.",
        "explanation": "Обращение по индексу, например arr[0], всегда одна операция независимо от размера списка — это O(1), константное время.",
    },
    3803: {
        "title": "Вложенный цикл",
        "description": "Какую сложность обычно дают два вложенных друг в друга цикла?",
        "hint": "Для каждого шага внешнего цикла внутренний цикл выполняется полностью.",
        "explanation": "Два вложенных цикла обычно дают O(n^2), потому что для каждой итерации внешнего цикла внутренний цикл снова выполняется n раз.",
    },
    3804: {
        "title": "Эффективные алгоритмы сортировки",
        "description": "Какие из перечисленных являются эффективными алгоритмами сортировки со сложностью O(n log n)?",
        "hint": "Два из них основаны на принципе 'разделяй и властвуй'.",
        "explanation": "Merge Sort и Quick Sort в среднем случае имеют сложность O(n log n). Bubble Sort и Selection Sort же имеют O(n^2).",
    },
    3805: {
        "title": "Сложность Binary Search",
        "description": "Запишите временную сложность алгоритма Binary Search в нотации Big O (например: O(log n)).",
        "hint": "На каждом шаге область поиска сокращается вдвое.",
        "expected_answer": "O(log n)",
    },
    3806: {
        "title": "Сложность одного цикла",
        "description": "Запишите сложность цикла, который проходит по списку только один раз.",
        "hint": "Каждый элемент рассматривается один раз.",
        "expected_answer": "O(n)",
    },
    3807: {
        "title": "Сортировка по скорости",
        "description": "Расположите типы сложности от самого быстрого к самому медленному.",
        "hint": "Константное время самое быстрое, квадратичное время самое медленное.",
    },
    3808: {
        "title": "Шаги Binary Search",
        "description": "Расположите шаги алгоритма Binary Search в правильном порядке.",
        "hint": "Сначала границы, затем средняя точка, затем сравнение.",
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
