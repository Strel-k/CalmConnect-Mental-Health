from django.db import migrations
from django.db import migrations, models  # Added models import
import django.db.models.deletion

def set_default_counselor(apps, schema_editor):
    Counselor = apps.get_model('mentalhealth', 'Counselor')
    Appointment = apps.get_model('mentalhealth', 'Appointment')
    default_counselor = Counselor.objects.get(name="Default Counselor")
    Appointment.objects.filter(counselor__isnull=True).update(counselor=default_counselor)

class Migration(migrations.Migration):
    dependencies = [
        ('mentalhealth', '0005_convert_counselor_data'),
    ]

    operations = [
        migrations.RunPython(set_default_counselor),
        migrations.AlterField(
            model_name='appointment',
            name='counselor',
            field=models.ForeignKey(
                to='mentalhealth.Counselor',
                on_delete=models.PROTECT,
                null=False,
                default=1  # Your default counselor ID
            ),
        ),
    ]