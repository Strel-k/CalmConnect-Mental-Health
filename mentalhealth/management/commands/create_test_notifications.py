from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mentalhealth.models import Notification
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test notifications for users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create notifications for'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} not found')
                )
                return
        else:
            # Get the first user
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No users found in database')
                )
                return
        
        # Create test notifications
        notifications = [
            {
                'message': 'Your appointment with Dr. Smith has been confirmed for tomorrow at 2:00 PM.',
                'type': 'appointment',
                'url': '/appointments/1/'
            },
            {
                'message': 'New DASS-21 assessment results are available. Click to view your report.',
                'type': 'report',
                'url': '/user-profile/'
            },
            {
                'message': 'Welcome to CalmConnect! Your account has been successfully created.',
                'type': 'general',
                'url': '/'
            },
            {
                'message': 'Your appointment with Dr. Johnson has been rescheduled to next week.',
                'type': 'appointment',
                'url': '/appointments/2/'
            },
            {
                'message': 'A new relaxation exercise is available. Try the new breathing technique!',
                'type': 'general',
                'url': '/'
            }
        ]
        
        created_count = 0
        for i, notif_data in enumerate(notifications):
            # Create notifications with different timestamps
            created_at = timezone.now() - timedelta(hours=i*2)
            
            notification = Notification.objects.create(
                user=user,
                message=notif_data['message'],
                type=notif_data['type'],
                url=notif_data['url'],
                created_at=created_at,
                read=False,
                dismissed=False
            )
            created_count += 1
            self.stdout.write(
                f'Created notification: {notification.message[:50]}...'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test notifications for {user.username}'
            )
        ) 