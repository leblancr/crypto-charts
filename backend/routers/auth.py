# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.crud import create_user, authenticate_user
from backend.config import JWT_SECRET
from backend.database import get_db
from backend.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from passlib.hash import argon2

import jwt

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await authenticate_user(user.username, user.password, db)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"sub": db_user.username, "exp": datetime.utcnow() + timedelta(hours=12)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if username already exists
    result = await db.execute(select(User).filter_by(username=user.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # normalize and validate password
    password = str(user.password)
    if isinstance(password, bytes):
        password = password.decode("utf-8")
    if not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Password must be a string")

    if len(password.encode("utf-8")) > 72:
        password = password[:72]  # bcrypt hard limit

    # hash password
    hashed_password = argon2.hash(password)

    # create user
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    return {"msg": "User created"}

