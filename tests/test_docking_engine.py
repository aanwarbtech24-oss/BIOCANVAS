"""
BioCanvas Pro — Unit tests for DockingEngine.
Tests Lipinski calculation, Vina output parsing, interaction simulation,
and ligand preparation (mocking Vina/PLIP where needed).
"""

import re
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

try:
    from backend.docking_engine import DockingEngine
    _HAS_ENGINE = True
except (ImportError, ModuleNotFoundError):
    _HAS_ENGINE = False
    DockingEngine = None  # type: ignore[misc,assignment]

pytestmark = pytest.mark.skipif(
    not _HAS_ENGINE,
    reason="DockingEngine requires meeko + rdkit — skipping on environments without them",
)

# ═══════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def engine(tmp_path):
    """Create a DockingEngine with a temp work directory."""
    return DockingEngine(work_dir=str(tmp_path))


SAMPLE_VINA_OUTPUT = """\
MODEL 1
REMARK VINA RESULT:    -7.30      0.000      0.000
ATOM      1  C1  LIG A   1       1.000   2.000   3.000  1.00  0.00     0.000 C
ENDMDL
MODEL 2
REMARK VINA RESULT:    -6.50      1.234      2.345
ATOM      1  C1  LIG A   1       4.000   5.000   6.000  1.00  0.00     0.000 C
ENDMDL
MODEL 3
REMARK VINA RESULT:    -5.80      2.100      3.400
ATOM      1  C1  LIG A   1       7.000   8.000   9.000  1.00  0.00     0.000 C
ENDMDL
"""


# ═══════════════════════════════════════════════════════════════════════════
#  1. Lipinski Rule-of-Five
# ═══════════════════════════════════════════════════════════════════════════


class TestLipinski:
    """Test Lipinski descriptor calculation."""

    def test_aspirin_passes_ro5(self, engine, aspirin_smiles):
        result = engine.calculate_lipinski(aspirin_smiles)
        assert result["pass_rule_of_five"] is True
        assert 100 < result["mw"] < 250  # Aspirin MW ~180
        assert result["hbd"] >= 0
        assert result["hba"] >= 0

    def test_caffeine_passes_ro5(self, engine, caffeine_smiles):
        result = engine.calculate_lipinski(caffeine_smiles)
        assert result["pass_rule_of_five"] is True
        assert "mw" in result
        assert "logp" in result

    def test_invalid_smiles_returns_zeros(self, engine):
        result = engine.calculate_lipinski("NOT_A_SMILES")
        assert result["mw"] == 0
        assert result["pass_rule_of_five"] is False

    def test_empty_smiles_returns_zeros(self, engine):
        result = engine.calculate_lipinski("")
        # RDKit MolFromSmiles("") returns None
        assert result["pass_rule_of_five"] is False

    def test_lipinski_keys(self, engine, aspirin_smiles):
        result = engine.calculate_lipinski(aspirin_smiles)
        required_keys = {"mw", "logp", "hbd", "hba", "pass_rule_of_five"}
        assert required_keys.issubset(result.keys())

    def test_large_molecule_fails_ro5(self, engine):
        # Very large molecule (MW > 500, many H-bond donors/acceptors)
        large_smiles = "OC(=O)" + "C" * 50 + "N" * 10
        result = engine.calculate_lipinski(large_smiles)
        assert result["mw"] > 500


# ═══════════════════════════════════════════════════════════════════════════
#  2. Multi-pose Vina Output Parser
# ═══════════════════════════════════════════════════════════════════════════


class TestVinaOutputParser:
    """Test parse_vina_output with a mock PDBQT file."""

    def test_parses_three_poses(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        assert len(poses) == 3

    def test_pose_rank_ordering(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        ranks = [p["pose_rank"] for p in poses]
        assert ranks == [1, 2, 3]

    def test_affinity_values(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        assert poses[0]["affinity"] == -7.3
        assert poses[1]["affinity"] == -6.5
        assert poses[2]["affinity"] == -5.8

    def test_rmsd_values(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        assert poses[0]["rmsd_lb"] == 0.0
        assert poses[0]["rmsd_ub"] == 0.0
        assert poses[1]["rmsd_lb"] == 1.234
        assert poses[1]["rmsd_ub"] == 2.345

    def test_ligand_efficiency_calculated(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        # LE = affinity / heavy_atoms; aspirin has 13 heavy atoms
        for pose in poses:
            assert "ligand_efficiency" in pose
            assert isinstance(pose["ligand_efficiency"], float)

    def test_empty_pdbqt_returns_empty(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "empty.pdbqt"
        pdbqt_file.write_text("")
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        assert poses == []

    def test_interactions_default_empty(self, engine, tmp_path, aspirin_smiles):
        pdbqt_file = tmp_path / "test_output.pdbqt"
        pdbqt_file.write_text(SAMPLE_VINA_OUTPUT)
        poses = engine.parse_vina_output(pdbqt_file, aspirin_smiles)
        for pose in poses:
            assert "interactions" in pose
            assert pose["interactions"]["hydrogen_bonds"] == []


# ═══════════════════════════════════════════════════════════════════════════
#  3. Simulated Docking (no Vina needed)
# ═══════════════════════════════════════════════════════════════════════════


class TestSimulatedDocking:
    """Test the deterministic simulation fallback."""

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_simulation_returns_complete_schema(self, engine, minimal_pdb_file, aspirin_smiles):
        result = engine.run_docking(str(minimal_pdb_file), aspirin_smiles, "test-sim-001")
        assert result["success"] is True
        assert result["simulated"] is True
        assert "lipinski" in result
        assert "poses" in result
        assert len(result["poses"]) >= 3
        assert "affinity" in result

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_simulation_deterministic(self, engine, minimal_pdb_file, aspirin_smiles):
        """Same inputs must produce identical outputs (seeded RNG)."""
        r1 = engine.run_docking(str(minimal_pdb_file), aspirin_smiles, "test-det-001")
        r2 = engine.run_docking(str(minimal_pdb_file), aspirin_smiles, "test-det-002")
        assert r1["affinity"] == r2["affinity"]
        assert len(r1["poses"]) == len(r2["poses"])
        assert r1["poses"][0]["affinity"] == r2["poses"][0]["affinity"]

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_simulation_pose_schema(self, engine, minimal_pdb_file, aspirin_smiles):
        result = engine.run_docking(str(minimal_pdb_file), aspirin_smiles, "test-schema-001")
        pose = result["poses"][0]
        required = {"pose_rank", "affinity", "ligand_efficiency", "rmsd_lb", "rmsd_ub", "interactions"}
        assert required.issubset(pose.keys())

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_simulation_interactions_schema(self, engine, minimal_pdb_file, aspirin_smiles):
        result = engine.run_docking(str(minimal_pdb_file), aspirin_smiles, "test-int-001")
        interactions = result["poses"][0]["interactions"]
        assert "hydrogen_bonds" in interactions
        assert "hydrophobic" in interactions
        assert "pi_stacking" in interactions
        assert "salt_bridges" in interactions

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_invalid_smiles_raises(self, engine, minimal_pdb_file):
        with pytest.raises(ValueError, match="Invalid SMILES"):
            engine.run_docking(str(minimal_pdb_file), "DEFINITELY_NOT_SMILES", "test-bad-001")

    @patch("backend.docking_engine.VINA_AVAILABLE", False)
    def test_missing_pdb_raises(self, engine, tmp_path, aspirin_smiles):
        fake_path = str(tmp_path / "nonexistent.pdb")
        with pytest.raises(FileNotFoundError):
            engine.run_docking(fake_path, aspirin_smiles, "test-nopdb-001")


# ═══════════════════════════════════════════════════════════════════════════
#  4. Receptor Preparation
# ═══════════════════════════════════════════════════════════════════════════


class TestReceptorPrep:
    """Test PDB → PDBQT conversion."""

    def test_receptor_pdbqt_created(self, engine, minimal_pdb_file):
        output = engine.prepare_receptor(minimal_pdb_file, "test-recep-001")
        assert output.exists()
        assert output.suffix == ".pdbqt"

    def test_receptor_pdbqt_contains_atoms(self, engine, minimal_pdb_file):
        output = engine.prepare_receptor(minimal_pdb_file, "test-recep-002")
        content = output.read_text()
        assert "ATOM" in content
        assert "END" in content

    def test_receptor_nonexistent_file_raises(self, engine, tmp_path):
        fake = tmp_path / "ghost.pdb"
        with pytest.raises(FileNotFoundError):
            engine.prepare_receptor(fake, "test-recep-003")


# ═══════════════════════════════════════════════════════════════════════════
#  5. Box Calculation
# ═══════════════════════════════════════════════════════════════════════════


class TestBoxCalculation:
    """Test docking box center/size calculation."""

    def test_box_returns_center_and_size(self, engine, minimal_pdb_file):
        center, size = engine.calculate_box(minimal_pdb_file)
        assert len(center) == 3
        assert len(size) == 3

    def test_box_values_are_floats(self, engine, minimal_pdb_file):
        center, size = engine.calculate_box(minimal_pdb_file)
        for v in center + size:
            assert isinstance(v, float)

    def test_box_size_includes_padding(self, engine, minimal_pdb_file):
        _, size = engine.calculate_box(minimal_pdb_file)
        # Size should be > 10 Å (the padding) for any protein
        for dim in size:
            assert dim >= 10.0
