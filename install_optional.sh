#!/bin/bash
# Install Optional BIOCANVAS Dependencies
# These are needed for full molecular docking functionality

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🧬 BIOCANVAS v2.0 - Optional Dependencies Installer      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    echo "   Download: https://docs.conda.io/projects/miniconda/en/latest/"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"
echo ""

# Menu
echo "Select what to install:"
echo "1) AutoDock Vina (required for docking scoring)"
echo "2) OpenBabel (required for PDB→PDBQT conversion)"
echo "3) Both"
echo "4) Exit"
echo ""

read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Installing AutoDock Vina..."
        echo "This will help you get the best molecular docking scoring."
        echo ""
        conda install -c bioconda autodock-vina -y
        echo ""
        echo "✅ AutoDock Vina installed successfully!"
        echo ""
        ;;
    2)
        echo ""
        echo "📦 Installing OpenBabel..."
        echo "This will enable PDB→PDBQT conversion for molecular preparation."
        echo ""
        conda install -c conda-forge openbabel -y
        echo ""
        echo "✅ OpenBabel installed successfully!"
        echo ""
        ;;
    3)
        echo ""
        echo "📦 Installing AutoDock Vina..."
        conda install -c bioconda autodock-vina -y
        echo "✅ AutoDock Vina installed!"
        echo ""
        echo "📦 Installing OpenBabel..."
        conda install -c conda-forge openbabel -y
        echo "✅ OpenBabel installed!"
        echo ""
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo "═════════════════════════════════════════════════════════════"
echo "✅ Installation complete!"
echo "═════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Ready to use BIOCANVAS:"
echo "   python3 run.py"
echo ""
echo "📚 Visit API docs:"
echo "   http://localhost:8000/docs"
echo ""
