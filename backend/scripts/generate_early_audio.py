"""Create the missing voice files for the kids' games: every activity instruction (uz + ru) and the praise phrases.

Safe to stop and re-run: a text whose file exists is skipped, a failed text is retried next time.

    python scripts/generate_early_audio.py --dry-run          # how many files and characters; no network, writes nothing
    python scripts/generate_early_audio.py --limit 5          # a small batch first
    python scripts/generate_early_audio.py                    # everything missing

Files land in {UPLOAD_DIR}/early-audio/{lang}/{key}.mp3 (key = hash of the text, see app/services/early_voice.py).
The app sees a new file within a minute. Exit code 1 if any text failed.

See docs/superpowers/specs/2026-11-11-early-voice-instructions-design.md §3.3.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.early_learning import EarlyActivity  # noqa: E402
from app.services.early_voice import LANGS, PHRASES, audio_path, norm_text  # noqa: E402

MODEL = "gpt-4o-mini-tts"
VOICE = "coral"
STYLE = "Warm, friendly, clear voice of a kind teacher speaking slowly to a five-year-old child."


async def synthesize(text: str, lang: str) -> bytes:
    """One OpenAI speech call through the app's relay/proxy settings. Never logs the key or the response body."""
    base = (settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    async with httpx.AsyncClient(timeout=90, proxy=settings.HTTP_PROXY or None) as client:
        resp = await client.post(
            f"{base}/audio/speech",
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            json={"model": MODEL, "voice": VOICE, "input": text, "instructions": STYLE, "response_format": "mp3"},
        )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")
    if not resp.content:
        raise RuntimeError("empty audio")
    return resp.content


async def collect_texts(lang: Optional[str]) -> list[tuple[str, str]]:
    """(lang, normalized text) pairs to voice: activity instructions + praise phrases, no blanks, no duplicates."""
    langs = [lang] if lang else list(LANGS)
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(EarlyActivity.instruction_text, EarlyActivity.instruction_text_ru))).all()
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []

    def add(lg: str, text: Optional[str]) -> None:
        if lg not in langs or not text or not text.strip():
            return
        item = (lg, norm_text(text))
        if item not in seen:
            seen.add(item)
            out.append(item)

    for uz, ru in rows:
        add("uz", uz)
        add("ru", ru)
    for texts in PHRASES.values():
        add("uz", texts["uz"])
        add("ru", texts["ru"])
    return out


async def run(*, dry_run: bool, limit: Optional[int], lang: Optional[str], sleep: float) -> dict:
    """{"created", "existing", "failed", "missing" (files without audio), "chars" (their characters)}.
    `limit` caps files created."""
    out = {"created": 0, "existing": 0, "failed": 0, "missing": 0, "chars": 0}
    for lg, text in await collect_texts(lang):
        path = audio_path(text, lg)
        if path.exists():
            out["existing"] += 1
            continue
        out["missing"] += 1
        out["chars"] += len(text)
        if dry_run:
            continue
        if limit is not None and out["created"] >= limit:
            break
        tmp = path.with_suffix(".mp3.tmp")
        try:
            data = await synthesize(text, lg)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_bytes(data)
            os.replace(tmp, path)
        except Exception as e:  # noqa: BLE001 — one bad text must not end the run
            out["failed"] += 1
            if tmp.exists():
                tmp.unlink()
            print(f"FAILED  [{lg}] «{text[:60]}»: {type(e).__name__}: {e}", flush=True)
        else:
            out["created"] += 1
            print(f"created [{lg}] «{text[:60]}»", flush=True)
        if sleep:
            await asyncio.sleep(sleep)
    return out


def main(argv: Optional[list[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="count what is missing; no network, writes nothing")
    ap.add_argument("--limit", type=int, default=None, help="stop after creating this many files")
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between speech calls")
    ap.add_argument("--lang", choices=LANGS, default=None, help="only this language")
    a = ap.parse_args(argv)
    out = asyncio.run(run(dry_run=a.dry_run, limit=a.limit, lang=a.lang, sleep=a.sleep))
    print(f"missing: {out['missing']} ({out['chars']} chars) | created: {out['created']} | "
          f"existing: {out['existing']} | failed: {out['failed']}", flush=True)
    if out["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
