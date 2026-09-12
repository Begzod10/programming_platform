"""Unit tests for team_project_planner.validate_plan/_find_cycle — pure,
deterministic logic, no DB/AI needed. See validate_plan's own docstring
for why these checks exist: the first shipped version of this planner
materialized whatever JSON the AI returned with only a generic
"non-empty tasks list" check, letting dangling/cyclic depends_on,
over-level task assignments, and unmatched consumes/produces through
silently.
"""
from app.services.team_project_planner import validate_plan, _find_cycle


def _members(*levels):
    return [{"student_id": i, "full_name": f"S{i}", "level": lvl, "summary": ""}
            for i, lvl in enumerate(levels)]


def _task(member_idx, required_level="Beginner", produces=None, consumes=None,
          depends_on=None, estimated_hours=4):
    return {
        "assign_to_member_index": member_idx,
        "title": "t", "title_ru": "t",
        "description": "d", "description_ru": "d",
        "required_level": required_level,
        "interface_contract": {"produces": produces or [], "consumes": consumes or []},
        "acceptance_criteria": ["ok"],
        "depends_on": depends_on or [],
        "estimated_hours": estimated_hours,
    }


def test_valid_plan_with_chained_dependency_has_no_errors():
    members = _members("Beginner", "Intermediate")
    plan = {
        "tasks": [
            _task(0, "Beginner", produces=["GET /api/items -> list[Item]"]),
            _task(1, "Intermediate", consumes=["GET /api/items -> list[Item]"], depends_on=[0]),
        ]
    }
    assert validate_plan(plan, members) == []


def test_no_tasks_list_is_rejected():
    assert validate_plan({}, _members("Beginner")) == ["Plan has no 'tasks' list."]
    assert validate_plan({"tasks": []}, _members("Beginner")) == ["Plan has no 'tasks' list."]


def test_task_count_must_equal_member_count():
    members = _members("Beginner", "Intermediate")
    plan = {"tasks": [_task(0)]}
    errors = validate_plan(plan, members)
    assert any("Expected 2 tasks" in e for e in errors)


def test_assign_to_member_index_must_be_a_permutation():
    members = _members("Beginner", "Intermediate")
    # both tasks point at member 0 — member 1 gets nothing, 0 gets two.
    plan = {"tasks": [_task(0), _task(0)]}
    errors = validate_plan(plan, members)
    assert any("assign_to_member_index must use each of 0..1 exactly once" in e for e in errors)


def test_invalid_required_level_string_is_rejected():
    members = _members("Beginner")
    plan = {"tasks": [_task(0, required_level="Expert")]}
    errors = validate_plan(plan, members)
    assert any("invalid required_level" in e for e in errors)


def test_required_level_above_assigned_members_level_is_rejected():
    members = _members("Beginner")
    plan = {"tasks": [_task(0, required_level="Advanced")]}
    errors = validate_plan(plan, members)
    assert any("exceeds member 0's level Beginner" in e for e in errors)


def test_required_level_at_or_below_members_level_is_fine():
    members = _members("Advanced")
    plan = {"tasks": [_task(0, required_level="Beginner")]}
    assert validate_plan(plan, members) == []


def test_non_positive_estimated_hours_is_rejected():
    members = _members("Beginner")
    plan = {"tasks": [_task(0, estimated_hours=0)]}
    errors = validate_plan(plan, members)
    assert any("estimated_hours must be a positive number" in e for e in errors)


def test_consumes_without_a_matching_produces_is_rejected():
    members = _members("Beginner", "Intermediate")
    plan = {
        "tasks": [
            _task(0, produces=["login form"]),
            _task(1, consumes=["something nobody produces"]),
        ]
    }
    errors = validate_plan(plan, members)
    assert any("which no other task produces" in e for e in errors)


def test_consumes_matching_own_produces_does_not_count():
    # a task "consuming" its own produces string isn't a real dependency —
    # others_produce excludes the current task's own produces.
    members = _members("Beginner")
    plan = {"tasks": [_task(0, produces=["x"], consumes=["x"])]}
    errors = validate_plan(plan, members)
    assert any("which no other task produces" in e for e in errors)


def test_depends_on_self_reference_is_rejected():
    members = _members("Beginner")
    plan = {"tasks": [_task(0, depends_on=[0])]}
    errors = validate_plan(plan, members)
    assert any("references itself" in e for e in errors)


def test_depends_on_unknown_index_is_rejected():
    members = _members("Beginner")
    plan = {"tasks": [_task(0, depends_on=[5])]}
    errors = validate_plan(plan, members)
    assert any("references unknown index 5" in e for e in errors)


def test_depends_on_cycle_is_rejected():
    members = _members("Beginner", "Intermediate")
    plan = {
        "tasks": [
            _task(0, depends_on=[1]),
            _task(1, depends_on=[0]),
        ]
    }
    errors = validate_plan(plan, members)
    assert any("depends_on has a cycle" in e for e in errors)


def test_find_cycle_returns_none_for_acyclic_graph():
    assert _find_cycle({0: [1], 1: [2], 2: []}) is None


def test_find_cycle_detects_three_node_cycle():
    cycle = _find_cycle({0: [1], 1: [2], 2: [0]})
    assert cycle is not None
    # the cycle should revisit its own start
    assert cycle[0] == cycle[-1]
