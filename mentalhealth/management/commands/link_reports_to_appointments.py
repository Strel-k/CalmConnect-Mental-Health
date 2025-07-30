from django.core.management.base import BaseCommand
from mentalhealth.models import Report, Appointment
from django.db.models import Q

class Command(BaseCommand):
    help = 'Link existing session reports to their appointments if possible.'

    def handle(self, *args, **options):
        count_linked = 0
        count_skipped = 0
        for report in Report.objects.filter(report_type='session', appointment__isnull=True):
            # Try to find a completed appointment for the same user, counselor, and date
            possible_appointments = Appointment.objects.filter(
                user=report.user,
                counselor=report.counselor,
                status='completed',
                date=report.created_at.date()
            )
            if possible_appointments.count() == 1:
                report.appointment = possible_appointments.first()
                report.save()
                count_linked += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Linked report {report.id} to appointment {report.appointment.id}'
                ))
            else:
                count_skipped += 1
                self.stdout.write(self.style.WARNING(
                    f'Skipped report {report.id}: found {possible_appointments.count()} possible appointments.'
                ))
        self.stdout.write(self.style.SUCCESS(f'Linked {count_linked} reports. Skipped {count_skipped} reports.')) 