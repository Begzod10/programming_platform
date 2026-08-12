"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=1 (L2)."""
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

LESSON_ID = 648

TITLE_RU = "2-Связный список (LinkedList)"

TEXT_RU = """\
<h3>Что такое LinkedList (связный список)?</h3>
<p>LinkedList &mdash; линейная структура данных, хранящая данные в виде отдельных элементов, называемых <strong>node</strong> (узел). Каждый узел состоит из двух частей: <em>value</em> (значение) и <em>next</em> (указатель на следующий узел). В отличие от списка (list), элементы LinkedList не располагаются в памяти последовательно &mdash; они связаны друг с другом через указатели (pointers).</p>
<p>Это свойство даёт LinkedList особые преимущества: добавление или удаление элемента в начале выполняется за O(1), потому что не нужно сдвигать остальные элементы, как в списке Python (list).</p>
<h3>Типы LinkedList</h3>
<ul>
<li><strong>Singly LinkedList</strong> &mdash; каждый узел указывает только на следующий узел.</li>
<li><strong>Doubly LinkedList</strong> &mdash; каждый узел указывает как на следующий, так и на предыдущий узел.</li>
<li><strong>Circular LinkedList</strong> &mdash; последний узел снова связывается с первым.</li>
</ul>
<h3>Таблица сравнения Python list и LinkedList</h3>
<table>
<tr><th>Операция</th><th>Python list</th><th>LinkedList</th></tr>
<tr><td>Чтение по индексу</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Добавление в начало</td><td>O(n)</td><td>O(1)</td></tr>
<tr><td>Добавление в конец</td><td>O(1)*</td><td>O(1) (с tail)</td></tr>
<tr><td>Удаление из середины</td><td>O(n)</td><td>O(n) (для поиска)</td></tr>
<tr><td>Память</td><td>Последовательная</td><td>Разрозненная (с указателями)</td></tr>
</table>
<p>Следующая диаграмма показывает структуру связного списка &mdash; каждый узел указывает на следующий, а последний узел связан с <code>None</code>:</p>
<pre class="mermaid">
flowchart LR
  Head["Head"] --> A["Node: 10"]
  A --> B["Node: 20"]
  B --> C["Node: 30"]
  C --> D["None"]
</pre>
<p>LinkedList в реальной жизни используется как основа для создания очередей (queue), стеков (stack) и других более сложных структур (например, chaining в hash table). Это не встроенный тип в Python, поэтому его нужно создавать самостоятельно с помощью класса. Понимание связного списка развивает навык работы с рекурсией и указателями, что служит фундаментом для следующих тем &mdash; деревьев и графов.</p>
"""

CODE_RU = """\
# Класс Singly LinkedList

class ListNode:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    # Добавление в конец списка - O(1)
    def append(self, value):
        node = ListNode(value)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.length += 1
        return self

    # Добавление в начало списка - O(1)
    def prepend(self, value):
        node = ListNode(value)
        if not self.head:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head = node
        self.length += 1
        return self

    # Удаление элемента - O(n)
    def delete(self, value):
        if not self.head:
            return False
        if self.head.value == value:
            self.head = self.head.next
            self.length -= 1
            return True
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self.length -= 1
                return True
            current = current.next
        return False

    # Превращение списка в Python list (удобно для отладки)
    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result


# Практика
linked_list = LinkedList()
linked_list.append(10)
linked_list.append(20)
linked_list.prepend(5)
print("Ro'yxat:", linked_list.to_list())  # [5, 10, 20]
linked_list.delete(10)
print("O'chirilgandan keyin:", linked_list.to_list())  # [5, 20]
print("Uzunlik:", linked_list.length)
"""

EX = {
    3816: {
        "title": "Структура узла",
        "description": "Из скольких основных полей состоит один узел в LinkedList?",
        "hint": "value и next.",
        "explanation": "Каждый узел состоит из двух основных полей: value (значение) и next (указатель на следующий узел).",
    },
    3817: {
        "title": "Сложность добавления в начало",
        "description": "Какой сложностью обладает добавление элемента в начало Singly LinkedList?",
        "hint": "Не нужно сдвигать другие элементы.",
        "explanation": "Создание нового узла, связывание его с head и обновление head — всё это требует постоянного времени, поэтому O(1).",
    },
    3818: {
        "title": "Типы LinkedList",
        "description": "Какие из перечисленных являются типами LinkedList?",
        "hint": "\"Binary\" здесь не подходит — это понятие из деревьев.",
        "explanation": "Три основных типа LinkedList: Singly, Doubly и Circular. Понятия \"Binary LinkedList\" не существует.",
    },
    3819: {
        "title": "Значение последнего узла",
        "description": "Чему обычно равно поле 'next' последнего узла в Singly LinkedList? (ответьте одним словом)",
        "hint": "Специальное значение в Python, обозначающее \"отсутствие\".",
        "expected_answer": "None",
    },
    3820: {
        "title": "Сложность поиска",
        "description": "Какой сложностью обладает поиск по значению в LinkedList? (запишите в форме Big O)",
        "hint": "Может потребоваться последовательно проверить каждый узел.",
        "expected_answer": "O(n)",
    },
    3821: {
        "title": "Шаги добавления в начало",
        "description": "Расположите шаги добавления нового узла в начало LinkedList в правильном порядке.",
        "hint": "Сначала создаётся узел, затем связывается, затем обновляется head.",
    },
    3822: {
        "title": "Python list vs LinkedList",
        "description": "Расположите операции в соответствии с их структурой данных (какая быстрее) от самого быстрого чтения до самого быстрого добавления.",
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
