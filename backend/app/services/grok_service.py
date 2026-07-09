"""Multi-provider AI calls with automatic fallback.

Chain order (configurable via settings.AI_PROVIDER_CHAIN, default
"groq,gemini,openai"):
  1) Groq        — fast and free for low volume; llama-3.3-70b-versatile
  2) Gemini 2.5  — cheap and reliable; gemini-2.5-flash with JSON mode
  3) OpenAI      — premium fallback; gpt-4.1-mini with JSON mode

Each provider is skipped if its API key is unset, and any HTTP / parse
failure transparently falls through to the next provider. We only return
an error dict if EVERY configured provider fails.

Public API:
  analyze_project_with_grok(...)   — grade a student project (1200 tok cap)
  explain_word_with_ai(word)       — dictionary lookup (400 tok cap)
  check_word_meaning_with_ai(...)  — review answer checker

Implementation is split across focused modules:
  grok_ai_client.py   — HTTP provider callers and fallback chain engine
  grok_translation.py — lesson/course content translation
  grok_review.py      — project grading and prompt builders
  grok_dictionary.py  — word explanation and answer checker
"""
from app.services.grok_ai_client import (
    ProviderError,
    call_chain,
    parse_ai_json,
    _ask_ai,
)
from app.services.grok_translation import translate_text_with_ai
from app.services.grok_review import analyze_project_with_grok
from app.services.grok_dictionary import (
    explain_word_with_ai,
    check_word_meaning_with_ai,
)

__all__ = [
    "ProviderError",
    "call_chain",
    "parse_ai_json",
    "_ask_ai",
    "translate_text_with_ai",
    "analyze_project_with_grok",
    "explain_word_with_ai",
    "check_word_meaning_with_ai",
]
