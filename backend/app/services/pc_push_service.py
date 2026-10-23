"""Push PC Guard state to connected lab-PC agents over the device websocket."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pc_control import PcDevice, PcSession
from app.services.pc_lock_service import compute_state
from app.ws.manager import pc_ws_manager


async def push_state_to_device(db: AsyncSession, device_id: int) -> None:
    device = await db.get(PcDevice, device_id)
    if device is None:
        return
    state = await compute_state(db, device)
    await pc_ws_manager.broadcast(device_id, {"type": "state", **state})


async def push_state_for_student(db: AsyncSession, student_id: int) -> None:
    """Every device with an open session for this student; no-op when none."""
    device_ids = (await db.execute(
        select(PcSession.device_id).where(
            PcSession.student_id == student_id, PcSession.signed_out_at.is_(None)
        ).distinct()
    )).scalars().all()
    for device_id in device_ids:
        await push_state_to_device(db, device_id)
