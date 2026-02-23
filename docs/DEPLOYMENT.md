# 🚀 BIOCANVAS Deployment Guide

## System Requirements

### Minimum
- Python 3.9+
- Node.js 16+ (for frontend build)
- 4GB RAM
- 2GB disk space

### Recommended
- Python 3.11+
- Node.js 18+
- 8GB RAM
- 5GB disk space
- macOS/Linux (Windows supported via WSL2)

---

## Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_WORKERS=4
DEBUG=false

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

Copy from `.env.example`:
```bash
cp .env.example .env
```

---

## Development Setup

### 1. Backend Setup

```bash
cd /path/to/BIOCANVAS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python3 -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# This will open http://localhost:5173
```

### 3. Run Both Services

**Terminal 1 (Backend)**:
```bash
source .venv/bin/activate
python3 -m uvicorn backend.main:app --reload
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Then visit: http://localhost:5173

---

## Production Deployment

### Using Docker (Recommended)

#### Backend Docker

Create `Dockerfile.backend`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY data ./data

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -f Dockerfile.backend -t biocanvas-api .
docker run -p 8000:8000 biocanvas-api
```

#### Frontend Docker

Create `Dockerfile.frontend`:
```dockerfile
FROM node:18 AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -f Dockerfile.frontend -t biocanvas-ui .
docker run -p 80:80 biocanvas-ui
```

### Using Python venv (Traditional)

```bash
# Create production venv
python3 -m venv /var/www/biocanvas/venv
source /var/www/biocanvas/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start with Gunicorn (multiple workers)
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

### Using systemd (Linux)

Create `/etc/systemd/system/biocanvas.service`:

```ini
[Unit]
Description=BIOCANVAS API Server
After=network.target

[Service]
Type=notify
User=biocanvas
WorkingDirectory=/var/www/biocanvas
Environment="PATH=/var/www/biocanvas/venv/bin"
ExecStart=/var/www/biocanvas/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable biocanvas
sudo systemctl start biocanvas
sudo systemctl status biocanvas
```

---

## Optional Dependencies Installation

### AutoDock Vina (Linux/Mac)

```bash
# Via conda (recommended)
conda install -c bioconda autodock-vina

# Via custom compilation
# See: https://github.com/ccsb-scripps/AutoDock-Vina
```

### OpenBabel

```bash
# Via conda
conda install -c conda-forge openbabel

# Via Homebrew (macOS)
brew install open-babel
```

---

## Monitoring & Logs

### Backend Logs

```bash
# View real-time logs
tail -f biocanvas_server.log

# Search for errors
grep ERROR biocanvas_server.log
```

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Visit: http://localhost:8000/docs

---

## Performance Tuning

### Backend

```python
# In backend/main.py
app = FastAPI()

# Increase worker count for high traffic
# uvicorn backend.main:app --workers 8

# Enable compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Frontend

```bash
# Optimize build
npm run build

# Size analysis
npm run build -- --analyze
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Build Issues

```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Security Checklist

- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS in production
- [ ] Set strong CORS allowed origins
- [ ] Validate file uploads
- [ ] Use environment variables for secrets
- [ ] Regular dependency updates
- [ ] Enable request rate limiting
