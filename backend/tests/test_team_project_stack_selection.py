"""Stack selection by members' course background: a framework stack is only
given to a team where at least half the members have seen that framework;
vanilla JS fits everyone."""
import random

from app.services.team_project_constants import TECH_STACKS_BY_KEY, TECH_STACKS
from app.services.team_project_service import stack_fits, pick_stacks_for_teams

JS = "Courses: JavaScript Basics. Current technologies: JavaScript, HTML"
REACT = "Courses: React Fundamentals. Current technologies: React, JavaScript"
VUE = "Current technologies: Vue.js"
NEXT = "Current technologies: Next.js"


def test_vanilla_always_fits():
    assert stack_fits(TECH_STACKS_BY_KEY["vanilla"], [JS, JS])
    assert stack_fits(TECH_STACKS_BY_KEY["vanilla"], [])


def test_framework_needs_half_the_team():
    react = TECH_STACKS_BY_KEY["react"]
    assert not stack_fits(react, [JS, JS, JS])
    assert not stack_fits(react, [REACT, JS, JS])        # 1 of 3
    assert stack_fits(react, [REACT, REACT, JS])
    assert stack_fits(react, [REACT, JS])                # exactly half


def test_word_boundaries_and_variants():
    assert stack_fits(TECH_STACKS_BY_KEY["vue"], [VUE])
    assert not stack_fits(TECH_STACKS_BY_KEY["vue"], ["revue reviewing"])
    assert stack_fits(TECH_STACKS_BY_KEY["next"], [NEXT])
    assert stack_fits(TECH_STACKS_BY_KEY["next"], [REACT])   # React background is enough


def test_unfit_draw_is_replaced_by_a_fitting_stack():
    drawn = [TECH_STACKS_BY_KEY["next"]]
    for seed in range(20):
        picks = pick_stacks_for_teams([[JS, JS, JS]], drawn, rng=random.Random(seed))
        assert picks[0]["key"] == "vanilla"


def test_fitting_draw_is_kept():
    drawn = [TECH_STACKS_BY_KEY["react"]]
    assert pick_stacks_for_teams([[REACT, REACT]], drawn)[0]["key"] == "react"


def test_replacement_avoids_repeating_previous_team_stack():
    teams = [[REACT, REACT], [REACT, REACT]]
    drawn = [TECH_STACKS_BY_KEY["react"], TECH_STACKS_BY_KEY["vue"]]  # vue doesn't fit team 2
    for seed in range(30):
        picks = pick_stacks_for_teams(teams, drawn, rng=random.Random(seed))
        assert picks[0]["key"] == "react"
        assert picks[1]["key"] != "react"
        assert picks[1]["key"] in {s["key"] for s in TECH_STACKS}
