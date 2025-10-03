# backend/routes.py
import requests
from fastapi import APIRouter, Query, HTTPException
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

@router.get("/top50")
async def get_top_50():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch top coins")
    return [{"id": coin["id"], "symbol": coin["symbol"], "name": coin["name"]} for coin in resp.json()]

# Endpoint: GET /coins/{symbol}/history — historical prices for charts
@router.get("/{symbol}/history")
async def history(symbol: str, days: str = "30", interval: Optional[str] = None):
    coin_id = resolve_coin(symbol)  # your existing resolver
    try:
        return await get_historical_prices(coin_id, days, interval)
    except HTTPException:
        # already has correct status/detail from get_historical_prices
        raise

# Endpoint: GET /coins/{symbol}/price — live price for header
@router.get("/{symbol}/price")
async def price_endpoint(symbol: str):
    import requests
    from fastapi import HTTPException

    # If you already have resolve_coin in this file, keep using that.
    coin_id = resolve_coin(symbol)

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}

    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", 502)
        detail = getattr(getattr(e, "response", None), "text", str(e))
        raise HTTPException(status_code=status, detail=detail)

    if resp.status_code != 200:
        # Surface upstream error (e.g., 429 Too Many Requests)
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    payload = resp.json()
    coin = payload.get(coin_id)
    if not coin or "usd" not in coin:
        # Upstream said OK but gave no price; make it explicit
        raise HTTPException(status_code=502, detail=f"Upstream empty price payload for {coin_id}")

    # Return under the original symbol key so frontend uses data[symbol.toLowerCase()]
    return {symbol.lower(): coin}
