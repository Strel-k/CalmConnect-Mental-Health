from django.core.management.base import BaseCommand
from mentalhealth.models import Counselor

class Command(BaseCommand):
    help = 'Seeds the database with initial counselor data'

    def handle(self, *args, **options):
        counselors = [
            {
                'name': 'Ms. Rivera',
                'unit': 'Career Guidance Unit',
                'rank': 'Associate Professor III',
                'available_days': ['Monday', 'Wednesday', 'Friday'],
                'available_times': ['09:00', '11:00', '14:00', '16:00']
            },
            {
                'name': 'Mr. Santos',
                'unit': 'Student Wellness Center',
                'rank': 'Assistant Professor I',
                'available_days': ['Tuesday', 'Thursday'],
                'available_times': ['10:00', '13:00', '15:00']
            },
            # Add more counselors as needed
        ]
        
        for data in counselors:
            Counselor.objects.get_or_create(
                name=data['name'],
                defaults={
                    'unit': data['unit'],
                    'rank': data['rank'],
                    'available_days': data['available_days'],
                    'available_times': data['available_times']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded counselors'))