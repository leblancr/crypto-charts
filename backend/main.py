from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import watchlist, coins, auth

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
# Grouped resources
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])

# Global actions (no prefix)
app.include_router(auth.router, tags=["auth"])

# ✅ Serve compiled Svelte from dist/
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
