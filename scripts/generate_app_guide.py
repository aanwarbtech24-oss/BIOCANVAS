"""
Generate BIOCANVAS v2.0 - Complete Web App Guide (PDF)
"""
from fpdf import FPDF
from datetime import datetime


class AppGuidePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "BIOCANVAS v2.0 - Complete Web Application Guide", align="L")
        self.ln(4)
        self.set_draw_color(139, 92, 246)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(139, 92, 246)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(139, 92, 246)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(139, 92, 246)
        self.cell(indent, 5.5, " - ")
        self.set_text_color(50, 50, 50)
        self.multi_cell(190 - indent - 10, 5.5, text)
        self.ln(1)

    def table_row(self, col1, col2, bold_first=False):
        self.set_font("Helvetica", "B" if bold_first else "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.cell(55, 7, col1, border=1)
        self.set_font("Helvetica", "", 10)
        self.cell(135, 7, col2, border=1)
        self.ln()

    def table_header(self, col1, col2):
        self.set_fill_color(139, 92, 246)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(55, 8, col1, border=1, fill=True)
        self.cell(135, 8, col2, border=1, fill=True)
        self.ln()
        self.set_text_color(50, 50, 50)

    def wide_table_header(self, col1, col2, col3):
        self.set_fill_color(139, 92, 246)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(40, 8, col1, border=1, fill=True)
        self.cell(25, 8, col2, border=1, fill=True)
        self.cell(125, 8, col3, border=1, fill=True)
        self.ln()
        self.set_text_color(50, 50, 50)

    def wide_table_row(self, col1, col2, col3):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(50, 50, 50)
        self.cell(40, 7, col1, border=1)
        self.set_font("Helvetica", "", 9)
        self.cell(25, 7, col2, border=1)
        self.cell(125, 7, col3, border=1)
        self.ln()


def generate():
    pdf = AppGuidePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ---- COVER PAGE ----
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(0, 15, "BIOCANVAS v2.0", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Complete Web Application Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Educational End-to-End Drug Discovery Platform", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%B %d, %Y')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Frontend: React 18 + TypeScript + Vite 6 + TailwindCSS v4", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Backend: FastAPI + Python 3.13 + AutoDock Vina", align="C", new_x="LMARGIN", new_y="NEXT")

    # ---- ARCHITECTURE ----
    pdf.add_page()
    pdf.section_title("1. Architecture Overview")
    pdf.body_text(
        "BIOCANVAS v2.0 is a full-stack molecular docking platform with a clear "
        "separation between frontend and backend."
    )
    pdf.bold_text("Data Flow:")
    pdf.bullet("Frontend (React, port 5173) communicates with Backend (FastAPI, port 8000) via REST API")
    pdf.bullet("Frontend fetches 3D protein structures directly from AlphaFold DB (via UniProt ID)")
    pdf.bullet("Frontend fetches 3D ligand structures directly from PubChem (via CID)")
    pdf.bullet("Backend handles docking job submission, execution (AutoDock Vina), and result storage")
    pdf.bullet("State managed client-side with Zustand (local) and React Query (server)")

    pdf.ln(4)
    pdf.bold_text("Server URLs:")
    pdf.ln(2)
    pdf.table_header("Service", "URL")
    pdf.table_row("Frontend", "http://localhost:5173")
    pdf.table_row("Backend API", "http://localhost:8000")
    pdf.table_row("Swagger Docs", "http://localhost:8000/docs")
    pdf.table_row("ReDoc", "http://localhost:8000/redoc")

    # ---- NAVIGATION ----
    pdf.ln(6)
    pdf.section_title("2. Navigation")
    pdf.body_text(
        "The app has a sticky top navigation bar (Navbar) with the BIOCANVAS logo "
        "and four tabs. The tab order is:"
    )
    pdf.bold_text("Visualize  ->  Docking  ->  Results  ->  Settings")
    pdf.body_text(
        "The default landing page is Visualize. On mobile, tabs collapse into a "
        "scrollable horizontal bar. A hamburger menu toggles the sidebar."
    )
    pdf.body_text(
        "A persistent left sidebar is visible on all pages. It contains a Backend "
        "Status card (green/red health indicator, engine status, running job count) "
        "and a scrollable Job History list."
    )

    # ---- PAGE 1: VISUALIZE ----
    pdf.add_page()
    pdf.section_title("3. Page 1: Visualize (Default)")
    pdf.bold_text("Purpose:")
    pdf.body_text(
        "Browse and visualize the curated molecule library with real-time 3D rendering. "
        "Protein and ligand structures are displayed side by side."
    )

    pdf.bold_text("Layout:")
    pdf.bullet("Two dropdown selectors at the top - protein (left) and ligand (right)")
    pdf.bullet("Two independent 3D WebGL viewers below - protein on left, ligand on right")
    pdf.bullet("Info cards beneath each viewer with metadata and external links")

    pdf.ln(2)
    pdf.bold_text("How It Works:")
    pdf.bullet("Click the protein dropdown to see all 10 proteins with name, category badge, function, and UniProt ID")
    pdf.bullet("Select a protein (e.g., Hemoglobin Beta) - the app calls the AlphaFold prediction API to resolve the latest PDB URL, downloads it, and renders a 3D model")
    pdf.bullet("Click the ligand dropdown to see all 10 ligands with name, type badge, description, and PubChem CID")
    pdf.bullet("Select a ligand (e.g., Aspirin) - fetches 3D SDF from PubChem and renders it. Falls back to 2D if no 3D conformer exists")
    pdf.bullet("Both viewers are fully independent - rotate, zoom, and change rendering style on each")
    pdf.bullet("Style options: Cartoon (rainbow), Stick, Sphere, Surface")
    pdf.bullet("Info cards link directly to UniProt and PubChem pages")

    pdf.ln(2)
    pdf.bold_text("Protein Library (10):")
    pdf.ln(2)
    proteins = [
        ("Hemoglobin Beta", "P68871", "Transport", "Transports oxygen in blood"),
        ("Insulin", "P01308", "Hormone", "Regulates blood glucose levels"),
        ("Myoglobin", "P02144", "Storage", "Stores oxygen in muscle tissue"),
        ("Lysozyme C", "P00698", "Enzyme", "Breaks down bacterial cell walls"),
        ("Cytochrome c", "P99999", "Transport", "Transfers electrons in mitochondria"),
        ("p53 Tumor Suppressor", "P04637", "Regulation", "Regulates cell division"),
        ("EGFR", "P00533", "Receptor", "Controls cell growth signaling"),
        ("Carbonic Anhydrase II", "P00915", "Enzyme", "Balances pH in blood"),
        ("Serum Albumin", "P02768", "Transport", "Transports hormones and fatty acids"),
        ("Pancreatic Alpha-Amylase", "P04746", "Enzyme", "Breaks down starch into sugars"),
    ]
    for name, uid, cat, func in proteins:
        pdf.bullet(f"{name} ({uid}) [{cat}] - {func}")

    pdf.add_page()
    pdf.bold_text("Ligand Library (10):")
    pdf.ln(2)
    ligands = [
        ("Heme B", "4973", "Cofactor", "Iron-containing molecule for oxygen binding"),
        ("Glucose", "5793", "Carbohydrate", "Primary energy source for cells"),
        ("Aspirin", "2244", "Drug", "Anti-inflammatory COX inhibitor"),
        ("Ibuprofen", "3672", "Drug", "Non-steroidal anti-inflammatory (NSAID)"),
        ("Caffeine", "2519", "Stimulant", "CNS stimulant, blocks adenosine receptors"),
        ("ATP", "5957", "Metabolite", "Primary energy currency of the cell"),
        ("Penicillin G", "5904", "Antibiotic", "Targets bacterial cell walls"),
        ("Dopamine", "681", "Neurotransmitter", "Reward and motor control messenger"),
        ("Cholesterol", "5997", "Lipid", "Cell membrane component"),
        ("Gefitinib", "123631", "Drug", "Cancer medication targeting EGFR"),
    ]
    for name, cid, typ, desc in ligands:
        pdf.bullet(f"{name} (CID {cid}) [{typ}] - {desc}")

    # ---- PAGE 2: DOCKING ----
    pdf.ln(4)
    pdf.section_title("4. Page 2: Docking")
    pdf.bold_text("Purpose:")
    pdf.body_text("Submit molecular docking jobs to the backend for computation.")

    pdf.bold_text("Layout:")
    pdf.bullet("DockingForm - the main submission form (top)")
    pdf.bullet("Job Monitor - appears below once a job is submitted")
    pdf.bullet("Empty state - beaker icon prompting submission when no active job")

    pdf.ln(2)
    pdf.bold_text("How It Works:")
    pdf.bullet("Upload a PDB file via drag-and-drop zone or file browser. Validates .pdb extension")
    pdf.bullet("Enter a SMILES string for the ligand's chemical structure (monospace input)")
    pdf.bullet("Expand Advanced Settings accordion to configure grid box center (X, Y, Z) and size (X, Y, Z)")
    pdf.bullet("Click Submit - sends FormData (file + SMILES) to POST /dock on the backend")
    pdf.bullet("Backend generates a job ID, saves the PDB file, and runs AutoDock Vina in a background thread")
    pdf.bullet("Job Monitor polls GET /jobs/{job_id} every 2 seconds showing status: queued -> running -> completed/failed")
    pdf.bullet("404 Killswitch: if the backend restarts and loses the job, polling stops and shows a 'job lost' state instead of retrying forever")

    # ---- PAGE 3: RESULTS ----
    pdf.add_page()
    pdf.section_title("5. Page 3: Results")
    pdf.bold_text("Purpose:")
    pdf.body_text("Display docking results for the currently active job.")

    pdf.bold_text("Layout:")
    pdf.bullet("Two metric cards at the top: Affinity Score (kcal/mol) and RMSD (Angstroms)")
    pdf.bullet("Job Details card below: Job ID, status, SMILES used, affinity value")
    pdf.bullet("Empty state when no completed job exists")

    pdf.ln(2)
    pdf.bold_text("How It Works:")
    pdf.bullet("Reads data from the active job in the Zustand store")
    pdf.bullet("Displays binding affinity (how strongly the ligand binds to the protein)")
    pdf.bullet("Displays RMSD (root-mean-square deviation) measuring structural accuracy")
    pdf.bullet("Job ID is truncated for display; full ID available in details")

    # ---- PAGE 4: SETTINGS ----
    pdf.ln(4)
    pdf.section_title("6. Page 4: Settings")
    pdf.body_text(
        "Currently a placeholder page showing a 'Coming soon' message. "
        "Future features planned: backend connection settings, default docking "
        "parameters, theme preferences, API key management."
    )

    # ---- SIDEBAR ----
    pdf.ln(4)
    pdf.section_title("7. Sidebar (All Pages)")
    pdf.bold_text("Backend Status Card:")
    pdf.bullet("Green/red dot showing if the FastAPI server is online")
    pdf.bullet("Engine status (ready/error)")
    pdf.bullet("Number of currently running docking jobs")
    pdf.bullet("Polls GET /health endpoint automatically")

    pdf.ln(2)
    pdf.bold_text("Job History:")
    pdf.bullet("Scrollable list of all submitted docking jobs")
    pdf.bullet("Each entry shows status badge (queued/running/completed/failed) and timestamp")
    pdf.bullet("Click any job to make it the active job (updates Results and Job Monitor)")

    # ---- API ENDPOINTS ----
    pdf.add_page()
    pdf.section_title("8. Backend API Endpoints")
    pdf.body_text("All endpoints are served from http://localhost:8000")
    pdf.ln(2)

    pdf.wide_table_header("Endpoint", "Method", "Purpose")
    endpoints = [
        ("/health", "GET", "Server health check + running job count"),
        ("/", "GET", "API info and available routes"),
        ("/proteins", "GET", "Returns 10 curated proteins from data/proteins.json"),
        ("/ligands", "GET", "Returns 10 curated ligands from data/ligands.json"),
        ("/dock", "POST", "Submit docking job (PDB file upload + SMILES string)"),
        ("/jobs/{job_id}", "GET", "Get job status, progress, and results"),
        ("/dock-sync", "POST", "Debug-only synchronous docking (blocks until done)"),
        ("/docs", "GET", "Interactive Swagger UI documentation"),
        ("/redoc", "GET", "Read-only ReDoc documentation"),
    ]
    for ep, method, purpose in endpoints:
        pdf.wide_table_row(ep, method, purpose)

    # ---- TECH STACK ----
    pdf.ln(8)
    pdf.section_title("9. Technology Stack")
    pdf.ln(2)
    pdf.table_header("Layer", "Technology")
    stack = [
        ("UI Framework", "React 18.3 + TypeScript 5.9"),
        ("Bundler", "Vite 6.4"),
        ("Styling", "Tailwind CSS v4.1"),
        ("State (Client)", "Zustand v5"),
        ("State (Server)", "TanStack React Query v5"),
        ("HTTP Client", "Axios (backend), native fetch (external APIs)"),
        ("3D Rendering", "3Dmol.js (WebGL)"),
        ("Toast Notifications", "Sonner"),
        ("Icons", "Lucide React"),
        ("Validation", "Zod v4"),
        ("Backend Framework", "FastAPI + Uvicorn"),
        ("Python", "3.13.5 (virtual environment)"),
        ("Docking Engine", "RDKit + Meeko + AutoDock Vina"),
        ("Protein Data", "AlphaFold DB (EBI)"),
        ("Ligand Data", "PubChem (NCBI)"),
    ]
    for layer, tech in stack:
        pdf.table_row(layer, tech, bold_first=True)

    # ---- SAVE ----
    output_path = "BIOCANVAS_Web_App_Guide.pdf"
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    generate()
