# Generated manually for renaming counselor unit field to college

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentalhealth', '0037_add_counselor_unit_choices'),
    ]

    operations = [
        migrations.RenameField(
            model_name='counselor',
            old_name='unit',
            new_name='college',
        ),
    ]