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
from dataclasses import dataclass
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


@dataclass(frozen=True)
class RedeemResult:
    """`minutes` is set on success only. `known_device` says whether the machine_key matched
    a PcDevice: the endpoint records failures only for known devices, so unknown keys leave
    no limiter state behind."""
    known_device: bool
    minutes: Optional[int] = None


async def redeem_code(db: AsyncSession, machine_key: str, code: str) -> RedeemResult:
    """Consume a code and record the device's maintenance window, in one transaction. Commits.

    Every active code of the device is checked, not only the newest: two concurrent
    issue_code calls can each run their supersede UPDATE before the other's INSERT is
    visible, leaving two active codes (review M3). Accepting either keeps the older holder
    working; success then retires all of them, and a wrong guess counts against each, so
    the per-code limit still bounds guessing at MAX_FAILED_ATTEMPTS per device.

    Lost response (review M4): if this commits but the HTTP response never reaches the agent
    (timeout, dropped connection), the code is used up and the PC stays locked. The teacher
    issues a new code (MAX_CODES_PER_HOUR allows for this); no idempotent replay is offered.

    Every failure path does comparable work: device lookup, active-code lookup, at least one
    HMAC and constant-time compare."""
    now = datetime.now(timezone.utc)
    device_id = (await db.execute(select(PcDevice.id).where(
        PcDevice.machine_key_hash == machine_key_hash(machine_key)))).scalar_one_or_none()
    known = device_id is not None
    # Never creates a device. Unknown keys still run the code query (id -1 matches nothing).
    active = (await db.execute(
        select(PcMaintenanceCode)
        .where(PcMaintenanceCode.device_id == (device_id if known else -1),
               PcMaintenanceCode.used_at.is_(None),
               PcMaintenanceCode.expires_at > now,
               PcMaintenanceCode.failed_attempts < MAX_FAILED_ATTEMPTS)
        .order_by(PcMaintenanceCode.id.desc())
        .limit(MAX_CODES_PER_HOUR))).scalars().all()

    if not active:
        # Dummy hash + compare so unknown key / no active code costs the same as a wrong guess.
        hmac.compare_digest(_hash(secrets.token_hex(16), code), secrets.token_hex(32))
        await db.rollback()
        return RedeemResult(known)

    match = None
    for row in active:  # compare against all, so timing does not depend on which one matched
        if hmac.compare_digest(_hash(row.salt, code), row.code_hash) and match is None:
            match = (row.id, row.minutes)
    active_ids = [row.id for row in active]

    if match is None:
        # Atomic: both SET expressions read the pre-update failed_attempts.
        await db.execute(
            update(PcMaintenanceCode)
            .where(PcMaintenanceCode.id.in_(active_ids), PcMaintenanceCode.used_at.is_(None))
            .values(failed_attempts=PcMaintenanceCode.failed_attempts + 1,
                    used_at=case((PcMaintenanceCode.failed_attempts + 1 >= MAX_FAILED_ATTEMPTS, now),
                                 else_=PcMaintenanceCode.used_at))
            .execution_options(synchronize_session=False))
        await db.commit()
        return RedeemResult(True)

    code_id, minutes = match
    # Conditional UPDATE: of two concurrent redeems only one sees rowcount == 1.
    res = await db.execute(
        update(PcMaintenanceCode)
        .where(PcMaintenanceCode.id == code_id,
               PcMaintenanceCode.used_at.is_(None),
               PcMaintenanceCode.expires_at > now,
               PcMaintenanceCode.failed_attempts < MAX_FAILED_ATTEMPTS)
        .values(used_at=now)
        .execution_options(synchronize_session=False))
    if res.rowcount != 1:
        await db.rollback()
        return RedeemResult(True)
    # Retire any other active code of this device (left by a concurrent issue).
    await db.execute(
        update(PcMaintenanceCode)
        .where(PcMaintenanceCode.device_id == device_id, PcMaintenanceCode.used_at.is_(None))
        .values(used_at=now)
        .execution_options(synchronize_session=False))
    await db.execute(
        update(PcDevice).where(PcDevice.id == device_id)
        .values(maintenance_until=now + timedelta(minutes=minutes))
        .execution_options(synchronize_session=False))
    await db.commit()
    logger.info("maintenance code redeemed device=%s minutes=%s", device_id, minutes)
    return RedeemResult(True, minutes)
