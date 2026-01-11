#!/usr/bin/env bash
set -e

# Usage: ./scripts/restore_pgsql_from_file.sh <dump-file> [DATABASE_URL]
# If DATABASE_URL not passed, script uses $DATABASE_URL from environment.

if [ -z "$1" ]; then
  echo "Usage: $0 <dump-file> [DATABASE_URL]"
  exit 1
fi

DUMP_FILE="$1"
DBURL="${2:-$DATABASE_URL}"

if [ -z "$DBURL" ]; then
  echo "Error: DATABASE_URL not provided. Pass as 2nd arg or set DATABASE_URL env var."
  exit 1
fi

# Ensure psql or pg_restore is available
if ! command -v psql >/dev/null 2>&1 && ! command -v pg_restore >/dev/null 2>&1; then
  echo "Error: neither psql nor pg_restore found. Install PostgreSQL client tools (pgcli, libpq).
For Debian/Ubuntu: sudo apt-get install postgresql-client"
  exit 1
fi

# Detect file type by extension
ext="${DUMP_FILE##*.}"

if [ "$ext" = "pg" ] || [ "$ext" = "dump" ]; then
  echo "Detected custom format dump — using pg_restore"
  pg_restore --verbose --clean --no-acl --no-owner --dbname="$DBURL" "$DUMP_FILE"
else
  echo "Assuming plain SQL file — using psql"
  psql "$DBURL" -f "$DUMP_FILE"
fi

echo "Restore finished. Run: python manage.py migrate --noinput && python manage.py collectstatic --noinput"