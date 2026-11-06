"""Quota shield in the store: 500 wallet points, stock of at most 2, rating untouched, never equippable."""
import uuid

from sqlalchemy import select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.store import StoreItem, StoreItemKind, StudentInventoryItem
from app.models.user import Student

PRICE = 500


async def _student(async_client, *, wallet=1000, rating=1000):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"qs_{uid}", "email": f"qs_{uid}@example.com", "password": "securepass123"})
    assert reg.status_code == 201, reg.text
    sid = reg.json()["user"]["id"]
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        s.total_points, s.lifetime_points = wallet, rating
        await db.commit()
    return sid, {"Authorization": f"Bearer {create_access_token(subject=sid)}"}


async def _shield_id():
    async with AsyncSessionLocal() as db:
        item = (await db.execute(select(StoreItem).where(StoreItem.slug == "quota_shield"))).scalar_one_or_none()
        if item is None:
            item = StoreItem(slug="quota_shield", kind=StoreItemKind.boost, title="Norma himoyasi",
                             title_ru="Защита нормы", price_coins=PRICE, is_active=True,
                             asset_ref={"effect": "quota_shield", "max_owned": 2})
            db.add(item)
            await db.commit()
            await db.refresh(item)
        return item.id


async def _cosmetic_id():
    async with AsyncSessionLocal() as db:
        item = StoreItem(slug=f"theme.t_{uuid.uuid4().hex[:6]}", kind=StoreItemKind.theme, title="T",
                         price_coins=100, is_active=True, asset_ref={"tokens": {}})
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item.id


async def _buy(async_client, headers, item_id):
    return await async_client.post("/api/v1/store/purchase", headers=headers,
                                   json={"store_item_id": item_id, "idempotency_key": uuid.uuid4().hex})


async def _balances(sid):
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == sid))).scalar_one()
        return s.total_points, s.lifetime_points


async def _rows(sid, item_id):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(StudentInventoryItem).where(
            StudentInventoryItem.student_id == sid, StudentInventoryItem.store_item_id == item_id))).scalars().all()


async def test_buying_a_shield_costs_500_wallet_points_and_leaves_the_rating_alone(async_client):
    sid, h = await _student(async_client)
    item = await _shield_id()
    r = await _buy(async_client, h, item)
    assert r.status_code == 201, r.text
    assert await _balances(sid) == (1000 - PRICE, 1000)
    rows = await _rows(sid, item)
    assert len(rows) == 1 and rows[0].quantity == 1


async def test_a_second_shield_adds_to_the_same_row(async_client):
    sid, h = await _student(async_client)
    item = await _shield_id()
    assert (await _buy(async_client, h, item)).status_code == 201
    assert (await _buy(async_client, h, item)).status_code == 201
    rows = await _rows(sid, item)
    assert len(rows) == 1 and rows[0].quantity == 2
    assert await _balances(sid) == (0, 1000)


async def test_a_third_shield_is_refused_with_409_and_costs_nothing(async_client):
    sid, h = await _student(async_client, wallet=5000)
    item = await _shield_id()
    await _buy(async_client, h, item)
    await _buy(async_client, h, item)
    r = await _buy(async_client, h, item)
    assert r.status_code == 409
    assert await _balances(sid) == (5000 - 2 * PRICE, 1000)
    assert (await _rows(sid, item))[0].quantity == 2


async def test_a_used_up_shield_can_be_bought_again(async_client):
    sid, h = await _student(async_client)
    item = await _shield_id()
    assert (await _buy(async_client, h, item)).status_code == 201
    async with AsyncSessionLocal() as db:
        row = (await db.execute(select(StudentInventoryItem).where(
            StudentInventoryItem.student_id == sid, StudentInventoryItem.store_item_id == item))).scalar_one()
        row.quantity = 0
        await db.commit()
    assert (await _buy(async_client, h, item)).status_code == 201
    rows = await _rows(sid, item)
    assert len(rows) == 1 and rows[0].quantity == 1


async def test_not_enough_wallet_points_is_402(async_client):
    sid, h = await _student(async_client, wallet=PRICE - 1)
    r = await _buy(async_client, h, await _shield_id())
    assert r.status_code == 402
    assert await _balances(sid) == (PRICE - 1, 1000)


async def test_the_shield_is_listed_as_purchasable_and_cannot_be_equipped(async_client):
    sid, h = await _student(async_client)
    item = await _shield_id()
    listed = (await async_client.get("/api/v1/store/items", headers=h)).json()
    assert next(i for i in listed if i["id"] == item)["purchasable"] is True
    await _buy(async_client, h, item)
    inv_id = (await _rows(sid, item))[0].id
    r = await async_client.post(f"/api/v1/store/inventory/{inv_id}/equip", headers=h)
    assert 400 <= r.status_code < 500


async def test_cosmetics_are_still_one_per_student(async_client):
    sid, h = await _student(async_client)
    item = await _cosmetic_id()
    assert (await _buy(async_client, h, item)).status_code == 201
    assert (await _buy(async_client, h, item)).status_code == 409
