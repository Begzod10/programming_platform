"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=5 (L6)."""
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

LESSON_ID = 656

TITLE_RU = "6-Сортировка II: Merge Sort и Quick Sort"

TEXT_RU = """\
<h3>Эффективная сортировка: Merge Sort и Quick Sort</h3>
<p>Merge Sort и Quick Sort &mdash; эффективные алгоритмы сортировки промышленного уровня, основанные на принципе <em>"разделяй и властвуй" (divide and conquer)</em>. Оба в среднем случае имеют сложность O(n log n), что значительно быстрее, чем O(n^2) у Bubble/Selection/Insertion Sort.</p>
<h3>Merge Sort</h3>
<p>Рекурсивно делит список пополам, пока каждая половина не сведётся к одному элементу, затем две отсортированные половины объединяются через функцию <code>merge</code>. Merge Sort всегда, даже в худшем случае, гарантирует O(n log n), но требует дополнительной памяти O(n).</p>
<h3>Quick Sort</h3>
<p>Выбирает из списка элемент <em>pivot</em>, разделяя (partition) элементы меньше него влево, а больше &mdash; вправо, затем рекурсивно сортирует обе части. Quick Sort в среднем случае работает очень быстро (O(n log n)) и требует мало дополнительной памяти (in-place), но при неудачном выборе pivot в худшем случае может деградировать до O(n^2).</p>
<h3>Таблица сравнения</h3>
<table>
<tr><th>Свойство</th><th>Merge Sort</th><th>Quick Sort</th></tr>
<tr><td>Средний случай</td><td>O(n log n)</td><td>O(n log n)</td></tr>
<tr><td>Худший случай</td><td>O(n log n)</td><td>O(n^2)</td></tr>
<tr><td>Память</td><td>O(n) дополнительно</td><td>O(log n) (in-place)</td></tr>
<tr><td>Устойчивость</td><td>Устойчив</td><td>Неустойчив</td></tr>
</table>
<p>Следующая диаграмма показывает дерево рекурсии Merge Sort:</p>
<pre class="mermaid">
flowchart TB
  A["[8,3,7,4,2,9,1,5]"] --> B["[8,3,7,4]"]
  A --> C["[2,9,1,5]"]
  B --> D["[8,3]"] & E["[7,4]"]
  C --> F["[2,9]"] & G["[1,5]"]
  D --> H["merge -> [3,8]"]
  E --> I["merge -> [4,7]"]
  F --> J["merge -> [2,9]"]
  G --> K["merge -> [1,5]"]
</pre>
<p>На практике встроенная функция Python <code>sorted()</code> использует алгоритм Timsort (гибрид Merge Sort и Insertion Sort). В крупных базах данных и системах Quick Sort часто выбирают из-за его скорости в среднем случае, но при ограничениях памяти или требовании устойчивости предпочтение отдаётся Merge Sort.</p>
"""

CODE_RU = """\
# Merge Sort - разделяй и властвуй
def merge_sort(arr):
    if len(arr) <= 1:
        return arr  # Базовый случай

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


# Объединение двух отсортированных списков
def merge(left, right):
    result = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Добавляем оставшиеся элементы
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Quick Sort - разделение через pivot (partition)
def quick_sort(arr):
    if len(arr) <= 1:
        return arr  # Базовый случай

    pivot = arr[-1]
    left = []
    right = []

    for i in range(len(arr) - 1):
        if arr[i] < pivot:
            left.append(arr[i])
        else:
            right.append(arr[i])

    return quick_sort(left) + [pivot] + quick_sort(right)


# Quick Sort - вариант in-place (экономящий память)
def quick_sort_in_place(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_index = partition(arr, low, high)
        quick_sort_in_place(arr, low, pivot_index - 1)
        quick_sort_in_place(arr, pivot_index + 1, high)
    return arr


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# Практика
data = [8, 3, 7, 4, 2, 9, 1, 5, 6]

print("Merge Sort:", merge_sort(data))
print("Quick Sort:", quick_sort(data))
print("Quick Sort (in-place):", quick_sort_in_place(data.copy()))
"""

EX = {
    3872: {
        "title": "Общая стратегия",
        "description": "Какую общую стратегию используют Merge Sort и Quick Sort?",
        "hint": "Делят список на маленькие части и решают отдельно.",
        "explanation": "Merge Sort и Quick Sort оба основаны на принципе \"разделяй и властвуй\" (divide and conquer).",
    },
    3873: {
        "title": "Сложность памяти Merge Sort",
        "description": "Какую дополнительную сложность по памяти обычно имеет Merge Sort?",
        "hint": "Для объединения (merge) создаются новые списки.",
        "explanation": "Merge Sort требует дополнительной памяти O(n) для объединения двух половин.",
    },
    3874: {
        "title": "Свойства Quick Sort",
        "description": "Какие утверждения о Quick Sort верны?",
        "hint": "При неудачном выборе pivot худший случай ухудшается.",
        "explanation": "Quick Sort в среднем случае имеет O(n log n) и использует элемент pivot. Но в худшем случае может деградировать до O(n^2), и обычно неустойчив.",
    },
    3875: {
        "title": "Худший случай Quick Sort",
        "description": "Запишите временную сложность Quick Sort в худшем случае в форме Big O.",
        "hint": "",
        "expected_answer": "O(n^2)",
    },
    3876: {
        "title": "Функция merge",
        "description": "Как обычно называется функция, объединяющая две уже отсортированные половины в Merge Sort? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "merge",
    },
    3877: {
        "title": "Шаги Merge Sort",
        "description": "Расположите основные шаги алгоритма Merge Sort в правильном порядке.",
        "hint": "",
    },
    3878: {
        "title": "Сопоставление алгоритмов по свойствам",
        "description": "Расположите алгоритмы в соответствии с их описанием: сначала Merge Sort (гарантированный O(n log n)), затем Quick Sort (в среднем быстрый, но в худшем случае O(n^2)).",
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
