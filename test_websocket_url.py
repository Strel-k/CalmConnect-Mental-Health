#!/usr/bin/env python
"""
Test WebSocket URL routing
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

def test_url_patterns():
    """Test URL patterns"""
    print("🔍 Testing URL Patterns...")
    
    try:
        from mentalhealth.routing import websocket_urlpatterns
        
        print(f"✅ Found {len(websocket_urlpatterns)} WebSocket patterns:")
        
        for i, pattern in enumerate(websocket_urlpatterns):
            print(f"  {i+1}. Pattern: {pattern.pattern}")
            print(f"     Callback: {pattern.callback}")
            print()
            
    except Exception as e:
        print(f"❌ URL pattern test failed: {e}")

def test_url_matching():
    """Test URL matching"""
    print("🔍 Testing URL Matching...")
    
    try:
        from mentalhealth.routing import websocket_urlpatterns
        from django.urls import reverse
        
        test_urls = [
            "/ws/test/",
            "/ws/live-session/appointment_54/",
            "/ws/chat/room123/",
            "/ws/invalid/",
        ]
        
        for test_url in test_urls:
            print(f"\nTesting URL: {test_url}")
            
            matched = False
            for pattern in websocket_urlpatterns:
                # Use the pattern's resolve method
                try:
                    match = pattern.resolve(test_url)
                    print(f"  ✅ Matches pattern: {pattern.pattern}")
                    print(f"  ✅ Resolved to: {match}")
                    matched = True
                    break
                except:
                    continue
            
            if not matched:
                print(f"  ❌ No pattern matches")
                
    except Exception as e:
        print(f"❌ URL matching test failed: {e}")

def test_asgi_routing():
    """Test ASGI routing"""
    print("🔍 Testing ASGI Routing...")
    
    try:
        from calmconnect_backend.asgi import application
        
        print(f"✅ ASGI application type: {type(application)}")
        
        if hasattr(application, 'application_mapping'):
            print("✅ Application mapping available")
            for protocol, app in application.application_mapping.items():
                print(f"  - {protocol}: {type(app)}")
        else:
            print("❌ No application mapping")
            
    except Exception as e:
        print(f"❌ ASGI routing test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 WebSocket URL Test")
    print("=" * 40)
    
    test_url_patterns()
    test_url_matching()
    test_asgi_routing()
    
    print("\n" + "=" * 40)
    print("🎯 DIAGNOSIS:")
    print("This will show if the URL patterns are correctly configured.")
    print("Check if the test URLs match the expected patterns.")

if __name__ == "__main__":
    main() 