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
JS_FLASK = member(javascript="Advanced", flask="Intermediate")
REACT_NODE = member(javascript="Advanced", react="Intermediate", node="Advanced")
HTML_ONLY = member(html_css="Advanced")


def test_vanilla_needs_javascript_and_a_backend_member():
    vanilla = TECH_STACKS_BY_KEY["vanilla"]
    assert stack_fits(vanilla, [JS_FLASK, JS_ONLY])
    assert not stack_fits(vanilla, [JS_ONLY, JS_ONLY])          # nobody can do the Flask side
    assert not stack_fits(vanilla, [HTML_ONLY, HTML_ONLY])      # nobody knows JavaScript
    assert not stack_fits(vanilla, [])


def test_react_stack_rejected_when_nobody_has_react():
    """Team 3 of project #6: Node/Express + React, nobody had finished a React course."""
    express = TECH_STACKS_BY_KEY["express"]
    assert not stack_fits(express, [member(javascript="Advanced", node="Advanced"), JS_ONLY, JS_ONLY])
    assert stack_fits(express, [REACT_NODE, REACT_NODE])


def test_half_of_the_team_is_enough_for_the_frontend():
    express = TECH_STACKS_BY_KEY["express"]
    assert stack_fits(express, [REACT_NODE, JS_ONLY])                         # exactly half
    assert not stack_fits(express, [REACT_NODE, JS_ONLY, JS_ONLY])            # 1 of 3


def test_unknown_area_stack_never_fits():
    everyone = [REACT_NODE, JS_FLASK]
    assert not stack_fits(TECH_STACKS_BY_KEY["vue"], everyone)                # no Vue course exists


def test_points_based_level_is_irrelevant():
    """An 'Advanced' by points who finished only HTML/CSS cannot carry a JS stack."""
    assert not stack_fits(TECH_STACKS_BY_KEY["vanilla"], [HTML_ONLY])


def test_pick_keeps_a_fitting_draw():
    drawn = [TECH_STACKS_BY_KEY["express"]]
    assert pick_stacks_for_teams([[REACT_NODE, REACT_NODE]], drawn)[0]["key"] == "express"


def test_pick_falls_back_to_a_fitting_stack():
    drawn = [TECH_STACKS_BY_KEY["express"]]
    for seed in range(20):
        picks = pick_stacks_for_teams([[JS_FLASK, JS_FLASK]], drawn, rng=random.Random(seed))
        assert picks[0]["key"] == "vanilla"                    # the only stack this team fits


def test_pick_raises_when_nothing_fits():
    with pytest.raises(NoFittingStack):
        pick_stacks_for_teams([[HTML_ONLY, HTML_ONLY]], [TECH_STACKS_BY_KEY["vanilla"]])


def test_every_stack_declares_requirements():
    assert all(s.get("requires", {}).get("frontend") and s["requires"]["backend"] for s in TECH_STACKS)
