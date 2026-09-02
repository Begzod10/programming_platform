"""SSO token verification and account resolution for the classroom ->
student_platform handoff — see docs/CLASSROOM_SSO_FOR_STUDENT_PLATFORM.md for
the full contract this implements.

classroom mints a 90-second HS256 JWT when a student opens a subject taught
here, and the browser lands on https://<us>/#sso=<TOKEN>. This resolves that
token to the SAME Student row auth_service.login would produce for the
equivalent gennis/turon account — the two paths MUST agree, or a person who
has logged in with a password before ends up split across two accounts with
their progress divided between them.
"""
import os
import time

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import Student, UserRole
from app.services.auth_service import create_ranking

ISSUER = "classroom"
AUDIENCE = "student_platform"
ALGORITHM = "HS256"

# jti -> unix timestamp after which it's safe to forget. In-memory and
# per-process: lost on restart, not shared across workers. That's an
# accepted gap, not an oversight — the token's own 90-second lifetime is the
# real defense; this is a second layer against the browser back button
# re-sending the same URL within that window.
_used_jti: dict[str, float] = {}
_JTI_RETENTION_SECONDS = 600

_INVALID_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired SSO token",
)


def _check_and_mark_jti(jti: str) -> None:
    now = time.time()
    expired = [k for k, exp in _used_jti.items() if exp <= now]
    for k in expired:
        del _used_jti[k]

    if jti in _used_jti:
        raise _INVALID_TOKEN
    _used_jti[jti] = now + _JTI_RETENTION_SECONDS


def _decode_sso_token(token: str) -> dict:
    """Decode + validate an SSO token. Every failure raises the SAME 401 —
    deliberately not distinguishing "expired" from "bad signature" etc., so
    the error can't be used to fingerprint a rejected token (see the doc's
    warning on this)."""
    try:
        claims = jwt.decode(
            token,
            settings.SSO_SHARED_SECRET,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
    except JWTError:
        raise _INVALID_TOKEN

    if claims.get("source") not in ("gennis", "turon"):
        raise _INVALID_TOKEN
    if not isinstance(claims.get("ext_id"), int):
        raise _INVALID_TOKEN
    if not claims.get("jti"):
        raise _INVALID_TOKEN

    return claims


async def resolve_sso_login(db: AsyncSession, token: str) -> dict:
    """Full SSO flow: verify the token, find-or-create the Student row,
    return the same {access_token, token_type, user} shape as /auth/login."""
    if not settings.SSO_SHARED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SSO is not configured",
        )

    claims = _decode_sso_token(token)
    _check_and_mark_jti(claims["jti"])

    source = claims["source"]
    ext_id = claims["ext_id"]
    id_col = f"{source}_id"
    role = UserRole.teacher if claims.get("role") == "teacher" else UserRole.student
    token_username = claims.get("username") or f"{source}_{ext_id}"

    # 1) Most reliable: the source system's own numeric id — it never
    # changes, unlike username. See the doc's section 5.
    result = await db.execute(select(Student).where(getattr(Student, id_col) == ext_id))
    user = result.scalar_one_or_none()

    # 2) Fall back to username — covers a person who logged in with a
    # password before this account ever got {id_col} backfilled.
    if user is None:
        ext_username = f"{source}_{ext_id}"
        result = await db.execute(
            select(Student).where(
                (Student.username == token_username) | (Student.username == ext_username)
            )
        )
        user = result.scalar_one_or_none()

    if user is None:
        name = claims.get("name", "")
        surname = claims.get("surname", "")
        username = token_username if role == UserRole.teacher else f"{source}_{ext_id}"
        user = Student(
            username=username,
            email=f"{source}_{ext_id}@{source}.uz",
            full_name=f"{name} {surname}".strip(),
            hashed_password=get_password_hash(os.urandom(32).hex()),
            role=role,
            is_active=True,
            **{id_col: ext_id},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        if user.role == UserRole.student:
            await create_ranking(db, user.id)
    else:
        changed = False
        if getattr(user, id_col) != ext_id:
            setattr(user, id_col, ext_id)
            changed = True
        if user.role != role:
            user.role = role
            changed = True
        if changed:
            await db.commit()
            await db.refresh(user)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Foydalanuvchi faol emas",
            )

    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
        "user": user,
    }
