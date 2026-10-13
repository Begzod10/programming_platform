"""Pure (DB-free) heuristic shared by the builder and the spec lint: does a fill-in/text answer need a RU translation?"""
from __future__ import annotations

import re
from typing import Optional

_CODE_LIKE_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.]*$"
    r"|^[A-Za-z0-9_\-]+\(.*\)$"
    r"|[<>{}();=]"
)


def is_natural_language_answer(answer: Optional[str]) -> bool:
    """True if `answer` looks like a real word/phrase worth a RU
    translation, False if it looks like a code/technical token that must
    stay literal in every language. Same heuristic check_ru_coverage.py
    uses to decide whether a missing correct_answers translation is a real
    gap — kept here too so spec authors (and the lint) can call it while
    writing content, not just discover a mismatch after the fact.

    Note: command-line flags such as "-a" or "--from" are NOT recognised as
    code, so they need an explicit correct_answers_ru (the same value)."""
    a = (answer or "").strip()
    if not a or len(a) > 40:
        return False
    if _CODE_LIKE_PATTERN.search(a):
        return False
    if a.isupper() or a.isdigit():
        return False
    return any(c.isalpha() for c in a)
