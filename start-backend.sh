#!/bin/bash
# Aman ga? Startup Script

# Change to project directory
cd /Users/filberthenrico/aman-ga/backend

# Activate virtual environment
source venv/bin/activate

# Install any missing dependencies
pip install -r requirements.txt

# Start the backend server
echo "🚀 Starting Aman ga? backend server..."
echo "📝 Server will be available at: http://localhost:8000"
echo "📝 API docs: http://localhost:8000/docs"
echo "📝 Press Ctrl+C to stop server"

# Start uvicorn server
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info