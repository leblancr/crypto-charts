from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    coin = Column(String, index=True)

class CryptoPrice(Base):
    __tablename__ = "crypto_prices"
    coin = Column(String, primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    price = Column(Float, nullable=False)
