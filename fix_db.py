#!/usr/bin/env python
"""
One-time database fix for Railway
Run this once to create missing tables
"""

import os
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect_backend.settings')
django.setup()

from django.core.management import execute_from_command_line

print("🔧 Fixing database tables...")
print("Running: python manage.py migrate --run-syncdb")

try:
    # Force create tables without migrations (for Railway)
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")

print("🎉 Database fix complete!")