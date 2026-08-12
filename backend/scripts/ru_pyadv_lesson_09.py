"""Russian translation for Python: Ilg'or Mavzular, lesson order=9 (L9)."""
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

LESSON_ID = 728

TITLE_RU = "9-Magic methods глубже"

TEXT_RU = """\
<h2>Magic methods глубже — добавление вашим объектам поведения Python</h2>

<pre class="mermaid">
flowchart LR
    EQ["__eq__"] --> COMPARE["определяет, как работает оператор =="]
    REPR["__repr__"] --> DEBUG["определяет, как выглядит в print()/debug"]
    DATACLASS["@dataclass"] --> AUTO["__init__, __repr__, __eq__ создаются АВТОМАТИЧЕСКИ"]
</pre>

<p>В уроке 1 мы видели <code>__str__</code>/<code>__doc__</code>, в уроке 3 &mdash; <code>__enter__</code>/<code>__exit__</code>. Это члены большого семейства, называемого <strong>magic methods</strong> (или "dunder methods"). Теперь посмотрим, как определить стандартные операторы вроде <code>==</code>, <code>&lt;</code>, <code>len()</code> для <strong>собственного класса</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — __eq__ и __repr__: сравнение и отображение</h4>
<pre><code>class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __eq__(self, boshqa):              # ❗ срабатывает при вызове оператора ==
        return (self.sarlavha == boshqa.sarlavha and
                self.sahifalar == boshqa.sahifalar)

    def __repr__(self):                     # ❗ срабатывает при показе через print() или в консоли
        return f"Kitob('{self.sarlavha}', {self.sahifalar} sahifa)"

k1 = Kitob("Python", 300)
k2 = Kitob("Python", 300)
print(k1 == k2)     # ✅ True - благодаря __eq__, хотя они РАЗНЫЕ объекты в памяти
print(k1)            # Kitob('Python', 300 sahifa) - красиво выводится благодаря __repr__</code></pre>

<h4>БЛОК 2 — __lt__ и sort(): сортировка объектов</h4>
<pre><code>class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __lt__(self, boshqa):               # ❗ для оператора '<', нужен для sort()
        return self.sahifalar < boshqa.sahifalar

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar})"

kitoblar = [Kitob("A", 300), Kitob("B", 150), Kitob("C", 450)]
kitoblar.sort()                              # ❗ внутри sort() используется __lt__
print(kitoblar)   # [Kitob('B', 150), Kitob('A', 300), Kitob('C', 450)]</code></pre>

<h4>БЛОК 3 — @dataclass: автоматическое создание magic methods</h4>
<pre><code>from dataclasses import dataclass

@dataclass                                   # ❗ АВТОМАТИЧЕСКИ создаёт __init__, __repr__, __eq__
class Kitob:
    sarlavha: str
    sahifalar: int

k1 = Kitob("Python", 300)    # ❗ __init__ не написан вручную, но работает!
k2 = Kitob("Python", 300)

print(k1)          # Kitob(sarlavha='Python', sahifalar=300) - __repr__ автоматически
print(k1 == k2)    # True - __eq__ автоматически</code></pre>

<h3>🐛 Намеренная ошибка — написали __eq__, забыли __hash__</h3>
<pre><code>class Kitob:
    def __init__(self, sarlavha):
        self.sarlavha = sarlavha

    def __eq__(self, boshqa):
        return self.sarlavha == boshqa.sarlavha
    # __hash__ НЕ НАПИСАН!

kitoblar_set = {Kitob("Python"), Kitob("Django")}
# ❌ TypeError: unhashable type: 'Kitob'
# (когда написан __eq__, Python АВТОМАТИЧЕСКИ делает __hash__ равным None!)</code></pre>

<p><strong>Результат:</strong> в Python по правилу, если два объекта считаются <strong>равными</strong> через <code>__eq__</code>, их значение <code>hash()</code> тоже должно быть <strong>одинаковым</strong>. Поэтому, если в классе <code>__eq__</code> написан <strong>вручную</strong>, Python в целях безопасности <strong>автоматически</strong> устанавливает <code>__hash__</code> в <code>None</code> (класс становится "нехешируемым") &mdash; это мешает использовать объект как элемент <code>set</code> или ключ <code>dict</code>. Решение: если объект должен быть хешируемым, нужно <strong>вручную</strong> написать и <code>__hash__</code> (или использовать <code>@dataclass(frozen=True)</code>, который решает это автоматически).</p>

<h3>Теперь объясним</h3>

<h4>1. Что такое magic methods (dunder methods)?</h4>
<p>Методы, начинающиеся и заканчивающиеся двойным подчёркиванием (<code>__init__</code>, <code>__eq__</code>, <code>__repr__</code> и т.д.) &mdash; они "обучают" Python тому, <strong>как</strong> ваш класс должен работать со стандартными операторами (<code>==</code>, <code>&lt;</code>, <code>len()</code>, <code>print()</code>).</p>

<h4>2. Разница между __eq__ и __repr__</h4>
<p><code>__eq__</code> срабатывает при вызове оператора <code>==</code>, <strong>сравнивая</strong> два объекта. <code>__repr__</code> определяет, какой <strong>текст</strong> выводится при <code>print()</code> объекта или его показе в консоли (очень полезно для отладки).</p>

<h4>3. Зачем нужен __lt__?</h4>
<p><code>__lt__</code> (<em>less than</em>) определяет оператор <code>&lt;</code>. Функции <code>list.sort()</code> и <code>sorted()</code> внутренне используют именно <code>__lt__</code> &mdash; поэтому объекты класса с написанным <code>__lt__</code> можно сортировать напрямую.</p>

<h4>4. Что делает @dataclass?</h4>
<p>Декоратор <code>@dataclass</code> <strong>автоматически</strong> создаёт <code>__init__</code>, <code>__repr__</code> и <code>__eq__</code> для классов, предназначенных в основном для <strong>хранения данных</strong> &mdash; достаточно объявить поля класса (с типами), остальной "шаблонный" (boilerplate) код писать не нужно.</p>

<h4>5. Почему при написании __eq__ нужен и __hash__?</h4>
<p>Правило Python: <strong>равные</strong> объекты обязаны иметь одинаковое значение <code>hash()</code> (это нужно для правильной работы <code>set</code>/<code>dict</code>). Когда <code>__eq__</code> написан вручную, Python не может автоматически гарантировать это правило, поэтому в качестве меры предосторожности устанавливает <code>__hash__</code> в <code>None</code>. Если объект должен быть хешируемым, разработчик должен исправить это <strong>вручную</strong> (или использовать <code>@dataclass(frozen=True)</code>).</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Magic methods (<code>__eq__</code>, <code>__repr__</code>, <code>__lt__</code>) добавляют вашему классу поведение стандартных операторов</li>
<li>✅ <code>__eq__</code> — для <code>==</code>, <code>__repr__</code> — для <code>print()</code>/debug, <code>__lt__</code> — для <code>&lt;</code>/<code>sort()</code></li>
<li>✅ <code>@dataclass</code> автоматически создаёт <code>__init__</code>, <code>__repr__</code>, <code>__eq__</code></li>
<li>✅ При ручном написании <code>__eq__</code> Python автоматически делает <code>__hash__</code> равным <code>None</code></li>
<li>✅ Для объектов, которые должны быть хешируемыми, нужно вручную написать <code>__hash__</code> или использовать <code>frozen=True</code></li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 9: Magic methods глубже
# ════════════════════════════════════════════════════════════════════

from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────
# 1) __eq__ и __repr__
# ─────────────────────────────────────────────────────────────────────


class Kitob:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __eq__(self, boshqa):
        return (self.sarlavha == boshqa.sarlavha and
                self.sahifalar == boshqa.sahifalar)

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar} sahifa)"


k1 = Kitob("Python", 300)
k2 = Kitob("Python", 300)
print(k1 == k2)
print(k1)

# ─────────────────────────────────────────────────────────────────────
# 2) __lt__ - сортировка
# ─────────────────────────────────────────────────────────────────────


class KitobSaralanuvchi:
    def __init__(self, sarlavha, sahifalar):
        self.sarlavha = sarlavha
        self.sahifalar = sahifalar

    def __lt__(self, boshqa):
        return self.sahifalar < boshqa.sahifalar

    def __repr__(self):
        return f"Kitob('{self.sarlavha}', {self.sahifalar})"


kitoblar = [KitobSaralanuvchi("A", 300), KitobSaralanuvchi("B", 150), KitobSaralanuvchi("C", 450)]
kitoblar.sort()
print(kitoblar)

# ─────────────────────────────────────────────────────────────────────
# 3) @dataclass - автоматические magic methods
# ─────────────────────────────────────────────────────────────────────


@dataclass
class KitobDC:
    sarlavha: str
    sahifalar: int


k3 = KitobDC("Python", 300)
k4 = KitobDC("Python", 300)

print(k3)
print(k3 == k4)

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - написан __eq__, забыт __hash__ (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# class KitobXato:
#     def __init__(self, sarlavha):
#         self.sarlavha = sarlavha
#     def __eq__(self, boshqa):
#         return self.sarlavha == boshqa.sarlavha
#     # __hash__ НЕ НАПИСАН!
#
# kitoblar_set = {KitobXato("Python"), KitobXato("Django")}
# ❌ TypeError: unhashable type: 'KitobXato'
"""

EX = {
    4244: {
        "title": "Для чего используется __eq__?",
        "description": "Для чего в основном нужно написание метода __eq__ в классе?",
        "hint": "Это срабатывает при использовании знака ==.",
        "explanation": "Метод __eq__ срабатывает при вызове оператора == и определяет, какие условия должны выполняться, чтобы два объекта считались \"равными\".",
    },
    4245: {
        "title": "Что делает @dataclass?",
        "description": "Что делает декоратор @dataclass, применённый к классу?",
        "hint": "Это предотвращает написание \"шаблонного\" (boilerplate) кода.",
        "explanation": "Декоратор @dataclass автоматически создаёт методы __init__, __repr__ и __eq__ на основе полей класса, разработчику не нужно писать их вручную.",
    },
    4246: {
        "title": "Расположите процесс работы kitoblar.sort()",
        "description": "Расположите процесс, происходящий при вызове sort() для списка объектов Kitob с написанным __lt__.",
        "hint": "",
        "explanation": "",
    },
    4247: {
        "title": "Метод, автоматически становящийся None при написании __eq__",
        "description": "Какой метод Python автоматически делает равным None, когда в классе вручную написан __eq__? (напишите название)",
        "hint": "Этот метод нужен для использования как элемент set/ключ dict.",
        "expected_answer": "__hash__",
    },
    4248: {
        "title": "Почему при написании __eq__ нужен и __hash__?",
        "description": (
            "В классе Kitob написан __eq__, но не написан __hash__. "
            "Почему при создании set вроде {Kitob(\"Python\"), "
            "Kitob(\"Django\")} возникает ошибка \"TypeError: "
            "unhashable type\"? Объясните своими словами."
        ),
        "hint": "Каким должно быть значение hash у \"равных\" объектов в Python?",
        "expected_answer": "В Python есть правило: если два объекта считаются равными через __eq__, их значение hash() обязательно должно быть одинаковым (на этом правиле основана корректная работа set и dict). Когда __eq__ написан разработчиком вручную, Python не может автоматически гарантировать соблюдение этого правила, поэтому в качестве меры предосторожности автоматически устанавливает метод __hash__ в None — это делает класс \"нехешируемым\". В результате при попытке использовать объекты такого класса как элемент set или ключ dict, Python выдаёт ошибку \"unhashable type\".",
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
