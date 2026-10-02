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
