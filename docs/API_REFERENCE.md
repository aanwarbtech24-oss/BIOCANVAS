# 🌐 BIOCANVAS API Reference

## Overview
FastAPI server running on `http://localhost:8000`

## Base URL
```
http://localhost:8000
```

## Documentation
- **Swagger UI**: http://localhost:8000/docs (interactive)
- **ReDoc**: http://localhost:8000/redoc (static)

---

## 📋 Endpoints

### Health & Status

#### GET /health
Check API server status
```bash
curl http://localhost:8000/health
```
**Response**:
```json
{
  "status": "active",
  "engine": "ready"
}
```

#### GET /
Get API information
```bash
curl http://localhost:8000/
```
**Response**:
```json
{
  "name": "BIOCANVAS API",
  "version": "2.0.0",
  "status": "production"
}
```

---

### Job Management

#### POST /jobs
Submit a new docking job
```bash
curl -X POST http://localhost:8000/jobs \
  -F "protein=@protein.pdb" \
  -F "ligand_smiles=CC(C)Cc1ccc(cc1)C"
```

**Parameters**:
- `protein` (file): PDB protein structure file
- `ligand_smiles` (string): SMILES string of ligand
- `search_box` (optional): Custom search box coordinates

**Response**:
```json
{
  "job_id": "job_12345",
  "status": "queued",
  "created_at": "2026-02-20T12:00:00Z"
}
```

#### GET /jobs/{job_id}
Get job status and results
```bash
curl http://localhost:8000/jobs/job_12345
```

**Response**:
```json
{
  "job_id": "job_12345",
  "status": "completed",
  "binding_affinity": "-7.5",
  "ligand_pose": "results/job_12345/ligand.pdb",
  "created_at": "2026-02-20T12:00:00Z",
  "completed_at": "2026-02-20T12:05:30Z"
}
```

#### GET /jobs
List all jobs
```bash
curl http://localhost:8000/jobs
```

---

### File Download

#### GET /results/{path}
Download docking result files
```bash
curl http://localhost:8000/results/job_12345/ligand.pdb
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid SMILES string"
}
```

### 404 Not Found
```json
{
  "detail": "Job not found"
}
```

### 500 Server Error
```json
{
  "detail": "Error during docking calculation"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request |
| 404 | Not found |
| 500 | Server error |

---

## Data Models

### Job Status
- `queued` - Waiting in queue
- `in_progress` - Currently processing
- `completed` - Finished successfully
- `failed` - Error occurred

### File Formats
- **Protein**: PDB format (`.pdb`)
- **Ligand**: SMILES string or SDF/MOL files
- **Results**: PDB, SDF, or PDBQT formats
