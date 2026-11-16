"""Active kids' games (collect, connect, catch, dragsort): backend knows them."""
import json

import pytest
from sqlalchemy import update

from app.models.early_learning import EarlyActivity
from app.services.early_levels import levels_for
from app.services.early_sections import section_for_modes
from tests._early_helpers import make_module, make_student, make_teacher

BASE = "/api/v1/early-learning"
NEW_MODES = ("collect", "connect", "catch", "dragsort")


@pytest.fixture(autouse=True)
def _games_unlocked():
    from app.main import app
    from app.dependencies import require_games_unlocked
    app.dependency_overrides[require_games_unlocked] = lambda: None
    yield
    app.dependency_overrides.pop(require_games_unlocked, None)


def _item(label, ru, emoji):
    return {"label": label, "label_ru": ru, "emoji": emoji}


CONTENT = {
    "mode": "dragsort",
    "character": {"label": "Oshpaz", "label_ru": "Повар", "emoji": "👨‍🍳"},
    "correct_items": [_item("Qozon", "Казан", "🍲")],
    "distractor_items": [_item("Bolg'a", "Молоток", "🔨")],
    "partner": {
        "character": {"label": "Shifokor", "label_ru": "Врач", "emoji": "👩‍⚕️"},
        "correct_items": [_item("Shprits", "Шприц", "💉")],
    },
    "partner2": {
        "character": {"label": "Uchuvchi", "label_ru": "Лётчик", "emoji": "👨‍✈️"},
        "correct_items": [_item("Samolyot", "Самолёт", "✈️")],
    },
}


def test_new_modes_have_three_levels_and_world_section():
    for mode in NEW_MODES:
        assert levels_for(mode) == 3, mode
        assert section_for_modes([mode] * 3) == "world", mode


async def _module_with(db_session, async_client, mode):
    teacher_id = await make_teacher(async_client, db_session)
    module, (activity,) = await make_module(db_session, teacher_id, n_activities=1, modes=[mode])
    await db_session.execute(
        update(EarlyActivity).where(EarlyActivity.id == activity.id)
        .values(content_json=json.dumps({**CONTENT, "mode": mode}))
    )
    await db_session.commit()
    return module


@pytest.mark.asyncio
async def test_ru_localizes_new_modes_and_partner(async_client, db_session):
    for mode in NEW_MODES:
        module = await _module_with(db_session, async_client, mode)
        _, headers = await make_student(async_client, db_session)
        res = await async_client.get(f"{BASE}/modules/{module.id}?lang=ru", headers=headers)
        assert res.status_code == 200, res.text
        content = res.json()["activities"][0]["content"]
        assert content["character"]["label"] == "Повар", mode
        assert content["correct_items"][0]["label"] == "Казан"
        assert content["distractor_items"][0]["label"] == "Молоток"
        assert content["partner"]["character"]["label"] == "Врач"
        assert content["partner"]["correct_items"][0]["label"] == "Шприц"
        assert content["partner2"]["character"]["label"] == "Лётчик"
        assert content["partner2"]["correct_items"][0]["label"] == "Самолёт"


@pytest.mark.asyncio
async def test_uz_leaves_content_unchanged(async_client, db_session):
    module = await _module_with(db_session, async_client, "dragsort")
    _, headers = await make_student(async_client, db_session)
    res = await async_client.get(f"{BASE}/modules/{module.id}?lang=uz", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["activities"][0]["content"] == CONTENT
