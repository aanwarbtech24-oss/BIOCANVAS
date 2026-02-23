"""
BioCanvas Pro — pytest configuration & shared fixtures.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Sample data fixtures ─────────────────────────────────────────────────

ASPIRIN_SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"
CAFFEINE_SMILES = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"

MINIMAL_PDB = """\
HEADER    TEST PROTEIN
ATOM      1  N   ALA A   1      10.000  10.000  10.000  1.00  0.00           N
ATOM      2  CA  ALA A   1      10.000  11.500  10.000  1.00  0.00           C
ATOM      3  C   ALA A   1      11.500  11.500  10.000  1.00  0.00           C
ATOM      4  O   ALA A   1      12.000  12.500  10.000  1.00  0.00           O
ATOM      5  N   GLY A   2      12.000  10.500  10.000  1.00  0.00           N
ATOM      6  CA  GLY A   2      13.500  10.500  10.000  1.00  0.00           C
ATOM      7  C   GLY A   2      14.000  11.500  10.000  1.00  0.00           C
ATOM      8  O   GLY A   2      15.000  11.500  10.000  1.00  0.00           O
ATOM      9  N   TYR A   3      14.000  12.500  10.000  1.00  0.00           N
ATOM     10  CA  TYR A   3      15.500  12.500  10.000  1.00  0.00           C
ATOM     11  C   TYR A   3      16.000  13.500  10.000  1.00  0.00           C
ATOM     12  O   TYR A   3      17.000  13.500  10.000  1.00  0.00           O
END
"""


@pytest.fixture
def aspirin_smiles():
    return ASPIRIN_SMILES


@pytest.fixture
def caffeine_smiles():
    return CAFFEINE_SMILES


@pytest.fixture
def minimal_pdb():
    return MINIMAL_PDB


@pytest.fixture
def minimal_pdb_file(tmp_path):
    """Write a minimal PDB to a temp file and return the Path."""
    p = tmp_path / "test_protein.pdb"
    p.write_text(MINIMAL_PDB)
    return p
