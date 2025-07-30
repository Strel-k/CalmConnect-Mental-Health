#!/usr/bin/env python
"""
ASGI Server Script for CalmConnect with WebSocket Support
"""
import os
import sys
import django
from django.core.asgi import get_asgi_application

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

# Import after Django setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from mentalhealth.routing import websocket_urlpatterns

# ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

if __name__ == "__main__":
    import uvicorn
    
    print("Starting ASGI server with WebSocket support...")
    print("Server will be available at http://localhost:8000/")
    print("WebSocket endpoints:")
    print("  - ws://localhost:8000/ws/test/")
    print("  - ws://localhost:8000/ws/live-session/<room_id>/")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "run_asgi_server:application",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting ASGI server: {e}")
        sys.exit(1) 