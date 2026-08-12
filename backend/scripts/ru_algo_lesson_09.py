"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=8 (L9)."""
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

LESSON_ID = 662

TITLE_RU = "9-Граф (Graph)"

TEXT_RU = """\
<h3>Что такое граф (Graph)?</h3>
<p>Граф &mdash; структура данных, состоящая из <strong>узлов (vertices)</strong> и связывающих их <strong>рёбер (edges)</strong>. С помощью графа можно моделировать множество реальных явлений: социальные сети (сеть друзей), карты дорог, ссылки между веб-страницами.</p>
<h3>Типы графов</h3>
<ul>
<li><strong>Directed (Ориентированный)</strong> &mdash; рёбра движутся только в одном направлении (например, "follow" в Instagram).</li>
<li><strong>Undirected (Неориентированный)</strong> &mdash; рёбра двусторонние (например, "friend" в Facebook).</li>
<li><strong>Weighted (Взвешенный)</strong> &mdash; каждое ребро имеет свой "вес" (расстояние, стоимость), например расстояния на карте дорог.</li>
</ul>
<h3>Способы представления графа</h3>
<table>
<tr><th>Способ</th><th>Память</th><th>Проверка соседства</th><th>Удобство</th></tr>
<tr><td>Adjacency List</td><td>O(V + E)</td><td>O(число соседей)</td><td>Хорош для разреженных графов</td></tr>
<tr><td>Adjacency Matrix</td><td>O(V^2)</td><td>O(1)</td><td>Хорош для плотных графов</td></tr>
</table>
<p>На практике Adjacency List часто предпочтительнее, потому что большинство реальных графов (социальные сети, веб-страницы) "разрежены" &mdash; то есть число рёбер невелико относительно числа узлов.</p>
<h3>Алгоритмы обхода графа</h3>
<ul>
<li><strong>BFS (Breadth-First Search)</strong> &mdash; обходит слой за слоем (level by level) с помощью Queue. Используется для нахождения кратчайшего пути.</li>
<li><strong>DFS (Depth-First Search)</strong> &mdash; идёт максимально вглубь в одном направлении с помощью Stack (или рекурсии).</li>
</ul>
<p>Следующая диаграмма показывает простой неориентированный граф:</p>
<pre class="mermaid">
flowchart TB
  A["A"] --- B["B"]
  A --- C["C"]
  B --- D["D"]
  C --- D
  D --- E["E"]
</pre>
<p>Графы широко применяются в анализе социальных сетей, системах GPS-навигации, определении маршрутов в сети (routing) и рекомендательных системах (recommendation systems). BFS и DFS составляют основу почти всех алгоритмов на графах (например, нахождение кратчайшего пути, определение цикла).</p>
"""

CODE_RU = """\
from collections import deque


# Реализация Graph - методом adjacency list
class Graph:
    def __init__(self):
        self.adjacency_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    # Двусторонняя связь для неориентированного графа
    def add_edge(self, vertex1, vertex2):
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        self.adjacency_list[vertex1].append(vertex2)
        self.adjacency_list[vertex2].append(vertex1)

    # BFS - обход слой за слоем с помощью Queue
    def bfs(self, start_vertex):
        visited = {start_vertex}
        queue = deque([start_vertex])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result

    # DFS - обход вглубь с помощью рекурсии
    def dfs(self, start_vertex, visited=None, result=None):
        if visited is None:
            visited = set()
        if result is None:
            result = []

        visited.add(start_vertex)
        result.append(start_vertex)

        for neighbor in self.adjacency_list.get(start_vertex, []):
            if neighbor not in visited:
                self.dfs(neighbor, visited, result)
        return result


# Практика
graph = Graph()
graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("C", "D")
graph.add_edge("D", "E")

print("BFS natija:", graph.bfs("A"))  # ['A', 'B', 'C', 'D', 'E']
print("DFS natija:", graph.dfs("A"))  # ['A', 'B', 'D', 'C', 'E']
"""

EX = {
    3914: {
        "title": "Элементы графа",
        "description": "Как называются два основных элемента, составляющих граф?",
        "hint": "Один — узлы, другой — связывающие их рёбра.",
        "explanation": "Граф состоит из узлов (vertices) и связывающих их рёбер (edges).",
    },
    3915: {
        "title": "Структура BFS",
        "description": "Какую структуру данных использует алгоритм BFS?",
        "hint": "Для обхода слой за слоем (level by level) нужна структура FIFO.",
        "explanation": "BFS обходит слой за слоем с помощью Queue (FIFO).",
    },
    3916: {
        "title": "Типы графов",
        "description": "Какие из перечисленных являются типами графов?",
        "hint": "\"Balanced\" — это понятие, относящееся к деревьям.",
        "explanation": "Directed, Undirected и Weighted — основные типы графов. \"Balanced\" же используется в контексте деревьев (BST, AVL).",
    },
    3917: {
        "title": "Структура DFS",
        "description": "Какую структуру или механизм обычно использует алгоритм DFS? (ответьте одним словом, например: stack или рекурсия)",
        "hint": "",
        "expected_answer": "stack",
    },
    3918: {
        "title": "Представление разреженного графа",
        "description": "Запишите более эффективный по памяти способ представления разреженных (с малым числом рёбер) графов.",
        "hint": "",
        "expected_answer": "adjacency list",
    },
    3919: {
        "title": "Шаги BFS",
        "description": "Расположите шаги выполнения алгоритма BFS в правильном порядке.",
        "hint": "",
    },
    3920: {
        "title": "Сопоставление способов представления",
        "description": "Сопоставьте способы представления графа с соответствующими им свойствами.",
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
