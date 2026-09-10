"""Tests for the "matching" exercise type's grading in check_answer_locally.

matching reuses drag_items (left column / terms, fixed display order) and
options (right column / definitions) exactly like drag_and_drop and
multiple_choice reuse the same generic columns for their own shapes:
options[i] is authored as the correct match for drag_items[i], so the
correct answer is always the identity permutation — never stored
separately. The frontend shuffles the right column for display but submits
each pairing as the right item's ORIGINAL (pre-shuffle) index.
"""

import json

from app.models.exercise import Exercise
from app.services.exercise_service import check_answer_locally


def _exercise(left: list, right: list) -> Exercise:
    return Exercise(
        id=1, lesson_id=1, title="t", description="d",
        exercise_type="matching",
        drag_items=json.dumps(left),
        options=json.dumps(right),
    )


def test_identity_mapping_is_correct():
    ex = _exercise(["list", "tuple", "dict"], ["mutable ordered", "immutable ordered", "key-value"])
    result = check_answer_locally(ex, json.dumps([0, 1, 2]))
    assert result["is_correct"] is True
    assert result["partial_score"] == 1.0
    assert result["needs_ai_explanation"] is False


def test_shuffled_but_correctly_reassembled_mapping_is_correct():
    # A student who paired every term with its right definition submits the
    # identity mapping regardless of what ORDER they tapped things in — the
    # submitted array is always indexed by LEFT position, not tap order.
    ex = _exercise(["list", "tuple", "dict"], ["mutable ordered", "immutable ordered", "key-value"])
    result = check_answer_locally(ex, json.dumps([0, 1, 2]))
    assert result["is_correct"] is True


def test_any_swapped_pair_is_wrong():
    ex = _exercise(["list", "tuple", "dict"], ["mutable ordered", "immutable ordered", "key-value"])
    result = check_answer_locally(ex, json.dumps([1, 0, 2]))
    assert result["is_correct"] is False
    assert result["partial_score"] == 0.0
    assert result["needs_ai_explanation"] is True


def test_completely_wrong_mapping_is_wrong():
    ex = _exercise(["list", "tuple", "dict"], ["mutable ordered", "immutable ordered", "key-value"])
    result = check_answer_locally(ex, json.dumps([2, 2, 2]))
    assert result["is_correct"] is False


def test_wrong_length_mapping_is_wrong_not_a_crash():
    ex = _exercise(["list", "tuple", "dict"], ["mutable ordered", "immutable ordered", "key-value"])
    result = check_answer_locally(ex, json.dumps([0, 1]))
    assert result["is_correct"] is False


def test_malformed_json_answer_is_wrong_not_a_crash():
    ex = _exercise(["list", "tuple"], ["a", "b"])
    result = check_answer_locally(ex, "not valid json")
    assert result["is_correct"] is False
    assert result["feedback"] == "Javob formati noto'g'ri"


def test_empty_right_column_never_marks_correct():
    # A misconfigured exercise (no options authored) must never be
    # trivially "solvable" by submitting an empty array.
    ex = _exercise(["list"], [])
    result = check_answer_locally(ex, json.dumps([]))
    assert result["is_correct"] is False


def test_correct_answer_string_pairs_left_and_right_for_ai_context():
    ex = _exercise(["list", "tuple"], ["mutable ordered", "immutable ordered"])
    result = check_answer_locally(ex, json.dumps([1, 0]))
    assert result["correct_answer"] == "list → mutable ordered, tuple → immutable ordered"


def test_no_translation_lookup_needed_since_grading_is_index_based(monkeypatch):
    """Unlike fill_in_blank/drag_and_drop, matching's grading must never
    reach into translation_store — the comparison is purely positional, so
    a RU-language student's submission grades identically to a UZ one."""
    import app.services.translation_store as ts

    def _boom(*a, **kw):
        raise AssertionError("matching grading must not consult translation_store")

    monkeypatch.setattr(ts, "get", _boom)

    ex = _exercise(["list", "tuple"], ["mutable ordered", "immutable ordered"])
    result = check_answer_locally(ex, json.dumps([0, 1]), lang="ru")
    assert result["is_correct"] is True
