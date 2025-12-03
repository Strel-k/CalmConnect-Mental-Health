#!/usr/bin/env python3
"""
Import exported data back into migrated database
"""

import os
import psycopg2
import json
from datetime import datetime

def import_exported_data():
    """Import data from exported_data.json into the current database"""

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

        # Load exported data
        if not os.path.exists('exported_data.json'):
            print("❌ ERROR: exported_data.json not found!")
            print("Run the export script first: python import_database_data.py")
            return

        print("📖 Loading exported data...")
        with open('exported_data.json', 'r', encoding='utf-8') as f:
            export_data = json.load(f)

        print(f"📊 Found data for {len(export_data)} tables")

        # Import data in correct order (respecting foreign keys)
        import_order = [
            'custom_user',  # Must be first
            'mentalhealth_counselor',  # References custom_user
            'mentalhealth_appointment',  # References both
            'mentalhealth_dassresult',
            'mentalhealth_report',
            'mentalhealth_notification'
        ]

        total_imported = 0

        for table_name in import_order:
            if table_name not in export_data:
                print(f"⏭️  No data for {table_name}, skipping")
                continue

            table_data = export_data[table_name]
            columns = table_data['columns']
            rows = table_data['data']

            if not rows:
                print(f"⏭️  {table_name} has no data, skipping")
                continue

            print(f"📥 Importing {len(rows)} records into {table_name}...")

            # Build INSERT statement
            columns_str = ', '.join(f'"{col}"' for col in columns)
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'

            # Handle potential conflicts (skip duplicates)
            insert_sql += ' ON CONFLICT DO NOTHING'

            imported = 0
            errors = 0

            for row in rows:
                try:
                    # Convert string values that should be proper types
                    processed_row = []
                    for i, value in enumerate(row):
                        col_name = columns[i].lower()

                        # Handle special cases
                        if value is None:
                            processed_row.append(None)
                        elif col_name in ['date_taken', 'created_at', 'updated_at', 'submitted_at',
                                        'scheduled_start', 'scheduled_end', 'joined_at', 'left_at',
                                        'expires_at', 'approved_denied_at', 'cancelled_at', 'date', 'time']:
                            # Try to parse as datetime
                            if isinstance(value, str):
                                try:
                                    # Handle different datetime formats
                                    if 'T' in value:
                                        processed_row.append(value)  # ISO format
                                    else:
                                        processed_row.append(value)  # Keep as string
                                except:
                                    processed_row.append(value)
                            else:
                                processed_row.append(value)
                        elif col_name in ['is_active', 'is_staff', 'is_superuser', 'email_verified',
                                        'force_password_change', 'read', 'dismissed']:
                            # Convert to boolean
                            if isinstance(value, str):
                                processed_row.append(value.lower() in ('true', '1', 'yes'))
                            else:
                                processed_row.append(bool(value))
                        else:
                            processed_row.append(value)

                    cursor.execute(insert_sql, processed_row)
                    imported += 1

                except Exception as e:
                    errors += 1
                    if errors <= 3:  # Show first few errors
                        print(f"⚠️  Error importing row: {str(e)[:100]}")

            print(f"✅ Imported {imported} records into {table_name}")
            if errors > 0:
                print(f"⚠️  {errors} records had errors (likely duplicates)")

            total_imported += imported

        print("\n🎉 Data import completed!")
        print(f"✅ Successfully imported: {total_imported} total records")

        # Verify import
        try:
            cursor.execute("SELECT COUNT(*) FROM custom_user")
            user_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM mentalhealth_appointment")
            appt_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM mentalhealth_dassresult")
            dass_count = cursor.fetchone()[0]

            print("\n📊 Verification:")
            print(f"👥 Users: {user_count}")
            print(f"📅 Appointments: {appt_count}")
            print(f"📊 DASS results: {dass_count}")

        except Exception as e:
            print(f"⚠️  Could not verify: {e}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Import error: {e}")

if __name__ == '__main__':
    print("📥 CalmConnect Data Import Tool")
    print("=" * 35)
    import_exported_data()