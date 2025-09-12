#!/bin/bash

# Setup script for MCP Vulnerability Dashboard Frontend
# This script sets up the TypeScript frontend and backend API

set -e

echo "🚀 Setting up MCP Vulnerability Dashboard Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   You can install it using Homebrew: brew install node"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build the frontend
echo "🔨 Building frontend..."
npm run build

# Go back to root directory
cd ..

# Install Python dependencies for backend API
echo "🐍 Installing Python dependencies for backend API..."
pip install fastapi uvicorn python-multipart

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p results
mkdir -p uploads
mkdir -p logs

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x setup-frontend.sh
chmod +x start-dashboard.sh
chmod +x stop-dashboard.sh

echo ""
echo "🎉 Frontend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the dashboard: ./start-dashboard.sh"
echo "2. Open your browser to: http://localhost:8000"
echo "3. The API documentation is available at: http://localhost:8000/docs"
echo ""
echo "⚠️  WARNING: This is intentionally vulnerable software for educational purposes only!"
echo "   Do NOT use in production or on systems with sensitive data."
