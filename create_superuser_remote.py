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

        # Create superuser directly in database bypassing CustomUser model
        from django.db import connection
        import hashlib
        from django.utils import timezone

        try:
            # Generate password hash
            from django.contrib.auth.hashers import make_password
            hashed_password = make_password(password)

            # Create user directly in auth_user table
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO auth_user (
                        username, email, password, is_staff, is_superuser,
                        is_active, date_joined, first_name, last_name
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (username) DO UPDATE SET
                        email = EXCLUDED.email,
                        password = EXCLUDED.password,
                        is_staff = EXCLUDED.is_staff,
                        is_superuser = EXCLUDED.is_superuser,
                        is_active = EXCLUDED.is_active
                """, [
                    username, email, hashed_password, True, True,
                    True, timezone.now(), 'Admin', 'Administrator'
                ])

            print("✅ Superuser created directly in database!")

            # Try to create minimal CustomUser record if table exists
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO mentalhealth_customuser (
                            user_ptr_id, full_name, age, gender, college,
                            program, year_level, student_id, email_verified
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, [
                        None, 'Administrator', 0, 'Prefer not to say', 'CBA',
                        'Administration', '4', 'admin001', True
                    ])
            except Exception:
                print("⚠️  CustomUser table not fully available - using basic auth user only")

        except Exception as db_error:
            print(f"❌ Direct database creation failed: {db_error}")
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