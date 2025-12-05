#!/usr/bin/env python
"""
Railway Migration Helper
Run this script on Railway if automatic migrations fail.
Usage: python migrate_railway.py
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def main():
    print("🚂 Railway Migration Helper")
    print("=" * 40)

    # Check if we're in Railway environment
    if not (os.environ.get('RAILWAY_PROJECT_ID') or os.environ.get('RAILWAY_ENVIRONMENT')):
        print("⚠️  Warning: Not running on Railway. This script is designed for Railway deployment.")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Aborted.")
            return

    # Run migrations
    success = run_command(
        "python manage.py migrate --verbosity=1",
        "Running Django migrations"
    )

    if success:
        print("\n🎉 Database migrations completed successfully!")
        print("Your Railway app should now work without database errors.")

        # Show migration status
        print("\n📊 Current migration status:")
        run_command("python manage.py showmigrations mentalhealth", "Checking migration status")

    else:
        print("\n❌ Migration failed. Please check the Railway logs for more details.")
        print("You may need to:")
        print("1. Check your DATABASE_URL environment variable")
        print("2. Verify database connectivity")
        print("3. Contact Railway support if issues persist")

if __name__ == '__main__':
    main()