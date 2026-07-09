"""Lesson/course content translation using AI (UZ ↔ RU ↔ EN).

Public API:
  translate_text_with_ai(text, *, source_lang, target_lang, is_json) — translate text
"""
from __future__ import annotations

from typing import Optional
import httpx

from app.config import settings

_LANG_NAMES = {
    "uz": "O'zbek tili",
    "ru": "Русский язык",
    "en": "English",
}

# Strip stray wrapper quotes the model occasionally adds around the
# translation (e.g. `"Profilingiz"` or `«Курсы»`). Only outer pairs.
_QUOTE_PAIRS = (("\"", "\""), ("'", "'"), ("«", "»"), ("“", "”"), ("`", "`"))


def _strip_outer_quotes(s: str) -> str:
    s = s.strip()
    for a, b in _QUOTE_PAIRS:
        if len(s) >= 2 and s.startswith(a) and s.endswith(b):
            inner = s[1:-1].strip()
            # Only strip if there's no matching delimiter inside — otherwise
            # we'd accidentally cut a quoted phrase mid-sentence.
            if a not in inner and b not in inner:
                return inner
    return s


async def _call_openai_translate(
    prompt: str, *, is_json: bool = False,
) -> Optional[str]:
    """Direct OpenAI call tuned for translation.

    Translation is quality-sensitive and predictable in shape, so we skip
    the Grok→Gemini→OpenAI fallback chain (which often retries multiple
    slow providers before settling) and hit gpt-4.1 directly. This keeps
    p95 latency tight enough for the catalogue endpoint to fit inside a
    single request budget.
    """
    if not settings.OPENAI_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0, proxy=settings.HTTP_PROXY or None) as client:
            payload = {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2000,
            }
            if is_json:
                payload["response_format"] = {"type": "json_object"}
            response = await client.post(
                settings.openai_chat_url,
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if response.status_code != 200:
                return None
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI translate xato: {e}")
        return None


async def translate_text_with_ai(
    text: str,
    *,
    source_lang: str,
    target_lang: str,
    is_json: bool = False,
) -> Optional[str]:
    """Translate `text` from `source_lang` to `target_lang`.

    Returns None on every failure path so the caller can fall back to the
    source string. For JSON payloads (sections_json), pass is_json=True —
    the prompt then instructs the model to preserve structure and only
    translate string values for known natural-language keys.
    """
    src = (text or "").strip()
    if not src:
        return src
    if source_lang == target_lang:
        return src
    if source_lang not in _LANG_NAMES or target_lang not in _LANG_NAMES:
        return None

    src_name = _LANG_NAMES[source_lang]
    tgt_name = _LANG_NAMES[target_lang]

    if is_json:
        prompt = f"""\
You are translating a JSON document used to render a programming lesson.

SOURCE LANGUAGE: {src_name}
TARGET LANGUAGE: {tgt_name}

RULES:
- Return VALID JSON only, parseable by JSON.parse — no markdown fences,
  no commentary, no leading or trailing prose.
- Preserve the structure exactly: keep every key, every array order,
  every type.
- Translate ONLY the string values of these keys when they appear:
  label, text, content, question, hint, prompt, answer, correctAnswer,
  description, title.
- Do NOT translate values for keys: type, id, url, videoUrl, imgUrl,
  code, codeLanguage, fileName, fileSize.
- Inside translated strings, leave inline code fragments (anything
  between backticks `…`) untouched.
- Preserve markdown formatting and HTML tags untouched in translated
  strings.

JSON to translate:
{src}
"""
    else:
        prompt = f"""\
You are a professional translator for a programming education platform.

Translate the following text from {src_name} to {tgt_name}.

RULES:
- Output ONLY the translation. No commentary, no quotes around the result.
- Keep technical terms in their accepted form (e.g. JavaScript stays
  JavaScript; HTML stays HTML).
- Preserve markdown (**, *, lists, headings) and HTML tags exactly.
- Inline code (`backticks`) stays in the original casing/spelling.
- Do not add or remove punctuation that changes meaning.
- If the source is already in {tgt_name}, return it unchanged.

SOURCE:
{src}
"""

    # Translation goes straight to GPT-4.1 (premium model, no fallback
    # chain) — quality matters more than provider redundancy here, and the
    # fallback chain often blocks for 10+ s waiting on a degraded Grok
    # before settling on OpenAI anyway.
    result = await _call_openai_translate(prompt, is_json=is_json)
    if not result:
        return None
    out = result.strip()
    if is_json:
        # Models sometimes wrap JSON in ```json fences despite the prompt.
        if out.startswith("```"):
            out = out.strip("`")
            # After stripping, an optional 'json' language tag may remain.
            if out.lstrip().lower().startswith("json"):
                out = out.lstrip()[4:].lstrip()
        out = out.strip()
    else:
        out = _strip_outer_quotes(out)
    return out or None
