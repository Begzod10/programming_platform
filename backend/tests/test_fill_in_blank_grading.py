"""Regression tests for fill_in_blank grading in check_answer_locally.

Covers a real production bug: a student answered ".is-invalid,.invalid-feedback"
for an exercise whose correct_answers is "is-invalid,invalid-feedback" and was
marked wrong. A leading "." is an extremely common, harmless mistake for a
CSS-class-name blank (docs/selectors almost always write classes with the
dot), so it should be tolerated -- but never when the correct answer itself
requires a literal leading dot (filenames, full CSS rules).
"""

from app.models.exercise import Exercise
from app.services.exercise_service import check_answer_locally


def _exercise(correct_answers: str) -> Exercise:
    return Exercise(
        id=1, lesson_id=1, title="t", description="d",
        exercise_type="fill_in_blank", correct_answers=correct_answers,
    )


def test_leading_dot_on_class_name_answers_is_tolerated():
    ex = _exercise("is-invalid,invalid-feedback")
    result = check_answer_locally(ex, ".is-invalid,.invalid-feedback")
    assert result["is_correct"] is True


def test_exact_match_without_dot_still_correct():
    ex = _exercise("is-invalid,invalid-feedback")
    result = check_answer_locally(ex, "is-invalid,invalid-feedback")
    assert result["is_correct"] is True


def test_genuinely_wrong_answer_with_dot_still_marked_wrong():
    ex = _exercise("is-invalid,invalid-feedback")
    result = check_answer_locally(ex, ".is-valid,.ivalid")
    assert result["is_correct"] is False


def test_dotfile_answer_still_requires_the_dot():
    ex = _exercise(".env")
    assert check_answer_locally(ex, ".env")["is_correct"] is True
    assert check_answer_locally(ex, "env")["is_correct"] is False


def test_css_rule_answer_with_leading_dot_selector_still_requires_it():
    ex = _exercise(".plan-feature--yes::before { content: '✓' }")
    full = ".plan-feature--yes::before { content: '✓' }"
    assert check_answer_locally(ex, full)["is_correct"] is True
