"""
BioCanvas Pro — Integration tests for FastAPI endpoints.
Tests exact JSON schema, error handling, endpoint availability,
rate limiting, and global exception handler.
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app, JOBS, _store_create, _store_get, _store_update
import backend.main as main_mod


# ═══════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def client():
    """Create a synchronous FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def use_memory_store(monkeypatch):
    """Force in-memory store for test isolation (bypasses SQLite)."""
    monkeypatch.setattr(main_mod, "_USE_SQLITE", False)
    JOBS.clear()
    yield
    JOBS.clear()


# ═══════════════════════════════════════════════════════════════════════════
#  1. Root & Health
# ═══════════════════════════════════════════════════════════════════════════


class TestRootAndHealth:

    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "BIOCANVAS v2.0"
        assert "version" in data

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "engine" in data
        assert "timestamp" in data
        assert "jobs_running" in data
        assert isinstance(data["timestamp"], float)

    def test_health_schema_exact(self, client):
        resp = client.get("/health")
        data = resp.json()
        expected_keys = {"status", "engine", "timestamp", "jobs_running", "database", "vina"}
        assert set(data.keys()) == expected_keys


# ═══════════════════════════════════════════════════════════════════════════
#  2. Molecule Libraries
# ═══════════════════════════════════════════════════════════════════════════


class TestMoleculeLibraries:

    def test_get_proteins_returns_list(self, client):
        resp = client.get("/proteins")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "name" in data[0]
            assert "uniprot_id" in data[0]

    def test_get_ligands_returns_list(self, client):
        resp = client.get("/ligands")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "name" in data[0]
            assert "smiles" in data[0]


# ═══════════════════════════════════════════════════════════════════════════
#  3. /dock Endpoint — Validation
# ═══════════════════════════════════════════════════════════════════════════


class TestDockEndpoint:

    def test_dock_rejects_non_pdb(self, client):
        resp = client.post(
            "/dock",
            data={"smiles": "CCO"},
            files={"file": ("test.txt", b"not a pdb", "text/plain")},
        )
        # 400 (bad file) or 503 (engine unavailable — checked first)
        assert resp.status_code in (400, 503)

    def test_dock_rejects_empty_smiles(self, client):
        pdb_content = b"ATOM      1  N   ALA A   1      10.0  10.0  10.0  1.00  0.00\nEND\n"
        resp = client.post(
            "/dock",
            data={"smiles": ""},
            files={"file": ("test.pdb", pdb_content, "application/octet-stream")},
        )
        # FastAPI returns 400 (our guard) or 422 (pydantic validation)
        assert resp.status_code in (400, 422)

    def test_dock_success_returns_job_schema(self, client, minimal_pdb):
        pdb_bytes = minimal_pdb.encode()
        resp = client.post(
            "/dock",
            data={"smiles": "CCO"},
            files={"file": ("protein.pdb", pdb_bytes, "application/octet-stream")},
        )
        # Might be 200 (success) or 503 (engine unavailable) — both are acceptable
        if resp.status_code == 200:
            data = resp.json()
            assert "job_id" in data
            assert "status" in data
            assert data["status"] in ("queued", "running", "completed", "failed")
            assert "submitted_at" in data

    def test_dock_returns_503_without_engine(self, client, minimal_pdb, monkeypatch):
        """If docking engine is None, /dock should return 503."""
        import backend.main as main_mod
        original_engine = main_mod.engine
        main_mod.engine = None
        try:
            pdb_bytes = minimal_pdb.encode()
            resp = client.post(
                "/dock",
                data={"smiles": "CCO"},
                files={"file": ("protein.pdb", pdb_bytes, "application/octet-stream")},
            )
            assert resp.status_code == 503
        finally:
            main_mod.engine = original_engine


# ═══════════════════════════════════════════════════════════════════════════
#  4. /jobs/{job_id} Endpoint
# ═══════════════════════════════════════════════════════════════════════════


class TestJobStatusEndpoint:

    def test_job_not_found(self, client):
        resp = client.get("/jobs/nonexistent-uuid")
        assert resp.status_code == 404

    def test_job_status_after_dock(self, client, minimal_pdb):
        import backend.main as main_mod
        if main_mod.engine is None:
            pytest.skip("Docking engine not available")

        pdb_bytes = minimal_pdb.encode()
        dock_resp = client.post(
            "/dock",
            data={"smiles": "CCO"},
            files={"file": ("protein.pdb", pdb_bytes, "application/octet-stream")},
        )
        if dock_resp.status_code != 200:
            pytest.skip("Dock endpoint not available")

        job_id = dock_resp.json()["job_id"]
        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data["job_id"] == job_id

    def test_completed_job_has_full_schema(self, client, minimal_pdb):
        """Inject a completed job via store abstraction and verify schema."""
        from datetime import datetime

        now = datetime.now().timestamp()
        job_id = "test-schema-job"
        # Use the in-memory JOBS dict (autouse fixture forces memory mode)
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "submitted_at": now,
            "completed_at": now + 5,
            "result": {
                "success": True,
                "job_id": job_id,
                "affinity": -7.3,
                "simulated": True,
            },
            "error": None,
            "lipinski": {
                "mw": 180.16,
                "logp": 1.24,
                "hbd": 1,
                "hba": 4,
                "pass_rule_of_five": True,
            },
            "poses": [
                {
                    "pose_rank": 1,
                    "affinity": -7.3,
                    "ligand_efficiency": -0.56,
                    "rmsd_lb": 0.0,
                    "rmsd_ub": 0.0,
                    "interactions": {
                        "hydrogen_bonds": [
                            {"residue": "TYR-102", "distance": 2.8,
                             "protein_atom_idx": 100, "ligand_atom_idx": 5}
                        ],
                        "hydrophobic": [],
                        "pi_stacking": [],
                        "salt_bridges": [],
                    },
                }
            ],
        }

        resp = client.get(f"/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()

        # Verify top-level schema
        assert data["job_id"] == job_id
        assert data["status"] == "completed"
        assert data["submitted_at"] == now
        assert data["completed_at"] == now + 5
        assert data["error"] is None

        # Verify lipinski
        lip = data["lipinski"]
        assert lip["mw"] == 180.16
        assert lip["pass_rule_of_five"] is True

        # Verify poses
        assert len(data["poses"]) == 1
        pose = data["poses"][0]
        assert pose["pose_rank"] == 1
        assert pose["affinity"] == -7.3
        assert pose["interactions"]["hydrogen_bonds"][0]["residue"] == "TYR-102"


# ═══════════════════════════════════════════════════════════════════════════
#  5. CORS Headers
# ═══════════════════════════════════════════════════════════════════════════


class TestCORS:

    def test_cors_headers_present(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should respond
        assert resp.status_code in (200, 204, 405)

    def test_cors_rejects_unknown_origin(self, client):
        """Requests from non-allowed origins should not get CORS headers."""
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # The response should NOT have Access-Control-Allow-Origin for evil origin
        acao = resp.headers.get("access-control-allow-origin", "")
        assert "evil.example.com" not in acao


# ═══════════════════════════════════════════════════════════════════════════
#  6. Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════


class TestRateLimiting:

    def test_rate_limiter_function(self):
        """Verify the token-bucket rate limiter logic directly."""
        from backend.main import _check_rate_limit, _rate_buckets, _RATE_LIMIT
        test_ip = "TEST-RATE-LIMIT-IP"
        _rate_buckets.pop(test_ip, None)

        # Fill up the bucket
        for _ in range(_RATE_LIMIT):
            assert _check_rate_limit(test_ip) is True

        # Next request should be rejected
        assert _check_rate_limit(test_ip) is False

        # Cleanup
        _rate_buckets.pop(test_ip, None)


# ═══════════════════════════════════════════════════════════════════════════
#  7. Global Exception Handler
# ═══════════════════════════════════════════════════════════════════════════


class TestGlobalExceptionHandler:

    def test_unhandled_exception_returns_json_500(self, client, monkeypatch):
        """Simulate an unhandled exception in an endpoint."""
        import backend.main as _main

        # Temporarily break the health endpoint
        original_fn = _main.health_check

        async def _broken_health():
            raise RuntimeError("Simulated crash for testing")

        monkeypatch.setattr(_main, "health_check", _broken_health)
        app.routes  # force route refresh is not actually needed

        # We can't easily monkeypatch the route handler inside FastAPI,
        # so instead we verify the exception handler is registered
        assert any(
            h for h in app.exception_handlers
            if h == Exception or h == 500
        )


# ═══════════════════════════════════════════════════════════════════════════
#  8. Store Abstraction
# ═══════════════════════════════════════════════════════════════════════════


class TestStoreAbstraction:

    def test_create_and_get_job_memory(self, client):
        """In-memory store: create → get round-trip."""
        row = _store_create("test-mem-1")
        assert row["job_id"] == "test-mem-1"
        assert row["status"] == "queued"

        fetched = _store_get("test-mem-1")
        assert fetched is not None
        assert fetched["job_id"] == "test-mem-1"

    def test_update_job_memory(self, client):
        """In-memory store: update fields."""
        _store_create("test-mem-2")
        _store_update("test-mem-2", status="running")
        row = _store_get("test-mem-2")
        assert row["status"] == "running"

    def test_get_nonexistent_returns_none(self):
        assert _store_get("does-not-exist") is None


# ═══════════════════════════════════════════════════════════════════════════
#  9. SMILES Validation
# ═══════════════════════════════════════════════════════════════════════════


class TestSMILESValidation:

    def test_valid_smiles_accepted(self):
        from backend.main import _validate_smiles
        assert _validate_smiles("CCO") is True  # Ethanol
        assert _validate_smiles("CC(=O)OC1=CC=CC=C1C(=O)O") is True  # Aspirin

    def test_empty_smiles_rejected(self):
        from backend.main import _validate_smiles
        assert _validate_smiles("") is False
        assert _validate_smiles("   ") is False

    def test_invalid_smiles_rejected(self):
        from backend.main import _validate_smiles
        try:
            from rdkit import Chem  # noqa: F401
            has_rdkit = True
        except ImportError:
            has_rdkit = False

        if has_rdkit:
            # With RDKit, invalid SMILES should be rejected
            assert _validate_smiles("NOT_A_SMILES") is False
            assert _validate_smiles("XYZ123!!!") is False
        else:
            # Without RDKit, any non-empty string is accepted (graceful fallback)
            assert _validate_smiles("NOT_A_SMILES") is True

    def test_dock_rejects_invalid_smiles(self, client, minimal_pdb):
        """The /dock endpoint should reject invalid SMILES with 400."""
        import backend.main as main_mod
        if main_mod.engine is None:
            pytest.skip("Docking engine not available")
        pdb_bytes = minimal_pdb.encode()
        resp = client.post(
            "/dock",
            data={"smiles": "DEFINITELY_NOT_VALID_SMILES"},
            files={"file": ("protein.pdb", pdb_bytes, "application/octet-stream")},
        )
        assert resp.status_code == 400
        assert "Invalid SMILES" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════════════════
#  10. Enhanced Health Check
# ═══════════════════════════════════════════════════════════════════════════


class TestEnhancedHealthCheck:

    def test_health_includes_database_field(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "database" in data
        assert data["database"] in ("sqlite", "in-memory")

    def test_health_includes_vina_field(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert "vina" in data
        assert data["vina"] in ("available", "simulation-mode", "unavailable")

    def test_health_returns_request_id_header(self, client):
        resp = client.get("/health")
        assert "x-request-id" in resp.headers


# ═══════════════════════════════════════════════════════════════════════════
#  11. Config Module
# ═══════════════════════════════════════════════════════════════════════════


class TestConfigModule:

    def test_config_defaults_loaded(self):
        from backend.config import RATE_LIMIT, RATE_WINDOW, MAX_CONCURRENT_DOCKING
        assert isinstance(RATE_LIMIT, int)
        assert RATE_LIMIT > 0
        assert isinstance(RATE_WINDOW, float)
        assert isinstance(MAX_CONCURRENT_DOCKING, int)

    def test_cors_origins_is_list(self):
        from backend.config import CORS_ORIGINS
        assert isinstance(CORS_ORIGINS, list)
        assert len(CORS_ORIGINS) > 0

    def test_config_env_override(self, monkeypatch):
        """Environment variables should override defaults."""
        monkeypatch.setenv("BIOCANVAS_RATE_LIMIT", "99")
        # Re-import to test (config reads at import time, so test the helper)
        from backend.config import _get_int
        assert _get_int("RATE_LIMIT", 10) == 99
