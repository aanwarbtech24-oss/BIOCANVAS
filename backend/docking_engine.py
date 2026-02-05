import random

def calculate_docking(protein_id: int, ligand_id: int, seed: int = None) -> dict:
    """
    Educational docking simulation that returns instant feedback based on
    biologically accurate protein-ligand interactions.
    
    Args:
        protein_id: ID of the protein
        ligand_id: ID of the ligand
        seed: Optional random seed for reproducible results (testing)
    """
    if seed is not None:
        random.seed(seed)
    
    # Case A: Hemoglobin + Heme B
    if protein_id == 1 and ligand_id == 1:
        return {
            "score": -11.5,
            "strength": "Strong Binding",
            "message": "Excellent! Heme is the natural cofactor that binds to Hemoglobin to transport oxygen.",
            "success": True
        }
    
    # Case B: EGFR + Gefitinib
    elif protein_id == 7 and ligand_id == 10:
        return {
            "score": -9.8,
            "strength": "Strong Binding",
            "message": "High affinity! Gefitinib effectively inhibits the EGFR tyrosine kinase domain.",
            "success": True
        }
    
    # Case C: Pancreatic Alpha-Amylase + Glucose
    elif protein_id == 10 and ligand_id == 2:
        return {
            "score": -6.2,
            "strength": "Moderate Binding",
            "message": "Moderate interaction. Glucose is the breakdown product of starch, which Amylase acts upon.",
            "success": True
        }
    
    # Case D: Insulin + Glucose
    elif protein_id == 2 and ligand_id == 2:
        return {
            "score": -7.1,
            "strength": "Moderate Binding",
            "message": "Moderate affinity. Insulin regulates glucose metabolism in cells.",
            "success": True
        }
    
    # Case E: Lysozyme + Penicillin
    elif protein_id == 4 and ligand_id == 7:
        return {
            "score": -5.8,
            "strength": "Moderate Binding",
            "message": "Moderate interaction. Both target bacterial cell walls through different mechanisms.",
            "success": True
        }
    
    # Case F: Default (any other combination)
    else:
        return {
            "score": round(random.uniform(-4.5, -3.0), 1),
            "strength": "Weak Binding",
            "message": "Low complementarity. The shape and chemical properties do not match well.",
            "success": True
        }
