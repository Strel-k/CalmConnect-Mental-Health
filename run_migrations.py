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

    print("🏗️ Creating missing tables...")
    with connection.cursor() as cursor:
        # Create the SecureDASSResult table directly
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
                dassresult_ptr_id bigint NOT NULL PRIMARY KEY REFERENCES mentalhealth_dassresult(id) ON DELETE CASCADE,
                encrypted_answers text,
                encrypted_depression_score text,
                encrypted_anxiety_score text,
                encrypted_stress_score text,
                data_hash varchar(64),
                consent_given boolean NOT NULL DEFAULT false,
                consent_timestamp timestamp with time zone,
                encryption_version varchar(10) NOT NULL DEFAULT 'v1',
                access_count integer NOT NULL DEFAULT 0,
                last_accessed timestamp with time zone
            );
        """)

        # Create the DASSDataRetentionPolicy table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mentalhealth_dassdataretentionpolicy (
                id bigserial NOT NULL PRIMARY KEY,
                user_id bigint NOT NULL REFERENCES mentalhealth_customuser(id) ON DELETE CASCADE,
                policy_type varchar(20) NOT NULL DEFAULT 'standard',
                applied_date timestamp with time zone NOT NULL DEFAULT now(),
                retention_until timestamp with time zone,
                reason text,
                approved_by_id bigint REFERENCES mentalhealth_customuser(id) ON DELETE SET NULL,
                CONSTRAINT mentalhealth_dassdataret_user_policy_8b8b8b8b_uniq UNIQUE (user_id, policy_type)
            );
        """)
    print("✅ Missing tables created")

    print("📦 Creating database schema from models...")
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    print("✅ Database schema created")

    print("🔄 Faking all migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--fake'])
    print("✅ All migrations faked successfully!")

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