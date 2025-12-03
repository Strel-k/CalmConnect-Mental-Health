#!/usr/bin/env python3
"""
Script to run migrations and create a superuser directly in Railway database
Run this locally to migrate database and create admin user in production database
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from mentalhealth.models import CustomUser

def create_superuser_remote():
    """Run migrations and create superuser in remote Railway database"""

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set your Railway DATABASE_URL:")
        print("Windows: set DATABASE_URL=postgresql://user:password@host:port/dbname")
        print("PowerShell: $env:DATABASE_URL = 'postgresql://user:password@host:port/dbname'")
        return

    print(f"🔗 Connecting to database: {database_url[:50]}...")
    print("📦 Running database migrations first...")

    try:
        # Run specific missing migrations
        print("🔧 Running specific missing migrations...")
        try:
            # Try to run the password reset migration specifically
            execute_from_command_line(['manage.py', 'migrate', 'mentalhealth', '0027'])
            print("✅ Password reset migration completed!")
        except Exception as e:
            print(f"⚠️  Migration 0027 failed: {e}")
            print("Trying to run all remaining migrations...")
            try:
                execute_from_command_line(['manage.py', 'migrate', '--fake-initial'])
                print("✅ Remaining migrations completed with --fake-initial!")
            except Exception as e2:
                print(f"⚠️  All migrations failed: {e2}")
                print("Continuing with superuser creation anyway...")

        print("🔄 Creating superuser...")
        # Check if superuser already exists
        superusers = CustomUser.objects.filter(is_superuser=True)
        if superusers.exists():
            print("⚠️  Superuser already exists:")
            for user in superusers:
                print(f"   - {user.username} ({user.email})")
            return

        # Create superuser with minimal required fields
        username = input("Enter username for superuser [admin]: ").strip() or 'admin'
        email = input("Enter email for superuser [admin@calmconnect.edu.ph]: ").strip() or 'admin@calmconnect.edu.ph'
        password = input("Enter password for superuser [admin123!]: ").strip() or 'admin123!'

        # Try to create superuser with minimal fields first
        try:
            # Create basic user first
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=True
            )

            # Set additional fields if they exist
            try:
                user.full_name = 'Administrator'
                user.age = 0
                user.gender = 'Prefer not to say'
                user.college = 'CBA'
                user.program = 'Administration'
                user.year_level = '4'
                user.student_id = 'admin001'
                user.email_verified = True
                user.save()
            except Exception as field_error:
                print(f"⚠️  Some additional fields couldn't be set: {field_error}")
                print("Superuser created with basic fields only.")

        except Exception as create_error:
            print(f"❌ Error creating superuser: {create_error}")
            print("Trying alternative approach...")

            # Alternative: Use Django management command
            from django.core.management import call_command
            try:
                call_command('createsuperuser', '--username', username, '--email', email, '--noinput')
                # Set password separately
                user = CustomUser.objects.get(username=username)
                user.set_password(password)
                user.save()
                print("✅ Superuser created using management command!")
            except Exception as cmd_error:
                print(f"❌ Management command also failed: {cmd_error}")
                return

        print("✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        try:
            student_id = getattr(user, 'student_id', 'N/A')
            print(f"   Student ID: {student_id}")
        except:
            print("   Student ID: N/A (basic user created)")
        print("\n🔐 Access admin panel at: /admin/")

    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        print("\n💡 Possible solutions:")
        print("1. Run database migrations first: python manage.py migrate")
        print("2. Check your DATABASE_URL is correct")
        print("3. Ensure Railway database is accessible")

if __name__ == '__main__':
    print("🚀 CalmConnect Superuser Creation Tool")
    print("=" * 40)
    create_superuser_remote()