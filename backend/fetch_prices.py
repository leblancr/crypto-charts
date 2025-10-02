# backend/fetch_prices.py
import httpx
from typing import List, Optional

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

async def get_historical_prices(symbol: str, days: str = "30", interval: Optional[str] = None):
    """
    symbol: "BTC" or "bitcoin"
    days: e.g. "30", "7", or "max"
    interval: optional, "daily" or "hourly" (CoinGecko handles granularity automatically)
    """
    coin_id = map_symbol_to_id(symbol)
    if not coin_id:
        return []

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    print("DEBUG historical request:", url, params)

    if interval:
        params["interval"] = interval

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            print("DEBUG historical response keys:", data.keys())
    except Exception as e:
        print("get_historical_prices error:", e)
        return []

    prices = data.get("prices", [])  # list of [timestamp_ms, price]
    out = []
    for ts, price in prices:
        # ensure JSON serializable types: timestamp as int (ms), price as float
        try:
            out.append({"timestamp": int(ts), "price": float(price)})
        except Exception:
            # skip malformed entries
            continue
    return out
