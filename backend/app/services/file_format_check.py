"""Does a submitted file's content match its extension? (Python code saved as "x.html", HTML in "style.css", ...)

Found by scanning 4478 uploaded lesson ZIPs: 13 students, 74 projects (33 of them one student's Python in .html
files), all approved because the grader reads the code, not the file name. The student is never told and the next
lesson repeats it. This module only DETECTS; callers warn (the upload response, the AI feedback) and never block.

Detection is deliberately strict: one language must clearly dominate the file (at least 4 signals and twice the
runner-up), only .html / .css / .js are checked, and dependency folders are skipped. A miss is cheap, a false
accusation is not.
"""
from __future__ import annotations

import io
import os
import re
import zipfile
from typing import Iterable, Optional

_SKIP_PATH = re.compile(r"(^|/)(venv|\.venv|node_modules|site-packages|__MACOSX|\.git)/", re.I)
_MAX_FILES = 300
_MAX_READ = 200_000
_BLOCK_RE = re.compile(r"^### (.+?)\n```\n(.*?)\n```", re.S | re.M)

_TAG = re.compile(r"<\s*/?\s*(?:html|head|body|div|span|p|a|img|h[1-6]|ul|li|table|tr|td|form|input|button|section|nav|link|meta|title|style|script)\b", re.I)
_CSS = re.compile(r"[.#]?[\w\-\s,>:+~\[\]=\"']+\{\s*[\w\-]+\s*:[^{}]*\}")
_PY = re.compile(r"^\s*(?:def \w+\(.*\):|class \w+.*:|import \w+|from [\w.]+ import|print\(|if __name__|elif .*:|for \w+ in .*:|while .*:)", re.M)
_JS = re.compile(r"\b(?:function\s+\w*\(|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|=>\s*[{(\w]|console\.log|document\.(?:getElementById|querySelector)|addEventListener)")

# (extension, what the content looks like) -> the extension that would fit
_MISMATCHES = {
    (".html", "python"): ".py", (".css", "html"): ".html", (".js", "html"): ".html",
    (".css", "python"): ".py", (".js", "python"): ".py",
}
_LANG_UZ = {"python": "Python", "html": "HTML"}
_LANG_RU = {"python": "Python", "html": "HTML"}


def detect_language(text: str) -> Optional[str]:
    """'html' | 'css' | 'python' | 'js' when one language clearly dominates the text, else None."""
    t = (text or "")[:20000]
    scores = {"html": len(_TAG.findall(t)), "css": 2 * len(_CSS.findall(t)),
              "python": 2 * len(_PY.findall(t)), "js": len(_JS.findall(t))}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    (kind, top), (_, second) = ranked[0], ranked[1]
    return kind if top >= 4 and top >= 2 * second else None


def format_warnings(files: Iterable[tuple[str, str]]) -> list[dict]:
    """Warnings for (path, text) pairs: [{file, extension, detected, suggested, message, message_ru}]."""
    out: list[dict] = []
    for path, text in files:
        if _SKIP_PATH.search(path or ""):
            continue
        ext = os.path.splitext((path or "").lower())[1]
        if ext not in (".html", ".css", ".js"):
            continue
        kind = detect_language(text)
        suggested = _MISMATCHES.get((ext, kind))
        if not suggested:
            continue
        name = path.rsplit("/", 1)[-1]
        out.append({
            "file": path, "extension": ext, "detected": kind, "suggested": suggested,
            "message": f"«{name}» fayli {ext} deb nomlangan, lekin ichida {_LANG_UZ[kind]} kodi bor. "
                       f"Fayl kengaytmasini {suggested} qilib o'zgartiring.",
            "message_ru": f"Файл «{name}» назван {ext}, но внутри код {_LANG_RU[kind]}. "
                          f"Измените расширение файла на {suggested}.",
        })
    return out


def zip_format_warnings(contents: bytes) -> list[dict]:
    """Warnings for an uploaded ZIP; an unreadable archive simply has none (other checks reject it)."""
    try:
        with zipfile.ZipFile(io.BytesIO(contents)) as zf:
            pairs = []
            for zi in zf.infolist()[:_MAX_FILES]:
                if zi.is_dir() or zi.file_size == 0 or zi.file_size > 5_000_000:
                    continue
                if os.path.splitext(zi.filename.lower())[1] not in (".html", ".css", ".js"):
                    continue
                pairs.append((zi.filename, zf.read(zi)[:_MAX_READ].decode("utf-8", "ignore")))
            return format_warnings(pairs)
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return []


def snapshot_format_warnings(snapshot: Optional[dict]) -> list[dict]:
    """Warnings for a repo/ZIP snapshot as the grader sees it ("### path" + fenced content blocks)."""
    return format_warnings(_BLOCK_RE.findall((snapshot or {}).get("content_text") or ""))


def apply_to_review(review: dict, warnings: list[dict]) -> None:
    """Tell the student in the review itself. The score is untouched: the code may be fine, the name is what is wrong."""
    if not warnings or not isinstance(review, dict):
        return
    lines = [w["message"] for w in warnings[:5]]
    more = len(warnings) - len(lines)
    if more > 0:
        lines.append(f"Yana {more} ta shunday fayl bor.")
    improvements = list(review.get("improvements") or [])
    improvements.extend(lines)
    review["improvements"] = improvements
    note = "⚠️ Fayl formati:\n" + "\n".join(f"• {line}" for line in lines)
    review["feedback"] = f"{(review.get('feedback') or '').rstrip()}\n\n{note}".strip()
    review["format_warnings"] = warnings
