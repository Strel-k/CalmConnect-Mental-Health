"""
Real-time notification service for CalmConnect
Handles creating, sending, and managing notifications via WebSocket
"""

import json
from datetime import datetime, timedelta
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, CustomUser


class NotificationService:
    """Service class for handling real-time notifications"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def create_notification(self, user, message, notification_type='general', 
                          priority='normal', action_url=None, action_text=None,
                          expires_in_hours=None, metadata=None):
        """
        Create a new notification and send it via WebSocket
        
        Args:
            user: User instance or user ID
            message: Notification message text
            notification_type: Type of notification (appointment, report, etc.)
            priority: Priority level (low, normal, high, urgent)
            action_url: URL for notification action
            action_text: Text for action button
            expires_in_hours: Hours until notification expires
            metadata: Additional data as dict
        
        Returns:
            Notification instance
        """
        if isinstance(user, int):
            user = CustomUser.objects.get(id=user)
        
        # Calculate expiration time
        expires_at = None
        if expires_in_hours:
            expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            message=message,
            type=notification_type,
            category=notification_type,
            priority=priority,
            action_url=action_url,
            action_text=action_text,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Send real-time notification
        self.send_notification(notification)
        
        return notification
    
    def send_notification(self, notification):
        """Send notification via WebSocket to user"""
        if not self.channel_layer:
            print("Warning: Channel layer not available for real-time notifications")
            return
        
        # Prepare notification data
        notification_data = {
            'id': notification.id,
            'message': notification.message,
            'type': notification.type,
            'priority': notification.priority,
            'action_url': notification.action_url,
            'action_text': notification.action_text,
            'created_at': notification.created_at.isoformat(),
            'icon': notification.get_icon(),
            'color': notification.get_color(),
            'metadata': notification.metadata
        }
        
        # Send to user's notification group
        group_name = f'notifications_{notification.user.id}'
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )
            print(f"Sent real-time notification to user {notification.user.username}")
        except Exception as e:
            print(f"Error sending real-time notification: {e}")
    
    def send_notification_count_update(self, user):
        """Send updated notification count to user"""
        if not self.channel_layer:
            return
        
        if isinstance(user, int):
            user = CustomUser.objects.get(id=user)
        
        # Get unread count
        unread_count = Notification.objects.filter(
            user=user,
            read=False,
            dismissed=False
        ).count()
        
        # Send count update
        group_name = f'notifications_{user.id}'
        
        try:
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_count_update',
                    'count': unread_count
                }
            )
        except Exception as e:
            print(f"Error sending notification count update: {e}")
    
    def create_appointment_notification(self, appointment, notification_type='created'):
        """Create appointment-related notifications"""
        if notification_type == 'created':
            # Notify student
            self.create_notification(
                user=appointment.user,
                message=f'Your appointment with {appointment.counselor.name} on {appointment.date} at {appointment.time.strftime("%I:%M %p")} has been booked successfully.',
                notification_type='appointment',
                priority='normal',
                action_url=f'/appointment/{appointment.id}/',
                action_text='View Details',
                expires_in_hours=72,
                metadata={
                    'appointment_id': appointment.id,
                    'counselor_name': appointment.counselor.name,
                    'appointment_date': appointment.date.isoformat(),
                    'appointment_time': appointment.time.strftime("%H:%M")
                }
            )
            
            # Notify counselor if they have a user account
            if appointment.counselor.user:
                self.create_notification(
                    user=appointment.counselor.user,
                    message=f'New appointment request from {appointment.user.full_name} on {appointment.date} at {appointment.time.strftime("%I:%M %p")}.',
                    notification_type='appointment',
                    priority='high',
                    action_url=f'/counselor/appointment/{appointment.id}/',
                    action_text='Review',
                    expires_in_hours=48,
                    metadata={
                        'appointment_id': appointment.id,
                        'student_name': appointment.user.full_name,
                        'appointment_date': appointment.date.isoformat(),
                        'appointment_time': appointment.time.strftime("%H:%M")
                    }
                )
        
        elif notification_type == 'reminder':
            # Send appointment reminder
            self.create_notification(
                user=appointment.user,
                message=f'Reminder: You have an appointment with {appointment.counselor.name} tomorrow at {appointment.time.strftime("%I:%M %p")}.',
                notification_type='reminder',
                priority='high',
                action_url=f'/appointment/{appointment.id}/',
                action_text='View Details',
                expires_in_hours=24,
                metadata={
                    'appointment_id': appointment.id,
                    'counselor_name': appointment.counselor.name,
                    'appointment_date': appointment.date.isoformat(),
                    'appointment_time': appointment.time.strftime("%H:%M")
                }
            )
        
        elif notification_type == 'cancelled':
            # Notify about cancellation
            self.create_notification(
                user=appointment.user,
                message=f'Your appointment with {appointment.counselor.name} on {appointment.date} has been cancelled.',
                notification_type='appointment',
                priority='high',
                action_url='/scheduler/',
                action_text='Book New',
                expires_in_hours=168,  # 1 week
                metadata={
                    'appointment_id': appointment.id,
                    'counselor_name': appointment.counselor.name,
                    'appointment_date': appointment.date.isoformat(),
                    'cancellation_reason': getattr(appointment, 'cancellation_reason', '')
                }
            )
    
    def create_report_notification(self, report):
        """Create report-related notifications"""
        if report.user:
            self.create_notification(
                user=report.user,
                message=f'Your session report with {report.counselor.name} has been completed.',
                notification_type='report',
                priority='normal',
                action_url='/user-profile/',
                action_text='View Report',
                expires_in_hours=168,  # 1 week
                metadata={
                    'report_id': report.id,
                    'counselor_name': report.counselor.name,
                    'report_type': report.report_type,
                    'report_title': report.title
                }
            )
    
    def create_feedback_request_notification(self, appointment):
        """Create feedback request notification"""
        self.create_notification(
            user=appointment.user,
            message=f'Please share your feedback about your session with {appointment.counselor.name}.',
            notification_type='feedback',
            priority='normal',
            action_url=f'/feedback/{appointment.id}/',
            action_text='Give Feedback',
            expires_in_hours=168,  # 1 week
            metadata={
                'appointment_id': appointment.id,
                'counselor_name': appointment.counselor.name,
                'appointment_date': appointment.date.isoformat()
            }
        )
    
    def create_system_notification(self, users, message, priority='normal', 
                                 action_url=None, action_text=None):
        """Create system-wide notifications for multiple users"""
        if not isinstance(users, list):
            users = [users]
        
        notifications = []
        for user in users:
            notification = self.create_notification(
                user=user,
                message=message,
                notification_type='system',
                priority=priority,
                action_url=action_url,
                action_text=action_text,
                expires_in_hours=72,
                metadata={'system_notification': True}
            )
            notifications.append(notification)
        
        return notifications
    
    def cleanup_expired_notifications(self):
        """Remove expired notifications"""
        expired_count = Notification.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        if expired_count > 0:
            print(f"Cleaned up {expired_count} expired notifications")
        
        return expired_count
    
    def mark_notification_read(self, notification_id, user):
        """Mark notification as read and update count"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user
            )
            notification.read = True
            notification.save()
            
            # Send updated count
            self.send_notification_count_update(user)
            
            return True
        except Notification.DoesNotExist:
            return False
    
    def mark_all_notifications_read(self, user):
        """Mark all notifications as read for user"""
        Notification.objects.filter(
            user=user,
            read=False
        ).update(read=True)
        
        # Send updated count
        self.send_notification_count_update(user)
    
    def dismiss_notification(self, notification_id, user):
        """Dismiss notification and update count"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user
            )
            notification.dismissed = True
            notification.save()
            
            # Send updated count
            self.send_notification_count_update(user)
            
            return True
        except Notification.DoesNotExist:
            return False


# Global instance
notification_service = NotificationService()


# Convenience functions
def create_notification(user, message, **kwargs):
    """Convenience function to create notification"""
    return notification_service.create_notification(user, message, **kwargs)


def create_appointment_notification(appointment, notification_type='created'):
    """Convenience function for appointment notifications"""
    return notification_service.create_appointment_notification(appointment, notification_type)


def create_report_notification(report):
    """Convenience function for report notifications"""
    return notification_service.create_report_notification(report)


def create_feedback_request_notification(appointment):
    """Convenience function for feedback request notifications"""
    return notification_service.create_feedback_request_notification(appointment)