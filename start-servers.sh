#!/bin/bash

# Start Servers Script for macOS
# This script starts both vulnerable MCP servers

set -e

echo "🚀 Starting MCP Vulnerable Servers on macOS..."

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
    echo "🛑 Stopping servers..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "📡 Starting STDIO MCP Server..."
python3 vuln-mcp.py &
STDIO_PID=$!

echo "📡 Starting Enhanced STDIO MCP Server..."
python3 enhanced-vuln-mcp.py &
ENHANCED_PID=$!

echo "🌐 Starting SSE MCP Server on port 9000..."
python3 mcp-sse-vulnerable-server.py &
SSE_PID=$!

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "📊 Server Status:"
echo "   - STDIO Server (PID: $STDIO_PID)"
echo "   - Enhanced STDIO Server (PID: $ENHANCED_PID)"
echo "   - SSE Server (PID: $SSE_PID) - http://localhost:9000"
echo ""
echo "🔍 Test endpoints:"
echo "   - SSE Ping: http://localhost:9000/ping"
echo "   - SSE Test: http://localhost:9000/sse-test/"
echo "   - Attack Endpoint: http://localhost:9000/attack"
echo ""
echo "⏹️  Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop
wait



