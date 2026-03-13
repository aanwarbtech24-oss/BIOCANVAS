# BIOCANVAS v2.0

BioCanvas v2.0 is a full-stack molecular docking platform built with FastAPI and React.
It provides a production-ready workflow for protein-ligand docking, interactive 3D visualization,
asynchronous job execution, and reproducible result analysis for computational chemistry and drug discovery.

## Features

- Real docking workflow powered by AutoDock Vina CLI.
- Deterministic simulation fallback when Vina is unavailable.
- Interactive 3D molecular viewing with protein + ligand pose rendering.
- Multi-step React docking pipeline with consistent selector UX.
- SQLite-backed job persistence and status tracking.
- API-first backend with health checks and robust error handling.
- Release-grade documentation and testing utilities.

## Tech Stack

- Frontend: React, Vite, TypeScript, Zustand
- Backend: FastAPI, Python, SQLite
- Visualization: 3Dmol.js
- Docking: AutoDock Vina (CLI)
- Chemistry/Structure: RDKit, Meeko, BioPython

## Monorepo Layout

```
BIOCANVAS/
├── README.md
├── .gitignore
├── requirements.txt
├── run.py
├── backend/
├── frontend/
├── data/
├── tests/
├── docs/
├── scripts/
└── docking_jobs/
```

## Quick Start

### 1) Backend (FastAPI)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Backend API will be available at:

- `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 2) Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

Frontend will be available at:

- `http://localhost:5173`

### 3) Optional One-Command Launcher

```bash
python run.py
```

## Core API Endpoints

- `GET /health` -> backend health and engine status
- `POST /dock` -> submit docking job (`file` + `smiles`)
- `GET /jobs/{job_id}` -> retrieve job status and results
- `GET /results/{path}` -> download generated result files

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/API_REFERENCE.md`
- `docs/DEPLOYMENT.md`
- `docs/FRONTEND_GUIDE.md`
- `docs/RELEASE_V2_0.md`

For issues and questions:
- Check [docs/](docs/) for detailed guides
- Review [API_REFERENCE.md](docs/API_REFERENCE.md) for endpoint usage
- See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for setup help
