"""
BIOCANVAS v2.0 — Configuration via environment variables.

Reads from environment variables (prefixed BIOCANVAS_) or falls back to defaults.
Supports .env files when python-dotenv is installed.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("biocanvas.config")

# Attempt to load .env file (optional dependency)
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
        logger.info("Loaded .env from %s", _env_path)
except ImportError:
    pass


def _get_str(key: str, default: str = "") -> str:
    return os.environ.get(f"BIOCANVAS_{key}", default)


def _get_int(key: str, default: int = 0) -> int:
    raw = os.environ.get(f"BIOCANVAS_{key}")
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid int for BIOCANVAS_%s=%r, using default=%d", key, raw, default)
        return default


def _get_float(key: str, default: float = 0.0) -> float:
    raw = os.environ.get(f"BIOCANVAS_{key}")
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        logger.warning("Invalid float for BIOCANVAS_%s=%r, using default=%s", key, raw, default)
        return default


def _get_bool(key: str, default: bool = False) -> bool:
    raw = os.environ.get(f"BIOCANVAS_{key}")
    if raw is None:
        return default
    return raw.lower() in ("true", "1", "yes")


def _get_list(key: str, default: Optional[List[str]] = None) -> List[str]:
    if default is None:
        default = []
    raw = os.environ.get(f"BIOCANVAS_{key}")
    if raw is None:
        return default
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    # Fallback: comma-separated
    return [s.strip() for s in raw.split(",") if s.strip()]


# ---------------------------------------------------------------------------
# Exported settings
# ---------------------------------------------------------------------------

# Server
HOST: str = _get_str("HOST", "127.0.0.1")
PORT: int = _get_int("PORT", 8000)
DEBUG: bool = _get_bool("DEBUG", False)
LOG_LEVEL: str = _get_str("LOG_LEVEL", "info")

# CORS
CORS_ORIGINS: List[str] = _get_list("CORS_ORIGINS", [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
])

# Rate limiting
RATE_LIMIT: int = _get_int("RATE_LIMIT", 10)
RATE_WINDOW: float = _get_float("RATE_WINDOW", 60.0)

# Docking
MAX_CONCURRENT_DOCKING: int = _get_int("MAX_CONCURRENT_DOCKING", 4)

# File upload
MAX_UPLOAD_SIZE: int = _get_int("MAX_UPLOAD_SIZE", 52_428_800)  # 50 MB
