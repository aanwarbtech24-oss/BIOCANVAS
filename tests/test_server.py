#!/usr/bin/env python3
"""
Quick server test to verify BIOCANVAS API is working
"""

import subprocess
import time
import sys
import requests
import json

def test_server():
    """Start server and run basic tests"""
    print("\n" + "="*60)
    print("🧬 BIOCANVAS v2.0 - Server Test")
    print("="*60 + "\n")
    
    # Start server
    print("🚀 Starting server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server
    time.sleep(3)
    
    try:
        # Test 1: Health check
        print("📋 TEST 1: Health Check")
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Status: OK")
            print(f"  └─ Response: {response.json()}\n")
        else:
            print(f"  ❌ Failed: {response.status_code}\n")
            return False
        
        # Test 2: Info endpoint
        print("📋 TEST 2: Info Endpoint")
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: OK")
            print(f"  └─ Title: {data.get('title')}")
            print(f"  └─ Version: {data.get('version')}\n")
        else:
            print(f"  ❌ Failed: {response.status_code}\n")
            return False
        
        # Test 3: Swagger UI
        print("📋 TEST 3: API Documentation")
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("  ✅ Swagger UI available at /docs\n")
        else:
            print(f"  ❌ Failed: {response.status_code}\n")
            return False
        
        # Summary
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🌐 API Endpoints:")
        print("  • API Documentation: http://localhost:8000/docs")
        print("  • API Server: http://localhost:8000")
        print("  • Health Check: http://localhost:8000/health")
        print("\n📝 To start the server, run:")
        print("  python3 run.py")
        print("  or")
        print("  python3 -m uvicorn backend.main:app --reload\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection Error: {e}\n")
        return False
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
