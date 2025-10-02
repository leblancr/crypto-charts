# backend/auth_utils.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .crud import authenticate_user
from .db import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dummy current user function (replace with JWT logic later)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # For now, just return a test user or look up by token
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user
