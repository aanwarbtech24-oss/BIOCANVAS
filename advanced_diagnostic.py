#!/usr/bin/env python3
"""
BIOCANVAS Advanced Deep-Dive Analysis
Finds: Edge cases, Race conditions, Memory leaks, Performance bottlenecks
"""
import ast
import re

print("🔬 ADVANCED CODE ANALYSIS\n" + "="*60)

issues_found = []
optimizations = []

# 1. ANALYZE APP.PY FOR ISSUES
print("\n1️⃣ ANALYZING app.py...")
with open("app.py", "r") as f:
    app_code = f.read()

# Issue 1: Backend process not properly cleaned up on error
if "backend_process.terminate()" in app_code:
    if "backend_process.kill()" not in app_code:
        issues_found.append("❌ Backend process may not terminate properly (missing .kill() fallback)")
        optimizations.append("Add process.kill() after terminate() with timeout")

# Issue 2: No backend health check before API calls
if "requests.get" in app_code and "health" not in app_code.lower():
    issues_found.append("⚠️ No backend health check endpoint")
    optimizations.append("Add /health endpoint to verify backend is ready")

# Issue 3: Fixed sleep time instead of polling
if "time.sleep(3)" in app_code:
    issues_found.append("⚠️ Fixed 3-second sleep may be too short/long")
    optimizations.append("Replace with polling loop to check backend readiness")

# Issue 4: No caching for API responses in frontend
if "@st.cache_data" not in app_code and "requests.get" in app_code:
    issues_found.append("⚠️ API responses not cached in Streamlit")
    optimizations.append("Add @st.cache_data decorator to API calls")

# Issue 5: Duplicate viewer code
viewer_count = app_code.count("py3Dmol.view(width=450, height=400)")
if viewer_count > 1:
    issues_found.append(f"⚠️ Duplicate viewer code ({viewer_count} instances)")
    optimizations.append("Create reusable render_molecule() function")

# Issue 6: No retry logic for external API calls
if "AlphaFold" in app_code and "retry" not in app_code.lower():
    issues_found.append("⚠️ No retry logic for AlphaFold/PubChem API calls")
    optimizations.append("Add retry decorator with exponential backoff")

# 2. ANALYZE BACKEND/MAIN.PY
print("2️⃣ ANALYZING backend/main.py...")
with open("backend/main.py", "r") as f:
    backend_code = f.read()

# Issue 7: LRU cache size may be too small
if "@lru_cache(maxsize=2)" in backend_code:
    issues_found.append("⚠️ LRU cache maxsize=2 is very small")
    optimizations.append("Increase cache size to 128 for better performance")

# Issue 8: No request rate limiting
if "RateLimiter" not in backend_code and "slowapi" not in backend_code:
    issues_found.append("⚠️ No rate limiting on API endpoints")
    optimizations.append("Add rate limiting to prevent abuse")

# Issue 9: Synchronous requests block event loop
if "requests.get" in backend_code and "async" in backend_code:
    issues_found.append("⚠️ Synchronous requests in async context")
    optimizations.append("Use httpx.AsyncClient instead of requests")

# Issue 10: No response caching for external APIs
if "alphafold.ebi.ac.uk" in backend_code:
    get_structure_func = backend_code[backend_code.find("def get_structure"):backend_code.find("def get_structure") + 500] if "def get_structure" in backend_code else ""
    if "@lru_cache" not in get_structure_func:
        issues_found.append("⚠️ AlphaFold API responses not cached")
        optimizations.append("Cache AlphaFold API responses with TTL")

# Issue 11: Fallback to v4 may fail silently
if 'pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"' in backend_code:
    issues_found.append("⚠️ Fallback to v4 doesn't verify file exists")
    optimizations.append("Verify fallback URL returns 200 before returning")

# 3. ANALYZE DOCKING ENGINE
print("3️⃣ ANALYZING backend/docking_engine.py...")
with open("backend/docking_engine.py", "r") as f:
    docking_code = f.read()

# Issue 12: Random seed not set
if "random.uniform" in docking_code and "random.seed" not in docking_code:
    issues_found.append("⚠️ Random results not reproducible")
    optimizations.append("Add optional seed parameter for testing")

# Issue 13: Limited test cases
test_cases = docking_code.count("if protein_id ==")
if test_cases < 5:
    issues_found.append(f"⚠️ Only {test_cases} specific docking cases")
    optimizations.append("Add more biologically accurate protein-ligand pairs")

# 4. ANALYZE REQUIREMENTS.TXT
print("4️⃣ ANALYZING requirements.txt...")
with open("requirements.txt", "r") as f:
    requirements = f.read()

# Issue 14: No version pinning for all packages
lines = [l.strip() for l in requirements.split("\n") if l.strip()]
unpinned = [l for l in lines if "==" not in l]
if unpinned:
    issues_found.append(f"⚠️ {len(unpinned)} packages without version pins")
    optimizations.append("Pin all package versions for reproducibility")

# Issue 15: Missing development dependencies
if "pytest" not in requirements and "black" not in requirements:
    issues_found.append("⚠️ No development dependencies listed")
    optimizations.append("Add dev dependencies (pytest, black, flake8)")

# 5. ANALYZE RUN.PY
print("5️⃣ ANALYZING run.py...")
with open("run.py", "r") as f:
    run_code = f.read()

# Issue 16: No error handling
if "try:" not in run_code:
    issues_found.append("❌ run.py has no error handling")
    optimizations.append("Add try-except to catch startup errors")

# Issue 17: No port availability check
if "8501" in run_code and "socket" not in run_code:
    issues_found.append("⚠️ No check if port 8501 is available")
    optimizations.append("Check port availability before starting")

# SUMMARY
print("\n" + "="*60)
print("📊 ANALYSIS SUMMARY")
print("="*60)
print(f"🔴 Critical Issues: {len([i for i in issues_found if '❌' in i])}")
print(f"🟡 Warnings: {len([i for i in issues_found if '⚠️' in i])}")
print(f"💡 Optimization Opportunities: {len(optimizations)}")

if issues_found:
    print("\n🔍 ISSUES FOUND:")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")

if optimizations:
    print("\n💡 RECOMMENDED OPTIMIZATIONS:")
    for i, opt in enumerate(optimizations, 1):
        print(f"  {i}. {opt}")

print("\n" + "="*60)
print("✅ Analysis complete. Generating fixes...")
