#!/usr/bin/env python
"""
Simple WebSocket test using built-in libraries
"""
import os
import django
import asyncio
import json
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

async def test_simple_websocket():
    """Test WebSocket connection using aiohttp"""
    print("🔍 Testing Simple WebSocket Connection...")
    
    try:
        import aiohttp
        
        # Test URL
        test_url = "ws://localhost:8000/ws/test/"
        
        print(f"Connecting to: {test_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(test_url) as ws:
                print("✅ WebSocket connection established!")
                
                # Send a test message
                test_message = "Hello WebSocket!"
                await ws.send_str(test_message)
                print(f"✅ Sent message: {test_message}")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(ws.receive(), timeout=5.0)
                    print(f"✅ Received: {response.data}")
                except asyncio.TimeoutError:
                    print("⚠️ No response received within 5 seconds")
                
                # Close connection
                await ws.close()
                print("✅ WebSocket connection closed")
                
    except ImportError:
        print("❌ aiohttp not available, trying alternative test")
        test_alternative_websocket()
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def test_alternative_websocket():
    """Alternative test using requests to check if server is running"""
    print("🔍 Testing Server Status...")
    
    try:
        import requests
        
        # Test HTTP endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ HTTP server is running (Status: {response.status_code})")
        
        # Test WebSocket endpoint (this will fail but show the error)
        try:
            response = requests.get("http://localhost:8000/ws/test/", timeout=5)
            print(f"⚠️ WebSocket endpoint returned HTTP: {response.status_code}")
        except Exception as e:
            print(f"✅ WebSocket endpoint is not HTTP (expected): {e}")
            
    except ImportError:
        print("❌ requests library not available")
    except Exception as e:
        print(f"❌ Server test failed: {e}")

def test_consumer_directly():
    """Test the consumer directly"""
    print("🔍 Testing Consumer Directly...")
    
    try:
        from mentalhealth.consumers import TestConsumer
        from channels.testing import WebsocketCommunicator
        from calmconnect_backend.asgi import application
        
        print("✅ Consumer and ASGI application imported successfully")
        print(f"✅ Application type: {type(application)}")
        
        # Test the consumer
        consumer = TestConsumer()
        print("✅ TestConsumer created successfully")
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Simple WebSocket Test")
    print("=" * 40)
    
    # Test 1: Check consumer
    test_consumer_directly()
    
    # Test 2: Check server status
    test_alternative_websocket()
    
    # Test 3: Try WebSocket connection
    print("\n" + "=" * 40)
    asyncio.run(test_simple_websocket())
    
    print("\n" + "=" * 40)
    print("🎯 DIAGNOSIS:")
    print("If you see 'WebSocket connection established', the issue is fixed!")
    print("If you see connection errors, check the server logs for more details.")

if __name__ == "__main__":
    main() 