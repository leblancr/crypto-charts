from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import watchlist, coins
import os

app = FastAPI()

# Include your existing API router
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])

# Mount the static folder at /static
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve index.html at root
@app.get("/")
async def root():
    return FileResponse(os.path.join("frontend", "index.html"))
