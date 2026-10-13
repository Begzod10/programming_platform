"""Lint a course spec BEFORE it touches the database.

A spec (see course_specs/_example.py) holds every UZ field with a `*_ru` sibling. The builder used to
write whatever it was given, so gaps surfaced months later (1,371 exercises without RU, courses without
`title_ru`, 64% of exercises without an explanation). This module is pure — dicts in, messages out — so it
runs in `build_course --dry-run` and in tests.

Errors stop the build. Warnings (code parity between languages, requirements that lean on something the
course never taught) are shown but do not.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Optional

from course_builder.glossary import forbidden_ru_terms

CYRILLIC = re.compile(r"[а-яёА-ЯЁ]")
TAGS = re.compile(r"<[^>]+>")
PRE = re.compile(r"<pre(?![^>]*mermaid)[^>]*>(.*?)</pre>", re.S | re.I)
MIN_LESSON_TEXT = 300
MIN_EXERCISES = 5
MIN_EXERCISE_TYPES = 3
TASK_FIELDS = ("task_title", "task_description", "task_requirements")
TYPES = ("multiple_choice", "fill_in_blank", "drag_and_drop", "text_input")


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _plain(value: Optional[str]) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAGS.sub(" ", value or ""))).strip()


def _natural(value: Optional[str]) -> bool:
    """Prose (needs a real translation) vs a code token / identifier (identical in both languages)."""
    return len(re.findall(r"[^\W\d_]{3,}", _plain(value))) >= 3


def _ru_problem(uz: Optional[str], ru: Optional[str], label: str) -> Optional[str]:
    if not (uz or "").strip():
        return None
    if not (ru or "").strip():
        return f"{label}: RU counterpart is missing"
    bad = forbidden_ru_terms(ru)
    if bad:
        wrong, right = bad[0]
        return f"{label}: use the glossary term '{right}' instead of '{wrong}'"
    if not _natural(uz):
        return None
    if _plain(ru) == _plain(uz):
        return f"{label}: RU is identical to UZ (not translated)"
    if not CYRILLIC.search(_plain(ru)):
        return f"{label}: RU has no Cyrillic text"
    return None


def _code_lines(markup: Optional[str]) -> list[str]:
    lines: list[str] = []
    for block in PRE.findall(markup or ""):
        for raw in html.unescape(TAGS.sub("", block)).splitlines():
            line = re.split(r"\s{2,}(?:#|//|--)\s", raw.rstrip())[0].strip()
            if line and not line.startswith(("#", "//", "--", "/*", "*")):
                lines.append(line)
    return lines


def _words(text: str) -> set[str]:
    """Every word of the taught text, lowercased (what the course actually discussed)."""
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_.@:-]+", text or "")}


def _tech_tokens(text: str) -> set[str]:
    """Technology-looking tokens of a requirement: `backticked` code, CamelCase / ALLCAPS / digits /
    symbols, and capitalised words in mid-sentence (product names: Redis, Docker). Uzbek prose is Latin
    script too, so plain lowercase words must NOT count — they would all be flagged."""
    found: set[str] = set()
    for code in re.findall(r"`([^`]+)`", text or ""):
        found.update(t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_.@:-]{2,}", code))
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9_.@:-]{2,}", re.sub(r"`[^`]*`", " ", text or "")):
        word, start = m.group(0).rstrip(".:-@_"), m.start()
        if len(word) < 3:
            continue
        sentence_start = not (text or "")[:start].strip() or (text or "")[:start].rstrip().endswith((".", "!", "?", ":", "\n"))
        techy = bool(re.search(r"[A-Z0-9_.@:-]", word[1:])) or (word[0].isupper() and not sentence_start)
        if techy:
            found.add(word.lower())
    return found


def _lint_exercise(ex: dict, where: str, out: LintResult) -> None:
    kind = ex.get("exercise_type")
    if kind not in TYPES:
        out.errors.append(f"{where}: exercise_type must be one of {', '.join(TYPES)} (got {kind!r})")
        return
    for key in ("title", "description"):
        if not (ex.get(key) or "").strip():
            out.errors.append(f"{where}: '{key}' is missing")
        if (msg := _ru_problem(ex.get(key), ex.get(f"{key}_ru"), f"{where}.{key}_ru")):
            out.errors.append(msg)
    if not (ex.get("hint") or "").strip():
        out.errors.append(f"{where}: 'hint' is missing (every exercise needs a hint)")
    elif (msg := _ru_problem(ex.get("hint"), ex.get("hint_ru"), f"{where}.hint_ru")):
        out.errors.append(msg)
    if not (ex.get("explanation") or "").strip():
        out.errors.append(f"{where}: 'explanation' is missing (UZ only — it is the grading context)")

    if kind == "multiple_choice":
        options = ex.get("options") or []
        if len(options) < 2:
            out.errors.append(f"{where}: multiple_choice needs at least 2 options")
        ru = ex.get("options_ru")
        if ru is None:
            out.errors.append(f"{where}: options_ru is missing")
        elif len(ru) != len(options):
            out.errors.append(f"{where}: options_ru length ({len(ru)}) differs from options ({len(options)})")
        letters = "ABCDEFGH"[: len(options)]
        answers = [a.strip().upper() for a in str(ex.get("correct_answers") or "").split(",") if a.strip()]
        if not answers or any(a not in letters for a in answers):
            out.errors.append(f"{where}: correct_answers {ex.get('correct_answers')!r} must be letters within {letters or 'the options'}")
    elif kind == "drag_and_drop":
        items, order = ex.get("drag_items") or [], ex.get("correct_order") or []
        if sorted(items) != sorted(order) or not items:
            out.errors.append(f"{where}: correct_order must be a permutation of drag_items")
        ru = ex.get("drag_items_ru")
        if ru is None:
            out.errors.append(f"{where}: drag_items_ru is missing")
        elif len(ru) != len(items):
            out.errors.append(f"{where}: drag_items_ru length ({len(ru)}) differs from drag_items ({len(items)})")
    elif kind == "fill_in_blank":
        if (ex.get("description") or "").count("___") != 1:
            out.errors.append(f"{where}: fill_in_blank description needs exactly one blank (___)")
        if not str(ex.get("correct_answers") or "").strip():
            out.errors.append(f"{where}: correct_answers is missing")
    elif kind == "text_input" and not (ex.get("expected_answer") or "").strip():
        out.errors.append(f"{where}: expected_answer is missing (the AI grading rubric)")


def lint_spec(course: dict, lessons: list[dict]) -> LintResult:
    out = LintResult()
    course = course or {}
    for key in ("title", "description"):
        if not (course.get(key) or "").strip():
            out.errors.append(f"course: '{key}' is missing")
        if (msg := _ru_problem(course.get(key), course.get(f"{key}_ru"), f"course.{key}_ru")):
            out.errors.append(msg)
    if not lessons:
        out.errors.append("course: LESSONS is empty")

    taught = ""
    for idx, les in enumerate(lessons or []):
        les = les or {}
        where = f"lesson #{idx} (order {les.get('order', '?')})"
        for key in ("order", "title"):
            if les.get(key) in (None, ""):
                out.errors.append(f"{where}: '{key}' is missing")
        if (msg := _ru_problem(les.get("title"), les.get("title_ru"), f"{where}.title_ru")):
            out.errors.append(msg)

        text = les.get("text_content")
        if text is not None or not les.get("task"):
            if len(_plain(text)) < MIN_LESSON_TEXT and not les.get("task"):
                out.errors.append(f"{where}: text_content must hold at least {MIN_LESSON_TEXT} characters of theory")
            if (msg := _ru_problem(text, les.get("text_content_ru"), f"{where}.text_content_ru")):
                out.errors.append(msg)
            if _code_lines(text) != _code_lines(les.get("text_content_ru")):
                out.warnings.append(f"{where}: code blocks differ between UZ and RU (only comments may differ)")
        taught += " " + _plain(text) + " " + " ".join(_code_lines(text)) + " " + (les.get("code_content") or "")

        exercises = les.get("exercises") or []
        task = les.get("task")
        if not task:
            kinds = {e.get("exercise_type") for e in exercises if isinstance(e, dict)}
            if len(exercises) < MIN_EXERCISES:
                out.errors.append(f"{where}: needs at least {MIN_EXERCISES} exercises (has {len(exercises)})")
            elif len(kinds) < MIN_EXERCISE_TYPES:
                out.errors.append(f"{where}: exercises must use at least {MIN_EXERCISE_TYPES} types (has {len(kinds)})")
        for e_idx, ex in enumerate(exercises):
            _lint_exercise(ex or {}, f"{where} exercise #{e_idx}", out)

        sample = les.get("sample")
        if sample:
            if not (sample.get("title") or "").strip():
                out.errors.append(f"{where}: sample 'title' is missing")
            for key in ("title", "description"):
                if (msg := _ru_problem(sample.get(key), sample.get(f"{key}_ru"), f"{where}.sample.{key}_ru")):
                    out.errors.append(msg)
            if not (sample.get("code_files") or sample.get("html_code") or sample.get("js_code")):
                out.errors.append(f"{where}: sample needs code_files (or html_code/js_code)")

        if task:
            for key in TASK_FIELDS:
                if not (task.get(key) or "").strip():
                    out.errors.append(f"{where}: task '{key}' is missing")
                if (msg := _ru_problem(task.get(key), task.get(f"{key}_ru"), f"{where}.{key}_ru")):
                    out.errors.append(msg)
            if not (task.get("task_technologies") or "").strip():
                out.errors.append(f"{where}: task 'task_technologies' is missing")
            days = task.get("task_deadline_days")
            if not isinstance(days, int) or days <= 0:
                out.errors.append(f"{where}: task 'task_deadline_days' must be a positive integer")
            unknown = sorted(_tech_tokens(task.get("task_requirements") or "") - _words(taught))
            if unknown:
                out.warnings.append(f"{where}: task requirements mention {', '.join(unknown[:8])}, which this course's lessons never discuss")
    return out
