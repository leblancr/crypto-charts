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
