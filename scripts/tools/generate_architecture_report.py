#!/usr/bin/env python3
"""
BIOCANVAS v2.0 - Architecture Documentation Generator
Generates a comprehensive architecture report in PDF format
"""

import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Output file
OUTPUT_FILE = "BIOCANVAS_Architecture_Report.pdf"

# Color scheme
PRIMARY_COLOR = colors.HexColor("#6366f1")  # Indigo
SECONDARY_COLOR = colors.HexColor("#10b981")  # Emerald
ACCENT_COLOR = colors.HexColor("#f59e0b")  # Amber
DARK_BG = colors.HexColor("#1e293b")  # Slate dark
LIGHT_BG = colors.HexColor("#f8fafc")  # Slate light

def create_document():
    """Create the PDF document"""
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=LETTER,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    return doc

def get_styles():
    """Create custom styles for the document"""
    # Create styles from scratch to avoid name conflicts
    styles = {}
    
    # Title style
    styles['CustomTitle'] = ParagraphStyle(
        name='CustomTitle',
        fontSize=28,
        textColor=PRIMARY_COLOR,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Section header
    styles['SectionHeader'] = ParagraphStyle(
        name='SectionHeader',
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Subsection header
    styles['SubSectionHeader'] = ParagraphStyle(
        name='SubSectionHeader',
        fontSize=13,
        textColor=DARK_BG,
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    # Body text
    styles['BodyText'] = ParagraphStyle(
        name='BodyText',
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    # Title style
    styles['Title'] = ParagraphStyle(
        name='Title',
        fontSize=24,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    
    # Subtitle
    styles['Subtitle'] = ParagraphStyle(
        name='Subtitle',
        fontSize=16,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Tagline
    styles['Tagline'] = ParagraphStyle(
        name='Tagline',
        fontSize=14,
        textColor=SECONDARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=40
    )
    
    # Footer
    styles['Footer'] = ParagraphStyle(
        name='Footer',
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    
    # Return as a dict-like object
    return styles

def create_title_page(styles):
    """Create the title page"""
    story = []
    
    # Main title
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("BIOCANVAS", styles['CustomTitle']))
    story.append(Paragraph("v2.0", styles['Title']))
    
    # Subtitle
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "<b>Comprehensive Architecture Documentation</b>",
        ParagraphStyle(
            name='Subtitle',
            fontSize=16,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=20
        )
    ))
    
    # Tagline
    story.append(Paragraph(
        "Production-Ready Molecular Docking Platform",
        ParagraphStyle(
            name='Tagline',
            fontSize=14,
            textColor=SECONDARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=40
        )
    ))
    
    # Metadata table
    meta_data = [
        ['Version', '2.0.0'],
        ['Release Date', datetime.now().strftime('%B %d, %Y')],
        ['Architecture', 'FastAPI + React'],
        ['Docking Engine', 'AutoDock Vina'],
        ['License', 'Proprietary']
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 3*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray)
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 1.5*inch))
    
    # Footer
    story.append(Paragraph(
        "For Developer Team Review",
        ParagraphStyle(
            name='Footer',
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER
        )
    ))
    
    return story

def create_overview_section(styles):
    """Create the system overview section"""
    story = []
    
    story.append(Paragraph("1. System Overview", styles['SectionHeader']))
    
    # Introduction
    story.append(Paragraph(
        "BIOCANVAS is a modern, full-stack bioinformatics application for computational "
        "chemistry research and drug discovery. It combines a powerful FastAPI backend with a "
        "responsive React frontend to provide an intuitive interface for molecular docking "
        "calculations using AutoDock Vina.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("1.1 Key Features", styles['SubSectionHeader']))
    
    features = [
        "FastAPI Backend - High-performance async API with automatic OpenAPI documentation",
        "React Frontend - Modern, responsive web interface with TypeScript",
        "Molecular Docking - AutoDock Vina integration for protein-ligand docking",
        "3D Visualization - Interactive molecular structure viewing using 3Dmol.js",
        "Job Management - Track docking jobs and results with SQLite persistence",
        "Async Tasks - Non-blocking job processing with background tasks",
        "Lipinski Analysis - Drug-likeness evaluation using Rule of Five",
        "PLIP Integration - Protein-ligand interaction analysis"
    ]
    
    for feature in features:
        story.append(Paragraph(f"• {feature}", styles['BodyText']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Technology Stack
    story.append(Paragraph("1.2 Technology Stack", styles['SubSectionHeader']))
    
    tech_data = [
        ['Category', 'Technology', 'Version'],
        ['Backend Framework', 'FastAPI', '0.109.0'],
        ['ASGI Server', 'Uvicorn', '0.27.0'],
        ['Data Validation', 'Pydantic', '2.5.3'],
        ['Frontend Framework', 'React', '18.3.1'],
        ['Build Tool', 'Vite', '6.4.1'],
        ['State Management', 'Zustand', '5.0.11'],
        ['Data Fetching', 'React Query', '5.90.20'],
        ['Molecular Viewer', '3Dmol.js', '2.0.4'],
        ['Molecular Docking', 'AutoDock Vina', '1.2.5+'],
        ['Chemistry Toolkit', 'RDKit', '2024.03.1'],
        ['Database', 'SQLite', '3.x']
    ]
    
    tech_table = Table(tech_data, colWidths=[2*inch, 2.5*inch, 1*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(tech_table)
    
    return story

def create_backend_section(styles):
    """Create the backend architecture section"""
    story = []
    
    story.append(Paragraph("2. Backend Architecture", styles['SectionHeader']))
    
    # Overview
    story.append(Paragraph(
        "The backend is built on FastAPI, providing a high-performance, asynchronous API "
        "for molecular docking operations. It handles job submission, manages docking workflows, "
        "and persists job state using SQLite.",
        styles['BodyText']
    ))
    
    # Components
    story.append(Paragraph("2.1 Core Components", styles['SubSectionHeader']))
    
    components = [
        ("backend/main.py", "FastAPI application entry point. Defines API routes, CORS middleware, "
                           "rate limiting, and background task management."),
        ("backend/docking_engine.py", "DockingEngine class. Handles ligand/receptor preparation, "
                                      "Vina docking execution, and result parsing."),
        ("backend/job_store.py", "SQLite-backed job persistence. Provides CRUD operations for "
                                 "tracking docking job status and results.")
    ]
    
    for file, desc in components:
        story.append(Paragraph(f"<b>{file}</b>", styles['BodyText']))
        story.append(Paragraph(desc, styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    # API Endpoints
    story.append(Paragraph("2.2 API Endpoints", styles['SubSectionHeader']))
    
    endpoints = [
        ['Method', 'Endpoint', 'Description'],
        ['GET', '/', 'Service info and status'],
        ['GET', '/health', 'Backend health check with engine status'],
        ['POST', '/dock', 'Submit new docking job (multipart form)'],
        ['GET', '/jobs/{job_id}', 'Get job status and results'],
        ['GET', '/proteins', 'Get curated protein library'],
        ['GET', '/ligands', 'Get curated ligand library']
    ]
    
    endpoint_table = Table(endpoints, colWidths=[0.8*inch, 2*inch, 3.2*inch])
    endpoint_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(endpoint_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Docking Workflow
    story.append(Paragraph("2.3 Docking Workflow", styles['SubSectionHeader']))
    
    workflow_steps = [
        "1. Client submits PDB file + SMILES string via POST /dock",
        "2. Server creates job record in SQLite with 'queued' status",
        "3. Background task executes _run_docking_job:",
        "   a. Prepare receptor: Convert PDB → PDBQT (add polar hydrogens, assign charges)",
        "   b. Prepare ligand: Convert SMILES → 3D structure → PDBQT via RDKit + Meeko",
        "   c. Calculate binding site: Find ligand centroid, define search box (20Å³)",
        "   d. Execute Vina: Run docking with exhaustiveness=8, max 9 poses",
        "   e. Parse results: Extract affinities, RMSD values, ligand efficiency",
        "   f. Run PLIP: Analyze non-covalent interactions (H-bonds, hydrophobic, π-stacking)",
        "4. Update job record with results, set status to 'completed' or 'failed'",
        "5. Client polls GET /jobs/{job_id} until status is terminal"
    ]
    
    for step in workflow_steps:
        story.append(Paragraph(step, styles['BodyText']))
    
    # Job State Machine
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("2.4 Job State Machine", styles['SubSectionHeader']))
    
    states = [
        ['State', 'Description'],
        ['queued', 'Job created, waiting for background worker'],
        ['running', 'Docking simulation in progress'],
        ['completed', 'Successfully finished with results'],
        ['failed', 'Error occurred during docking']
    ]
    
    state_table = Table(states, colWidths=[1.5*inch, 4.5*inch])
    state_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(state_table)
    
    return story

def create_frontend_section(styles):
    """Create the frontend architecture section"""
    story = []
    
    story.append(Paragraph("3. Frontend Architecture", styles['SectionHeader']))
    
    # Overview
    story.append(Paragraph(
        "The frontend is a React 18 application built with TypeScript, using Vite as the "
        "build tool. It features a wizard-style docking pipeline and dual molecule viewer "
        "for visualizing proteins and ligands.",
        styles['BodyText']
    ))
    
    # Project Structure
    story.append(Paragraph("3.1 Project Structure", styles['SubSectionHeader']))
    
    structure = [
        ['Path', 'Purpose'],
        ['src/App.tsx', 'Root component with QueryClient provider'],
        ['src/components/features/DockingPipeline.tsx', '4-step wizard orchestrator'],
        ['src/components/features/VisualizePage.tsx', 'Dual molecule viewer page'],
        ['src/components/features/docking-steps/', 'Step components (1-4)'],
        ['src/components/science/Viewer3D.tsx', '3Dmol.js wrapper for proteins'],
        ['src/components/science/DockingViewer3D.tsx', 'Complex viewer with interactions'],
        ['src/hooks/useDockingJob.ts', 'Job submission + polling hooks'],
        ['src/hooks/useMoleculeLibrary.ts', 'Protein/ligand data fetching'],
        ['src/stores/useDockingStore.ts', 'Zustand store for job state'],
        ['src/types/api.ts', 'TypeScript interfaces for API types']
    ]
    
    structure_table = Table(structure, colWidths=[2.5*inch, 3.5*inch])
    structure_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(structure_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Docking Pipeline Steps
    story.append(Paragraph("3.2 Docking Pipeline Steps", styles['SubSectionHeader']))
    
    steps = [
        ['Step', 'Name', 'Description'],
        ['1', 'Protein Target', 'Select from curated library or upload custom PDB'],
        ['2', 'Ligand Selection', 'Choose ligand from library or enter custom SMILES'],
        ['3', 'Docking Run', 'Submit job, monitor progress, view real-time status'],
        ['4', 'Results', 'View affinities, poses, Lipinski profile, interactions']
    ]
    
    step_table = Table(steps, colWidths=[0.5*inch, 1.5*inch, 4*inch])
    step_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(step_table)
    story.append(Spacer(1, 0.2*inch))
    
    # State Management
    story.append(Paragraph("3.3 State Management", styles['SubSectionHeader']))
    
    story.append(Paragraph(
        "The application uses Zustand for global state management with two stores:",
        styles['BodyText']
    ))
    
    stores = [
        ("useDockingStore", "Manages docking job state: jobs map, activeJobId, activePoseIndex, "
                          "CRUD operations for jobs, result updates"),
        ("useUIStore", "Manages UI state: activeTab ('docking' or 'visualize'), theme preferences")
    ]
    
    for store_name, desc in stores:
        story.append(Paragraph(f"<b>{store_name}</b>", styles['BodyText']))
        story.append(Paragraph(desc, styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    # Data Fetching
    story.append(Paragraph("3.4 Data Fetching Strategy", styles['SubSectionHeader']))
    
    story.append(Paragraph(
        "React Query (TanStack Query) handles all server state with the following patterns:",
        styles['BodyText']
    ))
    
    patterns = [
        "Smart polling: refetchInterval=2000ms for job status until terminal state",
        "Race-condition prevention: AbortController signals cancel stale requests",
        "Caching: 30-minute staleTime for protein/ligand libraries",
        "Error handling: Toast notifications via Sonner"
    ]
    
    for pattern in patterns:
        story.append(Paragraph(f"• {pattern}", styles['BodyText']))
    
    return story

def create_data_flow_section(styles):
    """Create the data flow section"""
    story = []
    
    story.append(Paragraph("4. Data Flow & Integration", styles['SectionHeader']))
    
    # External APIs
    story.append(Paragraph("4.1 External API Integrations", styles['SubSectionHeader']))
    
    apis = [
        ['Service', 'Purpose', 'Endpoint'],
        ['AlphaFold DB', 'Fetch protein 3D structures', 'https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}'],
        ['PubChem', 'Fetch ligand 3D conformers', 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF'],
        ['AutoDock Vina', 'Molecular docking simulations', 'Local installation (conda)']
    ]
    
    api_table = Table(apis, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    story.append(api_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Data Flow Diagram (text-based)
    story.append(Paragraph("4.2 Data Flow Architecture", styles['SubSectionHeader']))
    
    flow = [
        "┌─────────────────────────────────────────────────────────────────────────┐",
        "│                           FRONTEND (React)                              │",
        "│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │",
        "│  │   Docking    │  │   Visualize  │  │   3Dmol.js   │  │   Zustand  │ │",
        "│  │   Pipeline   │  │     Page     │  │   Viewer     │  │   Store    │ │",
        "│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  └──────┬─────┘ │",
        "│         │                 │                                    │       │",
        "│         └────────────────┼────────────────────────────────────┘       │",
        "│                          │                                         │",
        "│                    ┌─────▼─────┐                                    │",
        "│                    │   axios   │                                    │",
        "│                    │ instance  │                                    │",
        "│                    └─────┬─────┘                                    │",
        "└──────────────────────────┼───────────────────────────────────────────┘",
        "                              │",
        "                    ┌─────────▼─────────┐",
        "                    │   REST API (8000) │",
        "                    └─────────┬─────────┘",
        "                              │",
        "         ┌────────────────────┼────────────────────┐",
        "         │                    │                    │",
        "   ┌─────▼─────┐       ┌─────▼─────┐       ┌──────▼──────┐",
        "   │  /health  │       │   /dock   │       │ /proteins   │",
        "   │ /jobs/{id}│       │  (submit) │       │  /ligands   │",
        "   └─────┬─────┘       └─────┬─────┘       └──────┬──────┘",
        "         │                    │                    │",
        "         │              ┌─────▼─────┐              │",
        "         │              │  Docking  │              │",
        "         │              │  Engine   │              │",
        "         │              └─────┬─────┘              │",
        "         │                    │                    │",
        "   ┌─────▼───────────────►   │   ◄─────────────    │",
        "   │     Job Store        │                    │",
        "   │     (SQLite)         │                    │",
        "   └──────────────────────┘                    │",
        "                                                │",
        "                    ┌────────────────────────────▼───────────┐",
        "                    │          EXTERNAL SERVICES           │",
        "                    │  ┌────────────┐  ┌────────────────┐  │",
        "                    │  │  AlphaFold │  │    PubChem     │  │",
        "                    │  │     DB     │  │    (3D SDF)    │  │",
        "                    │  └────────────┘  └────────────────┘  │",
        "                    │                                       │",
        "                    │  ┌────────────────────────────┐     │",
        "                    │  │      AutoDock Vina        │     │",
        "                    │  │    (Local Installation)    │     │",
        "                    │  └────────────────────────────┘     │",
        "                    └───────────────────────────────────────┘"
    ]
    
    for line in flow:
        story.append(Paragraph(
            f"<font face='Courier' size='7'>{line}</font>",
            styles['BodyText']
        ))
    
    return story

def create_security_section(styles):
    """Create the security section"""
    story = []
    
    story.append(Paragraph("5. Security & Performance", styles['SectionHeader']))
    
    # Security
    story.append(Paragraph("5.1 Security Measures", styles['SubSectionHeader']))
    
    security = [
        "CORS Configuration: Restricts cross-origin requests to known origins",
        "Rate Limiting: IP-based token bucket algorithm (10 requests/minute)",
        "Input Validation: Pydantic models validate all request payloads",
        "File Upload Restrictions: Only .pdb files accepted, size limits enforced",
        "SQLite with WAL mode: Prevents database locking issues",
        "Error Handling: Internal errors not exposed to clients (generic messages)"
    ]
    
    for item in security:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Performance
    story.append(Paragraph("5.2 Performance Optimizations", styles['SubSectionHeader']))
    
    perf = [
        "Async I/O: FastAPI handles concurrent requests without threading",
        "Background Tasks: Docking simulations don't block the API",
        "React Query Caching: Minimize redundant API calls",
        "3Dmol.js WebGL: Hardware-accelerated molecular rendering",
        "SQLite WAL Mode: Improved concurrent read/write performance",
        "Static Frontend: Vite builds optimized production bundles"
    ]
    
    for item in perf:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    
    return story

def create_deployment_section(styles):
    """Create the deployment section"""
    story = []
    
    story.append(Paragraph("6. Deployment & Development", styles['SectionHeader']))
    
    # Quick Start
    story.append(Paragraph("6.1 Quick Start", styles['SubSectionHeader']))
    
    start = [
        "1. Clone the repository",
        "2. Run: <code>python3 run.py</code> (auto-installs dependencies)",
        "3. Backend starts on http://localhost:8000",
        "4. Frontend starts on http://localhost:5173"
    ]
    
    for item in start:
        story.append(Paragraph(item, styles['BodyText']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Requirements
    story.append(Paragraph("6.2 System Requirements", styles['SubSectionHeader']))
    
    reqs = [
        "Python 3.9+ with pip",
        "Node.js 16+ with npm",
        "4GB RAM minimum",
        "AutoDock Vina (optional, for real docking)"
    ]
    
    for item in reqs:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Testing
    story.append(Paragraph("6.3 Testing", styles['SubSectionHeader']))
    
    testing = [
        ("Backend Tests", "python3 test_server.py - Tests API endpoints"),
        ("Frontend Tests", "cd frontend && npm test - Runs Vitest unit tests"),
        ("E2E Test", "python3 tests/e2e_docking_test.py - Full docking workflow")
    ]
    
    for name, cmd in testing:
        story.append(Paragraph(f"<b>{name}</b>: {cmd}", styles['BodyText']))
    
    return story

def create_future_section(styles):
    """Create the future roadmap section"""
    story = []
    
    story.append(Paragraph("7. Roadmap & Future Enhancements", styles['SectionHeader']))
    
    # Planned Features
    story.append(Paragraph("7.1 Planned Features", styles['SubSectionHeader']))
    
    planned = [
        ("v2.1", [
            "User authentication and authorization",
            "Job history with filtering and search",
            "Advanced result export (PDF reports)",
            "Batch docking for multiple ligands"
        ]),
        ("v3.0", [
            "Multi-GPU support for parallel docking",
            "Real-time collaboration features",
            "Integration with external drug databases",
            "Advanced visualization modes"
        ])
    ]
    
    for version, features in planned:
        story.append(Paragraph(f"<b>{version}</b>", styles['BodyText']))
        for feature in features:
            story.append(Paragraph(f"  • {feature}", styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    # Contribution
    story.append(Paragraph("7.2 Contributing", styles['SubSectionHeader']))
    
    story.append(Paragraph(
        "Contributions are welcome! Please follow the standard GitHub workflow:",
        styles['BodyText']
    ))
    
    contrib = [
        "1. Fork the repository",
        "2. Create a feature branch (git checkout -b feature/your-feature)",
        "3. Commit changes with descriptive messages",
        "4. Push to your fork and create a Pull Request"
    ]
    
    for item in contrib:
        story.append(Paragraph(item, styles['BodyText']))
    
    return story

def create_conclusion_section(styles):
    """Create the conclusion section"""
    story = []
    
    story.append(Paragraph("8. Conclusion", styles['SectionHeader']))
    
    story.append(Paragraph(
        "BIOCANVAS v2.0 represents a modern, production-ready molecular docking platform "
        "that combines the power of AutoDock Vina with an intuitive web-based interface. "
        "The architecture follows best practices for both backend (FastAPI, async processing) "
        "and frontend (React, TypeScript, component-based) development.",
        styles['BodyText']
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "Key architectural highlights:",
        styles['BodyText']
    ))
    
    highlights = [
        "Separation of concerns: Backend handles computation, frontend handles presentation",
        "Scalable job management with SQLite persistence",
        "Rich 3D visualization with interactive features",
        "Type-safe API contracts between frontend and backend",
        "Modern state management with Zustand and React Query"
    ]
    
    for h in highlights:
        story.append(Paragraph(f"• {h}", styles['BodyText']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact/Support
    story.append(Paragraph(
        "For questions, issues, or contributions, please refer to the project repository "
        "or contact the development team.",
        styles['BodyText']
    ))
    
    return story

def create_appendix_section(styles):
    """Create the appendix section"""
    story = []
    
    story.append(Paragraph("Appendix A: File Directory Structure", styles['SectionHeader']))
    
    tree = [
        "BIOCANVAS/",
        "├── backend/",
        "│   ├── __init__.py",
        "│   ├── main.py                 # FastAPI app entry",
        "│   ├── docking_engine.py       # Docking logic",
        "│   └── job_store.py            # SQLite persistence",
        "├── frontend/",
        "│   ├── src/",
        "│   │   ├── App.tsx             # Root component",
        "│   │   ├── components/",
        "│   │   │   ├── features/       # Main feature components",
        "│   │   │   │   ├── DockingPipeline.tsx",
        "│   │   │   │   ├── VisualizePage.tsx",
        "│   │   │   │   └── docking-steps/",
        "│   │   │   ├── science/        # 3D viewers",
        "│   │   │   ├── layout/         # Navigation",
        "│   │   │   └── ui/             # Reusable UI",
        "│   │   ├── hooks/              # Custom React hooks",
        "│   │   ├── stores/             # Zustand stores",
        "│   │   ├── lib/                # Utilities",
        "│   │   └── types/              # TypeScript types",
        "│   └── package.json",
        "├── data/",
        "│   ├── proteins.json",
        "│   └── ligands.json",
        "├── tests/",
        "│   ├── e2e_docking_test.py",
        "│   ├── test_docking_engine.py",
        "│   └── test_api_endpoints.py",
        "├── docs/",
        "│   ├── API_REFERENCE.md",
        "│   ├── ARCHITECTURE.md",
        "│   └── DEPLOYMENT.md",
        "├── requirements.txt",
        "├── run.py",
        "└── README.md"
    ]
    
    for line in tree:
        story.append(Paragraph(
            f"<font face='Courier' size='8'>{line}</font>",
            styles['BodyText']
        ))
    
    return story

def build_document():
    """Build the complete PDF document"""
    doc = create_document()
    styles = get_styles()
    
    # Build all sections
    story = []
    
    # Title Page
    story.extend(create_title_page(styles))
    story.append(PageBreak())
    
    # Overview
    story.extend(create_overview_section(styles))
    story.append(PageBreak())
    
    # Backend
    story.extend(create_backend_section(styles))
    story.append(PageBreak())
    
    # Frontend
    story.extend(create_frontend_section(styles))
    story.append(PageBreak())
    
    # Data Flow
    story.extend(create_data_flow_section(styles))
    story.append(PageBreak())
    
    # Security
    story.extend(create_security_section(styles))
    story.append(PageBreak())
    
    # Deployment
    story.extend(create_deployment_section(styles))
    story.append(PageBreak())
    
    # Future
    story.extend(create_future_section(styles))
    story.append(PageBreak())
    
    # Conclusion
    story.extend(create_conclusion_section(styles))
    story.append(PageBreak())
    
    # Appendix
    story.extend(create_appendix_section(styles))
    
    # Build PDF
    doc.build(story)
    print(f"✓ PDF generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_document()
