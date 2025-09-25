#!/usr/bin/env python
"""
Check PostgreSQL database contents after migration
"""
import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
try:
    from decouple import AutoConfig
    config = AutoConfig(search_path=str(BASE_DIR))
    for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
                'DJANGO_DEBUG', 'DJANGO_SECRET_KEY', 'DJANGO_ALLOWED_HOSTS',
                'OPENAI_API_KEY', 'EMAIL_HOST', 'EMAIL_HOST_USER',
                'EMAIL_HOST_PASSWORD', 'EMAIL_PORT', 'SESSION_COOKIE_AGE']:
        value = config(key, default='')
        if value:
            os.environ[key] = str(value)
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-decouple not available")

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.db import connection

def check_database_contents():
    """Check what's actually in the PostgreSQL database"""
    print("\n=== Checking PostgreSQL Database Contents ===")

    with connection.cursor() as cursor:
        try:
            # Check all tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"\n📊 Total tables: {len(tables)}")

            # Separate Django tables from app tables
            django_tables = []
            app_tables = []

            for table in tables:
                table_name = table[0]
                if table_name.startswith(('django_', 'auth_', 'contenttypes_')):
                    django_tables.append(table_name)
                else:
                    app_tables.append(table_name)

            print(f"🔧 Django system tables: {len(django_tables)}")
            print(f"📱 Application tables: {len(app_tables)}")

            # Check mental health tables specifically
            mentalhealth_tables = [t for t in app_tables if t.startswith('mentalhealth_')]
            print(f"\n🧠 Mental Health tables: {len(mentalhealth_tables)}")
            for table in mentalhealth_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table}: {count} records")
                except Exception as e:
                    print(f"  - {table}: Error - {e}")

            # Check other app tables
            other_tables = [t for t in app_tables if not t.startswith('mentalhealth_')]
            if other_tables:
                print(f"\n📋 Other application tables: {len(other_tables)}")
                for table in other_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"  - {table}: {count} records")
                    except Exception as e:
                        print(f"  - {table}: Error - {e}")

            # Show sample data from key tables
            print("\nSample Data Check:")
            sample_tables = ['mentalhealth_customuser', 'mentalhealth_appointment', 'mentalhealth_counselor']

            for table in sample_tables:
                if table in mentalhealth_tables:
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        rows = cursor.fetchall()
                        print(f"\n  {table} (first 3 rows):")
                        if rows:
                            for i, row in enumerate(rows, 1):
                                print(f"    Row {i}: {row}")
                        else:
                            print("    No data found")
                    except Exception as e:
                        print(f"    Error checking {table}: {e}")

        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == '__main__':
    check_database_contents()
