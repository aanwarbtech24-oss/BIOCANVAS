"""
BIOCANVAS v2.0 — FastAPI Server
Serves molecule libraries, orchestrates docking jobs, and provides health checks.

Sprint 1 Fixes Applied:
- S1: CORS with explicit origins (no wildcard)
- B1: SQLite job persistence (via job_store.py)
- B3: ThreadPoolExecutor with semaphore to limit concurrent docking jobs
"""

import asyncio
import json
import logging
import shutil
import time
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from backend.docking_engine import DockingEngine
except Exception:
    DockingEngine = None  # type: ignore[misc,assignment]

try:
    from backend.job_store import init_db, create_job, get_job, update_job, count_by_status
except Exception:
    init_db = None  # type: ignore[misc,assignment]

# ---------------------------------------------------------------------------
# Paths & Logger
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WORK_DIR = Path("docking_jobs")
WORK_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("biocanvas")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S"))
    logger.addHandler(_h)

# ---------------------------------------------------------------------------
# Docking engine (optional — viewer-only mode without rdkit/meeko)
# ---------------------------------------------------------------------------

engine = None
if DockingEngine is not None:
    try:
        engine = DockingEngine(work_dir=str(WORK_DIR))
        logger.info("DockingEngine ready")
    except Exception as exc:
        logger.warning("DockingEngine unavailable: %s", exc)
else:
    logger.warning("DockingEngine not installed (rdkit/meeko) — viewer-only mode")

# ---------------------------------------------------------------------------
# SQLite job persistence (primary) or in-memory fallback
# ---------------------------------------------------------------------------

_USE_SQLITE = init_db is not None
if _USE_SQLITE:
    try:
        init_db()
        logger.info("SQLite job store ready")
    except Exception as exc:
        logger.warning("SQLite init failed, falling back to in-memory: %s", exc)
        _USE_SQLITE = False

# In-memory fallback (only used if SQLite fails)
JOBS: Dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Rate limiter — simple token-bucket per IP for /dock
# ---------------------------------------------------------------------------

_RATE_LIMIT = 10        # max requests …
_RATE_WINDOW = 60.0     # … per window (seconds)
_rate_buckets: Dict[str, list] = defaultdict(list)


def _check_rate_limit(ip: str) -> bool:
    """Return True if request is allowed, False if rate-limited."""
    now = time.time()
    bucket = _rate_buckets[ip]
    # Prune old entries
    _rate_buckets[ip] = [t for t in bucket if now - t < _RATE_WINDOW]
    if len(_rate_buckets[ip]) >= _RATE_LIMIT:
        return False
    _rate_buckets[ip].append(now)
    return True

# ---------------------------------------------------------------------------
# Bug B3 Fix: Thread Pool Executor to limit concurrent docking jobs
# ---------------------------------------------------------------------------
_MAX_CONCURRENT_DOCKING = 4  # Maximum concurrent docking jobs
_docking_executor = ThreadPoolExecutor(max_workers=_MAX_CONCURRENT_DOCKING)
_docking_semaphore: Optional[asyncio.Semaphore] = None


def _get_semaphore() -> asyncio.Semaphore:
    """Lazily create semaphore (must be created in async context)."""
    global _docking_semaphore
    if _docking_semaphore is None:
        _docking_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_DOCKING)
    return _docking_semaphore

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class LipinskiProfile(BaseModel):
    mw: float
    logp: float
    hbd: int
    hba: int
    pass_rule_of_five: bool


class InteractionSet(BaseModel):
    hydrogen_bonds: List[dict] = []
    hydrophobic: List[dict] = []
    pi_stacking: List[dict] = []
    salt_bridges: List[dict] = []


class DockingPose(BaseModel):
    pose_rank: int
    affinity: float
    ligand_efficiency: float
    rmsd_lb: float = 0.0
    rmsd_ub: float = 0.0
    interactions: Optional[InteractionSet] = None


class JobResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    job_id: str
    status: str  # queued | running | completed | failed
    submitted_at: float
    completed_at: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    lipinski: Optional[LipinskiProfile] = None
    poses: Optional[List[DockingPose]] = None


class HealthResponse(BaseModel):
    status: str
    engine: str
    timestamp: float
    jobs_running: int


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("BIOCANVAS v2.0 started — engine=%s SQLite=%s", 
                "ready" if engine else "viewer-only", _USE_SQLITE)
    yield
    # Shutdown: cancel pending jobs gracefully
    logger.info("Shutting down - draining thread pool...")
    _docking_executor.shutdown(wait=True)
    logger.info("Shutdown complete")


app = FastAPI(
    title="BIOCANVAS v2.0",
    description="Molecular Docking Server",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Global exception handler — any unhandled crash → clean JSON 500 ───
@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {type(exc).__name__}",
            "path": str(request.url.path),
        },
    )


# ── Bug S1 Fix: CORS — explicit origins (no wildcard with credentials) ───────────
_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

app.mount("/results", StaticFiles(directory=str(WORK_DIR)), name="results")

# ---------------------------------------------------------------------------
# Background docking task (runs in thread pool with semaphore limit)
# ---------------------------------------------------------------------------


def _run_docking_job(job_id: str, pdb_path: Path, smiles: str) -> None:
    """Execute a docking job in the background and update the store."""
    _store_update(job_id, status="running")
    try:
        result = engine.run_docking(str(pdb_path), smiles, job_id)
        if result.get("success"):
            out = result.get("output_file")
            if out:
                result["download_url"] = f"/results/{Path(out).name}"
            _store_update(
                job_id,
                status="completed",
                result=result,
                lipinski=result.get("lipinski"),
                poses=result.get("poses"),
                completed_at=datetime.now().timestamp(),
            )
        else:
            _store_update(
                job_id,
                status="failed",
                error=result.get("error", "Unknown error"),
                completed_at=datetime.now().timestamp(),
            )
    except Exception as exc:
        _store_update(
            job_id,
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
            completed_at=datetime.now().timestamp(),
        )
        logger.exception("Job %s failed", job_id)


# ---------------------------------------------------------------------------
# Store abstraction — SQLite primary, in-memory fallback
# ---------------------------------------------------------------------------


def _store_create(job_id: str) -> dict:
    """Create a new job record and return it."""
    now = datetime.now().timestamp()
    if _USE_SQLITE:
        return create_job(job_id)
    row = dict(
        job_id=job_id, status="queued", submitted_at=now,
        completed_at=None, result=None, error=None,
        lipinski=None, poses=None,
    )
    JOBS[job_id] = row
    return row


def _store_get(job_id: str) -> Optional[dict]:
    """Retrieve a job by id or None."""
    if _USE_SQLITE:
        return get_job(job_id)
    return JOBS.get(job_id)


def _store_update(job_id: str, **fields) -> None:
    """Update fields on an existing job."""
    if _USE_SQLITE:
        update_job(job_id, **fields)
    else:
        if job_id in JOBS:
            JOBS[job_id].update(fields)


def _store_running_count() -> int:
    """Count currently running jobs."""
    if _USE_SQLITE:
        return count_by_status("running")
    return sum(1 for j in JOBS.values() if j["status"] == "running")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health_check():
    running = _store_running_count()
    return HealthResponse(
        status="active",
        engine="ready" if engine else "viewer-only",
        timestamp=datetime.now().timestamp(),
        jobs_running=running,
    )


@app.post("/dock", response_model=JobResponse)
async def submit_docking_job(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    smiles: str = Form(...),
):
    """Submit a PDB + SMILES for asynchronous docking.
    
    Bug B3 Fix: Uses semaphore to limit concurrent jobs to prevent thread exhaustion.
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(429, "Rate limit exceeded — try again in a minute")

    if engine is None:
        raise HTTPException(
            503,
            "Docking engine unavailable — install rdkit & meeko to enable docking.",
        )
    if not file.filename or not file.filename.endswith(".pdb"):
        raise HTTPException(400, "File must be a .pdb file")
    if not smiles:
        raise HTTPException(400, "SMILES cannot be empty")

    # Bug B3 Fix: Check semaphore before accepting job
    semaphore = _get_semaphore()
    if semaphore.locked():
        raise HTTPException(
            429,
            f"Server busy - max {_MAX_CONCURRENT_DOCKING} concurrent jobs. Please try again later."
        )

    job_id = str(uuid.uuid4())
    pdb_path = WORK_DIR / f"{job_id}.pdb"

    with open(pdb_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    if not pdb_path.exists() or pdb_path.stat().st_size == 0:
        raise HTTPException(500, "Failed to save PDB file")

    row = _store_create(job_id)
    
    # Bug B3 Fix: Submit to thread pool executor instead of unlimited background tasks
    async def run_with_semaphore():
        async with semaphore:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(_docking_executor, _run_docking_job, job_id, pdb_path, smiles)
    
    background_tasks.add_task(run_with_semaphore)
    return JobResponse(**row)


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    row = _store_get(job_id)
    if row is None:
        raise HTTPException(404, f"Job {job_id} not found")
    return JobResponse(**row)


# ---------------------------------------------------------------------------
# Molecule library
# ---------------------------------------------------------------------------


def _load_json(filename: str) -> List[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        raise HTTPException(404, f"{filename} not found")
    with open(path) as f:
        return json.load(f)


@app.get("/proteins", response_model=List[dict])
async def get_proteins():
    return _load_json("proteins.json")


@app.get("/ligands", response_model=List[dict])
async def get_ligands():
    return _load_json("ligands.json")


@app.get("/")
async def root():
    return {
        "service": "BIOCANVAS v2.0",
        "version": "2.0.0",
        "status": "ready",
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
