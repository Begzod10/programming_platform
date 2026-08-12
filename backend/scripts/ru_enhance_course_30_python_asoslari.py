"""Russian translations for the enhance_course_30_python_asoslari.py content additions."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from write_ru_translations import _write  # noqa: E402

MARKER_RU = "🐛 Намеренная ошибка"

BUG_HTML_RU = {
    219: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пишет такую проверку:</p>
<pre><code class="lang-python">narx1 = 0.1
narx2 = 0.2
jami = narx1 + narx2
print(jami == 0.3)</code></pre>
<p><strong>Результат:</strong> <code>False</code>! Хотя "математически" 0.1 + 0.2 кажется равным 0.3. Причина: компьютер хранит числа <code>float</code> в двоичной системе счисления, и такие числа, как <code>0.1</code>, невозможно представить <strong>точно</strong> (так же, как 1/3 нельзя точно записать десятичной дробью). На самом деле <code>0.1 + 0.2 = 0.30000000000000004</code>.</p>
<p><strong>Правильное решение:</strong> не сравнивайте float напрямую через <code>==</code>. Вместо этого проверяйте, что разница очень мала: <code>abs(jami - 0.3) &lt; 1e-9</code>.</p>""",
    220: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пытается "исправить" одну букву в строке:</p>
<pre><code class="lang-python">ism = "Alimjon"
ism[0] = "S"
print(ism)</code></pre>
<p><strong>Результат:</strong> <code>TypeError: 'str' object does not support item assignment</code>. Строки в Python <strong>неизменяемы (immutable)</strong> — после создания их нельзя изменить по индексу (в отличие от списков).</p>
<p><strong>Правильное решение:</strong> нужно создать новую строку: <code>ism = "S" + ism[1:]</code> или <code>ism = ism.replace("A", "S", 1)</code>.</p>""",
    222: f"""<h3>{MARKER_RU}</h3>
<p>Ученик проверяет, введён ли балл, так:</p>
<pre><code class="lang-python">def natija_korsat(ball):
    if ball:
        print(f"Sizning balingiz: {{ball}}")
    else:
        print("Ball kiritilmagan!")

natija_korsat(0)</code></pre>
<p><strong>Результат:</strong> выводится <code>"Ball kiritilmagan!"</code> ("Балл не введён!") — хотя <code>0</code> на самом деле <strong>настоящее, корректное значение</strong> (студент действительно мог получить 0 баллов)! Причина: в Python при <code>if значение:</code> числа <code>0</code>, <code>0.0</code>, <code>""</code>, <code>[]</code>, <code>None</code>, <code>False</code> — все считаются "falsy" (ложными). Программа <strong>не может отличить</strong> "балл не введён" (<code>None</code>) от "балл равен нулю" (<code>0</code>).</p>
<p><strong>Правильное решение:</strong> нужна явная проверка на <code>None</code>: <code>if ball is not None:</code>.</p>""",
    224: f"""<h3>{MARKER_RU}</h3>
<p>Ученик пишет функцию для добавления элемента в список:</p>
<pre><code class="lang-python">def royxatga_qosh(element, royxat=[]):
    royxat.append(element)
    return royxat

print(royxatga_qosh("olma"))
print(royxatga_qosh("nok"))</code></pre>
<p><strong>Результат:</strong> вместо ожидаемого <code>['nok']</code> выводится <strong><code>['olma', 'nok']</code></strong>! Причина: в Python значения аргументов по умолчанию создаются <strong>только ОДИН РАЗ</strong>, при определении функции — не при каждом вызове. Поэтому <code>royxat=[]</code> на самом деле указывает на <strong>один общий список для всех вызовов</strong>.</p>
<p><strong>Правильное решение:</strong> никогда не используйте изменяемый объект (list, dict) как значение по умолчанию: <code>def royxatga_qosh(element, royxat=None): royxat = royxat or []</code>.</p>""",
    226: f"""<h3>{MARKER_RU}</h3>
<p>Ученик создаёт несколько функций (lambda) внутри цикла:</p>
<pre><code class="lang-python">funksiyalar = []
for i in range(3):
    funksiyalar.append(lambda: i)

print([f() for f in funksiyalar])</code></pre>
<p><strong>Результат:</strong> вместо ожидаемого <code>[0, 1, 2]</code> выводится <strong><code>[2, 2, 2]</code></strong>! Причина: lambda-функция запоминает <strong>не значение</strong> <code>i</code> на момент создания, а <strong>ссылку</strong> на переменную <code>i</code> ("позднее связывание" — late binding). После завершения цикла <code>i</code> имеет последнее значение — <code>2</code> — и именно его возвращают все lambda.</p>
<p><strong>Правильное решение:</strong> "зафиксировать" текущее значение <code>i</code> через аргумент по умолчанию: <code>lambda i=i: i</code>.</p>""",
    227: f"""<h3>{MARKER_RU}</h3>
<p>Ученик хочет удалить из словаря ключи по определённому условию:</p>
<pre><code class="lang-python">narxlar = {{"olma": 5000, "nok": 0, "uzum": 12000, "shaftoli": 0}}

for mahsulot in narxlar:
    if narxlar[mahsulot] == 0:
        del narxlar[mahsulot]</code></pre>
<p><strong>Результат:</strong> <code>RuntimeError: dictionary changed size during iteration</code>. Итератор цикла <code>for</code> в Python опирается на <strong>внутреннюю структуру</strong> словаря — изменять размер словаря (добавлять/удалять элементы) во время работы этого же цикла запрещено.</p>
<p><strong>Правильное решение:</strong> сначала собрать список ключей на удаление, затем удалить их в отдельном цикле: <code>uchun_ochirish = [k for k, v in narxlar.items() if v == 0]</code>, а затем удалить их отдельно. Либо итерировать по <code>narxlar.copy()</code>.</p>""",
    230: f"""<h3>{MARKER_RU}</h3>
<p>Ученик создаёт список оценок для каждого студента так:</p>
<pre><code class="lang-python">class Talaba:
    baholar = []   # атрибут уровня класса!

    def __init__(self, ism):
        self.ism = ism

ali = Talaba("Ali")
vali = Talaba("Vali")

ali.baholar.append(5)
print(vali.baholar)</code></pre>
<p><strong>Результат:</strong> <code>[5]</code> — в списке оценок Vali тоже оказывается оценка Ali! Причина: <code>baholar = []</code> написан на <strong>уровне класса</strong>, а не внутри <code>__init__</code> — это означает <strong>один общий</strong> список для всех объектов <code>Talaba</code>, а не отдельный для каждого.</p>
<p><strong>Правильное решение:</strong> атрибуты, специфичные для каждого объекта (instance), должны создаваться внутри <code>__init__</code> как <code>self.baholar = []</code>.</p>""",
    231: f"""<h3>{MARKER_RU}</h3>
<p>Ученик, чтобы "красиво" обработать ошибки, пишет так:</p>
<pre><code class="lang-python">try:
    fayl = open("malumot.txt")
    son = int(fayl.read())
    natija = 100 / son
except:
    print("Xatolik yuz berdi")</code></pre>
<p><strong>Результат:</strong> программа работает, но <strong>невозможно узнать</strong>, какая именно ошибка произошла — файл не найден (<code>FileNotFoundError</code>), число указано неверно (<code>ValueError</code>), деление на ноль (<code>ZeroDivisionError</code>)? Голый <code>except:</code> "проглатывает" <strong>абсолютно все</strong> исключения, даже <code>KeyboardInterrupt</code> (Ctrl+C) и логические ошибки самого разработчика — это делает отладку практически невозможной.</p>
<p><strong>Правильное решение:</strong> всегда указывайте <strong>конкретные</strong> типы исключений: <code>except FileNotFoundError:</code>, <code>except ValueError:</code>, <code>except ZeroDivisionError:</code> — с соответствующим сообщением для каждого.</p>""",
}

NEW_EXERCISES_RU = {
    219: {
        "uz_title": "print(0.1 + 0.2 == 0.3) nima chiqaradi?",
        "title": "Что выведет print(0.1 + 0.2 == 0.3)?",
        "description": "Как вы думаете, что выведет следующий код?\n`print(0.1 + 0.2 == 0.3)`",
        "options": '["True", "False", "SyntaxError", "0.3"]',
        "correct_answers": "B",
        "hint": "В какой системе счисления компьютер хранит числа float — десятичной или двоичной?",
        "explanation": "Числа float хранятся в двоичном формате IEEE 754, и такие десятичные дроби, как 0.1, невозможно представить в нём точно. 0.1 + 0.2 на самом деле равно 0.30000000000000004, поэтому == 0.3 возвращает False.",
    },
    220: {
        "uz_title": "ism = \"Alimjon\"; ism[0] = \"S\" kodini ishga tushirsak nima bo'ladi?",
        "title": "Что произойдёт при выполнении кода ism = \"Alimjon\"; ism[0] = \"S\"?",
        "description": "Какой результат даст следующий код?\n`ism = \"Alimjon\"`\n`ism[0] = \"S\"`",
        "options": '["ism изменится и станет \\"Slimjon\\"", "TypeError: \'str\' object does not support item assignment", "Ничего не изменится, код спокойно выполнится", "Появится IndexError"]',
        "correct_answers": "B",
        "hint": "Изменяемы ли строки в Python так же, как списки?",
        "explanation": "Строки в Python — неизменяемый (immutable) тип. Попытка изменить элемент по индексу вызывает TypeError. Если нужно новое значение, создаётся совершенно новая строка.",
    },
    222: {
        "uz_title": "natija_korsat(0) chaqirilsa, funksiya nima chop etadi?",
        "title": "Что выведет функция при вызове natija_korsat(0)?",
        "description": "def natija_korsat(ball):\n    if ball:\n        print(f\"Sizning balingiz: {ball}\")\n    else:\n        print(\"Ball kiritilmagan!\")\n\nЧто выведется на экран при natija_korsat(0), и почему это считается ошибкой?",
        "expected_answer": "Выведется \"Ball kiritilmagan!\" (\"Балл не введён!\"), хотя 0 — настоящее значение. Причина: в Python при if ball: число 0 считается 'falsy', так же как None. Программа не различает 0 и None. Правильное решение: использовать if ball is not None:.",
        "hint": "Какие значения в Python считаются 'falsy' (ложными)?",
        "explanation": "0, 0.0, \"\", [], {}, None, False — все они оцениваются как False в условии if. Если 0 может быть настоящим значением, его нельзя путать с None — нужна явная проверка 'is not None'.",
    },
    224: {
        "uz_title": "royxatga_qosh(\"olma\") va royxatga_qosh(\"nok\") ketma-ket chaqirilsa, ikkinchisi nima qaytaradi?",
        "title": "Что вернёт второй вызов, если подряд вызвать royxatga_qosh(\"olma\") и royxatga_qosh(\"nok\")?",
        "description": "def royxatga_qosh(element, royxat=[]):\n    royxat.append(element)\n    return royxat\n\nПри вызове royxatga_qosh(\"olma\"), а затем royxatga_qosh(\"nok\"), что вернёт второй вызов?",
        "options": '["[\'nok\']", "[\'olma\', \'nok\']", "[\'olma\']", "Появится TypeError"]',
        "correct_answers": "B",
        "hint": "Когда Python создаёт значения аргументов по умолчанию — при каждом вызове, или один раз при определении функции?",
        "explanation": "Изменяемый аргумент по умолчанию (например пустой список) создаётся ТОЛЬКО ОДИН РАЗ при определении функции, и все последующие вызовы ссылаются на этот же объект. Поэтому изменения из предыдущего вызова сохраняются.",
    },
    226: {
        "uz_title": "for i in range(3): funksiyalar.append(lambda: i) — [f() for f in funksiyalar] nima qaytaradi?",
        "title": "Что вернёт [f() for f in funksiyalar] после цикла с lambda?",
        "description": "funksiyalar = []\nfor i in range(3):\n    funksiyalar.append(lambda: i)\n\nЧто вернёт [f() for f in funksiyalar]?",
        "options": '["[0, 1, 2]", "[2, 2, 2]", "[0, 0, 0]", "TypeError"]',
        "correct_answers": "B",
        "hint": "Lambda запоминает значение переменной или ссылку на неё?",
        "explanation": "Lambda через closure сохраняет ССЫЛКУ на переменную i, а не её значение на момент создания. После цикла i становится равным 2, и все lambda при вызове возвращают именно это последнее значение — это проблема 'позднего связывания closure'.",
    },
    227: {
        "uz_title": "Lug'at ustida for bilan iteratsiya qilib, shu ichida del bilan kalit o'chirilsa nima bo'ladi?",
        "title": "Что произойдёт, если удалять ключ словаря через del прямо во время цикла for по этому словарю?",
        "description": "for mahsulot in narxlar:\n    if narxlar[mahsulot] == 0:\n        del narxlar[mahsulot]\n\nЧто произойдёт при выполнении этого кода, и почему?",
        "expected_answer": "Появится ошибка RuntimeError: dictionary changed size during iteration. Цикл for в Python во время работы со словарём опирается на его внутреннюю структуру, изменять словарь (добавлять/удалять элементы) в это время запрещено. Решение: сначала собрать ключи на удаление в отдельный список, затем удалить их в отдельном цикле, либо итерировать по narxlar.copy().",
        "hint": "Можно ли изменять размер коллекции, по которой идёт цикл, прямо во время его работы?",
        "explanation": "Внутренние итераторы Python полагаются на то, что размер коллекции не меняется во время цикла. Если он меняется, выбрасывается RuntimeError — это сделано намеренно, чтобы избежать потери данных.",
    },
    230: {
        "uz_title": "ali.baholar.append(5) qilingandan keyin, nega vali.baholar ham [5] bo'lib qoladi?",
        "title": "Почему после ali.baholar.append(5) список vali.baholar тоже становится [5]?",
        "description": "class Talaba:\n    baholar = []\n    def __init__(self, ism):\n        self.ism = ism\n\nali = Talaba(\"Ali\"); vali = Talaba(\"Vali\")\nali.baholar.append(5)\nprint(vali.baholar)\n\nКакой результат, и почему?",
        "options": '["[] — оценки vali остаются пустыми", "[5] — baholar объявлен на уровне класса и общий для всех объектов", "Появится AttributeError", "Выведется [5, 5]"]',
        "correct_answers": "B",
        "hint": "Где написано baholar = [] — внутри __init__ или на уровне класса? Что означает эта разница?",
        "explanation": "Атрибут уровня класса (написанный вне __init__) общий для всех экземпляров — он создаётся только один раз, при создании класса. Если нужен отдельный список для каждого объекта, его нужно создавать внутри __init__ как self.baholar = [].",
    },
    231: {
        "uz_title": "Yalang'och except: nima uchun xavfli hisoblanadi?",
        "title": "Почему голый except: считается опасным?",
        "description": "try:\n    ...\nexcept:\n    print(\"Xatolik yuz berdi\")\n\nЭтот код работает, но почему он не рекомендуется в профессиональном коде?",
        "expected_answer": "Голый except: перехватывает абсолютно все исключения (даже KeyboardInterrupt, SystemExit и настоящие ошибки разработчика), невозможно узнать, какая именно ошибка произошла, что усложняет отладку. Правильный подход: перехватывать каждый конкретный тип исключения отдельным блоком except (например except ValueError:, except FileNotFoundError:).",
        "hint": "Сколько типов ошибок перехватывает except: без указания типа — только ожидаемые, или вообще все?",
        "explanation": "Голый except перехватывает все Exception (и даже BaseException), включая настоящие ошибки, о которых разработчик должен знать. Это 'скрывает' проблему и затрудняет её обнаружение в будущем.",
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as db:
        for lesson_id, bug_html_ru in BUG_HTML_RU.items():
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()

            old_ru_text = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "text_content",
            ))).scalar_one().translated_text
            old_ru_sections = (await db.execute(select(TranslationCache).where(
                TranslationCache.entity_type == "lesson", TranslationCache.entity_id == lesson_id,
                TranslationCache.lang == "ru", TranslationCache.field_name == "sections_json",
            ))).scalar_one().translated_text

            new_ru_text = old_ru_text + "\n\n" + bug_html_ru
            await _write(db, "lesson", lesson_id, "text_content", lesson.text_content, new_ru_text)

            ru_tree = json.loads(old_ru_sections)
            uz_tree = json.loads(lesson.sections_json)
            uz_text_sections = [s for s in uz_tree if s["type"] == "text"]
            ru_text_sections = [s for s in ru_tree if s["type"] == "text"]
            assert len(uz_text_sections) == len(ru_text_sections)
            ru_text_sections[-1]["html"] = (ru_text_sections[-1].get("html") or "") + "\n\n" + bug_html_ru

            uz_exercise_section = next(s for s in uz_tree if s["type"] == "exercise")
            ru_exercise_section = next(s for s in ru_tree if s["type"] == "exercise")
            spec = NEW_EXERCISES_RU[lesson_id]
            uz_ex_dict = next(e for e in uz_exercise_section["exercises"] if e["title"] == spec["uz_title"])
            ex_id = uz_ex_dict["id"]
            ru_ex_dict = dict(uz_ex_dict)
            ru_ex_dict["title"] = spec["title"]
            ru_ex_dict["description"] = spec["description"]
            ru_ex_dict["hint"] = spec["hint"]
            ru_ex_dict["explanation"] = spec.get("explanation", "")
            if "expected_answer" in spec:
                ru_ex_dict["expected_answer"] = spec["expected_answer"]
            ru_exercise_section["exercises"].append(ru_ex_dict)

            new_ru_sections_json = json.dumps(ru_tree, ensure_ascii=False)
            await _write(db, "lesson", lesson_id, "sections_json", lesson.sections_json, new_ru_sections_json)

            ex = (await db.execute(select(Exercise).where(Exercise.id == ex_id))).scalar_one()
            await _write(db, "exercise", ex_id, "title", ex.title, spec["title"])
            await _write(db, "exercise", ex_id, "description", ex.description, spec["description"])
            await _write(db, "exercise", ex_id, "hint", ex.hint or "", spec["hint"])
            await _write(db, "exercise", ex_id, "explanation", ex.explanation or "", spec.get("explanation", ""))
            if ex.expected_answer:
                await _write(db, "exercise", ex_id, "expected_answer", ex.expected_answer, spec.get("expected_answer", ""))

            print(f"lesson {lesson_id}: RU translation written (exercise {ex_id})")

        await db.commit()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
