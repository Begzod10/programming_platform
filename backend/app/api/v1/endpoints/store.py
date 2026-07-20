"""Store endpoints — Phase 1 of the points-spending economy.

Student-facing:

    GET  /store/items                 — catalogue with per-student flags
    GET  /store/wallet                — coin balance + recent ledger
    POST /store/purchase              — buy a cosmetic (idempotent)
    GET  /store/inventory             — owned items
    POST /store/inventory/{id}/equip  — equip a theme / font / sound pack
    POST /store/inventory/{id}/unequip

All routes require the student role. Teacher/admin management + Phase-3
approval flow live in a separate teacher-scoped router (added later).
"""
from __future__ import annotations

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_instructor, get_current_student, get_db
from app.models.store import LedgerReason, StoreItemKind
from app.models.user import Student
from app.services import wallet_service


router = APIRouter()


# ─── schemas ───────────────────────────────────────────────────────────────


class StoreItemRead(BaseModel):
    id: int
    kind: str
    slug: str
    title: str
    title_ru: Optional[str] = None
    description: Optional[str] = None
    description_ru: Optional[str] = None
    price_coins: int
    asset_ref: Optional[dict] = None
    sort_order: int
    requires_approval: bool
    min_lifetime_points: Optional[int] = None
    can_afford: bool
    owned: bool
    purchasable: bool


class LedgerEntryRead(BaseModel):
    id: int
    delta_coins: int
    reason: str
    ref_type: Optional[str]
    ref_id: Optional[int]
    balance_after: int
    note: Optional[str]
    created_at: str


class WalletRead(BaseModel):
    balance_coins: int
    lifetime_points: int
    recent: List[LedgerEntryRead]


class InventoryItemRead(BaseModel):
    inventory_id: int
    store_item_id: int
    kind: str
    slug: str
    title: str
    title_ru: Optional[str] = None
    asset_ref: Optional[dict] = None
    quantity: int
    is_equipped: bool
    acquired_via: str
    acquired_at: Optional[str]


class PurchaseRequest(BaseModel):
    store_item_id: int
    # Client-supplied idempotency key. Anything unique per intent works
    # (a uuid4 is ideal). Optional — omit for one-off flows where a
    # duplicate submit is acceptable.
    idempotency_key: Optional[str] = Field(default=None, max_length=120)


class PurchaseResponse(BaseModel):
    purchase_id: int
    price_paid: int
    balance_after: int
    inventory_id: int
    equipped: bool


class GrantRequest(BaseModel):
    # If omitted, the grant lands on the calling teacher — handy for
    # smoke-testing the store from a teacher account before Phase 1
    # opens to students. Required once the endpoint is used to reward
    # a specific student.
    student_id: Optional[int] = None
    amount: int = Field(..., gt=0, le=1_000_000)
    note: Optional[str] = Field(default=None, max_length=500)


class GrantResponse(BaseModel):
    student_id: int
    amount: int
    balance_after: int
    ledger_id: int


# ─── helpers ───────────────────────────────────────────────────────────────


def _parse_kind(kind: Optional[str]) -> Optional[StoreItemKind]:
    if not kind:
        return None
    try:
        return StoreItemKind(kind)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown store kind: {kind!r}",
        )


# ─── catalogue ─────────────────────────────────────────────────────────────


@router.get("/items", response_model=List[StoreItemRead])
async def list_items(
    kind: Optional[str] = Query(
        None, description="Filter by store item kind (theme, font, sound_pack)",
    ),
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> List[StoreItemRead]:
    filter_kind = _parse_kind(kind)
    kinds = [filter_kind] if filter_kind else None
    rows = await wallet_service.list_catalogue(db, student_id=student.id, kinds=kinds)
    return [StoreItemRead(**row) for row in rows]


# ─── wallet ────────────────────────────────────────────────────────────────


@router.get("/wallet", response_model=WalletRead)
async def get_wallet(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> WalletRead:
    balance = await wallet_service.get_balance(db, student.id)
    entries = await wallet_service.list_ledger(db, student.id, limit=limit)
    return WalletRead(
        balance_coins=balance,
        lifetime_points=int(student.lifetime_points or 0),
        recent=[
            LedgerEntryRead(
                id=e.id,
                delta_coins=e.delta_coins,
                reason=e.reason.value,
                ref_type=e.ref_type,
                ref_id=e.ref_id,
                balance_after=e.balance_after,
                note=e.note,
                created_at=e.created_at.isoformat() if e.created_at else "",
            )
            for e in entries
        ],
    )


# ─── purchase ──────────────────────────────────────────────────────────────


@router.post("/purchase", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def purchase(
    body: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> PurchaseResponse:
    try:
        purchase, ledger, inv = await wallet_service.purchase_item(
            db,
            student_id=student.id,
            store_item_id=body.store_item_id,
            idempotency_key=body.idempotency_key,
        )
    except wallet_service.ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except wallet_service.AlreadyOwnedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except wallet_service.DuplicatePurchaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="idempotency_key already used",
        ) from exc
    except wallet_service.InsufficientFundsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc),
        ) from exc
    except wallet_service.ItemNotPurchasableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await db.commit()
    return PurchaseResponse(
        purchase_id=purchase.id,
        price_paid=purchase.price_paid,
        balance_after=ledger.balance_after,
        inventory_id=inv.id,
        equipped=inv.is_equipped,
    )


# ─── inventory ─────────────────────────────────────────────────────────────


@router.get("/inventory", response_model=List[InventoryItemRead])
async def list_inventory(
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> List[InventoryItemRead]:
    rows = await wallet_service.list_inventory(db, student_id=student.id)
    return [InventoryItemRead(**row) for row in rows]


@router.post("/inventory/{inventory_id}/equip", response_model=InventoryItemRead)
async def equip(
    inventory_id: int,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> InventoryItemRead:
    try:
        inv = await wallet_service.equip_inventory_item(
            db, student_id=student.id, inventory_id=inventory_id,
        )
    except wallet_service.ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except wallet_service.ItemNotPurchasableError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await db.commit()
    # Re-read inventory for a fresh, joined view.
    rows = [
        row for row in await wallet_service.list_inventory(db, student_id=student.id)
        if row["inventory_id"] == inv.id
    ]
    if not rows:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="inventory readback failed")
    return InventoryItemRead(**rows[0])


# ─── teacher grant (Phase 1 test hatch + Phase 2 reward hook) ──────────────


@router.post("/grant", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
async def grant_coins(
    body: GrantRequest,
    db: AsyncSession = Depends(get_db),
    instructor: Student = Depends(get_current_instructor),
) -> GrantResponse:
    """Teacher-only: mint coins for a student (or self).

    Writes a `earn_grant` row to the ledger, which credits the target's
    spendable balance. Does NOT touch `lifetime_points` — grants are
    fun-money, not earned status.
    """
    target_id = body.student_id or instructor.id
    try:
        entry = await wallet_service.record_earn(
            db,
            student_id=target_id,
            amount=body.amount,
            reason=LedgerReason.earn_grant,
            ref_type="grant",
            ref_id=instructor.id,
            note=body.note or f"grant by teacher {instructor.username}",
        )
    except wallet_service.ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    await db.commit()
    return GrantResponse(
        student_id=target_id,
        amount=body.amount,
        balance_after=entry.balance_after,
        ledger_id=entry.id,
    )


@router.post("/inventory/{inventory_id}/unequip", response_model=InventoryItemRead)
async def unequip(
    inventory_id: int,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
) -> InventoryItemRead:
    try:
        inv = await wallet_service.unequip_inventory_item(
            db, student_id=student.id, inventory_id=inventory_id,
        )
    except wallet_service.ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    await db.commit()
    rows = [
        row for row in await wallet_service.list_inventory(db, student_id=student.id)
        if row["inventory_id"] == inv.id
    ]
    if not rows:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="inventory readback failed")
    return InventoryItemRead(**rows[0])
