from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_teacher
from app.models.user import Student

router = APIRouter()


@router.get("/")
async def get_project_activity(
    db: AsyncSession = Depends(get_db),
    current_teacher: Student = Depends(get_current_teacher),
):
    rows = await db.execute(text("""
        SELECT
            p.id,
            COALESCE(s.full_name, s.username)   AS student_name,
            p.status,
            p.grade,
            COALESCE(c.title, '')               AS course_title,
            COALESCE(l.title, '')               AS lesson_title,
            p.time_spent_seconds,
            p.keystroke_count,
            p.paste_count,
            p.code_explanation,
            p.submitted_at
        FROM projects p
        JOIN students s ON s.id = p.student_id
        LEFT JOIN submissions sub ON sub.project_id = p.id
        LEFT JOIN lessons l ON l.id = sub.lesson_id
        LEFT JOIN courses c ON c.id = l.course_id
        WHERE p.submitted_at IS NOT NULL
        ORDER BY p.submitted_at DESC
        LIMIT 200
    """))
    result = []
    for r in rows.fetchall():
        result.append({
            "project_id":          r[0],
            "student_name":        r[1] or "",
            "status":              r[2] or "",
            "grade":               r[3] or "",
            "course_title":        r[4],
            "lesson_title":        r[5],
            "time_spent_seconds":  r[6],
            "keystroke_count":     r[7],
            "paste_count":         r[8],
            "code_explanation":    r[9] or "",
            "submitted_at":        r[10].isoformat() if r[10] else None,
        })
    return result


@router.get("/exercises")
async def get_exercise_activity(
    db: AsyncSession = Depends(get_db),
    current_teacher: Student = Depends(get_current_teacher),
):
    rows = await db.execute(text("""
        SELECT
            es.id,
            COALESCE(s.full_name, s.username)   AS student_name,
            ex.exercise_type,
            ex.description                       AS question,
            COALESCE(c.title, '')               AS course_title,
            COALESCE(l.title, '')               AS lesson_title,
            es.time_spent_ms,
            es.is_correct,
            es.submitted_at
        FROM exercise_submissions es
        JOIN students s ON s.id = es.student_id
        JOIN exercises ex ON ex.id = es.exercise_id
        LEFT JOIN lessons l ON l.id = ex.lesson_id
        LEFT JOIN courses c ON c.id = l.course_id
        WHERE es.time_spent_ms IS NOT NULL
        ORDER BY es.submitted_at DESC
        LIMIT 300
    """))
    result = []
    for r in rows.fetchall():
        question = (r[3] or "")[:120]
        result.append({
            "submission_id":  r[0],
            "student_name":   r[1] or "",
            "exercise_type":  r[2] or "",
            "question":       question,
            "course_title":   r[4],
            "lesson_title":   r[5],
            "time_spent_ms":  r[6],
            "is_correct":     r[7],
            "submitted_at":   r[8].isoformat() if r[8] else None,
        })
    return result
