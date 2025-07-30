import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import LiveSession, SessionMessage


class LiveSessionConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for live video sessions"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'live_session_{self.room_id}'
        
        print(f"WebSocket: Connection attempt to room {self.room_id}")
        user = self.scope['user']
        username = user.username if user.is_authenticated else 'Anonymous'
        print(f"WebSocket: User: {username}")
        channel_layer_str = str(self.channel_layer)
        print(f"WebSocket: Channel layer: {channel_layer_str}")
        
        # Verify user has access to this session
        if await self.can_access_session():
            print(
                f"WebSocket: Access granted for room {self.room_id}"
            )
            try:
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                
                await self.accept()
                print(
                    f"WebSocket: Connection accepted for room {self.room_id}"
                )
                
                # Notify others that user joined
                print(
                    f"WebSocket: Sending user_joined event for user "
                    f"{self.scope['user'].id} ("
                    f"{self.scope['user'].username}) in room "
                    f"{self.room_id}"
                )
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_joined',
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username,
                    }
                )
                print(
                    f"WebSocket: User joined notification sent for room {self.room_id}"
                )
            except Exception as e:
                print(
                    f"WebSocket: Error during connection: {e}"
                )
                await self.close()
        else:
            print(
                f"WebSocket: Access denied for room {self.room_id}"
            )
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.scope['user'].id,
                'username': self.scope['user'].username,
            }
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'webrtc_signal':
            # Forward WebRTC signaling messages
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_signal',
                    'user_id': self.scope['user'].id,
                    'signal': data.get('signal'),
                    'target': data.get('target'),
                }
            )
        
        elif message_type == 'chat_message':
            # Handle chat messages
            await self.save_chat_message(data.get('message'))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user_id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'message': data.get('message'),
                }
            )
        
        elif message_type == 'session_status':
            # Update session status
            await self.update_session_status(data.get('status'))
    
    async def webrtc_signal(self, event):
        """Send WebRTC signal to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'user_id': event['user_id'],
            'signal': event['signal'],
            'target': event['target'],
        }))
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message'],
        }))
    
    async def user_joined(self, event):
        print(
            f"WebSocket: user_joined handler called for user "
            f"{event['user_id']} ("
            f"{event['username']}) in room "
            f"{self.room_id}"
        )
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    @database_sync_to_async
    def can_access_session(self):
        """Check if user can access this session"""
        # Temporarily allow all connections for debugging
        print(f"WebSocket: Access to room {self.room_id}: GRANTED (debug mode)")
        return True
    
    @database_sync_to_async
    def save_chat_message(self, message):
        """Save chat message to database"""
        try:
            session = LiveSession.objects.get(room_id=self.room_id)
            # Only save if user is authenticated
            if self.scope['user'].is_authenticated:
                SessionMessage.objects.create(
                    session=session,
                    sender=self.scope['user'],
                    message=message,
                    message_type='text'
                )
        except LiveSession.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_session_status(self, status):
        """Update session status"""
        try:
            session = LiveSession.objects.get(room_id=self.room_id)
            session.status = status
            session.save()
        except LiveSession.DoesNotExist:
            pass


class ChatConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for text-only chat sessions"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Verify user has access to this session
        if await self.can_access_session():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        
        # Save message to database
        await self.save_chat_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_id': self.scope['user'].id,
                'username': self.scope['user'].username,
                'message': message,
            }
        )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message'],
        }))
    
    @database_sync_to_async
    def can_access_session(self):
        """Check if user can access this session"""
        if isinstance(self.scope['user'], AnonymousUser):
            return False
        
        try:
            session = LiveSession.objects.get(room_id=self.room_id)
            return (session.appointment.user == self.scope['user'] or 
                   session.appointment.counselor.user == self.scope['user'])
        except LiveSession.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_chat_message(self, message):
        """Save chat message to database"""
        try:
            session = LiveSession.objects.get(room_id=self.room_id)
            # Only save if user is authenticated
            if self.scope['user'].is_authenticated:
                SessionMessage.objects.create(
                    session=session,
                    sender=self.scope['user'],
                    message=message,
                    message_type='text'
                )
        except LiveSession.DoesNotExist:
            pass 


class TestConsumer(AsyncWebsocketConsumer):
    """Simple test consumer for debugging WebSocket connections"""
    
    async def connect(self):
        print(f"TestConsumer: Connection attempt")
        print(f"TestConsumer: User: {self.scope['user']}")
        print(f"TestConsumer: Channel layer: {self.channel_layer}")
        
        try:
            await self.accept()
            print(f"TestConsumer: Connection accepted")
            # Send a welcome message
            await self.send(text_data=json.dumps({
                'type': 'welcome',
                'message': 'WebSocket connection successful!'
            }))
        except Exception as e:
            print(f"TestConsumer: Error during connection: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        print(f"TestConsumer: Disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        print(f"TestConsumer: Received: {text_data}")
        
        # Echo the message back
        await self.send(text_data=json.dumps({
            'type': 'echo',
            'message': f'Echo: {text_data}'
        })) 