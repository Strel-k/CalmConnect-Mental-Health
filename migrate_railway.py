#!/usr/bin/env python
"""
Railway Database Migration Script
Runs Django migrations on Railway PostgreSQL database.
This script can be run directly on Railway to apply pending migrations.
"""

import os
import sys
import django
from pathlib import Path

def main():
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

    print("🚀 Starting Railway Database Migration...")

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
        print("=" * 50)

        # Run migrations with verbosity
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])

        print("=" * 50)
        print("✅ All migrations completed successfully!")

        # Show current migration status
        print("\n📊 Current migration status:")
        execute_from_command_line(['manage.py', 'showmigrations', 'mentalhealth'])

        # Verify the securedassresult table exists
        print("\n🔍 Verifying SecureDASSResult table...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'mentalhealth_securedassresult'
                );
            """)
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("✅ mentalhealth_securedassresult table exists")
            else:
                print("❌ mentalhealth_securedassresult table NOT found")

        print("\n🎉 Database migration completed successfully!")
        print("Your Railway app should now work without the ProgrammingError.")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()