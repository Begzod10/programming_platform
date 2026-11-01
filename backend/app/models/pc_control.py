"""PC Guard models: lab devices, per-group app allowlists, student sessions,
usage events and teacher commands."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer, Boolean, DateTime, String, ForeignKey, Index, JSON, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class PcDevice(Base):
    __tablename__ = "pc_devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    machine_key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_app: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PcAllowlist(Base):
    """Allowed apps per group; group_id NULL is the global row."""
    __tablename__ = "pc_allowlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, unique=True)
    # list of {"exe": str, "publisher": str}
    entries: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PcSession(Base):
    __tablename__ = "pc_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("pc_devices.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    signed_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    signed_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_pc_sessions_device_signed_out", "device_id", "signed_out_at"),
    )


class PcUsageEvent(Base):
    __tablename__ = "pc_usage_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("pc_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    was_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class PcCommand(Base):
    __tablename__ = "pc_commands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scope_type: Mapped[str] = mapped_column(String(10), nullable=False)  # device | group | all
    scope_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # lock | unlock | clear | message
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
