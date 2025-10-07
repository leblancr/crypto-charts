from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Example connection strings:
# Local SQLite:
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
#
# Local Postgres:
# DATABASE_URL = "postgresql+asyncpg://rich:reddpos@localhost:5432/crypto_db"
#
# Remote Postgres with SSL:
DATABASE_URL = "postgresql+asyncpg://crypto_dashboard_user:reddcry@skyebeau.com:5432/crypto_db?ssl=require"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory for async sessions
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base model class
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
