#!/usr/bin/env python3
"""
Cash Manager Application Entry Point
"""

import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Import and run the Flask application
from app import app

if __name__ == "__main__":
    print("🚀 Starting Cash Manager...")
    print("📱 Access at: http://127.0.0.1:19754")
    print("👤 Default login: admin / admin123")
    print("🛑 Press Ctrl+C to stop")

    app.run(host="127.0.0.1", port=19754, debug=True)
