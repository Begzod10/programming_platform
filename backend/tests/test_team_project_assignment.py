"""The deterministic split of a blueprint among members: always a plan validate_plan accepts, or AssignmentImpossible."""
import random

import pytest

from app.services.team_project_assignment import (
    AssignmentImpossible, assign_blueprint, build_text_prompt, merge_texts,
)
from app.services.team_project_blueprints import BLUEPRINTS, get_blueprint
from app.services.team_project_constants import SKILL_AREAS, TECH_STACKS_BY_KEY
from app.services.team_project_planner import validate_plan

LEVELS = ["Beginner", "Intermediate", "Advanced"]
BACKEND_AREAS = {"flask": ["flask", "python"], "express": ["node"], "django": ["django"], "fastapi": ["fastapi"],
                 "aiogram": ["aiogram"]}
PYTHON_AREAS = ("python", "flask", "django", "fastapi", "aiogram")


def member(i, rng=None, **areas):
    levels = {a: "Beginner" for a in SKILL_AREAS}
    levels.update(areas)
    return {"student_id": i, "full_name": f"S{i}", "level": (rng or random).choice(LEVELS), "summary": "",
            "is_lead": i == 0, "area_levels": levels,
            "has_python": any(levels[a] != "Beginner" for a in PYTHON_AREAS)}


def with_text(tasks):
    for t in tasks:
        t.update(title="T", title_ru="Т", description="x" * 200, description_ru="я" * 200,
                 acceptance_criteria=["a", "b"], acceptance_criteria_ru=["а", "б"])
    return {"project_title": "p", "project_description": "d", "tasks": tasks}


@pytest.mark.parametrize("key", sorted(BLUEPRINTS))
def test_the_split_is_always_a_valid_plan_or_impossible(key):
    theme, family = key
    bp = BLUEPRINTS[key]
    rng = random.Random(f"{theme}{family}")
    checked = 0
    for _ in range(40):
        members = [member(i, rng, **{a: rng.choice(LEVELS[1:]) for a in SKILL_AREAS if rng.random() < .35})
                   for i in range(rng.choice([2, 3, 4, 5]))]
        if not any(m["area_levels"][a] != "Beginner" for m in members for a in BACKEND_AREAS[family]):
            continue
        if family != "aiogram" and not any(m["area_levels"]["javascript"] != "Beginner" for m in members):
            continue
        try:
            tasks = assign_blueprint(bp, members)
        except AssignmentImpossible:
            continue
        assert validate_plan(with_text(tasks), members, require_level_match=True, blueprint=bp) == []
        checked += 1
    assert checked > 0


def test_a_member_with_no_finished_course_gets_a_small_beginner_markup_piece():
    bp = get_blueprint("quiz", "express")
    members = [member(0, node="Advanced", javascript="Advanced", html_css="Advanced"),
               member(1, javascript="Intermediate", html_css="Intermediate"), member(2)]
    tasks = assign_blueprint(bp, members)
    weak = tasks[2]
    assert weak["required_level"] == "Beginner" and weak["interface_contract"]["skill_area"] == "html_css"
    assert weak["interface_contract"]["files"] and all(f.endswith((".html", ".css")) for f in weak["interface_contract"]["files"])


def test_every_file_and_endpoint_has_exactly_one_owner_and_skeleton_stays_with_the_owner():
    bp = get_blueprint("online_shop", "vanilla")
    members = [member(0, flask="Advanced", python="Advanced", javascript="Advanced", html_css="Advanced"),
               member(1, javascript="Intermediate", html_css="Intermediate"), member(2, html_css="Beginner")]
    tasks = assign_blueprint(bp, members)
    files = [f for t in tasks for f in t["interface_contract"]["files"]]
    assert sorted(files) == sorted(f for g in bp["files"].values() for f in g)
    produced = [p for t in tasks for p in t["interface_contract"]["produces"]]
    assert sorted(produced) == sorted(e["id"] for e in bp["endpoints"])
    assert set(bp["files"]["skeleton"]) <= set(tasks[0]["interface_contract"]["files"])


def test_a_bot_flow_goes_to_the_owner_of_its_handler_and_handlers_wait_for_the_core():
    bp = get_blueprint("delivery_bot", "aiogram")
    members = [member(i, aiogram="Intermediate", python="Intermediate") for i in range(3)]
    tasks = assign_blueprint(bp, members)
    owner_of = {f: t["assign_to_member_index"] for t in tasks for f in t["interface_contract"]["files"]}
    producer = {p: t["assign_to_member_index"] for t in tasks for p in t["interface_contract"]["produces"]}
    assert producer["cart.add"] == owner_of["bot/handlers/cart.py"]
    core = owner_of["bot/core/db.py"]
    for t in tasks:
        has_handler = any(f.startswith("bot/handlers/") for f in t["interface_contract"]["files"])
        assert (core in t["depends_on"]) == (has_handler and t["assign_to_member_index"] != core)


def test_a_team_nobody_in_which_can_take_a_piece_is_impossible():
    bp = get_blueprint("delivery_bot", "aiogram")
    members = [member(0, aiogram="Advanced", python="Advanced"), member(1, typescript="Advanced")]
    with pytest.raises(AssignmentImpossible):
        assign_blueprint(bp, members)


def test_merge_keeps_the_split_and_takes_only_text_from_the_model():
    bp = get_blueprint("quiz", "express")
    members = [member(0, node="Advanced", javascript="Advanced", html_css="Advanced"), member(1, html_css="Intermediate")]
    skeleton = assign_blueprint(bp, members)
    parsed = {"project_title": "Viktorina", "project_description": "d", "tasks": [
        {"index": 1, "title": "B", "title_ru": "Б", "description": "d" * 30, "description_ru": "д" * 30,
         "acceptance_criteria": ["a", "b"], "acceptance_criteria_ru": ["а", "б"],
         "interface_contract": {"files": ["hijacked.js"]}, "required_level": "Advanced"},
        {"index": 0, "title": "A", "title_ru": "А", "description": "d" * 30, "description_ru": "д" * 30,
         "acceptance_criteria": ["a", "b"], "acceptance_criteria_ru": ["а", "б"]}]}
    plan = merge_texts(skeleton, parsed)
    assert [t["title"] for t in plan["tasks"]] == ["A", "B"]
    assert plan["tasks"][1]["interface_contract"]["files"] == skeleton[1]["interface_contract"]["files"]
    assert plan["tasks"][1]["required_level"] == skeleton[1]["required_level"]
    with pytest.raises(ValueError):
        merge_texts(skeleton, None)


def test_the_text_prompt_names_each_piece_but_hands_no_decisions_to_the_model():
    bp = get_blueprint("quiz", "express")
    members = [member(0, node="Advanced", javascript="Advanced"), member(1, html_css="Beginner")]
    skeleton = assign_blueprint(bp, members)
    prompt = build_text_prompt("Viktorina", TECH_STACKS_BY_KEY["express"], members, bp, skeleton)
    assert "QISMLAR" in prompt and "backend/server.js" in prompt and "TAYYOR va O'ZGARMAYDI" in prompt
    assert "assign_to_member_index" not in prompt


def test_express_server_files_go_only_to_members_who_finished_node_not_to_javascript_only_members():
    bp = get_blueprint("tournament", "express")
    members = [member(0, node="Advanced", javascript="Advanced", html_css="Advanced"),
               member(1, javascript="Advanced", html_css="Advanced"),
               member(2, javascript="Advanced", html_css="Advanced"),
               member(3, html_css="Beginner")]
    tasks = assign_blueprint(bp, members)
    for i in (1, 2, 3):
        files = tasks[i]["interface_contract"]["files"]
        assert files and not any(f.startswith("backend/") for f in files), (i, files)
        assert tasks[i]["interface_contract"]["produces"] == []
    assert tasks[0]["interface_contract"]["produces"]
    assert validate_plan(with_text(tasks), members, require_level_match=True, blueprint=bp) == []
