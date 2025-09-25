#!/usr/bin/env python
"""
Import SQLite data into PostgreSQL database
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
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-decouple not available")

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

try:
    import django
    django.setup()
    print("Django setup successful")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

from django.db import connection

def import_sqlite_data():
    """Import data from SQLite dump file"""
    print("Starting SQLite data import to PostgreSQL")
    print("=" * 50)

    # Read the SQLite dump file
    sqlite_dump_path = BASE_DIR / 'sqlite_dump.sql'
    if not sqlite_dump_path.exists():
        print(f"SQLite dump file not found: {sqlite_dump_path}")
        return False

    try:
        with open(sqlite_dump_path, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()

        print(f"Read SQLite dump file ({len(sql_content)} characters)")

        # Split the SQL content into individual statements
        statements = sql_content.split(';')
        successful_imports = 0
        failed_imports = 0

        with connection.cursor() as cursor:
            for i, statement in enumerate(statements, 1):
                statement = statement.strip()
                if not statement or statement.startswith('BEGIN') or statement.startswith('COMMIT'):
                    continue

                # Skip CREATE TABLE statements (tables already exist)
                if statement.upper().startswith('CREATE TABLE'):
                    continue

                # Skip CREATE INDEX statements
                if statement.upper().startswith('CREATE INDEX'):
                    continue

                # Only process INSERT statements
                if statement.upper().startswith('INSERT INTO'):
                    try:
                        cursor.execute(statement)
                        successful_imports += 1
                        if successful_imports % 10 == 0:
                            print(f"Imported {successful_imports} records...")
                    except Exception as e:
                        failed_imports += 1
                        print(f"Failed to import statement {i}: {str(e)[:100]}...")

        print("Import Summary:")
        print(f"Successful imports: {successful_imports}")
        print(f"Failed imports: {failed_imports}")
        print(f"Total processed: {successful_imports + failed_imports}")

        return successful_imports > 0

    except Exception as e:
        print(f"Error during data import: {e}")
        return False

def verify_import():
    """Verify the imported data"""
    print("Verifying imported data...")

    with connection.cursor() as cursor:
        try:
            # Check key tables
            tables_to_check = [
                'mentalhealth_customuser',
                'mentalhealth_appointment',
                'mentalhealth_counselor',
                'mentalhealth_dassresult',
                'mentalhealth_relaxationlog'
            ]

            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"{table}: {count} records")
                except Exception as e:
                    print(f"Error checking {table}: {e}")

        except Exception as e:
            print(f"Error during verification: {e}")

def main():
    """Main import function"""
    print("Starting SQLite to PostgreSQL Data Import")
    print("=" * 50)

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"PostgreSQL connection: {version[0]}")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False

    # Import data
    if not import_sqlite_data():
        return False

    # Verify import
    verify_import()

    print("=" * 50)
    print("Data import completed!")
    print("Next steps:")
    print("1. Test your application: python manage.py runserver")
    print("2. Check admin interface: http://localhost:8000/admin/")
    print("3. Verify data integrity with your application")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
