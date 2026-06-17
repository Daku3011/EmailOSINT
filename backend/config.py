"""Application configuration loaded from environment variables.

Uses pydantic-settings for validated, typed configuration with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

SHERLOCK_PATH: str = os.getenv("SHERLOCK_PATH", "sherlock")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///reports.db")
DB_PATH: str = os.getenv("DB_PATH", "reports.db")

# Security: restrict CORS origins in production
_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:80")
ALLOWED_ORIGINS: list[str] = [o.strip() for o in _origins_raw.split(",") if o.strip()]

# Rate limiting
RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# External service timeouts (seconds)
HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "10"))
SHERLOCK_TIMEOUT: int = int(os.getenv("SHERLOCK_TIMEOUT", "30"))
