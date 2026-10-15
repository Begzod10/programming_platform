"""Deadlines follow the work: recommended length from the critical path, backend due before frontend."""
from datetime import datetime, timedelta, timezone

import pytest

from app.services.team_project_deadlines import (
    MIN_DAYS, critical_path_hours, recommended_days, stage_deadlines,
)

T0 = datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)


def t(hours, deps=(), files=()):
    return {"estimated_hours": hours, "depends_on": list(deps), "interface_contract": {"files": list(files)}}


def test_critical_path_is_the_longest_dependency_chain_not_the_sum():
    tasks = [t(10), t(4, deps=[0]), t(6, deps=[0]), t(3, deps=[1, 2])]
    assert critical_path_hours(tasks) == 10 + 6 + 3
    assert critical_path_hours([t(5), t(7), t(2)]) == 7                 # independent: the longest single task
    assert critical_path_hours([]) == 0


def test_critical_path_survives_bad_references_and_cycles():
    assert critical_path_hours([t(5, deps=[9]), t(3, deps=[1])]) >= 5   # dangling / self reference must not crash
    assert critical_path_hours([t(2, deps=[1]), t(2, deps=[0])]) >= 2   # cycle must not loop forever


@pytest.mark.parametrize("hours,days", [(0, 7), (1, 7), (14, 9), (16, 10), (40, 19), (200, 21)])
def test_recommended_days_is_hours_over_2_5_plus_3_clamped(hours, days):
    assert recommended_days(hours) == days
    assert MIN_DAYS == 7


def test_backend_pieces_are_due_at_40_percent_and_the_rest_at_75_percent():
    tasks = [t(12, files=["backend/app.py", "README.md"]), t(8, files=["frontend/index.html"]), t(4, files=[])]
    due = stage_deadlines(tasks, T0, days=10)
    assert due[0] == T0 + timedelta(days=4)
    assert due[1] == due[2] == T0 + timedelta(days=7.5)
    assert all(d < T0 + timedelta(days=10) for d in due.values())     # integration (100%) stays after every piece


def test_stage_deadlines_never_fall_before_the_start():
    due = stage_deadlines([t(1, files=["backend/x.py"])], T0, days=1)
    assert due[0] > T0
