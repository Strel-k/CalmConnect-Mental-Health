#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from mentalhealth.models import Counselor

def check_counselor_images():
    """Check which counselors have images uploaded"""
    print("🔍 Checking counselor images...")
    
    counselors = Counselor.objects.all()
    print(f"👨‍⚕️ Total counselors: {counselors.count()}")
    
    counselors_with_images = 0
    counselors_without_images = 0
    
    for counselor in counselors:
        if counselor.image:
            print(f"✅ {counselor.name}: {counselor.image}")
            counselors_with_images += 1
        else:
            print(f"❌ {counselor.name}: No image")
            counselors_without_images += 1
    
    print(f"\n📊 Summary:")
    print(f"   - Counselors with images: {counselors_with_images}")
    print(f"   - Counselors without images: {counselors_without_images}")
    
    if counselors_with_images > 0:
        print(f"\n🎯 The feedback template should now display counselor images correctly!")
        print(f"📧 Test by creating a report and checking the feedback form.")
    else:
        print(f"\n⚠️  No counselors have images uploaded.")
        print(f"📧 The feedback template will show the default image.")

if __name__ == "__main__":
    check_counselor_images() 