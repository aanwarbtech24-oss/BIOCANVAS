#!/usr/bin/env python3
"""
BIOCANVAS v2.0 - Project Status Report PDF Generator
Generates a professional PDF handoff document.
"""

from fpdf import FPDF
from datetime import datetime
import os


class ReportPDF(FPDF):
    """Custom PDF with header/footer for BIOCANVAS report."""

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "BIOCANVAS v2.0 - Project Status Report", align="L")
        self.cell(0, 8, "February 20, 2026", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(139, 92, 246)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(139, 92, 246)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(139, 92, 246)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def sub_title(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 80)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=10):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(indent, 5.5, "")
        self.multi_cell(180 - indent, 5.5, "- " + text)

    def status_row(self, col1, col2, col3, is_header=False):
        self.set_font("Helvetica", "B" if is_header else "", 9)
        if is_header:
            self.set_fill_color(139, 92, 246)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(245, 245, 250)
            self.set_text_color(40, 40, 40)
        self.cell(55, 7, col1, border=1, fill=True)
        self.cell(30, 7, col2, border=1, fill=True, align="C")
        self.cell(105, 7, col3, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    def code_block(self, text):
        self.set_font("Courier", "", 9)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(240, 240, 245)
        y_before = self.get_y()
        self.multi_cell(190, 5, text, fill=True)
        self.ln(2)


def generate_report():
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ============================================================
    # COVER / TITLE
    # ============================================================
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 15, "BIOCANVAS v2.0", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Molecular Docking Platform", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Detailed Project Status Report", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_draw_color(139, 92, 246)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Date: February 20, 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Status: ~65-70% Complete", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Platform: macOS (dev) | Cross-platform deployment", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "This document provides a complete handoff of the project state,", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "including what has been built, what remains, and all known issues.", align="C", new_x="LMARGIN", new_y="NEXT")

    # ============================================================
    # PAGE 2: WHAT IS BIOCANVAS
    # ============================================================
    pdf.add_page()
    pdf.section_title("1. WHAT IS BIOCANVAS?")
    pdf.body_text(
        "BIOCANVAS is a full-stack web application for computational chemistry and drug discovery research. "
        "It provides an intuitive interface for molecular docking calculations, combining a powerful Python "
        "backend with a modern React frontend."
    )
    pdf.sub_title("What Researchers Can Do:")
    pdf.bullet("Upload a protein structure (PDB file)")
    pdf.bullet("Input a ligand molecule (SMILES string)")
    pdf.bullet("Run molecular docking calculations via AutoDock Vina")
    pdf.bullet("View interactive 3D results and binding affinity scores")
    pdf.bullet("Track and compare multiple docking jobs")

    pdf.sub_title("Target Users:")
    pdf.bullet("Computational chemists")
    pdf.bullet("Drug discovery researchers")
    pdf.bullet("Pharmaceutical companies")
    pdf.bullet("Academic research institutions")

    # ============================================================
    # TECH STACK
    # ============================================================
    pdf.section_title("2. TECHNOLOGY STACK")

    tech_data = [
        ("Layer", "Technology", "Status"),
        ("Backend API", "FastAPI + Uvicorn (Python 3.10+)", "COMPLETE"),
        ("Docking Engine", "AutoDock Vina + RDKit + Meeko + Biopython", "COMPLETE"),
        ("Frontend Framework", "React 18 + TypeScript + Vite 6", "PARTIAL"),
        ("State Management", "Zustand v5", "COMPLETE"),
        ("Data Fetching", "TanStack React Query v5 + Axios", "COMPLETE"),
        ("Styling", "TailwindCSS v4 (dark purple/sci-fi theme)", "COMPLETE"),
        ("Validation", "Zod v4 (defined, not wired at runtime)", "DEFINED ONLY"),
        ("Notifications", "Sonner (toast)", "COMPLETE"),
        ("Icons", "Lucide React", "COMPLETE"),
    ]

    for i, row in enumerate(tech_data):
        pdf.status_row(row[0], row[2], row[1], is_header=(i == 0))

    # ============================================================
    # BACKEND DETAILS
    # ============================================================
    pdf.add_page()
    pdf.section_title("3. BACKEND (100% Complete)")

    pdf.sub_title("3.1 API Server - backend/main.py (478 lines)")
    pdf.body_text(
        "FastAPI application with CORS middleware (allows all origins for dev). "
        "In-memory job state dictionary (no database yet). Background task execution with full error handling. "
        "Startup/shutdown lifecycle hooks with comprehensive console + file logging."
    )

    pdf.sub_title("API Endpoints:")
    endpoints = [
        ("Endpoint", "Method", "Description"),
        ("GET /", "-", "API info (version, status, endpoint list)"),
        ("GET /health", "-", "Health check (engine status, running job count, timestamp)"),
        ("POST /dock", "File Upload", "Submit docking job (PDB + SMILES). Creates background task, returns job_id"),
        ("GET /jobs/{job_id}", "-", "Poll job status (queued > running > completed/failed)"),
        ("POST /dock-sync", "JSON", "Synchronous docking (blocks, debug only)"),
        ("GET /results/{path}", "-", "Static file serving for result downloads"),
    ]
    for i, row in enumerate(endpoints):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    pdf.ln(4)
    pdf.sub_title("3.2 Docking Engine - backend/docking_engine.py (429 lines)")
    pdf.body_text("DockingEngine class orchestrating the full 4-phase docking pipeline:")
    pdf.bullet("Phase 1 - Ligand Preparation: SMILES to RDKit molecule to 3D embedding to Meeko to PDBQT file")
    pdf.bullet("Phase 2 - Receptor Preparation: PDB to Biopython clean (remove water/heteroatoms) to OpenBabel to PDBQT")
    pdf.bullet("Phase 3 - Box Calculation: Extract atom coordinates, compute center + dimensions with 10A padding")
    pdf.bullet("Phase 4 - Vina Docking: Load receptor + ligand, compute maps, dock (exhaustiveness=8), extract score")

    pdf.ln(2)
    pdf.body_text("Graceful degradation: Vina and OpenBabel are optional imports. Server starts without them and returns "
                  "clear error messages if docking is attempted without them.")

    pdf.sub_title("3.3 Dependency Status:")
    deps = [
        ("Dependency", "Status", "Notes"),
        ("RDKit", "INSTALLED", "Chemistry library - working"),
        ("Meeko", "INSTALLED", "Molecule preparation - working"),
        ("Biopython", "INSTALLED", "PDB parsing - working"),
        ("NumPy", "INSTALLED", "Calculations - working"),
        ("python-multipart", "INSTALLED", "File uploads - working"),
        ("AutoDock Vina", "NOT INSTALLED", "Required for actual docking. Install via conda"),
        ("OpenBabel", "NOT INSTALLED", "Required for PDB to PDBQT conversion. Install via conda"),
    ]
    for i, row in enumerate(deps):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    pdf.ln(4)
    pdf.sub_title("3.4 Sample Data")
    pdf.body_text("data/proteins.json - 10 curated proteins with UniProt IDs: Hemoglobin Beta, Insulin, Myoglobin, "
                  "Lysozyme C, Cytochrome c, p53, EGFR, Amylase, COX-2, ACE2")
    pdf.body_text("data/ligands.json - 10 ligands with PubChem CIDs: Heme B, Glucose, Aspirin, Ibuprofen, Caffeine, "
                  "ATP, Penicillin G, Gefitinib, Metformin, Tamiflu")

    pdf.sub_title("3.5 Other Backend Files")
    pdf.bullet("run.py (106 lines) - One-command launcher: creates .venv, installs deps, starts uvicorn, opens browser")
    pdf.bullet("test_server.py - Backend test suite (36/36 tests passing)")
    pdf.bullet("requirements.txt - All Python dependencies pinned")

    # ============================================================
    # FRONTEND DETAILS
    # ============================================================
    pdf.add_page()
    pdf.section_title("4. FRONTEND - Infrastructure (100% Complete)")

    pdf.body_text("The frontend infrastructure layer is fully built and production-quality. "
                  "React 18, TypeScript, Vite 6, TailwindCSS v4 with a dark purple sci-fi theme.")

    pdf.sub_title("4.1 Data/API Layer (Complete)")
    infra_files = [
        ("File", "Lines", "Description"),
        ("lib/axios.ts", "78", "Axios instance: baseURL from env, 30s timeout, error interceptor with toasts"),
        ("hooks/useDockingJob.ts", "125", "React Query hooks: useDockingJob (smart polling), useSubmitDocking, useHealthCheck"),
        ("stores/useDockingStore.ts", "68", "Zustand: jobs Map, active job, CRUD ops (create/update/remove/clear)"),
        ("stores/useUIStore.ts", "33", "Zustand: dark mode, sidebar, active tab, loading, notifications"),
        ("types/index.ts", "53", "TypeScript interfaces: JobStatus, DockingResult, DockingJob, etc."),
        ("types/api.ts", "78", "Zod schemas for same types (defined but .parse() never called)"),
        ("lib/cn.ts", "11", "clsx + tailwind-merge utility"),
    ]
    for i, row in enumerate(infra_files):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    pdf.ln(4)
    pdf.sub_title("4.2 UI Component Library (Complete)")
    ui_files = [
        ("Component", "Lines", "Description"),
        ("ui/Button.tsx", "43", "5 variants (primary/secondary/destructive/outline/ghost), 3 sizes, forwardRef"),
        ("ui/Card.tsx", "58", "Compound: Card + CardHeader + CardContent + CardFooter, 3 variants"),
        ("ui/Badge.tsx", "32", "5 color variants for status labels"),
        ("ui/LoadingSpinner.tsx", "51", "Animated spinner, 3 sizes, fullscreen mode, LazyLoadingFallback"),
        ("layout/PageContainer.tsx", "14", "Layout wrapper with padding + max-width"),
        ("layout/Navbar.tsx", "79", "Responsive navbar with tabs - BUILT BUT NOT RENDERED"),
    ]
    for i, row in enumerate(ui_files):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    pdf.ln(4)
    pdf.sub_title("4.3 App Shell (Complete)")
    pdf.body_text("App.tsx (270 lines) - Full app shell with QueryClientProvider, sidebar (health status + JobHistory), "
                  "main content with 4 tabs (Docking / Visualize / Results / Settings), lazy-loaded 3D viewer, "
                  "empty states per tab, results summary cards (affinity + RMSD).")
    pdf.body_text("index.css (115 lines) - Dark sci-fi theme with CSS variables (purple primary, green success, "
                  "dark backgrounds). TailwindCSS base/components/utilities layers.")

    pdf.sub_title("4.4 Complete Feature Components")
    pdf.bullet("JobHistory.tsx (107 lines) - FULLY FUNCTIONAL. Sidebar job list with status badges, "
               "affinity scores, view/remove buttons. Integrates with useDockingStore.")

    # ============================================================
    # WHAT'S NOT DONE
    # ============================================================
    pdf.add_page()
    pdf.section_title("5. WHAT'S NOT DONE (Needs Implementation)")

    pdf.body_text("These are the 3 critical placeholder components. They currently render only "
                  "'to be implemented' text (13-22 lines of stub code each).")

    pdf.sub_title("5.1 DockingForm.tsx (PLACEHOLDER - 13 lines)")
    pdf.body_text("Current state: Renders a static card with 'to be implemented' text. No form fields.")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 6, "Needs to become:", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("PDB file upload with drag-and-drop + browse button")
    pdf.bullet("SMILES string text input with validation indicator")
    pdf.bullet("Optional search box coordinate overrides")
    pdf.bullet("Submit button calling useSubmitDocking() hook (already built)")
    pdf.bullet("Loading state during submission + error display for invalid inputs")

    pdf.ln(3)
    pdf.sub_title("5.2 JobStatus.tsx (PLACEHOLDER - 13 lines)")
    pdf.body_text("Current state: Renders a static card with 'to be implemented' text. No polling or status display.")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 6, "Needs to become:", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("Real-time job monitor with animated status indicator (queued, running, completed/failed)")
    pdf.bullet("Progress timeline/stepper visualization")
    pdf.bullet("On completion: display affinity score, box center/size, download link")
    pdf.bullet("On failure: error message with details")
    pdf.bullet("Auto-polls using useDockingJob() hook (already built with smart polling)")

    pdf.ln(3)
    pdf.sub_title("5.3 Viewer3D.tsx (PLACEHOLDER - 22 lines)")
    pdf.body_text("Current state: Renders a gray box with placeholder text. No 3D rendering library integrated.")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 6, "Needs to become:", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("Interactive 3D molecular viewer using 3Dmol.js or NGL Viewer")
    pdf.bullet("Show protein structure with cartoon/ribbon/surface representations")
    pdf.bullet("Show docked ligand pose overlaid on protein")
    pdf.bullet("Controls: rotate, zoom, pan, representation toggles")
    pdf.bullet("Props already defined: pdbContent, title, height")

    # ============================================================
    # KNOWN ISSUES
    # ============================================================
    pdf.add_page()
    pdf.section_title("6. KNOWN ISSUES TO FIX")

    issues = [
        ("Issue", "Priority", "Details"),
        ("Navbar not rendered", "HIGH", "Navbar.tsx fully built but never imported in App.tsx"),
        ("Type duplication", "MEDIUM", "types/index.ts and types/api.ts have overlapping inconsistent types"),
        ("Zod not wired", "LOW", "Zod schemas exist but .parse() never called - no runtime validation"),
        ("Landing page outdated", "LOW", "frontend/pages/ still references port 8501 (old Streamlit app)"),
        ("No database", "MEDIUM", "Jobs in-memory dict - lost on server restart. Needs SQLite"),
        ("Vina not installed", "INFO", "Server runs fine but actual docking requires conda install"),
    ]
    for i, row in enumerate(issues):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    # ============================================================
    # FILE STRUCTURE
    # ============================================================
    pdf.ln(6)
    pdf.section_title("7. CURRENT FILE STRUCTURE")

    tree = """BIOCANVAS/
  README.md                     # Professional project README
  .env.example                  # Config template
  requirements.txt              # Python deps
  run.py                        # One-command launcher
  test_server.py                # Backend tests

  backend/
    __init__.py
    main.py                     # FastAPI server (478 lines) - COMPLETE
    docking_engine.py           # Docking pipeline (429 lines) - COMPLETE
    routers/                    # Empty (routes in main.py)

  frontend/
    index.html                  # Vite entry
    package.json                # React 18 + Vite 6 + TS
    vite.config.ts / tailwind.config.js / tsconfig.json
    pages/                      # Landing page (outdated)
    src/
      App.tsx                   # App shell (270 lines) - COMPLETE
      main.tsx / index.css      # Entry + dark theme
      components/
        features/
          DockingForm.tsx       # PLACEHOLDER (13 lines)
          JobStatus.tsx         # PLACEHOLDER (13 lines)
          JobHistory.tsx        # COMPLETE (107 lines)
        science/
          Viewer3D.tsx          # PLACEHOLDER (22 lines)
        layout/
          Navbar.tsx            # COMPLETE but NOT rendered
          PageContainer.tsx     # COMPLETE
        ui/
          Badge.tsx / Button.tsx / Card.tsx / LoadingSpinner.tsx  # ALL COMPLETE
      hooks/
        useDockingJob.ts        # COMPLETE (125 lines)
      stores/
        useDockingStore.ts      # COMPLETE (68 lines)
        useUIStore.ts           # COMPLETE (33 lines)
      types/
        index.ts / api.ts       # COMPLETE (type duplication issue)
      lib/
        axios.ts / cn.ts        # COMPLETE

  data/
    proteins.json               # 10 proteins with UniProt IDs
    ligands.json                # 10 ligands with PubChem CIDs

  docking_jobs/                 # Working directory for jobs
  tests/                        # Test suite
  docs/
    ARCHITECTURE.md / FRONTEND_GUIDE.md / API_REFERENCE.md / DEPLOYMENT.md"""

    pdf.code_block(tree)

    # ============================================================
    # PROGRESS SUMMARY
    # ============================================================
    pdf.add_page()
    pdf.section_title("8. PROGRESS SUMMARY")

    progress = [
        ("Area", "Progress", "Details"),
        ("Backend API", "100%", "All endpoints working, tested, production-ready"),
        ("Docking Engine", "100%", "Full pipeline coded, graceful degradation"),
        ("Frontend Infrastructure", "100%", "Axios, React Query, Zustand, types, theme"),
        ("Frontend UI Primitives", "100%", "Button, Card, Badge, Spinner, PageContainer"),
        ("Frontend App Shell", "95%", "Full layout with tabs - just missing Navbar render"),
        ("DockingForm Component", "0%", "Placeholder stub only"),
        ("JobStatus Component", "0%", "Placeholder stub only"),
        ("3D Viewer Component", "0%", "Placeholder stub only"),
        ("Database/Persistence", "0%", "Jobs in memory only"),
        ("Authentication", "0%", "Not started"),
        ("Landing Page", "80%", "Built but references old port"),
    ]
    for i, row in enumerate(progress):
        pdf.status_row(row[0], row[1], row[2], is_header=(i == 0))

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 10, "OVERALL: ~65-70% Complete", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6,
        "The backend is 100% done. The frontend foundation is 100% done. "
        "What remains is building the 3 core feature components (DockingForm, JobStatus, Viewer3D), "
        "wiring in the Navbar, and fixing minor issues (type duplication, Zod runtime validation, "
        "landing page port update)."
    )

    # ============================================================
    # NEXT STEPS
    # ============================================================
    pdf.ln(6)
    pdf.section_title("9. RECOMMENDED NEXT STEPS")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)

    steps = [
        "1. Wire Navbar.tsx into App.tsx (5 min fix - just import and render)",
        "2. Build DockingForm.tsx - file upload + SMILES input + submit handler",
        "3. Build JobStatus.tsx - real-time polling display with progress timeline",
        "4. Build Viewer3D.tsx - integrate 3Dmol.js for molecular visualization",
        "5. Consolidate types/index.ts and types/api.ts (remove duplication)",
        "6. Wire Zod schemas for runtime API response validation",
        "7. Update landing page (frontend/pages/) to reference correct ports",
        "8. Add SQLite database for job persistence across server restarts",
        "9. Install AutoDock Vina + OpenBabel for real docking calculations",
        "10. Add user authentication (JWT-based)",
    ]
    for step in steps:
        pdf.bullet(step)

    pdf.ln(8)
    pdf.set_draw_color(139, 92, 246)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "End of Report - Generated on February 20, 2026", align="C")

    # ============================================================
    # SAVE
    # ============================================================
    output_path = os.path.join(os.path.dirname(__file__), "BIOCANVAS_Project_Status_Report.pdf")
    pdf.output(output_path)
    print(f"\nPDF generated successfully!")
    print(f"Location: {output_path}")
    print(f"Pages: {pdf.page_no()}")
    return output_path


if __name__ == "__main__":
    generate_report()
