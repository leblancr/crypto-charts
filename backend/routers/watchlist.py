from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Watchlist

router = APIRouter()

@router.get("/{user_id}")
def get_watchlist(user_id: int, db: Session = Depends(get_db)):
    items = db.query(Watchlist).filter_by(user_id=user_id).all()
    return [item.coin for item in items]

@router.post("/{user_id}/{coin}")
def add_coin(user_id: int, coin: str, db: Session = Depends(get_db)):
    exists = db.query(Watchlist).filter_by(user_id=user_id, coin=coin).first()
    if not exists:
        db.add(Watchlist(user_id=user_id, coin=coin))
        db.commit()
    return get_watchlist(user_id, db)

@router.delete("/{user_id}/{coin}")
def remove_coin(user_id: int, coin: str, db: Session = Depends(get_db)):
    item = db.query(Watchlist).filter_by(user_id=user_id, coin=coin).first()
    if item:
        db.delete(item)
        db.commit()
    return get_watchlist(user_id, db)

# @router.get("/watchlist")
# async def get_watchlist():
#     # Example: fetch coins saved in DB
#     coins = db.query(Watchlist).all()
#     coin_ids = [c.symbol for c in coins]
#
#     if not coin_ids:
#         return []
#
#     # Get live prices for these coins
#     url = "https://api.coingecko.com/api/v3/simple/price"
#     params = {"ids": ",".join(coin_ids), "vs_currencies": "usd"}
#     async with httpx.AsyncClient() as client:
#         resp = await client.get(url, params=params)
#         prices = resp.json()
#
#     return [
#         {"symbol": coin, "price": prices.get(coin, {}).get("usd", None)}
#         for coin in coin_ids
#     ]
