"""Fetch a snapshot of a public GitHub repo so the LLM can grade the actual
code instead of hallucinating from the title.

Two HTTP calls per snapshot:
  1) GET /repos/{owner}/{repo}                — exists check + default_branch
  2) GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1  — full file list

Then up to MAX_FILES Contents API calls (one per file kept). Auth header is
attached when settings.GITHUB_TOKEN is set; otherwise we fall back to the
60-req/hr/IP anonymous tier and surface a clear error if rate-limited.

Output is byte-capped (MAX_REPO_BYTES) so it stays well inside the LLM
context window and OpenAI cost stays predictable.
"""
from __future__ import annotations

import base64
import re
from typing import Optional

import httpx

from app.config import settings


# Same shape as the regex in ai_review.py — accept owner/repo and an optional
# /tree/<branch> suffix. Branch may itself contain slashes (feature/foo).
_GITHUB_URL_RE = re.compile(
    r"^https://github\.com/"
    r"(?P<owner>[A-Za-z0-9_.\-]+)/"
    r"(?P<repo>[A-Za-z0-9_.\-]+)"
    r"/?"
    r"(?:tree/(?P<branch>[A-Za-z0-9_./\-]+))?"
    r"/?$"
)

MAX_REPO_BYTES = 25_000     # ~6-7K tokens — keeps prompt under gpt-4o-mini ctx
MAX_FILES = 12              # hard cap on files included in the snapshot
MAX_FILE_BYTES = 8_000      # any single file truncated to this many bytes
REQUEST_TIMEOUT = 20.0      # per-call HTTP timeout

# Skip noise paths regardless of priority match.
_SKIP_DIR_FRAGMENTS = (
    ".git/", "__pycache__/", "node_modules/", "venv/", ".venv/",
    "migrations/", "alembic/versions/", ".idea/", ".vscode/", ".pytest_cache/",
    "dist/", "build/", ".next/", "coverage/",
)
_SKIP_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".zip", ".tar", ".gz", ".tgz", ".rar",
    ".pdf", ".woff", ".woff2", ".ttf", ".eot",
    ".lock",
)

# Higher tier = read first. Within a tier we keep tree order for determinism.
_PRIORITY_TIERS: tuple[tuple[str, ...], ...] = (
    # Tier 0: project manifest / docs the LLM should see first
    ("readme.md", "readme", "readme.rst",
     "requirements.txt", "pyproject.toml", "package.json",
     "procfile", "runtime.txt", "dockerfile", ".env.example"),
    # Tier 1: app entrypoints
    ("app.py", "main.py", "run.py", "manage.py", "wsgi.py", "asgi.py",
     "server.py", "index.py"),
    # Tier 2: config + settings + factory
    ("config.py", "settings.py", "__init__.py"),
    # Tier 3: models / routes / blueprints (matched by suffix)
    ("models.py", "routes.py", "views.py", "forms.py", "urls.py"),
)


def parse_github_url(url: str) -> Optional[tuple[str, str, Optional[str]]]:
    """Return (owner, repo, branch_or_None) or None if URL doesn't match."""
    m = _GITHUB_URL_RE.match((url or "").strip())
    if not m:
        return None
    owner = m.group("owner")
    repo = m.group("repo")
    # Strip a trailing ".git" so https://github.com/x/y.git also works.
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo, m.group("branch")


def _should_skip(path: str) -> bool:
    lower = path.lower()
    if lower.startswith("."):
        return True
    if any(frag in lower for frag in _SKIP_DIR_FRAGMENTS):
        return True
    if any(lower.endswith(ext) for ext in _SKIP_EXTENSIONS):
        return True
    return False


def _priority_score(path: str) -> int:
    """Lower is better. Used to sort the file list before picking the top N."""
    name = path.rsplit("/", 1)[-1].lower()
    full = path.lower()
    for tier_idx, names in enumerate(_PRIORITY_TIERS):
        if name in names:
            return tier_idx
    # Tier 4: HTML templates anywhere
    if full.endswith(".html"):
        return 4
    # Tier 5: any python source in top two levels
    if full.endswith(".py") and full.count("/") <= 2:
        return 5
    # Tier 6: anything else worth reading (text by extension)
    if full.endswith((".js", ".ts", ".css", ".md", ".yml", ".yaml", ".toml", ".sh")):
        return 6
    return 9  # unknown / low value


async def _gh_get(client: httpx.AsyncClient, url: str) -> httpx.Response:
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    return await client.get(url, headers=headers)


def _empty(error: str) -> dict:
    return {
        "exists": False,
        "default_branch": "",
        "file_count": 0,
        "files_included": [],
        "content_text": "",
        "truncated": False,
        "error": error,
    }


async def fetch_repo_snapshot(github_url: str) -> dict:
    """Fetch a byte-capped snapshot of the repo for LLM context.

    Returns a dict with keys: exists, default_branch, file_count,
    files_included (list of paths actually included), content_text
    (formatted markdown blocks), truncated (True if hit byte cap),
    error (str or None).
    """
    parsed = parse_github_url(github_url)
    if not parsed:
        return _empty("Invalid GitHub URL")
    owner, repo, branch_hint = parsed

    proxy = settings.HTTP_PROXY or None
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, proxy=proxy,
                                     follow_redirects=True) as client:
            # 1) Repo metadata: confirm exists + resolve default branch
            meta = await _gh_get(client, f"https://api.github.com/repos/{owner}/{repo}")
            if meta.status_code == 404:
                return _empty("Repo not found or private")
            if meta.status_code == 403:
                # Rate-limit headers may be empty for proxy-injected 403s
                return _empty("GitHub rate limit reached — try again later")
            if meta.status_code >= 500:
                return _empty(f"GitHub API {meta.status_code}")
            if meta.status_code != 200:
                return _empty(f"GitHub API returned {meta.status_code}")

            meta_json = meta.json()
            default_branch = branch_hint or meta_json.get("default_branch") or "main"

            # 2) Recursive tree of the chosen branch
            tree_resp = await _gh_get(
                client,
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/"
                f"{default_branch}?recursive=1",
            )
            if tree_resp.status_code == 404:
                # Branch hint was wrong — retry on default if we had a hint
                if branch_hint and branch_hint != meta_json.get("default_branch"):
                    default_branch = meta_json.get("default_branch") or "main"
                    tree_resp = await _gh_get(
                        client,
                        f"https://api.github.com/repos/{owner}/{repo}/git/trees/"
                        f"{default_branch}?recursive=1",
                    )
                if tree_resp.status_code != 200:
                    return _empty("Branch tree not found")
            if tree_resp.status_code != 200:
                return _empty(f"Tree fetch failed ({tree_resp.status_code})")

            tree_json = tree_resp.json()
            entries = [e for e in tree_json.get("tree", []) if e.get("type") == "blob"]
            file_count = len(entries)
            if file_count == 0:
                return _empty("Repo is empty (no files)")

            # Filter + sort by priority, then pick MAX_FILES
            candidates = [e for e in entries if not _should_skip(e["path"])]
            candidates.sort(key=lambda e: (_priority_score(e["path"]), e["path"]))
            picked = candidates[:MAX_FILES]

            # 3) Fetch contents for each picked file (one Contents API call each)
            blocks: list[str] = []
            included: list[str] = []
            total_bytes = 0
            truncated = False
            for entry in picked:
                if total_bytes >= MAX_REPO_BYTES:
                    truncated = True
                    break
                path = entry["path"]
                content_resp = await _gh_get(
                    client,
                    f"https://api.github.com/repos/{owner}/{repo}/contents/"
                    f"{path}?ref={default_branch}",
                )
                if content_resp.status_code != 200:
                    continue
                content_json = content_resp.json()
                if content_json.get("encoding") != "base64":
                    continue
                try:
                    raw = base64.b64decode(content_json.get("content", ""))
                    text = raw.decode("utf-8", errors="replace")
                except Exception:
                    continue

                if len(text) > MAX_FILE_BYTES:
                    text = text[:MAX_FILE_BYTES] + "\n... [truncated]"
                    truncated = True

                # Reserve the trailing fence + header overhead (~50 bytes)
                if total_bytes + len(text) + 50 > MAX_REPO_BYTES:
                    remaining = MAX_REPO_BYTES - total_bytes - 50
                    if remaining < 200:
                        truncated = True
                        break
                    text = text[:remaining] + "\n... [truncated]"
                    truncated = True

                blocks.append(f"### {path}\n```\n{text}\n```")
                included.append(path)
                total_bytes += len(text) + 50

            return {
                "exists": True,
                "default_branch": default_branch,
                "file_count": file_count,
                "files_included": included,
                "content_text": "\n\n".join(blocks),
                "truncated": truncated,
                "error": None,
            }
    except httpx.TimeoutException:
        return _empty("GitHub fetch timed out")
    except httpx.HTTPError as e:
        return _empty(f"GitHub fetch failed: {type(e).__name__}")
