"""The Telegram-bot catalogue: 12 themes, each a blueprint of commands/buttons/FSM flows and files, plus the
aiogram lessons a team must have studied. Same integrability rules as the web blueprints (every file owned
once, every flow produced once), checked here for every bot theme."""
import pytest

from app.services.team_project_blueprints import (
    BlueprintMissing, all_files, backend_family, endpoint_ids, get_blueprint, lesson_needs,
)
from app.services.team_project_constants import BOT_THEMES, WEB_THEMES
from app.services.team_project_skills import need_met, unmet_needs

BOT_KEYS = [t["key"] for t in BOT_THEMES]
METHODS = {"COMMAND", "CALLBACK", "FSM", "JOB"}

# the real lesson titles of "Telegram Bot aiogram" (production, 2026-10-13)
AIOGRAM_LESSONS = [
    "1-BotFather, token va birinchi 'Salom' bot", "2-Message handler'lar (/start, /help, text, regex)",
    "3-Reply keyboard'lar va tugma boshqaruvi", "R1-Echo bot + 3 darajali menyu (takrorlash)",
    "4-Inline keyboard va callback_data", "5-FSM — multi-step formalar", "6-Filter'lar va middleware (auth, rate-limit)",
    "R2-Anketa to'ldiruvchi bot (takrorlash)", "7-SQLAlchemy async bilan database", "8-Fayllar bilan ishlash (rasm, hujjat, voice)",
    "9-Guruh va kanal admin xususiyatlari", "R3-Mini-shop bot (takrorlash)", "10-Webhook va deploy (Railway, env, logging)",
    "11-CAPSTONE: To'liq delivery bot (admin + payment)",
]
EVERYTHING = [("Telegram Bot aiogram", t) for t in AIOGRAM_LESSONS]


def test_the_aiogram_stack_maps_to_the_aiogram_family():
    assert backend_family("aiogram") == "aiogram"
    assert backend_family("vanilla") == "flask" and backend_family("fastapi") == "fastapi"


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_every_bot_theme_has_a_blueprint_with_unique_flow_ids_and_valid_methods(theme):
    bp = get_blueprint(theme, "aiogram")
    assert bp["theme"] == theme and bp["backend_family"] == "aiogram" and bp["kind"] == "bot"
    ids = endpoint_ids(bp)
    assert len(ids) == len(set(ids))
    assert all(e["method"] in METHODS and e["path"] for e in bp["endpoints"])
    pairs = [(e["method"], e["path"]) for e in bp["endpoints"]]
    assert len(pairs) == len(set(pairs)), "two flows share a trigger"
    assert bp["entities"] and all(isinstance(v, dict) for v in bp["entities"].values())


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_every_file_is_listed_once_and_the_skeleton_is_complete(theme):
    bp = get_blueprint(theme, "aiogram")
    files = all_files(bp)
    assert len(files) == len(set(files)), "a file listed twice"
    assert {"README.md", ".env.example", "bot/main.py", "bot/config.py", "bot/requirements.txt"} == set(bp["files"]["skeleton"])
    assert {"bot/core/db.py", "bot/core/models.py", "bot/keyboards.py", "bot/states.py"} <= set(bp["files"]["backend"])
    assert all(f.startswith(("bot/core/", "bot/handlers/", "bot/keyboards", "bot/states")) for f in bp["files"]["backend"])
    assert "python -m bot.main" in bp["run"]["backend"] and ".env" in bp["run"]["backend"]


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_a_team_of_ten_can_be_given_a_file_each_and_there_are_flows_to_split(theme):
    bp = get_blueprint(theme, "aiogram")
    assert len(bp["files"]["backend"]) >= 9
    assert len(bp["endpoints"]) >= 8


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_the_common_flows_exist_and_only_stats_is_admin_only_among_them(theme):
    flows = {e["id"]: e for e in get_blueprint(theme, "aiogram")["endpoints"]}
    assert flows["start.menu"]["path"] == "/start" and flows["help.show"]["path"] == "/help"
    assert flows["admin.stats"]["auth"] is True and not flows["start.menu"]["auth"] and not flows["help.show"]["auth"]


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_bot_blueprints_have_no_web_fields(theme):
    bp = get_blueprint(theme, "aiogram")
    assert bp["base_url"] is None and bp["cors"] is False and bp["files"]["frontend"] == []
    assert "token_key" not in bp["auth"]


def test_web_themes_have_no_aiogram_blueprint_and_bot_themes_no_web_one():
    with pytest.raises(BlueprintMissing):
        get_blueprint(WEB_THEMES[0]["key"], "aiogram")
    with pytest.raises(BlueprintMissing):
        get_blueprint(BOT_KEYS[0], "vanilla")
    with pytest.raises(BlueprintMissing):
        get_blueprint(BOT_KEYS[0], "express")


@pytest.mark.parametrize("theme", BOT_KEYS)
def test_every_bot_need_matches_a_real_aiogram_lesson(theme):
    needs = lesson_needs(theme, "aiogram")
    assert needs["frontend"] == [] and len(needs["backend"]) >= 7
    assert all(n["course"] == "aiogram" for n in needs["backend"])
    for need in needs["backend"]:
        assert need_met(EVERYTHING, need), f"{theme}: no lesson matches {need['label']}"
    assert unmet_needs(needs, [EVERYTHING]) == []


def test_a_student_without_the_aiogram_lessons_has_every_bot_need_unmet_and_userbot_courses_do_not_count():
    needs = lesson_needs("delivery_bot", "aiogram")
    assert len(unmet_needs(needs, [[]])) == len(needs["backend"])
    userbot = [("Telethon: Telegram Userbot va MTProto", "4-Xabar yuborish va o'qish: haqiqiy hisob nomidan ishlash"),
               ("Pyrogram: Zamonaviy Telegram Client Kutubxonasi", "6-Boy xabarlar: inline klaviaturalar, media guruhlari va formatlash")]
    assert len(unmet_needs(needs, [userbot])) == len(needs["backend"])


def test_the_advanced_course_lessons_also_count_for_the_matching_need():
    assert need_met([("Telegram Bot: Ilg'or Mavzular", "5-Redis bilan FSM: gorizontal masshtablash")],
                    next(n for n in lesson_needs("quiz_bot", "aiogram")["backend"] if "FSM" in n["label"]))
