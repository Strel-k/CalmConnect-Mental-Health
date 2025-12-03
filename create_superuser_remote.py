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
        # Run migrations with better error handling
        print("Running: python manage.py migrate")
        try:
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Migrations completed successfully!")
        except Exception as migrate_error:
            print(f"⚠️  Migration error: {migrate_error}")
            print("Trying with --fake-initial...")
            try:
                execute_from_command_line(['manage.py', 'migrate', '--fake-initial'])
                print("✅ Migrations completed with --fake-initial!")
            except Exception as fake_error:
                print(f"❌ Migration failed even with --fake-initial: {fake_error}")
                print("Continuing anyway - database might already be migrated...")

        print("🔄 Creating superuser...")
        # Check if superuser already exists
        superusers = CustomUser.objects.filter(is_superuser=True)
        if superusers.exists():
            print("⚠️  Superuser already exists:")
            for user in superusers:
                print(f"   - {user.username} ({user.email})")
            return

        # Create superuser
        username = input("Enter username for superuser [admin]: ").strip() or 'admin'
        email = input("Enter email for superuser [admin@calmconnect.edu.ph]: ").strip() or 'admin@calmconnect.edu.ph'
        password = input("Enter password for superuser [admin123!]: ").strip() or 'admin123!'

        # Generate unique student_id
        base_student_id = 'admin001'
        student_id = base_student_id
        counter = 1
        while CustomUser.objects.filter(student_id=student_id).exists():
            counter += 1
            student_id = f'admin{counter:03d}'

        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name='Administrator',
            age=0,
            gender='Prefer not to say',
            college='CBA',
            program='Administration',
            year_level='4',
            student_id=student_id
        )

        print("✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Student ID: {student_id}")
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