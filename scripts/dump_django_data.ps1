Param(
    [string]$OutFile = "dumpdata.json"
)

# PowerShell script to dump Django data on Windows
python manage.py dumpdata --natural-primary --natural-foreign --exclude auth.permission --exclude contenttypes --indent 2 > $OutFile
Write-Output "Django data dumped to $OutFile"
Write-Output "Upload $OutFile to Render or make available to the Render service and run:"
Write-Output "    python manage.py loaddata $OutFile"