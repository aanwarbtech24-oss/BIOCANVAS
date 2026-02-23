# 🧬 BIOCANVAS v2.0

**Production-Ready Molecular Docking Platform**

A modern, full-stack bioinformatics application for computational chemistry research and drug discovery. BIOCANVAS combines a powerful FastAPI backend with a responsive React frontend to provide an intuitive interface for molecular docking calculations.

---

## ✨ Features

- 🚀 **FastAPI Backend** - High-performance async API
- ⚛️ **React Frontend** - Modern, responsive web interface
- 🔬 **Molecular Docking** - AutoDock Vina integration
- 📊 **3D Visualization** - Interactive molecular structure viewing
- 📁 **Job Management** - Track docking jobs and results
- 🔄 **Async Tasks** - Non-blocking job processing
- 📱 **Responsive Design** - Works on desktop & tablet
- ✅ **Production Ready** - Comprehensive error handling

---

## 🚀 Quick Start

### Option 1: One-Command Launch (Recommended)

```bash
python3 run.py
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start API server (port 8000)
- ✅ Build and serve frontend (port 5173)
- ✅ Open browser automatically

### Option 2: Manual Setup

**Backend:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn backend.main:app --reload
```
→ http://localhost:8000/docs

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
→ http://localhost:5173

---

## 📋 System Requirements

- **Python** 3.9+
- **Node.js** 16+
- **4GB RAM** (minimum)
- **macOS, Linux, or Windows** (via WSL2)

---

## 📁 Project Structure

```
BIOCANVAS/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── run.py                       # Main launcher
├── test_server.py               # Testing utilities
│
├── backend/                     # FastAPI Server
│   ├── main.py                 # Application entry
│   ├── docking_engine.py       # Docking algorithms
│   └── routers/                # API route handlers
│
├── frontend/                    # React Application
│   ├── src/
│   │   ├── App.tsx             # Main component
│   │   ├── components/         # Reusable components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── stores/             # State management
│   │   └── types/              # TypeScript types
│   ├── pages/                  # Landing page
│   └── vite.config.ts          # Build config
│
├── data/                        # Sample data
│   ├── proteins.json           # PDB structures
│   └── ligands.json            # SMILES strings
│
├── docking_jobs/                # Working directory (auto-created)
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md         # System design
│   ├── FRONTEND_GUIDE.md       # Frontend setup
│   ├── API_REFERENCE.md        # API endpoints
│   └── DEPLOYMENT.md           # Production guide
│
└── tests/                       # Test suite
```

---

## 🌐 API Endpoints

**Base URL:** `http://localhost:8000`

### Health & Status
- `GET /` - API information
- `GET /health` - Server status

### Job Management
- `POST /jobs` - Submit docking job
- `GET /jobs` - List all jobs
- `GET /jobs/{job_id}` - Get job status

### Results
- `GET /results/{path}` - Download result files

### Documentation
- `GET /docs` - Interactive Swagger UI
- `GET /redoc` - ReDoc documentation

**Full API reference:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

---

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Key variables:**
```env
BACKEND_PORT=8000          # API server port
VITE_API_URL=http://localhost:8000  # Frontend API target
DEBUG=false                 # Debug mode
```

---

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design & technical decisions
- **[Frontend Guide](docs/FRONTEND_GUIDE.md)** - React setup & build
- **[API Reference](docs/API_REFERENCE.md)** - Complete endpoint documentation
- **[Deployment](docs/DEPLOYMENT.md)** - Production setup with Docker

---

## 🧪 Testing

```bash
# Test backend health & endpoints
python3 test_server.py

# Run frontend tests
cd frontend && npm test

# End-to-end testing
# (Configure in frontend/vitest.config.ts)
cd frontend && npm run test:e2e
```

---

## 🚀 Production Deployment

### Using Docker

```bash
# Backend
docker build -f Dockerfile.backend -t biocanvas-api .
docker run -p 8000:8000 biocanvas-api

# Frontend
docker build -f Dockerfile.frontend -t biocanvas-ui .
docker run -p 80:80 biocanvas-ui
```

### Using systemd (Linux)

See [Deployment Guide](docs/DEPLOYMENT.md#using-systemd-linux)

### Performance Tuning

- **Backend**: Increase worker count in deployment
- **Frontend**: Enable gzip compression
- **Caching**: Configure for static assets

See [Deployment Guide](docs/DEPLOYMENT.md#performance-tuning) for details.

---

## 🔗 Optional Dependencies

These enhance functionality but aren't required for basic operation:

### AutoDock Vina (Required for Docking)
```bash
conda install -c bioconda autodock-vina
```

### OpenBabel (PDB Format Conversion)
```bash
conda install -c conda-forge openbabel
```

See [Installation Guide](docs/DEPLOYMENT.md#optional-dependencies-installation)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Stop it
```

### Module Not Found
```bash
pip install -r requirements.txt --force-reinstall
```

### Frontend Build Fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📝 License

[Add your license here]

---

## 👨‍💻 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

---

## 📞 Support

For issues and questions:
- Check [docs/](docs/) for detailed guides
- Review [API_REFERENCE.md](docs/API_REFERENCE.md) for endpoint usage
- See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for setup help

---

## 🎯 Roadmap

### v2.0 (Current)
- ✅ FastAPI backend
- ✅ React frontend structure
- ⏳ Job management system
- ⏳ Results visualization

### v2.1 (Planned)
- Better error handling
- User authentication
- Job history persistence
- Advanced filtering

### v3.0 (Future)
- Multi-GPU support
- Real-time collaboration
- Result export formats
- Integration with external APIs

---

**Built with ❤️ for computational chemists**
