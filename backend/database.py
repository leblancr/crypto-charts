# FILE: backend/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

## ───────────────────────────────────────────────
# Load environment variables from .env

if os.getenv("APP_ENV") == "production":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://rich:reddpos@localhost:5432/crypto_charts",  # default local
)

print("🔍 Using DATABASE_URL:", DATABASE_URL)

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,   # ✅ prevents stale connections
    pool_recycle=180,     # recycle every 3 minutes
    future=True,
)

# Session factory (async)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Declarative base for models
Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session
