# 🚀 BIOCANVAS v2.0 - React Frontend Development Guide
## Quick Start for Prompt Engineer

---

## 📌 BEFORE YOU START

The backend is **100% complete and tested**. Your job is building the React UI.

### Get Server Running (2 commands)
```bash
cd /Users/atifanwar/Desktop/BIOCANVAS
python3 run.py
```
Server will start on `http://localhost:8000` with docs at `/docs`

---

## 🔌 API CONTRACT (What You'll Call)

### Endpoint 1: Submit Docking Job
```javascript
// POST /dock
const submitDocking = async (proteinFile, smilesString) => {
  const formData = new FormData();
  formData.append('protein_file', proteinFile);
  formData.append('ligand_smiles', smilesString);
  formData.append('box_padding', 10.0); // Optional
  
  const response = await fetch('http://localhost:8000/dock', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.job_id; // "550e8400-e29b-41d4-a716-..."
};
```

### Endpoint 2: Check Job Status & Get Results
```javascript
// GET /jobs/{job_id}
const getJobStatus = async (jobId) => {
  const response = await fetch(`http://localhost:8000/jobs/${jobId}`);
  return await response.json();
};

// Response when running:
// { job_id: "...", status: "running", message: "..." }

// Response when done:
// {
//   job_id: "...",
//   status: "completed",
//   affinity: -7.5,
//   rmsd: 2.3,
//   poses: 1,
//   receptor_pdbqt: "path/...",
//   ligand_pdbqt: "path/...",
//   output_pdbqt: "path/...",
//   duration: 45.2
// }
```

### Endpoint 3: Health Check
```javascript
// GET /health (useful for loading states)
const checkHealth = async () => {
  const response = await fetch('http://localhost:8000/health');
  return await response.json();
};
// { status: "active", engine: "ready", timestamp: ..., jobs_running: 0 }
```

### Endpoint 4: App Info
```javascript
// GET / (for footer/about section)
const getAppInfo = async () => {
  const response = await fetch('http://localhost:8000/');
  return await response.json();
};
// { title: "BIOCANVAS v2.0", version: "2.0.0", ... }
```

---

## 🎯 TYPICAL USER WORKFLOW

```
User clicks "Upload & Dock"
       ↓
[Upload Dialog] → Select PDB file
[SMILES Input] → Type/paste SMILES string
[Submit Button] → POST /dock
       ↓
Server returns: { job_id: "uuid-1234" }
       ↓
React polls: GET /jobs/uuid-1234 (every 2 seconds)
       ↓
Status responses:
  queued → "Processing..."
  running → "Running docking (phase 2/4)..."
  completed → Show results
  failed → Show error
       ↓
Results page displays:
  ✅ Binding affinity: -7.5 kcal/mol
  ✅ RMSD: 2.3 Å
  ✅ Search space: centered at (x,y,z), size (sx,sy,sz)
  ✅ Download buttons for PDBQT files
  ✅ 3D viewer with protein + ligand
```

---

## 📂 REACT PROJECT STRUCTURE (Recommendation)

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx              [Logo, title, status lights]
│   │   ├── UploadForm.jsx          [File + SMILES input]
│   │   ├── JobCard.jsx             [Single job in list]
│   │   ├── JobList.jsx             [Recent jobs history]
│   │   ├── Results.jsx             [Affinity, RMSD, downloads]
│   │   ├── MolecularViewer.jsx     [3D structure viewer]
│   │   ├── StatusBadge.jsx         [queued|running|completed|failed]
│   │   ├── LoadingSpinner.jsx      [Progress indicator]
│   │   └── ErrorAlert.jsx          [Error messages]
│   ├── pages/
│   │   ├── HomePage.jsx            [Main dock interface]
│   │   ├── JobDashboard.jsx        [View job history]
│   │   └── ResultsPage.jsx         [Full results view]
│   ├── services/
│   │   ├── api.js                  [Fetch wrappers]
│   │   ├── dockingService.js       [POST /dock logic]
│   │   └── jobService.js           [GET /jobs polling logic]
│   ├── hooks/
│   │   ├── useDocking.js           [Custom hook for submission]
│   │   ├── useJobStatus.js         [Custom hook for polling]
│   │   └── useAPI.js               [Generic fetch hook]
│   ├── context/
│   │   ├── AppContext.js           [Global app state]
│   │   ├── JobContext.js           [Job state management]
│   │   └── AuthContext.js          [(future) If auth needed]
│   ├── App.jsx                     [Main component]
│   ├── App.css                     [Global styles]
│   ├── main.jsx                    [React entry point]
│   └── index.css                   [Global CSS]
├── public/
│   ├── logo.svg
│   ├── favicon.ico
│   └── [Static assets]
├── package.json
├── vite.config.js                  [If using Vite]
└── .env                            [VITE_API_URL=http://localhost:8000]
```

---

## 🛠️ TECH STACK RECOMMENDATION

### Core
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0"
}
```

### State Management (Pick ONE)
```json
{
  "react-query": "^3.39.0",          // For server state (RECOMMENDED)
  "zustand": "^4.3.8",               // For client state
  "axios": "^1.4.0"                  // For HTTP calls (or use fetch)
}
```

### UI Framework (Pick ONE)
```json
{
  "@mui/material": "^5.13.0",        // Full featured material design
  "@chakra-ui/react": "^2.8.0",      // Very accessible + pretty
  "tailwindcss": "^3.3.0"            // Utility-first CSS
}
```

### Molecular Visualization (Pick ONE)
```json
{
  "py3dmol": "^0.8.0",               // Lightweight, easy integration
  "molstar": "^3.30.0",              // Advanced, professional
  "nglviewer": "^2.0.0"              // Standard PDB viewer
}
```

### Form & Validation
```json
{
  "react-hook-form": "^7.45.0",
  "zod": "^3.21.0"                   // Lightweight validation
}
```

### Build Tool
```json
{
  "vite": "^4.3.9"                   // Lightning fast dev server
}
```

**Sample package.json:**
```json
{
  "name": "biocanvas-frontend",
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-query": "^3.39.0",
    "@mui/material": "^5.13.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "py3dmol": "^0.8.0",
    "react-hook-form": "^7.45.0",
    "axios": "^1.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.3.9"
  }
}
```

---

## 💻 KEY COMPONENTS TO BUILD

### 1. UploadForm Component (FIRST)
```javascript
// Features:
// - File picker for PDB
// - Text input for SMILES
// - Submit button
// - Input validation
// - Show errors

function UploadForm({ onSubmit }) {
  const [proteinFile, setProteinFile] = useState(null);
  const [smiles, setSmiles] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Call: POST /dock
      const jobId = await onSubmit(proteinFile, smiles);
      // Navigate to job page
      window.location.href = `/jobs/${jobId}`;
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="file" 
        accept=".pdb"
        onChange={(e) => setProteinFile(e.target.files[0])}
        required
      />
      <input 
        type="text"
        placeholder="Enter SMILES (e.g., CC(=O)Oc1ccccc1C(=O)O)"
        value={smiles}
        onChange={(e) => setSmiles(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Dock Ligand'}
      </button>
      {error && <ErrorAlert message={error} />}
    </form>
  );
}
```

### 2. JobStatus Component (SECOND)
```javascript
// Features:
// - Display current status (queued|running|completed|failed)
// - Poll GET /jobs/{job_id} every 2 seconds
// - Show progress percentage
// - Display error messages

function JobStatus({ jobId }) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`/jobs/${jobId}`);
        const data = await response.json();
        setJob(data);
        
        // Stop polling if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          setLoading(false);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };
    
    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId]);
  
  if (!job) return <div>Loading...</div>;
  
  return (
    <div>
      <StatusBadge status={job.status} />
      {job.status === 'running' && <ProgressBar />}
      {job.status === 'completed' && <ResultsDisplay job={job} />}
      {job.status === 'failed' && <ErrorAlert message={job.error} />}
    </div>
  );
}
```

### 3. ResultsDisplay Component (THIRD)
```javascript
// Features:
// - Show binding affinity
// - Show RMSD values
// - Download buttons for PDBQT files
// - Display 3D molecular structure

function ResultsDisplay({ job }) {
  return (
    <div className="results-panel">
      <div className="metrics">
        <MetricCard 
          label="Binding Affinity" 
          value={`${job.affinity} kcal/mol`}
        />
        <MetricCard 
          label="RMSD" 
          value={`${job.rmsd} Å`}
        />
      </div>
      
      <div className="downloads">
        <DownloadButton 
          href={`/docking_jobs/${job.output_pdbqt}`}
          label="Poses (PDBQT)"
        />
        <DownloadButton 
          href={`/docking_jobs/${job.receptor_pdbqt}`}
          label="Receptor (PDBQT)"
        />
        <DownloadButton 
          href={`/docking_jobs/${job.ligand_pdbqt}`}
          label="Ligand (PDBQT)"
        />
      </div>
      
      <MolecularViewer 
        protein={job.receptor_pdbqt}
        ligand={job.ligand_pdbqt}
      />
    </div>
  );
}
```

### 4. MolecularViewer Component (OPTIONAL but cool)
```javascript
// Uses py3dmol or molstar to display 3D structures

import { useEffect, useRef } from 'react';

function MolecularViewer({ protein, ligand }) {
  const viewerRef = useRef(null);
  
  useEffect(() => {
    if (!viewerRef.current || !protein) return;
    
    // Initialize 3D viewer
    const viewer = window.py3Dmol.createViewer(
      viewerRef.current,
      { backgroundColor: 'white' }
    );
    
    // Load protein structure
    fetch(`/docking_jobs/${protein}`)
      .then(r => r.text())
      .then(data => {
        viewer.addModel(data, 'pdbqt');
        viewer.setStyle({cartoon: {color: 'spectrum'}});
        viewer.zoomTo();
        viewer.render();
      });
  }, [protein]);
  
  return <div ref={viewerRef} style={{ width: '100%', height: '500px' }} />;
}
```

---

## 🔄 POLLING PATTERN (Job Status)

```javascript
// Best practice for checking job status:

const useJobPolling = (jobId, interval = 2000) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (!jobId) return;
    
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/jobs/${jobId}`);
        
        if (!response.ok) throw new Error('Failed to fetch job status');
        
        const data = await response.json();
        setJob(data);
        
        // Stop polling when complete
        if (['completed', 'failed'].includes(data.status)) {
          setLoading(false);
        }
      } catch (err) {
        setError(err.message);
      }
    };
    
    // Poll immediately
    poll();
    
    // Then set up interval
    const intervalId = setInterval(poll, interval);
    
    return () => clearInterval(intervalId);
  }, [jobId, interval]);
  
  return { job, loading, error };
};

// Usage:
const { job, loading } = useJobPolling(jobId);
if (loading) return <Spinner />;
if (job.status === 'completed') return <Results job={job} />;
```

---

## 🎨 UI/UX RECOMMENDATIONS

### Color Scheme
```css
/* Status colors */
--color-queued: #9CA3AF (gray)
--color-running: #3B82F6 (blue)
--color-completed: #10B981 (green)
--color-failed: #EF4444 (red)
--color-warning: #F59E0B (amber)

/* Primary colors */
--primary: #0EA5E9 (sky blue)
--secondary: #8B5CF6 (purple)
--background: #F9FAFB (light gray)
--surface: #FFFFFF (white)
```

### Status Badge Examples
```
🟡 Queued     [Gray background, spinning dots]
🔵 Running    [Blue background, progress bar]
🟢 Completed  [Green background, checkmark]
🔴 Failed     [Red background, X icon]
```

### Progress Indicators
```
While Running:
│████░░░░░░│ Phase 2/4: Ligand Preparation
Time Elapsed: 12s / Est. 45s remaining

When Hovering Job Card:
╔════════════════════════════════════╗
║ Job ID: 550e8400-e29b-41d4...      ║
║ Status: Running 🔵                 ║
║ Started: 12:45:30 PM               ║
║ [View Details] [Cancel] [Favorite] ║
╚════════════════════════════════════╝
```

---

## 🚨 ERROR HANDLING

Common errors you'll encounter:

```javascript
// Error: File validation failed
if (!proteinFile.name.endsWith('.pdb')) {
  throw new Error('Please upload a valid PDB file');
}

// Error: Invalid SMILES string
if (!smiles.match(/^[A-Za-z0-9()[\]\\/@#%+=-]+$/)) {
  throw new Error('Invalid SMILES format');
}

// Error: Server not running
if (response.status === 503) {
  return 'Backend server is not running. Start with: python3 run.py';
}

// Error: Job not found
if (response.status === 404) {
  return `Job ${jobId} not found. Please submit a new docking job.`;
}

// Error: File too large
if (proteinFile.size > 5 * 1024 * 1024) { // 5MB limit
  throw new Error('Protein file must be less than 5MB');
}
```

---

## 📚 TESTING CHECKLIST

Before submitting code:

- [ ] Upload form accepts PDB files only
- [ ] SMILES validation prevents invalid entries
- [ ] Job submission returns job_id
- [ ] Job polling updates status every 2 seconds
- [ ] Results display when status = "completed"
- [ ] Download buttons work for all PDBQT files
- [ ] Error messages clear and helpful
- [ ] Responsive design on mobile & desktop
- [ ] No console warnings or errors
- [ ] Loading states smooth and clear
- [ ] Job history persists across page refresh
- [ ] API calls use correct endpoints

---

## 🔗 USEFUL RESOURCES

**Testing the API Directly:**
```bash
# While server is running:

# 1. Check health
curl http://localhost:8000/health

# 2. Try a docking job manually
curl -X POST http://localhost:8000/dock \
  -F "protein_file=@/path/to/protein.pdb" \
  -F "ligand_smiles=CC(=O)Oc1ccccc1C(=O)O"

# 3. Check job status
curl http://localhost:8000/jobs/{job_id}
```

**Sample PDB Files for Testing:**
```
Many available at:
- PDB.org (https://www.rcsb.org/)
- Example: 4lzg (small protein, ~50KB)

Sample SMILES strings:
- Aspirin: CC(=O)Oc1ccccc1C(=O)O
- Caffeine: CN1C=NC2=C1C(=O)N(C(=O)N2C)C
- Ethanol: CCO
```

---

## 🎯 DEVELOPMENT PHASES

### Phase 1 (MVP - Week 1-2)
- [ ] Setup React + Vite
- [ ] Build upload form
- [ ] Implement job submission
- [ ] Setup job polling
- [ ] Display results (text only)

### Phase 2 (Enhancement - Week 3)
- [ ] Add 3D molecular viewer
- [ ] Improve UI/styling
- [ ] Job history list
- [ ] Batch operations

### Phase 3 (Polish - Week 4)
- [ ] Advanced options form
- [ ] Export to PDF reports
- [ ] Comparison tools
- [ ] Dark mode
- [ ] Mobile optimization

---

## 📞 QUESTIONS?

Refer back to:
1. **API Documentation**: http://localhost:8000/docs
2. **DEVELOPMENT_SUMMARY.md** - Full details on backend
3. **FIX_SUMMARY.md** - What was fixed
4. **STATUS_READY.txt** - Current system status

---

**Good luck building! The backend is solid. Focus on UX.** 🚀

