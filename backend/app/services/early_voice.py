"""Pre-generated voice audio for the kids' games: instructions and short praise phrases.

The file name is derived from the text itself, so no database column is needed and an edited instruction never
plays the old recording: until scripts/generate_early_audio.py creates the new file the url is simply None.

See docs/superpowers/specs/2026-11-11-early-voice-instructions-design.md §3.1-3.2.
"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

from app.config import settings

VOICE_VERSION = "openai:gpt-4o-mini-tts:coral:v1"
LANGS = ("uz", "ru")
CACHE_SECONDS = 60

PHRASES: dict[str, dict[str, str]] = {
    "correct1": {"uz": "Barakalla!", "ru": "Молодец!"},
    "correct2": {"uz": "Zo'r!", "ru": "Здорово!"},
    "correct3": {"uz": "To'g'ri!", "ru": "Правильно!"},
    "correct4": {"uz": "Ofarin!", "ru": "Умница!"},
    "wrong1": {"uz": "Yana urinib ko'r.", "ru": "Попробуй ещё раз."},
    "wrong2": {"uz": "Hechqisi yo'q, yana bir bor.", "ru": "Ничего, давай ещё разок."},
    "star3": {"uz": "Zo'r! Hammasini topding!", "ru": "Отлично! Ты всё нашёл!"},
    "star2": {"uz": "Yaxshi! Deyarli hammasi to'g'ri!", "ru": "Хорошо! Почти всё правильно!"},
    "star1": {"uz": "Ajoyib urinish! Davom et, sen uddalaysan!", "ru": "Отличная попытка! Продолжай, у тебя получится!"},
}

_cache: dict[str, tuple[float, frozenset[str]]] = {}


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANGS else "uz"


def norm_text(text: str) -> str:
    return " ".join(text.split())


def audio_key(text: str, lang: str) -> str:
    raw = f"{VOICE_VERSION}|{norm_lang(lang)}|{norm_text(text)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def audio_dir(lang: str) -> Path:
    return Path(settings.UPLOAD_DIR) / "early-audio" / norm_lang(lang)


def audio_path(text: str, lang: str) -> Path:
    return audio_dir(lang) / f"{audio_key(text, lang)}.mp3"


def clear_cache() -> None:
    _cache.clear()


def _existing(lang: str) -> frozenset[str]:
    now = time.monotonic()
    hit = _cache.get(lang)
    if hit and hit[0] > now:
        return hit[1]
    try:
        names = frozenset(n for n in os.listdir(audio_dir(lang)) if n.endswith(".mp3"))
    except OSError:
        names = frozenset()
    _cache[lang] = (now + CACHE_SECONDS, names)
    return names


def audio_url(text: str | None, lang: str) -> str | None:
    if not text or not text.strip():
        return None
    lang = norm_lang(lang)
    name = f"{audio_key(text, lang)}.mp3"
    if name not in _existing(lang):
        return None
    return f"/uploads/early-audio/{lang}/{name}"


def phrase_urls(lang: str) -> dict[str, str]:
    lang = norm_lang(lang)
    urls = {key: audio_url(texts[lang], lang) for key, texts in PHRASES.items()}
    return {key: url for key, url in urls.items() if url}
