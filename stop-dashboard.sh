#!/bin/bash

# Stop Dashboard Script
# This script stops all dashboard-related processes

echo "🛑 Stopping MCP Vulnerability Dashboard..."

# Stop backend API server
echo "🌐 Stopping backend API server..."
pkill -f "backend_api.py" || true

# Stop frontend development server
echo "⚛️  Stopping frontend development server..."
pkill -f "vite" || true

# Stop any Node.js processes related to the frontend
echo "📦 Stopping Node.js processes..."
pkill -f "npm run dev" || true

# Stop any Python processes related to MCP servers
echo "🐍 Stopping MCP servers..."
pkill -f "vuln-mcp.py" || true
pkill -f "enhanced-vuln-mcp.py" || true
pkill -f "mcp-sse-vulnerable-server.py" || true

echo "✅ Dashboard stopped successfully!"
echo ""
echo "💡 To start the dashboard again, run: ./start-dashboard.sh"
