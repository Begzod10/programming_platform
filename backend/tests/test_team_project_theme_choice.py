"""A new team must not get a theme its members already built."""
import random

from app.services.team_project_constants import BOT_THEMES, THEMES, WEB_THEMES, themes_for_kind
from app.services.team_project_service import choose_themes_for_teams

KEYS = [t["key"] for t in WEB_THEMES]


def test_a_theme_none_of_the_members_built_is_preferred():
    past = {1: {"crm"}, 2: {"crm", "booking"}, 3: {"online_shop"}, 4: set()}
    for seed in range(60):
        picks = choose_themes_for_teams([[1, 2], [3, 4]], past, rng=random.Random(seed))
        assert picks[0]["key"] not in {"crm", "booking"}
        assert picks[1]["key"] != "online_shop"


def test_teams_of_one_assignment_get_different_themes_while_the_pool_allows():
    for seed in range(60):
        picks = choose_themes_for_teams([[i] for i in range(len(KEYS))], {}, rng=random.Random(seed))
        assert sorted(p["key"] for p in picks) == sorted(KEYS)


def test_when_every_theme_was_built_the_least_repeated_one_wins():
    past = {1: set(KEYS), 2: set(KEYS) - {"dashboard"}, 3: set(KEYS) - {"dashboard"}}
    # dashboard repeats for 1 member, any other theme for all 3
    assert choose_themes_for_teams([[1, 2, 3]], past, rng=random.Random(0))[0]["key"] == "dashboard"


def test_more_teams_than_themes_still_works():
    picks = choose_themes_for_teams([[i] for i in range(8)], {}, rng=random.Random(1))
    assert len(picks) == 8 and all(p["key"] in KEYS for p in picks)


def test_the_previous_teams_theme_is_only_a_tie_break():
    for seed in range(40):
        picks = choose_themes_for_teams([[1]], {}, rng=random.Random(seed), avoid_key="crm")
        assert picks[0]["key"] != "crm"
    # ...but history still wins over it: member built everything except crm
    past = {1: set(KEYS) - {"crm"}}
    assert choose_themes_for_teams([[1]], past, rng=random.Random(0), avoid_key="crm")[0]["key"] == "crm"


def test_no_members_no_history_is_fine():
    assert len(choose_themes_for_teams([[], []], {}, rng=random.Random(0))) == 2


def test_every_theme_has_a_kind_and_the_catalogue_has_24_web_and_12_bot_themes():
    assert all(t["kind"] in ("web", "bot") for t in THEMES)
    assert len(WEB_THEMES) == 24 and len(BOT_THEMES) == 12
    assert [t["key"] for t in BOT_THEMES] == [
        "delivery_bot", "quiz_bot", "queue_bot", "expense_bot", "flashcards_bot", "events_bot",
        "support_bot", "habits_bot", "library_bot", "survey_bot", "booking_bot", "notes_bot"]
    assert themes_for_kind("bot") == BOT_THEMES and themes_for_kind("web") == WEB_THEMES
    assert len({t["key"] for t in THEMES}) == 36
    assert all(t["label"] and t["label_ru"] for t in BOT_THEMES)


def test_the_default_theme_pool_stays_web_only():
    for seed in range(40):
        assert choose_themes_for_teams([[1, 2]], {}, rng=random.Random(seed))[0]["kind"] == "web"

