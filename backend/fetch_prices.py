# backend/services/fetch_prices.py
from typing import Optional, List, Dict, Any

import httpx
import requests, time
from fastapi import HTTPException

_price_cache = {}
_history_cache = {}
CACHE_TTL = 60  # seconds

# add more mappings if you need them
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    # extend as needed
}

def build_symbol_map(limit=200):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit, "page": 1}
    resp = requests.get(url, params=params, timeout=10)
    mapping = {}
    if resp.status_code == 200:
        for coin in resp.json():
            mapping[coin["symbol"].upper()] = coin["id"]
    return mapping

async def get_current_prices(symbols):
    ids = [map_symbol_to_id(s) for s in symbols if s]
    key = ",".join(sorted(ids))
    now = time.time()

    # 🔹 Return cached data if fresh
    if key in _price_cache and now - _price_cache[key]["time"] < CACHE_TTL:
        return _price_cache[key]["data"]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd", "include_24hr_change": "true"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            _price_cache[key] = {"time": now, "data": data}  # store in cache
            return data
    except Exception as e:
        print("get_current_prices error:", e)
        return {}

# Fetches from CoinGecko and returns [{ "timestamp": <ms>, "price": <float> }, ...]
async def get_historical_prices(coin_id, days="30", interval=None):
    key = (coin_id, days, interval)
    now = time.time()

    # 🔹 Return cached data if fresh
    if key in _history_cache and now - _history_cache[key]["time"] < CACHE_TTL:
        return _history_cache[key]["data"]

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    if interval:
        params["interval"] = interval

    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    payload = resp.json()
    prices = [{"timestamp": int(ts), "price": float(p)} for ts, p in payload.get("prices", [])]

    _history_cache[key] = {"time": now, "data": prices}  # store in cache
    return prices

def map_symbol_to_id(symbol: str) -> Optional[str]:
    if not symbol:
        return None
    s_upper = symbol.strip().upper()
    if s_upper in SYMBOL_TO_ID:
        return SYMBOL_TO_ID[s_upper]
    # assume the caller passed a full coingecko id already e.g. "bitcoin"
    return symbol.strip().lower()

# Build a larger symbol → id map on startup
SYMBOL_TO_ID = build_symbol_map()

