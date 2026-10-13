"""The builder writes a sample's RU title/description (entity 'lesson_sample') as an authored translation."""
import sys
import uuid
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from app.models.translation_cache import TranslationCache  # noqa: E402
from course_builder.translations import translate_sample_from_spec  # noqa: E402


class _Sample:
    def __init__(self, id_, title, description):
        self.id, self.title, self.description = id_, title, description


async def _rows(db, sample_id):
    return {r.field_name: r for r in (await db.execute(select(TranslationCache).where(
        TranslationCache.entity_type == "lesson_sample", TranslationCache.entity_id == sample_id,
        TranslationCache.lang == "ru"))).scalars().all()}


async def test_sample_title_and_description_are_written_as_authored_ru(db_session):
    sid = 920000 + uuid.uuid4().int % 70000
    sample = _Sample(sid, "Namuna: JWT", "Token namunasi.")
    written = await translate_sample_from_spec(db_session, sample, {"title_ru": "Пример: JWT", "description_ru": "Пример токена."})
    await db_session.commit()
    assert written == 2
    rows = await _rows(db_session, sid)
    assert rows["title"].translated_text == "Пример: JWT" and rows["title"].provider == "manual"
    assert rows["description"].translated_text == "Пример токена."


async def test_rerun_updates_instead_of_duplicating_and_skips_missing_fields(db_session):
    sid = 920000 + uuid.uuid4().int % 70000
    sample = _Sample(sid, "Namuna", None)
    await translate_sample_from_spec(db_session, sample, {"title_ru": "Пример"})
    await translate_sample_from_spec(db_session, sample, {"title_ru": "Пример 2"})
    await db_session.commit()
    rows = await _rows(db_session, sid)
    assert list(rows) == ["title"] and rows["title"].translated_text == "Пример 2"
    assert await translate_sample_from_spec(db_session, sample, {}) == 0
    assert await translate_sample_from_spec(db_session, sample, None) == 0
