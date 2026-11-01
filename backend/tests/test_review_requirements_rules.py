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
    assert '"requirements"' in text and "met" in text                          # a per-requirement checklist is asked for as JSON
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


# ── the checklist the model returns is formatted and enforced by code ───────────────────────────────

from app.services.grok_review import _normalize_grading_result  # noqa: E402


def result(points, requirements, feedback="Umumiy fikr.", improvements=None, grade="C"):
    return {"grade": grade, "points": points, "feedback": feedback, "improvements": improvements or [],
            "requirements": requirements}


def test_the_checklist_is_put_in_front_of_the_feedback_as_check_marks():
    out = _normalize_grading_result(result(68, [
        {"n": 1, "met": True, "note": "6 ta kartochka bor"},
        {"n": 2, "met": False, "note": "h2 ga class berilgan, lekin CSS'da .sarlavha yozilmagan. CSS'ga .sarlavha {...} qo'shing"},
    ]))
    assert out["feedback"].startswith("Talablar bo'yicha:\n✅ 1) 6 ta kartochka bor\n❌ 2) h2 ga class")
    assert out["feedback"].endswith("Umumiy fikr.")
    assert "requirements" not in out and [i["met"] for i in out["requirements_checklist"]] == [True, False]
    assert out["points"] == 68                                  # one requirement failed: the model's score stands


def test_when_every_requirement_is_met_the_score_is_at_least_75():
    out = _normalize_grading_result(result(68, [{"met": True, "note": "a"}, {"met": True, "note": "b"}]))
    assert out["points"] == 75 and out["grade"] == "B" and out["requirements_floor_applied"] is True


def test_a_higher_score_is_left_alone_when_everything_is_met():
    out = _normalize_grading_result(result(92, [{"met": True, "note": "a"}], grade="A"))
    assert out["points"] == 92 and "requirements_floor_applied" not in out


def test_stray_negative_prose_cannot_cap_a_project_whose_requirements_are_all_met():
    prose = "Talab qilingan elementlar mavjud emas deb o'ylagandim, lekin hammasi bor."
    out = _normalize_grading_result(result(80, [{"met": True, "note": "a"}], feedback=prose, grade="B"))
    assert out["points"] == 80 and "contradiction_flagged" not in out


def test_the_contradiction_guard_reads_the_models_prose_not_the_checklist_notes():
    out = _normalize_grading_result(result(80, [{"met": False, "note": "talab qilingan fayl mavjud emas"}],
                                           feedback="Yaxshi ish.", grade="B"))
    assert out["points"] == 80 and "contradiction_flagged" not in out       # the ❌ note alone does not trigger it


def test_a_missing_or_broken_checklist_changes_nothing():
    plain = _normalize_grading_result({"grade": "C", "points": 68, "feedback": "x", "improvements": []})
    assert plain["points"] == 68 and plain["feedback"] == "x" and "requirements_checklist" not in plain
    for broken in ([], "text", [{"met": "yes", "note": "x"}], [{"note": "x"}], [{"met": True}, "oops"]):
        out = _normalize_grading_result(result(68, broken))
        assert out["points"] == 68 and out["feedback"] == "Umumiy fikr." and "requirements_checklist" not in out

