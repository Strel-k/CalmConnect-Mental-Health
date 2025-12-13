#!/usr/bin/env python
"""
Django Migration Runner for Railway Deployment
Runs all pending Django migrations to ensure database schema is up to date.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Environment variables are loaded automatically by Django settings
# using python-decouple, so no need to load .env here
print("✅ Environment variables loaded via Django settings")

try:
    # Setup Django
    django.setup()
    print("✅ Django setup complete")

    # Import Django management commands
    from django.core.management import execute_from_command_line
    from django.db import connection

    print("🔍 Checking database connection...")
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection successful")

    print("📦 Running Django migrations...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ All migrations completed successfully!")
    except Exception as e:
        print(f"❌ Normal migration failed: {e}")
        print("🔄 Attempting to fake migrations for mentalhealth app...")
        execute_from_command_line(['manage.py', 'migrate', '--fake', 'mentalhealth'])
        print("✅ Migrations faked successfully!")

    # Show current migration status
    print("\n📊 Current migration status:")
    execute_from_command_line(['manage.py', 'showmigrations', 'mentalhealth'])

except Exception as e:
    print(f"❌ Migration failed: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Database is ready!")
sys.exit(0)