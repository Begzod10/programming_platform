"""Module sections (derived from activity modes) and per-student progress
fields on the module list."""
import pytest
import pytest_asyncio
from sqlalchemy import update

from app.models.early_learning import EarlyActivity
from app.services.early_sections import section_for_modes
from tests._early_helpers import make_module, make_student, make_teacher

BASE = "/api/v1/early-learning"


@pytest.fixture(autouse=True)
def _games_unlocked():
    from app.main import app
    from app.dependencies import require_games_unlocked
    app.dependency_overrides[require_games_unlocked] = lambda: None
    yield
    app.dependency_overrides.pop(require_games_unlocked, None)


def test_each_section():
    assert section_for_modes(["select", "sort"]) == "world"
    assert section_for_modes(["cause_effect", "sequence", "pairs"]) == "world"
    assert section_for_modes(["count", "maze", "rounds"]) == "logic"
    assert section_for_modes(["arithmetic", "compare", "pattern", "simon", "sudoku", "merge", "chart", "bubbles"]) == "logic"
    assert section_for_modes(["trace", "build"]) == "make"
    assert section_for_modes(["puzzle"]) == "make"
    assert section_for_modes(["typing", "keyboard"]) == "letters"
    assert section_for_modes(["wordbuild", "hangman"]) == "letters"


def test_majority_wins():
    assert section_for_modes(["select", "count", "count"]) == "logic"


def test_tie_priority():
    assert section_for_modes(["chart", "chart", "wordbuild", "wordbuild"]) == "letters"
    assert section_for_modes(["trace", "count"]) == "make"
    assert section_for_modes(["count", "select"]) == "logic"


def test_unknown_missing_and_empty():
    assert section_for_modes([None, "no_such_mode"]) == "world"
    assert section_for_modes([]) == "world"


@pytest_asyncio.fixture
async def teacher(async_client, db_session):
    return await make_teacher(async_client, db_session)


async def _item(async_client, headers, module_id, path="modules"):
    listed = (await async_client.get(f"{BASE}/{path}", headers=headers)).json()
    return next(m for m in listed if m["id"] == module_id)


@pytest.mark.asyncio
async def test_list_item_fields_unplayed(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    module, _ = await make_module(db_session, teacher, modes=["count", "count", "select"])
    item = await _item(async_client, headers, module.id)
    assert item["section"] == "logic"
    assert item["completed_count"] == 0
    assert item["last_played_at"] is None


@pytest.mark.asyncio
async def test_list_item_fields_played(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    module, acts = await make_module(db_session, teacher, modes=["trace", "trace", "trace"])
    for a in acts[:2]:
        res = await async_client.post(f"{BASE}/activities/{a.id}/complete", json={"stars": 2}, headers=headers)
        assert res.status_code == 200
    item = await _item(async_client, headers, module.id)
    assert item["section"] == "make"
    assert item["completed_count"] == 2
    assert isinstance(item["last_played_at"], str) and item["last_played_at"]
    detail = (await async_client.get(f"{BASE}/modules/{module.id}", headers=headers)).json()
    assert (detail["section"], detail["completed_count"]) == ("make", 2)
    assert detail["last_played_at"] == item["last_played_at"]


@pytest.mark.asyncio
async def test_unpublished_activity_not_counted(async_client, db_session, teacher):
    _, headers = await make_student(async_client, db_session)
    module, acts = await make_module(db_session, teacher)
    for a in acts[:2]:
        await async_client.post(f"{BASE}/activities/{a.id}/complete", json={"stars": 1}, headers=headers)
    await db_session.execute(update(EarlyActivity).where(EarlyActivity.id == acts[0].id).values(is_published=False))
    await db_session.commit()
    item = await _item(async_client, headers, module.id)
    assert item["completed_count"] == 1 and item["activities_count"] == 2


@pytest.mark.asyncio
async def test_public_list_has_section_and_zero_progress(async_client, db_session, teacher):
    module, _ = await make_module(db_session, teacher, modes=["typing", "typing", "typing"])
    item = await _item(async_client, {}, module.id, path="public/modules")
    assert item["section"] == "letters"
    assert item["completed_count"] == 0 and item["last_played_at"] is None
