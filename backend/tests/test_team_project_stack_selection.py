"""Stack choice follows what the team has actually finished (not a regex over a summary)."""
import random

import pytest

from app.services.team_project_constants import SKILL_AREAS, TECH_STACKS, TECH_STACKS_BY_KEY
from app.services.team_project_service import NoFittingStack, pick_stacks_for_teams, stack_fits
from app.services.team_project_skills import AreaSkill


def member(**areas):
    """member(javascript="Advanced", flask="Intermediate") -> {area: AreaSkill} (rest Beginner)."""
    return {a: AreaSkill(areas.get(a, "Beginner"), 0.0) for a in SKILL_AREAS}


JS_ONLY = member(javascript="Intermediate")
JS_FLASK = member(javascript="Advanced", flask="Intermediate", python="Intermediate")
JS_NODE = member(javascript="Advanced", node="Advanced")
JS_DJANGO = member(javascript="Advanced", django="Intermediate", python="Intermediate")
HTML_ONLY = member(html_css="Advanced")


def test_the_stacks_are_exactly_the_ones_with_a_blueprint_family():
    assert [s["key"] for s in TECH_STACKS] == ["vanilla", "express", "django"]
    assert all("React" not in s["label"] and "FastAPI" not in s["label"] for s in TECH_STACKS)


def test_flask_stack_needs_javascript_and_a_flask_or_python_member():
    vanilla = TECH_STACKS_BY_KEY["vanilla"]
    assert stack_fits(vanilla, [JS_FLASK, JS_ONLY])
    assert not stack_fits(vanilla, [JS_ONLY, JS_ONLY])          # nobody can do the backend
    assert not stack_fits(vanilla, [HTML_ONLY, HTML_ONLY])      # nobody knows JavaScript
    assert not stack_fits(vanilla, [])


def test_each_backend_stack_needs_its_own_course():
    express, django = TECH_STACKS_BY_KEY["express"], TECH_STACKS_BY_KEY["django"]
    assert stack_fits(express, [JS_NODE, JS_ONLY]) and not stack_fits(express, [JS_FLASK, JS_ONLY])
    assert stack_fits(django, [JS_DJANGO, JS_ONLY]) and not stack_fits(django, [JS_FLASK, JS_NODE])


def test_node_trained_students_are_no_longer_locked_out_of_express():
    """Before: express demanded a React course nobody had, so every team got Flask."""
    assert stack_fits(TECH_STACKS_BY_KEY["express"], [JS_NODE, JS_NODE, JS_ONLY])


def test_half_of_the_team_is_enough_for_the_frontend():
    express = TECH_STACKS_BY_KEY["express"]
    assert stack_fits(express, [JS_NODE, member(html_css="Advanced")])                  # exactly half
    assert not stack_fits(express, [JS_NODE, HTML_ONLY, HTML_ONLY])                    # 1 of 3


def test_points_based_level_is_irrelevant():
    """An 'Advanced' by points who finished only HTML/CSS cannot carry a JS stack."""
    assert not stack_fits(TECH_STACKS_BY_KEY["vanilla"], [HTML_ONLY])


def test_pick_keeps_a_fitting_draw():
    assert pick_stacks_for_teams([[JS_NODE, JS_NODE]], [TECH_STACKS_BY_KEY["express"]])[0]["key"] == "express"


def test_pick_falls_back_to_the_only_fitting_stack():
    django_only = member(javascript="Advanced", django="Intermediate")          # no python area: Flask stack cannot fit
    for seed in range(20):
        picks = pick_stacks_for_teams([[django_only, django_only]], [TECH_STACKS_BY_KEY["express"]], rng=random.Random(seed))
        assert picks[0]["key"] == "django"


def test_a_django_team_with_python_also_fits_the_flask_stack():
    assert stack_fits(TECH_STACKS_BY_KEY["vanilla"], [JS_DJANGO, JS_ONLY])         # Python is Python


def test_a_team_that_fits_several_backends_gets_a_spread_of_them():
    team = [JS_FLASK, JS_NODE, JS_DJANGO, JS_ONLY]
    seen = {pick_stacks_for_teams([team], [TECH_STACKS_BY_KEY["vanilla"]], rng=random.Random(s))[0]["key"] for s in range(5)}
    assert seen == {"vanilla"}                       # a fitting draw is kept...
    from app.services.team_project_service import _cycle_sample
    draws = {_cycle_sample(TECH_STACKS, 1, avoid_key=None)[0]["key"] for _ in range(60)}
    assert draws == {"vanilla", "express", "django"}  # ...and the random draw covers every backend


def test_pick_raises_when_nothing_fits():
    with pytest.raises(NoFittingStack):
        pick_stacks_for_teams([[HTML_ONLY, HTML_ONLY]], [TECH_STACKS_BY_KEY["vanilla"]])


def test_every_stack_declares_requirements():
    assert all(s.get("requires", {}).get("frontend") and s["requires"]["backend"] for s in TECH_STACKS)
