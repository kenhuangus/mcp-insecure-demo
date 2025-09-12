#!/bin/bash

# Run Attacks Script for macOS
# This script runs comprehensive attacks against the vulnerable MCP servers

set -e

echo "🎯 Running MCP Vulnerability Attacks on macOS..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup-macos.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create results directory
mkdir -p results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📊 Running comprehensive attacks..."
echo "📁 Results will be saved to results/ directory"
echo ""

# Test 1: Basic STDIO Server
echo "🔍 Testing Basic STDIO Server..."
python3 attack-mcp-client.py vuln-mcp.py > "results/stdio_basic_${TIMESTAMP}.txt" 2>&1
echo "✅ Basic STDIO attack completed"

# Test 2: Enhanced STDIO Server
echo "🔍 Testing Enhanced STDIO Server..."
python3 comprehensive-attack-client.py enhanced-vuln-mcp.py > "results/stdio_enhanced_${TIMESTAMP}.txt" 2>&1
echo "✅ Enhanced STDIO attack completed"

# Test 3: SSE Server (if running)
echo "🔍 Testing SSE Server..."
if curl -s http://localhost:9000/ping > /dev/null; then
    python3 mcp-sse-client-attack.py > "results/sse_${TIMESTAMP}.txt" 2>&1
    echo "✅ SSE attack completed"
else
    echo "⚠️  SSE server not running, skipping SSE tests"
fi

# Test 4: Good Client (for comparison)
echo "🔍 Testing Good Client (for comparison)..."
echo "This will run in interactive mode. Press Ctrl+C to exit."
python3 good-mcp-client.py vuln-mcp.py > "results/good_client_${TIMESTAMP}.txt" 2>&1 &
GOOD_CLIENT_PID=$!
sleep 5
kill $GOOD_CLIENT_PID 2>/dev/null || true
echo "✅ Good client test completed"

echo ""
echo "📋 Attack Summary:"
echo "=================="
echo "📁 Results saved to: results/"
echo "🕐 Timestamp: $TIMESTAMP"
echo ""

# Show quick summary of results
echo "📊 Quick Results Summary:"
echo "------------------------"
for file in results/*_${TIMESTAMP}.txt; do
    if [ -f "$file" ]; then
        echo "📄 $(basename "$file"):"
        if grep -q "Attack Success Rate" "$file"; then
            grep "Attack Success Rate" "$file" | tail -1
        elif grep -q "COMPREHENSIVE ATTACK REPORT" "$file"; then
            grep "Overall Success Rate" "$file" | tail -1
        else
            echo "   (No success rate found)"
        fi
        echo ""
    fi
done

echo "🎉 All attacks completed!"
echo "📖 Check the results/ directory for detailed reports"



