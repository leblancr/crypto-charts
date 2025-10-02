from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routers import auth, coins, watchlist
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="Crypto Dashboard API")

# Path to frontend/static folder
frontend_static_path = Path(__file__).parent.parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=frontend_static_path), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(coins.router, prefix="/coins", tags=["coins"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])

# Serve chart.html when you go to http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return FileResponse(Path("frontend/chart.html"))
