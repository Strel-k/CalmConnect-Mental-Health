#!/usr/bin/env python
"""
Simple ASGI test
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

def test_asgi_import():
    """Test ASGI application import"""
    print("🔍 Testing ASGI Import...")
    
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

def test_websocket_patterns():
    """Test WebSocket patterns import"""
    print("\n🔍 Testing WebSocket Patterns...")
    
    try:
        from mentalhealth.routing import websocket_urlpatterns
        print("✅ WebSocket patterns imported successfully")
        print(f"✅ Patterns count: {len(websocket_urlpatterns)}")
        return True
    except Exception as e:
        print(f"❌ WebSocket patterns import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests"""
    print("🚀 Simple ASGI Test")
    print("=" * 30)
    
    asgi_ok = test_asgi_import()
    patterns_ok = test_websocket_patterns()
    
    print("\n" + "=" * 30)
    if asgi_ok and patterns_ok:
        print("✅ All tests passed - ASGI should work")
    else:
        print("❌ Some tests failed - check the errors above")

if __name__ == "__main__":
    main() 