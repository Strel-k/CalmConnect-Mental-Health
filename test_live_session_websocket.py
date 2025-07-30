#!/usr/bin/env python
"""
Test script for live session WebSocket
"""
import asyncio
import websockets
import json

async def test_live_session_websocket():
    room_id = "appointment_51"
    uri = f"ws://localhost:8000/ws/live-session/{room_id}/"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to live session: {uri}")
            
            # Send a test message
            test_message = {"type": "chat_message", "message": "Hello from test!"}
            await websocket.send(json.dumps(test_message))
            print("Sent test message")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error connecting to live session WebSocket: {e}")

if __name__ == "__main__":
    print("Testing live session WebSocket connection...")
    asyncio.run(test_live_session_websocket()) 