"""Russian translation for Python: Ilg'or Mavzular, lesson order=5 (L6)."""
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

LESSON_ID = 720

TITLE_RU = "6-Type Hints глубже"

TEXT_RU = """\
<h2>Type Hints глубже — точное указание типов через модуль typing</h2>

<pre class="mermaid">
flowchart LR
    OPT["Optional[str]"] --> NONE["str ИЛИ None"]
    UNION["Union[int, str]"] --> EITHER["int ИЛИ str"]
    GENERIC["Stack[T]"] --> ANYTYPE["класс, работающий с любым типом T"]
    PROTOCOL["Protocol"] --> DUCK["без наследования, только совпадение 'формы'"]
</pre>

<p>Простые type hints (<code>def f(x: int) -> str</code>) вам уже знакомы. Теперь рассмотрим, как через модуль <code>typing</code> указывать <strong>более сложные</strong> случаи — значения "либо то, либо это", generic-классы и проверку типов на основе "протокола".</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — Optional и Union</h4>
<pre><code>from typing import Optional, Union

def foydalanuvchi_topish(id: int) -> Optional[str]:   # ❗ Optional[str] = Union[str, None]
    if id == 1:
        return "Olim"
    return None                                          # ❗ возврат None РАЗРЕШЁН

def id_korsatish(id: Union[int, str]) -> str:          # ❗ id может быть ЛИБО int, ЛИБО str
    return f"ID: {id}"

id_korsatish(101)        # ✅ int
id_korsatish("ABC-101")  # ✅ str</code></pre>

<h4>БЛОК 2 — Generic-класс (TypeVar)</h4>
<pre><code>from typing import Generic, TypeVar

T = TypeVar('T')                       # ❗ "переменная типа" - может означать любой тип

class Stack(Generic[T]):               # ❗ Stack - generic-класс, работающий с ЛЮБЫМ типом T
    def __init__(self) -> None:
        self._elementlar: list[T] = []

    def qoshish(self, item: T) -> None:
        self._elementlar.append(item)

    def olish(self) -> T:
        return self._elementlar.pop()

son_stack: Stack[int] = Stack()        # ❗ Stack[int] - Stack, работающий только с int
son_stack.qoshish(5)
# son_stack.qoshish("matn")             # ❌ type checker (mypy) выдаст ошибку: ожидался int, не str</code></pre>

<h4>БЛОК 3 — Protocol: проверка типов для "duck typing"</h4>
<pre><code>from typing import Protocol

class ChizishMumkin(Protocol):          # ❗ Protocol - наследование НЕ ОБЯЗАТЕЛЬНО, важна лишь "форма"
    def chizish(self) -> str: ...

class Doira:                            # ❗ НЕ НАСЛЕДУЕТ от ChizishMumkin!
    def chizish(self) -> str:
        return "○ chizildi"

class Kvadrat:
    def chizish(self) -> str:
        return "□ chizildi"

def shaklni_korsatish(shakl: ChizishMumkin) -> None:   # ❗ подходит любой объект с методом "chizish() -> str"
    print(shakl.chizish())

shaklni_korsatish(Doira())     # ✅ работает - у Doira есть chizish()
shaklni_korsatish(Kvadrat())   # ✅ работает, даже без наследования</code></pre>

<h3>🐛 Намеренная ошибка — использование Optional без проверки на None</h3>
<pre><code>def foydalanuvchi_topish(id: int) -> Optional[str]:
    if id == 1:
        return "Olim"
    return None

ism = foydalanuvchi_topish(2)
print(ism.upper())    # ❌ AttributeError: 'NoneType' object has no attribute 'upper'
# (type checker ПРЕДУПРЕДИЛ БЫ об этом заранее, но во время выполнения Python сам не проверяет!)</code></pre>

<p><strong>Результат:</strong> <code>Optional[str]</code> сообщает <strong>type checker'у</strong> (например <code>mypy</code>), что функция может вернуть <strong>либо <code>str</code>, либо <code>None</code></strong>. Но <strong>сам Python во время выполнения</strong> <strong>не проверяет</strong> type hints — они лишь "документированное обещание" и сигнал для внешних инструментов (mypy, IDE). Поэтому, зная о возможности <code>None</code>, писать реальную проверку вроде <code>if ism is not None</code> в коде &mdash; <strong>собственная ответственность</strong> разработчика.</p>

<h3>Теперь объясним</h3>

<h4>1. Есть ли разница между Optional[str] и Union[str, None]?</h4>
<p>Нет &mdash; <code>Optional[X]</code> фактически <strong>сокращение</strong> для <code>Union[X, None]</code>. <code>Optional[str]</code> означает "это значение может быть <code>str</code> или <code>None</code>".</p>

<h4>2. Зачем нужны TypeVar и Generic?</h4>
<p><code>TypeVar('T')</code> создаёт "переменную типа" &mdash; этот <code>T</code> впоследствии может соответствовать <strong>любому</strong> конкретному типу (<code>int</code>, <code>str</code>, другой класс). Через <code>Generic[T]</code> можно написать класс с этой переменной типа, позволяя безопасно использовать один класс <code>Stack</code> с <strong>разными типами</strong> данных (<code>Stack[int]</code>, <code>Stack[str]</code>).</p>

<h4>3. Зачем нужен Protocol?</h4>
<p><code>Protocol</code> объединяет философию "duck typing" Python (<em>"если оно ходит как утка и крякает как утка, значит это утка"</em>) с системой типов: класс <strong>не обязан наследоваться</strong> от <code>Protocol</code> &mdash; если у него есть нужные методы (например <code>chizish() -> str</code>), он считается <strong>соответствующим</strong> этому типу Protocol.</p>

<h4>4. Проверяются ли type hints во время выполнения?</h4>
<p><strong>Нет.</strong> Сам Python (CPython) не выдаёт никаких ошибок на основе type hints &mdash; они предназначены только для <strong>отдельных</strong> инструментов проверки типов вроде <code>mypy</code> и IDE. Это очень полезно для выявления ошибок <strong>на этапе написания</strong> кода, но не даёт никакой защиты <strong>во время запуска</strong> программы.</p>

<h4>5. Почему при работе с Optional нужна проверка на None?</h4>
<p><code>Optional[str]</code> сообщает, что функция <strong>может</strong> вернуть <code>None</code>, но это предупреждение работает только на уровне type checker. Во время выполнения у <code>None</code> <strong>нет</strong> методов вроде <code>.upper()</code>, свойственных <code>str</code>, поэтому разработчик <strong>сам</strong> должен написать проверку вроде <code>if natija is not None:</code>, чтобы предотвратить ошибку.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ <code>Optional[X]</code> — сокращение для <code>Union[X, None]</code></li>
<li>✅ <code>Union[A, B]</code> — означает, что значение может быть типа A или B</li>
<li>✅ <code>Generic[T]</code> + <code>TypeVar</code> — позволяют безопасно использовать один класс с разными типами</li>
<li>✅ <code>Protocol</code> — распознавание объектов как типа по "форме", без наследования</li>
<li>✅ Type hints — только для внешних инструментов (mypy, IDE), Python не проверяет их во время выполнения</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# УРОК 6: Type Hints глубже
# ════════════════════════════════════════════════════════════════════

from typing import Optional, Union, Generic, TypeVar, Protocol

# ─────────────────────────────────────────────────────────────────────
# 1) Optional и Union
# ─────────────────────────────────────────────────────────────────────


def foydalanuvchi_topish(id: int) -> Optional[str]:
    if id == 1:
        return "Olim"
    return None


def id_korsatish(id: Union[int, str]) -> str:
    return f"ID: {id}"


id_korsatish(101)
id_korsatish("ABC-101")

# ─────────────────────────────────────────────────────────────────────
# 2) Generic-класс (TypeVar)
# ─────────────────────────────────────────────────────────────────────

T = TypeVar('T')


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._elementlar: list = []

    def qoshish(self, item: T) -> None:
        self._elementlar.append(item)

    def olish(self) -> T:
        return self._elementlar.pop()


son_stack: Stack = Stack()
son_stack.qoshish(5)

# ─────────────────────────────────────────────────────────────────────
# 3) Protocol
# ─────────────────────────────────────────────────────────────────────


class ChizishMumkin(Protocol):
    def chizish(self) -> str: ...


class Doira:
    def chizish(self) -> str:
        return "○ chizildi"


class Kvadrat:
    def chizish(self) -> str:
        return "□ chizildi"


def shaklni_korsatish(shakl: ChizishMumkin) -> None:
    print(shakl.chizish())


shaklni_korsatish(Doira())
shaklni_korsatish(Kvadrat())

# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - Optional без проверки на None (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# ism = foydalanuvchi_topish(2)
# print(ism.upper())    # ❌ AttributeError: 'NoneType' object has no attribute 'upper'
"""

EX = {
    4206: {
        "title": "Что означает Optional[str]?",
        "description": "Что означает type hint Optional[str]?",
        "hint": "Это сокращение для Union[str, None].",
        "explanation": "Optional[str] — сокращение для Union[str, None], то есть значение может быть str или None.",
    },
    4207: {
        "title": "Зачем нужен Protocol?",
        "description": "Для чего используется typing.Protocol?",
        "hint": "Это соответствует философии \"duck typing\" Python.",
        "explanation": "Protocol позволяет распознавать объект как соответствующий типу, если у него есть нужные методы (например chizish() -> str), даже без наследования от Protocol.",
    },
    4208: {
        "title": "Расположите процесс работы с Stack[int]",
        "description": "Расположите процесс создания son_stack: Stack[int] = Stack() и работы с ним.",
        "hint": "",
        "explanation": "",
    },
    4209: {
        "title": "Проверяются ли type hints во время выполнения?",
        "description": "Сам Python (CPython) автоматически выдаёт ошибку во время запуска кода при несоответствии type hints? (ответьте да/нет)",
        "hint": "Для каких инструментов работают type hints?",
        "expected_answer": "нет",
    },
    4210: {
        "title": "Почему при работе с Optional нужна проверка на None?",
        "description": (
            "Если foydalanuvchi_topish(2) из функции, возвращающей "
            "Optional[str], вернёт None, и сразу же вызвать у этого "
            "результата .upper(), почему возникает ошибка "
            "AttributeError, хотя type hint это \"предполагал\"? "
            "Объясните своими словами."
        ),
        "hint": "Кому type hints дают \"сигнал\" — самому Python или внешним инструментам?",
        "expected_answer": "Optional[str] даёт сигнал только type checker'у (например mypy) и IDE о том, что \"эта функция может вернуть str или None\" — это \"документированное обещание\", но сам Python во время выполнения (CPython) не проверяет это и не даёт никакой защиты. У объекта None вообще нет методов str, таких как .upper(), поэтому если результат действительно окажется None, а в коде это заранее не проверено (например через if natija is not None:), программа столкнётся с ошибкой AttributeError во время выполнения.",
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
