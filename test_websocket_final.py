#!/usr/bin/env python
"""
Final WebSocket connection test
"""
import requests
import time


def test_http_server():
    """Test if HTTP server is running"""
    print("🔍 Testing HTTP server...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ HTTP server is running")
            return True
        else:
            print(f"⚠️ HTTP server returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP server test failed: {e}")
        return False


def test_websocket_endpoint():
    """Test WebSocket endpoint availability"""
    print("🔍 Testing WebSocket endpoint...")
    
    try:
        # Try to connect to WebSocket endpoint
        response = requests.get("http://localhost:8000/ws/test/", timeout=5)
        print(f"📡 WebSocket endpoint response: {response.status_code}")
        
        # Note: WebSocket endpoints typically return 400 or 426 for upgrade requests
        # A 404 means the endpoint doesn't exist
        if response.status_code in [400, 426]:
            print("✅ WebSocket endpoint exists (expected upgrade response)")
            return True
        elif response.status_code == 404:
            print("❌ WebSocket endpoint not found (404)")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ WebSocket endpoint test failed: {e}")
        return False


def main():
    """Run WebSocket tests"""
    print("🚀 Final WebSocket Connection Test")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test HTTP server
    http_ok = test_http_server()
    
    # Test WebSocket endpoint
    ws_ok = test_websocket_endpoint()
    
    print("\n" + "=" * 40)
    print("🎯 RESULTS:")
    
    if http_ok and ws_ok:
        print("✅ Server is ready for WebSocket connections!")
        print("\n📋 Next Steps:")
        print("1. Open browser to: http://localhost:8000")
        print("2. Open browser console and test:")
        print("   const ws = new WebSocket('ws://localhost:8000/ws/test/');")
        print("   ws.onopen = () => console.log('✅ Connected!');")
        print("   ws.onerror = (e) => console.error('❌ Error:', e);")
    else:
        print("❌ Server is not ready for WebSocket connections")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure server is running with: py start_websocket_server.py")
        print("2. Check that Uvicorn is installed: pip install uvicorn")
        print("3. Verify Django settings are correct")


if __name__ == "__main__":
    main() 