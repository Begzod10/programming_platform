"""Unit tests for skill-balanced team formation
(app/services/team_project_service.py::_form_balanced_teams and friends).

Team formation used to be a plain random.shuffle + contiguous chunking —
teams were as likely to end up all-strong or all-struggling as evenly
mixed. Replaced with a snake draft (strongest students distributed one per
team first, direction reversing each round, same shape as a sports-league
draft) so every team's overall skill mix stays close to even. These tests
exercise the pure functions directly (no DB) with lightweight stand-ins for
Student/SkillProfile.
"""
from types import SimpleNamespace

from app.models.user import StudentLevel
from app.schemas.team_project import SkillProfile
from app.services.team_project_service import (
    _team_count, _skill_rank, _form_balanced_teams, _pick_lead,
)


def _student(id_):
    return SimpleNamespace(id=id_, current_level=StudentLevel.Beginner, lifetime_points=0)


def _profile(student_id, level, points):
    return SkillProfile(
        student_id=student_id, full_name=f"S{student_id}",
        current_level=level, lifetime_points=points,
        streak=0, summary="",
    )


# ── _team_count: must match the old contiguous-chunking code's team counts ──

def test_team_count_exact_multiple():
    assert _team_count(4, 2) == 2


def test_team_count_lone_trailing_member_folds_into_previous_team():
    # 5 students / team_size 2 -> old code: [2, 2, 1] -> lone 5th folds
    # into the previous team -> 2 teams (sizes 2 and 3).
    assert _team_count(5, 2) == 2


def test_team_count_remainder_of_two_or_more_stands_as_its_own_team():
    # 6 students / team_size 4 -> old code: [4, 2] -> remainder of 2 is a
    # valid team on its own -> 2 teams.
    assert _team_count(6, 4) == 2


def test_team_count_fewer_students_than_team_size_is_one_team():
    assert _team_count(2, 4) == 1


# ── _skill_rank: profile wins over the bare Student fallback ────────────────

def test_skill_rank_prefers_profile_over_student_fallback():
    student = SimpleNamespace(id=1, current_level=StudentLevel.Beginner, lifetime_points=0)
    profiles = {1: _profile(1, StudentLevel.Advanced, 500)}
    assert _skill_rank(student, profiles) == (2, 500)


def test_skill_rank_falls_back_to_student_when_no_profile():
    student = SimpleNamespace(id=1, current_level=StudentLevel.Intermediate, lifetime_points=50)
    assert _skill_rank(student, {}) == (1, 50)


# ── _form_balanced_teams: the actual balance guarantee ───────────────────────

def test_snake_draft_splits_top_students_across_teams_not_onto_one():
    # 4 students, 2 of them clearly the strongest -- a random shuffle could
    # put both on the same team; the snake draft must not.
    students = [_student(i) for i in range(1, 5)]
    profiles = {
        1: _profile(1, StudentLevel.Advanced, 900),
        2: _profile(2, StudentLevel.Advanced, 800),
        3: _profile(3, StudentLevel.Beginner, 10),
        4: _profile(4, StudentLevel.Beginner, 5),
    }
    teams = _form_balanced_teams(students, team_size=2, profiles_by_id=profiles)

    assert len(teams) == 2
    strongest_ids = {1, 2}
    team_ids = [{s.id for s in team} for team in teams]
    assert not any(strongest_ids.issubset(ids) for ids in team_ids), (
        "the two strongest students both landed on the same team"
    )


def test_snake_draft_keeps_team_sizes_within_one_of_each_other():
    students = [_student(i) for i in range(1, 10)]  # 9 students
    profiles = {
        i: _profile(i, StudentLevel.Beginner, i) for i in range(1, 10)
    }
    teams = _form_balanced_teams(students, team_size=4, profiles_by_id=profiles)
    sizes = sorted(len(t) for t in teams)
    assert max(sizes) - min(sizes) <= 1


def test_snake_draft_places_every_student_exactly_once():
    students = [_student(i) for i in range(1, 12)]
    profiles = {i: _profile(i, StudentLevel.Beginner, i) for i in range(1, 12)}
    teams = _form_balanced_teams(students, team_size=3, profiles_by_id=profiles)
    placed = [s.id for team in teams for s in team]
    assert sorted(placed) == list(range(1, 12))


def test_snake_draft_balances_total_skill_across_teams():
    # 8 students at 8 distinct levels of "strength" (points), team_size 2 ->
    # 4 teams. A snake draft pairs strongest-with-weakest each round, so no
    # team's point total should be wildly ahead of another's.
    students = [_student(i) for i in range(1, 9)]
    profiles = {
        i: _profile(i, StudentLevel.Beginner, points=i * 100) for i in range(1, 9)
    }
    teams = _form_balanced_teams(students, team_size=2, profiles_by_id=profiles)
    totals = [sum(_skill_rank(s, profiles)[1] for s in team) for team in teams]
    assert max(totals) - min(totals) <= 100, totals


def test_form_balanced_teams_and_pick_lead_agree_on_the_strongest_member():
    students = [_student(i) for i in range(1, 5)]
    profiles = {
        1: _profile(1, StudentLevel.Advanced, 900),
        2: _profile(2, StudentLevel.Beginner, 10),
        3: _profile(3, StudentLevel.Advanced, 700),
        4: _profile(4, StudentLevel.Beginner, 5),
    }
    teams = _form_balanced_teams(students, team_size=2, profiles_by_id=profiles)
    for team in teams:
        lead_id = _pick_lead(team, profiles)
        expected_lead = max(team, key=lambda s: _skill_rank(s, profiles)).id
        assert lead_id == expected_lead
