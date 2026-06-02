from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_student, get_db
from app.models.project import Project
from app.models.user import Student
from app.services.github_repo_service import fetch_repo_snapshot, parse_github_url
from app.services.grok_service import analyze_project_with_grok
from app.services.ranking_service import RankingService

router = APIRouter()


def _utc_day_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


async def _count_reviews_today(db: AsyncSession, student_id: int) -> int:
    """Daily AI reviews already consumed by this student (UTC day window)."""
    start = _utc_day_start()
    end = start + timedelta(days=1)
    result = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.reviewed_at >= start,
            Project.reviewed_at < end,
        )
    )
    return int(result.scalar() or 0)


@router.post("/{project_id}/ai-review")
async def ai_review(
        project_id: int,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db),
):
    """AI orqali loyihani baholash.

    Xavfsizlik:
      - Daily cap: bir o'quvchi kuniga MAX_AI_REVIEWS_PER_DAY marta AI
        baholash chaqira oladi (OpenAI byudjeti va ball-farming oldini olish).
      - Re-review bloki: agar loyiha bir marta baholangan bo'lsa
        (reviewed_at IS NOT NULL), uni qayta baholashga ruxsat berilmaydi.
      - Repo fetch: GitHub'dan asl fayllar yuklab olinadi va LLM'ga ko'rsatiladi.
        Agar repo bo'sh / mavjud emas / private bo'lsa — 400 qaytadi va AI
        chaqirilmaydi (token sarflanmaydi).
    """
    if settings.MAX_AI_REVIEWS_PER_DAY <= 0:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="AI baholash hozircha o'chirilgan")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Loyiha topilmadi")
    if project.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    # Block re-review on reviewed_at (not just status="Approved"). Prevents
    # bypass via re-submission cycles that change status but leave the
    # original AI review timestamp in place.
    if project.reviewed_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Bu loyiha allaqachon baholangan, qayta AI baholash mumkin emas",
        )

    if not project.github_url:
        raise HTTPException(status_code=400, detail="AI baholash uchun GitHub URL kerak")

    if parse_github_url(project.github_url) is None:
        raise HTTPException(
            status_code=400,
            detail="GitHub URL formati noto'g'ri (faqat https://github.com/owner/repo)",
        )

    used_today = await _count_reviews_today(db, current_student.id)
    if used_today >= settings.MAX_AI_REVIEWS_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(f"Bugun AI baholash limiti tugadi "
                    f"({settings.MAX_AI_REVIEWS_PER_DAY}/kun). "
                    f"Ertaga qayta urinib ko'ring."),
        )

    # Real code, not just metadata. If repo can't be read, refuse the AI call
    # entirely — no point spending tokens for the LLM to hallucinate.
    snapshot = await fetch_repo_snapshot(project.github_url)
    if not snapshot["exists"]:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub repo o'qib bo'lmadi: {snapshot.get('error') or 'noma''lum xato'}",
        )
    if not snapshot["content_text"]:
        raise HTTPException(
            status_code=400,
            detail="Repo bo'sh yoki o'qiladigan fayllar topilmadi",
        )

    repo_summary = (
        f"default_branch={snapshot['default_branch']}, "
        f"jami fayl soni={snapshot['file_count']}, "
        f"kiritildi ({len(snapshot['files_included'])}): "
        f"{', '.join(snapshot['files_included'])}"
        + (" [truncated]" if snapshot["truncated"] else "")
    )

    technologies = project.technologies_used.split(",") if project.technologies_used else []

    review = await analyze_project_with_grok(
        title=project.title,
        description=project.description or "",
        github_url=project.github_url,
        technologies=technologies,
        difficulty_level=str(project.difficulty_level or "Easy"),
        repo_content=snapshot["content_text"],
        repo_summary=repo_summary,
    )

    # AI call failed (network, malformed JSON, etc.) — surface as 502.
    # No points awarded, project state unchanged. Daily quota is not consumed
    # because reviewed_at stays NULL.
    if review.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=review.get("feedback") or "AI baholash muvaffaqiyatsiz",
        )

    # Default to 0 (NOT 60) — malformed AI response must never grant free points.
    new_points = int(review.get("points", 0) or 0)
    new_points = max(0, min(100, new_points))

    old_points = project.points_earned or 0
    ranking_service = RankingService(db)
    if old_points > 0:
        await ranking_service.subtract_points_from_student(project.student_id, old_points)
    if new_points > 0:
        await ranking_service.add_points_to_student(project.student_id, new_points)

    project.instructor_feedback = review.get("feedback", "")
    project.grade = review.get("grade", "F")
    project.points_earned = new_points
    project.status = "Approved"
    project.reviewed_at = datetime.now(timezone.utc)

    await db.commit()

    return {
        "message": "AI baholash yakunlandi!",
        "project_id": project_id,
        "old_points": old_points,
        "new_points": new_points,
        "reviews_remaining_today": max(
            0, settings.MAX_AI_REVIEWS_PER_DAY - used_today - 1
        ),
        "files_reviewed": snapshot["files_included"],
        **{k: v for k, v in review.items() if k != "error"},
    }
