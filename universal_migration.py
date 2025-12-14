#!/usr/bin/env python
"""
Universal Migration Script for CalmConnect
Works with both SQLite and PostgreSQL databases
Automatically detects database type and runs appropriate migrations
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables
try:
    from decouple import AutoConfig
    config = AutoConfig(search_path=str(BASE_DIR))
    # Load database config
    for key in ['DATABASE_URL', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
                'DJANGO_DEBUG', 'DJANGO_SECRET_KEY', 'DJANGO_ALLOWED_HOSTS']:
        value = config(key, default='')
        if value:
            os.environ[key] = str(value)
except ImportError:
    print("[WARN] python-decouple not available, trying python-dotenv...")
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
        print("[OK] Environment variables loaded using python-dotenv")
    except ImportError:
        print("[WARN] Neither python-decouple nor python-dotenv available")

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

def detect_database_type():
    """Detect the database backend type"""
    db_engine = connection.vendor
    print(f"🔍 Detected database type: {db_engine}")
    return db_engine

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ PostgreSQL connection successful: {version[0][:50]}...")
            elif connection.vendor == 'sqlite':
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"✅ SQLite connection successful: {version[0]}")
            else:
                cursor.execute("SELECT 1;")
                print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run Django migrations with appropriate verbosity"""
    try:
        print("🔄 Running Django migrations...")
        # Use higher verbosity for better output
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=1'])
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_missing_tables_sqlite():
    """Create missing tables for SQLite if migrations fail"""
    print("🔧 Attempting to create missing tables for SQLite...")

    try:
        with connection.cursor() as cursor:
            # Create the SecureDASSResult table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
                    dassresult_ptr_id INTEGER NOT NULL PRIMARY KEY REFERENCES mentalhealth_dassresult(id),
                    encrypted_answers TEXT,
                    encrypted_depression_score TEXT,
                    encrypted_anxiety_score TEXT,
                    encrypted_stress_score TEXT,
                    data_hash VARCHAR(64),
                    consent_given BOOLEAN NOT NULL DEFAULT 0,
                    consent_timestamp DATETIME,
                    encryption_version VARCHAR(10) NOT NULL DEFAULT 'v1',
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed DATETIME
                );
            """)

            # Create the DASSDataRetentionPolicy table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentalhealth_dassdataretentionpolicy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES mentalhealth_customuser(id),
                    policy_type VARCHAR(20) NOT NULL DEFAULT 'standard',
                    applied_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    retention_until DATETIME,
                    reason TEXT,
                    approved_by_id INTEGER REFERENCES mentalhealth_customuser(id),
                    UNIQUE(user_id, policy_type)
                );
            """)

            print("✅ Missing tables created for SQLite")
            return True
    except Exception as e:
        print(f"❌ Failed to create tables for SQLite: {e}")
        return False

def create_missing_tables_postgresql():
    """Create missing tables for PostgreSQL if migrations fail"""
    print("🔧 Attempting to create missing tables for PostgreSQL...")

    try:
        with connection.cursor() as cursor:
            # Create sequences if they don't exist
            cursor.execute("CREATE SEQUENCE IF NOT EXISTS mentalhealth_securedassresult_dassresult_ptr_id_seq;")
            cursor.execute("CREATE SEQUENCE IF NOT EXISTS mentalhealth_dassdataretentionpolicy_id_seq;")

            # Create the SecureDASSResult table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
                    dassresult_ptr_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_securedassresult_dassresult_ptr_id_seq'),
                    encrypted_answers TEXT,
                    encrypted_depression_score TEXT,
                    encrypted_anxiety_score TEXT,
                    encrypted_stress_score TEXT,
                    data_hash VARCHAR(64),
                    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
                    consent_timestamp TIMESTAMP WITH TIME ZONE,
                    encryption_version VARCHAR(10) NOT NULL DEFAULT 'v1',
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed TIMESTAMP WITH TIME ZONE
                );
            """)

            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE mentalhealth_securedassresult
                ADD CONSTRAINT mentalhealth_securedassresult_dassresult_ptr_id_fkey
                FOREIGN KEY (dassresult_ptr_id) REFERENCES mentalhealth_dassresult(id);
            """)

            # Create the DASSDataRetentionPolicy table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentalhealth_dassdataretentionpolicy (
                    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_dassdataretentionpolicy_id_seq'),
                    user_id INTEGER NOT NULL,
                    policy_type VARCHAR(20) NOT NULL DEFAULT 'standard',
                    applied_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    retention_until TIMESTAMP WITH TIME ZONE,
                    reason TEXT,
                    approved_by_id INTEGER,
                    CONSTRAINT mentalhealth_dassdataretentionpolicy_user_id_fkey
                        FOREIGN KEY (user_id) REFERENCES mentalhealth_customuser(id),
                    CONSTRAINT mentalhealth_dassdataretentionpolicy_approved_by_id_fkey
                        FOREIGN KEY (approved_by_id) REFERENCES mentalhealth_customuser(id),
                    CONSTRAINT mentalhealth_dassdataretentionpolicy_user_id_policy_type_uniq
                        UNIQUE (user_id, policy_type)
                );
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_access_count_idx ON mentalhealth_securedassresult(access_count);")
            cursor.execute("CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_last_accessed_idx ON mentalhealth_securedassresult(last_accessed);")
            cursor.execute("CREATE INDEX IF NOT EXISTS mentalhealth_dassdataretentionpolicy_user_id_idx ON mentalhealth_dassdataretentionpolicy(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS mentalhealth_dassdataretentionpolicy_approved_by_id_idx ON mentalhealth_dassdataretentionpolicy(approved_by_id);")

            print("✅ Missing tables created for PostgreSQL")
            return True
    except Exception as e:
        print(f"❌ Failed to create tables for PostgreSQL: {e}")
        return False

def show_migration_status():
    """Show current migration status"""
    try:
        print("\n📊 Current migration status:")
        execute_from_command_line(['manage.py', 'showmigrations', 'mentalhealth'])
    except Exception as e:
        print(f"⚠️  Could not show migration status: {e}")

def main():
    """Main migration function"""
    print("🚀 Starting Universal Migration for CalmConnect")
    print("=" * 60)

    # Detect database type
    db_type = detect_database_type()

    # Check database connection
    if not check_database_connection():
        return False

    # Try running migrations first
    if run_migrations():
        print("🎉 Migration completed successfully via Django migrations!")
        show_migration_status()
        return True

    # If migrations fail, try creating missing tables manually
    print("⚠️  Django migrations failed, attempting manual table creation...")

    if db_type == 'sqlite':
        success = create_missing_tables_sqlite()
    elif db_type == 'postgresql':
        success = create_missing_tables_postgresql()
    else:
        print(f"❌ Unsupported database type: {db_type}")
        return False

    if success:
        print("🎉 Manual table creation completed successfully!")
        print("📝 Note: This creates only the missing tables. Full migrations are recommended for production.")
        return True
    else:
        print("❌ All migration methods failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)