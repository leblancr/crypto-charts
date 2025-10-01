from fastapi import FastAPI
from backend.services import get_crypto_prices
from fastapi.responses import HTMLResponse

app = FastAPI(title="FastAPI Crypto API")

@app.get("/api/prices")
async def prices():
    data = await get_crypto_prices()
    return {"prices": data}


@app.get("/", response_class=HTMLResponse)
async def root():
    data = await get_crypto_prices()
    html_content = "<h1>Crypto Prices</h1><ul>"
    for coin, price in data.items():
        html_content += f"<li><b>{coin.title()}</b>: {price}</li>"
    html_content += "</ul>"
    return html_content
