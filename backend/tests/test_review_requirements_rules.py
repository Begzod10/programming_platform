"""The AI grader gets explicit rules for grading against the lesson's "Talablar" list (see _format_requirements_rules)."""
from app.services.grok_review import _build_review_prompt, _format_requirements_rules

CTX = {"course_title": "HTML CSS", "lesson_title": "Class id", "task_title": "Kartochkalar",
       "task_description": "Kamida 3 ta kartochka", "task_requirements": "• Kamida 3 ta kartochka\\n• #header faqat 1 marta"}


def prompt(ctx):
    return _build_review_prompt(
        title="T", description="d", github_url="(ZIP)", technologies=["HTML5"], difficulty_level="Easy",
        previous_points=0, repo_content="<div class='card'></div>", repo_summary="1 fayl", lesson_context=ctx)


def test_rules_are_in_the_prompt_when_the_lesson_lists_requirements():
    text = prompt(CTX)
    assert "TALABLAR BO'YICHA BAHOLASH" in text
    assert "✅" in text and "❌" in text                                       # a per-requirement checklist is asked for
    assert "kamida N" in text and "KO'P to'g'ri" in text                       # "at least N" is not "exactly N"
    assert "O'YLAB TOPMA" in text                                              # no invented criteria
    assert "AYNAN bir xil" in text                                             # HTML class names must match the CSS selectors
    assert "kamida 75" in text                                                 # all requirements met -> passes


def test_rules_come_after_the_lesson_context_and_before_the_metadata():
    text = prompt(CTX)
    assert text.index("DARS KONTEKSTI") < text.index("TALABLAR BO'YICHA BAHOLASH") < text.index("## METADATA")


def test_no_rules_for_a_lesson_without_requirements_or_a_standalone_project():
    assert _format_requirements_rules(None) == ""
    assert _format_requirements_rules({"task_requirements": "  "}) == ""
    assert "TALABLAR BO'YICHA BAHOLASH" not in prompt({"course_title": "HTML CSS", "lesson_title": "x"})
    assert "TALABLAR BO'YICHA BAHOLASH" not in prompt(None)


def test_the_strict_wrong_technology_rules_still_win():
    text = prompt(CTX)
    assert "QATTIQ QOIDA" in text and "bundan ustun" in text
