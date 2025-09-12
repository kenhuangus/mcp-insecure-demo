#!/bin/bash

# macOS Setup Script for MCP Vulnerability Demonstration System
# This script sets up the environment and dependencies for macOS

set -e  # Exit on any error

echo "🍎 Setting up MCP Vulnerability Demo for macOS..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "   You can install it using Homebrew: brew install python3"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set up database
echo "🗄️  Setting up database..."
python3 -c "
import sqlite3
conn = sqlite3.connect('vulnerable_mcp.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print('Database created successfully')
"

# Set up SSE database
python3 -c "
import sqlite3
conn = sqlite3.connect('vulnerable_mcp_sse.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print('SSE database created successfully')
"

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x setup-macos.sh
chmod +x start-servers.sh
chmod +x run-attacks.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the servers: ./start-servers.sh"
echo "3. Run attacks: ./run-attacks.sh"
echo ""
echo "⚠️  WARNING: This is intentionally vulnerable software for educational purposes only!"
echo "   Do NOT use in production or on systems with sensitive data."



