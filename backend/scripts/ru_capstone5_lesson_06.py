"""Russian translation for Capstone 5: Testlash va Algoritmlar, lesson order=5 (L6)."""
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

LESSON_ID = 796

TITLE_RU = "6-HashMap-кэш + мокирование"

TEXT_RU = """\
<h2>Этап 6: HashMap-кэш + мокирование — mock, "подделывающий" успех</h2>

<pre class="mermaid">
flowchart LR
    RANK["Пользователь попадает в ТОП-10"] --> NOTIFY["notify_top_10() - вызывает внешний сервис уведомлений"]
    NOTIFY --> MOCK["В тесте: через @patch ВСЕГДА возвращается успех"]
    MOCK --> BLIND["Ошибка/таймаут сервиса НИКОГДА не тестировались"]
    BLIND --> PROD["В production при сбое сервиса - неожиданный крах"]
</pre>

<p>В курсе Python: Algoritmlar va Ma'lumotlar Tuzilmasi вы уже изучили HashMap (Hash Table), а в курсе Python: Testlash — Mock и <code>@patch</code>. На этом уроке вы объедините их: напишете HashMap-кэш со скоростью O(1) для рейтинга и функцию, вызывающую внешний сервис уведомлений, когда пользователь попадает в ТОП-10. Но на этот раз вы познакомитесь с самым опасным неправильным применением Mock: <strong>мокированием только случая успеха.</strong></p>

<h3>🏆 Победа за 5 минут</h3>

<h4>БЛОК 1 — HashMap-кэш: поиск username → rank со скоростью O(1)</h4>
<pre><code># app/cache.py
class RankCache:
    def __init__(self):
        self._cache = {}   # HashMap: username -> rank

    def get(self, username):
        return self._cache.get(username)          # O(1) - знакомо по уроку Hash Table

    def set_all(self, ranked_list):
        self._cache = {
            entry.username: i + 1
            for i, entry in enumerate(ranked_list)
        }   # перестраивается КАЖДЫЙ раз при обновлении рейтинга</code></pre>

<h4>БЛОК 2 — вызов внешнего сервиса уведомлений</h4>
<pre><code># app/notifications.py
import requests

def notify_top_10(username):
    response = requests.post(
        'https://notify.example.com/send',
        json={'username': username, 'message': "Вы попали в ТОП-10!"},
        timeout=5,
    )
    response.raise_for_status()
    return True</code></pre>

<h4>БЛОК 3 — тестирование через @patch И успеха, И ошибки</h4>
<pre><code># tests/test_notifications.py
from unittest.mock import patch
import requests

@patch('app.notifications.requests.post')
def test_notify_top_10_success(mock_post):
    mock_post.return_value.status_code = 200
    assert notify_top_10('ali') is True

@patch('app.notifications.requests.post')
def test_notify_top_10_service_down(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    # Если сервис не отвечает, функция НЕ ДОЛЖНА падать:
    result = notify_top_10_safe('ali')
    assert result is False   # ошибка "поймана", программа продолжает работать</code></pre>

<h3>🐛 Намеренная ошибка — mock возвращает ТОЛЬКО успех</h3>
<pre><code># tests/test_notifications.py - тестируется ТОЛЬКО случай успеха:
@patch('app.notifications.requests.post')
def test_notify_top_10(mock_post):
    mock_post.return_value.status_code = 200   # ❌ ВСЕГДА успех!
    assert notify_top_10('ali') is True

# ОШИБКА или ТАЙМАУТ сервиса НИКОГДА не тестировались!

# app/notifications.py - в реальном коде тоже НЕТ try/except, ловящего ошибку:
def notify_top_10(username):
    response = requests.post(
        'https://notify.example.com/send',
        json={'username': username, 'message': "Вы попали в ТОП-10!"},
        timeout=5,
    )
    response.raise_for_status()   # ❗ Если сервис вернёт 500/timeout - эта СТРОКА выбросит ошибку!
    return True

# app/routes.py - эта функция вызывается СИНХРОННО ВНУТРИ POST /scores:
@app.route('/scores', methods=['POST'])
def create_score():
    score = save_score(request.get_json())
    if is_top_10(score):
        notify_top_10(score.user_id)   # ❌ Если здесь выброшена ошибка...
    return jsonify(score.to_dict()), 201

# Набор тестов 100% "зелёный" - но если сервис уведомлений хотя бы
# ОДИН РАЗ замедлится или перестанет работать, КАЖДЫЙ запрос /scores
# (не только относящийся к ТОП-10!) упадёт с ошибкой 500 - потому что
# необработанная ошибка внутри notify_top_10() "вылетает" наверх и
# ломает весь эндпоинт.</code></pre>

<p><strong>Результат:</strong> mock — это поддельный объект, заменяющий <strong>реальный</strong> внешний сервис, и настроить его так, чтобы он <strong>всегда возвращал успех</strong>, ускоряет тесты, но <strong>никогда</strong> не тестирует, как код ведёт себя, когда сервис <strong>терпит неудачу</strong>. Если в реальном коде для этого случая нет <code>try/except</code>, набор тестов может быть 100% "зелёным", а в production реальный сбой сервиса может сломать весь эндпоинт — это <strong>самый опасный</strong> тип ложной уверенности от mock-тестов: ощущение "я протестировал эту часть", хотя на самом деле протестирован лишь <strong>один, самый благоприятный</strong> сценарий.</p>

<h3>Теперь объясним</h3>

<h4>1. Почему HashMap-кэш работает со скоростью O(1)?</h4>
<p><code>dict</code> в Python (HashMap) использует хеш-функцию для ключа (username), чтобы <strong>напрямую</strong> обращаться к значению (rank), без необходимости перебирать список. Это — <strong>средняя сложность O(1)</strong>, изученная в курсе алгоритмов, в отличие от O(n) линейного поиска.</p>

<h4>2. Для чего используется Mock?</h4>
<p>Mock используется в тестах для <strong>подделки поведения</strong> реального внешнего сервиса (интернета, другого сервера), без реального обращения к нему. Это делает тесты быстрее, стабильнее и независимыми от того, работает ли внешний сервис.</p>

<h4>3. Почему опасно мокировать только случай успеха?</h4>
<p>В реальной жизни внешние сервисы <strong>не всегда</strong> работают — сетевая ошибка, таймаут, ошибка 500 <strong>неизбежны</strong>. Если набор тестов тестирует только сценарий "всё хорошо", <strong>никогда</strong> не проверяется, как код ведёт себя в этих <strong>неизбежных</strong> случаях сбоя - хотя они <strong>обязательно</strong> произойдут в production.</p>

<h4>4. Почему ошибка в одном эндпоинте влияет на ДРУГИЕ, не связанные запросы?</h4>
<p>Если <code>notify_top_10()</code> вызывается <strong>синхронно</strong> внутри <code>POST /scores</code>, без <code>try/except</code>, любая необработанная в ней ошибка <strong>останавливает</strong> обработку всего запроса. В результате не только у пользователя, попавшего в ТОП-10, но и у <strong>любого</strong> пользователя, просто добавляющего балл, запрос упадёт с ошибкой 500 из-за сбоя сервиса.</p>

<h4>5. Каково правильное решение?</h4>
<p>Нужны две вещи: (1) в <strong>тестах</strong> через mock тестировать И успех, И ошибку/таймаут, и (2) в <strong>реальном коде</strong> обернуть вызов внешнего сервиса в <code>try/except</code>, чтобы при ошибке остальная часть программы (сохранение балла) <strong>всё равно</strong> успешно завершалась - даже если уведомление не отправлено, балл должен быть сохранён.</p>

<h3>📌 После этого урока вы знаете</h3>
<ul>
<li>✅ HashMap (Python dict) позволяет обращаться к значению по ключу со скоростью O(1)</li>
<li>✅ Mock используется в тестах для подделки поведения внешнего сервиса</li>
<li>✅ Мокирование только случая успеха никогда не тестирует готовность к сбою сервиса</li>
<li>✅ Синхронный вызов без try/except может "заразить" весь эндпоинт одним сбоем сервиса</li>
<li>✅ Правильный подход: тестировать И успех, И ошибку + ловить ошибку в реальном коде</li>
</ul>
"""

CODE_RU = """\
# ════════════════════════════════════════════════════════════════════
# ЭТАП 6: HashMap-кэш + мокирование
# ════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────
# 1) app/cache.py - O(1) кэш рейтинга через HashMap
# ─────────────────────────────────────────────────────────────────────

class RankCache:
    def __init__(self):
        self._cache = {}

    def get(self, username):
        return self._cache.get(username)

    def set_all(self, ranked_list):
        self._cache = {
            entry.username: i + 1
            for i, entry in enumerate(ranked_list)
        }


# ─────────────────────────────────────────────────────────────────────
# 2) app/notifications.py - версия, ЛОВЯЩАЯ ошибку, безопасная
# ─────────────────────────────────────────────────────────────────────

import requests


def notify_top_10_safe(username):
    try:
        response = requests.post(
            'https://notify.example.com/send',
            json={'username': username, 'message': "Вы попали в ТОП-10!"},
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False   # ошибка поймана - программа продолжает работать


# ─────────────────────────────────────────────────────────────────────
# 3) tests/test_notifications.py - И успех, И ошибка
# ─────────────────────────────────────────────────────────────────────

from unittest.mock import patch


@patch('app.notifications.requests.post')
def test_notify_top_10_success(mock_post):
    mock_post.return_value.status_code = 200
    assert notify_top_10_safe('ali') is True


@patch('app.notifications.requests.post')
def test_notify_top_10_service_down(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    assert notify_top_10_safe('ali') is False


# ─────────────────────────────────────────────────────────────────────
# 4) Намеренная ошибка - замокан только успех, нет try/except (в комментарии)
# ─────────────────────────────────────────────────────────────────────

# def notify_top_10(username):
#     response = requests.post(..., timeout=5)
#     response.raise_for_status()   # БЕЗ try/except!
#     return True
#
# @patch('app.notifications.requests.post')
# def test_notify_top_10(mock_post):
#     mock_post.return_value.status_code = 200   # ТОЛЬКО успех!
#     assert notify_top_10('ali') is True
# Ошибка сервиса НИКОГДА не тестировалась - в production при сбое
# сервиса POST /scores полностью падает с 500.
"""

EX = {
    4584: {
        "title": "Почему HashMap-кэш работает со скоростью O(1)?",
        "description": "Почему self._cache.get(username) в классе RankCache работает со скоростью O(1) (в среднем случае)?",
        "hint": "Это знакомое понятие из урока Hash Table в курсе алгоритмов.",
        "explanation": "dict (HashMap) использует хеш-функцию для ключа, чтобы напрямую обращаться к значению - это не требует последовательного перебора списка, поэтому имеет среднюю сложность O(1).",
    },
    4585: {
        "title": "Почему опасно мокировать только случай успеха?",
        "description": "Почему опасно, если в наборе тестов внешний сервис уведомлений замокан так, что ВСЕГДА возвращает успешный ответ?",
        "hint": "Всегда ли внешние сервисы работают без сбоев?",
        "explanation": "В реальной жизни внешние сервисы неизбежно иногда перестают работать (сетевая ошибка, таймаут, ошибка 500) - если этот случай никогда не тестируется, остаётся неизвестным, как код поведёт себя в такой ситуации.",
    },
    4586: {
        "title": "Расположите, как сбой сервиса ломает весь эндпоинт",
        "description": "Расположите процесс того, как notify_top_10() без try/except ломает весь эндпоинт POST /scores.",
        "hint": "",
        "explanation": "",
    },
    4587: {
        "title": "Способ симуляции ошибки сервиса в mock",
        "description": "Какой атрибут используется в unittest.mock для симуляции того, что объект mock_post при вызове выбрасывает ОШИБКУ (например Timeout)? (например: mock_post.xxx = ...)",
        "hint": "Не return_value, а атрибут, выбрасывающий ошибку как 'побочный эффект'.",
        "expected_answer": "side_effect",
    },
    4588: {
        "title": "Правильное решение состоит из двух частей - почему нужны обе?",
        "description": (
            "Для правильного решения этой проблемы нужно И мокировать "
            "случай ошибки в тестах, И добавить try/except в реальный "
            "код. Почему недостаточно только одного из них (например "
            "только тестирования, без добавления try/except в код)? "
            "Объясните своими словами."
        ),
        "hint": "Что ОБНАРУЖИВАЕТ тестирование в одиночку, но чего НЕ ИСПРАВЛЯЕТ?",
        "expected_answer": "Если случай ошибки тестируется только в тестах, а в реальном коде нет try/except, тест ОБНАРУЖИТ сломанное поведение (например падение программы), но НЕ ИСПРАВИТ его - тест просто будет оставаться проваленным, потому что сам код не ловит ошибку. Если же try/except добавлен только в реальный код, но этот случай никогда не тестируется, в будущем кто-то может случайно убрать try/except или неправильно его изменить, и НИКАКОЙ тест этого не заметит. Поэтому нужны обе части вместе: тест ОБНАРУЖИВАЕТ случай ошибки и ПОСТОЯННО следит за ним в будущем, а код РЕАЛЬНО ловит ошибку.",
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
        TASK_TITLE_RU = "RankVault — HashMap-кэш + мокирование (с обработкой сбоев)"
        TASK_DESCRIPTION_RU = (
            "Напишите класс RankCache (O(1) поиск username->rank через "
            "HashMap) и функцию notify_top_10_safe(). В тестах замокайте "
            "внешний сервис уведомлений через @patch — протестируйте И "
            "успех, И сбой сервиса (Timeout/ошибка)."
        )
        TASK_REQUIREMENTS_RU = (
            "• app/cache.py: RankCache — поиск username->rank со скоростью O(1) через dict\n"
            "• app/notifications.py: notify_top_10_safe() — ловит ошибку через try/except, возвращает False\n"
            "• tests/test_notifications.py: через @patch отдельно протестированы И успех, И ошибка/таймаут\n"
            "• POST /scores — подтверждено, что даже при ошибке вызова notify балл сохраняется и возвращается 201\n"
            "• Обновлён чеклист статуса в README.md"
        )
        TASK_TECHNOLOGIES_RU = "Python, Flask, pytest, unittest.mock, алгоритмы"
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
