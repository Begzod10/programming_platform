"""Points-economy store, wallet ledger, and student inventory.

Phase 1 of the points-spending economy (see design doc). Adds four tables:

  * `store_items`           — the catalogue (teacher/admin managed).
  * `student_wallet_ledger` — append-only earn/spend log; balance = replay.
  * `student_purchases`     — one row per purchase, with a status machine.
  * `student_inventory`     — what a student owns; supports equip for
                              theme/font/sound.

Only cosmetics ship in Phase 1 (themes / fonts / sound packs). Cases,
subscriptions, boosts, and real-value rewards get their own tables in
Phases 2–3 and are intentionally NOT declared here.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Enum, Text, ForeignKey, JSON, func,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student


class StoreItemKind(str, enum.Enum):
    """What kind of thing sits behind a catalogue row.

    Only theme/font/sound_pack are handled by Phase 1 endpoints. The other
    values are defined here so the enum is stable when later phases add
    the code to consume them — cheaper than an enum migration later.
    """
    theme = "theme"
    sound_pack = "sound_pack"
    font = "font"
    pro_plan = "pro_plan"
    case = "case"
    boost = "boost"
    gift = "gift"
    hosting = "hosting"
    api_credit = "api_credit"


class LedgerReason(str, enum.Enum):
    """Why the wallet moved.

    `earn_*` reasons must have delta > 0; `spend_*` must have delta < 0.
    The wallet service enforces this so no caller can flip a sign by
    accident and silently mint coins.
    """
    earn_activity = "earn_activity"     # generic earn (exercise, lesson, project…)
    earn_grant = "earn_grant"           # teacher hand-grants coins
    spend_purchase = "spend_purchase"
    refund = "refund"                   # positive delta reversing a spend


class PurchaseStatus(str, enum.Enum):
    completed = "completed"
    requested = "requested"
    approved = "approved"
    fulfilled = "fulfilled"
    rejected = "rejected"
    refunded = "refunded"


class AcquiredVia(str, enum.Enum):
    purchase = "purchase"
    case_drop = "case_drop"
    grant = "grant"


# ─── catalogue ─────────────────────────────────────────────────────────────


class StoreItem(Base):
    __tablename__ = "store_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    kind: Mapped[StoreItemKind] = mapped_column(
        Enum(StoreItemKind, name="store_item_kind"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    # Bilingual, UZ-primary (matches the rest of the platform).
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    title_ru: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    price_coins: Mapped[int] = mapped_column(Integer, nullable=False)

    # Kind-specific payload: theme token map, font family + url, sound URLs,
    # etc. Kept as JSON so adding a new kind doesn't require a column.
    asset_ref: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    # NULL = unlimited stock. When set, the wallet service decrements it
    # atomically per purchase (Phase 2 for cases; Phase 1 doesn't use it).
    stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    # Phase-3 hooks — no code reads these in Phase 1, but declaring them
    # up front avoids a schema change later.
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    min_lifetime_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StoreItem id={self.id} slug={self.slug!r} price={self.price_coins}>"


# ─── ledger (append-only) ──────────────────────────────────────────────────


class WalletLedgerEntry(Base):
    """One row per wallet movement. Never updated, never deleted.

    Balance is `sum(delta_coins) WHERE student_id = ?`. We also snapshot
    the post-transaction balance in `balance_after` so hot reads
    (wallet chip, history page) don't need to re-sum the whole ledger.

    `idempotency_key` is the anti-abuse spine: a client that retries a
    purchase submits the same key and the second insert fails cleanly
    on the unique constraint — the debit only happens once.
    """
    __tablename__ = "student_wallet_ledger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    delta_coins: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[LedgerReason] = mapped_column(
        Enum(LedgerReason, name="wallet_ledger_reason"),
        nullable=False,
    )

    # What caused this movement: ('purchase', 42), ('project', 88), etc.
    # ref_type is free-form (short slug); ref_id is nullable for grants.
    ref_type: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    ref_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, unique=True)

    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_wallet_ledger_student_created", "student_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<WalletLedgerEntry student_id={self.student_id} "
            f"delta={self.delta_coins} reason={self.reason.value} "
            f"balance_after={self.balance_after}>"
        )


# ─── purchases ─────────────────────────────────────────────────────────────


class StudentPurchase(Base):
    """One row per purchase or redemption request.

    Cosmetic purchases short-circuit to `completed`. Phase-3 real-value
    items enter `requested` and traverse approved → fulfilled/rejected.
    Refunds insert a positive ledger entry and flip status to `refunded`.
    """
    __tablename__ = "student_purchases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    store_item_id: Mapped[int] = mapped_column(
        ForeignKey("store_items.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Snapshot the price at purchase time — the catalogue price is
    # mutable, but a receipt should not be.
    price_paid: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="student_purchase_status"),
        nullable=False,
        default=PurchaseStatus.completed,
        server_default=PurchaseStatus.completed.value,
        index=True,
    )

    approved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ─── inventory ─────────────────────────────────────────────────────────────


class StudentInventoryItem(Base):
    """What a student owns.

    * Cosmetic items (theme / font / sound_pack) live here as one row per
      owned item with quantity=1. `is_equipped` is set on at most one row
      per kind — the wallet service enforces that.

    * Boost items (Phase 2) will use `quantity` for remaining charges.

    Uniqueness on (student_id, store_item_id) prevents duplicate rows;
    a re-purchase (currently forbidden for cosmetics by service logic)
    would violate this constraint at DB level.
    """
    __tablename__ = "student_inventory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    store_item_id: Mapped[int] = mapped_column(
        ForeignKey("store_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # Denormalized so equip queries don't need to join `store_items`.
    kind: Mapped[StoreItemKind] = mapped_column(
        Enum(StoreItemKind, name="store_item_kind"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)

    acquired_via: Mapped[AcquiredVia] = mapped_column(
        Enum(AcquiredVia, name="inventory_acquired_via"),
        nullable=False,
        default=AcquiredVia.purchase,
        server_default=AcquiredVia.purchase.value,
    )
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "store_item_id", name="uq_inventory_student_item"),
        Index("ix_inventory_student_kind", "student_id", "kind"),
    )
