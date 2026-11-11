"""Which home-page section a kids' module belongs to.

EarlyModule.subject cannot do this job (nearly every shipped module is
"logic"), so the section is derived from what the module's games actually
are — the majority `content.mode` of its activities. Nothing is stored: a
new module lands in the right section by itself.
"""
from collections import Counter
from typing import List, Optional

SECTION_MODES = {
    "world": ("select", "sort", "cause_effect", "sequence", "pairs"),
    "logic": ("count", "arithmetic", "compare", "pattern", "maze", "simon",
              "sudoku", "merge", "chart", "rounds", "bubbles"),
    "make": ("trace", "build", "puzzle"),
    "letters": ("typing", "keyboard", "wordbuild", "hangman"),
}
DEFAULT_SECTION = "world"
# Equal votes: the rarer kind of game wins, so a mixed module is filed where
# it adds variety rather than under the already-crowded sections.
TIE_PRIORITY = ("letters", "make", "logic", "world")

_MODE_SECTION = {mode: section for section, modes in SECTION_MODES.items() for mode in modes}


def section_for_modes(modes: List[Optional[str]]) -> str:
    """Majority section of the given activity modes. A missing or unknown
    mode counts as the default game ("select" → world); no activities →
    world."""
    if not modes:
        return DEFAULT_SECTION
    votes = Counter(_MODE_SECTION.get(mode, DEFAULT_SECTION) for mode in modes)
    best = max(votes.values())
    return next(section for section in TIE_PRIORITY if votes.get(section) == best)
