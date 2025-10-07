from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Example connection strings:
# Local SQLite:
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
#
# Local Postgres:
# DATABASE_URL = "postgresql+asyncpg://rich:reddpos@localhost:5432/crypto_db"
#
# Remote Postgres with SSL:
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://crypto_dashboard_user:reddcry@skyebeau.com:5432/crypto_db?ssl=require"
DATABASE_URL = SQLALCHEMY_DATABASE_URL

# For Alembic (psycopg2)
SQLALCHEMY_SYNC_DATABASE_URL = (
    SQLALCHEMY_DATABASE_URL
    .replace("+asyncpg", "+psycopg2")
    .replace("?ssl=require", "?sslmode=require")
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory for async sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base model class
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with SessionLocal() as session:
        yield session
