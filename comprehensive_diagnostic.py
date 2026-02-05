#!/usr/bin/env python3
"""
BIOCANVAS Comprehensive Deep-Dive Diagnostic Test
Tests: Architecture, Performance, Security, Code Quality, Functionality
"""
import json
import os
import sys
import time
import requests
from pathlib import Path

class DiagnosticTest:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def log(self, category, test, status, details=""):
        result = f"[{category}] {test}: {status}"
        if details:
            result += f" - {details}"
        self.results.append(result)
        print(result)
        
    def error(self, msg):
        self.errors.append(msg)
        print(f"❌ ERROR: {msg}")
        
    def warning(self, msg):
        self.warnings.append(msg)
        print(f"⚠️  WARNING: {msg}")

def test_file_structure(dt):
    """Test 1: File Structure & Organization"""
    print("\n" + "="*60)
    print("TEST 1: FILE STRUCTURE & ORGANIZATION")
    print("="*60)
    
    required_files = [
        "app.py",
        "run.py",
        "requirements.txt",
        "README.md",
        "backend/main.py",
        "backend/docking_engine.py",
        "data/proteins.json",
        "data/ligands.json"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            dt.log("STRUCTURE", f"File exists: {file}", "✅ PASS")
        else:
            dt.error(f"Missing required file: {file}")

def test_data_integrity(dt):
    """Test 2: Data Integrity & Validation"""
    print("\n" + "="*60)
    print("TEST 2: DATA INTEGRITY & VALIDATION")
    print("="*60)
    
    # Test proteins.json
    try:
        with open("data/proteins.json", "r") as f:
            proteins = json.load(f)
        
        if len(proteins) == 10:
            dt.log("DATA", "Protein count", "✅ PASS", "10 proteins found")
        else:
            dt.warning(f"Expected 10 proteins, found {len(proteins)}")
        
        # Validate protein structure
        required_keys = ["id", "name", "uniprot_id", "function", "category"]
        for p in proteins:
            missing = [k for k in required_keys if k not in p]
            if missing:
                dt.error(f"Protein {p.get('name', 'unknown')} missing keys: {missing}")
            else:
                dt.log("DATA", f"Protein {p['name']} structure", "✅ PASS")
                
    except Exception as e:
        dt.error(f"Failed to load proteins.json: {e}")
    
    # Test ligands.json
    try:
        with open("data/ligands.json", "r") as f:
            ligands = json.load(f)
        
        if len(ligands) == 10:
            dt.log("DATA", "Ligand count", "✅ PASS", "10 ligands found")
        else:
            dt.warning(f"Expected 10 ligands, found {len(ligands)}")
        
        # Validate ligand structure
        required_keys = ["id", "name", "type", "description", "pubchem_cid"]
        for l in ligands:
            missing = [k for k in required_keys if k not in l]
            if missing:
                dt.error(f"Ligand {l.get('name', 'unknown')} missing keys: {missing}")
            else:
                dt.log("DATA", f"Ligand {l['name']} structure", "✅ PASS")
                
    except Exception as e:
        dt.error(f"Failed to load ligands.json: {e}")

def test_code_quality(dt):
    """Test 3: Code Quality & Best Practices"""
    print("\n" + "="*60)
    print("TEST 3: CODE QUALITY & BEST PRACTICES")
    print("="*60)
    
    # Check for proper error handling in app.py
    with open("app.py", "r") as f:
        app_code = f.read()
    
    if "try:" in app_code and "except" in app_code:
        dt.log("QUALITY", "Error handling in app.py", "✅ PASS")
    else:
        dt.warning("app.py lacks proper error handling")
    
    if "timeout=" in app_code:
        dt.log("QUALITY", "Request timeouts configured", "✅ PASS")
    else:
        dt.warning("Missing timeout configurations")
    
    # Check backend code quality
    with open("backend/main.py", "r") as f:
        backend_code = f.read()
    
    if "@lru_cache" in backend_code:
        dt.log("QUALITY", "Caching implemented", "✅ PASS")
    else:
        dt.warning("No caching found in backend")
    
    if "HTTPException" in backend_code:
        dt.log("QUALITY", "Proper HTTP exceptions", "✅ PASS")
    else:
        dt.warning("Missing proper HTTP exception handling")

def test_api_endpoints(dt):
    """Test 4: API Endpoint Availability"""
    print("\n" + "="*60)
    print("TEST 4: API ENDPOINT TESTING (requires backend running)")
    print("="*60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test if backend is running
    try:
        response = requests.get(f"{base_url}/proteins", timeout=2)
        if response.status_code == 200:
            dt.log("API", "/proteins endpoint", "✅ PASS")
        else:
            dt.warning(f"/proteins returned status {response.status_code}")
    except:
        dt.warning("Backend not running - skipping API tests")
        return
    
    # Test other endpoints
    endpoints = ["/ligands", "/structure/P69905"]
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                dt.log("API", f"{endpoint} endpoint", "✅ PASS")
            else:
                dt.warning(f"{endpoint} returned status {response.status_code}")
        except Exception as e:
            dt.error(f"{endpoint} failed: {e}")

def test_performance(dt):
    """Test 5: Performance Metrics"""
    print("\n" + "="*60)
    print("TEST 5: PERFORMANCE METRICS")
    print("="*60)
    
    # Test data loading speed
    start = time.perf_counter()
    with open("data/proteins.json", "r") as f:
        json.load(f)
    load_time = (time.perf_counter() - start) * 1000
    
    if load_time < 10:
        dt.log("PERFORMANCE", f"Data loading speed", "✅ PASS", f"{load_time:.2f}ms")
    else:
        dt.warning(f"Slow data loading: {load_time:.2f}ms")
    
    # Check file sizes
    app_size = os.path.getsize("app.py") / 1024
    if app_size < 50:
        dt.log("PERFORMANCE", f"app.py size", "✅ PASS", f"{app_size:.1f}KB")
    else:
        dt.warning(f"Large app.py file: {app_size:.1f}KB")

def test_security(dt):
    """Test 6: Security Best Practices"""
    print("\n" + "="*60)
    print("TEST 6: SECURITY CHECKS")
    print("="*60)
    
    # Check for hardcoded credentials
    files_to_check = ["app.py", "backend/main.py"]
    for file in files_to_check:
        with open(file, "r") as f:
            content = f.read().lower()
        
        if "password" in content or "api_key" in content:
            dt.warning(f"Potential hardcoded credentials in {file}")
        else:
            dt.log("SECURITY", f"No hardcoded credentials in {file}", "✅ PASS")
    
    # Check CORS configuration
    with open("backend/main.py", "r") as f:
        backend = f.read()
    
    if "CORSMiddleware" in backend:
        dt.log("SECURITY", "CORS configured", "✅ PASS")
    else:
        dt.warning("CORS not configured")

def test_dependencies(dt):
    """Test 7: Dependencies & Requirements"""
    print("\n" + "="*60)
    print("TEST 7: DEPENDENCIES & REQUIREMENTS")
    print("="*60)
    
    with open("requirements.txt", "r") as f:
        requirements = f.read()
    
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "requests", 
        "py3Dmol", "stmol", "pydantic"
    ]
    
    for package in required_packages:
        if package in requirements:
            dt.log("DEPENDENCIES", f"{package} listed", "✅ PASS")
        else:
            dt.error(f"Missing required package: {package}")

def test_documentation(dt):
    """Test 8: Documentation Quality"""
    print("\n" + "="*60)
    print("TEST 8: DOCUMENTATION QUALITY")
    print("="*60)
    
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            readme = f.read()
        
        if len(readme) > 500:
            dt.log("DOCS", "README.md exists and detailed", "✅ PASS")
        else:
            dt.warning("README.md is too brief")
        
        if "Quick Start" in readme or "Installation" in readme:
            dt.log("DOCS", "Setup instructions present", "✅ PASS")
        else:
            dt.warning("Missing setup instructions")
    else:
        dt.error("README.md not found")

def test_git_status(dt):
    """Test 9: Git Repository Status"""
    print("\n" + "="*60)
    print("TEST 9: GIT REPOSITORY STATUS")
    print("="*60)
    
    if os.path.exists(".git"):
        dt.log("GIT", "Repository initialized", "✅ PASS")
        
        # Check for .gitignore
        if os.path.exists(".gitignore"):
            dt.log("GIT", ".gitignore exists", "✅ PASS")
        else:
            dt.warning(".gitignore not found")
    else:
        dt.error("Not a git repository")

def main():
    print("\n" + "🧬"*30)
    print("BIOCANVAS COMPREHENSIVE DIAGNOSTIC TEST")
    print("🧬"*30)
    
    dt = DiagnosticTest()
    
    # Run all tests
    test_file_structure(dt)
    test_data_integrity(dt)
    test_code_quality(dt)
    test_api_endpoints(dt)
    test_performance(dt)
    test_security(dt)
    test_dependencies(dt)
    test_documentation(dt)
    test_git_status(dt)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"✅ Total Tests: {len(dt.results)}")
    print(f"❌ Errors: {len(dt.errors)}")
    print(f"⚠️  Warnings: {len(dt.warnings)}")
    
    if dt.errors:
        print("\n🔴 CRITICAL ERRORS:")
        for error in dt.errors:
            print(f"  - {error}")
    
    if dt.warnings:
        print("\n🟡 WARNINGS:")
        for warning in dt.warnings:
            print(f"  - {warning}")
    
    if not dt.errors and not dt.warnings:
        print("\n🎉 ALL TESTS PASSED! System is production-ready.")
    elif not dt.errors:
        print("\n✅ No critical errors. Review warnings for optimization.")
    else:
        print("\n❌ Critical errors found. Fix before deployment.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
