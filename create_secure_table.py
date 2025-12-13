#!/usr/bin/env python
"""
Simple script to create the missing SecureDASSResult table
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Setup Django
django.setup()

from django.db import connection

def create_secure_dass_result_table():
    """Create the mentalhealth_securedassresult table manually."""

    sql = """
    CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
        dassresult_ptr_id INTEGER PRIMARY KEY,
        encrypted_answers TEXT,
        encrypted_depression_score TEXT,
        encrypted_anxiety_score TEXT,
        encrypted_stress_score TEXT,
        data_hash VARCHAR(64),
        consent_given BOOLEAN NOT NULL,
        consent_timestamp TIMESTAMP,
        encryption_version VARCHAR(10) NOT NULL,
        access_count INTEGER NOT NULL DEFAULT 0,
        last_accessed TIMESTAMP,
        FOREIGN KEY (dassresult_ptr_id) REFERENCES mentalhealth_dassresult(id)
    );
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print("Successfully created mentalhealth_securedassresult table")
            return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

if __name__ == "__main__":
    print("Creating missing database table...")
    success = create_secure_dass_result_table()
    if success:
        print("Table created successfully!")
    else:
        print("Failed to create table.")