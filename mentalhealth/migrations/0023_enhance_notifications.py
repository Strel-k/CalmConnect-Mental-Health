# Generated migration for enhanced notifications

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentalhealth', '0022_appointment_video_call_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='priority',
            field=models.CharField(
                choices=[
                    ('low', 'Low'),
                    ('normal', 'Normal'),
                    ('high', 'High'),
                    ('urgent', 'Urgent')
                ],
                default='normal',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='category',
            field=models.CharField(
                choices=[
                    ('appointment', 'Appointment'),
                    ('report', 'Report'),
                    ('system', 'System'),
                    ('reminder', 'Reminder'),
                    ('feedback', 'Feedback'),
                    ('general', 'General')
                ],
                default='general',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='action_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='action_text',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(
                choices=[
                    ('appointment', 'Appointment'),
                    ('report', 'Report'),
                    ('system', 'System'),
                    ('reminder', 'Reminder'),
                    ('feedback', 'Feedback'),
                    ('general', 'General')
                ],
                default='general',
                max_length=20
            ),
        ),
    ]