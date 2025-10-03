from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.crud import get_watchlist, add_to_watchlist, remove_from_watchlist
from backend.database import get_db

router = APIRouter()
TEST_USER_ID = 1  # hard-coded for testing

@router.get("/")
def read_watchlist(db: Session = Depends(get_db)):
    return get_watchlist(db, TEST_USER_ID)

@router.post("/{symbol}")
def add_watchlist(symbol: str, db: Session = Depends(get_db)):
    return add_to_watchlist(db, TEST_USER_ID, symbol)

@router.delete("/{symbol}")
def remove_watchlist(symbol: str, db: Session = Depends(get_db)):
    return remove_from_watchlist(db, TEST_USER_ID, symbol)
