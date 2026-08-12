"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=6 (L7)."""
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

LESSON_ID = 798

TITLE_RU = "7-Финальная полировка и деплой (завершение CAPSTONE)"

TEXT_RU = """\
<h2>Этап 7 (завершение CAPSTONE): деплой и ошибка "зелёный CI, красная реальность"</h2>

<pre class="mermaid">
flowchart LR
    PUSH["Код запушен"] --> CI["CI: запускается тестовый скрипт"]
    CI --> SCRIPT{"Скрипт ПРАВИЛЬНО передаёт код выхода?"}
    SCRIPT -->|"Неправильно: ошибка проглатывается"| GREEN["CI: 'успешно' - зелёная галочка"]
    SCRIPT -->|"Правильно: код выхода передаётся"| RED["CI: при провале тестов - КРАСНЫЙ"]
    GREEN --> DEPLOY["Деплой происходит - хотя тесты СЛОМАНЫ!"]
</pre>

<p>Собственный мини-capstone курса Python: Testlash (6-й урок: "Полностью протестированный Flask API") и собственный мини-capstone курса Python: Algoritmlar (10-й урок: "Практика алгоритмов") — оба в малом масштабе показали идею "завершённого, протестированного проекта". Это — настоящий, полномасштабный финальный этап RankVault. И здесь раскрывается самое <strong>обнажённое</strong> проявление идеи, которую вы видели на протяжении всего capstone: на этот раз даже <strong>сам CI</strong> — система, которая должна вас защищать — может дать ложный сигнал.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — CI: запуск тестов при каждом push</h4>
<pre><code># .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-fail-under=80</code></pre>

<h4>БЛОК 2 — Деплой ТОЛЬКО при успешных тестах</h4>
<pre><code># .github/workflows/deploy.yml
jobs:
  deploy:
    needs: test   # ❗ job 'test' ДОЛЖЕН быть успешным - иначе деплой не запустится
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh</code></pre>

<h4>БЛОК 3 — локальный тестовый скрипт: ПРАВИЛЬНАЯ передача кода выхода</h4>
<pre><code>#!/bin/bash
# run_tests.sh - правильная версия
set -o pipefail   # ❗ ВАЖНО: сохраняет код ПЕРВОЙ неудачной команды в pipeline

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Код выхода тестового скрипта: $?"   # теперь РЕАЛЬНЫЙ результат pytest</code></pre>

<h3>🐛 Намеренная ошибка — потеря кода выхода в bash pipeline</h3>
<pre><code>#!/bin/bash
# run_tests.sh - НЕПРАВИЛЬНАЯ версия (set -o pipefail ОТСУТСТВУЕТ)

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Тесты выполнены, результат сохранён в test_output.log"
# ❌ Даже без явного 'exit 0', скрипт ВСЁ РАВНО завершится успешно -
# потому что последняя команда - `tee`, а `tee` ПОЧТИ ВСЕГДА
# выполняется успешно (он просто записывает поток в файл).

# В bash pipeline (cmd1 | cmd2), ПО УМОЛЧАНИЮ, код выхода отражает
# ТОЛЬКО ПОСЛЕДНЮЮ команду (tee) - даже если внутри самого pytest
# тесты ПРОВАЛИЛИСЬ, это НИКАК не влияет на итоговый код!

# Результат CI:
# $ ./run_tests.sh; echo $?
# ... (pytest провалил 3 теста, но мы этого не видим) ...
# 0   ❌ "Успешно" - хотя 3 теста сломаны!
#
# GitHub Actions считает этот скрипт "успешным", запускается job
# "deploy" - СЛОМАННЫЙ код выходит в production.</code></pre>

<p><strong>Результат:</strong> когда в bash написан pipeline <code>cmd1 | cmd2</code>, <strong>стандартное</strong> поведение — код выхода всего pipeline равен коду выхода <strong>только последней</strong> команды (здесь <code>tee</code>). А <code>tee</code> почти никогда сам не проваливается — он просто записывает входящий поток в файл и выводит на экран. Поэтому, даже если внутри <strong>самого</strong> <code>pytest</code> тесты провалились (код выхода ≠ 0), весь pipeline <code>pytest | tee ...</code> считается <strong>успешным</strong> (код выхода 0). Система CI принимает решение на основе этого кода выхода — "0 = успех, значит можно деплоить" — и выпускает <strong>сломанный</strong> код в production.</p>

<h3>Теперь объясним</h3>

<h4>1. Что по умолчанию отражает код выхода в bash pipeline?</h4>
<p>Когда написано <code>cmd1 | cmd2</code>, bash по умолчанию возвращает в качестве кода выхода всего pipeline <strong>только</strong> код выхода <strong>последней</strong> команды (<code>cmd2</code>). То, с каким кодом выхода завершилась <code>cmd1</code> (здесь <code>pytest</code>), <strong>игнорируется</strong>.</p>

<h4>2. Почему <code>tee</code> почти всегда завершается "успешно"?</h4>
<p>Задача <code>tee</code> — прочитать входящий текстовый поток, записать его в файл и вывести на экран. Для выполнения этой задачи <code>tee</code> <strong>совершенно неважно</strong>, являются ли входящие данные "успешным" или "проваленным" результатом теста — он просто копирует текст и почти всегда завершается с кодом 0 (успех).</p>

<h4>3. Что делает <code>set -o pipefail</code>?</h4>
<p>Эта настройка bash заставляет брать код выхода pipeline не из <strong>последней</strong> команды, а из кода выхода <strong>первой неудачной</strong> команды внутри pipeline. С этой настройкой, если <code>pytest</code> провалится, весь pipeline <code>pytest | tee ...</code> тоже будет считаться проваленным (с ненулевым кодом выхода) — даже если сам <code>tee</code> выполнился успешно.</p>

<h4>4. Почему эта ошибка особенно опасна?</h4>
<p>Эта ошибка полностью <strong>отменяет</strong> самую основную задачу CI — <strong>защиту</strong> от выхода сломанного кода в production. Ошибки в других capstone-проектах (например неверный SQL, cast без проверки) ломают <strong>часть</strong> кода. Эта же ошибка выводит из строя весь <strong>механизм безопасности</strong> (gate CI) — теперь ЛЮБАЯ другая ошибка (даже все ошибки, изученные на предыдущих 6 уроках, если они ещё не исправлены) может беспрепятственно, "незамеченной" CI, попасть прямо в production.</p>

<h4>5. Как это завершает общую идею всего 7-этапного capstone?</h4>
<p>На уроках 1-6 вы увидели, что сами <strong>метрики</strong> вроде "зелёного теста", "высокого coverage" тоже не гарантируют корректность. Здесь же раскрывается <strong>самая финальная</strong> истина: даже <strong>сам</strong> "успешный" сигнал CI, если в самом скрипте есть тонкая ошибка, может быть <strong>ложным</strong>. Это — финальный урок capstone, показывающий, что разницу между "видеть зелёную галочку" и "быть уверенным в реальной корректности" <strong>никогда нельзя</strong> забывать.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ В bash pipeline (<code>|</code>) код выхода по умолчанию отражает только последнюю команду</li>
<li>✅ Команды вроде <code>tee</code> почти всегда завершаются успешно, независимо от результата предыдущей команды</li>
<li>✅ <code>set -o pipefail</code> используется для сохранения кода первой неудачной команды в pipeline</li>
<li>✅ Такая ошибка полностью отменяет основную задачу CI (остановку сломанного кода)</li>
<li>✅ Даже сигнал CI "успешно" может быть ложным, если в самом скрипте есть ошибка</li>
</ul>

<h3>🎉 Поздравляем!</h3>
<p>Вы построили RankVault с нуля - с документа политики TDD на этапе 1, через Flask API, PostgreSQL, алгоритм рейтинга, test coverage, HashMap-кэш и, наконец, до <strong>правильного, надёжного CI/CD pipeline</strong>. За этот capstone вы объединили знания, полученные отдельно на курсах Python: Testlash и Python: Algoritmlar va Ma'lumotlar Tuzilmasi, в <strong>одном реальном проекте</strong> — и, что самое важное, в отличие от четырёх других capstone-проектов, вы увидели не то, как обманывает TypeScript, а то, как обманывать может <strong>сама система тестирования и метрик</strong>, в семи разных проявлениях: <strong>зелёный тест, высокий coverage и "успешный" CI — ничто из этого, само по себе, не гарантирует реальную корректность.</strong></p>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 7 (ЗАВЕРШЕНИЕ CAPSTONE): Деплой и ошибка кода выхода CI
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) .github/workflows/test.yml - запуск тестов при каждом push
# ─────────────────────────────────────────────────────────────────────

# name: Test
# on: [push]
# jobs:
#   test:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: pip install -r requirements.txt
#       - run: pytest --cov=app --cov-fail-under=80

# ─────────────────────────────────────────────────────────────────────
# 2) .github/workflows/deploy.yml - ТОЛЬКО после прохождения тестов
# ─────────────────────────────────────────────────────────────────────

# jobs:
#   deploy:
#     needs: test
#     runs-on: ubuntu-latest
#     steps:
#       - run: ./deploy.sh

# ─────────────────────────────────────────────────────────────────────
# 3) run_tests.sh - ПРАВИЛЬНАЯ версия
# ─────────────────────────────────────────────────────────────────────

#!/bin/bash
set -o pipefail

pytest --cov=app --cov-fail-under=80 | tee test_output.log
echo "Код выхода тестового скрипта: $?"


# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - скрипт без pipefail (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# #!/bin/bash
# # set -o pipefail ОТСУТСТВУЕТ!
#
# pytest --cov=app --cov-fail-under=80 | tee test_output.log
# echo "Тесты выполнены"
# # Код выхода ВСЕГДА равен коду tee (почти всегда 0) - даже если
# # ВНУТРИ pytest есть проваленные тесты, CI считает это "зелёным"
# # и деплоит СЛОМАННЫЙ код.
"""

EX = {
    4594: {
        "title": "Что по умолчанию отражает код выхода в bash pipeline?",
        "description": "В стандартной настройке bash, чей код выхода возвращает pipeline cmd1 | cmd2 в качестве результата всего pipeline?",
        "hint": "Ошибка в этом уроке возникает именно из-за этого стандартного поведения.",
        "explanation": "По умолчанию bash возвращает в качестве кода выхода всего pipeline только код выхода последней команды (cmd2) - то, как завершилась предыдущая команда в pipeline, игнорируется.",
    },
    4595: {
        "title": "Что делает set -o pipefail?",
        "description": "Как добавление команды set -o pipefail в bash-скрипт изменяет код выхода pipeline?",
        "hint": "Слово 'pipefail' означает 'провал pipeline'.",
        "explanation": "set -o pipefail заставляет брать код выхода pipeline не из последней команды, а из кода выхода первой неудачной команды внутри pipeline.",
    },
    4596: {
        "title": "Расположите, как сломанный код всё же попадает в деплой",
        "description": "Расположите процесс того, как при отсутствии set -o pipefail проваленные тесты всё же приводят к деплою в production.",
        "hint": "",
        "explanation": "",
    },
    4597: {
        "title": "С каким кодом выхода почти всегда завершается команда tee?",
        "description": "С каким кодом выхода ОБЫЧНО завершается сама команда tee (записывающая входящий поток в файл), независимо от результата предыдущей команды? (ответьте цифрой)",
        "hint": "0 означает успех.",
        "expected_answer": "0",
    },
    4598: {
        "title": "Почему эта ошибка серьёзнее других ошибок capstone?",
        "description": (
            "Почему ошибка 'потери кода выхода' в CI считается особенно "
            "серьёзной по сравнению с ошибками из предыдущих уроков "
            "(например flaky-тесты, off-by-one)? Объясните своими "
            "словами."
        ),
        "hint": "Эта ошибка влияет на одну функцию, или на ВСЮ систему защиты?",
        "expected_answer": "Ошибки из предыдущих уроков (flaky-тесты, off-by-one, непроверенный mock) обычно относились к ОПРЕДЕЛЁННОЙ части кода или одной функции. Эта же ошибка CI выводит из строя ВСЮ СИСТЕМУ БЕЗОПАСНОСТИ (gate обязательной проверки тестов перед деплоем) - это означает, что ТЕПЕРЬ любая другая ошибка (даже все ошибки, изученные на предыдущих 6 уроках, если они ещё не исправлены) может беспрепятственно, не будучи 'пойманной' CI, попасть прямо в production. То есть эта ошибка делает бесполезными все остальные меры защиты.",
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
        TASK_TITLE_RU = "RankVault — завершение CAPSTONE: проект с правильным CI/CD-деплоем"
        TASK_DESCRIPTION_RU = (
            "Задеплойте RankVault на реальный хостинг и настройте CI "
            "pipeline (GitHub Actions) — подтвердите, что деплой НИКОГДА "
            "не запускается при ПРОВАЛЕННЫХ тестах. Убедитесь, что во "
            "всех тестовых скриптах код выхода передаётся правильно "
            "(set -o pipefail или эквивалентное решение)."
        )
        TASK_REQUIREMENTS_RU = (
            "• .github/workflows/test.yml — при каждом push запускается pytest --cov=app\n"
            "• .github/workflows/deploy.yml — job deploy зависит от job test через 'needs: test'\n"
            "• Во всех bash-скриптах используется set -o pipefail (или эквивалентное решение) — код выхода pipeline не теряется\n"
            "• Ручная проверка: намеренно сломав один тест, подтвердите, что CI ДЕЙСТВИТЕЛЬНО становится 'красным' и деплой НЕ ЗАПУСКАЕТСЯ\n"
            "• Flask backend работает на реальном хостинге\n"
            "• README.md: живая ссылка, чеклист завершения 7/7 этапов, диаграмма CI/CD\n"
            "• Для отправки требуется ТОЛЬКО GitHub URL репозитория"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, GitHub Actions, Render/Railway"
        if lesson.task_title:
            section_map[lesson.task_title] = TASK_TITLE_RU
        if lesson.task_description:
            section_map[lesson.task_description] = TASK_DESCRIPTION_RU
        for ex in ex_rows:
            for field_name, translated in EX[ex.id].items():
                source = getattr(ex, field_name)
                if source:
                    section_map[source] = translated

        await translate_lesson(
            db, LESSON_ID,
            flat_fields={
                "title": TITLE_RU,
                "text_content": TEXT_RU,
                "task_title": TASK_TITLE_RU,
                "task_description": TASK_DESCRIPTION_RU,
                "task_requirements": TASK_REQUIREMENTS_RU,
                "task_technologies": TASK_TECHNOLOGIES_RU,
            },
            section_translations=section_map,
        )
        await translate_exercises(db, EX)
        await db.commit()
        print(f"Lesson {LESSON_ID}: wrote {len(section_map)} section strings")


if __name__ == "__main__":
    asyncio.run(_run())
