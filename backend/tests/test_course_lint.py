"""Spec lint: a course spec is rejected BEFORE it touches the database if its UZ/RU content is incomplete."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from course_builder.lint import LintResult, lint_spec  # noqa: E402

PROSE_UZ = ("Token foydalanuvchini har so'rovda qayta login qilmasdan tanitadi. Server uni imzolaydi, mijoz esa har bir "
            "so'rovga Authorization sarlavhasi bilan qo'shib yuboradi. " * 3)
PROSE_RU = ("Токен позволяет узнавать пользователя без повторного входа при каждом запросе. Сервер подписывает его, а клиент "
            "добавляет в каждый запрос в заголовке Authorization. " * 3)


def mc(i):
    return {"title": f"Savol {i}", "title_ru": f"Вопрос {i}", "description": "Token nima uchun kerak?",
            "description_ru": "Для чего нужен токен?", "exercise_type": "multiple_choice",
            "options": ["Foydalanuvchini tanish", "Rasm saqlash", "CSS yozish", "Hech narsa"],
            "options_ru": ["Идентификация пользователя", "Хранение картинок", "Написание CSS", "Ничего"],
            "correct_answers": "A", "hint": "Login haqida o'ylang.", "hint_ru": "Подумайте о входе.",
            "explanation": "Token foydalanuvchini keyingi so'rovlarda tanishga xizmat qiladi.", "difficulty_level": "Easy", "points": 3}


def dnd():
    return {"title": "Tartib", "title_ru": "Порядок", "description": "Qadamlarni joylang", "description_ru": "Расставьте шаги",
            "exercise_type": "drag_and_drop", "drag_items": ["Login", "Token olish", "So'rov yuborish"],
            "drag_items_ru": ["Вход", "Получение токена", "Отправка запроса"],
            "correct_order": ["Login", "Token olish", "So'rov yuborish"], "hint": "Avval kirish.", "hint_ru": "Сначала вход.",
            "explanation": "Avval login, keyin token.", "difficulty_level": "Easy", "points": 3}


def fib():
    return {"title": "Bo'sh joy", "title_ru": "Пропуск", "description": "Sarlavha nomi: ___ Bearer", "description_ru": "Название заголовка: ___ Bearer",
            "exercise_type": "fill_in_blank", "correct_answers": "Authorization", "hint": "Sarlavha nomi.", "hint_ru": "Имя заголовка.",
            "explanation": "Token Authorization sarlavhasida yuboriladi.", "difficulty_level": "Easy", "points": 3}


def txt():
    return {"title": "Izoh", "title_ru": "Пояснение", "description": "Token nima ekanini o'z so'zingiz bilan yozing.",
            "description_ru": "Объясните своими словами, что такое токен.", "exercise_type": "text_input",
            "expected_answer": "Foydalanuvchini tanitadigan imzolangan satr", "hint": "Qisqa yozing.", "hint_ru": "Пишите кратко.",
            "explanation": "Token — imzolangan identifikator.", "difficulty_level": "Medium", "points": 4}


def lesson(order=0, **over):
    base = {
        "order": order, "title": f"{order + 1}-Token nima", "title_ru": f"{order + 1}-Что такое токен",
        "text_content": f"<h3>Token</h3><p>{PROSE_UZ}</p><pre><code>token = create_token(user)\nprint(token)</code></pre>",
        "text_content_ru": f"<h3>Токен</h3><p>{PROSE_RU}</p><pre><code>token = create_token(user)\nprint(token)</code></pre>",
        "exercises": [mc(1), mc(2), dnd(), fib(), txt()],
    }
    base.update(over)
    return base


def course():
    return {"title": "Flask: Token", "title_ru": "Flask: токены", "description": "API autentifikatsiya haqida qisqa kurs.",
            "description_ru": "Короткий курс об аутентификации API.", "instructor_id": 2, "difficulty_level": "Intermediate",
            "duration_weeks": 1, "max_points": 30}


def lint(lessons=None, c=None):
    return lint_spec(c or course(), lessons if lessons is not None else [lesson()])


def errs(result: LintResult) -> str:
    return " | ".join(result.errors)


def test_a_complete_bilingual_spec_passes():
    r = lint()
    assert r.ok and r.errors == []


@pytest.mark.parametrize("path", ["title_ru", "text_content_ru"])
def test_missing_ru_counterpart_of_a_lesson_field_is_an_error(path):
    les = lesson()
    del les[path]
    assert any(path in e for e in lint([les]).errors)


def test_missing_ru_on_exercise_fields_and_course_is_an_error():
    les = lesson()
    for key in ("description_ru", "options_ru", "hint_ru"):
        les["exercises"][0].pop(key)
    r = lint([les])
    for key in ("description_ru", "options_ru", "hint_ru"):
        assert any(key in e for e in r.errors), key
    c = course()
    c.pop("title_ru")
    assert any("title_ru" in e for e in lint(c=c).errors)


def test_ru_equal_to_uz_or_without_cyrillic_is_an_error():
    les = lesson()
    les["text_content_ru"] = les["text_content"]
    les["exercises"][0]["description_ru"] = "Token nima uchun kerak?"
    r = lint([les])
    assert any("text_content_ru" in e and "identical" in e for e in r.errors)
    assert any("description_ru" in e and ("identical" in e or "Cyrillic" in e) for e in r.errors)


def test_a_short_code_like_answer_needs_no_translation_marker():
    les = lesson()
    les["exercises"][3]["hint"] = "print"          # a code token: identical in RU is fine
    les["exercises"][3]["hint_ru"] = "print"
    assert lint([les]).ok


def test_exercise_without_hint_or_explanation_is_an_error():
    les = lesson()
    les["exercises"][1]["hint"] = ""
    del les["exercises"][2]["explanation"]
    r = lint([les])
    assert any("hint" in e for e in r.errors) and any("explanation" in e for e in r.errors)


def test_multiple_choice_shape():
    les = lesson()
    les["exercises"][0]["correct_answers"] = "E"                      # only A-D exist
    les["exercises"][1]["options_ru"] = ["bir", "ikki"]               # length differs from options
    r = lint([les])
    assert any("correct_answers" in e for e in r.errors)
    assert any("options_ru" in e and "length" in e for e in r.errors)


def test_drag_and_drop_order_must_be_a_permutation():
    les = lesson()
    les["exercises"][2]["correct_order"] = ["Login", "Token olish"]
    assert any("correct_order" in e for e in lint([les]).errors)


def test_fill_in_blank_needs_exactly_one_blank_and_an_answer():
    les = lesson()
    les["exercises"][3]["description"] = "Sarlavha nomi bo'sh joysiz"
    les["exercises"][3]["correct_answers"] = ""
    r = lint([les])
    assert any("blank" in e for e in r.errors) and any("correct_answers" in e for e in r.errors)


def test_text_input_needs_expected_answer():
    les = lesson()
    les["exercises"][4]["expected_answer"] = ""
    assert any("expected_answer" in e for e in lint([les]).errors)


def test_lesson_needs_five_exercises_of_three_types_unless_it_is_a_task_lesson():
    les = lesson(exercises=[mc(1), mc(2), mc(3), mc(4), mc(5)])       # five, but one type
    assert any("types" in e for e in lint([les]).errors)
    les = lesson(exercises=[mc(1), dnd()])
    assert any("5 exercises" in e for e in lint([les]).errors)
    task = {"task_title": "Mini-API", "task_title_ru": "Мини-API", "task_description": "Token bilan himoyalangan API yozing.",
            "task_description_ru": "Напишите API, защищённый токеном.", "task_requirements": "Token ishlatilsin.",
            "task_requirements_ru": "Используйте токен.", "task_technologies": "Python, Flask", "task_deadline_days": 3}
    assert lint([lesson(exercises=[], task=task)]).ok


def test_task_lesson_needs_complete_task_fields():
    task = {"task_title": "Mini-API", "task_description": "Token bilan himoyalangan API yozing.", "task_requirements": "Token ishlatilsin."}
    r = lint([lesson(exercises=[], task=task)])
    for key in ("task_title_ru", "task_description_ru", "task_requirements_ru", "task_technologies", "task_deadline_days"):
        assert any(key in e for e in r.errors), key


def test_code_blocks_must_match_between_languages_as_a_warning():
    les = lesson()
    les["text_content_ru"] = les["text_content_ru"].replace("create_token(user)", "make_token(user)")
    r = lint([les])
    assert r.ok and any("code" in w.lower() for w in r.warnings)       # a warning, not an error
    les = lesson()
    les["text_content_ru"] = les["text_content_ru"].replace("print(token)", "print(token)  # chop etish")
    assert lint([les]).warnings == []                                   # comments may differ


def test_requirement_tokens_absent_from_the_taught_text_are_a_warning():
    task = {"task_title": "Mini-API", "task_title_ru": "Мини-API", "task_description": "Token bilan himoyalangan API yozing.",
            "task_description_ru": "Напишите API, защищённый токеном.",
            "task_requirements": "Natijani keshlash uchun Redis ishlating va Docker da ishga tushiring.",
            "task_requirements_ru": "Используйте кэш Redis и запустите в Docker.", "task_technologies": "Python", "task_deadline_days": 3}
    r = lint([lesson(0), lesson(1, exercises=[], task=task)])
    assert r.ok and any("Redis" in w or "redis" in w.lower() for w in r.warnings)


def test_missing_keys_give_a_clear_message_not_a_crash():
    r = lint_spec({}, [{}])
    assert not r.ok and any("title" in e for e in r.errors)
    assert not lint_spec(course(), []).ok
    assert any("exercises" in e or "5 exercises" in e for e in lint([{"order": 0, "title": "x", "title_ru": "х"}]).errors)


def test_plain_uzbek_words_in_requirements_are_not_flagged():
    """Uzbek is Latin script: only technology-looking tokens may be compared with the taught text."""
    task = {"task_title": "Mini-API", "task_title_ru": "Мини-API", "task_description": "Token bilan himoyalangan API yozing.",
            "task_description_ru": "Напишите API, защищённый токеном.",
            "task_requirements": "Foydalanuvchi ro'yxatdan o'tadi, keyin tizimga kiradi va himoyalangan sahifani ko'radi. Token ishlatilsin.",
            "task_requirements_ru": "Пользователь регистрируется, затем входит и видит защищённую страницу. Используйте токен.",
            "task_technologies": "Python", "task_deadline_days": 3}
    assert lint([lesson(0), lesson(1, exercises=[], task=task)]).warnings == []


def test_backticked_and_product_names_are_compared():
    task = {"task_title": "Mini-API", "task_title_ru": "Мини-API", "task_description": "Token bilan himoyalangan API yozing.",
            "task_description_ru": "Напишите API, защищённый токеном.",
            "task_requirements": "`create_token` ishlatilsin va `flask_cors` ulansin.",
            "task_requirements_ru": "Используйте `create_token` и подключите `flask_cors`.", "task_technologies": "Python", "task_deadline_days": 3}
    r = lint([lesson(0), lesson(1, exercises=[], task=task)])
    assert any("flask_cors" in w for w in r.warnings) and not any("create_token" in w for w in r.warnings)


# ── glossary ────────────────────────────────────────────────────────────────

from course_builder.glossary import RU_GLOSSARY, forbidden_ru_terms  # noqa: E402


def test_glossary_flags_a_forbidden_ru_variant_and_names_the_preferred_one():
    found = forbidden_ru_terms("Каждый конечная точка API возвращает JSON, а бекенд проверяет токен.")
    pairs = {(bad, good) for bad, good in found}
    assert ("конечная точка", "эндпоинт") in pairs and ("бекенд", "бэкенд") in pairs


def test_glossary_accepts_the_preferred_terms():
    assert forbidden_ru_terms("Эндпоинт возвращает ответ, бэкенд проверяет токен, фронтенд показывает результат.") == []


def test_glossary_covers_the_core_terms():
    assert {"endpoint", "token", "middleware", "deploy", "frontend", "backend", "request", "response", "route", "database",
            "framework", "library", "commit", "branch", "repository", "bug", "API"} <= set(RU_GLOSSARY)


def test_lint_reports_glossary_violations_as_errors():
    les = lesson()
    les["text_content_ru"] = les["text_content_ru"].replace("Сервер", "Бекенд")
    r = lint([les])
    assert any("бекенд" in e.lower() and "бэкенд" in e for e in r.errors)


def test_glossary_is_not_applied_to_code_blocks():
    les = lesson()
    les["text_content_ru"] = les["text_content_ru"].replace("print(token)", "print(бекенд)")
    assert not any("бекенд" in e.lower() for e in lint([les]).errors)


def test_the_example_spec_passes_lint_with_no_errors():
    """The documented example must itself obey the rules it documents."""
    from course_builder.spec_loader import load_spec
    module = load_spec(str(Path(__file__).resolve().parents[1] / "scripts" / "course_specs" / "_example.py"))
    result = lint_spec(module.COURSE, module.LESSONS)
    assert result.errors == [], result.errors
