#!/usr/bin/env python3
"""
BioCanvas Pro — Phase 3 Part A: Bento Box Results UI Report (PDF)
Professional dark-themed report matching Phase 1/2/2.5 style.
"""

import os
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "scripts", "fonts")
OUTPUT   = os.path.join(BASE_DIR, "BioCanvas_Pro_Phase3_PartA_Report.pdf")

# ── Colours ──────────────────────────────────────────────────────────────────
BG             = (12, 14, 22)
CARD_BG        = (20, 24, 36)
PRIMARY        = (99, 102, 241)
ACCENT         = (16, 185, 129)
WHITE          = (235, 235, 240)
MUTED          = (140, 155, 175)
RED            = (239, 68, 68)
AMBER          = (245, 158, 11)
CYAN           = (34, 211, 238)
DIVIDER        = (38, 42, 58)
TBL_HDR        = (32, 38, 56)
PASS_GREEN     = (34, 197, 94)
CODE_BG        = (18, 20, 30)
ORANGE         = (251, 146, 60)
VIOLET         = (167, 139, 250)
SKY            = (56, 189, 248)
EMERALD        = (52, 211, 153)


class ReportPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(True, 18)
        self.add_font("DJ",  "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
        self.add_font("DJ",  "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
        self.add_font("DJ",  "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))
        self.add_font("DJM", "", os.path.join(FONT_DIR, "DejaVuSansMono.ttf"))

    def header(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")

    def footer(self):
        self.set_y(-12)
        self.set_font("DJ", "I", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 8,
                  f"BioCanvas Pro  \u2022  Phase 3 Part A Report  \u2022  Page {self.page_no()}/{{nb}}",
                  align="C")

    # ── helpers ───────────────────────────────────────────────────────────
    def _tc(self, c): self.set_text_color(*c)
    def _fc(self, c): self.set_fill_color(*c)

    def h1(self, text, num=None):
        self.ln(5)
        self.set_font("DJ", "B", 17)
        self._tc(PRIMARY)
        pre = f"{num}.  " if num is not None else ""
        self.cell(0, 11, pre + text, new_x="LMARGIN", new_y="NEXT")
        self._fc(PRIMARY)
        self.rect(self.l_margin, self.get_y(), 180, 0.5, "F")
        self.ln(4)

    def h2(self, text):
        self.set_font("DJ", "B", 12)
        self._tc(ACCENT)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def h3(self, text):
        self.set_font("DJ", "B", 10)
        self._tc(WHITE)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("DJ", "", 9)
        self._tc(WHITE)
        self.multi_cell(0, 5.2, text)
        self.ln(1)

    def muted_body(self, text):
        self.set_font("DJ", "I", 8)
        self._tc(MUTED)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def bullet(self, text, indent=8):
        self.set_font("DJ", "", 9)
        self._tc(WHITE)
        x = self.l_margin + indent
        self.set_x(x)
        w = self.w - self.l_margin - self.r_margin - indent
        self.multi_cell(w, 5.2, "\u2022  " + text)

    def bold_bullet(self, label, desc, indent=8):
        x = self.l_margin + indent
        self.set_x(x)
        self.set_font("DJ", "B", 9)
        self._tc(CYAN)
        w_label = self.get_string_width(label + "  ") + 2
        self.cell(w_label, 5.2, label + "  ")
        self.set_font("DJ", "", 9)
        self._tc(WHITE)
        remaining = self.w - self.l_margin - self.r_margin - indent - w_label
        self.multi_cell(remaining, 5.2, desc)

    def colored_bullet(self, label, desc, label_color, indent=8):
        x = self.l_margin + indent
        self.set_x(x)
        self.set_font("DJ", "B", 9)
        self._tc(label_color)
        w_label = self.get_string_width(label + "  ") + 2
        self.cell(w_label, 5.2, label + "  ")
        self.set_font("DJ", "", 9)
        self._tc(WHITE)
        remaining = self.w - self.l_margin - self.r_margin - indent - w_label
        self.multi_cell(remaining, 5.2, desc)

    def code(self, text):
        self.set_font("DJM", "", 7.5)
        self._tc(MUTED)
        self._fc(CODE_BG)
        lines = text.strip().split("\n")
        w = 180
        h = len(lines) * 4.5 + 4
        if self.get_y() + h > 275:
            self.add_page()
        self.rect(self.l_margin, self.get_y(), w, h, "F")
        self.ln(2)
        for ln in lines:
            self.cell(4)
            self.cell(0, 4.5, ln, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def table(self, headers, rows, widths=None):
        if widths is None:
            widths = [180 / len(headers)] * len(headers)
        self.set_font("DJ", "B", 8)
        self._fc(TBL_HDR)
        self._tc(PRIMARY)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, f" {h}", fill=True)
        self.ln()
        fill = False
        for row in rows:
            if self.get_y() + 6 > 280:
                self.add_page()
            self.set_font("DJ", "", 8)
            self._fc((26, 30, 44) if fill else BG)
            self._tc(WHITE)
            for i, v in enumerate(row):
                self.cell(widths[i], 6, f" {v}", fill=True)
            self.ln()
            fill = not fill
        self.ln(2)

    def badge(self, text, color):
        self.set_font("DJ", "B", 8)
        self._fc(color)
        self._tc(BG)
        w = self.get_string_width(text) + 8
        self.cell(w, 6, f" {text} ", fill=True)
        self.cell(3)

    def safe_page_break(self, needed=40):
        if self.get_y() + needed > 278:
            self.add_page()


# ══════════════════════════════════════════════════════════════════════════════
#  BUILD REPORT
# ══════════════════════════════════════════════════════════════════════════════

def build():
    pdf = ReportPDF()
    pdf.alias_nb_pages()

    # ══════════════════════════════════════════════════════════════════════
    #  COVER PAGE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("DJ", "B", 36)
    pdf._tc(PRIMARY)
    pdf.cell(0, 16, "BioCanvas Pro", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "B", 14)
    pdf._tc(ACCENT)
    pdf.cell(0, 10, "Phase 3 Part A: The Bento Box Results UI", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DJ", "", 11)
    pdf._tc(AMBER)
    pdf.cell(0, 8, "Molecular Dashboard with Metrics, Lipinski Pulse & Pose Table",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf._fc(DIVIDER)
    pdf.rect(55, pdf.get_y(), 100, 0.4, "F")
    pdf.ln(8)

    for line in [
        "Date: February 23, 2026",
        "Engineer: AI-Assisted Development (GitHub Copilot + Claude Opus 4)",
        "Scope: Transform Step4_Results placeholder into Bento dashboard",
        "Risk Level: Zero \u2014 Steps 1-3 untouched, backward-compatible",
        "Status: tsc --noEmit PASSES CLEAN (0 errors)",
    ]:
        pdf.set_font("DJ", "", 10)
        pdf._tc(MUTED)
        pdf.cell(0, 7, line, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(16)
    pdf.set_font("DJ", "I", 9)
    pdf._tc(MUTED)
    pdf.multi_cell(0, 5, (
        "This document covers Phase 3 Part A of BioCanvas Pro \u2014 the transformation "
        "of the Step4_Results placeholder (38 lines) into a complete molecular docking "
        "dashboard (528 lines) featuring a 12-column Bento grid layout, Lead Compound "
        "metrics card, Lipinski Rule-of-Five pulse badges, and an interactive sortable "
        "Pose Table with Zustand state integration."
    ), align="C")

    # ══════════════════════════════════════════════════════════════════════
    #  TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Table of Contents")
    toc = [
        ("1",  "Executive Summary", "3"),
        ("2",  "Scope & Constraints", "3"),
        ("3",  "Bento Grid Architecture", "4"),
        ("4",  "Props Interface & Data Flow", "5"),
        ("5",  "Sub-Component: ResultsHeader", "6"),
        ("6",  "Sub-Component: LeadCard", "7"),
        ("7",  "Sub-Component: LipinskiPulse", "8"),
        ("8",  "Sub-Component: PoseTable", "9"),
        ("9",  "Sub-Component: AIAnalysisTeaser", "10"),
        ("10", "Zustand Integration", "11"),
        ("11", "Color System & Visual Design", "12"),
        ("12", "Orchestrator Changes", "13"),
        ("13", "TypeScript Verification", "13"),
        ("14", "File Change Summary", "14"),
        ("15", "Phase 3 Part B Roadmap", "15"),
    ]
    for num, title, pg in toc:
        pdf.set_font("DJ", "", 10)
        pdf._tc(WHITE)
        pdf.cell(12, 7, num + ".")
        pdf.cell(135, 7, title)
        pdf._tc(MUTED)
        pdf.cell(33, 7, pg, align="R", new_x="LMARGIN", new_y="NEXT")

    # ══════════════════════════════════════════════════════════════════════
    #  1. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Executive Summary", 1)
    pdf.body(
        "Phase 3 Part A delivers the first visual results dashboard for BioCanvas Pro. "
        "The Step4_Results component has been transformed from a 38-line placeholder "
        "into a 528-line industry-standard molecular dashboard featuring:\n\n"
        "\u2022  A 12-column Bento Box grid with responsive breakpoints\n"
        "\u2022  A Lead Card showing binding affinity and ligand efficiency with "
        "color-coded severity scales\n"
        "\u2022  A Lipinski Rule-of-Five Pulse with 4 pass/fail badges\n"
        "\u2022  A sortable, interactive Pose Table that syncs with Zustand global state\n"
        "\u2022  A 3D viewer placeholder (col-span-8, 600px) ready for Part B\n\n"
        "Only 2 files were modified. Steps 1, 2, and 3 are completely untouched. "
        "TypeScript strict mode passes with zero errors."
    )

    pdf.h2("Phase 3 Part A Key Metrics")
    pdf.table(
        ["Metric", "Detail"],
        [
            ["Step4_Results.tsx", "38 lines -> 528 lines (+490 lines)"],
            ["DockingPipeline.tsx", "138 lines -> 145 lines (+7 lines)"],
            ["Sub-components built", "5 (ResultsHeader, LeadCard, LipinskiPulse, PoseTable, AIAnalysisTeaser)"],
            ["Props interface", "Step4Props (4 props from orchestrator)"],
            ["Zustand hooks used", "2 (activePoseIndex read, setActivePose write)"],
            ["Phase 2 types consumed", "SelectedJobData, DockingPose, LipinskiProfile"],
            ["Lucide icons added", "13 new icon imports"],
            ["New npm dependencies", "0"],
            ["tsc --noEmit result", "0 errors, 0 warnings"],
            ["Steps 1-3 files changed", "0 (untouched)"],
        ],
        widths=[55, 125],
    )

    # ══════════════════════════════════════════════════════════════════════
    #  2. SCOPE & CONSTRAINTS
    # ══════════════════════════════════════════════════════════════════════
    pdf.h1("Scope & Constraints", 2)
    pdf.body(
        "Phase 3 Part A operates under strict isolation constraints inherited "
        "from the Phase 2.5 refactor:"
    )
    pdf.bold_bullet("Target file:",
                    "ONLY Step4_Results.tsx was rebuilt. Plus 7 lines added to the "
                    "orchestrator to pass props.")
    pdf.bold_bullet("Steps 1-3:",
                    "Zero modifications. Step1_ProteinTarget, Step2_LigandSelection, "
                    "step3_DockingRun are completely untouched.")
    pdf.bold_bullet("Data consumption:",
                    "All data comes from the Phase 2 typed data layer \u2014 SelectedJobData "
                    "(from useDockingJob hook), DockingPose[], and LipinskiProfile.")
    pdf.bold_bullet("State management:",
                    "Zustand's activePoseIndex and setActivePose (added in Phase 2) are now "
                    "consumed for the first time by the Pose Table.")
    pdf.bold_bullet("No new dependencies:",
                    "Only existing libraries (React, Zustand, Lucide, Tailwind CSS).")

    # ══════════════════════════════════════════════════════════════════════
    #  3. BENTO GRID ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Bento Grid Architecture", 3)
    pdf.body(
        "The dashboard uses a responsive 12-column CSS Grid (Tailwind's grid-cols-12) "
        "with a 16px gap (gap-4). The layout adapts between desktop (lg:) and mobile "
        "breakpoints."
    )

    pdf.h2("Grid Layout Map")
    pdf.code(
        "+------------------------------------------+\n"
        "| ResultsHeader (col-span-12)              |\n"
        "+------------------------------------------+\n"
        "| 3D Viewer Placeholder  | Lead Card       |\n"
        "| (col-span-8, 600px)    | (col-span-4)    |\n"
        "|                        +-----------------+\n"
        "|                        | Lipinski Pulse  |\n"
        "|                        | (col-span-4)    |\n"
        "|                        +-----------------+\n"
        "|                        | AI Teaser       |\n"
        "|                        | (col-span-4)    |\n"
        "+------------------------+-----------------+\n"
        "| PoseTable (col-span-12)                  |\n"
        "+------------------------------------------+"
    )

    pdf.h2("Responsive Behavior")
    pdf.table(
        ["Breakpoint", "Hero Viewer", "Data Column", "Pose Table"],
        [
            ["< lg (mobile)", "col-span-12", "col-span-12 (stacked)", "col-span-12"],
            [">= lg (desktop)", "col-span-8 (left)", "col-span-4 (right)", "col-span-12"],
        ],
        widths=[35, 50, 50, 45],
    )

    pdf.h2("3D Viewer Placeholder")
    pdf.body(
        "The hero area is a 600px tall container with a radial gradient background, "
        "an Eye icon, and placeholder text. It is architecturally ready for Phase 3 "
        "Part B where it will host the interactive 3Dmol.js docked-complex viewer."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  4. PROPS INTERFACE & DATA FLOW
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Props Interface & Data Flow", 4)

    pdf.h2("Step4Props Interface")
    pdf.code(
        "export interface Step4Props {\n"
        "  jobData: SelectedJobData | null\n"
        "  selectedProtein: Protein | null\n"
        "  customPdbName: string | null\n"
        "  selectedLigand: Ligand | null\n"
        "}"
    )

    pdf.h2("Data Extraction Inside Step4")
    pdf.code(
        "// From jobData (SelectedJobData)\n"
        "const poses     = jobData?.dockingPoses ?? []     // DockingPose[]\n"
        "const lipinski  = jobData?.lipinski ?? null        // LipinskiProfile | null\n"
        "const activePose = poses[activePoseIndex] ?? null  // active DockingPose\n"
        "const isSimulated = jobData?.result?.simulated     // boolean\n"
        "\n"
        "// From Zustand store\n"
        "const activePoseIndex = useDockingStore(s => s.activePoseIndex)\n"
        "const setActivePose   = useDockingStore(s => s.setActivePose)"
    )

    pdf.h2("Data Flow Diagram")
    pdf.code(
        "DockingPipeline (orchestrator)\n"
        "  |-- jobQuery.data (SelectedJobData) --->\n"
        "  |-- selectedProtein ------------------>\n"
        "  |-- customPdbName --------------------> Step4_Results\n"
        "  |-- selectedLigand ------------------->   |\n"
        "                                            |-- poses[] -------> PoseTable\n"
        "                                            |-- lipinski ------> LipinskiPulse\n"
        "                                            |-- activePose ----> LeadCard\n"
        "                                            |-- labels --------> ResultsHeader\n"
        "                                            |\n"
        "  Zustand Store (useDockingStore) <-------> PoseTable (onClick)\n"
        "                                  -------> LeadCard (read activePoseIndex)"
    )

    pdf.ln(2)
    pdf.muted_body(
        "The parent orchestrator passes jobData as a single prop. Step4 internally "
        "destructures it into poses, lipinski, and display labels, then distributes "
        "to sub-components. The Zustand store is accessed directly by Step4 (not "
        "passed as props) following Zustand's recommended selector pattern."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  5. ResultsHeader
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Sub-Component: ResultsHeader", 5)
    pdf.body(
        "A full-width header bar that summarizes the docking run. It provides "
        "immediate context: what was docked, how many poses were found, and "
        "whether the results are from a real or simulated engine."
    )

    pdf.h2("Props")
    pdf.table(
        ["Prop", "Type", "Purpose"],
        [
            ["proteinLabel", "string", "Protein name or custom PDB filename"],
            ["ligandLabel", "string", "Ligand name or 'Custom SMILES'"],
            ["poseCount", "number", "Number of docking poses found"],
            ["isSimulated", "boolean", "Whether engine used simulation mode"],
        ],
        widths=[40, 35, 105],
    )

    pdf.h2("Visual Elements")
    pdf.bullet("Title: \"Docking Results\" in semibold white")
    pdf.bullet("Subtitle: \"[Ligand] docked into [Protein]\" with FlaskConical icon")
    pdf.bullet("Pose count badge with Layers icon (e.g., \"9 poses\")")
    pdf.bullet("Simulated badge (amber) with Zap icon \u2014 only shown when isSimulated=true")

    # ══════════════════════════════════════════════════════════════════════
    #  6. LeadCard
    # ══════════════════════════════════════════════════════════════════════
    pdf.h1("Sub-Component: LeadCard", 6)
    pdf.body(
        "The hero metrics card displaying the binding affinity and ligand efficiency "
        "for the currently selected pose. Updates instantly when the user clicks a "
        "different row in the Pose Table (via Zustand sync)."
    )

    pdf.h2("Props")
    pdf.table(
        ["Prop", "Type", "Purpose"],
        [
            ["pose", "DockingPose | null", "The active pose data"],
            ["poseIndex", "number", "Index for display (\"Pose #N\")"],
        ],
        widths=[40, 50, 90],
    )

    pdf.h2("Binding Affinity Color Scale")
    pdf.table(
        ["Affinity Range", "Color", "Interpretation"],
        [
            ["<= -8.0 kcal/mol", "Emerald (green)", "Strong binder"],
            ["-8.0 to -6.0", "Sky (blue)", "Moderate binder"],
            ["-6.0 to -4.0", "Amber (yellow)", "Weak binder"],
            ["> -4.0", "Red", "Very weak / non-binder"],
        ],
        widths=[45, 45, 90],
    )

    pdf.h2("Visual Layout")
    pdf.bullet("Header bar: Activity icon + \"Lead Compound\" label + \"Pose #N\" badge")
    pdf.bullet("Hero number: Affinity in 4xl extrabold font, color-coded, with kcal/mol unit")
    pdf.bullet("Bottom row: 2-column grid for Ligand Efficiency (LE) and RMSD (UB)")
    pdf.bullet("Graceful null state: \"No pose data available\" centered text when poses=[]")

    # ══════════════════════════════════════════════════════════════════════
    #  7. LipinskiPulse
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Sub-Component: LipinskiPulse", 7)
    pdf.body(
        "Displays the Lipinski Rule-of-Five drug-likeness profile as four "
        "pass/fail pill badges. This is the first component in BioCanvas to "
        "consume the Phase 1 LipinskiProfile type."
    )

    pdf.h2("Rule Definitions")
    pdf.table(
        ["Property", "Threshold", "Operator", "Description"],
        [
            ["MW (mw)", "<= 500 Da", "lte", "Molecular weight"],
            ["LogP (logp)", "<= 5", "lte", "Partition coefficient"],
            ["HBD (hbd)", "<= 5", "lte", "Hydrogen bond donors"],
            ["HBA (hba)", "<= 10", "lte", "Hydrogen bond acceptors"],
        ],
        widths=[35, 35, 25, 85],
    )

    pdf.h2("Badge Color Logic")
    pdf.code(
        "const passes = value <= threshold\n"
        "\n"
        "Pass:  border-emerald-500/20  bg-emerald-500/5  text-emerald-400\n"
        "Fail:  border-red-500/20      bg-red-500/5      text-red-400"
    )

    pdf.h2("Visual Layout")
    pdf.bullet("Header bar: ShieldCheck (green) or ShieldAlert (amber) icon based on pass_rule_of_five")
    pdf.bullet("Overall badge: \"PASS\" (emerald) or \"VIOLATION\" (amber)")
    pdf.bullet("2x2 grid of property pills, each showing: label, value, and threshold comparison")
    pdf.bullet("Graceful null state: \"Lipinski data unavailable\" when lipinski=null")

    # ══════════════════════════════════════════════════════════════════════
    #  8. PoseTable
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Sub-Component: PoseTable", 8)
    pdf.body(
        "A full-width sortable table displaying all docking poses. This is the "
        "primary interactive element in the results dashboard \u2014 clicking a row "
        "updates the global Zustand state, which in turn updates the Lead Card "
        "and will drive the 3D viewer in Part B."
    )

    pdf.h2("Props")
    pdf.table(
        ["Prop", "Type", "Purpose"],
        [
            ["poses", "DockingPose[]", "Full array of docking poses"],
            ["activePoseIndex", "number", "Currently selected pose index"],
            ["onSelectPose", "(index: number) => void", "Zustand setActivePose callback"],
        ],
        widths=[40, 55, 85],
    )

    pdf.h2("Table Columns")
    pdf.table(
        ["Column", "Source", "Sortable", "Display"],
        [
            ["Rank", "pose.pose_rank", "Yes", "Numbered circle badge"],
            ["Affinity", "pose.affinity", "Yes", "Color-coded kcal/mol value"],
            ["RMSD", "pose.rmsd_ub", "Yes", "Angstrom value (2 decimals)"],
            ["LE", "pose.ligand_efficiency", "No", "kcal/mol/HA (2 decimals)"],
            ["Interactions", "sum of all interaction types", "No", "Atom icon + count"],
        ],
        widths=[35, 45, 25, 75],
    )

    pdf.h2("Sort Implementation")
    pdf.code(
        "type SortKey = 'pose_rank' | 'affinity' | 'rmsd_ub'\n"
        "type SortDir = 'asc' | 'desc'\n"
        "\n"
        "// Click toggles asc/desc on same column, or switches column\n"
        "const handleSort = (key: SortKey) => {\n"
        "  if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')\n"
        "  else { setSortKey(key); setSortDir('asc') }\n"
        "}\n"
        "\n"
        "// Sorted with original index preserved\n"
        "const sortedPoses = poses.map((p, i) => ({ pose: p, originalIndex: i }))\n"
        "  .sort((a, b) => sortDir === 'asc' ? a[key] - b[key] : b[key] - a[key])"
    )

    pdf.h2("Active Row Highlighting")
    pdf.body(
        "The currently selected row (matching activePoseIndex) is highlighted with "
        "bg-primary/10 and a primary-colored rank badge with a ring. Clicking any "
        "row calls onSelectPose(originalIndex), which maps through Zustand to update "
        "the global activePoseIndex \u2014 instantly reflecting in the Lead Card."
    )

    pdf.h2("Interaction Count")
    pdf.code(
        "const totalInteractions =\n"
        "  (pose.interactions?.hydrogen_bonds?.length ?? 0) +\n"
        "  (pose.interactions?.hydrophobic?.length ?? 0) +\n"
        "  (pose.interactions?.pi_stacking?.length ?? 0) +\n"
        "  (pose.interactions?.salt_bridges?.length ?? 0)"
    )

    # ══════════════════════════════════════════════════════════════════════
    #  9. AIAnalysisTeaser
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Sub-Component: AIAnalysisTeaser", 9)
    pdf.body(
        "Compact \"Coming Soon\" card retained from the original placeholder, "
        "redesigned to fit within the Bento column. Serves as a visual anchor "
        "for Phase 3 Part C (GPT integration)."
    )
    pdf.bullet("Sparkles icon in secondary color")
    pdf.bullet("\"AI Binding Analysis\" title")
    pdf.bullet("Brief description of planned GPT-powered features")
    pdf.bullet("Animated ping dot with \"Coming Soon\" label")
    pdf.bullet("No props \u2014 self-contained placeholder component")

    # ══════════════════════════════════════════════════════════════════════
    #  10. ZUSTAND INTEGRATION
    # ══════════════════════════════════════════════════════════════════════
    pdf.h1("Zustand Integration", 10)
    pdf.body(
        "Phase 3 Part A is the first component in BioCanvas to consume the Zustand "
        "state fields added in Phase 2. The integration follows Zustand's recommended "
        "selector pattern for minimal re-renders."
    )

    pdf.h2("Selectors Used")
    pdf.code(
        "// In Step4_Results (parent)\n"
        "const activePoseIndex = useDockingStore(s => s.activePoseIndex)\n"
        "const setActivePose   = useDockingStore(s => s.setActivePose)\n"
        "\n"
        "// Passed to sub-components via props:\n"
        "//   activePoseIndex -> LeadCard (reads active pose)\n"
        "//   activePoseIndex -> PoseTable (highlights active row)\n"
        "//   setActivePose   -> PoseTable (onClick handler)"
    )

    pdf.h2("State Flow: Pose Selection")
    pdf.code(
        "User clicks PoseTable row\n"
        "  -> onSelectPose(originalIndex)\n"
        "  -> useDockingStore.setActivePose(index)\n"
        "  -> Zustand store updates activePoseIndex\n"
        "  -> Step4_Results re-renders (selector changed)\n"
        "  -> activePose = poses[newIndex] computed\n"
        "  -> LeadCard receives new pose -> displays new affinity/LE\n"
        "  -> PoseTable receives new activePoseIndex -> highlights new row\n"
        "  -> [Phase 3B] 3D viewer will rotate to new pose conformation"
    )

    pdf.ln(2)
    pdf.muted_body(
        "Note: useDockingStore.setActivePose was defined in Phase 2 (Zustand store "
        "upgrade) but never consumed until now. Phase 3A is the first consumer."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  11. COLOR SYSTEM
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Color System & Visual Design", 11)
    pdf.body(
        "The Bento dashboard uses a scientific color coding system designed for "
        "rapid visual triage of docking results:"
    )

    pdf.h2("Affinity Severity Scale (used in LeadCard + PoseTable)")
    pdf.table(
        ["Range", "Tailwind Class", "Semantic Meaning"],
        [
            ["<= -8.0", "text-emerald-400", "Strong binder (drug-like)"],
            ["-8.0 to -6.0", "text-sky-400", "Moderate binder"],
            ["-6.0 to -4.0", "text-amber-400", "Weak binder"],
            ["> -4.0", "text-red-400", "Very weak / noise"],
        ],
        widths=[35, 55, 90],
    )

    pdf.h2("Lipinski Pass/Fail (used in LipinskiPulse)")
    pdf.table(
        ["State", "Border", "Background", "Text"],
        [
            ["Pass", "emerald-500/20", "emerald-500/5", "emerald-400"],
            ["Fail", "red-500/20", "red-500/5", "red-400"],
        ],
        widths=[25, 50, 50, 55],
    )

    pdf.h2("Table Row States (used in PoseTable)")
    pdf.table(
        ["State", "Class", "Effect"],
        [
            ["Default", "hover:bg-surface-highlight/50", "Subtle hover highlight"],
            ["Active", "bg-primary/10", "Primary tint + ring on rank badge"],
            ["Active hover", "hover:bg-primary/15", "Slightly deeper primary tint"],
        ],
        widths=[35, 65, 80],
    )

    pdf.h2("Component Card Style")
    pdf.body(
        "All cards follow a consistent pattern: rounded-2xl border with surface-border "
        "color, optional gradient background (from-surface/60 to-[accent]/5), and a "
        "header bar separated by border-b with icon + uppercase tracking-wider label."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  12. ORCHESTRATOR CHANGES
    # ══════════════════════════════════════════════════════════════════════
    pdf.h1("Orchestrator Changes", 12)
    pdf.body(
        "The DockingPipeline.tsx orchestrator was updated with a minimal change "
        "(+7 lines) to pass the required props to Step4_Results:"
    )

    pdf.h2("Before")
    pdf.code(
        "{activeStep === 4 && <Step4_Results />}"
    )

    pdf.h2("After")
    pdf.code(
        "{activeStep === 4 && (\n"
        "  <Step4_Results\n"
        "    jobData={jobQuery.data ?? null}\n"
        "    selectedProtein={selectedProtein}\n"
        "    customPdbName={customPdbName}\n"
        "    selectedLigand={selectedLigand}\n"
        "  />\n"
        ")}"
    )

    pdf.ln(2)
    pdf.body(
        "All four props already existed in the orchestrator's scope. The jobQuery.data "
        "is the SelectedJobData from the useDockingJob hook (called in the parent for "
        "step derivation since Phase 2.5). No new data fetching was added."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  13. TYPESCRIPT VERIFICATION
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("TypeScript Verification", 13)
    pdf.body("Final compilation check after Phase 3 Part A:")
    pdf.code(
        "$ cd frontend && npx tsc --noEmit\n"
        "\n"
        "(no output - 0 errors, 0 warnings)"
    )
    pdf.ln(2)
    pdf.badge("PASS", PASS_GREEN)
    pdf.badge("0 ERRORS", PASS_GREEN)
    pdf.badge("528 LINES", PRIMARY)
    pdf.badge("ZUSTAND SYNCED", ACCENT)
    pdf.ln(6)
    pdf.muted_body(
        "All source files compile cleanly in strict mode. The Step4Props interface "
        "correctly maps to the SelectedJobData shape from Phase 2. All DockingPose "
        "and LipinskiProfile field accesses are type-safe."
    )

    # ══════════════════════════════════════════════════════════════════════
    #  14. FILE CHANGE SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    pdf.h1("File Change Summary", 14)

    pdf.h2("Modified Files")
    pdf.table(
        ["File", "Before", "After", "Change"],
        [
            ["docking-steps/Step4_Results.tsx", "38", "528", "+490 lines (rebuilt)"],
            ["DockingPipeline.tsx", "138", "145", "+7 lines (pass props)"],
        ],
        widths=[55, 20, 20, 85],
    )

    pdf.h2("Untouched Files")
    pdf.table(
        ["File", "Lines", "Status"],
        [
            ["docking-steps/Step1_ProteinTarget.tsx", "361", "Untouched"],
            ["docking-steps/Step2_LigandSelection.tsx", "397", "Untouched"],
            ["docking-steps/Step3_DockingRun.tsx", "393", "Untouched"],
            ["docking-steps/index.ts", "4", "Untouched"],
            ["pipeline/StepNav.tsx", "169", "Untouched"],
            ["pipeline/ElapsedTimer.tsx", "22", "Untouched"],
            ["pipeline/helpers.ts", "27", "Untouched"],
            ["stores/useDockingStore.ts", "98", "Untouched (consumed, not modified)"],
            ["types/api.ts", "120", "Untouched (consumed, not modified)"],
        ],
        widths=[72, 20, 88],
    )

    pdf.h2("Sub-Components Inside Step4_Results.tsx")
    pdf.table(
        ["Component", "Approx Lines", "Purpose"],
        [
            ["Step4_Results (main)", "~60", "Bento grid orchestrator + data extraction"],
            ["ResultsHeader", "~45", "Run summary with protein/ligand labels"],
            ["LeadCard", "~85", "Binding affinity + LE hero card"],
            ["LipinskiPulse", "~85", "RO5 4-badge pass/fail grid"],
            ["AIAnalysisTeaser", "~30", "Coming Soon placeholder"],
            ["PoseTable", "~195", "Sortable interactive pose table"],
        ],
        widths=[55, 30, 95],
    )

    # ══════════════════════════════════════════════════════════════════════
    #  15. PHASE 3 PART B ROADMAP
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Phase 3 Part B Roadmap", 15)
    pdf.body(
        "Part A establishes the data dashboard. Part B will add the interactive "
        "3D molecular visualization to complete the results experience."
    )

    pdf.h2("Part B: 3D Docked Complex Viewer")
    pdf.bold_bullet("Replace placeholder:",
                    "The col-span-8 / 600px placeholder will host a 3Dmol.js viewer "
                    "rendering the protein + docked ligand overlay.")
    pdf.bold_bullet("Pose switching:",
                    "When activePoseIndex changes (from PoseTable click), the viewer "
                    "will animate to the new ligand conformation.")
    pdf.bold_bullet("Interaction overlays:",
                    "Hydrogen bonds, hydrophobic contacts, pi-stacking, and salt bridges "
                    "from the DockingPose.interactions will be rendered as dashed lines "
                    "and labels in the 3D scene.")
    pdf.bold_bullet("Style controls:",
                    "Surface/ribbon/cartoon toggle for protein, ball-and-stick for ligand, "
                    "with optional residue labeling.")

    pdf.h2("Part C: AI Analysis (Future)")
    pdf.bold_bullet("GPT integration:",
                    "The AIAnalysisTeaser placeholder will be replaced with a real "
                    "AI-powered binding interpretation panel.")
    pdf.bold_bullet("Interaction summary:",
                    "Natural-language description of key binding contacts.")
    pdf.bold_bullet("Drug-likeness assessment:",
                    "AI interpretation of Lipinski results with ADMET predictions.")

    pdf.h2("Architecture Readiness")
    pdf.body(
        "Phase 3 Part A was specifically designed to make Part B straightforward:"
    )
    pdf.bullet("The 600px placeholder div is exactly where the 3Dmol viewer will mount")
    pdf.bullet("viewerData (PDB string) is available in the orchestrator and can be passed as a new prop")
    pdf.bullet("Zustand activePoseIndex is already synced \u2014 the viewer just needs to subscribe")
    pdf.bullet("DockingPose.interactions is fully typed and available via poses[activePoseIndex]")
    pdf.bullet("output_pdbqt with the docked ligand coordinates is in SelectedJobData")

    # ══════════════════════════════════════════════════════════════════════
    #  CLOSING
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("DJ", "B", 24)
    pdf._tc(PRIMARY)
    pdf.cell(0, 14, "Phase 3 Part A Complete", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf._fc(DIVIDER)
    pdf.rect(55, pdf.get_y(), 100, 0.4, "F")
    pdf.ln(8)

    pdf.set_font("DJ", "", 11)
    pdf._tc(WHITE)
    pdf.multi_cell(0, 6, (
        "The Step4_Results placeholder has been transformed into a complete molecular "
        "docking dashboard. The Bento layout, Lead Card, Lipinski Pulse, and interactive "
        "Pose Table are fully operational. Zustand integration is live. The 3D viewer "
        "placeholder is architecturally ready for Phase 3 Part B."
    ), align="C")

    pdf.ln(10)
    summary_items = [
        ("Step4_Results.tsx:", "38 -> 528 lines (5 sub-components)"),
        ("DockingPipeline.tsx:", "138 -> 145 lines (+7 props pass-through)"),
        ("Sub-components:", "ResultsHeader, LeadCard, LipinskiPulse, PoseTable, AITeaser"),
        ("Phase 2 types consumed:", "SelectedJobData, DockingPose, LipinskiProfile"),
        ("Zustand fields consumed:", "activePoseIndex (read), setActivePose (write)"),
        ("TypeScript errors:", "0"),
        ("Steps 1-3 modified:", "0"),
        ("Next:", "Phase 3 Part B \u2014 3D Docked Complex Viewer"),
    ]
    for label, value in summary_items:
        pdf.set_font("DJ", "B", 10)
        pdf._tc(ACCENT)
        w_label = pdf.get_string_width(label + "  ") + 2
        x_start = (210 - 150) / 2
        pdf.set_x(x_start)
        pdf.cell(w_label, 7, label + "  ")
        pdf.set_font("DJ", "", 10)
        pdf._tc(WHITE)
        pdf.cell(150 - w_label, 7, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_font("DJ", "I", 9)
    pdf._tc(MUTED)
    pdf.cell(0, 7, "BioCanvas Pro  \u2022  Phase 3 Part A: Bento Box Results UI  \u2022  February 23, 2026",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Generated by GitHub Copilot + Claude Opus 4",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Write ────────────────────────────────────────────────────────────
    pdf.output(OUTPUT)
    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\n\u2705  Report saved to {OUTPUT}")
    print(f"   {pdf.page_no()} pages | {size_kb:.0f} KB")


if __name__ == "__main__":
    build()
