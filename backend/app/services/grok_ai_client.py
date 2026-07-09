"""Multi-provider AI HTTP clients with automatic fallback chain.

Provides:
  ProviderError          — raised when a single provider fails
  call_chain(...)        — tries providers in configured order, returns first success
  parse_ai_json(text)    — extract JSON object from AI response text
  _ask_ai(prompt)        — simple best-effort fallback (no JSON enforcement)
"""
from __future__ import annotations

from typing import Optional, Any, Awaitable, Callable
import httpx
import re
import json
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Raised when a single provider can't return usable text."""


# ─────────────────────────────────────────────────────────────────────────────
# Per-provider HTTP calls (call_chain versions)
# ─────────────────────────────────────────────────────────────────────────────

async def _call_groq(prompt: str, max_tokens: int) -> str:
    if not settings.GROK_API_KEY:
        raise ProviderError("Groq API key not set")
    async with httpx.AsyncClient(timeout=60.0, proxy=settings.HTTP_PROXY or None) as client:
        resp = await client.post(
            settings.GROK_API_URL,
            headers={
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            },
        )
        if resp.status_code >= 400:
            raise ProviderError(f"Groq HTTP {resp.status_code}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"Groq response shape: {e}")


async def _call_gemini(prompt: str, max_tokens: int) -> str:
    if not settings.GEMINI_API_KEY:
        raise ProviderError("Gemini API key not set")
    url = (f"{settings.GEMINI_API_URL.rstrip('/')}/"
           f"{settings.GEMINI_MODEL}:generateContent"
           f"?key={settings.GEMINI_API_KEY}")
    async with httpx.AsyncClient(timeout=60.0, proxy=settings.HTTP_PROXY or None) as client:
        resp = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": max_tokens,
                    "responseMimeType": "application/json",
                },
            },
        )
        if resp.status_code >= 400:
            raise ProviderError(f"Gemini HTTP {resp.status_code}")
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"Gemini response shape: {e}")


async def _call_openai(prompt: str, max_tokens: int) -> str:
    if not settings.OPENAI_API_KEY:
        raise ProviderError("OpenAI API key not set")
    async with httpx.AsyncClient(timeout=60.0, proxy=settings.HTTP_PROXY or None) as client:
        resp = await client.post(
            settings.openai_chat_url,
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            },
        )
        if resp.status_code >= 400:
            raise ProviderError(f"OpenAI HTTP {resp.status_code}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"OpenAI response shape: {e}")


_PROVIDER_CALLERS: dict[str, Callable[[str, int], Awaitable[str]]] = {
    "groq": _call_groq,
    "gemini": _call_gemini,
    "openai": _call_openai,
}


async def call_chain(
        prompt: str,
        max_tokens: int,
        validator: Optional[Callable[[str], Any]] = None,
) -> tuple[str, Any, str, list[str]]:
    attempts: list[str] = []
    for provider in settings.ai_provider_chain_list:
        caller = _PROVIDER_CALLERS.get(provider)
        if caller is None:
            attempts.append(f"{provider}: unknown provider name")
            logger.warning("[ai-chain] %s -> skip (unknown provider name)", provider)
            continue

        started = time.perf_counter()
        try:
            text = await caller(prompt, max_tokens)
            if not text or not text.strip():
                raise ProviderError("empty response body")

            parsed: Any = None
            if validator is not None:
                parsed = validator(text)
                if parsed is None:
                    raise ProviderError("response failed validator (likely non-JSON)")

            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.info("[ai-chain] %s -> success in %dms", provider, elapsed_ms)
            return text, parsed, provider, attempts

        except ProviderError as e:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            attempts.append(f"{provider}: {e}")
            logger.warning("[ai-chain] %s -> error in %dms (%s)", provider, elapsed_ms, e)
        except httpx.TimeoutException:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            attempts.append(f"{provider}: timeout")
            logger.warning("[ai-chain] %s -> timeout after %dms", provider, elapsed_ms)
        except httpx.HTTPError as e:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            detail = str(e) or type(e).__name__
            attempts.append(f"{provider}: {type(e).__name__}: {detail}")
            logger.warning("[ai-chain] %s -> http error in %dms (%s: %s)", provider, elapsed_ms, type(e).__name__,
                           detail)
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            attempts.append(f"{provider}: unexpected {type(e).__name__}")
            logger.exception("[ai-chain] %s -> unexpected in %dms", provider, elapsed_ms)

    logger.error("[ai-chain] all providers failed: %s", "; ".join(attempts))
    raise ProviderError("; ".join(attempts) or "no providers configured")


def parse_ai_json(text: str) -> Optional[dict]:
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Simple fallback chain (_ask_ai versions)
# ─────────────────────────────────────────────────────────────────────────────

async def _call_grok(prompt: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                }
            )
            if response.status_code == 429:
                return None
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
    except Exception as e:
        print(f"Grok xato: {e}")
        return None


async def _call_gemini_simple(prompt: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000}
                }
            )
            if response.status_code == 429:
                return None
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return None
    except Exception as e:
        print(f"Gemini xato: {e}")
        return None


async def _call_openai_simple(prompt: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=60.0, proxy=settings.HTTP_PROXY or None) as client:
            response = await client.post(
                settings.openai_chat_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"}
                }
            )
            if response.status_code == 429:
                return None
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
    except Exception as e:
        print(f"OpenAI xato: {e}")
        return None


async def _ask_ai(prompt: str) -> Optional[str]:
    result = await _call_grok(prompt)
    if result:
        return result
    result = await _call_gemini_simple(prompt)
    if result:
        return result
    result = await _call_openai_simple(prompt)
    if result:
        return result
    return None
