"""Voice instructions: audio url from the hashed text, and the public phrase list."""
import pytest
import pytest_asyncio

from app.config import settings
from app.services import early_voice
from app.services.early_voice import PHRASES, audio_key, audio_path, audio_url, clear_cache
from tests._early_helpers import make_module, make_student, make_teacher

BASE = "/api/v1/early-learning"


@pytest.fixture
def tmp_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    clear_cache()
    yield tmp_path
    clear_cache()


@pytest.fixture(autouse=True)
def _games_unlocked():
    from app.main import app
    from app.dependencies import require_games_unlocked
    app.dependency_overrides[require_games_unlocked] = lambda: None
    yield
    app.dependency_overrides.pop(require_games_unlocked, None)


def _touch(text, lang):
    path = audio_path(text, lang)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")


def test_audio_key_stable_and_normalized():
    assert audio_key("Salom  dunyo ", "uz") == audio_key("Salom dunyo", "uz")
    assert len(audio_key("Salom", "uz")) == 20
    assert audio_key("Salom", "uz") != audio_key("Salom", "ru")
    assert audio_key("Salom", "uz") != audio_key("Salom!", "uz")


def test_audio_url_only_when_file_exists(tmp_upload):
    assert audio_url("Harfni chiz.", "uz") is None
    assert audio_url("", "uz") is None
    assert audio_url(None, "uz") is None
    _touch("Harfni chiz.", "uz")
    clear_cache()
    assert audio_url("Harfni chiz.", "uz") == f"/uploads/early-audio/uz/{audio_key('Harfni chiz.', 'uz')}.mp3"


def test_audio_url_cache_hides_new_file_until_cleared(tmp_upload):
    assert audio_url("A", "uz") is None
    _touch("A", "uz")
    assert audio_url("A", "uz") is None
    clear_cache()
    assert audio_url("A", "uz") is not None


def test_phrases_cover_spec_table():
    assert set(PHRASES) == {"correct1", "correct2", "correct3", "correct4", "wrong1", "wrong2",
                            "star1", "star2", "star3"}
    assert PHRASES["correct1"] == {"uz": "Barakalla!", "ru": "Молодец!"}
    assert PHRASES["star1"]["uz"] == "Ajoyib urinish! Davom et, sen uddalaysan!"


@pytest.mark.asyncio
async def test_activity_detail_has_audio_url_per_language(async_client, db_session, tmp_upload):
    teacher = await make_teacher(async_client, db_session)
    module, (activity,) = await make_module(db_session, teacher, n_activities=1)
    activity.instruction_text = "Harfni chiz."
    activity.instruction_text_ru = "Обведи букву."
    await db_session.commit()
    _touch("Harfni chiz.", "uz")
    clear_cache()
    expected = f"/uploads/early-audio/uz/{audio_key('Harfni chiz.', 'uz')}.mp3"

    _, headers = await make_student(async_client, db_session)
    uz = (await async_client.get(f"{BASE}/modules/{module.id}?lang=uz", headers=headers)).json()
    assert uz["activities"][0]["instruction_audio_url"] == expected
    ru = (await async_client.get(f"{BASE}/modules/{module.id}?lang=ru", headers=headers)).json()
    assert ru["activities"][0]["instruction_audio_url"] is None
    public = (await async_client.get(f"{BASE}/public/modules/{module.id}?lang=uz")).json()
    assert public["activities"][0]["instruction_audio_url"] == expected


@pytest.mark.asyncio
async def test_public_voice_lists_only_existing_phrases(async_client, tmp_upload):
    _touch(PHRASES["correct1"]["uz"], "uz")
    clear_cache()
    expected = {"correct1": f"/uploads/early-audio/uz/{audio_key('Barakalla!', 'uz')}.mp3"}
    res = await async_client.get(f"{BASE}/public/voice?lang=uz")
    assert res.status_code == 200, res.text
    assert res.json() == {"phrases": expected}
    other = await async_client.get(f"{BASE}/public/voice?lang=xx")
    assert other.status_code == 200
    assert other.json() == {"phrases": expected}
    ru = await async_client.get(f"{BASE}/public/voice?lang=ru")
    assert ru.json() == {"phrases": {}}
