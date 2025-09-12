#!/bin/bash

# Start Dashboard Script
# This script starts both the backend API and frontend development server

set -e

echo "🚀 Starting MCP Vulnerability Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup-macos.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping dashboard..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "📦 Building frontend..."
    cd frontend
    npm run build
    cd ..
fi

# Start backend API server
echo "🌐 Starting backend API server on port 8000..."
python3 backend_api.py &
API_PID=$!

# Wait a moment for the API to start
sleep 3

# Start frontend development server (if not built)
if [ ! -d "frontend/dist" ]; then
    echo "⚛️  Starting frontend development server on port 3000..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
else
    echo "✅ Frontend is built and will be served by the API server"
fi

echo ""
echo "✅ Dashboard started successfully!"
echo ""
echo "📊 Dashboard URLs:"
echo "   - Main Dashboard: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
if [ ! -d "frontend/dist" ]; then
    echo "   - Frontend Dev Server: http://localhost:3000"
fi
echo ""
echo "🔍 Test endpoints:"
echo "   - API Health: http://localhost:8000/api/reports"
echo "   - Server Status: http://localhost:8000/api/servers/status"
echo ""
echo "⏹️  Press Ctrl+C to stop the dashboard"
echo ""

# Wait for user to stop
wait
