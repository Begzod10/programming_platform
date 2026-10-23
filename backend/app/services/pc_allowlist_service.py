"""PC Guard: allowlist of apps lab PCs may run while unlocked."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pc_control import PcAllowlist

DEFAULT_ALLOWLIST = ["code.exe", "windowsterminal.exe", "cmd.exe", "powershell.exe",
                     "python.exe", "node.exe", "chrome.exe", "msedge.exe"]


def default_entries() -> list[dict]:
    return [{"exe": e, "publisher": None} for e in DEFAULT_ALLOWLIST]


def validate_entries(entries: list[dict]) -> list[dict]:
    if not entries:
        raise ValueError("allowlist must not be empty")
    out = []
    for e in entries:
        exe = (e.get("exe") or "").strip().lower()
        if not exe.endswith(".exe") or exe == ".exe":
            raise ValueError(f"invalid executable name: {exe!r}")
        if "\\" in exe or "/" in exe:
            raise ValueError(f"executable name must not contain a path: {exe!r}")
        out.append({"exe": exe, "publisher": e.get("publisher")})
    return out


async def _row(db: AsyncSession, group_id: Optional[int]) -> Optional[PcAllowlist]:
    cond = PcAllowlist.group_id.is_(None) if group_id is None else PcAllowlist.group_id == group_id
    return (await db.execute(select(PcAllowlist).where(cond).order_by(PcAllowlist.id))).scalars().first()


async def get_own_entries(db: AsyncSession, group_id: Optional[int]) -> list[dict]:
    """Entries stored for exactly this scope (global falls back to defaults; a group has none)."""
    row = await _row(db, group_id)
    if row is None:
        return default_entries() if group_id is None else []
    return [dict(e) for e in row.entries]


async def set_entries(db: AsyncSession, group_id: Optional[int], entries: list[dict],
                      updated_by: Optional[int]) -> list[dict]:
    """Validate and upsert (find-or-create by `group_id IS NULL`, never a 2nd global row)."""
    clean = validate_entries(entries)
    row = await _row(db, group_id)
    if row is None:
        row = PcAllowlist(group_id=group_id, entries=clean, updated_by=updated_by)
        db.add(row)
    else:
        row.entries = clean
        row.updated_by = updated_by
    await db.commit()
    return clean


async def effective_allowlist(db: AsyncSession, group_id: Optional[int]) -> list[dict]:
    merged: dict[str, dict] = {}
    for e in await get_own_entries(db, None):
        merged.setdefault(e["exe"], e)
    if group_id is not None:
        for e in await get_own_entries(db, group_id):
            merged.setdefault(e["exe"], e)
    return list(merged.values())
