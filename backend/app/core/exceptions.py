from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.config import settings


async def _persist_error_log(request: Request, exc: Exception, tb_text: str) -> None:
    """Write one row to app_error_logs — see that model's docstring. Opens
    its own session (never the request's — that session may itself be
    what's in a bad state after the exception) and never lets a logging
    failure turn one 500 into a worse one: any exception here is swallowed
    after printing to stderr, same as before this existed."""
    import sys
    from sqlalchemy import select
    from app.db.database import AsyncSessionLocal
    from app.core.security import decode_access_token
    from app.models.user import Student
    from app.models.error_log import AppErrorLog
    from datetime import datetime, timezone

    try:
        actor_id = None
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            actor_id = decode_access_token(auth[7:])

        async with AsyncSessionLocal() as db:
            actor_username = None
            actor_role = None
            if actor_id is not None:
                row = (
                    await db.execute(
                        select(Student.username, Student.role).where(Student.id == actor_id)
                    )
                ).first()
                if row:
                    actor_username, actor_role = row[0], (row[1].value if row[1] else None)

            db.add(AppErrorLog(
                method=request.method,
                path=request.url.path,
                error_type=type(exc).__name__,
                message=str(exc)[:8000],
                traceback=tb_text[:20000],
                actor_id=actor_id,
                actor_username=actor_username,
                actor_role=actor_role,
                created_at=datetime.now(timezone.utc),
            ))
            await db.commit()
    except Exception:
        print("Failed to persist error log entry:", file=sys.stderr)
        import traceback as tb_mod
        tb_mod.print_exc()



def register_exception_handlers(app):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        import sys
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", ""),
            })
        # Diagnostik: 422 sabablarini server logiga yozamiz (journalctl ko'rinishi uchun)
        print(
            f"422 {request.method} {request.url.path}: {errors}",
            file=sys.stderr,
            flush=True,
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": errors
                }
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        import traceback
        import sys
        print(f"UNHANDLED EXCEPTION on {request.method} {request.url}:", file=sys.stderr)
        traceback.print_exc()
        tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        await _persist_error_log(request, exc, tb_text)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Internal server error"
                }
            }
        )