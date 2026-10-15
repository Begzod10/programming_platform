"""POST /admin/translations/reload: RU rows written by a separate process (build_course) become visible without a restart."""
import uuid

from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.ranking import Ranking
from app.models.translation_cache import TranslationCache
from app.models.user import Student, UserRole
from app.services import translation_store as ts

URL = "/api/v1/admin/translations/reload"


async def _user(async_client, role=None):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"tr_{uid}", "email": f"tr_{uid}@example.com", "password": "securepass123"})
    sid = reg.json()["user"]["id"]
    if role:
        async with AsyncSessionLocal() as db:
            s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
            s.role = role
            await db.execute(delete(Ranking).where(Ranking.student_id == sid))
            await db.commit()
    return {"Authorization": f"Bearer {create_access_token(subject=sid)}"}


async def test_teacher_reload_picks_up_a_row_written_behind_the_apps_back(async_client):
    headers = await _user(async_client, UserRole.teacher)
    entity_id = 910000 + uuid.uuid4().int % 80000
    async with AsyncSessionLocal() as db:
        db.add(TranslationCache(entity_type="lesson", entity_id=entity_id, lang="ru", field_name="title",
                                translated_text="Что такое токен", source_text_hash="x", provider="author"))
        await db.commit()
    assert ts.get("lesson", entity_id, "ru", "title") is None            # the in-memory store is still stale

    res = await async_client.post(URL, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["entries"] >= 1
    assert ts.get("lesson", entity_id, "ru", "title") == "Что такое токен"


async def test_a_student_cannot_reload(async_client):
    res = await async_client.post(URL, headers=await _user(async_client))
    assert res.status_code == 403


async def test_anonymous_cannot_reload(async_client):
    assert (await async_client.post(URL)).status_code in (401, 403)
