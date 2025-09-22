import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Notification, LiveSession, SessionParticipant


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

        # Check if user has access to this room
        if await self.has_room_access():
            try:
                print(
                    f"WebSocket: Access granted for room {self.room_id}"
                )
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                print(
                    f"WebSocket: Connection accepted for room "
                    f"{self.room_id}"
                )

                # Track participant connection
                await self.track_participant_connection()

                # Send user joined notification to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_joined',
                        'user_id': self.scope['user'].id,
                        'username': self.scope['user'].username
                    }
                )
                print(
                    f"WebSocket: Sending user_joined event for user "
                    f"{self.scope['user'].id} "
                    f"({self.scope['user'].username})"
                )
                print(
                    f"WebSocket: User joined notification sent for room "
                    f"{self.room_id}"
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
        # Track participant disconnection
        await self.track_participant_disconnection()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'webrtc_signal':
                # Validate WebRTC signal data
                signal = data.get('signal')
                if not signal or not signal.get('type'):
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Invalid WebRTC signal format'
                    }))
                    return

                # Forward WebRTC signaling data
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'webrtc_signal',
                        'signal': signal,
                        'user_id': self.scope['user'].id,
                        'sender': self.scope['user'].id
                    }
                )
            elif message_type == 'chat_message':
                # Validate chat message
                message = data.get('message', '').strip()
                if not message:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Empty message not allowed'
                    }))
                    return

                # Handle chat messages
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.scope['user'].username,
                        'user_id': self.scope['user'].id,
                        'timestamp': timezone.now().isoformat()
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            print(f"Error in receive method: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def webrtc_signal(self, event):
        """Send WebRTC signal to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal': event['signal'],
            'sender': event['sender']
        }))

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    async def user_joined(self, event):
        """Send user joined notification to WebSocket"""
        print(
            f"WebSocket: user_joined handler called for user "
            f"{event['user_id']} ({event['username']})"
        )
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username']
        }))

        # Check if both parties are connected and start session
        await self.check_and_start_session()

    async def user_left(self, event):
        """Send user left notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username']
        }))

    @database_sync_to_async
    def track_participant_connection(self):
        """Track when a participant joins the session"""
        try:
            live_session = LiveSession.objects.get(room_id=self.room_id)
            user = self.scope['user']

            # Determine participant role
            if user == live_session.appointment.user:
                role = 'student'
            elif (hasattr(user, 'counselor_profile') and
                  user.counselor_profile == live_session.appointment.counselor):
                role = 'counselor'
            else:
                role = 'observer'

            # Create or update participant record
            participant, created = SessionParticipant.objects.get_or_create(
                session=live_session,
                user=user,
                defaults={'role': role, 'joined_at': timezone.now()}
            )

            if not created:
                # Update joined_at if rejoining
                participant.joined_at = timezone.now()
                participant.left_at = None
                participant.save()

            print(f"WebSocket: Participant {user.username} ({role}) "
                  f"joined session {self.room_id}")

        except LiveSession.DoesNotExist:
            print(f"WebSocket: LiveSession not found for room {self.room_id}")
        except Exception as e:
            print(f"WebSocket: Error tracking participant connection: {e}")

    @database_sync_to_async
    def track_participant_disconnection(self):
        """Track when a participant leaves the session"""
        try:
            live_session = LiveSession.objects.get(room_id=self.room_id)
            user = self.scope['user']

            participant = SessionParticipant.objects.filter(
                session=live_session,
                user=user,
                left_at__isnull=True
            ).first()

            if participant:
                participant.left_at = timezone.now()
                participant.save()
                print(f"WebSocket: Participant {user.username} left session {self.room_id}")

        except Exception as e:
            print(f"WebSocket: Error tracking participant disconnection: {e}")

    async def check_and_start_session(self):
        """Check if both parties are connected and start the session"""
        try:
            # Check session status and participants
            session_started = await self._check_session_participants()

            if session_started:
                # Notify all clients that session has started
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'session_started',
                        'message': 'Session has started',
                        'status': 'active'
                    }
                )

        except Exception as e:
            print(f"WebSocket: Error checking session start: {e}")

    @database_sync_to_async
    def _check_session_participants(self):
        """Check if both parties are connected and start session if ready"""
        try:
            live_session = LiveSession.objects.get(room_id=self.room_id)

            # Only check if session is in waiting status
            if live_session.status != 'waiting':
                return False

            # Get connected participants (those without left_at)
            connected_participants = SessionParticipant.objects.filter(
                session=live_session,
                left_at__isnull=True
            ).select_related('user')

            # Check if we have both student and counselor
            has_student = any(p.role == 'student' for p in connected_participants)
            has_counselor = any(p.role == 'counselor' for p in connected_participants)

            if has_student and has_counselor:
                # Start the session
                live_session.status = 'active'
                live_session.actual_start = timezone.now()
                live_session.save()

                print(f"WebSocket: Session {self.room_id} started automatically")
                return True

            return False

        except LiveSession.DoesNotExist:
            print(f"WebSocket: LiveSession not found for room {self.room_id}")
            return False
        except Exception as e:
            print(f"WebSocket: Error in _check_session_participants: {e}")
            return False

    async def session_started(self, event):
        """Send session started notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'session_started',
            'message': event['message'],
            'status': event['status'],
            'started_at': event['started_at']
        }))

    @database_sync_to_async
    def has_room_access(self):
        # Temporarily allow all connections for debugging
        print(f"WebSocket: Access to room {self.room_id}: GRANTED (debug mode)")
        return True


class ChatConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for text-only chat sessions"""

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].username,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """Handle real-time notifications via WebSocket"""

    async def connect(self):
        """Accept WebSocket connection and add user to their notification group"""
        user = self.scope['user']
        
        if user.is_authenticated:
            # Create a unique group for this user's notifications
            self.notification_group_name = f'notifications_{user.id}'
            
            # Add this connection to the user's notification group
            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )
            
            await self.accept()
            print(f"NotificationConsumer: User {user.username} "
                  f"connected to notifications")
            
            # Send initial notification count
            unread_count = await self.get_unread_count(user.id)
            await self.send(text_data=json.dumps({
                'type': 'notification_count',
                'count': unread_count
            }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Remove user from notification group on disconnect"""
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
            print(f"NotificationConsumer: User {user.username} "
                  f"disconnected from notifications")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                # Mark notification as read
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    
            elif message_type == 'mark_all_read':
                # Mark all notifications as read
                user_id = self.scope['user'].id
                await self.mark_all_notifications_read(user_id)
                
            elif message_type == 'get_notifications':
                # Send recent notifications
                user_id = self.scope['user'].id
                notifications = await self.get_recent_notifications(user_id)
                await self.send(text_data=json.dumps({
                    'type': 'notifications_list',
                    'notifications': notifications
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    async def notification_count_update(self, event):
        """Send updated notification count to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification_count',
            'count': event['count']
        }))

    @database_sync_to_async
    def get_unread_count(self, user_id):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(
            user_id=user_id,
            read=False,
            dismissed=False
        ).count()

    @database_sync_to_async
    def get_recent_notifications(self, user_id):
        """Get recent notifications for user"""
        notifications = Notification.objects.filter(
            user_id=user_id,
            dismissed=False
        ).order_by('-created_at')[:10]
        
        return [{
            'id': notif.id,
            'message': notif.message,
            'type': notif.type,
            'url': notif.url,
            'read': notif.read,
            'created_at': notif.created_at.isoformat(),
            'priority': getattr(notif, 'priority', 'normal')
        } for notif in notifications]

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.scope['user']
            )
            notification.read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self, user_id):
        """Mark all notifications as read for user"""
        Notification.objects.filter(
            user_id=user_id,
            read=False
        ).update(read=True)


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
        
        try:
            data = json.loads(text_data)
            # Echo the message back
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'message': f"Echo: {data.get('message', 'No message')}"
            }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))