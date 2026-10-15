"""The Flask token/CORS course spec must stay lint-clean as lessons are added (UZ+RU parity, hints, shapes)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from course_builder.lint import lint_spec  # noqa: E402
from course_builder.spec_loader import load_spec  # noqa: E402

SPEC = Path(__file__).resolve().parents[1] / "scripts" / "course_specs" / "flask_jwt_cors.py"


def test_the_spec_has_no_lint_errors_or_warnings():
    module = load_spec(str(SPEC))
    result = lint_spec(module.COURSE, module.LESSONS)
    assert result.errors == [] and result.warnings == [], (result.errors, result.warnings)


def test_course_settings_match_the_existing_flask_courses():
    module = load_spec(str(SPEC))
    c = module.COURSE
    assert (c["instructor_id"], c["category_id"], c["prerequisite_course_id"], c["is_published"]) == (2, 8, 28, False)
    orders = [lesson["order"] for lesson in module.LESSONS]
    assert orders == sorted(set(orders)) and orders[0] == 0
