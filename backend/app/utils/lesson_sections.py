"""Every lesson section needs a stable id.

The student page keys React blocks, the "Mundarija" jump links, the scroll-spy,
video-watch tracking and the progress maths on `section.id`. Lessons created by a
bulk import had sections with NO id at all (87 lessons in 13 courses), so every block
got the same `undefined` id: the table of contents could not jump anywhere and clicking
one block's header toggled them all.
"""
from __future__ import annotations

import json
from typing import Any, Optional


def section_id(lesson_id: int, index: int) -> str:
    """The id given to a section that has none. Deterministic, so every reader (API, page, DB repair) agrees."""
    return f"s{lesson_id}-{index}"


def ensure_section_ids(lesson_id: int, sections_json: Optional[str]) -> tuple[Optional[str], bool]:
    """(sections_json with an id on every section, whether anything changed).

    Existing ids are kept; a missing/blank id — or a duplicate of an earlier section's id —
    gets `s{lesson_id}-{index}`. Anything that is not a JSON list of objects is returned untouched.
    """
    if not sections_json:
        return sections_json, False
    try:
        sections: Any = json.loads(sections_json)
    except (TypeError, ValueError):
        return sections_json, False
    if not isinstance(sections, list):
        return sections_json, False

    changed, seen = False, set()
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            continue
        sid = sec.get("id")
        if sid in (None, "") or str(sid) in seen:
            sec["id"] = section_id(lesson_id, i)
            changed = True
        seen.add(str(sec["id"]))
    return (json.dumps(sections, ensure_ascii=False) if changed else sections_json), changed
