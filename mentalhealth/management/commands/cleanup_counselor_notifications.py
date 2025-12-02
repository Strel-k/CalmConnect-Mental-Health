#!/usr/bin/env python
"""
Management command to clean up incorrect counselor notifications.
Removes admin notifications sent to counselors for followup requests they don't own.
"""

from django.core.management.base import BaseCommand
from mentalhealth.models import Notification, FollowupRequest


class Command(BaseCommand):
    help = 'Clean up incorrect counselor notifications for followup requests they don\'t own'

    def handle(self, *args, **options):
        # Find all notifications where:
        # 1. User is a counselor (has counselor_profile)
        # 2. Notification is about a followup request
        # 3. The followup request doesn't belong to this counselor

        counselors_with_wrong_notifications = []

        # Get all counselor users
        from django.contrib.auth import get_user_model
        User = get_user_model()
        counselor_users = User.objects.filter(counselor_profile__isnull=False)

        for counselor_user in counselor_users:
            counselor = counselor_user.counselor_profile

            # Get all followup notifications for this counselor
            followup_notifications = Notification.objects.filter(
                user=counselor_user,
                type='followup'
            )

            wrong_notifications = []
            for notif in followup_notifications:
                # Check if this is an admin notification (user_type='admin' in metadata)
                metadata = notif.metadata or {}
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}

                user_type = metadata.get('user_type')
                followup_request_id = metadata.get('followup_request_id')

                # Check if this notification is for a followup request the counselor doesn't own
                if followup_request_id:
                    try:
                        followup_request = FollowupRequest.objects.get(id=followup_request_id)
                        # If this is an admin notification (user_type='admin') or no user_type specified (old notifications)
                        # and the counselor doesn't own this followup request
                        if followup_request.report.counselor != counselor and \
                           (user_type == 'admin' or user_type is None):
                            # This counselor doesn't own this followup request - wrong notification
                            wrong_notifications.append(notif)
                    except FollowupRequest.DoesNotExist:
                        # Followup request doesn't exist - wrong notification
                        wrong_notifications.append(notif)

            if wrong_notifications:
                counselors_with_wrong_notifications.append((counselor_user, wrong_notifications))

        # Report and clean up
        total_cleaned = 0
        for counselor_user, wrong_notifications in counselors_with_wrong_notifications:
            self.stdout.write(
                self.style.WARNING(
                    f'Counselor {counselor_user.username} has {len(wrong_notifications)} incorrect notifications'
                )
            )

            for notif in wrong_notifications:
                metadata = notif.metadata or {}
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                followup_id = metadata.get('followup_request_id', 'unknown')
                self.stdout.write(f'  - Deleting notification {notif.id} for followup_request {followup_id}')
                notif.delete()
                total_cleaned += 1

        if total_cleaned > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up {total_cleaned} incorrect notifications')
            )
        else:
            self.stdout.write('No incorrect notifications found')