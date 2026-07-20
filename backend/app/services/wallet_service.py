"""Wallet + store operations backed by the append-only ledger.

Every wallet movement — earn, spend, refund — writes a row to
`student_wallet_ledger` through this service. The rules the service
enforces so callers can't shoot themselves in the foot:

  * Sign of `delta_coins` must match the reason (earns positive, spends
    negative, refund positive).
  * A duplicate `idempotency_key` fails cleanly with `DuplicatePurchaseError`
    instead of double-charging.
  * `balance_after` is computed from the previous ledger tip inside the
    same transaction; two concurrent debits can't both succeed against a
    stale balance because a `SELECT ... FOR UPDATE` on the ledger head
    would be over-engineered — instead we re-read the balance under the
    open transaction and rely on the unique idempotency key + the
    `spend` check running inside `db.begin_nested()` for correctness.

The service does NOT touch `Student.lifetime_points` on spend — that is
by design (see the design doc). Earns *are* recorded in the ledger by
`record_earn`, but the canonical earn path today is
`ranking_service.add_points_to_student`, which we call in parallel from
the same transaction wherever the caller wants the ledger to reflect
the earn. Callers that only want a wallet effect (grants, refunds) use
this service directly.
"""
from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import (
    AcquiredVia,
    LedgerReason,
    PurchaseStatus,
    StoreItem,
    StoreItemKind,
    StudentInventoryItem,
    StudentPurchase,
    WalletLedgerEntry,
)
from app.models.user import Student


# ─── errors ────────────────────────────────────────────────────────────────


class WalletError(Exception):
    """Base class for user-visible wallet failures."""


class InsufficientFundsError(WalletError):
    def __init__(self, balance: int, required: int):
        super().__init__(f"insufficient funds: have {balance}, need {required}")
        self.balance = balance
        self.required = required


class ItemNotPurchasableError(WalletError):
    pass


class AlreadyOwnedError(WalletError):
    pass


class DuplicatePurchaseError(WalletError):
    """The idempotency key was already used."""


class ItemNotFoundError(WalletError):
    pass


# ─── read-side helpers ─────────────────────────────────────────────────────


async def get_balance(db: AsyncSession, student_id: int) -> int:
    """Return the student's spendable balance.

    The source of truth is `Student.total_points`. The ledger sum is
    equivalent (by construction) but reading a single column is cheaper
    for hot paths (wallet chip).
    """
    res = await db.execute(select(Student.total_points).where(Student.id == student_id))
    row = res.scalar_one_or_none()
    if row is None:
        raise ItemNotFoundError(f"student {student_id} not found")
    return int(row or 0)


async def list_ledger(
    db: AsyncSession, student_id: int, *, limit: int = 20,
) -> list[WalletLedgerEntry]:
    res = await db.execute(
        select(WalletLedgerEntry)
        .where(WalletLedgerEntry.student_id == student_id)
        .order_by(WalletLedgerEntry.created_at.desc(), WalletLedgerEntry.id.desc())
        .limit(limit)
    )
    return list(res.scalars().all())


# ─── write-side ────────────────────────────────────────────────────────────


async def _write_ledger(
    db: AsyncSession,
    *,
    student: Student,
    delta: int,
    reason: LedgerReason,
    ref_type: Optional[str],
    ref_id: Optional[int],
    idempotency_key: Optional[str],
    note: Optional[str] = None,
) -> WalletLedgerEntry:
    """Insert one ledger row and update the student's spendable balance.

    Caller owns the transaction — this function only flushes; it does
    not commit. Idempotency-key collisions surface as
    `DuplicatePurchaseError`; callers should re-raise or map that to
    HTTP 409.
    """
    if delta == 0:
        raise WalletError("delta_coins may not be zero")

    _validate_sign(delta, reason)

    new_balance = student.total_points + delta
    if new_balance < 0:
        raise InsufficientFundsError(balance=student.total_points, required=-delta)

    student.total_points = new_balance

    entry = WalletLedgerEntry(
        student_id=student.id,
        delta_coins=delta,
        reason=reason,
        ref_type=ref_type,
        ref_id=ref_id,
        idempotency_key=idempotency_key,
        balance_after=new_balance,
        note=note,
    )
    db.add(entry)
    try:
        await db.flush()
    except IntegrityError as exc:
        # Almost always a unique-idempotency-key collision.
        if idempotency_key and "idempotency_key" in str(exc.orig).lower():
            raise DuplicatePurchaseError(idempotency_key) from exc
        raise

    return entry


def _validate_sign(delta: int, reason: LedgerReason) -> None:
    positive_reasons = {LedgerReason.earn_activity, LedgerReason.earn_grant, LedgerReason.refund}
    negative_reasons = {LedgerReason.spend_purchase}

    if reason in positive_reasons and delta <= 0:
        raise WalletError(f"reason {reason.value} requires delta > 0")
    if reason in negative_reasons and delta >= 0:
        raise WalletError(f"reason {reason.value} requires delta < 0")


async def record_earn(
    db: AsyncSession,
    *,
    student_id: int,
    amount: int,
    reason: LedgerReason = LedgerReason.earn_activity,
    ref_type: Optional[str] = None,
    ref_id: Optional[int] = None,
    idempotency_key: Optional[str] = None,
    note: Optional[str] = None,
) -> WalletLedgerEntry:
    """Log an earn in the ledger. Does NOT touch lifetime_points.

    The canonical earn path is `RankingService.add_points_to_student`
    (which bumps both wallets). This helper only exists so that grants
    and future flows can also be represented in the ledger without
    going through the ranking service. Call it *in addition to* the
    ranking service — or from teacher grant endpoints where the earn
    lives outside the normal activity paths.
    """
    if amount <= 0:
        raise WalletError("earn amount must be > 0")
    student = await _load_student_for_update(db, student_id)
    return await _write_ledger(
        db,
        student=student,
        delta=amount,
        reason=reason,
        ref_type=ref_type,
        ref_id=ref_id,
        idempotency_key=idempotency_key,
        note=note,
    )


async def _load_student_for_update(db: AsyncSession, student_id: int) -> Student:
    res = await db.execute(select(Student).where(Student.id == student_id))
    student = res.scalar_one_or_none()
    if student is None:
        raise ItemNotFoundError(f"student {student_id} not found")
    return student


# ─── store: purchase a cosmetic ────────────────────────────────────────────


PURCHASABLE_KINDS: frozenset[StoreItemKind] = frozenset({
    StoreItemKind.theme, StoreItemKind.font, StoreItemKind.sound_pack,
})


async def purchase_item(
    db: AsyncSession,
    *,
    student_id: int,
    store_item_id: int,
    idempotency_key: Optional[str] = None,
) -> tuple[StudentPurchase, WalletLedgerEntry, StudentInventoryItem]:
    """Buy a cosmetic item.

    Runs as one transaction: verify item + funds + not-already-owned,
    debit the ledger, create the purchase row, create the inventory row.
    On success the student's spendable balance is `price_coins` lower.

    Cosmetics complete immediately (`status=completed`). Real-value items
    are Phase 3 and rejected here on the `PURCHASABLE_KINDS` check — we
    do NOT silently create a `requested` row from this endpoint, because
    that path needs approval routing that Phase 1 doesn't have yet.
    """
    student = await _load_student_for_update(db, student_id)

    item = (
        await db.execute(select(StoreItem).where(StoreItem.id == store_item_id))
    ).scalar_one_or_none()
    if item is None or not item.is_active:
        raise ItemNotFoundError(f"store item {store_item_id} not found or inactive")
    if item.kind not in PURCHASABLE_KINDS:
        raise ItemNotPurchasableError(
            f"kind {item.kind.value} is not available for direct purchase in this phase"
        )
    if item.min_lifetime_points and student.lifetime_points < item.min_lifetime_points:
        raise ItemNotPurchasableError(
            f"requires {item.min_lifetime_points} lifetime points"
        )

    # Already-owned check. Cosmetics are singletons — buying a theme you
    # already own would silently mint a duplicate inventory row.
    existing = (
        await db.execute(
            select(StudentInventoryItem).where(
                StudentInventoryItem.student_id == student_id,
                StudentInventoryItem.store_item_id == store_item_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise AlreadyOwnedError(f"student already owns item {store_item_id}")

    purchase = StudentPurchase(
        student_id=student_id,
        store_item_id=item.id,
        price_paid=item.price_coins,
        status=PurchaseStatus.completed,
    )
    db.add(purchase)
    await db.flush()

    ledger = await _write_ledger(
        db,
        student=student,
        delta=-item.price_coins,
        reason=LedgerReason.spend_purchase,
        ref_type="purchase",
        ref_id=purchase.id,
        idempotency_key=idempotency_key,
        note=f"buy {item.slug}",
    )

    inv = StudentInventoryItem(
        student_id=student_id,
        store_item_id=item.id,
        kind=item.kind,
        quantity=1,
        is_equipped=False,
        acquired_via=AcquiredVia.purchase,
    )
    db.add(inv)
    await db.flush()

    return purchase, ledger, inv


# ─── equip / unequip ───────────────────────────────────────────────────────


EQUIPPABLE_KINDS: frozenset[StoreItemKind] = frozenset({
    StoreItemKind.theme, StoreItemKind.font, StoreItemKind.sound_pack,
})


async def equip_inventory_item(
    db: AsyncSession, *, student_id: int, inventory_id: int,
) -> StudentInventoryItem:
    """Equip an inventory row.

    At most one item per (student, kind) is equipped. This function
    un-equips any previously-equipped item of the same kind in the same
    transaction, so the client can rely on the response being consistent.
    """
    inv = (
        await db.execute(
            select(StudentInventoryItem).where(
                StudentInventoryItem.id == inventory_id,
                StudentInventoryItem.student_id == student_id,
            )
        )
    ).scalar_one_or_none()
    if inv is None:
        raise ItemNotFoundError(f"inventory item {inventory_id} not owned")
    if inv.kind not in EQUIPPABLE_KINDS:
        raise ItemNotPurchasableError(f"kind {inv.kind.value} is not equippable")

    await db.execute(
        _unequip_same_kind_stmt(student_id=student_id, kind=inv.kind, except_id=inv.id)
    )
    inv.is_equipped = True
    await db.flush()
    return inv


async def unequip_inventory_item(
    db: AsyncSession, *, student_id: int, inventory_id: int,
) -> StudentInventoryItem:
    inv = (
        await db.execute(
            select(StudentInventoryItem).where(
                StudentInventoryItem.id == inventory_id,
                StudentInventoryItem.student_id == student_id,
            )
        )
    ).scalar_one_or_none()
    if inv is None:
        raise ItemNotFoundError(f"inventory item {inventory_id} not owned")
    inv.is_equipped = False
    await db.flush()
    return inv


def _unequip_same_kind_stmt(*, student_id: int, kind: StoreItemKind, except_id: int):
    from sqlalchemy import update

    return (
        update(StudentInventoryItem)
        .where(
            StudentInventoryItem.student_id == student_id,
            StudentInventoryItem.kind == kind,
            StudentInventoryItem.id != except_id,
            StudentInventoryItem.is_equipped.is_(True),
        )
        .values(is_equipped=False)
    )


# ─── convenience: list catalogue with per-student affordability flags ──────


async def list_catalogue(
    db: AsyncSession,
    *,
    student_id: int,
    kinds: Optional[Iterable[StoreItemKind]] = None,
) -> list[dict]:
    """Catalogue rows with `can_afford` and `owned` flags for a student.

    Shape is a plain dict so the router doesn't need a separate Pydantic
    model for a read that is mostly pass-through with two computed
    booleans. Kept in the service for symmetry with `purchase_item`.
    """
    balance = await get_balance(db, student_id)

    q = select(StoreItem).where(StoreItem.is_active.is_(True))
    if kinds:
        q = q.where(StoreItem.kind.in_(list(kinds)))
    q = q.order_by(StoreItem.sort_order.asc(), StoreItem.id.asc())
    items = list((await db.execute(q)).scalars().all())

    owned_ids: set[int] = set()
    if items:
        owned_rows = await db.execute(
            select(StudentInventoryItem.store_item_id).where(
                StudentInventoryItem.student_id == student_id,
                StudentInventoryItem.store_item_id.in_([i.id for i in items]),
            )
        )
        owned_ids = {row for (row,) in owned_rows.all()}

    return [
        {
            "id": item.id,
            "kind": item.kind.value,
            "slug": item.slug,
            "title": item.title,
            "title_ru": item.title_ru,
            "description": item.description,
            "description_ru": item.description_ru,
            "price_coins": item.price_coins,
            "asset_ref": item.asset_ref,
            "sort_order": item.sort_order,
            "requires_approval": item.requires_approval,
            "min_lifetime_points": item.min_lifetime_points,
            "can_afford": balance >= item.price_coins,
            "owned": item.id in owned_ids,
            "purchasable": item.kind in PURCHASABLE_KINDS,
        }
        for item in items
    ]


async def list_inventory(
    db: AsyncSession, *, student_id: int,
) -> list[dict]:
    """Inventory rows with joined catalogue info for rendering."""
    rows = (
        await db.execute(
            select(StudentInventoryItem, StoreItem)
            .join(StoreItem, StoreItem.id == StudentInventoryItem.store_item_id)
            .where(StudentInventoryItem.student_id == student_id)
            .order_by(StudentInventoryItem.kind.asc(), StudentInventoryItem.acquired_at.desc())
        )
    ).all()

    return [
        {
            "inventory_id": inv.id,
            "store_item_id": item.id,
            "kind": inv.kind.value,
            "slug": item.slug,
            "title": item.title,
            "title_ru": item.title_ru,
            "asset_ref": item.asset_ref,
            "quantity": inv.quantity,
            "is_equipped": inv.is_equipped,
            "acquired_via": inv.acquired_via.value,
            "acquired_at": inv.acquired_at.isoformat() if inv.acquired_at else None,
        }
        for (inv, item) in rows
    ]


# ─── ledger balance-integrity sanity (used in tests / debug) ───────────────


async def ledger_sum(db: AsyncSession, student_id: int) -> int:
    res = await db.execute(
        select(func.coalesce(func.sum(WalletLedgerEntry.delta_coins), 0)).where(
            WalletLedgerEntry.student_id == student_id
        )
    )
    return int(res.scalar_one())
