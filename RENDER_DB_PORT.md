Porting your database to Render — Quick Guide

Overview
- Two straightforward paths depending on your source DB type and size:
  1) Django fixture route (recommended for medium/small projects)
  2) pg_dump/psql route (recommended for large Postgres DBs)

Prerequisites
- Local `python` and project dependencies installed
- `manage.py` available
- Access to Render dashboard and the Render Postgres connection string (DATABASE_URL)
- Optional: `pg_dump` and `psql` installed locally for SQL transfer

Path A — Django fixtures (universal, safe)
1. Locally create a fixture: 

```bash
./scripts/dump_django_data.sh dumpdata.json
# or on Windows
./scripts/dump_django_data.ps1 -OutFile dumpdata.json
```

2. Upload `dumpdata.json` to your repository (temporary branch) or to a storage bucket accessible from Render.
3. In Render Dashboard, open the Web Service shell (or use `renderctl`/Deploy Hook) and run:

```bash
# Ensure env vars set (DATABASE_URL pointing to Render Postgres)
python manage.py migrate --noinput
python manage.py loaddata dumpdata.json
```

4. Verify app behavior, test key pages, and check logs.

Pros: Simple, uses Django ORM, respects natural keys.
Cons: Can be slow for very large datasets; many related objects may require careful ordering.

Path B — pg_dump + psql (direct SQL transfer for Postgres)
Prereqs: `pg_dump` and `psql` installed; source DB accessible over network or you can run these from the source host.

1. Export from source Postgres:

```bash
pg_dump --format=custom --no-acl --no-owner -h <SRC_HOST> -U <SRC_USER> -d <SRC_DB> -f dump.pg
# or plain SQL
pg_dump -h <SRC_HOST> -U <SRC_USER> -d <SRC_DB> -F p > dump.sql
```

2. Transfer `dump.pg` or `dump.sql` to a machine that can reach Render Postgres.
3. Restore into Render Postgres (get `DATABASE_URL` from Render service env or dashboard):

```bash
# If using plain SQL
psql <DATABASE_URL> -f dump.sql

# If using custom format (recommended)
pg_restore --verbose --clean --no-acl --no-owner -h <RENDER_HOST> -U <RENDER_USER> -d <RENDER_DB> dump.pg
```

4. On Render, run Django migrations (if schema changed) and run any post-import fixes:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Pros: Fast and reliable for large DBs; preserves sequence states and indexes.
Cons: Requires network access and Postgres client tools.

Verification & Rollback
- Always take a backup from the source before migrating.
- Verify a subset of important rows/tables after import (SELECT counts, sample rows).
- Keep old Railway DB running until Render is fully validated.
- Rollback: point DNS back to Railway and/or restore from your pre-migration dumps.

Notes specific to this repo
- `settings.py` already parses `DATABASE_URL` and supports build-time no-DB commands.
- Use `python manage.py dumpdata` to avoid DB-specific nuances when going from SQLite→Postgres or Postgres→Postgres.

If you'd like, I can:
- Add an automated script to upload fixtures to the repo and run `loaddata` during deploy (requires repo push privileges), or
- Add a safe `pg_restore` helper that reads `DATABASE_URL` from environment and runs `pg_restore` (you'll still need to provide credentials locally).

Tell me which path you prefer and I will create the corresponding helper script and run/check it locally where possible.