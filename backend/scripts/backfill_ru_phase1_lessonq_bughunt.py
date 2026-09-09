"""Phase 1: backfill question_text_ru + bug_explanation_ru on LessonQuestion
bug_hunt rows that are missing RU translation.

Idempotent: re-running only picks up rows still missing question_text_ru.
Commits every COMMIT_EVERY rows. Uses translate_text_with_ai (is_json=True,
bundling question_text + bug_explanation into one call per row) from
app.services.grok_translation, with our own retry/backoff wrapper modeled
on scripts/bulk_translate.py's conservative CONCURRENCY=2 + Retry-After
handling (that script found concurrency=24 caused a 95% 429-fail rate).

code_snippet is NEVER translated.

Safe pattern: ORM only via AsyncSessionLocal, no app.main import, no DDL.
"""
from __future__ import annotations

import asyncio
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select, or_  # noqa: E402
from app.config import settings  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.lesson_question import LessonQuestion  # noqa: E402
import httpx  # noqa: E402

CONCURRENCY = 3
COMMIT_EVERY = 20
MAX_RETRIES = 6
TIMEOUT_S = 60.0
MODEL = "gpt-4.1"
LOG_PATH = Path(__file__).resolve().parent / "phase1_progress.log"

_PROMPT_TMPL = """\
You are a professional translator for a programming education platform.
Translate the JSON object below from Uzbek to Russian.

RULES:
- Return VALID JSON only, parseable by JSON.parse — no markdown fences, no commentary.
- Preserve the exact same keys: "question_text", "bug_explanation".
- Keep technical terms in their accepted form (HTML, CSS, JavaScript, Python, etc. stay as-is).
- Preserve markdown formatting and any inline code (`backticks`) untouched.
- Do not translate code identifiers, tag names, property names, or variable names.
- If a value is empty string, return it as empty string.

JSON to translate:
{payload}
"""


def _log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


async def _translate_pair(client: httpx.AsyncClient, question_text: str, bug_explanation: str) -> dict | None:
    payload = json.dumps({"question_text": question_text, "bug_explanation": bug_explanation or ""}, ensure_ascii=False)
    prompt = _PROMPT_TMPL.format(payload=payload)
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = await client.post(settings.openai_chat_url, headers=headers, json=body, timeout=TIMEOUT_S)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.strip("`")
                    if content.lstrip().lower().startswith("json"):
                        content = content.lstrip()[4:].lstrip()
                try:
                    parsed = json.loads(content)
                    if "question_text" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    pass
                return None
            if resp.status_code == 429 or resp.status_code in (500, 502, 503, 504):
                ra = resp.headers.get("retry-after")
                wait = float(ra) if ra and ra.replace(".", "", 1).isdigit() else (2 ** attempt) + random.random()
                await asyncio.sleep(min(wait, 30))
                continue
            return None
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError):
            await asyncio.sleep((2 ** attempt) + random.random())
        except Exception as e:
            _log(f"  exception: {e}")
            return None
    return None


async def main(dry_run: bool = False) -> None:
    t_start = time.monotonic()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LessonQuestion).where(
                LessonQuestion.question_kind == "bug_hunt",
                or_(LessonQuestion.question_text_ru.is_(None), LessonQuestion.question_text_ru == ""),
            ).order_by(LessonQuestion.id)
        )
        rows = result.scalars().all()

    _log(f"Phase1: {len(rows)} LessonQuestion bug_hunt rows need RU")
    if not rows:
        _log("Phase1: nothing to do.")
        return
    if dry_run:
        for row in rows[:5]:
            _log(f"  [{row.id}] {row.question_text[:80]!r}")
        _log("(dry run, no API calls)")
        return

    sem = asyncio.Semaphore(CONCURRENCY)
    translations: dict[int, dict] = {}
    failed: list[int] = []
    completed = 0

    async with httpx.AsyncClient(timeout=TIMEOUT_S, proxy=settings.HTTP_PROXY or None) as client:
        async def _one(row):
            nonlocal completed
            async with sem:
                res = await _translate_pair(client, row.question_text, row.bug_explanation or "")
                if res:
                    translations[row.id] = res
                else:
                    failed.append(row.id)
                completed += 1
                _log(f"  [{completed}/{len(rows)}] id={row.id} lesson={row.lesson_id} {'OK' if res else 'FAILED'}")

        await asyncio.gather(*[_one(r) for r in rows])

    _log(f"Translated: {len(translations)}  Failed: {len(failed)}")
    if failed:
        _log(f"Failed ids (left as-is, re-run to retry): {failed}")

    written = 0
    async with AsyncSessionLocal() as db:
        for i, (rid, tr) in enumerate(translations.items(), start=1):
            row = await db.get(LessonQuestion, rid)
            if row is None:
                continue
            row.question_text_ru = tr.get("question_text") or None
            row.bug_explanation_ru = tr.get("bug_explanation") or None
            written += 1
            if written % COMMIT_EVERY == 0:
                await db.commit()
                _log(f"  committed {written}/{len(translations)}")
        await db.commit()

    _log(f"Phase1 done in {time.monotonic() - t_start:.1f}s. Wrote {written} rows.")


if __name__ == "__main__":
    asyncio.run(main(dry_run="--dry-run" in sys.argv))
