#!/usr/bin/env python3
"""BIOCANVAS - One-Click Launcher"""
import subprocess
import sys
import socket

def check_port(port):
    """Check if port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

try:
    if not check_port(8501):
        print("❌ Port 8501 is already in use. Please close the other application.")
        sys.exit(1)
    
    print("🧬 Starting BIOCANVAS...")
    print("📍 Opening at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop\n")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
except KeyboardInterrupt:
    print("\n🛑 BIOCANVAS stopped.")
except Exception as e:
    print(f"❌ Error starting BIOCANVAS: {e}")
    sys.exit(1)
