from sqlalchemy.orm import Session
from .models import User, Watchlist, CryptoPrice
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Users
def create_user(db: Session, username: str, password: str):
    hashed = pwd_context.hash(password)
    user = User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None

# Watchlist
def get_watchlist(db: Session, user_id: int):
    return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

def add_to_watchlist(db: Session, user_id: int, coin: str):
    coin = coin.lower()
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.coin == coin
    ).first()

    if existing:
        return {"detail": f"{coin.upper()} already in watchlist"}

    item = Watchlist(user_id=user_id, coin=coin)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"detail": f"{coin.upper()} added"}

def remove_from_watchlist(db: Session, user_id: int, coin: str):
    coin = coin.lower()
    item = db.query(Watchlist).filter(
        Watchlist.user_id == user_id,
        Watchlist.coin == coin
    ).first()

    if not item:
        return {"detail": f"{coin.upper()} not in watchlist"}

    db.delete(item)
    db.commit()
    return {"detail": f"{coin.upper()} removed"}
