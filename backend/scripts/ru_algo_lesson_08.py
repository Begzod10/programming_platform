"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=7 (L8)."""
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

LESSON_ID = 660

TITLE_RU = "8-Бинарное дерево поиска (BST)"

TEXT_RU = """\
<h3>Что такое Binary Search Tree (BST)?</h3>
<p>Binary Search Tree (BST) &mdash; древовидная структура данных, каждый узел которой имеет максимум двух потомков (левого и правого), и обладающая важным <strong>свойством порядка</strong> (BST property): <em>значение левого потомка меньше родительского узла, а значение правого потомка &mdash; больше</em>.</p>
<p>Благодаря этому свойству операции поиска, добавления и удаления в BST в среднем случае выполняются за <strong>O(log n)</strong> &mdash; как и Binary Search, но для динамических (изменяемых) данных.</p>
<h3>Виды обхода дерева (Traversal)</h3>
<ul>
<li><strong>Inorder</strong> (лево &rarr; корень &rarr; право) &mdash; выдаёт элементы в порядке возрастания.</li>
<li><strong>Preorder</strong> (корень &rarr; лево &rarr; право) &mdash; полезен для копирования структуры дерева.</li>
<li><strong>Postorder</strong> (лево &rarr; право &rarr; корень) &mdash; полезен при удалении узлов.</li>
</ul>
<h3>Таблица сложности</h3>
<table>
<tr><th>Операция</th><th>Средний случай (сбалансированное)</th><th>Худший случай (несбалансированное)</th></tr>
<tr><td>Поиск</td><td>O(log n)</td><td>O(n)</td></tr>
<tr><td>Добавление</td><td>O(log n)</td><td>O(n)</td></tr>
<tr><td>Удаление</td><td>O(log n)</td><td>O(n)</td></tr>
</table>
<p>Худший случай возникает, когда дерево становится "несбалансированным" (skewed), то есть каждый узел имеет только одного потомка и дерево фактически превращается в LinkedList. Поэтому на практике применяются <em>самобалансирующиеся</em> (self-balancing) деревья, такие как AVL Tree или Red-Black Tree.</p>
<p>Следующая диаграмма показывает типичную структуру BST:</p>
<pre class="mermaid">
flowchart TB
  A["8"] --> B["3"]
  A --> C["10"]
  B --> D["1"]
  B --> E["6"]
  C --> F["14"]
</pre>
<p>Древовидные структуры BST широко применяются в задачах хранения отсортированных данных, функций автозаполнения (autocomplete) и поиска по диапазону (range query). Рекурсия является основным инструментом при работе с BST, поскольку каждое поддерево (subtree) само по себе также обладает свойством BST.</p>
"""

CODE_RU = """\
# Реализация Binary Search Tree (BST)

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    # Добавление нового значения - O(log n) в среднем
    def insert(self, value):
        new_node = TreeNode(value)
        if not self.root:
            self.root = new_node
            return self

        current = self.root
        while True:
            if value < current.value:
                if not current.left:
                    current.left = new_node
                    return self
                current = current.left
            else:
                if not current.right:
                    current.right = new_node
                    return self
                current = current.right

    # Поиск значения - O(log n) в среднем
    def search(self, value):
        current = self.root
        while current:
            if value == current.value:
                return True
            current = current.left if value < current.value else current.right
        return False

    # Inorder traversal - возвращает все значения в порядке возрастания
    def inorder_traversal(self, node="root", result=None):
        if result is None:
            result = []
        if node == "root":
            node = self.root
        if node:
            self.inorder_traversal(node.left, result)
            result.append(node.value)
            self.inorder_traversal(node.right, result)
        return result

    # Нахождение минимального значения дерева
    def find_min(self, node="root"):
        if node == "root":
            node = self.root
        while node and node.left:
            node = node.left
        return node.value if node else None


# Практика
bst = BinarySearchTree()
for value in [8, 3, 10, 1, 6, 14, 4, 7]:
    bst.insert(value)

print("Inorder (tartiblangan):", bst.inorder_traversal())
print("6 ni qidirish:", bst.search(6))  # True
print("100 ni qidirish:", bst.search(100))  # False
print("Minimal qiymat:", bst.find_min())
"""

EX = {
    3900: {
        "title": "Свойство BST",
        "description": "Согласно свойству BST, каким должно быть значение правого потомка относительно родительского узла?",
        "hint": "Слева — меньше, справа — больше.",
        "explanation": "Согласно свойству BST, значение левого потомка меньше родительского узла, а значение правого потомка — больше.",
    },
    3901: {
        "title": "Сложность BST",
        "description": "Какова средняя сложность поиска в сбалансированном BST?",
        "hint": "Как в Binary Search, на каждом шаге отбрасывается половина.",
        "explanation": "Поиск в сбалансированном BST в среднем случае O(log n), потому что на каждом шаге половина дерева исключается из поиска.",
    },
    3902: {
        "title": "Виды traversal",
        "description": "Какие из перечисленных считаются видами обхода (traversal) дерева BST?",
        "hint": "Binary Search — это алгоритм поиска, а не вид traversal.",
        "explanation": "Inorder, Preorder и Postorder — три основных вида обхода BST. Binary Search же — отдельный алгоритм поиска.",
    },
    3903: {
        "title": "Причина худшего случая",
        "description": "Запишите одним словом основную причину, по которой BST имеет сложность O(n) в худшем случае (например: каким становится дерево?).",
        "hint": "",
        "expected_answer": "skewed",
    },
    3904: {
        "title": "Порядок возрастания",
        "description": "Какой вид traversal при обходе BST даёт список в порядке возрастания? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "inorder",
    },
    3905: {
        "title": "Шаги добавления (insert)",
        "description": "Расположите шаги процесса добавления нового значения в BST в правильном порядке.",
        "hint": "",
    },
    3906: {
        "title": "Соответствие результатов traversal",
        "description": "Сопоставьте виды traversal с их основным назначением.",
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
