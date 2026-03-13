#!/usr/bin/env python3
"""
Generate the BioCanvas v2.0 Cleanup & Architecture Report as a professional PDF.
Includes: full cleanup changelog + detailed working-model explanation.

Usage:  python3 generate_cleanup_pdf.py
Output: BioCanvas_Cleanup_Report.pdf
"""

import os
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "scripts", "fonts")
OUTPUT = os.path.join(BASE_DIR, "BioCanvas_Cleanup_Report.pdf")

# ── Colour palette ──────────────────────────────────────────────────────────
BG       = (15, 18, 25)
CARD_BG  = (22, 27, 38)
PRIMARY  = (99, 102, 241)   # indigo-500
ACCENT   = (16, 185, 129)   # emerald-500
WHITE    = (240, 240, 245)
MUTED    = (148, 163, 184)
RED      = (239, 68, 68)
AMBER    = (245, 158, 11)
DIVIDER  = (40, 45, 60)
TABLE_HEADER_BG = (35, 40, 58)


class ReportPDF(FPDF):
    """Custom PDF with dark sci-fi theme matching BioCanvas UI."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        # Register DejaVu fonts (Unicode support)
        self.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
        self.add_font("DejaVu", "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))
        self.add_font("Mono", "", os.path.join(FONT_DIR, "DejaVuSansMono.ttf"))

    # ── Page background ──
    def header(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "I", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"BioCanvas v2.0  |  Cleanup & Architecture Report  |  Page {self.page_no()}/{{nb}}", align="C")

    # ── Helpers ──
    def _color(self, c):
        self.set_text_color(*c)

    def _bg(self, c):
        self.set_fill_color(*c)

    def section_title(self, text, num=None):
        self.ln(4)
        self.set_font("DejaVu", "B", 16)
        self._color(PRIMARY)
        prefix = f"{num}. " if num else ""
        self.cell(0, 10, prefix + text, ln=True)
        # divider line
        self._bg(PRIMARY)
        self.rect(self.l_margin, self.get_y(), 180, 0.5, "F")
        self.ln(4)

    def sub_title(self, text):
        self.set_font("DejaVu", "B", 12)
        self._color(ACCENT)
        self.cell(0, 8, text, ln=True)
        self.ln(1)

    def sub_sub_title(self, text):
        self.set_font("DejaVu", "B", 10)
        self._color(WHITE)
        self.cell(0, 7, text, ln=True)
        self.ln(1)

    def body(self, text):
        self.set_font("DejaVu", "", 9)
        self._color(WHITE)
        self.multi_cell(0, 5.2, text)
        self.ln(1)

    def muted(self, text):
        self.set_font("DejaVu", "I", 8)
        self._color(MUTED)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def bullet(self, text, indent=8):
        self.set_font("DejaVu", "", 9)
        self._color(WHITE)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.w - self.l_margin - self.r_margin - indent, 5.2, "\u2022  " + text)

    def code_block(self, text):
        self.set_font("Mono", "", 7.5)
        self._color(MUTED)
        self._bg(CARD_BG)
        lines = text.strip().split("\n")
        x0 = self.l_margin
        w = 180
        self.rect(x0, self.get_y(), w, len(lines) * 4.5 + 4, "F")
        self.ln(2)
        for line in lines:
            self.cell(4)
            self.cell(0, 4.5, line, ln=True)
        self.ln(3)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [180 / len(headers)] * len(headers)
        # Header
        self.set_font("DejaVu", "B", 8)
        self._bg(TABLE_HEADER_BG)
        self._color(PRIMARY)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, f" {h}", border=0, fill=True)
        self.ln()
        # Rows
        self.set_font("DejaVu", "", 8)
        fill = False
        for row in rows:
            self._bg((28, 33, 46) if fill else BG)
            self._color(WHITE)
            max_h = 6
            for i, val in enumerate(row):
                self.cell(col_widths[i], max_h, f" {val}", border=0, fill=True)
            self.ln()
            fill = not fill
        self.ln(2)

    def card(self, title, content):
        """Draw a rounded-corner card with title and body."""
        self._bg(CARD_BG)
        y0 = self.get_y()
        # estimate height
        self.set_font("DejaVu", "", 9)
        # rough line count
        nlines = len(content) // 80 + content.count("\n") + 3
        h = max(nlines * 5.2 + 14, 20)
        if y0 + h > 280:
            self.add_page()
            y0 = self.get_y()
        self.rect(self.l_margin, y0, 180, h, "F")
        self.set_xy(self.l_margin + 4, y0 + 3)
        self.set_font("DejaVu", "B", 10)
        self._color(PRIMARY)
        self.cell(0, 6, title, ln=True)
        self.set_x(self.l_margin + 4)
        self.set_font("DejaVu", "", 9)
        self._color(WHITE)
        self.multi_cell(172, 5.2, content)
        self.set_y(y0 + h + 3)


def build_pdf():
    pdf = ReportPDF()
    pdf.alias_nb_pages()

    # ════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("DejaVu", "B", 32)
    pdf._color(PRIMARY)
    pdf.cell(0, 14, "BioCanvas v2.0", ln=True, align="C")
    pdf.set_font("DejaVu", "", 14)
    pdf._color(WHITE)
    pdf.cell(0, 10, "Codebase Cleanup & Architecture Report", ln=True, align="C")
    pdf.ln(10)
    pdf._bg(DIVIDER)
    pdf.rect(60, pdf.get_y(), 90, 0.4, "F")
    pdf.ln(10)
    pdf.set_font("DejaVu", "", 10)
    pdf._color(MUTED)
    pdf.cell(0, 7, "Date: February 21, 2025", ln=True, align="C")
    pdf.cell(0, 7, "Engineer: AI-Assisted Development (GitHub Copilot)", ln=True, align="C")
    pdf.cell(0, 7, "Scope: Full codebase audit, restructuring, documentation", ln=True, align="C")
    pdf.cell(0, 7, "Risk Level: Low — all changes preserve existing functionality", ln=True, align="C")
    pdf.ln(25)
    pdf.set_font("DejaVu", "I", 9)
    pdf._color(MUTED)
    pdf.multi_cell(0, 5, (
        "This report provides a complete technical overview of BioCanvas v2.0 — a molecular "
        "docking web platform — including the architecture, data flow, every component's role, "
        "and a detailed changelog of the professional cleanup performed on the codebase."
    ), align="C")

    # ════════════════════════════════════════════════════════════════════
    # PART A — WORKING MODEL (FULL ARCHITECTURE)
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 20)
    pdf._color(ACCENT)
    pdf.cell(0, 12, "PART A — System Architecture & Working Model", ln=True)
    pdf._bg(ACCENT)
    pdf.rect(pdf.l_margin, pdf.get_y(), 180, 0.5, "F")
    pdf.ln(6)

    # ── 1. Overview ──
    pdf.section_title("System Overview", 1)
    pdf.body(
        "BioCanvas v2.0 is a full-stack web application for computational molecular docking. "
        "It enables researchers to select protein targets and small-molecule ligands, submit "
        "docking jobs to a server running AutoDock Vina, and visualise the resulting 3D "
        "molecular structures in the browser.\n\n"
        "The system follows a client-server architecture with a clear separation of concerns:"
    )
    pdf.bullet("Frontend: React 18 + TypeScript + Vite (port 5173)")
    pdf.bullet("Backend: FastAPI + Uvicorn (port 8000)")
    pdf.bullet("Docking Engine: RDKit + Meeko + BioPython + AutoDock Vina (optional)")
    pdf.bullet("3D Visualisation: 3Dmol.js v2.4.2 loaded via CDN")
    pdf.bullet("State Management: React Query v5 (server state) + Zustand (UI state)")
    pdf.ln(2)

    # ── 2. Data Flow ──
    pdf.section_title("End-to-End Data Flow", 2)
    pdf.body(
        "The application implements a 4-step wizard pipeline. Here is the complete data "
        "flow from user action to rendered result:"
    )
    pdf.ln(1)
    pdf.sub_sub_title("Step 1: Protein Target Selection")
    pdf.body(
        "The user selects a protein from a curated library (data/proteins.json, served by "
        "GET /proteins). The frontend calls the AlphaFold Protein Structure Database API:\n\n"
        "  1. GET https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}\n"
        "  2. The response contains a pdbUrl pointing to the latest predicted PDB file\n"
        "  3. The PDB file is fetched and passed to the Viewer3D component\n"
        "  4. 3Dmol.js parses the PDB and renders the 3D structure (cartoon/stick/sphere/surface)\n\n"
        "Alternatively, the user can upload a custom .pdb file which bypasses AlphaFold entirely."
    )
    pdf.sub_sub_title("Step 2: Ligand Selection")
    pdf.body(
        "The user picks a small-molecule ligand from the curated library (data/ligands.json, "
        "served by GET /ligands). Each ligand has a PubChem CID and SMILES string.\n\n"
        "  1. The PubChem 3D Conformer API is queried for an SDF structure file:\n"
        "     GET https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d\n"
        "  2. The SDF is rendered in a second Viewer3D instance\n"
        "  3. Alternatively, the user can paste a custom SMILES string\n\n"
        "The SMILES string (from library or custom input) is stored for submission in Step 3."
    )
    pdf.sub_sub_title("Step 3: Docking Execution")
    pdf.body(
        "When the user clicks 'Run Docking', the frontend sends a multipart POST request:\n\n"
        "  POST /dock\n"
        "  Body: { file: <protein.pdb>, smiles: <ligand SMILES> }\n\n"
        "The backend processes this asynchronously:\n"
        "  1. A unique job_id (UUID) is generated and returned immediately\n"
        "  2. A background task (_run_docking_job) is spawned\n"
        "  3. The DockingEngine is invoked:\n"
        "     a. prepare_receptor() — cleans PDB, removes water/HETATM, writes PDBQT\n"
        "     b. prepare_ligand() — SMILES → 3D coords (RDKit) → PDBQT (Meeko)\n"
        "     c. calculate_box() — computes search box from protein coordinates\n"
        "     d. Vina.dock() — runs AutoDock Vina with exhaustiveness=8\n"
        "  4. The frontend polls GET /jobs/{job_id} every 2 seconds\n"
        "  5. When status becomes 'completed', results are displayed\n\n"
        "If Vina is not installed, the engine falls back to a deterministic simulation mode "
        "that generates realistic mock results seeded from a hash of the inputs."
    )
    pdf.sub_sub_title("Step 4: Results & AI Analysis")
    pdf.body(
        "Currently a 'Coming Soon' placeholder. Planned features:\n"
        "  - GPT-powered interpretation of docking results\n"
        "  - Binding affinity prediction and interaction residue analysis\n"
        "  - Drug-likeness scoring (Lipinski's Rule of Five)"
    )
    pdf.ln(2)

    # ── 3. Backend Architecture ──
    pdf.section_title("Backend Architecture (FastAPI)", 3)
    pdf.sub_title("3.1 API Endpoints")
    pdf.table(
        ["Method", "Path", "Description"],
        [
            ["GET",  "/",              "App info (name, version, status)"],
            ["GET",  "/health",        "Health check — engine status, jobs running, timestamp"],
            ["POST", "/dock",          "Submit docking job (multipart: PDB file + SMILES string)"],
            ["GET",  "/jobs/{job_id}", "Poll job status and retrieve results"],
            ["GET",  "/proteins",      "Return curated protein library from data/proteins.json"],
            ["GET",  "/ligands",       "Return curated ligand library from data/ligands.json"],
        ],
        col_widths=[18, 42, 120],
    )

    pdf.sub_title("3.2 Job Lifecycle")
    pdf.code_block(
        "POST /dock\n"
        "  ├─ Validate file + SMILES\n"
        "  ├─ Generate UUID job_id\n"
        "  ├─ Save PDB to docking_jobs/{job_id}.pdb\n"
        "  ├─ Set status = 'queued'\n"
        "  ├─ Spawn background task → _run_docking_job()\n"
        "  └─ Return { job_id, status: 'queued' }\n"
        "\n"
        "_run_docking_job()\n"
        "  ├─ Set status = 'running'\n"
        "  ├─ Call engine.run_docking(pdb_file, smiles, job_id)\n"
        "  ├─ On success: status = 'completed', store result dict\n"
        "  └─ On failure: status = 'failed', store error message"
    )

    pdf.sub_title("3.3 Docking Engine Pipeline")
    pdf.body(
        "The DockingEngine class (backend/docking_engine.py) orchestrates the full molecular "
        "docking workflow. All heavy computation uses established bioinformatics libraries:"
    )
    pdf.table(
        ["Step", "Method", "Library", "What It Does"],
        [
            ["1", "prepare_receptor()", "BioPython",  "Parse PDB, strip water/HETATM, write AutoDock PDBQT"],
            ["2", "prepare_ligand()",   "RDKit+Meeko", "SMILES→3D embedding→geometry optimisation→PDBQT"],
            ["3", "calculate_box()",    "NumPy",       "Compute search box center & size (10A padding)"],
            ["4", "Vina.dock()",        "AutoDock Vina", "Molecular docking (exhaustiveness=8, 1 pose)"],
        ],
        col_widths=[12, 42, 36, 90],
    )
    pdf.body(
        "The pure-Python PDB→PDBQT converter assigns AutoDock atom types (AD4) directly — "
        "no OpenBabel binary is required. This makes deployment simpler and avoids a common "
        "pain point in computational chemistry toolchains.\n\n"
        "When AutoDock Vina is not installed, _simulate_docking() generates deterministic "
        "mock results using a SHA-256 hash of the input PDB + SMILES as a random seed. This "
        "ensures the same inputs always produce the same scores, making development and "
        "testing reproducible."
    )

    # ── 4. Frontend Architecture ──
    pdf.section_title("Frontend Architecture (React + TypeScript)", 4)
    pdf.sub_title("4.1 Technology Stack")
    pdf.table(
        ["Technology", "Version", "Role"],
        [
            ["React",         "18.3.1",  "UI library — component model, hooks, virtual DOM"],
            ["TypeScript",    "5.9.3",   "Type safety across the entire frontend"],
            ["Vite",          "6.4.1",   "Build tool — HMR dev server + production bundler"],
            ["SWC",           "—",       "Rust-based compiler (faster than Babel)"],
            ["TailwindCSS",   "4.1.18",  "Utility-first CSS — dark sci-fi theme via @theme"],
            ["React Query",   "5.90",    "Server state — fetching, caching, smart polling"],
            ["Zustand",       "5.0.11",  "Client state — minimal store (activeTab only)"],
            ["3Dmol.js",      "2.4.2",   "WebGL molecular visualisation (loaded via CDN)"],
            ["Axios",         "1.13.5",  "HTTP client with global error interceptor"],
            ["Sonner",        "2.0.7",   "Toast notification system"],
            ["Lucide React",  "0.563",   "Icon library (tree-shakeable SVG icons)"],
        ],
        col_widths=[36, 20, 124],
    )

    pdf.sub_title("4.2 Component Hierarchy")
    pdf.code_block(
        "App.tsx (Root Shell)\n"
        "├── QueryClientProvider   — React Query context\n"
        "├── ErrorBoundary         — Catches render errors\n"
        "├── Navbar                — Tab navigation (Pipeline / Visualize)\n"
        "├── DockingPipeline       — 4-step wizard (default tab)\n"
        "│   ├── ProgressBar       — Horizontal step indicator\n"
        "│   ├── Step 1: Protein   — Dropdown + AlphaFold 3D preview\n"
        "│   ├── Step 2: Ligand    — Grid + PubChem 3D preview\n"
        "│   ├── Step 3: Docking   — Submit + live polling + results\n"
        "│   ├── Step 4: AI        — Coming Soon placeholder\n"
        "│   ├── BottomNav         — Back / Next buttons (fixed)\n"
        "│   └── ElapsedTimer      — Live ticking elapsed display\n"
        "├── VisualizePage         — Side-by-side protein + ligand viewer\n"
        "│   ├── MoleculeSelector  — Generic dropdown for proteins/ligands\n"
        "│   └── ViewerCard        — Viewer3D wrapper with header bar\n"
        "├── Viewer3D              — 3Dmol.js WebGL canvas wrapper\n"
        "│   └── Style switcher    — cartoon / stick / sphere / surface\n"
        "└── Toaster (Sonner)      — Toast notifications"
    )

    pdf.sub_title("4.3 Data Fetching Strategy")
    pdf.body(
        "All server communication uses React Query v5 hooks:\n\n"
        "• useProteins() / useLigands() — fetch curated libraries (staleTime: 5min)\n"
        "• useProteinStructure(uniprotId) — AlphaFold API → PDB text (staleTime: 10min)\n"
        "• useLigandStructure(pubchemCid) — PubChem API → SDF text (staleTime: 10min)\n"
        "• useDockingJob(jobId) — polls GET /jobs/{id} every 2s, stops on terminal state\n"
        "• useSubmitDocking() — mutation that POST /dock and prefetches the job query\n"
        "• useHealthCheck() — polls GET /health every 10s\n\n"
        "The polling in useDockingJob has smart behaviour:\n"
        "  - Polls every 2 seconds while status is 'queued' or 'running'\n"
        "  - Automatically stops on 'completed', 'failed', or HTTP 404\n"
        "  - HTTP 404 means the job was lost due to server restart — a toast is shown\n"
        "  - Uses placeholderData to avoid flickering during refetches"
    )

    pdf.sub_title("4.4 3D Molecular Visualisation")
    pdf.body(
        "Viewer3D.tsx wraps the 3Dmol.js library (loaded via CDN <script> tag in index.html, "
        "accessed as window.$3Dmol). Key implementation details:\n\n"
        "• Canvas is created once via $3Dmol.createViewer() and reused across data changes\n"
        "• Data updates use removeAllModels() + addModel() + setStyle() + zoomTo()\n"
        "• ResizeObserver handles dynamic container resizing\n"
        "• Four visualisation styles: cartoon (default for proteins), stick (default for "
        "ligands), sphere, and surface\n"
        "• The component is wrapped in React.memo to prevent unnecessary WebGL re-renders\n"
        "• Loading state shows a skeleton with a spinning loader\n"
        "• Error state shows a message with the error details"
    )

    pdf.sub_title("4.5 State Management")
    pdf.body(
        "The frontend uses a two-tier state model:\n\n"
        "Server State (React Query):\n"
        "  All data from the backend — proteins, ligands, structures, job status — is managed "
        "by React Query. This provides automatic caching, background refetching, stale-while-"
        "revalidate patterns, and garbage collection of unused queries.\n\n"
        "Client State (Zustand):\n"
        "  useDockingStore — tracks job history (Map<jobId, DockingJob>), active job ID\n"
        "  useUIStore — tracks the active tab ('pipeline' or 'visualize')\n\n"
        "Local Component State (useState):\n"
        "  The DockingPipeline wizard uses ~15 useState hooks for step-local UI state "
        "(selected protein, selected ligand, search queries, dropdown open states, etc.). "
        "This state is intentionally local because it only matters within the wizard."
    )

    # ── 5. External APIs ──
    pdf.section_title("External API Integrations", 5)
    pdf.table(
        ["API", "Endpoint", "Purpose"],
        [
            ["AlphaFold DB", "alphafold.ebi.ac.uk/api/prediction/{id}", "Fetch predicted protein 3D structure (PDB)"],
            ["PubChem",      "pubchem.ncbi.nlm.nih.gov/rest/pug/...",   "Fetch ligand 3D conformer (SDF)"],
            ["UniProt",      "uniprot.org/uniprot/{id}",                "External link for protein info"],
            ["3Dmol.js CDN", "cdnjs.cloudflare.com/.../3Dmol-min.js",   "WebGL molecular renderer script"],
        ],
        col_widths=[30, 80, 70],
    )

    # ── 6. Curated Data ──
    pdf.section_title("Curated Molecular Libraries", 6)
    pdf.body(
        "The application ships with two JSON data files served by the backend:"
    )
    pdf.sub_sub_title("data/proteins.json")
    pdf.body(
        "A curated set of well-known protein targets with fields: id, name, uniprot_id, "
        "function (description), and category (Transport, Enzyme, Hormone, Storage, "
        "Regulation, Receptor). Each protein's 3D structure is fetched on-demand from "
        "AlphaFold using the UniProt accession ID."
    )
    pdf.sub_sub_title("data/ligands.json")
    pdf.body(
        "A curated set of small molecules with fields: id, name, type (Drug, Cofactor, "
        "Carbohydrate, Stimulant, Metabolite, Antibiotic, Neurotransmitter, Lipid), "
        "description, pubchem_cid, and smiles. The SMILES string is used for docking; "
        "the PubChem CID is used for 3D visualisation."
    )

    # ════════════════════════════════════════════════════════════════════
    # PART B — CLEANUP CHANGELOG
    # ════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 20)
    pdf._color(RED)
    pdf.cell(0, 12, "PART B — Codebase Cleanup Changelog", ln=True)
    pdf._bg(RED)
    pdf.rect(pdf.l_margin, pdf.get_y(), 180, 0.5, "F")
    pdf.ln(6)

    # ── Metrics ──
    pdf.section_title("Cleanup Metrics Summary", 7)
    pdf.table(
        ["File", "Before", "After", "Change"],
        [
            ["backend/main.py",        "558 lines",  "243 lines",  "-56%"],
            ["backend/docking_engine.py","527 lines", "274 lines",  "-48%"],
            ["DockingPipeline.tsx",     "1,365 lines","1,133 lines","-17%"],
            ["VisualizePage.tsx",       "419 lines",  "389 lines",  "-7%"],
            ["axios.ts",               "80 lines",   "41 lines",   "-49%"],
            ["api.ts (types)",         "100 lines",  "58 lines",   "-42%"],
            ["NPM dependencies",       "12 packages","9 packages", "-3 removed"],
            ["Dead files removed",     "—",          "~25 files",  "—"],
        ],
        col_widths=[55, 35, 35, 55],
    )

    # ── Files deleted ──
    pdf.section_title("Files & Dead Code Removed", 8)
    pdf.sub_title("8.1 Files Deleted")
    deleted_files = [
        ("Badge.tsx, Button.tsx", "Never imported by any component"),
        ("Viewer3D.tsx.broken, 3dmol.d.ts.bak", "Backup files from debugging"),
        ("test3dmol.html", "One-off test file"),
        ("# Code Citations* (multiple)", "5,272-line conversation dumps"),
        ("frontend/pages/ (entire dir)", "Old Streamlit landing page + node_modules"),
        ("frontend/src/pages/, backend/routers/", "Empty directories"),
        ("STATUS_READY.txt (210 lines)", "Old status report"),
        ("3 PDF files", "Generated artifacts"),
        ("biocanvas_server.log (302 KB)", "Log file"),
        ("tests/diagnostics/ (4 scripts)", "Obsolete diagnostic scripts"),
    ]
    for f, reason in deleted_files:
        pdf.bullet(f"{f}  —  {reason}")
    pdf.ln(2)

    pdf.sub_title("8.2 Dead Code Removed from Live Files")
    dead_code = [
        ("useDockingJob.ts → useAppInfo()", "Hook defined but never imported"),
        ("Card.tsx → CardHeader, CardFooter", "Exported but never imported"),
        ("axios.ts → Request interceptor", "Commented-out auth token code"),
        ("api.ts → SubmitDockingRequestSchema", "Zod schema never validated at runtime"),
        ("api.ts → APIErrorSchema", "Zod schema never validated at runtime"),
        ("backend/main.py → /dock-sync", "Debug endpoint not used by frontend"),
        ("backend/main.py → DockingRequest", "Pydantic model never referenced"),
    ]
    for loc, reason in dead_code:
        pdf.bullet(f"{loc}  —  {reason}")
    pdf.ln(2)

    # ── Backend changes ──
    pdf.section_title("Backend Changes", 9)
    pdf.sub_title("9.1 backend/main.py  (558 → 243 lines, −56%)")
    pdf.body("Removed:")
    for item in [
        "~40 logger.info()/debug() calls that added noise without diagnostic value",
        "_setup_server_logger() — custom file handler (standard logging is sufficient)",
        'Decorative banner comments ("=" * 60 separator lines at startup)',
        "Verbose multi-line docstrings on trivial two-line endpoints",
        "DockingRequest Pydantic schema (unused — /dock accepts multipart form)",
        "/dock-sync endpoint (debug-only synchronous docking, not called by frontend)",
    ]:
        pdf.bullet(item)
    pdf.ln(1)
    pdf.body("Preserved: All 6 endpoints, CORS middleware, background task for async docking, "
             "503 guard when DockingEngine is unavailable, graceful engine import.")

    pdf.sub_title("9.2 backend/docking_engine.py  (527 → 274 lines, −48%)")
    pdf.body("Removed:")
    for item in [
        "_setup_logging() — replaced with module-level logging.getLogger()",
        "_validate_dependencies() — printed info but validated nothing",
        "~30 redundant self.logger calls",
        "14-line PDBQT column-format spec comment block",
        "Verbose Args/Returns/Raises docstrings on internal methods",
    ]:
        pdf.bullet(item)
    pdf.ln(1)
    pdf.body("Preserved: All 5 core methods, pure-Python PDB→PDBQT converter, "
             "deterministic simulation mode, all error handling.")

    # ── Frontend changes ──
    pdf.section_title("Frontend Changes", 10)
    pdf.sub_title("10.1 DockingPipeline.tsx  (1,365 → 1,133 lines)")
    pdf.body(
        "Extracted 3 sub-components into pipeline/ sub-directory:\n"
        "  • StepNav.tsx — ProgressBar + BottomNav + STEPS constant\n"
        "  • ElapsedTimer.tsx — Live-ticking elapsed time display\n"
        "  • helpers.ts — categoryColor() + ligandTypeColor() classifiers\n\n"
        "Cleaned all verbose ═══ and ── separator comments throughout."
    )

    pdf.sub_title("10.2 Type System — api.ts  (100 → 58 lines)")
    pdf.body(
        "Replaced all Zod schemas with plain TypeScript interfaces. The schemas were never "
        "used for runtime validation — only for z.infer<> type extraction. This removed the "
        "zod dependency entirely (13 KB min+gzip saved)."
    )

    pdf.sub_title("10.3 Other Frontend Files")
    for item in [
        "VisualizePage.tsx (419→389) — deduplicated color helpers, cleaned separators",
        "axios.ts (80→41) — Record lookup instead of if/else chain, removed dead interceptor",
        "useDockingJob.ts (163→128) — removed useAppInfo(), cleaned comments",
        "Card.tsx (65→38) — removed unused CardHeader and CardFooter exports",
    ]:
        pdf.bullet(item)
    pdf.ln(2)

    # ── Config changes ──
    pdf.section_title("Configuration Changes", 11)
    pdf.sub_title("11.1 package.json")
    for item in [
        "Removed zod from dependencies (no longer used after types conversion)",
        "Removed 3dmol from dependencies (loaded via CDN, not npm import)",
        "Removed duplicate @vitejs/plugin-react-swc from dependencies (kept in devDeps)",
    ]:
        pdf.bullet(item)
    pdf.ln(1)

    pdf.sub_title("11.2 vite.config.ts")
    for item in [
        "Removed /api proxy — frontend uses direct http://127.0.0.1:8000 via axios",
        "Removed minify: 'terser' — terser was not installed; using default esbuild",
        "Removed manualChunks — react-vendor was empty; Vite auto-splits sufficiently",
    ]:
        pdf.bullet(item)
    pdf.ln(1)

    pdf.sub_title("11.3 Project Structure")
    pdf.body(
        "• generate_report.py, generate_app_guide.py → moved to scripts/\n"
        "• .fonts/ → moved to scripts/fonts/\n"
        "• Added *.pdf to .gitignore"
    )

    # ── Verification ──
    pdf.section_title("Verification", 12)
    pdf.body("All changes were verified before delivery:")
    for item in [
        "tsc --noEmit: Zero TypeScript errors",
        "vite build: Completes in 1.22s, output 107 KB gzipped",
        "Backend import: 'from backend.main import app' succeeds (viewer-only mode)",
        "Dev server: Vite starts in 115ms on port 5173",
    ]:
        pdf.bullet(item)
    pdf.ln(2)

    # ── Recommendations ──
    pdf.section_title("Recommendations for the Team", 13)
    recommendations = [
        ("Add runtime API validation",
         "Re-add Zod with actual .parse() calls on API responses if the team wants "
         "response validation."),
        ("Split DockingPipeline.tsx further",
         "At 1,133 lines it's still the largest file. Consider React Context to share "
         "wizard state, then extract each step into its own file."),
        ("Add unit tests",
         "Currently only tests/e2e_docking_test.py exists. Consider adding Vitest for "
         "React component tests."),
        ("Install real Vina",
         "The docking engine runs in simulation mode. 'pip install vina' enables real "
         "molecular docking."),
        ("Clean node_modules",
         "3dmol is still installed from the lockfile even though it's loaded via CDN. "
         "Run 'npm prune' to clean up."),
        ("Update docs/",
         "ARCHITECTURE.md (31 KB) and FRONTEND_GUIDE.md (16 KB) pre-date these changes "
         "and should be refreshed."),
    ]
    for i, (title, desc) in enumerate(recommendations, 1):
        pdf.set_font("DejaVu", "B", 9)
        pdf._color(AMBER)
        pdf.cell(0, 6, f"  {i}. {title}", ln=True)
        pdf.set_font("DejaVu", "", 9)
        pdf._color(WHITE)
        pdf.set_x(pdf.l_margin + 8)
        pdf.multi_cell(172, 5.2, desc)
        pdf.ln(1)

    # ── Final page ──
    pdf.add_page()
    pdf.ln(80)
    pdf.set_font("DejaVu", "B", 18)
    pdf._color(PRIMARY)
    pdf.cell(0, 12, "End of Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 10)
    pdf._color(MUTED)
    pdf.cell(0, 7, "BioCanvas v2.0 — Molecular Docking Platform", ln=True, align="C")
    pdf.cell(0, 7, "Codebase Cleanup & Architecture Report", ln=True, align="C")
    pdf.cell(0, 7, "February 2025", ln=True, align="C")

    # ── Save ──
    pdf.output(OUTPUT)
    print(f"\n✅ PDF saved to: {OUTPUT}")
    print(f"   Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
