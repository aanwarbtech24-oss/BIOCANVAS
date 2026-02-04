import streamlit as st  # type: ignore
import requests  # type: ignore
import py3Dmol  # type: ignore
from stmol import showmol  # type: ignore

# Page Configuration
st.set_page_config(page_title="BIOCANVAS", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🧬 BIOCANVAS")
st.markdown("### Educational End-to-End Drug Discovery Pipeline")
st.divider()

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# Sidebar: Control Panel
st.sidebar.header("🎛️ Control Panel")

try:
    # Fetch proteins and ligands from backend
    proteins_response = requests.get(f"{API_URL}/proteins", timeout=5)
    ligands_response = requests.get(f"{API_URL}/ligands", timeout=5)
    
    proteins = proteins_response.json()
    ligands = ligands_response.json()
    
    # Protein selection
    protein_options = {f"{p['name']} ({p['uniprot_id']})": p for p in proteins}
    selected_protein_key = st.sidebar.selectbox("Select Protein", list(protein_options.keys()))
    selected_protein = protein_options[selected_protein_key]
    
    # Ligand selection
    ligand_options = {f"{l['name']} ({l['type']})": l for l in ligands}
    selected_ligand_key = st.sidebar.selectbox("Select Ligand", list(ligand_options.keys()))
    selected_ligand = ligand_options[selected_ligand_key]
    
    backend_online = True
    
except requests.exceptions.RequestException:
    st.sidebar.error("⚠️ Backend is offline. Please run uvicorn.")
    backend_online = False

# Main Area: 3D Visualization
if backend_online:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔬 3D Protein Structure")
        
        try:
            # Get AlphaFold PDB URL
            structure_response = requests.get(f"{API_URL}/structure/{selected_protein['uniprot_id']}")
            pdb_url = structure_response.json()["pdb_url"]
            
            # Fetch PDB content
            pdb_response = requests.get(pdb_url)
            pdb_content = pdb_response.text
            
            # Create 3D viewer
            view = py3Dmol.view(width=800, height=500)
            view.addModel(pdb_content, "pdb")
            view.setStyle({'cartoon': {'color': 'spectrum'}})
            view.zoomTo()
            
            # Render
            showmol(view, height=500, width=800)
            
        except Exception as e:
            st.error(f"Could not load 3D structure: {str(e)}")
    
    with col2:
        st.subheader("📋 Protein Details")
        st.markdown(f"**Name:** {selected_protein['name']}")
        st.markdown(f"**UniProt ID:** {selected_protein['uniprot_id']}")
        st.markdown(f"**Category:** {selected_protein['category']}")
        st.markdown(f"**Function:** {selected_protein['function']}")
        
        st.divider()
        
        st.subheader("💊 Ligand Details")
        st.markdown(f"**Name:** {selected_ligand['name']}")
        st.markdown(f"**Type:** {selected_ligand['type']}")
        st.markdown(f"**Description:** {selected_ligand['description']}")
    
    st.divider()
    
    # Action: Run Docking Simulation
    if st.button("🚀 Run Educational Docking Simulation", type="primary", use_container_width=True):
        with st.spinner("⚗️ Simulating interaction parameters..."):
            try:
                # Send POST request to docking endpoint
                docking_response = requests.post(
                    f"{API_URL}/dock",
                    json={"protein_id": selected_protein["id"], "ligand_id": selected_ligand["id"]}
                )
                result = docking_response.json()
                
                # Result Display Dashboard
                st.success("✅ Docking Simulation Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("⚡ Interaction Score", f"{result['score']} kcal/mol")
                
                with col2:
                    strength = result['strength']
                    if "Strong" in strength:
                        st.success(f"💪 {strength}")
                    elif "Moderate" in strength:
                        st.info(f"🔵 {strength}")
                    else:
                        st.warning(f"⚠️ {strength}")
                
                with col3:
                    st.info("📊 Binding Strength")
                
                st.divider()
                st.subheader("🧠 Biological Explanation")
                st.write(result['message'])
                
            except Exception as e:
                st.error(f"Docking simulation failed: {str(e)}")
