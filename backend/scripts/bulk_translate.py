"""Bulk-translate every lesson + exercise to Russian, dedup'd by source string.

Strategy:
  1. Collect every unique translatable source string across all lessons +
     exercises (single pass over the DB).
  2. For each unique string, check if a cache hit already exists anywhere
     (lookup by source_text_hash — if any cache row has the same hash,
     reuse its translation; the dedup table is implicit in the cache).
  3. Otherwise call gpt-4.1 with a bounded semaphore so we never have
     more than CONCURRENCY simultaneous requests.
  4. Once we have a {hash → translation} map for every unique string,
     walk lessons + exercises again and write a translation_cache row
     per (entity, lang, field) — only for rows that don't already exist
     with the current source hash.

Incremental: commits in batches so an interrupt doesn't lose work.
"""
import asyncio, json, time, sys, random
from collections import defaultdict
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import httpx
from app.config import settings
from app.services.translation_service import _collect_translatable_strings, _set_at_path, _hash_source

TARGET_LANG = 'ru'
SOURCE_LANG_DEFAULT = 'uz'
# Previous run died at concurrency=24 with 95% 429-fail. Drop to 8.
# Even gpt-4.1 with a tier-2 key tops out around 10 concurrent.
CONCURRENCY = 2
COMMIT_EVERY = 50
MAX_RETRIES = 6
TIMEOUT_S = 60.0
MODEL = 'gpt-4.1'

_LANG_NAMES = {"uz": "Uzbek", "ru": "Russian", "en": "English"}


def _build_prompt(text_in: str) -> str:
    return f"""You are a professional translator for a programming education platform.

Translate the following text from {_LANG_NAMES[SOURCE_LANG_DEFAULT]} to {_LANG_NAMES[TARGET_LANG]}.

RULES:
- Output ONLY the translation. No commentary, no quotes around the result.
- Keep technical terms in their accepted form (JavaScript, HTML, CSS, Git, etc.).
- Preserve markdown (**, *, lists, headings) and HTML tags exactly.
- Inline code (`backticks`) stays in original casing/spelling.
- If the input is a code block: translate ONLY comment lines (lines starting with # or //).
  Leave all commands, variable names, strings inside echo/print, and code structure EXACTLY as-is.
- If the source is already in {_LANG_NAMES[TARGET_LANG]}, return it unchanged.

SOURCE:
{text_in}
"""


async def translate_with_retry(client: httpx.AsyncClient, text_in: str) -> str | None:
    """Direct OpenAI call w/ proper 429 + retry-after handling.

    The grok_service.translate_text_with_ai swallows non-200 as plain
    failure, so a 429 storm produces a quiet 95% failure rate. Here we
    honor Retry-After and back off exponentially with jitter.
    """
    if not text_in or not text_in.strip(): return text_in
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": _build_prompt(text_in)}],
        "temperature": 0.1,
        "max_tokens": 2000,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = await client.post(settings.openai_chat_url, headers=headers, json=payload, timeout=TIMEOUT_S)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            if resp.status_code == 429 or resp.status_code in (500, 502, 503, 504):
                ra = resp.headers.get("retry-after")
                wait = float(ra) if ra and ra.replace('.','',1).isdigit() else (2 ** attempt) + random.random()
                await asyncio.sleep(min(wait, 30))
                continue
            return None  # unrecoverable 4xx
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError):
            await asyncio.sleep((2 ** attempt) + random.random())
        except Exception:
            return None
    return None


engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)


def collect_lesson_field_strings(row) -> dict[str, list[str]]:
    """Return dict {field_name: [source_string, ...]} for one lesson row.

    `sections_json` is special — its translation is a whole reassembled
    JSON blob, not a single string, so we hand off the parsed tree
    separately and the caller handles stitching.
    """
    out: dict[str, list[str]] = {}
    for fld in ("title","chapter","text_content","task_title","task_description","task_requirements","task_technologies"):
        v = row[fld]
        if v and v.strip():
            out[fld] = [v]
    return out


def collect_exercise_field_strings(row) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for fld in ("description","hint","expected_answer","explanation"):
        v = row[fld]
        if v and v.strip():
            out[fld] = [v]
    return out


async def main():
    t_start = time.monotonic()
    async with engine.connect() as conn:
        lessons = (await conn.execute(text("""
            SELECT id, title, chapter, text_content, task_title, task_description,
                   task_requirements, task_technologies, sections_json,
                   COALESCE(source_lang,'uz') AS source_lang
            FROM lessons
            ORDER BY id
        """))).mappings().all()
        exercises = (await conn.execute(text("""
            SELECT id, lesson_id, description, hint, expected_answer, explanation
            FROM exercises WHERE is_active = true ORDER BY id
        """))).mappings().all()
        cached = {
            (r[0], r[1], r[2], r[3]): r[4]
            for r in (await conn.execute(text("""
                SELECT entity_type, entity_id, lang, field_name, source_text_hash
                FROM translation_cache WHERE lang = :lang
            """), {"lang": TARGET_LANG})).all()
        }

    # ──────────────────────────────────────────────────────────────
    # 1. Collect every unique source string we need to translate
    # ──────────────────────────────────────────────────────────────
    unique_sources: dict[str, str] = {}  # source_string -> hash

    def remember(s: str):
        s = (s or "").strip()
        if not s: return
        unique_sources[s] = _hash_source(s)

    # All scalar lesson fields
    for l in lessons:
        if l["source_lang"] != "uz": continue
        for fld, strings in collect_lesson_field_strings(l).items():
            for s in strings: remember(s)
        # sections_json — translate strings inside, not the blob
        if l["sections_json"]:
            try:
                tree = json.loads(l["sections_json"])
                pairs = []
                _collect_translatable_strings(tree, pairs)
                for _, s in pairs: remember(s)
            except Exception: pass

    for e in exercises:
        for fld, strings in collect_exercise_field_strings(e).items():
            for s in strings: remember(s)

    print(f"Unique source strings to translate: {len(unique_sources)}")

    # ──────────────────────────────────────────────────────────────
    # 2. Build hash → translation map. Reuse existing cache hits.
    # ──────────────────────────────────────────────────────────────
    hash_to_translation: dict[str, str] = {}
    async with engine.connect() as conn:
        # Pull every existing translation row; if its source_text_hash matches
        # something we're about to translate, reuse it.
        existing_translations = (await conn.execute(text("""
            SELECT source_text_hash, translated_text FROM translation_cache
            WHERE lang = :lang
        """), {"lang": TARGET_LANG})).all()
    for h, t in existing_translations:
        if t and t.strip():
            hash_to_translation[h] = t

    needs_translation = [s for s, h in unique_sources.items() if h not in hash_to_translation]
    print(f"Already in cache by hash: {len(unique_sources) - len(needs_translation)}")
    print(f"Need fresh translation:    {len(needs_translation)}")

    if needs_translation:
        sem = asyncio.Semaphore(CONCURRENCY)
        completed = 0
        failed = 0
        async with httpx.AsyncClient(timeout=TIMEOUT_S, proxy=settings.HTTP_PROXY or None) as client:
            async def _translate_one(s: str):
                nonlocal completed, failed
                async with sem:
                    tr = await translate_with_retry(client, s)
                    if tr and tr.strip():
                        hash_to_translation[unique_sources[s]] = tr
                    else:
                        failed += 1
                    completed += 1
                    if completed % 50 == 0 or completed == len(needs_translation):
                        print(f"  [{completed}/{len(needs_translation)}] failed={failed} elapsed={time.monotonic()-t_start:.0f}s", flush=True)

            print(f"\nTranslating {len(needs_translation)} strings (concurrency={CONCURRENCY}, retry+backoff on 429)…", flush=True)
            await asyncio.gather(*[_translate_one(s) for s in needs_translation])
        print(f"Translation phase done. ok={completed-failed} failed={failed}")

    # ──────────────────────────────────────────────────────────────
    # 3. Write cache rows for every (entity, field) using the map
    # ──────────────────────────────────────────────────────────────
    rows_to_upsert: list[tuple] = []  # (entity_type, entity_id, field_name, src_hash, translated)

    def schedule(entity_type, entity_id, field_name, source: str, translated: str):
        if not source or not translated: return
        h = _hash_source(source.strip())
        existing_h = cached.get((entity_type, entity_id, TARGET_LANG, field_name))
        if existing_h == h:
            return  # already cached with current source hash
        rows_to_upsert.append((entity_type, entity_id, field_name, h, translated))

    # Lessons: scalar fields
    for l in lessons:
        if l["source_lang"] != "uz": continue
        for fld, strings in collect_lesson_field_strings(l).items():
            src = strings[0]
            tr = hash_to_translation.get(_hash_source(src.strip()))
            if tr: schedule("lesson", l["id"], fld, src, tr)
        # Lessons: sections_json blob — stitch translations back
        if l["sections_json"]:
            try:
                tree = json.loads(l["sections_json"])
            except Exception:
                continue
            pairs = []
            _collect_translatable_strings(tree, pairs)
            mutated = False
            for path, src in pairs:
                tr = hash_to_translation.get(_hash_source(src.strip()))
                if tr and tr.strip() != src.strip():
                    _set_at_path(tree, path, tr)
                    mutated = True
            if mutated:
                out = json.dumps(tree, ensure_ascii=False)
                schedule("lesson", l["id"], "sections_json", l["sections_json"], out)

    # Exercises: scalar fields
    for e in exercises:
        for fld, strings in collect_exercise_field_strings(e).items():
            src = strings[0]
            tr = hash_to_translation.get(_hash_source(src.strip()))
            if tr: schedule("exercise", e["id"], fld, src, tr)

    print(f"\nRows to upsert: {len(rows_to_upsert)}")
    if not rows_to_upsert:
        print("Everything already cached.")
        await engine.dispose()
        return

    UPSERT = text("""
        INSERT INTO translation_cache
          (entity_type, entity_id, lang, field_name, source_text_hash, translated_text, provider, created_at, updated_at)
        VALUES (:et, :eid, :lang, :fn, :h, :tr, 'openai', NOW(), NOW())
        ON CONFLICT (entity_type, entity_id, lang, field_name) DO UPDATE
          SET source_text_hash = EXCLUDED.source_text_hash,
              translated_text  = EXCLUDED.translated_text,
              updated_at       = NOW()
    """)
    # Commit in batches so a dropped connection only loses one batch.
    batch: list[dict] = []
    written = 0
    for i, (et, eid, fn, h, tr) in enumerate(rows_to_upsert, 1):
        batch.append({"et": et, "eid": eid, "lang": TARGET_LANG, "fn": fn, "h": h, "tr": tr})
        if len(batch) >= COMMIT_EVERY or i == len(rows_to_upsert):
            async with engine.begin() as conn:
                for params in batch:
                    await conn.execute(UPSERT, params)
            written += len(batch)
            batch = []
            print(f"  upserted {written}/{len(rows_to_upsert)}", flush=True)

    print(f"\nDone. Total time: {time.monotonic()-t_start:.0f}s")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
