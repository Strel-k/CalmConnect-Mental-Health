from django.db import migrations

def convert_data(apps, schema_editor):
    Appointment = apps.get_model('mentalhealth', 'Appointment')
    Counselor = apps.get_model('mentalhealth', 'Counselor')
    
    default_counselor, _ = Counselor.objects.get_or_create(
        name="Default Counselor",
        defaults={
            'unit': 'General Counseling',
            'rank': 'Counselor',
            'is_active': True
        }
    )
    
    for appointment in Appointment.objects.all():
        if not hasattr(appointment, 'counselor') or appointment.counselor is None:
            # Handle appointments without counselor data
            appointment.counselor = default_counselor
            appointment.save()
        elif isinstance(appointment.counselor, str):
            # Convert text counselors
            counselor, _ = Counselor.objects.get_or_create(
                name=appointment.counselor,
                defaults={
                    'unit': 'General Counseling',
                    'rank': 'Counselor',
                    'is_active': True
                }
            )
            appointment.counselor = counselor
            appointment.save()

class Migration(migrations.Migration):
    dependencies = [
        ('mentalhealth', '0004_merge_20250628_0943'),
    ]

    operations = [
        migrations.RunPython(convert_data),
    ]