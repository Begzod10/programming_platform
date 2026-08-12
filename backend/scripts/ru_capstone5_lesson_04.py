"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=3 (L4)."""
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

LESSON_ID = 792

TITLE_RU = "4-Алгоритм рейтинга"

TEXT_RU = """\
<h2>Этап 4: Алгоритм рейтинга — "стабильная сортировка" и скрытая ошибка ничьих</h2>

<pre class="mermaid">
flowchart LR
    SCORES["Одинаковый балл: Али=100, Вали=100"] --> QUERY{"Score.query.all() - есть ли ORDER BY?"}
    QUERY -->|"ORDER BY нет"| UNDEFINED["SQL: порядок строк НЕ ОПРЕДЕЛЁН"]
    UNDEFINED --> SORT["Python sorted() - СТАБИЛЬНА, но относительно неопределённого входа"]
    SORT --> INCONSISTENT["Результат: порядок Али/Вали может меняться от запроса к запросу"]
</pre>

<p>В курсе Python: Algoritmlar va Ma'lumotlar Tuzilmasi вы уже изучили нотацию Big O и алгоритмы сортировки (Bubble/Selection/Insertion, Merge/Quick Sort). На этом уроке вы строите сердце RankVault — вычисление рейтинга. Но здесь вы столкнётесь с распространённым заблуждением: факт <strong>"Python-функция <code>sorted()</code> стабильна"</strong>, если применён неправильно, может привести к <strong>ложному спокойствию</strong>.</p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — GET /leaderboard: по убыванию баллов</h4>
<pre><code># app/routes.py
@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.order_by(Score.points.desc(), Score.user_id.asc()).all()
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(scores)
    ])</code></pre>

<h4>БЛОК 2 — Big O: почему это O(n log n)?</h4>
<pre><code># И ORDER BY в PostgreSQL (обычно), и функция sorted() в Python
# (алгоритм Timsort) имеют сложность O(n log n) - это из семейства
# Merge Sort/Quick Sort, изученного на 5-6 уроках.
#
# Для n = 1000 пользователей: ~10 000 сравнений
# Для n = 1 000 000 пользователей: ~20 000 000 сравнений
# (для O(n^2) - Bubble Sort - было бы: 1 000 000 000 000!)</code></pre>

<h4>БЛОК 3 — разрешение ничьей с ЯВНЫМ вторым ключом (tie-break)</h4>
<pre><code># Если два пользователя имеют ОДИНАКОВЫЙ балл (например Али=100, Вали=100),
# нужно ЯВНО указать, на основе чего разрешается порядок:
Score.query.order_by(
    Score.points.desc(),      # 1) основной: по убыванию баллов
    Score.user_id.asc()       # 2) ЯВНЫЙ tie-break: при равенстве баллов - по user_id
).all()
# Теперь результат ВСЕГДА, при КАЖДОМ запросе одинаков - потому что
# порядок ПОЛНОСТЬЮ определён.</code></pre>

<h3>🐛 Намеренная ошибка — запрос без ORDER BY + ложное спокойствие "сортировка Python стабильна"</h3>
<pre><code># Решив "sorted() в Python стабильна, значит проблем нет":
@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.all()   # ❌ НЕТ ORDER BY!
    ranked = sorted(scores, key=lambda s: -s.points)
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(ranked)
    ])

# Логическая ошибка здесь: sorted() в Python ДЕЙСТВИТЕЛЬНО стабильна -
# она сохраняет ОТНОСИТЕЛЬНЫЙ порядок РАВНЫХ элементов. НО "относительно
# чего"? Относительно того порядка, который вернул сам Score.query.all()!
#
# А PostgreSQL без ORDER BY НИКОГДА не гарантирует порядок строк - это
# закреплено в самом стандарте SQL. На практике этот порядок при малой,
# ещё не изменённой таблице часто выглядит как "в порядке записи", но
# это НЕ ГАРАНТИЯ - VACUUM, ANALYZE, использование индексов, или рост
# таблицы, приводящий планировщик запросов к другому решению (например
# parallel workers), могут изменить этот "практический" порядок БЕЗ
# КАКИХ-ЛИБО изменений кода.
#
# Результат: Али и Вали оба имеют 100 баллов. Сегодня /leaderboard
# показывает Али на 1-м месте. Завтра, с теми же самыми данными, он
# может показать Вали на 1-м месте - хотя НИКТО ничего не менял!</code></pre>

<p><strong>Результат:</strong> эта ошибка особенно <strong>коварна</strong>, потому что основана на наполовину <strong>верном</strong> факте — функция <code>sorted()</code> в Python <strong>действительно</strong> стабильна. Проблема в том, что "стабильность" имеет смысл только <strong>относительно порядка входных данных</strong> — если сам вход (здесь: порядок, который <code>Score.query.all()</code> вернул без <code>ORDER BY</code>) <strong>не определён</strong>, то и итоговый результат "стабильной" сортировки, построенной поверх него, остаётся <strong>не определённым</strong>. Это — разница между корректностью на уровне алгоритма (сортировка стабильна) и корректностью на уровне <strong>системы</strong> (весь поток детерминирован).</p>

<h3>Теперь объясним</h3>

<h4>1. Действительно ли <code>sorted()</code> в Python стабильна?</h4>
<p><strong>Да</strong> — <code>sorted()</code> (и <code>list.sort()</code>) в Python используют алгоритм Timsort, который <strong>стабилен</strong>: если два элемента равны по ключу сравнения, они сохраняют своё относительное расположение <strong>во входном списке</strong>. Это факт — проблема не здесь.</p>

<h4>2. Тогда в чём проблема?</h4>
<p>Проблема в том, что <strong>сам входной список</strong> — <code>Score.query.all()</code> без <code>ORDER BY</code> — приходит в <strong>неопределённом</strong> порядке. Согласно стандарту SQL, PostgreSQL без <code>ORDER BY</code> <strong>никогда</strong> не гарантирует порядок строк. "Стабильная сортировка поверх неопределённого входа" — в результате весь поток <strong>всё ещё не определён</strong>.</p>

<h4>3. Почему на практике это часто "выглядит рабочим"?</h4>
<p>На маленькой, ещё не сильно изменённой таблице PostgreSQL <strong>на практике</strong> часто возвращает строки в физически сохранённом (часто в порядке создания) порядке — но это <strong>случайное</strong> поведение, а не гарантия. Такие факторы, как <code>VACUUM</code>, <code>ANALYZE</code>, использование индексов, или рост таблицы, приводящий планировщик запросов к решению использовать параллельные воркеры, могут нарушить этот "практический" порядок <strong>без единого изменения кода</strong>.</p>

<h4>4. Каково правильное решение?</h4>
<p>Добавить <strong>явный</strong> второй (или третий) ключ для разрешения ничьих — например по <code>user_id</code> или <code>submitted_at</code> — тогда порядок будет <strong>полностью определён</strong> даже при равных баллах. Кроме того, использование самого <code>ORDER BY</code> на уровне SQL (без дополнительного вызова <code>sorted()</code> на уровне Python) часто более эффективно и надёжно.</p>

<h4>5. Какое место занимает этот урок в capstone?</h4>
<p>Это — первый тип ошибки в capstone, возникающий на этот раз <strong>не в написании тестов</strong>, а <strong>в самом алгоритме</strong>, причём из-за <strong>неполного понимания</strong> правильно задокументированного свойства (стабильности сортировки Python). Это показывает, что даже мысль "я использую правильный, надёжный инструмент" недостаточна, если вы не понимаете, как вся система (SQL + Python) работает <strong>вместе</strong>.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ Функция <code>sorted()</code> в Python действительно стабильна, но это имеет смысл только относительно порядка входных данных</li>
<li>✅ PostgreSQL без <code>ORDER BY</code> <strong>никогда</strong> не гарантирует порядок строк (стандарт SQL)</li>
<li>✅ "Стабильная сортировка" + "неопределённый вход" = итоговый результат всё равно не определён</li>
<li>✅ Для случаев ничьей нужно добавлять явный второй ключ (tie-break), например <code>user_id</code></li>
<li>✅ Использование правильного инструмента (стабильная сортировка) недостаточно, если не понимать весь поток целиком</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 4: Алгоритм рейтинга
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) GET /leaderboard - с ЯВНЫМ tie-break
# ─────────────────────────────────────────────────────────────────────

@app.route('/leaderboard')
def leaderboard():
    scores = Score.query.order_by(
        Score.points.desc(),      # основной: по убыванию баллов
        Score.user_id.asc()       # ЯВНЫЙ tie-break: при равенстве баллов
    ).all()
    return jsonify([
        {'user_id': s.user_id, 'points': s.points, 'rank': i + 1}
        for i, s in enumerate(scores)
    ])


# ─────────────────────────────────────────────────────────────────────
# 2) tests/test_leaderboard.py - явная проверка случая ничьей
# ─────────────────────────────────────────────────────────────────────

def test_leaderboard_tie_break_is_deterministic(client):
    client.post('/scores', json={'user_id': 5, 'points': 100})
    client.post('/scores', json={'user_id': 2, 'points': 100})

    first_call = client.get('/leaderboard').get_json()
    second_call = client.get('/leaderboard').get_json()

    assert first_call == second_call   # оба вызова ДОЛЖНЫ совпадать
    assert first_call[0]['user_id'] == 2   # меньший user_id первый (tie-break)


# ─────────────────────────────────────────────────────────────────────
# 3) Намеренная ошибка - запрос без ORDER BY (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# @app.route('/leaderboard')
# def leaderboard():
#     scores = Score.query.all()   # НЕТ ORDER BY!
#     ranked = sorted(scores, key=lambda s: -s.points)
#     return jsonify([...])
# Python sorted() стабильна - НО сам порядок входных данных без
# ORDER BY НЕ ОПРЕДЕЛЁН. "Стабильная сортировка поверх неопределённого
# входа" - результат всё равно остаётся не определённым.
"""

EX = {
    4564: {
        "title": "Действительно ли функция sorted() в Python стабильна?",
        "description": "Правда ли, что функция sorted() (и list.sort()) в Python действительно является стабильным алгоритмом сортировки?",
        "hint": "Ошибка в этом уроке не в самом Python.",
        "explanation": "Функция sorted() в Python использует алгоритм Timsort, и он действительно стабилен - но 'стабильность' имеет смысл только относительно относительного порядка входного списка.",
    },
    4565: {
        "title": "Гарантирует ли запрос PostgreSQL без ORDER BY порядок строк?",
        "description": "При вызове Score.query.all() (без добавления ORDER BY), гарантирует ли PostgreSQL, в каком порядке вернутся строки?",
        "hint": "Это правило закреплено в самом стандарте SQL.",
        "explanation": "Согласно стандарту SQL, без ORDER BY PostgreSQL никогда не гарантирует порядок строк - видимый на практике порядок является лишь случайным результатом, а не гарантией.",
    },
    4566: {
        "title": "Расположите процесс возникновения неопределённого результата при ничьей",
        "description": "Расположите процесс того, как запрос без ORDER BY + стабильная сортировка Python приводят к неопределённому результату рейтинга.",
        "hint": "",
        "explanation": "",
    },
    4567: {
        "title": "Сложность Big O запроса рейтинга",
        "description": "Какова сложность Big O сортировки n пользователей по баллам (эффективным алгоритмом вроде Merge Sort/Timsort)? (ответьте в нотации Big O, например: O(x))",
        "hint": "Это сложность Merge Sort/Quick Sort, изученная на 5-6 уроках.",
        "expected_answer": "O(n log n)",
    },
    4568: {
        "title": "Почему мысли 'я использую стабильную сортировку' недостаточно?",
        "description": (
            "Если разработчик считает, что 'я использую стабильную "
            "функцию sorted() в Python, значит мой рейтинг "
            "детерминирован', почему эта мысль может быть неверной? "
            "Объясните своими словами."
        ),
        "hint": "Что именно гарантирует 'стабильность' - порядок входных данных или постоянство порядка выходных данных?",
        "expected_answer": "'Стабильность' сортировки означает лишь сохранение относительного порядка РАВНЫХ элементов в ТОМ порядке, в котором они пришли на вход - это никак не влияет на то, в каком порядке пришёл сам входной список. Если входной список (например, полученный из SQL-запроса без ORDER BY) уже приходит в неопределённом порядке, то независимо от того, насколько 'стабильна' сама сортировка, итоговый результат всё равно остаётся неопределённым - потому что 'стабильность' означает лишь 'равные элементы не перемешиваются', а не 'порядок входных данных всегда одинаков'. Для получения детерминированного результата нужен явный, отдельный ключ разрешения ничьей (например user_id).",
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
        TASK_TITLE_RU = "RankVault — алгоритм рейтинга (с явным tie-break)"
        TASK_DESCRIPTION_RU = (
            "Напишите эндпоинт GET /leaderboard — верните всех "
            "пользователей по убыванию баллов, с ЯВНЫМ ключом разрешения "
            "ничьей (например user_id). Пользователи с одинаковым баллом "
            "всегда должны выводиться в ОДНОМ И ТОМ ЖЕ, предсказуемом "
            "порядке."
        )
        TASK_REQUIREMENTS_RU = (
            "• GET /leaderboard — отсортирован через Score.query.order_by() с ЯВНЫМ вторым (tie-break) ключом\n"
            "• Комбинация Score.query.all() (без ORDER BY) + Python sorted() НЕ ИСПОЛЬЗУЕТСЯ\n"
            "• Тест: /leaderboard вызывается дважды с двумя пользователями одинакового балла, результаты проверяются на совпадение\n"
            "• README.md: объяснена стратегия tie-break, обновлён чеклист статуса"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, PostgreSQL, SQLAlchemy, алгоритмы"
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
