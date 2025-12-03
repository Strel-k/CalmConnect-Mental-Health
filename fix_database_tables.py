#!/usr/bin/env python3
"""
Emergency database table creation script
Creates only the essential tables needed for admin login
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def fix_database_tables():
    """Create essential database tables for admin functionality"""

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Set it with: set DATABASE_URL='your_railway_database_url'")
        return

    print(f"🔗 Connecting to database: {database_url[:50]}...")

    try:
        # Parse DATABASE_URL
        if not database_url.startswith('postgresql://'):
            print("❌ ERROR: DATABASE_URL must be a PostgreSQL URL")
            return

        # Remove postgresql://
        url = database_url[13:]
        user_pass, host_db = url.split('@', 1)
        host_port, dbname = host_db.split('/', 1)

        if ':' in user_pass:
            user, password = user_pass.split(':', 1)
        else:
            user = user_pass
            password = ''

        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host = host_port
            port = 5432

        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("✅ Connected to database successfully!")

        # Create essential tables
        tables_created = 0

        # 1. Create auth_user table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    password VARCHAR(128) NOT NULL,
                    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    first_name VARCHAR(150) NOT NULL DEFAULT '',
                    last_name VARCHAR(150) NOT NULL DEFAULT ''
                )
            """)
            print("✅ auth_user table ready!")
            tables_created += 1
        except Exception as e:
            print(f"❌ Failed to create auth_user: {e}")

        # 2. Create mentalhealth_customuser table (try both possible names)
        try:
            # First try the correct Django table name
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mentalhealth_customuser (
                    user_ptr_id INTEGER PRIMARY KEY REFERENCES auth_user(id) ON DELETE CASCADE,
                    full_name VARCHAR(100) NOT NULL DEFAULT '',
                    age INTEGER NOT NULL DEFAULT 0,
                    gender VARCHAR(20) NOT NULL DEFAULT 'Prefer not to say',
                    college VARCHAR(10) NOT NULL DEFAULT 'CBA',
                    program VARCHAR(100) NOT NULL DEFAULT '',
                    year_level VARCHAR(5) NOT NULL DEFAULT '1',
                    student_id VARCHAR(20) NOT NULL DEFAULT '',
                    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    verification_token VARCHAR(64) DEFAULT NULL,
                    password_reset_token VARCHAR(64) DEFAULT NULL,
                    password_reset_expires TIMESTAMP WITH TIME ZONE NULL,
                    profile_picture VARCHAR(100) DEFAULT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """)
            print("✅ mentalhealth_customuser table ready!")
            tables_created += 1
        except Exception as e:
            print(f"⚠️  mentalhealth_customuser failed: {e}")
            # Try alternative table name that Django might be looking for
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_user (
                        user_ptr_id INTEGER PRIMARY KEY REFERENCES auth_user(id) ON DELETE CASCADE,
                        full_name VARCHAR(100) NOT NULL DEFAULT '',
                        age INTEGER NOT NULL DEFAULT 0,
                        gender VARCHAR(20) NOT NULL DEFAULT 'Prefer not to say',
                        college VARCHAR(10) NOT NULL DEFAULT 'CBA',
                        program VARCHAR(100) NOT NULL DEFAULT '',
                        year_level VARCHAR(5) NOT NULL DEFAULT '1',
                        student_id VARCHAR(20) NOT NULL DEFAULT '',
                        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                        verification_token VARCHAR(64) DEFAULT NULL,
                        password_reset_token VARCHAR(64) DEFAULT NULL,
                        password_reset_expires TIMESTAMP WITH TIME ZONE NULL,
                        profile_picture VARCHAR(100) DEFAULT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """)
                print("✅ custom_user table ready (alternative name)!")
                tables_created += 1
            except Exception as e2:
                print(f"❌ Failed to create custom_user table: {e2}")

        # 3. Create django_session table (for admin sessions)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_session (
                    session_key VARCHAR(40) PRIMARY KEY,
                    session_data TEXT NOT NULL,
                    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            print("✅ django_session table ready!")
            tables_created += 1
        except Exception as e:
            print(f"❌ Failed to create django_session: {e}")

        # 4. Create django_content_type table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_content_type (
                    id SERIAL PRIMARY KEY,
                    app_label VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    UNIQUE(app_label, model)
                )
            """)
            print("✅ django_content_type table ready!")
            tables_created += 1
        except Exception as e:
            print(f"❌ Failed to create django_content_type: {e}")

        print(f"\n🎯 Created {tables_created} essential tables!")

        # Check if superuser exists
        try:
            cursor.execute("SELECT username FROM auth_user WHERE is_superuser = TRUE LIMIT 1")
            existing = cursor.fetchone()
            if existing:
                print(f"✅ Superuser already exists: {existing[0]}")
            else:
                print("⚠️  No superuser found - run create_superuser_manual.py to create one")
        except Exception as e:
            print(f"⚠️  Could not check for superuser: {e}")

        cursor.close()
        conn.close()

        print("\n🎉 Database tables are ready!")
        print("Try accessing the admin panel now: /admin/")

    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\n💡 Make sure:")
        print("1. DATABASE_URL is correct")
        print("2. Railway database is accessible")
        print("3. You have the external DATABASE_URL")

if __name__ == '__main__':
    print("🔧 CalmConnect Database Table Fix Tool")
    print("=" * 45)
    fix_database_tables()