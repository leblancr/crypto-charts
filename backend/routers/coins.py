import httpx
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter()

@router.get("/current")
async def get_current_prices(symbols: str = Query(..., description="Comma-separated symbols, e.g. bitcoin,ethereum,ada")):
    """Return current USD prices for one or more coins"""
    coins = [s.strip().lower() for s in symbols.split(",") if s.strip()]
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(coins), "vs_currencies": "usd"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@router.get("/{symbol}/history")
async def get_historical_prices(symbol: str, days: str = "30", interval: Optional[str] = None):
    """Return historical chart data for a coin"""
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    if interval:
        params["interval"] = interval
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json()
    return [{"timestamp": ts, "price": price} for ts, price in data.get("prices", [])]

@router.get("/top50")
async def get_top_50():
    """Return top 50 coins by market cap"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1, "sparkline": False}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return [{"id": coin["id"], "symbol": coin["symbol"], "name": coin["name"]} for coin in resp.json()]
