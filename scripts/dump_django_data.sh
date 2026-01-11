#!/usr/bin/env bash
set -e

# Dump all Django app data (excludes auth permissions and contenttypes)
# Usage: ./scripts/dump_django_data.sh [output-file.json]
OUT_FILE=${1:-dumpdata.json}
python manage.py dumpdata --natural-primary --natural-foreign --exclude auth.permission --exclude contenttypes --indent 2 > "$OUT_FILE"

echo "Django data dumped to $OUT_FILE"

echo "Next steps: upload $OUT_FILE to Render (e.g. in repo or temporary storage) and run on Render:"
echo "  python manage.py loaddata $OUT_FILE"