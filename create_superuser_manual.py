#!/usr/bin/env python3
"""
Manual SQL script to create superuser directly in Railway database
Bypasses all Django migration issues by creating tables and user manually
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

def create_superuser_manual():
    """Create superuser using direct SQL commands"""

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set your Railway DATABASE_URL:")
        print("Windows: set DATABASE_URL=postgresql://user:password@host:port/dbname")
        print("PowerShell: $env:DATABASE_URL = 'postgresql://user:password@host:port/dbname'")
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

        # Create auth_user table if it doesn't exist
        print("🔧 Creating auth_user table...")
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
            print("✅ Auth user table created!")
        except Exception as table_error:
            print(f"⚠️  Table creation failed: {table_error}")
            print("Trying to check if table exists...")
            try:
                cursor.execute("SELECT 1 FROM auth_user LIMIT 1")
                print("✅ Auth user table already exists!")
            except Exception as check_error:
                print(f"❌ Table check failed: {check_error}")
                print("❌ Cannot proceed without auth_user table")
                return

        # Create mentalhealth_customuser table if it doesn't exist
        print("🔧 Creating mentalhealth_customuser table...")
        try:
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
            print("✅ Custom user table created!")
        except Exception as custom_table_error:
            print(f"⚠️  Custom user table creation failed: {custom_table_error}")
            print("Continuing anyway - basic auth user will work...")

        # Check if superuser already exists
        cursor.execute("SELECT username, email FROM auth_user WHERE is_superuser = TRUE")
        existing = cursor.fetchall()
        if existing:
            print("⚠️  Superuser already exists:")
            for user_row in existing:
                print(f"   - {user_row[0]} ({user_row[1]})")
            return

        # Get user input
        username = input("Enter username for superuser [admin]: ").strip() or 'admin'
        email = input("Enter email for superuser [admin@calmconnect.edu.ph]: ").strip() or 'admin@calmconnect.edu.ph'
        password = input("Enter password for superuser [admin123!]: ").strip() or 'admin123!'

        # Hash password using Django's algorithm
        import hashlib
        from datetime import datetime
        algorithm = 'pbkdf2_sha256'
        iterations = 600000
        salt = os.urandom(32).hex()[:32]  # Generate random salt

        # Create PBKDF2 hash
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        hashed_password = f'{algorithm}${iterations}${salt}${hash_obj.hex()}'

        # Insert superuser
        cursor.execute("""
            INSERT INTO auth_user (
                username, email, password, is_staff, is_superuser,
                is_active, date_joined, first_name, last_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                email = EXCLUDED.email,
                password = EXCLUDED.password,
                is_staff = EXCLUDED.is_staff,
                is_superuser = EXCLUDED.is_superuser,
                is_active = EXCLUDED.is_active
        """, [
            username, email, hashed_password, True, True,
            True, datetime.now(), 'Admin', 'Administrator'
        ])

        print("✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print("\n🔐 Access admin panel at: /admin/")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("1. DATABASE_URL is set correctly")
        print("2. Railway database is accessible")
        print("3. You have the external DATABASE_URL (not internal)")

if __name__ == '__main__':
    print("🚀 CalmConnect Manual Superuser Creation Tool")
    print("=" * 50)
    create_superuser_manual()