#!/usr/bin/env python
"""
Minimal ASGI test to identify the WebSocket issue
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

def test_asgi_application():
    """Test the ASGI application directly"""
    print("🔍 Testing ASGI Application...")
    
    try:
        from calmconnect_backend.asgi import application
        from channels.routing import ProtocolTypeRouter
        
        print(f"✅ ASGI application loaded: {type(application)}")
        
        if isinstance(application, ProtocolTypeRouter):
            print("✅ ProtocolTypeRouter configured")
            protocols = list(application.application_mapping.keys())
            print(f"✅ Available protocols: {protocols}")
            
            # Test the WebSocket application
            if 'websocket' in application.application_mapping:
                ws_app = application.application_mapping['websocket']
                print(f"✅ WebSocket app type: {type(ws_app)}")
                
                # Test if it's a URLRouter
                if hasattr(ws_app, 'url_patterns'):
                    print(f"✅ URL patterns: {len(ws_app.url_patterns)}")
                    for pattern in ws_app.url_patterns:
                        print(f"  - {pattern.pattern}")
                else:
                    print("❌ WebSocket app is not a URLRouter")
            else:
                print("❌ No WebSocket protocol in application mapping")
        else:
            print("❌ Expected ProtocolTypeRouter")
            
    except Exception as e:
        print(f"❌ ASGI application error: {e}")
        import traceback
        traceback.print_exc()

def test_websocket_routing():
    """Test WebSocket routing specifically"""
    print("\n🔍 Testing WebSocket Routing...")
    
    try:
        from mentalhealth.routing import websocket_urlpatterns
        
        print(f"✅ WebSocket patterns: {len(websocket_urlpatterns)}")
        
        for i, pattern in enumerate(websocket_urlpatterns):
            print(f"  {i+1}. {pattern.pattern}")
            print(f"     Callback: {pattern.callback}")
            
            # Test if the callback is callable
            try:
                # This should be an ASGI application
                app = pattern.callback
                print(f"     Type: {type(app)}")
                if hasattr(app, '__call__'):
                    print("     ✅ Callable")
                else:
                    print("     ❌ Not callable")
            except Exception as e:
                print(f"     ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ WebSocket routing error: {e}")
        import traceback
        traceback.print_exc()

def test_consumer_import():
    """Test consumer import and creation"""
    print("\n🔍 Testing Consumer Import...")
    
    try:
        from mentalhealth.consumers import TestConsumer
        
        print("✅ TestConsumer imported")
        
        # Test consumer creation
        consumer = TestConsumer()
        print("✅ TestConsumer created")
        
        # Test if it has required methods
        required_methods = ['connect', 'disconnect', 'receive']
        for method in required_methods:
            if hasattr(consumer, method):
                print(f"✅ Has {method} method")
            else:
                print(f"❌ Missing {method} method")
                
    except Exception as e:
        print(f"❌ Consumer test error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Minimal ASGI Test")
    print("=" * 50)
    
    test_asgi_application()
    test_websocket_routing()
    test_consumer_import()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("This will show exactly where the WebSocket routing is failing.")

if __name__ == "__main__":
    main() 