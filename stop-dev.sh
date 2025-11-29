#!/bin/bash

# ScholarSidekick Development Stop Script
# Stops both backend and frontend services

PROJECT_DIR="/Users/seehorn/Downloads/Development/ScholarSidekick"

echo "================================================"
echo "   Stopping ScholarSidekick Services"
echo "================================================"
echo ""

# Stop backend
if [ -f "$PROJECT_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_DIR/backend.pid")
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend already stopped"
    rm "$PROJECT_DIR/backend.pid"
    echo "✅ Backend stopped"
else
    echo "⚠️  No backend PID file found"
    # Try to kill any process on port 5001
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
fi

echo ""

# Stop frontend
if [ -f "$PROJECT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_DIR/frontend.pid")
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend already stopped"
    rm "$PROJECT_DIR/frontend.pid"
    echo "✅ Frontend stopped"
else
    echo "⚠️  No frontend PID file found"
    # Try to kill any process on port 3000
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

echo ""
echo "================================================"
echo "   ✅ All services stopped"
echo "================================================"
