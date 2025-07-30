from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('mentalhealth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='counselor',
            field=models.ForeignKey(
                to='mentalhealth.Counselor',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,  # Temporary, we'll remove this later
                blank=True
            ),
        ),
    ]