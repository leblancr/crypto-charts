from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.crud import create_user, authenticate_user
from backend.config import JWT_SECRET
import jwt
from datetime import datetime, timedelta

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Signup
@router.post("/signup")
async def signup(user: UserCreate):
    if await create_user(user.username, user.password):
        return {"msg": "User created"}
    raise HTTPException(status_code=400, detail="User already exists")


# Login
@router.post("/login")
async def login(user: UserLogin):
    db_user = await authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": db_user.username, "exp": datetime.utcnow() + timedelta(hours=12)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
