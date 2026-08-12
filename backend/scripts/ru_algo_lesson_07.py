"""Russian translation for Python: Algoritmlar va Ma'lumotlar Tuzilmasi,
lesson order=6 (L7)."""
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

LESSON_ID = 658

TITLE_RU = "7-HashMap (Хеш-таблица)"

TEXT_RU = """\
<h3>Что такое HashMap (Hash Table)?</h3>
<p>HashMap &mdash; структура данных, хранящая пары ключ-значение (key-value) и обеспечивающая доступ к ним в среднем за <strong>O(1)</strong>. Это её главное преимущество &mdash; если поиск в списке или LinkedList занимает O(n), в HashMap это происходит практически мгновенно.</p>
<h3>Как это работает</h3>
<p>Внутри HashMap <strong>хеш-функция</strong> превращает каждый ключ в числовой индекс, который указывает на место в списке (наборе bucket'ов). Например, хеш-функция может превратить ключ "email" в индекс 42, и значение сохраняется именно в этом месте.</p>
<h3>Разрешение коллизий (Collision Resolution)</h3>
<ul>
<li><strong>Chaining</strong> &mdash; все элементы, попавшие на один индекс, хранятся внутри этого bucket в виде LinkedList (или списка).</li>
<li><strong>Open Addressing</strong> &mdash; при возникновении коллизии алгоритм ищет следующее свободное место (например, linear probing).</li>
</ul>
<p><strong>Load factor</strong> (коэффициент загрузки) &mdash; отношение числа элементов к числу bucket'ов. Высокий load factor приводит к большему числу коллизий, поэтому HashMap обычно увеличивает свой размер (resize) при превышении определённого порога.</p>
<h3>Таблица сравнения</h3>
<table>
<tr><th>Операция</th><th>Средний случай</th><th>Худший случай</th></tr>
<tr><td>Добавление (set)</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Поиск (get)</td><td>O(1)</td><td>O(n)</td></tr>
<tr><td>Удаление (delete)</td><td>O(1)</td><td>O(n)</td></tr>
</table>
<p>Следующая диаграмма показывает структуру bucket'ов внутри hash table (методом chaining):</p>
<pre class="mermaid">
flowchart LR
  H["hash('email')=2"] --> B0["Bucket 0: пусто"]
  H --> B1["Bucket 1: пусто"]
  H --> B2["Bucket 2: [email -> user@site.com]"]
  H --> B3["Bucket 3: [age -> 25] -> [name -> Ali]"]
</pre>
<p>В Python природа HashMap реализована через <code>dict</code>. Объект <code>dict</code> позволяет использовать в качестве ключа любой неизменяемый (immutable) тип, удобно итерироваться и получать размер через <code>len()</code>. Внутри встроенного <code>dict</code> Python используется именно та логика хеш-таблицы, которую мы рассмотрели в этом уроке.</p>
"""

CODE_RU = """\
# Простая реализация HashMap (методом chaining)

class HashMap:
    def __init__(self, size=16):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    # Простая хеш-функция - превращает ключ в числовой индекс
    def _hash(self, key):
        hash_value = 0
        string_key = str(key)
        for i, char in enumerate(string_key):
            hash_value = (hash_value + ord(char) * (i + 1)) % self.size
        return hash_value

    # Добавление или обновление пары ключ-значение - O(1) в среднем
    def set(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]

        for entry in bucket:
            if entry[0] == key:
                entry[1] = value  # Обновление существующего ключа
                return
        bucket.append([key, value])  # Добавление новой пары

    # Получение значения по ключу - O(1) в среднем
    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for entry in bucket:
            if entry[0] == key:
                return entry[1]
        return None

    # Удаление ключа - O(1) в среднем
    def delete(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, entry in enumerate(bucket):
            if entry[0] == key:
                bucket.pop(i)
                return True
        return False

    def has(self, key):
        return self.get(key) is not None


# Практика
my_map = HashMap()
my_map.set("name", "Ali")
my_map.set("age", 25)
my_map.set("email", "ali@example.com")

print("name:", my_map.get("name"))  # Ali
print("age:", my_map.get("age"))  # 25
print("has phone:", my_map.has("phone"))  # False

my_map.delete("age")
print("age o'chirilgandan keyin:", my_map.get("age"))  # None

# Сравнение со встроенным dict Python
builtin_dict = {}
builtin_dict["name"] = "Ali"
print("Built-in dict:", builtin_dict["name"])
"""

EX = {
    3886: {
        "title": "Сложность HashMap",
        "description": "Какова средняя сложность получения значения по ключу в HashMap?",
        "hint": "Хеш-функция напрямую вычисляет индекс.",
        "explanation": "Поиск по ключу в HashMap в среднем случае O(1), потому что хеш-функция напрямую превращает ключ в индекс.",
    },
    3887: {
        "title": "Что такое коллизия",
        "description": "Что означает термин 'коллизия' (collision) в HashMap?",
        "hint": "Это связано с результатом хеш-функции.",
        "explanation": "Коллизия означает, что два разных ключа через хеш-функцию попадают на один и тот же индекс.",
    },
    3888: {
        "title": "Способы разрешения коллизий",
        "description": "Какие из перечисленных являются способами разрешения коллизий?",
        "hint": "Два относятся именно к HashMap, два — к другим темам.",
        "explanation": "Chaining и Open Addressing — два основных способа разрешения коллизий в HashMap.",
    },
    3889: {
        "title": "Превращение ключа в число",
        "description": "Как называется функция внутри HashMap, превращающая ключ в числовой индекс? (ответьте одним словом)",
        "hint": "",
        "expected_answer": "hash",
    },
    3890: {
        "title": "Отношение элементов к bucket'ам",
        "description": "Запишите термин, обозначающий отношение числа элементов к числу bucket'ов.",
        "hint": "",
        "expected_answer": "load factor",
    },
    3891: {
        "title": "Шаги HashMap.set()",
        "description": "Расположите шаги процесса добавления новой пары ключ-значение (set) в HashMap в правильном порядке.",
        "hint": "",
    },
    3892: {
        "title": "Соответствие структуры и сложности",
        "description": "Расположите структуры данных в соответствии со средней сложностью поиска: от самой быстрой к самой медленной.",
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
