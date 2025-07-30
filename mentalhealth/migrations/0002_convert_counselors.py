from django.db import migrations


def convert_counselors(apps, schema_editor):
    Appointment = apps.get_model('mentalhealth', 'Appointment')
    Counselor = apps.get_model('mentalhealth', 'Counselor')
    
    for appointment in Appointment.objects.all():
        if isinstance(appointment.counselor, str):  # If it's still text
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
        ('mentalhealth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_counselors),
    ]