param(
    [Parameter(Mandatory=$true)][string]$DumpFile,
    [string]$DatabaseUrl
)

if (-not $DatabaseUrl) { $DatabaseUrl = $env:DATABASE_URL }
if (-not $DatabaseUrl) { Write-Error "DATABASE_URL not provided. Pass as second arg or set DATABASE_URL env var."; exit 1 }

# Choose tool based on file extension
$ext = [System.IO.Path]::GetExtension($DumpFile).TrimStart('.')

if ($ext -in @('pg','dump')) {
    Write-Output "Detected custom format dump — using pg_restore"
    & pg_restore --verbose --clean --no-acl --no-owner --dbname=$DatabaseUrl $DumpFile
} else {
    Write-Output "Assuming plain SQL file — using psql"
    & psql $DatabaseUrl -f $DumpFile
}

Write-Output "Restore finished. Run: python manage.py migrate --noinput; python manage.py collectstatic --noinput"