# 🧬 BIOCANVAS

**Educational End-to-End Drug Discovery Pipeline**

A modern bioinformatics web application featuring AlphaFold 3D protein visualization and educational molecular docking simulations.

---

## 🚀 Quick Start

### One-Command Launch:

```bash
python3 run.py
```

**That's it!** Your browser will open automatically at:

### 🌐 **http://localhost:8501**

---

## 📋 What Happens Next

1. **Browser opens** → You see the BIOCANVAS welcome screen
2. **Click "START BIOCANVAS"** → Backend launches automatically (3 seconds)
3. **Select protein & ligand** → From the sidebar dropdowns
4. **View 3D structure** → AlphaFold protein visualization
5. **Run docking simulation** → Click the big button
6. **See results** → Binding score, strength, and biological explanation

---

## 🎯 Features

- ✅ **10 Curated Proteins** with real UniProt IDs
- ✅ **10 Biologically Relevant Ligands**
- ✅ **3D Protein Visualization** via AlphaFold
- ✅ **Educational Docking Engine** with instant results
- ✅ **Biologically Accurate Pairs**:
  - Hemoglobin + Heme B (Strong: -11.5 kcal/mol)
  - EGFR + Gefitinib (Strong: -9.8 kcal/mol)
  - Amylase + Glucose (Moderate: -6.2 kcal/mol)

---

## 🛑 To Stop

Press `Ctrl + C` in the terminal, or click **"STOP BIOCANVAS"** in the sidebar.

---

## 📁 Project Structure

```
BIOCANVAS/
├── app.py                  # Main unified application
├── backend/
│   ├── main.py            # FastAPI backend
│   └── docking_engine.py  # Docking simulation logic
├── data/
│   ├── proteins.json      # 10 proteins with UniProt IDs
│   └── ligands.json       # 10 ligands
├── frontend/
│   └── app.py            # Alternative frontend (standalone)
└── requirements.txt       # All dependencies
```

---

## 🔧 Manual Setup (Optional)

If you prefer manual control:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run app.py
```

---

## 💡 Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **3D Visualization**: py3Dmol + stmol
- **Data**: AlphaFold Protein Database
- **Language**: Python 3.10+

---

## 📊 Test the System

```bash
python3 test_system.py
```

---

## 👨‍💻 Developer

Built with ❤️ for bioinformatics education

**Version**: 1.0.0  
**Status**: Production Ready ✅
