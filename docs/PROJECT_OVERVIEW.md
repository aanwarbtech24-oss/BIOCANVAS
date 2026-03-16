# BIOCANVAS v2.0 — Project Overview (10-Line Summary)

1. **BIOCANVAS v2.0** is a full-stack molecular docking platform built for computational chemistry research and drug discovery, combining a **FastAPI (Python) backend** with a **React 18 + TypeScript frontend** powered by Vite.

2. The application provides a **guided 4-step docking pipeline**: (1) select or upload a protein target (PDB), (2) choose or enter a ligand molecule (SMILES), (3) submit and monitor the docking job in real-time, and (4) explore results on an interactive dashboard with 3D visualization, binding affinities, and drug-likeness scores.

3. The **backend docking engine** uses industry-standard tools — **RDKit** for cheminformatics, **Meeko** for PDBQT format conversion, **BioPython** for PDB parsing, and **AutoDock Vina** for actual molecular docking scoring — with a smart **simulation fallback mode** when Vina is not installed, making it usable for demos and development without external dependencies.

4. Job orchestration is handled asynchronously via a **bounded ThreadPoolExecutor** (max 4 concurrent docking jobs) with SQLite-based persistence, so jobs survive server restarts, and the frontend polls job status every 2 seconds using **TanStack React Query**.

5. The frontend uses **Zustand** for lightweight state management (pipeline step tracking, protein/ligand selection, job history), **3Dmol.js** for interactive 3D molecular visualization (protein cartoon + docked ligand sticks), and **Tailwind CSS** for a clean, responsive UI.

6. A curated **molecule library** ships with the app — 10 biologically important proteins (Hemoglobin, Insulin, Lysozyme, p53, EGFR, etc.) and 10 common ligands (Aspirin, Caffeine, ATP, Glucose, etc.) — with live structure fetching from **AlphaFold** (proteins) and **PubChem** (ligands).

7. The **Results Dashboard** (Step 4) displays a bento-grid layout with the best binding pose, a **Lipinski Rule-of-Five** drug-likeness profile (MW, LogP, HBD, HBA), a ranked pose table, and protein-ligand interaction details (hydrogen bonds, hydrophobic contacts, π-stacking, salt bridges).

8. The backend exposes **7 REST endpoints** (`/dock`, `/jobs/{id}`, `/proteins`, `/ligands`, `/health`, `/`, `/results/`) with built-in **rate limiting** (token bucket, 10 req/60s per IP), **CORS** middleware, and automatic **Swagger/ReDoc** API documentation.

9. The project includes a comprehensive **test suite** — pytest for backend API and docking engine tests, Vitest + Testing Library for frontend component and store tests, plus end-to-end integration tests — along with a **one-click launcher** (`python3 run.py`) that auto-creates a virtual environment, installs dependencies, and starts both servers.

10. In essence, BIOCANVAS is a **complete, production-ready web application** that democratizes molecular docking by providing an intuitive visual interface over complex computational chemistry workflows, suitable for researchers, students, and drug discovery professionals who want to perform protein-ligand docking without command-line expertise.
