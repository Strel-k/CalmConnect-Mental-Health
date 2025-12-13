from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('mentalhealth', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE mentalhealth_appointment ADD COLUMN IF NOT EXISTS "
            "counselor_id INTEGER REFERENCES mentalhealth_counselor(id) "
            "ON DELETE CASCADE NULL;",
            reverse_sql="ALTER TABLE mentalhealth_appointment DROP COLUMN "
            "counselor_id;",
        ),
    ]