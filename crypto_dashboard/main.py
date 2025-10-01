from fastapi import FastAPI
from crypto_dashboard.services import get_crypto_prices

app = FastAPI(title="FastAPI Crypto API")

@app.get("/api/prices")
async def prices():
    data = await get_crypto_prices()
    return {"prices": data}
