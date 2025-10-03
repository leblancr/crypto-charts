# backend/services/fetch_prices.py
from typing import Optional, List, Dict, Any
import requests
from fastapi import HTTPException

# add more mappings if you need them
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    # extend as needed
}

def map_symbol_to_id(symbol: str) -> Optional[str]:
    if not symbol:
        return None
    s_upper = symbol.strip().upper()
    if s_upper in SYMBOL_TO_ID:
        return SYMBOL_TO_ID[s_upper]
    # assume the caller passed a full coingecko id already e.g. "bitcoin"
    return symbol.strip().lower()

async def get_current_prices(symbols: List[str]):
    ids = [map_symbol_to_id(s) for s in symbols]
    ids = [i for i in ids if i]
    if not ids:
        return {}

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        # log if you want; return empty dict on failure
        print("get_current_prices error:", e)
        return {}

# Fetches from CoinGecko and returns [{ "timestamp": <ms>, "price": <float> }, ...]
async def get_historical_prices(coin_id: str, days: str = "30", interval: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    if interval:
        params["interval"] = interval

    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", 502)
        detail = getattr(getattr(e, "response", None), "text", str(e))
        raise HTTPException(status_code=status, detail=detail)

    if resp.status_code != 200:
        # Surface the actual upstream error (e.g., 429 Too Many Requests)
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    payload = resp.json()
    prices = payload.get("prices", [])
    return [{"timestamp": int(ts), "price": float(p)} for ts, p in prices]