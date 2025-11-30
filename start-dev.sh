#!/bin/bash

# ScholarSidekick Development Startup Script
# Starts both backend (Flask) and frontend (React/Vite)

set -e  # Exit on error

PROJECT_DIR="/Users/seehorn/Downloads/Development/ScholarSidekick"
FRONTEND_DIR="$PROJECT_DIR/tool-code"

echo "================================================"
echo "   ScholarSidekick - Full Stack Startup"
echo "================================================"
echo ""

# Check if backend virtual environment exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_DIR/.venv"
    echo "Please create it first:"
    echo "  cd $PROJECT_DIR"
    echo "  python -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "❌ Frontend dependencies not installed"
    echo "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Kill any existing processes on ports 5001 and 3000
echo "Checking for existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
echo "✅ Ports cleared"
echo ""

# Start backend
echo "Starting backend (Flask)..."
cd "$PROJECT_DIR"
source .venv/bin/activate
nohup python run.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: $PROJECT_DIR/backend.log"
echo "   URL: http://localhost:5001"
echo ""

# Wait for backend to start
echo "Waiting for backend to be ready..."
sleep 3

# Check if backend is responding
if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend might not be ready yet"
fi
echo ""

# Start frontend
echo "Starting frontend (Vite)..."
cd "$FRONTEND_DIR"
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: $PROJECT_DIR/frontend.log"
echo "   URL: http://localhost:3000"
echo ""

# Wait for frontend to start
echo "Waiting for frontend to be ready..."
sleep 5

echo "================================================"
echo "   ✅ ScholarSidekick is running!"
echo "================================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:5001"
echo "📊 API Docs: See API_REFERENCE.md"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f $PROJECT_DIR/backend.log"
echo "   Frontend: tail -f $PROJECT_DIR/frontend.log"
echo ""
echo "🛑 To stop both services:"
echo "   ./stop-dev.sh"
echo "   or: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "================================================"

# Open browser (optional)
# sleep 2
# open http://localhost:3000
