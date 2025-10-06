from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Watchlist
import httpx
import asyncio

router = APIRouter()

# # Manual overrides for common tickers
# OVERRIDES = {
#     "btc": "bitcoin",
#     "eth": "ethereum",
#     "ada": "cardano"
# }

# add coin to watchlist
@router.post("/{user_id}/{coin_id}")
def add_coin_to_watchlist(user_id: int, coin_id: str, db: Session = Depends(get_db)):
    exists = db.query(Watchlist).filter_by(user_id=user_id, coingecko_id=coin_id).first()
    if not exists:
        db.add(Watchlist(
            user_id=user_id,
            ticker=coin_id.upper(),   # display
            coingecko_id=coin_id      # actual CoinGecko ID
        ))
        db.commit()
    return get_watchlist(user_id, db)

@router.get("/{user_id}")
def get_watchlist(user_id: int, db: Session = Depends(get_db)):
    items = db.query(Watchlist).filter_by(user_id=user_id).all()
    return [{"ticker": item.ticker, "id": item.coingecko_id} for item in items]


@router.delete("/{user_id}/{coin_id}")
def remove_coin_from_watchlist(user_id: int, coin_id: str, db: Session = Depends(get_db)):
    # coin_id here is the CoinGecko ID (e.g. "bitcoin")
    item = db.query(Watchlist).filter_by(user_id=user_id, coingecko_id=coin_id).first()
    if item:
        db.delete(item)
        db.commit()
    return get_watchlist(user_id, db)
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


