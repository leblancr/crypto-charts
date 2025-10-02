from fastapi import FastAPI
from backend.routers import auth, coins, watchlist

app = FastAPI(title="Crypto Dashboard API")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])

