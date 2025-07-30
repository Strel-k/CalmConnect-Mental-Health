#!/usr/bin/env python
"""
Minimal ASGI test
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

def test_asgi_application():
    """Test the ASGI application"""
    print("🔍 Testing ASGI Application...")
    
    try:
        from calmconnect_backend.asgi import application
        from channels.routing import ProtocolTypeRouter
        
        print(f"✅ ASGI application loaded: {type(application)}")
        
        if isinstance(application, ProtocolTypeRouter):
            print("✅ ProtocolTypeRouter configured correctly")
            protocols = list(application.application_mapping.keys())
            print(f"✅ Available protocols: {protocols}")
            
            if 'websocket' in protocols:
                print("✅ WebSocket protocol available")
            else:
                print("❌ WebSocket protocol missing")
                
            if 'http' in protocols:
                print("✅ HTTP protocol available")
            else:
                print("❌ HTTP protocol missing")
        else:
            print("❌ Expected ProtocolTypeRouter")
            
    except Exception as e:
        print(f"❌ ASGI application error: {e}")

def test_websocket_routing():
    """Test WebSocket routing"""
    print("\n🔍 Testing WebSocket Routing...")
    
    try:
        from mentalhealth.routing import websocket_urlpatterns
        
        print(f"✅ WebSocket URL patterns loaded: {len(websocket_urlpatterns)} patterns")
        
        for i, pattern in enumerate(websocket_urlpatterns):
            print(f"  {i+1}. {pattern.pattern}")
            
    except Exception as e:
        print(f"❌ WebSocket routing error: {e}")

def test_consumer_import():
    """Test consumer import"""
    print("\n🔍 Testing Consumer Import...")
    
    try:
        from mentalhealth.consumers import LiveSessionConsumer, TestConsumer
        
        print("✅ LiveSessionConsumer imported successfully")
        print("✅ TestConsumer imported successfully")
        
        # Test consumer creation
        test_consumer = TestConsumer()
        print("✅ TestConsumer created successfully")
        
    except Exception as e:
        print(f"❌ Consumer import error: {e}")

def main():
    """Run all tests"""
    print("🚀 Minimal ASGI Test")
    print("=" * 40)
    
    test_asgi_application()
    test_websocket_routing()
    test_consumer_import()
    
    print("\n" + "=" * 40)
    print("🎯 SUMMARY:")
    print("If all tests pass, the ASGI configuration is correct.")
    print("The issue might be with the server startup or routing.")

if __name__ == "__main__":
    main() 