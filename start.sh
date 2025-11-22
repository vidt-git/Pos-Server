#!/bin/bash

# Café Todo Start Script

echo "🎨 Starting Café Todo..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "☕ Brewing your todo list app..."
echo "🌐 Open http://localhost:8000 in your browser"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
