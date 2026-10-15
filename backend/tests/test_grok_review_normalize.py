from app.services.grok_review import _has_task_mismatch_signal, _normalize_grading_result


def test_optional_unused_element_is_not_flagged_as_mismatch():
    """Regression: 'talab qilinmagan' (NOT required) must not trigger the
    contradiction guard just because it shares words with 'talab qilingan'
    (required). Confirmed production false positive: an HTML/CSS
    submission whose only note was an optional, unused <link> tag had its
    AI-stated 80 capped to 50 by this sentence."""
    feedback = (
        "Loyiha yaxshi bajarilgan. Bitta qo'shimcha <link> tegi bor, lekin "
        "u dars doirasida talab qilinmagan va CSS ishlatilmagan, shuning "
        "uchun bu ortiqcha, lekin xato emas."
    )
    assert _has_task_mismatch_signal(feedback, []) is False


def test_missing_required_element_is_flagged_as_mismatch():
    feedback = "Sizning topshirig'ingizda talab qilingan elementlar mavjud emas."
    assert _has_task_mismatch_signal(feedback, []) is True


def test_task_does_not_match_lesson_is_flagged_as_mismatch():
    feedback = "Bu kod boshqa mavzuga oid, vazifaga mos kelmaydi."
    assert _has_task_mismatch_signal(feedback, []) is True


def test_normalize_does_not_cap_score_for_optional_unused_element_note():
    result = {
        "points": 80,
        "grade": "B",
        "feedback": (
            "Loyiha yaxshi bajarilgan. Bitta qo'shimcha <link> tegi bor, "
            "lekin u dars doirasida talab qilinmagan va CSS ishlatilmagan."
        ),
        "improvements": [],
    }
    out = _normalize_grading_result(result)
    assert out["points"] == 80
    assert "contradiction_flagged" not in out


def test_normalize_caps_score_for_genuine_task_mismatch():
    result = {
        "points": 100,
        "grade": "A",
        "feedback": "Ushbu kod vazifaga mos kelmaydi, talab qilingan elementlar mavjud emas.",
        "improvements": [],
    }
    out = _normalize_grading_result(result)
    assert out["points"] == 50
    assert out["contradiction_flagged"] is True
