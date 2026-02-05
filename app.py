import streamlit as st  # type: ignore
import requests  # type: ignore
import py3Dmol  # type: ignore
from stmol import showmol  # type: ignore
import subprocess
import time
import sys
import os

# Page Configuration
st.set_page_config(page_title="BIOCANVAS", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'backend_started' not in st.session_state:
    st.session_state.backend_started = False
    st.session_state.backend_process = None

# Header
st.title("🧬 BIOCANVAS v1.5")
st.markdown("### Educational End-to-End Drug Discovery Pipeline - Dual Visualization")
st.divider()

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# START Button
if not st.session_state.backend_started:
    st.info("👋 Welcome! Click START to launch the application.")
    if st.button("🚀 START BIOCANVAS", type="primary", use_container_width=True):
        with st.spinner("🔧 Starting backend services..."):
            backend_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "backend.main:app", 
                 "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            st.session_state.backend_process = backend_process
            
            # Poll backend health instead of fixed sleep
            max_attempts = 15
            for attempt in range(max_attempts):
                time.sleep(0.5)
                try:
                    response = requests.get(f"{API_URL}/health", timeout=1)
                    if response.status_code == 200:
                        break
                except:
                    if attempt == max_attempts - 1:
                        st.error("Backend failed to start")
                        backend_process.kill()
                        st.stop()
            
            st.session_state.backend_started = True
            st.rerun()
    st.stop()

# Sidebar: Control Panel
st.sidebar.header("🎛️ Control Panel")

if st.sidebar.button("🛑 STOP BIOCANVAS", type="secondary"):
    if st.session_state.backend_process:
        st.session_state.backend_process.terminate()
        time.sleep(1)
        if st.session_state.backend_process.poll() is None:
            st.session_state.backend_process.kill()
    st.session_state.backend_started = False
    st.rerun()

@st.cache_data(ttl=300)
def fetch_proteins():
    response = requests.get(f"{API_URL}/proteins", timeout=5)
    return response.json()

@st.cache_data(ttl=300)
def fetch_ligands():
    response = requests.get(f"{API_URL}/ligands", timeout=5)
    return response.json()

try:
    proteins = fetch_proteins()
    ligands = fetch_ligands()
    
    protein_options = {f"{p['name']} ({p['uniprot_id']})": p for p in proteins}
    selected_protein_key = st.sidebar.selectbox("Select Protein", list(protein_options.keys()))
    selected_protein = protein_options[selected_protein_key]
    
    ligand_options = {f"{l['name']} ({l['type']})": l for l in ligands}
    selected_ligand_key = st.sidebar.selectbox("Select Ligand", list(ligand_options.keys()))
    selected_ligand = ligand_options[selected_ligand_key]
    
    backend_online = True
    
except requests.exceptions.RequestException:
    st.sidebar.error("⚠️ Backend connection lost. Please restart.")
    backend_online = False

# Main Area: Dual 3D Visualization
if backend_online:
    st.subheader("🔬 Dual 3D Molecular Visualization")
    
    # Top: Dual 3D Viewers
    viewer_col1, viewer_col2 = st.columns(2)
    
    # Left: Protein Viewer
    with viewer_col1:
        st.markdown("#### 🧬 Protein Structure")
        with st.spinner("Loading protein from AlphaFold..."):
            try:
                structure_response = requests.get(f"{API_URL}/structure/{selected_protein['uniprot_id']}")
                pdb_url = structure_response.json()["pdb_url"]
                pdb_response = requests.get(pdb_url, timeout=30)
                
                if pdb_response.status_code == 200 and len(pdb_response.text) > 100:
                    view = py3Dmol.view(width=450, height=400)
                    view.addModel(pdb_response.text, "pdb")
                    view.setStyle({'cartoon': {'color': 'spectrum'}})
                    view.zoomTo()
                    showmol(view, height=400, width=450)
                    st.success("✅ Protein loaded")
                else:
                    st.error("❌ Protein structure unavailable")
            except Exception as e:
                st.error(f"❌ Error: {str(e)[:50]}")
    
    # Right: Ligand Viewer (NEW in v1.5)
    with viewer_col2:
        st.markdown("#### 💊 Ligand Structure")
        with st.spinner("Loading ligand from PubChem..."):
            try:
                ligand_response = requests.get(
                    f"{API_URL}/ligand-structure/{selected_ligand['pubchem_cid']}",
                    timeout=30
                )
                if ligand_response.status_code == 200:
                    sdf_data = ligand_response.json()["sdf_data"]
                    view = py3Dmol.view(width=450, height=400)
                    view.addModel(sdf_data, "sdf")
                    view.setStyle({'stick': {'colorscheme': 'Jmol'}})
                    view.zoomTo()
                    showmol(view, height=400, width=450)
                    st.success("✅ Ligand loaded")
                else:
                    st.error(f"❌ Ligand unavailable (CID: {selected_ligand['pubchem_cid']})")
            except Exception as e:
                st.error(f"❌ Error: {str(e)[:50]}")
    
    st.divider()
    
    # Bottom: Details
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("#### 📋 Protein Information")
        st.markdown(f"**Name:** {selected_protein['name']}")
        st.markdown(f"**UniProt ID:** {selected_protein['uniprot_id']}")
        st.markdown(f"**Category:** {selected_protein['category']}")
        st.markdown(f"**Function:** {selected_protein['function']}")
    
    with detail_col2:
        st.markdown("#### 💊 Ligand Information")
        st.markdown(f"**Name:** {selected_ligand['name']}")
        st.markdown(f"**PubChem CID:** {selected_ligand['pubchem_cid']}")
        st.markdown(f"**Type:** {selected_ligand['type']}")
        st.markdown(f"**Description:** {selected_ligand['description']}")
    
    st.divider()
    
    # Action: Run Docking Simulation
    if st.button("🚀 Run Educational Docking Simulation", type="primary", use_container_width=True):
        with st.spinner("⚗️ Simulating interaction parameters..."):
            try:
                docking_response = requests.post(
                    f"{API_URL}/dock",
                    json={"protein_id": selected_protein["id"], "ligand_id": selected_ligand["id"]}
                )
                result = docking_response.json()
                
                st.success("✅ Docking Simulation Complete!")
                
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.metric("⚡ Interaction Score", f"{result['score']} kcal/mol")
                
                with result_col2:
                    strength = result['strength']
                    if "Strong" in strength:
                        st.success(f"💪 {strength}")
                    elif "Moderate" in strength:
                        st.info(f"🔵 {strength}")
                    else:
                        st.warning(f"⚠️ {strength}")
                
                with result_col3:
                    st.info("📊 Binding Strength")
                
                st.divider()
                st.subheader("🧠 Biological Explanation")
                st.write(result['message'])
                
            except Exception as e:
                st.error(f"Docking simulation failed: {str(e)}")
