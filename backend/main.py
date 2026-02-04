import json
import os
import requests
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.docking_engine import calculate_docking

# Initialize FastAPI app
app = FastAPI(title="BIOCANVAS API")

# Configure CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Protein(BaseModel):
    id: int
    name: str
    uniprot_id: str
    function: str
    category: str

class Ligand(BaseModel):
    id: int
    name: str
    type: str
    description: str

class DockingRequest(BaseModel):
    protein_id: int
    ligand_id: int

# Data Loading Helper
def load_data(filename: str) -> List[Dict[str, Any]]:
    """Load JSON data from the data/ folder with error handling."""
    try:
        # Construct absolute path to data folder (one level up from backend/)
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", filename)
        with open(data_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# API Endpoints
@app.get("/proteins", response_model=List[Protein])
def get_proteins():
    """Returns the curated list of proteins available for docking."""
    return load_data("proteins.json")

@app.get("/ligands", response_model=List[Ligand])
def get_ligands():
    """Returns the library of small molecule ligands."""
    return load_data("ligands.json")

@app.get("/structure/{uniprot_id}")
def get_structure(uniprot_id: str) -> Dict[str, str]:
    """Generates the direct download link for the AlphaFold 3D structure."""
    try:
        # Query AlphaFold API to get latest version
        api_response = requests.get(f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}", timeout=10)
        if api_response.status_code == 200:
            data = api_response.json()[0]
            latest_version = data['latestVersion']
            pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v{latest_version}.pdb"
        else:
            # Fallback to v4 if API fails
            pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    except:
        # Fallback to v4 if API fails
        pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    
    return {"uniprot_id": uniprot_id, "pdb_url": pdb_url}

@app.post("/dock")
def dock_protein_ligand(request: DockingRequest) -> Dict[str, Any]:
    """Performs educational docking simulation between a protein and ligand."""
    return calculate_docking(request.protein_id, request.ligand_id)
