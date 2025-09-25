#!/usr/bin/env python
"""
SQLite to PostgreSQL Migration Script for CalmConnect

This script helps migrate data from SQLite to PostgreSQL database.
Run this after setting up PostgreSQL and configuring environment variables.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
try:
    from decouple import AutoConfig
    config = AutoConfig(search_path=str(BASE_DIR))
    # Set environment variables from .env file
    for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
                'DJANGO_DEBUG', 'DJANGO_SECRET_KEY', 'DJANGO_ALLOWED_HOSTS',
                'OPENAI_API_KEY', 'EMAIL_HOST', 'EMAIL_HOST_USER',
                'EMAIL_HOST_PASSWORD', 'EMAIL_PORT', 'SESSION_COOKIE_AGE']:
        value = config(key, default='')
        if value:
            os.environ[key] = str(value)
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-decouple not available, trying python-dotenv...")
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
        print("✅ Environment variables loaded using python-dotenv")
    except ImportError:
        print("⚠️  Neither python-decouple nor python-dotenv available")
        print("Please install one: pip install python-decouple OR pip install python-dotenv")

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.core.management import execute_from_command_line
from django.db import connection

def check_database_connection():
    """Check if PostgreSQL connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL connection successful: {version[0]}")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        print("🔄 Running Django migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create a superuser for the admin interface"""
    try:
        print("👤 Creating superuser...")
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput', '--username', 'admin', '--email', 'admin@example.com'])
        print("✅ Superuser created successfully")
        return True
    except Exception as e:
        print(f"⚠️  Superuser creation failed (might already exist): {e}")
        return True  # Not a critical error

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL Migration for CalmConnect")
    print("=" * 60)

    # Check environment variables
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment variables.")
        print("\nRequired .env file content:")
        print("""
# Database Configuration
DB_NAME=calmconnect_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
        """)
        return False

    # Check database connection
    if not check_database_connection():
        return False

    # Run migrations
    if not run_migrations():
        return False

    # Create superuser
    create_superuser()

    print("=" * 60)
    print("🎉 Migration completed successfully!")
    print("📝 Next steps:")
    print("   1. Visit http://localhost:8000/admin/ to access Django admin")
    print("   2. Create your admin user if not already created")
    print("   3. Test your application functionality")
    print("   4. Update your production settings")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
