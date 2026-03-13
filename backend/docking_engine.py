"""
BioCanvas v2.0 — Molecular Docking Engine

Production-ready AutoDock Vina integration with pure-Python PDB-to-PDBQT
conversion.  Falls back to deterministic simulation when Vina is absent.
"""

import hashlib
import logging
import random
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from Bio.PDB import PDBParser, PDBIO
from meeko import MoleculePreparation
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

logger = logging.getLogger("biocanvas.docking")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AD4_ATOM_TYPES: Dict[str, str] = {
    "C": "C", "N": "N", "O": "OA", "S": "SA", "H": "HD",
    "F": "F", "CL": "Cl", "BR": "Br", "I": "I", "P": "P",
    "FE": "Fe", "ZN": "Zn", "MG": "Mg", "MN": "Mn", "CA": "Ca",
}

STANDARD_RESIDUES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS",
    "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP",
    "TYR", "VAL",
}

# Detect Vina CLI binary (prefer CLI over broken Python bindings)
VINA_BIN = shutil.which("vina")
VINA_AVAILABLE = VINA_BIN is not None

# Optional PLIP import (needs openbabel)
try:
    from plip.structure.preparation import PDBComplex  # noqa: F401
    PLIP_AVAILABLE = True
except ImportError:
    PLIP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class DockingEngine:
    """Handles ligand/receptor preparation and Vina docking."""

    def __init__(self, work_dir: str = "docking_jobs"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        logger.info("DockingEngine ready  work_dir=%s  vina=%s",
                     self.work_dir, VINA_AVAILABLE)

    # ------------------------------------------------------------------
    # Ligand preparation
    # ------------------------------------------------------------------

    def prepare_ligand(self, smiles: str, job_id: str) -> Path:
        """Convert a SMILES string to a 3-D optimised PDBQT via RDKit + Meeko."""
        if not smiles or not isinstance(smiles, str):
            raise ValueError("SMILES cannot be empty")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")

        mol = Chem.AddHs(mol)

        # 3-D embedding with fallback
        if AllChem.EmbedMolecule(mol, randomSeed=42) == -1:
            if AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=42) == -1:
                raise RuntimeError("Failed to generate 3D coordinates for ligand")
        AllChem.MMFFOptimizeMolecule(mol)

        # Meeko PDBQT conversion
        prep = MoleculePreparation()
        prep.prepare(mol)
        pdbqt_string = prep.write_pdbqt_string()

        output_path = self.work_dir / f"{job_id}_ligand.pdbqt"
        output_path.write_text(pdbqt_string)
        logger.info("Job %s: ligand PDBQT written (%d bytes)", job_id, len(pdbqt_string))
        return output_path

    # ------------------------------------------------------------------
    # Receptor preparation (pure-Python, no OpenBabel)
    # ------------------------------------------------------------------

    def prepare_receptor(self, raw_pdb_path: Path, job_id: str) -> Path:
        """Clean a PDB (remove water/HETATM) and write AutoDock-style PDBQT."""
        raw_pdb_path = Path(raw_pdb_path)
        if not raw_pdb_path.exists():
            raise FileNotFoundError(f"PDB file not found: {raw_pdb_path}")

        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("protein", raw_pdb_path)
        model = structure[0]

        # Strip non-standard residues (water, ligands, ions)
        for chain in model:
            to_remove = [r.id for r in chain if r.id[0] != " "]
            for rid in to_remove:
                chain.detach_child(rid)

        # Save cleaned PDB (used later for box calculation)
        clean_pdb = self.work_dir / f"{job_id}_clean.pdb"
        io = PDBIO()
        io.set_structure(structure)
        io.save(str(clean_pdb))

        # Write PDBQT with AutoDock atom types
        output_pdbqt = self.work_dir / f"{job_id}_receptor.pdbqt"
        lines: list[str] = []
        serial = 0

        for chain in model:
            for residue in chain:
                res_name = residue.get_resname().strip()
                res_seq = residue.get_id()[1]
                chain_id = chain.get_id()
                for atom in residue:
                    serial += 1
                    name = atom.get_name()
                    coord = atom.get_vector()
                    element = (atom.element.strip().upper()
                               if atom.element else name[0].upper())

                    ad_map = {"H": "HD", "N": "NA", "O": "OA", "S": "SA"}
                    ad_type = ad_map.get(element, AD4_ATOM_TYPES.get(element, element[:2]))

                    atom_name = f" {name:<3s}" if len(name) < 4 else name[:4]
                    lines.append(
                        f"ATOM  {serial:5d} {atom_name:4s} "
                        f"{res_name:>3s} {chain_id:1s}{res_seq:4d}    "
                        f"{coord[0]:8.3f}{coord[1]:8.3f}{coord[2]:8.3f}"
                        f"{1.00:6.2f}{0.00:6.2f}    "
                        f"{0.000:+7.3f} {ad_type:<2s}"
                    )

        lines.append("END")
        output_pdbqt.write_text("\n".join(lines) + "\n")
        logger.info("Job %s: receptor PDBQT written (%d atoms)", job_id, serial)
        return output_pdbqt

    # ------------------------------------------------------------------
    # Box calculation
    # ------------------------------------------------------------------

    def calculate_box(self, pdb_file: Path) -> Tuple[List[float], List[float]]:
        """Return (center, size) of the docking search box with 10 A padding."""
        pdb_file = Path(pdb_file)
        if not pdb_file.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_file}")

        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("protein", pdb_file)
        model = structure[0]

        coords = [
            atom.coord
            for chain in model
            for residue in chain
            if residue.id[0] == " "
            for atom in residue
        ]
        if not coords:
            coords = [
                atom.coord
                for chain in model
                for residue in chain
                for atom in residue
            ]

        arr = np.array(coords)
        center = np.mean(arr, axis=0)
        size = (np.max(arr, axis=0) - np.min(arr, axis=0)) + 10.0

        if np.any(size > 40.0):
            logger.warning("Large search space: %s A", size.tolist())

        return center.tolist(), size.tolist()

    # ------------------------------------------------------------------
    # Lipinski / Drug-likeness descriptors (RDKit)
    # ------------------------------------------------------------------

    def calculate_lipinski(self, smiles: str) -> Dict[str, Any]:
        """Calculate Lipinski Rule-of-Five descriptors from a SMILES string."""
        if not smiles or not smiles.strip():
            return {"mw": 0, "logp": 0, "hbd": 0, "hba": 0, "pass_rule_of_five": False}
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"mw": 0, "logp": 0, "hbd": 0, "hba": 0, "pass_rule_of_five": False}

        mw = round(Descriptors.MolWt(mol), 2)
        logp = round(Descriptors.MolLogP(mol), 2)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        passes = mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10

        return {
            "mw": mw, "logp": logp, "hbd": hbd, "hba": hba,
            "pass_rule_of_five": passes,
        }

    # ------------------------------------------------------------------
    # Multi-pose Vina output parser
    # ------------------------------------------------------------------

    def parse_vina_output(self, pdbqt_file: Path, smiles: str) -> List[Dict[str, Any]]:
        """Parse ALL poses from a Vina output PDBQT (affinity + RMSD + LE)."""
        content = Path(pdbqt_file).read_text()

        mol = Chem.MolFromSmiles(smiles)
        heavy_atoms = mol.GetNumHeavyAtoms() if mol else 1

        poses: List[Dict[str, Any]] = []
        for i, match in enumerate(re.finditer(
            r"REMARK VINA RESULT:\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", content
        )):
            affinity = float(match.group(1))
            rmsd_lb = float(match.group(2))
            rmsd_ub = float(match.group(3))
            le = round(affinity / heavy_atoms, 3) if heavy_atoms > 0 else 0.0

            poses.append({
                "pose_rank": i + 1,
                "affinity": affinity,
                "ligand_efficiency": le,
                "rmsd_lb": rmsd_lb,
                "rmsd_ub": rmsd_ub,
                "interactions": {
                    "hydrogen_bonds": [], "hydrophobic": [],
                    "pi_stacking": [], "salt_bridges": [],
                },
            })

        logger.info("Parsed %d poses from %s", len(poses), pdbqt_file.name)
        return poses

    # ------------------------------------------------------------------
    # PDBQT → PDB helpers (for PLIP complex building)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_pose_block(pdbqt_content: str, pose_num: int = 1) -> str:
        """Extract a single MODEL block from multi-pose PDBQT."""
        blocks = re.split(r"^MODEL\s+\d+\s*$", pdbqt_content, flags=re.MULTILINE)
        if pose_num < len(blocks):
            block = blocks[pose_num]
            return re.sub(r"^ENDMDL.*$", "", block, flags=re.MULTILINE).strip()
        return pdbqt_content

    @staticmethod
    def _pdbqt_to_pdb_lines(pdbqt_text: str, resname: str = "LIG") -> List[str]:
        """Convert PDBQT ATOM lines → standard PDB HETATM lines for a ligand."""
        lines: List[str] = []
        serial = 1
        for raw in pdbqt_text.split("\n"):
            if raw.startswith(("ATOM", "HETATM")):
                name = raw[12:16]
                coord_block = raw[30:54]
                atom_name = name if len(name.strip()) == 4 else f" {name.strip():<3s}"
                lines.append(
                    f"HETATM{serial:5d} {atom_name:4s} "
                    f"{resname:>3s} X   1    "
                    f"{coord_block}"
                    f"  1.00  0.00"
                )
                serial += 1
        return lines

    def _build_complex_pdb(
        self,
        protein_pdb: Path,
        ligand_pdbqt_path: Path,
        output: Path,
    ) -> Path:
        """Merge protein PDB + docked ligand (pose 1) into a PLIP-ready complex."""
        pdbqt_content = ligand_pdbqt_path.read_text()
        pose1_block = self._extract_pose_block(pdbqt_content, 1)
        ligand_lines = self._pdbqt_to_pdb_lines(pose1_block)

        protein_text = protein_pdb.read_text()
        protein_lines = [
            l for l in protein_text.split("\n")
            if l.startswith(("ATOM", "TER"))
            or (l.startswith("HETATM") and "HOH" not in l)
        ]

        all_lines = protein_lines + ["TER"] + ligand_lines + ["END"]
        output.write_text("\n".join(all_lines) + "\n")
        logger.info("Complex PDB written: %s", output.name)
        return output

    # ------------------------------------------------------------------
    # PLIP interaction analysis
    # ------------------------------------------------------------------

    def _run_plip_analysis(
        self,
        job_id: str,
        protein_pdb: Path,
        ligand_pdbqt: Path,
    ) -> Dict[str, List]:
        """Run PLIP on protein + ligand complex; extract all interaction types."""
        empty: Dict[str, List] = {
            "hydrogen_bonds": [], "hydrophobic": [],
            "pi_stacking": [], "salt_bridges": [],
        }

        if not PLIP_AVAILABLE:
            logger.info("Job %s: PLIP not installed — skipping interaction analysis", job_id)
            return empty

        complex_pdb = self.work_dir / f"{job_id}_complex.pdb"
        self._build_complex_pdb(protein_pdb, ligand_pdbqt, complex_pdb)

        try:
            mol = PDBComplex()
            mol.load_pdb(str(complex_pdb))
            mol.analyze()

            result: Dict[str, List] = {
                "hydrogen_bonds": [], "hydrophobic": [],
                "pi_stacking": [], "salt_bridges": [],
            }

            for _bsid, site in mol.interaction_sets.items():
                # H-bonds (protein-donor + ligand-donor)
                all_hbonds = (
                    list(getattr(site, "hbonds_pdon", []))
                    + list(getattr(site, "hbonds_ldon", []))
                )
                for hb in all_hbonds:
                    result["hydrogen_bonds"].append({
                        "residue": f"{getattr(hb, 'restype', '?')}-{getattr(hb, 'resnr', '?')}",
                        "distance": round(getattr(hb, "distance_ah", 0.0), 2),
                        "protein_atom_idx": getattr(getattr(hb, "d", None), "idx", None),
                        "ligand_atom_idx": getattr(getattr(hb, "a", None), "idx", None),
                    })

                # Hydrophobic contacts
                for hp in getattr(site, "hydrophobic_contacts", []):
                    result["hydrophobic"].append({
                        "residue": f"{getattr(hp, 'restype', '?')}-{getattr(hp, 'resnr', '?')}",
                        "distance": round(getattr(hp, "distance", 0.0), 2),
                    })

                # Pi-stacking
                for ps in getattr(site, "pistacking", []):
                    result["pi_stacking"].append({
                        "residue": f"{getattr(ps, 'restype', '?')}-{getattr(ps, 'resnr', '?')}",
                        "distance": round(getattr(ps, "distance", 0.0), 2),
                        "type": getattr(ps, "type", ""),
                    })

                # Salt bridges
                all_sb = (
                    list(getattr(site, "saltbridge_lneg", []))
                    + list(getattr(site, "saltbridge_pneg", []))
                )
                for sb in all_sb:
                    result["salt_bridges"].append({
                        "residue": f"{getattr(sb, 'restype', '?')}-{getattr(sb, 'resnr', '?')}",
                        "distance": round(getattr(sb, "distance", 0.0), 2),
                    })

            logger.info(
                "Job %s: PLIP → %d H-bonds, %d hydrophobic, %d π-stack, %d salt-bridges",
                job_id,
                len(result["hydrogen_bonds"]),
                len(result["hydrophobic"]),
                len(result["pi_stacking"]),
                len(result["salt_bridges"]),
            )
            return result

        except Exception as exc:
            logger.warning("Job %s: PLIP analysis failed — %s", job_id, exc)
            return empty

    # ------------------------------------------------------------------
    # Simulated interactions (deterministic mock for non-Vina mode)
    # ------------------------------------------------------------------

    def _simulate_interactions(
        self,
        rng: random.Random,
        pdb_text: str,
    ) -> Dict[str, List]:
        """Generate deterministic mock interactions from PDB residue list."""
        residues: List[str] = []
        seen: set = set()
        for line in pdb_text.split("\n"):
            if line.startswith("ATOM") and len(line) > 26:
                resname = line[17:20].strip()
                resnr = line[22:26].strip()
                key = f"{resname}-{resnr}"
                if resname in STANDARD_RESIDUES and key not in seen:
                    residues.append(key)
                    seen.add(key)

        if not residues:
            return {
                "hydrogen_bonds": [], "hydrophobic": [],
                "pi_stacking": [], "salt_bridges": [],
            }

        def _pick(n: int, pool: List[str]) -> List[str]:
            return [rng.choice(pool) for _ in range(min(n, len(pool)))]

        hbonds = [
            {
                "residue": r,
                "distance": round(rng.uniform(2.5, 3.5), 2),
                "protein_atom_idx": rng.randint(1, 500),
                "ligand_atom_idx": rng.randint(1, 30),
            }
            for r in _pick(rng.randint(1, 5), residues)
        ]

        hydrophobic = [
            {"residue": r, "distance": round(rng.uniform(3.3, 4.0), 2)}
            for r in _pick(rng.randint(2, 8), residues)
        ]

        aromatic = [r for r in residues if r[:3] in ("PHE", "TYR", "TRP", "HIS")]
        pi_stacking = [
            {
                "residue": r,
                "distance": round(rng.uniform(3.5, 5.5), 2),
                "type": rng.choice(["P", "T"]),
            }
            for r in _pick(rng.randint(0, 2), aromatic)
        ] if aromatic else []

        charged = [r for r in residues if r[:3] in ("ASP", "GLU", "LYS", "ARG", "HIS")]
        salt_bridges = [
            {"residue": r, "distance": round(rng.uniform(3.5, 5.0), 2)}
            for r in _pick(rng.randint(0, 2), charged)
        ] if charged else []

        return {
            "hydrogen_bonds": hbonds,
            "hydrophobic": hydrophobic,
            "pi_stacking": pi_stacking,
            "salt_bridges": salt_bridges,
        }

    # ------------------------------------------------------------------
    # Simulated ligand 3D coordinate generation (for visualization)
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_simulated_ligand(
        mol, center: List[float], rng: random.Random
    ) -> str | None:
        """Generate HETATM lines for a ligand conformer placed at pocket center."""
        try:
            mol3d = Chem.AddHs(mol)
            params = AllChem.ETKDGv3()
            params.randomSeed = rng.randint(0, 2**31)
            status = AllChem.EmbedMolecule(mol3d, params)
            if status != 0:
                # Fallback: less strict embedding
                AllChem.EmbedMolecule(mol3d, AllChem.ETKDGv3())
            AllChem.MMFFOptimizeMolecule(mol3d, maxIters=200)
            mol3d = Chem.RemoveHs(mol3d)

            conf = mol3d.GetConformer()
            # Compute ligand centroid and translate to pocket center
            positions = conf.GetPositions()
            centroid = positions.mean(axis=0)
            translation = np.array(center) - centroid

            lines: List[str] = []
            for i, atom in enumerate(mol3d.GetAtoms()):
                pos = conf.GetAtomPosition(i)
                x = pos.x + translation[0]
                y = pos.y + translation[1]
                z = pos.z + translation[2]
                elem = atom.GetSymbol()
                name = f" {elem:<3s}" if len(elem) < 4 else elem
                lines.append(
                    f"HETATM{i + 1:5d} {name:4s} LIG X   1    "
                    f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {elem:>2s}"
                )
            return "\n".join(lines)
        except Exception as exc:
            logger.warning("Could not generate simulated ligand 3D: %s", exc)
            return None

    @staticmethod
    def _offset_ligand_lines(
        base_lines: str, rng: random.Random, pose_index: int
    ) -> str:
        """Apply small random translation to ligand HETATM lines for pose variety."""
        if pose_index == 0:
            return base_lines
        dx = rng.uniform(-1.5, 1.5)
        dy = rng.uniform(-1.5, 1.5)
        dz = rng.uniform(-1.5, 1.5)
        out: List[str] = []
        for line in base_lines.split("\n"):
            if line.startswith("HETATM"):
                try:
                    x = float(line[30:38]) + dx
                    y = float(line[38:46]) + dy
                    z = float(line[46:54]) + dz
                    line = f"{line[:30]}{x:8.3f}{y:8.3f}{z:8.3f}{line[54:]}"
                except (ValueError, IndexError):
                    pass
            out.append(line)
        return "\n".join(out)

    # ------------------------------------------------------------------
    # Simulation mode (deterministic mock when Vina is absent)
    # ------------------------------------------------------------------

    def _simulate_docking(self, pdb_file: str, smiles: str, job_id: str) -> Dict[str, Any]:
        """Generate deterministic mock results — Unified Discovery Report schema."""
        logger.warning("Job %s: SIMULATION mode (Vina not installed)", job_id)

        pdb_path = Path(pdb_file)
        if not pdb_path.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_path}")

        pdb_text = pdb_path.read_text()
        if len(pdb_text) < 50:
            raise ValueError("PDB file appears empty")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")

        # Deterministic seed from inputs
        seed = int(hashlib.sha256(
            (pdb_text[:2000] + smiles).encode()
        ).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        delay = rng.uniform(3.0, 6.0)
        time.sleep(delay)

        try:
            center, size = self.calculate_box(pdb_path)
        except Exception:
            center, size = [0.0, 0.0, 0.0], [20.0, 20.0, 20.0]

        # Lipinski — real calculation (only needs SMILES + RDKit)
        lipinski = self.calculate_lipinski(smiles)

        # Generate 3D ligand conformer placed at the binding pocket center
        ligand_pdbqt_str = self._generate_simulated_ligand(mol, center, rng)

        # Mock multi-pose results
        heavy_atoms = mol.GetNumHeavyAtoms() or 1
        num_poses = rng.randint(3, 9)
        best_affinity = round(rng.uniform(-11.5, -3.5), 2)

        # Build multi-MODEL PDBQT string with slightly varied poses
        model_blocks: List[str] = []
        poses: List[Dict[str, Any]] = []
        for i in range(num_poses):
            aff = best_affinity if i == 0 else round(
                best_affinity + i * rng.uniform(0.3, 0.8), 2
            )
            rmsd_ub = 0.0 if i == 0 else round(rng.uniform(0.5, 4.0), 3)
            rmsd_lb = 0.0 if i == 0 else round(rmsd_ub * rng.uniform(0.5, 0.9), 3)
            le = round(aff / heavy_atoms, 3)
            interactions = self._simulate_interactions(rng, pdb_text)

            poses.append({
                "pose_rank": i + 1,
                "affinity": aff,
                "ligand_efficiency": le,
                "rmsd_lb": rmsd_lb,
                "rmsd_ub": rmsd_ub,
                "interactions": interactions,
            })

            # Apply small random translation for each pose > 0
            if ligand_pdbqt_str:
                pose_lines = self._offset_ligand_lines(
                    ligand_pdbqt_str, rng, i,
                )
                remark = (
                    f"REMARK VINA RESULT:    {aff:.1f}      "
                    f"{rmsd_lb:.3f}      {rmsd_ub:.3f}"
                )
                model_blocks.append(
                    f"MODEL {i + 1}\n{remark}\n{pose_lines}\nENDMDL"
                )

        output_pdbqt = "\n".join(model_blocks) if model_blocks else None

        # Save to disk for consistency with the real path
        if output_pdbqt:
            out_path = self.work_dir / f"{job_id}_out.pdbqt"
            out_path.write_text(output_pdbqt)

        logger.info(
            "Job %s: simulation done — %d poses, best=%.2f kcal/mol",
            job_id, num_poses, best_affinity,
        )

        return {
            "success": True,
            "job_id": job_id,
            "lipinski": lipinski,
            "poses": poses,
            # Backward-compatible top-level shortcuts
            "affinity": best_affinity,
            "rmsd": poses[0]["rmsd_ub"] if poses else 0.0,
            "poses_count": len(poses),
            "duration": round(delay, 2),
            "box_center": center,
            "box_size": size,
            "simulated": True,
            # Ligand coordinates for the 3D viewer
            "output_pdbqt": output_pdbqt,
        }

    # ------------------------------------------------------------------
    # Main entry point — Unified Discovery Report
    # ------------------------------------------------------------------

    def run_docking(self, pdb_file: str, smiles: str, job_id: str) -> Dict[str, Any]:
        """Execute full docking workflow and return Unified Discovery Report."""
        logger.info("Job %s: docking workflow started", job_id)

        if not VINA_AVAILABLE:
            return self._simulate_docking(pdb_file, smiles, job_id)

        try:
            receptor_path = self.prepare_receptor(Path(pdb_file), job_id)
            ligand_path = self.prepare_ligand(smiles, job_id)
            center, size = self.calculate_box(Path(pdb_file))

            # Lipinski descriptors (always available — RDKit only)
            lipinski = self.calculate_lipinski(smiles)

            # Run Vina CLI — request up to 9 poses
            out_path = self.work_dir / f"{job_id}_out.pdbqt"
            cmd = [
                VINA_BIN,
                "--receptor", str(receptor_path),
                "--ligand", str(ligand_path),
                "--center_x", f"{center[0]:.3f}",
                "--center_y", f"{center[1]:.3f}",
                "--center_z", f"{center[2]:.3f}",
                "--size_x", f"{size[0]:.3f}",
                "--size_y", f"{size[1]:.3f}",
                "--size_z", f"{size[2]:.3f}",
                "--exhaustiveness", "8",
                "--num_modes", "9",
                "--out", str(out_path),
            ]
            logger.info("Job %s: running vina CLI: %s", job_id, " ".join(cmd))
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"Vina exited with code {proc.returncode}: {proc.stderr[:500]}"
                )

            # Parse all poses (affinity + RMSD + LE per pose)
            poses = self.parse_vina_output(out_path, smiles)

            # PLIP interaction analysis on best pose
            clean_pdb = self.work_dir / f"{job_id}_clean.pdb"
            if clean_pdb.exists():
                try:
                    interactions = self._run_plip_analysis(job_id, clean_pdb, out_path)
                    if poses:
                        poses[0]["interactions"] = interactions
                except Exception as exc:
                    logger.warning("Job %s: PLIP skipped — %s", job_id, exc)

            best = poses[0]["affinity"] if poses else 0.0
            logger.info(
                "Job %s: complete — %d poses, best=%.2f kcal/mol",
                job_id, len(poses), best,
            )

            # Read output PDBQT content for the 3D viewer
            output_pdbqt = out_path.read_text() if out_path.exists() else None

            return {
                "success": True,
                "job_id": job_id,
                "lipinski": lipinski,
                "poses": poses,
                # Backward-compatible top-level shortcuts
                "affinity": best,
                "rmsd": poses[0]["rmsd_ub"] if poses else 0.0,
                "poses_count": len(poses),
                "output_file": str(out_path),
                "output_pdbqt": output_pdbqt,
                "box_center": center,
                "box_size": size,
                "simulated": False,
            }
        except Exception as e:
            logger.error("Job %s: docking failed — %s", job_id, e)
            return {"success": False, "job_id": job_id, "error": str(e)}
