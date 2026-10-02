from app.services import exercise_service


async def test_ai_explanation_prompt_includes_the_students_actual_answer(monkeypatch):
    """Regression: the prompt used to carry only the question, so the AI
    guessed the mistake blind (told a student who typed "$primary" that
    their "$" was missing)."""
    captured = {}

    async def fake_call_chain(prompt, **kwargs):
        captured["prompt"] = prompt
        return "Siz ismni ikki marta yozdingiz.", None, "fake", []

    monkeypatch.setattr(exercise_service, "call_chain", fake_call_chain)

    await exercise_service.get_ai_explanation(
        question="Bo'sh joyni to'ldiring: ___primary: #3498db;",
        student_answer="$primary",
    )

    assert "'$primary'" in captured["prompt"]


def test_matching_answer_is_spelled_out_as_pairs_for_the_ai():
    """A raw index list means nothing to the model; it must see which
    definition the student attached to which term."""
    from types import SimpleNamespace

    ex = SimpleNamespace(
        exercise_type="matching",
        title="Juftlikni top: dict va set",
        description="Atamalarni ta'riflar bilan moslashtiring.",
        drag_items='["dict", "set", ".get()"]',
        options='["kalit-qiymat juftliklari", "takrorlanmas elementlar", "kalitni xavfsiz oladi"]',
    )
    # dict->options[1], set->options[2], .get()->options[0]  (all three wrong)
    question, answer = exercise_service._describe_answer_for_ai(ex, "[1,2,0]")

    assert "dict -> takrorlanmas elementlar" in answer
    assert ".get() -> kalit-qiymat juftliklari" in answer
    assert "Atamalar: dict, set, .get()" in question


def test_non_matching_answer_passes_through_unchanged():
    from types import SimpleNamespace

    ex = SimpleNamespace(exercise_type="fill_in_blank", title="t", description="q?",
                         drag_items=None, options=None)
    assert exercise_service._describe_answer_for_ai(ex, "$primary") == ("q?", "$primary")


def test_unparseable_matching_answer_falls_back_to_raw_text():
    from types import SimpleNamespace

    ex = SimpleNamespace(exercise_type="matching", title="t", description="q?",
                         drag_items='["a"]', options='["b"]')
    assert exercise_service._describe_answer_for_ai(ex, "not json") == ("q?", "not json")
