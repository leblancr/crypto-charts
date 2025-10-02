# backend/models.py
from sqlalchemy import Column, String, Float, DateTime, Integer, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CryptoPrice(Base):
    __tablename__ = "crypto_prices"

    coin = Column(String, nullable=False)             # e.g. "BTC"
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    price = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("coin", "timestamp", name="crypto_pk"),
    )

# -------------------------------
# Add User model for auth
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coin = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
