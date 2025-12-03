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
    """Create a custom superuser account"""

    print("👤 Creating custom superuser account...")
    print("Please provide the following information:")

    # Get user input
    username = input("Username: ").strip()
    if not username:
        print("❌ Username is required")
        return

    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required")
        return

    password = input("Password: ").strip()
    if not password:
        print("❌ Password is required")
        return

    full_name = input("Full Name: ").strip()
    student_id = input("Student ID (optional): ").strip() or f"ADMIN-{username.upper()}"
    college = input("College (optional): ").strip() or "CBA"
    program = input("Program (optional): ").strip() or "Administration"
    year_level = input("Year Level (optional): ").strip() or "4"
    age_input = input("Age (optional): ").strip()
    age = int(age_input) if age_input.isdigit() else 25
    gender = input("Gender (optional): ").strip() or "Prefer not to say"

    # Check if user already exists
    try:
        existing_user = CustomUser.objects.filter(username=username).first()
        if existing_user:
            print(f"❌ User with username '{username}' already exists")
            return

        existing_email = CustomUser.objects.filter(email=email).first()
        if existing_email:
            print(f"❌ User with email '{email}' already exists")
            return
    except Exception as e:
        print(f"⚠️  Error checking existing users: {e}")

    # Create superuser
    try:
        superuser = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            student_id=student_id,
            college=college,
            program=program,
            year_level=year_level,
            age=age,
            gender=gender
        )

        print("\n✅ Superuser created successfully!")
        print(f"   Username: {superuser.username}")
        print(f"   Email: {superuser.email}")
        print(f"   Full Name: {superuser.full_name}")
        print("   ⚠️  Remember to change the password after first login!")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

        # Try alternative method
        try:
            print("🔄 Trying alternative creation method...")

            # Create user manually
            user = CustomUser(
                username=username,
                email=email,
                full_name=full_name,
                student_id=student_id,
                college=college,
                program=program,
                year_level=year_level,
                age=age,
                gender=gender,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                email_verified=True
            )
            user.set_password(password)
            user.save()

            print("\n✅ Superuser created with alternative method!")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Full Name: {user.full_name}")

        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")

if __name__ == '__main__':
    print("🚀 CalmConnect Superuser Creation Tool")
    print("=" * 40)
    create_superuser()