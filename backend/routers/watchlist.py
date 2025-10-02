from fastapi import APIRouter, Depends, HTTPException
from backend.crud import get_watchlist, add_to_watchlist, remove_from_watchlist
from backend.auth_utils import get_current_user

router = APIRouter()

@router.get("/")
async def read_watchlist(user=Depends(get_current_user)):
    return await get_watchlist(user.id)

@router.post("/{symbol}")
async def add_watchlist(symbol: str, user=Depends(get_current_user)):
    await add_to_watchlist(user.id, symbol)
    return {"msg": f"{symbol} added"}

@router.delete("/{symbol}")
async def remove_watchlist(symbol: str, user=Depends(get_current_user)):
    await remove_from_watchlist(user.id, symbol)
    return {"msg": f"{symbol} removed"}
