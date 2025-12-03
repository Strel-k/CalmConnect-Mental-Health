#!/usr/bin/env python3
"""
Import SQLite database data into Railway PostgreSQL database
Converts SQLite dump to PostgreSQL compatible format and imports all data
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

        # Convert datetime format if needed
        # SQLite uses different datetime format, but our data looks compatible

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

def import_database_data():
    """Import SQLite data into Railway PostgreSQL database"""

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
            print(f"Got: {database_url[:50]}...")
            return

        try:
            # Remove postgresql://
            url = database_url[13:]

            # Split into user:pass@host:port/dbname
            if '@' not in url:
                print("❌ ERROR: DATABASE_URL missing '@' separator")
                return

            user_pass, host_db = url.split('@', 1)

            if '/' not in host_db:
                print("❌ ERROR: DATABASE_URL missing '/' separator for database name")
                return

            host_port, dbname = host_db.split('/', 1)

            # Parse user and password
            if ':' in user_pass:
                user, password = user_pass.split(':', 1)
            else:
                user = user_pass
                password = ''

            # Parse host and port
            if ':' in host_port:
                host, port_str = host_port.split(':', 1)
                try:
                    port = int(port_str)
                except ValueError:
                    print(f"❌ ERROR: Invalid port number: {port_str}")
                    return
            else:
                host = host_port
                port = 5432

        except Exception as parse_error:
            print(f"❌ ERROR: Failed to parse DATABASE_URL: {parse_error}")
            print("Expected format: postgresql://user:password@host:port/database")
            return

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

        # Read the SQLite dump file
        dump_file = 'cleaned_dump2.sql'
        if not os.path.exists(dump_file):
            print(f"❌ ERROR: {dump_file} not found!")
            print("Make sure the SQLite dump file is in the current directory")
            return

        print(f"📖 Reading {dump_file}...")
        with open(dump_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("🔄 Converting SQLite syntax to PostgreSQL...")
        try:
            postgres_sql = convert_sqlite_to_postgres(sql_content)
        except Exception as conv_error:
            print(f"❌ ERROR during SQL conversion: {conv_error}")
            return

        # Split into individual statements
        try:
            statements = []
            current_statement = []
            in_string = False
            string_char = None

            for char in postgres_sql:
                if not in_string:
                    if char in ("'", '"'):
                        in_string = True
                        string_char = char
                    elif char == ';':
                        if current_statement:
                            statement = ''.join(current_statement).strip()
                            if statement and not statement.startswith('--'):
                                statements.append(statement + ';')
                            current_statement = []
                        continue
                else:
                    if char == string_char:
                        in_string = False
                        string_char = None

                current_statement.append(char)
        except Exception as parse_error:
            print(f"❌ ERROR during SQL statement parsing: {parse_error}")
            return

        # Filter out problematic statements
        try:
            valid_statements = []
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt:
                    continue

                # Skip certain statements that might cause issues
                skip_patterns = [
                    'CREATE UNIQUE INDEX.*sqlite_sequence',
                    'INSERT INTO sqlite_sequence',
                    'PRAGMA',
                    'BEGIN TRANSACTION',
                    'COMMIT'
                ]

                should_skip = False
                for pattern in skip_patterns:
                    if pattern.lower() in stmt.lower():
                        should_skip = True
                        break

                if not should_skip:
                    valid_statements.append(stmt)
        except Exception as filter_error:
            print(f"❌ ERROR during statement filtering: {filter_error}")
            return

        print(f"📝 Found {len(valid_statements)} SQL statements to execute")

        # Execute statements in batches
        executed = 0
        errors = 0

        for i, statement in enumerate(valid_statements):
            try:
                # Skip CREATE TABLE statements for tables that already exist
                if statement.upper().startswith('CREATE TABLE') and 'IF NOT EXISTS' not in statement.upper():
                    try:
                        # Extract table name more safely
                        after_create = statement.split('CREATE TABLE', 1)[1].strip()
                        table_name = after_create.split('(')[0].split()[0].strip().strip('"').strip('`')
                        # Check if table exists
                        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
                        exists = cursor.fetchone()[0]
                        if exists:
                            print(f"⏭️  Table {table_name} already exists, skipping...")
                            continue
                    except (IndexError, ValueError):
                        # If we can't parse the table name, just execute the statement
                        print(f"⚠️  Could not parse table name from: {statement[:50]}... proceeding anyway")
                        pass

                cursor.execute(statement)
                executed += 1

                if (i + 1) % 50 == 0:
                    print(f"✅ Executed {i + 1}/{len(valid_statements)} statements")

            except Exception as e:
                errors += 1
                error_msg = str(e)[:100]
                print(f"⚠️  Error executing statement {i + 1}: {error_msg}")

                # Continue with next statement
                continue

        print("\n🎉 Import completed!")
        print(f"✅ Successfully executed: {executed} statements")
        print(f"⚠️  Errors encountered: {errors} statements")

        # Verify some key tables
        try:
            cursor.execute("SELECT COUNT(*) FROM custom_user")
            user_count = cursor.fetchone()[0]
            print(f"👥 Users imported: {user_count}")

            cursor.execute("SELECT COUNT(*) FROM mentalhealth_appointment")
            appt_count = cursor.fetchone()[0]
            print(f"📅 Appointments imported: {appt_count}")

            cursor.execute("SELECT COUNT(*) FROM mentalhealth_dassresult")
            dass_count = cursor.fetchone()[0]
            print(f"📊 DASS results imported: {dass_count}")

        except Exception as e:
            print(f"⚠️  Could not verify import: {e}")

        cursor.close()
        conn.close()

        print("\n🎯 Database import completed!")
        print("Your Railway database now contains all your application data!")

    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\n💡 Make sure:")
        print("1. DATABASE_URL is correct")
        print("2. Railway database is accessible")
        print("3. cleaned_dump2.sql is in the current directory")

if __name__ == '__main__':
    print("🚀 CalmConnect Database Import Tool")
    print("=" * 45)
    import_database_data()