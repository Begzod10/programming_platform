"""Regression tests for the OpenAI json_object 400 fix.

Live production error, confirmed via journalctl: OpenAI hard-rejects
`response_format: {"type": "json_object"}` with a 400
("'messages' must contain the word 'json' in some form...") unless the
literal word "json" appears somewhere in the messages sent. This broke
every OpenAI call for exercise_service.py's get_ai_explanation (a
plain-prose prompt that never mentions "json"), which then fell back to
Gemini and hit ITS quota too — net effect: AI grading was silently
non-functional platform-wide for hours.

Fix: `_ensure_json_keyword` appends a fixed instruction when "json" is
missing, applied only when `json_mode=True` (the new default); callers
that want plain prose back (get_ai_explanation) now pass
`json_mode=False`, which also drops `response_format`/`responseMimeType`
entirely rather than forcing a plain-text prompt into JSON mode.
"""
import json as json_module
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.grok_ai_client import (
    _ensure_json_keyword, _call_openai, _call_groq, _call_gemini, call_chain,
)


def test_ensure_json_keyword_adds_suffix_when_missing():
    prompt = "Sen dasturlash o'qituvchisisiz. Tushuntirib ber."
    result = _ensure_json_keyword(prompt)
    assert "json" in result.lower()
    assert result.startswith(prompt)


def test_ensure_json_keyword_leaves_prompt_untouched_when_present():
    prompt = "Faqat JSON formatda javob ber: {...}"
    assert _ensure_json_keyword(prompt) == prompt


def test_ensure_json_keyword_is_case_insensitive():
    prompt = "Please respond in Json format."
    assert _ensure_json_keyword(prompt) == prompt


def _mock_openai_response(content: str, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = "" if status_code == 200 else '{"error": {"message": "boom"}}'
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    return resp


async def test_call_openai_json_mode_true_sends_response_format_and_json_word(monkeypatch):
    monkeypatch.setattr("app.config.settings.OPENAI_API_KEY", "sk-test")
    captured = {}

    async def fake_post(self, url, headers=None, json=None):
        captured["payload"] = json
        return _mock_openai_response('{"ok": true}')

    with patch("httpx.AsyncClient.post", new=fake_post):
        await _call_openai("Explain this exercise.", 300, json_mode=True)

    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert "json" in captured["payload"]["messages"][0]["content"].lower()


async def test_call_openai_json_mode_false_omits_response_format_and_prompt(monkeypatch):
    monkeypatch.setattr("app.config.settings.OPENAI_API_KEY", "sk-test")
    captured = {}
    original_prompt = "Explain this exercise in plain prose."

    async def fake_post(self, url, headers=None, json=None):
        captured["payload"] = json
        return _mock_openai_response("plain text explanation")

    with patch("httpx.AsyncClient.post", new=fake_post):
        await _call_openai(original_prompt, 300, json_mode=False)

    assert "response_format" not in captured["payload"]
    # Prompt must be sent verbatim -- no "json" instruction glued on when
    # the caller explicitly doesn't want JSON-mode output.
    assert captured["payload"]["messages"][0]["content"] == original_prompt


async def test_call_openai_reproduces_the_live_400_without_the_fix(monkeypatch):
    """Sanity check that the mock actually models the real failure: a
    prompt with no "json" mention, sent WITHOUT going through
    _ensure_json_keyword, is exactly what production logs showed OpenAI
    rejecting. This doesn't call the fixed code path -- it documents the
    bug the fix addresses."""
    monkeypatch.setattr("app.config.settings.OPENAI_API_KEY", "sk-test")

    async def fake_post_400(self, url, headers=None, json=None):
        assert "json" not in json["messages"][0]["content"].lower()
        return _mock_openai_response("", status_code=400)

    from app.services.grok_ai_client import ProviderError

    async def raw_call_without_fix(prompt, max_tokens):
        # Mirrors the pre-fix _call_openai body exactly: unconditional
        # response_format, no _ensure_json_keyword.
        import httpx
        from app.config import settings
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                settings.openai_chat_url,
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                },
            )
            if resp.status_code >= 400:
                raise ProviderError(f"OpenAI HTTP {resp.status_code}")

    with patch("httpx.AsyncClient.post", new=fake_post_400):
        with pytest.raises(ProviderError):
            await raw_call_without_fix("Explain this exercise.", 300)


async def test_call_groq_json_mode_false_omits_response_format(monkeypatch):
    monkeypatch.setattr("app.config.settings.GROK_API_KEY", "gsk-test")
    captured = {}

    async def fake_post(self, url, headers=None, json=None):
        captured["payload"] = json
        return _mock_openai_response("plain text")

    with patch("httpx.AsyncClient.post", new=fake_post):
        await _call_groq("Explain this.", 300, json_mode=False)

    assert "response_format" not in captured["payload"]


async def test_call_gemini_json_mode_false_omits_mime_type(monkeypatch):
    monkeypatch.setattr("app.config.settings.GEMINI_API_KEY", "gm-test")
    captured = {}

    async def fake_post(self, url, headers=None, json=None):
        captured["payload"] = json
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"candidates": [{"content": {"parts": [{"text": "hi"}]}}]}
        return resp

    with patch("httpx.AsyncClient.post", new=fake_post):
        await _call_gemini("Explain this.", 300, json_mode=False)

    assert "responseMimeType" not in captured["payload"]["generationConfig"]


async def test_call_chain_threads_json_mode_to_provider(monkeypatch):
    monkeypatch.setattr("app.config.settings.AI_PROVIDER_CHAIN", "openai")
    monkeypatch.setattr("app.config.settings.OPENAI_API_KEY", "sk-test")
    captured = {}

    async def fake_post(self, url, headers=None, json=None):
        captured["payload"] = json
        return _mock_openai_response("plain prose result")

    with patch("httpx.AsyncClient.post", new=fake_post):
        text, parsed, provider, attempts = await call_chain(
            "Tell me why this answer is wrong.", 300, validator=None, json_mode=False,
        )

    assert text == "plain prose result"
    assert "response_format" not in captured["payload"]
