"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=4 (L5)."""
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

LESSON_ID = 654

TITLE_RU = "5-Сортировка I: Bubble, Selection, Insertion Sort"

TEXT_RU = """\
<h3>Простые алгоритмы сортировки</h3>
<p>Сортировка (sorting) &mdash; процесс расположения набора данных в определённом порядке (по возрастанию или убыванию). Bubble Sort, Selection Sort и Insertion Sort &mdash; самые простые и наиболее понятные алгоритмы сортировки. Все они имеют сложность O(n^2) в худшем случае, поэтому неэффективны для больших объёмов данных, но очень полезны для небольших списков и в учебных целях.</p>
<h3>Bubble Sort</h3>
<p>Сравнивает два соседних элемента и, если они расположены в неправильном порядке, меняет их местами (swap). Этот процесс повторяется, пока список полностью не отсортируется. На каждом "проходе" (pass) самый большой элемент "всплывает" (bubble up) на своё место, отсюда и название.</p>
<h3>Selection Sort</h3>
<p>На каждом шаге находит наименьший элемент в неотсортированной части и помещает его в конец отсортированной части. В отличие от Bubble Sort, выполняет меньше обменов (swap) &mdash; только один swap за проход.</p>
<h3>Insertion Sort</h3>
<p>Разделяет список на отсортированную и неотсортированную части, "вставляя" (insert) каждый элемент из неотсортированной части в правильное место отсортированной части. Особенно эффективен для небольших или почти отсортированных списков &mdash; в таких случаях скорость приближается к O(n).</p>
<h3>Таблица сравнения</h3>
<table>
<tr><th>Алгоритм</th><th>Средний случай</th><th>Худший случай</th><th>Устойчивость</th></tr>
<tr><td>Bubble Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Устойчив</td></tr>
<tr><td>Selection Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Неустойчив</td></tr>
<tr><td>Insertion Sort</td><td>O(n^2)</td><td>O(n^2)</td><td>Устойчив</td></tr>
</table>
<p>Следующая диаграмма показывает несколько проходов (pass) Bubble Sort:</p>
<pre class="mermaid">
flowchart TB
  A["[5,3,8,1]"] --> B["1-й проход: [3,5,1,8]"]
  B --> C["2-й проход: [3,1,5,8]"]
  C --> D["3-й проход: [1,3,5,8] - Отсортировано"]
</pre>
<p>Все эти три алгоритма являются "comparison-based" (основанными на сравнении) алгоритмами сортировки, которые редко применяются в реальных проектах, потому что встроенная функция Python <code>sorted()</code> и алгоритмы вроде Merge/Quick Sort гораздо эффективнее. Однако их понимание очень важно для развития алгоритмического мышления и часто спрашивается на технических собеседованиях. Устойчивость (stability) означает сохранение относительного порядка элементов с равными значениями, что имеет значение в некоторых практических случаях.</p>
"""

CODE_RU = """\
# Bubble Sort - сравнение и обмен соседних элементов
def bubble_sort(arr):
    result = arr.copy()
    n = len(result)

    for i in range(n - 1):
        swapped = False
        # На каждом проходе самый большой элемент "всплывает" в конец
        for j in range(n - 1 - i):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True
        # Если обменов не было, список уже отсортирован
        if not swapped:
            break
    return result


# Selection Sort - выбор наименьшего элемента и его размещение
def selection_sort(arr):
    result = arr.copy()
    n = len(result)

    for i in range(n - 1):
        min_index = i
        # Находим наименьший элемент в неотсортированной части
        for j in range(i + 1, n):
            if result[j] < result[min_index]:
                min_index = j
        if min_index != i:
            result[i], result[min_index] = result[min_index], result[i]
    return result


# Insertion Sort - вставка каждого элемента на правильное место
def insertion_sort(arr):
    result = arr.copy()

    for i in range(1, len(result)):
        current = result[i]
        j = i - 1

        # Сдвигаем элементы больше current на одну позицию
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


# Практика
data = [5, 3, 8, 1, 9, 2, 7]
print("Bubble Sort:", bubble_sort(data))
print("Selection Sort:", selection_sort(data))
print("Insertion Sort:", insertion_sort(data))

# На почти отсортированном списке Insertion Sort работает быстрее
almost_sorted = [1, 2, 4, 3, 5, 6, 7]
print("Deyarli tartiblangan:", insertion_sort(almost_sorted))
"""

EX = {
    3858: {
        "title": "Принцип Bubble Sort",
        "description": "На какой операции в основном базируется алгоритм Bubble Sort?",
        "hint": "В самом названии есть значение \"всплывание\" (bubble up).",
        "explanation": "Bubble Sort сравнивает два соседних элемента и, если порядок неверен, меняет их местами — этот процесс повторяется.",
    },
    3859: {
        "title": "Сложность всех трёх алгоритмов",
        "description": "Какова сложность в худшем случае алгоритмов Bubble, Selection и Insertion Sort?",
        "hint": "Все три используют вложенные циклы.",
        "explanation": "Bubble, Selection и Insertion Sort — все три в худшем случае имеют сложность O(n^2).",
    },
    3860: {
        "title": "Устойчивые алгоритмы",
        "description": "Какие из перечисленных алгоритмов считаются устойчивыми (stable) алгоритмами сортировки?",
        "hint": "Selection Sort перемещает элементы на большие расстояния, поэтому неустойчив.",
        "explanation": "Bubble Sort и Insertion Sort считаются устойчивыми алгоритмами, так как они сохраняют относительный порядок равных значений. Selection Sort и обычный Quick Sort неустойчивы.",
    },
    3861: {
        "title": "Число обменов в Selection Sort",
        "description": "Сколько обменов (swap) обычно выполняет Selection Sort за один проход? (ответьте числом)",
        "hint": "Только после нахождения наименьшего элемента происходит один обмен.",
        "expected_answer": "1",
    },
    3862: {
        "title": "Почти отсортированный список",
        "description": "Запишите название самого эффективного простого алгоритма сортировки для почти отсортированных списков.",
        "hint": "",
        "expected_answer": "Insertion Sort",
    },
    3863: {
        "title": "Шаги Bubble Sort",
        "description": "Расположите шаги внутри одного прохода алгоритма Bubble Sort в правильном порядке.",
        "hint": "",
    },
    3864: {
        "title": "Подбор алгоритмов по скорости",
        "description": "Сопоставьте алгоритмы с рекомендуемыми для них ситуациями для небольших списков.",
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
