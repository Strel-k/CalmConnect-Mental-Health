#!/usr/bin/env python3
"""
Fix existing schema by adding missing columns to make it compatible with Django
"""

import os
import psycopg2

def fix_schema():
    """Add missing columns to existing tables to make them Django-compatible"""

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        return

    print(f"🔗 Connecting to database: {database_url[:50]}...")

    try:
        # Parse DATABASE_URL
        if not database_url.startswith('postgresql://'):
            print("❌ ERROR: DATABASE_URL must be a PostgreSQL URL")
            return

        url = database_url[13:]
        if '@' not in url:
            print("❌ ERROR: DATABASE_URL missing '@' separator")
            return

        user_pass, host_db = url.split('@', 1)
        if '/' not in host_db:
            print("❌ ERROR: DATABASE_URL missing '/' separator for database name")
            return

        host_port, dbname = host_db.split('/', 1)

        if ':' in user_pass:
            user, password = user_pass.split(':', 1)
        else:
            user = user_pass
            password = ''

        if ':' in host_port:
            host, port_str = host_port.split(':', 1)
            port = int(port_str)
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

        # Check what tables exist
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Existing tables: {existing_tables}")

        # Define the schema fixes needed
        schema_fixes = []

        # Fix custom_user table - add missing Django User fields
        if 'custom_user' in existing_tables:
            print("🔧 Fixing custom_user table...")

            # Check what columns exist in custom_user
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'custom_user'
                ORDER BY column_name
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            print(f"   Existing columns: {existing_columns}")

            # Add missing columns for Django User compatibility
            missing_columns = {
                'password_reset_token': 'VARCHAR(255)',
                'password_reset_expires': 'TIMESTAMP WITH TIME ZONE',
                'email_verified': 'BOOLEAN DEFAULT FALSE',
                'verification_token': 'VARCHAR(255)',
                'force_password_change': 'BOOLEAN DEFAULT FALSE',
                'profile_picture': 'VARCHAR(100)',
                'student_id': 'VARCHAR(20)',
                'full_name': 'VARCHAR(150)',
                'college': 'VARCHAR(10)',
                'program': 'VARCHAR(100)',
                'year_level': 'VARCHAR(10)',
                'age': 'INTEGER',
                'gender': 'VARCHAR(20)',
                'phone': 'VARCHAR(15)',
                'bio': 'TEXT',
                'is_active': 'BOOLEAN DEFAULT TRUE',
                'is_staff': 'BOOLEAN DEFAULT FALSE',
                'is_superuser': 'BOOLEAN DEFAULT FALSE',
                'date_joined': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
                'last_login': 'TIMESTAMP WITH TIME ZONE'
            }

            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE custom_user ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
                        print(f"   ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"   ⚠️  Error adding {col_name}: {str(e)[:50]}")

        # Fix mentalhealth_appointment table
        if 'mentalhealth_appointment' in existing_tables:
            print("🔧 Fixing mentalhealth_appointment table...")

            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'mentalhealth_appointment'
                ORDER BY column_name
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]

            missing_columns = {
                'video_call_url': 'VARCHAR(500)',
                'cancellation_token': 'VARCHAR(255)',
                'cancellation_deadline': 'TIMESTAMP WITH TIME ZONE',
                'cancellation_reason': 'TEXT',
                'notes': 'TEXT',
                'session_type': "VARCHAR(20) DEFAULT 'face_to_face'",
                'status': "VARCHAR(20) DEFAULT 'pending'",
                'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
                'updated_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }

            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE mentalhealth_appointment ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
                        print(f"   ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"   ⚠️  Error adding {col_name}: {str(e)[:50]}")

        # Fix mentalhealth_counselor table
        if 'mentalhealth_counselor' in existing_tables:
            print("🔧 Fixing mentalhealth_counselor table...")

            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'mentalhealth_counselor'
                ORDER BY column_name
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]

            missing_columns = {
                'email': 'VARCHAR(254)',
                'unit': 'VARCHAR(100)',
                'rank': 'VARCHAR(100)',
                'is_active': 'BOOLEAN DEFAULT TRUE',
                'bio': 'TEXT',
                'image': 'VARCHAR(100)',
                'available_days': 'JSONB DEFAULT \'[]\'',
                'available_start_time': 'TIME',
                'available_end_time': 'TIME',
                'day_schedules': 'JSONB DEFAULT \'{}\'',
                'user_id': 'INTEGER'
            }

            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE mentalhealth_counselor ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
                        print(f"   ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"   ⚠️  Error adding {col_name}: {str(e)[:50]}")

        # Fix mentalhealth_dassresult table
        if 'mentalhealth_dassresult' in existing_tables:
            print("🔧 Fixing mentalhealth_dassresult table...")

            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'mentalhealth_dassresult'
                ORDER BY column_name
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]

            missing_columns = {
                'is_followup': 'BOOLEAN DEFAULT FALSE',
                'followup_appointment_id': 'INTEGER',
                'wellbeing_progress': 'INTEGER',
                'symptoms_progress': 'INTEGER',
                'strategies_progress': 'INTEGER',
                'mood_change': 'VARCHAR(50)',
                'practice_frequency': 'VARCHAR(50)',
                'helpful_things': 'TEXT',
                'new_challenges': 'TEXT',
                'challenges_description': 'TEXT',
                'future_session_preference': 'VARCHAR(50)',
                'future_focus': 'TEXT'
            }

            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE mentalhealth_dassresult ADD COLUMN IF NOT EXISTS {col_name} {col_type}')
                        print(f"   ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"   ⚠️  Error adding {col_name}: {str(e)[:50]}")

        # Add any missing Django core tables
        django_tables = {
            'django_migrations': """
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id SERIAL PRIMARY KEY,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """,
            'django_content_type': """
                CREATE TABLE IF NOT EXISTS django_content_type (
                    id SERIAL PRIMARY KEY,
                    app_label VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    UNIQUE(app_label, model)
                )
            """,
            'auth_permission': """
                CREATE TABLE IF NOT EXISTS auth_permission (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id),
                    codename VARCHAR(100) NOT NULL,
                    UNIQUE(content_type_id, codename)
                )
            """,
            'auth_group': """
                CREATE TABLE IF NOT EXISTS auth_group (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL UNIQUE
                )
            """,
            'auth_group_permissions': """
                CREATE TABLE IF NOT EXISTS auth_group_permissions (
                    id SERIAL PRIMARY KEY,
                    group_id INTEGER NOT NULL REFERENCES auth_group(id),
                    permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
                    UNIQUE(group_id, permission_id)
                )
            """,
            'django_session': """
                CREATE TABLE IF NOT EXISTS django_session (
                    session_key VARCHAR(40) PRIMARY KEY,
                    session_data TEXT NOT NULL,
                    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """
        }

        print("🔧 Adding missing Django core tables...")
        for table_name, create_sql in django_tables.items():
            if table_name not in existing_tables:
                try:
                    cursor.execute(create_sql)
                    print(f"   ✅ Created table: {table_name}")
                except Exception as e:
                    print(f"   ⚠️  Error creating {table_name}: {str(e)[:50]}")

        # Populate django_migrations table with applied migrations
        try:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES
                    ('contenttypes', '0001_initial', NOW()),
                    ('auth', '0001_initial', NOW()),
                    ('admin', '0001_initial', NOW()),
                    ('sessions', '0001_initial', NOW()),
                    ('mentalhealth', '0001_initial', NOW())
                ON CONFLICT DO NOTHING
            """)
            print("✅ Populated django_migrations table")
        except Exception as e:
            print(f"⚠️  Error populating migrations: {str(e)[:50]}")

        print("\n🎉 Schema fixes completed!")
        print("Your database should now be compatible with Django.")

        # Test by trying to query the user table
        try:
            cursor.execute("SELECT COUNT(*) FROM custom_user WHERE is_superuser = TRUE")
            superuser_count = cursor.fetchone()[0]
            print(f"✅ Found {superuser_count} superusers in database")
        except Exception as e:
            print(f"⚠️  Test query failed: {str(e)[:50]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    print("🔧 CalmConnect Schema Fix Tool")
    print("=" * 35)
    fix_schema()