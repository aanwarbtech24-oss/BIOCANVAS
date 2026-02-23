"""
SQLite-backed persistent job store for BioCanvas.

Replaces the volatile in-memory `JOBS: Dict[str, dict]` with a durable
SQLite database. Jobs survive server restarts.
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("biocanvas.job_store")

# ---------------------------------------------------------------------------
# DB path — stored alongside docking output files
# ---------------------------------------------------------------------------

_DB_DIR = Path(__file__).resolve().parent.parent / "docking_jobs"
_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _DB_DIR / "jobs.db"

# ---------------------------------------------------------------------------
# Thread-local connections (sqlite3 objects are not shareable across threads)
# ---------------------------------------------------------------------------

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """Return a thread-local SQLite connection, creating one if needed."""
    conn: Optional[sqlite3.Connection] = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        _local.conn = conn
    return conn


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Create the jobs table if it does not exist."""
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id       TEXT PRIMARY KEY,
            status       TEXT NOT NULL DEFAULT 'queued',
            submitted_at REAL NOT NULL,
            completed_at REAL,
            result       TEXT,   -- JSON blob
            error        TEXT,
            lipinski     TEXT,   -- JSON blob
            poses        TEXT    -- JSON blob
        )
        """
    )
    conn.commit()
    logger.info("Job store initialised (SQLite @ %s)", DB_PATH)


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------


def create_job(job_id: str) -> dict:
    """Insert a new job with status='queued'. Returns the row as dict."""
    now = datetime.now().timestamp()
    conn = _get_conn()
    conn.execute(
        "INSERT INTO jobs (job_id, status, submitted_at) VALUES (?, 'queued', ?)",
        (job_id, now),
    )
    conn.commit()
    return _row_to_dict(job_id)


def get_job(job_id: str) -> Optional[dict]:
    """Retrieve a single job by id, or None."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    if row is None:
        return None
    return _row_to_dict_from_row(row)


def update_job(job_id: str, **fields) -> None:
    """Update arbitrary columns on a job row.

    Accepted fields: status, completed_at, result, error, lipinski, poses.
    JSON-serialisable values for result / lipinski / poses are auto-encoded.
    """
    conn = _get_conn()
    allowed = {"status", "completed_at", "result", "error", "lipinski", "poses"}
    sets: List[str] = []
    vals: list = []
    for key, val in fields.items():
        if key not in allowed:
            continue
        if key in ("result", "lipinski", "poses") and val is not None:
            val = json.dumps(val)
        sets.append(f"{key} = ?")
        vals.append(val)

    if not sets:
        return

    vals.append(job_id)
    conn.execute(f"UPDATE jobs SET {', '.join(sets)} WHERE job_id = ?", vals)
    conn.commit()


def list_jobs(limit: int = 100) -> List[dict]:
    """Return most-recent jobs, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM jobs ORDER BY submitted_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [_row_to_dict_from_row(r) for r in rows]


def count_by_status(status: str) -> int:
    """Count jobs with a given status (e.g. 'running')."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM jobs WHERE status = ?", (status,)
    ).fetchone()
    return row["cnt"] if row else 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(job_id: str) -> dict:
    """Fetch a row by job_id and convert to plain dict."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    if row is None:
        return {}
    return _row_to_dict_from_row(row)


def _row_to_dict_from_row(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, JSON-parsing blob columns."""
    d: Dict = dict(row)
    for col in ("result", "lipinski", "poses"):
        if d.get(col) and isinstance(d[col], str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return d
