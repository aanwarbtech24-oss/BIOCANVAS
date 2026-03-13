#!/usr/bin/env python3
"""
BIOCANVAS v2.0 - One-Click Launcher
Simply run this script to start the complete application
"""

import subprocess
import sys
import socket
import webbrowser
import time
import os
from pathlib import Path

def check_port(port):
    """Check if port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def setup_venv():
    """Create and activate virtual environment if needed."""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        
        # Get the Python executable in the venv
        if sys.platform == "win32":
            python_exe = ".venv\\Scripts\\python"
            pip_exe = ".venv\\Scripts\\pip"
        else:
            python_exe = ".venv/bin/python"
            pip_exe = ".venv/bin/pip"
        
        print("📚 Installing dependencies...")
        subprocess.run([pip_exe, "install", "-q", "-r", "requirements.txt"], check=True)
        print("✅ Virtual environment ready")

def main():
    """Main launcher function."""
    print("")
    print("🧬 BIOCANVAS v2.0 - Molecular Docking Platform")
    print("=" * 50)
    print("")
    
    # Setup virtual environment
    setup_venv()
    
    # Check if port 8000 is available
    if not check_port(8000):
        print("")
        print("⚠️  Port 8000 is already in use.")
        print("   Either:")
        print("   1. Close the application using port 8000, or")
        print("   2. Run on a different port:")
        print("      python3 -m uvicorn backend.main:app --port 8001")
        print("")
        sys.exit(1)
    
    print("🚀 Starting BIOCANVAS Server...")
    print("")
    print("📍 Access Points:")
    print("   • API Server:   http://localhost:8000")
    print("   • API Docs:     http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("")
    print("⏳ Opening browser in 3 seconds...")
    print("🛑 Press Ctrl+C to stop the server")
    print("")
    
    time.sleep(3)
    
    # Try to open browser
    try:
        webbrowser.open("http://localhost:8000/docs")
    except:
        pass  # Browser open is optional
    
    # Start the server
    try:
        if sys.platform == "win32":
            python_exe = ".venv\\Scripts\\python"
        else:
            python_exe = ".venv/bin/python"
        
        subprocess.run([
            python_exe, "-m", "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("")
        print("")
        print("🛑 BIOCANVAS stopped.")
        print("")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
