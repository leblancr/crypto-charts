from fastapi import APIRouter, Depends
from backend.fetch_prices import get_current_prices, get_historical_prices

router = APIRouter()

@router.get("/")
async def current_prices(symbols: str):
    """
    symbols: comma-separated list of coin symbols
    """
    coins = symbols.split(",")
    prices = await get_current_prices(coins)
    print("DEBUG:", prices)
    return prices

@router.get("/{symbol}/history")
async def history(symbol: str, days: int = 30):
    return await get_historical_prices(symbol, days)
