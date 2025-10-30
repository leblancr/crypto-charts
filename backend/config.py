# FILE: backend/config.py
from dotenv import load_dotenv
import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise SystemExit("❌ DATABASE_URL missing after loading .env")

# ✅ Add this:
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")

print(f"🔍 Using DATABASE_URL: {DATABASE_URL}")
print(f"🔑 Loaded JWT_SECRET: {JWT_SECRET[:4]}****")  # optional partial print for safety
