import random

def calculate_docking(protein_id: int, ligand_id: int) -> dict:
    """
    Educational docking simulation that returns instant feedback based on
    biologically accurate protein-ligand interactions.
    """
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
    
    # Case D: Default (any other combination)
    else:
        return {
            "score": round(random.uniform(-4.5, -3.0), 1),
            "strength": "Weak Binding",
            "message": "Low complementarity. The shape and chemical properties do not match well.",
            "success": True
        }
