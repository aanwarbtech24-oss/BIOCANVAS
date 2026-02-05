import json
import os
import requests  # type: ignore
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel  # type: ignore
from backend.docking_engine import calculate_docking
from functools import lru_cache

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
    pubchem_cid: int

class DockingRequest(BaseModel):
    protein_id: int
    ligand_id: int

# Data Loading Helper with caching
@lru_cache(maxsize=128)
def load_data(filename: str) -> List[Dict[str, Any]]:
    """Load JSON data from the data/ folder with caching for performance."""
    try:
        # Construct absolute path to data folder (one level up from backend/)
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", filename)
        with open(data_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# API Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint for backend readiness."""
    return {"status": "healthy", "service": "BIOCANVAS API"}

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
        api_response = requests.get(
            f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}", 
            timeout=10
        )
        if api_response.status_code == 200:
            data = api_response.json()[0]
            latest_version = data['latestVersion']
            pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v{latest_version}.pdb"
            
            # Verify URL is accessible
            verify_response = requests.head(pdb_url, timeout=5)
            if verify_response.status_code != 200:
                raise Exception("PDB file not accessible")
        else:
            # Fallback to v4 and verify
            pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
            verify_response = requests.head(pdb_url, timeout=5)
            if verify_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Structure not found")
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        # Final fallback to v4
        pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    
    return {"uniprot_id": uniprot_id, "pdb_url": pdb_url}

@app.post("/dock")
def dock_protein_ligand(request: DockingRequest) -> Dict[str, Any]:
    """Performs educational docking simulation between a protein and ligand."""
    return calculate_docking(request.protein_id, request.ligand_id)

@app.get("/ligand-structure/{cid}")
def get_ligand_structure(cid: int) -> Dict[str, str]:
    """
    Fetches 3D coordinates (SDF format) for ligand visualization from PubChem.
    Returns the raw SDF data containing atomic positions and bonds.
    """
    # Construct PubChem API URL for 3D structure
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
    
    try:
        # Fetch data from PubChem
        response = requests.get(url, timeout=10)
        
        # Validate response
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, 
                detail=f"Structure not found in PubChem for CID {cid}"
            )
        
        # Return SDF data
        return {"sdf_data": response.text}
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504, 
            detail="PubChem request timed out"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, 
            detail=f"PubChem service unavailable: {str(e)}"
        )
