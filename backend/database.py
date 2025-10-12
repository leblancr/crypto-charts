# FILE: backend/db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Local Postgres
# DATABASE_URL = "postgresql+asyncpg://rich:reddpos@localhost:5432/crypto_db"

# Remote Postgres with sslmode
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://crypto_dashboard_user:reddcry@skyebeau.com:5432/crypto_db?sslmode=require"

#
DATABASE_URL = SQLALCHEMY_DATABASE_URL

# Optional: sync URL (for Alembic migrations)
SQLALCHEMY_SYNC_DATABASE_URL = (
    SQLALCHEMY_DATABASE_URL
    .replace("+asyncpg", "+psycopg2")
    .replace("?ssl=require", "?sslmode=require")
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
