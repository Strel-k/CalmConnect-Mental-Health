#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import FollowupRequest, Appointment
from datetime import date, time

def schedule_followup():
    try:
        # Get the followup request
        fr = FollowupRequest.objects.get(id=1)
        print(f'FollowupRequest {fr.id} status before: {fr.status}')

        # Create the appointment
        appointment = Appointment.objects.create(
            user=fr.report.user,
            counselor=fr.report.counselor,
            date=date(2025, 11, 28),  # Tomorrow
            time=time(14, 0),  # 2 PM
            session_type='followup',
            services=['Follow-up Session'],
            reason=f'Follow-up: {fr.reason}',
            phone=getattr(fr.report.user, 'phone', ''),
            course_section=getattr(fr.report.user, 'program', ''),
            status='confirmed'
        )

        # Update the followup request
        fr.status = 'scheduled'
        fr.scheduled_date = date(2025, 11, 28)
        fr.scheduled_time = time(14, 0)
        fr.resulting_appointment = appointment
        fr.save()

        print(f'Created appointment {appointment.id} for followup request {fr.id}')
        print(f'Appointment: {appointment.date} {appointment.time}, Status: {appointment.status}')
        print(f'FollowupRequest status after: {fr.status}')

        # Send the scheduled notification
        from mentalhealth.notification_service import create_followup_notification
        create_followup_notification(fr, 'scheduled')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    schedule_followup()