"""
Integration tests for the dictionary endpoints.

Verifies:
- GET /dictionary/ requires auth; returns empty list when authenticated.
- POST /dictionary/ requires auth; saves and returns a word when authenticated.
- DELETE /dictionary/{id} requires auth; returns 404 for unknown id.
- GET /dictionary/review/words requires auth; returns 404 when no words exist.
- GET /dictionary/practice/words requires auth; returns 400 when fewer than
  2 words exist (the minimum required by the practice engine).

The POST test mocks explain_word_with_ai to avoid external AI network calls.
"""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


_EXPLAIN_AI_PATH = "app.api.v1.endpoints.dictionary.explain_word_with_ai"


# ── GET /dictionary/ ──────────────────────────────────────────────────────────


async def test_get_dictionary_requires_auth(async_client: AsyncClient):
    """GET /api/v1/dictionary/ returns 401 without a token."""
    resp = await async_client.get("/api/v1/dictionary/")
    assert resp.status_code == 401


async def test_get_dictionary_authenticated_returns_empty_list(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /api/v1/dictionary/ with auth returns 200 and an empty list for a fresh user."""
    resp = await async_client.get("/api/v1/dictionary/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_dictionary_with_lang_filter(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /api/v1/dictionary/?lang=uz returns 200 (empty list when no words saved)."""
    resp = await async_client.get("/api/v1/dictionary/?lang=uz", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── POST /dictionary/ ─────────────────────────────────────────────────────────


async def test_add_word_requires_auth(async_client: AsyncClient):
    """POST /api/v1/dictionary/ returns 401 without a token."""
    resp = await async_client.post(
        "/api/v1/dictionary/",
        json={"word": "function", "lang": "uz"},
    )
    assert resp.status_code == 401


async def test_add_word_with_auth_returns_word(
    async_client: AsyncClient, auth_headers: dict
):
    """POST /api/v1/dictionary/ with auth saves the word and returns DictionaryOut.

    explain_word_with_ai is mocked to avoid any external network call.
    """
    with patch(
        _EXPLAIN_AI_PATH,
        new=AsyncMock(return_value={"short_definition": "A reusable block of code"}),
    ):
        resp = await async_client.post(
            "/api/v1/dictionary/",
            json={"word": "function", "lang": "uz"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "function"
    assert "id" in data
    assert "created_at" in data


async def test_add_word_empty_word_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """POST /api/v1/dictionary/ with an empty word returns 422."""
    resp = await async_client.post(
        "/api/v1/dictionary/",
        json={"word": "", "lang": "uz"},
        headers=auth_headers,
    )
    # Pydantic min_length=1 fires before the handler runs.
    assert resp.status_code == 422


# ── DELETE /dictionary/{id} ───────────────────────────────────────────────────


async def test_delete_word_requires_auth(async_client: AsyncClient):
    """DELETE /api/v1/dictionary/{id} returns 401 without a token."""
    resp = await async_client.delete("/api/v1/dictionary/99999")
    assert resp.status_code == 401


async def test_delete_word_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """DELETE /api/v1/dictionary/{id} returns 404 when the word doesn't exist."""
    resp = await async_client.delete("/api/v1/dictionary/99999", headers=auth_headers)
    assert resp.status_code == 404


# ── GET /dictionary/review/words ──────────────────────────────────────────────


async def test_review_words_requires_auth(async_client: AsyncClient):
    """GET /api/v1/dictionary/review/words returns 401 without a token."""
    resp = await async_client.get("/api/v1/dictionary/review/words")
    assert resp.status_code == 401


async def test_review_words_empty_dictionary_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /api/v1/dictionary/review/words returns 404 when no words have been saved."""
    resp = await async_client.get("/api/v1/dictionary/review/words", headers=auth_headers)
    assert resp.status_code == 404


# ── GET /dictionary/practice/words ────────────────────────────────────────────


async def test_practice_words_requires_auth(async_client: AsyncClient):
    """GET /api/v1/dictionary/practice/words returns 401 without a token."""
    resp = await async_client.get("/api/v1/dictionary/practice/words")
    assert resp.status_code == 401


async def test_practice_words_empty_dictionary_returns_400(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /api/v1/dictionary/practice/words returns 400 when fewer than 2 words exist.

    The practice engine requires at least 2 words to build a distractor set.
    """
    resp = await async_client.get(
        "/api/v1/dictionary/practice/words", headers=auth_headers
    )
    assert resp.status_code == 400
