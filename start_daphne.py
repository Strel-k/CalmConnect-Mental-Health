#!/usr/bin/env python
"""
Start Daphne server with proper Django settings
"""
import os
import sys
import django
import asyncio

def start_daphne_server():
    """Start Daphne server with Django settings"""
    print("🚀 Starting Daphne server with Django settings...")
    print("📡 WebSocket support enabled")
    print("🌐 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/")
    print("=" * 50)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
    
    # Setup Django
    django.setup()
    
    # Import and start Daphne
    from daphne.server import Server
    from calmconnect_backend.asgi import application
    
    print("✅ Django settings configured")
    print("✅ ASGI application loaded")
    print("✅ Starting Daphne server...")
    
    # Start the server with proper endpoint configuration
    server = Server(application)
    server.run(host='127.0.0.1', port=8000, verbosity=1)

if __name__ == "__main__":
    start_daphne_server() 