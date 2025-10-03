# backend/routes.py
import requests
from fastapi import APIRouter, Query
from typing import List, Optional
from backend.fetch_prices import get_current_prices, get_historical_prices

router = APIRouter()

COIN_MAP = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "ada": "cardano",
    "cardano": "cardano"
}

def resolve_coin(symbol: str) -> str:
    return COIN_MAP.get(symbol.lower(), symbol.lower())


@router.get("/all")
async def all_coins():
    resp = requests.get("https://api.coingecko.com/api/v3/coins/list")
    return resp.json()

@router.get("/")
async def current_prices(symbols: str = Query(..., description="Comma-separated symbols, e.g. BTC,ETH or bitcoin,ethereum")):
    coins = [s.strip() for s in symbols.split(",") if s.strip()]
    return await get_current_prices(coins)

@router.get("/{symbol}/price")
async def get_price(symbol: str):
    import requests
    coin_id = resolve_coin(symbol)
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return {symbol.lower(): data.get(coin_id)}

@router.get("/{symbol}/history")
async def history(symbol: str, days: str = "30", interval: Optional[str] = None):
    """
    days: numeric string like "30" or "7", or "max"
    interval: optional, "daily" or "hourly"
    """
    return await get_historical_prices(symbol, days, interval)
