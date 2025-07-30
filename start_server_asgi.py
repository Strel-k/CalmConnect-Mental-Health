#!/usr/bin/env python
"""
Start Django server with ASGI support for WebSocket functionality
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def start_asgi_server():
    """Start Django server with ASGI support"""
    print("🚀 Starting Django server with ASGI support...")
    print("📡 WebSocket support enabled")
    print("🌐 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/")
    print("=" * 50)
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
    django.setup()
    
    # Start server with ASGI
    sys.argv = ['manage.py', 'runserver', '--noreload']
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    start_asgi_server() 