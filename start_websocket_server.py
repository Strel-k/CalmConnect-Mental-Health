#!/usr/bin/env python
"""
Start WebSocket server with proper Django configuration
"""
import os
import sys
import django
import uvicorn

def setup_django():
    """Setup Django environment"""
    print("🔧 Setting up Django environment...")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
    
    # Setup Django
    django.setup()
    
    print("✅ Django environment configured")

def test_asgi_application():
    """Test ASGI application import"""
    print("🔍 Testing ASGI application...")
    
    try:
        from calmconnect_backend.asgi import application
        print("✅ ASGI application imported successfully")
        print(f"✅ Type: {type(application)}")
        return True
    except Exception as e:
        print(f"❌ ASGI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_server():
    """Start the WebSocket server"""
    print("🚀 Starting WebSocket server...")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Test ASGI application
    if not test_asgi_application():
        print("❌ Failed to load ASGI application")
        return False
    
    print("✅ All checks passed!")
    print("🌐 Starting server at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/")
    print("=" * 50)
    
    # Start Uvicorn server
    uvicorn.run(
        "calmconnect_backend.asgi:application",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server() 