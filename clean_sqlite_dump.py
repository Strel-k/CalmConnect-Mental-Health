#!/usr/bin/env python
"""
Clean and decode SQLite dump file for proper import
"""
import os
from pathlib import Path

def clean_sqlite_dump():
    """Clean and decode the SQLite dump file"""
    print("Cleaning SQLite dump file...")

    input_path = Path('sqlite_dump.sql')
    output_path = Path('sqlite_dump_clean.sql')

    if not input_path.exists():
        print(f"SQLite dump file not found: {input_path}")
        return False

    try:
        # Read the file as binary to handle encoding properly
        with open(input_path, 'rb') as f:
            raw_content = f.read()

        print(f"Original file size: {len(raw_content)} bytes")

        # Try to decode as UTF-16 (common for SQLite dumps)
        try:
            # Remove null bytes and decode
            cleaned_content = raw_content.replace(b'\x00', b'').decode('utf-16')
            print("Successfully decoded as UTF-16")
        except UnicodeDecodeError:
            try:
                # Try UTF-8 with error handling
                cleaned_content = raw_content.decode('utf-8', errors='ignore')
                print("Decoded as UTF-8 with error handling")
            except UnicodeDecodeError:
                print("Failed to decode file")
                return False

        # Clean up the content
        lines = cleaned_content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and line != '':
                cleaned_lines.append(line)

        # Write cleaned content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))

        print(f"Cleaned file saved as: {output_path}")
        print(f"Cleaned file size: {len(cleaned_lines)} lines")

        # Count INSERT statements in cleaned file
        insert_count = sum(1 for line in cleaned_lines if line.upper().startswith('INSERT INTO'))
        print(f"INSERT statements found: {insert_count}")

        return True

    except Exception as e:
        print(f"Error cleaning file: {e}")
        return False

def show_sample_data():
    """Show sample data from cleaned file"""
    output_path = Path('sqlite_dump_clean.sql')

    if not output_path.exists():
        print("Cleaned file not found")
        return

    print("\nSample data from cleaned file:")
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Show first few INSERT statements
    insert_lines = [line for line in lines if line.upper().startswith('INSERT INTO')]

    for i, line in enumerate(insert_lines[:3]):
        print(f"\nINSERT {i+1}: {line[:200]}...")

if __name__ == '__main__':
    if clean_sqlite_dump():
        show_sample_data()
        print("\nSQLite dump file cleaned successfully!")
        print("You can now run: python import_data.py")
    else:
        print("Failed to clean SQLite dump file")
