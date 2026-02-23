# 🧬 BIOCANVAS v2.0 - Frontend

Modern, type-safe React + Vite frontend for molecular docking visualization and job management.

## 🎯 Quick Start

### Prerequisites
- Node.js 18+ (LTS recommended)
- Backend running on `http://127.0.0.1:8000`

### Setup (One Command)
```bash
cd frontend
bash setup.sh
```

Or manually:
```bash
cd frontend
npm install
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

---

## 📋 Architecture Overview

### Phase 1: Foundation ✅
- **Vite + React 18 + TypeScript (SWC)**
- **TailwindCSS** with custom "Deep Science" theme
- **Atomic components** (Button, Card, Input, Badge, Badge, Loader)
- **Layout system** (Navbar, Sidebar, PageContainer)

### Phase 2: Smart Logic ✅
- **Axios** with global error interceptors → Sonner toasts
- **Zod** schemas for runtime validation
- **Zustand** stores (UI state + Docking state)
- **@tanstack/react-query** with smart polling

### Phase 3: API Integration ✅
- **src/lib/axios.ts** - Singleton Axios instance with interceptors
- **src/types/api.ts** - Zod schemas for all API responses
- **src/hooks/useDockingJob.ts** - React Query hooks with polling strategy
- Error handling with global toast notifications

### Phase 4: App Shell ✅
- **App.tsx** - Main orchestrator with tab-based navigation
- **Sidebar** - Job history + System status
- **Main canvas** - Dynamic content based on active tab
- **Code splitting** - Lazy load 3D viewer (Suspense + React.lazy)
- **Global Toaster** - Sonner for error/success notifications

---

## 📁 Project Structure

```
src/
├── assets/              # Static images & icons
├── components/
│   ├── ui/             # Atomic components (reusable, no business logic)
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Loader.tsx
│   │   └── LoadingSpinner.tsx
│   ├── layout/         # Layout wrappers
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── PageContainer.tsx
│   ├── features/       # Business logic components
│   │   ├── DockingForm.tsx       # Upload interface
│   │   ├── JobStatus.tsx         # Job polling & results
│   │   └── JobHistory.tsx        # Recent jobs list
│   └── science/        # Science-specific components
│       └── Viewer3D.tsx          # Molecular visualization (lazy-loaded)
├── hooks/              # Custom React hooks
│   ├── useQuery.ts     # React Query wrapper
│   └── useDockingJob.ts # Docking-specific hooks
├── lib/
│   ├── axios.ts        # Axios singleton with interceptors
│   ├── cn.ts           # Tailwind class merger
│   └── validators.ts   # Input validation (Zod)
├── stores/             # Zustand stores
│   ├── useUIStore.ts   # UI state (activeTab, sidebarOpen, etc)
│   └── useDockingStore.ts # Docking state (jobs, activeJobId, etc)
├── types/
│   ├── index.ts        # App-specific types
│   └── api.ts          # Zod schemas for API responses
├── App.tsx             # Root component with tab navigation
├── main.tsx            # React entry point
├── index.css           # Global styles (Tailwind)
└── vite-env.d.ts       # Vite environment types
```

---

## 🔌 API Integration

### Endpoints Used

```typescript
// Health Check (every 10 seconds)
GET /health
Response: { status: "active", engine: "ready", jobs_running: 0 }

// Submit Docking Job
POST /dock (multipart/form-data)
Body: { protein_file: File, ligand_smiles: string }
Response: { job_id: "uuid", status: "queued" }

// Get Job Status (polls every 2 seconds while running)
GET /jobs/{job_id}
Response: { status: "running|completed|failed", result: {...} }

// Get App Info
GET /
Response: { title: "BIOCANVAS v2.0", version: "2.0.0" }
```

### Error Handling

All API errors are automatically caught by the Axios interceptor and displayed as Sonner toasts:

- **4xx errors** → "Bad request", "Validation error", etc
- **5xx errors** → "Server error"
- **503** → "🔌 Backend server is offline. Start with: python3 run.py"
- **Network** → "🌐 Network error or backend unreachable"

---

## 🎨 Design System

### Color Palette (Deep Science)
```
background:        #09090b  (Zinc 950)
surface:           #18181b  (Zinc 900)
surface-highlight: #27272a  (Zinc 800)
surface-border:    #3f3f46  (Zinc 700)
primary:           #0ea5e9  (Sky 500 - Electric Blue)
accent:            #8b5cf6  (Violet 500)
success:           #10b981  (Emerald 500)
destructive:       #ef4444  (Red 500)
muted:             #71717a  (Zinc 500)
```

### Component Variants
- **Button**: primary, secondary, ghost, destructive, success
- **Card**: default, glass, elevated
- **Badge**: default, primary, success, destructive, warning
- **Input**: default, subtle (with error states)

---

## 🚀 Development Commands

```bash
# Start dev server (with HMR)
npm run dev

# Type-check
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📊 State Management Strategy

### Zustand Stores

**useUIStore** - UI State
```typescript
{
  sidebarOpen: boolean
  activeTab: 'docking' | 'visualize' | 'results' | 'settings'
  isDarkMode: boolean
  isLoading: boolean
  notification: { type, message } | null
}
```

**useDockingStore** - Docking State
```typescript
{
  jobs: Map<jobId, DockingJob>
  activeJobId: string | null
  methods: createJob, updateJobStatus, removeJob, setActiveJob, ...
}
```

### React Query Configuration

```typescript
{
  staleTime: 1000 * 60,          // 1 minute
  gcTime: 1000 * 60 * 10,        // 10 minutes (cache)
  retry: 2,
  refetchOnWindowFocus: false    // Don't refetch on tab switch
}
```

---

## 🔄 Job Polling Strategy

When a job is submitted:
1. Return job status with ID
2. Automatically poll every 2 seconds: `GET /jobs/{jobId}`
3. Display real-time status: "⏳ Queued", "🔬 Running", etc
4. **Auto-stop polling** when status === "completed" or "failed"
5. Show results & affinity score

---

## 🎯 Features & Tabs

### Docking Tab
- Upload PDB file (protein)
- Enter SMILES (ligand)
- Submit button with loading state
- Real-time job monitor with status

### Visualize Tab
- 3D molecular structure viewer (lazy-loaded)
- Shows docking result poses
- Interactive (zoom, rotate, color)
- Uses 3Dmol.js

### Results Tab
- Binding affinity score
- RMSD value
- Job metadata
- Links to download files

### Settings Tab
- (Placeholder for future configuration)

---

## 🧪 Testing the Frontend

### 1. Start Backend
```bash
cd /Users/atifanwar/Desktop/BIOCANVAS
python3 run.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Flow
1. Go to http://localhost:5173
2. Upload a PDB file
3. Enter SMILES: `CC(=O)O` (acetic acid)
4. Click "Start Docking"
5. Watch job status update in real-time
6. See results once complete

---

## 🔧 Environment Variables

`.env` file:
```
VITE_API_URL=http://127.0.0.1:8000
VITE_ENV=development
```

For production:
```
VITE_API_URL=https://api.biocanvas.io
VITE_ENV=production
```

---

## 📦 Dependencies

### Core
- `react@18` - UI library
- `react-dom@18` - DOM renderer
- `vite` - Build tool with SWC compiler
- `typescript` - Type safety

### State & Data
- `zustand@4` - Client state (lightweight)
- `@tanstack/react-query@5` - Server state (with polling)
- `axios@1.7` - HTTP client
- `zod@3` - Runtime validation

### UI & Styling
- `tailwindcss@3` - Utility CSS framework
- `clsx` + `tailwind-merge` - Intelligent class merging
- `class-variance-authority` - Component variants
- `lucide-react` - Icon library

### Feedback
- `sonner` - Modern toast notifications

### Science
- `3dmol` - WebGL molecular viewer

---

## 🚀 Production Deployment

### Build
```bash
npm run build
# Output: dist/
```

### Deploy to Vercel
```bash
vercel deploy
```

### Environment for Production
1. Set `VITE_API_URL` to your backend domain
2. Enable CORS on backend
3. Use HTTPS for API calls

---

## 🐛 Common Issues

### Issue: "Backend server is offline"
**Solution:** Make sure FastAPI server is running
```bash
cd /Users/atifanwar/Desktop/BIOCANVAS
python3 run.py
```

### Issue: CORS errors
**Solution:** Ensure backend has CORS middleware for frontend origin

### Issue: 3D viewer not loading
**Solution:** Check browser console. 3dmol.js is lazy-loaded

### Issue: Jobs not polling
**Solution:** Check Network tab in DevTools. Should see `/jobs/{id}` requests every 2 seconds

---

## 🎓 Architecture Patterns Used

1. **Compound Components** - Button + Icon, Card + Header + Content
2. **Custom Hooks** - useDockingJob, useHealthCheck with polling logic
3. **Store-based State** - Zustand for predictable updates
4. **Lazy Code Splitting** - React.lazy() for 3D viewer
5. **Interceptor Pattern** - Global error handling via Axios
6. **Zod Validation** - Runtime type safety
7. **CVA Variants** - Automatic className merging
8. **SWC Compilation** - Fast TypeScript → JavaScript

---

## 📞 Support

For issues or questions:
1. Check console for errors
2. Review Network tab for API calls
3. Verify backend is running
4. Check `.env` file configuration

---

**Status:** ✅ Production Ready  
**Last Updated:** February 11, 2026  
**Version:** 2.0.0
