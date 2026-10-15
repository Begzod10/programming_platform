"""A teacher archives team projects whose time is over. Production reality that shapes the rule: project #6 has
status `planning` and no `activated_at` although its teams work and its last task deadline passed, so "past" must
come from the teams' and tasks' data, not from the project's own status."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from app.models.team_project import TeamProjectStatus, TeamStatus
from app.services.team_project_archive import is_past

NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)


def project(status="planning", teams=(), activated_at=None, deadline_days=14):
    return NS(status=TeamProjectStatus(status), teams=list(teams), activated_at=activated_at, deadline_days=deadline_days)


def team(status="working", deadlines=()):
    return NS(status=TeamStatus(status), tasks=[NS(deadline_at=d) for d in deadlines])


def test_a_project_with_every_task_deadline_in_the_past_is_past_even_if_its_status_is_planning():
    tp = project("planning", [team("working", [NOW - timedelta(days=3)]), team("reviewed", [NOW - timedelta(days=5)])])
    assert is_past(tp, NOW)


def test_one_task_with_a_future_deadline_keeps_the_project_open():
    tp = project("active", [team("working", [NOW - timedelta(days=3), NOW + timedelta(days=2)])])
    assert not is_past(tp, NOW)


def test_naive_database_datetimes_are_treated_as_utc():
    tp = project("active", [team("working", [datetime(2026, 10, 10, 9, 0)])])
    assert is_past(tp, NOW)


def test_finished_or_cancelled_projects_are_past_without_looking_at_deadlines():
    assert is_past(project("cancelled", []), NOW)
    assert is_past(project("planning", [team("submitted", [NOW + timedelta(days=9)]), team("reviewed")]), NOW)


def test_a_project_still_being_planned_is_not_past():
    assert not is_past(project("planning", [team("forming")]), NOW)               # no tasks, no deadlines
    assert not is_past(project("pending_approval", [team("forming", [])]), NOW)


def test_without_any_task_deadline_a_started_project_ends_when_its_days_run_out():
    started = NOW - timedelta(days=20)
    assert is_past(project("active", [team("working")], activated_at=started, deadline_days=14), NOW)
    assert not is_past(project("active", [team("working")], activated_at=NOW - timedelta(days=3), deadline_days=14), NOW)
    assert not is_past(project("active", [], activated_at=None), NOW)


def test_an_empty_project_is_not_past():
    assert not is_past(project("planning", []), NOW)
