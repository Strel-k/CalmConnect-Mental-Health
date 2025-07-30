#!/usr/bin/env python
"""
Test WebSocket connection for live sessions
"""
import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection to live session"""
    print("🔍 Testing WebSocket Connection...")
    
    # Test URL
    test_url = "ws://localhost:8000/ws/live-session/test_room/"
    
    try:
        print(f"Connecting to: {test_url}")
        
        async with websockets.connect(test_url) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "chat_message",
                "message": "Test message from client"
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Test message sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Received response: {response}")
            except asyncio.TimeoutError:
                print("⚠️ No response received within 5 seconds")
            
            # Close connection
            await websocket.close()
            print("✅ WebSocket connection closed")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - Server might not be running")
        print("💡 Make sure to run: python manage.py runserver")
        
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
        
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print(f"Error type: {type(e).__name__}")

def test_server_status():
    """Test if Django server is running"""
    print("🔍 Testing Django Server Status...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Django server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running")
        print("💡 Start the server with: python manage.py runserver")
        return False
    except ImportError:
        print("⚠️ requests library not available, skipping HTTP test")
        return True

def check_asgi_configuration():
    """Check ASGI configuration"""
    print("🔍 Checking ASGI Configuration...")
    
    try:
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
        
        import django
        django.setup()
        
        from channels.routing import ProtocolTypeRouter
        from calmconnect_backend.asgi import application
        
        print("✅ ASGI application configured correctly")
        print(f"✅ Application type: {type(application)}")
        
        if isinstance(application, ProtocolTypeRouter):
            print("✅ ProtocolTypeRouter configured")
            print(f"✅ Available protocols: {list(application.application_mapping.keys())}")
        else:
            print("❌ Expected ProtocolTypeRouter, got different type")
            
    except Exception as e:
        print(f"❌ ASGI configuration error: {e}")
        return False
    
    return True

def main():
    """Run all WebSocket tests"""
    print("🚀 WebSocket Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Check server status
    server_running = test_server_status()
    
    # Test 2: Check ASGI configuration
    asgi_ok = check_asgi_configuration()
    
    # Test 3: Test WebSocket connection
    if server_running and asgi_ok:
        print("\n" + "=" * 50)
        asyncio.run(test_websocket_connection())
    else:
        print("\n❌ Skipping WebSocket test due to server/configuration issues")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY:")
    
    if not server_running:
        print("❌ Django server is not running")
        print("💡 Solution: Run 'python manage.py runserver'")
        
    elif not asgi_ok:
        print("❌ ASGI configuration has issues")
        print("💡 Check calmconnect_backend/asgi.py and settings.py")
        
    else:
        print("✅ Server and ASGI configuration look good")
        print("💡 WebSocket connection should work")
        print("💡 If still failing, check browser console for specific errors")

if __name__ == "__main__":
    main() 