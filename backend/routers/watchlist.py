from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import Watchlist

router = APIRouter()

# # Manual overrides for common tickers
# OVERRIDES = {
#     "btc": "bitcoin",
#     "eth": "ethereum",
#     "ada": "cardano"
# }

# add coin to watchlist
@router.post("/{user_id}/{coingecko_id}")
async def add_coin_to_watchlist(
    user_id: int, coingecko_id: str, db: AsyncSession = Depends(get_db)
):
    coingecko_id = coingecko_id.lower()
    result = await db.execute(
        select(Watchlist).filter_by(user_id=user_id, coingecko_id=coingecko_id)
    )
    existing = result.scalars().first()

    if existing:
        return {"detail": f"{coingecko_id.upper()} already in watchlist"}

    item = Watchlist(user_id=user_id, coingecko_id=coingecko_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"detail": f"{coingecko_id.upper()} added"}

@router.get("/{user_id}")
async def get_watchlist(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Watchlist).filter_by(user_id=user_id))
    items = result.scalars().all()
    return [
        {
            "id": item.id,                # database row id
            "coingecko_id": item.coingecko_id  # coin id for CoinGecko API
        }
        for item in items
    ]

@router.delete("/{user_id}/{coingecko_id}")
async def remove_coin_from_watchlist(
    user_id: int, coingecko_id: str, db: AsyncSession = Depends(get_db)
):
    coingecko_id = coingecko_id.lower()
    result = await db.execute(
        select(Watchlist).filter_by(user_id=user_id, coingecko_id=coingecko_id)
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{coingecko_id.upper()} not in watchlist")

    await db.delete(item)
    await db.commit()
    return {"detail": f"{coingecko_id.upper()} removed"}

#
async def resolve_to_id(symbol: str) -> str:
    sym = symbol.lower()
    if sym in OVERRIDES:
        return OVERRIDES[sym]
    url = "https://api.coingecko.com/api/v3/coins/list"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        for coin in resp.json():
            if coin["symbol"].lower() == sym:
                return coin["id"]
    return None


