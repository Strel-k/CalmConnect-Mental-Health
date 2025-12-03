#!/usr/bin/env python3
"""
Clean up Railway PostgreSQL database and prepare for proper Django migrations
Drops all tables created from SQLite dump so Django can create proper schema
"""

import os
import psycopg2
import re
from pathlib import Path

def convert_sqlite_to_postgres(sql_content):
    """Convert SQLite SQL to PostgreSQL compatible format"""

    # Replace SQLite-specific syntax with PostgreSQL equivalents
    conversions = [
        # Remove SQLite-specific pragmas and settings
        (r'PRAGMA.*;', ''),
        (r'BEGIN TRANSACTION;', ''),
        (r'COMMIT;', ''),

        # Convert AUTOINCREMENT to SERIAL
        (r'\bAUTOINCREMENT\b', 'SERIAL'),

        # Convert INTEGER PRIMARY KEY to SERIAL PRIMARY KEY for auto-increment
        (r'(\w+)\s+INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', r'\1 SERIAL PRIMARY KEY'),

        # Convert SQLite boolean values
        (r'\bTRUE\b', 'true'),
        (r'\bFALSE\b', 'false'),

        # Handle SQLite's replace() function calls
        (r"replace\('([^']*)',\s*'([^']*)',\s*char\(10\)\)", r"replace(\1, \2, '\n')"),

        # Convert datetime to timestamp (PostgreSQL doesn't have datetime type)
        (r'\bdatetime\b', 'timestamp'),

        # Remove unsigned from integers (PostgreSQL doesn't support unsigned)
        (r'\binteger unsigned\b', 'integer'),
        (r'\bsmallint unsigned\b', 'smallint'),

        # Convert SQLite's "datetime" fields to "timestamp"
        (r'"date_taken"\s+datetime', '"date_taken" timestamp'),
        (r'"applied"\s+datetime', '"applied" timestamp'),
        (r'"timestamp"\s+datetime', '"timestamp" timestamp'),
        (r'"created_at"\s+datetime', '"created_at" timestamp'),
        (r'"updated_at"\s+datetime', '"updated_at" timestamp'),
        (r'"submitted_at"\s+datetime', '"submitted_at" timestamp'),
        (r'"scheduled_start"\s+datetime', '"scheduled_start" timestamp'),
        (r'"scheduled_end"\s+datetime', '"scheduled_end" timestamp'),
        (r'"joined_at"\s+datetime', '"joined_at" timestamp'),
        (r'"left_at"\s+datetime', '"left_at" timestamp'),
        (r'"expires_at"\s+datetime', '"expires_at" timestamp'),
        (r'"approved_denied_at"\s+datetime', '"approved_denied_at" timestamp'),
        (r'"cancelled_at"\s+datetime', '"cancelled_at" timestamp'),
        (r'"date"\s+datetime', '"date" date'),
        (r'"time"\s+datetime', '"time" time'),

        # Remove table creation for sqlite_sequence (PostgreSQL handles this differently)
        (r'CREATE TABLE sqlite_sequence.*?\);', ''),

        # Remove INSERT into sqlite_sequence
        (r'INSERT INTO sqlite_sequence VALUES.*;', ''),

        # Handle JSON_VALID function - PostgreSQL doesn't have this
        # Remove the CHECK constraint for JSON fields
        (r'CHECK \(\(JSON_VALID\("(\w+)"\) OR "\1" IS NULL\)\)', ''),

        # Convert UNIQUE constraints
        (r'UNIQUE\("([^"]+)"\)', r'UNIQUE (\1)'),

        # Handle foreign key constraints - make them DEFERRABLE
        (r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', r'REFERENCES \1(\2) DEFERRABLE INITIALLY DEFERRED'),
    ]

    result = sql_content
    for pattern, replacement in conversions:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

    return result

def cleanup_database():
    """Clean up Railway PostgreSQL database by dropping all tables"""

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Set it with: set DATABASE_URL='your_railway_database_url'")
        return

    print(f"🔗 Connecting to database: {database_url[:50]}...")

    try:
        # Parse DATABASE_URL (same parsing logic as before)
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

        # Get all tables in public schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        table_names = [row[0] for row in tables]

        if not table_names:
            print("ℹ️  No tables found in database - already clean!")
            cursor.close()
            conn.close()
            return

        print(f"🗑️  Found {len(table_names)} tables to drop:")
        for table in table_names:
            print(f"   - {table}")

        # Drop all tables with CASCADE to handle dependencies
        dropped = 0
        errors = 0

        # First, disable all constraints and triggers
        try:
            cursor.execute("""
                SELECT 'ALTER TABLE ' || schemaname || '."' || tablename || '" DISABLE TRIGGER ALL;'
                FROM pg_tables
                WHERE schemaname = 'public'
            """)
            trigger_commands = cursor.fetchall()
            for cmd in trigger_commands:
                try:
                    cursor.execute(cmd[0])
                except:
                    pass
        except:
            pass

        # Drop all tables
        for table_name in table_names:
            try:
                # Use CASCADE to drop dependent objects
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                dropped += 1
                print(f"✅ Dropped table: {table_name}")
            except Exception as e:
                errors += 1
                print(f"⚠️  Error dropping {table_name}: {str(e)[:50]}")

        # Also drop any remaining sequences, indexes, etc.
        try:
            cursor.execute("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO postgres;
                GRANT ALL ON SCHEMA public TO public;
            """)
            print("✅ Dropped and recreated public schema")
        except Exception as e:
            print(f"⚠️  Schema recreation failed: {str(e)[:50]}")

        print(f"\n🧹 Cleanup completed!")
        print(f"✅ Successfully dropped: {dropped} tables")

        # Verify cleanup
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        remaining = cursor.fetchone()[0]

        if remaining == 0:
            print("✅ Database is now clean - ready for Django migrations!")
        else:
            print(f"⚠️  {remaining} tables still remain")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == '__main__':
    print("🧹 CalmConnect Database Cleanup Tool")
    print("=" * 40)
    cleanup_database()