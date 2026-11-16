"""scripts/generate_early_audio.py: creates only missing files, dedupes texts, survives one failure, dry-runs."""
import uuid

import pytest

from app.config import settings
from app.services.early_voice import audio_path, clear_cache
from scripts import generate_early_audio as gen
from tests._early_helpers import make_module, make_teacher



@pytest.fixture
def tmp_upload(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    clear_cache()
    yield tmp_path
    clear_cache()


def _synth(monkeypatch, fail_on=()):
    calls = []

    async def fake(text, lang):
        calls.append((lang, text))
        if text in fail_on:
            raise RuntimeError("HTTP 500")
        return b"mp3"

    monkeypatch.setattr(gen, "synthesize", fake)
    return calls


async def _activities(async_client, db_session, uz_texts, ru_texts):
    teacher = await make_teacher(async_client, db_session)
    _, activities = await make_module(db_session, teacher, n_activities=len(uz_texts))
    for a, uz, ru in zip(activities, uz_texts, ru_texts):
        a.instruction_text = uz
        a.instruction_text_ru = ru
    await db_session.commit()


def _tag():
    return uuid.uuid4().hex[:8]


async def test_dry_run_writes_nothing_and_calls_nothing(async_client, db_session, tmp_upload, monkeypatch):
    t = _tag()
    await _activities(async_client, db_session, [f"Sana {t}.", f"Chiz {t}."], [f"Считай {t}.", None])
    calls = _synth(monkeypatch)
    out = await gen.run(dry_run=True, limit=None, lang=None, sleep=0)
    assert calls == []
    assert out["created"] == 0 and out["chars"] > 0
    assert not (tmp_upload / "early-audio").exists() or not any((tmp_upload / "early-audio").rglob("*.mp3"))


async def test_creates_missing_skips_existing_and_dedupes(async_client, db_session, tmp_upload, monkeypatch):
    t = _tag()
    same = f"Sana {t}."
    await _activities(async_client, db_session, [same, f"  Sana   {t}. "], [f"Считай {t}.", f"Обведи {t}."])
    calls = _synth(monkeypatch)
    first = await gen.run(dry_run=False, limit=None, lang=None, sleep=0)
    assert calls.count(("uz", same)) == 1
    assert ("ru", f"Считай {t}.") in calls and ("ru", f"Обведи {t}.") in calls
    assert ("uz", "Barakalla!") in calls
    assert audio_path(same, "uz").read_bytes() == b"mp3"
    assert first["failed"] == 0 and first["created"] == len(calls)

    again = _synth(monkeypatch)
    second = await gen.run(dry_run=False, limit=None, lang=None, sleep=0)
    assert again == []
    assert second["created"] == 0 and second["existing"] >= first["created"]


async def test_one_failure_does_not_stop_others(async_client, db_session, tmp_upload, monkeypatch):
    t = _tag()
    bad, good = f"Sana {t}.", f"Chiz {t}."
    await _activities(async_client, db_session, [bad, good], [None, None])
    _synth(monkeypatch, fail_on={bad})
    out = await gen.run(dry_run=False, limit=None, lang="uz", sleep=0)
    assert out["failed"] == 1
    assert audio_path(good, "uz").exists()
    assert not audio_path(bad, "uz").exists()
    assert not list(audio_path(bad, "uz").parent.glob("*.tmp"))


async def test_lang_filter_and_limit(async_client, db_session, tmp_upload, monkeypatch):
    t = _tag()
    await _activities(async_client, db_session, [f"Sana {t}."], [f"Считай {t}."])
    calls = _synth(monkeypatch)
    await gen.run(dry_run=False, limit=None, lang="ru", sleep=0)
    assert calls and all(lang == "ru" for lang, _ in calls)

    limited = _synth(monkeypatch)
    clear_cache()
    out = await gen.run(dry_run=False, limit=2, lang="uz", sleep=0)
    assert len(limited) == 2 and out["created"] == 2


def test_main_exit_code_on_failure(monkeypatch):
    async def fake_run(**kwargs):
        return {"created": 0, "existing": 0, "failed": 1, "missing": 0, "chars": 0}

    monkeypatch.setattr(gen, "run", fake_run)
    with pytest.raises(SystemExit) as exc:
        gen.main([])
    assert exc.value.code == 1
