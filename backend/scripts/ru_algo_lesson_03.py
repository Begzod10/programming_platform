"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=2 (L3)."""
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

LESSON_ID = 650

TITLE_RU = "3-Stack и Queue"

TEXT_RU = """\
<h3>Что такое Stack и Queue?</h3>
<p>Stack (стек) и Queue (очередь) &mdash; две фундаментальные линейные структуры данных, различающиеся порядком доступа к данным. Они часто строятся на основе списка (list) или LinkedList, но ограничивают порядок входа/выхода.</p>
<h3>Stack &mdash; принцип LIFO</h3>
<p><strong>Stack</strong> основан на принципе <em>LIFO (Last In, First Out)</em>: последний добавленный элемент извлекается первым. Это похоже на стопку тарелок &mdash; вы берёте верхнюю тарелку первой. Основные операции: <code>push</code> (добавить) и <code>pop</code> (извлечь).</p>
<p>Применение Stack: история "назад" в браузере, вызовы функций (call stack), функции undo/redo, проверка соответствия скобок.</p>
<h3>Queue &mdash; принцип FIFO</h3>
<p><strong>Queue</strong> основан на принципе <em>FIFO (First In, First Out)</em>: первый добавленный элемент извлекается первым. Это похоже на очередь &mdash; кто пришёл первым, тот первым обслуживается. Основные операции: <code>enqueue</code> (добавить) и <code>dequeue</code> (извлечь).</p>
<p>Применение Queue: очереди печати (print queue), алгоритм BFS (Breadth-First Search), обработка запросов по очереди (task scheduling).</p>
<h3>Таблица сравнения</h3>
<table>
<tr><th>Свойство</th><th>Stack</th><th>Queue</th></tr>
<tr><td>Принцип</td><td>LIFO</td><td>FIFO</td></tr>
<tr><td>Операция добавления</td><td>push</td><td>enqueue</td></tr>
<tr><td>Операция извлечения</td><td>pop</td><td>dequeue</td></tr>
<tr><td>Сложность</td><td>O(1)</td><td>O(1)</td></tr>
<tr><td>Пример</td><td>Call stack</td><td>Print queue</td></tr>
</table>
<p>Следующая диаграмма показывает принцип работы обеих структур:</p>
<pre class="mermaid">
flowchart TB
  subgraph Stack["Stack (LIFO)"]
    S1["push(3)"] --> S2["push(2)"] --> S3["push(1)"] --> S4["pop() -> 1"]
  end
  subgraph Queue["Queue (FIFO)"]
    Q1["enqueue(3)"] --> Q2["enqueue(2)"] --> Q3["enqueue(1)"] --> Q4["dequeue() -> 3"]
  end
</pre>
<p>В Python нет специальных встроенных типов для Stack и Queue, но их можно реализовать с помощью обычного списка (list) через <code>append/pop</code> (для Stack). При работе с большими объёмами данных помните, что извлечение из начала списка (<code>pop(0)</code>) может занять O(n) времени, поэтому для эффективной Queue используется <code>collections.deque</code> (двусторонняя очередь) &mdash; она обеспечивает добавление/извлечение с начала и конца за O(1).</p>
"""

CODE_RU = """\
from collections import deque


# Реализация Stack (LIFO)
class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0


# Реализация Queue (FIFO) - эффективно с deque
class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, value):
        self.items.append(value)

    def dequeue(self):
        return self.items.popleft()  # O(1) - list.pop(0) был бы O(n)

    def front(self):
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0


# Практический пример: проверка соответствия скобок через Stack
def is_balanced(expression):
    stack = Stack()
    pairs = {")": "(", "]": "[", "}": "{"}

    for char in expression:
        if char in "([{":
            stack.push(char)
        elif char in ")]}":
            # Открывающая скобка, соответствующая закрывающей, должна быть на вершине стека
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False
    return stack.is_empty()


# Практика
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)
print("Stack pop:", stack.pop())  # 3 (LIFO)

queue = Queue()
queue.enqueue("A")
queue.enqueue("B")
queue.enqueue("C")
print("Queue dequeue:", queue.dequeue())  # A (FIFO)

print(is_balanced("{[()]}"))  # True
print(is_balanced("{[(])}"))  # False
"""

EX = {
    3830: {
        "title": "Принцип Stack",
        "description": "На каком принципе основан Stack?",
        "hint": "Последний добавленный элемент выходит первым.",
        "explanation": "Stack основан на принципе LIFO (Last In, First Out): последний добавленный элемент извлекается первым.",
    },
    3831: {
        "title": "Операция Queue",
        "description": "Какая операция используется для добавления элемента в Queue?",
        "hint": "Это термин, характерный для Queue.",
        "explanation": "Для добавления элемента в Queue используется операция enqueue, а для извлечения — dequeue.",
    },
    3832: {
        "title": "Области применения Stack",
        "description": "Какие из перечисленных являются реальными случаями применения Stack?",
        "hint": "В самом названии \"Print queue\" уже написано Queue.",
        "explanation": "Call stack, undo/redo и проверка скобок — всё это основано на логике Stack (LIFO). Print queue же — пример Queue (FIFO).",
    },
    3833: {
        "title": "Извлечение элемента из Stack",
        "description": "Запишите название метода, используемого для извлечения элемента из Stack.",
        "hint": "",
        "expected_answer": "pop",
    },
    3834: {
        "title": "Алгоритм BFS",
        "description": "Какую структуру обычно использует алгоритм BFS (Breadth-First Search)? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "queue",
    },
    3835: {
        "title": "Порядок операций Stack",
        "description": "Расположите результаты в правильном порядке при выполнении операций push(1), push(2), push(3), pop().",
        "hint": "",
    },
    3836: {
        "title": "Алгоритм проверки скобок",
        "description": "Расположите шаги алгоритма проверки соответствия скобок с помощью Stack в правильном порядке.",
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
