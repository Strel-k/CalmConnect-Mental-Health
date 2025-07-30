#!/usr/bin/env python
"""
Simple WebSocket test script
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/test/"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Send a test message
            test_message = {"type": "test", "message": "Hello WebSocket!"}
            await websocket.send(json.dumps(test_message))
            print("Sent test message")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

if __name__ == "__main__":
    print("Testing WebSocket connection...")
    asyncio.run(test_websocket()) 