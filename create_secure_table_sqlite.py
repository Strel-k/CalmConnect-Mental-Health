#!/usr/bin/env python
"""
Script to manually create the mentalhealth_securedassresult table in SQLite.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django - mimic manage.py behavior
project_root = Path(__file__).parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Set sys.argv to trick Django into thinking we're running a management command
sys.argv = ['manage.py', 'shell']

django.setup()

from django.db import connection

def create_secure_dass_result_table():
    """Create the mentalhealth_securedassresult table manually for SQLite."""

    sql = """
    CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
        dassresult_ptr_id INTEGER NOT NULL PRIMARY KEY,
        encrypted_answers TEXT,
        encrypted_depression_score TEXT,
        encrypted_anxiety_score TEXT,
        encrypted_stress_score TEXT,
        data_hash VARCHAR(64),
        consent_given BOOLEAN NOT NULL DEFAULT 0,
        consent_timestamp DATETIME,
        encryption_version VARCHAR(10) NOT NULL DEFAULT 'v1',
        access_count INTEGER NOT NULL DEFAULT 0,
        last_accessed DATETIME,
        FOREIGN KEY (dassresult_ptr_id) REFERENCES mentalhealth_dassresult(id) DEFERRABLE INITIALLY DEFERRED
    );
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print("Successfully created mentalhealth_securedassresult table")
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

    # Create indexes separately
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_access_count_idx
                ON mentalhealth_securedassresult(access_count)
            """)
            print("Successfully created access_count index")

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_last_accessed_idx
                ON mentalhealth_securedassresult(last_accessed)
            """)
            print("Successfully created last_accessed index")
    except Exception as e:
        print(f"Error creating indexes: {e}")

    return True

if __name__ == "__main__":
    print("Creating mentalhealth_securedassresult table for SQLite...")

    success = create_secure_dass_result_table()

    if success:
        print("\nTable created successfully!")
        print("Try logging in as a student now - the database error should be fixed!")
    else:
        print("\nTable creation failed.")