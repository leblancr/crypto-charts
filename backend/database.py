from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # adjust to your DB
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://rich:reddpos@localhost:5432/crypto_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
