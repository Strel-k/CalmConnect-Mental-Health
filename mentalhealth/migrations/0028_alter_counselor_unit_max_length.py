# Generated manually to fix counselor unit field max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentalhealth', '0027_customuser_password_reset_expires_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counselor',
            name='unit',
            field=models.CharField(max_length=100),
        ),
    ]