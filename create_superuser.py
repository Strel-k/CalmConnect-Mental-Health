#!/usr/bin/env python3
"""
Create a superuser programmatically
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from mentalhealth.models import CustomUser

def create_superuser():
    """Create a superuser account"""

    print("👤 Creating superuser account...")

    # Check if superuser already exists
    try:
        existing_superuser = CustomUser.objects.filter(is_superuser=True).first()
        if existing_superuser:
            print(f"✅ Superuser already exists: {existing_superuser.username}")
            print(f"   Email: {existing_superuser.email}")
            return
    except Exception as e:
        print(f"⚠️  Error checking existing superusers: {e}")

    # Create superuser
    try:
        superuser = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@calmconnect.com',
            password='admin123',
            full_name='System Administrator',
            student_id='ADMIN001',
            college='CBA',
            program='Administration',
            year_level='4',
            age=25,
            gender='Prefer not to say'
        )

        print("✅ Superuser created successfully!")
        print(f"   Username: {superuser.username}")
        print(f"   Email: {superuser.email}")
        print(f"   Password: admin123")
        print("   ⚠️  Remember to change the password after first login!")

    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

        # Try alternative method
        try:
            print("🔄 Trying alternative creation method...")

            # Create user manually
            user = CustomUser(
                username='admin',
                email='admin@calmconnect.com',
                full_name='System Administrator',
                student_id='ADMIN001',
                college='CBA',
                program='Administration',
                year_level='4',
                age=25,
                gender='Prefer not to say',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                email_verified=True
            )
            user.set_password('admin123')
            user.save()

            print("✅ Superuser created with alternative method!")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password: admin123")

        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")

if __name__ == '__main__':
    print("🚀 CalmConnect Superuser Creation Tool")
    print("=" * 40)
    create_superuser()