#!/usr/bin/env python3
"""End-to-end docking test — fetches PDB, submits job, polls for result."""
import requests
import time
import sys

BASE = "http://127.0.0.1:8000"

def main():
    # 1. Health check
    print("1. Checking backend health...")
    h = requests.get(f"{BASE}/health").json()
    print(f"   Status: {h['status']}, Engine: {h['engine']}")
    assert h["engine"] == "ready", "Engine not ready!"

    # 2. Fetch proteins/ligands
    print("2. Checking molecule library...")
    proteins = requests.get(f"{BASE}/proteins").json()
    ligands = requests.get(f"{BASE}/ligands").json()
    print(f"   Proteins: {len(proteins)}, Ligands: {len(ligands)}")
    assert len(proteins) > 0, "No proteins!"
    assert len(ligands) > 0, "No ligands!"

    # 3. Fetch a test PDB file (Insulin)
    print("3. Fetching insulin PDB from AlphaFold...")
    meta = requests.get("https://alphafold.ebi.ac.uk/api/prediction/P01308").json()
    pdb_url = meta[0]["pdbUrl"]
    pdb_text = requests.get(pdb_url).text
    print(f"   PDB fetched: {len(pdb_text)} chars")
    assert "ATOM" in pdb_text, "Invalid PDB!"

    # 4. Submit docking job
    smiles = "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O"  # Glucose
    print(f"4. Submitting docking job (Insulin + Glucose)...")
    resp = requests.post(
        f"{BASE}/dock",
        files={"file": ("insulin.pdb", pdb_text, "chemical/x-pdb")},
        data={"smiles": smiles},
    )
    assert resp.status_code == 200, f"Submit failed: {resp.status_code} {resp.text}"
    job = resp.json()
    job_id = job["job_id"]
    print(f"   Job submitted: {job_id[:8]}... status={job['status']}")

    # 5. Poll for result (up to 120 seconds)
    print("5. Polling for result...")
    for i in range(60):
        time.sleep(2)
        r = requests.get(f"{BASE}/jobs/{job_id}")
        j = r.json()
        status = j["status"]
        print(f"   Poll {i+1}: status={status}")
        if status == "completed":
            result = j["result"]
            print(f"\n   ✓ DOCKING SUCCESS!")
            print(f"     Affinity: {result.get('affinity')} kcal/mol")
            print(f"     Simulated: {result.get('simulated', False)}")
            print(f"     Box center: {result.get('box_center')}")
            print(f"     Box size: {result.get('box_size')}")
            if result.get("output_file"):
                print(f"     Output file: {result['output_file']}")
            print("\n   ALL TESTS PASSED ✓")
            return 0
        elif status == "failed":
            print(f"\n   ✗ DOCKING FAILED: {j.get('error')}")
            return 1

    print("\n   ⚠ Timed out after 120 seconds")
    return 1


if __name__ == "__main__":
    sys.exit(main())
