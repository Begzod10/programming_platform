"""Shared helpers between team_game_session.py and team_game_questions.py.

Kept in its own module (rather than one endpoint file importing from the
other) since those two files have no existing dependency in either
direction and this avoids introducing one just for a payload builder.
"""


def question_start_payload(q) -> dict:
    """Build the question_start WS payload for a GameQuestion.

    Used both when a teacher activates a question (broadcast to everyone)
    and when a student's WS reconnects mid-question (late-joiner catch-up)
    — those two call sites had drifted into two separately hand-written
    dict literals before this extraction.

    SECURITY: must never include the answer (bug_line, bug_explanation,
    bug_explanation_ru, or correct_option) — a student could read it out of
    devtools before the timer runs. Same discipline this payload already
    applied to correct_option; extend it to the new bug-hunt fields.
    """
    return {
        "id": q.id,
        "question_text": q.question_text,
        "question_text_ru": q.question_text_ru,
        "options": q.options,
        "time_limit": q.time_limit,
        "points": q.points,
        "order_index": q.order_index,
        "activated_at": q.activated_at.isoformat() if q.activated_at else None,
        "question_kind": q.question_kind,
        "code_snippet": q.code_snippet,
        "code_language": q.code_language,
    }
