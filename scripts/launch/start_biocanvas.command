#!/bin/bash
# BIOCANVAS v2.0 - One-Click Launcher
# Simply double-click this file to start the complete application
# Launches Backend API + React Frontend + Opens Browser

cd "$(dirname "$0")"

PROJECT_ROOT="$(pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_PID_FILE="/tmp/biocanvas-backend.pid"
FRONTEND_PID_FILE="/tmp/biocanvas-frontend.pid"

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  🧬 BIOCANVAS v2.0 - Molecular Docking         ║"
echo "║     Complete React Application                 ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Kill any old processes on ports 8000 and 5173
echo "🔄 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173,5174,5175 | xargs kill -9 2>/dev/null || true
sleep 1

# Activate virtual environment and start backend
echo "▶️  Starting Backend API (port 8000)..."
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true

python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 > /tmp/biocanvas-backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > $BACKEND_PID_FILE
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for Backend..."
for i in {1..15}; do
  if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is ready!"
    break
  fi
  sleep 1
done

# Start frontend
echo ""
echo "▶️  Starting Frontend React App (port 5173)..."
cd "$FRONTEND_DIR"

# Install dependencies if needed
npm install -q 2>/dev/null || true

npm run dev > /tmp/biocanvas-frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > $FRONTEND_PID_FILE
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "⏳ Waiting for Frontend..."
for i in {1..15}; do
  if curl -s http://localhost:5173/ > /dev/null 2>&1 || curl -s http://localhost:5174/ > /dev/null 2>&1; then
    echo "✅ Frontend is ready!"
    break
  fi
  sleep 1
done

# Open browser - try different ports
echo ""
echo "🌐 Opening BIOCANVAS in your browser..."
sleep 1

if curl -s http://localhost:5173/ > /dev/null 2>&1; then
  open "http://localhost:5173"
elif curl -s http://localhost:5174/ > /dev/null 2>&1; then
  open "http://localhost:5174"
elif curl -s http://localhost:5175/ > /dev/null 2>&1; then
  open "http://localhost:5175"
else
  open "http://localhost:5173"
fi

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║  ✨ BIOCANVAS IS RUNNING!                      ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "📍 App:         http://localhost:5173 (or 5174+)"
echo "📍 API Docs:    http://127.0.0.1:8000/docs"
echo "📍 API Health:  http://127.0.0.1:8000/"
echo ""
echo "🛑 To stop: Press Ctrl+C below"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running
wait
wait $SERVER_PID

# Cleanup
echo ""
echo "🛑 BIOCANVAS stopped."
echo ""

