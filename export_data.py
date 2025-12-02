#!/usr/bin/env python
"""
Clean data export script for CalmConnect
"""
import os
import sys
import django
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')

# Setup Django (suppress startup prints)
django.setup()

from django.core.management import call_command
from django.core.management.base import CommandError

def export_data():
    """Export production data cleanly"""
    try:
        print("Exporting production data...")

        # Export data excluding problematic models
        with open('production_data_clean.json', 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                '--exclude=contenttypes',
                '--exclude=auth.permission',
                '--exclude=sessions',
                '--exclude=admin.logentry',
                '--indent=2',
                stdout=f
            )

        print("✅ Data exported successfully to production_data_clean.json")

        # Verify the file starts with valid JSON
        with open('production_data_clean.json', 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('[') or first_line.startswith('{'):
                print("✅ JSON file appears valid")
            else:
                print(f"⚠️  Warning: File starts with: {first_line}")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = export_data()
    sys.exit(0 if success else 1)