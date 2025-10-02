# backend/crud.py
from sqlalchemy.orm import Session
from .models import CryptoPrice, User
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Add a coin to watchlist
def add_to_watchlist(db: Session, user_id: int, coin: str):
    item = Watchlist(user_id=user_id, coin=coin)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None

# Create a new user
def create_user(db: Session, username: str, password: str):
    hashed = pwd_context.hash(password)
    user = User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_history(db: Session, coin: str, interval: str = "day"):
    """
    Fetch historical prices for a coin, aggregated by interval.
    interval: 'minute', 'day', 'week'
    """
    query = db.query(CryptoPrice).filter(CryptoPrice.coin == coin)

    if interval == "minute":
        # last 24 hours
        since = datetime.utcnow() - timedelta(hours=24)
    elif interval == "day":
        # last 90 days
        since = datetime.utcnow() - timedelta(days=90)
    elif interval == "week":
        # last 52 weeks
        since = datetime.utcnow() - timedelta(weeks=52)
    else:
        since = datetime(1970,1,1)

    query = query.filter(CryptoPrice.timestamp >= since).order_by(CryptoPrice.timestamp)
    return query.all()

# Get a user's watchlist
def get_watchlist(db: Session, user_id: int):
    return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

# Remove a coin from watchlist
def remove_from_watchlist(db: Session, user_id: int, coin: str):
    item = db.query(Watchlist).filter(Watchlist.user_id==user_id, Watchlist.coin==coin).first()
    if item:
        db.delete(item)
        db.commit()
    return item
