Restoring a PostgreSQL dump into Render — Quick Steps

Prerequisites
- Your Postgres dump file (`dump.sql` or custom `dump.pg`) available locally or uploaded to a machine that can reach Render Postgres.
- `psql` and/or `pg_restore` installed locally (or use Render's shell).
- Render Web Service or Database service created and `DATABASE_URL` or connection info available.

Options
A) Restore from your local machine (recommended when network access allowed)
1. Get Render Postgres connection string (DATABASE_URL) from Render dashboard for your Database service.
   - It looks like: `postgres://user:pass@host:port/dbname`

2. On your machine, confirm `psql` / `pg_restore` are installed.

3. Use the provided helper script (Linux/macOS):

```bash
# Make script executable once
chmod +x scripts/restore_pgsql_from_file.sh

# For plain SQL
./scripts/restore_pgsql_from_file.sh dump.sql "postgres://user:pass@host:port/dbname"

# For custom-format dump (.pg)
./scripts/restore_pgsql_from_file.sh dump.pg "postgres://user:pass@host:port/dbname"
```

Or on Windows (PowerShell):

```powershell
# Example
.
cripts\restore_pgsql_from_file.ps1 -DumpFile dump.sql -DatabaseUrl "postgres://user:pass@host:port/dbname"
```

4. After restore, run migrations and collectstatic in your Render Web Service (or locally with `DATABASE_URL` set):

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

B) Restore from Render's Shell (no local client needed)
1. Upload `dump.sql` or `dump.pg` into your repo or to a temporary storage (S3, blob) and make it available to the Render service, or push it to a temporary branch and deploy.
2. Open the Web Service shell in Render dashboard (each service has a Shell option) or the Database shell.
3. Run inside Render shell:

```bash
# If plain SQL
psql "$DATABASE_URL" -f /path/to/dump.sql

# If custom format
pg_restore --verbose --clean --no-acl --no-owner --dbname="$DATABASE_URL" /path/to/dump.pg
```

C) Notes & Caveats
- Custom-format dumps preserve ownership and sequences better; use `pg_restore` for `.pg` files.
- If you get authentication or network errors, ensure your machine's IP isn't blocked and check Render DB permissions.
- After restore, verify sequences (serial columns) are set correctly; a quick fix:

```sql
SELECT setval(pg_get_serial_sequence('your_table','id'), COALESCE(MAX(id),1)) FROM your_table;
```

Verification
- Connect with psql and check table counts:

```bash
psql "$DATABASE_URL" -c "SELECT count(*) FROM mentalhealth_customuser;"
```

- Start the app pointing to Render DB and smoke-test key flows (login, forms, WebSocket endpoints).

Rollback
- Keep your old Railway DB running until you're satisfied.
- If needed, restore from your backup dump or point app back to Railway DB by resetting `DATABASE_URL`.

If you want, I can:
- Attempt a local dry-run restore (if you provide a sample dump and have `psql` locally), or
- Prepare a small script that fetches the Render `DATABASE_URL` from a Render service via `render` CLI (requires `render` CLI auth).

