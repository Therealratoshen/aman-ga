#!/bin/bash
#===============================================================================
# Aman ga? v2.1 - Simple Startup Script for Demo Mode
# This script starts the backend in demo mode without requiring a database
#===============================================================================

echo "🚀 Starting Aman ga? in Demo Mode..."
echo "📋 This will run the backend with mock database (no external services needed)"

# Change to backend directory
cd /Users/filberthenrico/aman-ga/backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "🐍 Activating existing virtual environment..."
    source venv/bin/activate
fi

# Create .env file for demo mode if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file for demo mode..."
    cat > .env << EOF
# Supabase Configuration (Will trigger mock mode)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=Aman ga?
DEBUG=True

# DEMO MODE - No database service needed
MOCK_MODE=True
EOF
fi

# Start the application
echo "🌟 Starting Aman ga? backend server..."
echo "🌐 Access the API at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "📱 Frontend will be available at: http://localhost:3000 (if you run the frontend separately)"

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload