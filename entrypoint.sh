#!/bin/bash
set -e

echo "Running database migrations..."
python run_migrations.py

echo "Starting Django server..."
exec "$@"