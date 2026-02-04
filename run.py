#!/usr/bin/env python3
"""BIOCANVAS - One-Click Launcher"""
import subprocess
import sys

print("🧬 Starting BIOCANVAS...")
print("📍 Opening at: http://localhost:8501")
print("🛑 Press Ctrl+C to stop\n")

subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
