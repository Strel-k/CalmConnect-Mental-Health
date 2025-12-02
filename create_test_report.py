#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Report, Counselor, CustomUser
from django.utils import timezone

def create_test_report():
    print("=== CREATING TEST REPORT ===")

    # Get Lucius Fox counselor
    counselor = Counselor.objects.filter(name='Lucius Fox', is_active=True).first()
    if not counselor:
        print("Lucius Fox counselor not found!")
        return

    print(f"Found counselor: {counselor.name}")

    # Get a test user (or create one)
    user = CustomUser.objects.filter(username__icontains='test').first()
    if not user:
        user = CustomUser.objects.filter(is_staff=False).first()

    if not user:
        print("No suitable user found for report")
        return

    print(f"Using user: {user.username}")

    # Create a pending report
    report = Report.objects.create(
        title="Test Pending Report",
        description="This is a test report to verify the counselor dashboard displays pending reports correctly.",
        counselor=counselor,
        user=user,
        status='pending',
        report_type='session'
    )

    print(f"Created report: {report.title} (ID: {report.id})")
    print(f"Report status: {report.status}")
    print(f"Report counselor: {report.counselor.name}")

    # Verify the report was created
    pending_reports = Report.objects.filter(counselor=counselor, status='pending')
    print(f"Total pending reports for {counselor.name}: {pending_reports.count()}")

if __name__ == '__main__':
    create_test_report()