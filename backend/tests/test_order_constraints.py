"""Ordering exercises with more than one valid sequence (stored as order_constraints)."""
import json
from types import SimpleNamespace

from app.services.exercise_service import check_answer_locally

ITEMS = ["Note: user_id FK", "Note: user relationship", "User: notes relationship", "User: cascade", "migration"]
RULES = json.dumps({"order_constraints": [[0, 1], [2, 3], [1, 4], [3, 4]]})


def _ex(rules=RULES):
    return SimpleNamespace(id=1, exercise_type="drag_and_drop", correct_order=json.dumps(ITEMS),
                           drag_items=json.dumps(ITEMS), correct_answers=rules)


def _grade(order, rules=RULES):
    return check_answer_locally(_ex(rules), json.dumps([ITEMS[i] for i in order]))["is_correct"]


def test_the_authored_order_is_still_correct():
    assert _grade([0, 1, 2, 3, 4])


def test_the_two_halves_may_come_in_either_order():
    assert _grade([2, 3, 0, 1, 4])
    assert _grade([0, 2, 1, 3, 4])      # interleaved is fine too


def test_a_broken_dependency_or_a_misplaced_migration_is_still_wrong():
    assert not _grade([1, 0, 2, 3, 4])  # relationship before its foreign key
    assert not _grade([3, 2, 0, 1, 4])  # cascade before the relationship it belongs to
    assert not _grade([0, 1, 2, 4, 3])  # migration before the last step
    assert not _grade([4, 0, 1, 2, 3])


def test_without_rules_only_the_exact_order_passes():
    assert not _grade([2, 3, 0, 1, 4], rules=None)
    assert not _grade([2, 3, 0, 1, 4], rules="not json")
    assert _grade([0, 1, 2, 3, 4], rules=None)


def test_bad_rules_never_crash_or_accept():
    assert not _grade([2, 3, 0, 1, 4], rules=json.dumps({"order_constraints": [[0, 99]]}))
    assert not _grade([2, 3, 0, 1, 4], rules=json.dumps({"order_constraints": "x"}))


def test_a_sequence_with_missing_or_extra_items_is_wrong():
    r = check_answer_locally(_ex(), json.dumps(ITEMS[:4]))
    assert r["is_correct"] is False
