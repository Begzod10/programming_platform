"""PC Guard one-time maintenance codes.

A teacher issues a 6-digit code bound to one device; the (signed-out, token-less) agent
redeems it with its machine_key and is told how many minutes to stop blocking.

Hashing: HMAC-SHA256 keyed with the server SECRET_KEY over a per-row random salt + code.
A 6-digit code has only 10**6 values, so a plain salted SHA-256 found in a DB dump/backup
would be reversed in milliseconds; keying with a secret that is not in the database means
the stored hash alone reveals nothing. The per-row salt keeps equal codes from producing
equal hashes. Codes also live only 5 minutes and are single-use."""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import case, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pc_control import PcDevice, PcMaintenanceCode

logger = logging.getLogger(__name__)

ALLOWED_MINUTES = (15, 60, 240)
CODE_TTL = timedelta(minutes=5)
MAX_FAILED_ATTEMPTS = 5
MAX_CODES_PER_HOUR = 10
RETENTION = timedelta(days=7)


class IssueLimitExceeded(Exception):
    pass


def _hash(salt: str, code: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), f"{salt}:{code}".encode("utf-8"),
                    hashlib.sha256).hexdigest()


def machine_key_hash(machine_key: str) -> str:
    # Same derivation as pc_device.pc_login, which stores PcDevice.machine_key_hash.
    return hashlib.sha256(machine_key.encode("utf-8")).hexdigest()


async def issue_code(db: AsyncSession, device: PcDevice, minutes: int, user_id: int) -> tuple[str, PcMaintenanceCode]:
    """Create a code for `device`, superseding its older unused codes. Returns (plain code, row);
    the plain code exists only in this return value. Commits."""
    if minutes not in ALLOWED_MINUTES:
        raise ValueError("minutes")
    now = datetime.now(timezone.utc)

    # Retention: opportunistic, all devices.
    await db.execute(delete(PcMaintenanceCode).where(PcMaintenanceCode.created_at < now - RETENTION))

    recent = (await db.execute(select(func.count(PcMaintenanceCode.id)).where(
        PcMaintenanceCode.device_id == device.id,
        PcMaintenanceCode.created_at > now - timedelta(hours=1)))).scalar_one()
    if recent >= MAX_CODES_PER_HOUR:
        await db.commit()  # keep the retention delete
        raise IssueLimitExceeded()

    await db.execute(
        update(PcMaintenanceCode)
        .where(PcMaintenanceCode.device_id == device.id, PcMaintenanceCode.used_at.is_(None))
        .values(used_at=now)
        .execution_options(synchronize_session=False))

    code = f"{secrets.randbelow(10 ** 6):06d}"
    salt = secrets.token_hex(16)
    row = PcMaintenanceCode(device_id=device.id, code_hash=_hash(salt, code), salt=salt,
                            minutes=minutes, created_by_user_id=user_id, created_at=now,
                            expires_at=now + CODE_TTL, failed_attempts=0)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    logger.info("maintenance code issued device=%s by=%s minutes=%s", device.id, user_id, minutes)
    return code, row


async def redeem_code(db: AsyncSession, machine_key: str, code: str) -> Optional[int]:
    """Minutes on success (code consumed in this call's transaction), None on any failure.
    Commits. Every failure path does the same work: device lookup, active-code lookup,
    one HMAC and one constant-time compare."""
    now = datetime.now(timezone.utc)
    device_id = (await db.execute(select(PcDevice.id).where(
        PcDevice.machine_key_hash == machine_key_hash(machine_key)))).scalar_one_or_none()
    # Never creates a device. Unknown keys still run the code query (id -1 matches nothing).
    active = (await db.execute(
        select(PcMaintenanceCode)
        .where(PcMaintenanceCode.device_id == (device_id if device_id is not None else -1),
               PcMaintenanceCode.used_at.is_(None),
               PcMaintenanceCode.expires_at > now,
               PcMaintenanceCode.failed_attempts < MAX_FAILED_ATTEMPTS)
        .order_by(PcMaintenanceCode.id.desc())
        .limit(1))).scalars().first()

    if active is None:
        # Dummy hash + compare so unknown key / no active code costs the same as a wrong guess.
        hmac.compare_digest(_hash(secrets.token_hex(16), code), secrets.token_hex(32))
        await db.rollback()
        return None

    code_id, minutes = active.id, active.minutes
    if not hmac.compare_digest(_hash(active.salt, code), active.code_hash):
        # Atomic: both SET expressions read the pre-update failed_attempts.
        await db.execute(
            update(PcMaintenanceCode)
            .where(PcMaintenanceCode.id == code_id, PcMaintenanceCode.used_at.is_(None))
            .values(failed_attempts=PcMaintenanceCode.failed_attempts + 1,
                    used_at=case((PcMaintenanceCode.failed_attempts + 1 >= MAX_FAILED_ATTEMPTS, now),
                                 else_=PcMaintenanceCode.used_at))
            .execution_options(synchronize_session=False))
        await db.commit()
        return None

    # Conditional UPDATE: of two concurrent redeems only one sees rowcount == 1.
    res = await db.execute(
        update(PcMaintenanceCode)
        .where(PcMaintenanceCode.id == code_id,
               PcMaintenanceCode.used_at.is_(None),
               PcMaintenanceCode.expires_at > now,
               PcMaintenanceCode.failed_attempts < MAX_FAILED_ATTEMPTS)
        .values(used_at=now)
        .execution_options(synchronize_session=False))
    await db.commit()
    if res.rowcount != 1:
        return None
    logger.info("maintenance code redeemed device=%s minutes=%s", device_id, minutes)
    return minutes
