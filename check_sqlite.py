#!/usr/bin/env python
"""
Check SQLite database contents
"""
import sqlite3
import os

def check_sqlite_contents():
    """Check what's in the SQLite database"""
    print("=== Checking SQLite Database Contents ===")

    if not os.path.exists('db.sqlite3'):
        print("❌ SQLite database file not found")
        return

    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
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

        conn.close()

    except Exception as e:
        print(f"❌ Error checking SQLite database: {e}")

if __name__ == '__main__':
    check_sqlite_contents()
