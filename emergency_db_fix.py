#!/usr/bin/env python
"""
Emergency Database Fix - Direct SQL Execution
Run this script to create missing database tables directly
"""

import os
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.db import connection

def run_sql_file():
    """Execute the SQL file to create missing tables"""
    sql_file = project_root / 'create_tables.sql'

    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False

    print("📄 Reading SQL file...")
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print("🔧 Executing SQL commands...")
    try:
        with connection.cursor() as cursor:
            # Split SQL into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]

            for statement in statements:
                if statement:
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)

            # Check results
            cursor.execute("""
                SELECT table_name,
                       CASE WHEN table_name IN (
                           SELECT tablename FROM pg_tables WHERE schemaname = 'public'
                       ) THEN 'EXISTS' ELSE 'MISSING' END as status
                FROM (VALUES ('mentalhealth_securedassresult'), ('mentalhealth_dassdataretentionpolicy')) AS t(table_name)
            """)

            results = cursor.fetchall()
            print("\n📊 Table Status:")
            for table_name, status in results:
                print(f"   {table_name}: {status}")

        print("✅ Database fix completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚨 Emergency Database Fix")
    print("=" * 40)

    success = run_sql_file()

    if success:
        print("\n🎉 Try logging in as a student now - the database error should be fixed!")
    else:
        print("\n❌ Fix failed. Check the error messages above.")
        print("You may need to run the SQL commands manually in Railway's database shell.")