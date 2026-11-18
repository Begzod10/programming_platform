"""Only the teachers listed in settings.LESSON_EDITOR_USERNAMES may change lessons and their
content (lessons, exercises, files, questions, vocabulary); every other teacher reads only."""
import pytest
import pytest_asyncio
from sqlalchemy import select

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import Student
from tests import _vocab_helpers as H

pytestmark = pytest.mark.real_lesson_editor


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    await H.cleanup()


async def _username(uid: int) -> str:
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(Student.username).where(Student.id == uid))).scalar_one()


@pytest_asyncio.fixture
async def setup(monkeypatch):
    editor = await H.make_user(teacher=True)
    other = await H.make_user(teacher=True)
    monkeypatch.setattr(settings, "LESSON_EDITOR_USERNAMES", f"someone_else, {await _username(editor)}")
    cid, (lid,) = await H.make_course(editor, lessons=1)
    return editor, other, cid, lid


WRITES = [
    ("post", "/api/v1/courses/{cid}/lessons", {"title": "Yangi dars", "order": 9}),
    ("put", "/api/v1/courses/{cid}/lessons/{lid}", {"title": "O'zgargan"}),
    ("post", "/api/v1/courses/{cid}/lessons/{lid}/exercises", {"title": "Mashq", "type": "text", "content": "x"}),
    ("post", "/api/v1/lessons/{lid}/questions", {"question": "Savol?", "options": ["a", "b"], "correct_index": 0}),
    ("post", "/api/v1/courses/{cid}/lessons/{lid}/vocabulary", {"word": "div", "definition": "blok"}),
    ("delete", "/api/v1/courses/{cid}/lessons/{lid}", None),
]


@pytest.mark.parametrize("method,path,body", WRITES)
async def test_other_teacher_cannot_change_lessons(async_client, setup, method, path, body):
    _, other, cid, lid = setup
    url = path.format(cid=cid, lid=lid)
    kwargs = {"headers": H.h(other)}
    if body is not None:
        kwargs["json"] = body
    res = await getattr(async_client, method)(url, **kwargs)
    assert res.status_code == 403, (url, res.status_code, res.text)


async def test_editor_can_change_lessons(async_client, setup):
    editor, _, cid, lid = setup
    res = await async_client.put(f"/api/v1/courses/{cid}/lessons/{lid}", json={"title": "O'zgargan"}, headers=H.h(editor))
    assert res.status_code == 200, res.text
    res = await async_client.post(f"/api/v1/courses/{cid}/lessons", json={"title": "Yangi dars", "order": 9}, headers=H.h(editor))
    assert res.status_code == 201, res.text


async def test_other_teacher_still_reads_lessons(async_client, setup):
    _, other, cid, lid = setup
    res = await async_client.get(f"/api/v1/courses/{cid}/lessons", headers=H.h(other))
    assert res.status_code == 200, res.text


def test_default_editors():
    from app.config import Settings
    assert {"rimefara_teach", "Shahzodweb"} <= set(Settings().lesson_editor_usernames)
