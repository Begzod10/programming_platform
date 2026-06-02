"""Fetch a code snapshot for AI grading. Two backends, one output shape:

  fetch_github_snapshot(url)  — public GitHub repo via REST API
  fetch_zip_snapshot(file_url) — student-uploaded ZIP on local disk

Both return the same dict so the AI-review endpoint can dispatch transparently.
Output is byte-capped (MAX_REPO_BYTES) so it stays inside the LLM context
window and OpenAI cost stays predictable.

GitHub backend:
  1) GET /repos/{owner}/{repo}                — exists check + default_branch
  2) GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1  — file list
  3) Up to MAX_FILES Contents API calls (one per kept file).
  Auth header attached when settings.GITHUB_TOKEN is set; falls back to the
  60-req/hr/IP anonymous tier otherwise.

ZIP backend:
  Reads via zipfile.ZipFile against PROJECTS_UPLOAD_DIR. Per-entry file_size
  cap defends against zip bombs (we decompress in-memory, never extract).
  Path-traversal patterns in member names are rejected even though we read
  by ZipInfo (defense in depth).
"""
from __future__ import annotations

import base64
import re
import zipfile
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings


PROJECTS_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "projects"


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


def _empty_authorship(reason: str = "") -> dict:
    """Authorship dict shape returned when we can't read git history."""
    return {
        "available": False,
        "reason": reason or "git history not available",
        "is_fork": False,
        "parent_repo": None,
        "commit_count": None,
        "commit_count_capped": False,
        "unique_authors": None,
        "owner_is_contributor": None,
        "first_commit_at": None,
        "last_commit_at": None,
    }


def _empty(error: str) -> dict:
    return {
        "exists": False,
        "default_branch": "",
        "file_count": 0,
        "files_included": [],
        "content_text": "",
        "truncated": False,
        "error": error,
        "authorship": _empty_authorship("snapshot failed"),
    }


async def _fetch_authorship(
        client: httpx.AsyncClient, owner: str, repo: str, meta_json: dict,
) -> dict:
    """Read git-history signals that help detect copy-paste / forks.

    Cheap: one extra Contents-API equivalent call (commits?per_page=100).
    Fork detection is free (already in the meta payload we have).
    """
    out: dict = {
        "available": True,
        "reason": None,
        "is_fork": bool(meta_json.get("fork")),
        "parent_repo": None,
        "commit_count": None,
        "commit_count_capped": False,
        "unique_authors": None,
        "owner_is_contributor": None,
        "first_commit_at": None,
        "last_commit_at": None,
    }
    if out["is_fork"]:
        parent = meta_json.get("parent") or {}
        out["parent_repo"] = parent.get("full_name")

    try:
        resp = await _gh_get(
            client,
            f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100",
        )
    except (httpx.TimeoutException, httpx.HTTPError):
        return _empty_authorship("commits fetch failed")

    if resp.status_code == 409:
        # Empty repo (no commits yet). Still authoritative — record zero.
        out["commit_count"] = 0
        out["unique_authors"] = 0
        out["owner_is_contributor"] = False
        return out
    if resp.status_code != 200:
        return _empty_authorship(f"commits HTTP {resp.status_code}")

    commits = resp.json()
    if not isinstance(commits, list):
        return _empty_authorship("commits response shape")

    # GitHub returns a Link header with rel="next" when there are >100 commits.
    has_more = 'rel="next"' in resp.headers.get("link", "")
    out["commit_count"] = len(commits)
    out["commit_count_capped"] = has_more

    authors: set[str] = set()
    for c in commits:
        # Prefer the linked GH user login (authoritative); fall back to
        # the raw commit author email when GitHub can't resolve the user.
        login = ((c.get("author") or {}) or {}).get("login")
        if login:
            authors.add(login.lower())
            continue
        email = (((c.get("commit") or {}).get("author") or {}) or {}).get("email")
        if email:
            authors.add(email.lower())

    out["unique_authors"] = len(authors)
    # `owner_is_contributor` only makes sense when the owner is a real user.
    # Organizations (helloflask, pallets, ...) never appear in commit author
    # lists because authors are individuals — checking "owner in authors"
    # would always false-positive and unfairly penalize legit org repos.
    # For student projects the URL owner IS the student's user account, so
    # the check still catches the intended case: someone else's commits in
    # a repo the student claims to have written.
    owner_type = (meta_json.get("owner") or {}).get("type") or "User"
    if owner_type == "Organization":
        out["owner_is_contributor"] = None  # not applicable, frontend hides badge
    else:
        out["owner_is_contributor"] = owner.lower() in authors

    if commits:
        # GitHub returns commits newest-first.
        last = ((commits[0].get("commit") or {}).get("author") or {}).get("date")
        first = ((commits[-1].get("commit") or {}).get("author") or {}).get("date")
        out["last_commit_at"] = last
        out["first_commit_at"] = first

    return out


async def fetch_github_snapshot(github_url: str) -> dict:
    """Fetch a byte-capped snapshot of a public GitHub repo for LLM context.

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

            # Authorship signals (fork / commit count / unique authors). Fetched
            # alongside the snapshot because they share the same auth tokens
            # and rate-limit budget. Always returned, even on partial failure.
            authorship = await _fetch_authorship(client, owner, repo, meta_json)

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
                "authorship": authorship,
            }
    except httpx.TimeoutException:
        return _empty("GitHub fetch timed out")
    except httpx.HTTPError as e:
        return _empty(f"GitHub fetch failed: {type(e).__name__}")


# ─────────────────────────────────────────────────────────────────────────────
# ZIP backend — student-uploaded archive on local disk
# ─────────────────────────────────────────────────────────────────────────────

# Refuse to read any single ZIP entry whose declared uncompressed size is
# larger than this. Defense against zip bombs (e.g. 10 KB ZIP that expands
# to 10 GB). 32 KB is 4x our per-file truncation cap, which is plenty of
# headroom for any real source file we'd want to grade.
MAX_ZIP_ENTRY_BYTES = 4 * MAX_FILE_BYTES


def _is_zip_path_unsafe(name: str) -> bool:
    """Reject path-traversal patterns in ZIP member names.

    We never extract to disk (only `zf.read(zi)`), so this is defense in
    depth. The bigger concern is that crafted names like `../../etc/passwd`
    end up in the prompt or logs, which is misleading and noisy.
    """
    if not name:
        return True
    if name.startswith("/") or name.startswith("\\"):
        return True
    parts = name.replace("\\", "/").split("/")
    if ".." in parts:
        return True
    # Windows-style absolute path: "C:\..."
    if len(name) >= 2 and name[1] == ":":
        return True
    return False


def _resolve_zip_path(project_files_url: str) -> Optional[Path]:
    """Map project.project_files (URL form) to an absolute on-disk path.

    Only the basename is used — Path(...).name strips any directory
    components, so a crafted `project_files = "/etc/passwd"` reduces to
    `passwd`, which then fails the `.zip` extension check below.
    """
    if not project_files_url:
        return None
    name = Path(project_files_url).name
    if not name.endswith(".zip"):
        return None
    path = PROJECTS_UPLOAD_DIR / name
    if not path.exists() or not path.is_file():
        return None
    return path


def fetch_zip_snapshot(project_files_url: str) -> dict:
    """Read a byte-capped snapshot from a student-uploaded ZIP.

    Same return shape as fetch_github_snapshot. `default_branch` is set
    to "(zip)" so the LLM prompt clearly distinguishes the source.
    """
    path = _resolve_zip_path(project_files_url)
    if path is None:
        return _empty("ZIP fayl topilmadi yoki yo'l noto'g'ri")

    try:
        with zipfile.ZipFile(path) as zf:
            # ZipFile.testzip() catches CRC errors. Skipped for speed —
            # individual zf.read() calls below will surface corruption.
            entries = [
                zi for zi in zf.infolist()
                if not zi.is_dir() and not _is_zip_path_unsafe(zi.filename)
            ]
            file_count = len(entries)
            if file_count == 0:
                return _empty("ZIP fayl bo'sh yoki o'qiladigan fayllar yo'q")

            candidates = [zi for zi in entries if not _should_skip(zi.filename)]
            candidates.sort(key=lambda zi: (_priority_score(zi.filename), zi.filename))
            picked = candidates[:MAX_FILES]

            blocks: list[str] = []
            included: list[str] = []
            total_bytes = 0
            truncated = False
            for zi in picked:
                if total_bytes >= MAX_REPO_BYTES:
                    truncated = True
                    break
                # Zip-bomb guard: refuse to decompress oversized entries.
                # file_size is the declared uncompressed size in the header.
                if zi.file_size > MAX_ZIP_ENTRY_BYTES:
                    continue
                try:
                    raw = zf.read(zi)
                except (zipfile.BadZipFile, KeyError, RuntimeError):
                    # RuntimeError fires for encrypted entries (no password).
                    continue

                try:
                    text = raw.decode("utf-8", errors="replace")
                except Exception:
                    continue

                if len(text) > MAX_FILE_BYTES:
                    text = text[:MAX_FILE_BYTES] + "\n... [truncated]"
                    truncated = True

                if total_bytes + len(text) + 50 > MAX_REPO_BYTES:
                    remaining = MAX_REPO_BYTES - total_bytes - 50
                    if remaining < 200:
                        truncated = True
                        break
                    text = text[:remaining] + "\n... [truncated]"
                    truncated = True

                blocks.append(f"### {zi.filename}\n```\n{text}\n```")
                included.append(zi.filename)
                total_bytes += len(text) + 50

            if not blocks:
                return _empty(
                    "ZIP'da o'qiladigan kod fayli yo'q (faqat rasm/binar yoki "
                    "barchasi juda katta)"
                )

            return {
                "exists": True,
                "default_branch": "(zip)",
                "file_count": file_count,
                "files_included": included,
                "content_text": "\n\n".join(blocks),
                "truncated": truncated,
                "error": None,
                # ZIP uploads don't carry git history. The prompt will tell
                # the AI to weight code quality more heavily as a result.
                "authorship": _empty_authorship("ZIP upload — no git history"),
            }
    except zipfile.BadZipFile:
        return _empty("ZIP fayl buzuq yoki noto'g'ri format")
    except Exception as e:
        return _empty(f"ZIP o'qishda xato: {type(e).__name__}")
