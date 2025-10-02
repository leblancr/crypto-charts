# fetch_prices.py
import requests
from .db import SessionLocal
from .models import CryptoPrice
import datetime

coins = ["bitcoin", "ethereum", "cardano"]
session = SessionLocal()

# mapping symbols to CoinGecko IDs
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
}

# backend/fetch_prices.py
async def get_current_prices(symbols):
    ids = [SYMBOL_TO_ID.get(s.upper()) for s in symbols if SYMBOL_TO_ID.get(s.upper())]
    if not ids:
        return {}  # no valid coins

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(coins), "vs_currencies": "usd"}
    resp = requests.get(url, params=params)
    return resp.json()  # e.g., { "bitcoin": {"usd": 27900}, "ethereum": {"usd": 1800} }

async def get_historical_prices(coin: str, days: int = 30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    resp = requests.get(url, params=params)
    data = resp.json()
    # data["prices"] is a list of [timestamp, price]
    return [{"timestamp": ts, "price": price} for ts, price in data.get("prices", [])]

session.commit()
session.close()
