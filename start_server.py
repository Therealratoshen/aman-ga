#!/usr/bin/env python3
"""
Simple server starter for Aman ga?
"""

import sys
import os
sys.path.insert(0, '/Users/filberthenrico/aman-ga/backend')

# Change to backend directory
os.chdir('/Users/filberthenrico/aman-ga/backend')

try:
    from main import app
    import uvicorn
    print("✅ Successfully imported main app")
    
    # Start server
    print("🚀 Starting server on http://0.0.0.0:8000")
    print("📝 API docs: http://0.0.0.0:8000/docs")
    print("📱 Frontend: http://0.0.0.0:8000/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)