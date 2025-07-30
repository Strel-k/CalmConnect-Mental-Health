#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor, CustomUser, Appointment, Report

def check_appointments():
    """Check what appointments are available in the database"""
    print("🔍 Checking appointments in database...")
    
    # Check counselors
    counselors = Counselor.objects.all()
    print(f"👨‍⚕️ Total counselors: {counselors.count()}")
    for counselor in counselors[:3]:  # Show first 3
        print(f"   - {counselor.name}")
    
    # Check appointments by status
    appointments = Appointment.objects.all()
    print(f"\n📅 Total appointments: {appointments.count()}")
    
    status_counts = {}
    for appointment in appointments:
        status = appointment.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   - {status}: {count}")
    
    # Show some sample appointments
    print(f"\n📋 Sample appointments:")
    for appointment in appointments[:5]:
        print(f"   - ID {appointment.id}: {appointment.user.full_name} with {appointment.counselor.name} on {appointment.date} at {appointment.time} (Status: {appointment.status})")
    
    # Check for confirmed appointments specifically
    confirmed_appointments = Appointment.objects.filter(status='confirmed')
    print(f"\n✅ Confirmed appointments: {confirmed_appointments.count()}")
    
    if confirmed_appointments.exists():
        print("   Sample confirmed appointments:")
        for appointment in confirmed_appointments[:3]:
            print(f"   - ID {appointment.id}: {appointment.user.full_name} with {appointment.counselor.name}")
    else:
        print("   ❌ No confirmed appointments found")
        
        # Check what statuses exist
        print("   Available statuses:")
        for status in set(appointments.values_list('status', flat=True)):
            print(f"     - {status}")

if __name__ == "__main__":
    check_appointments() 