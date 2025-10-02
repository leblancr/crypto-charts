# backend/routes.py
from fastapi import APIRouter, Query
from typing import List, Optional
from backend.fetch_prices import get_current_prices, get_historical_prices

router = APIRouter()

@router.get("/")
async def current_prices(symbols: str = Query(..., description="Comma-separated symbols, e.g. BTC,ETH or bitcoin,ethereum")):
    coins = [s.strip() for s in symbols.split(",") if s.strip()]
    return await get_current_prices(coins)

@router.get("/{symbol}/history")
async def history(symbol: str, days: str = "30", interval: Optional[str] = None):
    """
    days: numeric string like "30" or "7", or "max"
    interval: optional, "daily" or "hourly"
    """
    return await get_historical_prices(symbol, days, interval)
