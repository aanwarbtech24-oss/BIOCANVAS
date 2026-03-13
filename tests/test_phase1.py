#!/usr/bin/env python3
"""Phase 1 End-to-End Test: Submit docking job and verify Unified Discovery Report schema."""
import json
import time
import requests

PDB_CONTENT = """\
ATOM      1  N   ALA A   1       1.000  2.000  3.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       2.000  3.000  4.000  1.00  0.00           C
ATOM      3  C   ALA A   1       3.000  4.000  5.000  1.00  0.00           C
ATOM      4  O   ALA A   1       4.000  5.000  6.000  1.00  0.00           O
ATOM      5  N   PHE A   2       5.000  6.000  7.000  1.00  0.00           N
ATOM      6  CA  PHE A   2       6.000  7.000  8.000  1.00  0.00           C
ATOM      7  N   TYR A   3       7.000  8.000  9.000  1.00  0.00           N
ATOM      8  CA  TYR A   3       8.000  9.000 10.000  1.00  0.00           C
ATOM      9  N   HIS A   4       9.000 10.000 11.000  1.00  0.00           N
ATOM     10  CA  HIS A   4      10.000 11.000 12.000  1.00  0.00           C
ATOM     11  N   ASP A   5      11.000 12.000 13.000  1.00  0.00           N
ATOM     12  CA  ASP A   5      12.000 13.000 14.000  1.00  0.00           C
ATOM     13  N   LYS A   6      13.000 14.000 15.000  1.00  0.00           N
ATOM     14  CA  LYS A   6      14.000 15.000 16.000  1.00  0.00           C
ATOM     15  N   LEU A   7      15.000 16.000 17.000  1.00  0.00           N
ATOM     16  CA  LEU A   7      16.000 17.000 18.000  1.00  0.00           C
END
"""

SMILES = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin

# Write test PDB
with open("/tmp/test_protein.pdb", "w") as f:
    f.write(PDB_CONTENT)

# Submit docking job
print("=== Submitting docking job ===")
resp = requests.post(
    "http://127.0.0.1:8000/dock",
    files={"file": ("protein.pdb", open("/tmp/test_protein.pdb", "rb"), "chemical/x-pdb")},
    data={"smiles": SMILES},
)
job = resp.json()
print(f"  job_id: {job['job_id']}")
print(f"  status: {job['status']}")

# Poll until complete
print("\n=== Polling for results ===")
data = None
for i in range(30):
    time.sleep(1)
    r = requests.get(f"http://127.0.0.1:8000/jobs/{job['job_id']}")
    data = r.json()
    if data["status"] in ("completed", "failed"):
        break
    print(f"  [{i+1}s] status={data['status']}")

# Print full response
print(f"\n=== Final Response (status={data['status']}) ===")
print(json.dumps(data, indent=2))

# Validate schema
print("\n=== Schema Validation ===")
assert data["status"] == "completed", f"Job failed: {data.get('error')}"

# Top-level fields
assert "lipinski" in data, "Missing top-level 'lipinski'"
assert "poses" in data, "Missing top-level 'poses'"
print("  ✅ lipinski and poses at top level")

# Lipinski
lip = data["lipinski"]
for key in ("mw", "logp", "hbd", "hba", "pass_rule_of_five"):
    assert key in lip, f"Missing lipinski.{key}"
print(f"  ✅ lipinski: MW={lip['mw']}, LogP={lip['logp']}, HBD={lip['hbd']}, HBA={lip['hba']}, RO5={'PASS' if lip['pass_rule_of_five'] else 'FAIL'}")

# Poses
poses = data["poses"]
assert isinstance(poses, list) and len(poses) > 0, "poses must be a non-empty list"
print(f"  ✅ {len(poses)} poses returned")

for i, pose in enumerate(poses):
    for key in ("pose_rank", "affinity", "ligand_efficiency", "rmsd_ub", "interactions"):
        assert key in pose, f"Missing pose[{i}].{key}"

pose1 = poses[0]
print(f"  ✅ Pose 1: affinity={pose1['affinity']} kcal/mol, LE={pose1['ligand_efficiency']}, RMSD_UB={pose1['rmsd_ub']}")

# Interactions
inter = pose1["interactions"]
for key in ("hydrogen_bonds", "hydrophobic", "pi_stacking", "salt_bridges"):
    assert key in inter, f"Missing interactions.{key}"
print(f"  ✅ Interactions: {len(inter['hydrogen_bonds'])} H-bonds, {len(inter['hydrophobic'])} hydrophobic, "
      f"{len(inter['pi_stacking'])} π-stack, {len(inter['salt_bridges'])} salt-bridges")

# Backward compat
assert "result" in data, "Missing result dict for backward compat"
result = data["result"]
assert "affinity" in result, "Missing result.affinity (backward compat)"
print(f"  ✅ Backward-compat: result.affinity={result['affinity']}")

print("\n🎉 Phase 1 — ALL TESTS PASSED")
