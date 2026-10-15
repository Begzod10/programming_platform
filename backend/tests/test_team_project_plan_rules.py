"""Planning redesign, stage 3: a plan built on a blueprint must be integrable — every file owned once,
every endpoint produced once, tasks only for areas the owner has finished courses in, and a skeleton."""
import copy

from app.services.team_project_blueprints import get_blueprint
from app.services.team_project_planner import (
    augment_plan, skeleton_owner_index, validate_plan,
)

BP = get_blueprint("booking", "vanilla")


def member(i, lead=False, **areas):
    base = {"html_css": "Beginner", "javascript": "Beginner", "python": "Beginner", "flask": "Beginner",
            "node": "Beginner", "react": "Beginner", "sql": "Beginner"}
    base.update(areas)
    return {"student_id": i, "full_name": f"S{i}", "level": "Beginner", "summary": "", "is_lead": lead, "area_levels": base}


MEMBERS = [
    member(0, lead=True, javascript="Advanced", flask="Advanced", python="Advanced"),
    member(1, javascript="Intermediate"),
    member(2, javascript="Intermediate"),
    member(3, html_css="Intermediate"),
]


def task(idx, level, area, files, produces=(), consumes=()):
    return {
        "assign_to_member_index": idx, "title": f"T{idx}", "title_ru": f"Т{idx}",
        "description": "Aniq vazifa tavsifi, shartnomadagi endpointlarga mos.",
        "description_ru": "Подробное описание задачи, соответствующее эндпоинтам контракта.",
        "required_level": level,
        "interface_contract": {"files": list(files), "produces": list(produces), "consumes": list(consumes), "skill_area": area},
        "acceptance_criteria": ["Birinchi aniq mezon", "Ikkinchi aniq mezon"],
        "acceptance_criteria_ru": ["Первый критерий", "Второй критерий"],
        "depends_on": [], "estimated_hours": 6,
    }


def valid_plan():
    ids = [e["id"] for e in BP["endpoints"]]
    f = BP["files"]
    return {"project_title": "p", "project_description": "d", "tasks": [
        task(0, "Advanced", "flask", f["skeleton"] + f["backend"], produces=ids),
        task(1, "Intermediate", "javascript", ["frontend/index.html", "frontend/js/booking_form.js"],
             consumes=["slots.list", "bookings.create"]),
        task(2, "Intermediate", "javascript",
             ["frontend/bookings.html", "frontend/js/bookings_list.js", "frontend/js/auth.js", "frontend/js/api.js"],
             consumes=["bookings.list", "bookings.cancel"]),
        task(3, "Intermediate", "html_css", ["frontend/login.html", "frontend/css/styles.css"]),
    ]}


def errors_of(plan, members=None):
    return validate_plan(plan, members or MEMBERS, require_level_match=True, blueprint=BP)


def test_a_valid_blueprint_plan_has_no_errors():
    assert errors_of(valid_plan()) == []


def test_a_file_in_two_tasks_is_rejected():
    plan = valid_plan()
    plan["tasks"][2]["interface_contract"]["files"].append("frontend/index.html")
    assert any("frontend/index.html" in e and "exactly one task" in e for e in errors_of(plan))


def test_a_file_outside_the_blueprint_is_rejected():
    plan = valid_plan()
    plan["tasks"][1]["interface_contract"]["files"].append("frontend/js/made_up.js")
    assert any("made_up.js" in e and "not in the blueprint" in e for e in errors_of(plan))


def test_a_blueprint_file_nobody_owns_is_rejected():
    plan = valid_plan()
    plan["tasks"][3]["interface_contract"]["files"].remove("frontend/login.html")
    assert any("login.html" in e and "no task" in e for e in errors_of(plan))


def test_consumes_must_be_a_blueprint_endpoint_id():
    plan = valid_plan()
    plan["tasks"][1]["interface_contract"]["consumes"] = ["clients_list"]       # the clients/customers drift
    assert any("clients_list" in e and "blueprint endpoint" in e for e in errors_of(plan))


def test_an_endpoint_produced_by_two_tasks_is_rejected():
    plan = valid_plan()
    plan["tasks"][1]["interface_contract"]["produces"] = ["slots.list"]
    assert any("slots.list" in e and "more than one task" in e for e in errors_of(plan))


def test_every_endpoint_must_be_produced_by_some_task():
    plan = valid_plan()
    plan["tasks"][0]["interface_contract"]["produces"].remove("bookings.cancel")
    assert any("bookings.cancel" in e and "no task produces" in e for e in errors_of(plan))


def test_skill_area_is_required_and_must_be_a_known_area():
    plan = valid_plan()
    del plan["tasks"][1]["interface_contract"]["skill_area"]
    plan["tasks"][2]["interface_contract"]["skill_area"] = "cooking"
    errors = errors_of(plan)
    assert any("Task 1" in e and "skill_area" in e for e in errors)
    assert any("Task 2" in e and "skill_area" in e for e in errors)


def test_a_task_in_an_area_the_owner_has_not_finished_is_rejected():
    """The Amirshox_web case: a React/JS piece for someone who only finished HTML/CSS."""
    plan = valid_plan()
    plan["tasks"][3]["interface_contract"]["skill_area"] = "javascript"
    plan["tasks"][3]["required_level"] = "Beginner"
    assert any("Task 3" in e and "has not finished" in e and "javascript" in e for e in errors_of(plan))


def test_code_files_cannot_hide_behind_a_markup_area():
    plan = valid_plan()
    plan["tasks"][3]["interface_contract"]["files"].append("frontend/js/auth.js")
    plan["tasks"][2]["interface_contract"]["files"].remove("frontend/js/auth.js")
    assert any("Task 3" in e and "code files" in e for e in errors_of(plan))


def test_the_skeleton_must_be_one_task_owned_by_the_skeleton_owner():
    plan = valid_plan()
    plan["tasks"][0]["interface_contract"]["files"].remove("README.md")
    plan["tasks"][1]["interface_contract"]["files"].append("README.md")
    errors = errors_of(plan)
    assert any("skeleton" in e.lower() and "README.md" in e for e in errors)


def test_skeleton_owner_is_the_lead_unless_the_lead_cannot_do_the_backend():
    assert skeleton_owner_index(MEMBERS, BP) == 0
    weak_lead = [member(0, lead=True, javascript="Advanced"), member(1, flask="Advanced", python="Intermediate"),
                 member(2, javascript="Intermediate"), member(3, html_css="Intermediate")]
    assert skeleton_owner_index(weak_lead, BP) == 1


def test_without_a_blueprint_none_of_these_rules_apply():
    plan = valid_plan()
    plan["tasks"][2]["interface_contract"]["files"].append("frontend/index.html")      # duplicate file
    assert validate_plan(plan, MEMBERS, require_level_match=True) == [] or all(
        "exactly one task" not in e for e in validate_plan(plan, MEMBERS, require_level_match=True))


# ── stage 3 / task 7: skeleton + frontend criteria are added deterministically ─────────

def test_augment_adds_skeleton_and_mock_data_criteria_once_and_keeps_languages_aligned():
    plan = valid_plan()
    augment_plan(plan, MEMBERS, BP)
    lead, frontend = plan["tasks"][0], plan["tasks"][1]
    assert any("README" in c for c in lead["acceptance_criteria"])
    assert any("soxta" in c for c in frontend["acceptance_criteria"])
    assert not any("soxta" in c for c in lead["acceptance_criteria"])       # backend task: no mock criterion
    for t in plan["tasks"]:
        assert len(t["acceptance_criteria"]) == len(t["acceptance_criteria_ru"])
    snapshot = copy.deepcopy(plan)
    augment_plan(plan, MEMBERS, BP)
    assert plan == snapshot                                                  # idempotent


def test_fastapi_skeleton_goes_to_a_member_who_finished_the_fastapi_course():
    fastapi_bp = {"backend_family": "fastapi", "files": BP["files"], "endpoints": BP["endpoints"]}
    team = [member(0, lead=True, javascript="Advanced", python="Advanced", flask="Advanced"),
            member(1, javascript="Intermediate", fastapi="Intermediate", python="Intermediate"),
            member(2, javascript="Intermediate"), member(3, html_css="Intermediate")]
    assert skeleton_owner_index(team, fastapi_bp) == 1        # Python/Flask is not FastAPI
    assert skeleton_owner_index(team, BP) == 0                # the Flask blueprint still goes to the lead



def test_the_prompt_tells_the_model_each_member_s_finished_areas_and_that_required_level_follows_the_area():
    from app.services.team_project_blueprints import get_blueprint
    from app.services.team_project_planner import _build_plan_prompt
    from app.services.team_project_constants import TECH_STACKS_BY_KEY
    members = [
        {"student_id": 1, "full_name": "Ali", "level": "Advanced", "summary": "", "is_lead": True,
         "area_levels": {"html_css": "Advanced", "javascript": "Intermediate", "node": "Beginner"}},
        {"student_id": 2, "full_name": "Vali", "level": "Advanced", "summary": "", "is_lead": False,
         "area_levels": {"html_css": "Beginner", "javascript": "Beginner"}},
    ]
    prompt = _build_plan_prompt("Tadbirlar", TECH_STACKS_BY_KEY["express"], members, get_blueprint("quiz", "express"))
    assert "a'zo 0 (Ali): html_css=Advanced, javascript=Intermediate" in prompt
    assert "a'zo 1 (Vali): hech qaysi soha" in prompt
    assert "umumiy darajasi EMAS" in prompt


def test_repair_prompt_lists_unowned_files_and_unproduced_endpoints_and_the_level_rule():
    from app.services.team_project_planner import _build_repair_prompt
    errors = ["Blueprint file 'README.md' is assigned to no task.", "Blueprint file 'frontend/js/api.js' is assigned to no task.",
              "Endpoint 'auth.login' — no task produces it.", "Task 2: required_level Advanced exceeds member 2's level Beginner.",
              "Task 3: area javascript is assigned to X, who has not finished a course in it — give this piece to a member who has."]
    text = _build_repair_prompt("PROMPT", {"tasks": []}, errors)
    assert "README.md, frontend/js/api.js" in text and "auth.login" in text
    assert "darajasiga tenglang" in text and "kursi tugatilmagan" in text


def test_repair_prompt_without_known_error_kinds_has_no_hint_block():
    from app.services.team_project_planner import _build_repair_prompt
    assert "TUZATISH KO'RSATMALARI" not in _build_repair_prompt("P", None, ["Task 0 is not a JSON object"])


def test_a_member_with_no_finished_course_may_take_a_beginner_html_css_piece_but_not_javascript():
    from app.services.team_project_planner import _beginner_markup_task
    nothing = {"area_levels": {"html_css": "Beginner", "javascript": "Beginner"}}
    assert _beginner_markup_task(nothing, "html_css") and not _beginner_markup_task(nothing, "javascript")
    some = {"area_levels": {"html_css": "Advanced", "javascript": "Beginner"}}
    assert not _beginner_markup_task(some, "html_css")


def test_a_criterion_that_is_only_code_may_be_identical_in_both_languages():
    from app.services.team_project_planner import validate_plan
    from tests.test_team_project_assignment import member, with_text
    from app.services.team_project_assignment import assign_blueprint
    from app.services.team_project_blueprints import get_blueprint
    bp = get_blueprint("quiz", "express")
    members = [member(0, node="Advanced", javascript="Advanced", html_css="Advanced"), member(1, html_css="Intermediate")]
    plan = with_text(assign_blueprint(bp, members))
    plan["tasks"][0]["acceptance_criteria"] = ["GET /api/quizzes", "Ro'yxat sahifada ko'rinadi"]
    plan["tasks"][0]["acceptance_criteria_ru"] = ["GET /api/quizzes", "Список виден на странице"]
    assert validate_plan(plan, members, require_level_match=True, blueprint=bp) == []
    plan["tasks"][0]["acceptance_criteria"] = ["Sahifa foydalanuvchiga ro'yxatni ko'rsatadi", "b c"]
    plan["tasks"][0]["acceptance_criteria_ru"] = ["Sahifa foydalanuvchiga ro'yxatni ko'rsatadi", "б в"]
    assert any("identical" in e for e in validate_plan(plan, members, require_level_match=True, blueprint=bp))
