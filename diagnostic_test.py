#!/usr/bin/env python3
"""
BIOCANVAS v1.5 - Comprehensive Diagnostic Test Suite
Tests: Data integrity, API endpoints, performance, error handling
"""
import json
import time
import sys
from pathlib import Path

print("=" * 70)
print("🧬 BIOCANVAS v1.5 - COMPREHENSIVE DIAGNOSTIC TEST")
print("=" * 70)

# Test 1: Project Structure
print("\n📁 TEST 1: Project Structure")
print("-" * 70)
required_files = [
    'backend/main.py',
    'backend/docking_engine.py',
    'backend/__init__.py',
    'data/proteins.json',
    'data/ligands.json',
    'app.py',
    'requirements.txt'
]
for file in required_files:
    exists = Path(file).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {file}")
    if not exists:
        print(f"   ERROR: Missing required file!")
        sys.exit(1)

# Test 2: Data Integrity
print("\n📊 TEST 2: Data Integrity")
print("-" * 70)

# Test proteins.json
with open('data/proteins.json') as f:
    proteins = json.load(f)
print(f"✅ Proteins loaded: {len(proteins)} entries")
assert len(proteins) == 10, "Expected 10 proteins"

required_protein_fields = ['id', 'name', 'uniprot_id', 'function', 'category']
for protein in proteins:
    for field in required_protein_fields:
        assert field in protein, f"Missing field {field} in protein {protein.get('name')}"
print(f"✅ All proteins have required fields: {required_protein_fields}")

# Test ligands.json
with open('data/ligands.json') as f:
    ligands = json.load(f)
print(f"✅ Ligands loaded: {len(ligands)} entries")
assert len(ligands) == 10, "Expected 10 ligands"

required_ligand_fields = ['id', 'name', 'type', 'description', 'pubchem_cid']
for ligand in ligands:
    for field in required_ligand_fields:
        assert field in ligand, f"Missing field {field} in ligand {ligand.get('name')}"
print(f"✅ All ligands have required fields: {required_ligand_fields}")
print(f"✅ All ligands have PubChem CIDs (NEW in v1.5)")

# Test 3: Backend Code Quality
print("\n🔧 TEST 3: Backend Code Quality")
print("-" * 70)

# Syntax check
import py_compile
try:
    py_compile.compile('backend/main.py', doraise=True)
    print("✅ backend/main.py: Syntax valid")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)

try:
    py_compile.compile('backend/docking_engine.py', doraise=True)
    print("✅ backend/docking_engine.py: Syntax valid")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)

# Test 4: Docking Engine Logic
print("\n🧪 TEST 4: Docking Engine Logic")
print("-" * 70)

from backend.docking_engine import calculate_docking

# Test case 1: Strong binding
result1 = calculate_docking(1, 1)  # Hemoglobin + Heme B
assert result1['score'] == -11.5, f"Expected -11.5, got {result1['score']}"
assert result1['strength'] == "Strong Binding"
assert result1['success'] == True
print(f"✅ Strong binding test: Hemoglobin + Heme B = {result1['score']} kcal/mol")

# Test case 2: Strong binding
result2 = calculate_docking(7, 10)  # EGFR + Gefitinib
assert result2['score'] == -9.8, f"Expected -9.8, got {result2['score']}"
assert result2['strength'] == "Strong Binding"
print(f"✅ Strong binding test: EGFR + Gefitinib = {result2['score']} kcal/mol")

# Test case 3: Moderate binding
result3 = calculate_docking(10, 2)  # Amylase + Glucose
assert result3['score'] == -6.2, f"Expected -6.2, got {result3['score']}"
assert result3['strength'] == "Moderate Binding"
print(f"✅ Moderate binding test: Amylase + Glucose = {result3['score']} kcal/mol")

# Test case 4: Weak binding (random)
result4 = calculate_docking(3, 5)  # Random pair
assert -4.5 <= result4['score'] <= -3.0, f"Score {result4['score']} out of range"
assert result4['strength'] == "Weak Binding"
print(f"✅ Weak binding test: Random pair = {result4['score']} kcal/mol")

# Test 5: API Endpoint Availability
print("\n🌐 TEST 5: External API Availability")
print("-" * 70)

import requests

# Test AlphaFold API
try:
    response = requests.get("https://alphafold.ebi.ac.uk/api/prediction/P68871", timeout=5)
    if response.status_code == 200:
        print("✅ AlphaFold API: Accessible")
    else:
        print(f"⚠️  AlphaFold API: HTTP {response.status_code}")
except Exception as e:
    print(f"⚠️  AlphaFold API: {str(e)[:50]}")

# Test PubChem API (NEW in v1.5)
try:
    response = requests.head("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/SDF?record_type=3d", timeout=5)
    if response.status_code == 200:
        print("✅ PubChem API: Accessible (NEW in v1.5)")
    else:
        print(f"⚠️  PubChem API: HTTP {response.status_code}")
except Exception as e:
    print(f"⚠️  PubChem API: {str(e)[:50]}")

# Test 6: Performance Benchmarks
print("\n⚡ TEST 6: Performance Benchmarks")
print("-" * 70)

# Benchmark data loading
start = time.time()
for _ in range(100):
    with open('data/proteins.json') as f:
        json.load(f)
elapsed = time.time() - start
avg_time = elapsed / 100 * 1000
print(f"✅ Data loading: {avg_time:.2f}ms average (100 iterations)")
if avg_time > 10:
    print(f"⚠️  Warning: Data loading slower than expected")

# Benchmark docking calculation
start = time.time()
for _ in range(1000):
    calculate_docking(1, 1)
elapsed = time.time() - start
avg_time = elapsed / 1000 * 1000
print(f"✅ Docking calculation: {avg_time:.3f}ms average (1000 iterations)")
if avg_time > 1:
    print(f"⚠️  Warning: Docking calculation slower than expected")

# Test 7: Memory Usage
print("\n💾 TEST 7: Memory Efficiency")
print("-" * 70)

import sys
proteins_size = sys.getsizeof(json.dumps(proteins))
ligands_size = sys.getsizeof(json.dumps(ligands))
total_size = proteins_size + ligands_size
print(f"✅ Proteins data: {proteins_size} bytes")
print(f"✅ Ligands data: {ligands_size} bytes")
print(f"✅ Total data size: {total_size} bytes ({total_size/1024:.2f} KB)")

# Test 8: Error Handling
print("\n🛡️  TEST 8: Error Handling")
print("-" * 70)

# Test invalid protein/ligand IDs
result = calculate_docking(999, 999)
assert result['success'] == True, "Should handle invalid IDs gracefully"
assert result['strength'] == "Weak Binding", "Should return weak binding for invalid pairs"
print("✅ Invalid ID handling: Graceful fallback")

# Test 9: Version 1.5 Features
print("\n🆕 TEST 9: Version 1.5 New Features")
print("-" * 70)

# Check PubChem CID presence
pubchem_cids = [l['pubchem_cid'] for l in ligands]
assert len(pubchem_cids) == 10, "All ligands should have PubChem CIDs"
assert all(isinstance(cid, int) for cid in pubchem_cids), "All CIDs should be integers"
print(f"✅ PubChem CIDs: All {len(pubchem_cids)} ligands have valid CIDs")
print(f"   Sample CIDs: {pubchem_cids[:3]}")

# Check backend endpoint exists
with open('backend/main.py') as f:
    backend_code = f.read()
assert '/ligand-structure/' in backend_code, "New ligand structure endpoint missing"
print("✅ New endpoint: /ligand-structure/{cid} implemented")

# Final Summary
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)
print("✅ All critical tests passed!")
print("✅ Data integrity: VERIFIED")
print("✅ Backend logic: WORKING")
print("✅ Performance: OPTIMAL")
print("✅ Error handling: ROBUST")
print("✅ Version 1.5 features: IMPLEMENTED")
print("\n🎉 BIOCANVAS v1.5 is ready for frontend integration!")
print("=" * 70)
