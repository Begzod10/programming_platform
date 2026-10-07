"""
Tests for the dictionary practice_words module.

Split into:
  - Unit tests for the pure _serialize helper (no DB, no HTTP).
  - Integration tests for the /words and /due-counts HTTP endpoints.

The GET /words endpoint requires at least 2 words in the student's dictionary
to build options lists; fewer triggers a 400.  A dedicated fixture inserts 5
rows directly via SQLAlchemy so no AI call is needed.
"""

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.practice_words import _serialize
from app.db.database import AsyncSessionLocal
from app.models.dictionary import UserDictionary


# ── Helpers / fixtures ────────────────────────────────────────────────────────

def _make_word(word_id: int, word: str, context: str = "") -> UserDictionary:
    """Create an in-memory UserDictionary ORM instance (not committed)."""
    w = UserDictionary()
    w.id = word_id
    w.word = word
    w.context = context
    w.lesson_id = None
    w.interval_days = 0
    w.lapses = 0
    w.ease_factor = 2.5
    w.review_count = 0
    w.reps = 0
    w.next_review_at = None
    w.lang = "uz"
    return w


@pytest_asyncio.fixture
async def student_with_words(async_client: AsyncClient) -> dict:
    """Register a student, log them in, seed 5 dictionary words, return context."""
    uid = uuid.uuid4().hex[:8]
    username = f"dictuser_{uid}"
    email = f"dict_{uid}@example.com"
    password = "testpassword123"

    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert reg.status_code == 201, reg.text

    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    user_id = me.json()["id"]

    # Insert 5 words directly — avoids the AI explain-word call.
    async with AsyncSessionLocal() as session:
        words = [
            UserDictionary(
                student_id=user_id,
                word=f"word{i}_{uid}",
                context=f"context sentence {i}",
                lang="uz",
            )
            for i in range(5)
        ]
        session.add_all(words)
        await session.commit()

    return {"headers": headers, "user_id": user_id}


# ── Unit tests: _serialize (pure function, no DB, no HTTP) ───────────────────

def test_serialize_target_word_is_in_options():
    """The serialized options list must always contain the word itself."""
    target = _make_word(1, "python")
    pool = [target] + [_make_word(i, f"distractor{i}") for i in range(2, 6)]
    result = _serialize(target, pool)
    assert target.word in result["options"]


def test_serialize_options_list_has_at_least_two_entries():
    """With a pool of 2, options contains 2 entries (word + 1 distractor)."""
    target = _make_word(1, "python")
    other = _make_word(2, "java")
    result = _serialize(target, [target, other])
    assert len(result["options"]) >= 2


def test_serialize_result_contains_required_fields():
    """Every key that the frontend depends on must be present."""
    target = _make_word(10, "algorithm", "a step-by-step process")
    pool = [target] + [_make_word(i, f"w{i}") for i in range(11, 15)]
    result = _serialize(target, pool)

    required = {
        "id", "word", "context", "lesson_id", "options",
        "context_options", "interval_days", "lapses",
        "ease_factor", "review_count", "next_review_at",
    }
    assert required.issubset(result.keys())


def test_serialize_options_max_four_entries():
    """Options should not exceed 4 (word + up to 3 distractors)."""
    target = _make_word(1, "python")
    pool = [target] + [_make_word(i, f"lang{i}") for i in range(2, 20)]
    result = _serialize(target, pool)
    assert len(result["options"]) <= 4


def test_serialize_metadata_matches_source_word():
    """Scalar fields in the result must match the source word object."""
    target = _make_word(42, "recursion", "a function that calls itself")
    target.interval_days = 3
    target.lapses = 1
    target.ease_factor = 2.3
    target.review_count = 5
    result = _serialize(target, [target] + [_make_word(i, f"x{i}") for i in range(2, 5)])

    assert result["id"] == 42
    assert result["word"] == "recursion"
    assert result["context"] == "a function that calls itself"
    assert result["interval_days"] == 3
    assert result["lapses"] == 1
    assert result["ease_factor"] == 2.3
    assert result["review_count"] == 5
    assert result["next_review_at"] is None


# ── Integration: /words endpoint ─────────────────────────────────────────────

async def test_words_endpoint_requires_authentication(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/dictionary/practice/words")
    assert resp.status_code == 401


async def test_words_empty_dictionary_returns_400(
    async_client: AsyncClient, auth_headers: dict
):
    """No words in dict → the 'not enough words' guard raises 400."""
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words", headers=auth_headers
    )
    assert resp.status_code == 400


async def test_words_with_five_entries_returns_non_empty_list(
    async_client: AsyncClient, student_with_words: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words",
        headers=student_with_words["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


async def test_words_count_param_limits_number_of_results(
    async_client: AsyncClient, student_with_words: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words?count=2",
        headers=student_with_words["headers"],
    )
    assert resp.status_code == 200
    assert len(resp.json()) <= 2


async def test_words_each_item_has_required_fields(
    async_client: AsyncClient, student_with_words: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words",
        headers=student_with_words["headers"],
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert "id" in item
        assert "word" in item
        assert "options" in item
        assert isinstance(item["options"], list)
        assert len(item["options"]) >= 2


async def test_words_target_always_present_in_options(
    async_client: AsyncClient, student_with_words: dict
):
    """For each word returned, the word itself must appear in its options."""
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words",
        headers=student_with_words["headers"],
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert item["word"] in item["options"], (
            f"word '{item['word']}' missing from options {item['options']}"
        )


# ── Integration: /due-counts endpoint ────────────────────────────────────────

async def test_due_counts_requires_authentication(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/dictionary/practice/due-counts")
    assert resp.status_code == 401


async def test_due_counts_returns_expected_keys(
    async_client: AsyncClient, auth_headers: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/due-counts", headers=auth_headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "due" in body
    assert "fragile" in body
    assert "total" in body


async def test_due_counts_total_zero_for_empty_dictionary(
    async_client: AsyncClient, auth_headers: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/due-counts", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_due_counts_total_matches_seeded_words(
    async_client: AsyncClient, student_with_words: dict
):
    resp = await async_client.get(
        "/api/v1/dictionary/practice/due-counts",
        headers=student_with_words["headers"],
    )
    assert resp.status_code == 200
    body = resp.json()
    # We seeded exactly 5 words; total must equal 5.
    assert body["total"] == 5
    # All newly created words have next_review_at=None → all are due.
    assert body["due"] == 5


# ── "pick the meaning" options must all be in the same language ──────────────

def test_context_options_never_mix_uzbek_and_russian_definitions():
    uz = "Veb-sahifalarning tuzilishini belgilash uchun ishlatiladigan markup tili."
    ru = "Задаёт горизонтальный размер элемента на веб-странице."
    target = _make_word(1, "HTML", uz)
    pool = [
        target,
        _make_word(2, "width", ru),
        _make_word(3, "div", "Sahifa tarkibini guruhlash uchun ishlatiladigan element."),
        _make_word(4, "flex", "Элементы выстраиваются в гибкую строку."),
        _make_word(5, "plan", "Muayyan maqsadga erishish uchun rejalashtirilgan ishlar."),
    ]
    for _ in range(30):
        opts = _serialize(target, pool)["context_options"]
        assert not any(any("Ѐ" <= c <= "ӿ" for c in o) for o in opts), opts
        assert len(opts) == 3   # target + the two other Uzbek definitions


def test_russian_word_only_gets_russian_options():
    ru = "Задаёт горизонтальный размер элемента на веб-странице."
    target = _make_word(1, "width", ru)
    pool = [target, _make_word(2, "HTML", "Veb-sahifalar tuzilishi uchun markup tili."),
            _make_word(3, "flex", "Элементы выстраиваются в гибкую строку.")]
    for _ in range(20):
        opts = _serialize(target, pool)["context_options"]
        assert all(any("Ѐ" <= c <= "ӿ" for c in o) for o in opts), opts


def test_no_same_language_distractor_leaves_a_single_option_so_the_client_falls_back():
    target = _make_word(1, "HTML", "Veb-sahifalar tuzilishi uchun markup tili.")
    pool = [target, _make_word(2, "width", "Задаёт горизонтальный размер элемента.")]
    assert len(_serialize(target, pool)["context_options"]) == 1


# ── masking: suffixes, apostrophes, fixed length ─────────────────────────────

from app.api.v1.endpoints.practice_words import _mask_word_in_text, _one_row_per_word  # noqa: E402


def test_mask_catches_apostrophe_and_plain_suffixes():
    out = _mask_word_in_text("JavaScript'da funksiyalar va funksiyani yoziladi", "funksiya")
    assert "funksiya" not in out.lower()
    assert _mask_word_in_text("JavaScript's tili, JavaScript'da", "JavaScript").count("_____") == 2


def test_mask_has_a_fixed_length_and_leaves_longer_words_alone():
    assert _mask_word_in_text("a width b", "width") == "a _____ b"
    assert _mask_word_in_text("a hypertext b", "hypertext") == "a _____ b"
    # a short token only matches as a whole word / apostrophe form
    assert _mask_word_in_text("interface in the end", "in") == "interface _____ the end"


def test_mask_of_a_phrase_skips_function_words():
    out = _mask_word_in_text("the end of the road is near", "in the end")
    assert out == "the _____ of the road is near"


# ── options: no twin rows, no duplicates ─────────────────────────────────────

def test_options_never_contain_the_target_twice_or_a_duplicate():
    target = _make_word(1, "array", "Massiv — elementlar to'plami.")
    twin = _make_word(2, "Array", "Массив — набор элементов.")
    twin.lang = "ru"
    same_def = _make_word(3, "list", "Massiv — elementlar to'plami.")
    pool = [target, twin, same_def, _make_word(4, "set", "Noyob qiymatlar to'plami."),
            _make_word(5, "dict", "Kalit-qiymat juftliklari.")]
    for _ in range(40):
        r = _serialize(target, pool)
        assert [o.lower() for o in r["options"]].count("array") == 1
        assert len({o.lower() for o in r["options"]}) == len(r["options"])
        ctx = [c.lower() for c in r["context_options"]]
        assert len(set(ctx)) == len(ctx)


def test_one_row_per_word_prefers_the_ui_language():
    uz = _make_word(1, "array", "uz def")
    ru = _make_word(2, "Array", "ru def")
    ru.lang = "ru"
    other = _make_word(3, "set", "x")
    assert [w.id for w in _one_row_per_word([uz, ru, other], "ru")] == [2, 3]
    assert [w.id for w in _one_row_per_word([uz, ru, other], None)] == [1, 3]


# ── SRS: ease recovers, lapses are forgiven once learned ─────────────────────

from app.services import srs  # noqa: E402


def test_good_reviews_win_back_ease_and_long_intervals_forgive_a_lapse():
    s = srs.schedule_after_review(reps=3, lapses=2, ease_factor=1.9, interval_days=30, grade=2)
    assert s["ease_factor"] == 1.95
    assert s["lapses"] == 1                 # interval >= 21 days
    young = srs.schedule_after_review(reps=2, lapses=2, ease_factor=1.9, interval_days=3, grade=2)
    assert young["lapses"] == 2 and young["ease_factor"] == 1.95
    capped = srs.schedule_after_review(reps=5, lapses=0, ease_factor=2.5, interval_days=10, grade=2)
    assert capped["ease_factor"] == 2.5     # never above the default
    hard = srs.schedule_after_review(reps=5, lapses=0, ease_factor=2.0, interval_days=10, grade=1)
    assert hard["ease_factor"] == 1.85


# ── HTTP: stats overview, UTC timestamps, session validation ─────────────────

def test_weeks_active_handles_naive_first_seen_against_aware_now():
    from datetime import datetime, timedelta, timezone
    from app.api.v1.endpoints.practice_stats import _weeks_active
    now = datetime.now(timezone.utc)
    assert _weeks_active(now, (now - timedelta(days=21)).replace(tzinfo=None)) == pytest.approx(3.0, abs=0.01)
    assert _weeks_active(now, now.replace(tzinfo=None)) == 1.0   # never below one week


async def test_completed_session_times_are_marked_utc(async_client, student_with_words):
    h = student_with_words["headers"]
    created = await async_client.post("/api/v1/dictionary/practice/session", json={"mode": "flashcard"}, headers=h)
    assert created.status_code == 200, created.text
    assert created.json()["started_at"].endswith("Z")       # parsed as UTC by the browser
    sid = created.json()["id"]
    done = await async_client.put(f"/api/v1/dictionary/practice/session/{sid}/complete",
                                  json={"total_words": 5, "correct": 4}, headers=h)
    assert done.status_code == 200, done.text
    assert done.json()["completed_at"].endswith("Z")


async def test_complete_session_rejects_more_correct_than_total(async_client, student_with_words):
    h = student_with_words["headers"]
    sid = (await async_client.post("/api/v1/dictionary/practice/session", json={"mode": "quiz"}, headers=h)).json()["id"]
    bad = await async_client.put(f"/api/v1/dictionary/practice/session/{sid}/complete",
                                 json={"total_words": 3, "correct": 4}, headers=h)
    assert bad.status_code == 400
