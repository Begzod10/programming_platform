"""The planner on a Telegram-bot blueprint: its own prompt (flows, no base_url/token/frontend), the same
integrability rules (every file owned once, every flow produced once, tasks only for areas the owner studied)."""
import copy

from app.services.team_project_blueprints import get_blueprint
from app.services.team_project_planner import (
    _BACKEND_AREAS, _CODE_FILE_EXT, _build_plan_prompt, augment_plan, skeleton_owner_index, validate_plan,
)
from app.services.team_project_constants import TECH_STACKS_BY_KEY

BOT = get_blueprint("delivery_bot", "aiogram")
STACK = TECH_STACKS_BY_KEY["aiogram"]


def member(i, lead=False, **areas):
    base = {"html_css": "Beginner", "javascript": "Beginner", "python": "Beginner", "flask": "Beginner", "node": "Beginner",
            "react": "Beginner", "sql": "Beginner", "aiogram": "Beginner", "telegram": "Beginner"}
    base.update(areas)
    return {"student_id": i, "full_name": f"S{i}", "level": "Beginner", "summary": "", "is_lead": lead, "area_levels": base}


# member 0 finished the aiogram course; nobody has finished a JavaScript course
MEMBERS = [member(0, lead=True, aiogram="Advanced", python="Advanced"), member(1, aiogram="Intermediate"),
           member(2, aiogram="Intermediate"), member(3, aiogram="Intermediate")]


def task(idx, area, files, produces=(), consumes=()):
    return {
        "assign_to_member_index": idx, "title": f"T{idx}", "title_ru": f"Т{idx}",
        "description": "Aniq vazifa tavsifi, shartnomadagi oqimlarga mos handler va klaviaturalar.",
        "description_ru": "Подробное описание задачи, соответствующее потокам контракта.",
        "required_level": "Advanced" if idx == 0 else "Intermediate",
        "interface_contract": {"files": list(files), "produces": list(produces), "consumes": list(consumes), "skill_area": area},
        "acceptance_criteria": ["Birinchi aniq mezon", "Ikkinchi aniq mezon"],
        "acceptance_criteria_ru": ["Первый критерий", "Второй критерий"],
        "depends_on": [], "estimated_hours": 6,
    }


def valid_bot_plan(bp=BOT):
    """4 tasks: the skeleton + the base flows, then three handler groups, every flow produced exactly once."""
    flows = [e["id"] for e in bp["endpoints"]]
    core = ["bot/core/db.py", "bot/core/models.py", "bot/keyboards.py", "bot/states.py"]
    handlers = [f for f in bp["files"]["backend"] if f.startswith("bot/handlers/")]
    chunk = [flows[0:3], flows[3:6], flows[6:]]
    return {"project_title": "p", "project_description": "d", "tasks": [
        task(0, "aiogram", bp["files"]["skeleton"] + core + handlers[:1], produces=chunk[0]),
        task(1, "aiogram", handlers[1:2] + handlers[2:3], produces=chunk[1], consumes=[chunk[0][0]]),
        task(2, "aiogram", handlers[3:4], produces=chunk[2][:2]),
        task(3, "aiogram", handlers[4:5], produces=chunk[2][2:]),
    ]}


def errors_of(plan, members=None, bp=BOT):
    return validate_plan(plan, members or MEMBERS, require_level_match=True, blueprint=bp)


def test_the_bot_prompt_lists_flows_and_files_and_has_no_web_lines():
    prompt = _build_plan_prompt("Yetkazib berish boti", STACK, MEMBERS, BOT)
    assert "start.menu" in prompt and "cb:cart:add:<id>" in prompt and "bot/handlers/cart.py" in prompt
    assert "aiogram" in prompt and "ADMIN_IDS" in prompt
    assert "base_url" not in prompt and "localStorage" not in prompt and "frontend/" not in prompt
    assert "html_css, javascript" not in prompt                    # the web skill_area list is not offered to a bot team
    assert "Telegram bot (aiogram)" in prompt                      # the stack label, not "— (frontend) va aiogram (backend)"
    for web_word in ("Login", "login", "navbar", "LoginForm", "Python/Django", "JavaScript o'rganayotgan"):
        assert web_word not in prompt, web_word
    assert "bot/handlers/cart.py" in prompt and '"skill_area": "aiogram"' in prompt   # the bot example task


def test_the_web_prompt_keeps_its_contract_block_and_area_list():
    web = get_blueprint("booking", "vanilla")
    prompt = _build_plan_prompt("Bandlash", TECH_STACKS_BY_KEY["vanilla"], MEMBERS, web)
    assert "base_url:" in prompt and "FAYLLAR:" in prompt and "html_css, javascript, python, flask" in prompt
    assert "ADMIN_IDS" not in prompt


def test_a_valid_bot_plan_has_no_errors():
    assert errors_of(valid_bot_plan()) == []


def test_a_bot_plan_with_an_unknown_flow_or_file_is_rejected():
    plan = valid_bot_plan()
    plan["tasks"][1]["interface_contract"]["consumes"] = ["cart.teleport"]
    assert any("cart.teleport" in e for e in errors_of(plan))
    plan = valid_bot_plan()
    plan["tasks"][2]["interface_contract"]["files"].append("frontend/index.html")
    assert any("frontend/index.html" in e for e in errors_of(plan))


def test_a_flow_nobody_produces_and_a_file_nobody_owns_are_rejected():
    plan = valid_bot_plan()
    plan["tasks"][3]["interface_contract"]["produces"] = []
    plan["tasks"][3]["interface_contract"]["files"] = []
    errors = errors_of(plan)
    assert any("no task produces it" in e for e in errors) and any("assigned to no task" in e for e in errors)


def test_a_python_file_needs_the_aiogram_area_for_a_bot_task():
    assert {"aiogram", "python"} <= _CODE_FILE_EXT[".py"]
    plan = valid_bot_plan()
    plan["tasks"][2]["interface_contract"]["skill_area"] = "javascript"
    assert any("skill_area" in e and "bot/handlers" in e for e in errors_of(plan))


def test_a_task_for_a_member_who_did_not_study_the_area_is_rejected():
    plan = valid_bot_plan()
    members = copy.deepcopy(MEMBERS)
    members[2]["area_levels"]["aiogram"] = "Beginner"
    assert any("has not finished a course" in e for e in errors_of(plan, members))


def test_the_prompt_area_list_contains_aiogram_for_bots_and_the_validator_accepts_it():
    assert _BACKEND_AREAS["aiogram"] == ["aiogram"]
    assert errors_of(valid_bot_plan()) == []


def test_skeleton_goes_to_the_member_who_finished_the_aiogram_course_not_to_a_python_lead():
    team = [member(0, lead=True, python="Advanced", telegram="Advanced"), member(1, aiogram="Intermediate"), member(2), member(3)]
    assert skeleton_owner_index(team, BOT) == 1
    assert skeleton_owner_index(MEMBERS, BOT) == 0                       # the lead has the aiogram course


def test_augment_adds_the_env_and_token_criterion_for_the_skeleton_owner_of_a_bot_only():
    plan = valid_bot_plan()
    augment_plan(plan, MEMBERS, BOT)
    owner = plan["tasks"][0]["acceptance_criteria"]
    assert any(".env.example" in c and "BOT_TOKEN" in c for c in owner)
    assert any("README.md" in c for c in owner)
    assert not any("base_url" in c for t in plan["tasks"] for c in t["acceptance_criteria"])
    assert len(plan["tasks"][0]["acceptance_criteria"]) == len(plan["tasks"][0]["acceptance_criteria_ru"])
    again = copy.deepcopy(plan)
    augment_plan(again, MEMBERS, BOT)
    assert again == plan                                                    # idempotent


def test_a_member_whose_summary_only_names_the_aiogram_course_counts_as_having_python_experience():
    from app.services.team_project_planner import mentions_python
    assert mentions_python("Telegram Bot aiogram (14 darsdan 12 tasi)") and mentions_python("Python: aiogram")
    assert not mentions_python("HTML CSS, JavaScript")


def test_the_python_experience_rule_does_not_reject_a_bot_plan_for_aiogram_members():
    plan = valid_bot_plan()
    members = copy.deepcopy(MEMBERS)
    for m in members:
        m["summary"] = "Telegram Bot aiogram"
        m["has_python"] = True
    assert validate_plan(plan, members, require_level_match=True, blueprint=BOT) == []

