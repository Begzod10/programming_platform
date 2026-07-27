"""Verify (and optionally set) a course's image_url/thumbnail_url.

Why this exists: a platform audit this session found 16 courses with no
image_url/thumbnail_url at all, and 14 more whose stored URL pointed at a
dead/renamed asset (mostly stale Wikimedia thumbnail paths that had been
regenerated server-side with a different width segment) — the course card
rendered a broken image to students. Both classes of bug are checked here.

Two modes:
  1. Check (default) — for one/more/all courses, verify image_url and
     thumbnail_url are both set AND both resolve with a live HTTP request
     (not just "looks like a URL"). Reports what's missing/dead.
  2. Set — for one course, verify the given URL(s) resolve BEFORE writing
     them to the DB, so a course-building script can't silently persist a
     dead link the way the original 14 did.

Usage:
    cd backend
    python scripts/check_course_images.py <course_id> [<course_id> ...]
    python scripts/check_course_images.py --all
    python scripts/check_course_images.py --set <course_id> --image <url> [--thumbnail <url>]

Exit code 0 = no problems (check mode) / write succeeded (set mode),
1 = problems found / a given URL didn't resolve.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402

_TIMEOUT = 10.0
# Several image hosts (icon-icons.com confirmed; likely others) return 403
# to requests with no User-Agent or a bare httpx/curl one, but serve fine to
# an actual browser <img> tag — which is what students' pages really send.
# Without this header the checker false-flags perfectly working images.
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


async def _url_resolves(client: httpx.AsyncClient, url: str) -> tuple[bool, str]:
    """True + status if the URL returns a usable response; False + reason otherwise."""
    if not url or not url.strip():
        return False, "empty"
    if url.startswith("/"):
        # Relative path served by our own backend (uploaded file) — can't
        # verify without knowing the base URL/host; treat as "assumed ok"
        # rather than false-flagging every locally-uploaded course image.
        return True, "relative path (assumed served by backend, not checked)"
    try:
        resp = await client.head(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
        if resp.status_code == 405 or resp.status_code >= 400:
            # Some hosts (e.g. icons8, some CDNs) reject HEAD; retry with GET
            # before concluding it's actually dead.
            resp = await client.get(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
        if resp.status_code < 400:
            return True, str(resp.status_code)
        return False, f"HTTP {resp.status_code}"
    except httpx.HTTPError as e:
        return False, f"request failed: {e}"


async def check_course(client: httpx.AsyncClient, course: Course) -> list[str]:
    problems: list[str] = []
    for field in ("image_url", "thumbnail_url"):
        url = getattr(course, field)
        if not url or not url.strip():
            problems.append(f"course {course.id} ({course.title!r}): {field} is empty")
            continue
        ok, detail = await _url_resolves(client, url)
        if not ok:
            problems.append(
                f"course {course.id} ({course.title!r}): {field} does not resolve ({detail}): {url}"
            )
    return problems


async def run_check(course_ids: list[int] | None) -> int:
    async with AsyncSessionLocal() as db, httpx.AsyncClient() as client:
        if course_ids is None:
            course_ids = list((await db.execute(select(Course.id))).scalars().all())

        courses = (await db.execute(select(Course).where(Course.id.in_(course_ids)))).scalars().all()
        by_id = {c.id: c for c in courses}

        any_problems = False
        for cid in course_ids:
            course = by_id.get(cid)
            if not course:
                print(f"course {cid}: does not exist")
                any_problems = True
                continue
            problems = await check_course(client, course)
            if problems:
                any_problems = True
                print(f"\n=== course {cid} ({course.title!r}): {len(problems)} problem(s) ===")
                for p in problems:
                    print(p)
            else:
                print(f"course {cid} ({course.title!r}): OK — image_url and thumbnail_url both resolve")

    await engine.dispose()
    return 1 if any_problems else 0


async def run_set(course_id: int, image_url: str | None, thumbnail_url: str | None) -> int:
    async with AsyncSessionLocal() as db, httpx.AsyncClient() as client:
        course = (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none()
        if not course:
            print(f"course {course_id}: does not exist")
            return 1

        to_set = {}
        for field, url in (("image_url", image_url), ("thumbnail_url", thumbnail_url)):
            if url is None:
                continue
            ok, detail = await _url_resolves(client, url)
            if not ok:
                print(f"REFUSED: {field} does not resolve ({detail}), not writing: {url}")
                return 1
            to_set[field] = url
            print(f"verified {field} ({detail}): {url}")

        if not to_set:
            print("nothing to set — pass --image and/or --thumbnail")
            return 1

        for field, url in to_set.items():
            setattr(course, field, url)
        await db.commit()
        print(f"course {course_id} ({course.title!r}): updated {list(to_set.keys())}")

    await engine.dispose()
    return 0


def _parse_args(argv: list[str]):
    if not argv:
        print(__doc__)
        sys.exit(2)
    if argv[0] == "--all":
        return ("check", None)
    if argv[0] == "--set":
        rest = argv[1:]
        if not rest or not rest[0].isdigit():
            print("usage: --set <course_id> --image <url> [--thumbnail <url>]")
            sys.exit(2)
        course_id = int(rest[0])
        image_url = None
        thumbnail_url = None
        i = 1
        while i < len(rest):
            if rest[i] == "--image" and i + 1 < len(rest):
                image_url = rest[i + 1]
                i += 2
            elif rest[i] == "--thumbnail" and i + 1 < len(rest):
                thumbnail_url = rest[i + 1]
                i += 2
            else:
                i += 1
        return ("set", (course_id, image_url, thumbnail_url))
    return ("check", [int(a) for a in argv])


if __name__ == "__main__":
    mode, payload = _parse_args(sys.argv[1:])
    if mode == "check":
        sys.exit(asyncio.run(run_check(payload)))
    else:
        course_id, image_url, thumbnail_url = payload
        sys.exit(asyncio.run(run_set(course_id, image_url, thumbnail_url)))
