"""Question point scale: 0-10, keyed off the owning course's difficulty_level."""

POINTS_BY_DIFFICULTY = {
    "Beginner": 4,
    "Intermediate": 6,
    "Advanced": 8,
    "Expert": 10,
}
DEFAULT_POINTS = 6


def points_for_difficulty(difficulty_level: str | None) -> int:
    return POINTS_BY_DIFFICULTY.get(difficulty_level, DEFAULT_POINTS)
